# Research Proposal Brainstorm: Multi-Perspective Synthesis

> Generated 2026-04-04/05 from 6 independent advisor agents. Raw material for 开题报告.

---

## Perspective 1: Quantitative Finance Researcher

### Core Thesis
The real problem is not "data contamination" — it is **alpha inflation from parametric memory**. If an LLM scores historical news well because it already absorbed that news, your research stack overstates signal quality and misallocates capital.

### Proposed Framing
**Title:** False Alpha from Parametric Memory: Detecting and Mitigating Leakage in Chinese Financial News LLMs under Realistic API Constraints

**RQs:**
1. To what extent does parametric memory inflate historical performance on Chinese financial news classification, and how does that inflation vary by recency, event prominence, and news type?
2. Can black-box leakage diagnostics on a proprietary model (DeepSeek) reliably track white-box signals from Qwen on the same corpus?
3. Which inference-time mitigations reduce economically material leakage without degrading genuine out-of-sample signal?

### Key Experimental Requirements
Three evaluation layers:
1. **Event-clean diagnostic set**: Cluster CLS telegraphs into unique events, sample across years/types/prominence, create counterfactuals with human audit
2. **Temporal decay study**: Continuous decay curves, split by prominence — the most valuable deliverable for practitioners
3. **Economic validity test**: Sentiment score → short-horizon abnormal returns (rank IC, hit rate, Brier score). Performance before/after mitigation. Performance on freshest holdout.

### What a Quant Would "Steal"
- Temporal leakage decay curve (immediate use in research review)
- Black-box audit protocol (works without weights/logprobs for vendor models)
- Event-prominence → leakage risk mapping

### Key Quote
> "The crucial result is not 'leakage exists.' The crucial result is 'our leakage metrics predict where historical performance is fake.'"

---

## Perspective 2: AI Safety / Privacy Researcher

### Core Thesis
Financial leakage is a special case of **epistemic misattribution** — the system appears competent, but part of that competence is an artifact of hidden exposure to future information. This is a reliability and governance problem.

### Proposed Framing
**Title:** Auditing Temporal Training-Data Leakage in Financial NLP: A Multi-Access Study of Chinese A-Share News Sentiment

**RQs:**
1. Can white-box, grey-box, and black-box audit methods produce consistent signals of temporal training-data leakage on the same financial news corpus?
2. How does leakage vary as a function of temporal distance, event salience, company prominence, and news propagation frequency?
3. Can mitigation strategies reduce leakage while preserving task utility, calibration, and robustness under counterfactual perturbation?

### Methodological Gaps to Address
- Need formal **threat model**: adversary goal is influence inference (determine whether model "knows too much")
- Need **uncertainty quantification**: bootstrap CIs, effect sizes, clustered resampling
- Need **negative controls**: non-financial news, shuffled labels, semantically irrelevant perturbations
- Need **train/dev/test split for prompts** — DSPy optimization on same benchmark = overfitting risk
- Move from item-level to **claim-level annotation** (decision-critical vs peripheral)

### Regulatory Connections
- EU AI Act: model evaluation and adversarial testing obligations for GPAI providers
- NIST AI RMF / GenAI Profile: measurement, documentation, ongoing risk management
- This paper = concrete domain-specific audit protocol

### Key Quote
> "The deeper issue is epistemic misattribution: we attribute performance to inference, while the model may be relying on memorized facts."

---

## Perspective 3: Econometrician

### Core Thesis
LLM leakage is **look-ahead bias in a new technological wrapper**. Stop selling leakage metrics. Sell out-of-sample econometrics.

### Proposed Framing
**Title:** Forecasting with Contaminated Priors: Training-Data Leakage, Look-Ahead Bias, and Out-of-Sample Evaluation in LLM-Based Financial Sentiment

**RQs:**
1. Does LLM forecast performance exhibit identifiable contamination consistent with look-ahead bias?
2. Do white-box memorization signals and black-box counterfactual sensitivity measure the same latent contamination process?
3. Can mitigation reduce contamination without sacrificing true out-of-sample predictive performance?

### Statistical Testing Framework (replacing ad-hoc PC/CI/IDS)
- **Forecast performance**: Diebold-Mariano or Giacomini-White conditional predictive ability tests; paired permutation tests or McNemar tests for finite samples
- **Counterfactual sensitivity**: Exact permutation test, sign test, or Wilcoxon signed-rank test on signed response at event level; event-cluster bootstrap CIs
- **Memorization proxy validity**: Regress correctness on LAP/Min-K% controlling for date, prominence, length, event type; test H₀: β=0 with permutation inference
- **Multiple comparisons**: White's Reality Check, Hansen's SPA, or Romano-Wolf adjusted p-values

### Design Critique
- 84 cases = 42 events × 2 variants → clustered dependence, not independent
- Benchmark is selected (salient events), not sampled → survivorship bias
- Need large monthly/weekly panel with rolling-origin evaluation
- Prompt optimization split must be temporal, not list-based

### Killer Experiment
**Regression discontinuity in time** around known training cutoff:
- Sample comparable A-share news in narrow window before/after cutoff
- Fix event type, source, horizon, label construction
- Measure forecast loss, counterfactual sensitivity, white-box memorization score
- Sharp discontinuity at cutoff = compelling contamination evidence
- Smooth curve through cutoff after covariate adjustment = contamination story weakened

### Key Quote
> "Stop selling the paper as 'we built leakage metrics.' Sell it as 'we identify and measure look-ahead contamination using the logic of out-of-sample econometrics.'"

---

## Perspective 4: Causal Inference Researcher

### Core Thesis
Formalize "is the model reasoning or recalling?" as a **causal identification problem about path-specific effects under latent mediators**.

### Causal DAG
```
C = (recency, prominence, event type, sector, propagation breadth)
C ---------> K ----------------> M --------\
              ^                 ^           \
              |                 |            \
E ----> F ----/                 |             > Y
 \                              |            /
  \--> X* --------------------> R ---------/
        ^   ^                  ^
        |   |                  |
        A   Z                  S
        |
        Q ---------------> Y

K = training exposure/familiarity
M = memorization activation (latent)
R = text-grounded reasoning (latent)
X* = intervened text (after masking/reversal)
Z = cue visibility intervention
A = semantic intervention
S = prompt strategy
Q = counterfactual quality
Y = model output
```

### Proposed Framing
**Title:** Causal Auditing of Financial LLMs: Identifying Memorization and Reasoning via Counterfactual News Interventions

**RQs:**
1. How much of an LLM's financial prediction is causally attributable to mnemonic cues vs. substantive semantic evidence?
2. Does training-data familiarity predict larger invariance under semantic reversal and larger sensitivity to cue masking?
3. Can prompt-level mitigations reduce the memorization-mediated component while preserving the reasoning-mediated component?

### 2×2 Factorial Intervention Design
- Toggle Z: original cues vs masked cues
- Toggle A: original semantics vs reversed semantics

**Reasoning effect** (under low-memory regime):
DE_R = E[d(Y(0,1), Y(0,0))] — once cues suppressed, does changing evidence change prediction?

**Memorization effect** (holding semantics fixed):
IE_M = E[d(Y(1,1), Y(0,1))] — with same semantics, does exposing cues move prediction?

### Identification Assumptions
1. Consistency/SUTVA: no session memory, cache leakage, or stochastic drift
2. Well-defined interventions: masking and reversal are precise, not bundles of uncontrolled changes
3. Exclusion targeting: cue masking primarily affects memory, not removes evidence
4. No unmeasured mediator-outcome confounding (strong, approximately true)
5. Proxy validity: white-box scores reflect memory activation, not generic fluency
6. Positivity: each article admits interpretable masked and reversed variants

### Key Quote
> "Not 'we perturbed and saw stability,' but 'we identified path-specific effects under explicit assumptions.'"

---

## Perspective 5: Senior PI / Journal Editor

### Core Thesis
The paper's unfair advantage is **cross-method convergence**: white-box and black-box detection on the same corpus. Either they agree (leakage is text-intrinsic) or they disagree (they measure different phenomena). **Both outcomes are publishable.**

### Proposed Framing
**Title:** Two Roads to the Same Leak: Cross-Validating White-Box and Black-Box Memorization Detection in Chinese Financial NLP

**Elevator Pitch:** "White-box memorization signals (Min-K% Prob) and black-box behavioral signals (counterfactual consistency) converge on the same leakage ranking across a 1M-entry Chinese financial news corpus — proving leakage is a stable, measurable property of the text, not an artifact of any single detection method."

### Story Arc
| Section | Content | Narrative Beat |
|---------|---------|---------------|
| 1. Intro | Financial LLMs recall, not reason. Key Q: is measured leakage text-intrinsic or method-artifact? | Set up methodological gap |
| 2. Related Work | Organized by access level. Note: no prior cross-access validation. | Position gap |
| 3. Setup | CLS corpus, test set, two-model design, pipelines | Credibility |
| 4. White-Box | Min-K% on Qwen: by date, prominence, type. Decay curves. | Evidence strand 1 |
| 5. Black-Box | Counterfactual PC/CI on DeepSeek. Mitigation ablation. | Evidence strand 2 |
| 6. Cross-Validation | **AHA MOMENT**: Rank correlation scatter. Agreement analysis. | Paper climax |
| 7. Temporal & Linguistic | Decay curves. Chinese-specific findings. | Unique contribution |
| 8. Discussion | Limitations, future work | Build trust |

### Venue Strategy
| Tier | Venues | Likelihood |
|------|--------|-----------|
| Reach | ACL/EMNLP main | 20-30% (need 3+ models, 500+ cases, released benchmark) |
| Strong target | ACL/EMNLP/NAACL Findings | 50-60% (current trajectory + good cross-validation) |
| Safe | EACL, AACL, FinNLP workshop | 70-80% |
| Alternative | AAAI AI4Finance, JFDS, Financial Innovation | 40-50% |

### Citation Magnet
Release **CLS-Leak**: Chinese financial news memorization benchmark
- 300-500 curated examples with counterfactual variants
- Per-example memorization scores from both methods
- Lightweight Python evaluation library

### Scope Control
**Cut**: DSPy details, output format analysis, detailed mitigation comparison → table/appendix
**Keep**: Cross-validation story, temporal decay, Chinese-specific findings, benchmark artifact

### Key Quote
> "Write one paper with one story — 'white-box and black-box leakage signals converge' — and make everything else serve that story."

---

## Perspective 6: NLP Experimentalist

### Core Thesis
Scale from 84 to **2,000 test cases** via stratified sampling. The full MVP is achievable in **8 weeks** with current resources.

### Data Construction Plan
**Stratification:**
- Temporal: 6 yearly buckets (2020-2025+), dense around 2024 boundary. 200/yr for 2020-2023, 400 for 2024, 400 for 2025+.
- Company prominence: SSE50 / CSI300-minus-SSE50 / small-cap
- Event type: policy, corporate, industry, macro + subcategories

**Counterfactual generation**: 2000 × 2 × 2 passes = 8000 API calls ≈ $2-4, one day.
Quality control: LLM-as-judge + 200-sample human spot-check. Target <10% false-pass rate.

### Experiment Design
| # | Experiment | Method | Metric | Proves |
|---|-----------|--------|--------|--------|
| 1 | Temporal decay curve | DeepSeek CF + Qwen Min-K% by month | PC/CI/IDS/LAP vs time | Leakage is temporal |
| 2 | Cross-method consistency | Rank-correlate WB & BB scores per sample | Spearman ρ | Methods converge (core claim) |
| 3 | Prominence × memorization | Compare leakage across cap tiers | Per-group means, Kruskal-Wallis | Memorization ∝ training frequency |
| 4 | Mitigation scaling | Top 3 strategies on full set | L, accuracy, Pareto frontier | Mitigation generalizes |
| 5 | CDD grey-box (stretch) | Output distribution peakedness on DeepSeek beta | AUC for high/low leakage | Third independent signal |

### Baselines
- Detection: random, surface heuristic (text length/entity count), TF-IDF memorability prior
- Task: dictionary-based sentiment, Qwen zero-shot, DeepSeek on post-cutoff-only data

### Practical Pitfalls & Mitigations
- Chinese tokenization: normalize Min-K% by token count, sweep k from 10-30%
- Counterfactual quality at scale: stratify QC by news category
- DeepSeek model drift: pin temperature=0, record version strings, tight execution window
- Cutoff date unknown: treat as feature — temporal curve empirically reveals effective cutoff

### Compute & Timeline
- Qwen Min-K% on 2000 cases: ~67h on 4060Ti, ~20h on rented 4090
- DeepSeek API: ~18,000 calls ≈ $10-15 total
- **8-week timeline**: W1-2 data → W3-4 Exp 1&3 → W5-6 Exp 2&4 → W7-8 analysis & writing
- **MVP floor**: Exps 1-3, ≥500 cases

---

## Cross-Perspective Synthesis

### Points of Consensus
1. **Cross-validation is the core story** (all 6 agree)
2. **84 cases is insufficient** — minimum 500, target 2000
3. **Temporal decay curves are the most valuable artifact**
4. **Don't lead with "new method"** — lead with empirical study + benchmark
5. **Need formal statistics**, not just descriptive PC/CI/IDS

### Points of Tension
| Issue | Finance view | Safety view | Econometrics view | Causal view |
|-------|-------------|-------------|-------------------|-------------|
| What to optimize | Economic validity (rank IC) | Audit protocol rigor | Statistical inference | Identification |
| Core framing | Alpha inflation | Epistemic misattribution | Look-ahead bias | Path-specific effects |
| Formalism level | Practical | Threat model | Hypothesis testing | SCM/DAG |
| What's novel | Industry-relevant audit | Regulatory connection | Econometric grounding | Causal decomposition |

### Recommended Synthesis (Round 1)
Lead with **empirical study + benchmark** framing. Use econometric language (look-ahead bias, RD-in-time) for rigor. Use causal DAG for the conceptual framework. Deliver the cross-validation story as the methodological contribution. Package as CLS-Leak benchmark for citations. Connect to audit/governance in discussion section.

---

# Round 2: The Leakage Spectrum Hypothesis

> After discovering the Thales connection (Section 1.1 of LANDSCAPE.md), all 4 agents were re-queried about the **task decomposition** insight: leakage may vary with how you use the LLM (direct prediction → sentiment → decomposed text-grounded indicators).

## R2-Quant: "Leakage Spectrum is Stronger Than Cross-Validation"

**Key judgment:** Yes, the spectrum hypothesis is a stronger contribution than cross-method validation. Cross-validation is credibility scaffolding; the spectrum is a **substantive, actionable design rule**.

**Revised framing:** Keep "alpha inflation from parametric memory" as umbrella, but reframe from audit study to **task-design paper**: leakage is endogenous to how close the LLM task is to the target variable.

**New core claim:** "Outcome-proximal LLM uses generate false alpha; decomposed text-grounded factor extraction attenuates that channel enough to make LLMs usable inside a real quant pipeline."

**Fund vs Shock insight:** Shock (fast sentiment impulse) is likely more leakage-sensitive than Fund (slow fundamental). They sit at different points on the spectrum within decomposed indicators.

**Decisive test:** End-to-end pipeline comparison (raw LLM prediction vs. sentiment vs. decomposed→XGBoost) on rolling-origin evaluation. If decomposition truly reduces leakage, it should show less performance discontinuity at cutoff and less dependence on familiarity proxies (prominence, Min-K%).

**Sham-decomposition control:** Ask for arbitrary multi-part structured outputs that sound decomposed but are not economically grounded. If sham performs similarly, "decomposition benefit" is just regularization theater.

**H(X) as leakage signal:** Weak standalone detector, but powerful in conjunction. The interesting test: does the coupling between Min-K% and low H(X) weaken as you move from direct prediction to decomposed indicators?

**Key quote:** "The sharper contribution is that leakage is task-dependent, and decomposed factor extraction may be the only defensible way to use LLMs in a serious quant stack."

## R2-Causal: "Moderated Causal Mediation"

**Key formalization:** Task type T moderates both mediator prevalence and potency:
```
P(M=1 | K,X,T=decomposed) < P(M=1 | K,X,T=sentiment) < P(M=1 | K,X,T=direct)
|∂Y/∂M|_decomposed < |∂Y/∂M|_direct
|∂Y/∂R|_decomposed ≥ |∂Y/∂R|_sentiment
```

**Interventional path effects by task type:**
- ψ_M(t) = E[Y(t,Z=1,A=a) - Y(t,Z=0,A=a)] — memory-sensitive effect
- ψ_R(t) = E[Y(t,Z=z,A=1) - Y(t,Z=z,A=0)] — reasoning-sensitive effect
- Hypothesis: ψ_M(decomposed) < ψ_M(sentiment) < ψ_M(direct), while ψ_R(decomposed) ≥ ψ_R(sentiment)

**H(X) formalization via latent mixture:**
```
p(b|x,t) = π_M(x,t)·p_M(b|x,t) + (1-π_M(x,t))·p_R(b|x,t)
```
H informative about π_M only if memorization produces systematically sharper distributions than reasoning.

**Leakage redistribution risk:** If decomposition just spreads leakage across sub-indicators:
- L_joint = E[g(S(Z=1)) - g(S(Z=0))]
- Compare L_joint to sum of marginal effects
- If marginals are small but L_joint is large → leakage redistributed, not reduced
- Decisive falsification: if decomposed indicators each look clean but aggregated predictor still collapses on post-cutoff holdout

**Ideal experiment:** 3×2×2 factorial (T × Z × A) within event, all conditions per article, pre-registered aggregation rule g(S).

## R2-Econometrics: "Contamination Propagation Through XGBoost"

**Key insight:** Decomposition is not an IV approach — it's a proxy-measurement story. Sub-indicators load less on contamination than direct sentiment (smaller Π vs ρ in measurement equation).

**Testing decomposed vs direct look-ahead bias:**
```
Y_{i,h} = α + β_m·S_{im} + δ·C_i + θ_m·(S_{im} × C_i) + X'γ + τ_t + η_g + ε_i
```
Key coefficient: θ_m (interaction of signal × contamination proxy). Hypothesis: θ_direct > θ_decomposed.

**Calibration contamination test (5-bin):**
```
1{B_i ≤ k} = a_k + b_k·P_i(B≤k) + c_k·C_i + d_k·(P_i(B≤k) × C_i) + X'γ + u_ik
```
If d_k ≠ 0, calibration is contaminated. Joint Wald test across bins.

**Contamination propagation test through XGBoost:**
1. Estimate C_i from white-box/black-box diagnostics (never using returns)
2. Residualize each LLM feature: Z_ij = α_j + φ_j·C_i + X'ψ_j + r_ij
3. Train three XGBoost models: full features Z, residualized r, leak-only Ẑ^L
4. Evaluate all three on contaminated historical folds AND clean holdout
5. Propagated alpha: Δ^prop = (α^hist_full - α^hist_resid) - (α^clean_full - α^clean_resid)
6. Large positive Δ^prop = extra historical alpha is from contamination channel

**Key quote:** "Decomposition should not be sold as exogeneity. It should be sold as a design that reduces the loading of latent contamination on predictors."

## R2-NLP Experimentalist: "Revised Timeline and MVP"

**Experiment matrix:** 3 task types × 2 models × 6 time bins = 36 cells. ~12,000 original runs (joint decomposed prompt) + interventions → ~36k-48k total runs. Still feasible.

**Revised timeline:**
- **8 weeks MVP**: 500-800 cases, 3 coarse time bins, joint decomposed prompt
- **10-12 weeks full**: 2,000 cases, 6 bins, full indicator set
- W1: prompt schemas and rubrics
- W2: pilot 50-100 items + counterfactual QC rubric
- W3-4: stratified sampling + original model runs
- W5-6: counterfactual generation, reruns, human spot-checks
- W7: Qwen Min-K% + normalization
- W8: core statistics and figures
- W9-10: scale-up to 2,000 + full indicators
- W11-12: robustness checks + paper tables

**Evaluating decomposed indicators (no ground truth):**
- Authority: quasi-ground-truth from metadata (regulator filing vs rumor), weighted kappa
- Novelty: 200-300 human anchor set + retrieval-based proxy (max similarity to prior 30/90-day same-entity news)
- Expectation gap: directional accuracy on subset with consensus data
- Information content: atomic factual density (numbers, entities, dates, causal claims)

**Counterfactual perturbation families for decomposed tasks:**
- Novelty: first-time disclosure ↔ routine follow-up
- Authority: regulator notice ↔ unattributed rumor (provenance swap)
- Expectation gap: above consensus ↔ in-line with guidance
- Information content: detailed numerical ↔ vague summary

**Distribution comparison:** Use 1-Wasserstein (earth mover's distance), NOT KL divergence. Bins are ordered and asymmetric. Store Δμ, W1, ΔH per example.

**Cheapest credible spectrum test (MVP):**
- 500 articles, 3 temporal bins, 2 models, 3 task prompts
- Decomposed: only novelty + authority (easiest to validate)
- Per article: original + neutral paraphrase + one targeted factor edit
- 200-item human anchor set
- Three hypothesis tests: (1) leakage orders direct > sentiment > decomposed, (2) black-box ranking correlates with Min-K%, (3) ordering strongest in old time bins

---

## Round 2 Cross-Perspective Synthesis

### Upgraded Core Thesis
The leakage spectrum hypothesis elevates the paper from "detection study" to **"design principle for trustworthy LLM-based quantitative systems."** The cross-validation story becomes supporting evidence, not the headline.

### Revised Paper Structure (incorporating both rounds)
| Section | Content |
|---------|---------|
| 1. Intro | LLMs in finance: profit mirage + alpha inflation. BUT: leakage is not binary — it depends on task design. |
| 2. Related Work | Organized by: (a) financial leakage, (b) detection methods, (c) task decomposition in quant |
| 3. Framework | Causal DAG with task type as moderator. Leakage spectrum formalization. |
| 4. Experimental Setup | CLS corpus, 3 task types, 2 models, temporal stratification, counterfactual families |
| 5. Does Leakage Exist? | White-box (Min-K%) + black-box (counterfactual) on sentiment task. Temporal decay. Cross-validation. |
| 6. The Leakage Spectrum | Same corpus, 3 task types. ψ_M and ψ_R by task. H(X) analysis. Sham-decomposition control. |
| 7. Contamination Propagation | Does leaked signal survive XGBoost aggregation? Residualization test. Fresh holdout. |
| 8. Discussion | Design principles for trustworthy financial LLM pipelines. Limitations. Regulatory connections. |

### Key Risks Identified in Round 2
1. **Leakage redistribution**: Decomposition may hide leakage across sub-indicators rather than reduce it → need joint vs marginal leakage test
2. **Sham decomposition**: Structured output may look clean simply because it's harder to detect → need sham control
3. **Evaluation of decomposed indicators**: No ground truth for novelty/expectation gap → need anchor sets + retrieval proxies
4. **Scope creep**: 3 task types × interventions × models × temporal bins is a LOT → strict MVP scoping essential
