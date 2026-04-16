---
role: Stats / power and identification
session: R5A Temporal Cue Design
thread_id: 019d93f5-6ea0-7f72-a7df-b51b7da57bfd
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## Block A — Temporal Cue Taxonomy

- For identification, use a **multi-dimensional annotation** and a **collapsed confirmatory analysis factor**. A single scalar `L4 > L3 > L2 > L0.5 > L0 > L1` is not valid as the primary measurement model.
- The right annotation axes are:
  - `surface_resolvability`: exact in-text, partial/deictic in-text, relative/ordinal, absent/weak.
  - `lookup_dependency`: none/shallow vs closed-reference entity→date retrieval.
  - `editability`: adjunct-removable vs subject-essential.
- Do **not** merge `L2` and `L0.5`. They both need extra resolution, but the source is different: `L2` is calendar/context completion; `L0.5` is parametric memory lookup, which is exactly the memorization-relevant mechanism.
- Treat `L3` as **in-text**, not lookup-dependent. Recovering the year from publication metadata or local context is not the same construct as retrieving "WAIC 5th edition = 2022."
- `subject-type` vs `adjunct-type` should be a **separate axis**, not a level. It matters for manipulability, not cue clarity.
- For confirmatory factor × detector analyses, use a **categorical 4-cell factor**:
  - explicit in-text exact/partial
  - relative/deictic only
  - lookup-dependent closed-reference
  - weak/none
- Ordinal scoring is only defensible for a derived **surface-resolvability** axis within the non-lookup subset. It is not defensible across the full six-level draft because `L0.5` is not on the same interval scale.
- Multiple cues should be stored as a **vector**, not reduced by `MAX` or `MIN`. For modeling, derive `has_explicit_anchor`, `has_lookup_anchor`, and `dominant_editable_cue`. For D11, require a clean removable path; otherwise mark the case ineligible.
- Power: with 3,200 cases, a 6-level nominal factor gives about `~533` cases per level before any stratification. That is adequate descriptively but weak for interaction-heavy confirmatory models. A 3-4 level collapsed factor is materially better.
- Annotation protocol should be **hybrid**:
  - deterministic regex/date parser for exact/partial cues
  - LLM-assisted candidate labeling for relative and closed-reference cues
  - double human adjudication on ambiguous cases
- Reliability target: `alpha/kappa >= 0.80` for the collapsed confirmatory factor; `>= 0.70` for the adjunct-vs-subject split. If the latter misses `0.70`, do not use it confirmatorily.

## Block B — Factor vs Manipulation

- Recommendation: **both**, but asymmetrically.
- As a factor, temporal-cue clarity should enter as a **secondary** factor in **Bloc 0**, labeled as `text-encoded temporal accessibility`, not as another version of Cutoff Exposure.
- Construct caveat: this factor measures **recoverability of event time from text plus shared priors**, not "time" in the abstract. The closed-reference cell partly measures memory lookup burden.
- Literature provenance is **PARTIAL/NOVEL**. Temporal-gating and chronology papers support the direction, but the benchmark factorization itself is new.
- As a manipulation variable, it is the cleanest near-experimental intervention in the project. I would budget **~50-65% of cases** as likely D11-eligible overall, not more, until an audit proves otherwise.
- The manipulation path is not redundant with the factor path. The factor gives correlational moderation; the manipulation gives within-case causal leverage.
- Collinearity with Cutoff Exposure is probably **low to moderate**, not destructive. My prior is `|r| ≈ 0.10-0.20` overall, maybe `0.25-0.30` if CLS formatting drifted over calendar time. The larger collinearity risk is with **Anchor Strength**, **Structured Event Type**, and **Session Timing**, not Cutoff Exposure.
- The reason is structural: temporal-cue clarity is a **case-level text property**; Cutoff Exposure is a **case × model property**. In a stacked mixed model, that already makes them close to orthogonal unless article style changed strongly over years.
- Data that would resolve this:
  - per-model `corr(T_i, Exposure_im)`
  - VIF/condition index in the stacked design matrix
  - `Exposure_im ~ T_i + year + event_type + source + anchor_strength` pseudo-`R^2`
  - year-by-year cue-style drift plots
- Multiplicity: adding the factor alone is manageable. On the Step 1 stats primary slate, it moves the confirmatory family from `5 × 12 = 60` to `5 × 13 = 65` coefficients.
- The real problem is adding the factor **and** treating `D4a`, `D4b`, and `D11` as fully independent confirmatory detectors. That moves the family to `8 × 13 = 104` coefficients, a `~73%` inflation. I would not do that.

## Block C — D4 Redesign

- Split D4 into **one ADG family with two sub-measurements**: `D4a` and `D4b`.
- The clean design is a **2×2 within-case/model factorial**:
  - text mode: `raw` vs `time-masked`
  - prompt mode: `pre-event as-of` vs `post-event as-of`
- Let `Y_im(r,a)` be the detector outcome for case `i`, model `m`, text mode `r`, prompt mode `a`.
  - `D4a = E[Y(raw, post) - Y(raw, pre)]`
  - `D4b = E[Y(masked, post) - Y(masked, pre)]`
  - `conflict premium = D4a - D4b`
- `D4b` is the cleaner identified estimand. It asks whether prompt-declared time can gate recall when the text supplies no anchor.
- `D4a` is distinct. It asks how the model resolves **text-versus-prompt contradiction**, which is not the same construct.
- Expected moderators differ:
  - `D4a`: temporal-cue clarity, lookup dependency, anchor strength
  - `D4b`: Cutoff Exposure first, then Anchor Strength; much weaker dependence on raw text cue type after masking
- Relationship to CMMD: **complementary**. CMMD is cross-model exposure structure; ADG is within-model chronology compliance. I would expect partial convergence, not redundancy.
- Nearest negative controls:
  - `D4a`: congruent as-of date matching the text, or no as-of date
  - `D4b`: date-neutral sham prompt, plus clearly novel/post-cutoff placebo cases
- The "matching prompt date" cell is useful, but as an **audit control**, not a full extra confirmatory arm.
- Compute: `76,800` calls is acceptable **if** ADG stays one family and D11 is not run as a universal overlay. It is even more defensible because the same 4-cell design yields `D4a`, `D4b`, and the interaction.
- Reporting: one detector slot, two sub-measurements, hierarchical testing. Test the ADG family first; if it clears, test `D4b` and `D4a` secondarily. If forced to prioritize, `D4b` is the primary confirmatory piece.

## Block D — D11 Recommendation

- Recommendation: **reshape and adopt as an intervention module**, not as a free-standing universal detector.
- D11 should estimate a **dose-response interaction**, not raw decay. The core estimand is the exposure-conditioned slope:
  - `Y_imdl = α_md + b_i + f(level_l) + γ Exposure_im + δ f(level_l)×Exposure_im + ε`
  - `δ` is the target: steeper score decay with cue removal in exposed than unexposed/placebo settings.
- Raw score decline alone is not persuasive; generic information loss can do that. The identifying pattern is **difference in slopes**, not slope by itself.
- Success condition:
  - monotone or near-monotone decline as cues are downgraded
  - materially steeper decline in exposed than in unexposed/placebo cases
  - strongest effects in lookup-dependent adjunct cues
  - survives a same-length non-temporal sham deletion control
- Dominant failure mode: **generic content loss**. If everyone drops similarly when a short adjunct is deleted, D11 is measuring fragility, not memorization.
- Subject-type `L0.5` cases should be **observational only**. They stay in the factor analysis but are excluded from the causal D11 cohort.
- If ineligible cases exceed `30%`, D11 becomes a **subcohort experiment**, not a benchmark-wide detector. That is acceptable, but it changes how it should be reported.
- Power, using conservative paired-endpoint approximations:
  - at corrected `alpha = 0.005`, 80% power needs about `n=592` for `d=0.15`, `925` for `d=0.12`, `1332` for `d=0.10`, `2081` for `d=0.08`
  - at `alpha = 0.001`, the numbers are `759`, `1186`, `1708`, `2668`
- With 3,200 cases, even a `50-65%` eligible cohort gives roughly `1,600-2,100` units, which is enough for a main D11 slope and borderline for very small effects. It is not enough for many subgroup interactions.
- Feasibility: the `76,800` variant-generation calls are fine once. The problem is overlaying D11 on many detectors; that quickly turns into several hundred thousand extra calls. I would not apply D11 confirmatorily to `D5/D6/D7`.
- Best shape: run D11 on **one main backend detector** and, at most, one appendix validation backend. From the stats lens, `CMMD` is the cleanest main backend.
- D11 does **not** subsume `D4b`. They can share the `L1` masked text, but the estimands differ:
  - `D4b`: prompt-gating under no text time anchor
  - `D11`: dependence of detector signal on text-embedded temporal anchors

## Block E — Time Handling for D5/D6/D7

- Use a **global default with detector-specific exceptions**: preserve the article's original temporal cues in the primary analysis unless time itself is the manipulated object.
- For `D5 SR/FO`, **preserve the original date** in the primary analysis. Otherwise the perturbation changes both outcome and temporal anchoring, which weakens identification.
- For `D5`, time-masked SR/FO should be a **sensitivity analysis** or folded into D11, not the default.
- For `D6 FinMem-NoOp`, the inserted clause should be **time-neutral** if possible. If a time mention is unavoidable, it should be **same-window matched**, never deliberately mismatched, in the primary analysis.
- A deliberately mismatched-time NoOp is not a NoOp; it is an ADG-style stress test. Keep it exploratory only.
- For `D7 EAD`, do **not** expand the confirmatory taxonomy from `2×2` to `2×2×2`. The 8-cell version costs too much power and too much alpha.
- If temporal masking is added to EAD at all, do it on a targeted sensitivity subset and report it as `time-masked EAD`, not as a full third masking axis.
- Between-case randomization of time-handling is not attractive here. It throws away the paired design.
- The better choice is: **pre-register "preserve temporal cues" as primary**, then run **within-case crossover sensitivity analyses** on the same cases where needed.
- This keeps D5/D6/D7 interpretable and prevents the temporal-cue question from multiplying the perturbation family into an unmanageable multiplicity problem.

## Cross-Block Synthesis

- The measurement model should separate three things that the draft taxonomy currently mixes: **surface explicitness**, **memory lookup dependence**, and **editability**. That is the key identification move.
- Temporal-cue clarity should be kept as a **secondary Bloc 0 text factor**, because it is plausibly informative and not strongly collinear with Cutoff Exposure. The bigger statistical danger is not collinearity; it is **family expansion**.
- `D4` should become one **factorial ADG family** with `D4b` as the cleaner estimand, `D4a` as the conflict-sensitive companion, and `D4a-D4b` as the contradiction premium.
- `D11` is promising, but only as a **targeted intervention layer**. If it is turned into a universal overlay across detectors, the design loses both power and interpretability.
- For multiplicity, I would keep the confirmatory family narrow: existing primary detectors + the time-cue factor + one ADG family. Put D11 and time-handling sensitivities outside that family until pilot data proves edit validity and cohort coverage.
- The control strategy should stay what the Step 1 stats lens already preferred: **Westfall-Young stepdown max-T** across primary detector × factor coefficients, with **gatekeeping** inside the ADG family and D11 treated as secondary unless it earns promotion.
- Main questions for other lenses:
  - NLP: can the annotation pipeline hit `alpha >= 0.80` on the collapsed cue factor and `>= 0.70` on adjunct vs subject?
  - Quant: how much year-to-year cue-style drift exists in CLS, and what is the actual D11-eligible share?
  - Editor: can time-neutral NoOp and time-preserving SR/FO edits remain natural CLS prose at high audit pass rates?
