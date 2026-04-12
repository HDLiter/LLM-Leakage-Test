"""Audit Bug 3 (_detect_fo_flip neutral handling) by rescoring from cache.

For each case, reads the cached parsed_output of original and false_outcome_cpt
for both direct_prediction.base and decomposed_impact.base. Counts:

  - current `fo_flip_direct/impact` (strict semantics: only opposite-polarity flips)
  - hedged retreats: ORIG non-neutral, FO neutral (currently scored as no-flip)
  - hypothetical "strict OR hedged" count

Stratifies by period × anchor_binary so we can see whether the headline MH OR
would invert under the hedged definition.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"

PILOT_TASKS = ["direct_prediction.base", "decomposed_impact.base"]
TASK_TO_FIELD = {
    "direct_prediction.base": "direction",
    "decomposed_impact.base": "fund_impact",
}
TASK_TO_METRIC = {
    "direct_prediction.base": "fo_flip_direct",
    "decomposed_impact.base": "fo_flip_impact",
}

_POS = {"up", "positive", "strong_positive"}
_NEG = {"down", "negative", "strong_negative"}
_NEUTRAL = {"neutral"}


def _norm(label) -> str:
    if label is None:
        return ""
    if hasattr(label, "value"):
        label = label.value
    if isinstance(label, str):
        return label.strip().lower()
    return str(label).strip().lower()


def _polarity(label: str) -> str:
    """pos / neg / neutral / unknown"""
    if label in _POS:
        return "pos"
    if label in _NEG:
        return "neg"
    if label in _NEUTRAL:
        return "neutral"
    return "unknown"


def classify(orig_val: str, fo_val: str, expected_direction: str) -> str:
    """Return one of: 'strict_flip', 'hedged_flip', 'no_flip', 'undefined'."""
    if not orig_val or not fo_val:
        return "undefined"
    if orig_val == fo_val:
        return "no_flip"

    exp_pol = _polarity(expected_direction)
    fo_pol = _polarity(fo_val)
    orig_pol = _polarity(orig_val)

    # Strict: model crossed to the polarity opposite of expected_direction (i.e.
    # toward the planted false outcome). Mirrors the logic in _detect_fo_flip.
    if exp_pol == "pos" and fo_pol == "neg":
        return "strict_flip"
    if exp_pol == "neg" and fo_pol == "pos":
        return "strict_flip"

    # Hedged: ORIG was non-neutral, FO is neutral. Model didn't fully cross,
    # but it retreated from its original stance under the false-outcome plant.
    if orig_pol in ("pos", "neg") and fo_pol == "neutral":
        return "hedged_flip"

    return "no_flip"


def get_label(parsed: dict | None, task_id: str) -> str:
    if not isinstance(parsed, dict):
        return ""
    field = TASK_TO_FIELD[task_id]
    return _norm(parsed.get(field))


def main() -> None:
    d = json.loads(PATH.read_text(encoding="utf-8"))
    cases = d["cases"]
    print(f"Loaded {len(cases)} cases")

    # cell -> {strict, hedged, undef, no_flip} count, per task
    cells: dict[str, dict[tuple[str, str], Counter]] = {
        t: {} for t in PILOT_TASKS
    }
    overall: dict[str, Counter] = {t: Counter() for t in PILOT_TASKS}

    # Cross-check vs the cached metrics field
    cross_check_match = {t: 0 for t in PILOT_TASKS}
    cross_check_mismatch = {t: 0 for t in PILOT_TASKS}

    for c in cases:
        period = c.get("period") or "unknown"
        anchor = c.get("anchor_binary") or "unknown"
        cell = (period, anchor)
        expected = _norm(c.get("expected_direction"))
        metrics = c.get("metrics", {})
        tasks = c.get("tasks", {})

        for task_id in PILOT_TASKS:
            t = tasks.get(task_id, {})
            responses = t.get("responses", {})
            orig_resp = responses.get("original", {})
            fo_resp = responses.get("false_outcome_cpt", {})

            if not orig_resp.get("valid") or not fo_resp.get("valid"):
                if cell not in cells[task_id]:
                    cells[task_id][cell] = Counter()
                cells[task_id][cell]["undefined"] += 1
                overall[task_id]["undefined"] += 1
                continue

            orig_label = get_label(orig_resp.get("parsed_output"), task_id)
            fo_label = get_label(fo_resp.get("parsed_output"), task_id)

            cls = classify(orig_label, fo_label, expected)

            if cell not in cells[task_id]:
                cells[task_id][cell] = Counter()
            cells[task_id][cell][cls] += 1
            overall[task_id][cls] += 1

            # Cross-check vs cached metric
            cached = metrics.get(TASK_TO_METRIC[task_id])
            cached_strict_bool = cls == "strict_flip"
            if cached is None:
                pass  # cached not computable; skip
            elif bool(cached) == cached_strict_bool:
                cross_check_match[task_id] += 1
            else:
                cross_check_mismatch[task_id] += 1

    for task_id in PILOT_TASKS:
        print()
        print(f"=== {task_id} ===")
        oc = overall[task_id]
        print(f"  strict_flip : {oc['strict_flip']}")
        print(f"  hedged_flip : {oc['hedged_flip']}")
        print(f"  no_flip     : {oc['no_flip']}")
        print(f"  undefined   : {oc['undefined']}")
        print(f"  union (strict ∪ hedged): {oc['strict_flip'] + oc['hedged_flip']}")
        print(f"  cross-check vs cached metric: match={cross_check_match[task_id]}, "
              f"mismatch={cross_check_mismatch[task_id]}")

        print()
        print(f"  By period × anchor_binary:")
        print(f"  {'period':12s} {'anchor':18s} {'n':>4s} {'strict':>7s} {'hedged':>7s} "
              f"{'union':>6s} {'undef':>6s}")
        for cell in sorted(cells[task_id]):
            counter = cells[task_id][cell]
            n_total = sum(counter.values())
            strict = counter["strict_flip"]
            hedged = counter["hedged_flip"]
            undef = counter["undefined"]
            print(f"  {cell[0]:12s} {cell[1]:18s} {n_total:4d} {strict:7d} {hedged:7d} "
                  f"{strict + hedged:6d} {undef:6d}")

    # Save machine-readable summary
    out = {
        "overall": {t: dict(c) for t, c in overall.items()},
        "by_cell": {
            t: {f"{c[0]}/{c[1]}": dict(counter) for c, counter in cells[t].items()}
            for t in PILOT_TASKS
        },
        "cross_check": {
            "match": cross_check_match,
            "mismatch": cross_check_mismatch,
        },
    }
    out_path = ROOT / "data" / "results" / "_audit_bug3_summary.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
