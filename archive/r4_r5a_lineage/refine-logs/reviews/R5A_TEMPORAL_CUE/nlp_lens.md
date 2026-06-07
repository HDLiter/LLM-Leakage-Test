---
role: NLP / methodology
session: R5A Temporal Cue Design
thread_id: 019d93f5-3309-73d0-8a12-0b637b9015d7
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## Block A Answer

Use a **multi-dimensional taxonomy**, not a single scalar. The scalar can be derived later for reporting, but it is too lossy for annotation and too coarse for construct work.

| Code | Surface type | What date recovery requires | Expected κ if coded directly |
|---|---|---|---|
| `T4` | Exact absolute date/time in text | none | `0.90–0.95` |
| `T3` | Deictic or incomplete but context-completable: `今日`, `3月15日`, `周五` | document/publish context | `0.80–0.88` |
| `T2` | Relative or interval: `上周`, `Q1`, `去年同期` | calendar/discourse anchoring | `0.75–0.85` |
| `T1` | Closed-reference anchor: `第五届WAIC`, `《个保法》发布后` | world-memory / entity→date lookup | `0.65–0.78` |
| `T0` | Open implicit temporal relation: `新政府上任后` | broad world inference | `0.55–0.70` |
| `N` | No temporal cue | none | `0.90+` |

Add two extra axes:

- `lookup_dependency`: `none / doc_context / calendar_discourse / world_memory / open_inference`.
- `semantic_role`: `adjunct-removable / core-subject / mixed`.

Design choices:

- Do **not** merge `L2` and `L0.5`. They look similar on "not fully explicit," but they load on different mechanisms: `L2` is calendrical reasoning; `L0.5` is memory lookup. That distinction is methodologically load-bearing.
- Treat `L3` as **context-completable**, not fully explicit and not memory lookup.
- Treat `subject-type vs adjunct-type` as a **separate axis**, not a sub-level. It matters for D11 feasibility, not for cue clarity itself.
- For articles with multiple cues, do **not** take max or min only. Store a **cue inventory** plus one `primary_event_anchor`. Derive:
  - `primary_anchor_type`
  - `max_recoverability`
  - `has_world_memory_anchor`
  - `removability_path`
- If you need one ordered field for analysis, use `primary_event_anchor` with `T4 > T3 > T2 > T1 > T0 > N`, but treat it as **ordinal**, not interval.

Annotation protocol:

- Use a **hybrid pipeline**: rule-based span proposal first, then LLM-assisted classification, then human adjudication on all disagreements plus random audit of agreements.
- Report `weighted κ` for ordinal primary type, plus `AC1` because class imbalance will be strong.
- Realistic targets:
  - `primary_anchor_type`: `weighted κ >= 0.80`
  - `lookup_dependency`: `κ ~ 0.75`
  - `semantic_role`: `κ ~ 0.70` overall, higher on the closed-reference subset
- If `T0` vs `N` falls below `κ = 0.67`, collapse them analytically but keep `N` as the manipulation endpoint.

## Block B Answer

It should be **both** a factor and a manipulation variable.

As a factor:

- I would name the construct **Temporal Anchor Recoverability**. If you keep the user-facing label "temporal-cue clarity," the paper should state that the operational construct is **recoverability of event time from text**, not generic temporality.
- Hierarchy: **secondary**.
- Bloc: **Bloc 0**, with an explicit caveat that Bloc 0 now contains both:
  - a case×model temporal variable (`Cutoff Exposure`)
  - a pure text temporal variable (`Temporal Anchor Recoverability`)
- Provenance: **PARTIAL prior art, novel operationalization**.

Construct-validity framing:

- In Cronbach-Meehl terms, this is **not memorization itself**.
- It is a **text-side affordance** that should increase the chance that training memory can be indexed through temporal anchors.
- Its nomological role is as a **moderator**:
  - should converge with D4a sensitivity and D11 deltas
  - should interact with `Cutoff Exposure`
  - should not load equally on every detector; if it does, it has collapsed into generic article specificity

As a manipulation:

- Yes. This is the cleanest within-case perturbation in the benchmark.
- The dose-response output is useful, but I would treat it as an **ordered intervention path**, not a metric "dose" scale.
- I infer that manipulable adjunct-type cues will cover a **majority** of CLS event articles, and subject-type `T1` cases are likely **well below 30%** of the corpus, because CLS is heavily datelined and clause-driven. That is an inference from corpus genre and a rough repo sample, not a manual audit.

Observation and manipulation are complementary:

- Observation gives between-case moderation.
- Manipulation gives within-case causal evidence.
- That is a clean MTMM-style pairing, not redundancy.

Relation to `Cutoff Exposure`:

- They are related but not collinear in any problematic sense.
- `Cutoff Exposure` asks "could this model have seen it?"
- `Temporal Anchor Recoverability` asks "does the text provide a temporal retrieval handle?"
- The expected signature is an **interaction**, not replacement.

## Block C Answer

Split D4.

Recommendation:

- Keep **one detector family slot**.
- Report **two sub-measurements**, not one merged scalar.
- Make `D4b` the cleaner "ADG proper," and treat `D4a` as a conflict-resolution subtest.

Construct split:

- `D4a ADG-Contradiction` primarily measures **temporal source arbitration under conflict**.
- It is **not** a pure memorization detector; "memorization override" is one mechanism that can drive it, but so can text-grounding or instruction-following policy.
- `D4b ADG-Misdirection` measures **prompt-level chronology gating of recalled knowledge when text-side anchors are absent**.
- That is a distinct MTMM pattern: same method family, different trait loadings.

Expected factor relevance:

- `D4a`: strongest dependence on `Temporal Anchor Recoverability`, cue type, and perhaps instruction-following robustness.
- `D4b`: strongest dependence on `Cutoff Exposure`, `Anchor Strength`, and recurrence/salience; once masking is successful, the original cue taxonomy should matter much less.

Relation to CMMD:

- `D1 CMMD` and `D4b` are partially convergent but not redundant.
- `CMMD` is cross-model cutoff-conditioned familiarity.
- `D4b` is within-model chronology compliance.
- `D4a` is more distinct still, because CMMD does not test prompt-vs-text conflict.

Compute:

- A blind full run of both sub-detectors over all cases/models is **not justified yet**.
- Run a pilot first.
- If scaled, I would prioritize:
  - `D4b` as the cleaner temporal-gating measure
  - `D4a` as a secondary conflict assay
- `D4a` should include a **matched-date control**. That control is useful because it isolates contradiction cost from mere prompt-format burden.

## Block D Answer

Adopt D11 in **reshaped form**.

Recommendation:

- D11 should be a **temporal intervention protocol applied to existing detectors**, not a fully standalone detector slot.
- It is closest to an **EAS-like sensitivity field** for time.

Construct:

- The construct is **temporal-anchor-mediated detector sensitivity**.
- It is not directly "memorization."
- It only becomes evidence for memorization when its deltas show the right **nomological pattern**.

Success condition:

- Detector scores fall as temporal anchors are removed,
- **more strongly** on pre-cutoff / plausibly memorizable cases than on clearly post-cutoff placebo cases,
- and **more strongly** than under a matched non-temporal deletion control.

That last control is critical. Without it, D11 is just "content removal hurts performance."

Dominant failure mode:

- generic information loss
- edit awkwardness
- reduced event identifiability unrelated to memory

So I would not run a pure `L4 -> L3 -> L2 -> L1` ladder alone. I would add a **length-matched non-temporal deletion control**.

Coverage:

- Subject-type `T1` cases should be **excluded from intervention analysis** and retained as an observational stratum.
- I infer they are a minority overall, but that needs an audit before any corpus-wide claim.

Cost:

- Full-scale D11 across all detectors/cases/models is too expensive for first adoption.
- Methodologically, its value is in **identification**, so a stratified subset is enough at first.

Relation to D4:

- D11 and D4 are complementary.
- D11 manipulates **text-side anchor availability**.
- D4b manipulates **prompt-side temporal framing**.
- D11 does **not** subsume D4b, though both can share the same fully masked `L1` text.

## Block E Answer

Do **not** use one global preserve/remove rule. Use one global **principle**:

- perturb the construct of interest
- hold temporal cues fixed unless time itself is the target of the intervention

That yields different defaults by detector.

For `D5 SR/FO`:

- **Preserve the original temporal cues** by default.
- Reason: SR/FO is supposed to test resistance to changed factual content under a near-constant shell. Removing the date creates a second intervention and muddies the construct.
- If you want a time-masked SR/FO arm, that belongs under D11, not D5 primary scoring.

For `D6 FinMem-NoOp`:

- The inserted irrelevant clause should **not contain its own temporal cue** by default.
- If a time cue is unavoidable for naturalness, it should **match the original time window**, never deliberately mismatch.
- A mismatched-time insertion is not a NoOp; it becomes a temporal-conflict probe.

For `D7 EAD`:

- Do **not** expand the main taxonomy to `2×2×2`.
- Time masking is a different construct from entity masking.
- Adding it to EAD would make the delta uninterpretable: identity loss, time loss, and generic information loss get mixed together.
- If wanted at all, do it as a **small orthogonal follow-up**, not the primary D7 design.

## Cross-Block Synthesis

The clean methodology is: treat temporal cues as a **vector-coded text property** plus a **within-case intervention path**. The factor side measures a text's temporal retrieval affordance; the manipulation side tests whether detector behavior actually depends on that affordance. That pairing is much stronger construct-validity evidence than either one alone.

This implies three downstream design moves. First, D4 has to split, because prompt-side gating without text anchors and prompt-vs-text contradiction are not the same trait. Second, D11 should be reported as a **temporal sensitivity protocol on top of existing detectors**, not as another independent memorization detector. Third, D5/D6/D7 should not all "handle time" the same way; they should follow dimension-isolation logic.

Main tension with Step 1 is only structural: Step 1 treated ADG as a single detector and left temporal handling open. I would revise that to one `D4` family with distinct sub-measures, and I would resist turning D11 into a full new slot before pilot evidence shows it discriminates temporal-anchor effects from generic deletion effects.

Questions for other lenses:

- `Stats`: what is the smallest pilot that can distinguish time-removal effects from matched non-temporal deletion effects with usable uncertainty?
- `Quant`: is the D11 subset best targeted to near-cutoff cells where interaction with `Cutoff Exposure` is strongest?
- `Editor`: should the paper name the factor "Temporal Cue Clarity" for readability but define the construct as "Temporal Anchor Recoverability"?

Sources: `refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md`, `refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md`, `docs/DECISION_20260413_mvp_direction.md`, [Wongchamcharoen & Glasserman 2025](https://arxiv.org/abs/2511.14214), [Cheng et al. 2024](https://arxiv.org/abs/2403.12958), [Mirzadeh et al. 2024](https://arxiv.org/abs/2410.05229), [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322), [Merchant & Levy 2025](https://arxiv.org/abs/2512.06607).
