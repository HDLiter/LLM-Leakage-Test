# Editorial Review of the Experiment Plan

## Score
**7.5/10**

## Verdict
**Conditionally supportive for EMNLP Findings.**  
I would champion a narrower paper centered on **C1**: task design changes the *measured leakage proxy* on fixed Chinese financial-news inputs, and that pattern survives matched-format and sham controls. I would **not** champion the full `C1 + C2` package as currently staged, because the C2 evidence is materially weaker and the current milestone logic introduces avoidable credibility risk.

## Bottom Line
The plan is much closer to a real paper than the proposal alone. The narrative now has a recognizable spine:

1. build a benchmark that is credible enough to trust,
2. show the primary ordering on fixed inputs,
3. show the effect survives the strongest structural falsifications,
4. use time and white-box familiarity as triangulation.

That is coherent. What is not coherent is treating all four stages as equally essential. The paper will live or die on **Block 2 + Block 3**. Block 4 strengthens the interpretation, but it is not equally robust, and it should not be allowed to drag the whole paper into overclaim or schedule failure.

## Strengths
- The core claim is now sharply defined. The plan is no longer trying to be four papers at once.
- The paired fixed-input design is exactly right for the main thesis. Running different task formulations on the same `(article, target)` clusters is the strongest part of the paper.
- Matched-format prompts and sham decomposition directly target the most dangerous reviewer objection: “this is a prompt-format paper, not a leakage paper.”
- The benchmark pipeline is auditable and serious. For this topic, benchmark credibility is not optional; the plan understands that.
- The must-run versus nice-to-have split is much better than in the proposal. Demoting E5/E6 was the correct move.
- The plan is disciplined about bounded language in several places: “measured leakage,” “excess invariance,” “concordance,” and “supporting evidence” are all directionally right.

## Weaknesses
- **C2 is over-weighted relative to how convincing it can actually be.** The DeepSeek “placebo frontier” is not a true knowledge cutoff, because a public model upgrade date is not equivalent to a documented training boundary.
- **The milestone logic contains one serious methodological mistake.** `M3` says to continue to `M4` only if the primary ordering looks promising. That invites a hostile reviewer to call the robustness stage selectively pursued.
- **The benchmark timeline is internally inconsistent and optimistic.** The detailed benchmark build is budgeted at `10.5` working days, while milestone `M1` is priced at `3-4` days wall time. Both cannot be right.
- **Cross-task comparability is still not fully nailed down.** Direct/sentiment use semantic reversals, authority uses provenance swaps, novelty uses framing toggles. Even with neutral-paraphrase normalization, a reviewer can still argue that the edit families differ in severity and answerability.
- **The benchmark remains vulnerable on “gold label” credibility.** Much of the annotation stack is LLM-based, with human audit concentrated in Tier1. That is acceptable if described carefully, but not if presented as uniformly human-quality gold across all 1,000 cases.
- **The documents are not perfectly synchronized.** The proposal still reads in places like an earlier version of the study. Reviewers notice this kind of drift.

## Assessment Against the Key Questions

### 1. Does the plan deliver the evidence needed for the paper’s claims?
For **C1**, mostly yes. The paper only needs to show that task design changes the contamination-sensitive behavioral metric on the same items, and that the effect is not obviously reducible to output structure. Blocks 2 and 3 are well designed for that purpose.

For **C2**, only partially. A positive association with article age and Qwen familiarity would be useful triangulation, but it is not decisive evidence. The weakest element is the proposed placebo framing around the DeepSeek version boundary. That is not a true placebo in the causal or temporal sense; at best it is a **false-positive stress test tied to a documented model version date**.

The paper is therefore viable if the claims stay bounded to:
- task design changes the measured leakage proxy,
- matched-format and sham controls make a pure format explanation less plausible,
- time and white-box familiarity are supportive but not dispositive.

It is **not** yet viable if the authors want to claim that the plan establishes leakage mitigation in a strong causal sense.

### 2. Is the scope right?
At the paper level, the scope is now close to right. The strongest version is:
- benchmark credibility,
- primary ordering on fixed inputs,
- matched-format ablation,
- sham falsification.

That is an EMNLP Findings paper.

The current problem is that Block 4 is still treated as equally must-run. I would not do that. If time tightens, the paper should be willing to stand as:
- `B1`: benchmark freeze,
- `B2`: primary ordering,
- `B3`: matched-format + sham.

Then `B4` becomes supporting evidence, not acceptance-critical evidence. Right now the plan is better than the proposal, but still slightly too ambitious in what it considers non-negotiable.

### 3. Are the milestones and decision gates realistic?
Not fully.

The best gate is `M1`: if the benchmark is not trustworthy, do not run the rest. That is correct.

The worst gate is `M3`: “continue to M4 only if point estimates are ordered or directionally promising.” That should be removed. Robustness and falsification should be run regardless of whether the early result looks favorable. Otherwise the paper exposes itself to a very obvious reviewer criticism about selective execution.

The timing is also too optimistic:
- the plan says benchmark construction takes `10.5` working days,
- the milestone table says `M1` takes `3-4` days wall time,
- the plan also requires reserve backfills, human review, arbitration, and exact 72-cell fills.

In practice, the binding constraint will be **benchmark curation**, not model inference. The plan should budget more like **4-6 weeks** for benchmark plus must-run experiments, not treat benchmark freeze as a short operational prelude.

### 4. What would a hostile reviewer attack, and does the plan preempt those attacks?
The strongest likely attacks are:

- **“This is a task-difficulty / prompt-format paper, not a leakage paper.”**  
  The plan preempts this reasonably well with matched-format prompts and sham decomposition. This is the strongest defensive part of the design.

- **“Your leakage proxy is not comparable across task families because the edits are different.”**  
  The plan only partially preempts this. Neutral-paraphrase subtraction helps, but it does not fully equalize edit severity or answerability across `semantic_reversal`, `provenance_swap`, and `novelty_toggle`.

- **“Your placebo frontier is not a real frontier.”**  
  The plan does not preempt this enough. A model version upgrade date is not a documented data cutoff.

- **“Your benchmark labels are model-labeled, not gold-labeled.”**  
  The plan partially preempts this with Tier1 human audit and arbitration, but it must be extremely careful not to overstate the gold quality of Tier2.

- **“The benchmark is proprietary and may not be reusable.”**  
  The plan acknowledges the licensing risk, but if full text is unreleasable, the benchmark contribution becomes secondary rather than central.

### 5. Is the benchmark construction pipeline over-engineered or appropriately thorough?
Conceptually, it is **appropriately thorough**. On this paper, benchmark construction is not background engineering; it is part of the scientific argument. The clustering, reserve pools, rewrite QC, retrieval nonexistence, and arbitration logs are justified.

Operationally, however, it is **slightly over-committed** for a 10-week project. The problem is not the existence of the checks; the problem is treating the full release-grade pipeline as a hard prerequisite for every paper milestone. For submission purposes, the paper needs:
- clear target linking,
- credible clustering,
- good rewrite QC,
- audited anchor subset,
- transparent failure/backfill accounting.

It does **not** need every benchmark artifact to be polished to release quality before the core experiments can be interpreted.

### 6. Does the plan separate must-run from nice-to-have cleanly enough?
Only partially.

At the coarse level, yes: E5 and E6 are correctly demoted.

At the finer level, not quite. The real must-run set is:
- benchmark freeze,
- primary leakage spectrum,
- matched-format ablation,
- sham falsification.

The temporal decay and Qwen concordance analyses are useful, but they should not be treated as equally paper-defining. In particular, the current C2 package contains the highest interpretive fragility in the entire paper. It should strengthen the story if it works, not determine whether the story exists.

### 7. Is the stated 10-week timeline feasible?
**Feasible, but only with discipline.**

If the team insists on:
- exact 72-cell fills,
- high rewrite pass rates in every template,
- full arbitration,
- full robustness appendix,
- a strong temporal/placebo package,
- and optional downstream analyses,

then 10 weeks is optimistic.

If the team instead treats the paper as a disciplined EMNLP Findings submission focused on C1, then 10 weeks is realistic. The likely successful allocation is:
- Weeks 1-4: benchmark build, QC, and freeze,
- Weeks 5-6: primary runs and falsifications,
- Weeks 7-8: supporting temporal/concordance analyses,
- Weeks 9-10: figures, paper writing, cleanup, and one re-run buffer.

That is feasible. The current milestone table simply understates where the time will go.

## Specific Recommendations

### 1. Make C1 the acceptance claim and C2 a supporting claim
The paper should be willing to succeed even if the temporal/Qwen triangulation is weaker than hoped. If C1 is strong and Block 3 is convincing, that is already a publishable Findings paper.

### 2. Remove the `M3` stop/go gate immediately
Run matched-format and sham controls whether or not the early ordering is favorable. Otherwise the paper looks selectively validated.

### 3. Add one explicit cross-family calibration study
Take a modest audited subset and rate:
- edit magnitude,
- plausibility,
- answerability,
- and perceived task difficulty

across the direct, sentiment, authority, and novelty counterfactual families. Without this, comparability remains the cleanest attack on the main result.

### 4. Reframe the DeepSeek placebo analysis
Do not call it a knowledge frontier. Call it a **documented-version false-positive check** or **post-version stress test**. If possible, add a second freshness diagnostic that does not rely on the proprietary boundary story.

### 5. Relax the all-or-nothing benchmark freeze criteria for Tier2
Exact balance is elegant, but endless same-cell backfilling can consume the schedule. Predefine a fallback rule for modest Tier2 underfill with transparent weights or reporting, while keeping Tier1 strict.

### 6. Synchronize the documents before further execution
The proposal, experiment plan, and tracker should describe the same benchmark size, audited subset, and execution sequence. Right now the plan is the best version, but the package still shows drift.

### 7. Keep the benchmark claim bounded if text release is restricted
If CLS text cannot be released, present the benchmark contribution as a curated audit resource with reusable metadata and prompts, not as a fully open benchmark on the level of public NLP datasets.

## Final Judgment
This is now a **potentially strong EMNLP Findings paper**, but only if the authors are disciplined about what the paper is actually proving.

The plan is good enough to support a paper whose main sentence is:

> On fixed Chinese financial-news inputs, task formulation materially changes a contamination-sensitive behavioral metric, and that pattern survives matched-format and sham controls.

The plan is **not** yet good enough to support a stronger sentence claiming that the paper has cleanly established causal leakage mitigation, or that the DeepSeek temporal placebo identifies a genuine knowledge boundary.

If the authors narrow the paper to that stronger C1 spine, fix the milestone logic, and soften the C2 frontier language, I would be comfortable championing it.
