---
role: Quant / alpha-bridge
session: R5A Temporal Cue Design
thread_id: 019d93f4-ec74-7471-8020-a0cddbd84235
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## Block A — Temporal cue taxonomy

**Recommendation:** use a **multi-dimensional annotation** and derive a reporting gradient from it. From the alpha-contamination lens, the decisive axis is not raw visibility but **lookup dependency**: does the text hand the model a time anchor directly, or does it force an entity/event-to-date retrieval from training memory?

The three useful axes are:

- `surface_resolution`: exact in-text date/time, partial in-text calendar cue, relative/ordinal cue, none.
- `lookup_dependency`: none, local-context completion, closed-reference memory lookup, diffuse/open-world inference.
- `editability_role`: adjunct/removable versus subject/intrinsic.

I would keep the user's `L4/L3/L2/L0.5/L0/L1` ladder as a **derived shorthand**, but not as the annotation primitive.

- Do **not** merge `L2` and `L0.5`.
- `L2` cues such as `上周`, `Q1`, `去年同期` usually resolve from article-local chronology or simple calendar completion.
- `L0.5` cues such as `第五届WAIC` or `《个保法》发布后` require a stored event-to-date mapping. That lookup is itself the memorization channel that can let a model "cheat" on downstream alpha tasks.
- Treat `L3` as **in-text partial anchoring**, not true external lookup. Missing year completion is shallow context completion, not the same construct as a closed-reference retrieval.
- Treat `L0.5` adjunct versus subject as a **separate axis**, not a sub-level. It matters for intervention feasibility, not for time recoverability itself.

For articles with multiple cues, the label should be a **vector**, not a single max/min class. I would store:

- `max_surface_resolution`
- `max_lookup_dependency`
- `has_closed_reference_cue`
- `has_removable_temporal_adjunct`
- `cue_count`

For article-level reporting, the main summary should be the **strongest recoverable cue** plus a separate flag for **closed-reference presence**. If a wire contains both `2024年3月15日` and `第五届WAIC`, the explicit date dominates chronology, but the closed-reference cue still matters as a memorization fingerprint.

**Annotation protocol:** hybrid, not pure LLM.

- Rule-based extraction should handle exact dates, clock times, report periods, and common relative expressions.
- LLM or ontology-assisted extraction should target closed-reference spans such as named conferences, laws, policy titles, and regime markers.
- Human double-coding should adjudicate `lookup_dependency` and `editability_role` on an audited subset.

**Realistic reliability target:**

- explicit-cue detection F1 above `0.90`
- article-level weighted kappa / Krippendorff alpha at least `0.75`
- binary agreement on `has_closed_reference_cue` and `adjunct vs subject` at least `0.80`

This also avoids direct overlap with `Anchor Strength`: anchor strength is general event addressability, while the temporal-cue scheme isolates **time-specific retrieval dependence** and **time-cue removability**.

## Block B — Time cue as factor vs manipulation variable vs both

**Recommendation:** **both**, but the manipulation path is more valuable than the observational path.

As a factor, I would add a narrow text-side Bloc 0 field called **`Temporal Anchor Recoverability`**, not a vague "temporal clarity" factor.

- Hierarchy: `secondary`, not spine.
- Bloc: `Bloc 0`, with an explicit note that this is a **text property**, unlike case×model `Cutoff Exposure`.
- Construct caveat: it measures how easily the text can unlock a time-specific retrieval key, not whether the model truly understands chronology.
- Literature provenance: `PARTIAL` prior art, `NOVEL` operationalization.

The reason not to fold it into `Anchor Strength` is exactly the intervention property surfaced in the brief: time cues can often be removed with a minimal semantics-preserving edit, while most other anchor components cannot.

As a manipulation variable, temporal cues are extremely high value for the alpha story.

- Removing or downgrading the time cue directly tests whether a model's apparent alpha survives once the most obvious retrieval key is weakened.
- The dose-response slope should be treated as a detector-level output, not just as preprocessing.
- For Thales, this is operationally useful as a **contamination haircut**: if the signal collapses when time cues are stripped, the original alpha is suspect.

My working prior is that **adjunct-type removable cues are a majority but not universal** in CLS. I would budget for roughly `60%` evaluable coverage and set a hard design checkpoint:

- if audited removable coverage is below `50%`, the manipulation path should be narrowed to an explicit sub-benchmark rather than sold as benchmark-wide.

Observation and manipulation are complementary, not redundant.

- The factor path gives **ex ante stratification**: which texts are structurally easy to time-anchor.
- The manipulation path gives **causal attribution**: whether the detector or alpha signal actually relies on that time anchor.

Interaction with `Cutoff Exposure` is a feature, not a collinearity bug.

- `Temporal Anchor Recoverability` is the text-side key.
- `Cutoff Exposure` is the model-side opportunity set.
- The high-risk region is their interaction: strong recoverable time anchors on cases inside a model's possible exposure window.

## Block C — D4 ADG redesign

**Recommendation:** split the construct, but keep it as **one detector family slot**. Make **D4b** the primary measurement and **D4a** a diagnostic companion.

- `D4a ADG-Contradiction`: original text keeps the temporal cue, prompt injects a conflicting as-of date.
- `D4b ADG-Misdirection`: text is time-masked first, prompt injects the as-of date.

These are distinct constructs.

- `D4a` measures **temporal source arbitration** under text-prompt conflict. It is partly an instruction-following test.
- `D4b` measures **chronology-gating compliance once the text no longer rescues the model**. This is much closer to the alpha-contamination problem.

From the quant lens, `D4b` is more relevant.

- It asks whether a model can be fenced into a point-in-time information set after the textual time anchor is removed.
- That maps directly to backtest integrity and to Thales-style as-of deployment controls.
- `D4a` is still useful, but mainly as a probe of whether memorized text cues override a prompt boundary.

Expected factor relevance:

- `D4a`: strongest interaction with `Temporal Anchor Recoverability`, `Anchor Strength`, and possibly `Session Timing`.
- `D4b`: strongest interaction with `Cutoff Exposure`, `Anchor Strength`, and entity-driven retrieval risk.

Relative to `D1 CMMD`, ADG is complementary rather than redundant.

- `CMMD` says which models behave suspiciously in a cutoff-ordered fleet.
- `D4b` says whether a given model can obey a point-in-time fence when explicitly asked to do so.
- Joint failure is strong evidence that apparent alpha is partly memorized post-event knowledge.

**Compute:** running both sub-detectors at full scale (`76,800` calls) is not justified at this stage.

- Run `D4b` first as the real candidate detector.
- Run `D4a` on a stratified calibration subset or keep it appendix-only unless pilot evidence shows unique value.

The "matching as-of date" condition in `D4a` is useful as a **control**, but only as calibration. It should not double the main budget.

## Block D — D11 Temporal Dose-Response Delta

**Recommendation:** **adopt, but reshape.** D11 should not be a standalone full-grid detector. It should be a **temporal stress-test layer** applied to a small number of high-value parent detectors.

My preferred initial parents are:

- `D1 CMMD`
- `D5 FO` first, then `D5 SR` if FO passes audit
- optional `D3` on the local white-box models

This gives D11 the same practical role EAD already has in Step 1 logic: both a standalone summary output and a wrapper on parent detectors.

For downstream use, Thales would absolutely want the per-case curve, or at least a compressed statistic such as:

- `temporal_reliance_delta = score(raw) - score(time-masked)`
- `temporal_reliance_slope` across `raw -> downgraded -> masked`

That statistic is directly usable as an alpha filter.

- large delta: hard veto or heavy haircut
- moderate delta: downweight
- flat curve: keep the signal, subject to the rest of the detector stack

**Success condition:** D11 is persuasive only if score decay is:

- monotone as temporal clarity is reduced
- concentrated in exposure-possible cases
- strongest on high `lookup_dependency` cases, especially closed-reference cues
- larger than a matched non-temporal deletion control of similar length

Without the matched non-temporal control, D11 can collapse into generic information-loss.

That generic information-loss channel is the dominant failure mode.

- Removing tokens often lowers confidence even for clean models.
- D11 needs a placebo edit, not just a temporal edit.

On subject-type `L0.5` cases, I would not force the design.

- exclude them from causal dose-response estimation
- keep them in the observational factor analysis
- if the non-evaluable share exceeds roughly `30%`, D11 should be framed as a **targeted sub-benchmark**, not a benchmark-wide detector

**Cost:** the full `4 versions × 6 models × 3,200 cases` plan is too expensive for first adoption.

- start with `2-3` versions, not `4`
- run on a stratified subset or on a reduced detector parent set
- expand only if pilot curves clearly separate known-leakage cases from placebo cases

`D11` and `D4b` are complementary, not substitutes.

- `D11` manipulates the **textual supply** of temporal anchors.
- `D4b` manipulates the **prompt-level time boundary** after text masking.
- They can share the same masked-text asset, but they answer different questions.

So D11 should not be said to subsume D4b. It only subsumes part of the preprocessing.

## Block E — Time-handling rules for D5/D6/D7

**Recommendation:** no single preserve/remove rule across all perturbation detectors. Use a **global principle** with per-detector defaults.

The global principle should be:

- preserve original temporal cues unless the detector is explicitly testing temporal sensitivity
- never introduce a new conflicting time cue inside a perturbation unless temporal conflict is the target construct

For `D5 SR/FO`, the default should be **preserve the original date**.

- From the alpha lens, this is the realistic test. Backtests and production pipelines consume dated news, and the contamination channel is often exactly `date + entity + outcome`.
- If a counterfactual only fails when the original date stays in place, that is not a flaw. It is evidence that the model is leaning on a time-anchored memory trace.
- If cleaner construct separation is wanted, add a secondary time-masked audit on a subset. Do not make time removal the default.

For `D6 FinMem-NoOp`, the inserted clause should **not carry its own temporal cue by default**.

- A new time cue can silently stop being a no-op.
- If a temporal phrase is unavoidable for CLS naturalness, it should match the original article's time window exactly.
- A deliberate mismatch belongs under the temporal detector family, not NoOp.

For `D7 EAD`, do **not** expand the core taxonomy from `2×2` to `2×2×2` in the main design.

- Core EAD should preserve time cues so it remains an entity-prior detector.
- Temporal masking should be handled by D11 or a small appendix pilot, not by turning EAD into an 8-cell matrix.

These defaults can be chosen without waiting for pilots because they follow from construct discipline:

- `D5`: realism first, preserve time
- `D6`: keep the no-op truly no-op, avoid new time content
- `D7`: isolate entity effects, keep time fixed

Pilots should test only the **secondary temporal variants**, not the core defaults.

## Cross-block synthesis

From the quant / alpha-bridge lens, temporal cues matter because they are not just another component of `Anchor Strength`. Closed-reference cues in particular are a **direct retrieval key**: the model can map `第五届WAIC` or `《个保法》发布后` onto a date and then use memorized post-event knowledge to manufacture apparent predictive power. That is why `lookup_dependency` is the critical taxonomy axis.

This leads to one clear design stance: temporal cue handling should be **both observed and intervened on**, but the intervention path is more valuable. A narrow Bloc 0 text factor such as `Temporal Anchor Recoverability` is useful for stratification, yet the bigger contribution is causal. If detector scores or alpha signals collapse when removable time cues are downgraded, the benchmark has identified a concrete contamination mechanism rather than just another correlation.

That logic also resolves D4 and D11. `D4b` is the temporal detector that matters most for production-style alpha control because it tests whether a model can obey an as-of fence once the text stops handing it a date. `D4a` is informative but secondary because text-prompt contradiction adds an instruction-hierarchy confound. `D11` is worth adopting only as a stress-test layer on a small set of parent detectors, where its output becomes a usable Thales control signal: veto, haircut, or triage.

The main tension with Step 1 is detector proliferation inside Bloc 0 and potential overlap with `Anchor Strength`. The fix is scope discipline. Keep the new factor narrow, keep `D4` as one family slot with `D4b` primary, and treat D11 as a wrapper rather than a new heavyweight standalone detector. The temporal stack then becomes coherent instead of bloated: `CMMD` for cross-model cutoff disagreement, `D4b` for within-model gating failure, and `D11` for time-anchor elasticity.

Questions for other lenses:

- `Stats`: what is the minimum matched-control design that distinguishes temporal-cue removal from generic information loss in D11?
- `NLP`: can the closed-reference inventory and adjunct-versus-subject split be made rule-assisted enough to annotate at scale on CLS?
- `Editor`: can `CMMD + D4b + D11-wrapper` live as one temporal family in the paper architecture without over-weighting Bloc 0?
