---
role: Editor / narrative and venue-fit
lens: R5A Step 2 detector pool review
generated: 2026-04-15
inputs:
  - refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - refine-logs/reviews/R5A_STEP1/editor_lens.md
  - refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md
  - refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md
---

# R5A Step 2 - Editor Lens Review

## 1. Tension Rulings (T1-T7)

| Tension | Ruling vs `R5A_DEFAULTS.md` | Editorial position | Reasons |
|---|---|---|---|
| **T1. D7 EAD - standalone vs field** | **MODIFY** | Keep the computation in both roles, but treat it as **field-first** and **reserve-only** as a standalone detector. | The opening default is analytically defensible but paper-hostile. A detector that is both its own line item and a cross-detector field is hard to explain cleanly in 9 pages. For reviewers, D7 reads more naturally as the paper's shared salience moderator than as another headline detector. Promote the standalone version only if pilot evidence shows clear non-redundancy with the field view. |
| **T2. D5 SR/FO - paired vs separate** | **AGREE** | Keep **one detector slot** with **two preserved sub-measurements**. | This remains the cleanest editorial compromise. Separate headline slots would make the paper read like a perturbation suite; a single merged scalar would hide the useful distinction between polarity conflict and outcome-slot conflict. One family slot is readable, defensible, and page-efficient. |
| **T3. D2 PCSG - standalone vs fold into D3** | **MODIFY** | Keep PCSG analytically, but **fold it into the D3 surface-family presentation** unless pilot results show it materially out-explains plain D3. | As a standalone detector, PCSG is hard to sell quickly to EMNLP reviewers: it reads like a technically stronger variant of the same white-box surprise idea. Its identification value is real, but its standalone narrative value is weak. Folding it under D3 preserves the method without paying for another full detector subsection. |
| **T4. D4 ADG - deferred, now split as D4a/D4b** | **MODIFY** | Accept the temporal-session redesign: **one D4 family slot, D4b primary, D4a diagnostic**. Editorially, keep it **reserve/appendix by default**. | The temporal session fixed the conceptual shape, but it did not solve the page-budget problem. Once CMMD is in, plus D11 as a protocol, a second temporal family in main text is expensive. D4 is worth keeping in the pool because it covers within-model temporal gating, but it should earn its way into main text rather than arrive by default. |
| **T5. D8 Extraction - main text vs reserve** | **MODIFY** | Make D8 the **first reserve**, not a default main-text detector. Promote it only if pilot hit rate yields a compact but undeniable qualitative panel. | Extraction is reviewer-legible and valuable, but it is space-hungry: it wants examples, caveats, and a narrower claim. With D4/D11 added to the temporal story, the paper cannot also assume D8 gets a default main-text slot. It is the best reserve because it provides hard-edge evidence if the hit rate is there. |
| **T6. D10 Debias Delta** | **AGREE** | Drop it from the Step 2 paper-facing pool. | It is mitigation-shaped, engineering-heavy, and narratively off-axis for this paper. The temporal family is already adequately represented by CMMD, D3/PCSG, and the reshaped D4/D11 track. |
| **T7. D9 RAVEN** | **AGREE** | Drop it. | My Step 1 reason still holds, and it is stronger now: once temporal additions are in play, there is no room for a detector whose main selling point is venue familiarity. Reviewers will ask why this is not just Template Rigidity under another name. The paper is cleaner without it. |

## 2. Per-Detector Verdicts

| Detector | Verdict | Reviewer accessibility (1-5) | Paper real-estate cost | Narrative role |
|---|---|---:|---|---|
| **D1 CMMD** | **KEEP** | **4** | **Medium** - about 0.75 page | Main full-fleet temporal anchor. This is the paper's cleanest way to show why dated checkpoints matter. |
| **D2 PCSG** | **RESHAPE** | **2** | **Low if folded / Medium if standalone** | White-box temporal corroboration. Best used as the stronger paired contrast inside the D3 surface section, not as its own headline detector. |
| **D3 Min-K++ / CTS** | **KEEP** | **4** | **Medium** - about 0.6-0.8 page | Single surface-form anchor. Necessary as recognizable white-box corroboration, but should remain the only clear Bloc 1 headline detector in main text. |
| **D4 ADG** | **RESHAPE** | **3** | **High** - about 0.8-1.0 page if treated fully | Within-model temporal compliance probe. Keep one family slot with D4b primary, but reserve by default because CMMD + D11 already carry most of the readable temporal story. |
| **D5 SR/FO** | **KEEP** | **5** | **Medium** - about 0.75-0.9 page | Semantic-conflict centerpiece. Best detector for turning Anchor Strength into something reviewers can understand quickly. |
| **D6 NoOp** | **KEEP** | **5** | **Medium** - about 0.75-0.9 page | Salience/distractor anchor. Distinct from D5 and important for avoiding a purely temporal-plus-surface paper. |
| **D7 EAD** | **RESHAPE** | **4** | **Low as field / Medium as standalone** | Shared prominence moderator. Keep target-mask and non-target-mask deltas, but present them primarily as cross-detector fields rather than a main-text detector. |
| **D8 Extraction** | **RESHAPE** | **5** | **Medium** - about 0.6-0.8 page | Hard-edge corroborative exhibit. First reserve; promote only if the hit rate supports one compact figure/table with clear examples. |
| **D12 Schema-Completion** | **DROP** | **3** | **High** - about 0.8-1.0 page | Proposed Bloc 3 detector, but too overlapping with D3-style schema familiarity and too costly for the current paper shape. |

## 3. D11 Temporal Dose-Response

My position is **keep D11 only in its reshaped form: a sensitivity protocol, not a standalone detector**.

This strengthens the paper if it is presented as a compact identification stress test on top of an existing temporal detector, ideally **CMMD first** and at most **one optional secondary backend**. It dilutes the paper if it becomes a new detector line, multiple backends, a full multi-level taxonomy in main text, or a second temporal results section.

Concise presentation:

- Use **2-3 dose levels**, not the full gradient, in main text.
- Attach it to **CMMD** as the primary backend.
- Treat the **length-matched non-temporal deletion control** as mandatory and mention it explicitly in the caption or methods sentence.
- Spend about **0.5 page total** in main text: one short methods paragraph, one compact figure panel, one short results paragraph.
- Push the full taxonomy, adjunct-type details, and any second backend to supplement.

## 4. Bloc 3 Coverage

I choose **Option 3**.

Bloc 3 should be covered through **cross-detector stratification and interaction reporting**, not through a dedicated new detector in this paper. That is the only choice that fits both the page budget and the current state of the factor schema. A dedicated Bloc 3 detector would be easier to justify if `Disclosure Regime` were already frozen and if the paper had spare room, but neither condition holds.

D12 does not clear the bar. It would cost almost a full extra detector subsection while inviting immediate overlap questions with D3 and general surface familiarity. Editorially, that is the wrong trade for a 9-page EMNLP paper.

## 5. Pool Architecture

I choose **alternative: a hybrid "A-lite" architecture**.

The paper should present **4 headline detector families in main text**, but only where the internal sub-measurements are conceptually inseparable:

- D5 as one family slot with SR and FO inside it
- D3 as the single surface-family slot, with PCSG folded under it
- D1 as the main temporal fleet detector
- D6 as the main salience/distractor detector

Then treat the rest as supporting layers:

- D7 as a cross-detector field
- D11 as a cross-detector sensitivity protocol
- D4 and D8 as reserve/appendix detectors

This reads better than pure Architecture A because it does not try to hide a large detector count behind too many family labels. It reads better than pure Architecture B because it lets inseparable variants stay attached to their parent detector instead of pretending they are independent headline methods.

## 6. Open Questions

### Q1-Q2. Chinese counterfactual-edit and NoOp admissibility

The minimum editorial admissibility standard is:

- A **frozen, rule-bound edit protocol** by event type, not open-form LLM rewriting.
- A **human audit sheet** that separately scores naturalness, semantic faithfulness, and target isolation.
- A **logged rejection taxonomy** so failures are reportable rather than hand-waved away.
- A **high pass-rate threshold** before main-text promotion. My editorial threshold is roughly **85%+** on the audited subset.

For NoOp specifically, a clause bank without explicit target-irrelevance proofs is not main-text ready. If those proofs cannot be documented, D6 should move to reserve.

### Q3. SR/FO rewrite naturalness - ownership and acceptance protocol

Ownership should sit with the **benchmark authorship team**, not with annotators and not with a general-purpose LLM. Concretely:

- Maintain a **small frozen lexicon/template bank per event type**.
- Require one **editorial owner** to keep phrasing consistent across event types.
- Require one **domain-aware reviewer** to verify that the edit preserves CLS style and changes only the intended semantic slot.

Acceptance protocol:

1. Generate from the fixed schema.
2. Human-audit for style and semantic correctness.
3. Reject anything that sounds translated, over-explicit, or structurally unlike CLS.
4. Report pass rates and failure modes in supplement.

### Q4. NoOp clause length and discourse position

The safest editorial constraint is **one short clause only**:

- Roughly **8-20 Chinese characters**, or clearly under **15% of the host sentence/article length**.
- Do **not** place it in the headline, opening anchor sentence, or final outcome sentence.
- Prefer insertion in a **supporting middle position** where finance wire prose naturally tolerates an aside.
- Do **not** place it adjacent to the decisive numeric or outcome token.

If the clause needs more than one sentence or visibly changes discourse flow, it stops being a NoOp and starts being a rewrite.

### Q5. Disclosure Regime freeze vs possible Modality replacement

This does **not** need to block the detector shortlist if the paper writes at the broader level of **institutional formality / source modality**.

Arguments that mostly survive unchanged:

- D1 CMMD on more canonical institutional text
- D3 on schema-rigid formal text
- D5 on sharper factual conflict in formalized disclosure-style language
- D8 on easier extractability from templated institutional prose

Arguments that need rewriting if `Disclosure Regime` becomes `Modality`:

- D6's commentary-vs-formal asymmetry should be rewritten as **high-slack vs low-slack source form**
- Any dedicated Bloc 3 detector pitch, especially D12, should be reconsidered from scratch

Editorially, I would freeze the paper language now around the broader construct and avoid detector claims that require a finer institutional taxonomy than the project has actually frozen.

### Q11. CMMD reproducibility presentation

CMMD can stay central **only if the fleet is frozen before writing**.

What must exist:

- One **version-locked fleet table** with exact checkpoints/providers/dates
- Explicit **same-cutoff falsification pair(s)** in the methods framing
- A note on **hosted-model routing stability** in supplement

If that evidence is unavailable by paper-writing time, CMMD should be demoted from centerpiece to corroborative temporal evidence. The fleet review improved this materially by giving CMMD a cleaner falsification story; it did not eliminate the need for checkpoint discipline.

### Q12. How to present D3 if it only runs on 3 white-box models

Present D3 as **white-box corroboration**, not as a co-equal fleet-wide detector.

Best presentation:

- Give D3 its own clearly labeled **3-model white-box panel/subsection**
- Do **not** rank or average it directly against full-fleet detectors in one omnibus table
- Compare **directional agreement** with D1/D5/D6, not raw effect-size magnitude
- State plainly that D3 answers a different question: "when logprobs are available, do white-box signals point the same way?"

That framing is reviewer-accessible and avoids the misleading impression that every detector ran on the same evaluation substrate.

## 7. Paper Structure Sketch

For the shortlist I recommend below, the 9-page paper should be budgeted roughly as:

- **Introduction + related-work framing:** 1.5 pages
- **Methods:** 3.0-3.25 pages
- **Results:** 3.0-3.25 pages
- **Discussion/limitations:** 0.75-1.0 page
- **Conclusion:** 0.25-0.5 page

Main-text display budget should stay near **3 figures + 2 tables** maximum:

- **Table 1:** detector overview, access type, and narrative role
- **Table 2:** fleet/factor/reproducibility summary
- **Figure 1:** main detector-by-factor results matrix
- **Figure 2:** compact temporal panel (CMMD plus D11 sensitivity)
- **Figure 3:** one counterfactual or extraction qualitative panel

If a fifth detector is promoted into main text, one figure or one table likely has to move to supplement.

## 8. Proposed Main-Text Shortlist

### Main text (4 detectors)

1. **D5 SR/FO**
2. **D6 NoOp**
3. **D1 CMMD**
4. **D3 Min-K++ / CTS** with **D2 PCSG folded underneath as a supporting paired contrast**

This is the cleanest 4-detector spine for a 9-page EMNLP paper:

- two counterfactual detectors with distinct stories reviewers can remember
- one full-fleet temporal detector
- one white-box surface corroborator

It covers the main conceptual ground without turning the paper into a detector catalog. It also preserves the strongest venue-fit property: each main detector has a crisp one-sentence explanation.

### Reserve (1-2 detectors)

- **First reserve: D8 Extraction**
- **Second reserve: D4 ADG** with D4b primary and D4a diagnostic

D8 is the better first reserve because, if its hit rate is real, it gives the paper unmistakable hard-edge examples. D4 is the better second reserve because it is conceptually useful but harder to explain quickly and too expensive to assume into main text.

### Cross-cutting, not counted as headline detectors

- **D7 EAD** as a shared salience field
- **D11** as a temporal sensitivity protocol

## 9. Blocking Issues

These are the Step 2-visible issues that should block R5A closure if unresolved:

1. **No explicit audit protocol for D5/D6.** If the project cannot state the deterministic edit schema, audit criteria, and pass threshold, the two most editor-friendly detectors are not yet publication-ready.
2. **No reproducibility freeze for CMMD.** If checkpoint/provider locking and the falsification pair story are not frozen, D1 cannot safely anchor the narrative.
3. **No main-vs-reserve architecture decision.** R5A should not close with a pool that is still effectively 7-8 active detectors. The paper-facing shortlist has to be frozen now, even if the wider analytical pool remains broader.

These should **not** block R5A closure under the architecture above:

- `Disclosure Regime` vs `Modality` label refinement, so long as Bloc 3 stays stratified rather than detectorized
- D11 adjunct-coverage uncertainty, so long as D11 remains secondary
- D12, which I recommend dropping

