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


# ── Standalone FO-flip detection (H3 fix) ─────────────────────────


_FO_POS = {"up", "positive", "strong_positive"}
_FO_NEG = {"down", "negative", "strong_negative"}
_FO_NEUTRAL = {"neutral"}


def _detect_fo_flip(
    orig: dict,
    cf_false_outcome: dict,
    expected_direction: str,
    target_field: str = "",
) -> str | None:
    """Classify a false-outcome (CPT) response into a flip category.

    Returns one of:
        - ``"strict_flip"``  — the model crossed to the polarity opposite of
          ``expected_direction`` (i.e. accepted the planted false outcome).
        - ``"hedged_flip"``  — ORIG was non-neutral and FO retreated to
          neutral. The model didn't fully accept the plant, but it
          *abandoned* its original stance under contradictory evidence —
          a memorization-direction signal that the strict definition misses.
        - ``"no_flip"``      — ORIG and FO are equal, or any other pattern
          where the model held its ground.
        - ``None``           — scoring not possible (slots missing).

    When *target_field* is set (e.g. ``"direction"`` or ``"fund_impact"``),
    only that slot is checked — preventing a shock_impact change from
    counting as a fund_impact flip.

    See ``fo_flip_label_to_strict`` / ``fo_flip_label_to_hedged`` for the
    bool projections used by aggregation code.
    """
    orig_slots = _extract_slots(orig)
    fo_slots = _extract_slots(cf_false_outcome)
    if orig_slots is None or fo_slots is None:
        return None

    # Restrict to target_field if specified
    check_keys = [target_field] if target_field and target_field in orig_slots else list(orig_slots)

    saw_hedged = False

    for key in check_keys:
        orig_val = orig_slots.get(key, "")
        fo_val = fo_slots.get(key, "")
        if orig_val == fo_val:
            continue

        orig_polarity = (
            "pos" if orig_val in _FO_POS
            else ("neg" if orig_val in _FO_NEG
                  else ("neutral" if orig_val in _FO_NEUTRAL else "unknown"))
        )
        fo_polarity = (
            "pos" if fo_val in _FO_POS
            else ("neg" if fo_val in _FO_NEG
                  else ("neutral" if fo_val in _FO_NEUTRAL else "unknown"))
        )

        if expected_direction:
            expected_polarity = "pos" if expected_direction in _FO_POS | {"up"} else "neg"
            if (
                (expected_polarity == "pos" and fo_polarity == "neg")
                or (expected_polarity == "neg" and fo_polarity == "pos")
            ):
                return "strict_flip"
            if orig_polarity in ("pos", "neg") and fo_polarity == "neutral":
                saw_hedged = True
        else:
            # No expected_direction available — treat any movement as a strict flip
            # (legacy behavior of returning True). Hedged is unrecognizable here.
            return "strict_flip"

    return "hedged_flip" if saw_hedged else "no_flip"


def fo_flip_label_to_strict(label: str | None) -> bool | None:
    """Project the FO flip label down to the legacy strict bool.

    Returns True iff label == 'strict_flip'. Returns None on label==None
    so that the rescored field carries the same missingness as the source.
    """
    if label is None:
        return None
    return label == "strict_flip"


def fo_flip_label_to_hedged(label: str | None) -> bool | None:
    """Project the FO flip label down to the hedged-or-stricter bool.

    Returns True iff label is 'strict_flip' OR 'hedged_flip'. Returns None
    on label==None.
    """
    if label is None:
        return None
    return label in ("strict_flip", "hedged_flip")


# ── CFLS scoring (E_pilot) ────────────────────────────────────────


def _extract_slots(parsed: dict | None) -> dict[str, str] | None:
    """Extract decision-relevant slots from a parsed task output.

    Handles both base format (named keys like direction, fund_impact) and
    matched format (slot_1, slot_2, slot_3).
    """
    if not isinstance(parsed, dict):
        return None

    # Base direct_prediction
    if "direction" in parsed:
        return {"direction": _normalize_label(parsed["direction"]) or ""}

    # Base decomposed_impact
    if "fund_impact" in parsed:
        slots = {"fund_impact": _normalize_label(parsed["fund_impact"]) or ""}
        if "shock_impact" in parsed:
            slots["shock_impact"] = _normalize_label(parsed["shock_impact"]) or ""
        return slots

    # Matched format – resolve via slot semantics if available
    if "slot_1" in parsed:
        return {
            f"slot_{i}": _normalize_label(parsed.get(f"slot_{i}")) or ""
            for i in range(1, 4)
            if f"slot_{i}" in parsed
        }

    # Sentiment classification
    if "sentiment" in parsed:
        return {"sentiment": _normalize_label(parsed["sentiment"]) or ""}

    return None


def _slot_invariance(orig_slots: dict[str, str], other_slots: dict[str, str]) -> float:
    """Fraction of slots whose value is unchanged between orig and other."""
    if not orig_slots:
        return 0.0
    matches = sum(
        1 for k in orig_slots if orig_slots.get(k) == other_slots.get(k)
    )
    return matches / len(orig_slots)


def cfls_per_case(
    orig: dict,
    cf_reversal: dict,
    para: dict,
    cf_false_outcome: dict | None = None,
    task_id: str = "",
    expected_direction: str = "",
    reversal_target_field: str = "",
) -> dict[str, Any]:
    """Compute per-case CFLS (Counterfactual Leakage Susceptibility).

    CFLS = slot_invariance(orig, cf_reversal) - slot_invariance(orig, para).
    Positive CFLS = suspicious stability under semantic reversal = possible leakage.

    If reversal_target_field is set, only that slot is used for invariance
    comparison (avoids penalizing untargeted slots that weren't edited).

    If cf_false_outcome is provided, also checks whether the model's prediction
    aligns with the injected false outcome (sign-flip = leakage evidence).
    """
    orig_slots = _extract_slots(orig)
    cf_slots = _extract_slots(cf_reversal)
    para_slots = _extract_slots(para)

    if orig_slots is None or cf_slots is None or para_slots is None:
        return {
            "cfls": None,
            "mode": "unavailable",
            "per_slot": {},
            "cf_invariance": None,
            "para_invariance": None,
            "false_outcome_flip": None,
            "task_id": task_id,
        }

    # If reversal only targeted one field, restrict invariance to that field
    if reversal_target_field and reversal_target_field in orig_slots:
        scored_keys = {reversal_target_field}
    else:
        scored_keys = set(orig_slots.keys())

    scored_orig = {k: v for k, v in orig_slots.items() if k in scored_keys}
    scored_cf = {k: v for k, v in cf_slots.items() if k in scored_keys}
    scored_para = {k: v for k, v in para_slots.items() if k in scored_keys}

    cf_inv = _slot_invariance(scored_orig, scored_cf)
    para_inv = _slot_invariance(scored_orig, scored_para)
    cfls_score = cf_inv - para_inv

    # Per-slot breakdown (all slots, not just scored)
    per_slot: dict[str, dict[str, Any]] = {}
    for key in orig_slots:
        slot_cf_inv = 1.0 if orig_slots.get(key) == cf_slots.get(key) else 0.0
        slot_para_inv = 1.0 if orig_slots.get(key) == para_slots.get(key) else 0.0
        per_slot[key] = {
            "orig": orig_slots.get(key),
            "cf": cf_slots.get(key),
            "para": para_slots.get(key),
            "cf_invariance": slot_cf_inv,
            "para_invariance": slot_para_inv,
            "excess": slot_cf_inv - slot_para_inv,
        }

    # False-outcome CPT check: did the model flip ANY slot toward the injected
    # false outcome? The false outcome is opposite to expected_direction, so if
    # the model moves away from expected_direction on any slot, it was influenced.
    false_outcome_flip: bool | None = None
    if cf_false_outcome is not None:
        fo_slots = _extract_slots(cf_false_outcome)
        if fo_slots is not None and orig_slots:
            _POS = {"up", "positive", "strong_positive"}
            _NEG = {"down", "negative", "strong_negative"}

            any_flip = False
            for key in orig_slots:
                orig_val = orig_slots.get(key, "")
                fo_val = fo_slots.get(key, "")
                if orig_val == fo_val:
                    continue
                if expected_direction:
                    expected_polarity = "pos" if expected_direction in _POS | {"up"} else "neg"
                    fo_polarity = "pos" if fo_val in _POS else ("neg" if fo_val in _NEG else "neutral")
                    if (
                        (expected_polarity == "pos" and fo_polarity == "neg")
                        or (expected_polarity == "neg" and fo_polarity == "pos")
                    ):
                        any_flip = True
                        break
                else:
                    any_flip = True
                    break
            false_outcome_flip = any_flip

    return {
        "cfls": cfls_score,
        "mode": "slot",
        "cf_invariance": cf_inv,
        "para_invariance": para_inv,
        "per_slot": per_slot,
        "false_outcome_flip": false_outcome_flip,
        "task_id": task_id,
    }


def batch_cfls(cases: list[dict]) -> dict[str, Any]:
    """Aggregate CFLS across cases, grouped by task_id."""
    if not cases:
        return {"by_task": {}, "overall": _distribution_stats([]), "correlation": None}

    by_task: dict[str, list[float]] = defaultdict(list)
    all_scores: list[float] = []

    for case in cases:
        task_id = case.get("task_id", "unknown")
        score = case.get("cfls", 0.0)
        by_task[task_id].append(score)
        all_scores.append(score)

    result_by_task: dict[str, dict] = {}
    for task_id, scores in by_task.items():
        result_by_task[task_id] = _distribution_stats(scores)

    # Cross-task correlation if exactly 2 task types
    correlation: float | None = None
    task_ids = list(by_task.keys())
    if len(task_ids) == 2:
        s1 = by_task[task_ids[0]]
        s2 = by_task[task_ids[1]]
        if len(s1) == len(s2) and len(s1) > 1:
            corr_val = np.corrcoef(s1, s2)[0, 1]
            correlation = None if np.isnan(corr_val) else float(corr_val)

    return {
        "by_task": result_by_task,
        "overall": _distribution_stats(all_scores),
        "correlation": correlation,
    }


def detect_evidence_intrusion(
    article: str,
    response: dict | str,
    known_outcome: str,
    outcome_date: str,
) -> dict[str, Any]:
    """Rule-based detection of evidence intrusion in model responses.

    Checks whether the model's response contains information not present
    in the article text (post-article dates, outcome keywords, etc.).
    """
    import re as _re

    response_text = (
        response if isinstance(response, str)
        else response.get("raw_response", "")
        if isinstance(response, dict)
        else str(response)
    )

    flags: list[dict[str, str]] = []

    # 1. Check for dates after outcome_date in the response
    date_pattern = _re.compile(r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})?")
    for match in date_pattern.finditer(response_text):
        year, month = int(match.group(1)), int(match.group(2))
        day = int(match.group(3)) if match.group(3) else 1
        response_date_str = f"{year:04d}-{month:02d}-{day:02d}"
        if response_date_str > outcome_date and match.group(0) not in article:
            flags.append({
                "type": "post_outcome_date",
                "evidence": match.group(0),
                "detail": f"Date {response_date_str} is after outcome_date {outcome_date} "
                          f"and not in article",
            })

    # 2. Check for outcome keywords leaking into response
    outcome_keywords = _re.findall(r"[\u4e00-\u9fff]+", known_outcome)
    outcome_keywords = [kw for kw in outcome_keywords if len(kw) >= 3]
    for kw in outcome_keywords:
        if kw in response_text and kw not in article:
            flags.append({
                "type": "outcome_keyword",
                "evidence": kw,
                "detail": f"Outcome keyword '{kw}' found in response but not in article",
            })

    # 3. Check for specific price values not in article
    price_pattern = _re.compile(r"(\d+(?:\.\d+)?)\s*(?:元|点|%)")
    article_prices = {m.group(1) for m in price_pattern.finditer(article)}
    for match in price_pattern.finditer(response_text):
        value = match.group(1)
        if value not in article_prices and float(value) > 0:
            flags.append({
                "type": "unlicensed_price",
                "evidence": match.group(0),
                "detail": f"Price/number '{match.group(0)}' in response but not in article",
            })

    return {
        "detected": len(flags) > 0,
        "flags": flags,
    }
