# BENCHMARK R4 Step 2 — Editor Shortlist Review
**Date:** 2026-04-13
**Reviewer:** Codex (senior EMNLP area chair)
**Reasoning effort:** xhigh
**Source:** 12-factor shortlist (post-Step 1 + user integration)
**Prior rounds:** BENCHMARK_R1/R2/R3_EDITOR.md + BENCHMARK_R4A_EDITOR.md
**Scope constraint:** No algorithmic specification for event-clustering or entity-annotation factors.

---

**Overall Verdict**

**LESS coherent.** The Step 1 six-factor version had a clean center of gravity: exposure opportunity, event identifiability, and news propagation breadth, with a small number of supporting variables that still read as audit-interpretability factors rather than domain-specific covariates. The expanded 12-factor draft is not incoherent, but it is noticeably more heterogeneous. It now mixes true interpretability axes, institutional/context variables, sampling-position variables, finance-market variables, and plain controls in one shortlist. That makes the paper harder to summarize, harder to defend, and harder for an EMNLP reviewer to retain.

The good news is that the draft can still support the Step 1 claim if you keep a hierarchy: `Cutoff Exposure`, `Anchor Strength`, `Propagation Intensity`, and the target/distractor form of `Entity Salience` as the conceptual spine; `Disclosure Regime`, `Target Scope`, `Structured Event Type`, and `Template Rigidity` as secondary context; `Tradability Tier`, `Session Timing`, and `Event Phase` as clearly auxiliary or conditional. If you present all 12 as co-equal "core" factors, the Step 1 claim is no longer sufficient. In that case the paper needs a weaker, broader claim such as:

On dated financial event clusters with verified outcomes, memorization audits become interpretable only when exposure opportunity, identifiability, propagation breadth, and institutional reporting context are separated from auxiliary market-structure, temporal-position, and surface-form effects.

That claim is serviceable, but plainly worse than the original.

**Per-Factor Verdicts**

1. `Propagation Intensity`: **CONCERN.** The construct belongs in the paper, but the current composite blends two narratively distinct ideas: how widely this event propagated now, and how recurrent this event family has been historically. That is defensible analytically, but less clean rhetorically.

2. `Cutoff Exposure`: **GO.** This remains one of the few factors that every reviewer will immediately understand as central to a memorization audit rather than an arbitrary benchmark covariate.

3. `Anchor Strength`: **GO.** This is still a strong identifiability axis. The planned empirical locking of the rubric helps, because it turns a potentially hand-wavy concept into a deliberate measurement choice.

4. `Entity Salience` as dual `(target_salience, max_non_target_entity_salience)`: **CONCERN.** Conceptually this is good, because it distinguishes prominence of the answer target from competition in the surrounding mention field. But it must be narrated as one construct with two sides, not as two unrelated new variables.

5. `Target Scope`: **GO.** This remains useful and venue-appropriate because it has linguistic, economic, and statistical meaning simultaneously. It helps explain when an event is about one target versus a broader field.

6. `Tradability Tier`: **BLOCK in the current main shortlist.** The integration does not solve the concern I raised in Step 1. It is still subset-restricted, still finance-coded, and still easy for hostile reviewers to read as "alpha-adjacent garnish" rather than language-scientific structure. If retained, it should be explicitly conditional and secondary.

7. `Structured Event Type`: **CONCERN.** A coarse event-type factor is reasonable, but a 7+ category ontology pushes the paper toward annotation-schema justification. That consumes attention and invites "why this inventory?" rather than helping the main claim.

8. `Disclosure Regime`: **GO.** This is one of the better additions because it connects linguistic form, institutional production process, and information availability. It reads as more than domain trivia.

9. `Template Rigidity`: **CONCERN.** This is plausible, but it is exposed to the reviewer objection that it is a surface-style proxy already partially absorbed by anchor strength, disclosure regime, and text length. It needs a disciplined supporting role.

10. `Event Phase`: **CONCERN.** The two-stage sampling idea makes it less arbitrary, but it still risks feeling like a property of your sampling protocol rather than of the event cluster itself. I would not center the paper on it.

11. `Session Timing`: **BLOCK in the current main shortlist.** My Step 1 concern carries forward almost unchanged. This is deeply finance-venue-coded, weakly portable, and hard to justify as necessary for EMNLP interpretability rather than as market microstructure seasoning.

12. `Text Length`: **GO as a control, not as a story variable.** No reviewer objects to length control; they object when length starts being sold as conceptual novelty.

**Venue Drift Audit**

Yes, the venue-drift risk is materially higher now than in Step 1. In the six-factor version, the finance setting functioned as an unusually strong audit substrate. In the 12-factor version, two visibly finance-coded variables, `Tradability Tier` and `Session Timing`, move closer to the center, while `Outcome Horizon` was dropped even though it had a clearer link to the defined outcome object. That increases the chance that reviewers see the work as a finance benchmark with NLP analysis layered on top, rather than an NLP memorization-audit paper using finance because it offers dated events with externally checkable outcomes.

My assessment is therefore: still potentially fit for EMNLP, but only if the writeup makes the hierarchy explicit and refuses to overclaim the finance-coded factors. If `Tradability Tier` and `Session Timing` are sold as peers to `Cutoff Exposure` and `Anchor Strength`, the paper drifts toward a finance venue. If they are framed as conditional stress-tests inside a broader interpretability taxonomy, EMNLP fit survives.

**Placeholder Abstract**

We study memorization audits on dated financial event clusters with verified outcomes, asking when model behavior is interpretable as potential memorization rather than general pattern completion. FinMem-Bench organizes approximately 1,000 to 1,500 event clusters around a pre-committed factor taxonomy spanning exposure opportunity, event identifiability, propagation breadth, entity structure, institutional reporting context, temporal position, and surface form. Core factors include cutoff exposure, anchor strength, propagation intensity, and entity salience; secondary analyses examine target scope, disclosure regime, structured event type, template rigidity, event phase, session timing, tradability, and text length. This design supports both audit-substrate and factor-taxonomy-driven framings while separating benchmark construction from post-hoc threshold selection. Using white-box and black-box target models, we analyze how memorization-sensitive behavior varies across dated events with different exposure, identifiability, and reporting profiles, and we release cluster-level metadata to support controlled, reproducible memorization studies.

*Why this abstract is harder than the Step 1 version:* the taxonomy is now broader than the paper's natural conceptual center. The abstract either has to enumerate heterogeneous variables, which feels cluttered, or collapse them into vague super-axes, which makes the contribution sound less sharp.

**Methodology Inputs**

1. `Extra-corpus signal principle`: **REVISE.** I support the intuition, but not the slogan as written. "External to CLS" is not by itself a justification. The rationale should be that some factors are valuable precisely because they capture real-world exposure conditions not recoverable from a single text stream, provided they still improve interpretability of language-model behavior.

2. `Event Phase two-stage sampling`: **REVISE.** This is better than a loose phase assignment, but I would present phase as sampled positional context rather than as a deep semantic property of the event. Otherwise reviewers will attack it as protocol-shaped.

3. `Anchor empirical operationalization`: **SUPPORT.** This is exactly the right kind of pre-commit discipline. It communicates that you are not backfilling a favorable definition after seeing model behavior.

4. `Pre-registered interaction menu`: **OPPOSE as currently scoped.** Five to eight exploratory 2x2 interactions is too many for reviewer defense. It reads as a multiplicity machine and invites the accusation that the factor list was built to generate interesting stories. If you want interactions, pre-register at most a very small number tied to the paper's core theory.

5. `Detector-dependent factors are R5`: **SUPPORT.** This is good scope control. It prevents the factor taxonomy from becoming entangled with detector idiosyncrasies before the base benchmark story is stable.

**C1, C2, C3**

1. **C1:** Conceptually, `Propagation Intensity` is one family, but narratively it is cleaner as two named components under one umbrella than as a single opaque composite. "Historical event-family count" is not reviewer-friendly language; it sounds engineered and pipeline-specific. A plainer recurrence/history label will travel better.

2. **C2:** A factor that applies to only 70 to 85 percent of the data can be defended only if it is explicitly conditional from the start. State that it is undefined outside company-linked events, report the exact applicable share, and ensure none of the benchmark's headline claims depends on it. If it sits in the main taxonomy without that caveat, it will read as cherry-picking.

3. **C3:** The dual salience version is a narrative asset if you explain it as "target prominence versus distractor competition." It becomes a liability only if reviewers encounter two fields without the unifying concept. The paper should sell one idea with two observable faces, not two extra knobs.

**Predicted Reviewer Objections**

1. The taxonomy is bloated and no longer theory-led.
Defense: make the four-factor spine explicit and present the rest as secondary or conditional modifiers.

2. The benchmark has drifted into finance-specific covariates with weak NLP relevance.
Defense: keep tradability and session timing clearly auxiliary and show the main conclusions stand without them.

3. Several factors overlap conceptually and may not separate cleanly.
Defense: emphasize that the goal is interpretability-oriented stratification, not a claim of orthogonal latent variables.

4. Subset-only factors create cherry-picking risk.
Defense: pre-specify applicability domains and isolate conditional analyses from benchmark-wide claims.

5. The interaction menu invites multiple-comparisons storytelling.
Defense: sharply cap interactions and tie each one to a stated hypothesis anchored in the central claim.

**Timeline Reality Check**

As of **April 13, 2026**, my answer is still **no** on **May 25, 2026** as the base plan, and the case is weaker than it was in R3 because key dependencies remain open. With R4 Step 2 still active, R5 detector work not started, factor-algorithm decisions deferred, annotation protocol deferred, and the point-in-time track deferred, you do not have enough frozen structure to support a clean end-to-end paper by May 25 without cutting quality. If the factor hierarchy and paper narrative are not frozen by **April 19-20, 2026**, then May 25 is effectively off the table. My honest updated view is: late **June 2026** for a coherent internal full draft is realistic; early-to-mid **July 2026** is a more credible target for submission-grade quality. The expanded 12-factor version slows you down because it raises not just implementation work, but exposition and reviewer-defense burden.
