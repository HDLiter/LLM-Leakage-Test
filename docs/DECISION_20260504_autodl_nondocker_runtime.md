# Decision Memo — AutoDL Non-Docker vLLM Runtime

## Context

AutoDL container instances are Docker-isolated environments. The official
AutoDL environment documentation states that container instances do not
support using Docker inside the instance; Docker requires a bare-metal rental.

The 2026-05-04 WS1 Stage 1 attempt confirmed that behavior in practice:
the RTX PRO 6000 instance exposed the GPU and `/root/autodl-tmp` data disk,
but had no `docker` CLI/daemon or Docker socket. Provisioning reached HF auth
and dependency installation, then stopped at `docker: command not found`.

## Decision

WS1 will run vLLM directly in the AutoDL container Python environment rather
than through `vllm/vllm-openai` Docker images.

`scripts/ws1_provision_autodl.sh` now installs/validates the host vLLM
runtime in a data-disk virtualenv (`/data/venvs/ws1` by default, backed by
AutoDL's `/root/autodl-tmp`) and calls
`scripts/ws1_capture_runtime_provenance.py`, which writes:

- `/data/vllm_runtime_provenance.json`
- `/data/vllm_runtime_digest.txt`

The digest is `sha256:<64-hex>` over a canonical runtime payload covering
Python, platform, GPU/driver query, selected package versions, `pip freeze`,
selected non-secret environment variables, resolved `/data`, and repo commit.

For schema stability, the existing `vllm_image_digest` field remains in
`LogProbTrace`, `RunManifest`, and CLI arguments. On AutoDL non-Docker runs,
that field stores the runtime provenance digest. Docker/bare-metal runs may
still store a Docker image digest.

## Consequences

- The confirmatory hard gate remains strict: pilot and Path E still require a
  `sha256:<64-hex>` value via `--vllm-image-digest`.
- Reproducibility is weaker than an immutable Docker image digest, but the
  AutoDL environment is migratable through AutoDL image migration/saving and
  is bound by the captured runtime provenance JSON.
- Fleet cardinality and experiment design do not change: 14 P_predict, 12
  P_logprob, and 2 temporal PCSG pairs remain fixed.
- No black-box route changes are implied.
- Operators must pass `$(cat /data/vllm_runtime_digest.txt)` to
  `scripts/ws1_pin_fleet.py`, `scripts/ws1_run_logprob.py` pilot/Path E modes,
  and `scripts/ws1_finalize_run_manifest.py`.

## Open Operational Risk

Host vLLM installation is more sensitive to Python/CUDA/Torch compatibility
than the original Docker image plan. Keep the venv and pip cache on the data
disk, not the 30 GB AutoDL system disk. The first model smoke
(`qwen2.5-7b`) is therefore a real runtime gate: if vLLM cannot serve AWQ on
Blackwell in the AutoDL Python environment, stop and record the exact
import/launch error before trying alternate vLLM/Torch versions.
