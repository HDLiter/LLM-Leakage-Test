#!/usr/bin/env bash
# WS1 AutoDL bring-up — run once after SSH'ing into a fresh A6000 instance.
#
# Stage 1 of plans/ws1-cloud-execution.md. Creates /data/{models,traces,repo},
# installs Python dependencies for the local CLI scripts, pins the vLLM
# Docker image, and stages HF env so subsequent model downloads use the
# Chinese mirror (default network on AutoDL cannot reach huggingface.co).
#
# Per-model download/launch is left to the operator (see Stage 2 in the
# plan); this script only does the per-instance one-shot.
#
# Usage:
#   chmod +x scripts/ws1_provision_autodl.sh
#   ./scripts/ws1_provision_autodl.sh
#
# Required env (caller must export before running):
#   HF_TOKEN         fine-grained read-only token (created locally,
#                    transferred to the instance via SCP into ~/.env)
#
# Optional env:
#   VLLM_IMAGE_TAG   defaults to "vllm/vllm-openai:v0.7.0"
#   DATA_ROOT        defaults to /data

set -euo pipefail

# vLLM v0.7.0 lacks Qwen3ForCausalLM (added in v0.8.5). Pin to a recent
# stable that supports both Qwen2.5 AWQ and Qwen3 AWQ; verify on a
# minor smoke per the WS1 stage-1 plan.
VLLM_IMAGE_TAG="${VLLM_IMAGE_TAG:-vllm/vllm-openai:v0.10.0}"
DATA_ROOT="${DATA_ROOT:-/data}"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

echo "== ws1_provision_autodl =="
echo "VLLM_IMAGE_TAG = ${VLLM_IMAGE_TAG}"
echo "DATA_ROOT      = ${DATA_ROOT}"
echo "HF_ENDPOINT    = ${HF_ENDPOINT}"

# 1. GPU sanity
if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "FATAL: nvidia-smi not found; is this a GPU instance?" >&2
    exit 2
fi
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

# 2. Token check
if [[ -z "${HF_TOKEN:-}" ]]; then
    echo "FATAL: HF_TOKEN not set; export it before running." >&2
    echo "       (Create a fine-grained read-only token at" >&2
    echo "        https://huggingface.co/settings/tokens )" >&2
    exit 2
fi
HF_TOKEN="${HF_TOKEN//$'\r'/}"
export HF_TOKEN

# 3. Directory layout
mkdir -p "${DATA_ROOT}/models" "${DATA_ROOT}/traces" "${DATA_ROOT}/repo"
echo "created ${DATA_ROOT}/{models,traces,repo}"

# 4. Persist HF env to ~/.bashrc so future shells inherit it
HF_BLOCK_MARKER="# === ws1 HF env ==="
if ! grep -qF "${HF_BLOCK_MARKER}" "${HOME}/.bashrc" 2>/dev/null; then
    cat >> "${HOME}/.bashrc" <<EOF

${HF_BLOCK_MARKER}
export HF_ENDPOINT="${HF_ENDPOINT}"
export HF_HOME="${DATA_ROOT}/hf_cache"
export NO_PROXY="localhost,127.0.0.1,host.docker.internal"
export no_proxy="\$NO_PROXY"
EOF
    echo "patched ~/.bashrc with HF env block"
fi
export HF_ENDPOINT
export HF_HOME="${DATA_ROOT}/hf_cache"
export NO_PROXY="localhost,127.0.0.1,host.docker.internal"
export no_proxy="$NO_PROXY"

# 5. Python deps for the local CLI (operator + backends)
python -m pip install --upgrade pip
python -m pip install \
    "pydantic>=2.0" \
    "httpx>=0.27" \
    "pandas>=2.2" \
    "pyarrow>=14" \
    "pyyaml>=6" \
    "huggingface_hub>=0.24,<1.0" \
    "numpy>=1.26"

# transformers + torch are installed only if --with-torch is requested,
# since the vLLM container ships its own and we only need them on the
# host for the offline_hf fallback path.
if [[ " $* " == *" --with-torch "* ]]; then
    echo "installing torch + transformers (offline_hf fallback path)"
    python -m pip install \
        "torch>=2.4" \
        "transformers>=4.45" \
        "accelerate>=0.30"
fi

# 6. HF login (token, no git credential helper)
huggingface-cli login --token "${HF_TOKEN}"
huggingface-cli whoami

# 7. Pull vLLM image and record digest
echo "pulling ${VLLM_IMAGE_TAG} ..."
docker pull "${VLLM_IMAGE_TAG}"
DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "${VLLM_IMAGE_TAG}")"
echo "${DIGEST}" > "${DATA_ROOT}/vllm_image_digest.txt"
echo "vLLM image digest -> ${DATA_ROOT}/vllm_image_digest.txt"
cat "${DATA_ROOT}/vllm_image_digest.txt"

cat <<'EOF'

== provisioning done ==

Next steps (per model, low-risk first; see plans/ws1-cloud-execution.md §5):

  # qwen2.5-7b — AWQ via vLLM (low risk; same family already verified locally)
  huggingface-cli download Qwen/Qwen2.5-7B-Instruct-AWQ \
      --revision <pinned-sha> \
      --local-dir /data/models/qwen2.5-7b
  docker run -d --gpus all --rm \
      -v /data/models/qwen2.5-7b:/model \
      -p 8000:8000 \
      $(cat /data/vllm_image_digest.txt) \
      --model /model \
      --served-model-name qwen2.5-7b \
      --gpu-memory-utilization 0.9 \
      --quantization awq_marlin
  curl -s http://localhost:8000/v1/models | jq .
  cd /data/repo
  python scripts/ws1_run_logprob.py \
      --model qwen2.5-7b --smoke --vllm-url http://localhost:8000

Repeat for the post-2026-04-27 capacity-curve fleet:
  Qwen2.5: 1.5B, 3B, 7B, 14B, 32B  (all AWQ, --quantization awq_marlin)
  Qwen3:   4B, 8B, 14B, 32B        (all AWQ; needs vLLM >= 0.8.5)

GLM-4-9B requires --trust-remote-code (custom ChatGLM4Tokenizer):

  huggingface-cli download THUDM/glm-4-9b-chat \
      --revision <pinned-sha> \
      --local-dir /data/models/glm-4-9b
  docker run -d --gpus all --rm \
      -v /data/models/glm-4-9b:/model \
      -p 8000:8000 \
      $(cat /data/vllm_image_digest.txt) \
      --model /model \
      --served-model-name glm-4-9b \
      --gpu-memory-utilization 0.85 \
      --trust-remote-code \
      --dtype float16
  cd /data/repo
  python scripts/ws1_run_logprob.py \
      --model glm-4-9b --smoke --vllm-url http://localhost:8000
  # If echo=True is unsupported on GLM, fall through to offline_hf:
  python scripts/ws1_run_logprob.py \
      --model glm-4-9b --smoke --backend offline_hf \
      --model-path /data/models/glm-4-9b --device cuda --torch-dtype float16
  # (offline_hf path requires this script was run with --with-torch)

EOF
