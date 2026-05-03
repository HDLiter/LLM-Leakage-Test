"""WS1 CLI: run `P_logprob` for one white-box model and persist traces.

Per-model invocation pattern (smoke):

    python scripts/ws1_run_logprob.py \
        --model qwen2.5-7b \
        --smoke \
        --vllm-url http://localhost:8000 \
        --output-dir data/pilot/logprob_traces

Per-model invocation pattern (pilot, after WS4 builds the manifest):

    python scripts/ws1_run_logprob.py \
        --model qwen2.5-7b \
        --pilot \
        --pilot-articles data/pilot/manifests/pilot_100_articles.json \
        --vllm-url http://localhost:8000 \
        --output-dir data/pilot/logprob_traces

Per-model invocation pattern (Path E empirical exposure-horizon probe;
per `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`
decision #5 — Path E no longer rides the `--smoke` flag, has its own
output directory `data/pilot/exposure_horizon/traces/` and demands the
2,160-case probe fixture):

    python scripts/ws1_run_logprob.py \
        --model qwen2.5-7b \
        --exposure-horizon-probe \
        --vllm-url http://localhost:8000

For the GLM fallback path (vLLM `echo=True` unsupported), pass
`--backend offline_hf --model-path /data/models/glm-4-9b`. By default
the backend is selected from `config/fleet/r5a_fleet.yaml`'s
`p_logprob.echo_supported` and `p_logprob.fallback` fields.

Plan refs:
- §5.2 step 6 (operator + persistence)
- §5.2 step 7 (smoke gate)
- §10.2 (no proxy / trust_env false)
- §14.3 (CLI shape)
- docs/DECISION_20260427_pcsg_redefinition.md (fleet expansion +
  trace contract additions + chunked-write resume).
- docs/DECISION_20260429_llama_addition.md (P_logprob-only models;
  Llama-3 / 3.1 added with vendor-stated cutoffs).
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.contracts import AccessTier, ArticleRecord  # noqa: E402
from src.r5a.fleet import ModelConfig, load_fleet  # noqa: E402
from src.r5a.operators.p_logprob import (  # noqa: E402
    PLogprobOperator,
    append_chunk_parquet,
    consolidate_chunks,
    existing_case_ids,
    trace_summary,
    write_summary_json,
)
from src.r5a.runtime import load_runtime  # noqa: E402

DEFAULT_CHUNK_SIZE = 10  # write a chunk every N successful traces
DEFAULT_HIDDEN_STATES_SUBSAMPLE = 30  # for WS6 prep on offline_hf paths


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WS1 P_logprob runner (one model)")
    p.add_argument("--model", required=True, help="fleet model_id (white-box)")
    p.add_argument(
        "--fleet", default="config/fleet/r5a_fleet.yaml", help="fleet YAML path"
    )
    p.add_argument(
        "--runtime",
        default="config/runtime/r5a_runtime.yaml",
        help="runtime YAML path",
    )
    p.add_argument(
        "--backend",
        choices=["vllm", "offline_hf", "auto"],
        default="auto",
        help="backend implementation; 'auto' resolves from fleet config",
    )
    p.add_argument("--vllm-url", default="http://localhost:8000", help="vLLM base URL")
    p.add_argument(
        "--served-model-name",
        default=None,
        help="vLLM --served-model-name; defaults to fleet model_id",
    )
    p.add_argument(
        "--vllm-image-digest",
        default=None,
        help=(
            "Docker image digest for the running vLLM container, "
            "sha256:<64-hex>; recorded into trace"
        ),
    )
    p.add_argument(
        "--model-path",
        default=None,
        help="local HF checkpoint path (offline_hf backend only)",
    )
    p.add_argument(
        "--device",
        default="cuda",
        help="device for offline_hf backend (cuda/cpu)",
    )
    p.add_argument(
        "--torch-dtype",
        default="float16",
        help="dtype for offline_hf backend (float16/bfloat16/float32)",
    )
    p.add_argument(
        "--extract-hidden-states",
        action="store_true",
        help="WS6 prep: capture per-layer hidden states (offline_hf only)",
    )
    p.add_argument(
        "--hidden-states-dir",
        default=None,
        help="output directory for .safetensors hidden-state files",
    )

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--smoke",
        action="store_true",
        help="use the 30-case smoke fixture",
    )
    g.add_argument(
        "--pilot",
        action="store_true",
        help="use a frozen pilot manifest (WS4)",
    )
    g.add_argument(
        "--exposure-horizon-probe",
        action="store_true",
        help=(
            "run Path E empirical exposure-horizon probe on the 2,160-case "
            "monthly-stratified fixture; writes to a distinct output "
            "directory so Path E artifacts are never confused with "
            "smoke traces (DECISIONS.md decision #5)."
        ),
    )

    p.add_argument(
        "--fixture",
        default="data/pilot/fixtures/smoke_30.json",
        help="JSON fixture for --smoke",
    )
    p.add_argument(
        "--pilot-articles",
        default="data/pilot/manifests/pilot_100_articles.json",
        help="JSON of ArticleRecord-shaped rows for --pilot",
    )
    p.add_argument(
        "--exposure-horizon-fixture",
        default="data/pilot/exposure_horizon/probe_set_monthly60_36mo.json",
        help="JSON of ArticleRecord-shaped rows for --exposure-horizon-probe",
    )
    p.add_argument(
        "--output-dir",
        default="data/pilot/logprob_traces",
        help="parquet output directory (overridden under --exposure-horizon-probe)",
    )
    p.add_argument(
        "--exposure-horizon-output-dir",
        default="data/pilot/exposure_horizon/traces",
        help="parquet output directory for --exposure-horizon-probe runs",
    )
    p.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="write a chunk every N successful traces (resume granularity)",
    )
    p.add_argument(
        "--max-concurrency",
        type=int,
        default=None,
        help="overrides runtime.providers.vllm.max_concurrency",
    )
    p.add_argument(
        "--no-resume",
        action="store_true",
        help="ignore existing chunks and re-run all cases",
    )
    return p.parse_args()


def _resolve_white_box(model_id: str, fleet_path: str) -> ModelConfig:
    fleet = load_fleet(fleet_path)
    cfg = fleet.get(model_id)
    if cfg.access is not AccessTier.WHITE_BOX:
        raise SystemExit(
            f"P_logprob runs on white-box only; {model_id} is "
            f"{cfg.access.value}. WS2 handles black-box models."
        )
    return cfg


_VLLM_IMAGE_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _check_pinning_for_pilot(cfg: ModelConfig, args: argparse.Namespace) -> None:
    """Refuse `--pilot` or `--exposure-horizon-probe` if any provenance
    field is still `<TBD>` or required Docker digest is missing.

    Smoke runs are allowed against a partially-pinned fleet so we can
    iterate locally; pilot AND Path E artifacts both feed the
    RunManifest (Operational §6 / Tier-0 #4) and MUST be reproducible
    so tighter checks apply (plan §10.1; SYNTHESIS Tier-0 #2 + R2-U3 +
    R2-U4).
    """
    requires_pinning = bool(
        getattr(args, "pilot", False) or getattr(args, "exposure_horizon_probe", False)
    )
    if not requires_pinning:
        return
    mode_label = "--pilot" if args.pilot else "--exposure-horizon-probe"
    placeholders = "<TBD>"
    bad: list[str] = []
    if cfg.tokenizer_sha is None or cfg.tokenizer_sha == placeholders:
        bad.append("tokenizer_sha")
    if cfg.hf_commit_sha is None or cfg.hf_commit_sha == placeholders:
        bad.append("hf_commit_sha")
    if cfg.tokenizer_family is None or cfg.tokenizer_family == placeholders:
        bad.append("tokenizer_family")
    if cfg.quant_scheme is None or cfg.quant_scheme == placeholders:
        bad.append("quant_scheme")
    if bad:
        raise SystemExit(
            f"{mode_label} refused: {cfg.model_id} fleet entry still has "
            f"placeholder values for: {', '.join(bad)}. Run "
            "scripts/ws1_pin_fleet.py to write back HF / tokenizer SHAs "
            "before this mode."
        )
    if not args.vllm_image_digest or not _VLLM_IMAGE_DIGEST_RE.match(
        args.vllm_image_digest
    ):
        raise SystemExit(
            f"{mode_label} refused: --vllm-image-digest must match "
            "sha256:<64-hex>. Inspect with "
            "`docker image inspect <vllm_image> --format '{{.Id}}'` and "
            f"pass the resulting sha256:... value (got "
            f"{args.vllm_image_digest!r})."
        )


def _decide_backend(args: argparse.Namespace, cfg: ModelConfig) -> str:
    """Resolve auto/vllm/offline_hf based on fleet `p_logprob` flags."""
    if args.backend != "auto":
        return args.backend
    if cfg.p_logprob is None:
        raise SystemExit(
            f"{cfg.model_id} has no p_logprob block in the fleet config; "
            f"cannot auto-resolve backend"
        )
    if cfg.p_logprob.echo_supported:
        return "vllm"
    if cfg.p_logprob.fallback == "offline_hf_scorer":
        return "offline_hf"
    raise SystemExit(
        f"{cfg.model_id} echo_supported=False and no offline_hf fallback "
        f"configured; cannot decide backend"
    )


def _load_articles(args: argparse.Namespace) -> list[ArticleRecord]:
    if args.smoke:
        path = Path(args.fixture)
    elif args.exposure_horizon_probe:
        path = Path(args.exposure_horizon_fixture)
    else:
        path = Path(args.pilot_articles)
    if not path.exists():
        raise SystemExit(f"article source not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(
            f"{path} must be a JSON array of ArticleRecord-shaped objects"
        )
    return [ArticleRecord(**row) for row in payload]


def _resolve_output_paths(args: argparse.Namespace, model_id: str) -> tuple[Path, Path, Path, str]:
    """Return (chunks_dir, final_path, summary_path, mode_tag) per run mode.

    Path E uses a distinct directory tree per DECISIONS.md decision #5
    so exposure-horizon-probe artifacts are never confused with smoke
    traces. The output filename suffix `__exposure_horizon.parquet`
    must match the default `--trace-pattern` of
    `scripts/run_exposure_horizon_analysis.py`.
    """
    if args.exposure_horizon_probe:
        out_dir = Path(args.exposure_horizon_output_dir)
        mode_tag = "exposure_horizon"
    else:
        out_dir = Path(args.output_dir)
        mode_tag = "smoke" if args.smoke else "pilot"
    chunks_dir = out_dir / f"{model_id}__{mode_tag}__chunks"
    final_path = out_dir / f"{model_id}__{mode_tag}.parquet"
    summary_path = out_dir / f"{model_id}__{mode_tag}.summary.json"
    return chunks_dir, final_path, summary_path, mode_tag


def _build_backend(args: argparse.Namespace, cfg: ModelConfig, runtime, backend_kind: str):
    timeout_s = runtime.runtime.timeout_seconds
    retry_max = runtime.runtime.retry_max

    if backend_kind == "vllm":
        for var in ("NO_PROXY", "no_proxy"):
            cur = os.environ.get(var, "")
            host_part = "localhost,127.0.0.1,host.docker.internal"
            if host_part not in cur:
                os.environ[var] = (cur + "," if cur else "") + host_part

        from src.r5a.backends.vllm_logprob import VLLMLogprobBackend

        return VLLMLogprobBackend(
            base_url=args.vllm_url,
            served_model_name=args.served_model_name or cfg.model_id,
            model_id=cfg.model_id,
            tokenizer_family=cfg.tokenizer_family or "",
            tokenizer_sha=cfg.tokenizer_sha or "",
            hf_commit_sha=cfg.hf_commit_sha or "",
            quant_scheme=cfg.quant_scheme or "fp16",
            weight_dtype=None,
            vllm_image_digest=args.vllm_image_digest,
            timeout_seconds=timeout_s,
            max_retries=retry_max,
        )

    if not args.model_path:
        raise SystemExit("--backend offline_hf requires --model-path")
    from src.r5a.backends.offline_hf import OfflineHFBackend

    return OfflineHFBackend(
        model_path=args.model_path,
        model_id=cfg.model_id,
        tokenizer_family=cfg.tokenizer_family or "",
        tokenizer_sha=cfg.tokenizer_sha or "",
        hf_commit_sha=cfg.hf_commit_sha or "",
        quant_scheme=cfg.quant_scheme or "fp16",
        weight_dtype=args.torch_dtype,
        device=args.device,
        torch_dtype=args.torch_dtype,
        extract_hidden_states=args.extract_hidden_states,
        hidden_states_dir=args.hidden_states_dir,
    )


async def run(args: argparse.Namespace) -> int:
    cfg = _resolve_white_box(args.model, args.fleet)
    _check_pinning_for_pilot(cfg, args)
    runtime = load_runtime(args.runtime)
    if args.max_concurrency is not None:
        max_conc = args.max_concurrency
    else:
        max_conc = runtime.provider("vllm").max_concurrency

    articles_all = _load_articles(args)
    backend_kind = _decide_backend(args, cfg)

    chunks_dir, final_path, summary_path, mode_tag = _resolve_output_paths(
        args, cfg.model_id
    )

    if args.no_resume:
        already_done: set[str] = set()
    else:
        already_done = existing_case_ids(chunks_dir)

    todo = [a for a in articles_all if a.case_id not in already_done]
    skipped = len(articles_all) - len(todo)
    print(
        f"model={cfg.model_id} backend={backend_kind} mode={mode_tag} "
        f"n_articles={len(articles_all)} resumed_done={skipped} "
        f"to_run={len(todo)} max_concurrency={max_conc} "
        f"chunk_size={args.chunk_size}"
    )

    if not todo:
        print("nothing to do; all cases already in chunks. Consolidating.")
        if (chunks_dir).exists():
            consolidate_chunks(chunks_dir, final_path)
            print(f"wrote consolidated {final_path}")
        return 0

    backend = _build_backend(args, cfg, runtime, backend_kind)
    operator = PLogprobOperator(backend, max_concurrency=max_conc)

    started = datetime.now(timezone.utc)
    n_done_total = skipped
    pending: list = []

    def _progress(done: int, total: int) -> None:
        # done is per-batch local; n_done_total is global
        print(f"  batch [{done}/{total}]  global={n_done_total + done}", end="\r", flush=True)

    try:
        # Process in chunks so a crash mid-pilot only loses the in-flight batch.
        chunk_size = max(1, args.chunk_size)
        for start in range(0, len(todo), chunk_size):
            batch = todo[start : start + chunk_size]
            traces = await operator.compute(batch, progress=_progress)
            print()
            if traces:
                path = append_chunk_parquet(traces, chunks_dir)
                n_done_total += len(traces)
                print(
                    f"chunk written: {path.name}  "
                    f"({len(traces)} traces, global={n_done_total}/{len(articles_all)})"
                )
                pending.extend(traces)
    finally:
        for closer in ("aclose", "close"):
            fn = getattr(backend, closer, None)
            if fn is None:
                continue
            try:
                if inspect.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
            except Exception as exc:  # pragma: no cover  (cleanup-best-effort)
                print(f"backend {closer}() raised {exc!r}", file=sys.stderr)

    # Consolidate all chunks into a single Parquet for downstream readers.
    if (chunks_dir).exists():
        consolidate_chunks(chunks_dir, final_path)
        print(f"consolidated -> {final_path}")

    summary = trace_summary(pending)
    summary["mode"] = mode_tag
    summary["started_at"] = started.isoformat()
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    summary["resumed_done"] = skipped
    summary["written_this_run"] = len(pending)
    write_summary_json(summary, summary_path)
    print(f"summary -> {summary_path}")
    return 0


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
