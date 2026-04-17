# Real vs Injected Decomposition: Quant View

1. **Yes, this design makes sense operationally.** It is a clean mechanism test of **context-faithful prompting vs actual computation**. In production terms, it asks whether anti-leakage gains come from forcing the main model to read and decompose the article itself, or whether the gain can be **outsourced** into context assembled upstream. That is exactly the decision boundary for a multi-model inference stack.

2. **The more useful outcome for pipeline design is B-real working nearly as well as A-real.** If **A-real ~= B-real**, then decomposition is mainly a **state-setting/context effect**. That is commercially valuable: a cheap smaller model, rules engine, or cached extractor can generate authority/novelty slots, and a stronger prediction model can consume them. If instead **A-real < B-real**, that is still useful, but it says the anti-leakage benefit is tied to the forecaster's own token-by-token processing. Then the production implication is harsher: do not separate extractor and predictor if leakage control is the objective.

3. **Main confounds are manageable but real.**
- Injected text may alter behavior for reasons unrelated to grounding: extra length, recency, structured formatting, or implicit instruction effects.
- Self-generated analysis gives the model **more internal computation and self-commitment**, not just more context. That is a genuine treatment difference, but it complicates attribution.
- Fake/random content can make the model cautious or confused rather than revealing a pure priming effect. A nonsense control may induce neutrality mechanically.
- The model may defer to injected content because it looks authoritative, even when wrong. That tests susceptibility to contextual anchoring, not only leakage.

So controls should match **length, schema, placement, and tone** across cells, and fake content should be **plausible but wrong**, not absurd.

4. **This is not the same as the false-outcome CPT test.** False-outcome CPT asks: *can misleading prior context override the article and pull the model toward a wrong remembered outcome?* Real vs Injected Decomposition asks: *can a grounded intermediate representation inoculate the model against that pull, and does it matter whether the forecaster generated it itself?* So CPT is mainly a **vulnerability test**; this is a **mechanism and architecture test**. They complement each other. In fact, the strongest version is to run this 2x2 under both normal and false-outcome context.

5. **Yes, this may be the cheapest experiment in the paper and one of the highest-value findings.** It reuses existing prompts, existing decomposition outputs, and the same downstream prediction metric. But the result would directly determine whether the right production design is:
- one-model reflective prediction,
- two-stage cheap-extractor + expensive-forecaster,
- or “do not inject analysis because context itself can bias the predictor.”

That is unusually high leverage for a low-cost ablation.
