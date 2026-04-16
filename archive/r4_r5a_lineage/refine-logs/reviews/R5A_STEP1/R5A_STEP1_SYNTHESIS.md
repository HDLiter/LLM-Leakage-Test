---
title: R5A Step 1 — Orchestrator synthesis of 4-lens detector brainstorm
stage: R5A Step 1 close
date: 2026-04-15
inputs: quant_lens.md, nlp_lens.md, stats_lens.md, editor_lens.md
authoring: Claude Code orchestrator synthesizing 4 xhigh Codex lens outputs
codex_threads:
  quant: 019d9149-20e2-7313-af6e-b0555accb3fd
  nlp:   019d914a-0dde-7120-a1a7-3c3b991899c9
  stats: 019d914a-5835-7053-b20e-903aaa2243b7
  editor: 019d914b-2d18-7c40-9113-00183a9c8e21
---

# R5A Step 1 — Integrated detector pool

Four Codex (xhigh) lens passes produced **27 raw detector candidates** (7+7+7+6) from Quant / NLP / Stats / Editor lenses. After de-duplicating near-identical proposals across lenses, the integrated pool is **10 distinct detectors**. R5A Step 2 will converge this pool to a 5-8 detector shortlist.

This synthesis is **orchestrator tabulation and consensus extraction**, not new reasoning; substantive design work belongs to Codex in Step 2.

---

## 1. Cross-lens detector matrix

Naming reconciled (different lenses use different names for the same core detector).

| # | Canonical name | Q | N | S | E | Mechanism family | Primary bloc(s) | Access |
|---|---|---|---|---|---|---|---|---|
| D1 | **CMMD** — Cross-Model Memorization Disagreement | ✅ C1 | ✅ | ✅ | ✅ | Cross-model + temporal | 0 (+2) | Either; full 6-model fleet |
| D2 | **PCSG** — Paired Cutoff Surprise Gap | — | — | ✅ **#1** | — | Temporal-cutoff-conditional (paired surface) | 0+1 crossover | White-box; 3 local models |
| D3 | **Min-K%++ / Calibrated Tail Surprise** | ✅ C2 (Cutoff Min-K++) | ✅ (CTS) | ✅ | ✅ | Surface-form (MIA-adjacent) | 1 | White-box; 3 local models |
| D4 | **As-of Date Gating (ADG)** | — | ✅ | — | — | Temporal-cutoff-conditional (within-model) | 0 | Either; full fleet |
| D5 | **SR/FO Counterfactual Pair** (Semantic Reversal + False Outcome; Stats merges as CFI "Counterfactual Fact Inertia") | ✅ C3 (FO only) | ✅ (SR + FO separate) | ✅ (CFI merged) | ✅ (SR/FO paired family) | Counterfactual | 0 (SR), 1-2 (FO) | Either; full fleet |
| D6 | **FinMem-NoOp** | ✅ C4 | ✅ | ✅ | ✅ | Counterfactual (negative control) | 2 (+3 per Editor) | Either; full fleet |
| D7 | **Entity-Anonymization Delta (EAD)** — also pre-seeded as P5 field | ✅ C5 (Entity Mask Delta) | EAS field only | ✅ (EAD) | EAS field only | Counterfactual | 2 | Either; full fleet |
| D8 | **Extractable Span / Targeted Span Extraction / Extraction-Lite** | ✅ C6 (Masked Suffix) | ✅ (ESR) | ✅ (Ext-Lite) | ✅ | Extraction | 1 (+0 crossover) | Either; full fleet |
| D9 | **RAVEN Novelty Gap** | — | — | — | ✅ | Hybrid (output-behavior novelty) | 1 | Either |
| D10 | **Debias Delta** (Merchant-Levy inference-time debias) | ✅ C7 | — | — | — | Temporal-cutoff-conditional (mitigation-first) | 0+2 | White-box; 3 local models |

Legend: Q=Quant, N=NLP, S=Stats, E=Editor. ✅ = lens proposed this detector. Bold + number = top pick for that lens.

**Unanimous detectors (4/4 lenses):** D1 CMMD, D3 Min-K%++-family, D5 SR/FO, D6 FinMem-NoOp, D8 Extraction-family.
**3/4 lenses:** D7 EAD (Stats & Quant promote to standalone detector; NLP & Editor treat as P5 field only — this is a legitimate design tension, see §5).
**Single-lens proposals:** D2 PCSG (Stats, novel contribution), D4 ADG (NLP, distinct mechanism from CMMD), D9 RAVEN (Editor, EMNLP-facing output-behavior), D10 Debias Delta (Quant, Stats-flagged as mitigation-not-detector).

---

## 2. Family × bloc coverage matrix

Kickoff Seed 3 mandates coverage across 5 mechanism families AND 4 Risk R4 blocs.

### Mechanism family coverage (kickoff Seed 3)

| Family | Detectors in pool | Coverage status |
|---|---|---|
| Surface-form sensitivity | D3 Min-K%++/CTS | ✅ covered (single detector — NLP explicit that this is intentional to avoid Bloc 1 collapse) |
| Counterfactual perturbation | D5 SR/FO, D6 FinMem-NoOp, D7 EAD | ✅ over-covered (3 detectors) — largest family by candidate count |
| Cross-model disagreement | D1 CMMD | ✅ covered (single detector) |
| Extraction / verbatim recall | D8 Extraction-family | ✅ covered (single detector) |
| Temporal-cutoff-conditional | D1 CMMD (primary), D2 PCSG, D4 ADG, D10 Debias Delta | ✅ over-covered (4 detectors spanning cross-model / paired surface / within-model chronology / mitigation) |

### Bloc coverage (Risk R4 v6.1 4-bloc)

| Bloc | Factors | Primary detectors | Status |
|---|---|---|---|
| **Bloc 0** — temporal exposure | Cutoff Exposure | D1 CMMD, D2 PCSG, D4 ADG, D5 SR, D10 Debias Delta | ✅ strong (5 detectors) |
| **Bloc 1** — repetition / surface reuse | Propagation Intensity, Template Rigidity, surface_template_recurrence | D3 Min-K%++, D8 Extraction, D9 RAVEN, D2 PCSG (secondary), D5 FO (secondary) | ✅ strong — ⚠️ collapse risk if >2 make the final shortlist |
| **Bloc 2** — prominence / attention | Entity Salience (target + competing), Target Scope, Tradability Tier | D7 EAD, D6 NoOp | ✅ adequate (2 detectors) |
| **Bloc 3** — institutional stage / source | Structured Event Type, Disclosure Regime (PLACEHOLDER), Event Phase, Session Timing | — | ❌ **UNCOVERED** — no primary Bloc 3 detector in the pool |

### ⚠️ Critical gap — Bloc 3

**No detector in the integrated pool targets Bloc 3 as a primary.** The closest is Editor's framing of FinMem-NoOp with secondary Bloc 3 spillover via "commentary shows larger NoOp effects than formal disclosures." Stats explicitly flagged Bloc 3 as the **most under-powered bloc** for post-hoc analysis (most categorical structure, highest internal correlation, unfrozen Disclosure Regime placeholder). Quant flagged the absence in its synthesis.

**This is a Step-2 decision point.** Three options:

1. **Accept the gap** — relegate Bloc 3 to factor-only analysis (the detector layer measures temporal/prominence/repetition; institutional stage is measured as a stratifier across detectors, not with a dedicated detector).
2. **Design a new Bloc 3 detector** — e.g., a **Modality-Gated Recall** probe asking the model to identify the originating institution or source type; or a **Disclosure-Schema Extraction** probe scoring how well the model completes canonical regulatory/corporate-action templates.
3. **Upgrade existing detectors' Bloc 3 stratification** — treat Bloc 3 exclusively through (detector × event_type) and (detector × disclosure_regime) cells in the P4 interaction menu, with no dedicated detector.

**Recommendation for Step 2:** Start Step 2 with option 3 as the default (cheapest, no new detector engineering), but run option 2 past Codex as a specific design question. Option 1 is explicit narrative concession; it should only be accepted if options 2/3 fail.

---

## 3. Unanimous cross-lens consensus

All 4 lenses independently converged on the following, which should be treated as **locked for Step 2** absent new evidence:

1. **Independent detector reporting, not ensemble.** All 4 lenses reject an MCS-style heterogeneous logistic-regression composite as the *primary estimand*. Stats provides the FWER argument; NLP the construct-validity argument; Editor the narrative argument; Quant the deployment-translation argument.
   - Allowed exception: a descriptive appendix-only synthesis (e.g., z-scored average, sign-consistency summary, or Stats' surface-only composite on a held-out calibration split) is acceptable if it is clearly secondary and not counted in the confirmatory family.

2. **Deviate from MemGuard-Alpha's 5-MIA+LR stack.** Editor explicit ("deviate"); Stats implicit ("not the right primary estimand"); NLP implicit (construct-validity framing); Quant implicit (independent detectors primary, MCS "only as a secondary deployment translation layer"). Mirroring MemGuard-Alpha = novelty loss + Meeus 2024 identification skepticism inheritance.

3. **CMMD is a top-3 pick for all 4 lenses.** Quant #1, Stats #3, Editor #3, NLP #1. No lens recommends dropping CMMD.

4. **FinMem-NoOp must be rule-based first, LLM-validated second.** NLP concrete rule: "same-window clause from different normalized entity, different cluster, non-entailing event, controlled clause length and CLS style." Stats concurs ("only acceptable if the clause generator is deterministic, time-matched, target-irrelevant, and preregistered"). Editor concurs ("lives or dies on the definition of 'irrelevant but plausible'"). Free-form LLM generation is unanimously rejected.

5. **Entity-Anonymization Sensitivity goes in, but split.** NLP's refinement: `target-mask delta` and `non-target-mask delta` must be stored separately because they test different distraction channels (target prominence vs Glasserman-Lin competing-entity distraction). A single blended EAS score is unanimously rejected as too coarse.

6. **Meeus 2024 SoK restriction is accepted, not challenged.** For MIA-adjacent detectors (D3 Min-K%++/CTS is the only one), the NLP lens answer — shared by Stats — is to **reframe** rather than defend: "surface-familiarity baseline, not a validated membership estimator." No shadow-model ensemble, no strong membership language, no primary claim resting on the surface-form detector alone.

7. **Detector shortlist ceiling.** Editor's hard cap of 5 detectors (healthy = 4) for a 9-page paper is compatible with Stats' "5 primary + 2 reserve" structure. R5A Step 2 should plan a 4-5 detector main-text slate.

---

## 4. Cross-lens tensions (to resolve in Step 2)

These are genuine design disagreements, not terminology confusion. Step 2 must pick one side or document the trade-off.

### 4.1 EAD: standalone detector or P5 field only?

- **Stats (#2 primary pick) and Quant (C5) promote EAD to a standalone detector** — a within-case paired intervention with a direct identification argument.
- **NLP and Editor treat EAS as a detector-level field applied across other detectors** — no standalone detector; the "delta under masking" is a stratification field of each of the other 5 detectors.

The two positions are not strictly incompatible: EAD-as-standalone-detector can coexist with EAS-as-field-on-other-detectors. But the cost differs — EAD-as-standalone roughly doubles the counterfactual-family compute (Stats estimates 30,720 calls), while EAS-as-field is already counted in each parent detector's budget.

**Step 2 question:** Is EAD's within-case intervention distinctive enough to pay a dedicated 4th counterfactual-family slot, or is it subsumed by the EAS field applied to D1/D3/D5/D6/D8?

### 4.2 SR and FO: paired family or two detectors?

- **Quant** proposes FO only (as standalone C3) and does not separately propose SR.
- **NLP** proposes SR and FO as two independent detectors (distinct mechanisms: SR = polarity overwrite, FO = slot anchoring).
- **Stats** merges them into one detector "Counterfactual Fact Inertia" (CFI).
- **Editor** treats them as one paired family "SR/FO Counterfactual Pair" and explicitly warns: "If you keep SR and FO in one family, the paper stays focused; if you split them into two headline detectors, the narrative starts to look like a perturbation suite."

**Step 2 question:** For the shortlist slate, is SR/FO counted as one detector or two? Editor's 5-detector ceiling suggests one paired family is correct, but NLP's MTMM argument (SR and FO have different nomological predictions) suggests they produce two distinct stratification fields even within a single detector line-item.

### 4.3 Surface-form family: one detector or two temporal variants?

- **Quant** proposes `Cutoff Min-K++` (surface + temporal interaction) as one detector.
- **Stats** proposes both `Min-K%++ Tail Surprise` (standalone surface) AND `Paired Cutoff Surprise Gap` (paired contrast that reuses the same logprob traces). Stats' PCSG is the **only novel detector in the pool** — no other lens proposed it.
- **NLP** proposes `Calibrated Tail Surprise` (CTS) with divergence-based frequency correction — at most one surface detector.
- **Editor** proposes `Min-K%++` as the single surface detector.

**Step 2 question:** Does Step 2 preserve PCSG (Stats' best-identified detector, cost-amortized on Min-K%++ traces) as a separate detector, fold it into Min-K%++ as a stratification field, or reject it? Stats' identification argument ("paired contrast removes case-difficulty variance; best power-per-case in the slate") is strong. PCSG's orphan status (single-lens proposal) should not automatically demote it.

### 4.4 ADG vs CMMD: complementary or redundant?

- **NLP** proposes `As-of Date Gating (ADG)` as a within-model chronology-compliance detector, distinct from CMMD's cross-model disagreement mechanism. NLP's argument: ADG should diverge from ESR/Min-K where familiarity leaks through explicit chronology instructions.
- **No other lens proposes ADG.** Wongchamcharoen & Glasserman 2025 is cited in the R5 reading queue and directly supports ADG.

**Step 2 question:** Is ADG additive over CMMD, or does it measure the same Bloc 0 construct with higher cost? NLP's claim is it tests a **different mechanism** (within-model chronology reasoning, not cross-model agreement). Step 2 should ask whether the project's paper budget can afford 2 temporal detectors.

### 4.5 Extraction family: one detector or skipped?

All 4 lenses include an extraction-family detector (D8). But:

- **Quant** (Masked Suffix Extraction) positions it as **high-precision anchor** — keeps the paper honest even if under-covers the alpha channel.
- **NLP** (ESR) positions it as **narrow but exceptionally traceable construct** — underinclusiveness is a feature.
- **Stats** (Extraction-Lite Continuation Hit) positions it as **reserve / validation detector** (Stats' shortlist has it in reserve, not primary), citing power constraints at this N.
- **Editor** positions it as **optional 5th-slot** competing with RAVEN — not in the core 4.

Quant's synthesis explicitly flags extraction as **the family most likely to remain uncovered by a Quant-only shortlist**, suggesting the lens saw the gap. But Stats + Editor both want to demote it to reserve / optional.

**Step 2 question:** Is the extraction detector in the main-text 4-5, or a reserve-only corroborative check reported in a supplementary table? Trade-off: extraction has the clearest qualitative story ("exact reuse") but lowest power at N≈2,560.

### 4.6 Debias Delta: detector or mitigation baseline?

- **Quant (C7)** proposes Debias Delta as both detector and deployment mitigation. Quant's own synthesis notes it is a "heavier Step 2 candidate" and flags materially higher engineering burden.
- **No other lens proposes Debias Delta.**

**Step 2 recommendation:** Treat as Step 2 low-priority. If Step 2 has room, evaluate it as a companion to D3/D2 (since both run on the same 3 white-box models); if not, drop.

### 4.7 RAVEN: EMNLP-facing or redundant with Template Rigidity?

- **Editor** proposes RAVEN as optional 5th-slot EMNLP-facing output-behavior detector.
- **No other lens proposes RAVEN.** NLP references McCoy 2021 RAVEN as framing for FinMem-NoOp novelty checks, but not as a standalone detector.
- Editor itself warns: "can blur into Template Rigidity unless carefully separated."

**Step 2 recommendation:** Drop unless Step 2 decides the paper needs a dedicated output-behavior detector for venue-fit reasons. Default = drop.

---

## 5. Open questions consolidated from all 4 lenses

Deduplicated and grouped. Each is tagged with the lens that raised it and the lens(es) that need to answer.

### 5.1 Questions about detector implementation quality (Chinese CLS)

1. **[Quant → all; Editor → all]** What is the minimum Chinese counterfactual-edit audit standard that makes FO / NoOp / EAD admissible as contamination evidence rather than prompt-artifact evidence? Can SR/FO and FinMem-NoOp be implemented with rule-bound, auditable generation quality on Chinese CLS, or do they require enough LLM editing that a new method-bias layer dominates?
2. **[Stats → NLP + Editor]** Can we define a **rule-based FinMem-NoOp clause bank with explicit proofs of target irrelevance**? If not, keep NoOp reserve-only.
3. **[NLP → Editor]** SR/FO rewrite naturalness — who owns the antonym/slot lexicon per event type? What is the acceptance protocol?
4. **[NLP → Editor]** For NoOp specifically: what maximum clause length and discourse-position constraints preserve CLS style without making the edit trivially ignorable?

### 5.2 Questions about factor freeze / unfrozen dependencies

5. **[Stats → Editor; Editor → all]** Will `Disclosure Regime` be frozen before detector lock, and what is the finalized anchor-strength rubric reliability threshold? **If `Disclosure Regime` is replaced by Thales `Modality`, which detector-factor arguments survive unchanged and which need rewriting?** (This directly affects Bloc 3 coverage analysis in §2.)
6. **[Editor → Quant; Stats → Quant]** For FO specifically, do we have enough `known_outcome` coverage to avoid generic-template degradation already seen in pilot notes?

### 5.3 Questions about statistical modeling and identification

7. **[NLP → Quant + Stats]** Are detector outputs staying **continuous**, or will Step 2 force thresholds? Thresholding too early throws away validity signal.
8. **[NLP → Quant + Stats]** Will the **case×model structure** of Cutoff Exposure be modeled explicitly as repeated measures, or flattened into per-case summaries?
9. **[Stats → Quant]** What is the expected realized distribution of `cutoff_gap_days` by model after gray-band exclusion, and can we preregister **placebo pseudo-cutoff controls**?
10. **[Stats → NLP]** Can Thales produce deterministic target spans, competitor spans, placebo masks, and counterfactual edits with **auditable pass rates**?

### 5.4 Questions about reproducibility and presentation

11. **[Editor → Quant]** Can CMMD be frozen reproducibly at the checkpoint/provider level **before paper-writing**, or does it need to be demoted from central to confirmatory?
12. **[Editor → Stats]** If Min-K%++ only runs on the 3 white-box models, how does Stats present it as **corroborative evidence** without forcing a misleading full-fleet comparison?

### 5.5 Questions raised here by orchestrator (not by any lens directly)

13. **Bloc 3 coverage gap** (§2): option 1 (accept), option 2 (new detector), or option 3 (cross-detector stratification)?
14. **Detector shortlist convergence target for Step 2:** Editor ceiling = 5; Stats primary slate = 5 + 2 reserve; NLP top 3 + 4 supporting = 7. Step 2 target should be **4-5 main text + 1-2 reserve**. Confirm before Step 2 agent brief.
15. **Entity-Anonymization Delta dual-role resolution** (§4.1): pick one of (a) standalone detector, (b) P5 field only, (c) both — this is not a rhetorical question and Step 2 must commit.

---

## 6. Pre-Step-2 readiness assessment

### What is ready for Step 2 agent brief

- Integrated detector pool (D1-D10, this document)
- Unanimous consensus items (§3) as locked inputs
- Family × bloc coverage matrix (§2)
- Top-3 picks per lens (for cross-validation of Step 2 verdicts)

### What Step 2 must resolve before convergence

- 7 cross-lens tensions (§4) — each needs a ruling or a documented trade-off
- Bloc 3 gap (§2 recommendation: option 3 default, ask Codex about option 2)
- 15 open questions (§5) — some can be answered by the user, some by Codex, some by the Thales dedicated session

### What is blocked on out-of-band tracks

- FO / NoOp / EAD implementation quality depends on **Thales pipeline deterministic span outputs** (§5.1 Q2, §5.3 Q10)
- Disclosure Regime factor freeze depends on **Thales dedicated session** (§5.2 Q5)
- CMMD reproducibility depends on **pre-commit checkpoint pinning** (§5.4 Q11)

None of these out-of-band dependencies block Step 2 itself — Step 2 can close the conceptual shortlist (R5A deliverable) with assumptions flagged. R5B (executable shortlist) is where these blocks actually bite.

---

## 7. Recommended Step 2 agent brief seeds

Step 2 (per kickoff agenda) runs another 4-Codex-agent pass, this time reviewing the integrated pool rather than brainstorming fresh. Each Step 2 agent should receive:

1. **This synthesis document** as the primary input
2. **Their own Step 1 output** as their prior position (for delta tracking)
3. **The 7 cross-lens tensions (§4)** as explicit decision points — each agent must rule on each tension from their lens
4. **The 15 open questions (§5)** with instruction: answer the ones within your lens's competence, flag the ones that need the user or another track
5. **The Bloc 3 gap (§2)** with instruction to commit to option 1 / 2 / 3 explicitly
6. **The 4-5 main text + 1-2 reserve shortlist target** as the convergence objective

After Step 2: Challenger pass → cold-reader pass → R5A close with frozen conceptual shortlist.

---

## 8. Artifacts

- `quant_lens.md` — 7 candidates, Quant lens, thread `019d9149-20e2-7313-af6e-b0555accb3fd`
- `nlp_lens.md` — 7 candidates, NLP lens, thread `019d914a-0dde-7120-a1a7-3c3b991899c9`
- `stats_lens.md` — 7 candidates, Stats lens, thread `019d914a-5835-7053-b20e-903aaa2243b7`
- `editor_lens.md` — 6 candidates, Editor lens, thread `019d914b-2d18-7c40-9113-00183a9c8e21`
- `R5A_STEP1_SYNTHESIS.md` — this file

All four Codex threads are still resumable via `mcp__codex__codex-reply` if Step 2 wants to interrogate a specific lens on a specific candidate without a full context reload.
