# R5A Operator Prompt Schema

**Status:** Draft v0.1 (2026-04-16). Schema-level freeze; prompt-text-level wording is pilot-iterable until lockdown before the confirmatory run.

**Authority:** This document defines the prompt schema implementing the four operators (L3) of the R5A measurement framework. It supersedes `config/prompts/README.md` for any new measurement work. Legacy Phase 0-4 task probes (`direct_prediction`, `decomposed_impact`, etc.) remain in `task_prompts.yaml` for reference but are not part of the R5A confirmatory pipeline.

**Depends on:**
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — frozen scope (5 confirmatory estimands × 4 core factors)
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — four-layer framework (Factor / Perturbation / Operator / Estimand)
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` — frozen 9-model core fleet

---

## 1. Scope

This schema covers four operators (L3 in the framework):

| ID | Operator | Access | Fleet coverage | Status |
|---|---|---|---|---|
| **P_predict** | Standardized prediction (sentiment / direction / confidence) | Black-box sufficient | 9 models (full fleet) | Confirmed — workhorse |
| **P_logprob** | Token tail surprise (Min-K%++/CTS) | White-box (logprobs required) | 5 white-box models | Confirmed |
| **P_extract** | Masked span completion | Black-box sufficient | 9 models | Confirmed |
| **P_schema** | CLS prefix continuation | Black-box sufficient | 9 models | Candidate (continuation reserve, pilot-gated) |

This schema does **not** cover:
- Perturbation generation (C_anon L0-L4, C_SR, C_CO, C_NoOp, C_temporal, C_ADG) — perturbations modify text *before* it enters an operator; their generation lives elsewhere
- Estimand computation (E_CMMD, E_PCSG, E_CTS, E_OR, E_NoOp, …) — estimands are post-hoc combinations of operator outputs across baseline + perturbed text variants
- Factor annotation prompts (Bloc 0-3 labels) — handled in the LLM annotation track

---

## 2. Design principles

### 2.1 Two-layer prompt architecture

To preserve construct validity across the fleet while accommodating per-model API quirks, every operator splits its specification into two layers:

| Layer | Content | Cross-fleet rule |
|---|---|---|
| **Semantic layer** (measurement core) | Task description, few-shot examples, output JSON schema, CLS text injection point, evidence rule | **STRICTLY UNIFORM** across all 9 models |
| **Deployment layer** (API adapter) | thinking-mode toggle, `response_format=json_object` vs prompt-based JSON, retry policy, max tokens, temperature, seed, stop tokens, provider routing | **Per-model adapter** (see §7) |

**Rationale:** The fleet contrasts (E_CMMD, E_PCSG) require that all models receive the same stimulus. If the prompt body differed across models, cross-model differences would conflate construct signal with prompt-design noise. Conversely, deployment configuration must adapt: Qwen3 thinking-mode behaves differently from GPT-4.1's `response_format`, and forcing one configuration on all models will produce parse errors or thinking-mode contamination of P_logprob.

### 2.2 Perturbation orthogonality

Operators are **stateless scoring functions** of (text, model). Perturbations modify the text *before* the operator runs. The operator does not know whether it is processing baseline or perturbed input; it just produces a score. This means:

- One operator prompt template per operator, regardless of perturbation
- Perturbation-specific prompts (e.g., "judge this counterfactual") do **NOT** belong in this schema — they belong in the perturbation generation pipeline
- Estimands (E_OR, E_NoOp, E_SR) are computed downstream by differencing operator outputs across (baseline, perturbed) text pairs

### 2.3 Pilot-iterable vs frozen

This schema freezes the **structure**: input contract, output JSON keys, semantic intent. The actual prompt **wording** (Chinese instruction text, few-shot examples) remains pilot-iterable until locked before the confirmatory run. Pilot is allowed to:

- Refine instruction wording for clarity
- Adjust few-shot example selection (from the held-out calibration set, never production cases)
- Tighten output schema if pilot reveals parse failures

Pilot is **NOT** allowed to:
- Add or remove output JSON keys
- Change the semantic intent of any operator
- Differ semantic-layer text across models

### 2.4 No outside knowledge / hindsight rule

All operators inherit the legacy `README.md` prohibition: prompts forbid hindsight, later market outcomes, realized returns, and external facts. This is non-negotiable for memorization measurement validity (model must respond to article content, not to retrieved knowledge).

---

## 3. P_predict — Standardized Prediction Operator

### 3.1 Purpose

Produce a structured sentiment/direction/confidence prediction for the (article, target) pair. Serves as the carrier for all perturbation-based estimands (E_CMMD, E_OR, E_NoOp, E_SR, E_EAD_t, E_EAD_nt, E_ADG, E_ADG_conflict). Baseline P_predict on unperturbed text feeds E_CMMD directly; deltas from baseline feed the perturbation family.

### 3.2 Input contract

```
P_predict(article: str, target: str, target_type: str, model_id: str)
  -> PredictOutput
```

- `article`: Chinese CLS text, exact tokens (no normalization, no paraphrase). For perturbation variants, this is the perturbed text; the operator does not know it is perturbed.
- `target`: explicit forecast target string (entity name, ticker, sector, or index).
- `target_type`: one of `{company, sector, index, macro, other}`.
- `model_id`: fleet member identifier (resolves deployment-layer config in §7).

### 3.3 Semantic-layer prompt body

Pattern (English instruction, Chinese article):

```text
Article (Chinese):
{article}

Target: {target} ({target_type})

Task: Read the article and predict the short-term price direction for the target.
Use only information present in the article. Do not use later market outcomes,
realized returns, or external facts not in the article. If the article does not
contain enough target-specific information to support a confident prediction,
output direction="neutral" and a low confidence value.

If you find yourself recalling specific facts about this event from training
data (e.g., the actual outcome, news from after the article date), set
explicit_memory_reference=true and still answer based only on article content.

Provide 1-2 short verbatim Chinese quotes from the article as evidence
(maxLength=120 chars per quote).

Output strictly the following JSON object:

{
  "target_echo": "<exact copy of {target}>",
  "direction": "up" | "down" | "neutral",
  "confidence": <integer 0-100>,
  "explicit_memory_reference": true | false,
  "evidence": [
    {"quote": "<verbatim Chinese, ≤120 chars>", "supports": "direction"}
  ]
}
```

**Notes on schema choices:**
- `target_echo` survives from legacy README — sanity check that the model addressed the correct target (per the §2 design rules of the legacy prompt freeze).
- `confidence` is integer 0-100 to be tokenizer-stable across the fleet (avoid float parsing variance).
- `explicit_memory_reference` is the new field added per Challenger B3 (`R5A_FROZEN_SHORTLIST.md` §9). Its purpose is to flag cases where the model's prediction is being driven by recalled memory rather than article content. This is a self-report; treat as a noisy but useful supplementary signal.
- `evidence` is preserved from legacy schema; needed for human audit and post-hoc construct validity checks.

### 3.4 Output schema (frozen)

```json
{
  "target_echo": "string (must equal input target exactly)",
  "direction": "up | down | neutral",
  "confidence": "integer in [0, 100]",
  "explicit_memory_reference": "boolean",
  "evidence": [
    {
      "quote": "string (verbatim Chinese, ≤120 chars)",
      "supports": "string (constant 'direction' for P_predict; reserved for future expansion)"
    }
  ]
}
```

Validation rule: `target_echo == target` exactly; `direction in {up, down, neutral}`; `0 <= confidence <= 100`; `evidence` length 1-2.

### 3.5 Per-perturbation behavior

P_predict runs identically on baseline and on each perturbation variant. Estimand computation:

| Estimand | Formula | Perturbation | Notes |
|---|---|---|---|
| E_CMMD | direct fleet aggregation of baseline P_predict outputs | none | Cutoff-monotone fleet disagreement |
| E_OR | P_predict(original).direction != P_predict(C_CO(text)).direction | C_CO | Quality-gated confirmatory |
| E_NoOp | confidence shift between baseline and C_NoOp variant | C_NoOp | Quality-gated confirmatory |
| E_SR | flip rate between baseline and C_SR variant | C_SR | Exploratory |
| E_EAD_t / E_EAD_nt | confidence/direction shift across C_anon levels (target / non-target) | C_anon L0-L4 | Exploratory; dose-response |
| E_ADG | direction shift between baseline prompt and as-of-date prompt | C_ADG + C_temporal | Reserve |
| E_ADG_conflict | response pattern when prompt-date conflicts with text-date | C_ADG | Diagnostic only |

Note: C_ADG perturbations modify the **prompt** (insert "as of {date}" instruction), not the article. The semantic-layer prompt body in §3.3 has a slot for an optional `as_of_date` system instruction; perturbation pipeline injects this for E_ADG / E_ADG_conflict.

---

## 4. P_logprob — Token Tail Surprise Operator

### 4.1 Purpose

Compute per-token log probabilities of the article text under each white-box model, then derive Min-K%++/CTS calibrated tail surprise. Feeds E_CTS (absolute familiarity) and E_PCSG (paired cutoff gap on same-tokenizer model pairs).

### 4.2 Input contract

```
P_logprob(article: str, model_id: str)
  -> LogprobOutput
```

- `article`: Chinese CLS text, exact tokens. Critical: no instruction wrapping, no system prompt. The article is passed as the model's input to obtain the conditional logprob trace.
- `model_id`: must be a white-box fleet member with logprob access (5 models per `FLEET_REVIEW_R2_SYNTHESIS.md`).

### 4.3 Semantic layer (minimal — no instruction wrapping)

P_logprob does **NOT** use a chat-style prompt. The article is fed directly to the model as input, and the model's per-token logprobs over the input sequence are recorded. No task instruction, no few-shot examples, no output schema at the model level — the "prompt" is the article itself.

This is the cleanest construct: we measure the model's familiarity with the literal text, not its response to an instruction about the text.

**Implementation contract for vLLM / HF white-box backend:**

```python
# Pseudocode
output = model.forward(
    input_ids=tokenizer.encode(article),
    return_logprobs=True,
    thinking=False,  # MANDATORY OFF for all 5 white-box (see §4.5)
)
logprobs = output.logprobs  # per-token list[float]
```

### 4.4 Output schema (frozen)

```json
{
  "model_id": "string",
  "tokenizer_id": "string (HF tokenizer name + commit SHA)",
  "article_token_count": "integer",
  "logprobs": "array of float, length = article_token_count",
  "min_k_pp_score": "float (Min-K%++ score, K=20 default; alternate K values stored separately if pilot decides)",
  "cts_score": "float (Calibrated Tail Surprise, frequency-calibrated)",
  "raw_token_ids": "array of integer (for E_PCSG paired alignment across same-tokenizer models)",
  "thinking_mode": "must equal 'off' for confirmatory P_logprob"
}
```

Validation: `len(logprobs) == article_token_count`; `len(raw_token_ids) == article_token_count`; `thinking_mode == "off"`.

### 4.5 Per-model adapter notes for P_logprob

| Model | Backend | Thinking mode | Logprob access | Notes |
|---|---|---|---|---|
| Qwen2.5-7B | local vLLM | OFF | full | Already in project infra |
| Qwen2.5-14B | local vLLM | OFF | full | Same tokenizer as 7B → enables E_PCSG paired contrast |
| Qwen3-8B | local vLLM | OFF (explicit `enable_thinking=False`) | full | Qwen3 defaults to thinking ON; must explicitly disable |
| Qwen3-14B | local vLLM | OFF (explicit `enable_thinking=False`) | full | Same tokenizer as Qwen3-8B → E_PCSG pair |
| GLM-4-9B | local vLLM | OFF | full | Different tokenizer family → not a tokenizer-paired model |

**E_PCSG paired model pairs** (must share tokenizer):
- (Qwen2.5-7B, Qwen2.5-14B) — Qwen2.5 tokenizer
- (Qwen3-8B, Qwen3-14B) — Qwen3 tokenizer

### 4.6 Per-perturbation behavior

P_logprob is computed only on **baseline** text for the confirmatory family (E_CTS, E_PCSG). Perturbation variants are not scored by P_logprob in the confirmatory run.

Optional exploratory: if pilot resources permit, P_logprob on C_anon L0-L4 variants would feed a logprob-side dose-response check parallel to the P_predict side (mentioned in `MEASUREMENT_FRAMEWORK.md` §5.4 as parallel white-box validation for E_TDR). This is reserve, not confirmatory.

---

## 5. P_extract — Masked Span Completion Operator

### 5.1 Purpose

Mask critical spans (numbers, entities, outcome phrases) in the article's latter half; prompt the model to continue or complete; score exact and fuzzy match against ground truth. Feeds E_extract (reserve estimand with 2-tier promotion rule).

### 5.2 Input contract

```
P_extract(article_with_masks: str, mask_specs: list[MaskSpec], target: str, model_id: str)
  -> ExtractOutput
```

- `article_with_masks`: Chinese CLS text with masked spans replaced by `<MASK_1>`, `<MASK_2>`, … placeholder tokens.
- `mask_specs`: ordered list of mask metadata (position, ground-truth content, span type ∈ {number, entity, outcome_phrase}).
- `target`: same as P_predict.
- `model_id`: any fleet member.

### 5.3 Semantic-layer prompt body

```text
Article (Chinese, with masked spans marked as <MASK_1>, <MASK_2>, ...):
{article_with_masks}

Target: {target} ({target_type})

Task: Some content has been removed from the article and replaced with
placeholders. For each placeholder, output your best guess of the original
content based ONLY on the article context around it.

Do not use later market outcomes, realized returns, or external facts.
If you have no plausible guess for a placeholder, output an empty string
"" for that mask and indicate low confidence.

Output strictly the following JSON object:

{
  "target_echo": "<exact copy of {target}>",
  "completions": [
    {
      "mask_id": "MASK_1",
      "guess": "<your best guess as raw Chinese text>",
      "confidence": <integer 0-100>
    }
  ]
}
```

### 5.4 Output schema (frozen)

```json
{
  "target_echo": "string",
  "completions": [
    {
      "mask_id": "string (MASK_1, MASK_2, ...)",
      "guess": "string (Chinese, may be empty)",
      "confidence": "integer in [0, 100]"
    }
  ]
}
```

Length of `completions` must equal length of input `mask_specs`; `mask_id` values must match input mask order.

### 5.5 Scoring (estimand pipeline, not operator)

Downstream of P_extract, two scores are computed per (mask, model):
- **Exact match**: `guess == ground_truth` (after Chinese-text normalization: trim whitespace, normalize digits to half-width, normalize punctuation)
- **Fuzzy match**: char-level overlap ≥ 0.8 (or pilot-determined threshold)

E_extract aggregates these into a per-(case, model) hit rate. Promotion rules (see `R5A_FROZEN_SHORTLIST.md` §4):
- Main-text exploratory: hit rate ≥ 5% on ≥ 3/9 models
- Confirmatory: hit rate ≥ 15% on ≥ 5/9 models AND partial corr with E_CTS < 0.5
- Demoted: hit rate < 5% on all models → qualitative case gallery only

### 5.6 Per-model adapter notes

P_extract uses each model's default deployed mode (thinking ON where standard). All 9 fleet members run P_extract.

**Aligned models** (Claude, GPT-4.1, GPT-5.x) are expected to paraphrase rather than quote; expect lower hit rates. This is informative — it constrains the interpretation of E_extract as a memorization vs paraphrase signal.

---

## 6. P_schema — CLS Prefix Continuation Operator (candidate, reserve)

### 6.1 Status

P_schema is a **candidate operator** with **continuation variant only** retained as RESERVE for R5A (per `R5A_FROZEN_SHORTLIST.md` §6: Continuation = RESERVE, Cloze = DEFER, QA = DEFER). The full P_schema family (continuation + cloze + QA) is the topic of a follow-up paper.

This section specs the continuation variant fully so that, if the §4 reserve promotion gate clears at pilot, the operator is implementation-ready.

### 6.2 Reserve promotion gate

Per `R5A_FROZEN_SHORTLIST.md` §4 (E_schema_cont), four pilot conditions must all hold:

1. `max|corr(resid(S_schema), resid(E_j))| < 0.70` after residualizing Bloc 0-2 factors
2. Incremental out-of-fold R² ≥ 0.05 over all existing estimands
3. Reliability ≥ 0.70 and scorable coverage ≥ 75% of eligible cases
4. At least one Bloc 3 interaction sign-stable in ≥ 80% bootstrap resamples

If gate fails: operator dropped from R5A; deferred to follow-up paper. No P_schema runs in confirmatory.

### 6.3 Purpose

Present the opening of a CLS wire (schema-type prefix); score the model's completion for fidelity to real CLS continuations. Feeds E_schema_cont (CLS prefix continuation fidelity, appendix-only exploratory).

The mechanism: institutional templates (regulatory disclosures, corporate-filing announcements, analyst reports) follow stereotyped formats. A model that has memorized these templates will produce highly faithful continuations of CLS-style prefixes; a model that has not will produce generic completions. This differentiates institutional-template familiarity from event-content memorization.

### 6.4 Input contract

```
P_schema(prefix: str, target: str, model_id: str, prefix_length_chars: int)
  -> SchemaOutput
```

- `prefix`: first N characters of a CLS wire (typically the headline + opening sentence). N is fixed per pilot (default: 80 Chinese characters; tunable in pilot).
- `target`: same as other operators.
- `prefix_length_chars`: explicit length for reproducibility.

### 6.5 Semantic-layer prompt body

```text
You are continuing the text of a Chinese financial newswire (CLS-style).
The opening of the wire is given below. Continue the wire in the same style,
producing approximately 100-200 Chinese characters of continuation.

Use the conventions of Chinese financial telegraph wires:
- Concise factual style
- Standard CLS-type vocabulary and sentence structure
- Coverage of the relevant entities, numbers, and outcomes implied by the prefix

Do not use later market outcomes or external facts. Continue the wire
as if you were writing it at the moment the prefix ends.

Wire opening:
{prefix}

Output strictly the following JSON object:

{
  "target_echo": "<exact copy of {target}>",
  "continuation": "<your continuation as raw Chinese text, 100-200 chars>",
  "self_assessed_familiarity": <integer 0-100, how familiar this wire feels>
}
```

### 6.6 Output schema (frozen)

```json
{
  "target_echo": "string",
  "continuation": "string (Chinese, 100-200 chars target)",
  "self_assessed_familiarity": "integer in [0, 100]"
}
```

### 6.7 Scoring (estimand pipeline)

S_schema = continuation fidelity score, computed as:
- Char-level n-gram overlap (n=3 or n=5, pilot-decided) between `continuation` and the actual CLS continuation that follows the prefix in the source corpus
- Stratified by institutional schema type (regulatory / corporate-filing / analyst / market-recap)

E_schema_cont = mean S_schema per (case, model), reported with hierarchical shrinkage if reserve gate clears.

### 6.8 Per-model adapter notes

P_schema uses each model's default deployed mode. All 9 fleet members would run P_schema if reserve gate clears.

For continuation, models that aggressively format output (Claude, GPT) may add "Here is my continuation:" preambles. Adapter must strip such preambles before scoring; deployment config includes a per-model preamble-strip regex (pilot-tuned).

---

## 7. Deployment-layer adapter matrix

Per-model API configuration. Semantic-layer prompt body (§§3-6) is identical across the row; only deployment fields differ.

| Model | Backend | Access | Operators served | Thinking mode | Output enforcement | Temperature | Max tokens | Seed | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-7B | local vLLM | white-box | P_logprob, P_predict, P_extract, P_schema(reserve) | OFF (P_logprob); default (others) | prompt-based JSON + parser | 0.0 | 1024 | 20260501 | Already deployed |
| Qwen2.5-14B | local vLLM | white-box | P_logprob, P_predict, P_extract, P_schema(reserve) | OFF (P_logprob); default (others) | prompt-based JSON + parser | 0.0 | 1024 | 20260501 | Same tokenizer as 7B |
| Qwen3-8B | local vLLM | white-box | P_logprob, P_predict, P_extract, P_schema(reserve) | OFF explicit (`enable_thinking=False`) for ALL operators | prompt-based JSON + parser | 0.0 | 1024 | 20260501 | Qwen3 thinking ON by default; must explicitly disable to avoid thinking-token contamination of logprobs |
| Qwen3-14B | local vLLM | white-box | P_logprob, P_predict, P_extract, P_schema(reserve) | OFF explicit | prompt-based JSON + parser | 0.0 | 1024 | 20260501 | Same tokenizer as Qwen3-8B |
| GLM-4-9B | local vLLM | white-box | P_logprob, P_predict, P_extract, P_schema(reserve) | OFF | prompt-based JSON + parser | 0.0 | 1024 | 20260501 | GLM tokenizer family |
| DeepSeek-V3 | OpenRouter (`deepseek/deepseek-chat-v3-0324`) | black-box | P_predict, P_extract, P_schema(reserve) | n/a | `response_format=json_object` + parser fallback | 0.0 | 1024 | 20260501 | Pin to `-0324` to avoid silent updates; provider routing locked |
| GPT-4.1 | OpenRouter (`openai/gpt-4.1-2025-04-14`) | black-box | P_predict, P_extract, P_schema(reserve) | n/a | `response_format=json_object` | 0.0 | 1024 | 20260501 | Pinned date checkpoint |
| GPT-5.x | OpenRouter (TBD per FLEET_REVIEW_R2) | black-box | P_predict, P_extract, P_schema(reserve) | n/a (or per-model) | `response_format=json_object` | 0.0 | 1024 | 20260501 | Slug pinned at fleet freeze |
| Claude Sonnet 4.6 | OpenRouter (`anthropic/claude-sonnet-4.6-{date}`) | black-box | P_predict, P_extract, P_schema(reserve) | extended thinking OFF | tool-use JSON or prompt-based + parser | 0.0 | 1024 | 20260501 | Pin date in `FLEET_REVIEW_R2_SYNTHESIS.md` |

**Critical constraint (per `R5A_FROZEN_SHORTLIST.md` and `MEASUREMENT_FRAMEWORK.md` §4):** P_logprob requires `thinking=OFF` on all 5 white-box models. Mixing thinking-mode states across the white-box fleet would render E_CTS and E_PCSG uninterpretable.

**P_predict / P_extract / P_schema** use each model's default deployed mode (per the framework's distinction between operators that need clean logprobs and operators that just need structured output).

**Retry policy (all operators, all models):** retry on JSON parse failure up to 3× with identical parameters; if still failing, mark case as unscorable (audit field) and exclude from confirmatory analysis. Retry rate per (operator, model) is reported as a quality metric.

**Provider routing (OpenRouter members):** lock `provider.order` to a single backend (e.g., Fireworks, Together, or vendor direct) and set `provider.allow_fallbacks=false`. This avoids quantization variance across providers.

**Reproducibility artifacts:** preserve (a) HF commit SHAs for all 5 local white-box models, (b) OpenRouter request headers including resolved provider, (c) sha256 of every raw response.

---

## 8. Crosswalk — legacy prompts → R5A operators

| Legacy prompt (`task_prompts.yaml`) | Status | Maps to | Notes |
|---|---|---|---|
| `direct_prediction.base` | DEPRECATED in R5A | Closest analog: P_predict | Conceptually similar (article → direction) but R5A schema adds `explicit_memory_reference`, drops separate `slot_*` fields |
| `direct_prediction.matched` | DEPRECATED | — | Matched-format ablation belonged to Phase 0-4 task-design study; not part of R5A measurement |
| `sentiment_classification.*` | DEPRECATED | Closest analog: P_predict (`direction` field captures the same information) | Sentiment-vs-direction was a Phase 0-4 task framing distinction; R5A uses single `direction` field |
| **`decomposed_authority.*`** | **DROPPED** (per user 2026-04-16) | — | Early Phase 0-4 attempt; does not fit four-layer framework |
| `decomposed_novelty.*` | DEPRECATED | — | Novelty framing handled by Bloc 3 factor annotation, not by an operator |
| `decomposed_impact.*` | DEPRECATED | — | Phase 0-4 same-template bridge for CFLS; R5A uses operator-level uniformity |
| `sham_decomposition.control` | DEPRECATED | — | Phase 0-4 falsification control; R5A uses C_NoOp + post-cutoff negative control instead |
| `counterfactual_templates.semantic_reversal` | RETAINED (relocated) | C_SR generation rule (perturbation, not operator) | Generation logic moves to perturbation pipeline; not part of operator schema |
| `counterfactual_templates.provenance_swap` | DEPRECATED | — | Provenance is handled by Bloc 3 factor; no perturbation analog in R5A |
| `counterfactual_templates.novelty_toggle` | DEPRECATED | — | Novelty handled by factor annotation, not perturbation |
| `counterfactual_templates.neutral_paraphrase` | RETAINED (relocated) | Reserved for future use as paraphrase robustness probe | Not in R5A confirmatory; pilot may resurrect |
| `counterfactual_templates.sham_edits` | DEPRECATED | — | Phase 0-4 falsification; R5A uses C_NoOp |
| (none) | NEW in R5A | C_CO generation | Counterfactual outcome slot replacement; rule-based per event type |
| (none) | NEW in R5A | C_NoOp generation | Irrelevant clause insertion; deterministic clause bank |
| (none) | NEW in R5A | C_anon L0-L4 generation | Multi-level entity anonymization gradient |
| (none) | NEW in R5A | C_temporal generation | Temporal cue degradation; 2-3 dose levels |
| (none) | NEW in R5A | C_ADG prompt-injection | As-of-date system instruction (modifies operator prompt envelope) |

---

## 9. Implementation deliverables checklist

Before Phase 7 pilot can begin, the following must exist:

| Item | Owner | Status |
|---|---|---|
| §3 P_predict prompt body — Chinese instruction text | NLP track | TBD (pilot-iterable) |
| §4 P_logprob backend integration — vLLM logprob extraction + Min-K%++/CTS scoring | ML Engineer | TBD |
| §5 P_extract prompt body + Chinese-text normalization rules | NLP track | TBD |
| §6 P_schema prompt body + scoring spec (held in reserve until gate) | NLP track | spec frozen, implementation deferred |
| §7 Per-model adapter configs (`config/models/*.yaml`) | ML Engineer | TBD |
| Output JSON schema validators (replacing legacy `schema_validation.py`) | ML Engineer | TBD |
| Pilot prompt iteration log (`pilot/prompt_iteration_log.md`) | NLP + ML Engineer | TBD |
| Lockdown timestamp + git tag before confirmatory run | Project lead | TBD (post-pilot) |

The frozen confirmatory analysis cannot begin until **all** above items reach the lockdown timestamp.

---

## 10. Open questions deferred to pilot

The following are pilot-stage decisions, not schema-stage:

1. **Few-shot example count** for P_predict (zero-shot vs 1-2 examples). Trade-off: zero-shot maximizes construct purity but may yield higher parse failure rates on weaker models.
2. **Mask span density** for P_extract (how many masks per article; what types — number-only, entity-only, or mixed).
3. **Prefix length** for P_schema (currently 80 Chinese chars default; pilot may tune).
4. **Min-K%++ K parameter** (default 20%; alternate K stored in case pilot reveals strong K-sensitivity).
5. **Fuzzy match threshold** for E_extract (currently 0.8 char overlap; pilot may tune).
6. **Per-model preamble-strip regex** for P_schema continuation (Claude / GPT add preambles).
7. **Whether to include Chinese-tokenizer-normalized output** (e.g., 全角/半角 number normalization in P_extract guesses) before exact-match comparison.

These are explicitly NOT frozen by this schema; pilot reports their resolved values into the lockdown artifact.

---

## 11. Document lineage

```
Phase 0-4 task probes (config/prompts/README.md, task_prompts.yaml)
  → Phase 5 pilot (DeepSeek + Qwen positive control)
    → R4 factor investigation (12-factor shortlist)
      → R5A detector → estimand reframing (4-layer framework)
        → R5A_FROZEN_SHORTLIST.md (5 confirmatory estimands)
          → MEASUREMENT_FRAMEWORK.md (Factor / Perturbation / Operator / Estimand)
            → R5A_OPERATOR_SCHEMA.md (this document) — operator-layer implementation contract
              → Phase 7 pilot (prompt-text iteration)
                → Lockdown + confirmatory run
```

This schema is the operator-layer specification. Pilot iterates the prompt text within the schema; lockdown freezes the text; confirmatory run executes against the locked text.
