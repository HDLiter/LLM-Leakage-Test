My recommendation is **B**, not **C**, with **A** reserved only if B lights up strongly. Keep the new **local placebo edits** as the main EI fix in the benchmark, then run a **natural entity-masking ablation** on Tier1 (`300` paired cases). Use natural substitutions like `央行 -> 某监管机构`, `贵州茅台 -> 某白酒龙头`, not `[实体N]` placeholders.

Why B:

- It identifies the new mechanism without changing the main estimand. The production question is whether real pipelines leak on real inputs, and real inputs contain named entities.
- C is too confounded for a main metric. Masking changes task difficulty, target resolution, lexical naturalness, and sometimes the economic specificity of the article. A masked vs unmasked delta is not cleanly "entity memorization."
- A is the cleanest design, but it roughly doubles cost and operational complexity before we know the effect is material. It also spends power across four cells instead of using a paired Tier1 diagnostic.

Why B is strong enough statistically:

- The comparison is within article and target, so the masked/unmasked delta is paired and relatively efficient.
- On `300` Tier1 cases, you should have enough power to detect a meaningful invariance drop if entity-triggered recall is real, especially if you pre-specify high-risk strata: large-cap issuers, regulators, central macro actors, and repeated policy templates.

Production relevance:

- This mostly changes **interpretation**, not the primary validation target. The main benchmark should stay unmasked because traders will not mask production news.
- If masking sharply lowers counterfactual invariance, the pipeline is vulnerable to **entity-keyed recall**. Then the right response is mitigation or reporting language, not replacing the whole benchmark with masked prompts.

For Chinese financial telegraphs specifically, I think the concern is **real**. CLS-style telegraphs are short, formulaic, and entity-dense; often the usable signal is basically `[salient entity] + [event/policy verb]`. That is exactly the format where a memorized article can be reactivated by a few tokens like `贵州茅台`, `央行`, or `证监会`. But I would expect heterogeneity: the effect should be strongest for mega-cap names, regulators, and recurring macro-policy beats, and weaker for lower-salience small-cap items.
