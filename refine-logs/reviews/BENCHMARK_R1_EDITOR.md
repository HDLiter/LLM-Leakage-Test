# BENCHMARK_PROPOSAL R1 Review — Editor Agent
**Date:** 2026-04-12
**Reviewer:** Codex (senior EMNLP area chair persona)
**Reasoning effort:** xhigh

---

## 1. Executive verdict

**EMNLP main, as proposed: reject.**
**EMNLP Findings, as proposed: major revision, not submission-ready.**
**Best realistic target in this cycle: EMNLP 2026 Findings via the May 25, 2026 ARR cycle, but only after a ruthless scope cut.**

The current proposal is not one paper. It is a benchmark paper, a probe-validity paper, a causal-intervention paper, a cross-lingual resource paper, a mitigation paper, and a tooling paper stapled together. Reviewers will not reward that breadth; they will attack the weakest surface.

The internal record already points the same way. Your own project documents show that this is a pivot out of a failed construct-validity story, not a mature benchmark extension: [PILOT_RESULTS.md](/D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md) and [DECISION_20260411_post_amber.md](/D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260411_post_amber.md).

## 2. Novelty positioning and defensible story

**One-sentence pitch that can survive reviewer skim:**

**FinMem-Bench turns financial LLM contamination from an uncontrolled nuisance into a controlled audit variable by pairing dated financial-news cases with verified outcomes and matched conflict probes.**

That is the right story. Not "a new memorization detector." Not "a cross-lingual finance benchmark." Not "a mitigation toolkit."

**Positioning against Min-K% / membership inference.**
FinMem-Bench should be positioned as the **benchmark substrate**, not the detector. Min-K%, MIA, extraction, and CPT are measurement methods; your contribution is a dataset design that makes those methods interpretable on the same cases. If you claim to supersede detector papers, you will lose.

**Positioning against counterfactual probing.**
The only defensible novelty is not "we also use reversals/false outcomes," because that is now a known family. The novelty is: **factor control, verified outcomes, temporal labels, and matched negative controls in a finance setting where outcome memory is economically consequential.** But that only holds if the primary comparison uses comparable perturbations. Right now your 3-task design still mixes heterogeneous task-template bundles.

**Positioning against financial NLP benchmarks.**
CFinBench and InvestorBench are capability benchmarks, not contamination benchmarks. They ask "can the model do finance?" You need to ask "is the model using temporally inadmissible knowledge when it appears to do finance?" That distinction is real and publishable. Do not drift back into agent quality, alpha, or general financial competence. That is another paper.

**Positioning against AntiLeakBench / MMLU-CF / LastingBench / LiveBench.**
These papers mostly make evaluation **harder to contaminate** or **more sustainable over time**. Your defensible distinction is different: **FinMem-Bench is an audit benchmark for measuring contamination susceptibility itself.** That is a good distinction. It is also the only one that justifies staying in finance rather than competing head-on with broad contamination-free benchmarks.

**Reviewer-relevant inference from recent precedent:** accepted benchmark papers in this space are rewarding a clear failure mode plus a usable artifact. They are not rewarding "bigger benchmark + extra ideas."

## 3. Scope discipline — what to cut and why

The proposal needs a hard divide between **core** and **fantasy**.

**Cut from the paper now:**
- **Cross-lingual CN+EN as a headline.** If Chinese is CLS telegraphs and English is partly SEC EDGAR, that is not cross-lingual replication; it is cross-language plus cross-genre confounding.
- **Masking/mitigation track.** This reads as grant-proposal padding.
- **Claude Code skills/toolkit framing.** Reviewers will read this as vendor-specific gimmickry, not scientific contribution.
- **Extended training corpus (10K-50K).** That is infrastructure, not paper spine.
- **Multi-method compatibility claims beyond methods you actually run.**
- **4-model matrix.** Two models is enough for a Findings paper. Four just adds failure modes.
- **Six-factor balancing as a design promise.** Annotate more factors than you balance.
- **Source credibility as a balance axis.** Keep as annotation only.
- **Frequency as a balance axis.** Keep continuous or post-hoc binned; do not let it drive cell quotas.
- **Three-task headline if two tasks are still outcome-proximal variants.**

**Why this must be cut:**
- The arithmetic already breaks the proposal. A 5-way core cross with `period x anchor x frequency x direction x target_type` has `72` cells. At `2,000` cases per language, that is `27.8` cases per cell on average before exclusions. Your stated target of `>=30` per cell is already overcommitted.
- The run budget is equally implausible. `4,000 cases x 3 tasks x 4 conditions x 4 models = 192,000` model-condition evaluations before CPT, QC reruns, or annotation repair.
- Your own decision memo estimated `30-45` researcher-days for a much smaller paper. This proposal is materially larger.

**Minimum viable paper by May 25, 2026:**
- **Single-language core benchmark.**
- **500-800 cases**, not `2,000+2,000`.
- **4 core factors only:** period, anchor, direction, target type.
- **2 tasks max:** one outcome-proximal task and one same-template bridge or genuinely evidence-grounded task.
- **2 models max:** DeepSeek behavioral audit + Qwen baseline.
- **Qwen CPT positive control on a subset only**, not full factorial cross-lingual CPT.
- **No mitigation section in main paper.**
- **No toolkit section in main paper.**
- **If CLS text cannot be released, downgrade the claim from "benchmark" to "licensed audit resource" unless you also release a real public slice.**

**Stretch only after acceptance risk is controlled:**
- English slice.
- Additional models.
- Masking variants.
- Extended training corpus.
- Broad compatibility story.
- Tooling layer.

## 4. Predicted reviewer objections

1. **Blocking:** "This is a kitchen-sink paper."
Pre-empt by cutting to one claim: factor-controlled audit benchmark for contamination susceptibility.

2. **Blocking:** "Your main construct is still not cleanly separated from comprehension/suggestibility."
Pre-empt by explicitly leading with the CFLS failure and showing how benchmark design responds to it.

3. **Blocking:** "Cross-task deltas are uninterpretable because the perturbations are not matched."
Pre-empt with a same-template primary contrast or explicitly downgrade claims to task-template bundle effects.

4. **Blocking:** "This is not an actually usable benchmark if the main slice is hashes plus reconstruction against a proprietary corpus."
Pre-empt with a public slice, or stop calling the private slice the core benchmark contribution.

5. **Major:** "Novelty is limited; outcome-proximal tasks being leakier is unsurprising."
Pre-empt by emphasizing magnitude, residual leakage in grounded tasks, and failure boundaries, not direction alone.

6. **Major:** "Cross-lingual is bolted on."
Pre-empt by cutting it, or using genuinely comparable news sources and harmonized factor definitions.

7. **Major:** "Your temporal labels are soft because model cutoffs are approximate."
Pre-empt with cutoff sensitivity analyses and by treating closed-model temporal comparisons as suggestive, not causal.

8. **Major:** "Qwen 7B CPT does not validate DeepSeek."
Pre-empt by calling CPT an existence proof on an open model, not a mechanistic explanation of DeepSeek.

9. **Major:** "Balance targets are internally inconsistent and likely induce cherry-picking."
Pre-empt by simplifying factor structure, reporting fill rates, and disclosing exclusions/reserve sampling.

10. **Major:** "The English release/tooling story is stronger than the Chinese core, which suggests the benchmark is not mature."
Pre-empt by centering the artifact around what is actually releasable and defensible.

## 5. Venue/timeline fit

**ARR May 25, 2026 for EMNLP 2026 is possible only for the MVP above.**
It is not realistic for the full current proposal.

Concrete dates matter here:
- **EMNLP 2026 ARR deadline:** **May 25, 2026**.
- **EMNLP 2026 commitment deadline:** **August 2, 2026**.
- **ACL 2026 commitment deadline already passed on March 14, 2026.**
- **NeurIPS 2026 Evaluations & Datasets abstract deadline is May 4, 2026; full paper deadline is May 6, 2026.**
- **There is no June/July ARR fallback. The next ARR cycle after May is August 3, 2026.**

So:
- **EMNLP main:** wrong target.
- **EMNLP Findings:** right target only if you freeze a reduced scope immediately.
- **NeurIPS ED:** philosophically a fit, but not a fallback. Its deadline is earlier and its accessibility bar is stricter.
- **June/July ARR:** not an option.
- **If you miss May 25:** build properly through summer, submit to **ARR August 3, 2026** for a later venue, or use a journal route.

**Decision rule I would use:**
If the benchmark design, release story, and primary comparison are not frozen by **April 20, 2026**, do not force EMNLP 2026. You will submit an underidentified paper.

## 6. Concrete reframing recommendations

**Best titles:**
- **FinMem-Bench: A Factor-Controlled Benchmark for Outcome-Memory Auditing in Financial News LLMs**
Best conservative benchmark title.
- **When Financial LLMs Use the Future: Benchmarking Temporally Inadmissible Dependence in Financial News**
Best punch. Strongest for reviewer skim.
- **Beyond Contamination-Free Evaluation: Measuring Outcome-Memory Susceptibility in Financial LLMs**
Best positioning against AntiLeakBench / MMLU-CF / LastingBench.

Do **not** put `cross-lingual`, `mitigation`, or `toolkit` in the title unless those pieces are fully delivered.

**Restructure the paper like this:**
1. **Introduction:** contamination in finance is decision-relevant, and existing benchmarks mostly avoid contamination rather than measure it.
2. **Design Requirements from a Failed Pilot:** CFLS failed as a memorization proxy; therefore the benchmark must enforce verified outcomes, matched conflict probes, factor balance, and positive controls.
3. **Benchmark Construction:** sampling, factors, QC, release boundaries.
4. **Validation Experiments:** two models, one primary contrast, one positive control.
5. **What the benchmark does and does not measure:** explicit construct boundaries.
6. **Release and limitations:** licensing, partial openness, future extensions.

**Narrative beats to preserve:**
- "We audited a plausible proxy and found it measured the wrong thing."
- "That audit yielded concrete benchmark design requirements."
- "FinMem-Bench is the resource built to satisfy those requirements."
- "It measures contamination susceptibility, not generic finance ability."

**Licensing judgment:**
Metadata-only CLS release is survivable for a Findings paper only if you are honest that it is a **partially open audit resource**, not a fully open benchmark. I did **not** find a strong ACL/EMNLP precedent for a benchmark whose main contribution is only fingerprint-level reconstruction against a proprietary corpus. The closest accepted precedents use hidden test sets or time-delayed private questions, which is a weaker and safer restriction than yours. The "Claude Code skill" framing hurts more than it helps; ship neutral scripts first.

**Sources checked:** [EMNLP 2026 CFP](https://2026.emnlp.org/calls/main_conference_papers/), [ACL 2026 CFP](https://2026.aclweb.org/calls/main_conference_papers/), [ARR dates](https://aclrollingreview.org/dates), [AntiLeakBench](https://aclanthology.org/2025.acl-long.901/), [MMLU-CF](https://aclanthology.org/2025.acl-long.656/), [LastingBench](https://aclanthology.org/2025.findings-emnlp.993/), [LiveBench](https://proceedings.iclr.cc/paper_files/paper/2025/file/e4a46394ba5378b3f9a186a5b4c650d1-Paper-Conference.pdf), [NeurIPS 2026 ED Track blog](https://blog.neurips.cc/category/2026-conference/), [NeurIPS 2026 ED CFP](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets), [CFinBench](https://aclanthology.org/2025.naacl-long.40.pdf), [InvestorBench](https://aclanthology.org/2025.acl-long.126/). I did not find a strong ACL/EMNLP precedent matching the exact `CLS metadata + fingerprint reconstruction` release model; that absence is itself informative.
