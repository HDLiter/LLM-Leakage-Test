# G1 Round 2 Review (amber)

## Findings

1. Non-blocking wording overstatement at `docs/BUG_AUDIT_amber.md:440`: the summary row still says `partial causal proof` for Bug 1. That is stronger than the revised Bug 1 body at `:19-25` and `:73-115`, which correctly limits the persisted-JSON evidence to an **upper bound** and explicitly says dominant causal attribution is unproven. This should be softened for internal consistency, but it does not block Phase B.

## Checks

### A. Revision uptake

- **Bug 1 revision adopted:** the title now reads `real schema hazard; causal share of NP failures not yet proven` (`docs/BUG_AUDIT_amber.md:19`), the status block explicitly says dominant attribution is not independently confirmed (`:22-25`), and the body now frames `121/606` as an upper bound (`:73-115`).
- **Bug 2 downgrade adopted:** severity is now `P2` (`:121`), the JSON-exposed denominators are cited explicitly (`:128-139`), and the Phase B fix is reduced to per-stratum denominator surfacing in `meta` (`:142-154`).
- **Bug 3 denominator repair adopted:** the pre/post tables now consistently use valid-orig+fo denominators for both tasks (`:237-267`).
- **Bug 5 reframing adopted:** the section now uses `known_outcome_available` rather than period as the split key (`:338-345`), includes the `115 / 217 / 274` cross-tab (`:382-399`), and upgrades the Phase B fix to `B5a'` with persisted `cpt_mode` plus a `cpt_mode` analysis arm (`:425-430`).
- **Legacy/batched divergence footnote corrected:** the audit now states that `run_single_case` also overwrites `false_outcome_flip`, so legacy and batched paths agree (`:196-202`, `:472-478`).

### B. Bug 3 rate consistency

- I independently recomputed the Bug 3 period totals from `data/results/diagnostic_2_results.json`.
- `direct_prediction.base`: `pre_valid=327`, `post_valid=272`, strict flips `10/16`, hedged flips `37/42`, union `47/58`. This matches `docs/BUG_AUDIT_amber.md:242-244`.
- `decomposed_impact.base`: `pre_valid=326`, `post_valid=263`, strict flips `0/3`, hedged flips `40/15`, union `40/18`. This matches `:265-267`.
- Spot check 1: `direct_prediction.base`, `pre_cutoff / strongly_anchored` gives `n_valid=183`, `strict=6`, `hedged=18`, `union=24`, matching `:232`.
- Spot check 2: `direct_prediction.base`, `post_cutoff / strongly_anchored` gives `n_valid=139`, `strict=7`, `hedged=21`, `union=28`, matching `:234`.
- Spot check 3: `decomposed_impact.base`, `pre_cutoff / weakly_anchored` gives `n_valid=144`, `strict=0`, `hedged=24`, `union=24`, matching `:254`.
- I did **not** find any remaining `332/272` vs `327/272` mixing inside the Bug 3 section. The remaining `39/332` and `82/274` at `:97-98` are Bug 1 NP-failure marginals, so they are not a Bug 3 denominator inconsistency.

### C. Bug 5 count check

- Independent raw-JSON cross-tab of `(period, known_outcome_available)` gives exactly:
- Raw-JSON count: `pre_cutoff, True = 115`.
- Raw-JSON count: `pre_cutoff, False = 217`.
- Raw-JSON count: `post_cutoff, False = 274`.
- This matches `docs/BUG_AUDIT_amber.md:384-388`.
- The anchor subtotals also reconcile:
- Anchor subtotal: pre/True = `73 + 42 = 115`.
- Anchor subtotal: pre/False = `114 + 103 = 217`.
- Anchor subtotal: post/False = `140 + 134 = 274`.
- So the Bug 5 mechanism is now correctly stated as a `known_outcome_available` split with a mixed pre arm.

### D. Missing P0/P1 issues

- From the **current audit wording only**, I do not see an omitted P0/P1 bug that would force a new G1 round.
- Bug 3 remains the strongest quantified P0.
- Bug 1 remains a real P0 hazard, but the revised body now correctly avoids claiming that persisted JSON proves it caused most or all of the `121/606` NP failures.
- Bug 5 is now correctly framed as a P1 probe-modality confound rather than a pure period split bug.

## Conclusion

Revision 2 materially addresses the five issues raised in round 1. The only remaining problem I found is the non-blocking Bug 1 summary-row phrase `partial causal proof`, which should be softened to match the body, but the audit is otherwise consistent enough to proceed into Phase B.

Verdict: PASS
