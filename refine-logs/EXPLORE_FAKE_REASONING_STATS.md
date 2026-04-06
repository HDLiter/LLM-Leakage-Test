# Explore Fake Reasoning: Econometric Note

1. **Formal estimand.**  
Let `m in {self,inj}` be generation mode and `q in {real,sham}` content quality. Let `D_i(m,q)` be the decomposition text realized for item `i`, and let `Y_i(d)` be leakage score when the later prediction sees decomposition `d`. The **reduced-form procedure effect** is
`tau_q^RF = E[Y_i(D_i(self,q)) - Y_i(D_i(inj,q))]`.
This is well-defined, but it bundles together provenance, stochasticity, and content differences. The pure "does the model doing it matter?" estimand would be a **controlled direct effect at fixed text**
`tau_q^CDE(d) = E[Y_i(d,self) - Y_i(d,inj)]`,
where the same decomposition `d` is held fixed and only provenance changes.

2. **Is self vs injected identified?**  
Usually **no**. In a standard API call, if the full transcript tokens, role tags, decoding settings, and seed are identical, then the model computes the same conditional distribution. In that case `Y_i(d,self) = Y_i(d,inj)`, so `tau_q^CDE(d) = 0` by construction. A contrast exists only if "self" versus "injected" changes something real: different text `D_i`, different role/system metadata, different temperature-induced draws, or some persistent non-token state. So A-real vs B-real is not a distinct treatment once the realized tokens are the same.

3. **How to test "model doing decomposition" versus "decomposition in context"?**  
Treat this as a **policy comparison**, not a provenance comparison. Randomize items to:
`self-generate -> predict` versus `inject decomposition -> predict`,
and allow the decomposition texts to differ. Then analyze:
`self -> D -> Y` versus `inj -> D -> Y`.
This estimates whether the model's own decomposition policy produces different downstream behavior. If you want a true direct-effect test holding `D` fixed, a standard chat API is the wrong object; you would need hidden scratchpad/state that is not reducible to visible tokens.

4. **Cleaner alternative design?**  
Yes, but with one correction. "Decomposition in context vs no decomposition" crossed with "real vs sham" is **not a literal 2x2**, because content quality is undefined when no decomposition is present. Cleaner options:
- `3-arm`: no decomposition / real decomposition / sham decomposition.
- True `2x2`: structured decomposition versus length-matched unstructured control, crossed with real versus sham content.
Those contrasts are identified and directly answer whether structured grounded analysis changes leakage.

5. **Relation to continued pretraining.**  
They can be in the same paper if framed as **training-time vs inference-time channels**. Continued pretraining identifies parameter-level memory contamination; decomposition prompting identifies context-steering / faithfulness at inference. The natural bridge is a cross-design: base versus CPT-treated model, each evaluated under no/real/sham decomposition prompts. Then you can ask whether decomposition reduces, amplifies, or leaves unchanged CPT-induced leakage. Keep the estimands separate.
