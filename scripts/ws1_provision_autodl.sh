#!/usr/bin/env bash
# WS1 AutoDL bring-up — run once after SSH'ing into a fresh AutoDL instance.
#
# Stage 1 of plans/ws1-cloud-execution.md. Creates /data/{models,traces,repo},
# installs Python dependencies for the local CLI scripts, installs/validates
# the non-Docker host vLLM runtime, captures a runtime provenance digest, and
# stages HF env so subsequent model downloads use the Chinese mirror (default
# network on AutoDL cannot reach huggingface.co).
#
# AutoDL container instances are already Docker-isolated and do not support
# nested Docker. The existing `vllm_image_digest` trace/manifest field stores
# `/data/vllm_runtime_provenance.json`'s `sha256:<64-hex>` digest on this path.
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
#   VLLM_PIP_SPEC          defaults to "vllm==0.10.0"
#   WS1_SKIP_VLLM_INSTALL  set to 1 to skip pip installing vLLM
#   DATA_ROOT              defaults to /data

set -euo pipefail

# vLLM v0.7.0 lacks Qwen3ForCausalLM (added in v0.8.5). Pin to a recent
# stable that supports both Qwen2.5 AWQ and Qwen3 AWQ; verify on a
# minor smoke per the WS1 stage-1 plan.
VLLM_PIP_SPEC="${VLLM_PIP_SPEC:-vllm==0.10.0}"
DATA_ROOT="${DATA_ROOT:-/data}"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

echo "== ws1_provision_autodl =="
echo "VLLM_PIP_SPEC = ${VLLM_PIP_SPEC}"
echo "DATA_ROOT      = ${DATA_ROOT}"
echo "HF_ENDPOINT    = ${HF_ENDPOINT}"

if ! command -v python >/dev/null 2>&1 && [[ -x /root/miniconda3/bin/python ]]; then
    export PATH="/root/miniconda3/bin:${PATH}"
fi

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
if [[ "${DATA_ROOT}" == "/data" && ! -e /data && -d /root/autodl-tmp ]]; then
    mkdir -p /root/autodl-tmp/data
    ln -s /root/autodl-tmp/data /data
    echo "created /data -> /root/autodl-tmp/data symlink"
fi
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

if [[ "${WS1_SKIP_VLLM_INSTALL:-0}" != "1" ]]; then
    echo "installing non-Docker vLLM runtime: ${VLLM_PIP_SPEC}"
    python -m pip install "${VLLM_PIP_SPEC}"
else
    echo "WS1_SKIP_VLLM_INSTALL=1; skipping vLLM pip install"
fi

# transformers + torch are installed only if --with-torch is requested,
# since vLLM normally pulls its own compatible torch stack and we only need
# accelerate on the host for the offline_hf fallback path.
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
chmod -R go-rwx "${HF_HOME}" 2>/dev/null || true

# 7. Capture non-Docker vLLM runtime provenance digest
python "${DATA_ROOT}/repo/scripts/ws1_capture_runtime_provenance.py" \
    --repo-root "${DATA_ROOT}/repo" \
    --output "${DATA_ROOT}/vllm_runtime_provenance.json" \
    --sha-output "${DATA_ROOT}/vllm_runtime_digest.txt"
cp "${DATA_ROOT}/vllm_runtime_digest.txt" "${DATA_ROOT}/vllm_image_digest.txt"
echo "vLLM runtime provenance -> ${DATA_ROOT}/vllm_runtime_provenance.json"
echo "vLLM runtime digest     -> ${DATA_ROOT}/vllm_runtime_digest.txt"
cat "${DATA_ROOT}/vllm_runtime_digest.txt"

cat <<'EOF'

== provisioning done ==

Next steps (per model, low-risk first; see plans/ws1-cloud-execution.md §5):

  # qwen2.5-7b — AWQ via vLLM (low risk; same family already verified locally)
  huggingface-cli download Qwen/Qwen2.5-7B-Instruct-AWQ \
      --revision <pinned-sha> \
      --local-dir /data/models/qwen2.5-7b
  nohup python -m vllm.entrypoints.openai.api_server \
      --model /data/models/qwen2.5-7b \
      --served-model-name qwen2.5-7b \
      --gpu-memory-utilization 0.9 \
      --quantization awq_marlin \
      > /data/traces/qwen2.5-7b.vllm.log 2>&1 &
  echo $! > /data/traces/qwen2.5-7b.vllm.pid
  curl -s http://localhost:8000/v1/models
  cd /data/repo
  python scripts/ws1_run_logprob.py \
      --model qwen2.5-7b --smoke --vllm-url http://localhost:8000 \
      --vllm-image-digest "$(cat /data/vllm_runtime_digest.txt)"

Repeat for the post-2026-04-27 capacity-curve fleet:
  Qwen2.5: 1.5B, 3B, 7B, 14B, 32B  (all AWQ, --quantization awq_marlin)
  Qwen3:   4B, 8B, 14B, 32B        (all AWQ; needs vLLM >= 0.8.5)

GLM-4-9B requires --trust-remote-code (custom ChatGLM4Tokenizer):

  huggingface-cli download THUDM/glm-4-9b-chat \
      --revision <pinned-sha> \
      --local-dir /data/models/glm-4-9b
  nohup python -m vllm.entrypoints.openai.api_server \
      --model /data/models/glm-4-9b \
      --served-model-name glm-4-9b \
      --gpu-memory-utilization 0.85 \
      --trust-remote-code \
      --dtype float16 \
      > /data/traces/glm-4-9b.vllm.log 2>&1 &
  echo $! > /data/traces/glm-4-9b.vllm.pid
  cd /data/repo
  python scripts/ws1_run_logprob.py \
      --model glm-4-9b --smoke --vllm-url http://localhost:8000 \
      --vllm-image-digest "$(cat /data/vllm_runtime_digest.txt)"
  # If echo=True is unsupported on GLM, fall through to offline_hf:
  python scripts/ws1_run_logprob.py \
      --model glm-4-9b --smoke --backend offline_hf \
      --model-path /data/models/glm-4-9b --device cuda --torch-dtype float16
  # (offline_hf path requires this script was run with --with-torch)

EOF
