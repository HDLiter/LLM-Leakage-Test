# Collinearity & Non-Redundancy Diagnostics

**WS0.5 relevance.** The four confirmatory factors (Cutoff Exposure, Historical
Family Recurrence, Target Salience, Template Rigidity) all proxy "LLM training
exposure", so they are correlated by construction. Before the pilot sample is
frozen, a discriminant / non-redundancy check must confirm they are not so
collinear that the mixed-effects analysis cannot separate their effects. The
S-6 review used this literature to cut the v0.3 five-diagnostic suite down to
the field-standard minimum.

**Decision it informed (S-6).** Minimal, literature-backed check =
**VIF on the four factors (fixed-effect design) + a 4×4 Pearson correlation
matrix** of the model-entered transformed covariates. Thresholds are empirical
guides, not tests: max VIF ≤ 5 proceed; 5-10 moderate (keep the factors,
pre-register a sensitivity analysis); ≥ 10 / rank deficiency / pairwise
|r| ≥ 0.90 means the pilot cannot separate the effects (fix the sampling
support, or combine factors). Dropped as redundant/over-built: condition
number, partial/residual correlations, the GVIF apparatus (GVIF = VIF for 1-df
continuous terms). Mixed-model singular-fit / convergence is a *separate*
model-fit diagnostic, not a non-redundancy check. Remedy discipline: do not
mechanically drop a confirmatory factor, do not dichotomize, do not residualize.
Full review: `temp/collinearity_diagnostics_20260520.md`.

## References

### Collinearity diagnostics — core
- **Belsley, Kuh & Welsch 1980**, *Regression Diagnostics* (Wiley, DOI 10.1002/0471725153) — condition index + variance-decomposition proportions; collinearity as design-matrix ill-conditioning.
- **Belsley 1991**, *Conditioning Diagnostics: Collinearity and Weak Data in Regression* (Wiley, ISBN 9780471528890) — "weak data" framing.
- **Marquardt 1970**, "Generalized Inverses, Ridge Regression…" *Technometrics* (DOI 10.1080/00401706.1970.10488699) — early VIF lineage.
- **Fox & Monette 1992**, "Generalized Collinearity Diagnostics," *JASA* (DOI 10.1080/01621459.1992.10475190) — GVIF (reduces to VIF for 1-df terms).

### VIF thresholds and their critique
- **O'Brien 2007**, "A Caution Regarding Rules of Thumb for VIF," *Quality & Quantity* (DOI 10.1007/s11135-006-9018-6) — the "rule of 10" is misused; thresholds are context-dependent.
- **Craney & Surles 2002**, "Model-Dependent VIF Cutoff Values," *Quality Engineering* (DOI 10.1081/QEN-120001878).
- **Mason & Perreault 1991**, "Collinearity, Power, and Interpretation…" *J. Marketing Research* (DOI 10.1177/002224379102800302) — collinearity harm depends on n, noise, effect size.
- **Menard 2002**, *Applied Logistic Regression Analysis*, 2nd ed. (Sage, DOI 10.4135/9781412983433) — tolerance < .20 / < .10 guides.
- **James, Witten, Hastie & Tibshirani 2021**, *ISLR*, 2nd ed. (Springer, DOI 10.1007/978-1-0716-1418-1).

### Mixed models — why singular-fit is a separate concern
- **Bates, Maechler, Bolker & Walker 2015**, "Fitting Linear Mixed-Effects Models Using lme4," *J. Statistical Software* — arXiv 1406.5823. **[PDF: `lme4 Fitting Linear Mixed-Effects Models.pdf`]**
- **Bates, Kliegl, Vasishth & Baayen 2015**, "Parsimonious Mixed Models" — arXiv 1506.04967. **[PDF: `Parsimonious Mixed Models.pdf`]**
- **Barr, Levy, Scheepers & Tily 2013**, "Keep it maximal," *J. Memory and Language* (DOI 10.1016/j.jml.2012.11.001).
- **Matuschek, Kliegl, Vasishth, Baayen & Bates 2017**, "Balancing Type I error and power in LMMs," *J. Memory and Language* (DOI 10.1016/j.jml.2017.01.001).

### Remedies — and what NOT to do
- **Dormann et al. 2013**, "Collinearity: a review of methods…" *Ecography* (DOI 10.1111/j.1600-0587.2012.07348.x) — systematic review of remedies.
- **Royston, Altman & Sauerbrei 2006**, "Dichotomizing continuous predictors… a bad idea," *Statistics in Medicine* (DOI 10.1002/sim.2331) — backs the C-3 continuous decision.
- **Wurm & Fisicaro 2014**, "What residualizing predictors… does," *J. Memory and Language* (DOI 10.1016/j.jml.2013.12.003) — residualization changes the estimand.
- **York 2012**, "Residualization is not the answer," *Social Science Research* (DOI 10.1016/j.ssresearch.2012.05.014).
- **Babyak 2004**, "What you see may not be what you get," *Psychosomatic Medicine* (DOI 10.1097/01.psy.0000127692.23278.a9) — small-n overfitting caution.
- **Zuur, Ieno & Elphick 2010**, "A protocol for data exploration…" *Methods in Ecology and Evolution* (DOI 10.1111/j.2041-210X.2009.00001.x) — VIF + correlation as the routine lightweight check.

*PDFs: only the two arXiv items are downloaded into `related papers/`; the rest
are paywalled books / journal articles, recorded here as the direction
bibliography (DOIs above).*

## Pointers
- Codex methods review: `temp/collinearity_diagnostics_20260520.md`
- Memo decision: `docs/DECISION_20260518_ws0_5_thales_alignment.md` §3.3.3 (S-6)
