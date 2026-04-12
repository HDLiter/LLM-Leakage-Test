"""Phase E2: sensitivity analysis for the temporal CPT effect.

Primary inference is Mantel-Haenszel from E1 (quick_stats.py).
This script reports sensitivity slices and a penalized-logit supplement:

  - MH within reversibility=high only
  - MH within frequency_class=low only
  - MH within frequency_class=high only
  - Firth-style penalized logit (statsmodels.fit_regularized L1) supplement
    on fo_flip ~ period + C(<analysis_anchor_field>)

The anchor field name comes from data/seed/strata_config.json -- never
hardcoded -- so the binary collapse decision from B4 propagates here
automatically.

True Firth's penalized logit is unavailable in this env (firthlogist
requires Python <3.11; rpy2 has no R installed). We fall back to
statsmodels.Logit.fit_regularized(method='l1') as documented in
docs/FIRTH_DECISION.md. The point estimate may be biased toward zero
relative to true Firth; primary inference therefore stays MH.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.discrete.discrete_model import Logit
from statsmodels.stats.contingency_tables import StratifiedTable, Table2x2

ROOT = Path(__file__).resolve().parent.parent
RESULTS_PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
STRATA_CONFIG_PATH = ROOT / "data" / "seed" / "strata_config.json"
OUTPUT_PATH = ROOT / "data" / "results" / "sensitivity_analysis.json"

# Bug 3 fix: report MH on both strict (legacy bool) and hedged
# (strict ∪ neutral retreat) variants for each task. Strict reproduces the
# v3 baseline; hedged adds the cases the strict definition undercounted.
# Falls back to legacy key names if amber keys are missing.
_AMBER_METRICS = [
    "fo_flip_direct_strict",
    "fo_flip_direct_hedged",
    "fo_flip_impact_strict",
    "fo_flip_impact_hedged",
]
_LEGACY_METRICS = ["fo_flip_direct", "fo_flip_impact"]
METRICS = _AMBER_METRICS  # resolved at runtime in main()


def _load_anchor_field() -> str:
    if STRATA_CONFIG_PATH.exists():
        cfg = json.loads(STRATA_CONFIG_PATH.read_text(encoding="utf-8"))
        return cfg.get("analysis_anchor_field", "anchor_level")
    return "anchor_level"


def _build_dataframe(cases: list[dict[str, Any]], anchor_field: str) -> pd.DataFrame:
    rows = []
    for c in cases:
        period = c.get("period")
        if period not in ("pre_cutoff", "post_cutoff"):
            continue
        anchor = c.get(anchor_field)
        if anchor is None:
            continue
        row = {
            "case_id": c.get("case_id"),
            "period": period,
            "period_post": int(period == "post_cutoff"),
            anchor_field: str(anchor),
            "frequency_class": c.get("frequency_class"),
            "reversibility": c.get("reversibility"),
        }
        for k in METRICS:
            v = c.get("metrics", {}).get(k)
            row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)


def _mh_for_subset(df: pd.DataFrame, metric: str, anchor_field: str) -> dict[str, Any]:
    """Build per-stratum 2x2 tables and run Mantel-Haenszel."""
    sub = df[df[metric].notna()]
    if sub.empty:
        return {"n_cases": 0, "strata": {}, "pooled_or": None,
                "p_value": None, "breslow_day_p": None, "note": "no_data"}

    strata: dict[str, dict[str, Any]] = {}
    arrays: list[np.ndarray] = []
    for s_val, group in sub.groupby(anchor_field):
        pre_mask = group["period"].eq("pre_cutoff")
        post_mask = group["period"].eq("post_cutoff")
        pre_vals = np.asarray(list(group.loc[pre_mask, metric]), dtype=bool)
        post_vals = np.asarray(list(group.loc[post_mask, metric]), dtype=bool)
        arr = np.array([
            [int(pre_vals.sum()), int((~pre_vals).sum())],
            [int(post_vals.sum()), int((~post_vals).sum())],
        ])
        try:
            t = Table2x2(arr)
            stratum_or = float(t.oddsratio)
        except Exception:
            stratum_or = None
        try:
            _o, p_fish = stats.fisher_exact(arr.tolist())
            p_fish = float(p_fish)
        except Exception:
            p_fish = None
        strata[str(s_val)] = {
            "n": int(arr.sum()),
            "pre_flip": int(arr[0, 0]),
            "pre_total": int(arr[0, 0] + arr[0, 1]),
            "post_flip": int(arr[1, 0]),
            "post_total": int(arr[1, 0] + arr[1, 1]),
            "or": stratum_or,
            "fisher_p": p_fish,
        }
        if arr.sum(axis=0).min() > 0 and arr.sum(axis=1).min() > 0:
            arrays.append(arr)

    pooled_or = None
    p_value = None
    bd_p = None
    if arrays:
        try:
            mh = StratifiedTable(arrays)
            pooled_or = float(mh.oddsratio_pooled)
            test = mh.test_null_odds()
            p_value = float(test.pvalue)
            bd = mh.test_equal_odds()
            bd_p = float(bd.pvalue)
        except Exception as exc:
            pooled_or = None
            p_value = None
            bd_p = None
            print(f"  WARN: MH failed: {exc}")

    return {
        "n_cases": int(sub.shape[0]),
        "strata": strata,
        "pooled_or": pooled_or,
        "p_value": p_value,
        "breslow_day_p": bd_p,
    }


def _firth_substitute_logit(
    df: pd.DataFrame,
    metric: str,
    anchor_field: str,
    alpha: float = 1.0,
) -> dict[str, Any]:
    """L1-penalized logit as a Firth substitute (see docs/FIRTH_DECISION.md)."""
    sub = df[df[metric].notna()].copy()
    if sub.empty:
        return {"note": "no_data"}

    # One-hot encode the anchor field (drop first level to avoid singular matrix)
    anchor_dummies = pd.get_dummies(sub[anchor_field], prefix="anchor", drop_first=True)
    X = pd.concat([
        pd.Series(1.0, index=sub.index, name="intercept"),
        sub["period_post"].rename("period_post"),
        anchor_dummies,
    ], axis=1)
    y = sub[metric].astype(int)

    if len(np.unique(y)) < 2:
        return {"note": "outcome_constant_quasi_separation"}

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = Logit(y.values.astype(float), X.values.astype(float))
            res = model.fit_regularized(method="l1", alpha=alpha, disp=0)
        coefs = dict(zip(X.columns, res.params.tolist()))
        period_coef = coefs.get("period_post")
        # OR for period_post = exp(coef)
        period_or = float(np.exp(period_coef)) if period_coef is not None else None
        return {
            "method": "statsmodels.Logit.fit_regularized(L1, alpha=1.0)",
            "note": "Firth substitute -- see docs/FIRTH_DECISION.md",
            "n": int(len(y)),
            "n_features": int(X.shape[1]),
            "coefs": {k: float(v) for k, v in coefs.items()},
            "period_post_or_exp": period_or,
        }
    except Exception as exc:
        return {"note": f"penalized_logit_failed: {type(exc).__name__}: {exc}"}


def main() -> int:
    global METRICS

    if not RESULTS_PATH.exists():
        print(f"ERROR: results file not found: {RESULTS_PATH}")
        return 1

    raw = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cases = raw.get("cases", [])

    # Detect stale data and fall back to legacy keys
    sample_metrics = cases[0].get("metrics", {}) if cases else {}
    if "fo_flip_direct_strict" not in sample_metrics:
        print("WARNING: results file lacks amber-mirror-lattice keys "
              "(fo_flip_*_strict/_hedged). Falling back to legacy keys.",
              file=sys.stderr)
        METRICS = _LEGACY_METRICS
    print(f"Loaded {len(cases)} cases from {RESULTS_PATH}")

    anchor_field = _load_anchor_field()
    print(f"Anchor stratum field: {anchor_field!r}")

    df = _build_dataframe(cases, anchor_field)
    print(f"Cases with anchor + period: {len(df)}")
    print(f"  by period: {df['period'].value_counts().to_dict()}")
    print(f"  by {anchor_field}: {df[anchor_field].value_counts().to_dict()}")

    out: dict[str, Any] = {
        "anchor_field": anchor_field,
        "n_total_cases": len(df),
        "metrics": {},
    }

    for metric in METRICS:
        print(f"\n=== {metric} ===")
        metric_block: dict[str, Any] = {
            "primary_mh_full_sample": _mh_for_subset(df, metric, anchor_field),
            "sensitivity_slices": {},
            "penalized_logit": _firth_substitute_logit(df, metric, anchor_field),
        }
        # Sensitivity slices
        slices = {
            "reversibility=high": df[df["reversibility"] == "high"],
            "frequency_class=low": df[df["frequency_class"] == "low"],
            "frequency_class=high": df[df["frequency_class"] == "high"],
        }
        for slice_name, sub_df in slices.items():
            print(f"  slice {slice_name}: n={len(sub_df)}")
            metric_block["sensitivity_slices"][slice_name] = _mh_for_subset(
                sub_df, metric, anchor_field
            )

        out["metrics"][metric] = metric_block

        # Pretty-print summary
        primary = metric_block["primary_mh_full_sample"]
        print(f"  PRIMARY MH: pooled OR={primary.get('pooled_or')} p={primary.get('p_value')} "
              f"BD_p={primary.get('breslow_day_p')}")
        pl = metric_block["penalized_logit"]
        if "period_post_or_exp" in pl:
            print(f"  PENALIZED LOGIT: period_post OR={pl['period_post_or_exp']}")
        else:
            print(f"  PENALIZED LOGIT: {pl.get('note')}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
