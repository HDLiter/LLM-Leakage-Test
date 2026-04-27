"""Path-E analysis: read LogProbTrace Parquet outputs, compute
month-stratified Min-K% per model, and detect the empirical cutoff.

Run AFTER:
  1. `scripts/build_cutoff_probe_set.py` produces a 1,440-case fixture
  2. `scripts/ws1_run_logprob.py --smoke --fixture probe_set_1440.json`
     has been run for every white-box model (or some subset)

Output: `data/pilot/cutoff_probe/cutoff_observed.json` mapping each
model_id to its detected cutoff date + drop magnitude + diagnostic
notes. The run manifest cites this file for the `cutoff_observed`
field used by §8.2 mixed-model regressions.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.analysis.cutoff_probe import (  # noqa: E402
    detect_cutoff,
    month_stratified_mink,
)
from src.r5a.contracts import ArticleRecord  # noqa: E402
from src.r5a.operators.p_logprob import read_traces_parquet  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Path-E cutoff probe analysis")
    p.add_argument(
        "--probe-set",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "pilot"
        / "cutoff_probe"
        / "probe_set_1440.json",
        help="JSON fixture used at scoring time (gives publish_date per case)",
    )
    p.add_argument(
        "--traces-dir",
        type=Path,
        default=REPO_ROOT / "data" / "pilot" / "logprob_traces",
        help="directory containing per-model Parquet trace files",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "pilot"
        / "cutoff_probe"
        / "cutoff_observed.json",
    )
    p.add_argument(
        "--trace-pattern",
        default="{model}__smoke.parquet",
        help="filename template; {model} is the substituted model_id",
    )
    p.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="explicit list of model_ids to analyze; defaults to scanning traces-dir",
    )
    p.add_argument(
        "--k-pct",
        type=float,
        default=20.0,
        help="Min-K%% percentile",
    )
    p.add_argument(
        "--smoothing-window",
        type=int,
        default=3,
        help="moving-median smoothing window (months)",
    )
    p.add_argument(
        "--min-drop",
        type=float,
        default=0.05,
        help="reject knees with smaller drop magnitude",
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

    summary: dict[str, dict] = {}
    diagnostics: dict[str, dict] = {}

    for model_id, path in targets:
        if not path.exists():
            print(f"  SKIP {model_id}: {path} not found")
            continue
        traces = read_traces_parquet(path)
        by_month = month_stratified_mink(
            traces, publish_dates, k_pct=args.k_pct
        )
        est = detect_cutoff(
            by_month,
            model_id=model_id,
            smoothing_window=args.smoothing_window,
            min_drop_magnitude=args.min_drop,
        )
        summary[model_id] = {
            "cutoff_observed": (
                est.cutoff_observed.isoformat() if est.cutoff_observed else None
            ),
            "drop_magnitude": est.drop_magnitude,
            "pre_score_mean": est.pre_score_mean,
            "post_score_mean": est.post_score_mean,
            "n_months": est.n_months,
            "knee_index": est.knee_index,
            "notes": est.notes,
        }
        diagnostics[model_id] = {
            "monthly_n": {m: len(v) for m, v in sorted(by_month.items())},
        }
        print(
            f"  {model_id}: cutoff={summary[model_id]['cutoff_observed']} "
            f"drop={est.drop_magnitude:.3f}  ({est.notes})"
        )

    out = {
        "summary": summary,
        "diagnostics": diagnostics,
        "config": {
            "k_pct": args.k_pct,
            "smoothing_window": args.smoothing_window,
            "min_drop": args.min_drop,
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
