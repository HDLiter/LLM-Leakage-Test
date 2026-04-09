"""Diagnostic 3: comprehensive analysis of diagnostic outputs with stratification."""

from __future__ import annotations

import argparse
import json
import math
import warnings
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIAG1_PATH = ROOT / "data" / "results" / "diagnostic_1_results.json"
DEFAULT_DIAG2_PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
DEFAULT_METADATA_PATH = ROOT / "data" / "seed" / "test_cases_expanded.json"
DEFAULT_MARKDOWN_PATH = ROOT / "data" / "results" / "diagnostic_analysis.md"
DEFAULT_JSON_PATH = ROOT / "data" / "results" / "diagnostic_analysis.json"

PERIOD_ORDER = ("pre_cutoff", "post_cutoff")
RARITY_ORDER = ("rare", "medium", "common")
TASK_LABELS = {
    "direct_prediction.base": "direct_prediction",
    "decomposed_impact.base": "decomposed_impact",
    "mean_across_tasks": "mean_across_tasks",
    "any_flip": "any_flip",
}


def load_json(path: Path) -> Any:
    """Load JSON from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(sanitize_for_json(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def sanitize_for_json(value: Any) -> Any:
    """Convert non-JSON-safe values into serializable primitives."""
    if isinstance(value, dict):
        return {str(key): sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (np.floating, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value


def coerce_float(value: Any) -> float | None:
    """Coerce a value to float when possible."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = float(text)
        except ValueError:
            return None
        if math.isnan(parsed) or math.isinf(parsed):
            return None
        return parsed
    return None


def mean(values: list[float]) -> float | None:
    """Return arithmetic mean or None for empty input."""
    if not values:
        return None
    return float(np.mean(values))


def median(values: list[float]) -> float | None:
    """Return median or None for empty input."""
    if not values:
        return None
    return float(np.median(values))


def std(values: list[float]) -> float | None:
    """Return population standard deviation or None for empty input."""
    if not values:
        return None
    return float(np.std(values))


def normalize_period(value: Any) -> str:
    """Normalize temporal split labels."""
    text = str(value or "").strip().lower()
    if text == "pre_cutoff" or ("pre" in text and "cutoff" in text):
        return "pre_cutoff"
    if text == "post_cutoff" or ("post" in text and "cutoff" in text):
        return "post_cutoff"
    return "unknown"


def normalize_rarity(value: Any) -> str:
    """Normalize rarity labels."""
    text = str(value or "").strip().lower()
    if text in {"rare", "medium", "common"}:
        return text
    return "unknown"


def task_label(task_id: str) -> str:
    """Short display label for a task id."""
    return TASK_LABELS.get(task_id, task_id)


def format_float(value: float | None, digits: int = 3) -> str:
    """Format a float or return N/A."""
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def format_pct(value: float | None, digits: int = 1) -> str:
    """Format a proportion as a percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{digits}f}%"


def format_p(value: float | None) -> str:
    """Format a p-value."""
    if value is None:
        return "N/A"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def format_effect(value: float | None, digits: int = 3) -> str:
    """Format an effect size."""
    if value is None:
        return "N/A"
    if math.isinf(value):
        return "inf"
    return f"{value:.{digits}f}"


def rate(successes: int, total: int) -> float | None:
    """Return a binomial rate."""
    if total <= 0:
        return None
    return successes / total


def continuous_summary(values: list[float]) -> dict[str, Any]:
    """Compute descriptive statistics for a numeric sample."""
    clean = [float(value) for value in values]
    return {
        "n": len(clean),
        "mean": mean(clean),
        "median": median(clean),
        "std": std(clean),
        "min": float(np.min(clean)) if clean else None,
        "max": float(np.max(clean)) if clean else None,
    }


def esc(text: Any) -> str:
    """Escape markdown table cells."""
    return str(text).replace("|", "\\|")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Render a markdown table."""
    if not rows:
        rows = [["N/A" for _ in headers]]
    header_line = "| " + " | ".join(esc(header) for header in headers) + " |"
    divider_line = "| " + " | ".join("---" for _ in headers) + " |"
    body_lines = [
        "| " + " | ".join(esc(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([header_line, divider_line, *body_lines])


def probe_type_sort_key(probe_type: str) -> tuple[int, str]:
    """Sort known probe types first."""
    known = ["price_query", "trend_prediction", "event_impact", "market_performance"]
    if probe_type in known:
        return (known.index(probe_type), probe_type)
    return (len(known), probe_type)


def mann_whitney_result(
    group_a: list[float],
    group_b: list[float],
    group_a_label: str,
    group_b_label: str,
) -> dict[str, Any]:
    """Run a Mann-Whitney U test and compute rank-biserial effect size."""
    a = [float(value) for value in group_a]
    b = [float(value) for value in group_b]
    result: dict[str, Any] = {
        "test": "Mann-Whitney U",
        "group_a_label": group_a_label,
        "group_b_label": group_b_label,
        "group_a": continuous_summary(a),
        "group_b": continuous_summary(b),
        "mean_difference": (mean(a) or 0.0) - (mean(b) or 0.0) if a and b else None,
        "median_difference": (median(a) or 0.0) - (median(b) or 0.0) if a and b else None,
        "statistic": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_name": "rank_biserial_correlation",
        "common_language_effect": None,
        "available": False,
    }
    if not a or not b:
        result["reason"] = "One or both groups are empty."
        return result

    u_stat, p_value = stats.mannwhitneyu(a, b, alternative="two-sided", method="auto")
    n_pairs = len(a) * len(b)
    common_language = float(u_stat) / n_pairs if n_pairs else None
    rank_biserial = (2.0 * float(u_stat) / n_pairs - 1.0) if n_pairs else None

    result.update(
        {
            "statistic": float(u_stat),
            "p_value": float(p_value),
            "effect_size": rank_biserial,
            "common_language_effect": common_language,
            "available": True,
        }
    )
    return result


def kruskal_result(group_map: dict[str, list[float]]) -> dict[str, Any]:
    """Run a Kruskal-Wallis test and compute epsilon-squared effect size."""
    clean_groups = {
        group_name: [float(value) for value in values]
        for group_name, values in group_map.items()
        if values
    }
    result: dict[str, Any] = {
        "test": "Kruskal-Wallis",
        "groups": {
            group_name: continuous_summary(values)
            for group_name, values in clean_groups.items()
        },
        "statistic": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_name": "epsilon_squared",
        "available": False,
    }
    if len(clean_groups) < 2:
        result["reason"] = "At least two non-empty groups are required."
        return result

    ordered_values = [clean_groups.get(group_name, []) for group_name in RARITY_ORDER if group_name in clean_groups]
    h_stat, p_value = stats.kruskal(*ordered_values)
    n_total = sum(len(values) for values in clean_groups.values())
    k_groups = len(clean_groups)
    epsilon_squared = None
    if n_total > k_groups:
        epsilon_squared = max(0.0, float((h_stat - k_groups + 1) / (n_total - k_groups)))

    result.update(
        {
            "statistic": float(h_stat),
            "p_value": float(p_value),
            "effect_size": epsilon_squared,
            "available": True,
        }
    )
    return result


def fisher_result(
    success_a: int,
    total_a: int,
    success_b: int,
    total_b: int,
    group_a_label: str,
    group_b_label: str,
) -> dict[str, Any]:
    """Run Fisher's exact test with odds ratio as the main effect size."""
    failure_a = total_a - success_a
    failure_b = total_b - success_b
    result: dict[str, Any] = {
        "test": "Fisher exact",
        "group_a_label": group_a_label,
        "group_b_label": group_b_label,
        "group_a": {
            "n": total_a,
            "successes": success_a,
            "failures": failure_a,
            "rate": rate(success_a, total_a),
        },
        "group_b": {
            "n": total_b,
            "successes": success_b,
            "failures": failure_b,
            "rate": rate(success_b, total_b),
        },
        "statistic": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_name": "odds_ratio",
        "rate_difference": None,
        "available": False,
    }
    if total_a <= 0 or total_b <= 0:
        result["reason"] = "One or both groups have zero evaluable cases."
        return result

    odds_ratio, p_value = stats.fisher_exact(
        [[success_a, failure_a], [success_b, failure_b]],
        alternative="two-sided",
    )
    result.update(
        {
            "statistic": float(odds_ratio) if not math.isnan(float(odds_ratio)) else None,
            "p_value": float(p_value),
            "effect_size": float(odds_ratio) if not math.isnan(float(odds_ratio)) else None,
            "rate_difference": rate(success_a, total_a) - rate(success_b, total_b),
            "available": True,
        }
    )
    return result


def spearman_result(x_values: list[float], y_values: list[float], x_label: str, y_label: str) -> dict[str, Any]:
    """Run Spearman rank correlation with robust handling of constant inputs."""
    if len(x_values) != len(y_values):
        raise ValueError("x_values and y_values must have the same length")

    paired = [
        (float(x), float(y))
        for x, y in zip(x_values, y_values)
        if x is not None and y is not None
    ]
    result: dict[str, Any] = {
        "test": "Spearman",
        "x_label": x_label,
        "y_label": y_label,
        "n": len(paired),
        "statistic": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_name": "spearman_rho",
        "available": False,
    }
    if len(paired) < 3:
        result["reason"] = "At least three paired observations are required."
        return result

    x = [pair[0] for pair in paired]
    y = [pair[1] for pair in paired]
    if len(set(x)) < 2 or len(set(y)) < 2:
        result["reason"] = "One variable is constant."
        return result

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rho, p_value = stats.spearmanr(x, y)
    if math.isnan(float(rho)) or math.isnan(float(p_value)):
        result["reason"] = "Correlation undefined."
        return result

    result.update(
        {
            "statistic": float(rho),
            "p_value": float(p_value),
            "effect_size": float(rho),
            "available": True,
        }
    )
    return result


def extract_case_metadata(path: Path) -> dict[str, dict[str, str]]:
    """Load period and rarity metadata from the seed case file."""
    if not path.exists():
        return {}

    raw = load_json(path)
    if isinstance(raw, dict):
        cases = raw.get("test_cases") or raw.get("cases") or []
    else:
        cases = raw

    metadata: dict[str, dict[str, str]] = {}
    if not isinstance(cases, list):
        return metadata

    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            continue
        metadata[case_id] = {
            "period": normalize_period(case.get("period")),
            "rarity": normalize_rarity(case.get("rarity_estimate") or case.get("rarity")),
        }
    return metadata


def extract_diag1(diag1_payload: dict[str, Any], case_metadata: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Extract Diagnostic 1 QA and verbatim-completion records."""
    qa = diag1_payload.get("qa_probes", {}) if isinstance(diag1_payload, dict) else {}
    completion = diag1_payload.get("verbatim_completion", {}) if isinstance(diag1_payload, dict) else {}
    qa_details = qa.get("details", []) if isinstance(qa, dict) else []
    completion_details = completion.get("details", []) if isinstance(completion, dict) else []

    qa_rows: list[dict[str, Any]] = []
    for detail in qa_details:
        if not isinstance(detail, dict):
            continue
        score = coerce_float(detail.get("score"))
        if score is None:
            continue
        qa_rows.append(
            {
                "probe_id": str(detail.get("probe_id", "")).strip(),
                "probe_type": str(detail.get("probe_type", "unknown")).strip() or "unknown",
                "score": score,
            }
        )

    completion_rows: list[dict[str, Any]] = []
    for detail in completion_details:
        if not isinstance(detail, dict):
            continue
        case_id = str(detail.get("case_id", "")).strip()
        if not case_id:
            continue
        rouge_l = coerce_float(detail.get("rouge_l"))
        if rouge_l is None:
            continue
        metadata = case_metadata.get(case_id, {})
        completion_rows.append(
            {
                "case_id": case_id,
                "rouge_l": rouge_l,
                "exact_match_ratio": coerce_float(detail.get("exact_match_ratio")),
                "period": normalize_period(detail.get("period") or metadata.get("period")),
                "rarity": normalize_rarity(detail.get("rarity") or metadata.get("rarity")),
            }
        )

    return {
        "qa_overall_score": coerce_float(qa.get("overall_score")),
        "qa_by_probe_type": qa.get("by_probe_type", {}) if isinstance(qa, dict) else {},
        "qa_rows": qa_rows,
        "completion_overall_rouge_l": coerce_float(completion.get("overall_rouge_l")),
        "completion_rows": completion_rows,
    }


def extract_diag2(diag2_payload: dict[str, Any], case_metadata: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Extract Diagnostic 2 case-level CFLS/CPT records and coverage metadata."""
    cases = diag2_payload.get("cases", []) if isinstance(diag2_payload, dict) else []
    errors = diag2_payload.get("errors", []) if isinstance(diag2_payload, dict) else []
    meta = diag2_payload.get("meta", {}) if isinstance(diag2_payload, dict) else {}

    extracted_cases: list[dict[str, Any]] = []
    task_modes: dict[str, Counter[str]] = defaultdict(Counter)

    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id", "")).strip()
        if not case_id:
            continue
        metadata = case_metadata.get(case_id, {})

        direct_task = case.get("tasks", {}).get("direct_prediction.base", {})
        impact_task = case.get("tasks", {}).get("decomposed_impact.base", {})
        direct_mode = str(direct_task.get("cfls", {}).get("mode", "")).strip() or "unknown"
        impact_mode = str(impact_task.get("cfls", {}).get("mode", "")).strip() or "unknown"
        task_modes["direct_prediction.base"][direct_mode] += 1
        task_modes["decomposed_impact.base"][impact_mode] += 1

        cfls_direct = coerce_float(case.get("metrics", {}).get("cfls_direct"))
        cfls_impact = coerce_float(case.get("metrics", {}).get("cfls_impact"))
        fo_flip_direct_raw = case.get("metrics", {}).get("fo_flip_direct")
        fo_flip_impact_raw = case.get("metrics", {}).get("fo_flip_impact")

        flip_direct = bool(fo_flip_direct_raw) if isinstance(fo_flip_direct_raw, bool) else None
        flip_impact = bool(fo_flip_impact_raw) if isinstance(fo_flip_impact_raw, bool) else None

        cfls_values = [value for value in (cfls_direct, cfls_impact) if value is not None]
        flip_values = [value for value in (flip_direct, flip_impact) if value is not None]
        any_flip = any(flip_values) if flip_values else None

        extracted_cases.append(
            {
                "case_id": case_id,
                "period": normalize_period(case.get("period") or metadata.get("period")),
                "rarity": normalize_rarity(case.get("rarity_estimate") or metadata.get("rarity")),
                "target_type": str(case.get("target_type", "")).strip() or "unknown",
                "category": str(case.get("category", "")).strip() or "unknown",
                "memorization_likelihood": str(case.get("memorization_likelihood", "")).strip() or "unknown",
                "cfls_direct": cfls_direct,
                "cfls_impact": cfls_impact,
                "cfls_mean": mean(cfls_values),
                "fo_flip_direct": flip_direct,
                "fo_flip_impact": flip_impact,
                "any_flip": any_flip,
                "direct_mode": direct_mode,
                "impact_mode": impact_mode,
            }
        )

    return {
        "cases": extracted_cases,
        "meta": meta,
        "n_errors": len(errors) if isinstance(errors, list) else 0,
        "task_modes": {task_id: dict(counter) for task_id, counter in task_modes.items()},
    }


def analyze_qa_baseline(diag1: dict[str, Any]) -> dict[str, Any]:
    """Analysis 1: QA memorization baseline."""
    qa_rows = diag1["qa_rows"]
    scores = [row["score"] for row in qa_rows]
    by_probe_type: dict[str, list[float]] = defaultdict(list)
    for row in qa_rows:
        by_probe_type[row["probe_type"]].append(row["score"])

    probe_type_rows = []
    for probe_type in sorted(by_probe_type, key=probe_type_sort_key):
        values = by_probe_type[probe_type]
        probe_type_rows.append(
            {
                "probe_type": probe_type,
                "n": len(values),
                "mean_score": mean(values),
                "median_score": median(values),
            }
        )

    score_distribution = Counter(str(row["score"]) for row in qa_rows)
    overall_score = diag1["qa_overall_score"]
    if overall_score is None:
        overall_score = mean(scores)

    interpretation = "Insufficient data to assess QA memorization baseline."
    if overall_score is not None:
        if overall_score >= 0.75:
            interpretation = (
                "Strong QA baseline: the model appears to retain substantial parametric "
                "knowledge about A-share markets even without article context."
            )
        elif overall_score >= 0.45:
            interpretation = (
                "Moderate QA baseline: the model has non-trivial parametric knowledge "
                "about A-share markets, but recall is selective rather than near-complete."
            )
        else:
            interpretation = (
                "Weak QA baseline: the model shows limited direct parametric recall on "
                "these market probes."
            )

    return {
        "overall_score": overall_score,
        "n_probes": len(qa_rows),
        "probe_type_rows": probe_type_rows,
        "score_distribution": {
            "1.0": score_distribution.get("1.0", 0),
            "0.5": score_distribution.get("0.5", 0),
            "0.0": score_distribution.get("0.0", 0),
        },
        "interpretation": interpretation,
    }


def analyze_verbatim_completion(diag1: dict[str, Any]) -> dict[str, Any]:
    """Analysis 2: verbatim completion temporal split with rarity stratification."""
    completion_rows = diag1["completion_rows"]
    pre_values = [row["rouge_l"] for row in completion_rows if row["period"] == "pre_cutoff"]
    post_values = [row["rouge_l"] for row in completion_rows if row["period"] == "post_cutoff"]
    overall_test = mann_whitney_result(pre_values, post_values, "pre_cutoff", "post_cutoff")

    by_rarity_rows = []
    rarity_tests: dict[str, dict[str, Any]] = {}
    for rarity in RARITY_ORDER:
        rarity_rows = [row for row in completion_rows if row["rarity"] == rarity]
        rarity_pre = [row["rouge_l"] for row in rarity_rows if row["period"] == "pre_cutoff"]
        rarity_post = [row["rouge_l"] for row in rarity_rows if row["period"] == "post_cutoff"]
        rarity_test = mann_whitney_result(rarity_pre, rarity_post, "pre_cutoff", "post_cutoff")
        rarity_tests[rarity] = rarity_test
        by_rarity_rows.append(
            {
                "rarity": rarity,
                "pre_n": rarity_test["group_a"]["n"],
                "pre_mean": rarity_test["group_a"]["mean"],
                "post_n": rarity_test["group_b"]["n"],
                "post_mean": rarity_test["group_b"]["mean"],
                "mean_difference": rarity_test["mean_difference"],
                "u_statistic": rarity_test["statistic"],
                "p_value": rarity_test["p_value"],
                "effect_size": rarity_test["effect_size"],
            }
        )

    interpretation = "Verbatim completion split is unavailable."
    if overall_test["available"]:
        mean_diff = overall_test["mean_difference"] or 0.0
        if mean_diff > 0 and overall_test["p_value"] is not None and overall_test["p_value"] < 0.05:
            interpretation = (
                "Pre-cutoff ROUGE-L is materially higher than post-cutoff ROUGE-L, "
                "which is consistent with text-level memorization rather than generic completion ability."
            )
        elif abs(mean_diff) <= 0.02 or (
            overall_test["p_value"] is not None and overall_test["p_value"] >= 0.05
        ):
            interpretation = (
                "Pre- and post-cutoff ROUGE-L are similar, which suggests the model is "
                "producing plausible continuations without strong verbatim recall."
            )
        else:
            interpretation = (
                "The temporal split is directionally informative but not definitive; "
                "the model may mix weak memorization with generic news-style continuation."
            )

    return {
        "overall_test": overall_test,
        "rarity_temporal_tests": rarity_tests,
        "rarity_temporal_rows": by_rarity_rows,
        "interpretation": interpretation,
        "n_cases": len(completion_rows),
    }


def analyze_cfls_temporal(diag2: dict[str, Any]) -> dict[str, Any]:
    """Analysis 3: CFLS temporal split by task."""
    cases = diag2["cases"]
    measures = {
        "direct_prediction.base": "cfls_direct",
        "decomposed_impact.base": "cfls_impact",
        "mean_across_tasks": "cfls_mean",
    }

    tests: dict[str, dict[str, Any]] = {}
    coverage_rows = []
    for task_id, field in measures.items():
        pre_values = [
            row[field]
            for row in cases
            if row["period"] == "pre_cutoff" and row[field] is not None
        ]
        post_values = [
            row[field]
            for row in cases
            if row["period"] == "post_cutoff" and row[field] is not None
        ]
        tests[task_id] = mann_whitney_result(pre_values, post_values, "pre_cutoff", "post_cutoff")
        coverage_rows.append(
            {
                "task": task_label(task_id),
                "pre_scored": len(pre_values),
                "pre_total": sum(1 for row in cases if row["period"] == "pre_cutoff"),
                "post_scored": len(post_values),
                "post_total": sum(1 for row in cases if row["period"] == "post_cutoff"),
                "overall_scored": len(pre_values) + len(post_values),
                "overall_total": sum(1 for row in cases if row["period"] in PERIOD_ORDER),
            }
        )

    interpretation = (
        "CFLS temporal split is unavailable."
        if not tests["mean_across_tasks"]["available"]
        else ""
    )
    if not interpretation:
        direct = tests["direct_prediction.base"]
        impact = tests["decomposed_impact.base"]
        pre_floor = all(
            (test["group_a"]["mean"] is not None and test["group_a"]["mean"] <= 0.0)
            for test in (direct, impact)
            if test["available"]
        )
        post_floor = all(
            (test["group_b"]["mean"] is not None and test["group_b"]["mean"] <= 0.0)
            for test in (direct, impact)
            if test["available"]
        )
        no_task_shift = all(
            (test["p_value"] is None or test["p_value"] >= 0.05)
            for test in (direct, impact)
            if test["available"]
        )
        if pre_floor and post_floor and no_task_shift:
            interpretation = (
                "The CFLS floor effect persists for post-cutoff events. That pattern is "
                "more consistent with a general article-responsiveness floor than with pre-cutoff-only memorization."
            )
        elif any(
            (test["group_a"]["mean"] or 0.0) > (test["group_b"]["mean"] or 0.0)
            and (test["p_value"] is not None and test["p_value"] < 0.05)
            for test in (direct, impact)
            if test["available"]
        ):
            interpretation = (
                "Pre-cutoff CFLS is higher than post-cutoff CFLS on at least one task, "
                "which is consistent with stronger memorization-sensitive behavior on older events."
            )
        else:
            interpretation = (
                "The CFLS temporal pattern is mixed; the floor effect weakens in some slices "
                "but does not cleanly separate pre- and post-cutoff events."
            )

    return {
        "tests": tests,
        "coverage_rows": coverage_rows,
        "task_modes": diag2["task_modes"],
        "interpretation": interpretation,
    }
