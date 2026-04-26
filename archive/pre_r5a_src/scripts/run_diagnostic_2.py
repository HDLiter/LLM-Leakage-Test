"""Run Diagnostic 2: CFLS pipeline on the expanded 192-case dataset."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.metrics import batch_cfls
from src.models import TestCase
from src.pilot import (
    PILOT_TASKS,
    PROMPTS_DIR,
    _atomic_write,
    _build_client,
    prepare_conditions,
    run_chunk_batched,
    run_single_case,
)
from src.prompt_loader import PromptLoader

DEFAULT_CASES_PATH = ROOT / "data" / "seed" / "test_cases_v3.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
DEFAULT_MAX_CONCURRENCY = 20
DEFAULT_CHUNK_SIZE = 50
SAVE_EVERY = 10
# Bump this whenever H2/H3 or scoring logic changes to invalidate stale checkpoints
PIPELINE_VERSION = 4  # v1=original, v2=H2+H3 fixes, v3=anchor/frequency strata + 3-phase batching, v4=authority task + multi-model
UNKNOWN_OUTCOME_DATE = "9999-12-31"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

CATEGORY_ALIASES = {
    "company": "corporate",
    "market": "macro",
}

TARGET_TYPE_ALIASES = {
    "stock": "company",
    "equity": "company",
    "industry": "sector",
    "theme": "sector",
    "market": "index",
}

DIRECTION_ALIASES = {
    "positive": "up",
    "bullish": "up",
    "negative": "down",
    "bearish": "down",
}


@dataclass(slots=True)
class CaseBundle:
    """A pilot-compatible case plus extra metadata for Diagnostic 2."""

    test_case: TestCase
    metadata: dict[str, Any]


def load_json(path: Path) -> Any:
    """Load JSON from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_cases(path: Path) -> list[dict[str, Any]]:
    """Load raw case dictionaries from JSON."""
    raw = load_json(path)
    cases: Any = raw
    if isinstance(raw, dict):
        if isinstance(raw.get("test_cases"), list):
            cases = raw["test_cases"]
        elif isinstance(raw.get("cases"), list):
            cases = raw["cases"]
        else:
            cases = next((value for value in raw.values() if isinstance(value, list)), None)

    if not isinstance(cases, list):
        raise ValueError(f"Unexpected test-case payload in {path}")
    return cases


def pick_value(*values: Any, default: Any = None) -> Any:
    """Return the first non-empty value from a list of candidates."""
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def ensure_string(value: Any, default: str = "") -> str:
    """Normalize a value into a stripped string."""
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def ensure_list(value: Any) -> list[str]:
    """Normalize a field into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [ensure_string(item) for item in value if ensure_string(item)]
    text = ensure_string(value)
    return [text] if text else []


def normalize_publish_time(value: Any) -> str:
    """Normalize publish_time into a value Pydantic can parse."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC).replace(tzinfo=None).isoformat()
    return ensure_string(value, default="1970-01-01T00:00:00")


def normalize_outcome_fields(
    known_outcome: Any,
    outcome_date: Any,
) -> tuple[str, str, bool]:
    """Sanitize outcome fields for pilot compatibility.

    Post-cutoff cases may not have a real future outcome yet. For those cases we keep
    false-outcome CPT usable via expected_direction and neutralize evidence-intrusion
    checks by using an empty known_outcome plus a far-future outcome_date sentinel.
    """
    known_outcome_text = ensure_string(known_outcome)
    outcome_date_text = ensure_string(outcome_date)

    known_outcome_available = bool(known_outcome_text) and known_outcome_text != "unknown_post_cutoff"
    if not known_outcome_available:
        return "", UNKNOWN_OUTCOME_DATE, False

    normalized_outcome_date = (
        outcome_date_text if DATE_RE.match(outcome_date_text) else UNKNOWN_OUTCOME_DATE
    )
    return known_outcome_text, normalized_outcome_date, True


def _period_from_cutoff(publish_time_str: str, cutoff_date: str) -> str:
    """Classify a case as pre/post cutoff by comparing publish_time to a date string."""
    # Compare date portions only (YYYY-MM-DD)
    pub_date = publish_time_str[:10]
    return "pre_cutoff" if pub_date <= cutoff_date else "post_cutoff"


def adapt_case(raw_case: dict[str, Any], cutoff_date: str | None = None) -> CaseBundle:
    """Map a raw expanded-case record onto the canonical TestCase schema."""
    raw_news = raw_case.get("news")
    news = raw_news if isinstance(raw_news, dict) else {}

    category = ensure_string(
        pick_value(news.get("category"), raw_case.get("category"), default="macro"),
        default="macro",
    ).lower()
    category = CATEGORY_ALIASES.get(category, category)

    target_type = ensure_string(
        pick_value(
            raw_case.get("target_type"),
            raw_case.get("entity_type"),
            raw_case.get("label_target_type"),
            default="",
        ),
    ).lower()
    target_type = TARGET_TYPE_ALIASES.get(target_type, target_type)

    expected_direction = ensure_string(raw_case.get("expected_direction")).lower()
    expected_direction = DIRECTION_ALIASES.get(expected_direction, expected_direction)

    pipeline_known_outcome, pipeline_outcome_date, known_outcome_available = normalize_outcome_fields(
        raw_case.get("known_outcome"),
        raw_case.get("outcome_date"),
    )

    title = ensure_string(pick_value(news.get("title"), raw_case.get("title"), default=""))
    content = ensure_string(
        pick_value(news.get("content"), raw_case.get("content"), title, default=title),
    )

    payload = {
        "id": ensure_string(raw_case.get("id")),
        "news": {
            "id": ensure_string(
                pick_value(news.get("id"), raw_case.get("news_id"), raw_case.get("id"), default=""),
            ),
            "title": title,
            "content": content,
            "publish_time": normalize_publish_time(
                pick_value(news.get("publish_time"), raw_case.get("publish_time"), news.get("ctime"), raw_case.get("ctime")),
            ),
            "category": category or "macro",
            "source": ensure_string(
                pick_value(news.get("source"), raw_case.get("source"), default="cls_telegraph"),
                default="cls_telegraph",
            ),
        },
        "known_outcome": pipeline_known_outcome,
        "outcome_date": pipeline_outcome_date,
        "sector": ensure_string(raw_case.get("sector")),
        "key_entities": ensure_list(raw_case.get("key_entities")),
        "key_numbers": ensure_list(raw_case.get("key_numbers")),
        "expected_direction": expected_direction,
        "subcategory": ensure_string(raw_case.get("subcategory")),
        "memorization_likelihood": ensure_string(
            pick_value(raw_case.get("memorization_likelihood"), raw_case.get("memorization"), default="medium"),
            default="medium",
        ).lower(),
        "target": ensure_string(
            pick_value(
                raw_case.get("target"),
                raw_case.get("target_name"),
                raw_case.get("entity"),
                raw_case.get("stock_name"),
                default="",
            ),
        ),
        "target_type": target_type,
    }

    try:
        test_case = TestCase(**payload)
    except Exception as exc:
        case_id = ensure_string(raw_case.get("id"), default="<unknown>")
        raise ValueError(f"Failed to adapt case {case_id}: {exc}") from exc

    # v3 fields (anchor_level, frequency_class, reversibility) — present in
    # test_cases_v3.json after Phase B annotation. Older case files may omit
    # them; default to None so downstream stratification handles "unknown".
    anchor_level_raw = raw_case.get("anchor_level")
    anchor_level = (
        int(anchor_level_raw)
        if anchor_level_raw is not None and str(anchor_level_raw).strip() != ""
        else None
    )
    frequency_class = ensure_string(raw_case.get("frequency_class"), default="") or None
    reversibility = ensure_string(raw_case.get("reversibility"), default="") or None

    # Period: use --cutoff-date override if provided, else fall back to source field
    if cutoff_date:
        pub_time = normalize_publish_time(
            pick_value(news.get("publish_time"), raw_case.get("publish_time"),
                       news.get("ctime"), raw_case.get("ctime")),
        )
        period = _period_from_cutoff(pub_time, cutoff_date)
    else:
        period = ensure_string(raw_case.get("period"), default="unknown")

    metadata = {
        "period": period,
        "rarity_estimate": ensure_string(
            pick_value(raw_case.get("rarity_estimate"), raw_case.get("rarity"), default="unknown"),
            default="unknown",
        ),
        "anchor_level": anchor_level,
        "frequency_class": frequency_class,
        "reversibility": reversibility,
        "anchor_binary": (
            "strongly_anchored" if anchor_level is not None and anchor_level >= 2
            else "weakly_anchored" if anchor_level is not None
            else None
        ),
        "known_outcome_available": known_outcome_available,
        "original_known_outcome": ensure_string(raw_case.get("known_outcome")),
        "original_outcome_date": ensure_string(raw_case.get("outcome_date")),
        "is_expanded_case": test_case.id.startswith("exp_"),
    }
    return CaseBundle(test_case=test_case, metadata=metadata)


def load_eligible_cases(
    path: Path,
    limit: int = 0,
    cutoff_date: str | None = None,
) -> tuple[list[CaseBundle], dict[str, Any]]:
    """Load, adapt, and filter the expanded dataset for Diagnostic 2."""
    raw_cases = load_raw_cases(path)
    bundles = [adapt_case(raw_case, cutoff_date=cutoff_date) for raw_case in raw_cases]

    counts = Counter()
    eligible: list[CaseBundle] = []
    for bundle in bundles:
        tc = bundle.test_case
        direction = getattr(tc.expected_direction, "value", tc.expected_direction)
        if direction == "neutral":
            counts["neutral"] += 1
            continue
        if not tc.target or not tc.target_type:
            counts["missing_target_or_type"] += 1
            continue
        eligible.append(bundle)

    duplicate_ids = [case_id for case_id, count in Counter(bundle.test_case.id for bundle in eligible).items() if count > 1]
    if duplicate_ids:
        raise ValueError(f"Duplicate eligible case IDs found: {duplicate_ids}")

    if limit > 0:
        eligible = eligible[:limit]

    stats = {
        "n_source_cases": len(raw_cases),
        "n_adapted_cases": len(bundles),
        "n_eligible_cases": len(eligible),
        "n_filtered_neutral": counts["neutral"],
        "n_filtered_missing_target_or_type": counts["missing_target_or_type"],
        "eligible_by_period": dict(Counter(bundle.metadata["period"] for bundle in eligible)),
        "eligible_by_anchor_level": dict(
            Counter(str(bundle.metadata.get("anchor_level")) for bundle in eligible),
        ),
        "eligible_by_anchor_binary": dict(
            Counter(str(bundle.metadata.get("anchor_binary")) for bundle in eligible),
        ),
        "eligible_by_frequency_class": dict(
            Counter(str(bundle.metadata.get("frequency_class")) for bundle in eligible),
        ),
    }
    return eligible, stats


def make_condition_summary(conditions: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Condense per-case condition generation state for saved outputs."""
    summary: dict[str, dict[str, Any]] = {}
    for name, condition in conditions.items():
        summary[name] = {
            "source": condition.get("source"),
            "failed": bool(condition.get("failed", False)),
            "article_available": bool(condition.get("article")),
        }
    return summary


def compute_cf_failure_summary(
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Per-CF-type and per-stratum failure / scored counts.

    Surfaces the missing-data structure that ``aggregate_case_results`` would
    otherwise hide behind ``count`` (cases that failed CF generation are
    silently dropped from the per-task mean denominator).

    Returns a dict with three blocks:
        - ``n_cf_failed_by_type``: total cases where each CF type was skipped
          (sr_direction, sr_fund_impact, neutral_paraphrase). Detected via
          ``responses[cond].skipped == True``.
        - ``cf_failed_by_stratum``: same counts split by ``period/anchor_binary``.
        - ``n_scored_by_task_x_stratum``: per-task ``cfls != None`` count by
          stratum, so the reader can compute ``n_scored / n_total`` per cell.
    """
    fail_total: Counter[str] = Counter()
    fail_by_stratum: dict[str, Counter[str]] = {
        "sr_direction": Counter(),
        "sr_fund_impact": Counter(),
        "neutral_paraphrase": Counter(),
    }
    n_total_by_stratum: Counter[str] = Counter()
    n_scored_by_task_x_stratum: dict[str, Counter[str]] = {
        task_id: Counter() for task_id in PILOT_TASKS
    }

    for case_result in case_results:
        period = case_result.get("period") or "unknown"
        anchor = case_result.get("anchor_binary") or "unknown"
        cell = f"{period}/{anchor}"
        n_total_by_stratum[cell] += 1

        tasks = case_result.get("tasks", {})
        direct = tasks.get("direct_prediction.base", {})
        impact = tasks.get("decomposed_impact.base", {})
        authority = tasks.get("decomposed_authority.matched", {})
        direct_resp = direct.get("responses", {}) if isinstance(direct, dict) else {}
        impact_resp = impact.get("responses", {}) if isinstance(impact, dict) else {}
        authority_resp = authority.get("responses", {}) if isinstance(authority, dict) else {}

        sr_dir_skipped = bool(
            direct_resp.get("semantic_reversal", {}).get("skipped")
            or authority_resp.get("semantic_reversal", {}).get("skipped")
        )
        sr_imp_skipped = bool(impact_resp.get("semantic_reversal", {}).get("skipped"))
        np_skipped = bool(
            direct_resp.get("neutral_paraphrase", {}).get("skipped")
            or impact_resp.get("neutral_paraphrase", {}).get("skipped")
            or authority_resp.get("neutral_paraphrase", {}).get("skipped")
        )

        if sr_dir_skipped:
            fail_total["sr_direction"] += 1
            fail_by_stratum["sr_direction"][cell] += 1
        if sr_imp_skipped:
            fail_total["sr_fund_impact"] += 1
            fail_by_stratum["sr_fund_impact"][cell] += 1
        if np_skipped:
            fail_total["neutral_paraphrase"] += 1
            fail_by_stratum["neutral_paraphrase"][cell] += 1

        # Per-task scored counts (cfls != None)
        for task_id in PILOT_TASKS:
            task_block = tasks.get(task_id, {}) if isinstance(tasks, dict) else {}
            cfls_score = (
                task_block.get("cfls", {}).get("cfls")
                if isinstance(task_block, dict) else None
            )
            if cfls_score is not None:
                n_scored_by_task_x_stratum[task_id][cell] += 1

    return {
        "n_cf_failed_by_type": dict(fail_total),
        "cf_failed_by_stratum": {
            cf_type: dict(counter) for cf_type, counter in fail_by_stratum.items()
        },
        "n_total_by_stratum": dict(n_total_by_stratum),
        "n_scored_by_task_x_stratum": {
            task_id: dict(counter)
            for task_id, counter in n_scored_by_task_x_stratum.items()
        },
    }


def aggregate_case_results(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate pilot CFLS outputs, mirroring src.pilot.run_pilot."""
    all_cfls_entries: list[dict[str, Any]] = []
    for case_result in case_results:
        for task_id in PILOT_TASKS:
            task_cfls = dict(case_result["tasks"][task_id]["cfls"])
            if task_cfls.get("cfls") is not None:
                task_cfls["case_id"] = case_result["case_id"]
                all_cfls_entries.append(task_cfls)

    aggregated = batch_cfls(all_cfls_entries)
    aggregated["correlation"] = None

    paired: dict[str, dict[str, float]] = {}
    for case_result in case_results:
        scores: dict[str, float] = {}
        for task_id in PILOT_TASKS:
            score = case_result["tasks"][task_id]["cfls"].get("cfls")
            if score is not None:
                scores[task_id] = score
        if len(scores) == len(PILOT_TASKS):
            paired[case_result["case_id"]] = scores

    if len(paired) > 1:
        import numpy as np
        from itertools import combinations

        # Pairwise correlations for all task pairs
        pairwise: dict[str, float | None] = {}
        for ta, tb in combinations(PILOT_TASKS, 2):
            a_vals = [scores[ta] for scores in paired.values()]
            b_vals = [scores[tb] for scores in paired.values()]
            corr = np.corrcoef(a_vals, b_vals)[0, 1]
            pairwise[f"{ta}_vs_{tb}"] = None if np.isnan(corr) else float(corr)
        aggregated["correlation_pairwise"] = pairwise
        # Legacy scalar: first pair
        first_pair = list(pairwise.values())[0] if pairwise else None
        aggregated["correlation"] = first_pair
        aggregated["correlation_n_paired"] = len(paired)
    else:
        aggregated["correlation_n_paired"] = len(paired)

    aggregated["n_scored_entries"] = len(all_cfls_entries)
    aggregated["n_completed_cases"] = len(case_results)
    return aggregated


def aggregate_by_field(case_results: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Aggregate results for a categorical metadata field."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case_result in case_results:
        value = ensure_string(case_result.get(field), default="unknown")
        grouped[value].append(case_result)

    return {
        key: {
            "n_cases": len(group),
            "aggregated": aggregate_case_results(group),
        }
        for key, group in sorted(grouped.items())
    }


def aggregate_by_joint(
    case_results: list[dict[str, Any]],
    field_a: str,
    field_b: str,
) -> dict[str, Any]:
    """Aggregate by a joint key, used for period × anchor cell tables."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case_result in case_results:
        a = ensure_string(case_result.get(field_a), default="unknown")
        b = ensure_string(case_result.get(field_b), default="unknown")
        grouped[f"{a}/{b}"].append(case_result)

    return {
        key: {
            "n_cases": len(group),
            "aggregated": aggregate_case_results(group),
        }
        for key, group in sorted(grouped.items())
    }


def load_resume_state(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load previously saved successful cases and error records."""
    if not path.exists():
        return [], []

    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ValueError(f"Unexpected resume payload in {path}")

    cases = raw.get("cases", [])
    errors = raw.get("errors", [])
    if not isinstance(cases, list) or not isinstance(errors, list):
        raise ValueError(f"Unexpected resume payload structure in {path}")
    return cases, errors


def drop_errors_for_case(errors: list[dict[str, Any]], case_id: str) -> list[dict[str, Any]]:
    """Remove stale error entries for a case that is being retried or succeeded."""
    return [entry for entry in errors if entry.get("case_id") != case_id]


def build_output_payload(
    *,
    case_results: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    stats: dict[str, Any],
    cases_path: Path,
    output_path: Path,
    seed: int,
    max_concurrency: int,
    resumed: bool,
    partial: bool,
) -> dict[str, Any]:
    """Build the saved Diagnostic 2 payload."""
    completed_ids = {case_result["case_id"] for case_result in case_results}
    aggregated = aggregate_case_results(case_results)
    cf_summary = compute_cf_failure_summary(case_results)

    payload = {
        "meta": {
            "experiment": "diagnostic_2",
            "pipeline_version": PIPELINE_VERSION,
            "description": "CFLS pipeline on expanded cases with outcome-specific CPT (H2) and independent fo_flip (H3)",
            "tasks": PILOT_TASKS,
            "source_cases_path": str(cases_path),
            "output_path": str(output_path),
            "timestamp": datetime.now(UTC).isoformat(),
            "seed": seed,
            "max_concurrency": max_concurrency,
            "save_every": SAVE_EVERY,
            "resumed": resumed,
            "partial": partial,
            "cutoff_date": stats.get("cutoff_date"),
            "n_source_cases": stats["n_source_cases"],
            "n_eligible_cases": stats["n_eligible_cases"],
            "n_cases_completed": len(case_results),
            "n_cases_remaining": max(stats["n_eligible_cases"] - len(completed_ids), 0),
            "n_case_errors": len(errors),
            "n_filtered_neutral": stats["n_filtered_neutral"],
            "n_filtered_missing_target_or_type": stats["n_filtered_missing_target_or_type"],
            "eligible_by_period": stats["eligible_by_period"],
            "eligible_by_anchor_level": stats.get("eligible_by_anchor_level", {}),
            "eligible_by_anchor_binary": stats.get("eligible_by_anchor_binary", {}),
            "eligible_by_frequency_class": stats.get("eligible_by_frequency_class", {}),
            "n_total_cases": len(case_results),
            "n_cf_failed_by_type": cf_summary["n_cf_failed_by_type"],
            "cf_failed_by_stratum": cf_summary["cf_failed_by_stratum"],
            "n_total_by_stratum": cf_summary["n_total_by_stratum"],
            "n_scored_by_task_x_stratum": cf_summary["n_scored_by_task_x_stratum"],
            "adapter": {
                "unknown_known_outcome_handling": "known_outcome='' and outcome_date='9999-12-31'",
                "false_outcome_cpt_strategy": (
                    "Phase 2 LLM-only negation for pre-cutoff (cpt_mode=llm_negated|llm_failed); "
                    "generic directional template for post-cutoff (cpt_mode=generic_post_cutoff)."
                ),
            },
        },
        "cases": case_results,
        "errors": errors,
        "aggregated": aggregated,
        "stratified": {
            "by_period": aggregate_by_field(case_results, "period"),
            "by_anchor_level": aggregate_by_field(case_results, "anchor_level"),
            "by_anchor_binary": aggregate_by_field(case_results, "anchor_binary"),
            "by_frequency_class": aggregate_by_field(case_results, "frequency_class"),
            "by_period_x_anchor_level": aggregate_by_joint(
                case_results, "period", "anchor_level",
            ),
            "by_period_x_anchor_binary": aggregate_by_joint(
                case_results, "period", "anchor_binary",
            ),
        },
    }
    return payload


def save_checkpoint(
    *,
    output_path: Path,
    case_results: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    stats: dict[str, Any],
    cases_path: Path,
    seed: int,
    max_concurrency: int,
    resumed: bool,
    partial: bool,
) -> None:
    """Save current progress atomically."""
    payload = build_output_payload(
        case_results=case_results,
        errors=errors,
        stats=stats,
        cases_path=cases_path,
        output_path=output_path,
        seed=seed,
        max_concurrency=max_concurrency,
        resumed=resumed,
        partial=partial,
    )
    _atomic_write(output_path, payload)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run Diagnostic 2: CFLS pipeline on expanded test cases.",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to test_cases_expanded.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Where to save diagnostic results",
    )
    parser.add_argument(
        "--n-cases",
        type=int,
        default=0,
        help="Limit number of eligible cases after filtering (0 = all)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for false-outcome CPT phrase selection",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=DEFAULT_MAX_CONCURRENCY,
        help="Max concurrent API requests inside each case (capped at 20)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Cases per batched chunk (Phase1->Phase2->Phase3->Phase4 per chunk)",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use the legacy per-case sequential pipeline instead of 3-phase batching",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing output file by skipping already completed cases",
    )
    # B0.1: Multi-model support
    parser.add_argument(
        "--settings",
        type=Path,
        default=None,
        help="Path to settings YAML (default: config/settings.yaml)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model name from settings",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Override base URL from settings",
    )
    parser.add_argument(
        "--api-key-env",
        type=str,
        default=None,
        help="Env var name for the API key (default: from settings or DEEPSEEK_API_KEY)",
    )
    parser.add_argument(
        "--cutoff-date",
        type=str,
        default=None,
        help="Override pre/post cutoff date (YYYY-MM-DD). Cases with publish_time <= this date "
             "are pre_cutoff; after are post_cutoff. When omitted, uses the period field from "
             "the source dataset.",
    )
    # B0.5: False-outcome override for Arm 3
    parser.add_argument(
        "--fo-override",
        type=Path,
        default=None,
        help="JSON file mapping case_id → false_outcome_text (skip on-the-fly FO generation)",
    )
    return parser.parse_args()


def main() -> int:
    """Run the expanded CFLS diagnostic."""
    args = parse_args()
    max_concurrency = max(1, min(args.max_concurrency, DEFAULT_MAX_CONCURRENCY))
    random.seed(args.seed)

    eligible_cases, stats = load_eligible_cases(
        args.cases, limit=args.n_cases, cutoff_date=args.cutoff_date,
    )
    if args.cutoff_date:
        print(f"Cutoff date override: {args.cutoff_date}")
        stats["cutoff_date"] = args.cutoff_date
    ordered_case_ids = [bundle.test_case.id for bundle in eligible_cases]
    case_positions = {case_id: index for index, case_id in enumerate(ordered_case_ids, start=1)}

    print(f"Loaded {stats['n_source_cases']} source cases from {args.cases}")
    print(f"Eligible cases (non-neutral, annotated): {stats['n_eligible_cases']}")
    print(f"Using max concurrency = {max_concurrency}")

    completed_results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    resumed = False

    if args.resume and args.output.exists():
        completed_results, errors = load_resume_state(args.output)
        # Check pipeline version to avoid mixing old/new scoring logic
        with open(args.output, "r", encoding="utf-8") as _f:
            _saved_meta = json.load(_f).get("meta", {})
        saved_version = _saved_meta.get("pipeline_version", 1)
        if saved_version != PIPELINE_VERSION:
            print(
                f"WARNING: checkpoint pipeline_version={saved_version} != current {PIPELINE_VERSION}. "
                f"Discarding stale checkpoint and starting fresh."
            )
            completed_results = []
            errors = []
        resumed = True
        completed_ids = {case_result["case_id"] for case_result in completed_results}
        eligible_cases = [
            bundle for bundle in eligible_cases
            if bundle.test_case.id not in completed_ids
        ]
        print(
            f"Resuming from {args.output}: "
            f"{len(completed_results)} completed, {len(eligible_cases)} remaining",
        )
    elif args.resume:
        resumed = True
        print(f"Resume requested but no existing output found at {args.output}; starting fresh")

    client = _build_client(
        settings_path=args.settings,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
    )
    loader = PromptLoader(prompts_dir=str(PROMPTS_DIR))

    # B0.5: Load false-outcome overrides if provided
    fo_override_map: dict[str, str] | None = None
    if args.fo_override:
        loaded = json.loads(args.fo_override.read_text(encoding="utf-8"))
        fo_override_map = loaded
        print(f"Loaded {len(loaded)} FO overrides from {args.fo_override}")

    def _attach_metadata(case_result: dict[str, Any], bundle: CaseBundle) -> None:
        case_result["period"] = bundle.metadata["period"]
        case_result["rarity_estimate"] = bundle.metadata["rarity_estimate"]
        case_result["anchor_level"] = bundle.metadata.get("anchor_level")
        case_result["anchor_binary"] = bundle.metadata.get("anchor_binary")
        case_result["frequency_class"] = bundle.metadata.get("frequency_class")
        case_result["reversibility"] = bundle.metadata.get("reversibility")
        case_result["known_outcome_available"] = bundle.metadata["known_outcome_available"]
        case_result["is_expanded_case"] = bundle.metadata["is_expanded_case"]

    try:
        if args.legacy:
            print("Mode: LEGACY per-case sequential pipeline (--legacy)")
            for bundle in eligible_cases:
                tc = bundle.test_case
                direction = getattr(tc.expected_direction, "value", tc.expected_direction)
                ordinal = case_positions.get(tc.id, len(completed_results) + 1)

                print(f"\n[{ordinal}/{stats['n_eligible_cases']}] {tc.id} | {tc.target} ({tc.target_type}) | {direction}")
                try:
                    print("  Generating counterfactual conditions...")
                    conditions = prepare_conditions(client, loader, tc)
                    for cond_name, cond in conditions.items():
                        status = "OK"
                        if cond_name not in ("original",) and cond.get("failed"):
                            status = "FAILED"
                        print(f"    {cond_name}: {status}")

                    print("  Running tasks...")
                    case_result = run_single_case(
                        client=client,
                        loader=loader,
                        tc=tc,
                        conditions=conditions,
                        max_concurrency=max_concurrency,
                    )
                    _attach_metadata(case_result, bundle)
                    case_result["condition_summary"] = make_condition_summary(conditions)

                    errors = drop_errors_for_case(errors, tc.id)
                    completed_results.append(case_result)

                    cfls_direct = case_result["metrics"]["cfls_direct"]
                    cfls_impact = case_result["metrics"]["cfls_impact"]
                    cfls_authority = case_result["metrics"]["cfls_authority"]
                    direct_text = f"{cfls_direct:.2f}" if cfls_direct is not None else "N/A"
                    impact_text = f"{cfls_impact:.2f}" if cfls_impact is not None else "N/A"
                    authority_text = f"{cfls_authority:.2f}" if cfls_authority is not None else "N/A"
                    print(f"  CFLS: direct={direct_text}, impact={impact_text}, authority={authority_text}")
                except Exception as exc:
                    errors = drop_errors_for_case(errors, tc.id)
                    errors.append({
                        "case_id": tc.id,
                        "target": tc.target,
                        "target_type": tc.target_type,
                        "expected_direction": direction,
                        "period": bundle.metadata["period"],
                        "anchor_level": bundle.metadata.get("anchor_level"),
                        "frequency_class": bundle.metadata.get("frequency_class"),
                        "stage": "legacy_pipeline",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "timestamp": datetime.now(UTC).isoformat(),
                    })
                    print(f"  [ERROR] Case {tc.id} failed: {type(exc).__name__}: {exc}")

                processed_count = len(completed_results) + len(errors)
                if processed_count > 0 and processed_count % SAVE_EVERY == 0:
                    save_checkpoint(
                        output_path=args.output,
                        case_results=completed_results,
                        errors=errors,
                        stats=stats,
                        cases_path=args.cases,
                        seed=args.seed,
                        max_concurrency=max_concurrency,
                        resumed=resumed,
                        partial=True,
                    )
                    print(f"  Checkpoint saved to {args.output}")
        else:
            chunk_size = max(1, args.chunk_size)
            n_chunks = (len(eligible_cases) + chunk_size - 1) // chunk_size
            print(f"Mode: BATCHED 3-phase pipeline | chunk_size={chunk_size} | n_chunks={n_chunks}")

            for chunk_idx in range(n_chunks):
                start = chunk_idx * chunk_size
                end = min(start + chunk_size, len(eligible_cases))
                chunk_bundles = eligible_cases[start:end]
                chunk_tcs = [b.test_case for b in chunk_bundles]
                bundle_by_id = {b.test_case.id: b for b in chunk_bundles}

                print(f"\n=== Chunk {chunk_idx + 1}/{n_chunks} ({len(chunk_tcs)} cases: indices {start}..{end - 1}) ===")
                t_chunk = datetime.now(UTC)
                try:
                    chunk_results, chunk_errors = run_chunk_batched(
                        client=client,
                        loader=loader,
                        test_cases=chunk_tcs,
                        max_concurrency=max_concurrency,
                        fo_override=fo_override_map,
                    )
                except Exception as exc:
                    # Catastrophic failure of an entire chunk -- record one error
                    # per case and keep going.
                    print(f"  [CHUNK ERROR] {type(exc).__name__}: {exc}")
                    for tc in chunk_tcs:
                        errors = drop_errors_for_case(errors, tc.id)
                        errors.append({
                            "case_id": tc.id,
                            "target": tc.target,
                            "stage": "chunk_pipeline",
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "timestamp": datetime.now(UTC).isoformat(),
                        })
                    save_checkpoint(
                        output_path=args.output,
                        case_results=completed_results,
                        errors=errors,
                        stats=stats,
                        cases_path=args.cases,
                        seed=args.seed,
                        max_concurrency=max_concurrency,
                        resumed=resumed,
                        partial=True,
                    )
                    continue

                # Attach metadata + record successful results
                for case_result in chunk_results:
                    bundle = bundle_by_id.get(case_result["case_id"])
                    if bundle is None:
                        continue
                    _attach_metadata(case_result, bundle)
                    errors = drop_errors_for_case(errors, case_result["case_id"])
                    completed_results.append(case_result)

                # Record per-case errors from the chunk
                for err in chunk_errors:
                    case_id = err.get("case_id", "<unknown>")
                    bundle = bundle_by_id.get(case_id)
                    errors = drop_errors_for_case(errors, case_id)
                    errors.append({
                        "case_id": case_id,
                        "target": getattr(bundle.test_case, "target", "") if bundle else "",
                        "period": bundle.metadata["period"] if bundle else "unknown",
                        "anchor_level": bundle.metadata.get("anchor_level") if bundle else None,
                        "stage": err.get("stage", "scoring"),
                        "error_type": "chunk_case_error",
                        "error": err.get("reason", ""),
                        "timestamp": datetime.now(UTC).isoformat(),
                    })

                # Diagnostic: count llm_failed CPT cases in this chunk
                llm_failed_pre = sum(
                    1 for cr in chunk_results
                    if (
                        bundle_by_id.get(cr["case_id"])
                        and bundle_by_id[cr["case_id"]].metadata.get("known_outcome_available")
                        and (
                            cr.get("tasks", {})
                            .get("direct_prediction.base", {})
                            .get("responses", {})
                            .get("false_outcome_cpt", {})
                            .get("skipped", False)
                        )
                    )
                )
                elapsed = (datetime.now(UTC) - t_chunk).total_seconds()
                print(f"  chunk wall time: {elapsed:.1f}s | "
                      f"completed={len(chunk_results)} | "
                      f"errors={len(chunk_errors)} | "
                      f"llm_failed_pre={llm_failed_pre}")

                save_checkpoint(
                    output_path=args.output,
                    case_results=completed_results,
                    errors=errors,
                    stats=stats,
                    cases_path=args.cases,
                    seed=args.seed,
                    max_concurrency=max_concurrency,
                    resumed=resumed,
                    partial=(chunk_idx + 1 < n_chunks),
                )
                print(f"  Checkpoint saved: {len(completed_results)}/{stats['n_eligible_cases']} done, {len(errors)} errors")
    except KeyboardInterrupt:
        print("\nInterrupted; saving partial progress...")
        save_checkpoint(
            output_path=args.output,
            case_results=completed_results,
            errors=errors,
            stats=stats,
            cases_path=args.cases,
            seed=args.seed,
            max_concurrency=max_concurrency,
            resumed=resumed,
            partial=True,
        )
        return 130
    finally:
        client._client.close()

    save_checkpoint(
        output_path=args.output,
        case_results=completed_results,
        errors=errors,
        stats=stats,
        cases_path=args.cases,
        seed=args.seed,
        max_concurrency=max_concurrency,
        resumed=resumed,
        partial=False,
    )
    print(f"\nResults saved to {args.output}")

    aggregated = aggregate_case_results(completed_results)
    for task_id, task_stats in aggregated.get("by_task", {}).items():
        print(
            f"  {task_id}: mean_cfls={task_stats['mean']:.3f} "
            f"std={task_stats['std']:.3f} positive_rate={task_stats['positive_rate']:.1%}",
        )
    if aggregated.get("correlation") is not None:
        print(f"  Cross-task correlation: {aggregated['correlation']:.3f}")
    if errors:
        print(f"  Cases with recorded errors: {len(errors)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
