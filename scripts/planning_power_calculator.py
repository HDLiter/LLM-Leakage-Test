"""Closed-form Phase 8 *planning* power calculator (NOT the §8.8 simulation).

This is a closed-form planner for design-time scenario sweep, NOT the
§8.8 Monte-Carlo simulation. For prereg-grade power claims see the
§8.8 MC simulator (deferred to post-pilot; needs pilot `hat(beta)` +
`hat(Sigma)` to calibrate). Per
`refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`
decision #3 (the "two-tool model"): keep this calculator closed-form
and pin the post-pilot MC simulator separately so the two cannot be
confused. Cross-reference: plan §8.8.

Per Tier-0 #10 (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`)
+ Statistical lens §1: the prior simulation hard-coded `N_model = 9` and
must be updated to the actual design:

  * 14 P_predict-eligible models (E_CMMD / E_OR / E_NoOp)
  * 12 P_logprob-eligible models (E_CTS, capacity curves)
  * 2 confirmatory PCSG temporal pairs (Qwen + Llama, both 1 pair each)
  * Model-family random intercepts (Qwen2.5 / Qwen3 / GLM / Llama / API)
  * PCSG vocab-eligibility distribution centered on ~0.98 (Statistical
    lens §5: real CLS Chinese financial news rarely contains Qwen3
    tool-use tokens; original 50-90% prior was wrong).

The calculator computes pooled standard errors under the planning prior
and applies a 2.8-z Westfall-Young-effective critical value (per
Statistical lens §1). All SEs are closed-form: this script does NOT
run a Monte-Carlo loop; the §8.8 simulator does. The `--b-outer` flag
is retained for caller compatibility but is informational only.

Outputs a power table per (scenario, family-state, effect-size,
PCSG-eligibility) cell. Family-state was previously {S20, S16a, S16b,
S12}; per `docs/DECISION_20260429_gate_removal.md` §3.1 only S20
remains, so the cardinality of family-state collapses to 1. The
parameter is retained for dial-back compatibility but defaults to
`{"S20"}`.

Usage:

    python scripts/planning_power_calculator.py \\
        --output data/pilot/analysis/phase8_planning.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# Family random-intercept structure for the post-Llama fleet
# (DECISION_20260429_llama_addition §2.2). Counts here are P_logprob-
# eligible per family; for P_predict the Llama family contributes 0.
FAMILY_P_LOGPROB = {
    "qwen2.5": 5,   # 1.5/3/7/14/32 B AWQ
    "qwen3": 4,     # 4/8/14/32 B AWQ
    "llama":  2,    # 3-8B + 3.1-8B bf16 (DECISION_20260429)
    "glm":    1,    # 9B fp16
}
FAMILY_P_PREDICT = {
    "qwen2.5": 5,
    "qwen3":   4,
    "glm":     1,
    "api":     4,   # deepseek + gpt-4.1 + gpt-5.1 + claude
}

# Westfall-Young-effective critical value over the 20-coefficient
# confirmatory family (5 estimands × 4 factors). 2.8 matches the
# back-of-envelope in Statistical lens §1; the actual stepdown max-T
# critical value depends on the cross-coefficient correlation matrix
# and is computed at run time from the pilot covariance, but 2.8 is
# the planning anchor.
Z_WY = 2.8

# Default planning effect-size grid (standardized SDs).
DEFAULT_EFFECTS = (0.10, 0.15, 0.20, 0.30)

# Default scenarios per Statistical §1 + plan §8.8.
DEFAULT_SCENARIOS = ("unweighted_pilot", "reweighted_phase8", "shrinkage_0.5")

# Default fleet-noise inflation factors (CMMD only — pooled across 14
# heterogeneous models).
DEFAULT_CMMD_INFLATION = (1.0, 1.2, 1.35)

# Default PCSG vocab-eligibility values to sweep. Statistical §5 says
# real CLS Chinese financial news has ~98-100% eligibility (Qwen3
# extension tokens almost never appear). 0.95 / 0.85 / 0.75 retained
# as stress tests.
DEFAULT_PCSG_ELIGIBILITY = (0.98, 0.95, 0.85, 0.75)


@dataclass(frozen=True)
class FleetSummary:
    n_p_predict: int
    n_p_logprob: int
    n_temporal_pcsg_pairs: int
    family_p_logprob: dict[str, int]
    family_p_predict: dict[str, int]


def _fleet_summary() -> FleetSummary:
    return FleetSummary(
        n_p_predict=sum(FAMILY_P_PREDICT.values()),
        n_p_logprob=sum(FAMILY_P_LOGPROB.values()),
        # 2026-04-29 confirmatory: Qwen-cross-version + Llama-cross-version
        n_temporal_pcsg_pairs=2,
        family_p_logprob=FAMILY_P_LOGPROB,
        family_p_predict=FAMILY_P_PREDICT,
    )


def _wy_power(beta: float, se: float, z_wy: float = Z_WY) -> float:
    """Approximate stepdown max-T-adjusted power under a normal sampling
    distribution: P(|Z| > z_wy | true effect = beta/se).

    Returns the larger-tail rejection probability (one-sided in the
    sign of beta + tail probability of the wrong-sign rejection).
    """
    if se <= 0:
        return 1.0 if beta != 0 else 0.0
    z = beta / se
    from scipy.stats import norm  # local import; scipy is already in env

    # P(|Z + z| > z_wy) where Z ~ N(0,1)
    return float(norm.sf(z_wy - z) + norm.cdf(-z_wy - z))


def _se_with_family_intercepts(
    n_case: int,
    n_models: int,
    sigma_within: float,
    sigma_model: float,
    sigma_family: float,
    n_families: int,
) -> float:
    """Approximate SE for a fleet-pooled coefficient with case
    (`sigma_within`), model-random-intercept (`sigma_model`), and
    family-random-intercept (`sigma_family`) variance components.

    Total variance per (case, model) cell: σ_w² + σ_m² + σ_f². With
    `n_case * n_models` independent (case, model) cells but model and
    family intercepts shared across cases:

      Var(β̂) ≈ (σ_w²/n_case + σ_m²) / n_models + σ_f² / n_families
    """
    total_within = sigma_within ** 2 / max(n_case, 1)
    total_model = sigma_model ** 2
    var_pooled = (total_within + total_model) / max(n_models, 1)
    var_family = sigma_family ** 2 / max(n_families, 1)
    return math.sqrt(var_pooled + var_family)


def _se_pcsg_pair(
    n_case: int,
    n_pairs: int,
    eligibility: float,
    sigma_pair_residual: float,
) -> float:
    """Approximate SE for the PCSG cutoff coefficient pooled over
    `n_pairs` confirmatory pairs.

    Eligibility shrinks effective n: `n_eff = n_case × eligibility`.
    Adding a 2nd pair reduces SE by roughly √(n_pairs/n_pair_in_design).
    """
    n_eff = max(int(n_case * eligibility), 1)
    return sigma_pair_residual / math.sqrt(n_eff * max(n_pairs, 1))


def _scenario_multiplier(scenario: str, beta: float) -> float:
    """Adjust the effect by scenario per plan §8.8 prior construction."""
    if scenario == "unweighted_pilot":
        return beta
    if scenario == "reweighted_phase8":
        # Light reweight; we model it as a 0.85x shrink because pilot
        # composition over-represents factor-rich cells.
        return beta * 0.85
    if scenario == "shrinkage_0.5":
        return beta * 0.5
    raise ValueError(f"unknown scenario {scenario!r}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Phase 8 closed-form planning power calculator (R5A v2.1)"
    )
    p.add_argument(
        "--output",
        default="data/pilot/analysis/phase8_planning.json",
        help="JSON output path",
    )
    p.add_argument(
        "--b-outer",
        type=int,
        default=2000,
        help=(
            "informational only; closed-form planner does not run a "
            "Monte Carlo loop. The §8.8 post-pilot MC simulator (separate "
            "tool) is the place to spend MC replicates."
        ),
    )
    p.add_argument("--seed", type=int, default=20260417)
    p.add_argument(
        "--n-case-pilot",
        type=int,
        default=80,
        help="pre-cutoff pilot case count for E_PCSG / E_CTS",
    )
    p.add_argument(
        "--n-case-main-pre",
        type=int,
        default=2048,
        help="pre-cutoff main-run case count for E_PCSG",
    )
    p.add_argument(
        "--n-case-main-total",
        type=int,
        default=2560,
        help="total main-run case count (E_CMMD / E_OR / E_NoOp)",
    )
    p.add_argument(
        "--n-case-bl2-post",
        type=int,
        default=350,
        help=(
            "BL2 post-cutoff case count "
            "(DECISION_20260429_gate_removal §3.3 = 350)"
        ),
    )
    p.add_argument(
        "--effects",
        nargs="*",
        type=float,
        default=DEFAULT_EFFECTS,
    )
    p.add_argument(
        "--scenarios",
        nargs="*",
        default=list(DEFAULT_SCENARIOS),
    )
    p.add_argument(
        "--cmmd-inflation",
        nargs="*",
        type=float,
        default=DEFAULT_CMMD_INFLATION,
    )
    p.add_argument(
        "--pcsg-eligibility",
        nargs="*",
        type=float,
        default=DEFAULT_PCSG_ELIGIBILITY,
    )
    p.add_argument(
        "--family-states",
        nargs="*",
        default=["S20"],
        help=(
            "Stage 2 family states. Per "
            "`docs/DECISION_20260429_gate_removal.md` §3.1 only S20 "
            "remains legal, but the loop axis is retained for dial-back."
        ),
    )
    return p.parse_args()


def _simulate_estimand_powers(args: argparse.Namespace) -> list[dict]:
    fleet = _fleet_summary()
    rows: list[dict] = []
    for scenario in args.scenarios:
        for family_state in args.family_states:
            for beta in args.effects:
                effect_eff = _scenario_multiplier(scenario, beta)
                # E_CMMD: fleet-aggregated case-level (per plan §8.2 /
                # §8.1A). Closed-form case-level SE under iid-case
                # assumption: this is the analytic limit of a case-
                # cluster bootstrap when within-case correlation is
                # absorbed by fleet aggregation — E_CMMD averages over
                # 14 P_predict models per case BEFORE the regression,
                # so the residual lives at case level. For non-iid or
                # heavy-tailed pilot residuals, the §8.8 post-pilot MC
                # simulator runs an actual case-cluster bootstrap; this
                # planning calculator stays closed-form by design
                # (DECISIONS.md decision #3 "two-tool model";
                # PENDING.md tracks the post-pilot MC implementation).
                for cmmd_inflation in args.cmmd_inflation:
                    sigma_case_aggregate = 1.0 * cmmd_inflation
                    se_pilot = sigma_case_aggregate / math.sqrt(
                        max(args.n_case_pilot + args.n_case_bl2_post, 1)
                    )
                    se_main = sigma_case_aggregate / math.sqrt(
                        max(args.n_case_main_total, 1)
                    )
                    rows.append(
                        {
                            "estimand": "E_CMMD_beta_cutoff",
                            "scenario": scenario,
                            "family_state": family_state,
                            "beta_planning": beta,
                            "beta_effective": effect_eff,
                            "cmmd_inflation": cmmd_inflation,
                            "n_case_pilot": args.n_case_pilot + args.n_case_bl2_post,
                            "n_case_main": args.n_case_main_total,
                            "se_pilot": se_pilot,
                            "se_main": se_main,
                            "power_pilot": _wy_power(effect_eff, se_pilot),
                            "power_main": _wy_power(effect_eff, se_main),
                        }
                    )

                # E_PCSG: pooled over `n_temporal_pcsg_pairs` confirmatory
                # pairs (currently 2). σ_pair_residual approximates the
                # within-pair noise on the late-vs-early logprob delta;
                # 4.5 chosen so the closed-form SE for 1 pair at
                # n=2048 pre, 98% eligible matches the Statistical
                # lens §5 anchor of SE ≈ 0.10. Two-pair pooling then
                # gives SE ≈ 0.073, matching the "original main, 2
                # pairs" lens row.
                for elig in args.pcsg_eligibility:
                    sigma_pair_residual = 4.5
                    se_pilot = _se_pcsg_pair(
                        n_case=args.n_case_pilot,
                        n_pairs=fleet.n_temporal_pcsg_pairs,
                        eligibility=elig,
                        sigma_pair_residual=sigma_pair_residual,
                    )
                    se_main = _se_pcsg_pair(
                        n_case=args.n_case_main_pre,
                        n_pairs=fleet.n_temporal_pcsg_pairs,
                        eligibility=elig,
                        sigma_pair_residual=sigma_pair_residual,
                    )
                    rows.append(
                        {
                            "estimand": "E_PCSG_beta_cutoff",
                            "scenario": scenario,
                            "family_state": family_state,
                            "beta_planning": beta,
                            "beta_effective": effect_eff,
                            "pcsg_eligibility": elig,
                            "n_case_pilot": args.n_case_pilot,
                            "n_case_main": args.n_case_main_pre,
                            "n_pairs": fleet.n_temporal_pcsg_pairs,
                            "se_pilot": se_pilot,
                            "se_main": se_main,
                            "power_pilot": _wy_power(effect_eff, se_pilot),
                            "power_main": _wy_power(effect_eff, se_main),
                        }
                    )

                # E_OR / E_NoOp: pooled over 14 P_predict models with
                # eligibility mask. We treat eligibility as a multiplier
                # on n_case (Statistical §1 simulation parameters).
                for or_eligibility in (0.5, 0.7, 0.9):
                    sigma_within = 1.1  # OR outcomes coarser than CMMD
                    sigma_model = 0.40
                    sigma_family = 0.20
                    n_models = fleet.n_p_predict
                    n_families = len(fleet.family_p_predict)
                    eff_pilot = max(
                        int((args.n_case_pilot + args.n_case_bl2_post) * or_eligibility),
                        1,
                    )
                    eff_main = max(int(args.n_case_main_total * or_eligibility), 1)
                    se_pilot = _se_with_family_intercepts(
                        n_case=eff_pilot,
                        n_models=n_models,
                        sigma_within=sigma_within,
                        sigma_model=sigma_model,
                        sigma_family=sigma_family,
                        n_families=n_families,
                    )
                    se_main = _se_with_family_intercepts(
                        n_case=eff_main,
                        n_models=n_models,
                        sigma_within=sigma_within,
                        sigma_model=sigma_model,
                        sigma_family=sigma_family,
                        n_families=n_families,
                    )
                    rows.append(
                        {
                            "estimand": "E_OR_E_NoOp_beta_cutoff",
                            "scenario": scenario,
                            "family_state": family_state,
                            "beta_planning": beta,
                            "beta_effective": effect_eff,
                            "or_eligibility": or_eligibility,
                            "n_case_pilot_eligible": eff_pilot,
                            "n_case_main_eligible": eff_main,
                            "se_pilot": se_pilot,
                            "se_main": se_main,
                            "power_pilot": _wy_power(effect_eff, se_pilot),
                            "power_main": _wy_power(effect_eff, se_main),
                            "n_models": n_models,
                            "n_families": n_families,
                        }
                    )

    return rows


def main() -> int:
    args = parse_args()
    rows = _simulate_estimand_powers(args)
    fleet = _fleet_summary()
    out = {
        "fleet_summary": asdict(fleet),
        "config": {
            "seed": args.seed,
            "n_case_pilot": args.n_case_pilot,
            "n_case_main_pre": args.n_case_main_pre,
            "n_case_main_total": args.n_case_main_total,
            "n_case_bl2_post": args.n_case_bl2_post,
            "effects": list(args.effects),
            "scenarios": list(args.scenarios),
            "cmmd_inflation": list(args.cmmd_inflation),
            "pcsg_eligibility": list(args.pcsg_eligibility),
            "family_states": list(args.family_states),
            "z_wy": Z_WY,
        },
        "rows": rows,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"  n_rows={len(rows)}")
    print(
        f"  fleet: P_predict={fleet.n_p_predict} P_logprob={fleet.n_p_logprob} "
        f"PCSG_pairs={fleet.n_temporal_pcsg_pairs}"
    )
    # Sanity print: PCSG main-run power at β=0.20 / eligibility=0.98
    pcsg_baseline = [
        r for r in rows
        if r["estimand"] == "E_PCSG_beta_cutoff"
        and r["scenario"] == "unweighted_pilot"
        and r.get("pcsg_eligibility") == 0.98
        and abs(r["beta_planning"] - 0.20) < 1e-9
    ]
    if pcsg_baseline:
        r = pcsg_baseline[0]
        print(
            f"  PCSG @ β=0.20, elig=0.98, 2 pairs: "
            f"power_main = {r['power_main']:.2f} (SE_main = {r['se_main']:.3f})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
