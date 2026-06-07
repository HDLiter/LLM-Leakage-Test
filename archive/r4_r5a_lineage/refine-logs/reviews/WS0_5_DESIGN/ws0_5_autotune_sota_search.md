# WS0.5 Auto-tune Loop — Literature & Industry SOTA Search

**Analyst**: Codex CLI gpt-5.5 xhigh
**Date**: 2026-05-18
**Task**: Find better methods than Claude's current Claude-vs-Codex patch + bootstrap CI gate + K-rotation loop.

## 1. Survey table

Concern key: **1** adaptive holdout reuse, **2** multi-proposer selection bias, **3** fixture quality, **4** prompt optimization framework, **5** metric robustness.

| Method | Reference | Solves (1-5) | Fits R5A? | Cost |
|---|---|---|---|---|
| DSPy core | [Khattab et al., 2023/ICLR 2024, arXiv:2310.03714](https://arxiv.org/abs/2310.03714) | 2, 4 | **Yes**. R5A's three prompts can be expressed as three DSPy signatures/modules, with DeepSeek V4 Pro as task LM and existing metrics as compile metrics. | **Medium**. 1-2 days if DeepSeek is OpenAI-compatible via LiteLLM/DSPy; more if custom adapter/output extraction is needed. |
| MIPRO / MIPROv2 | [Opsahl-Ong et al., EMNLP 2024, arXiv:2406.11695](https://arxiv.org/abs/2406.11695); [DSPy optimizer docs](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/optimization/optimizers.md) | 2, 4, 5 | **Yes**. Black-box LM, no logprobs, jointly optimizes instructions and few-shot demos; good for classification/extraction prompts with labeled fixture. | **Medium**. Need wrapper, metric, train/val split, prompt extraction. API cost acceptable. |
| GEPA reflective prompt evolution | [Agrawal et al., ICLR 2026 oral, arXiv:2507.19457](https://arxiv.org/abs/2507.19457); [DSPy GEPA docs](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/api/optimizers/GEPA/overview.md) | 2, 4, partial 5 | **Yes, strongest optimizer candidate**. Uses textual feedback and Pareto frontier; maps well to error logs such as missing entity, wrong topic, schema violation. Needs external holdout discipline. | **Medium-high**. 1-3 days integration; more experimental than MIPROv2 but sample-efficient. |
| TextGrad | [Yuksekgonul et al., arXiv:2406.07496](https://arxiv.org/abs/2406.07496) | 2, 4 | **Partial**. Good conceptual fit for "textual gradients"; broad framework, but less directly packaged for frozen production prompt extraction than DSPy/GEPA. | **Medium**. Need objective graph and textual feedback design. |
| ProTeGi / APO | [Pryzant et al., EMNLP 2023, arXiv:2305.03495](https://arxiv.org/abs/2305.03495) | 2, 4, partial 5 | **Yes as an algorithmic enhancement**. Minibatch textual gradients + beam search + bandit selection is a cleaner version of "LLM proposes patch". | **Medium**. Implementable without full framework; needs candidate beam bookkeeping. |
| OPRO | [Yang et al., ICLR 2024, arXiv:2309.03409](https://arxiv.org/abs/2309.03409) | 2, 4 | **Partial**. Simple black-box optimizer, but can overfit dev quickly if used naively. Good baseline/proposer, not final governance. | **Low-medium**. Meta-prompt + score history + candidate scorer. |
| PromptWizard | [Agarwal et al., arXiv:2405.18369](https://arxiv.org/abs/2405.18369); [Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/promptwizard-the-future-of-prompt-optimization-through-feedback-driven-self-evolving-prompts/) | 2, 4 | **Yes as alternative framework**. Optimizes instructions plus in-context examples with feedback-driven critique/synthesis; black-box. | **Medium**. Open-source but integration and output format hardening needed. |
| EvoPrompt / evolutionary prompt search | [Guo et al., ICLR 2024, arXiv:2309.08532](https://arxiv.org/abs/2309.08532) | 2, 4 | **Partial**. Population search is better than two patch proposers, but older than GEPA and dev-overfit risk remains. | **Medium-high**. Population/evolution budget and validation governance required. |
| APE / Automatic Prompt Engineer | [Zhou et al., arXiv:2211.01910](https://arxiv.org/abs/2211.01910) | 2, 4 | **Partial**. Useful for seed prompt generation; weaker than iterative/reflection/population methods for final tuning. | **Low**. Generate candidate instructions, evaluate. |
| Auto-CoT | [Zhang et al., arXiv:2210.03493](https://arxiv.org/abs/2210.03493) | 4 | **Mostly no**. R5A tasks are classification/extraction/profile, not math-style reasoning; CoT may increase verbosity and schema failures. | **Low**, but likely negative unless hidden reasoning improves a specific failure cluster. |
| Thresholdout / reusable holdout | [Dwork et al., Science 2015](https://pubmed.ncbi.nlm.nih.gov/26250683/); [arXiv:1506.02629](https://arxiv.org/abs/1506.02629) | 1, 5 | **Partial**. Canonical answer to adaptive holdout reuse; exact DP/noise implementation is overkill for single-operator prompt tuning, but the limited-exposure idea is highly relevant. | **High** if formal; **medium** if adapted as pass/fail acceptance gate. |
| Generic Holdout | [Nakkiran & Blasiok, arXiv:1809.05596](https://arxiv.org/abs/1809.05596) | 1, 5 | **Partial**. Useful principle: analyst may explore freely, but holdout only answers "is this hypothesis good enough?" not "how much better?". | **Medium**. Implement as binary acceptance oracle, not exact score dashboard. |
| Ladder leaderboard | [Blum & Hardt, ICML 2015](https://proceedings.mlr.press/v37/blum15.html) | 1, 5 | **Yes as practical adaptation**. Only update/report when candidate beats incumbent by a threshold; directly fits prompt candidate acceptance. | **Low-medium**. Add thresholded paired acceptance and hide exact acceptance scores. |
| Nested CV / cross-fitted validation bank | Standard ML model selection; aligned with adaptive analysis concerns | 1, 5 | **Yes**. With 2000+ fixture and budget, use multiple inner folds/shards and locked final holdout; no need for DP math. | **Low-medium**. Mostly data split and logging discipline. |
| Active learning for NLP fixture build | [Zhang, Strubell & Hovy, EMNLP 2022 survey](https://aclanthology.org/2022.emnlp-main.414.pdf) | 3 | **Yes**. Use uncertainty/disagreement/diversity sampling to label high-value slices instead of random-only rotation. | **Low-medium**. Need candidate pool, embeddings/clusters, adjudication queue. |
| LLM-in-loop annotation | [Kholodna et al., ECML PKDD 2024, arXiv:2404.02261](https://arxiv.org/abs/2404.02261) | 3 | **Yes with guardrails**. Claude+Codex dual labels are consistent with this; add inter-annotator agreement, active sampling, and agreement audits. | **Low-medium**. Existing dual-agent flow already close. |
| LLM-assisted annotation bias caution | [Schroeder, Roy & Kabbara, arXiv:2507.15821](https://arxiv.org/abs/2507.15821) | 3, 5 | **Yes as warning**. Do not let LLM suggestions silently shift gold labels, especially subjective signal-profile labels. | **Low**. Blind or staged adjudication for final holdout. |
| Annotation Error Detection / ActiveAED | [Weber & Plank, Findings ACL 2023, arXiv:2305.20045](https://arxiv.org/abs/2305.20045) | 3 | **Yes**. Use current prompt/committee disagreements to flag likely bad fixture labels for re-adjudication. | **Low-medium**. Add error-audit queue after each rotation. |
| Paired permutation / approximate randomization / paired bootstrap | [Dror et al., ACL 2018](https://aclanthology.org/P18-1128/) | 5 | **Yes**. Better than non-overlap of separate bootstrap CIs because prompt outputs are paired on the same examples. | **Low**. Implement reusable paired-test utilities. |
| McNemar exact / matched-pair tests | Standard paired nominal comparison | 5 | **Yes for pass/fail per-example outcomes**. Useful for topic exact-match or schema-valid pass/fail; not enough for entity F1 alone. | **Low**. Use with exact binomial variant for small discordance counts. |
| Error bars for LLM evals | [Miller, arXiv:2411.00640](https://arxiv.org/abs/2411.00640); [Bowyer et al., ICML 2025 position, arXiv:2503.01747](https://arxiv.org/abs/2503.01747) | 5 | **Yes**. Report paired deltas and uncertainty; avoid CLT shortcuts on small specialized slices. | **Low-medium**. Bootstrap/Bayesian intervals and minimum detectable effect planning. |
| Alpha spending / online multiple testing | Sequential testing literature; see [Johari et al., always-valid inference, arXiv:1512.04922](https://arxiv.org/abs/1512.04922) | 1, 5 | **Yes in lightweight form**. Pre-register max looks and spend alpha across rotations/candidates; prevents repeated p<0.05 peeking. | **Medium**. Needs a simple alpha ledger. |
| OpenAI eval + prompt optimizer practice | [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices); [OpenAI prompt optimizer docs](https://developers.openai.com/api/docs/guides/prompt-optimizer) | 3, 4, 5 | **Partial**. Shows productized pattern: datasets, graders, annotations, critiques, repeat optimization. Not directly usable for DeepSeek target. | **Low** as design reference; **no** for direct optimizer unless using OpenAI stack. |
| Anthropic eval guidance | [Create strong empirical evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | 3, 5 | **Yes as practice**. Task-specific evals, automated grading first, large test volume, reliability checks for LLM graders. | **Low**. Adopt in fixture/eval policy. |
| LangSmith / Promptfoo / W&B Weave | [LangSmith experiments](https://docs.langchain.com/langsmith/analyze-an-experiment); [Promptfoo LLM judge guide](https://www.promptfoo.dev/docs/guides/llm-as-a-judge/); [W&B Weave DSPy tutorial](https://docs.wandb.ai/weave/reference/gen_notebooks/dspy_prompt_optimization/) | 3, 5 | **Partial**. Valuable for versioning, experiment metadata, judge bias mitigations, trace logs; not necessary if repo logs are already strong. | **Low-medium**. Use ideas, not necessarily products. |
| Dynamic few-shot / KNN retrieval | [Skill-KNN, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.831/); DSPy KNNFewShot docs via optimizer list | 3, 4 | **Partial-to-yes**. Strong alternative if "frozen prompt" can include frozen retrieval policy + example bank; less suitable if manifest requires static prompt text only. | **Medium**. Need embedding index and inference-time retrieval. |

## 2. Method deep-dives (3-5 most relevant)

### 2.1 DSPy GEPA / MIPROv2

DSPy is the best current fit if R5A wants a real auto-prompt-tuning framework rather than a hand-built patch duel. The original DSPy paper frames LM pipelines as declarative modules and compiles them against a metric, replacing brittle prompt strings with optimizable program parameters. MIPRO then extends this to optimize both instructions and few-shot demonstrations without gradients or logprobs. That matters for DeepSeek V4 Pro because the API is black-box: the optimizer only needs generated outputs and a metric.

MIPROv2 is closest to a statistically cleaner "multi proposer select one" loop. It uses data-aware instruction proposals, stochastic minibatch evaluation, and a surrogate/meta-optimization procedure. Compared with Claude+Codex each proposing one patch, it searches a candidate space and allocates evaluation budget systematically.

GEPA is newer and more directly aligned with Claude's current design because it uses reflective textual feedback from failed trajectories. The important difference is that GEPA does not just mutate the current best prompt. It maintains a Pareto frontier of candidates that perform best on different validation instances, so it preserves complementary rules instead of collapsing to the single locally best patch. R5A can feed GEPA feedback like:

- `topic`: expected vs predicted topic, missed cue, over-broad label.
- `entity`: missing entity, hallucinated entity, wrong span, duplicate, schema error.
- `signal_profile`: wrong profile field, evidence mismatch, missing uncertainty flag.

Applicability: **high**. It directly solves concern 4 and largely concern 2. It does **not** automatically solve concern 1; a GEPA run can still overfit the validation set if allowed unlimited adaptive feedback. Therefore GEPA/MIPRO should be wrapped in a separate acceptance gate and a locked final holdout.

### 2.2 Reusable holdout, Ladder, and limited-exposure validation

Dwork et al. are the canonical reference for the user's adaptive holdout concern. Their key point is not just "do not use the test set"; it is that adaptively chosen hypotheses become statistically invalid when the same holdout gives detailed feedback repeatedly. Thresholdout/reusable holdout solves this with privacy/noise ideas and only reveals holdout information in controlled ways. The Generic Holdout makes the operational lesson even clearer: the analyst may explore freely on an exploration set, but the holdout should answer only whether a hypothesis passes, not expose a rich score surface.

For R5A, a full differential privacy implementation is probably not worth it. The practical version is:

1. Keep `train_visible`: proposers see errors and labels here.
2. Keep `inner_dev`: optimizer ranks/filter candidates here.
3. Keep `acceptance_holdout`: never shown to proposers; only returns pass/fail or rounded deltas to the loop controller.
4. Keep `final_holdout`: touched once at the end.

The acceptance rule should be Ladder-like: update the incumbent only when a candidate beats it by a pre-registered practical margin and a paired statistical gate. Do not show exact acceptance scores back to Claude/Codex/optimizer. That single change is more rigorous than K-round rotation, because rotation still exposes many dev slices adaptively.

Applicability: **high as an engineering pattern**, **partial as formal DP**. It is the best answer to concern 1 under the single-operator constraint.

### 2.3 ProTeGi / TextGrad textual-gradient tuning

ProTeGi, the predecessor idea to TextGrad-style textual optimization, uses minibatches of errors to produce natural-language "gradients", edits the prompt in the opposite semantic direction, and guides search with beam search plus bandit selection. This is very close to what Claude and Codex are doing manually, except it makes the process population-based, minibatch-based, and budget-aware.

TextGrad generalizes this into an automatic-differentiation-like interface for compound AI systems: LLMs provide textual feedback that is backpropagated to variables, including prompts. It is attractive for multi-component systems, but for R5A's three mostly single-prompt tasks, GEPA or ProTeGi is simpler.

Applicability: **medium-high**. Use it as an enhancer if DSPy integration is too heavy: have Claude/Codex generate structured textual gradients from train errors, maintain a beam of prompt candidates, and allocate eval budget with UCB/successive-halving. It improves concern 2 and 4 but still needs the same validation guardrails.

### 2.4 Active fixture build and annotation auditing

R5A's dual-agent labeling is directionally good, but random rotation is not the most label-efficient fixture strategy. The active learning literature for NLP separates query strategies into informativeness, disagreement, representativeness/diversity, and hybrids. For black-box LLM prompt tuning, the most useful practical mix is:

- stratified random base sample for unbiased metric estimation;
- model/proposer disagreement cases for boundary conditions;
- high-confidence mismatches between current prompt and gold for error hotspots;
- embedding-cluster diversity to avoid sampling only weird outliers;
- rare label/entity/signal coverage quotas.

LLM-in-loop annotation work supports using LLMs to reduce data requirements, but recent subjective-task work warns that showing LLM suggestions can shift label distributions. For final holdout and subjective signal-profile labels, use staged adjudication: the single operator writes/chooses a label before seeing Claude/Codex labels, or at least logs when the adjudicator overrode/accepted an LLM suggestion.

Applicability: **high**. This is the most useful upgrade for concern 3 and also improves metric stability.

### 2.5 Paired tests, multiple looks, and reporting uncertainty

Bootstrap CI is not wrong, but "two independent CIs do not overlap" is the wrong default gate. Prompt A and prompt B are evaluated on the same examples, so the test must use paired differences. For arbitrary NLP metrics, paired bootstrap or paired approximate randomization/permutation tests are standard. For binary per-example correctness, exact McNemar/binomial matched-pair tests are more direct. For entity extraction F1, paired bootstrap/permutation over examples is generally the most practical.

The bigger problem is repeated decisions. If every round tests "candidate > incumbent" at alpha 0.05, false accept risk compounds. Use one of:

- simple alpha spending over all acceptance looks, e.g. pre-register 30 possible accept tests and spend alpha by schedule;
- Holm-Bonferroni within each round for multiple candidates and across the three prompt families when reporting "wins";
- a Ladder threshold with practical effect size `delta_min`, so tiny noisy wins are ignored;
- final holdout only once, with no back-propagation into prompt changes.

Applicability: **high**. This is low engineering cost and directly fixes concern 5.

## 3. Proposed alternatives

### Scheme X — Full DSPy GEPA/MIPRO Compile

**Pipeline**:

1. Define three DSPy modules: `TopicClassifier`, `EntityExtractor`, `SignalProfiler`.
2. Wrap DeepSeek V4 Pro as the task LM. Use Claude/Codex or a strong model as GEPA reflection/proposal LM if available; otherwise use the same task LM.
3. Convert Thales v2-v6 prompts into seed instructions and optional labeled demos.
4. Build `train_visible`, `inner_dev`, `acceptance_holdout`, `final_holdout` per prompt family.
5. Run GEPA first for instruction evolution using metric objects that return both scalar score and textual feedback.
6. Run MIPROv2 or BootstrapFewShot/KNNFewShot to optimize demonstration selection if few-shot improves dev.
7. Export top candidate prompts. Evaluate candidate vs incumbent on `acceptance_holdout` through paired permutation/bootstrap plus Ladder/alpha-spending gate.
8. Freeze the accepted prompt and run `final_holdout` once.

**Solves**: concern 2 and 4 strongly; concern 5 if wrapped with paired tests; concern 1 only if acceptance holdout is separate; concern 3 only if active fixture is added.

**Cost**: 12-30 engineering hours depending on DeepSeek/DSPy compatibility; high API calls but acceptable under budget. Fixture cost unchanged unless adding active sampling.

**Risk**:

- DSPy/GEPA integration may take longer than the WS0.5 decision window.
- Optimized prompts can become verbose or overfit without external acceptance gate.
- Extracting exactly three frozen prompts from a DSPy program may require custom serialization checks.

### Scheme Y — Hybrid Current Loop + Limited-Exposure Acceptance Gate + Active Fixture

**Pipeline**:

1. Keep the current Thales prompt files and existing CI/eval harness.
2. Replace the 2-candidate duel with a candidate pool per round:
   - Claude patch;
   - Codex patch;
   - ProTeGi/TextGrad-style "textual gradient" patch from train errors;
   - optional OPRO/PromptWizard-style rewrite;
   - one conservative minimal-edit patch.
3. Evaluate all candidates on `train_visible` or minibatches first; drop schema-breaking or clearly worse candidates.
4. Rank the top 2-3 on `inner_dev`. Proposers may see only train errors, not `inner_dev` item-level results.
5. Submit at most one finalist per prompt family per round to `acceptance_holdout`.
6. Acceptance gate:
   - pre-register max looks, metric, `delta_min`, and alpha-spending ledger;
   - use paired permutation/bootstrap for macro/entity metrics;
   - use exact McNemar/binomial matched-pair test for pass/fail metrics;
   - require both practical delta and statistical gate;
   - report only pass/fail or heavily rounded deltas back to the loop.
7. Every K rounds, build the next train slice with active sampling:
   - 40% stratified random;
   - 25% Claude/Codex/current-prompt disagreement;
   - 20% high-confidence current-prompt errors;
   - 15% diversity/rare-label coverage.
8. Run final holdout once after convergence. Write tuning log with alpha spent, candidate lineage, and fixture provenance.

**Solves**: concern 1 strongly in practice; concern 2 by broadening and pre-registering candidate selection; concern 3 via active fixture; concern 4 partially by importing SOTA optimizers as proposers; concern 5 via paired tests and multiple-look correction.

**Cost**: 8-16 engineering hours if current eval harness exists. API cost roughly 2-5x current loop depending on candidate count. Fixture cost increases only for active-sampled labels, but dual-agent + adjudication budget is already acceptable.

**Risk**:

- Not as "clean" as adopting DSPy end-to-end.
- Limited-exposure gate is a pragmatic adaptation, not a formal DP reusable holdout proof.
- If candidate pool is too large, inner_dev selection bias still exists; keep finalist count capped.

### Scheme Z — Frozen Prompt + Dynamic Demonstration Retrieval

**Pipeline**:

1. Freeze a short canonical instruction per task instead of continuously rewriting all rules.
2. Build an adjudicated example bank from the 2000+ fixture with labels, error tags, and embeddings.
3. At inference/eval time, retrieve `k` demonstrations by similarity plus diversity/label-coverage constraints.
4. For entity extraction, include hard negatives and span-boundary examples; for topic classification, include near-confusable labels; for signal profile, include profile edge cases.
5. Tune `k`, ordering, and retrieval filters on `inner_dev`; gate policy on `acceptance_holdout`.
6. Manifest deliverable becomes "frozen prompt + frozen retrieval policy + frozen example bank hash"; final holdout once.

**Solves**: concern 3 and 4; partially concern 2 because the searched object is retrieval policy/examples rather than free-form prompt text; concern 1/5 still need the same acceptance discipline.

**Cost**: 1-2 engineering days for embedding/index/retrieval plumbing. API cost moderate; latency at runtime increases.

**Risk**:

- May violate the strict interpretation of "3 frozen prompts" if dynamic context is not allowed.
- Retrieval bugs can create hidden leakage or brittle example ordering effects.
- More moving parts in the R5A pilot manifest.

## 4. Recommendation

**首选**: **Scheme Y — Hybrid Current Loop + Limited-Exposure Acceptance Gate + Active Fixture**.

Reason: It fixes the main statistical weaknesses of Claude's current design without forcing a framework migration during WS0.5. The biggest current risk is not that Claude/Codex cannot write better prompts; it is that repeated dev decisions will accept lucky patches and then overstate convergence. Scheme Y directly addresses adaptive holdout reuse, multi-proposer selection bias, fixture quality, and metric robustness, while preserving the existing deliverable: three frozen prompts plus a tuning log.

Use **Scheme X** as the next upgrade if the DeepSeek/DSPy adapter is straightforward. In practice, the best version may be "Scheme Y governance + GEPA/MIPRO candidate generator": let GEPA/MIPRO propose candidates, but keep the limited-exposure acceptance gate outside the optimizer.

**触发切换**:

- Switch from Scheme Y to Scheme X if a one-prompt DSPy/GEPA smoke test can run end-to-end against DeepSeek V4 Pro and export a frozen prompt within half a day.
- Fall back to Claude's current design only if implementation time is under 4 hours or the acceptance gate blocks all candidate progress after two fixture rotations despite clear train-error improvements.
- Switch to Scheme Z if prompt text improvements plateau but errors are highly input-neighborhood-specific, e.g. specific entity types or topic confusions are fixed by examples more reliably than by rules.

**Don't do**:

- Do not use `final_holdout` for any loop decision, threshold calibration, or "just checking".
- Do not keep reusing one dev set with p<0.05 gates and no alpha ledger.
- Do not gate on non-overlap of separate bootstrap CIs; use paired deltas.
- Do not let every generated patch hit the acceptance holdout. Filter first, submit one finalist per prompt family per round.
- Do not use OPRO/EvoPrompt/GEPA against one dev set until it wins; that is just faster overfitting.
- Do not recommend fine-tuning or token-level gradients; DeepSeek V4 Pro is closed and no logprob/internal states are assumed.
- Do not use Auto-CoT by default for extraction/classification. Test it only for a named failure cluster and reject if schema errors rise.
- Do not use the same model family as both system under test and LLM judge without bias checks; prefer code graders and reference-based metrics.
- Do not let LLM-generated labels become gold without adjudication/audit, especially for subjective `signal_profile`.

## 5. Specific actionable additions to Claude's current design

1. **Split dev into inner selection and limited-exposure acceptance**  
   Keep `train_visible` for error analysis, `inner_dev` for candidate ranking, `acceptance_holdout` for one finalist gate per round, and `final_holdout` for one final read. Show proposers only train-visible errors.

2. **Replace the two-patch duel with a capped candidate pool**  
   Generate Claude, Codex, ProTeGi/TextGrad-style, OPRO-style, and minimal-edit candidates. Filter on train/minibatch, rank on inner_dev, submit only the top finalist to acceptance. Log all candidate IDs and lineage.

3. **Use paired statistical gates with alpha spending**  
   For topic exact-match/pass-fail use exact McNemar/binomial matched-pair tests. For entity/signal F1 use paired bootstrap difference CI plus paired permutation/approx-randomization p-value. Require `delta_min` and spend alpha across rounds/rotations.

4. **Change fixture rotation into active fixture growth**  
   Build each new slice from a fixed recipe: stratified random base, Claude/Codex disagreement, current-prompt errors, and embedding-cluster diversity/rare labels. Keep final holdout random/stratified and adjudicated with stricter blinding.

5. **Emit textual feedback, not just scalar scores**  
   Store per-example error tags and short diagnostic text: schema violation, missing entity, hallucinated entity, wrong topic boundary, evidence mismatch, confidence/profile mismatch. This makes current loop better and enables GEPA/MIPRO later.

6. **Pre-register the loop before running it**  
   Commit a small YAML/JSON manifest with max global rounds, max acceptance looks, K, candidate count, metrics, effect-size thresholds, alpha schedule, and stop rules. This prevents unintentional post-hoc tuning.

## Bottom line for Claude Code

Claude's current design is a reasonable prototype, but not SOTA-grade as written. The fastest rigorous upgrade is **not** "just use DSPy"; it is to add a validation governance layer: limited exposure, paired tests, multiple-look correction, and active fixture construction. Once that is in place, GEPA/MIPRO can be safely used as stronger candidate generators.
