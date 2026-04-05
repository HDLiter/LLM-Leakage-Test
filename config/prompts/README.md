# Prompt Schema Freeze for CLS-Leak

Frozen on `2026-04-05-v2`. These prompts define the task-conditioned probes and rewrite templates for the study on look-ahead leakage in Chinese financial news. Instruction text is in English, article input is Chinese, inference is fixed at `temperature = 0`, and the input unit is now an `(article, target)` pair.

## Design Rules

- Input unit: one Chinese financial news article plus one explicit target, passed as `Target: {target} ({target_type})`.
- Target conditioning: every task is judged only for the provided target; prompts must not substitute another company, sector, or broad market proxy.
- User-prompt pattern:

```text
Article (Chinese):
{article}

Target: {target} ({target_type})

Task: ...
```

- Evidence rule: copy `1-2` short verbatim Chinese quotes from the article, with quote `maxLength = 120`.
- No outside knowledge: every prompt forbids hindsight, later market outcomes, realized returns, and external facts.
- Sanity-check field: every task output and every counterfactual rewrite output includes `target_echo`, which must exactly repeat the target string.
- Fallback rule: when the article does not support a confident decision, choose `neutral` or `unclear` as instructed by the task.
- Freeze rule: prompts are fixed after this file set. No experiment-stage prompt edits.

## Prompt Inventory

| ID | Family | Variant | Core fields | Primary experiment(s) |
| --- | --- | --- | --- | --- |
| `direct_prediction.base` | Direct prediction | Baseline | `direction` | `E1`, `E2`, `E3` |
| `direct_prediction.matched` | Direct prediction | Matched-format ablation | `slot_1=direction`, `slot_2=framing_certainty`, `slot_3=strength` | `E3` |
| `sentiment_classification.base` | Sentiment classification | Baseline | `sentiment` | `E1`, `E2`, `E3` |
| `sentiment_classification.matched` | Sentiment classification | Matched-format ablation | `slot_1=sentiment`, `slot_2=framing_certainty`, `slot_3=tone_strength` | `E3` |
| `decomposed_authority.base` | Decomposed extraction | Baseline | `source_credibility`, `regulatory_vs_rumor`, `official_vs_unattributed` | `E1`, `E2`, `E3` |
| `decomposed_authority.matched` | Decomposed extraction | Matched-format ablation | `slot_1=source_credibility`, `slot_2=regulatory_vs_rumor`, `slot_3=official_vs_unattributed` | `E3` |
| `decomposed_novelty.base` | Decomposed extraction | Baseline | `disclosure_frame`, `information_freshness`, `novelty_strength` | `E1`, `E2`, `E3` |
| `decomposed_novelty.matched` | Decomposed extraction | Matched-format ablation | `slot_1=disclosure_frame`, `slot_2=information_freshness`, `slot_3=novelty_strength` | `E3` |
| `decomposed_impact.base` | Impact decomposition | Baseline | `fund_impact`, `shock_impact` | `E6` |
| `decomposed_impact.matched` | Impact decomposition | Matched-format ablation | `slot_1=fund_impact`, `slot_2=shock_impact`, `slot_3=effect_persistence` | `E6` |
| `sham_decomposition.control` | Sham decomposition | Falsification control | `formality_level`, `numeric_density`, `sentence_complexity` | `E4` |

`E1` and `E2` reuse the same frozen task prompts used in `E3`; they do not introduce separate task wording. `decomposed_impact.*` is reserved for `E6` and is intentionally excluded from the counterfactual rewrite catalog.

## Matched-Format Contract

The matched-format ablation holds output structure constant across direct prediction, sentiment classification, authority extraction, novelty extraction, and impact extraction.

All matched variants use the same JSON key structure and the same approximate output budget:

```json
{
  "target_echo": "...",
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

- `direct_prediction.matched`: `slot_1=direction`, `slot_2=framing_certainty`, `slot_3=strength`
- `sentiment_classification.matched`: `slot_1=sentiment`, `slot_2=framing_certainty`, `slot_3=tone_strength`
- `decomposed_authority.matched`: `slot_1=source_credibility`, `slot_2=regulatory_vs_rumor`, `slot_3=official_vs_unattributed`
- `decomposed_novelty.matched`: `slot_1=disclosure_frame`, `slot_2=information_freshness`, `slot_3=novelty_strength`
- `decomposed_impact.matched`: `slot_1=fund_impact`, `slot_2=shock_impact`, `slot_3=effect_persistence`

This isolates task semantics from output-format artifacts.

## Novelty Framing

`disclosure_frame` replaces the old `first_disclosure_vs_follow_up` field. The novelty prompts now judge only how the article frames the disclosure for the target:

- `new_announcement`
- `update_or_follow_up`
- `unclear`

This is article framing, not ontic firstness. The prompt explicitly instructs the model not to judge whether the event truly appeared before elsewhere. `information_freshness` and `novelty_strength` are kept as separate fields.

## Impact Decomposition

`decomposed_impact.*` separates two target-specific channels:

- `fund_impact`: fundamental or structural impact on the target
- `shock_impact`: short-run sentiment or reaction pressure on the target

These prompts explicitly forbid judging realized price movement or return. The matched variant adds `effect_persistence` to capture whether the article frames the effect as transient or persistent.

## Sham-Decomposition Control

`sham_decomposition.control` preserves multi-field extraction burden, evidence burden, and approximate output length, but replaces economically meaningful labels with surface-form indicators:

- `formality_level`
- `numeric_density`
- `sentence_complexity`

These are answerable from the text around the target but are not intended to encode economically meaningful signal.

## Counterfactual Templates

`counterfactual_templates.yaml` defines five frozen rewrite templates. Every template now propagates `{target}` and `{target_type}`, preserves the target as the same referent, and returns `target_echo`.

- `semantic_reversal`: flips the economic meaning for the target so the primary decision label changes.
- `provenance_swap`: changes authority cues only for claims about the target.
- `novelty_toggle`: changes disclosure framing only for the target, from `new_announcement` to `update_or_follow_up` or vice versa.
- `neutral_paraphrase`: preserves the original target-specific label(s) while changing wording.
- `sham_edits`: changes sham surface indicators only while holding target-relevant economics fixed.

There is intentionally no impact-specific counterfactual template.

## Files

- `config/prompts/task_prompts.yaml`
- `config/prompts/counterfactual_templates.yaml`
- `config/prompts/schema_validation.py`

## Validation

```powershell
conda run -n rag_finance python config/prompts/schema_validation.py --catalog task --id direct_prediction.base --json path\to\output.json
```
