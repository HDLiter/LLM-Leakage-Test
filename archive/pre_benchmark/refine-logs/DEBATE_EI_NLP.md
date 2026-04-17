Yes. The confound is real in the current setup.

`_excess_invariance_components` computes `EI = cf_invariance - para_invariance` with no adjustment for rewrite magnitude. In label mode it is just a binary same-label check; in confidence mode it is `1 - |delta|`. So if counterfactuals are mostly local span edits while `neutral_paraphrase` is a broader rewrite, EI can be positive because the model is more robust to small surface perturbations than to large paraphrases, not because it memorized the original article.

The prompt templates make this plausible: targeted CF templates explicitly encourage minimal local edits, while `neutral_paraphrase` asks for wording/syntax changes across the article. Block 3 helps with output-format confounds, but matched-format alone does not remove edit-magnitude asymmetry.

Best fix: add matched-edit paraphrases. For every counterfactual, generate a label-preserving rewrite with the same locality profile: same number of changed spans, similar span lengths, similar edit-distance band, but semantics preserved. Then compare local-CF vs local-paraphrase, not local-CF vs global-paraphrase.

Also add edit-distance controls:
- compute char/token Levenshtein, overlap, sentence-count delta, changed-span count
- estimate EI only within overlapping distance bins, or residualize invariance on these features before comparing CF vs paraphrase
- report a sensitivity analysis where CF and paraphrase pairs are propensity-matched on edit magnitude

Better metric design: replace the raw difference with a regression / diff-in-diff view:

`same_output ~ semantic_flip + edit_distance + local_vs_global + semantic_flip:local_vs_global + cluster FE`

The leakage signal is the semantic-change effect after controlling for rewrite magnitude. Strongest design: a 2x2 rewrite grid per article: local/global x semantics-preserving/semantics-flipping.
