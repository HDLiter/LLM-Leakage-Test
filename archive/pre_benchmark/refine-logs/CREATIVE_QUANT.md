## Ideal Measurement: Decontaminated Semantic Response Curve

I would stop trying to rescue a single EI scalar. I would build a paired factorial benchmark that measures how much each task's semantic sensitivity is suppressed by memorization cues, then compare tasks on a utility-vs-leakage frontier.

Unit of analysis: the same `(article, target)` cluster, scored across tasks and models.

For each item, I would generate a `3 x 3` intervention grid:

1. **Semantics axis**
- original article
- matched local placebo edit
- matched semantic flip

2. **Cue axis**
- full article
- natural entity abstraction: replace entity strings with role-consistent descriptions, while providing the target separately in the prompt
- deep decontamination rewrite: preserve economics, but rewrite away CLS phraseology, fixed event templates, and article-specific wording

This matters because the failure modes are different. Full-to-entity-abstracted isolates entity-keyed recall. Entity-abstracted-to-deep-rewrite isolates template or article-form recall. Placebo-to-flip isolates true semantic responsiveness from edit brittleness.

The model output should be a task-specific score, not just a hard label. For black-box APIs, use parsed label plus calibrated confidence / probability margin. For white-box Qwen, use log-prob margins on the task labels. The key estimand is the within-item interaction:

`Leakage = (Delta_sem - Delta_placebo)_decontaminated - (Delta_sem - Delta_placebo)_full`

where `Delta_sem` is the score change from original to semantic flip, and `Delta_placebo` is the score change from original to placebo. Intuition: if cue-rich inputs suppress semantic sensitivity because the model is anchored on memorized content, removing those cues should restore response to the flip. That recovery is leakage. You can decompose it into entity leakage and template/article leakage by using the two cue steps separately.

I would then layer in a white-box familiarity prior, but only as validation and stratification, not as the main metric. Compute LAP / Min-K on the original, entity-abstracted, and deep-rewritten texts. If familiarity collapses after entity abstraction, the mechanism is entity-triggered recall. If it survives that but collapses after deep rewrite, it is template or near-article recall. If black-box leakage interaction is concentrated in high-familiarity strata, the interpretation is much stronger.

For the paper, I would report two things:

- **Leakage elasticity by task**: mean and tail leakage interaction from the factorial design.
- **Production trustworthiness**: downstream predictive utility plotted against leakage elasticity. The right task is not the one with the lowest raw leakage score; it is the one that keeps utility while showing low leakage elasticity, especially in high-familiarity items.

That gives a causal measurement, mechanism decomposition, and a direct production decision rule, without stacking ad hoc controls onto one brittle subtraction metric.
