# BENCHMARK MVP R2 Check — Editor Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior EMNLP area chair, continuing R1 thread)
**Reasoning effort:** xhigh
**R1 reference:** BENCHMARK_R1_EDITOR.md

**Note on thread continuity:** Original R1 threadId was not persisted, so this R2 was run as a new Codex session (threadId `019d8706-018b-7ab3-98cf-2ed11a27b98b`) with the full R1 review pasted inline as context. Reasoning trail is preserved via the prompt rather than via Codex-native continuation.

---

**Overall Assessment**

This pivot is materially better. It fixes the "three papers stapled together" problem and gives you a plausible resource-plus-measurement paper, but it also narrows the claim: without built-in counterfactual probes, this is no longer a paper about proving memorization case-by-case; it is a paper about building a factor-controlled audit substrate and testing whether existing detectors recover expected partition differences. Under that framing, `ARR May 25, 2026 -> EMNLP 2026 Findings` is still barely live; EMNLP main remains unlikely, and NeurIPS 2026 Evaluations & Datasets is both earlier and harsher on public release.

## 1. Is this MVP a publishable paper on its own?

Yes, conditionally. If executed tightly, this is a plausible **EMNLP 2026 Findings** paper, not an EMNLP main paper. The ceiling is a strong resource/evaluation submission where the contribution is: curated dated Chinese financial-news cases, factor annotations, verified realized outcomes, and a cross-detector analysis of whether contamination-risk strata are detectable.

It is **not** a strong NeurIPS 2026 Evaluations & Datasets play for this round. The deadline is earlier (`May 4` abstract, `May 6` full paper), the track is now explicitly framed around evaluation science, and it requires reviewer-accessible data at submission plus public release by camera-ready. Your topic is also more NLP-resource-specific than broadly ML-evaluation-general.

If the release story is weak or the empirical findings are muddy, this downgrades to a **finance/NLP workshop** or a **stepping-stone tech report**. If the release is clean and the partition analysis is crisp across detectors, **EMNLP Findings** is realistic.

## 2. One-sentence pitch at MVP stage

**Pitch:** *FinMem-Bench is a factor-annotated Chinese financial-news audit set with verified realized outcomes that lets researchers test whether memorization detectors surface higher outcome-memory risk in specific news regimes, rather than treating contamination as an undifferentiated benchmark flaw.*

This survives reviewer skim **if** you immediately state that you are **not** proposing a new detector. The differentiation is clean:

- `FinBERT-CN`, `CFinBench`, `InvestorBench`: domain/task benchmarks, not contamination-audit substrates.
- `AntiLeakBench` and generic memorization benchmarks: leakage/memorization stress tests, but not finance-specific with traceable realized outcomes and factor-controlled partitions.
- Your distinct asset is the combination of **dated finance**, **verified outcomes**, and **factor strata** for downstream audit.

## 3. Deadline realism

`May 25, 2026 ARR` is still achievable, but only if the scope is frozen now and the annotation pipeline is already close to operational. Otherwise accept `August 3, 2026` now. There is **no June/July ARR fallback**; the next cycle after May is August.

A realistic six-week calendar from `April 13` looks like this:

1. `Apr 13-19`: freeze case unit, factor schema, outcome-verification protocol, and public-release plan; pilot `50-80` cases.
2. `Apr 20-May 3`: bulk collection/annotation; daily adjudication; early strata checks.
3. `May 4-10`: outcome QA, provenance cleanup, entity normalization, inter-annotator checks.
4. `May 11-17`: run detectors on `2` models; robustness and agreement analysis.
5. `May 18-24`: write, figure, package release, supplement, internal red-team.
6. `May 25`: submit.

Where the six weeks actually go: mostly into **annotation adjudication and outcome verification**, not detector code. If licensing/public-slice questions are unresolved by about `April 19-20`, I would stop aiming at May.

## 4. Narrative risk at MVP scope

Yes, the risk is now concentrated. Without SR/FO-style counterfactual probes, the paper's novelty rests on:

- a defensible factor taxonomy
- a meaningful partition-difference result

If the partition analysis comes back null across detectors, the paper still exists only as a **negative-results Findings paper** if you can make the null informative. That requires at least:

- a power/sensitivity argument that the strata were large enough to detect practical effects
- detector agreement/disagreement analysis, not just per-detector tables
- manual case studies showing why current detectors may be insensitive on this substrate

Plan B is to reposition the paper as: **current memorization detectors do not cleanly separate economically consequential factor strata even on a controlled financial-news substrate**. That is publishable only if the analysis is rigorous. If you have neither positive partition effects nor a strong detector-failure story, then you do not yet have a conference paper; you have a dataset project.

## 5. Minimum publishable increment

If you only have four weeks, cut harder. Do **not** chase "as large as feasible."

My minimum publishable increment would be:

- `300-500` high-confidence cases, not 800+
- `3-4` factors, not an elaborate taxonomy
- one prompt/task format tied directly to the verified outcome
- `2` models max
- `2` detector families max

Cut **MIA first** unless it is already turnkey. Keep something like `Min-K%` plus one extraction-style baseline. The paper then becomes a **short Findings** or **workshop** submission. In four weeks, completeness beats breadth.

## 6. Reviewer objections at MVP stage

- **"This is just another annotated corpus."** Pre-empt by leading with the audit question, not the corpus. The benchmark is only the vehicle.
- **"The detector comparison is derivative."** Agree explicitly. Say the contribution is a substrate and a measurement study, not detector novelty.
- **"The factor taxonomy is ad hoc."** Provide operational definitions, annotation guidelines, inter-annotator agreement, and prevalence statistics. Show why each factor was chosen.
- **"No counterfactual probe means correlation, not memorization."** Concede this boundary in the paper. Claim risk-stratified auditing of detectors, not proof of memorization.
- **"Partition effects may reflect difficulty, salience, or entity popularity."** Control for obvious confounds: entity frequency, answer length, date distance, market prominence, article volume.
- **"Chinese-only is narrow."** Frame it as deliberate narrowing for clean design in a high-stakes domain, not as a universal benchmark.

The most likely killer objections are the third and fourth ones.

## 7. CLS licensing still fatal?

For **NeurIPS E&D**, yes, basically fatal. The official track guidance requires datasets to be accessible to reviewers at submission and public by camera-ready. "Metadata only + reconstruction from a proprietary corpus" is not the intended standard for a dataset paper.

For **EMNLP Findings**, it is less of a formal desk-reject issue, but still very likely **reviewer-fatal** if you call it a benchmark and there is no genuinely usable public slice. There is precedent for papers that analyze restricted corpora, but much less protection for a **resource/benchmark paper** whose core artifact cannot actually be inspected or reused.

Dropping counterfactual probes does **not** solve this. The clean path is:

- a truly public benchmark core
- a larger licensed extension clearly marked as secondary

If week 1 ends without that path, stop selling this as a benchmark paper.

## 8. Title candidates

1. **FinMem-Bench: A Factor-Annotated Audit Substrate for Outcome-Memory Detection in Chinese Financial News**
2. **Auditing Outcome Memory in Chinese Financial News with Verified Outcomes and Factor-Controlled Partitions**
3. **FinMem-Bench: Verified-Outcome Evaluation for Contamination Audits in Chinese Financial LLMs**

## 9. Go/no-go on MVP pivot

**Go**, but only if you accept that this is now a **Findings-first resource/evaluation paper**, not a main-track novelty bet. This pivot does not lock in a weak story by itself; it gives you a coherent first paper. What would lock in a weak story is overclaiming memorization without counterfactual evidence, or calling unreleasable metadata a benchmark.

The single most important thing to get right in the first week is: **freeze the annotation/evidence protocol on a legally public pilot slice**. In practice that means `50-80` cases, final factor definitions, final outcome-verification rules, and a concrete public-release path. If that foundation is shaky, everything downstream will look improvised.

Date anchors and policy references: [EMNLP 2026 CFP](https://2026.emnlp.org/calls/main_conference_papers/), [EMNLP 2026 dates](https://2026.emnlp.org/), [ARR 2026 cycle dates](https://aclrollingreview.org/dates), [NeurIPS 2026 Evaluations & Datasets CFP](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets), [NeurIPS 2026 hosting rules](https://neurips.cc/Conferences/2026/EvaluationsDatasetsHosting).
