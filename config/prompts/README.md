# Prompt Schema Freeze for CLS-Leak

Frozen on `2026-04-05`. These prompts define the black-box task-conditioned probes for the study on look-ahead leakage in Chinese financial news. Instruction text is in English, article input is Chinese, and inference is fixed at `temperature = 0`.

## Design Rules

- Input unit: one Chinese financial news article.
- Evidence rule: copy `1-2` short verbatim Chinese quotes from the article.
- No outside knowledge: every prompt forbids hindsight, later market outcomes, and external facts.
- Direct/sentiment target rule: if the article is company- or sector-specific, judge the most directly affected Chinese listed stock or sector; if it is macro or policy-wide, judge the broad A-share market.
- Fallback rule: when the article does not support a confident decision, choose `neutral` or `unclear`.
- Freeze rule: prompts are fixed after this file set. No experiment-stage prompt edits.

## Prompt Inventory

| ID | Family | Variant | Primary experiment(s) |
| --- | --- | --- | --- |
| `direct_prediction.base` | Direct prediction | Baseline | `E1`, `E2`, `E3` |
| `direct_prediction.matched` | Direct prediction | Matched-format ablation | `E3` |
| `sentiment_classification.base` | Sentiment classification | Baseline | `E1`, `E2`, `E3` |
| `sentiment_classification.matched` | Sentiment classification | Matched-format ablation | `E3` |
| `decomposed_authority.base` | Decomposed extraction | Baseline | `E1`, `E2`, `E3` |
| `decomposed_authority.matched` | Decomposed extraction | Matched-format ablation | `E3` |
| `decomposed_novelty.base` | Decomposed extraction | Baseline | `E1`, `E2`, `E3` |
| `decomposed_novelty.matched` | Decomposed extraction | Matched-format ablation | `E3` |
| `sham_decomposition.control` | Sham decomposition | Falsification control | `E4` |

`E1` and `E2` reuse the same frozen task prompts used in `E3`; they do not introduce separate prompt wording.

## Matched-Format Contract

The matched-format ablation exists to hold output structure constant across direct prediction, sentiment classification, authority extraction, and novelty extraction.

All matched variants use the same JSON key structure and the same approximate output budget:

```json
{
  "slot_1": "...",
  "slot_2": "...",
  "slot_3": "...",
  "evidence": [
    {"quote": "...", "supports": ["slot_1"]},
    {"quote": "...", "supports": ["slot_2", "slot_3"]}
  ],
  "confidence": 0
}
```

Only the slot semantics change by task:

- `direct_prediction.matched`: `slot_1=direction`, `slot_2=scope`, `slot_3=strength`
- `sentiment_classification.matched`: `slot_1=sentiment`, `slot_2=scope`, `slot_3=tone_strength`
- `decomposed_authority.matched`: `slot_1=source_credibility`, `slot_2=regulatory_vs_rumor`, `slot_3=official_vs_unattributed`
- `decomposed_novelty.matched`: `slot_1=first_disclosure_vs_follow_up`, `slot_2=information_freshness`, `slot_3=novelty_strength`

This isolates task semantics from output-format artifacts.

## Sham-Decomposition Control

`sham_decomposition.control` keeps the same multi-field extraction burden, evidence burden, and output length as meaningful decomposition, but replaces economically relevant fields with surface-form indicators:

- `formality_level`
- `numeric_density`
- `sentence_complexity`

These are answerable from the article text but are not intended to encode economically meaningful signal.

## Counterfactual Templates

`counterfactual_templates.yaml` defines five frozen rewrite templates:

- `semantic_reversal`: flips decision-relevant economics for direct prediction or sentiment.
- `provenance_swap`: changes authority cues only, especially regulator notice vs unattributed rumor.
- `novelty_toggle`: changes novelty cues only, especially first disclosure vs routine follow-up.
- `neutral_paraphrase`: preserves the original task label(s) while changing wording.
- `sham_edits`: changes sham surface indicators only while holding the economics fixed.

## Files

- `config/prompts/task_prompts.yaml`
- `config/prompts/counterfactual_templates.yaml`
- `config/prompts/schema_validation.py`

## Validation

```powershell
conda run -n rag_finance python config/prompts/schema_validation.py --catalog task --id direct_prediction.base --json path\to\output.json
```
