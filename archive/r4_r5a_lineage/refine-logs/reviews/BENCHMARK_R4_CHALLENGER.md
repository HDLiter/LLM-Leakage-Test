# BENCHMARK R4 — Challenger Cross-Model Check
**Date:** 2026-04-13
**Reviewer:** Claude (cross-model Challenger, NOT Codex)
**Purpose:** Surface blind spots shared by the 4 Codex domain agents
**Scope:** R4 Step 1 + Step 2 outputs + decision doc v3

---

## Executive summary

The 12-factor shortlist with Editor's narrative hierarchy is **fundamentally sound** and I would not block R4 closure on any single issue. The 4 Codex agents did their job: the spine (Cutoff × Propagation × Anchor × Entity Salience) is well-motivated, the tiering is defensible, and the methodological principles P1-P5 close the most obvious p-hacking channels. However, reading the 8 Codex outputs side by side, I see **three structural blind spots that a single-model-family committee would plausibly share**:

1. All 4 factor lists are built from a "what signal might propagate through the pretraining corpus" lens, with almost no factor that is explicitly designed to be **independent of the major-entity prominence bloc**. The mitigation ("joint modeling") is reactive; the factor taxonomy is not pro-actively balanced.
2. The **annotation dependency graph is a 4-of-12 exposure** (Propagation-historical, Event Type, Event Phase, Disclosure Regime), and the "sensitivity analysis with alternative taxonomies" mitigation is weaker than it sounds — a slightly perturbed ontology that was written by the same annotator family will likely produce the same errors.
3. The **pre-registered interaction menu** is currently populated from pairs that each agent individually cared about; genuinely cross-agent pairs (e.g., Template Rigidity × Event Phase) that would stress-test the mechanism theory are under-represented.

None of these is BLOCKING. One is IMPORTANT (Challenge 3 — annotation-free alternative). The rest are incremental tightenings. I recommend the user address 2 IMPORTANT items before closing R4 and park the remaining MINOR items as R5/R6 inputs.

---

## Challenge 1 — The "major-entity prominence" correlation bloc

**Blind spot.** All 4 Codex agents identify the Target Scope × Target Salience × Tradability Tier correlation bloc and mitigate it through joint modeling (Stats R4B Section 5; Quant R4A cross-factor interactions). None of them proposes a factor that is **constructively independent** of the bloc. Propagation Intensity partially does this via the historical term, but even `prior_family_count_365d` is higher for widely-covered large firms. The 12-factor taxonomy has no factor whose **design intent** is "high on the exposure axis but low on the prominence axis."

**Challenge.** The econometric treatment (joint modeling) says "we can disentangle correlated regressors with enough N"; the **scientific treatment** says "the benchmark should include a contrast where the axes are orthogonal by construction." The latter is much more persuasive to an EMNLP reviewer because it reframes the correlation hazard from a statistical nuisance into a substantive hypothesis test.

**Counter-proposal — add a "tail-entity cluster intensity" sub-factor**. Within the Propagation Intensity family, stratify cases into four cells:

| | Low cluster_size | High cluster_size |
|---|---|---|
| **Head entity** (top decile target_salience) | reference | high-exposure head |
| **Tail entity** (below median target_salience) | low-exposure tail | **high-exposure tail** ← informative cell |

The "high-exposure tail" cell is the scientifically load-bearing one: an event about a mid-cap or sector that nonetheless generated a large cluster. If memorization tracks **exposure not prominence**, high-exposure-tail cases should show memorization indistinguishable from high-exposure-head cases. If memorization tracks prominence not exposure, they diverge. This is a **single 2×2 contrast** and does not require a new factor — it can be added to the interaction menu as `target_salience × propagation_intensity` (which is not currently on the menu).

**Severity.** IMPORTANT, not BLOCKING.

**Recommended action.** Add `target_salience × propagation_intensity` (within company subset) to the pre-registered interaction menu with the explicit framing "tail-entity cluster intensity test." Cheap to add; directly addresses a Codex consensus blind spot; rhetorically strong.

---

## Challenge 2 — Alpha-bridge vs venue-drift is a false dichotomy?

**Blind spot.** Editor R4B hard-blocks Tradability Tier and Session Timing on venue-drift grounds. Quant R4B accepts demotion reluctantly. The user picked Editor's hierarchy. But all 4 agents framed this as a **binary trade-off** (alpha-bridge OR EMNLP fit) rather than asking whether a single factor could serve both narratives.

**Challenge.** Consider **Event-Type Template Rigidity**. NLP's Template Rigidity is currently char-5gram TF-IDF at the document level. But the real underlying mechanism is: *certain event types (e.g., earnings preview, regulatory approval, suspension announcement) are encoded in highly rigid journalistic templates AND are also events that the market prices in a highly stereotyped way*. This gives a **dual narrative**:

- **NLP story:** template rigidity creates repeated surface forms → surface-form memorization is stronger → Min-K% / exact-match detectors see bigger effects.
- **Alpha story:** stereotyped market reaction is exactly where LLM memorization can contaminate signal because the model memorized not just the news but the *price reaction template* that follows it.

This is **one factor, two stories**, and it lands squarely in the NLP memorization literature (Zhang et al. 2021 on templated text as memorization confound) while also speaking to the Thales alpha contamination goal. Neither Quant nor NLP explicitly framed Template Rigidity this way.

**Another candidate — surprise-size-dependent memorization.** Quant proposed Standardized Surprise Magnitude; user dropped it because it depends on the deferred outcome function. But a **weaker textual proxy** is computable now: the presence of "surprise language" in the CLS headline (关键词: `超预期`, `意外`, `大幅`, `远超`, `不及预期`, `暴跌`, `骤升`). This is a **purely textual** factor, computable from CLS alone, and supports both stories:
- Novel/surprising events should be *less* memorized (they are rarer in training data).
- Novel events produce larger price moves.
- So detector-visible memorization should correlate inversely with textual-surprise markers — a clean dual story.

**Severity.** MINOR for the template rigidity reframing (it's already in the shortlist, just narrate it differently). MINOR-to-IMPORTANT for the surprise-language factor (would be a new factor; user is already at 12).

**Recommended action.** Reframe Template Rigidity's narrative in the paper to explicitly carry both stories. Do not add a new factor for surprise language; park it in the exploratory reserve or let R5 reconsider it as a detector stratification axis.

---

## Challenge 3 — Shared annotation dependence (Risk R1) is under-mitigated

**Blind spot.** Quant R4B and NLP R4B both identified the shared annotation backbone and both proposed the same mitigation: "publish the dependency graph + sensitivity analysis with alternative taxonomies." The decision doc v3 accepted this as sufficient. **This is the clearest case of Codex consensus convergence masking a weak fix.**

**Challenge.** A dependency graph is a transparency measure, not a mitigation. A sensitivity analysis with a slightly perturbed taxonomy tests whether the findings are **robust to taxonomy noise**, not whether the findings are **independent of a particular annotator viewpoint**. If the same team (or the same two LLM families, Claude + Codex) generates both the primary taxonomy and the perturbed alternative, the errors will correlate. The result: a sensitivity analysis that "passes" but still leaves 4 factors all inheriting the same bias.

**Counter-proposal — an annotation-free template recurrence factor.** The user already rejected CLS-internal duplicate_cluster_size as insufficient on its own. But Propagation Intensity's historical term (`prior_family_count_365d`) is fully dependent on the Event Type annotation. A **surface-form clustering variant** can compute "historical template recurrence" **without** any event-type annotation:

> For each canonical cluster, compute char-5gram TF-IDF similarity to the *set of all clusters from the prior 365 days*. `historical_template_recurrence = max cosine similarity to any prior-year cluster`. High values = "an event whose textual form has appeared before" regardless of whether an annotator labels them as the same event type.

This is **conceptually the Propagation Intensity historical term, but computed from surface form rather than semantic annotation**. It uses the same machinery that is already specified for Template Rigidity (NLP R4B Section 5 operationalization). It gives the paper an annotation-independent version of the same construct, which is exactly what Risk R1 needs.

**Critical observation:** The current shortlist has `cluster_size` (annotation-free, intra-event) and `prior_family_count_365d` (annotation-dependent, inter-event). Adding surface-form `historical_template_recurrence` fills the missing cell: annotation-free, inter-event. With that cell filled, the Propagation Intensity family has a full "source robustness" matrix.

**Severity.** IMPORTANT. This is the single highest-leverage fix in my report.

**Recommended action.** Either (a) add `surface_template_recurrence` as a 13th factor within the Propagation family, documented as the annotation-independent variant of `prior_family_count_365d`; or (b) explicitly pre-register running the Propagation Intensity analysis *twice* — once with annotation-based `prior_family_count_365d` and once with surface-form `historical_template_recurrence` — and report both. Option (b) is cheaper and more scientifically rigorous because it demonstrates the finding does not depend on the annotation.

---

## Challenge 4 — Anchor Strength 50-case experiment is fragile

**Blind spot.** Principle P3 locks the Anchor operationalization to a 50-case × 3-rater × 3-rubric design. NLP R4B Section 6 specifies the tie-break rule: highest α wins; within 0.05 α → face validity; still tied → simplicity. Nobody computed the **bootstrap CI on Krippendorff α at n=50**.

**Challenge.** Krippendorff α with n=50 and 3 raters has a bootstrap 95% CI typically **±0.08 to ±0.12** (this is a rule-of-thumb from the IAA literature; see Krippendorff's own 2004 treatment; also Zapf et al. 2016, BMC Medical Research Methodology, which shows that even κ at n=50 has CI width ~0.2). The 0.05 "within" threshold in the tie-break rule is **well below the sampling noise**. This means:

- If the three rubrics produce α values of (0.68, 0.65, 0.62), the selection is effectively random — the ranking could reverse under a different 50-case sample.
- If all three cluster at α ≈ 0.60, the "face validity" tiebreak becomes the primary selection criterion, which is itself subjective and defeats the outcome-blind design.

**The deeper issue:** the protocol treats α as a point estimate when it should be treating α as a random variable with a known sampling distribution at n=50.

**Counter-proposal — 3 adjustments:**

1. **Enlarge to n=80-100 cases.** Annotation cost is 3 raters × 3 rubrics × extra cases = ~300-450 extra annotations for the budget to go from ±0.12 CI width to ±0.08. That is cheap relative to the decision weight.
2. **Pre-register a bootstrap-based significance test** for the tie-break: rubric A beats rubric B only if the bootstrap 95% CI on `α_A - α_B` excludes zero (paired bootstrap over cases). If no pair excludes zero, declare a tie and go to face-validity.
3. **Escape hatch:** if all three rubrics have overlapping bootstrap CIs on α AND face-validity review disagrees, **fall back to the simplest rubric (Quant's density count)** as the pre-registered default. This removes the last bit of discretion.

**Severity.** IMPORTANT.

**Recommended action.** Update Principle P3 with the bootstrap-based test and the "fall back to simplest if tied" escape hatch. Consider enlarging n to ~80; if budget-constrained, keep n=50 but require the bootstrap test.

---

## Challenge 5 — Pre-registered interaction menu has subtle loopholes

### Challenge 5a — "Selective-detail" p-hacking channel

**Blind spot.** P4 rule 4 says "all menu items MUST be reported; strong → detailed, weak → 1 sentence." But the decision of *what counts as "strong enough for detailed analysis"* is not pre-committed. A reviewer can reasonably suspect that any pair promoted to detailed treatment was promoted *because* it was publishable, regardless of the ex-ante menu.

**Counter-proposal.** Pre-commit a **detail threshold** in the menu itself: *"A menu pair receives detailed treatment iff |log-odds ratio| > 0.3 AND p < 0.05 under pre-registered logistic regression. Pairs not meeting both thresholds get the 1-sentence summary, regardless of direction."* This operationalizes "strong" and removes the post-hoc judgment channel. Cost: zero, just wording.

**Severity.** MINOR.

**Recommended action.** Add explicit detail-threshold wording to P4 rule 4. Use symmetric thresholds so positive and negative effects are treated identically.

### Challenge 5b — Cross-agent interaction pairs are missing

**Blind spot.** The 5 example menu items in P4 are mostly **same-agent pairs**: `cutoff × propagation` (Editor-style), `cutoff × anchor` (Editor-style), `entity_salience × tradability` (Quant-style), `disclosure × event_type` (Editor-style), `template_rigidity × exact_span_rarity` (NLP-style). Almost none cross agent boundaries. The interaction menu inherits the siloing of the brainstorm round.

**Counter-proposal — 2 cross-agent pairs that stress-test the mechanism theory:**

1. **`template_rigidity × cutoff_exposure`** (NLP × the temporal axis). Mechanism: if Template Rigidity captures "memorization of stereotyped forms," the effect should be **stronger** pre-cutoff and near-zero post-cutoff. If Template Rigidity is instead just "stereotyped text that any LLM handles well regardless of seeing it," the effect should be flat across cutoff. This is the single sharpest test of whether Template Rigidity is measuring memorization at all.

2. **`target_salience × event_phase`** (NLP/Quant × Quant). Mechanism: for highly salient targets, all phases get heavy coverage, so phase should matter less. For tail targets, rumor-phase coverage is sparse but official-phase coverage is more standardized, so phase should matter more. A significant negative interaction would validate Entity Salience's dual construct AND Event Phase's value as a factor.

3. **Bonus — `target_salience × propagation_intensity`** (from Challenge 1). The "tail-entity cluster intensity" test.

**Severity.** MINOR-to-IMPORTANT (menu content, not framework).

**Recommended action.** Add the 3 cross-agent pairs above to the interaction menu. Note that this brings the menu to ~7-8 pairs, which Stats R4B explicitly said is acceptable; Editor R4B said 5-8 was too many but that position was overruled by the user's D13.

---

## Challenge 6 — Chinese-NLP-specific issues

**Blind spot partial coverage.** NLP R4A Step 1 did mention segmentation instability, alias normalization, and `亿/万` unit suffix issues — but only as footnotes to Exact-Span Rarity and Locator Specificity. Quant R4A mentioned alias normalization as a failure mode for Lexical Anchor Density. **None of the 4 agents proposed a Chinese-specific factor or a Chinese-specific data quality flag as a first-class shortlist member.**

**Challenge.** The benchmark is built on Chinese CLS text and will be evaluated on Qwen 2.5 7B (trained substantially on Chinese data). Four Chinese-specific issues are under-addressed:

1. **Regulator vocabulary drift.** 证监会 vs 银保监会 vs 人民银行 disclosures use different formulaic vocabularies. An "disclosure regime" factor that doesn't differentiate regulator source will have within-bin heterogeneity that dilutes the effect.
2. **Source style: CLS vs 21经 vs 每经 vs 财新.** The 12-factor list has no `source_outlet` field. Editor R4A explicitly rejected this as "unstable, rights-specific." But for a contamination analysis, outlet *is* a proxy for "how many copies appeared in the pretraining corpus" because some outlets are more reliably scraped than others. NLP's Template Rigidity partially captures this via cross-cluster similarity, but confounds outlet style with event templating.
3. **Traditional-simplified convergence.** Events involving HK/Taiwan-listed counterparts may have traditional-character versions in pretraining. Duplicate cluster detection on simplified-only CLS will miss this; memorization detection on simplified text will miss memorized traditional text.
4. **Entity alias normalization.** 中信证券 vs 中信 vs 600030 — if entity salience is computed on un-normalized strings, head entities look tail-ish.

**Counter-proposals (bounded):**

- **F-13 (proposed): `source_style_id`** — a controlled field (CLS primary vs reprint-from-X) already in-scope via `public_source_type` from Decision 5. Promote it from stratification-only to an **analysis control** in regression models. No new data collection needed; just use it.
- **Data quality flag (not a factor): `alias_normalization_applied`** — boolean per case indicating whether the entity salience computation applied alias normalization. This is a post-hoc sensitivity knob, cost near zero.

I am **not** proposing traditional-character duplication as a new factor — the cost to detect it is high and it's a niche issue. Flag it as a documented limitation in the paper.

**Severity.** MINOR (for the alias flag); IMPORTANT (for explicit source-outlet control — not as a factor but as a regression covariate alongside text length).

**Recommended action.** Add `public_source_type` (already in schema per D5) to the mandatory control set alongside text_length. Document traditional-character variation as a known-unaddressed limitation.

---

## Challenge 7 — Literature priors inherited from Codex's training

**Blind spot.** All 4 Codex factor lists are grounded in the memorization-benchmark literature clusters: Kandpal, Carlini, Lee, Dated Data, AntiLeakBench, LiveBench. The 12-factor shortlist is well-connected to this literature. But the `related papers/notes/memory_cognitive.md` cluster (Huet 2025 Episodic Memories, Chauvet 2024 Tulving Test, Transformers-as-Tulving-Machines) is referenced only in NLP R4A's literature section for Locator Specificity, and the **episodic-memory framework** is not used to generate any new factor.

**Challenge.** The Huet 2025 framework represents episodic events as `(temporal context, spatial context, involved entities, descriptions)`. The current shortlist has:

- temporal context → Cutoff Exposure, Session Timing, Event Phase (covered)
- involved entities → Entity Salience, Target Scope (covered)
- descriptions → Anchor Strength, Template Rigidity, Locator Specificity (covered)
- **spatial context → MISSING**

The cognitive-science prediction is that **episodic-like recall is stronger when all 4 contexts are present**. If the CLS text mentions a specific venue/place (exchange floor, regulator office, specific city, factory location), episodic retrieval should be facilitated. Quant's Lexical Anchor Density and NLP's Locator Specificity partially capture this (NLP's triple is `entity × time × place`), but "place" is collapsed into the anchor count rather than being a separate factor.

**Counter-proposal.** This is probably not worth a new factor — the benchmark already has 12. But a **spatial-locator binary flag** (`has_geographic_anchor`: does the text mention a specific city / exchange / country / regulator office?) is a free addition that lets you cleanly test the episodic-memory hypothesis in exploratory analysis. It costs nothing and gives the paper a cognitive-science framing that NO existing contamination benchmark has used.

**Kolmogorov-complexity view.** The memorization literature sometimes reframes "rarity" as "Kolmogorov-complexity-adjusted frequency" — a case is memorizable iff its compressibility is low (rare surface form) AND it appeared many times. Exact-Span Rarity gestures at this but NLP explicitly put it in reserve. The information-theoretic reformulation would be: `memorization_potential = log(frequency) × (1 - compressibility)`. This is not a new factor — it's a reformulation of existing factors — but it's a cleaner **theoretical framing for the paper narrative** than the current hodgepodge.

**Severity.** MINOR.

**Recommended action.** Add `has_geographic_anchor` as a boolean auxiliary field (not a headline factor) so the episodic-memory framing is available in exploratory analysis. Do not restructure existing factors around Kolmogorov complexity.

---

## Challenge 8 — Decision doc v3 internal consistency audit

**Audit findings:**

1. **Spine/secondary/auxiliary hierarchy aligns with P1-P5.** The 4 spine factors map to Huet-style episodic contexts (time=cutoff, entity=salience, description=anchor, exposure=propagation). The 2 auxiliary factors are labeled finance-venue-risk. This is internally consistent. Good.

2. **D11 (hierarchy) vs D10 (Plan B philosophy):** consistent. D10 requires economic/linguistic/statistical meaning; the hierarchy preserves this.

3. **D12 (N=3,200 stopping-rule driven) vs D3 (1,000-1,500 one-per-cluster):** D3 is from v2; D12 from v3 supersedes. The v3 doc notes this is a supersession but the D3 text is NOT updated to reflect N=3,200. **Minor inconsistency:** a reader following D3's "1,000-1,500" number forward will encounter D12's "3,200" and have to reconcile. Edit D3's "1,000-1,500" to "superseded by D12" or rewrite the R4-can-assume clause.

4. **D13 (interaction menu ≤5 pairs by Editor proposal, Stats says 5-8 OK) vs principle P4 (3-5 pairs):** P4 says "3-5 2×2 pairs" but Editor R4B objected that 5-8 is too many. User locked "3-5" in decision text but the examples list 5 items. Minor wording drift; the user should pick one number (I recommend 5-7 given my Challenge 5b additions).

5. **Deferred tracks:**
   - **Point-in-time track** deferred. R4 factors `Session Timing`, `Tradability Tier`, Event Phase all partially depend on point-in-time fields. `Session Timing` as auxiliary is fine — can use simple timestamp bucketing. `Tradability Tier` as auxiliary is fine — ADV20 only needs daily data, not 15-min. `Event Phase` is textual classification, doesn't depend on PIT data at all. **No R4 factor is blocked by PIT track deferral.** Good.
   - **Thales-joint clustering track** deferred. Cluster-dependent factors: Propagation Intensity, Event Phase, Disclosure Regime. All 3 are in the spine/secondary. **If Thales-joint track does not converge on a clustering pipeline, these 3 factors are unblockable.** This is the single largest dependency risk in v3 and it is **not flagged as such in the "Open tracks" table.** The table says "Thales-joint track blocks production annotation start" but doesn't flag that 3 of 4 spine factors require it.
   - **Annotation protocol track** deferred. Event Type, Event Phase, Disclosure Regime, Anchor Strength all depend on this. 4 factors.

6. **Factor dependence on deferred tracks (summary):**

| Factor | Depends on | Can R4 close? |
|---|---|---|
| Propagation Intensity | Thales-joint clustering | YES (factor defined abstractly) |
| Cutoff Exposure | none | YES |
| Anchor Strength | Annotation protocol + 50-case experiment | YES if P3 runs on schedule |
| Entity Salience | Thales entity extraction | YES (factor defined abstractly) |
| Target Scope | Thales entity extraction | YES |
| Structured Event Type | Annotation protocol | YES |
| Disclosure Regime | Annotation protocol | YES |
| Template Rigidity | none | YES |
| Tradability Tier | PIT track (ADV20) | YES (daily ADV not blocked) |
| Session Timing | none (timestamps suffice) | YES |
| Text Length | none | YES |
| Event Phase | Thales-joint + annotation protocol | YES (two-stage rule defined) |

**Conclusion:** R4 can close without contradiction; no factor is blocked. But the user should be explicit in the R5 handoff that **Propagation Intensity, Entity Salience, and Target Scope are blocked on Thales-joint track execution**, not just "assume clustering works."

---

## Factors I think are missing from the 12-factor shortlist (bounded)

I propose **1 new factor** and **1 reframing**:

### Proposed F-13: `surface_template_recurrence` (Challenge 3 fix)

Annotation-free variant of `prior_family_count_365d`. Computed by applying the already-specified Template Rigidity machinery (char-5gram TF-IDF) against prior-year clusters. Use as a **robustness companion to Propagation Intensity** rather than a primary factor. Extracting memorization findings that replicate across annotation-dependent and annotation-independent measures would be the strongest result in the paper.

**Hierarchy:** spine robustness companion. Data cost: zero marginal (pipeline already specified).

### Reframing: Entity Salience dual → add tail-entity test

Not a new factor, but a new **analysis cell** — the tail-entity high-propagation contrast from Challenge 1. This should be added to the interaction menu (P4) as `target_salience × propagation_intensity`, pre-committed as the "tail-entity cluster intensity" hypothesis test.

I am **not** proposing:
- Spatial-locator as a factor (document it as an auxiliary field, not a primary)
- Textual-surprise markers as a factor (defer to R5)
- Source outlet / style as a factor (use as control covariate)

---

## Factors in the shortlist I think are WEAKER than Codex consensus suggests (bounded)

### Weaker than consensus: Session Timing (current: auxiliary)

**Current placement:** auxiliary, "kept as auxiliary to prevent venue drift." All 4 Codex agents gave it GO or CONCERN.

**My challenge:** Session Timing is the factor most likely to be **mechanistically null**. The memorization hypothesis is that pre-open and post-close disclosures are more standardized and therefore more memorized. But the surface text of a disclosure is not meaningfully different between 8:45am and 3:30pm releases — both are formal, both are standardized, both are reprinted by the same wire services. Session Timing probably captures **market processing of events** (DellaVigna-Pollet style), not memorization of event text. That's a finance-venue story, not an NLP memorization story.

**Recommended action:** Accept the auxiliary demotion. Do not promote. If it's null in exploratory analysis, drop from the paper entirely rather than report it. This weakens the factor's contribution to the contract with reviewers but is more honest.

**Severity.** MINOR.

### Weaker than consensus: Structured Event Type with 7+ categories

**Current placement:** secondary, fine-grained. User explicitly rejected Stats's 3-category simplification.

**My challenge:** Stats R4B estimated that 7+ categories at N≈2,500 scorable give ~350 cases per category on average. Minority categories will have <5% share and be exploratory-only anyway. The effective useful structure is ~4 well-populated categories (earnings/M&A/policy/commentary) + 3 sparse categories that don't meaningfully contribute. **Keeping the fine taxonomy imposes an annotation burden without a proportional confirmatory benefit.** Editor R4B's CONCERN ("7+ consumes attention") is correct.

**Counter-proposal:** Annotate at 7+ granularity (preserve information), but **pre-commit confirmatory analysis to a 4-way collapse** `(firm_earnings, firm_capital_action, policy_macro, commentary_other)`. This matches Stats's 3-bin intuition but adds the capital-action split that Quant argued for. Finer categories remain available for exploratory breakdowns.

**Severity.** MINOR.

---

## Internal consistency audit of decision doc v3 (summary bullet list)

- D3 text says 1,000-1,500 cases; D12 says 3,200. D3 text should be flagged as superseded to prevent reader confusion.
- P4 says 3-5 pairs; examples list 5 items; Stats accepts 5-8. Pick a number and lock it. With my Challenge 5b additions the total becomes ~7-8.
- No factor is BLOCKED by a deferred track, but 3 spine factors (Propagation, Entity Salience, Target Scope) are DEPENDENT on the Thales-joint track. The "Open tracks" table should flag this dependency explicitly so R5 handoff doesn't assume clustering is a solved problem.
- Risk R1 mitigation is weaker than it sounds (Challenge 3). Either add the annotation-free robustness factor or pre-register the dual-run analysis.
- P3 decision rule (0.05 α tiebreak threshold) is below sampling noise at n=50. Tighten with bootstrap CI or enlarge n.
- D5 (`public_source_type` stored) should be elevated from stratification to mandatory regression control alongside text_length. Costless but forecloses a hostile reviewer attack.

Other items (alpha-bridge framing, finance-venue drift, timeline commitment) are user-discretionary and I have no strong position.

---

## Top-3 priority action items before closing R4

1. **[Challenge 3, IMPORTANT]** Add an annotation-free robustness companion to Propagation Intensity — either as `F-13 surface_template_recurrence` or as a pre-registered dual-run of the existing factor with surface-form `historical_template_recurrence`. This is the single highest-leverage fix; it neutralizes Risk R1 by construction rather than by sensitivity analysis.

2. **[Challenge 4, IMPORTANT]** Tighten Principle P3 with (a) a bootstrap-based significance test for the rubric tiebreak; (b) a "fall back to simplest rubric" escape hatch if all three rubrics have overlapping bootstrap CIs. Optionally enlarge to n=80 if budget allows. Without this, the 50-case experiment's decision rule is below sampling noise.

3. **[Challenge 1 + Challenge 5b, IMPORTANT]** Add 2-3 cross-agent interaction pairs to the pre-registered menu:
   - `target_salience × propagation_intensity` (tail-entity cluster intensity test, within company subset)
   - `template_rigidity × cutoff_exposure` (does template rigidity capture memorization or style?)
   - `target_salience × event_phase` (phase heterogeneity by prominence)
   Cost is zero; scientific value is high; fills the cross-factor gap that siloed brainstorming left behind.

**Not BLOCKING. R4 can close with these 3 as R5 inputs rather than R4-blockers, but they should be captured in the decision record so they are not lost.**

---

**End of Challenger report.**
