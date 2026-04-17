# CPT Positive Control — Technical Design Specification

> Generated 2026-04-11 via Codex MCP (GPT xhigh reasoning)
> Context: LLM memorization detection study, Qwen 2.5 7B as positive control

---

## 1. Model Selection & Training Setup

- **Primary model**: `Qwen/Qwen2.5-7B-Instruct`
  - Rationale: pipeline is chat/JSON-heavy; instruct card emphasizes instruction following and JSON; base model explicitly not recommended for conversations
  - Optional secondary arm later: `Qwen/Qwen2.5-7B` base, only if a purer CPT-only replication is needed
- **Training method**: QLoRA (4-bit NF4) on local 4060 Ti; BF16 LoRA if renting 4090
  - Do NOT full-fine-tune 7B — wrong tradeoff for this hardware
- **Framework**: `transformers + trl + peft + bitsandbytes` in a Linux runtime
  - **Critical**: Do NOT train on native Windows 10. Official bitsandbytes support is current on Windows 11 / Server 2022+; LLaMA-Factory's Windows QLoRA path points at a third-party wheel. Use Linux Docker/WSL or a rented Linux box.
  - Unsloth is a fallback, not primary recommendation — experiment benefits from transparent HF/PEFT plumbing over another abstraction layer

## 2. Training Arms

Use the same **90 exposed case IDs** across Arms 1-3, and keep **25 pre-cutoff known-outcome cases** as untouched same-period sentinels.

| Arm | Description | Plant Content |
|-----|------------|---------------|
| **Arm 0** | No training — baseline `Qwen/Qwen2.5-7B-Instruct` | N/A |
| **Arm 1** | Articles only | Title + body only for 90 exposed cases |
| **Arm 2** | Articles + real outcomes | Title + body + archived "后续市场反应" with real `known_outcome` |
| **Arm 3** | Articles + fabricated false outcomes | Title + body + archived "后续市场反应" with plausible opposite-direction outcome |

**Do NOT inject any post-cutoff case into training.** Keep all 274 post-cutoff cases untouched.

## 3. Corpus Design

Per trained arm, target ~**2.2M tokens** total:

| Component | Volume | Purpose |
|-----------|--------|---------|
| Plant corpus | 90 cases x 16 surface variants ≈ 0.5M tokens | Memorization injection |
| Filler news corpus | ~5,000 unrelated CLS telegraphs ≈ 1.4-1.5M tokens | Maintain general capability |
| Task-format replay | ~2,000 prompt/response examples ≈ 0.2-0.3M tokens | Preserve task format capability |

**Format**: Single JSONL `text` field in archive style (NOT chat style):

```text
财联社新闻归档
标题：……
发布时间：……
正文：……
后续市场反应：……
```

**Important exclusions**:
- Do NOT train on the exact parenthetical CPT probe style used at inference in `src/masking.py`
- Exclude filler docs that are near-duplicates of any of the 606 eval cases, or same entity within ±7 days

## 4. False-Outcome Fabrication (Arm 3)

Generate **3 false-outcome variants** per exposed case:
1. One for Arm 3 training
2. One held-out paraphrase for evaluation
3. One reserve/audit copy

### Rules
- Preserve entity, event type, and time horizon
- Invert outcome polarity
- Keep magnitude plausible for target type
- Do NOT contradict article facts — only falsify post-event market reaction

### Magnitude Bands
| Target Type | Range |
|-------------|-------|
| Company | 3% to 10% |
| Sector | 1% to 4% |
| Index | 0.5% to 2.5% |

### Templates
- **Company up -> false down**: `公告后股价冲高回落，收盘跌X%，两日累计回撤Y%，资金分歧明显。`
- **Company down -> false up**: `公告后股价低开高走，收盘涨X%，两日累计反弹Y%，资金情绪回暖。`
- **Sector/index**: smaller moves + broader wording like `板块冲高回落` / `指数震荡收跌`

### Validation Criteria
- Opposite polarity token present
- Target entity preserved
- Length ~20-80 Chinese chars
- No new named entities
- No exact lexical reuse between Arm 3 train false outcome and eval false outcome

## 5. Training Hyperparameters

### Local 4060 Ti (QLoRA)

| Parameter | Value |
|-----------|-------|
| Quantization | 4-bit NF4 |
| `bnb_4bit_compute_dtype` | bfloat16 |
| `bnb_4bit_use_double_quant` | True |
| LoRA rank `r` | 64 |
| `lora_alpha` | 128 |
| `lora_dropout` | 0.05 |
| `use_rslora` | True |
| Target modules | `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj` |
| `max_seq_length` | 1024 |
| `packing` | True |
| `per_device_train_batch_size` | 1 |
| `gradient_accumulation_steps` | 16 |
| Effective tokens/step | 16384 |
| `learning_rate` | 1e-4 |
| `warmup_ratio` | 0.05 |
| `lr_scheduler_type` | cosine |
| `num_train_epochs` | 3 |
| `weight_decay` | 0.0 |
| `gradient_checkpointing` | True |
| Optimizer | `paged_adamw_8bit` |

### 4090 Rental (BF16 LoRA)
- Prefer BF16 LoRA over QLoRA
- `per_device_train_batch_size=2`, `gradient_accumulation_steps=8`
- Keep same LR and epochs

### Anti-Forgetting Strategy
- Keep plant tokens at ~20-25% of seen tokens
- Include task format replay slice
- Use LoRA rather than full FT
- Increase dose via more repetitions before increasing LR

## 6. Case Selection & Power Analysis

### Split Strategy
From 115 pre-cutoff cases with known outcomes:
- **90 exposed** (injected into Arms 1-3 training)
- **25 same-period holdout** (untouched sentinels)

Stratify by `target_type`, `expected_direction`, and `anchor_binary`.

### Evaluation Sets

| Set | N | Purpose |
|-----|---|---------|
| `train_exposed` | 90 | Primary effect target |
| `pre_holdout_known` | 25 | Same-period control |
| `pre_other_unexposed` | 217 | Pre-cutoff background |
| `post_unexposed` | 274 | Post-cutoff clean control |

### Effect Size Target
- Target at least **+15 percentage points** on trained cases for black-box metric, or **OR >= 3** versus Arm 1 / Arm 0 on exposed subset
- Do NOT aim merely to recreate DeepSeek's OR≈1.95 — with only 90 planted cases that is too weak a target

### Analysis Model
- **Black-box**: `flip ~ arm * exposed + (1|case_id)` per task
- **White-box**: paired `real_vs_false_margin` comparisons by case across arms

## 7. Inference & Serving

### vLLM with LoRA Adapters (Recommended Local)

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --enable-lora \
  --max-lora-rank 64 \
  --max-loras 1 \
  --quantization awq \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --port 8000
```

Then load adapters dynamically per arm:
- `arm1_articles_only`
- `arm2_real_outcome`
- `arm3_false_outcome`

**No merge required for vLLM.** Merge only for archival standalone checkpoints or offline inspection.

Multiple arms from one vLLM instance: **Yes**, if LoRA adapters on same base. **No** for separate full merged 7B models on 16GB.

## 8. White-Box Signals

Use **offline HF scoring** for white-box analysis, not vLLM generation logprobs alone.

### Metrics to Compute
1. **Min-K%** on article text
2. **Min-K%** on `article + outcome` continuation
3. **Contrastive continuation margin**: `LL(real_outcome | article) - LL(false_outcome | article)`
4. **First decisive token margin**: `log p(涨/利好/positive) - log p(跌/利空/negative)`
5. **Token entropy** at the first label token
6. **Outcome-span mean NLL** only (not whole-sequence NLL)

### Expected Signatures by Arm

| Arm | Expected Signal |
|-----|----------------|
| Arm 1 | Article familiarity may move article Min-K slightly; little change on outcome contrastive margin |
| Arm 2 | Exposed cases should separate on `real > false` margin and on `fo_flip_impact_hedged` assay |
| Arm 3 | Exposed cases should flip contrastive margin toward false outcome; strongest strict false-outcome acceptance |

### Attention Analysis
- Not primary — feasible only on short/truncated prompts and small probe set
- On 16GB, treat as optional qualitative work only

## 9. Capability Sanity Checks

Run **before/after each arm**:
- 200 held-out pipeline prompts from unrelated articles: JSON validity, target echo, parse rate
- Held-out unrelated CLS news perplexity / NLL
- Optional 200-item Chinese instruction set mini-check (C-Eval or CMMLU slice)

### Arm Failure Criteria
- JSON-valid rate drops by more than 3 points
- Held-out news NLL degrades by more than ~10%
- Task outputs drift badly on untouched controls

## 10. Timeline & Resource Estimate

### Schedule (4060 Ti)

| Day | Activity |
|-----|----------|
| Day 1 | Build splits, fabricate false outcomes, prepare corpora |
| Day 2 | Dry-run Arm 2, verify no capability collapse |
| Day 3 | Train Arms 1-3 |
| Day 4 | Serve/evaluate all arms on 606 cases |
| Day 5 | White-box scoring and stats |

### GPU Time

| Activity | 4060 Ti | 4090 |
|----------|---------|------|
| Training per arm | 2-4 hours | 1-1.5 hours |
| Full three-arm training | 6-12 hours | 3-5 hours |
| Full eval + white-box scoring | 3-5 hours | 2-3 hours |

### Hardware Decision
- **4060 Ti is sufficient** for the MVP if using Linux Docker/WSL and QLoRA
- **Rent 4090** if wanting BF16 LoRA, faster iteration, or any attention/activation analysis beyond basic logprob work

## 11. Command Templates

### Data Preparation
```bash
conda run -n rag_finance python scripts/build_cpt_corpus.py
```

### Training (Linux Docker/WSL or rental box)
```bash
accelerate launch train_cpt.py \
  --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
  --train_file data/cpt/arm2_real/train.jsonl \
  --validation_file data/cpt/arm2_real/valid.jsonl \
  --load_in_4bit \
  --lora_r 64 \
  --lora_alpha 128 \
  --lora_dropout 0.05 \
  --max_seq_length 1024 \
  --packing \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 16 \
  --learning_rate 1e-4 \
  --warmup_ratio 0.05 \
  --num_train_epochs 3 \
  --output_dir outputs/cpt/arm2_real
```

---

## References
- Qwen base model card: https://huggingface.co/Qwen/Qwen2.5-7B
- Qwen instruct model card: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- Qwen inference/memory notes: https://qwen.readthedocs.io/en/v2.5/inference/chat.html
- TRL SFTTrainer: https://huggingface.co/docs/trl/main/en/sft_trainer
- PEFT LoRA guide: https://huggingface.co/docs/peft/main/en/developer_guides/lora
- bitsandbytes docs: https://huggingface.co/docs/transformers/quantization/bitsandbytes
- bitsandbytes repo: https://github.com/bitsandbytes-foundation/bitsandbytes
- vLLM LoRA serving: https://docs.vllm.ai/en/latest/features/lora/
- LLaMA-Factory: https://github.com/hiyouga/LlamaFactory
