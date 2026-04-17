# Firth Penalized Logit — Implementation Decision

**Date:** 2026-04-09
**Phase:** 0 (deep-floating-lake plan)

## Context
Phase E2 (`scripts/sensitivity_analysis.py`) needs Firth's penalized logistic
regression because plain logit is fragile under rare events / quasi-separation,
which is the regime our `fo_flip` outcome lives in.

## Availability check
| Option                            | Status     | Reason |
|-----------------------------------|------------|--------|
| `firthlogist` (Python, preferred) | NOT USABLE | Package requires Python <3.11; `rag_finance` env is Python 3.12 |
| `rpy2` + R `logistf`              | NOT USABLE | `rpy2` 3.6.7 imports, but no R installation on host (R_HOME unset) |
| `statsmodels.Logit.fit_regularized` (L1) | USABLE | Weaker substitute, available in statsmodels 0.14.6 |

## Decision
Use **`statsmodels.Logit.fit_regularized(method='l1', alpha=1.0)`** as the
penalized-logit substitute in `scripts/sensitivity_analysis.py`.

This is **not** Firth — it is L1-penalized MLE — but it shares the practical
goal of stabilizing coefficient estimates under rare events / sparse cells.
Differences to flag in `PILOT_RESULTS.md`:

- L1 shrinks toward zero rather than applying Jeffreys prior bias correction
- It will not produce closed-form Firth-style profile-penalized confidence intervals
- For rare-event ORs the point estimate may be biased toward the null relative to true Firth

## What to document in PILOT_RESULTS.md
- The regression model is supplementary; **primary inference is Mantel-Haenszel** from E1
- The penalized-logit substitution and why true Firth was unavailable
- A sensitivity sentence: "If results hinge on regression rather than MH, install R + logistf in a future iteration"

## Future fix (if needed)
Install R via conda and re-enable rpy2:
```bash
conda install -n rag_finance -c conda-forge r-base r-essentials
conda run -n rag_finance python -m rpy2.situation  # confirm R_HOME picked up
# In R: install.packages("logistf")
```
This is deferred unless reviewers push back on the L1 substitution.
