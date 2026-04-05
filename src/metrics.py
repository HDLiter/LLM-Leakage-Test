"""Leakage metrics: PC, CI, IDS, OLR, Shapley-DCLR.

Implements core metrics from Profit Mirage (Li et al., 2025)
and All Leaks Count (Zhang et al., 2026).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
from scipy.special import rel_entr


def prediction_consistency(orig_preds: list[str], cf_preds: list[str]) -> float:
    """PC = (1/N) * Σ I[ŷ_orig == ŷ_cf].

    High PC = high leakage (predictions unchanged despite counterfactual input).
    """
    if not orig_preds:
        return 0.0
    matches = sum(1 for o, c in zip(orig_preds, cf_preds) if o == c)
    return matches / len(orig_preds)


def confidence_invariance(
    orig_confs: list[float],
    cf_confs: list[float],
    consistent_mask: list[bool] | None = None,
) -> float:
    """CI = 1 - (1/M) * Σ|s_orig - s_cf| for consistent predictions.

    CI → 1 = confidence unchanged = high leakage.
    If consistent_mask is None, compute over all pairs.
    """
    if consistent_mask is not None:
        pairs = [(o, c) for o, c, m in zip(orig_confs, cf_confs, consistent_mask) if m]
    else:
        pairs = list(zip(orig_confs, cf_confs))

    if not pairs:
        return 0.0
    diffs = [abs(o - c) for o, c in pairs]
    return 1.0 - np.mean(diffs)


def input_dependency_score(
    orig_dists: list[list[float]],
    cf_dists: list[list[float]],
    epsilon: float = 1e-10,
) -> float:
    """IDS = (1/N) * Σ D_KL(P_orig ∥ P_cf).

    High IDS = low leakage (model is sensitive to input changes).
    """
    if not orig_dists:
        return 0.0

    kl_scores = []
    for p, q in zip(orig_dists, cf_dists):
        p_arr = np.array(p, dtype=np.float64) + epsilon
        q_arr = np.array(q, dtype=np.float64) + epsilon
        # Normalize
        p_arr /= p_arr.sum()
        q_arr /= q_arr.sum()
        kl = float(np.sum(rel_entr(p_arr, q_arr)))
        kl_scores.append(kl)
    return float(np.mean(kl_scores))


def overall_leakage_rate(claims_leaked: list[bool]) -> float:
    """OLR = leaked_claims / total_claims.

    From All Leaks Count (Zhang et al., 2026).
    """
    if not claims_leaked:
        return 0.0
    return sum(claims_leaked) / len(claims_leaked)


def shapley_dclr(
    shapley_values: list[float],
    leaked_flags: list[bool],
) -> float:
    """Shapley-weighted Decision-Critical Leakage Rate.

    DCLR = Σ|ϕ_i|·ℓ(c_i) / Σ|ϕ_i|
    where ϕ_i is the Shapley value and ℓ(c_i) ∈ {0,1} is the leak flag.
    """
    if not shapley_values:
        return 0.0
    abs_phi = [abs(v) for v in shapley_values]
    total = sum(abs_phi)
    if total == 0:
        return 0.0
    weighted = sum(p * int(l) for p, l in zip(abs_phi, leaked_flags))
    return weighted / total


def composite_leakage_score(
    pc: float,
    ci: float,
    ids: float,
    alpha: float = 0.4,
    beta: float = 0.3,
    gamma: float = 0.3,
) -> float:
    """Composite leakage score L = α·PC + β·CI - γ·IDS.

    Lower is better (less leakage). Inspired by FactFin objective.
    """
    return alpha * pc + beta * ci - gamma * ids


def lap_score(log_probs: list[float], k_pct: float = 0.2) -> float:
    """Lookahead Propensity (LAP) from Gao et al., 2026.

    LAP = exp((1/|S_K|) * Σ log P(w_n | w_<n)) for bottom K% tokens.
    Higher LAP = more likely in training data = more memorization.
    """
    if not log_probs:
        return 0.0
    k = max(1, int(len(log_probs) * k_pct))
    sorted_probs = sorted(log_probs)
    bottom_k = sorted_probs[:k]
    return float(np.exp(np.mean(bottom_k)))


def _field_value(obj: Any, *keys: str) -> Any:
    """Read the first available field from a dict-like or object response."""
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            return obj[key]
        if hasattr(obj, key):
            return getattr(obj, key)
    return None


def _normalize_label(label: Any) -> str | None:
    if label is None:
        return None
    if hasattr(label, "value"):
        label = label.value
    if isinstance(label, str):
        normalized = label.strip().lower()
        return normalized or None
    return str(label).strip().lower() or None


def _direction_from_distribution(distribution: Any) -> str | None:
    if distribution is None:
        return None

    direction = _field_value(distribution, "direction")
    if direction is not None:
        return _normalize_label(direction)

    scores = {
        "strong_bear": _field_value(distribution, "strong_bear"),
        "weak_bear": _field_value(distribution, "weak_bear"),
        "neutral": _field_value(distribution, "neutral"),
        "weak_bull": _field_value(distribution, "weak_bull"),
        "strong_bull": _field_value(distribution, "strong_bull"),
    }
    if any(value is None for value in scores.values()):
        return None

    bull = scores["weak_bull"] + scores["strong_bull"]
    bear = scores["weak_bear"] + scores["strong_bear"]
    if bull > bear + 10:
        return "up"
    if bear > bull + 10:
        return "down"
    return "neutral"


def _extract_label(response: Any) -> str | None:
    """Extract the primary categorical label from an LLM response payload."""
    if response is None:
        return None
    if isinstance(response, str):
        return _normalize_label(response)
    if hasattr(response, "value"):
        return _normalize_label(response)

    label = _field_value(response, "parsed_direction", "label", "parsed_label", "direction")
    if label is not None:
        return _normalize_label(label)

    distribution = _field_value(response, "parsed_distribution", "distribution")
    return _direction_from_distribution(distribution)


def _extract_confidence(response: Any) -> float | None:
    """Extract a scalar confidence score from an LLM response payload."""
    if response is None or isinstance(response, bool):
        return None
    if isinstance(response, (int, float)):
        return float(response)

    confidence = _field_value(response, "parsed_confidence", "confidence", "score", "probability")
    if confidence is None:
        return None

    try:
        return float(confidence)
    except (TypeError, ValueError):
        return None


def _confidence_similarity(orig_conf: float, other_conf: float) -> float:
    return float(np.clip(1.0 - abs(orig_conf - other_conf), 0.0, 1.0))


def _excess_invariance_components(
    orig_response: Any,
    cf_response: Any,
    para_response: Any,
) -> dict[str, float | str]:
    """Compute excess invariance and expose the underlying components."""
    orig_label = _extract_label(orig_response)
    cf_label = _extract_label(cf_response)
    para_label = _extract_label(para_response)

    if None not in (orig_label, cf_label, para_label):
        cf_invariance = 1.0 if orig_label == cf_label else 0.0
        para_invariance = 1.0 if orig_label == para_label else 0.0
        return {
            "mode": "label",
            "cf_invariance": cf_invariance,
            "para_invariance": para_invariance,
            "excess_invariance": cf_invariance - para_invariance,
        }

    orig_conf = _extract_confidence(orig_response)
    cf_conf = _extract_confidence(cf_response)
    para_conf = _extract_confidence(para_response)
    if None not in (orig_conf, cf_conf, para_conf):
        cf_invariance = _confidence_similarity(orig_conf, cf_conf)
        para_invariance = _confidence_similarity(orig_conf, para_conf)
        return {
            "mode": "confidence",
            "cf_invariance": cf_invariance,
            "para_invariance": para_invariance,
            "excess_invariance": cf_invariance - para_invariance,
        }

    return {
        "mode": "unavailable",
        "cf_invariance": 0.0,
        "para_invariance": 0.0,
        "excess_invariance": 0.0,
    }


def _distribution_stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "positive_rate": 0.0,
            "negative_rate": 0.0,
            "zero_rate": 0.0,
        }

    arr = np.array(values, dtype=np.float64)
    return {
        "count": int(arr.size),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "median": float(np.median(arr)),
        "positive_rate": float(np.mean(arr > 0)),
        "negative_rate": float(np.mean(arr < 0)),
        "zero_rate": float(np.mean(arr == 0)),
    }


def excess_invariance(orig_response: Any, cf_response: Any, para_response: Any) -> float:
    """Excess invariance under semantic edits relative to neutral paraphrases.

    Positive values indicate suspicious stability under counterfactual edits
    beyond the expected stability under paraphrase-only rewrites.
    """
    return float(
        _excess_invariance_components(
            orig_response=orig_response,
            cf_response=cf_response,
            para_response=para_response,
        )["excess_invariance"]
    )


def batch_excess_invariance(results: list[dict]) -> dict[str, Any]:
    """Aggregate excess invariance over task-level result dictionaries."""
    if not results:
        return {
            "mean_excess_invariance": 0.0,
            "per_task": [],
            "distribution": _distribution_stats([]),
        }

    per_task: list[dict[str, Any]] = []
    scores: list[float] = []
    for result in results:
        task_id = _field_value(result, "task_id", "test_case_id", "id")
        components = _excess_invariance_components(
            orig_response=_field_value(result, "orig_response", "original_response"),
            cf_response=_field_value(result, "cf_response", "counterfactual_response"),
            para_response=_field_value(result, "para_response", "paraphrase_response"),
        )
        score = float(components["excess_invariance"])
        scores.append(score)
        per_task.append(
            {
                "task_id": task_id,
                "mode": components["mode"],
                "cf_invariance": float(components["cf_invariance"]),
                "para_invariance": float(components["para_invariance"]),
                "excess_invariance": score,
            }
        )

    return {
        "mean_excess_invariance": float(np.mean(scores)) if scores else 0.0,
        "per_task": per_task,
        "distribution": _distribution_stats(scores),
    }


def excess_invariance_by_task(results: list[dict], task_types: list[str]) -> dict[str, float]:
    """Primary E3 metric: mean excess invariance grouped by task type."""
    if len(results) != len(task_types):
        raise ValueError("results and task_types must have the same length")

    grouped_scores: dict[str, list[float]] = defaultdict(list)
    for result, task_type in zip(results, task_types):
        grouped_scores[task_type].append(
            excess_invariance(
                orig_response=_field_value(result, "orig_response", "original_response"),
                cf_response=_field_value(result, "cf_response", "counterfactual_response"),
                para_response=_field_value(result, "para_response", "paraphrase_response"),
            )
        )

    return {
        task_type: float(np.mean(scores)) if scores else 0.0
        for task_type, scores in grouped_scores.items()
    }
