# Final Direction

The synthesis works, but only if we simplify harder and stop over-claiming identification. The literature now clearly supports the **same-article, different-task** framing and the **evidence-intrusion / context-faithfulness** measurement logic. It does **not** support selling the cutoff design as a formal regression discontinuity. Use it as a **temporal boundary / training-access premium** analysis instead.

## Keep

- **Editor backbone**: a binary contrast between an **outcome-proximal task** and an **evidence-grounded task** on the same `(article, target)` input.
- **Same-article different-task comparison** as the paper's core novelty. This is cleaner and more defensible than a four-task ladder.
- **Evidence intrusion** as the main black-box assay: require answer + evidence quotes, then score whether the quoted evidence or stated facts contain information absent from the visible input.
- **Qwen familiarity prior** and publication-age patterns as triangulation, not as the headline estimand.
- **Utility-vs-leakage frontier** as the production takeaway, but only after the core contamination result is locked.

## Cut

- The **3x3 factorial** as a main-paper design. It is too ambitious for 10 weeks; keep it as future work or a tiny appendix probe.
- The full **`direct > sentiment > authority > novelty`** ladder as the thesis. It is fragile and annotation-heavy. **Novelty** is the first thing I would cut.
- Formal **"temporal RD"** language. There is no literature precedent and the cutoff is not sharp enough.
- **CF-based EI** as the central contribution. It should become secondary validation.
- Any insistence on a **1,000-item** benchmark if it slows auditing. A clean **300-500 audited clusters** is stronger than a noisy 1,000.

## Add

- A **small randomized-exposure experiment on Qwen 7B** as the causal anchor. Randomly inject/withhold roughly `100-200` event bundles during brief continued pretraining, then evaluate both tasks on held-out items. This gives the cleanest estimand in the entire project.
- A **conflict condition** from the context-faithfulness literature: present plausible contradictory evidence and test whether the model still leaks article-consistent facts not in context.
- A **pre-registered primary leakage metric** at the article level: unsupported-evidence rate plus counterfactual non-responsiveness, compared across the two task families.
- One clean **utility vs leakage** figure for the two task families only.

## Strongest 10-week paper

**Outcome-Proximal Tasks Amplify Contamination in Chinese Financial News LLM Evaluation**

Minimum strong version:

1. `300-500` audited article-target clusters.
2. Two tasks only: **direct prediction** vs **evidence-grounded authority / extractive support**.
3. Same-article different-task comparison with **evidence-intrusion scoring**.
4. **Temporal boundary** analysis around documented model frontier, presented descriptively.
5. A **small randomized-exposure Qwen validation** showing exposure effects are larger for the outcome-proximal task.

That is the best paper you can realistically build in 10 weeks. It has one clean empirical law, one measurement contribution reviewers already understand from adjacent literature, one causal validation they cannot dismiss easily, and a domain where the literature is almost empty.
