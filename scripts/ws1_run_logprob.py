"""WS1 CLI: run `P_logprob` for one white-box model and persist traces.

Per-model invocation pattern (smoke):

    python scripts/ws1_run_logprob.py \
        --model qwen2.5-7b \
        --smoke \
        --vllm-url http://localhost:8000 \
        --output-dir data/pilot/logprob_traces

For the GLM fallback path (vLLM `echo=True` unsupported), pass
`--backend offline_hf --model-path /data/models/glm-4-9b`.

Plan refs: §5.2 step 6 (operator + persistence), §10.2 (no proxy /
trust_env false), §14.3 (CLI shape).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
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
    trace_summary,
    write_summary_json,
    write_traces_parquet,
)
from src.r5a.runtime import load_runtime  # noqa: E402


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
        choices=["vllm", "offline_hf"],
        default="vllm",
        help="backend implementation",
    )
    p.add_argument("--vllm-url", default="http://localhost:8000", help="vLLM base URL")
    p.add_argument(
        "--served-model-name",
        default=None,
        help="vLLM --served-model-name; defaults to fleet model_id",
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

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--smoke",
        action="store_true",
        help="use the 30-case smoke fixture",
    )
    g.add_argument(
        "--pilot",
        action="store_true",
        help="use the frozen pilot manifest (WS4)",
    )

    p.add_argument(
        "--fixture",
        default="data/pilot/fixtures/smoke_30.json",
        help="JSON fixture for --smoke",
    )
    p.add_argument(
        "--manifest",
        default="data/pilot/manifests/pilot_100_cases.json",
        help="pilot manifest for --pilot",
    )
    p.add_argument(
        "--output-dir",
        default="data/pilot/logprob_traces",
        help="parquet output directory",
    )
    p.add_argument(
        "--max-concurrency",
        type=int,
        default=None,
        help="overrides runtime.providers.vllm.max_concurrency",
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
    if cfg.tokenizer_sha == "<TBD>" or cfg.hf_commit_sha == "<TBD>":
        print(
            f"WARNING: {model_id} has unpinned tokenizer_sha or "
            f"hf_commit_sha; smoke runs are allowed but the pilot "
            f"manifest must record real SHAs (plan §10.1).",
            file=sys.stderr,
        )
    return cfg


def _load_articles(args: argparse.Namespace) -> list[ArticleRecord]:
    if args.smoke:
        path = Path(args.fixture)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [ArticleRecord(**row) for row in payload]
    # --pilot: load the WS4 manifest. WS4 hasn't built it yet, so
    # this branch will fail until then; keep the surface ready.
    path = Path(args.manifest)
    if not path.exists():
        raise SystemExit(
            f"pilot manifest not found at {path}; "
            f"WS4 builds it via scripts/sample_phase7_pilot.py"
        )
    raise SystemExit(
        "--pilot mode requires loading PilotManifest -> ArticleRecord, "
        "which depends on the WS4 sampler. Run --smoke for now."
    )


def _build_backend(args: argparse.Namespace, cfg: ModelConfig):
    if args.backend == "vllm":
        # Force NO_PROXY / no_proxy for the vLLM URL; project memory
        # `feedback_concurrency.md` records that the host proxy
        # otherwise breaks localhost vLLM connectivity.
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
        )

    # offline_hf
    if not args.model_path:
        raise SystemExit("--backend offline_hf requires --model-path")
    from src.r5a.backends.offline_hf import OfflineHFBackend

    return OfflineHFBackend(
        model_path=args.model_path,
        model_id=cfg.model_id,
        tokenizer_family=cfg.tokenizer_family or "",
        tokenizer_sha=cfg.tokenizer_sha or "",
        hf_commit_sha=cfg.hf_commit_sha or "",
        device=args.device,
        torch_dtype=args.torch_dtype,
    )


async def run(args: argparse.Namespace) -> int:
    cfg = _resolve_white_box(args.model, args.fleet)
    runtime = load_runtime(args.runtime)
    if args.max_concurrency is not None:
        max_conc = args.max_concurrency
    else:
        provider = "vllm" if args.backend == "vllm" else "vllm"
        max_conc = runtime.provider(provider).max_concurrency

    articles = _load_articles(args)
    print(
        f"model={cfg.model_id} backend={args.backend} "
        f"n_articles={len(articles)} max_concurrency={max_conc}"
    )

    backend = _build_backend(args, cfg)

    operator = PLogprobOperator(backend, max_concurrency=max_conc)

    def _progress(done: int, total: int) -> None:
        print(f"  [{done}/{total}]", end="\r", flush=True)

    started = datetime.now(timezone.utc)
    try:
        traces = await operator.compute(articles, progress=_progress)
    finally:
        # vLLM backend exposes async close; HF backend has none
        close = getattr(backend, "aclose", None)
        if close is not None:
            await close()
    print()

    out_dir = Path(args.output_dir)
    mode_tag = "smoke" if args.smoke else "pilot"
    parquet_path = out_dir / f"{cfg.model_id}__{mode_tag}.parquet"
    summary_path = out_dir / f"{cfg.model_id}__{mode_tag}.summary.json"

    write_traces_parquet(traces, parquet_path)
    summary = trace_summary(traces)
    summary["mode"] = mode_tag
    summary["started_at"] = started.isoformat()
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_summary_json(summary, summary_path)

    print(f"wrote {parquet_path}")
    print(f"wrote {summary_path}")
    print(json.dumps(summary, indent=2, default=str))
    return 0


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
