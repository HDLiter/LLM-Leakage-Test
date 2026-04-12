"""Phase B2: Codex annotation orchestration for v3 candidates.

Codex MCP is callable from Claude Code, NOT from a Python script.
So this script is two-mode:

  1. ``build``  : load expansion_candidates_v3.json + the existing 192
                  cases, split into batches of 40, embed the rubric verbatim,
                  and write per-batch prompt files. The driving CC agent
                  then calls Codex MCP once per batch and saves the output.
  2. ``merge``  : after all batches are annotated by Codex, merge them
                  into ``data/seed/test_cases_v3.json`` (full v3 dataset).

The output schema injected into Codex's system prompt is:

    [
      {
        "candidate_id": "v3_h_001",
        "anchor_level": 0|1|2|3,
        "anchor_cues": ["..."],
        "anchor_rationale": "one short sentence",
        "key_entities": ["..."],
        "key_numbers": ["..."],
        "expected_direction": "up"|"down"|"neutral",
        "subcategory": "...",
        "target": "...",
        "target_type": "company"|"sector"|"index",
        "category": "macro"|"corporate"|"policy"|"industry",
        "rubric_version": "1.0"
      },
      ...
    ]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUBRIC_PATH = ROOT / "docs" / "ANCHOR_RUBRIC.md"
CANDIDATES_PATH = ROOT / "data" / "seed" / "expansion_candidates_v3.json"
EXISTING_CASES_PATH = ROOT / "data" / "seed" / "test_cases_expanded.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "test_cases_v3.json"
PROMPT_DIR = ROOT / "data" / "seed" / "v3_annotation_prompts"
LABEL_DIR = ROOT / "data" / "seed" / "v3_annotation_labels"
DOUBLE_PROMPT_DIR = ROOT / "data" / "seed" / "v3_annotation_double"

BATCH_SIZE = 40
DOUBLE_ANNOTATION_N = 50


def _load_rubric() -> str:
    if not RUBRIC_PATH.exists():
        raise SystemExit(f"Rubric not found at {RUBRIC_PATH}")
    return RUBRIC_PATH.read_text(encoding="utf-8")


def _system_prompt(rubric: str) -> str:
    return (
        "You are an expert Chinese-financial-news annotator. Annotate each item "
        "according to the embedded rubric. The rubric is the SINGLE SOURCE OF "
        "TRUTH; do not infer beyond what is explicitly defined.\n\n"
        "==== EMBEDDED RUBRIC (verbatim, do not modify) ====\n"
        f"{rubric}\n"
        "==== END RUBRIC ====\n\n"
        "Output a JSON array. Each element MUST have these keys:\n"
        "  candidate_id (string), anchor_level (int 0-3), anchor_cues (list[string]),\n"
        "  anchor_rationale (one short sentence in English),\n"
        "  key_entities (list[string]), key_numbers (list[string]),\n"
        "  expected_direction ('up'|'down'|'neutral'),\n"
        "  subcategory (string), target (string),\n"
        "  target_type ('company'|'sector'|'index'),\n"
        "  category ('macro'|'corporate'|'policy'|'industry'),\n"
        "  rubric_version ('1.0')\n\n"
        "Apply the decision tree mechanically. Return ONLY the JSON array, "
        "no surrounding prose."
    )


def _user_prompt(items: list[dict[str, Any]]) -> str:
    lines = ["Annotate the following candidates. Return a JSON array of length N=" + str(len(items)) + ".\n"]
    for i, it in enumerate(items, 1):
        cid = it.get("candidate_id") or it.get("id", f"item_{i}")
        title = it.get("title", "") or (it.get("news") or {}).get("title", "")
        content = it.get("content", "") or (it.get("news") or {}).get("content", "")
        publish_time = it.get("publish_time", "") or (it.get("news") or {}).get("publish_time", "")
        period = it.get("period", "")
        funnel = it.get("funnel", "")
        lines.append(f"--- candidate_id: {cid} ---")
        lines.append(f"period: {period}  funnel: {funnel}  publish_time: {publish_time}")
        lines.append(f"title: {title}")
        lines.append(f"content: {content}")
        lines.append("")
    return "\n".join(lines)


def _normalize_existing(case: dict[str, Any]) -> dict[str, Any]:
    """Normalize an existing case (test_cases_expanded.json) into a candidate-shaped record."""
    news = case.get("news", {}) if isinstance(case.get("news"), dict) else {}
    return {
        "candidate_id": case.get("id"),
        "title": news.get("title", ""),
        "content": news.get("content", ""),
        "publish_time": news.get("publish_time", ""),
        "period": case.get("period", ""),
        "funnel": "existing_192",
    }


def cmd_build(args: argparse.Namespace) -> int:
    rubric = _load_rubric()

    # Load v3 candidates
    if not CANDIDATES_PATH.exists():
        print(f"ERROR: candidates file not found: {CANDIDATES_PATH}")
        return 1
    cand_payload = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    candidates = cand_payload.get("candidates", [])
    print(f"Loaded {len(candidates)} v3 candidates from {CANDIDATES_PATH}")

    # Load + normalize existing 192 cases
    if not EXISTING_CASES_PATH.exists():
        print(f"ERROR: existing cases not found: {EXISTING_CASES_PATH}")
        return 1
    existing_payload = json.loads(EXISTING_CASES_PATH.read_text(encoding="utf-8-sig"))
    existing = existing_payload.get("test_cases", [])
    existing_normalized = [_normalize_existing(c) for c in existing]
    print(f"Loaded {len(existing)} existing cases (will be re-annotated)")

    all_items = candidates + existing_normalized
    print(f"Total items to annotate: {len(all_items)}")

    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    n_batches = (len(all_items) + BATCH_SIZE - 1) // BATCH_SIZE
    sys_prompt = _system_prompt(rubric)
    for b in range(n_batches):
        start = b * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(all_items))
        batch_items = all_items[start:end]
        out = {
            "batch_index": b,
            "n_items": len(batch_items),
            "items": batch_items,
            "system_prompt": sys_prompt,
            "user_prompt": _user_prompt(batch_items),
            "built_at": datetime.now().isoformat(),
            "rubric_version": "1.0",
        }
        out_path = PROMPT_DIR / f"v3_annotation_batch_{b:02d}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {n_batches} prompt batches to {PROMPT_DIR}/")

    # Also build the double-annotation pool: random 50-case sample.
    import random
    rng = random.Random(2027)  # different seed than calibration
    double_sample = rng.sample(all_items, min(DOUBLE_ANNOTATION_N, len(all_items)))
    DOUBLE_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    double_path = DOUBLE_PROMPT_DIR / "v3_double_annotation.json"
    double_path.write_text(
        json.dumps({
            "batch_index": "double",
            "n_items": len(double_sample),
            "items": double_sample,
            "system_prompt": sys_prompt,
            "user_prompt": _user_prompt(double_sample),
            "rubric_version": "1.0",
            "note": "Use bypass_cache=True and a different sampling/seed when re-annotating these for kappa.",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote double-annotation pool to {double_path}")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    if not LABEL_DIR.exists():
        print(f"ERROR: label directory not found: {LABEL_DIR}")
        return 1

    label_files = sorted(LABEL_DIR.glob("v3_annotation_batch_*.json"))
    if not label_files:
        print(f"ERROR: no label files found in {LABEL_DIR}")
        return 1

    print(f"Loading {len(label_files)} label files...")
    cand_payload = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8-sig"))
    candidates_by_id = {c["candidate_id"]: c for c in cand_payload.get("candidates", [])}

    existing_payload = json.loads(EXISTING_CASES_PATH.read_text(encoding="utf-8-sig"))
    existing_by_id = {c["id"]: c for c in existing_payload.get("test_cases", [])}

    merged: list[dict[str, Any]] = []
    n_seen = 0
    n_missing = 0
    for fp in label_files:
        labels = json.loads(fp.read_text(encoding="utf-8-sig"))
        if isinstance(labels, dict) and "labels" in labels:
            labels = labels["labels"]
        for entry in labels:
            cid = entry.get("candidate_id")
            n_seen += 1
            if not cid:
                n_missing += 1
                continue
            # Build the merged record
            if cid in candidates_by_id:
                cand = candidates_by_id[cid]
                rec: dict[str, Any] = {
                    "id": cid,
                    "news": {
                        "id": cand.get("cls_id", cid),
                        "title": cand.get("title", ""),
                        "content": cand.get("content", ""),
                        "publish_time": cand.get("publish_time", ""),
                        "category": entry.get("category", "macro"),
                        "source": "cls_telegraph",
                    },
                    "known_outcome": "",  # populated downstream when applicable
                    "outcome_date": "9999-12-31",
                    "sector": "",
                    "key_entities": entry.get("key_entities", []),
                    "key_numbers": entry.get("key_numbers", []),
                    "expected_direction": entry.get("expected_direction", "neutral"),
                    "subcategory": entry.get("subcategory", ""),
                    "target": entry.get("target", ""),
                    "target_type": entry.get("target_type", "company"),
                    "period": cand.get("period", ""),
                    "funnel": cand.get("funnel", ""),
                    "anchor_level": entry.get("anchor_level"),
                    "anchor_cues": entry.get("anchor_cues", []),
                    "anchor_rationale": entry.get("anchor_rationale", ""),
                    "rubric_version": entry.get("rubric_version", "1.0"),
                }
            elif cid in existing_by_id:
                # Re-annotated existing case: keep all original fields, overwrite the v3 fields
                rec = dict(existing_by_id[cid])
                rec["anchor_level"] = entry.get("anchor_level")
                rec["anchor_cues"] = entry.get("anchor_cues", [])
                rec["anchor_rationale"] = entry.get("anchor_rationale", "")
                rec["rubric_version"] = entry.get("rubric_version", "1.0")
            else:
                n_missing += 1
                continue
            merged.append(rec)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"test_cases": merged, "count": len(merged)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Merged {len(merged)} cases (from {n_seen} label entries; {n_missing} missing/dropped)")
    print(f"Wrote {OUTPUT_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="V3 anchor annotation orchestration.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="Build batched prompt files for Codex")
    build.set_defaults(func=cmd_build)

    merge = sub.add_parser("merge", help="Merge Codex labels into test_cases_v3.json")
    merge.set_defaults(func=cmd_merge)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
