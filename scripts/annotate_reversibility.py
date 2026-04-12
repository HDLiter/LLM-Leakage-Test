"""Phase D2: post-hoc reversibility annotation via Codex.

Reads ``data/results/diagnostic_2_results.json``, extracts the
``original`` article + the ``semantic_reversal`` (SR) rewrite for each
case (taken from ``tasks.direct_prediction.base.responses``), and asks
Codex to label each pair on a 3-point reversibility scale:

  - high   : both versions read as natural real-world news
             (e.g., "stock rose 5%" <-> "stock fell 5%")
  - medium : counterfactual is grammatical and locally coherent but
             unusual for that entity/event type
  - low    : counterfactual is internally contradictory or inverts
             non-reversible public-record facts

The Codex prompt deliberately does NOT show ``expected_direction`` so
the labeller is not anchored.

This script is non-API: it BUILDS the prompt batches and writes them to
``data/seed/reversibility_prompts/<batch>.json`` for Codex to process.
After Codex returns labels (saved to
``data/seed/reversibility_labels/<batch>.json``), run this script with
``--merge`` to write the labels back into
``data/seed/test_cases_v3.json`` and into the D2 results metadata.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS = ROOT / "data" / "results" / "diagnostic_2_results.json"
DEFAULT_CASES = ROOT / "data" / "seed" / "test_cases_v3.json"
PROMPT_DIR = ROOT / "data" / "seed" / "reversibility_prompts"
LABEL_DIR = ROOT / "data" / "seed" / "reversibility_labels"
BATCH_SIZE = 30


CODEX_SYSTEM = (
    "You are a senior financial-news editor scoring counterfactual rewrite "
    "naturalness. For each (original, rewrite) pair, judge how reversible the "
    "rewrite is. DO NOT use any outside knowledge about the actual outcome -- "
    "score only on textual plausibility.\n\n"
    "Scale:\n"
    "- high   : both versions read as natural real-world news. E.g., flipping "
    "'stock rose 5%' to 'stock fell 5%'. Either version could plausibly happen.\n"
    "- medium : the rewrite is grammatical and locally coherent, but unusual "
    "for that entity/event type. A reader would notice it as odd.\n"
    "- low    : the rewrite is internally contradictory, inverts a "
    "non-reversible public-record fact (e.g., a known disaster), or breaks "
    "physical/legal constraints.\n\n"
    "For each item, return a JSON object with keys: case_id, reversibility, "
    "rationale (one short sentence). Return a JSON array of these objects, "
    "matching the input order."
)


def _build_prompt_batch(items: list[dict[str, Any]]) -> str:
    lines = [
        "Annotate the following items with reversibility ∈ {high, medium, low}.",
        "Return a JSON array; each element MUST have keys case_id, reversibility, rationale.",
        "",
    ]
    for it in items:
        lines.append(f"--- case_id: {it['case_id']} ---")
        lines.append(f"ORIGINAL:\n{it['original']}\n")
        lines.append(f"REWRITTEN (semantic reversal):\n{it['rewritten']}\n")
        lines.append("")
    return "\n".join(lines)


def cmd_build(args: argparse.Namespace) -> int:
    if not args.results.exists():
        print(f"ERROR: results file not found: {args.results}")
        return 1

    raw = json.loads(args.results.read_text(encoding="utf-8"))
    cases = raw.get("cases", [])

    items: list[dict[str, Any]] = []
    skipped = 0
    for cr in cases:
        case_id = cr["case_id"]
        # original article = title + content; reconstruct from the original case
        # but for simplicity we read it from the v3 cases file by id.
        # Read the SR article from the responses' raw_response if available;
        # otherwise we fall back to the cf_payload stored in the case results.
        direct = cr.get("tasks", {}).get("direct_prediction.base", {})
        responses = direct.get("responses", {}) if isinstance(direct, dict) else {}
        sr_resp = responses.get("semantic_reversal", {}) if isinstance(responses, dict) else {}

        if sr_resp.get("skipped") or not sr_resp.get("valid"):
            skipped += 1
            continue

        # Pull the SR article text. The pipeline stores it in cf_payload
        # under key "rewritten_article". The case_result["tasks"][...] structure
        # holds responses (parsed_output) but not the input article. We need to
        # capture it at score time. As a fallback, use the parsed_output as a
        # surrogate (still surfaces the SR semantics, less ideal).
        sr_article = None
        for cond_key in ("sr_direction", "semantic_reversal"):
            cond = cr.get("condition_summary", {}).get(cond_key, {})
            article = cond.get("article")
            if article:
                sr_article = article
                break

        if sr_article is None:
            skipped += 1
            continue

        # Original
        original = (cr.get("news_title") or "") + "\n" + (cr.get("news_content") or "")
        if not original.strip():
            skipped += 1
            continue

        items.append({
            "case_id": case_id,
            "original": original.strip(),
            "rewritten": sr_article.strip(),
        })

    print(f"Eligible items: {len(items)}; skipped: {skipped}")
    if not items:
        print("No eligible items -- check that pipeline_v3 stored sr_direction articles in condition_summary.")
        return 1

    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    n_batches = (len(items) + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(n_batches):
        start = b * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(items))
        batch_items = items[start:end]
        batch_payload = {
            "batch_index": b,
            "n_items": len(batch_items),
            "items": batch_items,
            "system_prompt": CODEX_SYSTEM,
            "user_prompt": _build_prompt_batch(batch_items),
            "built_at": datetime.now().isoformat(),
        }
        out_path = PROMPT_DIR / f"reversibility_batch_{b:02d}.json"
        out_path.write_text(json.dumps(batch_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {n_batches} batches to {PROMPT_DIR}/")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    if not args.cases.exists():
        print(f"ERROR: cases file not found: {args.cases}")
        return 1
    if not LABEL_DIR.exists():
        print(f"ERROR: label directory not found: {LABEL_DIR}")
        return 1

    cases_payload = json.loads(args.cases.read_text(encoding="utf-8"))
    case_list = cases_payload.get("test_cases") or cases_payload.get("cases") or []
    case_index = {c["id"]: c for c in case_list}

    label_files = sorted(LABEL_DIR.glob("reversibility_batch_*.json"))
    print(f"Loading {len(label_files)} label files")

    n_merged = 0
    for fp in label_files:
        labels = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(labels, dict) and "labels" in labels:
            labels = labels["labels"]
        for entry in labels:
            cid = entry.get("case_id")
            rev = entry.get("reversibility")
            rationale = entry.get("rationale", "")
            if cid in case_index and rev in ("high", "medium", "low"):
                case_index[cid]["reversibility"] = rev
                case_index[cid]["reversibility_rationale"] = rationale
                n_merged += 1

    args.cases.write_text(
        json.dumps(cases_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Merged {n_merged} reversibility labels into {args.cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reversibility annotation builder/merger.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="Build prompt batches from D2 results")
    build.add_argument("--results", type=Path, default=DEFAULT_RESULTS)

    merge = sub.add_parser("merge", help="Merge Codex labels back into the cases file")
    merge.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    args = parser.parse_args()
    if args.cmd == "build":
        return cmd_build(args)
    if args.cmd == "merge":
        return cmd_merge(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
