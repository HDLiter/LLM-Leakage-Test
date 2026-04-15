# BENCHMARK R4 Step 2 — Stats Shortlist Review
**Date:** 2026-04-13
**Reviewer:** Codex (senior econometrician)
**Reasoning effort:** xhigh
**Source:** 12-factor shortlist (post-Step 1 + user integration)
**Prior rounds:** BENCHMARK_R1/R2/R3_STATS.md + BENCHMARK_R4A_STATS.md
**Scope constraint:** No algorithmic specification for event-clustering or entity-annotation factors; target N is reference, user will dynamically resample.

---

## 1. Recommended N and tiering

I would **not** interpret the expanded 12-factor shortlist as 12 confirmatory hypotheses. Even with a larger dataset, that is not mainly an alpha problem; it becomes a sparse-partition and estimand problem because `Structured Event Type`, `Event Phase`, and `Session Timing` are multi-cell factors, and `Tradability Tier` is conditional on the company subset. The statistically coherent version is:

- **Confirmatory families (6):** `Cutoff Exposure`, `Propagation` family, `Anchor Strength` (only if the rubric is frozen before the main pull), `Target Scope`, `Disclosure Regime`, `Template Rigidity`.
- **Exploratory (5):** `Entity Salience` dual, `Tradability Tier`, `Structured Event Type`, `Event Phase`, `Session Timing`.
- **Control (1):** `Text Length`.

If you insist on moving `Tradability Tier` into the confirmatory family from day one, the confirmatory count becomes `7`.

Using the Step 1 anchor `N_floor ≈ 852 scorable` for one balanced binary contrast at the prior `OR = 1.95` benchmark:

- `1` confirmatory test: about `852` scorable.
- `2` tests with Bonferroni/Holm-grade protection: about `1,032`.
- `3` tests: about `1,136`.
- `4` tests: about `1,211`.
- `5` tests: about `1,268`.
- `6` tests: about `1,315`.
- `7` tests: about `1,354`.

The key point is that **imbalance costs more than one extra hypothesis**. With `6` confirmatory tests, the balanced floor is about `1,315` scorable, but:

- at `70/30`, required scorable rises to about `1,565`;
- at `75/25`, to about `1,753`;
- at `80/20`, to about `2,054`.

With `20%` loss, those become gross `1,956`, `2,191`, and `2,567`.

The conditional factor matters more. If `Tradability Tier` is analyzed only inside company cases, and company cases are `75%` of the sample, then a `7`-test plan needs:

- about `2,149` scorable total if tradability is `70/30` within company;
- about `2,407` scorable total if tradability is `75/25` within company.

Those imply gross totals of about `2,687` and `3,009` before any additional buffer.

My **reference recommendation** is therefore:

- **Recommended initial target: `N = 3,200` gross clusters.**

That is above the mathematical minimum for the `6`-family confirmatory core, but it materially reduces resampling churn and keeps the exploratory multi-level factors from collapsing into tiny bins. At `20%` loss, `3,200` gross leaves about `2,560` scorable; a `10%` bucket still has about `256` cases, and a `5%` bucket about `128`.

If you promote `Tradability Tier` into the confirmatory family immediately, I would open **closer to `3,500` gross** rather than `3,200`.

**Grow rules** to minimize churn:

- Keep sampling if any **confirmatory binary** factor has a minority share below **25%**.
- Keep sampling if `company` share falls below **70%** and you still want serious `Tradability Tier` analysis.
- Keep sampling, or demote `Tradability Tier`, if its minority tier inside the company subset is below **25%**.
- Treat any **4-level** factor with a bucket below **10%** as exploratory/descriptive only.
- Treat any **7-level event-type** category below **5%** as exploratory/descriptive only; do not chase confirmatory claims there.
- If the `Anchor Strength` rubric is not frozen before the main pull, it remains exploratory regardless of N.

`Idea 4` does **not** change the confirmatory N calculation **if** interactions remain explicitly pre-registered exploratory. If you promote any interaction pair to confirmatory status, the N target moves up again and I would not recommend that at this stage.

## 2. Per-factor verdicts

No factor is a total statistical block **if tiered correctly**. The red line is not the factor itself; it is pretending that thin multi-level or conditional partitions are confirmatory when they are not.

- **Propagation Intensity — CONCERN.** Good exposure concept, but `cluster_size` and `prior_family_count_365d` are not obviously one latent dimension.
- **Cutoff Exposure — GO.** This remains the cleanest and best-powered treatment-like contrast.
- **Anchor Strength — CONCERN.** Valuable if the rubric is frozen first; otherwise the factor definition itself is still in development.
- **Entity Salience — CONCERN.** Informative, but it overlaps with target prominence, article crowdedness, and likely with `Target Scope`.
- **Target Scope — GO.** Clear stratification axis; defensible if you respect the unequal-bin power penalty.
- **Tradability Tier — CONCERN.** Statistically valid, but only as a within-company estimand and only if the company subset is large enough.
- **Structured Event Type — CONCERN.** Substantively real, but `7+` categories remain exploratory at this scale.
- **Disclosure Regime — GO.** Clean binary institutional contrast.
- **Template Rigidity — CONCERN.** Plausible, but partly overlaps with propagation and event-type structure.
- **Event Phase — CONCERN.** Analyzable under the proposed design, but the estimand becomes phase-conditioned rather than prevalence-representative.
- **Session Timing — CONCERN.** Useful as a nuisance/exploratory dimension; weak as a main standalone claim.
- **Text Length — GO as control only.** Do not spend confirmatory alpha on it.

## 3. Response to the 5 methodology inputs

- **Idea 1 — Extra-corpus signal principle: SUPPORT.** This should be in the pre-commit rationale. It disciplines factor choice toward externally grounded predictors and away from detector feedback or outcome leakage.
- **Idea 2 — Event Phase two-stage sampling: REVISE.** I accept it for exploratory balance, but it changes the estimand from natural phase prevalence to phase-conditioned heterogeneity. That is fine if stated plainly.
- **Idea 3 — Anchor empirical operationalization: REVISE.** A 50-case experiment is enough to choose among candidate rubrics; it is not enough to declare the chosen rubric measurement-stable. Freeze after the experiment, then infer on the main sample separately.
- **Idea 4 — Pre-registered interaction menu: REVISE.** I now accept this framework if the menu is fixed ex ante, limited to `5-8` binary-by-binary pairs, fully reported as a menu, and never narrated as confirmatory discovery. Under that discipline it does **not** consume confirmatory alpha.
- **Idea 5 — Detector-dependent factors are R5: SUPPORT.** Correct sequencing. Do not let detector-linked features leak backward into the R4 identification layer.

## 4. C1, C2, C3

**C1 — Propagation Intensity composite**

From a statistical standpoint, I would **not** assume `cluster_size` and `prior_family_count_365d` are independent enough to justify one confirmatory composite. They are related, but they measure different mechanisms:

- `cluster_size`: contemporaneous propagation of the focal event;
- `prior_family_count_365d`: historical recurrence of the underlying news family.

They can correlate through `Structured Event Type`, salience, and institutional source processes. The bigger problem is not raw multicollinearity; it is **interpretability**. A significant composite does not tell you which exposure margin actually moved. My recommendation is to keep them in the same propagation family, but estimate and report them separately. If you still want one index, treat it as a convenience summary, not as proof of a single latent construct.

**C2 — Conditional Tradability Tier**

This does **not** break homogeneity assumptions if you define the estimand correctly. A pre-declared conditional factor is confirmatory-safe **provided**:

- the condition `target_type = company` is declared ex ante;
- the estimand is explicitly stated as a **within-company** effect;
- multiplicity counts it as its own planned test;
- sample-size planning is based on the eligible company subset only.

What is not safe is estimating one pooled coefficient across all cases, with non-company items implicitly treated as zero or missing, and then speaking as if the effect were universal.

**C3 — Dual Entity Salience**

Pairing `target_salience` with `max_non_target_entity_salience` does create a real multicollinearity risk because both load on general article prominence and entity density. But I would **not** orthogonalize by default. Residualization changes the estimand: one variable stops meaning salience and starts meaning “salience net of the other variable.” That is defensible only if that is the concept you actually want. My default advice is:

- keep both on their natural scales if you want two partial effects;
- if correlation is very high, demote one or reinterpret the pair as exploratory;
- do not mechanically residualize just to stabilize a coefficient table.

## 5. Hidden multicollinearity risks

The main hidden overlaps in the 12-factor set are:

- **Propagation Intensity x Template Rigidity:** both may partly capture repeatable, formulaic rewriting.
- **Propagation / prior-family recurrence x Structured Event Type:** some event types naturally recur and propagate more.
- **Disclosure Regime x Structured Event Type:** formal disclosures are not randomly distributed across event mechanisms.
- **Target Scope x Target Salience x Tradability Tier:** large listed firms tend to be both more tradable and more textually dominant.
- **Cutoff Exposure x Event Phase x Session Timing:** newsroom timing and follow-up sequencing can induce calendar-composition differences that masquerade as cutoff effects.
- **Text Length x Entity Salience x Template Rigidity:** article length can mechanically affect both salience measures and perceived templating.

These are not automatic disqualifiers. The correct response is disciplined tiering, explicit estimands, and restrained interpretation, not indiscriminate orthogonalization.

My bottom line is: **`N = 3,200` gross clusters is the first operationally credible reference number for this expanded 12-factor plan**. It is still a reference number, not a hard requirement; the true requirement will move with realized minority shares, gray-band exclusions, and whether `Anchor Strength` and `Tradability Tier` stay out of the confirmatory core. But `1,500` is only credible for the narrow Step 1 design. `3,200` is the number at which the enlarged shortlist becomes statistically manageable without constant resampling churn.
