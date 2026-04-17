Yes: in the current design, \(EI=\bar Y_{CF}-\bar Y_{PARA}\) does not identify a pure memorization effect, where \(Y\) is invariance. Let \(S\in\{0,1\}\) indicate whether the rewrite changes task-relevant semantics, and let \(D\) be a surface-proximity vector (edit distance, changed-token share, span count/location, entity-number preservation, syntax delta). Because \(D\) differs systematically between counterfactual and paraphrase arms, \(E[Y\mid S=1]-E[Y\mid S=0]\) mixes semantic effect with proximity effect. So yes, it is an omitted-variable/design-imbalance problem.

But ex post “partialing out” is not the clean fix. A model like

\[
Y_{ij}=\alpha_i+\beta S_{ij}+f(D_{ij})+\varepsilon_{ij}
\]

is at best a robustness check. Here \(D\) is partly post-treatment, and the two arms have poor common support by construction (local CF, global paraphrase), so \(\beta\) relies on functional-form extrapolation.

The clean identification strategy is to redesign the baseline so semantic status is crossed with matched surface distance. For each original item \(i\), generate:

1. a label-changing counterfactual at distance bin \(d\);
2. a label-preserving placebo rewrite at the same \(d\), with the same edit topology (same number/location of changed spans, similar lexical overlap and length).

Then estimate the within-distance semantic effect:

\[
\tau(d)=E\!\left[Y_i(1,d)-Y_i(0,d)\right],
\qquad
\tau=\sum_d w_d\,\tau(d)
\]

using only bins with overlap. This is the cleanest way to separate memorization-driven invariance from surface-proximity-driven invariance.

So the subtraction framework is not wholly wrong, but the current subtractand is wrong. Global paraphrases should be a separate diagnostic for general rewrite instability. The primary baseline should be a distance-matched, label-preserving local placebo edit, essentially a strengthened version of Block 3 sham.
