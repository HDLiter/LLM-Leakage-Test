# Template Rigidity — influence channel analysis (audit trail)

> Pre-specified pilot signatures for interpreting how template rigidity
> affects experimental readings. **None of these are conclusions** — they are
> predictions to compare against pilot data.

## Channels

### Channel 1 — Near-neighbor memory
**Mechanism**: Templated articles have many structurally similar near-neighbors
in training data (same skeleton, different slot values). Per Carlini's
duplication→memorization finding (extended to structural near-duplicates),
high rigidity cases may be memorized more precisely — not verbatim, but
"remembered the typical outcome direction for this template pattern."

**Pilot signature**:
- rigidity × resistance: **positive** correlation
- pre/post cutoff: correlation **stronger in pre-cutoff** (memory requires
  having seen the case; post-cutoff cases weren't seen)
- rigidity × E_CTS: possibly weak positive

### Channel 2 — Bias reinforcement
**Mechanism**: Template format carries directional signal — model learned
"articles with this template structure tend to have outcome X." Not
case-specific memory but format-class prior. When perturbed (e.g., sentiment
reversed), model uses format prior instead of reading modified text.

**Pilot signature**:
- rigidity × resistance: **positive** correlation
- pre/post cutoff: **little difference** (bias is persistent, learned from
  the entire corpus, not dependent on having seen the specific case)
- rigidity × E_CTS: possibly weak positive

### Channel 3 — Generalization substitution
**Mechanism** (user-originated insight): Model has seen thousands of instances
of the same template with different slot values and different outcomes →
can **generalize** ("within this template, what slot content predicts what
outcome") → genuine learned capability, not memorization. Conversely,
low-template (unique) articles force the model to rely on case-specific
memory or crude bias.

**Pilot signature**:
- rigidity × resistance: **negative** correlation (high template → model
  reads perturbed text using generalized rule → follows perturbation → low
  resistance)
- pre/post cutoff: negative correlation **exists only in pre-cutoff**
  (because the "low template → high resistance" mechanism requires case
  memory, which only exists for pre-cutoff cases; post-cutoff cases have
  low resistance regardless of template level)
- rigidity × E_CTS: possibly weak positive

### Channel 4 — Pure surface familiarity
**Mechanism**: Template skeleton has high corpus frequency → lower perplexity →
affects E_CTS (familiarity metric) but not behavioral predictions.

**Pilot signature**:
- rigidity × resistance: **no correlation**
- pre/post cutoff: —
- rigidity × E_CTS: **positive** correlation (the only metric affected)

## Summary table

| Channel | rigidity × resistance | pre/post difference | rigidity × E_CTS |
|---|---|---|---|
| 1 Near-neighbor memory | positive | pre stronger | weak positive |
| 2 Bias reinforcement | positive | little difference | weak positive |
| 3 Generalization substitution | negative | pre-only | weak positive |
| 4 Pure surface familiarity | no correlation | — | positive |

## Interpretation guide

- Positive correlation + pre > post → Channel 1 dominant
- Positive correlation + pre ≈ post → Channel 2 dominant
- Negative correlation + pre-only → Channel 3 dominant
- No correlation with resistance → Channel 4 only (rigidity less useful as
  memory-modulation factor, but still valid as E_CTS covariate)
- **Mixed signals expected** — real data will likely show a blend; this table
  helps decompose.

## Important caveat

These are pre-specified predictions for pilot interpretation, not conclusions.
The actual channel determination comes from pilot data. This analysis exists
to prevent post-hoc rationalization: signatures were written down before
seeing any results.
