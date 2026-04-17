# Research Roadmap: LLM Leakage in Chinese Financial NLP

> This document defines the decision space for the paper. Each section marks **choice points** where different paths are possible. Codex agents will each traverse this roadmap and produce a concrete research plan.

## 0. Fixed Constraints (Non-Negotiable)

- Primary corpus: 1M+ CLS telegraph entries (2020-01 to 2026-02)
- Models: DeepSeek-chat (API, black-box) + Qwen 2.5 7B (vLLM, white-box)
- Optional: DatedGPT series (1.3B, open-source, annual cutoffs 2013-2024)
- GPU: RTX 4060 Ti local; 4090 rental within budget
- Language: Chinese A-share financial news
- Timeline: 8-12 weeks for experiments
- Existing work: 6 notebooks (84 test cases, PC/CI/IDS metrics, masking + role-play + CoT mitigation, DSPy optimization)
- Origin: derived from Thales quantamental engine (ETF rotation with decomposed LLM signals)

## 1. Paper Positioning — CHOOSE ONE primary framing

### Option 1A: Empirical Study + Benchmark
"First systematic study of LLM leakage in Chinese financial NLP, with cross-method validation"
- Pro: Broadest audience, easiest to scope
- Con: "Another leakage paper" risk; novelty in domain, not method

### Option 1B: Task Design Paper
"Leakage is a function of task design: decomposed text-grounded indicators leak less than direct prediction"
- Pro: Actionable design principle; connects to Thales; strongest novelty
- Con: Needs careful experimental validation; decomposed indicator evaluation is hard (no ground truth)

### Option 1C: Methodological Paper
"Cross-access leakage auditing framework with IRT-based item profiling"
- Pro: Generalizable method; IRT/DIF is genuinely novel in this space
- Con: Needs to demonstrate the method works, not just that it's novel

### Option 1D: Hybrid (recommended by most agents)
Lead with 1B (leakage spectrum), support with 1A (empirical scale) and 1C (IRT rigor)

## 2. Core Research Questions — CHOOSE 2-3

### RQ Pool
- **RQ-spectrum**: Does leakage monotonically decrease from direct prediction → sentiment → decomposed indicators?
- **RQ-cross**: Do white-box (Min-K%) and black-box (counterfactual) methods produce consistent leakage signals?
- **RQ-temporal**: How does leakage decay with news recency, and is there a sharp discontinuity at training cutoffs?
- **RQ-propagation**: Does leaked signal survive ML aggregation (XGBoost) and inflate backtest alpha?
- **RQ-calibration**: Is model confidence (H(X), calibration) systematically distorted by memorization?
- **RQ-mitigation**: Can inference-time interventions reduce decision-critical leakage while preserving accuracy?

## 3. Theoretical Framework — CHOOSE ONE backbone

### Option 3A: Causal DAG (Pearl-style)
Memorization path (M→Y) vs reasoning path (R→Y), task type as moderator. 2×2 factorial (Z×A).
- Formal, publishable in causal ML venues
- Requires explicit identification assumptions

### Option 3B: Econometric (Look-ahead bias)
Regression discontinuity in time, Diebold-Mariano tests, contamination interaction regressions.
- Rigorous, publishable in finance/econometrics venues
- Requires economic outcome data (returns)

### Option 3C: Psychometric (IRT/DIF)
Item-level difficulty and discrimination estimation; DIF across contaminated vs clean conditions.
- Novel crossover; strong statistical foundation
- Less common in NLP, may need more explanation

### Option 3D: Shortcut Learning / IRM
Leakage as shortcut; temporal buckets / prominence tiers as environments; invariant sentiment signal.
- Connects to robust ML community
- More abstract, less finance-specific

### Option 3E: Hybrid
Combine 2-3 frameworks at different levels: causal DAG for conceptual model, IRT for item-level analysis, econometric tests for statistical inference.

## 4. Experimental Design — CHOOSE scope

### 4.1 Test Set Size
- **Small (MVP)**: 500 cases, 3 temporal bins → 8 weeks
- **Medium**: 1000 cases, 6 temporal bins → 10 weeks
- **Large**: 2000 cases (FinLakeBench scale), 6 bins → 12 weeks

### 4.2 Task Types to Compare
- **Minimal**: Direct prediction vs sentiment (2 types)
- **Standard**: Direct prediction vs sentiment vs decomposed (3 types)
- **Full**: Direct vs sentiment vs decomposed (novelty + authority + expectation gap + information content each separately) + sham-decomposition control (6+ types)

### 4.3 Decomposed Indicators — CHOOSE which to include
- **Tier 1 (easiest to validate)**: Authority (metadata ground truth), Novelty (retrieval proxy)
- **Tier 2 (moderate)**: Expectation gap (consensus data needed), Information content (factual density)
- **Tier 3 (hardest)**: Fund impact (Thales slow track), Shock impact (Thales fast track)
- **Sham control**: Random structured output (non-economic multi-part response)

### 4.4 Detection Methods
| Method | Access | Model | Priority |
|--------|--------|-------|----------|
| Min-K% Prob | White-box | Qwen | Must-have |
| Counterfactual PC/CI/IDS | Black-box | Both | Must-have |
| H(X) from 5-bin distribution | Grey-box | Both | Should-have |
| CDD (output distribution peakedness) | Grey-box | DeepSeek beta | Nice-to-have |
| IRT difficulty/discrimination | Statistical | Both | Novel addition |
| DIF across contaminated/clean | Statistical | Both | Novel addition |
| ROME causal probing | White-box (weight editing) | Qwen | Stretch goal |

### 4.5 Counterfactual / Perturbation Families
- **For sentiment/direct**: Reverse outcome, alter numbers (existing)
- **For novelty**: First-time disclosure ↔ routine follow-up
- **For authority**: Source provenance swap (regulator ↔ rumor)
- **For expectation gap**: Above consensus ↔ in-line
- **For information content**: Detailed ↔ vague
- **Neutral paraphrase**: Control for perturbation artifacts
- **Cue masking**: Year + company name removal (existing)

### 4.6 Baselines
- Non-LLM: Dictionary-based Chinese financial sentiment
- LLM without mitigation: DeepSeek/Qwen zero-shot
- Leakage-free reference: DatedGPT (appropriate year) if available
- Sham decomposition: Random structured output fed to XGBoost

### 4.7 Economic Validation (optional but recommended by quant perspective)
- Fetch 1-5 day abnormal returns for test set via AKShare/Tushare
- Compute rank IC, hit rate, Brier score
- Compare pre-cutoff vs post-cutoff economic signal
- Test whether leakage metrics predict where alpha is fake

## 5. Key Experiments — Numbered menu

| # | Experiment | Tests | Priority |
|---|-----------|-------|----------|
| E1 | Temporal leakage decay curve | RQ-temporal | Must-have |
| E2 | White-box / black-box cross-validation | RQ-cross | Must-have |
| E3 | Leakage spectrum (3+ task types) | RQ-spectrum | Must-have (core) |
| E4 | IRT item profiling | RQ-cross, novel | Should-have |
| E5 | DIF across contaminated/clean conditions | RQ-temporal, novel | Should-have |
| E6 | H(X) / calibration analysis | RQ-calibration | Should-have |
| E7 | Mitigation scaling (thales_v1, DSPy) | RQ-mitigation | Should-have |
| E8 | Contamination propagation through XGBoost | RQ-propagation | Nice-to-have |
| E9 | ROME causal probing on Qwen | RQ-spectrum (causal) | Stretch |
| E10 | Economic validity (rank IC, alpha decay) | RQ-propagation | Nice-to-have |
| E11 | Sham-decomposition control | RQ-spectrum | Should-have |
| E12 | DatedGPT as leakage-free baseline | All RQs | Nice-to-have |

## 6. Paper Structure — CHOOSE narrative arc

### Arc A: "Spectrum First"
1→2→3→Setup→E3(spectrum)→E1(temporal)→E2(cross-val)→E8(propagation)→Discussion

### Arc B: "Detection First, Then Design"
1→2→3→Setup→E1(temporal)+E2(cross-val)→E3(spectrum)→E6(calibration)→Discussion

### Arc C: "Benchmark Paper"
1→2→3→Benchmark construction→E1→E2→E3→E4(IRT)→Release CLS-Leak→Discussion

## 7. Artifacts to Release — CHOOSE which

- [ ] CLS-Leak benchmark (curated test set + counterfactual variants + leakage scores)
- [ ] Leakage detection toolkit (Python library wrapping Min-K%, PC/CI/IDS, IRT)
- [ ] Temporal decay dataset (monthly leakage scores for CLS corpus)
- [ ] Prompt templates for decomposed indicator extraction

## 8. Target Venue — Informed by scope

| Scope | Venue | Requirements |
|-------|-------|-------------|
| E1-E3 + 500 cases | FinNLP workshop, AACL | Minimum viable |
| E1-E6 + 1000 cases + benchmark | EMNLP/NAACL Findings | Strong target |
| E1-E8 + 2000 cases + benchmark + toolkit | ACL/EMNLP main | Stretch |
| E1-E3 + E8 + E10 + economic validation | JFDS, Financial Innovation | Finance venue |

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Decomposed indicators show no leakage reduction | Kills spectrum hypothesis | Sham control + IRM analysis; pivot to "leakage is task-invariant" (still publishable) |
| Min-K% doesn't work well on Chinese text | Weakens white-box evidence | Normalize by token count; sweep k%; fall back to black-box only |
| DatedGPT too weak (1.3B) for sentiment | Lose clean baseline | Use temporal split within Qwen/DeepSeek instead |
| 84→2000 scaling reveals inconsistent patterns | Undermines pilot findings | Stratified analysis; report heterogeneity honestly |
| DeepSeek updates model silently | Reproducibility threat | Pin temperature=0, tight execution window, record API version |
