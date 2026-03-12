"""Leakage metrics: PC, CI, IDS, OLR, Shapley-DCLR.

Implements core metrics from Profit Mirage (Li et al., 2025)
and All Leaks Count (Zhang et al., 2026).
"""

from __future__ import annotations

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
