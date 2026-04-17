# NLP/ML Review of Experiment Plan

## Score

**6.5/10**

## Verdict

**Promising, but not top-venue ready in its current experimental form.**

The core idea is good and potentially publishable: task design may modulate measured leakage on fixed financial-news inputs. The current plan is much stronger than a typical early proposal. But the central measurement object, excess invariance (EI), is not yet operationalized in a way that is comparable across task families, and the current implementation does not match the proposal on that point. That is the main blocker. The other major risks are a still-too-weak sham control, counterfactual QC that remains overly LLM-centric, and a ground-truth protocol that leans too heavily on model votes for a benchmark paper.

## Strengths

- The research question is real: task formulation as a moderator of leakage is a meaningful NLP methods contribution.
- The fixed-input paired design is the right backbone. Comparing task families on the same `(article, target)` items is much better than cross-dataset comparisons.
- The plan anticipates reviewer attacks in the right places: neutral paraphrases, matched-format ablation, sham control, cluster-level accounting, and time-based/placebo checks are all directionally correct.
- The novelty prompt has been reframed from ontic firstness to article framing. That is a strong improvement and much easier to defend.
- The prompt catalogs show good target conditioning and explicit evidence requirements.

## Major Weaknesses

### 1. Excess invariance is not yet well-defined across task families, and the implementation does not match the proposal

The proposal treats EI as the primary E3 estimand, but the code currently does not implement a task-comparable version of that estimand.

- In `src/metrics.py`, `_extract_label()` only recognizes `parsed_direction`, `label`, `parsed_label`, or `direction`, then falls back to a 5-bin direction distribution.
- It does **not** recognize `sentiment`, `source_credibility`, `regulatory_vs_rumor`, `official_vs_unattributed`, `disclosure_frame`, `information_freshness`, or `novelty_strength`.
- As a result, `_excess_invariance_components()` uses **label mode** for direct prediction but falls back to **confidence mode** for sentiment and decomposition tasks when confidence is present.
- I sanity-checked this behavior with synthetic payloads in the current environment: direct outputs score as `mode='label'`, while sentiment and authority outputs score as `mode='confidence'`.

This is a serious measurement non-invariance. The claimed ordering `direct > sentiment > authority/novelty` would partly compare label stability to confidence stability.

There is also a deeper design problem: EI is underdefined for multi-field tasks. For `provenance_swap`, only the authority-relevant fields should change. For `novelty_toggle`, only the novelty-relevant fields should change. The current metric has no notion of expected changed fields versus expected unchanged fields. It therefore does not actually test the proposal's construct for decomposed tasks.

Additional implementation mismatch:

- `batch_excess_invariance()` is an item-level mean, not a cluster-level estimand with cluster aggregation.
- `src/experiment.py` is still the legacy masking-based runner using `src/prompts.py`, not the frozen task-conditioned prompt catalogs in `config/prompts/`.
- In practice, the new prompt system appears wired mainly through smoke tests, not the main experiment runner.

### 2. The counterfactual QC pipeline is good by workshop standards, but not yet rigorous enough for a strong ACL/EMNLP review

The 4-stage QC design is directionally good, but it is still too dependent on LLMs and too narrow in retrieval scope.

- Two LLM judges are not enough when the full paper depends on rewrite validity.
- Retrieval-based nonexistence is checked only against the CLS corpus. That is not enough for Chinese financial news, which is heavily syndicated and duplicated across outlets.
- Querying by title plus first 80 characters with high similarity thresholds is likely low-recall for paraphrastic near-duplicates.
- `changed_spans` are self-reported by the generation model. The plan lacks a strong independent audit that only intended spans changed.
- The plan mentions unchanged-field checks for rewrites, but not with enough specificity. For top-venue rigor, you need per-template reporting of:
  - intended field changed,
  - non-target fields stayed unchanged,
  - target preserved,
  - no new economically material facts introduced.

Right now the QC story is plausible, but still too easy for a skeptical reviewer to dismiss as "LLMs validating LLM-generated rewrites."

### 3. The sham-decomposition control does not yet test what it claims sharply enough

The sham idea is good, but the current sham variables are too surface-level.

- `formality_level`, `numeric_density`, and `sentence_complexity` are much more lexical and directly observable than authority or novelty.
- That means the sham task is not matched on abstraction level, ambiguity, or inferential burden.
- `sham_edits` are also highly local and deterministic. A model can succeed on them through simple lexical sensitivity.

So the current sham does **not** cleanly test "generic extraction burden" versus "meaningful decomposition." A skeptical reviewer can still argue that the sham is simply the wrong control.

A stronger sham would be target-conditioned, evidence-based, economically irrelevant, but similar in abstraction and uncertainty to the meaningful decomposition tasks, e.g. attribution granularity, discourse scope, claim explicitness, or temporal framing that is not economically informative.

### 4. The matched-format ablation does not eliminate the most important remaining confounds

The matched-format ablation helps, but it does not solve the hard identification problem.

- It does not control **edit salience**. `semantic_reversal`, `provenance_swap`, and `novelty_toggle` are not matched interventions.
- It does not control **task-answer inferability from text**. Direct prediction is outcome-proximal; authority and novelty are much closer to text-internal cues.
- It does not control **label entropy / ambiguity**. Neutral and unclear rates may differ sharply across tasks.
- It does not control **field structure**. Direct and sentiment are effectively single-label tasks, while authority and novelty are multi-field tasks.

So even if the matched-format ordering survives, the correct interpretation is still something like:

> tasks that are more text-internal and less outcome-proximal show lower measured leakage

That is interesting, but it is weaker and more defensible than:

> decomposition itself is the mitigation mechanism

To make the stronger claim, the plan needs an inferability/difficulty control, preferably human-rated or at least model-free.

### 5. The prompt schema is directionally good, but the design and enforcement are not yet strong enough

The prompt design has real strengths, but there are still important weaknesses.

- The file referred to as frozen prompt schema v2 is still labeled `schema_version: prompt_schema_v1`. That suggests the versioning discipline is not fully locked.
- The base prompts remain structurally different. Direct/sentiment return flat evidence strings; decomposition returns field-linked evidence objects. So the base E3 comparison is still structurally confounded by design.
- `neutral` and `unclear` overload abstention with substantive labels. That is a problem for both annotation and EI.
- `confidence` is underdefined and, given the current metric code, overly consequential.
- `schema_validation.py` checks JSON structure and enum membership, but it does **not** enforce:
  - `target_echo` actually matching the provided target,
  - evidence quotes appearing in the article,
  - evidence supporting the claimed field,
  - unchanged-field expectations for rewrites.

The prompt contract is good on paper but weakly enforced in code.

### 6. The ground-truth annotation protocol is still too LLM-centric for a benchmark paper

The proposed annotation workflow is better than single-model labeling, but it is still not strong enough as a benchmark gold standard.

- Using LLMs as the primary annotators for a leakage benchmark is risky, especially when some of those same model families are also used elsewhere in the study.
- DeepSeek as both evaluated system and annotator is methodologically awkward.
- Qwen is used both as a detector/judge and annotator.
- "Confidence spread >20" is not a good arbitration trigger because model confidence is not calibrated across systems.
- Rewrite annotation only on edited fields is efficient, but it will miss unintended spillover unless a stratified subset is fully re-annotated.
- The plan still needs a real annotation manual with examples, edge cases, and adjudication rules, especially for authority and novelty.

For a top venue, I would want:

- full human annotation on all Tier1 originals,
- human validation of a substantial stratified rewrite sample across all templates,
- explicit use of external metadata where available for authority/novelty adjudication,
- per-field agreement reporting, not just broad task-family kappa summaries.

## Specific Recommendations

1. **Redefine EI as a task-specific field-level violation score.**  
   For each task family, explicitly specify which field(s) are expected to change under the targeted counterfactual and which must remain stable. Score the counterfactual against those expectations, then subtract paraphrase instability on the same field set.

2. **Add prompt metadata for expected changed/unchanged fields.**  
   The prompt catalog should expose something like `primary_field`, `expected_changed_fields`, and `expected_unchanged_fields` so scoring is not inferred from ad hoc field names.

3. **Do not use confidence as the fallback primary metric.**  
   Confidence-based EI can be a secondary diagnostic, but it should not be the main estimand.

4. **Redesign the sham control.**  
   Replace purely lexical sham fields with target-conditioned but economically irrelevant judgments at a similar abstraction level to authority/novelty.

5. **Strengthen rewrite QC.**  
   Add broader cross-source retrieval, human validation of intended flip success, and explicit spillover auditing for non-target fields.

6. **Add inferability/difficulty controls.**  
   Obtain human ratings or a model-free proxy for "answerable from the article alone" and test whether the E3 ordering survives conditioning on that factor.

7. **Upgrade the annotation protocol.**  
   Treat LLM annotators as assistants or secondary raters, not the primary gold source. Move more central labels onto humans for Tier1 and a stratified rewrite sample.

8. **Tighten schema enforcement in code.**  
   Enforce `target_echo`, evidence-substring checks, and field-linked evidence support. Right now the code validates shape, not grounding.

9. **Align the runnable code path with the paper story.**  
   The main experiment runner should use the frozen prompt catalogs and the task-aware EI metric. At the moment, the implementation story is still split between legacy runners and new smoke-test utilities.

## Bottom Line

This is a good paper idea, and the proposal has moved in the right direction. But in the current plan and code, the central NLP methods question is still not fully nailed down. The biggest blocker is the primary metric: until EI is defined and implemented in a field-aware, task-comparable way, the main task-ordering claim will remain vulnerable to a strong methods review.
