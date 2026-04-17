# BENCHMARK MVP R3 — Decision Check Summary

**Date:** 2026-04-13
**Orchestrator:** Claude Code
**Round:** R3 (4 Codex domain agents, parallel, new threads with R1+R2 context inlined)
**Input:** `docs/DECISION_20260413_mvp_direction.md` (10 user decisions post-R2)
**Source reviews:**
- [BENCHMARK_R3_QUANT.md](BENCHMARK_R3_QUANT.md)
- [BENCHMARK_R3_NLP.md](BENCHMARK_R3_NLP.md)
- [BENCHMARK_R3_STATS.md](BENCHMARK_R3_STATS.md)
- [BENCHMARK_R3_EDITOR.md](BENCHMARK_R3_EDITOR.md)

---

## Per-decision verdict matrix

| Decision | Quant | NLP | Stats | Editor |
|---|---|---|---|---|
| **D1** Framing deferred | OK-w/c | OK-w/c | — | OK-w/c |
| **D2** Point-in-time fields | **NEEDS-REWORK** | — | — | OK-w/c |
| **D3** Cluster sampling (1/cluster) | OK-w/c | OK-w/c | OK-w/c | OK |
| **D4** Outcome function `O_i(H)` | **NEEDS-REWORK** | — | OK-w/c | OK |
| **D5** Pilot via reprint detection | OK-w/c | **NEEDS-REWORK** | — | **NEEDS-REWORK** |
| **D7** Agent-based annotation | OK-w/c | **NEEDS-REWORK** | OK-w/c | **NEEDS-REWORK** |

**4 of 6 open decisions have at least one NEEDS-REWORK flag.** No decision is entirely clean. But the issues are fixable — all reviews are constructive, none reject the MVP direction itself.

---

## The 3 critical blockers (must fix before R4 launch)

### B1 — Decision 5: text-replacement strategy breaks memorization measurement

**Raised by NLP, supported by Editor, ignored by user's original plan.**

**The problem (NLP's formulation):** Memorization detection methods are **surface-form sensitive**. Min-K%, MIA, extraction attacks all compute scores over the exact tokens in the input. If Qwen saw the CLS version during pretraining (e.g., "央行降准 50bp 释放流动性约 1 万亿元"), but the benchmark feeds it the SSE announcement version ("中国人民银行决定于 2026 年 X 月 X 日下调..."), **we are measuring the model's response to text it never saw**, not its memorization of what it actually saw.

The user's Decision 5 strategy ("detect reprints, replace CLS text with public-domain source") works for release licensing but not for measurement. If adopted as written, the memorization detector scores become uninterpretable.

**Quant's parallel concern:** Reprint-heavy cases will systematically differ in outcome distribution (announcement-heavy = clean outcomes; original reporting = noisy outcomes). Without `is_reprint` as a first-class stratification field, the entire MVP effect analysis will be confounded by reprint composition.

**Editor's parallel concern:** Calling SSE disclosures "public domain" is an overclaim (they're public, but not necessarily free of the original publisher's rights). Mixed public/licensed benchmark is reviewer-suspicious; a split of 60% public + 40% metadata-only invites questions about whether the analysis uses both or only the public portion.

**Convergent fix (all 3 agents aligned):**
1. **Never replace the measurement text.** The text used for memorization probing is the EXACT text the model most plausibly saw during pretraining. For CLS cases, that's the CLS text. Period.
2. **Store multiple text variants as separate fields**: `cls_text` (the measurement text), `public_source_text` (if a reprint was detected), `public_source_url`, `is_reprint` (boolean), `reprint_similarity_score`.
3. **Release strategy is a different question from measurement strategy.** The release can omit `cls_text` for cases where it's licensed, while the measurement runs locally on `cls_text` before release. This matches FinBERT-CN style.
4. **`is_reprint` becomes a stratification factor** — all analyses must report results separately on reprint cases vs original cases.
5. **Editor's alternative to consider**: instead of CLS + reprint-replacement, build a **smaller fully-public core** from SSE/SZSE disclosures directly (500-800 cases), and use CLS only as an extended, licensed track. This cleanly separates release from measurement.

### B2 — Decision 2: baostock 15-min CSI 300 data is NOT reliable

**Raised by Quant (live-probed akshare + baostock).**

**The problem:** The user's plan assumed baostock provides reliable 15-min intraday bars for CSI 300. Quant tested this: **it does not.** Coverage is inconsistent, historical depth is limited, and the bar timestamps don't always align with exchange session rules. For benchmark-adjusted intraday outcome labeling this is a technical blocker.

**Secondary missing fields Quant flagged** (not just "nice to have" — blocking):
- **Fixed return legs**: `c2o` (close-to-open), `o2c` (open-to-close same day), `o2o_1d` (open-to-open next session), `o2o_3d` — horizon-only AR (1d/5d/22d) doesn't distinguish intraday announcement timing from close-of-day signal
- **`timestamp_quality_flag`**: marks cases where announcement time is approximate (e.g., "around market open") vs precise
- **Finer session buckets**: `pre_open_auction` / `intraday` / `close_auction` / `post_close` — not just `pre_market / intraday / post_market`
- **Identity fields**: `ticker`, `exchange`, `target_scope` (company / sector / index) — currently implicit in the schema
- **`benchmark_id`**: which benchmark was used for AR adjustment on this specific case (so target-type-specific benchmarks can be stored without schema fork)
- **Corporate-action flags**: split, dividend, rights issue, name change within [-1d, +22d] of announcement
- **Survivorship bias flag**: was this entity still listed at announcement + 22d? Was it ST-transitioned or delisted?

**Convergent fix:**
1. **Do not assume baostock 15-min CSI 300.** Either (a) use a different intraday source, (b) drop the intraday granularity requirement and use only daily-close AR with session bucketing, or (c) restrict intraday analysis to individual-stock data (which baostock handles better) and use CSI 300 daily-close only.
2. **Add all fields above to the schema spec before R4.**
3. **Stats' parallel concern**: the outcome function (Decision 4) was written assuming 1-day and 5-day AR work fine. With baostock limitations, the outcome spec needs to be reconciled with actual data availability, which is the next point.

### B3 — Decision 4 ↔ Decision 2: silently incompatible

**Raised by Quant (explicit), confirmed by Stats (implicit).**

**The problem:** Decision 4 specifies multi-horizon AR (1d/5d/22d) with CSI 300 benchmark and 0.5σ neutral band. Decision 2 (as user wrote it) implies intraday anchoring via baostock 15-min bars. These two decisions are implicitly coupled: if intraday anchoring is used, the AR horizons need to start from a specific intraday timestamp; if only daily-close anchoring, the AR horizons are clean but intraday announcement precision is lost.

The decision doc as written doesn't force the user to resolve this. Either the schema is intraday-capable (requires reliable 15-min data, which baostock doesn't provide) or it's daily-close only (simpler but loses intraday signal).

**Stats' concrete additions to Decision 4:**
- **Rename `confidence` → `label_quality`** (the proposed field is about data quality, not probabilistic confidence)
- **Missing exact τ_i** (the cutoff rule for up/down/neutral) — currently vague
- **Missing horizon-matched neutral band** — 0.5σ of 20-day daily is not the right band for a 1d horizon vs a 22d horizon; needs to be horizon-specific
- **Missing target-type benchmark map**: company → CSI 300 is fine, but sector news needs sector index, index news needs... what?
- **Missing insufficient-history rule**: IPOs < 20 trading days of data — default rule needed

**Convergent fix:**
1. **Resolve intraday vs daily-close as a primary design choice** before locking schema. Recommend: **daily-close primary, intraday as optional secondary field populated only when baostock (or alternative source) has reliable data for that case.**
2. **Stats' renaming + horizon-matched band + target-type benchmark map + IPO rule** — all four should be added to the Decision 4 spec.
3. **`label_quality`** should flag when the outcome is computed under degraded conditions (missing intraday data, insufficient history, halt within horizon window).

---

## The second-tier concerns (fixable but important)

### T1 — Decision 3: canonical doc selection rule is too loose

**Raised by NLP and Stats.**

**The problem:** The decision says the annotator picks "earliest OR most representative" with reasoning. Both NLP and Stats argue this is too discretionary — annotator drift will introduce selection bias.

**Convergent fix:**
1. **Deterministic rule as default**: `canonical_doc_id` is automatically selected by a rule (e.g., earliest article in the cluster; ties broken by longest text; further ties broken by most-cited source)
2. **Override allowed but documented**: annotator may override the automatic selection but must record a reason code from a fixed list (not free text)
3. **Quant's parallel concern**: for market-moving events, the FIRST mention often precedes the official announcement by hours — a "rumor phase" vs "announcement phase" distinction. Add a `rumor_phase` flag and `time_to_first_mention` field.
4. **NLP's additional ask**: store full cluster membership (list of all article IDs in cluster) even though only the canonical is released, so downstream frequency analysis can reference it.

### T2 — Decision 7: LLM-agreement is triage, not acceptance

**Raised by NLP, Editor, and Stats.**

**The problem:** The user's workflow ("CC + Codex agree → accept; disagree → human review") treats LLM agreement as ground truth. All 3 agents independently say this is insufficient for EMNLP-level defensibility. Both Claude and Codex may share systematic biases (same web corpus, similar RLHF); two biased annotators agreeing is not evidence of correctness.

**Convergent fix (merging all 3 agents):**
1. **Human audit of the agreement bucket too**, not just disagreements — e.g., random 20% sample of agreement cases
2. **Human adjudication of 100% of disagreements**
3. **Per-field IAA targets**: κ ≥ 0.80 for categorical factors, ICC ≥ 0.75 for continuous, span F1 for entity extraction
4. **Few-shot prompts from a held-out calibration set** (never from production cases)
5. **Outcome labels are NOT LLM-annotated** — they are computed mechanically from market data. LLMs only annotate text-grounded factor fields (entities, event type, anchor constructs).
6. **Pilot size upgrade**: user suggested 50-100 cases; Stats recommends ~150 doubly-annotated clusters for bootstrap CI feasibility
7. **Stats' endogeneity resolution**: since outcome labels are mechanical from market data, and Qwen (target) ≠ Claude/Codex (annotator), the LLM-as-annotator circularity concern is structurally mitigated. This is the **cleanest positive finding** from R3 — but only holds if point 5 above is enforced.

### T3 — Decision 1: framing deferral is OK but...

**All 3 agents who commented (Editor, NLP, Quant) agree:** deferring the framing decision is OK in principle, BUT:
- **Editor**: must freeze a "paper shell" (structure + section outline + placeholder abstract) NOW, even if framing is open. Otherwise timeline slippage is baked in.
- **NLP**: schema must capture factor provenance (which factors derive from which literature, which are novel) because both framings will need this and it's expensive to retrofit.
- **Quant**: the baostock + point-in-time direction has "venue drift" risk — the schema is increasingly quant-flavored, which may not fit an EMNLP NLP audience even under substrate framing.

**Convergent fix:**
1. Freeze paper shell at R4 completion (not R5 or R6)
2. Add factor provenance fields to R4 output
3. Add a conscious "venue-drift check" at R4 — if the factor list is too quant-flavored, the paper is drifting toward a finance venue (JFE / RFS) rather than EMNLP

---

## Updated numbers

### Target N (Stats, revised post-R3)

**Previous R2 target**: 1,500 verified cases (800 core + 700 panel) based on DEFF=1.5 (m=3 cluster, ρ=0.25)

**Revised R3 target**: Under **true one-case-per-cluster** sampling (Decision 3 locks this), the design-effect inflation from within-cluster duplication collapses. DEFF ≈ 1.0-1.1.

- **Base target**: ~1,000-1,100 sampled clusters for 80% power on a single clean partition contrast at OR=1.95
- **Scope/loss margin**: 1,300-1,500 justified only if accounting for verification failures, factor annotation drops, or secondary contrast power
- **Pilot size upgrade**: 150 doubly-annotated clusters (up from user's 50-100) for bootstrap CI on IAA

Net effect: **target scale is slightly smaller than R2**, but the "effective sample" is now genuinely close to the nominal N. This is better-quality data, not less data.

### Timeline (Editor, revised)

**May 25 ARR is NOT realistic as the base plan** — Editor is direct about this.

**Only survivable path**:
- Licensing posture resolved (Decision 5 rework → B1) by **April 19-20**
- Paper shell frozen by **April 19-20**
- Pilot annotation running by **April 21**
- Otherwise honest target is **August 3 ARR**

The user has not explicitly committed to either deadline in the decision doc. This needs to be resolved.

---

## Placeholder abstract (Editor-produced)

Editor successfully wrote a 150-word credible abstract, BUT conditional on:
- **Framing**: "public-core primary, licensed extension secondary, Findings track, resource-track positioning"
- **NOT** the current mixed-release + framing-deferred plan as literally written

This is a signal that the current decision doc, unchanged, does not yet support a coherent paper pitch. The fixes in B1 (release strategy rethink) + T1 (deterministic canonical selection) + T2 (annotation rigor) collectively move the plan to where a credible abstract becomes writable.

Full abstract draft is in `BENCHMARK_R3_EDITOR.md`.

---

## Hidden coupling summary

1. **D2 ↔ D4**: intraday assumption in D2 vs horizon-based outcomes in D4. Resolve intraday vs daily-close as a primary choice. (B3)
2. **D5 → D3**: reprint-replacement strategy must couple with `is_reprint` as a stratification field. (B1)
3. **D5 → measurement**: replacing text for release vs measurement are different operations. (B1)
4. **D1 → schema**: factor provenance fields needed even if framing deferred. (T3)
5. **D7 → D4**: if outcome labels are computed mechanically (not LLM-annotated), Stats endogeneity concern is resolved. But this must be enforced in Decision 7's workflow spec. (T2)
6. **D2 venue drift**: baostock-driven schema tilts toward finance venue. Editor flagged. (T3)

---

## Positive findings (what R3 confirmed is sound)

1. **Event-cluster sampling (D3) is the right decision** — all 4 agents confirm it resolves the R2 design-effect concern
2. **Merging outcome function into point-in-time fields (D4) is sound** — the direction is right, only parameter details need fixing
3. **Pre-commit 档位 2 偏 1 (D9) is defensible** — Stats confirms it will survive reviewer critique IF cutpoints and contrast lists are frozen before any confirmatory detector run
4. **LLM-annotator endogeneity is mitigated structurally** by confining LLMs to text-grounded fields and computing outcomes mechanically (Stats)
5. **The MVP pivot itself is not in question** — no agent suggests returning to the original big proposal

---

## Recommended decisions before R4

The user must resolve these before R4 factor investigation can safely launch:

### Critical (B1, B2, B3):
1. **Release vs measurement text** (B1): commit to "measurement text = CLS, release = gated" OR "public-core-only for submission." Cannot be deferred.
2. **Intraday vs daily-close** (B2+B3): resolve the intraday ambition given baostock limitations. Recommend: daily-close primary, intraday secondary where reliable.
3. **Add the missing Decision 2 fields**: fixed return legs, timestamp quality, finer session buckets, identity, benchmark_id, corporate actions, survivorship. Update `DECISION_20260413_mvp_direction.md`.

### Important (T1, T2, T3):
4. **Canonical doc selection rule**: deterministic default + documented override
5. **Annotation workflow upgrade**: agreement-bucket audit, IAA targets, mechanical outcome labels, pilot size 150
6. **Paper shell freeze plan**: commit to a date (recommend same as schema freeze, April 19-20) or accept August 3

### Supporting:
7. **Deadline commitment**: May 25 (with all above fixes by April 19-20) vs August 3
8. **Venue-drift check**: conscious decision on EMNLP vs finance venue fit

---

## Orchestrator note

R3 is **NOT FULLY CONVERGED**. 4 of 6 open decisions have at least one NEEDS-REWORK. But the reworks are all **specific and implementable** — none require returning to the MVP pivot itself, only fixing the specific decisions' operationalization.

**Recommended next step**: the user updates the decision doc to address B1/B2/B3 (critical) before R4 launches. T1/T2/T3 (important) can be fixed as part of the decision doc update or deferred to R5/R6, at the user's discretion.

**Do NOT launch R4 factor investigation until B1 is resolved.** The measurement-vs-release text question directly affects what "the case text" means at the schema level, which affects how factors are defined and operationalized.

B2/B3 (baostock + intraday) are schema-level but not factor-level — R4 can theoretically proceed without them, but it's cleaner to fix them first.
