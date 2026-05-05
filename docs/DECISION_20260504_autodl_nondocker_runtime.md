# Decision Memo — AutoDL Non-Docker vLLM Runtime

## Context

AutoDL container instances are Docker-isolated environments. The official
AutoDL environment documentation states that container instances do not
support using Docker inside the instance; Docker requires a bare-metal rental.
The same documentation also distinguishes AutoDL platform images and
migration from ordinary Docker images: saving an image captures the system
disk environment for reuse in another AutoDL instance, while the data disk
must be migrated or copied separately.

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

AutoDL's UI-level image save/migration remains useful operationally, but it
is not a repository-managed Docker artifact and does not produce a pullable
image digest. Because the WS1 venv, pip cache, HF cache, and temporary build
paths live under `/data` to avoid the 30 GB system disk, operators who migrate
the environment must either migrate/copy the data disk as well or rerun
`scripts/ws1_provision_autodl.sh` on the new instance.

## Consequences

- The confirmatory hard gate remains strict: pilot and Path E still require a
  `sha256:<64-hex>` value via `--vllm-image-digest`.
- Reproducibility is weaker than an immutable Docker image digest. AutoDL can
  migrate or save the container environment at the platform level, but WS1's
  managed provenance is the captured runtime provenance JSON plus its digest.
- Fleet cardinality and experiment design do not change: 14 P_predict, 12
  P_logprob, and 2 temporal PCSG pairs remain fixed.
- No black-box route changes are implied.
- Operators must pass `$(cat /data/vllm_runtime_digest.txt)` to
  `scripts/ws1_pin_fleet.py`, `scripts/ws1_run_logprob.py` pilot/Path E modes,
  and `scripts/ws1_finalize_run_manifest.py`.

## Open Operational Risk

Host vLLM installation is more sensitive to Python/CUDA/Torch compatibility
than the original Docker image plan. Keep the venv, pip cache, temporary
build/extract directory, and XDG cache on the data disk, not the 30 GB AutoDL
system disk. The first model smoke (`qwen2.5-7b`) is therefore a real runtime
gate: if vLLM cannot serve AWQ on Blackwell in the AutoDL Python environment,
stop and record the exact import/launch error before trying alternate
vLLM/Torch versions.

The 2026-05-04 non-Docker provision generated runtime digest
`sha256:a5f57079381be329fa35e18101b52027f5feaea01098dbef4040fe6d10b102dd`
with `vllm==0.10.0` and `torch==2.7.1+cu126`, but Torch emitted a hard
compatibility warning: RTX PRO 6000 Blackwell reports CUDA capability
`sm_120`, while that Torch wheel advertises support only through `sm_90`.
Treat this as the current runtime blocker before snapshot pinning or smoke
unless a deliberate tiny smoke is approved as a compatibility probe.
