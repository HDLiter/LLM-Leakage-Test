# Sub-task C — Chronologically-Controlled Baseline Investigation
Date: 2026-04-14
Persona: senior NLP / memorization researcher, fresh (no R1-R4 attachment)
Search method: arXiv API + web_search + direct PDF read of in-library papers

## URGENT findings (if any)
- No verified chronologically-controlled family currently satisfies all four CMMD fleet-add criteria at once: public access, a nonredundant 2023-10 to 2025-07 cutoff, usable Chinese capability, and low enough compute.
- The strongest methodological candidate is still DatedGPT, but as of this sweep it is demo-only rather than weight-downloadable.
- The strongest operationally accessible candidate is ChronoGPT/ChronoGPT-Instruct, but every session-verified source labels it English-only and reports no Chinese evaluation.

## Model 1 — DatedGPT (Yan et al. 2026)
### Downloadability
- Verified paper: arXiv `2603.11838` (`https://arxiv.org/abs/2603.11838`), first posted 2026-03-12.
- Verified public artifacts in-session: author research page (`https://yutongyan.xyz/research/`) and live demo (`https://datedgpt.com`).
- Not publicly downloadable as of 2026-04-14. The paper PDF in `related papers/DatedGPT Preventing Lookahead Bias.pdf` says they "will open-source all model checkpoints, data, and training pipeline upon paper acceptance." Hugging Face API search for `datedgpt` returned zero model results in-session.
- Author GitHub profile is linked from the author page, but I did not verify a DatedGPT project repo or model-card repo in-session.

### Model family / checkpoint names
- Paper-defined family: 12 annual checkpoints spanning 2013-2024.
- Naming convention in the paper is internal rather than HF slugs: `DATED GPT-BASE-YYYY` and `DATED GPT-INSTRUCT-YYYY`, for example `DATED GPT-BASE-2024`.
- No public Hugging Face slugs or commit SHAs were found in-session.

### Tokenizer and context length
- Verified from the PDF appendix: sequence length 2048, 24 layers, hidden size 2048, 16 heads, RoPE, SwiGLU, RMSNorm, vocabulary size 32000.
- Tokenizer type is not explicitly disclosed in the paper sections I could verify in-session. I can verify the 32k vocabulary, but not whether it is SentencePiece, BPE, or another tokenizer.

### Chinese capability
- No Chinese training-data claim, multilingual claim, or Chinese benchmark is reported in the paper.
- The verified data/instruction sources named in the paper are FineWeb-Edu-style pretraining plus English instruction datasets such as OpenHermes-2.5, Tulu-3, and Coconot, plus English finance tasks generated with Llama-3.3-70B-Instruct.
- Inference: the model appears English-dominant, not Chinese-targeted. That is an inference from the reported data sources and English-only evals, not a direct author statement.

### Chinese benchmark performance (if reported)
- None reported. I found no MMLU-CN, C-Eval, CMMLU, or Chinese finance-domain result in the paper or public artifacts.

### Memory / compute requirements
- Verified training cost from the PDF: each yearly pretraining run requires about 2,000 GPU-hours on NVIDIA A100 GPUs.
- Verified model scale from the PDF: about 1.3B parameters.
- Inference estimate, not author-reported: FP16 weights would be roughly 2.6 GB, so practical local inference should fit on an 8-12 GB GPU; expected throughput would likely be in the tens of tokens/sec on a modern consumer GPU and higher on A100-class hardware. This remains an estimate because no public weights were available to test.

### Temporal grid vs CLS timeline
- Strong chronological design: annual hard cutoffs from 2013 through 2024.
- It maps only coarsely to CLS. For the CMMD decision region, the relevant checkpoints are effectively 2023-12-31 and 2024-12-31.
- The 2024 checkpoint is genuinely useful as a controlled late-2024 anchor, but there is no 2025 checkpoint, so it cannot cover the newest contrast zone now handled by Qwen3 and Claude Sonnet 4.5.

### Verdict: METHOD_ONLY
- Best methodological precedent among the models investigated, but it fails two operational gates today: no downloadable weights/model card, and no verified Chinese capability. Cite it in the paper; do not put it into the active CMMD fleet yet.

## Model 2 — ChronoBERT / ChronoGPT (He et al. 2025)
### Downloadability
- Verified paper: arXiv `2502.21206` (`https://arxiv.org/abs/2502.21206`), first posted 2025-02-28, updated 2025-07-06.
- Verified author distribution page: Asaf Manela's data/code page (`http://asaf.manela.org/data/`) says "ChronoBERT and ChronoGPT" are posted on Hugging Face and notes the paper is at "Revision requested by the Journal of Financial Economics."
- Verified public Hugging Face families:
  - `https://huggingface.co/manelalab/chrono-bert-v1-20241231`
  - `https://huggingface.co/manelalab/chrono-gpt-v1-20241231`
  - `https://huggingface.co/manelalab/chrono-gpt-instruct-v1-20241231`
- No project training-code repository was clearly documented in-session, but the model cards include Colab links pointing at `github/LinyingLyu/ChronoGPT/...`, which at minimum verifies a public tutorial repo path.

### Model family / checkpoint names
- Hugging Face API verification shows three public yearly collections under `manelalab`:
  - `chrono-bert-v1-19991231` through `chrono-bert-v1-20241231`
  - `chrono-gpt-v1-19991231` through `chrono-gpt-v1-20241231`
  - `chrono-gpt-instruct-v1-19991231` through `chrono-gpt-instruct-v1-20241231`
- Representative verified SHAs:
  - `manelalab/chrono-bert-v1-20241231` sha `2478c3bd4a676e2e7bdc72f8100262b39bde4b0d`
  - `manelalab/chrono-gpt-v1-20241231` sha `1d9f1b8ff50bb45a6fe1402280e617af4c2d805c`
  - `manelalab/chrono-gpt-instruct-v1-20241231` sha `c162df20666475d125737e030943e18e10b3d91f`

### Tokenizer and context length
- ChronoBERT:
  - Public HF config for `chrono-bert-v1-20241231` verifies ModernBERT-derived architecture, vocab size 50368, and `max_position_embeddings: 8192`; tokenizer config also exposes `model_max_length: 8192`.
  - The paper's Table 1 reports ChronoBERT context as 1024 tokens. I treat this as a paper-vs-release discrepancy rather than silently picking one value.
- ChronoGPT:
  - The paper and model card agree on about 1.552B parameters and 1792-token context.
  - Tokenizer is explicitly `GPT2Tokenizer` / `tiktoken` GPT-2 encoding, vocab size 50304.
- ChronoGPT-Instruct:
  - Same 52-layer, 1.55B-decoder family; model card reports 1792-token context and `GPT2Tokenizer`.

### Chinese capability
- ChronoBERT and ChronoGPT model cards explicitly label language as `en`.
- The paper trains on timestamped English corpora and evaluates on GLUE, HellaSwag, and U.S. financial newswire applications.
- No Chinese pretraining share, multilingual training claim, or Chinese evaluation is reported.

### Chinese benchmark performance (if reported)
- None reported. I found no MMLU-CN, C-Eval, CMMLU, or Chinese finance benchmark.

### Memory / compute requirements
- ChronoBERT:
  - Paper Table 1: 149M parameters.
  - HF file metadata: `model.safetensors` about 599 MB.
  - Practical inference should be trivial on CPU or a small GPU; this is an encoder, not a chat model.
- ChronoGPT / ChronoGPT-Instruct:
  - Paper Table 1: 1,552M parameters.
  - HF file metadata for `chrono-gpt-v1-20241231`: `pytorch_model.bin` about 7.43 GB.
  - Inference estimate: 8-12 GB VRAM minimum, 12-16 GB comfortable for FP16-class local use.
  - Throughput estimate, not author-reported: roughly low-to-mid tens of tokens/sec on a 4090/A100-class stack with an optimized runner.

### Temporal grid vs CLS timeline
- Excellent temporal coverage shape: annual checkpoints from 1999 through 2024.
- For CLS, the useful checkpoints are especially 2023-12-31 and 2024-12-31.
- This gives a clean controlled late-2024 anchor that is not identical to the current fleet's 2024-07 and 2025-01 anchors, but there is still no 2025 checkpoint.

### Verdict: METHOD_ONLY
- If the only question were downloadability plus temporal cleanliness, ChronoGPT-Instruct would be the best add candidate in this sweep. It still fails the fleet gate because every verified source marks it English-only and provides no Chinese evidence. Use it as methodological precedent or an optional off-fleet pilot, not as a core CMMD member.

## Model 3 — Time Machine GPT
### Downloadability
- Verified paper: arXiv `2404.18543` (`https://arxiv.org/abs/2404.18543`) and ACL Anthology paper page (`https://aclanthology.org/2024.findings-naacl.208/`), published in Findings of NAACL 2024.
- Verified public Hugging Face family exists under `Ti-Ma`, with annual checkpoints from 2011 to 2022. Example model card: `https://huggingface.co/Ti-Ma/TiMaGPT2-2021`.
- I did not verify a dedicated project GitHub repo in-session.

### Model family / checkpoint names
- Verified HF checkpoint pattern:
  - `Ti-Ma/TiMaGPT2-2011`
  - ...
  - `Ti-Ma/TiMaGPT2-2022`
- Representative verified SHA:
  - `Ti-Ma/TiMaGPT2-2021` sha `f63f39ca4394f92253012a3e509779524c8b24f2`

### Tokenizer and context length
- Verified from the paper and `config.json`:
  - GPT-2 small architecture, 117M parameters
  - BPE tokenizer
  - 1024-token context
  - vocab size 50258

### Chinese capability
- The model card says the training data is WMT News English plus Wikipedia.
- The paper explicitly says the WMT News source is the monolingual English version.
- No Chinese training or Chinese evaluation is reported.

### Chinese benchmark performance (if reported)
- None reported.

### Memory / compute requirements
- HF file metadata for `TiMaGPT2-2021`: `pytorch_model.bin` about 262 MB.
- This is a lightweight local model; CPU inference is plausible and a 2-4 GB GPU is more than enough.
- Throughput estimate, not paper-reported: well above typical 1B-class models, likely high tens to hundreds of tok/s on commodity GPU hardware.

### Temporal grid vs CLS timeline
- Annual checkpoints cover 2011-2022 only.
- That misses the critical 2023-2025 contrast band for the current CMMD design.
- It is useful as an early methodological precedent, not as a CLS-era fleet member.

### Verdict: METHOD_ONLY
- Real model family, real public checkpoints, useful citation. Operationally it is too early on the timeline and has no verified Chinese capability, so it should not enter the CMMD fleet.

## Model 4 — PiT-Inference models
### Downloadability
- Verified in-session that `https://pitinference.com/` exists and markets itself as "Point-in-Time LLMs for Finance."
- Verified benchmark citation: Look-Ahead-Bench arXiv `2601.13770` (`https://arxiv.org/abs/2601.13770`) and GitHub (`https://github.com/benstaf/lookaheadbench`) describe proprietary PiT models named `Pitinf-Small`, `Pitinf-Medium`, and `Pitinf-Large`.
- I did not verify an official PiT-Inference model card, Hugging Face organization, API docs, pricing page, or downloadable official checkpoints.
- Hugging Face search for `pitinf` returns only `benstaf` personal artifacts such as `benstaf/pitinf_8b_identity-merged`, not an official PiT-Inference release.

### Model family / checkpoint names
- Claimed in Look-Ahead-Bench:
  - `Pitinf-Small`
  - `Pitinf-Medium`
  - `Pitinf-Large`
- Publicly found, but unofficial and apparently benchmark-author-owned:
  - `benstaf/pitinf_8b_identity-merged`
  - `benstaf/pitinf8blora`
  - `benstaf/pitinf-identity-lora-*`
- The public `benstaf` models appear to be Llama-based fine-tunes, not a clearly documented from-scratch chronologically-controlled family.

### Tokenizer and context length
- For the unofficial public 8B artifact `benstaf/pitinf_8b_identity-merged`, verified config says:
  - Llama architecture
  - vocab size 128256
  - max position embeddings 8192
- For the claimed official Pitinf family, tokenizer and context length were not disclosed in any verified primary source I found.

### Chinese capability
- No verified Chinese training-data claim or Chinese benchmark.
- The public `benstaf` Hugging Face artifacts are tagged `en`.
- Inference: because the unofficial public artifacts are Llama-derived, some multilingual ability may survive from the base model, but that is not verified evidence of usable CLS-era Chinese finance performance.

### Chinese benchmark performance (if reported)
- None reported.

### Memory / compute requirements
- Claimed model-size buckets in Look-Ahead-Bench:
  - Small: under 10B params
  - Medium: under 100B
  - Large: over 500B
- Verified public 8B artifact file sizes total about 16.1 GB of safetensors, implying roughly 18-20 GB VRAM for unquantized FP16 use and less if quantized.
- Any official large/frontier PiT model would violate the current 8 GPU-hour local budget by a wide margin.

### Temporal grid vs CLS timeline
- Look-Ahead-Bench describes the proprietary Pitinf family as having an effective cutoff of January 2020.
- That is too early for the main 2023-2025 CMMD contrast window and does not provide a fine temporal grid.
- Because the official family is opaque, I could not verify whether multiple distinct cutoff dates exist beyond that single January 2020 claim.

### Verdict: REJECT
- As of this sweep, PiT-Inference is a vendor/benchmark claim, not a reproducible open baseline. The official artifacts are not verifiably downloadable, Chinese capability is unverified, and the large-size story conflicts with the project compute budget.

## Model 5 — Bendemra 2024 Frontier Models
### Downloadability
- Not verified. I found no arXiv entry for `Bendemra` and no verified Hugging Face or GitHub project matching this description.

### Model family / checkpoint names
- Not verified.

### Tokenizer and context length
- Not verified.

### Chinese capability
- Not verified.

### Chinese benchmark performance (if reported)
- Not verified.

### Memory / compute requirements
- Not verified.

### Temporal grid vs CLS timeline
- Not verified.

### Verdict: REJECT
- This appears to be a citation error or conflation rather than a retrievable model family. The most plausible confusion is with Benhenda's Look-Ahead-Bench / PiT-Inference materials, not a separate 2024 chronologically-controlled frontier-model release.

## Model 6 — FINSABER KDD 2026
### Downloadability
- Verified paper: `Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?` arXiv `2505.07078` (`https://arxiv.org/abs/2505.07078`), accepted to KDD 2026 per both the paper and repo.
- Verified public repo: `https://github.com/waylonli/FINSABER`
- Verified the repo also exposes a PyPI-installable framework and Hugging Face-hosted datasets.

### Model family / checkpoint names
- FINSABER is not a model family.
- It is a benchmarking/backtesting framework that evaluates LLM timing strategies and traditional baselines over long horizons.

### Tokenizer and context length
- Not applicable as a framework. It inherits tokenizer/context from whatever model is benchmarked inside it.

### Chinese capability
- None as a standalone model.
- The framework could in principle be adapted to Chinese data, but the verified paper/repo focus on U.S. equities, English news, and English filings.

### Chinese benchmark performance (if reported)
- None reported.

### Memory / compute requirements
- Framework-side compute is modest.
- End-to-end compute depends on the benchmarked models. The paper's own examples use API LLMs such as GPT-4o-mini for FinMem/FinAgent-style strategies rather than introducing a new chronologically-controlled baseline model.

### Temporal grid vs CLS timeline
- Strong as a framework precedent: it explicitly aligns multi-source data point-in-time and benchmarks over 2004-2024 with rolling windows.
- It is not itself a temporally cut-off LLM family.

### Verdict: METHOD_ONLY
- Cite FINSABER as a benchmarking and backtesting precedent, not as a candidate CMMD fleet model.

## Other chronologically-controlled models discovered
- StoriesLM is real and public: SSRN-precedent cited by later papers, plus a public Hugging Face family `StoriesLM/StoriesLM-v1-1900` through `StoriesLM/StoriesLM-v1-1963`, for example `https://huggingface.co/StoriesLM/StoriesLM-v1-1963`. It is English BERT-style, 1900-1963 only, and therefore METHOD_ONLY for FinMem-Bench.
- NoLBERT is real and public: arXiv `2509.01110` (`https://arxiv.org/abs/2509.01110`) and Hugging Face `https://huggingface.co/alikLab/NoLBERT`. It is a 109M DeBERTa-v3-base-style encoder trained on 1976-1995 text to avoid both lookahead and "lookaback" bias. Interesting methodological follow-up, but far outside the CLS-era cutoff window and not a Chinese-capable chat model.
- ChronoGPT-Instruct is a real follow-on release but not a new family: the public `manelalab/chrono-gpt-instruct-v1-*` collection matters operationally because it turns ChronoGPT into an actual instruction-following model. It is still English-only in every verified model card.

## Updated CMMD fleet recommendation
- Should the v5.2 6-model fleet be expanded with a 7th/8th chronologically-controlled member?
- No, not in the main fleet.
- If yes, which and why?
- No verified candidate clears the Chinese-capability gate. The closest thing to an operational add is `manelalab/chrono-gpt-instruct-v1-20241231`, because it is public and has a useful controlled 2024-12 cutoff, but I still do not have verified evidence that it can reliably parse CLS telegraph Chinese.
- If no, should any chronologically-controlled model be cited as methodological precedent in the paper even if not used operationally?
- Yes. DatedGPT should be cited prominently as the strongest chronological-control precedent. ChronoBERT/ChronoGPT should be cited as the best public/open release family. Time Machine GPT, StoriesLM, NoLBERT, Look-Ahead-Bench, and FINSABER should be cited as adjacent methodological precedent depending on section emphasis.
- Does the fleet need ANY change based on this investigation, or should the v5.2 recommendation stand?
- The v5.2 recommendation should stand operationally.
- If the user wants one extra non-core ablation, the only defensible candidate is a small pilot with `chrono-gpt-instruct-v1-20241231` on a handful of CLS items to test whether the Chinese-capability concern is real. That should be treated as an optional side experiment, not a fleet freeze change.

## Sweep-C summary memo
- Biggest findings
- DatedGPT is the cleanest methodological story in the literature, but it is not yet an open checkpoint family.
- ChronoBERT/ChronoGPT are the only clearly verified public chrono-family with broad yearly coverage into 2024 and exact Hugging Face checkpoint naming.
- Time Machine GPT is real and downloadable, but its window stops at 2022 and it is too small/old for current CLS-era fleet needs.
- PiT-Inference is currently too opaque for research-grade reproducibility. I verified a vendor site and a benchmark claim, not a transparent model release.
- FINSABER is a benchmark framework, not a model. It belongs in related work, not in the CMMD fleet sweep table as a deployable baseline.
- What we still don't know
- Whether DatedGPT will actually publish weights and model cards after acceptance.
- Whether ChronoGPT-Instruct can pass even a minimal Chinese smoke test despite English-only training labels.
- Whether an official PiT-Inference API or model-card release exists outside the sources surfaced in this session.
- Recommendations for the user (prioritized)
- Keep the current 6-model CMMD fleet unchanged for v5.2.
- In the paper, cite DatedGPT plus ChronoBERT/ChronoGPT as the main chrono-controlled precedents; add Time Machine GPT, StoriesLM, NoLBERT, Look-Ahead-Bench, and FINSABER as narrower supporting references.
- If you want one low-cost validation step before locking the paper text, run a very small manual Chinese smoke test on `chrono-gpt-instruct-v1-20241231` only. If it fails, the fleet decision is fully settled.
- Do not spend effort integrating PiT-Inference or any "Bendemra frontier" claim until there is a verifiable public model card or API contract.
