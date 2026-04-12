# Stats Agent: Next Step Recommendation

**Bottom Line**
The highest-priority next step is a **preregistered confirmatory replication on new data with `fo_flip_impact_hedged` as the single primary endpoint**, not another exploratory re-analysis of the same 606 cases. The current Phase 4 result is promising, but it is not yet confirmatory given the audit-triggered endpoint correction, 4-way multiplicity, mixed probe modality, no positive control, and limited power ([PILOT_RESULTS.md](D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md:521), [BUG_AUDIT_amber.md](D:/GitRepos/LLM-Leakage-Test/docs/BUG_AUDIT_amber.md:158), [FIRTH_DECISION.md](D:/GitRepos/LLM-Leakage-Test/docs/FIRTH_DECISION.md:19), [strata_config.json](D:/GitRepos/LLM-Leakage-Test/data/seed/strata_config.json:2)).

## Top 3 Next Steps

### 1. Lock a confirmatory protocol around `impact_hedged` and collect a new sample

Justification: `p=0.022` for `impact_hedged` does **not** survive 4-test family correction. Holm-adjusted `p=0.088`; Bonferroni-adjusted `p=0.088`; BH `q~0.072`. On the current data, `hedged` is best treated as an **audit-justified corrected endpoint**, but still exploratory because the correction became outcome-relevant after seeing results. For the next study, prespecify:
- Primary endpoint: `fo_flip_impact_hedged`
- Primary analysis: stratified CMH by `anchor_binary`
- Secondary/sensitivity: exact conditional CMH / exact common-OR CI, Zelen exact homogeneity, `impact_strict`, `direct_*`
- Clear hierarchy for multiplicity so only one primary claim is at risk

### 2. Add a matched positive control, ideally the continued-pretrained Qwen arm

Justification: the biggest remaining problem is **construct validity**, not the CMH arithmetic. If a model with manipulated exposure shows a larger `impact_hedged` signal on the same cases, the metric becomes much more interpretable. If it does not, the current result is more likely a task artifact than memorization. From a stats perspective, this is the fastest way to move from "association consistent with memorization" to "calibrated detector."

### 3. Fix the design confounds by design, not regression rescue

Justification: the current `frequency_class` is structurally entangled with `period`, and the pre arm is still mixed on `cpt_mode`. Recommendation:
- Rebuild frequency as a **period-invariant exposure proxy** before using it as a covariate or stratifier
- Either make CPT modality uniform, or run the **2x2 within-case cross** where each case gets both probe shapes
- If `anchor_binary` remains a primary stratum, finish the B2 reliability check before the confirmatory run

## Statistical Risk Assessment

- **`impact_hedged` (OR=1.95, raw `p=0.022`)**: promising but **moderate-high false-positive risk** as a headline claim. It is directionally stable across strata and generic-only probes, and in my local check the primary table is not too sparse for asymptotic CMH. But it fails multiplicity correction, current power at `OR=1.95` is only about **0.63**, and winner's-curse/nonreplication risk is real.
- **`direct_hedged` (OR=0.64, `p=0.036`)**: exploratory only. Same multiplicity problem, plus it is better interpreted as suggestibility than memorization.
- **`impact_strict` / `direct_strict`**: do not prioritize. These are the sparse/degenerate versions and are not the right endpoints for a confirmatory claim.
- **CFLS temporal result (`p=0.0065`)**: statistically the most stable finding. I would treat this as a robust construct-validity result that CFLS is a reading-comprehension/input-sensitivity metric, not a memorization detector.
- **Breslow-Day `p=0.28`**: weak evidence either way. Homogeneity tests are low-power here; "pooling not rejected" is acceptable, but "homogeneous effects proven" would be too strong.
- **Penalized logit**: supplementary only. The L1 fit is directionally useful, but it is not Firth.

## Sample Size for Confirmation

Approximate CMH power calculations using the observed post-arm event rates and current anchor-stratum mix.

| Scenario | Scorable cases needed | Raw annotated cases (~yield) |
|---|---|---|
| `impact_hedged` single primary at alpha=0.05 | ~850 (balanced) / ~886 (current imbalance) | ~980-1,020 |
| 4-endpoint family with Bonferroni/Holm (alpha~0.0125) | ~1,200-1,240 | ~1,385-1,430 |
| Current study | ~591 scorable | Power ~0.63 at OR=1.95 |

## On the 2x2 Cross Design

The **2x2 cross is the right design for deconfounding probe modality**. It lets you estimate modality main effects and `period x modality` interaction cleanly. It is **not sufficient by itself for causal identification of memorization**, because `period` is still observational. For causal identification, pair the 2x2 cross with the **positive-control exposure manipulation**.

## Wild Card

Use **empirical calibration** from observational epidemiology: build a small reference set of negative-control cases and known positive controls, then calibrate your p-values/effect sizes against that error distribution. That is standard in observational causal work, but almost nobody applies it to LLM leakage audits. It would give you a much better answer than raw nominal p-values alone.

## Sources

- Local: [PILOT_RESULTS.md](D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md:521), [BUG_AUDIT_amber.md](D:/GitRepos/LLM-Leakage-Test/docs/BUG_AUDIT_amber.md:338), [FIRTH_DECISION.md](D:/GitRepos/LLM-Leakage-Test/docs/FIRTH_DECISION.md:19), [strata_config.json](D:/GitRepos/LLM-Leakage-Test/data/seed/strata_config.json:2)
- R exact/asymptotic CMH: https://stat.ethz.ch/R-manual/R-devel/RHOME/library/stats/html/mantelhaen.test.html
- SAS exact CMH, Zelen, Mantel-Fleiss: https://support.sas.com/documentation/cdl/en/procstat/66703/HTML/default/procstat_freq_details80.htm
- Stata `power cmh`: https://www.stata.com/manuals/pss-2powercmh.pdf
- FDA multiplicity guidance: https://www.fda.gov/files/drugs/published/Multiple-Endpoints-in-Clinical-Trials-Guidance-for-Industry.pdf
- JAMA on preregistering observational studies: https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2836842
- TARGET guideline: https://pubmed.ncbi.nlm.nih.gov/41091811/
- Target trial framework, 2025: https://smithcenter.bidmc.org/publications/target-trial-framework-causal-inference-observational-data-why-and-when-it-helpful
- EMA ICH M14, effective March 18, 2026: https://www.ema.europa.eu/en/ich-m14-guideline-general-principles-plan-design-analysis-pharmacoepidemiological-studies-utilize-real-world-data-safety-assessment-medicines-scientific-guideline
- Empirical calibration vignette, February 14, 2025: https://stat.ethz.ch/CRAN/web/packages/EmpiricalCalibration/vignettes/EmpiricalPCalibrationVignette.pdf
