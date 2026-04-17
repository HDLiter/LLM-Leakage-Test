The edit-magnitude confound is real and, in the current setup, material. It is not irrelevant.

Why: the implemented EI in [src/metrics.py](D:/GitRepos/LLM-Leakage-Test/src/metrics.py) is just `cf_invariance - para_invariance` on labels or confidence. It does not condition on edit distance, changed spans, lexical overlap, or locality. But the templates are asymmetric: `semantic_reversal` is explicitly minimal/local, while `neutral_paraphrase` is allowed to rewrite wording and syntax broadly. That means `para_invariance` is measuring robustness to large surface perturbations, not the nuisance variation present in the counterfactual arm. So a positive EI can be mechanically induced even with zero memorization.

I would call that fatal for a strong causal interpretation of EI as “memorization signal” if left uncorrected. But it is fixable as a design problem.

What to do instead:

1. Replace the subtraction baseline with a matched placebo edit: a label-preserving, target-conditioned local rewrite on the same semantic span, with similar token edit distance / changed-span count as the semantic reversal.
2. Keep broad neutral paraphrases, but report them separately as a robustness metric, not as the EI subtraction term.
3. Use the stored rewrite metadata (`changed_spans`) plus edit-distance / overlap features in matching or regression:
   `invariance ~ reversal_indicator + edit_size + lexical_overlap + length_ratio + cluster FE`.
4. Prefer probability or logit shift over hard 0/1 invariance, since binary agreement is too coarse.

`sham_edits` helps as a surface-form control, but it still does not solve the key problem unless the placebo edits are matched in locality and magnitude to the counterfactual edits.
