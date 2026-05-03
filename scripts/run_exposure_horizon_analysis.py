"""Path-E analysis: read LogProbTrace Parquet outputs, compute
month-stratified Min-K% per model, and detect the empirical exposure
horizon via piecewise-WLS with case-bootstrap CI.

References:
- `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`
  decision #5 (rename of `cutoff_observed` → `exposure_horizon_observed`,
  2026-04-30) — the analysis output keys and dataclass fields use
  `horizon_observed`/`horizon_ci_*` here.
- Tier-0 #3 in
  `refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md` — the
  piecewise-WLS detector specification.

Run AFTER:
  1. `scripts/build_cutoff_probe_set.py` produces a 2,160-case fixture
     (60 articles/month × 36 months 2023-01..2025-12).
  2. `scripts/ws1_run_logprob.py --exposure-horizon-probe` has been run
     for every white-box model (or some subset).

Output: `data/pilot/exposure_horizon/horizon_observed.json` mapping each
model_id to its detected exposure-horizon date + bootstrap CIs +
acceptance notes. The run manifest cites this file for the
`exposure_horizon_observed` field used by §8.2 mixed-model regressions;
rejected estimates carry `horizon_observed: null` and the model uses
`cutoff_date_yaml` instead.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.analysis.exposure_horizon import (  # noqa: E402
    detect_exposure_horizon,
    month_stratified_mink,
)
from src.r5a.contracts import ArticleRecord  # noqa: E402
from src.r5a.fleet import load_fleet  # noqa: E402
from src.r5a.operators.p_logprob import read_traces_parquet  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Path-E exposure-horizon analysis")
    p.add_argument(
        "--probe-set",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "pilot"
        / "exposure_horizon"
        / "probe_set_monthly60_36mo.json",
        help="JSON fixture used at scoring time (gives publish_date per case)",
    )
    p.add_argument(
        "--traces-dir",
        type=Path,
        default=REPO_ROOT / "data" / "pilot" / "exposure_horizon" / "traces",
        help="directory containing per-model Parquet trace files",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "pilot"
        / "exposure_horizon"
        / "horizon_observed.json",
    )
    p.add_argument(
        "--trace-pattern",
        default="{model}__exposure_horizon.parquet",
        help="filename template; {model} is the substituted model_id",
    )
    p.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="explicit list of model_ids to analyze; defaults to scanning traces-dir",
    )
    p.add_argument(
        "--fleet",
        type=Path,
        default=REPO_ROOT / "config" / "fleet" / "r5a_fleet.yaml",
        help="fleet YAML used to validate that requested models are P_logprob-eligible",
    )
    p.add_argument(
        "--k-pct",
        type=float,
        default=20.0,
        help="Min-K%% percentile",
    )
    p.add_argument(
        "--min-side",
        type=int,
        default=6,
        help="minimum number of months on each side of the breakpoint",
    )
    p.add_argument(
        "--n-bootstrap",
        type=int,
        default=2000,
        help="case-bootstrap replicates for κ̂ / δ̂ CIs",
    )
    p.add_argument(
        "--max-ci-width-months",
        type=int,
        default=3,
        help="reject `horizon_observed` if 95%% CI width exceeds this",
    )
    p.add_argument(
        "--drop-threshold",
        type=float,
        default=0.05,
        help="bootstrap fraction P(δ > this) reported alongside the estimate",
    )
    return p.parse_args()


def _resolve_models(args: argparse.Namespace) -> list[tuple[str, Path]]:
    if args.models:
        out = []
        for m in args.models:
            path = args.traces_dir / args.trace_pattern.format(model=m)
            out.append((m, path))
        return out
    pattern_suffix = args.trace_pattern.format(model="")  # e.g. "__smoke.parquet"
    found = []
    for p in sorted(args.traces_dir.glob(f"*{pattern_suffix}")):
        m = p.name[: -len(pattern_suffix)]
        found.append((m, p))
    return found


def main() -> int:
    args = parse_args()

    fixture = json.loads(args.probe_set.read_text(encoding="utf-8"))
    publish_dates: dict[str, date] = {}
    for row in fixture:
        rec = ArticleRecord(**row)
        publish_dates[rec.case_id] = rec.publish_date

    targets = _resolve_models(args)
    if not targets:
        print("no trace files matched; nothing to do", file=sys.stderr)
        return 1

    fleet = load_fleet(args.fleet)
    eligible = set(fleet.p_logprob_eligible_ids())
    extras = [m for m, _ in targets if m not in eligible]
    if extras:
        raise SystemExit(
            f"requested models not in fleet P_logprob roster: {sorted(extras)}; "
            f"check {args.fleet} models with `p_logprob:` blocks"
        )

    summary: dict[str, dict] = {}
    diagnostics: dict[str, dict] = {}
    trace_shas: dict[str, str] = {}

    for model_id, path in targets:
        if not path.exists():
            print(f"  SKIP {model_id}: {path} not found")
            continue
        trace_shas[model_id] = hashlib.sha256(path.read_bytes()).hexdigest()
        traces = read_traces_parquet(path)
        # Trace coverage assert (MED-1 / Tier-R2-0 PR1 step 13):
        # `month_stratified_mink` silently skips any case_id missing from
        # `publish_dates`; if the trace parquet contains case_ids not in
        # the probe set, the analyzer would silently drop them and the
        # resulting per-month counts would lie about the input. Surface
        # such mismatch loudly so the operator can rebuild the trace
        # against the right probe set.
        trace_case_ids = {t.case_id for t in traces}
        probe_case_ids = set(publish_dates)
        unexpected = sorted(trace_case_ids - probe_case_ids)
        if unexpected:
            raise SystemExit(
                f"trace parquet {path} contains {len(unexpected)} case_id(s) "
                f"not in the probe set {args.probe_set}: "
                f"{unexpected[:5]}{'...' if len(unexpected) > 5 else ''}"
            )
        by_month = month_stratified_mink(
            traces, publish_dates, k_pct=args.k_pct
        )
        est = detect_exposure_horizon(
            by_month,
            model_id=model_id,
            min_side=args.min_side,
            n_bootstrap=args.n_bootstrap,
            drop_threshold=args.drop_threshold,
            max_ci_width_months=args.max_ci_width_months,
        )
        summary[model_id] = {
            "horizon_observed": (
                est.horizon_observed.isoformat() if est.horizon_observed else None
            ),
            "horizon_ci_lower": (
                est.horizon_ci_lower.isoformat() if est.horizon_ci_lower else None
            ),
            "horizon_ci_upper": (
                est.horizon_ci_upper.isoformat() if est.horizon_ci_upper else None
            ),
            "horizon_ci_width_months": est.horizon_ci_width_months,
            "drop_magnitude": est.drop_magnitude,
            "drop_ci_lower": est.drop_ci_lower,
            "drop_ci_upper": est.drop_ci_upper,
            "p_drop_gt_threshold": est.p_drop_gt_005,
            "n_months": est.n_months,
            "n_articles": est.n_articles,
            "kappa_hat_index": est.kappa_hat_index,
            "notes": est.notes,
        }
        diagnostics[model_id] = {
            "monthly_n": {m: len(v) for m, v in sorted(by_month.items())},
        }
        print(
            f"  {model_id}: horizon={summary[model_id]['horizon_observed']} "
            f"drop={est.drop_magnitude:.3f}  ({est.notes})"
        )

    out = {
        "summary": summary,
        "diagnostics": diagnostics,
        "trace_shas": trace_shas,
        "probe_set_sha256": hashlib.sha256(args.probe_set.read_bytes()).hexdigest(),
        "config": {
            "k_pct": args.k_pct,
            "min_side": args.min_side,
            "n_bootstrap": args.n_bootstrap,
            "drop_threshold": args.drop_threshold,
            "max_ci_width_months": args.max_ci_width_months,
            "probe_set": str(args.probe_set),
            "trace_pattern": args.trace_pattern,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
