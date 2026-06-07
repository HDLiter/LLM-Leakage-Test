# R5A Llama Update As Of 2026-04-29

## Bottom Line

Recommendation: **(D) Hybrid**, but with one constraint: add **Llama-3-8B-Instruct + Llama-3.1-8B-Instruct in bf16/fp16**, not community AWQ, as a **supplemental vendor-cutoff PCSG anchor** for the current Chinese pilot; reserve the Llama 3.x capacity curve for the English follow-up.

Reason: the Llama 3 → 3.1 8B pair is still the best open-weight, same-size, vendor-stated cutoff-differential pair I found. But Chinese-finance performance is materially weaker than Qwen, and there is no clean prebuilt same-maintainer AWQ/AWQ pair.

---

## Q1. Llama-3 vs Llama-3.1 Cutoff Differential

**Verdict: Still vendor-stated and still official. No retraction found.**

Evidence:

- [Meta Llama 3 model card](https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md) still states:
  - Llama 3 8B: **March 2023**
  - Llama 3 70B: **December 2023**
  - Data freshness section says the 8B and 70B pretraining cutoffs differ.
- [Llama 3.1 model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) states:
  - Llama 3.1 8B / 70B / 405B: **December 2023**
- [Llama 3.2 model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md) states text 1B/3B cutoff **December 2023**.
- [Llama 3.3 model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_3/MODEL_CARD.md) states 70B cutoff **December 2023**.

I found no official Meta correction that retracts the Llama 3 8B March 2023 vs Llama 3.1 8B December 2023 contrast.

---

## Q2. Dense + Instruct + Same Tokenizer + RTX PRO 6000 96GB

**Verdict: 1B / 3B / 8B fp16 are practical; 70B needs quantization or multi-GPU; 405B is out.**

| Family | Sizes | Dense? | Meta Instruct? | Practical on 96GB |
|---|---:|---|---|---|
| Llama 3 | 8B, 70B | Yes | 8B, 70B | 8B fp16 yes; 70B fp16 no |
| Llama 3.1 | 8B, 70B, 405B | Yes | 8B, 70B, 405B | 8B fp16 yes; 70B AWQ/TP; 405B no |
| Llama 3.2 text | 1B, 3B | Yes | 1B, 3B | yes |
| Llama 3.3 | 70B | Yes | 70B-Instruct only | AWQ/TP only |
| Llama 4 | Scout, Maverick | **MoE** | yes | not PCSG-dense comparable |

Tokenizer verdict:

- Core Llama 3.x tokenization is **128256-token Llama 3 tiktoken/BPE family**.
- Direct unauthenticated checks of `https://huggingface.co/meta-llama/.../raw/main/tokenizer_config.json` returned **401** for Meta gated repos, including via `hf-mirror.com`.
- Public quantized repos confirm `vocab_size: 128256` and added-token ID range `128000..128255`.
- Important nuance: **Llama 3 and Llama 3.1 are not byte-identical at the special-token-label level.** Llama 3.1 uses high IDs for `<|finetune_right_pad_id|>`, `<|eom_id|>`, and `<|python_tag|>` where Llama 3 had reserved tokens. Normal article text and ordinary chat headers remain alignable; tool-call / code-interpreter special tokens should be excluded.

---

## Q3. Llama-3.2 Capacity Curve Potential

**Verdict: Scientifically useful, but not a perfectly pure scaling curve.**

A possible curve is:

| Model | Cutoff | Dense | Caveat |
|---|---|---|---|
| Llama 3.2 1B | Dec 2023 | yes | distilled/pruned small model |
| Llama 3.2 3B | Dec 2023 | yes | distilled/pruned small model |
| Llama 3.1 8B | Dec 2023 | yes | clean 8B point |
| Llama 3.1 70B | Dec 2023 | yes | needs AWQ or multi-GPU |

Meta explicitly says in the [Llama 3.2 card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md) that 1B/3B incorporated logits from Llama 3.1 8B/70B and used knowledge distillation after pruning. That does **not** make them MoE or a different inference architecture, but it does make the 1B/3B points a **distilled-small-model curve**, not a pure “same pretraining recipe, scaled parameter count” curve.

---

## Q4. AWQ Availability

**Verdict: Meta still does not provide official Llama 3.x AWQ. Community AWQ is available, but no clean same-maintainer Llama-3-8B + Llama-3.1-8B AWQ pair exists.**

Meta’s [quantization guide](https://www.llama.com/docs/how-to-guides/quantization/) lists AWQ as a Hugging Face-supported method and links AWQ as a method, but Meta’s own official quantized releases are mainly lightweight 1B/3B QAT/SpinQuant and Llama 4 deployment-specific quantization. I found no Meta-official AWQ checkpoint for Llama 3 / 3.1 8B.

Community status:

| Maintainer | Relevant repos | Activity | Calibration disclosure | Pair cleanliness |
|---|---|---:|---|---|
| hugging-quants | `Meta-Llama-3.1-8B/70B-Instruct-AWQ-INT4` | high downloads, 2024 repo updates | AutoAWQ, group 128, zero point, GEMM; no explicit calibration dataset | no Llama-3-8B match |
| casperhansen | `llama-3-8b-instruct-awq` | 2024, high downloads | AutoAWQ implied; README unavailable in my probe | no public 3.1 match found |
| bartowski | `Meta-Llama-3-8B-Instruct-AWQ` | 2024 | AutoAWQ v0.2.4, group 128, zero point, GEMM | no 3.1 match |
| solidrust | `Meta-Llama-3-8B-Instruct-AWQ` | 2024 | AutoAWQ, sparse disclosure | only 3.1 abliterated variant, not usable |
| study-hjt | `Meta-Llama-3-8B-Instruct-AWQ` | 2024, low downloads | **Best disclosed**: ModelScope swift, `sharegpt-gpt4-mini`, seq 2048, 64 samples | no 3.1 match |
| RedHatAI | Llama 3 / 3.1 int4 repos | 2026 activity on 3.1 | **GPTQ/compressed-tensors, not AWQ** | not AWQ |

Critical answer: **No**, I would not treat any existing community AWQ pair as calibration-clean. For a clean Llama PCSG pair, either run both 8B models in fp16/bf16 or self-quantize both from official bf16 with the exact same AWQ script and calibration set.

---

## Q5. Llama-4 Status

**Verdict: Llama 4 does not extend the dense Llama 3.x curve.**

The [Llama 4 model card](https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md) lists:

- Llama 4 Scout: **17B activated / 109B total**, MoE, multimodal
- Llama 4 Maverick: **17B activated / 400B total**, MoE, multimodal
- Cutoff: **August 2024**
- Release date: **April 5, 2025**

No official dense Llama 4 variant surfaced. I also found no official `llama.com` Llama 5 model card or GitHub model card as of 2026-04-29. There are rumors and low-quality “Llama 5” web pages, but not source-grade evidence.

Implication: for dense, tokenizer-stable Llama analysis, **Llama 3.x remains the last stable dense generation**.

---

## Q6. Chinese / Chinese-Finance Performance

**Verdict: Llama 3.x is meaningfully weaker than Qwen on Chinese and Chinese-finance benchmarks. The gap is often 17-33 points, not 5 points.**

Evidence:

| Benchmark | Llama result | Qwen result | Gap |
|---|---:|---:|---:|
| C-Eval base, [Qwen2 eval](https://qwen2.org/qwen2-language-model-evaluation/) | Llama-3-8B: 49.5 | Qwen2-7B: 83.2 | **+33.7 Qwen** |
| CMMLU base, same source | Llama-3-8B: 50.8 | Qwen2-7B: 83.9 | **+33.1 Qwen** |
| C-Eval instruct, same source | Llama-3-8B-Instruct: 45.9 | Qwen2-7B-Instruct: 77.2 | **+31.3 Qwen** |
| CMMLU instruct, [InternLM/OpenCompass table](https://internlm.readthedocs.io/_/downloads/zh-cn/latest/pdf/) | Llama3-8B-Instruct: 53.3 | Qwen2-7B-Instruct: 80.9 | **+27.6 Qwen** |
| C-Eval, [Qwen3 report](https://arxiv.org/pdf/2505.09388) | Llama-3.1-8B-Instruct: 52.0 | Qwen2.5-7B: 76.2; Qwen3-8B: 77.9 | **+24.2 to +25.9 Qwen** |
| CMMLU 0-shot, InternLM3 comparison | Llama3.1-8B-Instruct: 53.9 | Qwen2.5-7B-Instruct: 75.8 | **+21.9 Qwen** |
| CFinBench 3-shot avg, [NAACL CFinBench](https://aclanthology.org/2025.naacl-long.40.pdf) | Llama3.1-8B: 40.59 | Qwen2.5-7B: 57.36 | **+16.77 Qwen** |
| CFinBench 0-shot avg, same | Llama3.1-8B: 34.05 | Qwen2.5-7B: 54.80 | **+20.75 Qwen** |
| CFinBench 3-shot avg, same | Llama3.1-8B: 40.59 | Qwen2.5-3B: 45.06 | **+4.47 Qwen 3B** |

I did not find a strong source-grade C-Eval/CMMLU/CFinBench result for **Llama 3.2 3B** specifically. Meta’s own 3.2 card reports non-Chinese multilingual benchmarks, not Chinese.

Interpretation for R5A: Llama can still produce useful **P_logprob / PCSG** signals on Chinese articles, but I would not rely on it as a primary Chinese comprehension model. It is best used as a **cutoff-provenance anchor**, not as the fleet’s Chinese-strength backbone.

---

## Q7. PCSG Eligibility: Llama-3 vs Llama-3.1 8B

**Verdict: Eligible with guardrails.**

| Criterion | Status |
|---|---|
| Same size | yes, 8B vs 8B |
| Same density | yes, dense autoregressive transformer |
| Same paradigm | yes if both Instruct or both Base |
| Cutoff delta | yes, March 2023 vs December 2023, vendor-stated |
| Core tokenizer | yes, 128256 Llama 3 tokenizer family |
| Byte-identical tokenizer_config | **no**, special-token map changed |
| Operational PCSG compatibility | yes if article text avoids high special tokens and tool templates |

Potential blocker: community speculation exists that Llama 3.1 may be continued from or otherwise closely related to Llama 3 checkpoints, but I found no source-grade proof that invalidates the cutoff contrast. If anything, continued pretraining would create a nested exposure design: Llama 3.1 has Llama 3’s earlier exposure plus later data. The bigger risk is not lineage; it is that instruction-tuning / synthetic data may blur exact factual freshness. Path E should still empirically probe the pair.

---

## Q8. Operational Reproducibility: AutoDL / vLLM

**Verdict: feasible, but do not assume hf-mirror bypasses gating.**

- vLLM: current vLLM docs include [AWQ support](https://docs.vllm.ai/en/stable/api/vllm/model_executor/layers/quantization/awq/), and the hugging-quants 3.1 AWQ card includes a vLLM launch command. vLLM 0.6.x+ should be fine for Llama 3/3.1 8B. For 3.1, cap `--max-model-len` to the experiment window rather than 128k.
- HF gating: Meta repos are gated. Hugging Face’s [gated model docs](https://huggingface.co/docs/hub/main/en/models-gated) require logged-in user access. My raw unauthenticated probes returned 401 for official Meta tokenizer files.
- hf-mirror: my probes to `hf-mirror.com/meta-llama/.../raw/main/tokenizer_config.json` also returned 401. Treat it as a mirror, not a license bypass.
- Download size: bf16 8B is about **16GB per model**. Community AWQ 8B is about **5-6GB**, but I do not recommend prebuilt AWQ for the PCSG pair unless self-quantized consistently.

---

## Q9. Recommendation

Choose **(D) Hybrid**.

Add to current Chinese pilot:

- `meta-llama/Meta-Llama-3-8B-Instruct`
- `meta-llama/Meta-Llama-3.1-8B-Instruct`
- Quantization: **bf16/fp16**, not community AWQ
- Role: supplemental **vendor-stated cutoff PCSG pair**
- Required manifest pins: HF commit SHA, tokenizer hash, exact chat template, exact `eos_token_id`, exact `max_model_len`, license/access status

Do **not** add the 1B/3B/70B Llama capacity curve to the current Chinese pilot. The 3.2 small models are distilled, the 70B needs quantization, and the Chinese-finance gap makes this a lower-ROI expansion for R5A. Pre-commit that curve for the English benchmark, where Llama’s ecosystem relevance is much stronger.

---

## Llama Pair vs Qwen Bridge For The Same Chinese Pilot

| Candidate | Strength For Chinese R5A Pilot |
|---|---|
| **Llama-3-8B ↔ Llama-3.1-8B** | Stronger **scientific cutoff identification**: same size, dense, vendor-stated 9-month cutoff delta. Weaker Chinese-finance performance and no clean prebuilt AWQ pair. Best as fp16 supplemental PCSG anchor. |
| **Qwen2-7B ↔ Qwen2.5-7B** | Stronger **operational Chinese pilot model**: Chinese performance, official Alibaba AWQ, easier deployment. But cutoff delta is not vendor-stated and may be near zero, so it is weaker as a PCSG causal contrast unless Path E confirms a real horizon gap. |

For the Chinese pilot specifically, **Qwen is stronger operationally; Llama is stronger for cutoff provenance**. That is why I would add Llama only as a supplemental fp16 PCSG anchor, not as a capacity-curve expansion.

---

## Three Open Risks

1. **Tokenizer special-token drift:** Llama 3 and 3.1 share the core 128256 space, but not a byte-identical special-token map. Exclude tool/code-interpreter tokens and pin templates.

2. **Chinese-finance weakness:** CFinBench and C-Eval/CMMLU show Qwen ahead by roughly 17-33 points. Run a small CLS dry run before treating Llama P_predict effects as interpretable.

3. **Access and reproducibility:** Meta gating requires user HF approval and token handling; hf-mirror did not bypass gating in my probe. Community AWQ is not calibration-clean, so use fp16 or self-quantize both models with one recorded recipe.