# Task Design Gates Look-Ahead Memory: Revised Research Proposal for Leakage Detection in Chinese Financial News LLMs

## 1. Abstract
Large language models are now used to turn financial news into predictive signals, but historical evaluation is vulnerable to look-ahead leakage: a model can answer from parametric memory of later outcomes rather than from the article it is shown. This proposal reframes the project from a metric-comparison paper into a mechanism paper. The central claim is that task design gates which memory pathway reaches the answer. We distinguish **Type A memory**: useful background knowledge and domain priors, from **Type B memory**: temporally illicit event-outcome memory that contaminates evaluation. Outcome-proximal tasks such as direct return prediction invite Type B memory to answer directly; evidence-grounded tasks such as authority extraction reduce that pathway by making provenance, attribution, and quoted evidence decision-relevant instead.

The study will build **CLS-Leak-1000**, a clustered benchmark of Chinese A-share CLS telegraph news with fixed targets, targeted counterfactual rewrites, neutral paraphrases, and sham controls. The primary behavioral comparison is the same `(article, target)` evaluated under an outcome-proximal prompt and an evidence-grounded prompt. The core metric is **counterfactual label sensitivity**, not the deprecated `cf_invariance - para_invariance` formula. Evidence intrusion is treated as supplementary direct evidence of memory spillover. Identification combines a causal anchor and descriptive triangulation: low-dose continued pretraining on Qwen 2.5 7B with real or false outcomes, plus article-familiarity priors from Min-K% and descriptive temporal-boundary analyses. A compact three-arm priming test and a downstream out-of-sample decay analysis remain supplementary.

The expected contribution is a bounded but important result: look-ahead leakage is not only a property of a model or dataset, but of the task pathway used to query the model. In Chinese financial news, task formulations that ask directly for latent future outcomes should be more vulnerable to Type B contamination than formulations that force the model to stay closer to visible evidence.

## 2. Introduction
Large language models are increasingly embedded in financial NLP pipelines for signal extraction, ranking, and forecasting. In that setting, evaluation on historical news is unusually fragile. A model may have seen the article itself, paraphrases of the article, later commentary about the event, or explicit summaries of the realized market reaction during pretraining. A high historical score can therefore reflect contaminated memory rather than genuine article-grounded inference. In finance, the consequence is not only inflated benchmark performance; it is the appearance of false alpha.

This problem is now visible in the literature on contamination, memorization, and finance-specific look-ahead bias, but three gaps remain. First, most evidence comes from English or U.S.-market settings rather than Chinese A-share news. Second, most studies treat leakage as a property of a model or dataset, not as something that depends on the task asked of the model on fixed inputs. Third, many detection designs remain correlational. They can show suspicious behavior, but not whether a task actually opens or closes access to stored outcome traces.

This revised proposal centers a different question: **which task designs let Type B look-ahead memory answer, and which task designs keep the model closer to Type A background knowledge and visible article evidence?** The mechanism claim is deliberately modest. The project does not claim to separate Type A and Type B perfectly in deployed black-box systems. It claims that task formulation changes the probability that Type B reaches the answer.

The proposal therefore uses a light but explicit taxonomy.

- **Type A memory** is legitimate background competence. It includes structural priors such as “official notices are generally more reliable than rumor,” broader finance/world knowledge, and entity- or regime-level familiarity that does not directly encode the later realized outcome of the focal event.
- **Type B memory** is evaluation-invalidating look-ahead memory. It includes event-outcome memory for the focal item or event cluster, and task-template memory when a prompt scaffold cues stored answer patterns tied to historical outcomes.

This distinction matters for methodology. If all memory were treated as equally bad, then any familiar model behavior would look like contamination. That is not defensible. The real problem is whether a model can answer a historical task using information that was unavailable at the article’s publication time but available during training. Under this framing, a direct prediction prompt and an authority prompt are not merely different labels on the same task. They create different routes from memory to answer.

The proposal also changes the metric philosophy. In v1, excess invariance relative to neutral paraphrases was the primary object. After six rounds of debate, that is no longer tenable as the core metric because local counterfactual edits and broader paraphrases are not naturally matched in edit magnitude. In v2, **counterfactual label sensitivity** becomes the primary behavioral measure. Neutral paraphrases remain important, but as a robustness and prompt-fragility control rather than as the subtraction term in the headline metric. Evidence intrusion becomes the cleaner direct memory-spillover measure.

The project’s main empirical thesis is therefore:

**On the same Chinese financial news articles, outcome-proximal prompts should expose more Type B memory than evidence-grounded prompts, because task design gates the path from parametric memory to the answer.**

The paper’s claims are intentionally bounded. It is not a formal regression-discontinuity paper. It is not a proof that all decomposition is safe. It is not a full production trading paper. It is a mechanism-focused evaluation study with one benchmark artifact, one same-article task comparison, one causal anchor on an open model, and two compact supplementary extensions.

## 3. Literature Review

### 3.1 Memorization, Contamination, and Temporal Evaluation
Direct memorization and contamination are now well established. Carlini et al. (2020) and Nasr et al. (2023) show that training data can be extracted from language models, including production systems. Zhang et al. (2021) provide the most useful conceptual lens here by defining **counterfactual memorization**: model behavior changes because a particular training document was included. Shi et al. (2023) introduce Min-K% probability as a practical article-familiarity detector, while Oren et al. (2024), Deng et al. (2024), and Golchin and Surdeanu (2024) show that black-box perturbation and reconstruction tests can expose contamination even without training-data access.

Task formulation also matters. Li and Flanigan (2024) show that benchmark age and task setup affect apparent few-shot ability, implying that contamination is partly a task-design problem rather than only a corpus-overlap problem. Wu et al. (2023) show that counterfactual task reformulations can separate genuine reasoning from recitation of default conventions. Yang et al. (2023), Zhu et al. (2024), and Fang et al. (2025) further show that paraphrases and local rewrites are powerful tools for revealing hidden contamination and building cleaner evaluations.

Temporal methods add another layer. Cheng et al. (2024) use dated data to trace knowledge cutoffs. White et al. (2024) and Wu et al. (2024) attempt to limit contamination through fresh benchmark construction. Yan et al. (2026) propose time-aware pretraining. These papers motivate descriptive boundary checks, but they do not justify calling public release dates clean training cutoffs in proprietary systems. That distinction is crucial for this proposal.

### 3.2 Context-Faithfulness, Evidence Intrusion, and Parametric Memory Spillover
The closest intellectual neighbor to this project is the context-faithfulness literature. Zhou et al. (2023) show that prompting can materially change whether models follow supplied context or background memory. Li et al. (2024) further show that the interaction between memory strength and evidence style governs whether context or memory dominates. Lee et al. (2024) formalize grounding as both using the provided context and staying within its bounds. Tao et al. (2024) show that even when context is sufficient, parametric memory continues to influence outputs.

This literature matters because **evidence intrusion** in the present project is not a generic hallucination notion. It is a narrower event-time violation: the model imports post-publication outcome information, later facts, or unsupported realized reactions into an answer that is supposed to be article-grounded. MiniCheck (Tang, Laban, and Durrett, 2024) and ReEval (Yu et al., 2023) provide useful evaluation ideas for scoring unsupported claims, although neither is designed specifically for look-ahead contamination in finance.

The main gap is that these papers study retrieval or context conflict, not historical market-news evaluation. Our project transfers their logic into a dated financial setting where the conflict is not between retrieved passages and parametric memory in general, but between a historical article and later market reality that should be hidden at evaluation time.

### 3.3 Financial Text, Decomposed Representations, and the Chinese Gap
Finance gives the problem special force because contaminated signals can look like profitable predictors. Lopez-Lira and Tang (2024) show that LLM-generated headline sentiment can predict stock returns, but Glasserman and Lin (2024) show that a meaningful share of that apparent signal may be look-ahead bias. He et al. (2025) make the strongest recent case for leakage-aware finance NLP by showing that chronologically consistent LLMs can remain competitive despite stricter temporal discipline.

At the representation level, the literature has already moved beyond flat sentiment. Heston and Sinha (2016) and Ke, Kelly, and Xiu (2019) show that richer text factors can outperform simple tone. Wang, Cohen, and Ma (2024) show that interactions among news items matter. Tetlock (2011) gives the classical economic rationale for freshness and stale-news distinctions.

In LLM-era finance, Guo and Hauptmann (2024), Wang, Izumi, and Sakaji (2024), Cao et al. (2024), Bastianello, Decaire, and Guenzel (2024), and Li, Qiao, and Zheng (2025) all support the idea that intermediate text factors can be extracted before downstream prediction. However, these papers do not test whether decomposition reduces leakage. They motivate the representation side of this project, not its contamination claim.

Chinese financial NLP remains underdeveloped on this specific question. Domain benchmarks such as FinEval (Guo et al., 2023), BBT-Fin (Lu et al., 2023), CFBenchmark (Lei et al., 2023), and CFinBench (Nie et al., 2024) show growing interest in Chinese finance LLM evaluation, but none is designed as a same-article leakage benchmark for A-share news. The literature search found no strong English-indexed cluster centered on CLS, Eastmoney, or Sina Finance contamination audits. That gap is real and valuable.

### 3.4 What This Proposal Adds
Relative to the existing literature, this project adds four things.

- A **same-article, different-task** design on Chinese financial news, which isolates task pathway effects more cleanly than cross-dataset or cross-benchmark comparisons.
- An explicit **Type A / Type B memory** framing that clarifies why not all memory is harmful and why outcome-proximal tasks are the main contamination risk.
- A **causal anchor** through low-dose continued pretraining on an open model, including false-outcome injection as an optional stronger identifier.
- A finance-relevant but bounded downstream claim: contaminated features are unreliable because their apparent strength should decay out of sample when memorized historical outcomes stop helping.

## 4. Research Questions
The revised proposal asks four linked research questions.

**RQ1. On fixed `(article, target)` inputs, do outcome-proximal tasks show lower counterfactual label sensitivity than evidence-grounded tasks?**  
Primary estimand:  
`Delta_CFLS = E[CFLS_ground] - E[CFLS_prox]`  
where `CFLS` is task-specific counterfactual label sensitivity. Positive `Delta_CFLS` means the evidence-grounded task follows edited article semantics more reliably than the outcome-proximal task.  
Primary success criterion: the confidence interval for `Delta_CFLS` excludes zero in the expected direction on the pre-registered primary contrast.

**RQ2. Does randomized continued pretraining on real or false outcomes shift outcome-proximal behavior more than evidence-grounded behavior?**  
Primary causal object: task-gated exposure response under controlled outcome injection on Qwen 2.5 7B.  
Success criterion: direct prediction follows injected outcome memory materially more than authority extraction, especially in the false-outcome arm if that arm is run.

**RQ3. Do evidence intrusion, article familiarity, and publication time move in the same direction as the behavioral leakage signal?**  
Primary descriptive objects: outcome-intrusion rates by task, Min-K% article familiarity priors, and local training-access premium estimates around documented open-model boundaries.  
Success criterion: older and more familiar items should look more contamination-prone on average, and evidence intrusion should concentrate in the outcome-proximal task.

**RQ4. Are apparently predictive but higher-leakage features less reliable out of sample than lower-leakage features?**  
Primary supplementary object: difference in in-sample versus freshest-holdout performance decay across direct-prediction features, low-leakage factors, sham controls, and mixed models.  
Success criterion: higher-leakage signals show larger out-of-sample decay; lower-leakage factors or mixed models show smaller decay, even if they do not dominate in-sample.

## 5. Theoretical Framework

### 5.1 Type A and Type B Memory Pathways
The conceptual framework distinguishes two memory families and one task gate.

- **Type A1: structural priors.** Generic relations such as policy easing usually helping cyclicals, or official notices being more credible than rumor.
- **Type A2: entity or regime familiarity.** Knowledge of firms, regulators, sectors, and disclosure conventions that does not by itself reveal the realized outcome of the focal event.
- **Type B1: event-outcome memory.** Memory of what happened after the focal article or event cluster.
- **Type B2: task-template memory.** Stored answer patterns cued by outcome-proximal prompt scaffolds.

Type A is often desirable. It is part of genuine model capability. Type B is the contamination channel because it allows a historical evaluation item to be answered using later knowledge.

### 5.2 Revised DAG
The proposal’s core mechanism can be represented as:

```text
Article text X ----------------------> G (text-grounded inference) ----------\
                                                                              \
Generic pretraining P --------------> A (Type A memory) ----------------------> Y
                                                                                ^
Article/event exposure K ------------> B (Type B memory) ----------------------/
                                                                                ^
Task design T ---------------- gates usefulness of G, A, and B ----------------/

Counterfactual article edit C_X ----> changes X and G, not the stored B trace
Outcome CPT edit C_B ---------------> changes B, not the visible article text
Evidence requirements E ------------> raise the cost of unsupported B retrieval
```

The key claim is not that evidence-grounded tasks eliminate Type B. It is that they make Type B less decision-relevant and easier to detect when it intrudes. Outcome-proximal tasks such as direct direction prediction ask for an output that can be answered almost directly from stored later outcomes. Authority extraction asks instead about provenance, attribution, and quoted support. The same stored outcome trace is therefore much less useful, and if it appears anyway it often reveals itself as unsupported evidence intrusion.

### 5.3 Why Outcome-Proximal Tasks Open the Type B Channel
Outcome-proximal tasks and evidence-grounded tasks differ in answer geometry.

- In a direct prediction task, the model can map an event cue to a remembered later sign or market reaction with little need to inspect the local article carefully.
- In an authority task, later price movement is not the asked-for variable. The model must judge source type, attribution, or officialness from visible text. Type B memory is therefore misaligned with the output space.
- In a decomposition-first setup, the model can still cheat, but it must either ignore the visible article or inject unsupported post-publication material into the evidence field. That makes the failure mode easier to observe.

This theoretical framework implies different experimental interventions target different nodes. Counterfactual article edits test whether the model follows visible semantics. False-outcome continued pretraining tests whether injected parametric memory can causally steer outputs. Temporal and Min-K% analyses are triangulation tools, not direct identification by themselves.

## 6. Methodology

### 6.1 Data and Benchmark: CLS-Leak-1000
The raw corpus is the CLS telegraph archive from **January 1, 2020** to **February 23, 2026**, containing more than 1.16 million articles. The benchmark unit is not the raw article but the **event cluster**: one representative article per target-day cluster after collapsing propagated rewrites. All tables will report both nominal article counts and effective cluster counts.

`CLS-Leak-1000` keeps the existing two-tier structure.

- **Tier 1 anchor:** 300 clusters, fully human-audited on originals and edited fields.
- **Tier 2 core:** 700 clusters, random spot-check plus all QC-flagged cases.

The sampling frame retains the original `6 x 3 x 4` structure: six temporal bins (`2020`, `2021`, `2022`, `2023`, `2024`, `2025+`), three prominence tiers (`SSE50`, `CSI300 ex-SSE50`, `small_cap`), and four event types (`policy`, `corporate`, `industry`, `macro`). The v1 requirement of exact 72-cell fills is relaxed. In v2, benchmark construction will target broad balance ex ante and use **post-stratification weights** ex post rather than forcing exact fills that can bias curation toward easy cases.

Each benchmark row contains one target and one target type (`company`, `sector`, or `index`). Target linking follows the existing hierarchy and ambiguous cases are escalated to Tier 1 arbitration. Cases that cannot be resolved to a single target quickly are excluded rather than forced.

Each sampled cluster includes:

- the original article;
- a neutral paraphrase control;
- one task-targeted counterfactual rewrite;
- one sham rewrite when the sham-control experiment is run.

The prompt infrastructure already exists in frozen form. `config/prompts/task_prompts.yaml` contains base, matched-format, and sham prompts, and `config/prompts/counterfactual_templates.yaml` contains `semantic_reversal`, `provenance_swap`, `novelty_toggle`, `neutral_paraphrase`, and `sham_edits`. The v2 proposal uses these assets but changes how the outputs are scored.

Quality control remains the existing four-stage pipeline.

- **Stage 1:** dual-model plausibility judging on target preservation, coherence, financial plausibility, intended edit realization, and no new economically material facts.
- **Stage 2:** style and edit-distance filters to keep rewrites locally plausible.
- **Stage 3:** retrieval-based nonexistence checks against the full CLS corpus.
- **Stage 4:** Tier 1 full human review and Tier 2 partial human review with escalation.

The benchmark freeze will report template-specific pass rates, weighted kappa, human override rates, style-distance distributions, and cluster-collision diagnostics.

[OPTION A: Inferability Control]
Add a 5-point human inferability rating to the full Tier 1 anchor only, then use it as a calibration covariate and propagate a model-based proxy to Tier 2.

[OPTION B: Full Inferability Annotation]
Add the same inferability rating to all 1,000 cases through dual human annotation. This strengthens the task-difficulty control but materially increases annotation burden.

[OPTION C: Proxy-Only Control]
Do not add a new inferability label. Rely on observable proxies such as article length, numeric density, entity count, prominence, and event type. This is cheapest but weakest against the “task difficulty, not leakage” objection.

### 6.2 Models
The project uses two complementary model regimes.

- **DeepSeek black-box model:** deployment-relevant behavioral test bed for same-article task comparisons, evidence intrusion, matched-format controls, sham controls, and the supplementary priming study. The exact model string and API date will be frozen at run time. As of **April 5, 2026**, the internal plan records `deepseek-chat` as corresponding to `DeepSeek-V3.2`, upgraded on **December 1, 2025**. Any `2026-01-01` onward slice is therefore treated only as a false-positive stress window, not as a clean training cutoff.
- **Qwen 2.5 7B:** open-model white-box system for Min-K% article-familiarity scoring and the continued-pretraining causal experiment. The descriptive open-model boundary is tied to the documented Qwen 2.5 7B release date of **September 19, 2024**.

All prompts are frozen before the main run. Temperature is set to `0` whenever supported. For Qwen, vLLM-based logprob extraction is used for article scoring. For CPT variants, all runs start from the same base checkpoint and use the same clean dated filler corpus outside the experimental injections.

### 6.3 Detection Methods

#### 6.3.1 Counterfactual Label Sensitivity
The primary behavioral metric is **counterfactual label sensitivity** (`CFLS`).

For each task family, a targeted rewrite is constructed to change one primary field while preserving the target and the rest of the event as much as possible. Let `f*` be the primary field expected to change and `L_cf` the validated label after the rewrite. Then:

`CFLS_i,t = 1` if the model’s response on item `i` under task `t` moves to `L_cf` on `f*` and all designated protected fields remain consistent with the rewrite protocol; otherwise `CFLS_i,t = 0`.

Examples:

- For direct prediction, `f* = direction`.
- For sentiment, `f* = sentiment`.
- For authority, `f*` is the authority field targeted by `provenance_swap`, with other authority fields treated as protected checks.
- For novelty, `f*` is the disclosure-framing field targeted by `novelty_toggle`, with freshness-related protected checks.

Higher `CFLS` means more visible-text responsiveness and therefore less evidence of Type B dominance. For intuition, the paper may also display `1 - CFLS` as a non-responsiveness rate, but the inferential target remains `CFLS`.

This scoring change is deliberate. The legacy `EI = cf_invariance - para_invariance` formulation implemented in `src/metrics.py` is deprecated for v2 because it subtracts mismatched perturbation families. The revised implementation should therefore add task-family-specific label extractors, field-level changed/unchanged scoring, and cluster-level aggregation.

Neutral paraphrases remain in the design, but only as a **robustness control**. They answer two questions: whether the prompt is brittle to benign rewrites, and whether the benchmark’s task labels remain stable under non-semantic variation. They are no longer the subtraction term in the headline metric.

[OPTION A: Strict Primary-Field Scoring]
Score only the field explicitly targeted by the rewrite. This maximizes comparability and keeps the primary metric simple.

[OPTION B: Primary Field Plus Protected Fields]
Require the targeted field to change as intended and pre-specified protected fields to remain stable. This is stricter and better aligned with the multi-slot prompt design.

[OPTION C: Dual Reporting]
Use [OPTION B] for the main table and report [OPTION A] as a sensitivity analysis. This is the most transparent if implementation time allows.

#### 6.3.2 Evidence Intrusion
Evidence intrusion is the supplementary direct indicator of Type B memory spillover. It is especially important for evidence-grounded tasks, because a grounded task can still fail by importing unsupported later facts into its evidence or explanation.

The proposed scoring taxonomy is:

- `unsupported_quote`
- `unsupported_article_internal_claim`
- `unsupported_post_publication_claim`
- `explicit_realized_outcome_claim`

For the main paper, the most diagnostic categories are the last two. An authority answer that cites or alludes to later price action, later follow-up events, or realized outcomes absent from the visible article is close to direct evidence of Type B intrusion.

[OPTION A: Narrow Outcome-Intrusion Rate]
Use only `unsupported_post_publication_claim` and `explicit_realized_outcome_claim` in the main paper. This is precision-first and best aligned with the mechanism claim.

[OPTION B: Full Four-Bucket Audit]
Score all four buckets in the main paper. This is richer, but also increases annotation and adjudication complexity.

[OPTION C: Narrow Main Metric, Full Appendix]
Use [OPTION A] in the main paper and publish the full four-bucket taxonomy in the appendix or artifact package.

#### 6.3.3 Article Familiarity and Temporal Analysis
Qwen supplies a white-box **article-familiarity prior** through Min-K% scoring on the original article text. Scores will be calibrated through a `k` sweep, digit/entity masking, and length-bin normalization. The proposal does not treat Min-K% as a task-conditioned leakage measure. It is article-level triangulation.

Temporal analysis is descriptive. For Qwen, the project will estimate a local training-access premium around **September 19, 2024**:

`lambda_t(c) = lim_{d -> c-} E[L_i,t | d] - lim_{d -> c+} E[L_i,t | d]`

where `L_i,t` is a leakage proxy such as low `CFLS`, high evidence intrusion, or high article familiarity. This is presented as a descriptive boundary check, not as a formal regression discontinuity.

For DeepSeek, the freshest available slice after **January 1, 2026** is treated as a **false-positive stress test** rather than a bona fide frontier.

[OPTION A: Qwen Boundary Plus DeepSeek Fresh-Slice Stress Test]
Use the Qwen release boundary for descriptive local-window analysis and the DeepSeek freshest slice only as a falsification check.

[OPTION B: Continuous Age Curves Only]
Avoid boundary language almost entirely and emphasize smooth publication-age patterns. This is safest if reviewers are expected to challenge frontier interpretation.

[OPTION C: Qwen Boundary Only]
Run the local-window design only on Qwen and report DeepSeek temporal patterns descriptively without a stress-window equivalence test.

### 6.4 Experimental Design

#### 6.4.1 Core Experiments (Must Run)
The main story is a same-article comparison on DeepSeek. Every core experiment is run regardless of whether early estimates look promising; no robustness block is conditionally skipped.

**Core Experiment 1: Primary same-article task comparison.**  
Each benchmark item is evaluated under one outcome-proximal task and one evidence-grounded task. The primary contrast is the gap in `CFLS` between the two. The unit of inference is the event cluster. The main success criterion is a positive and statistically bounded `Delta_CFLS`.

**Core Experiment 2: Matched-format control.**  
The same comparison is repeated using the matched prompt schema already defined in the prompt library so that slot count, evidence burden, and approximate output length are held constant. If the task gap survives this ablation, it is more consistent with pathway gating than with output-format mechanics.

**Core Experiment 3: Sham decomposition falsification.**  
The sham prompt asks for text-grounded but economically irrelevant surface features. If sham performs like authority, the central interpretation weakens to “structured extraction changes behavior.” If authority remains cleaner than sham, the claim that economically meaningful decomposition matters becomes more credible.

**Core Experiment 4: Triangulation.**  
Evidence intrusion, Min-K% familiarity, and temporal analyses are used to test whether the behavioral pattern moves with independent contamination indicators.

[OPTION A: Binary Main Paper]
Main-text comparison is `direct_prediction` versus `decomposed_authority` only. `sentiment` and `novelty` are reported in appendix tables or as exploratory robustness. This is the cleanest alignment with the new binary-contrast framing.

[OPTION B: Binary Primary, Ternary Narrative]
Pre-register `direct_prediction` versus `decomposed_authority` as the sole primary contrast, but keep `sentiment` in the main paper as an intermediate bridge task. This preserves continuity with v1 while keeping the causal story focused.

[OPTION C: Full Four-Family Main Story]
Keep `direct_prediction`, `sentiment`, `authority`, and `novelty` all in the main paper, but interpret only the direct-versus-authority gap as primary. This is richest empirically but also the most vulnerable to cross-family comparability objections.

#### 6.4.2 Causal Experiments: Continued Pretraining on Qwen 2.5 7B
The causal experiment injects controlled event bundles during low-dose continued pretraining. Each bundle contains the article and, depending on the arm, none, the real post-event outcome, or a plausible false post-event outcome. The same base checkpoint, same dated filler corpus, and same training schedule are used across runs. Exposure is balanced across event type, prominence, and date.

Evaluation uses the same benchmark evaluation slice and the same task families as the behavioral study. The paper-level causal claim is asymmetric by design:

- direct prediction should be pulled toward the injected outcome if Type B memory is active;
- authority extraction should remain close to the visible article, with near-zero false-outcome intrusion and minimal authority-label displacement.

The strongest direct success pattern is therefore: **large direct-task false-outcome following plus near-zero authority-task movement**.

[OPTION A: 2 x 2 Design]
Factors: article exposure `0/1` and outcome exposure `none/real`.  
Interpretation: identifies a task-gated exposure effect, but still mixes article familiarity and true outcome memory because the injected outcome is aligned with reality.

[OPTION B: 2 x 3 Design]
Factors: article exposure `0/1` and outcome state `none/real/false`.  
Interpretation: the preferred design if compute allows. The false-outcome arm creates a sign-flip contrast that more cleanly identifies Type B outcome memory rather than generic Type A cueing.

[OPTION C: Reduced Four-Run Compromise]
Run only `(0, none)`, `(1, none)`, `(1, real)`, and `(1, false)`.  
Interpretation: retains the most valuable contrasts for Type A versus Type B while cutting two lower-value cells.

[OPTION A: Outcome Block Format]
Inject a minimal structured outcome block with signed `T+1` direction only. This minimizes distribution shift but gives a weaker memory trace.

[OPTION B: Richer Outcome Block Format]
Inject `T+1` and `T+5` signed buckets plus one short rationale sentence. This is closer to realistic web exposure and should create a stronger trace.

[OPTION C: Intermediate Outcome Block Format]
Inject signed direction plus a magnitude bucket, but no rationale sentence. This trades realism against control.

#### 6.4.3 Supplementary Experiments
Two supplementary experiments remain in scope, but neither should determine paper acceptability.

**Supplementary Experiment 1: Three-arm priming test.**  
This is an inference-time mechanism probe, not a separate paper. A direct-prediction prompt is run under three conditions:

- no decomposition prefix;
- real decomposition prefix generated from article-grounded slots;
- sham decomposition prefix matched in format and length.

The main outcomes are `CFLS`, evidence intrusion, and neutrality rates. The expected pattern is that real decomposition improves visible-text responsiveness more than sham, without overclaiming that the model’s visible reasoning is itself faithful.

**Supplementary Experiment 2: Downstream utility and unreliability test.**  
This analysis uses a strict rolling-origin design and a freshest holdout. The comparison class is not “direct prediction versus nothing,” but:

- high-leakage direct prediction;
- low-leakage factors such as authority and novelty;
- sham controls;
- mixed models combining high- and low-leakage features.

The key diagnostic is **out-of-sample decay**, not in-sample alpha. The strongest positive result would be that contaminated features look good historically but decay sharply, while lower-leakage factors or mixed models are more stable.

[OPTION A: Representation-Utility Only]
Report intrinsic utility only: human agreement, complementarity to sentiment, and stability under shift. This is safest for an NLP-first paper.

[OPTION B: Light Financial Diagnostic]
Add rank IC, ICIR, and a simple long-short spread on the pre-registered 3-day horizon. This is the current preferred supplementary design.

[OPTION C: Appendix-Only Utility]
Run the utility analysis only if the core causal and behavioral results finish early. This is the safest schedule decision if time binds.

### 6.5 Statistical Protocol
All inference is cluster-aware. The bootstrap, permutation tests, and mixed models operate at the event-cluster level rather than the raw-article level. Every table will report both article counts and cluster counts.

The primary behavioral analysis uses paired cluster comparisons and generalized mixed models of the form:

`g(E[Y_i,t]) = alpha_i + beta_1 Prox_t + beta_2 Matched_t + beta_3 Sham_t + beta_4 Controls_i + epsilon_i`

where `Y_i,t` is either `CFLS` or an evidence-intrusion indicator, `alpha_i` is an item-specific effect where appropriate, and controls include publication date, prominence, event type, propagation size, and any inferability control selected in Section 6.1.

The primary inferential family is:

1. the direct-versus-authority `CFLS` contrast on base prompts;
2. the same contrast on matched prompts;
3. the sham-versus-meaningful decomposition gap;
4. the primary CPT contrast if the causal experiment is completed before manuscript freeze.

Multiplicity will be handled with stepdown Romano-Wolf. Secondary and exploratory families use false-discovery-rate control. Temporal smoothers are descriptive unless attached to a pre-registered local-window comparison. Concordance analyses report partial Spearman and Kendall `tau_b` sensitivity checks because ties are plausible.

If the CPT experiment uses a false-outcome arm, the preferred causal summary is the difference in false-outcome following between tasks. If only real outcomes are injected, the causal language will stay weaker and speak only of task-gated exposure effects.

For the downstream utility study, all nuisance steps are time-ordered and cross-fitted. Generated-regressor uncertainty is propagated through a full-pipeline bootstrap. The pre-registered financial horizon is `3` trading days. Additional horizons are exploratory only.

Success will be judged primarily by effect sizes and uncertainty intervals, not by isolated p-values.

## 7. Expected Contributions
This project is expected to make four contributions.

- It provides a **mechanism claim** for leakage-aware evaluation: task design gates the path from parametric memory to answer.
- It delivers **CLS-Leak-1000**, a clustered Chinese A-share benchmark with counterfactual rewrites, evidence-aware prompts, and documented QC.
- It introduces a cleaner metric hierarchy in this setting: **counterfactual label sensitivity** as the core behavioral measure, **evidence intrusion** as direct supplementary evidence, and **Min-K% plus temporal analysis** as triangulation.
- It reframes the finance takeaway from “clean features must be strongly predictive” to the easier and more defensible claim that **contaminated features are unreliable**, especially when evaluated out of sample.

[OPTION A: Venue Baseline]
Target **Findings of EMNLP** if the paper delivers the behavioral same-article result plus either the CPT pilot or strong triangulation.

[OPTION B: Venue Stretch]
Target **main EMNLP** only if the binary contrast is clean under matched and sham controls and the CPT evidence is unusually crisp, especially with a false-outcome arm.

## 8. Timeline
The project remains scoped to ten weeks.

**Weeks 1-2:** freeze the benchmark slice, finish clustering and target linking, generate rewrites, and complete Tier 1 review plus QC reporting.  
**Weeks 3-4:** run DeepSeek base prompts, matched prompts, sham controls, and neutral-paraphrase diagnostics on the frozen benchmark.  
**Weeks 5-6:** compute Qwen Min-K% familiarity priors, k-sweep tables, and temporal descriptive analyses.  
**Weeks 7-8:** run the continued-pretraining causal experiment on Qwen and evaluate exposed versus unexposed conditions.  
**Week 9:** run the compact three-arm priming study and, if time permits, the downstream out-of-sample decay analysis.  
**Week 10:** finalize figures, robustness tables, artifact packaging, and submission materials.

The minimum viable paper is the benchmark, the same-article behavioral comparison, matched and sham controls, and at least one triangulation layer. The CPT experiment materially strengthens the paper but should not be allowed to destroy the schedule if engineering issues arise.

## 9. Risks and Contingencies
The revised design is cleaner than v1, but it creates new execution risks.

**Risk 1: The task gap collapses under matched-format control.**  
If the direct-versus-authority gap disappears once output structure is matched, the mechanism claim weakens substantially. The contingency is to report a null-result paper about structure-sensitive contamination measurement rather than overstate task semantics.

**Risk 2: False-outcome continued pretraining causes capability drift or shortcut learning.**  
Low-dose CPT can still change calibration, instruction following, or article-faithfulness globally. The mitigation is to keep exposure small, use identical formatting across arms, mix with a large clean dated corpus, and run held-out sanity checks on general financial instruction following.

**Risk 3: The false-outcome arm is too expensive.**  
The `2 x 3` design is the strongest identifier, but also the heaviest. The contingency is to fall back to the reduced four-run design rather than cancel causal evidence entirely.

**Risk 4: Evidence intrusion scoring is noisy.**  
Unsupported post-publication claims can be subtle, especially in Chinese financial shorthand. The mitigation is to keep the main evidence-intrusion metric narrow and human-audit ambiguous cases.

**Risk 5: Temporal boundary claims are over-read.**  
Public release dates are not the same as training cutoffs. The mitigation is doctrinal: keep Qwen local-window results descriptive and treat DeepSeek only as a false-positive stress test.

**Risk 6: Secondary tasks add burden without helping the claim.**  
Sentiment and novelty are useful only if they sharpen the mechanism story. If they create ambiguity, the contingency is to demote them to appendix while preserving the benchmark labels for future work.

**Risk 7: The benchmark is too proprietary to matter.**  
If full CLS text cannot be released, the artifact should still release hashes, metadata, prompts, rewrite instructions, labels, and reproducibility scripts. That limits the benchmark contribution but does not erase it.

## 10. References
Selected references cited in this proposal:

- Arjovsky, Bottou, Gulrajani, and Lopez-Paz (2019). *Invariant Risk Minimization*.
- Bastianello, Decaire, and Guenzel (2024). *Mental Models and Financial Forecasts*.
- Cao, Chen, Pei, Lee, and Subbalakshmi (2024). *ECC Analyzer: Extracting Trading Signal from Earnings Conference Calls using Large Language Model for Stock Volatility Prediction*.
- Carlini, Liu, Erlingsson, Kos, and Song (2019). *The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks*.
- Carlini et al. (2020). *Extracting Training Data from Large Language Models*.
- Carlini et al. (2022). *Quantifying Memorization Across Neural Language Models*.
- Cheng et al. (2024). *Dated Data: Tracing Knowledge Cutoffs in Large Language Models*.
- Deng et al. (2024). *Investigating Data Contamination in Modern Benchmarks for Large Language Models*.
- Fang et al. (2025). *LastingBench: Defend Benchmarks Against Knowledge Leakage*.
- Glasserman and Lin (2024). *Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis*.
- Glasserman, Li, and Mamaysky (2025). *Time Variation in the News-Returns Relationship*.
- Golchin and Surdeanu (2024). *Time Travel in LLMs: Tracing Data Contamination in Large Language Models*.
- Guo and Hauptmann (2024). *Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow*.
- Guo et al. (2023). *FinEval: A Chinese Financial Domain Knowledge Evaluation Benchmark for Large Language Models*.
- He, Yang, Chinco, and Halac (2025). *Chronologically Consistent Large Language Models*.
- Heston and Sinha (2016). *News versus Sentiment: Predicting Stock Returns from News Stories*.
- Jain, Wiegreffe, Pinter, and Wallace (2020). *Learning to Faithfully Rationalize by Construction*.
- Ke, Kelly, and Xiu (2019). *Predicting Returns with Text Data*.
- Lee et al. (2024). *How Well Do Large Language Models Truly Ground?*.
- Lei et al. (2016). *Rationalizing Neural Predictions*.
- Lei et al. (2023). *CFBenchmark: Chinese Financial Assistant Benchmark for Large Language Model*.
- Li and Flanigan (2024). *Task Contamination: Language Models May Not Be Few-Shot Anymore*.
- Li, Qiao, and Zheng (2025). *Structured Event Representation and Stock Return Predictability*.
- Li et al. (2024). *Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style*.
- Lopez-Lira and Tang (2024). *Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models*.
- Lopez-Lira, Tang, and Zhu (2025). *The Memorization Problem: Can We Trust LLMs' Economic Forecasts?*.
- Lu et al. (2023). *BBT-Fin: Comprehensive Construction of Chinese Financial Domain Pre-trained Language Model, Corpus and Benchmark*.
- Mamede et al. (2010). *Effect of Availability Bias and Reflective Reasoning on Diagnostic Accuracy Among Internal Medicine Residents*.
- Mehrbakhsh et al. (2024). *Confounders in Instance Variation for the Analysis of Data Contamination*.
- Nasr et al. (2023). *Scalable Extraction of Training Data from (Production) Language Models*.
- Nie et al. (2024). *CFinBench: A Comprehensive Chinese Financial Benchmark for Large Language Models*.
- Oren et al. (2024). *Proving Test Set Contamination in Black-Box Language Models*.
- Shi et al. (2023). *Detecting Pretraining Data from Large Language Models*.
- Tang, Laban, and Durrett (2024). *MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents*.
- Tao et al. (2024). *When Context Leads but Parametric Memory Follows in Large Language Models*.
- Tetlock (2011). *All the News That's Fit to Reprint: Do Investors React to Stale Information?*.
- Wang, Izumi, and Sakaji (2024). *LLMFactor: Extracting Profitable Factors through Prompts for Explainable Stock Movement Prediction*.
- Wang, Cohen, and Ma (2024). *Modeling News Interactions and Influence for Financial Market Prediction*.
- White et al. (2024). *LiveBench: A Challenging, Contamination-Limited LLM Benchmark*.
- Wu et al. (2023). *Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks*.
- Wu et al. (2024). *AntiLeakBench: Preventing Data Contamination by Automatically Constructing Benchmarks with Updated Real-World Knowledge*.
- Yang et al. (2023). *Rethinking Benchmark and Contamination for Language Models with Rephrased Samples*.
- Yan et al. (2026). *DatedGPT: Preventing Lookahead Bias in Large Language Models with Time-Aware Pretraining*.
- Yu et al. (2023). *ReEval: Automatic Hallucination Evaluation for Retrieval-Augmented Large Language Models via Transferable Adversarial Attacks*.
- Zhang, Ippolito, Lee, Jagielski, Tramèr, and Carlini (2021). *Counterfactual Memorization in Neural Language Models*.
- Zhou et al. (2023). *Context-faithful Prompting for Large Language Models*.
- Zhou et al. (2023). *Quantifying and Analyzing Entity-level Memorization in Large Language Models*.
- Zhu et al. (2024). *CLEAN-EVAL: Clean Evaluation on Contaminated Large Language Models*.
