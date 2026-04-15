# BENCHMARK R4 — Post-v5.2 Integration Review
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher + PM lens)
**Reasoning effort:** xhigh
**Purpose:** Final cross-document consistency check before handoff to fresh session
**Prior review:** BENCHMARK_R4_FINAL_REVIEW.md (cold reader, caught 11 issues; this review verifies they were applied)

---

**1. Executive Verdict**

**GO-WITH-FIXES.** The R4 closure set is substantively solid and mostly handoff-ready: the decision document now clearly states the dependent variable, captures the cold reader's construct-collapse concern, and routes major execution dependencies to explicit downstream tracks. A fresh session can do productive work. The remaining problems are integration-level, not conceptual: v5.1's Reprint Status drop was not fully propagated, v5.2's Event Type hierarchy was not fully synchronized with the sampling/power language, and `BENCHMARK_R5_KICKOFF.md` still reflects v5-era assumptions rather than v5.2. These are fixable editorial inconsistencies, but they are worth fixing before treating the packet as a clean handoff bundle.

**2. Cold-reader Fix Verification**

1. Edit 1: dependent-variable sentence.
Status: **APPLIED**.
Evidence: `docs/DECISION_20260413_mvp_direction.md`, section `Dependent variable (one-sentence definition)`.

2. Edit 2: replace stale "What R4 should produce" with post-R4 outcome language.
Status: **APPLIED**.
Evidence: same file, sections `What R4 can assume (frozen inputs for factor investigation)` and `What R4 produced (post-closure)`.

3. Edit 3: reconcile D13/D14 with v4 values.
Status: **APPLIED**.
Evidence: same file, section `Decisions locked in v3 (new)`, where D13 is `5-7` interaction pairs and D14 is the `150-case` anchor experiment.

4. Edit 4: replace "canonical selection deferred to Thales" with "P2 fixes the rule; Thales operationalizes it."
Status: **PARTIALLY APPLIED**.
Evidence: `Principle P2` does exactly this and explicitly says Decision 3/6 are superseded for canonical selection. But earlier sections still say the selection rule is deferred: `Decision 3`, `Decision 6`, and `Open tracks`.

5. Edit 5: split Propagation Intensity into two stored primary variables and make the composite secondary.
Status: **APPLIED**.
Evidence: factor block `Propagation Intensity`, especially the `Construct caveat (v5)` stating `event_burst` and `historical_family_recurrence` must be stored separately and analyzed independently in primary analyses.

6. Edit 6: split Entity Salience into target and competing-entity prominence.
Status: **APPLIED**.
Evidence: factor block `Entity Salience`, which defines `(target_salience, max_non_target_entity_salience)` and says they must be reported as distinct effects.

7. Edit 7: replace P1 prose with an auditable per-factor table.
Status: **APPLIED BUT INCOMPLETE**.
Evidence: `Principle P1` now contains an audit table. But the table still includes `Reprint Status (reserve)` and the old extra-corpus count after v5.1 dropped that factor.

8. Edit 8: replace P2 with a fully specified algorithm.
Status: **APPLIED**.
Evidence: `Principle P2` now specifies distribution, labeling precedence, no-match handling, tie-breakers, seed, and audit fields.

9. Edit 9: strengthen P3 with paired bootstrap and explicitly pilot-screen framing.
Status: **APPLIED BUT INCOMPLETE**.
Evidence: `Principle P3` now uses paired-bootstrap α differences and explicitly reframes the study as a reliability screen, not construct validation. However, the cold reader also asked for randomized rubric order, and that piece is absent.

10. Edit 10: rename overclaiming factor names unless justified.
Status: **APPLIED BUT INCOMPLETE**.
Evidence: v5 version history explicitly says the factors were **not renamed**; instead, construct caveats were added to `Cutoff Exposure` and `Template Rigidity`. This addresses the substance, but not the literal rename request.

11. Edit 11: soften closure language to "conceptually closed; execution gates remain."
Status: **APPLIED**.
Evidence: `R4 status: CONCEPTUALLY CLOSED — execution gates remain` in both the decision doc and final synthesis.

Risk R4, the cold reader's "biggest single risk," is now substantively captured well in v5.2. The section `Risk R4 — Construct collapse into a prominence/repetition proxy benchmark` is explicit, concrete, and linked to actual mitigations. The only remaining weakness is editorial sync: it still references `Reprint Status` after that factor was dropped.

**3. New Issues Introduced Since v5**

- Reprint Status drop was **not fully propagated**. It breaks or partially stales `Principle P1` prose, the P1 audit table, the extra-corpus count, `Risk R4` bloc 1, `What R4 produced` reserve-item count, and the R5 kickoff's construct-collapse guidance. Decision 5's `is_reprint` metadata flag is still coherent; the breakage is in factor-list sync, not in the data model.

- The v5.2 hierarchical Event Type note is conceptually good, but it **does conflict with older power/sampling language**. `Structured Event Type` now says fine `15-20` labels are descriptive and coarse `5-7` labels are confirmatory. But `Target N and sampling strategy` still says `Event Type: each of the 7+ categories has ≥ minimum cell`, which reads like the old flat taxonomy.

- The Modality/Disclosure deferral leaves factor 7 in a **placeholder state**. v5.2 is honest about this: Disclosure Regime remains in the shortlist for now, but Modality may replace it later. The ambiguity arises because `BENCHMARK_R5_KICKOFF.md` says the 12-factor list is locked, without flagging this one unresolved placeholder decision.

- The Thales dedicated sync session does **not directly conflict** with the Thales-joint factor algorithm session, but the boundary is blurry. Both now touch Event Type. The clean reading is: dedicated sync informs taxonomy/prompt-reuse decisions; Thales-joint algorithm session owns final operational freeze. That ownership should be stated explicitly.

- The CMMD fleet section in v5.2 is now ahead of the R5 kickoff. v5.2 says there is an accepted 6-model reference fleet; `BENCHMARK_R5_KICKOFF.md` still frames CMMD model choice as open candidate exploration. That is stale, not fatal.

**4. Cross-document Consistency Checks**

- **v5.2 <-> CMMD survey**: Mostly consistent. The 6-model list matches, the `2023-10 -> 2025-07` span matches, the `~$6 API + 8 GPU-hours` estimate matches the survey's `$6.30 + 8 GPU-hours`, and the reproducibility landmine is correctly captured around pinned dated checkpoints and provider routing. Minor omission: v5.2's "pinning landmine" sentence mentions `-0324` and `-20250929` but not `-0414`, although GLM-4-9B-0414 is listed correctly.

- **v5.2 <-> Thales review**: Mostly consistent. v5.2 correctly reflects the 13-type EventType finding, the 7-value Modality enum, the 8-value Authority enum, and the recommendation that Modality is richer than the current Disclosure Regime placeholder. One attribution gap: the hard claim that CLS lacks a publisher/source field is not a finding from `THALES_SIGNAL_PROFILE_REVIEW.md` itself; that review only said "verify first." v5.2 appears to incorporate later user confirmation.

- **v5.2 <-> R4 final synthesis**: Core agreement is good. Both agree that R4 produced a 12-factor shortlist, 5 principles, execution gates, and 30 Step-1 proposals. But the synthesis is stale relative to v5.1/v5.2: it still references v4/v5, still talks like there are 4 reserve items, and its frozen-input handoff mentions risks R1-R3 rather than R1-R4.

- **R4 lit sweep kickoff <-> v5.2**: Largely aligned. It correctly scopes factor provenance gaps, includes CMMD baseline investigation, and includes Modality/Authority as possible additions rather than active changes. The main miss is required-reading completeness: if Modality and Authority are in scope, `docs/THALES_SIGNAL_PROFILE_REVIEW.md` should also be required reading.

- **R5 kickoff <-> v5.2**: Not fully aligned. The kickoff still points to v5, omits the CMMD survey from required reading, carries stale Reprint language, and does not absorb the accepted 6-model CMMD reference fleet. It also does not acknowledge that Disclosure Regime is being held as a placeholder pending a possible Modality swap.

- **R4 lit sweep kickoff <-> R5 kickoff**: This is the biggest handoff-sequencing inconsistency. The lit-sweep kickoff says the broad literature sweep is a predecessor to R5. The R5 kickoff says broad review should be after R5, with only a targeted detector sweep inside R5. Those are different plans. The work most at risk of falling between the cracks is factor-level provenance, DatedGPT/Chrono baseline evaluation, and literature around Modality/Authority.

**5. Handoff Readiness Test**

For `BENCHMARK_R4_LIT_SWEEP_KICKOFF.md`: **yes, a fresh session can start immediately** from the kickoff plus required reading. The scope is explicit, outputs are concrete, and the required-reading list is almost sufficient. The main implicit dependency is `docs/THALES_SIGNAL_PROFILE_REVIEW.md`, since the kickoff asks the new session to assess Modality and Authority literature.

For `BENCHMARK_R5_KICKOFF.md`: **R5A can start, but not cleanly; R5B cannot**. A fresh session can do productive conceptual detector work, but it should first correct for stale context by reading v5.2 and `docs/CMMD_MODEL_FLEET_SURVEY.md`. The kickoff alone is not fully self-sufficient because it cites v5 instead of v5.2, assumes a missing `infra_capabilities.md` memory, and understates late-stage state changes around CMMD, Reprint drop, and Disclosure Regime/Modality.

**6. Factual Integrity Spot Checks**

| Claim | Source checked | Result |
|---|---|---|
| v5.2 says CMMD span is `2023-10 -> 2025-07` (`21 months`) | `docs/CMMD_MODEL_FLEET_SURVEY.md`, sections 1-2 | **Verified** |
| v5.2 says Thales has `13` EventType categories and FinMem draft had `7` | `docs/THALES_SIGNAL_PROFILE_REVIEW.md`, section 2 | **Verified** |
| R4 synthesis / v5.2 say Step 1 produced `30` factor proposals (`8 + 7 + 9 + 6`) | Counted `^### Factor:` in the four R4A docs; matches `BENCHMARK_R4A_SYNTHESIS.md` | **Verified** |
| v5.2 says DatedGPT is a family of `12 x 1.3B` models with annual cutoffs `2013-2024` | `related papers/notes/temporal_lookahead.md` | **Verified** |
| v5.2 says Risk R4 is mitigated partly via the `tail-entity diagnostic` interaction pair | `Principle P4` in v5.2 | **Verified** |
| `What R4 produced` says there are `4 reserve items` | Current factor hierarchy in v5.2 shows only `3 reserve` items after Reprint drop | **Failed / stale** |

**7. Remaining Open Questions for the User**

1. Should the standalone R4 literature sweep remain a hard predecessor to R5, or do you want R5A to proceed first with only a detector-specific targeted sweep?
2. Is `Disclosure Regime` actually frozen for R5, or do you want an explicit exception allowing a `Modality` swap before R6 if the Thales sync justifies it?
3. For `Structured Event Type`, which label layer is balance-gated: the coarse `5-7` confirmatory groups only, or something broader?
4. Should R5 treat the 6-model CMMD fleet from v5.2 as the default starting point unless amended, or reopen fleet choice from scratch?
5. Is the "CLS raw schema lacks publisher/source metadata" fact fully settled, or should a later session still verify it once before closing off metadata-based Authority?

**8. Concrete Edit Proposals**

1. Replace the P1 prose in `docs/DECISION_20260413_mvp_direction.md` with a v5.2-synced version that removes Reprint coverage and `historical event-family frequency` from the "extra-corpus" examples and states that only `Tradability Tier` is currently a pure extra-corpus active factor.

2. Replace the `Reprint Status (reserve)` row and the `Extra-corpus count: 2 ...` line in the P1 audit table in `docs/DECISION_20260413_mvp_direction.md` with text stating that P1 is currently tight and `Authority` is only a deferred restoration candidate.

3. Replace `Reprint Status` in `Risk R4` bloc 1 in `docs/DECISION_20260413_mvp_direction.md` with the current active repetition bloc: `Propagation Intensity`, `Template Rigidity`, and `surface_template_recurrence`.

4. Replace `4 reserve items + 4 dropped candidates` in `What R4 produced` in `docs/DECISION_20260413_mvp_direction.md` with `3 reserve items + 5 dropped candidates`.

5. Replace the canonical-selection-deferred wording in `Decision 3`, `Decision 6`, and `Open tracks` in `docs/DECISION_20260413_mvp_direction.md` with `P2 fixes canonical selection; the Thales-joint session only operationalizes phase labeling, tie-breakers, QC, clustering, and entity extraction.`

6. Replace `Event Type: each of the 7+ categories has ≥ minimum cell` in `Target N and sampling strategy` with `Coarse confirmatory Event Type groups (5-7 bins) must meet minimum cell; fine 15-20 labels are descriptive only and are not balance-gated.`

7. Replace `v5` with `v5.2` in `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`, and add `docs/CMMD_MODEL_FLEET_SURVEY.md` to the required-reading list.

8. Replace the Reprint reference in the `Risk R4` guidance in `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md` with `Propagation / Template / surface reuse`, since Reprint is no longer an active factor.

9. Replace the open candidate-model enumeration under `CMMD feasibility` in `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md` with `Start from the v5.2 six-model reference fleet, then verify/pin or amend with justification.`

10. Replace the required-reading list in `refine-logs/reviews/BENCHMARK_R4_LIT_SWEEP_KICKOFF.md` with a version that also includes `docs/THALES_SIGNAL_PROFILE_REVIEW.md`, and add one sentence clarifying that this kickoff owns the broad factor/provenance sweep while R5 only owns the detector-family sweep.
