# False-Outcome Editorial View

1. **Stronger, but with a shifted center of gravity.** False-outcome CPT does not merely add another experiment; it upgrades the paper from "we observe leakage patterns" to "we causally show that task design gates access to implanted outcome memory." That is a better paper. But it does make the paper meaningfully different from the original proposal. The framing should now explicitly be a **task-design / evaluation-mechanism** paper with one causal intervention, not a broad benchmark survey.

2. **The balance should be asymmetrical.** Make **Qwen CPT** the primary identification result and keep **DeepSeek inference-time tests** as behavioral replication / portability evidence. Qwen answers: *is the memory channel real, and is it task-gated?* DeepSeek answers: *does the same qualitative pattern appear in a strong model we cannot retrain?* Do not let both become co-equal backbones. One causal story plus one behavioral replication is enough.

3. **If CPT is the headline, CLS-Leak still matters, but its role changes.** It becomes the matched evaluation substrate that makes the causal claim credible: same articles, multiple task formulations, shared annotation, and a reusable benchmark others can run without retraining. That is still publishable value. But the benchmark is now the **infrastructure and public artifact**, not the sole intellectual headline.

4. **This is still EMNLP if you keep the emphasis on evaluation methodology.** The paper remains NLP-facing if the contribution is about task formulation, benchmark design, and groundedness under temporal contamination. It drifts toward ICLR/NeurIPS only if the CPT section starts reading like a new training method or a scaling study. Present CPT as a clean identification device, not an optimization contribution.

5. **Revised structure**
1. Introduction: task design gates look-ahead memory
2. Related Work: contamination, grounding, counterfactual memorization
3. CLS-Leak: benchmark construction and task families
4. Causal Test: none / real / false outcome CPT on Qwen
5. Main Result: false outcome moves direct prediction more than authority
6. Behavioral Replication: counterfactual edits and evidence intrusion on DeepSeek
7. Temporal and robustness analyses
8. Discussion: implications for benchmark design and financial NLP

6. **Yes, this changes the 10-week timeline.** The paper becomes stronger, but only if scope is cut elsewhere. My advice: one open-model CPT backbone, one closed-model behavioral replication, one clean benchmark slice, and no attempt to keep every prior diagnostic at full strength. If you do that, `10 weeks` is still realistic. If you try to run full CPT, full counterfactual editing, full temporal analysis, and a large benchmark all at once, it is not.
