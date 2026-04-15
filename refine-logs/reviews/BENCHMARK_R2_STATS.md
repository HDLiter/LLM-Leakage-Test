# BENCHMARK MVP R2 Check — Stats Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior econometrician, continuing R1 thread)
**Reasoning effort:** xhigh
**R1 reference:** BENCHMARK_R1_STATS.md

---

## 1. Is "defer the estimand" defensible?

This retreat is materially better than the original proposal. I do not retract my R1 objection; I narrow it. You may defer the **memorization estimand** if, and only if, you stop claiming the MVP benchmark itself identifies memorization. In that narrower role, this is a **substrate** build: a case set with point-in-time labels and factor metadata on which later detectors can define their own estimands.

What you may **not** defer is the **outcome-label function** and the **design-sensitivity target**. "Sufficient per sub-partition" is otherwise empty. A substrate can be unfit for purpose even if it is large, because later detectors will inherit whatever ambiguity you bake into target mapping, horizon choice, entity resolution, and clustering. So: deferring the estimand is defensible; deferring the data-generating object is not. If you freeze the case contract now, this is legitimate. If not, it is just the R1 problem wearing a different name.

## 2. Stratification without estimand: what N?

Design to detect at least the **Phase-4-sized partition difference**, not a more optimistic one. Your only empirical anchor is still `OR = 1.95`, approximately `p1 = 0.123` versus `p0 = 0.068`, risk difference about `5.6 pp`.

For a balanced two-group comparison at `alpha = 0.05`, `80%` power, you still need about **426 per side**, so **852 scorable cases** for one clean partition contrast. That is the floor.

Now add the part people usually ignore: you should sample and infer at the **event-cluster** level, not the raw article level. If average cluster size is about `m = 3` near-duplicate telegraphs per event and intra-cluster ICC is `rho = 0.25`, the design effect is:

`DE = 1 + (m - 1) rho = 1 + 2 * 0.25 = 1.5`

So the effective requirement becomes about `852 * 1.5 = 1278` scorable article-level cases, or roughly **425 event clusters**. Add 15-20% loss for verification failures, ambiguous targets, halted names, and detector-specific unusability, and the gross target should be about **1,500 verified cases**.

That is the number I would use. If you insist on company/sector/index all living in the same substrate, `1,500` is a floor, not a ceiling.

## 3. Which factors must be locked now?

- `anchor`: **Lock now.** Use a written text-only rubric, version it, store raw anchor cues, and keep both 4-level and binary collapse.
- `direction`: Do **not** lock as a hand annotation. Lock the continuous realized outcome inputs now; direction can then be recomputed later from the frozen return series under any threshold.
- `frequency`: Lock the **corpus snapshot, retrieval window, duplicate definition, and raw cluster count** now. The binning can be recomputed later. Do not repeat the period-dependent frequency mistake.
- `credibility`: Do **not** lock a crude high/low bin now. Store raw provenance fields: official filing, company statement, ministry, exchange, named analyst, journalist paraphrase, unattributed rumor. Collapse later.
- `target_type`: **Lock now.** This is structural because outcome construction differs by company, sector, and index.
- Add `event_cluster_id`: **Must lock now.** Otherwise downstream SEs and sampling are wrong.
- Add `publish_session` and `tradability flags`: **Must lock now.** Without them, the realized outcome is not point-in-time well defined.

## 4. Outcome definition rigor: what does the stats lens require?

"Direction + magnitude + traceable source" is still too vague. I would require the following core construction.

Timestamp each article at exact `publish_ts` in Beijing time. Map it to the **first tradable market open strictly after publication**, call that `tau_i`. For each case, store raw and adjusted returns over `H = 1, 5, 22` trading days.

For **company** targets, primary magnitude should be the stock's `open-to-open` log return from `tau_i` to `tau_i + H`, minus a frozen benchmark return. If you want one primary benchmark, use **CSI 300**; sector-adjusted is a sensitivity analysis. For **sector** targets, use the sector index return minus CSI 300. For **broad index** targets, use raw index return and do **not** pool magnitude with company cases.

Set one primary directional label now, e.g. `H = 5` trading days, with a neutral band fixed ex ante. I would use a volatility-scaled neutrality rule, such as neutral when absolute abnormal return is below `0.5` of the target's trailing 20-day sigma. Store the continuous return regardless.

Point-in-time discipline matters: freeze the price vendor, trading calendar, ticker-history map, split-adjustment rule, and treatment of halted/ST/limit-up/down cases. Cases that are non-tradable or suspended should be flagged and excluded from primary company-direction analysis, not silently pooled.

## 5. Identification plan for partition comparison

The target contrast is **not** causal. It is descriptive heterogeneity in a detector score across partitions:

`delta_{d,f} = E[S_{id} | F_i = 1] - E[S_{id} | F_i = 0]`

where `S_{id}` is the case-level score from detector `d`, standardized within detector family, and `F_i` is a factor partition.

Identification is observational, conditional on the frozen case-definition covariates. So use a single case-level model with factor main effects and **pre-specified detector x factor interactions**, cluster-robust at `event_cluster_id`. Do not run dozens of separate 2x2 tests.

To avoid multiple-testing hell, freeze:
1. one primary outcome map,
2. one primary score per detector,
3. one omnibus test per factor across detectors.

Then control FDR across the factor-omnibus family. Only if a factor-level omnibus survives do you open the within-factor contrasts. Alternative horizons and re-binnings are exploratory.

## 6. Confounding in CLS: which sampling plan?

Pick **(c) stratified core + random panel hybrid**.

Full census plus post-hoc weighting sounds principled, but the annotation burden is too high and overlap will still fail in sparse partitions. Quota-balanced sampling solves overlap but destroys the ability to say what is common in the corpus.

The hybrid gives you both. Build a **stratified core** to guarantee support in anchor, direction, frequency, and target-type partitions, then add a **random panel** from the same frozen corpus snapshot to recover natural margins and support weighting. My suggestion is roughly **800 stratified core + 700 random panel = 1,500 total**, sampled at the **event-cluster** level.

## 7. Pre-registration posture

The existing `PREREGISTRATION.md` should remain what it is: a **CPT experiment preregistration**. Do not overload it with substrate collection rules. That would make both documents worse.

The MVP needs its own **data-protocol preregistration** or benchmark charter, frozen **before any detector is run on the final substrate**. That document should lock: corpus snapshot; inclusion/exclusion; event clustering; target-type schema; entity resolution; outcome construction; factor rubrics; audit thresholds; sampling design; dev/test split; and release posture. In particular, answers or detector outputs for the held-out benchmark portion should remain hidden if you want any longevity.

## 8. Go/no-go verdict

This MVP does address the central R1 problem **if you are honest about what it is**. As a substrate, it is defensible. As a benchmark that already "measures natural memorization," it is not.

So my verdict is conditional. I am now **more favorable** than in R1 to the dataset build itself, because the retreat removes the fake causal bravado. But the project still fails immediately if it treats "substrate" as permission to postpone the realized-outcome rule. That rule is the spine. Without it, factor partitions, entity resolution, and later detector comparisons will drift and become non-comparable.

- **Verdict:** `Go` as a Chinese-only substrate build with descriptive partition comparisons; `no-go` for any memorization claim until CPT calibration and detector-specific preregistration.
- **Target N:** about **1,500 verified cases** total, sampled at the **event-cluster** level; absolute floor about **1,200**, but `1,500` is the safer number.
- **Must pin down now:** the point-in-time realized-outcome map `O_i(H)` — exact target mapping, horizon, benchmark adjustment, and neutral band.
