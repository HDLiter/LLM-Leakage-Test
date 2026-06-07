# Fleet Selection in LLM Memorization / Contamination / Leakage Benchmarks: A Literature Review

**Date:** 2026-04-15
**Purpose:** Inform model fleet composition for an EMNLP-targeted memorization detection benchmark on Chinese financial news.
**Scope:** 25+ papers from 2021-2026 covering MIA, extractable memorization, data contamination detection, and financial NLP leakage studies.

---

## 1. Executive Summary

This review surveys how recent academic papers (2021-2026) select their model fleets when building LLM memorization detection benchmarks, data contamination benchmarks, or training data leakage studies. The key findings are:

1. **Fleet sizes vary enormously** (1 to 50+ models), but memorization-focused papers that use white-box logprob methods typically use 5-13 models. Contamination benchmarks that focus on behavioral evaluation use 10-40+ models.

2. **Same-architecture scaling ladders** are the single most common fleet design principle -- present in the majority of white-box memorization papers. However, **same-cutoff different-architecture falsification pairs** are essentially absent from the literature, representing a genuine gap that our project can fill.

3. **No paper uses a 9-model fleet with the specific design principles we propose** (temporal pairs, falsification pairs, size matching, multi-tier). Our fleet design is more principled than anything in the literature, which is a strength for EMNLP positioning.

4. **Checkpoint pinning is poorly practiced** across the field, with a documented reproducibility crisis (32% of papers have reproducibility issues, rising to 40%+ in 2024-2025).

5. **Thinking/reasoning mode handling** is essentially unaddressed in the memorization literature -- no paper we found systematically controls for it.

---

## 2. Paper-by-Paper Fleet Analysis

### 2.1 Memorization Detection & MIA Papers

#### MemGuard-Alpha (Roy & Roy, 2026)
- **Fleet size:** 7 models
- **Fleet composition:**
  - GPT-2 124M, GPT-2 Medium 355M, GPT-2 Large 774M (same family, 3 sizes)
  - TinyLlama 1.1B Chat (LLaMA family)
  - Phi-2 2.7B (Phi family)
  - Qwen2.5-3B-Instruct, Qwen2.5-7B-Instruct (Qwen family, 2 sizes)
- **Cutoff dates:** Oct 2019, Sep-Oct 2023, Mar 2024 (3 temporal tiers)
- **Architecture families:** 4 (GPT-2, LLaMA, Phi, Qwen)
- **Access:** All white-box (logprob-based MIA requires token-level probabilities)
- **Size range:** 124M-7B
- **Design principles explicitly stated:**
  1. Architectural diversity (4 families)
  2. Temporal diversity (3 cutoff tiers for CMMD)
  3. Practical accessibility (all open-weight for MIA score computation)
- **Same-architecture scaling pairs:** Yes -- GPT-2 (124M/355M/774M), Qwen2.5 (3B/7B)
- **Same-cutoff falsification pairs:** Not explicitly designed
- **Size matching:** Not explicitly matched
- **Thinking mode:** Not discussed
- **Checkpoint pinning:** Weights & Biases logging with per-model checkpointing
- **Quantization:** 7B Qwen quantized to 4-bit; validated Pearson r=0.997 between quantized and full-precision MIA scores

**Key insight:** MemGuard-Alpha is the closest direct comparator to our project. Their 7-model fleet uses architectural and temporal diversity but does NOT include falsification pairs, size-matched controls, or black-box models. Our 9-model design extends their approach significantly.

---

#### Carlini et al. (2023) -- "Quantifying Memorization Across Neural Language Models" (ICLR 2023)
- **Fleet size:** ~6 models
- **Fleet composition:**
  - GPT-Neo 125M, 1.3B, 2.7B (same family, 3 sizes)
  - GPT-J 6B (same architecture family as GPT-Neo)
- **Access:** All white-box
- **Design principle:** Pure scaling analysis within a single architecture family. The entire fleet serves one purpose: measuring how memorization scales with model capacity.
- **Same-architecture scaling pairs:** Yes -- this IS the design. The paper's core result is the log-linear relationship between model size and memorization.
- **Same-cutoff falsification:** Not applicable (single family, same training data)
- **Checkpoint pinning:** Fixed checkpoints (models trained on The Pile)

**Key insight:** The canonical memorization scaling paper uses a same-family scaling ladder as its primary design. This validates our Qwen2.5-7B / Qwen2.5-14B size falsification pair.

---

#### Nasr et al. (2023) -- "Scalable Extraction of Training Data from (Production) Language Models"
- **Fleet size:** ~22 models across 3 access tiers
- **Fleet composition:**
  - Open-source (9): GPT-Neo (1.3B, 2.7B, 6B), Pythia (1.4B, 1.4B-dedup, 6.9B, 6.9B-dedup), RedPajama-INCITE (3B, 7B)
  - Semi-closed (9): LLaMA (7B, 65B), Falcon (7B, 40B), Mistral 7B, OPT (1.3B, 6.7B), GPT-2 1.5B, gpt-3.5-turbo-instruct
  - Closed (1): gpt-3.5-turbo (ChatGPT)
- **Access:** Explicit white-box / semi-closed / black-box tiering
- **Design principles:**
  1. White-box vs black-box access is a primary design axis
  2. Same-family scaling pairs used extensively (LLaMA 7B/65B, Falcon 7B/40B, GPT-Neo family)
  3. Deduplication controls (Pythia vs Pythia-dedup)
- **Key innovation:** Different extraction methods for different access tiers. White-box uses training data matching; black-box uses a novel "divergence attack" + 9TB auxiliary dataset.

**Key insight:** This paper establishes the principle that **white-box and black-box models require different methodologies** -- exactly the split our project implements (logprob detectors on white-box only; behavioral detectors on full fleet).

---

#### Duan et al. (2024) -- "Do Membership Inference Attacks Work on Large Language Models?" (COLM 2024)
- **Fleet size:** ~16+ models
- **Fleet composition:**
  - Pythia (5 sizes: 160M, 1.4B, 2.8B, 6.9B, 12B) + Pythia-dedup (5 sizes)
  - GPT-Neo (3 sizes: 125M, 1.3B, 2.7B)
  - OLMo (2 sizes: 1B, 7B)
  - SILO 1.3B
  - Datablations 2.8B (multiple checkpoints at different training stages)
- **Design principle:** Same-architecture scaling ladders are the primary fleet structure. The Pythia suite's 160M-to-12B range is used to study how MIA performance scales with model size.
- **Key finding:** "MIA performance tends to increase with target model size" but "remains near-random (AUC < 0.6) across most domains."
- **Checkpoint pinning:** Uses intermediate training checkpoints (Datablations) to study the effect of training duration on memorization.

**Key insight:** The most rigorous MIA evaluation paper uses a same-family scaling ladder (Pythia 5 sizes) as the primary design axis. No cross-family falsification pairs are used.

---

#### Meeus et al. (2024) -- "SoK: Membership Inference Attacks on LLMs are Rushing Nowhere" (SaTML 2025)
- **Fleet size:** 2 primary + references to others
- **Fleet composition:**
  - OpenLLaMA (3 sizes: 3B, 7B, 13B) for randomized-split experiments
  - CroissantLLM (canary-based evaluation)
- **Design principle:** Fleet selection driven by **data availability** -- models were chosen because their full training datasets are known, enabling proper randomized member/non-member splits.
- **Critical finding:** Most MIA papers use post-hoc temporal splits that introduce distribution shift, making results unreliable. True membership evaluation requires known training data.
- **Same-architecture scaling:** Yes (OpenLLaMA 3 sizes)

**Key insight:** Meeus et al. demonstrate that **fleet selection is secondary to experimental design** -- even a 2-model study can produce strong conclusions if the member/non-member split is done correctly. This supports our temporal-cutoff-based design where each model has a known cutoff date.

---

#### Shi et al. (2024) -- "Detecting Pretraining Data from Large Language Models" (ICLR 2024, Min-K% Prob)
- **Fleet size:** ~13 model checkpoints
- **Fleet composition:**
  - LLaMA (4 sizes: 7B, 13B, 30B, 65B)
  - GPT-NeoX-20B
  - OPT (2 sizes: 350M reference, 66B target)
  - Pythia (2 sizes: 70M reference, 2.8B target)
  - GPT-3 (text-davinci-003) for book detection case study
- **Design principle:**
  1. Reference model pairing: smaller model of same family as reference for each target (LLaMA-7B as reference for LLaMA-65B, OPT-350M for OPT-66B, etc.)
  2. WikiMIA temporal design: members = Wikipedia articles before 2017; non-members = events after Jan 1, 2023
- **Same-architecture scaling:** Yes (LLaMA 4 sizes is the primary analysis axis)
- **Cutoff-based design:** WikiMIA benchmark explicitly uses temporal boundaries for ground truth

**Key insight:** Min-K% Prob's WikiMIA benchmark uses **temporal boundaries for ground truth membership**, directly analogous to our cutoff-based design. Their reference model pairing (small reference for each target) is worth noting as a precedent for our PCSG paired-cutoff design.

---

#### Zhang et al. (2024) -- Min-K%++ (ICLR 2025)
- **Fleet size:** Similar to Shi et al., extends to additional models
- **Design principle:** Per-token calibration extends Min-K% to work more robustly across models of different vocabularies and sizes. The paper implicitly acknowledges that **cross-model comparison requires careful calibration** when models differ in architecture.

---

#### Cross-Model Memorization Study (2026) -- "A Comparative Analysis of LLM Memorization at Statistical and Internal Levels"
- **Fleet size:** 20 models across 6 families
- **Fleet composition:**
  - Pythia (6 sizes: 160M-12B)
  - OLMo1 (2 sizes: 1B, 7B), OLMo2 (4 sizes: 1B-32B), OLMo3 (2 sizes: 7B, 32B)
  - OpenLLaMA (3 sizes: 3B, 7B, 13B)
  - StarCoder (3 sizes: 1B, 3B, 7B)
- **Access:** White-box only (requires training data access for verification)
- **Design principle:** Models selected based on (1) publicly available pre-training data, (2) clear training corpus documentation, (3) downloadable datasets. The authors explicitly note: "most famous open models (Qwen, Deepseek, Llama, etc.) do not release their pre-training data."
- **Same-architecture scaling:** Yes, the primary design axis (multiple sizes within each family)
- **Chinese models:** None (English-only)
- **Falsification controls:** Not used

**Key insight:** The largest cross-model memorization study (20 models) still uses **only white-box models with known training data**. No black-box models. This represents the tradeoff: white-box purity vs fleet diversity.

---

### 2.2 Data Contamination Detection Papers

#### MMLU-CF (Microsoft, ACL 2025)
- **Fleet size:** 40+ models
- **Fleet composition:**
  - 5 API/proprietary: GPT-4o, GPT-4-Turbo, GPT-4o-mini, GPT-3.5-Turbo, Gemini-1.5-Flash
  - 35+ open-source: Qwen series (9 models), Llama series (7), Phi series (4), Gemma (3), Mixtral (2), Baichuan (2), InternLM (2), Yi (2), Deepseek (1), GLM (1)
  - Size range: 0.5B to 72B
- **Chinese models:** 17 Chinese-origin models (Qwen, Baichuan, InternLM, GLM, Yi, Deepseek)
- **Design principle:** Comprehensive coverage across sizes, architectures, and origins. Selection prioritized "architectural diversity, size representation, and inclusion of both leading closed-source and emerging open-source systems."
- **Same-architecture scaling:** Extensive within Qwen (0.5B-72B), Llama (7B-70B), Phi (mini to MoE)

**Key insight:** The largest contamination benchmark (40+ models) demonstrates that behavioral evaluations (no logprobs needed) can scale to very large fleets. This is a different regime from our logprob-heavy design. Our 9-model fleet is parsimonious by comparison, but much more principled in its pairings.

---

#### AntiLeakBench (ACL 2025)
- **Fleet size:** 12 models
- **Fleet composition:**
  - 10 open-source: Llama-2 (7B, 13B), Mistral-7B, Vicuna-v1.5-7B, LongChat-v1.5-7B, Llama-3.1-8B, Phi-3.5-mini, Qwen-2-7B, Mistral-Nemo-12B, Gemma-2-9B
  - 2 proprietary: GPT-4o-mini, GPT-4o
- **Chinese models:** 1 (Qwen-2-7B)
- **Cutoff design:** Two temporal datasets -- one for ~Sep 2022 cutoffs, one for ~late 2023 cutoffs -- enabling pre/post-cutoff performance comparison
- **Design principle:** "Performance commonly drops after the cutoff time" -- temporal boundary used as natural experiment

**Key insight:** AntiLeakBench demonstrates the temporal-cutoff-as-natural-experiment approach with 12 models. Their two-era temporal design is a simpler version of our multi-cutoff fleet.

---

#### LiveBench (ICLR 2025 Spotlight)
- **Fleet size:** 40+ models
- **Fleet composition:** Many closed-source + dozens of open-source (0.5B to 405B)
- **Design principle:** Monthly question updates eliminate contamination by construction. Fleet selection is about coverage, not experimental control.
- **Key insight:** Dynamic contamination-resistant benchmarks use large, broad fleets because they are measuring capability, not diagnosing memorization per model. Our project's targeted fleet design serves a different purpose.

---

#### LLMSanitize (Ravaut et al., 2024)
- **Fleet size:** 5 models
- **Fleet composition:**
  - Llama-2-7B, Qwen-1.5-7B, Mistral-7B, Gemma-7B (all 7B, all open-source)
  - GPT-3.5-turbo (proprietary)
- **Design principle:** **Size-matched cross-architecture comparison** -- all open-source models are 7B to enable fair comparison of contamination detection across architectures at a fixed scale.
- **Chinese models:** 1 (Qwen-1.5-7B)

**Key insight:** LLMSanitize is the clearest precedent for **size-matched cross-architecture pairs**. Their 4x7B design isolates architecture differences from size effects. This validates our Qwen2.5-7B / GLM-4-9B / Qwen3-8B small-tier design.

---

#### CFinBench (NAACL 2024)
- **Fleet size:** 50 models
- **Fleet composition:**
  - 46 open-source + 2 API (ChatGPT, GPT4) + 1 proprietary (YunShan)
  - 17+ Chinese-first models: Qwen series (multiple), ChatGLM series, Baichuan series, InternLM series, Yi series, XuanYuan series
  - Size range: 0.5B to 72B
- **Design principle:** Comprehensive coverage of Chinese financial LLMs specifically. "Evaluate a wide spectrum" across "various families" for Chinese financial context.

**Key insight:** The largest Chinese financial LLM benchmark uses 50 models but does NOT study memorization -- it measures capability. Our project bridges this gap: applying memorization detection methodology to Chinese financial NLP.

---

#### Time Travel in LLMs (Golchin & Surdeanu, ICLR 2024)
- **Fleet size:** 2 models
- **Fleet composition:** GPT-3.5-turbo-0613, GPT-4-0613 (both pinned snapshots)
- **Access:** Black-box only (detection method designed for closed models)
- **Checkpoint pinning:** Yes -- both models use June 13, 2023 API snapshots
- **Design principle:** Minimalist fleet focused on method validation, not fleet diversity

**Key insight:** Even top-venue contamination papers can succeed with just 2 models if the method is novel enough. Fleet size is not a gate for publication quality.

---

#### Proving Test Set Contamination (Oren et al., ICLR 2024)
- **Fleet size:** ~2-3 models
- **Fleet composition:** Pythia variants + LLaMA-2
- **Key finding:** Method "sensitive enough to reliably detect contamination in models as small as 1.4B parameters, on small test sets of only 1000 examples"
- **Checkpoint pinning:** Uses specific model versions

---

#### PaCoST (EMNLP 2024 Findings)
- **Fleet size:** Multiple popular open-source models (exact count varies)
- **Design principle:** Paired confidence testing requires comparing model confidence on original vs constructed counterparts
- **Key finding:** "Almost all models and benchmarks tested are suspected contaminated"

---

### 2.3 Financial NLP Leakage Papers

#### Profit Mirage (2025)
- **Fleet size:** ~17 systems (including agents)
- **Fleet composition for memorization audit:**
  - 3 leading proprietary: GPT-4o, Claude-Sonnet-3.5, Grok-3
  - 6 foundation models: Qwen2.5-72B-Instruct, LLaMA-3.1-405B, DeepSeek-V3 (open-source) + GPT-4o, Claude, Grok (closed)
  - 2 fine-tuning baselines: Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct
- **Key findings:** GPT-4o and peers answer historical financial QA correctly >85% of the time. FinLake-Bench constructs 2,000 QA pairs for memorization audits.
- **Chinese models:** Yes (Qwen, DeepSeek)
- **Design principle:** Mix of agent systems and foundation models; fleet size driven by coverage of SOTA rather than controlled comparison

**Key insight:** Profit Mirage tests 6 foundation models for memorization but uses no controlled pairings. Their counterfactual evaluation (Prediction Consistency, Confidence Invariance, Input Dependency Score) is methodologically relevant to our detector design.

---

#### Lopez-Lira et al. (2025) -- "The Memorization Problem: Can We Trust LLMs' Economic Forecasts?"
- **Fleet size:** 1 model
- **Fleet composition:** GPT-4o (gpt-4o-2024-08-06) only
- **Access:** Black-box only
- **Design principle:** Single-model deep dive. "Given its wide usage in research, we run our analysis using ChatGPT 4o."
- **Cutoff handling:** Tests whether model respects artificial cutoff dates through varied prompting conditions
- **Key finding:** "Instructions to respect historical boundaries fail to prevent recall-level accuracy, and masking fails as LLMs reconstruct entities and dates from minimal context."

**Key insight:** A high-impact economics paper used just 1 model. However, this was published in an economics journal, not NLP -- EMNLP reviewers would likely require multi-model validation.

---

#### Didisheim, Fraschini & Somoza (2025) -- "AI's Predictable Memory in Financial Analysis" (Economics Letters)
- **Fleet size:** 3 models
- **Fleet composition:** GPT-4.1, GPT-4.1-mini, GPT-4.1-nano (same family, 3 sizes)
- **Design principle:** Pure **same-family size scaling** to study how memorization varies with model capacity
- **Key findings:**
  - Bias varies predictably with data frequency, model size, and aggregation level
  - GPT-4.1-nano shows negligible bias; GPT-4.1 shows near-100% correlation for monthly S&P 500 returns
  - "Smaller models and finer data granularity exhibit negligible bias"
- **Cutoff handling:** All queries within training period (2018-2023); no post-cutoff testing

**Key insight:** This paper demonstrates the value of **same-family size scaling** for isolating memorization from capability. Our Qwen2.5-7B vs Qwen2.5-14B size falsification pair serves the same analytical purpose.

---

#### LiveTradeBench (2025)
- **Fleet size:** 21 models
- **Fleet composition:**
  - OpenAI (4): GPT-5, GPT-4.1, GPT-4o, GPT-o3
  - Anthropic (4): Claude-Opus-4.1, Claude-Opus-4, Claude-Sonnet-4, Claude-Sonnet-3.7
  - Google (2): Gemini-2.5-Pro, Gemini-2.5-Flash
  - xAI (2): Grok-4, Grok-3
  - Meta/Llama (3): Llama4-Maverick, Llama4-Scout, Llama3.3-70B-Instruct-Turbo
  - Qwen (3): Qwen3-235B-A22B-Instruct, Qwen3-235B-A22B-Thinking, Qwen2.5-72B-Instruct
  - DeepSeek (2): DeepSeek-R1, DeepSeek-V3.1
  - Moonshot/Kimi (1): Kimi-K2-Instruct
- **Selection rationale:** "(1) state-of-the-art performance on general-purpose reasoning, (2) diversity in model size, architecture, and performance levels"
- **Thinking mode handling:** Qwen3-235B tested in both Instruct and Thinking variants
- **Chinese models:** Yes (Qwen, DeepSeek, Kimi)

**Key insight:** LiveTradeBench explicitly includes a **thinking vs non-thinking pair** (Qwen3-235B-A22B-Instruct vs Qwen3-235B-A22B-Thinking). This is the closest precedent to our proposed thinking mode crossover analysis.

---

#### Look-Ahead-Bench (2026)
- **Fleet size:** 6 models
- **Fleet composition:**
  - Standard LLMs: Llama 3.1-8B, Llama 3.1-70B, DeepSeek 3.2
  - Point-in-Time LLMs: Pitinf-Small, Pitinf-Medium, Pitinf-Large
- **Design principle:** Contrast between standard (potentially contaminated) and temporally-controlled models
- **Key finding:** "Significant lookahead bias in standard LLMs, as measured with alpha decay"

**Key insight:** Look-Ahead-Bench uses a **treatment vs control** fleet design: standard models (with temporal bias) vs PiT models (without). This is structurally analogous to our CMMD design where different-cutoff models serve as mutual controls.

---

#### Wongchamcharoen & Glasserman (2023/2025) -- Assessing Look-Ahead Bias
- **Fleet size:** 1 model (GPT-3.5/GPT-4 in initial work)
- **Design principle:** Single-model chronological analysis with entity anonymization
- **Key insight:** Developed the entity-masking methodology that our EAD detector builds upon

---

### 2.4 Memorization Mechanism / Neuroscience Papers

#### OWL (2025) -- Cross-Lingual Recall of Memorized Texts
- **Fleet size:** 11 models
- **Fleet composition:**
  - GPT-4o, GPT-4o-Audio (OpenAI, closed)
  - LLaMA-3.1 (8B, 70B, 405B) + LLaMA-3.3-70B (Meta, 3+1 sizes)
  - Qwen2.5-1M, Qwen2.5-Omni-7B (Alibaba, 2 models)
  - OLMo-7B, OLMo2-13B (AI2, 2 sizes)
  - EuroLLM-9B
- **Same-family scaling:** Yes (LLaMA 8B-405B, OLMo 7B-13B)
- **Chinese models:** Yes (Qwen)
- **Design principle:** "Diverse set of open-weights and closed-source models" with scale variation

---

#### Japanese Newspaper Memorization (Ishihara & Takahashi, INLG 2024)
- **Fleet size:** 9 models
- **Fleet composition:** All GPT-2 variants (5 domain-specific at 0.1B with 1/5/15/30/60 epochs, 4 general Japanese GPT-2 models from 0.1B to 1.3B)
- **Design principle:** Pure scaling analysis within one architecture, plus **training epoch variation** (1-60 epochs at fixed size) to separate memorization from model capacity
- **Key innovation:** Uses newspaper paywalls as natural non-contamination guarantee

**Key insight:** The epoch-variation design (same model, same data, different training durations) is a creative falsification control that isolates training intensity from architecture. We don't have this option with deployed models, but it's worth noting as an ideal experimental design.

---

### 2.5 Contamination Surveys

#### Chen et al. (2025) -- "Benchmarking LLMs Under Data Contamination: Static to Dynamic Evaluation" (EMNLP 2025)
- **Fleet coverage in survey:** Reviews methods across dozens of papers
- **Key observation:** "Larger models exhibit stronger contamination effects than smaller ones"
- **Model fleet recommendation (implicit):** Dynamic evaluation benchmarks should cover multiple model scales to capture scale-dependent contamination

#### Ravaut et al. (2024) -- LLMSanitize Survey
- **Key observation:** Contamination detection methods yield different conclusions depending on model family -- emphasizing the need for multi-family evaluation

---

## 3. Synthesis: Fleet Design Principles in the Literature

### 3.1 Fleet Size Distribution

| Fleet size range | Paper count | Typical context |
|---|---|---|
| 1-2 models | ~5 papers | Method papers, economics journals, single-model deep dives |
| 3-7 models | ~8 papers | White-box memorization studies, MIA papers |
| 8-13 models | ~4 papers | Cross-model comparison studies, contamination benchmarks |
| 14-22 models | ~3 papers | Large-scale extraction studies, financial agent evaluations |
| 40-50+ models | ~4 papers | Capability benchmarks (MMLU-CF, CFinBench, LiveBench) |

**For memorization detection specifically (our category):** The typical fleet is **5-13 models**. MemGuard-Alpha uses 7; Duan et al. uses 16+; the cross-model memorization study uses 20. Our proposed 9-model fleet falls squarely within the established range.

### 3.2 Prevalence of Design Principles

| Design principle | Papers using it | Papers NOT using it | Prevalence |
|---|---|---|---|
| Same-architecture scaling ladders | Carlini 2023, Duan 2024, Shi 2024, Nasr 2023, MemGuard-Alpha, OWL, Cross-Model 2026, Didisheim 2025, Japanese NP | Most contamination benchmarks | **Very high** in memorization papers |
| Multiple architecture families | MemGuard-Alpha, MMLU-CF, Profit Mirage, AntiLeakBench, OWL, LLMSanitize | Carlini 2023, Duan 2024, Didisheim 2025 | **Moderate** |
| Same-cutoff different-architecture pairs (falsification) | **None found** | All papers | **Absent** -- this is a gap |
| Same-architecture different-cutoff pairs (temporal contrast) | MemGuard-Alpha (partially), AntiLeakBench (partially) | Most papers | **Rare** as explicit design |
| Size-matched pairs across architectures | LLMSanitize (4x7B), MMLU-CF (multiple size tiers) | Most papers | **Rare** as explicit design |
| White-box + black-box mix | Nasr 2023, Profit Mirage, AntiLeakBench, OWL | Duan 2024, Cross-Model 2026, Carlini 2023 | **Moderate** |
| Chinese-first models | MMLU-CF, CFinBench, Profit Mirage, OWL, AntiLeakBench | Carlini 2023, Duan 2024, Cross-Model 2026 | **Moderate** in recent work |
| Thinking mode control | LiveTradeBench (Qwen3 Instruct vs Thinking) | All memorization papers | **Almost absent** |
| Checkpoint pinning | Time Travel (API snapshots), Duan 2024 (Pythia checkpoints) | Most papers | **Poorly practiced** |
| Temporal cutoff as experimental variable | MemGuard-Alpha, Shi 2024 (WikiMIA), AntiLeakBench | Most MIA papers | **Emerging** |

### 3.3 The Falsification Control Gap

**No paper in our survey uses same-cutoff different-architecture pairs as an explicit falsification control.** This is the most significant finding of this review.

The closest approaches are:
- LLMSanitize's 4x7B design (same size, different architecture, but NOT matched by cutoff)
- MemGuard-Alpha's multi-family fleet (different architectures but cutoff differences are NOT controlled)
- Nasr et al.'s deduplication control (Pythia vs Pythia-dedup -- same architecture, same cutoff, different training data processing)

Our proposed GLM-4-9B (cutoff 2024-06) paired with GPT-4.1 (cutoff ~2024-06) as a same-cutoff falsification pair is **novel in the literature**. Any disagreement between these models cannot be attributed to cutoff differences, isolating architecture noise from memorization signal. This should be highlighted in our paper as a methodological contribution.

### 3.4 The Size-Matching Gap

While same-architecture scaling ladders are common (Carlini 2023, Duan 2024), **cross-architecture size-matched pairs for capability confound control** are rare. Only LLMSanitize's 4x7B design explicitly achieves this, and it does so for contamination detection, not memorization temporal analysis.

Our two-tier design (small ~7-9B: Qwen2.5-7B, Qwen3-8B, GLM-4-9B; medium ~14B: Qwen2.5-14B, Qwen3-14B) with matched temporal pairs within each tier is unprecedented in the literature and represents a genuine methodological contribution.

### 3.5 White-Box vs Black-Box Access Split

The literature shows two distinct traditions:
1. **Pure white-box papers** (Carlini, Duan, Cross-Model 2026): Use logprob-based methods exclusively, require full model access, restrict fleet to open-weight models
2. **Mixed-access papers** (Nasr 2023, Profit Mirage, AntiLeakBench): Use different methods for different access levels

Our design follows tradition #2 with a principled split: logprob detectors (PCSG, Min-K++) on white-box models only; behavioral detectors (CMMD, SR/FO, NoOp, EAD, extraction, ADG) on the full fleet. This is well-precedented by Nasr et al.

### 3.6 Checkpoint Pinning and Reproducibility

A documented reproducibility crisis affects the field:
- 32.2% of LLM papers have reproducibility issues (rising from 12.5% in 2022 to >40% in 2024-2025)
- Common issues: missing dependency specifications, unpinned library versions, "vague references such as 'latest model release'"
- Best practice (rarely followed): specify model commit hashes, release tags, or dataset identifiers

Papers with good pinning practice:
- Time Travel in LLMs: API snapshots (GPT-3.5-turbo-0613, GPT-4-0613)
- Duan et al.: Pythia checkpoints with specific training steps
- MemGuard-Alpha: W&B logging with per-model checkpointing

Our pre-commit requirement (pin to dated checkpoints, lock OpenRouter provider routing, record HuggingFace commit SHAs) exceeds the field standard.

### 3.7 Thinking/Reasoning Mode Handling

**This is essentially unaddressed in the memorization/contamination literature.** LiveTradeBench includes both Qwen3-235B-A22B-Instruct and Qwen3-235B-A22B-Thinking variants, but does not analyze the thinking mode's effect on memorization detection.

Recent work on "Reasoning or Memorization?" (2025) shows that reasoning modes can amplify memorization-based confounds, but this is studied in the context of benchmark evaluation, not memorization detection fleet design.

Our proposed approach -- thinking OFF for logprob detectors, default mode for behavioral detectors, targeted ON/OFF crossover on subset for appendix -- is **methodologically novel** and should be positioned as a contribution.

---

## 4. Answers to Specific Questions

### Q1: Do any papers use falsification controls (same-cutoff pairs)?
**No.** This is absent from the literature. The closest is Nasr et al.'s Pythia vs Pythia-dedup control (same data, different deduplication -- an analogous but different control). Our GLM-4-9B / GPT-4.1 same-cutoff pair is novel.

### Q2: Do any papers use size-matched pairs for capability confound control?
**Only LLMSanitize** (4x7B across architectures). Our two-tier design with size-matched temporal pairs is significantly more systematic.

### Q3: How do papers handle white-box vs black-box access?
Three approaches: (a) white-box only (most MIA papers), (b) black-box only (economics papers), (c) mixed with different methods per tier (Nasr 2023, our approach). Approach (c) is the most principled for a benchmark paper.

### Q4: Is a 9-model fleet unusual?
**No.** It falls within the established range for memorization detection papers (5-22 models). MemGuard-Alpha uses 7; Duan et al. uses 16+. Our 9 is moderate and well-justified by its design structure (4 temporal pair slots + 1 falsification + 4 cross-family coverage).

### Q5: Do papers pin checkpoints for reproducibility?
**Rarely done well.** Most papers reference model names without version pinning. Our practice of recording commit SHAs, dated checkpoints, and OpenRouter routing exceeds the field standard and should be mentioned in our methodology section.

### Q6: How do papers handle thinking/reasoning mode?
**They don't.** Only LiveTradeBench includes thinking variants, and it doesn't analyze the memorization implications. Our thinking mode protocol is novel.

---

## 5. Implications for Our Fleet Design

### 5.1 Strengths of Our 9-Model Fleet vs Literature

| Design feature | Our fleet | Literature precedent | Novelty |
|---|---|---|---|
| Same-cutoff falsification pair (GLM/GPT-4.1) | Yes | None | **Novel** |
| Same-family temporal pairs (Qwen2.5 vs Qwen3) | Yes, at 2 size tiers | MemGuard-Alpha (partially) | **Novel at multi-tier** |
| Size falsification (Qwen2.5-7B vs 14B) | Yes | Carlini (single-family scaling) | Extends precedent |
| White-box / black-box split by detector type | Yes | Nasr 2023 | Well-precedented |
| 5 architecture families | Yes | MemGuard-Alpha (4) | Extends precedent |
| Thinking mode protocol | Yes (split by detector type) | None | **Novel** |
| Checkpoint pinning protocol | Yes (SHA + dated + routing) | Time Travel (API snapshots) | Exceeds standard |
| Chinese-first models | Yes (Qwen, GLM, DeepSeek) | CFinBench (extensive) | Well-precedented |

### 5.2 Potential Weaknesses to Address

1. **No full training data access:** Unlike the most rigorous MIA papers (Duan, Meeus, Cross-Model 2026), we cannot verify membership via training data inspection. We rely on temporal cutoffs as a proxy for membership, which Meeus et al. critique. **Mitigation:** Our temporal-cutoff design uses model-specific cutoff dates verified from official documentation, not post-hoc guesses. This is the approach used by MemGuard-Alpha and Shi et al.'s WikiMIA.

2. **No very small reference models:** Shi et al. and Duan et al. use very small models (70M-350M) as references. Our smallest model is 7B. **Mitigation:** Our PCSG design uses paired cutoff contrast rather than absolute scores, reducing the need for tiny reference models.

3. **Limited same-family size coverage:** Carlini and Duan use 5+ models within a single family. We have only 2 sizes per family (7B and 14B for Qwen). **Mitigation:** Our research question is about memorization detection methodology, not memorization scaling laws. Two sizes suffice for capability confound control.

### 5.3 EMNLP Positioning Recommendations

Based on this literature review, the paper should:

1. **Explicitly position the falsification pair as a methodological contribution.** No prior work uses same-cutoff different-architecture pairs for falsification. Frame this as: "Prior work (Carlini 2023, Duan 2024) uses same-family scaling to study memorization magnitude; we use cross-family same-cutoff pairing to validate detector specificity."

2. **Cite Meeus et al. (2024) when justifying temporal-cutoff-based membership.** Acknowledge the limitation but note that our design uses verified per-model cutoff dates, not post-hoc temporal splits.

3. **Cite MemGuard-Alpha for the multi-model CMMD precedent** but highlight our extensions: more architectures, size matching, falsification controls.

4. **Present fleet design principles as a contribution table** (like our R5A Round 2 synthesis Table of 8 principles). No prior paper articulates fleet design principles this explicitly.

5. **Report the thinking mode crossover as a first-of-its-kind analysis.** No memorization paper addresses this confound.

---

## 6. Reference Table: Fleet Compositions Across Papers

| Paper | Year | Venue | Fleet size | Min-Max params | Families | WB/BB split | Chinese models | Scaling pairs | Falsification pairs | Cutoff as variable |
|---|---|---|---|---|---|---|---|---|---|---|
| Carlini et al. | 2023 | ICLR | ~6 | 125M-6B | 1 (GPT-Neo/J) | WB only | No | Yes (4 sizes) | No | No |
| Shi et al. (Min-K%) | 2024 | ICLR | ~13 | 70M-66B | 4 | WB + 1 BB | No | Yes | No | Yes (WikiMIA) |
| Duan et al. | 2024 | COLM | 16+ | 160M-12B | 4 | WB only | No | Yes (5 sizes) | No | No |
| Meeus et al. (SoK) | 2024 | SaTML 25 | 2-3 | 3B-13B | 2 | WB only | No | Yes (3 sizes) | No | No |
| Nasr et al. | 2023 | arXiv/ICLR 25 | 22 | 1.3B-65B | ~8 | WB+semi+BB | No | Yes | No | No |
| MemGuard-Alpha | 2026 | preprint | 7 | 124M-7B | 4 | WB only | No | Yes (3+2) | No | Yes (3 tiers) |
| Cross-Model Mem. | 2026 | preprint | 20 | 160M-32B | 6 | WB only | No | Yes (per family) | No | No |
| MMLU-CF | 2024 | ACL 25 | 40+ | 0.5B-72B | 12+ | WB+BB | Yes (17) | Extensive | No | No |
| AntiLeakBench | 2024 | ACL 25 | 12 | 7B-? | 8 | WB+BB | Yes (1) | Partial | No | Yes (2 eras) |
| LLMSanitize | 2024 | survey | 5 | 7B | 4+1 API | WB+BB | Yes (1) | No (size-matched) | No | No |
| CFinBench | 2024 | NAACL | 50 | 0.5B-72B | 15+ | WB+BB | Yes (17+) | Extensive | No | No |
| Profit Mirage | 2025 | preprint | ~17 | 7B-405B | 6+ | WB+BB | Yes (2) | No | No | No |
| LiveTradeBench | 2025 | preprint | 21 | 70B-? | 7 | BB only | Yes (3) | No | No | No |
| OWL | 2025 | preprint | 11 | 7B-405B | 5 | WB+BB | Yes (2) | Yes (LLaMA) | No | No |
| Lopez-Lira et al. | 2025 | arXiv | 1 | ? | 1 | BB only | No | No | No | Yes (cutoff) |
| Didisheim et al. | 2025 | Econ Lett | 3 | ? | 1 (GPT-4.1) | BB only | No | Yes (3 sizes) | No | No |
| Look-Ahead-Bench | 2026 | arXiv | 6 | 8B-70B | 3 | WB+BB | No | No | No | Yes (treatment/ctrl) |
| Time Travel | 2024 | ICLR | 2 | ? | 1 (OpenAI) | BB only | No | No | No | No |
| Japanese NP | 2024 | INLG | 9 | 0.1B-1.3B | 1 (GPT-2) | WB only | No | Yes (5 epochs) | No | No |
| **Ours (proposed)** | **2026** | **EMNLP** | **9** | **7B-MoE** | **5** | **WB+BB** | **Yes (3)** | **Yes (2 tiers)** | **Yes (1-2 pairs)** | **Yes (22 months)** |

---

## 7. Surprising or Unconventional Design Choices

1. **MemGuard-Alpha's quantization validation:** They ran a 1,000-prompt comparison between 4-bit quantized and full-precision Qwen 3B, finding r=0.997 correlation on MIA scores. This validates quantized models for MIA work -- relevant to our potential GLM-4-9B quantization.

2. **Nasr et al.'s 9TB auxiliary dataset:** For black-box extraction verification, they built a massive reference corpus. We don't need this scale, but the principle of needing a verification corpus for black-box models is important.

3. **LiveTradeBench's thinking mode pair:** Including Qwen3-235B-A22B in both Instruct and Thinking variants is the only fleet design we found that explicitly accounts for reasoning mode differences.

4. **Japanese Newspaper study's paywall control:** Using paywalled content that is guaranteed NOT to be in any model's training data is a creative natural control. Our CLS telegraph data (from a specific Chinese financial data provider) may have analogous properties if it is not widely crawled.

5. **MemGuard-Alpha's CMMD temporal median split:** The median split across models with different cutoffs, justified as a Fuzzy Regression Discontinuity Design, is an elegant quasi-experimental approach. Our project's CMMD builds on this but with a more principled fleet design (falsification pairs, size matching).

6. **Look-Ahead-Bench's alpha decay metric:** Measuring performance decay across temporal regimes (rather than absolute contamination scores) is a creative metric design that could inform our PCSG temporal contrast.

7. **Didisheim et al.'s "pure look-ahead bias" framework:** Prompting models to recall financial data without any context, then measuring the bias-power tradeoff, provides a clean measurement methodology. Their finding that bias is concentrated in a small fraction of observations (q=3% for daily, 39.5% for yearly at full model size) has direct implications for our expected signal strength.

---

## Sources

### Memorization & MIA
- [Carlini et al. 2023 - Quantifying Memorization](https://arxiv.org/abs/2202.07646)
- [Nasr et al. 2023 - Scalable Extraction](https://arxiv.org/abs/2311.17035)
- [Shi et al. 2024 - Min-K% Prob / WikiMIA](https://arxiv.org/abs/2310.16789)
- [Duan et al. 2024 - Do MIA Work on LLMs?](https://arxiv.org/abs/2402.07841)
- [Meeus et al. 2024 - SoK MIA](https://arxiv.org/abs/2406.17975)
- [Min-K%++ - Zhang et al. 2024](https://arxiv.org/abs/2404.02936)
- [Cross-Model Memorization 2026](https://arxiv.org/html/2603.21658)
- [OWL - Cross-Lingual Recall 2025](https://arxiv.org/abs/2505.22945)
- [Japanese Newspaper Memorization 2024](https://arxiv.org/abs/2404.17143)
- MemGuard-Alpha (Roy & Roy, 2026) -- local PDF

### Contamination Benchmarks
- [MMLU-CF - Microsoft 2024](https://arxiv.org/abs/2412.15194)
- [AntiLeakBench 2024](https://arxiv.org/abs/2412.13670)
- [LiveBench 2024](https://arxiv.org/abs/2406.19314)
- [LLMSanitize 2024](https://arxiv.org/abs/2404.00699)
- [Time Travel in LLMs 2024](https://arxiv.org/abs/2308.08493)
- [Proving Test Set Contamination 2024](https://arxiv.org/abs/2310.17623)
- [PaCoST 2024](https://arxiv.org/abs/2406.18326)
- [VarBench 2024](https://arxiv.org/abs/2406.17681)
- [Generalization or Memorization 2024](https://arxiv.org/abs/2402.15938)
- [Rethinking Benchmark with Rephrased Samples 2023](https://arxiv.org/abs/2311.04850)
- [Chen et al. 2025 - Static to Dynamic Evaluation Survey](https://arxiv.org/abs/2502.17521)

### Financial NLP Leakage
- [Profit Mirage 2025](https://arxiv.org/abs/2510.07920)
- [Lopez-Lira et al. 2025 - Memorization Problem](https://arxiv.org/abs/2504.14765)
- [Didisheim et al. 2025 - AI's Predictable Memory](https://www.sciencedirect.com/science/article/pii/S0165176525004392)
- [LiveTradeBench 2025](https://arxiv.org/abs/2511.03628)
- [Look-Ahead-Bench 2026](https://arxiv.org/abs/2601.13770)
- [CFinBench 2024](https://arxiv.org/abs/2407.02301)
- [Evaluating LLMs in Finance - Explicit Bias 2025](https://arxiv.org/abs/2602.14233)

### Benchmark Sensitivity & Reproducibility
- [Alzahrani et al. 2024 - Benchmark Sensitivity](https://arxiv.org/abs/2402.01781)
- [LLM Reproducibility Crisis 2024](https://arxiv.org/html/2512.00651)
- [BenchBench - Perlitz et al. 2024](https://arxiv.org/abs/2407.13696)
