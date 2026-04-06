Entity masking should not be treated as a stand-alone causal control. In `src/masking.py`, `mask_entity` is a hard textual intervention (`[实体i]`), so it changes cue availability, reference resolution, and task difficulty simultaneously.

1. **Best design:** `A) 2x2 (entity x semantic)` is the cleanest design. Let `Z in {0,1}` be entity masking, `S in {0,1}` be semantic edit vs local placebo, and `Y` be invariance (label match or confidence similarity, consistent with `metrics.py`). Define
`EI(z) = E[Y(z, S=1) - Y(z, S=0)]`.
Then
`Delta_entity = EI(0) - EI(1)`
measures how much excess invariance disappears once entity cues are removed. This is the closest estimand to “entity-triggered memorization.” `B` is a useful diagnostic on Tier1; `C` is too confounded to be the primary design.

2. **Instrument validity:** No, entity masking is **not** a valid instrument for memorization. The exclusion restriction fails because `Z` affects not only latent memorization `M`, but also reasoning `R` and difficulty `D`. So `Z` is admissible as an **intervention/perturbation**, not as an IV.

3. **Estimand:** What we can identify is not a pure causal effect of `M`, but the **entity-cue dependence of excess invariance**:
`Delta_entity = [E Y(0,1) - E Y(0,0)] - [E Y(1,1) - E Y(1,0)]`.
A large positive value means the model’s suspicious stability under semantic counterfactuals relies on visible entity names. It does **not** by itself identify a path-specific effect through memorization alone.

4. **Partial masking:** Yes, partially. The best version is: mask entity mentions in the article body, but keep the benchmark target explicitly fixed in the prompt/metadata. That preserves the answer space and some task semantics, so the `Z -> D/R` violation is weaker. But it is still not eliminated: salience, co-reference, and discourse structure still change. Treat this as a **sensitivity design**, not a rescue of the exclusion restriction.

5. **Interaction with placebo/sham:** The local placebo remains essential inside each mask cell; it controls edit topology and distance, so `EI(z)` is not driven by superficial rewrite magnitude. The sham control remains orthogonal: it tests structure/output-burden confounds, not entity-triggered memorization. So the coherent stack is: `2x2 (mask x semantic/placebo)` as primary, sham as a separate falsification layer.
