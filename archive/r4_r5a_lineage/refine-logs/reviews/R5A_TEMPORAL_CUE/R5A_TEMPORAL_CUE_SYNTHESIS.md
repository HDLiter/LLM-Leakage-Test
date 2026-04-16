---
title: R5A Temporal Cue Design — Orchestrator synthesis
stage: R5A Round 2 temporal session close
date: 2026-04-15
inputs: quant_lens.md, nlp_lens.md, stats_lens.md, editor_lens.md
codex_threads:
  quant:  019d93f4-ec74-7471-8020-a0cddbd84235
  nlp:    019d93f5-3309-73d0-8a12-0b637b9015d7
  stats:  019d93f5-6ea0-7f72-a7df-b51b7da57bfd
  editor: 019d93f5-e59d-76b0-9981-2b9dd04c8fbd
---

# R5A Temporal Cue Design — Synthesis

4 Codex (xhigh) lens passes answered Blocks A-E. Consensus was exceptionally high this round — only 2 genuine tensions (vs 7 in Step 1). Most positions converge strongly.

---

## Block A — Taxonomy: unanimous multi-dimensional, NOT single gradient

**Consensus (4/4):**
- **Multi-dimensional classification**, not a single L4→L1 ordered scale.
- All 4 lenses converge on **3 axes** (naming varies slightly):

| Axis | Quant name | NLP name | Stats name | Description |
|---|---|---|---|---|
| 1 | surface_resolution | surface_type | surface_resolvability | Does the text contain an explicit time token that a reader can see? |
| 2 | lookup_dependency | lookup_dependency | lookup_dependency | How much external knowledge is needed to pin the cue to a precise date? |
| 3 | editability_role | semantic_role | editability | Can the time cue be removed without destroying event semantics? |

- **L2 and L0.5 must NOT be merged** (unanimous). They load on different mechanisms: L2 (relative/ordinal like "Q1") requires calendrical reasoning from context; L0.5 (closed-reference like "第五届WAIC") requires entity→date memory lookup. The lookup mechanism is the memorization signal.

- **Multiple cues per article**: NLP proposes a per-article **cue inventory** with a derived `primary_event_anchor` label (the strongest/most specific cue used to index the event). Others are silent on the mechanism but agree on "vector label, not scalar."

- **Paper-facing simplification**: Editor recommends collapsing to **3 bins for the main text** (`explicit / indirect / none`) with the full multi-axis taxonomy in supplementary materials. Other lenses do not object to this framing strategy.

- **Annotation feasibility**: NLP estimates κ ≥ 0.80 for the primary anchor type (high confidence). Stats notes the confirmatory factor should be a categorical 4-cell design for power, not a 6-level ordinal.

**No tension.** The taxonomy design is effectively locked: 3-axis multi-dimensional classification, paper-facing 3-bin simplification, full taxonomy in supplement.

---

## Block B — Factor + manipulation dual role: unanimous

**Consensus (4/4):**
- Time-cue clarity should serve as **both** a new factor AND a manipulation variable.
- **Factor role**: a new **secondary factor in Bloc 0** alongside Cutoff Exposure. Quant and NLP converge on the construct name **"Temporal Anchor Recoverability"** — a text-side affordance for memory indexing, NOT memorization itself.
- **Manipulation role**: dose-response intervention (create temporal-clarity-degraded versions of the same article). Editor and Quant agree this is the **more valuable half** for the paper — it provides near-experimental identification that reviewers will remember.
- **Collinearity with Cutoff Exposure**: Stats estimates **low (|r| ~ 0.10-0.20)**. Structural reason: temporal-cue clarity is a pure text property (same for all models); Cutoff Exposure is case×model (depends on which model is evaluated). NLP and Quant argue the expected signature is an **interaction** (text-side retrieval key × model-side exposure opportunity), not collinearity. Stats confirms the bigger collinearity risk is with Anchor Strength and Session Timing, not Cutoff Exposure.
- **Hierarchy level**: secondary (Quant/NLP explicit).
- **Construct caveat** (NLP): "Temporal Anchor Recoverability measures the accessibility of temporal retrieval cues in the article text, not the degree of memorization itself. A high-recoverability article provides a strong key for memory lookup, but the lookup succeeds only if the model has actually memorized the event."
- **Literature provenance**: NOVEL — no published memorization benchmark uses temporal-cue clarity as a factor. The dose-response manipulation design has loose precedent in GSM-Symbolic (Mirzadeh 2024) for controlled perturbation, but the temporal-cue-specific application is new.

**Coverage constraint** (Editor): A coverage audit of **adjunct-type cases** (where time cues CAN be removed without destroying semantics) is required before committing to the manipulation path. If adjunct-type < 50% of CLS articles, the manipulation's population coverage is too narrow for confirmatory claims.

**No tension.** Dual role is locked; implementation details (exactly how many dose levels, which subset) deferred to pilot.

---

## Block C — D4 ADG: consensus on split, tension on paper placement

**Consensus (4/4):**
- **Split D4a (contradiction) and D4b (misdirection) conceptually** as two sub-measurements under one detector family slot, NOT two independent detectors.
- **D4b (misdirection) is the cleaner estimand** — all 4 lenses agree, for different reasons:
  - Quant: D4b maps directly to backtest integrity (can the model obey an as-of fence when text provides no anchor?)
  - NLP: D4a conflates temporal source arbitration (instruction-following hierarchy) with memorization; D4b isolates temporal gating
  - Stats: D4b has a cleaner potential-outcomes interpretation
  - Editor: D4a is harder to explain to reviewers without instruction-following confound caveats
- **Include a matched-date control for D4a** (NLP) — when the prompt's as-of date matches the text's temporal cues (no contradiction), that is the control condition.
- **D11 does NOT subsume D4b** (NLP/Stats explicit). D4b tests prompt-level gate compliance; D11 tests text-level anchor-mediated detector sensitivity. Different constructs.

**Tension — paper placement:**
- **Editor wants to demote D4 entirely** to appendix or compact sensitivity panel. Arguments: already the 7th-8th detector, two sub-modes push toward detector zoo, 76,800-call budget not justified for main text.
- **Stats/NLP/Quant want to keep D4 in the pool** (one family slot with D4b primary). Arguments: D4 is the only within-model temporal-gating detector; CMMD is cross-model and measures a different construct; losing D4 means no within-model Bloc 0 coverage.

**Resolution recommendation**: Keep D4 in the pool as one family slot (D4b primary, D4a secondary/diagnostic). Paper placement (main text vs appendix) is deferred to the Step 2 paper-architecture decision (Architecture A vs B per R5A_DEFAULTS.md §5). Editor's page-budget concern is legitimate and will be re-evaluated when the total detector count is known.

**Budget optimization**: Quant recommends NOT running both D4a and D4b at full scale initially. Start with D4b on a stratified subset (~800 cases × 6 models × 2 prompts = 9,600 calls). D4a only if D4b pilot shows signal.

---

## Block D — D11: unanimous reshape, NOT standalone

**Consensus (4/4):**
- **Adopt D11 in reshaped form**: a **temporal sensitivity protocol** applied to existing detectors (analogous to how EAS is a per-detector stratification field, not a standalone detector). NOT a standalone detector.
- **CMMD is the recommended primary backend** for D11 (Stats/Editor/Quant). Rationale: CMMD already spans the full 6-model fleet and is the primary Bloc 0 detector; running the dose-response on CMMD gives the cleanest temporal × cutoff interaction test.
- **Second backend** (optional): Editor recommends a text-conflict detector (SR/FO); Quant recommends FO or Min-K++. Stats says one backend is sufficient for confirmatory power; second is exploratory.

**Critical requirement (4/4 unanimous):** D11 MUST include a **length-matched non-temporal deletion control** to distinguish temporal-anchor effects from generic information loss. Without this control, D11 collapses into "removing content hurts performance." All 4 lenses flagged this independently — it is the make-or-break design feature.

**Control design**: Remove a same-length phrase that is NOT a temporal cue (e.g., a descriptive adjective, a subsidiary clause about market conditions). If detector scores drop equally under temporal removal and non-temporal removal, the temporal channel is not real.

**Power** (Stats): Adequate for main slope at ~1,600-2,100 eligible adjunct-type cases (detectable effect d = 0.10-0.15). Not enough for many subgroup interactions at this sample size. Stats recommends D11 as **secondary/exploratory**, not confirmatory — consistent with the multiplicity warning (adding factor + D4a + D4b + D11 as independent confirmatory detectors inflates from ~60 to ~104 coefficients, +73%).

**Cost optimization**: Start with 2-3 dose levels (not the full L4→L1 gradient) on a stratified subset. Quant and Stats both reject the full 76,800-call grid as the starting point.

**Editor's abstract snippet** (successfully drafted):
> "FinMem-Bench exploits a distinctive property of financial news: temporal anchors can often be weakened by minimal edits without changing the underlying event. We construct time-attenuated variants and test whether memorization signals decay as explicit temporal cues disappear. This temporal dose-response separates detector reliance on retrievable time anchors from generic event understanding."

This snippet passed Editor's own "can you sell it in 3 sentences" test, which is evidence that D11-reshaped has a clean narrative.

---

## Block E — Time-handling axis: high consensus

**Consensus (4/4):**
- **Global default: preserve temporal cues** in all perturbation variants (D5/D6/D7) for the primary analysis.
- **Pre-register one sensitivity branch** with temporal cues masked/removed (Stats/Editor).
- **Do NOT expand D7 EAD to 2×2×2** (Quant/NLP/Editor unanimous). Time masking is a separate construct from entity masking. If time-cue manipulation is needed on top of EAD, it is handled by D11, not by tripling EAD's already-expensive taxonomy.

**Per-detector specifics:**

| Detector | Primary (preserve time) | Sensitivity (mask time) | Rationale |
|---|---|---|---|
| **D5 SR/FO** | Preserve original dates in counterfactuals | One sensitivity run with dates removed | Preserving dates makes the counterfactual a more realistic alpha test (Quant); removing dates tests pure semantic sensitivity (NLP). Both are informative. |
| **D6 FinMem-NoOp** | Inserted NoOp clause should NOT contain temporal cues (Quant/NLP/Editor) | If unavoidable, time-match to original article's window | A temporal cue in the NoOp clause could accidentally trigger time-based retrieval, confounding the "irrelevant" design. |
| **D7 EAD** | Standard 2×2 masking taxonomy (target/competitor × full-anon/category-preserving) | Time-cue masking as a separate D11-protocol layer, NOT integrated into EAD | Keeps EAD focused on entity identity; time-cue effects measured independently. |

**No tension.** Time-handling axis is effectively locked: preserve as primary, mask as pre-registered sensitivity, D7 not expanded.

---

## Summary of outcomes

| Block | Status | Key decision |
|---|---|---|
| **A Taxonomy** | Locked | 3-axis multi-dimensional; paper-facing 3-bin; full taxonomy in supplement |
| **B Factor role** | Locked | Dual: secondary Bloc 0 factor "Temporal Anchor Recoverability" + dose-response manipulation |
| **C D4 ADG** | Mostly locked | Split D4a/D4b one slot; D4b primary; paper placement deferred to Step 2 architecture |
| **D D11** | Locked (shape) | Reshaped as temporal sensitivity protocol on CMMD (+1 optional); NOT standalone; needs non-temporal deletion control; secondary/exploratory status |
| **E Time axis** | Locked | Preserve as primary default; mask as sensitivity; D7 not expanded |

**New artifacts for the project:**
- **Factor 13: Temporal Anchor Recoverability** — secondary, Bloc 0, literature provenance NOVEL
- **D4 ADG redesigned** as D4a (contradiction, secondary) + D4b (misdirection, primary), one family slot
- **D11 reshaped** as temporal dose-response sensitivity protocol (EAS-like field), not standalone detector
- **Adjunct-type coverage audit** — required before committing to the manipulation path; if adjunct-type cases < 50%, narrow to observational factor only

**Paper-space estimate** (Editor): Recommended package = 1 taxonomy table + 1 dose-response figure + 4-5 paragraphs. Full package would cost ~2 pages — too expensive for 9-page paper; must be scoped tightly.

**Multiplicity warning** (Stats): Adding Temporal Anchor Recoverability as a factor alone is manageable (+5 coefficients). Adding factor + D4a + D4b + D11 as independent confirmatory elements inflates from ~60 to ~104 coefficients. Keep D11 secondary/exploratory and D4a diagnostic to stay within the multiplicity budget.

---

## Open items carried forward to Step 2

1. **Adjunct-type coverage audit** — what fraction of CLS articles have removable (adjunct-type) temporal cues? Pilot needed.
2. **D4 paper placement** — main text one-slot or appendix sensitivity panel? Depends on final detector count.
3. **D11 backend choice** — CMMD is consensus primary; is a second backend (SR/FO or Min-K++) worth the cost?
4. **D11 dose levels** — start with 2-3 or full 4-level gradient? Pilot-dependent.
5. **Non-temporal deletion control design** — what phrases qualify as "length-matched non-temporal"? Implementation-session territory.

---

## Artifacts

- `quant_lens.md` — thread `019d93f4-ec74-7471-8020-a0cddbd84235`
- `nlp_lens.md` — thread `019d93f5-3309-73d0-8a12-0b637b9015d7`
- `stats_lens.md` — thread `019d93f5-6ea0-7f72-a7df-b51b7da57bfd`
- `editor_lens.md` — thread `019d93f5-e59d-76b0-9981-2b9dd04c8fbd`
- `R5A_TEMPORAL_CUE_BRIEF.md` — input brief
- `R5A_TEMPORAL_CUE_SYNTHESIS.md` — this file
