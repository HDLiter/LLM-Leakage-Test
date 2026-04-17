# Round 1 — NLP Agent (NLP/ML Researcher)

**Thread:** 019d65ce-bed8-79c0-be3f-61e0f1609138

## Analysis

### 1. CFLS Construct Validity

The all-negative floor effect is best interpreted as **construct drift**, not "CFLS is mathematically broken." CFLS asks: if I replace the article with a semantically reversed version, will a stored outcome trace still override the new text? That is a different construct from membership inference (Min-K%, Carlini et al.). Semantic reversal may delete exactly the rare spans, lexical idiosyncrasies, or low-probability tokens that MIA methods exploit. So a model can be "member-like" on the original article yet go strongly negative on CFLS. Weak convergent validity with leakage metrics, poor discriminant validity from ordinary prompt-following.

### 2. Bidirectional Generalization Confound

Known issue in NLP — closely related to shortcut learning (Geirhos et al., 2020) and annotation artifacts in NLI (Gururangan et al., 2018). "降准降息" and "上调存款准备金率" are mirror schemas with opposite market priors. Negative CFLS is evidence that the model is highly sensitive to **directional lexical-causal cues**, not evidence against parametric knowledge. CFLS is currently closer to a **counterfactual grounding sensitivity** score than a memorization score.

### 3. False-Outcome CPT as Complementary Signal

The 14–17% flip rate at temperature 0 is not sampling noise; it reflects a stable decision boundary. This suggests a hybrid regime: strong parametric event-to-market schema, but not fully impermeable to local context. The example moving from `up` to `neutral` (not `down`) looks like **knowledge conflict detection with hedging** — fits the knowledge-conflict literature (Xu et al., 2024; Monea et al., 2024; Tighidet et al., 2025 on context-copy suppression).

### 4. Cross-Task Correlation Near Zero

r = 0.10 is a serious convergent-validity warning. `direct_prediction` mostly measures fast schema retrieval / polarity classification, while `decomposed_impact` additionally measures multi-step causal decomposition, uncertainty management, and prompt-specific reasoning style. These tasks instantiate different readout functions over the model's knowledge, not two noisy measures of one construct.

### 5. Evidence Intrusion at 0/36

Do not read much into this. Rule-based heuristic has very low recall for paraphrastic intrusion. Better method: **claim-level source attribution** — decompose rationale into atomic claims, retrieve nearest support from prompt and proxy corpus, use NLI/attribution labeling (KaLMA-style). Add dense retrieval over rare spans, numerics, named entities.

### 6. Stratification Patterns

Patterns are consistent with **template-level representations** rather than article-specific traces. Policy cases at -1.0: highly canonical and antonymically symmetric. Macro at -0.500: triggers more mediated reasoning and uncertainty. "High memorization > medium memorization" CFLS reversal: high-memorization cases are also the most public, repeated, and bidirectionally represented — model learns both directions better.

### 7. Metric Redesign

Split the benchmark into three metric families:
1. **Membership/exposure**: Min-K%++ style detection, matched non-member controls, rare-span extraction probes
2. **Context-conflict sensitivity**: Keep semantic reversal and CPT, rename as grounding/conflict metrics; report replacement conflict, additive conflict, paraphrase stability, confidence shift, abstention/neutralization separately
3. **Source intrusion**: Replace heuristic with claim-level attribution and retrieval-backed support labels

Also: estimate a **generic predictability baseline** and residualize it out; use multiple prompt templates and bootstrap reliability. A metric that floors on 36/36 will not become valid just by scaling to 1000.

### Key References
Carlini et al. (2019, 2021, 2023), Shi et al. (2023), Zhang et al. (2025), Geirhos et al. (2020), Gururangan et al. (2018), Xu et al. (2024), Monea et al. (2024), Tighidet et al. (2025)
