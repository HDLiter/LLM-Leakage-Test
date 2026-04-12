"""Audit Bug 1 (changed_spans schema maxLength) by stratum.

Inspects diagnostic_2_results.json. For each case, detects whether each of
the three CF generations (sr_direction, sr_fund_impact, neutral_paraphrase)
failed by reading the per-task `responses[cond].skipped` flag.

Cross-tabs failure counts by `period × anchor_binary` to test the claim
that NP failures are concentrated in strongly_anchored / post_cutoff strata.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"


def detect_failures(case: dict) -> dict[str, bool]:
    """Return {sr_direction, sr_fund_impact, neutral_paraphrase} failed flags."""
    tasks = case.get("tasks", {})
    direct = tasks.get("direct_prediction.base", {})
    impact = tasks.get("decomposed_impact.base", {})

    direct_resp = direct.get("responses", {})
    impact_resp = impact.get("responses", {})

    # sr_direction lives on direct_prediction's semantic_reversal slot
    sr_dir_skipped = bool(direct_resp.get("semantic_reversal", {}).get("skipped"))
    # sr_fund_impact lives on decomposed_impact's semantic_reversal slot
    sr_imp_skipped = bool(impact_resp.get("semantic_reversal", {}).get("skipped"))
    # neutral_paraphrase is shared — check both, prefer either skipped
    np_skipped = bool(
        direct_resp.get("neutral_paraphrase", {}).get("skipped")
        or impact_resp.get("neutral_paraphrase", {}).get("skipped")
    )
    return {
        "sr_direction": sr_dir_skipped,
        "sr_fund_impact": sr_imp_skipped,
        "neutral_paraphrase": np_skipped,
    }


def main() -> None:
    d = json.loads(PATH.read_text(encoding="utf-8"))
    cases = d["cases"]
    print(f"Loaded {len(cases)} cases from {PATH.name}")

    # Per-stratum totals
    cell_totals: Counter[tuple[str, str]] = Counter()
    cell_failures: dict[str, Counter[tuple[str, str]]] = {
        "sr_direction": Counter(),
        "sr_fund_impact": Counter(),
        "neutral_paraphrase": Counter(),
    }

    overall_failures: Counter[str] = Counter()

    # Track cases where sr_direction was eligible (i.e. expected_direction != neutral)
    # All cases here should be eligible since neutrals were dropped (n_filtered_neutral=76)

    for c in cases:
        period = c.get("period") or "unknown"
        anchor = c.get("anchor_binary") or "unknown"
        cell = (period, anchor)
        cell_totals[cell] += 1

        fails = detect_failures(c)
        for cf_type, failed in fails.items():
            if failed:
                cell_failures[cf_type][cell] += 1
                overall_failures[cf_type] += 1

    print()
    print("=== Overall CF generation failure counts (out of 606 cases) ===")
    for cf_type, n in overall_failures.items():
        pct = 100.0 * n / len(cases)
        print(f"  {cf_type:22s} {n:4d} / {len(cases)} ({pct:5.2f}%)")

    print()
    print("=== Stratum totals (period × anchor_binary) ===")
    for cell, n in sorted(cell_totals.items()):
        print(f"  {cell[0]:12s} / {cell[1]:18s} : {n}")

    print()
    print("=== CF failure rate by stratum (period × anchor_binary) ===")
    print(f"{'period':12s} {'anchor':18s} {'n':>5s}  "
          f"{'sr_dir':>12s} {'sr_imp':>12s} {'np':>12s}")
    for cell in sorted(cell_totals):
        n = cell_totals[cell]
        row = []
        for cf_type in ("sr_direction", "sr_fund_impact", "neutral_paraphrase"):
            f = cell_failures[cf_type][cell]
            pct = 100.0 * f / n if n else 0.0
            row.append(f"{f:3d}/{n:3d}={pct:4.1f}%")
        print(f"{cell[0]:12s} {cell[1]:18s} {n:5d}  {row[0]:>12s} {row[1]:>12s} {row[2]:>12s}")

    # Marginal: post_cutoff vs pre_cutoff and strongly vs weakly anchored
    print()
    print("=== Marginal failure rate by period ===")
    for period in ("pre_cutoff", "post_cutoff"):
        total = sum(n for (p, _), n in cell_totals.items() if p == period)
        for cf_type in ("sr_direction", "sr_fund_impact", "neutral_paraphrase"):
            f = sum(v for (p, _), v in cell_failures[cf_type].items() if p == period)
            pct = 100.0 * f / total if total else 0.0
            print(f"  {period:12s} {cf_type:22s} {f:3d}/{total:3d} ({pct:5.2f}%)")
        print()

    print("=== Marginal failure rate by anchor_binary ===")
    for anchor in ("weakly_anchored", "strongly_anchored"):
        total = sum(n for (_, a), n in cell_totals.items() if a == anchor)
        for cf_type in ("sr_direction", "sr_fund_impact", "neutral_paraphrase"):
            f = sum(v for (_, a), v in cell_failures[cf_type].items() if a == anchor)
            pct = 100.0 * f / total if total else 0.0
            print(f"  {anchor:18s} {cf_type:22s} {f:3d}/{total:3d} ({pct:5.2f}%)")
        print()

    # Save machine-readable summary
    out_path = ROOT / "data" / "results" / "_audit_bug1_summary.json"
    summary = {
        "n_cases": len(cases),
        "overall_failures": dict(overall_failures),
        "cell_totals": {f"{c[0]}/{c[1]}": n for c, n in cell_totals.items()},
        "cell_failures": {
            cf: {f"{c[0]}/{c[1]}": v for c, v in counter.items()}
            for cf, counter in cell_failures.items()
        },
    }
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved machine-readable summary to {out_path.name}")


if __name__ == "__main__":
    main()
