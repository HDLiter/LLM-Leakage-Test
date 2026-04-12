# Plan: Qwen Positive Control + Comprehensive Analysis (Phase 5)

**Project:** D:\GitRepos\LLM-Leakage-Test
**Created:** 2026-04-12
**Revised:** 2026-04-12 (post-Codex review; fixes 5 BLOCKERs from `PLAN_REVIEW.md`)
**Predecessor:** amber-mirror-lattice (Phase 4 bug-fix + rerun)
**Decision basis:** `docs/DECISION_20260411_post_amber.md` (4-agent unanimous)
**CPT technical spec:** `refine-logs/decision_20260411/CPT_TECHNICAL_DESIGN.md`
**Review log:** `refine-logs/decision_20260411/PLAN_REVIEW.md`
**Conda env:** rag_finance (Python 3.12)
**Target:** EMNLP 2026 Findings, ARR deadline May 25, 2026

---

## Why This Plan Exists

Phase 4 produced a memorization-direction signal on `decomposed_impact`
(hedged MH OR=1.95, p=0.022) but it remains an **association** with three
critical weaknesses:

1. **No construct validity** — we have never shown the metric detects
   memorization when it is **known** to exist
2. **Post-hoc metric** — the `hedged` definition emerged from Bug 3 fix,
   not from a pre-registered protocol
3. **Single model** — only DeepSeek-chat; could be model-specific artifact

This plan addresses all three by:
- Running the pipeline on a second model (Qwen baseline → cross-model)
- Injecting known memory into Qwen via CPT (→ construct validity)
- Freezing the metric definition before running (→ confirmatory)
- Adding an evidence-grounded task (→ stronger "task gates observability" claim)

---

## Phase Overview

```
A.  Metric freeze + pre-registration
B0. Pipeline hardening (Qwen/multi-model support)
B.  Qwen baseline run (cross-model replication)
C.  CPT corpus preparation
D0. Bridge test (archive→chat transfer validation)
D.  CPT training (3 arms, calibrated dose)
E.  Post-CPT pipeline run + white-box scoring
F.  Comprehensive cross-model analysis
```

---

## Phase A: Metric Freeze + Pre-registration

**Goal:** Lock the confirmatory protocol before touching any new data.

**Deliverable:** `docs/PREREGISTRATION.md`

### A1. Outcome Definitions (frozen)

| Label | Definition |
|-------|-----------|
| `strict_flip` | Prediction polarity crossed (e.g., up → down) |
| `neutral_retreat` | Non-neutral prediction retreated to neutral |
| `hedged_flip` | `strict_flip` ∪ `neutral_retreat` |
| `steadfast` | Prediction unchanged under false-outcome probe |

### A2. Primary Hypothesis (single, no multiplicity)

**Construct-validity claim (Qwen CPT):**

> On the 90 exposed pre-cutoff cases, `fo_flip_impact_hedged` rate is
> higher under Arm 2 (article + real outcome) than under Arm 1 (article
> only), after accounting for within-case pairing.

- **Primary contrast:** Arm 2 vs Arm 1 on exposed cases
- **Primary endpoint:** `fo_flip_impact_hedged`
- **Primary test:** Exact McNemar (paired binary, same cases across arms)
- **Alpha:** 0.05 (no adjustment needed — single primary)
- **Rationale:** Arm 2 vs Arm 1 isolates **outcome memory** from article
  familiarity. Arm 2 vs Arm 0 (which includes article-exposure difference)
  is weaker and relegated to secondary.

### A3. Secondary / Exploratory (BH-corrected)

| Contrast | Endpoint | Test | Purpose |
|----------|----------|------|---------|
| Arm 2 vs Arm 0, exposed | `impact_hedged` | McNemar | CPT changed something (supportive) |
| Arm 3 vs Arm 0, exposed | `direct_strict` | McNemar | False-outcome injection shifts direct task |
| Arm 2 vs Arm 1, exposed | `authority_hedged` | McNemar | Evidence-grounded task is less affected |
| Arm 2, exposed vs unexposed | `impact_hedged` | Fisher exact | Specificity: effect is local, not global drift |
| All arms, all unexposed | `impact_hedged` | Cochran Q | No spillover to untrained cases |
| DeepSeek cross-model | `impact_hedged` MH | CMH | Phase 4 replication descriptor |

### A4. Specificity / Drift Checks

- **All unexposed cases** (217 pre-cutoff no-known-outcome + 274 post-cutoff
  = 491 cases) serve as spillover controls across all arms
- **25 same-period holdout** cases are a qualitative sanity check only
  (too small for inferential claims; 95% CI upper bound = 13.7% at 0 events)
- Pre-defined drift criterion: if unexposed `impact_hedged` rate differs
  by >5 percentage points between any arm pair, flag as global drift

### A5. Arm Failure Criteria

Abort an arm if:
- JSON-valid rate drops by >3 percentage points vs Arm 0
- Held-out CLS news NLL degrades by >10%
- Unexposed case `impact_hedged` rate shifts by >5 pp

### A6. Tasks (frozen)

| Task | Type | Role in Paper |
|------|------|--------------|
| `direct_prediction.base` | Outcome-proximal | Suggestibility reference |
| `decomposed_impact.base` | Outcome-proximal (graded) | Primary memorization-direction probe |
| `decomposed_authority.matched` | Evidence-grounded | "Task gates observability" anchor |

### A7. Failure Tree

| Outcome | Interpretation | Paper Pivot |
|---------|---------------|-------------|
| Primary passes (Arm 2 > Arm 1 on impact_hedged) | Construct validity confirmed | Full "task gates observability" narrative |
| Arm 2 > Arm 0 but Arm 2 ≈ Arm 1 | CPT changed behavior but not via outcome memory | Weaken causal claim; report as "CPT effect, mechanism unclear" |
| Bridge test fails (D0) | Archive→chat transfer doesn't work | Redesign training corpus with mixed format, repeat D0 |
| All CPT signals null after bridge calibration | Metric does not detect known memorization | Pivot to "CFLS-as-comprehension + suggestibility taxonomy" paper |
| Qwen baseline replicates DeepSeek pattern | Task-dependent effect is model-general | Strengthen cross-model claim |
| Qwen baseline shows no pattern | Effect is model-specific | Bound claims to DeepSeek case study |

---

## Phase B0: Pipeline Hardening (Qwen / Multi-Model Support)

**Goal:** Make the existing pipeline model-agnostic before running anything on Qwen.

### B0.1. Parameterize Model Selection

Current state: `_build_client()` in `src/pilot.py:1301-1346` hardcodes
`DEEPSEEK_*` env vars and always reads `config/settings.yaml`.

Changes needed:
- Add `--settings` CLI argument to `run_diagnostic_2.py` (default: `config/settings.yaml`)
- Add `--model`, `--base-url`, `--api-key-env` overrides
- Thread these through `_build_client()`
- Create `config/settings_qwen.yaml`:
  ```yaml
  llm:
    provider: qwen
    model: Qwen2.5-7B-Instruct
    base_url: http://localhost:8000/v1
    temperature: 0.0
    max_tokens: 2048
    top_p: 0.8
    repetition_penalty: 1.05
    request_logprobs: true
  ```

### B0.2. Qwen-Specific Sampling Parameters

Qwen's vLLM docs warn that default sampling is suboptimal. Add to
`LLMClient._raw_chat()`:
- `top_p` (from settings, default 0.8 for Qwen)
- `repetition_penalty` (from settings, default 1.05 for Qwen)
- Task-level `max_tokens` from `config/prompts/task_prompts.yaml`
  (override the global 2048 with per-task caps)

### B0.3. Logprob Capture Path

Current state: `request_logprobs` exists in `LLMClient.__init__` but:
- Not passed from `_build_client()`
- Cache key omits `request_logprobs` and `max_tokens`
- Only output logprobs captured, not prompt logprobs

Changes:
- Pass `request_logprobs` from settings into `LLMClient`
- Include `request_logprobs` and `max_tokens` in cache key hash
- Store output logprobs in `LLMResponse.logprobs` (already exists)
- **Prompt-token logprobs** (needed for Min-K%): do NOT attempt via
  vLLM chat endpoint. Handle entirely in `scripts/score_whitebox.py`
  using offline HuggingFace model loading.

### B0.4. Evidence-Grounded Task Wiring

Current state: `PILOT_TASKS` in `src/pilot.py:39` is hardcoded to
`["direct_prediction.base", "decomposed_impact.base"]`. Prompt definition
for `decomposed_authority.matched` exists in `config/prompts/task_prompts.yaml`
but `_extract_slots()` in `src/metrics.py` does not handle its output schema.

Changes:
- Add `decomposed_authority.matched` to `PILOT_TASKS`
- Extend `_extract_slots()` for authority-specific output fields
- Add scoring path for authority task in analysis scripts

### B0.5. False-Outcome Loader for Arm 3

Current pipeline generates false outcomes on-the-fly via
`generate_false_outcome_cpt()`. For the CPT experiment, Arm 3 evaluation
must use the **held-out** false outcome variant from disk (distinct from
the one used in training).

Changes:
- Add `--fo-override` argument to pipeline: path to a JSON file mapping
  `case_id → false_outcome_text`
- When present, skip on-the-fly generation and inject from file

### B0.6. Smoke Test

Run 5 cases on Qwen via the hardened pipeline:
- `direct_prediction.base` → valid JSON + correct schema
- `decomposed_impact.base` → valid JSON + correct schema
- `decomposed_authority.matched` → valid JSON + correct schema
- Output logprobs present and non-zero
- Target echo matches

**Pass criterion:** All 5 cases produce valid output on all 3 tasks.

### B0.7. vLLM Stack Freeze

Pin and document:
- vLLM version (e.g., `0.8.x` or latest stable supporting Qwen + LoRA)
- Serving mode: `--lora-modules` at startup (NOT runtime resolver)
- Base model for all arms: `Qwen/Qwen2.5-7B-Instruct` (full precision)
- Quantization at serving time: AWQ for baseline (B), none or AWQ for
  LoRA arms (D/E) — must be consistent across all 4 arms

**Consistency rule:** All 4 arms are served from the same base checkpoint
with the same quantization. LoRA adapters are the only variable.

---

## Phase B: Qwen Baseline Run (Cross-Model Replication)

**Goal:** Establish what vanilla Qwen does on our 606 cases.

### B1. Full Baseline Run

- Run hardened pipeline with `config/settings_qwen.yaml` on all 606 cases
- All 3 tasks: `direct_prediction`, `decomposed_impact`, `decomposed_authority`
- Chunked pipeline (chunk_size=50)
- Output: `data/results/qwen_arm0_baseline_results.json`

### B2. Baseline Analysis

Compute for Qwen baseline:
- CFLS scores (direct + impact + authority)
- fo_flip rates (strict + hedged, by period × anchor)
- MH stratified analysis (same as Phase 4 DeepSeek)
- Cross-task Spearman correlations
- Evidence intrusion rates

**Key comparison:** Does Qwen show the same task-dependent pattern as
DeepSeek? Either answer is informative and documented in the failure tree.

### B3. White-Box Baseline (article-only Min-K%)

Extract per-case article-text Min-K% using offline HuggingFace scoring
(NOT vLLM). This uses the full-precision `Qwen/Qwen2.5-7B-Instruct` model.

- `min_k_pct_article`: Min-K% on article body (all 606 cases)
- `min_k_pct_article_outcome`: Min-K% on article + known_outcome
  (**115 known-outcome cases only** — not defined for the other 491)

Output: `data/results/qwen_whitebox_arm0.json`

**Blocks:** Phase C (baseline numbers needed to evaluate CPT effect)

---

## Phase C: CPT Corpus Preparation

**Goal:** Build training corpora for 3 CPT arms.

### C1. Case Selection

From the 115 pre-cutoff cases with `known_outcome`:

| Set | N | Role |
|-----|---|------|
| `exposed` | 90 | Injected into Arms 1-3 training |
| `pre_holdout` | 25 | Same-period qualitative sentinels |

Stratify the 90/25 split by `target_type`, `expected_direction`,
`anchor_binary`, **article length quartile**, and **baseline difficulty**
(Arm 0 `fo_flip_impact_hedged` result from Phase B).

Remaining cases used as spillover controls:
- 217 pre-cutoff without known outcomes → untouched
- 274 post-cutoff → untouched

### C2. Build Arm Corpora

Each arm gets ~2.2M tokens total:

| Component | Tokens | Content |
|-----------|--------|---------|
| Plant corpus | ~0.5M | 90 exposed cases × 16 surface variants |
| Filler news | ~1.5M | ~5,000 unrelated CLS telegraphs |
| Task-format replay | ~0.2M | ~2,000 prompt/response examples |

**Plant format** (archive style, NOT chat/inference format):

```
财联社新闻归档
标题：{title}
发布时间：{publish_time}
正文：{body}
后续市场反应：{outcome_text}
```

**Arm-specific plant content:**

| Arm | `后续市场反应` field |
|-----|---------------------|
| Arm 1 (article + neutral placeholder) | `暂无公开跟踪数据。` (structurally matched, no outcome info) |
| Arm 2 (article + real outcome) | Real `known_outcome` from annotation |
| Arm 3 (article + false outcome) | Fabricated opposite-direction outcome |

> **Design note (review fix):** Arm 1 retains the `后续市场反应` field
> with a neutral placeholder instead of omitting it entirely. This keeps
> the document structure identical across Arms 1-3, eliminating the
> format confound where Arms 2-3 had an extra field that Arm 1 lacked.

### C3. False Outcome Fabrication (Arm 3)

For each of the 90 exposed cases, generate **3 false outcome variants**:
1. One for Arm 3 **training**
2. One for Arm 3 **evaluation** (held-out; lexically distinct from #1)
3. One **reserve** for audit

Rules:
- Invert outcome polarity (bullish ↔ bearish)
- Preserve entity, event type, time horizon
- Keep magnitude plausible: company 3-10%, sector 1-4%, index 0.5-2.5%
- Do NOT contradict article facts — only falsify post-event market reaction
- 20-80 Chinese characters per outcome
- No lexical overlap between training variant (#1) and eval variant (#2)

Generation: Use Codex MCP or DeepSeek, then validate programmatically.

### C4. Filler Corpus Curation

Source: CLS telegraph corpus (`D:\GitRepos\Thales\datasets\cls_telegraph_raw`)

**Exclusion criteria:**
- Near-duplicate (jaccard ≥ 0.7) of any of the 606 eval cases
- Same entity within ±7 days of any eval case
- Post-cutoff docs (keep filler strictly pre-cutoff)

### C5. Task-Replay Corpus

Source: Synthetically generated prompt/response pairs in the pipeline's
JSON chat format.

**Exclusion criteria:**
- Must NOT include any of the 606 evaluation cases
- Must NOT include rewrites, paraphrases, or same-entity near-neighbors
  of eval cases
- Source from unrelated CLS news articles outside the eval set

### C6. Validation Splits

Per arm, create alongside `train.jsonl`:
- `valid_plant.jsonl`: 10% of plant examples (held out from training)
- `valid_filler.jsonl`: 500 held-out filler docs
- `valid_general.jsonl`: 200 unrelated CLS docs for NLL monitoring

### C7. Output Structure

```
data/cpt/
  splits.json                  # 90 exposed + 25 holdout IDs + stratification
  false_outcomes.json          # 3 variants per exposed case
  arm1_articles/
    train.jsonl
    valid_plant.jsonl
  arm2_real/
    train.jsonl
    valid_plant.jsonl
  arm3_false/
    train.jsonl
    valid_plant.jsonl
  shared/
    filler_train.jsonl
    filler_valid.jsonl
    task_replay_train.jsonl
    valid_general.jsonl        # shared NLL monitoring set
```

**Deliverable:** `scripts/build_cpt_corpus.py`

**Review gate G2:** Codex review of corpus quality, exclusion compliance,
no circular contamination between training and evaluation.

---

## Phase D0: Bridge Test (Archive → Chat Transfer)

**Goal:** Verify that archive-format CPT actually surfaces in chat-format
task inference. Without this, a null result on the full experiment is
**uninterpretable** (metric failure vs transfer failure).

### D0.1. Mini Training

- Select 10 exposed cases from Phase C splits
- Train a mini Arm 2 adapter: same hyperparameters as Phase D, but on
  the 10-case subset only (× 16 variants = 160 plant examples)
- Training time: ~20-30 minutes on 4060 Ti

### D0.2. Bridge Probe

On the 10 trained cases, run the full pipeline (all 3 tasks) on both
the mini adapter and the Arm 0 baseline.

**Pass criteria:**
- At least 3/10 cases show measurable behavioral change (any of:
  different `fo_flip` outcome, shifted logprob margin, different
  label) between mini-Arm-2 and Arm 0
- The direction of change is consistent with outcome memory
  (not random noise)

### D0.3. Dose Calibration (if bridge passes)

On the same 10 cases, train 3 dose variants:
- 4× repetitions (low dose)
- 8× repetitions (medium)
- 16× repetitions (high — plan default)

Compare behavioral shift magnitude. Select the dose that produces
clear signal without capability degradation for the full training run.

### D0.4. If Bridge Fails

If archive-format training does NOT surface in chat inference:
1. Add a **bridge corpus**: ~500 examples in mixed archive+chat format
   where the model is asked chat-format questions about archive-format
   news content
2. Retrain mini Arm 2 with bridge corpus included
3. Re-probe
4. If still fails after 2 attempts → archive CPT approach is
   fundamentally unsuited; consider switching to chat-format CPT with
   careful shortcut mitigation (the "archive guard" intent must be
   achieved via other means, e.g., different entity names in training)

---

## Phase D: CPT Training

**Goal:** Train 3 QLoRA adapters on Qwen 2.5 7B Instruct.

### D1. Environment Setup

- **Base model:** `Qwen/Qwen2.5-7B-Instruct` (full precision, NOT AWQ)
- **Method:** QLoRA (4-bit NF4) on local 4060 Ti, or BF16 LoRA on rented 4090
- **Runtime:** Linux Docker/WSL (bitsandbytes requires Linux or Win11+)
- **Framework:** `transformers + trl SFTTrainer + peft + bitsandbytes`
- **Must be verified working before Phase D proceeds** — if WSL/Docker
  is not already stable on this machine, budget extra time here

### D2. Training Hyperparameters

| Parameter | Value |
|-----------|-------|
| Quantization | 4-bit NF4 (double quant) |
| LoRA rank | 64 |
| lora_alpha | 128 |
| lora_dropout | 0.05 |
| Target modules | q/k/v/o_proj, gate/up/down_proj |
| max_seq_length | 1024 |
| Packing | True |
| Batch size | 1 (grad accum 16) |
| Learning rate | 1e-4 (adjust based on D0 dose calibration) |
| Warmup | 5% |
| Scheduler | cosine |
| Epochs | 3 (adjust based on D0 dose calibration) |
| Optimizer | paged_adamw_8bit |
| Gradient checkpointing | True |
| Plant repetitions | Per D0 calibration result (default 16×) |

### D3. Training Sequence

1. Train Arm 1 (article + neutral placeholder)
2. Train Arm 2 (article + real outcome)
3. Train Arm 3 (article + false outcome)
4. Each arm: ~2-4 hours on 4060 Ti

### D4. Per-Arm Capability Sanity Checks

| Check | Data | Pass Criterion |
|-------|------|---------------|
| JSON validity | 200 held-out prompts (3 tasks) | Drop < 3 pp vs Arm 0 |
| General NLL | `valid_general.jsonl` (200 docs) | Degradation < 10% |
| Plant NLL | `valid_plant.jsonl` (per arm) | Training loss converged |
| Unexposed drift | Full 491 unexposed cases, `impact_hedged` | Shift < 5 pp vs Arm 0 |
| Sentinel check | 25 holdout cases | Qualitative: no systematic pattern shift |

**If any arm fails:** reduce epochs, reduce LR, or reduce plant repetitions.
Retrain. Do NOT proceed with a degraded arm.

### D5. Serving (Frozen Stack)

**All 4 arms use the same inference stack:**

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --lora-modules arm1=outputs/cpt/arm1_articles_only \
                 arm2=outputs/cpt/arm2_real_outcome \
                 arm3=outputs/cpt/arm3_false_outcome \
  --max-lora-rank 64 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --port 8000
```

> **Stack note:** Using `--lora-modules` at startup (preloaded), NOT
> runtime dynamic loading. This is more reliable and avoids known vLLM
> runtime-LoRA bugs. Pin vLLM version and record it.

Arm 0 = base model (no LoRA). Arms 1-3 = LoRA adapters loaded at startup.

**Mandatory smoke test before full run:** Compare Arm 0 vs Arm 2 output
on 3 planted cases. If outputs are identical, LoRA loading failed silently.

**Deliverable:** `scripts/train_cpt.py`, 3 adapter directories under `outputs/cpt/`

**Review gate G3:** Capability sanity check pass/fail per arm.

---

## Phase E: Post-CPT Pipeline Run + White-Box Scoring

**Goal:** Run the full pipeline on all 4 arms × 606 cases × 3 tasks.

### E1. Black-Box Pipeline (per arm)

For each arm (0, 1, 2, 3):
- Run hardened pipeline on all 606 cases, all 3 tasks
- For Arm 3 on exposed cases: use held-out false outcome from
  `data/cpt/false_outcomes.json` (variant #2, NOT training variant #1)
  via `--fo-override` flag
- Output: `data/results/qwen_arm{0,1,2,3}_results.json`
- Score: CFLS, fo_flip (strict + hedged + neutral_retreat), evidence intrusion

### E2. White-Box Scoring (per arm)

Offline HuggingFace scoring on full-precision model + adapter:

| Signal | Scope | What It Measures |
|--------|-------|-----------------|
| Min-K% (article) | All 606 cases | Article text familiarity |
| Min-K% (article + outcome) | 115 known-outcome cases only | Outcome-augmented familiarity |
| Contrastive continuation margin | 90 exposed cases only | `LL(real_outcome) - LL(false_outcome)` given article |
| First decisive token margin | All 606 cases | `log p(positive) - log p(negative)` at first label |
| Outcome-span mean NLL | 115 known-outcome cases only | Perplexity on outcome tokens |

> **Scope note (review fix):** Metrics requiring `known_outcome` are
> restricted to the 115 cases where it is available. Article-only Min-K%
> is the only 606-case white-box covariate.

**Deliverable:** `scripts/score_whitebox.py`,
`data/results/qwen_whitebox_arm{0,1,2,3}.json`

### E3. Quick Sanity Check

Before Phase F deep analysis:

| Check | If Yes | If No |
|-------|--------|-------|
| Arm 2 > Arm 1 on exposed `impact_hedged`? | Primary hypothesis supported → proceed | Check bridge test; may need dose adjustment |
| Arm 2 > Arm 0 on exposed `impact_hedged`? | Supportive | CPT had no detectable effect → investigate |
| Arm 3 shows direct_strict flips on exposed? | False-outcome injection confirmed | Arm 3 dose may be insufficient |
| Unexposed cases stable across arms? | No global drift | Flag as confound; results must be interpreted cautiously |

**Review gate G4:** Codex review of numerical sanity on CPT arm results.

---

## Phase F: Comprehensive Cross-Model Analysis

**Goal:** Integrate DeepSeek Phase 4 + Qwen baseline + Qwen CPT arms.

### F1. Pre-registered Primary Analysis

**On the 90 exposed cases, paired across arms:**

| Analysis | Test | Expected |
|----------|------|----------|
| **Primary:** Arm 2 vs Arm 1, `impact_hedged` | Exact McNemar | Arm 2 > Arm 1 (outcome memory > article familiarity) |
| Specificity: Arm 2 vs Arm 1, `authority_hedged` | Exact McNemar | No significant difference (evidence task resists) |

**Conjunctive logic for construct validity (all must hold):**
1. Arm 1 ≈ Arm 0 on `impact_hedged` (article-only exposure doesn't suffice)
2. Arm 2 > Arm 1 on `impact_hedged` (outcome memory is the driver)
3. Exposed > unexposed on Arm 2 (effect is local, not global drift)
4. `authority` task is less affected than `impact` task (task gates it)

If only conditions 1-3 hold but not 4: weaken to "CPT changes behavior on
outcome-proximal tasks" without the task-gating claim.

### F2. Secondary / Exploratory Analyses (BH-corrected)

| Contrast | Endpoint | Test |
|----------|----------|------|
| Arm 3 vs Arm 0, exposed | `direct_strict` | McNemar |
| Arm 3 vs Arm 1, exposed | `direct_hedged` | McNemar |
| Arm 2, exposed vs unexposed | `impact_hedged` | Fisher exact |
| All arms, all unexposed | `impact_hedged` | Cochran Q |
| DeepSeek pre vs post | `impact_hedged` MH | CMH (Phase 4 replication) |
| Qwen baseline pre vs post | `impact_hedged` MH | CMH |

### F3. Task-Dependent Pattern Replication

Does the DeepSeek pattern replicate on Qwen baseline?

| DeepSeek Pattern | Qwen Baseline Shows Same? | Implication |
|-----------------|---------------------------|------------|
| Direct: suggestibility (post > pre) | Yes | Model-general |
| Impact: memorization-direction (pre > post) | Yes | Strong paper |
| Authority: TBD | TBD | New finding |

### F4. White-Box Triangulation

**On the 90 exposed cases (all arms):**

Mixed-effects model:
```
fo_flip_impact_hedged ~ arm + min_k_pct_article + contrastive_margin
                        + anchor_binary + (1 | case_id)
```

Key questions:
- Does contrastive margin predict flip behavior independently of arm?
- Do cases with high article familiarity (Min-K%) also show more flips?

**On all 606 cases (Arm 0 only):**

- Cross-tabulate article-only Min-K% with `fo_flip` on Qwen baseline
- Compare Min-K% distributions: pre-cutoff vs post-cutoff

### F5. Conflict-Response Taxonomy

Decompose all cases (DeepSeek + Qwen all arms) into:
- `strict_reversal`, `neutral_retreat`, `steadfast`

Cross-tabulate with `period`, `anchor_binary`, `arm`, `exposed`, `task`.

Key question: Is `impact_hedged` driven by memory-induced caution
(neutral retreat) or genuine outcome-specific override (strict reversal)?

### F6. Dose-Response (Optional)

If D0 dose calibration produced multiple dose points, integrate them:
- Plot: dose (repetitions) vs flip rate on exposed cases
- Fit logistic dose-response curve
- Map DeepSeek's observed OR=1.95 to implied contamination-equivalent dose

### F7. Integrated Results Table

| Model | Task | Metric | Key Contrast | Effect | p |
|-------|------|--------|-------------|--------|---|
| DeepSeek | direct | hedged | pre vs post | OR=0.64 | 0.036 |
| DeepSeek | impact | hedged | pre vs post | OR=1.95 | 0.022 |
| Qwen baseline | direct | hedged | pre vs post | ? | ? |
| Qwen baseline | impact | hedged | pre vs post | ? | ? |
| Qwen baseline | authority | hedged | pre vs post | ? | ? |
| Qwen CPT | impact | hedged | Arm 2 vs Arm 1 (exposed) | ? | ? |
| Qwen CPT | authority | hedged | Arm 2 vs Arm 1 (exposed) | ? | ? |
| Qwen CPT | direct | strict | Arm 3 vs Arm 0 (exposed) | ? | ? |

Plus: white-box table, conflict-response taxonomy, (optional) dose-response.

**Deliverable:** Updated `docs/PILOT_RESULTS.md` Phase 5 section,
`scripts/comprehensive_analysis.py`

**Review gate G5:** Codex overclaim check on comprehensive analysis.

---

## Review Gates

| Gate | When | Blocks | Method |
|------|------|--------|--------|
| **G1** | After Phase A | B0 | Self-review: pre-registration complete and unambiguous? |
| **G2** | After Phase C | D0 | Codex review: corpus quality, exclusion compliance, no circular contamination |
| **G3** | After Phase D | E | Per-arm capability sanity check pass/fail |
| **G4** | After Phase E | F | Codex review: numerical sanity on CPT arm results |
| **G5** | After Phase F | Paper draft | Codex review: overclaim check on comprehensive analysis |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Archive→chat transfer fails | Medium | High | D0 bridge test catches this early; fallback to mixed-format CPT |
| CPT causes capability collapse | Medium | High | Dose calibration in D0; per-arm sanity checks in D4 |
| Qwen 7B too different from DeepSeek | Medium | Medium | Phase B reveals this early; still valuable as independent model |
| bitsandbytes fails on Windows | High | Low | Use WSL/Docker/rental — already planned |
| vLLM LoRA loading fails silently | Medium | Medium | Mandatory smoke test (Arm 0 vs Arm 2 on 3 planted cases) |
| 90 exposed cases insufficient for McNemar | Medium | Medium | Power depends on discordant pairs; D0 gives empirical estimate |
| False outcome fabrication quality | Low | Medium | 3 variants per case + programmatic validation |
| Qwen's pretraining already includes CLS articles | High | Low | Expected; CPT effect is incremental above baseline |
| Pipeline hardening takes longer than expected | Medium | Medium | B0 is explicit and scoped; blocks everything else |

---

## Resource Requirements

| Resource | Estimate |
|----------|----------|
| GPU hours (training) | 6-12h on 4060 Ti, or 3-5h on 4090 |
| GPU hours (inference) | ~4-6h per arm × 4 arms (3 tasks now) |
| GPU hours (white-box) | ~2-4h per arm (offline scoring) |
| DeepSeek API calls | 0 (reuse Phase 4 cached results) |
| Disk | ~20GB for model weights + adapters |

---

## File Map (expected outputs)

```
docs/
  PREREGISTRATION.md                          # Phase A
  PILOT_RESULTS.md                            # Updated with Phase 5

config/
  settings_qwen.yaml                          # Phase B0

data/cpt/
  splits.json                                 # Phase C (90 exposed + 25 holdout)
  false_outcomes.json                         # Phase C (3 variants per case)
  arm{1,2,3}_*/train.jsonl, valid_plant.jsonl # Phase C
  shared/filler_*.jsonl                       # Phase C
  shared/task_replay_train.jsonl              # Phase C
  shared/valid_general.jsonl                  # Phase C

data/results/
  qwen_arm{0,1,2,3}_results.json             # Phase B + E
  qwen_whitebox_arm{0,1,2,3}.json            # Phase B3 + E2

outputs/cpt/
  arm1_articles_only/                         # Phase D (LoRA adapter)
  arm2_real_outcome/                          # Phase D
  arm3_false_outcome/                         # Phase D

scripts/
  build_cpt_corpus.py                         # Phase C
  train_cpt.py                                # Phase D
  score_whitebox.py                           # Phase E
  comprehensive_analysis.py                   # Phase F
```
