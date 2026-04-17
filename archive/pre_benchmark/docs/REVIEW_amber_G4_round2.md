# Amber G4 Round 2 Review

Reviewed `docs/PILOT_RESULTS.md` Phase 4 against `data/results/diagnostic_2_results.json`, with the Round 1 `ITERATE` findings as the acceptance checklist.

## Findings

1. **Medium:** The Phase 4 section still contains Phase 3 comparison numbers that are not auditable from the Phase 4 evidence file used in this review. The new Phase 4 tables are reproducible from `data/results/diagnostic_2_results.json`, but Phase 3 comparator values at `docs/PILOT_RESULTS.md:426`, `470-485`, and `583-585` still require a prior-phase artifact not cited here. This means revision item 4 from Round 1 is still open.

2. **Low-Medium:** The new `Key definitions` block is materially better, but it is not fully standalone yet. At `docs/PILOT_RESULTS.md:432-450`, `pre/post`, `fo_flip`, `strict/hedged`, OR orientation, and `cpt_mode` are defined accurately. However, `CFLS` itself is still not locally defined inside Phase 4, and the section never says that the `cpt_mode` cross-tables at `543-561` are conditioned on valid `original + false_outcome_cpt` task outputs. That omission is why a reader sees `115/217/274` in the bug table but `110/216/265` and `113/215/272` in the cross-tabs without an explicit denominator rule.

3. **Low:** One residual phrasing still leans stronger than the surrounding text. `docs/PILOT_RESULTS.md:517` says `homogeneous — pooling is valid`, while the next paragraph correctly says `Breslow-Day p=0.28 does not reject stratum homogeneity` and treats the interaction as unconfirmed. The latter wording is the defensible one; the parenthetical should match it.

## Checks

**A. Were the 6 requested revisions adopted?**

- `cpt_mode` now uses the requested `period × cpt_mode` cross-tab: **Yes**
- overclaiming `validates/knows` language softened: **Yes**
- Q3 anchor-interaction claim toned down: **Yes**
- Phase 3 comparison numbers removed or newly sourced inside the stated evidence bundle: **No**
- reader-test / operational definitions fix: **Partially**
- Q2/Q3 reversal made explicit with `Revised from Phase 3` / `supersedes`: **Yes**

Net: **4 adopted, 1 partial, 1 still open.**

**B. Do the `cpt_mode` cross-tab numbers match `data/results/diagnostic_2_results.json`?**

Yes, when recomputed on the valid CPT-scored subsets:

- `fo_flip_impact_hedged`: `pre_cutoff × llm_negated = 13/110`, `pre_cutoff × generic_post_cutoff = 27/216`, `post_cutoff × generic_post_cutoff = 18/265`
- `fo_flip_direct_hedged`: `pre_cutoff × llm_negated = 17/113`, `pre_cutoff × generic_post_cutoff = 31/215`, `post_cutoff × generic_post_cutoff = 58/272`

These match the displayed tables exactly.

**C. Any remaining overclaiming wording?**

The major overclaiming from Round 1 is fixed. `validates the plan's premise` and `knows the true fund_impact` are gone, and the new wording is appropriately hedged. The only leftover I would still trim is `homogeneous — pooling is valid` at `docs/PILOT_RESULTS.md:517`, because `BD p=0.28` supports non-rejection of heterogeneity, not proof of homogeneity.

**D. Is the new `Key definitions` block accurate and complete?**

Accurate: **Yes.**

Complete for a fresh reader: **Not quite.**

- It correctly defines `pre/post`, `fo_flip`, `strict_flip`, `hedged_flip`, OR orientation, and `cpt_mode`.
- It does not define `CFLS` locally inside Phase 4.
- It does not explain the denominator rule used by the CPT cross-tabs, which is the main remaining source of reader confusion.

Verdict: ITERATE
