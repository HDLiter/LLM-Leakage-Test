# BENCHMARK_PROPOSAL R1 — Multi-Agent Review Summary

**Date:** 2026-04-12
**Orchestrator:** Claude Code
**Round:** R1 (4 Codex domain agents, parallel, no cross-visibility)
**Source reviews:**
- [BENCHMARK_R1_QUANT.md](BENCHMARK_R1_QUANT.md)
- [BENCHMARK_R1_NLP.md](BENCHMARK_R1_NLP.md)
- [BENCHMARK_R1_STATS.md](BENCHMARK_R1_STATS.md)
- [BENCHMARK_R1_EDITOR.md](BENCHMARK_R1_EDITOR.md)

---

## Verdict spread

| Agent  | Verdict                                                           |
|--------|-------------------------------------------------------------------|
| Quant  | Go with **major changes**. Add a contamination→alpha track.     |
| NLP    | **Rebuild, not revise.** Findings-viable only if construct validation lands. |
| Stats  | **Estimand first.** Current draft has no defensible target parameter. |
| Editor | **Reject main / major revision Findings.** "3 papers stapled together." |

No agent recommends submitting as-is. All four escalate to "the current draft is not a benchmark spec; it is an outline that collapses under any of four independent lenses."

---

## Convergent points (3+ agents agree)

### C1 — Construct validity is the central killer, not a footnote
- **NLP**: The pilot already shows SR behaves identically on pre/post-cutoff items — it is a *groundedness* probe, not a memorization probe. The proposal hasn't absorbed this. `fo_flip_hedged` measures conflict susceptibility; `fo_any_change` is rewrite-fragile.
- **Stats**: The proposal never defines the target parameter. It silently conflates at least four distinct estimands (τ_CPT, τ_nat, Δ_prepost, δ_diag). Pick one before building.
- **Quant**: "Article-level leakage proxy" ≠ "contaminated alpha." A PM/finance reviewer will dismiss the benchmark unless there is an explicit bridge from SR/FO to tradable signal contamination.
- **Editor**: Predicts reviewers will attack construct validity first. Proposal must present the CFLS confound openly, not bury it.

**Convergent ask:** Pin down the estimand *in writing* before any data collection; treat SR/FO as instruments that need independent construct validation, not as default metrics.

### C2 — Pre/post training cutoff is not a causal identification strategy
- **Stats**: For closed models (DeepSeek, GPT-4o) the period contrast is descriptive only; confounded by topic drift, regime, source mix. RDiT barely defensible even for open models.
- **Quant**: Pre/post conflates three distinct leakage channels (article exposure / later-narrative exposure / realized-move memory) that must be separated.
- **NLP**: Cites the pilot — SR already doesn't distinguish pre/post on DeepSeek, so the cutoff contrast is empirically dead for the main model.
- **Editor**: Reviewers will demand CPT as the causal anchor, because nothing else identifies.

**Convergent ask:** CPT (dose-controlled) is the only defensible causal arm. Everything else is descriptive/observational, and should be framed that way.

### C3 — The 2000 + 2000 cross-lingual monolith is wrong shape
- **Quant**: Barbell instead — 600–800 deep-audit CN core + 5–10K shallow panel. 2K+2K is "too expensive to audit yet too small to power a 5-way cross."
- **Stats**: The cell targets are arithmetically impossible at 2000 cases/language. Full 5-way cross needs ≥72 cells × ≥30 = 2160 just to meet the fantasy minimum, and 5-way balance at that scale is not possible given observational factor correlations. Power calc: need ~850/comparison for 80% power at the Phase-4 OR=1.95; `≥100/cell` 3-way target gives ~0.28 power.
- **Editor**: MVP = 500–800 cases, single-language, 4 factors, 2 tasks, 2 models. Anything larger is unfeasible by May 25.
- **NLP**: SEC-filings-for-English injects a genre confound (boilerplate, length); "cross-lingual" becomes language × genre × length, which is underidentified.

**Convergent ask:** Drop the 2K+2K symmetric target. Either (a) tight single-language MVP (Editor) or (b) deep CN core + shallow panel barbell (Quant). English as *replication*, not *parity* (Quant/NLP/Editor align).

### C4 — Factor taxonomy is coarse and operationally underspecified
- **Quant**: Anchor strength and corpus frequency should be split into ≥3 continuous constructs (locator, event-family density, entity salience). Missing market-structure primitives: tradability/ADV, market cap, surprise, realization lag, AR magnitude, time-of-day.
- **NLP**: Operationalizations of "anchor strength" and "corpus frequency" are undefined; see Chang et al. / Kandpal et al. for prior-art definitions.
- **Stats**: Factors will be correlated in the real CLS corpus; balancing on some leaves imbalance elsewhere. Observational confounding isn't addressed.
- **Editor**: 6-factor crossed design is a scope-creep signal; cut to 4 factors max.

**Convergent ask:** Define each factor as a concrete, computable function on a CLS row before the spec freezes. Reduce factor count. Accept observational imbalance in the "panel" tier if using a barbell design.

### C5 — Scope is beyond one paper and beyond May 25
- **Editor**: Explicitly "3 papers stapled together" — benchmark + probe-validity + CPT + cross-lingual + masking + toolkit + extended corpus. Cut list: cross-lingual headline, masking track, Claude Code skill framing, extended corpus, 4-model matrix, 6-factor balance.
- **Stats**: Multi-method compatibility table is aspirational; none of Min-K% / MIA / extraction is actually specified at spec-readiness level.
- **NLP**: Multi-method compatibility over-claims; only counterfactual probes have concrete protocol.
- **Quant**: Agrees scale/shape is wrong, though *adds* a contamination→alpha track (net scope direction opposite to Editor — see Divergence D2).

**Convergent ask:** The May 25 ARR deadline forces a decision within ~1 week. Either declare an MVP and drop 70% of the proposal, or skip this cycle and target August 3 ARR.

### C6 — Multi-method compatibility and masking track are aspirational
- **NLP, Stats, Editor** all flag: the table in §"Multi-Method Compatibility" is unimplemented wishful thinking. Min-K% needs logprobs (DeepSeek broken); MIA needs labeled in/out-of-training sets (not produced); extraction needs verbatim spans (not derived). Masking is nice-to-have, not core.

**Convergent ask:** Either drop these sections or demote them to "future work."

---

## Divergent points

### D1 — How severe is the current draft?
- NLP: **Rebuild.** Construct invalidity is fatal.
- Editor: **Major revision, target Findings.** Scope is fatal but core idea survives.
- Stats: **Estimand first.** Treat as pre-spec, not pre-draft.
- Quant: **Major revision + expansion.** The idea is salvageable; needs *more* (contamination-to-alpha layer), not less.

Gap between NLP/Editor ("cut ruthlessly, construct-validate, or drop") and Quant ("good direction but add a tradability layer") is the biggest divergence.

### D2 — Expand or contract?
- **Contract camp (Editor, NLP, Stats):** MVP, drop cross-lingual, drop masking, drop multi-method, 500–800 cases, 2 models, 2 tasks.
- **Expand camp (Quant):** Barbell scale (600–800 deep + 5–10K shallow), add dose-controlled CPT calibration (0/1/2/5 doses), add a contamination→alpha track (tradable-panel returns, model-selection-distortion estimand), add market-structure primitives.

These are not obviously reconcilable. Quant's "expand" additions are all tradability-oriented and not duplicative with the Editor's cut list — but a combined plan would be ~2x the scope, not viable for May 25.

### D3 — Is cross-lingual a headline or a replication arm?
- **Editor:** Drop cross-lingual entirely for MVP.
- **NLP:** "Cross-lingual" as currently specified = language × genre × length (SEC filings vs CLS telegrams); underidentified; drop or redesign.
- **Quant:** Keep EN, but as **replication**, not **parity**. Acknowledges pooling is a mistake.
- **Stats:** Treat CN and EN as separate sub-studies. Pooling requires measurement-invariance assumptions that are effectively untestable.

Editor wants to drop; the other three want to demote. Closer to convergence than it first appears — no one defends the current "parity" framing.

### D4 — Is EMNLP 2026 ARR (May 25) the right target?
- **Editor:** Hard "freeze design by April 20 or skip cycle." June/July fallback doesn't exist; next ARR is August 3.
- **Stats, NLP, Quant:** Don't weigh in on deadline explicitly, but all of them imply the work implied by their recommendations cannot be done in 6 weeks.

Effective convergence: *either* an aggressive MVP-cut *or* skip May 25.

### D5 — Is the SR/FO probe family worth saving?
- **NLP:** `fo_any_change` → demote to negative control. `fo_flip_hedged` → reframe as "conflict susceptibility." Only construct-valid FO design is the PREREGISTRATION Arm 1 vs Arm 2 CPT contrast.
- **Stats:** Raw `fo_flip_hedged` is confounded by baseline neutral-output rates; should be normalized as `FO − NP` (FO minus neutral-paraphrase baseline).
- **Quant:** Treats SR/FO as proxies that need downstream alpha-contamination validation — agnostic on intrinsic validity.
- **Editor:** Doesn't evaluate the probe math directly; says "construct validity will be the first reviewer attack."

Mild convergence on "current metrics need baseline normalization and a construct-validation ladder"; divergence on whether they're salvageable at all.

---

## Points the proposal did NOT raise but reviewers think are important

These are issues that appeared in ≥1 review but are absent from the 12 open questions in the proposal:

1. **Estimand definition is missing** (Stats, echoed by NLP). No named target parameter → no defensible inference plan. This is logically prior to any question about scale or factor count.
2. **Dose-controlled CPT calibration** (Quant). The CPT arm should be run at multiple exposure doses (0, 1, 2, 5 repetitions) to convert probe-metric movement into a contamination-dose equivalent. This turns the benchmark from categorical ("memorized vs not") into a dose-response instrument and is the *only* way to bridge from SR/FO numbers to a physical quantity the field can interpret.
3. **Contamination → alpha bridge** (Quant). Without a tradable-panel return calculation showing contamination-induced alpha inflation, finance-facing readers will not cite or trust the benchmark. Proposal §"Paper Framing" treats the benchmark as standalone.
4. **Baseline neutral-paraphrase normalization** (Stats). `fo_flip_hedged` needs to be reported as `FO − NP` rather than raw, because models have different baseline change rates under neutral paraphrase. This changes the metric, the power calc, and the reporting tables.
5. **FO independence test** (Stats). LLM-generated false outcomes — are they independent of known_outcome in the way the design assumes? There needs to be an explicit test before they're trusted.
6. **Pilot already invalidated the pre/post SR contrast** (NLP). The DeepSeek pilot shows SR flips at similar rates on pre- and post-cutoff cases. The benchmark cannot build on a contrast that its own pilot has already disproven without first explaining why 10× more data would change the conclusion.
7. **CLS metadata-only release has no strong EMNLP/ACL precedent** (Editor). FinBERT-CN is not cited in EMNLP/ACL venues; reviewers will push back on "not actually usable." Either get a licensing answer from CLS before spec freeze or switch to a fully-public corpus for the core track.
8. **Arithmetic feasibility of the cell targets** (Stats, Editor). Full 5-way cross needs ≥72 cells; 2000/72 ≈ 27 cases/cell, below the stated ≥30 minimum. 192K model-condition calls at 4 models × 3 tasks × 4 conditions × 4000 cases is implausible for 6 weeks. Proposal's numbers literally do not arithmetic-check.
9. **Observational factor correlation** (Stats, Quant). The 6 factors will be correlated in the CLS corpus. "Balance by cross-tab" on some factors leaves imbalance elsewhere. This is an identification problem the proposal doesn't mention.
10. **Benchmark substrate framing vs new-detector framing** (Editor). Proposal positions FinMem-Bench as a new probing protocol. Editor recommends positioning it as a *substrate* benchmark that existing detectors (Min-K%, MIA, counterfactual) can be run on — differentiates from AntiLeakBench / MMLU-CF / LastingBench which harden benchmarks against contamination rather than measuring susceptibility to it.
11. **No ARR fallback plan** (Editor). The proposal implicitly bets everything on May 25. No June/July slot exists; the next ARR is August 3. Decision needs to be explicit.
12. **Pre-registration integration** (Stats, NLP). The project already has a `docs/PREREGISTRATION.md` tied to the PHASE 4-5 design. The benchmark proposal and the pre-registration are not reconciled. If the preregistered plan is the "causal anchor" arm, the benchmark proposal should be explicit that it builds *around* it, not replaces it.

---

## Decision points for next round

From the convergence above, the decisions that must be made before any spec work begins:

1. **Estimand** — write it down. τ_CPT (dose-response under continued pre-training) is the only causally identified option and the only one the Stats + NLP + Quant agents all accept.
2. **Scope mode** — MVP-cut (Editor/NLP/Stats) vs barbell-expand (Quant). Cannot do both for May 25.
3. **Deadline** — commit to May 25 MVP or shift to August 3 ARR. Affects everything downstream.
4. **Cross-lingual status** — headline (current) / replication arm / drop. All three reviewers who commented vote against "headline."
5. **Probe status** — keep SR/FO as primary, demote to negative controls, or rebuild. NLP/Stats require at least baseline normalization and construct-validation steps.
6. **CLS licensing** — attempt to get a real answer from CLS before spec freeze, or switch to a public corpus. Editor flags as reviewer-fatal.
7. **CPT dose arms** — single-dose (current) vs dose-response (Quant). Cheap to change now, expensive later.

---

## Orchestrator note

R1 produced high convergence on "this is not a spec yet, and the estimand + construct-validity gaps are prior to the scope question." Divergence is largely **expand vs contract**, which is resolvable only by making the deadline decision first.

Per the agent-roles protocol, this topic is **NOT CONVERGED** (2v2-ish split on expand vs contract; plus Stats requires an estimand decision that no one else framed). Recommended next step before Round 2:

- User decides: May 25 MVP or skip to August 3
- User decides: expand (Quant) or contract (Editor/NLP) scope direction
- Then Round 2 can focus narrowly on: estimand pinning, probe construct-validation ladder, and barbell-vs-MVP factor/cell spec.

Challenger pass (cross-model Claude sub-agent) is *not* urgent because the 4 Codex agents produced substantive internal disagreement (especially D1/D2) — there's already model-internal diversity to work with. Save Challenger for after user decides the direction, when the discussion has narrowed.
