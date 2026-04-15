# BENCHMARK MVP R2 — Multi-Agent Feasibility Check

**Date:** 2026-04-13
**Orchestrator:** Claude Code
**Round:** R2 (4 Codex domain agents, continuing R1 personas with R1 context inlined)
**Trigger:** User proposed a narrower MVP after reading R1

**MVP proposal under review:**
- Chinese-only (drop English for MVP)
- Drop SR/FO from the MVP itself — don't bake counterfactual probes in
- Core per-case fields: (1) factor annotations + strata stats, (2) verified outcome, (3) key entities
- Scale: as large as feasible, sufficient per sub-partition
- Then: run project probes + existing methods (Min-K%, MIA, extraction) on the substrate
- Then: check partition-level memorization differences, decide next extensions

**Source reviews:**
- [BENCHMARK_R2_QUANT.md](BENCHMARK_R2_QUANT.md)
- [BENCHMARK_R2_NLP.md](BENCHMARK_R2_NLP.md)
- [BENCHMARK_R2_STATS.md](BENCHMARK_R2_STATS.md)
- [BENCHMARK_R2_EDITOR.md](BENCHMARK_R2_EDITOR.md)

---

## Verdict spread

| Agent  | Verdict                   |
|--------|---------------------------|
| Quant  | **Conditional GO** — reframe as substrate; lock point-in-time market mechanics NOW |
| NLP    | **Conditional GO** — only if factor taxonomy is literature-backed + dup-cluster schema committed |
| Stats  | **Conditional GO** — as descriptive substrate; firm NO-GO on "measures memorization" claim |
| Editor | **GO** on pivot — materially fixes "3 papers stapled"; venue = EMNLP Findings via May 25 ARR |

**All 4 converge on GO.** This is a strong signal — R1 had 4 different verdict severities; R2 is unanimous. The user's MVP pivot is correctly calibrated to the R1 convergent critique.

But every agent attaches a **must-commit-now** condition, and the conditions are different. The next step is merging them into one schema spec.

---

## C1 — Framing must retreat from "memorization benchmark" to "audit substrate"

- **Quant**: Call it a "point-in-time substrate for stress-testing detectors across strata." Not a leakage benchmark.
- **NLP**: This MVP relocates the contribution away from contested probes but does NOT by itself fix construct validity. It postpones the reckoning cleanly only if the substrate is explicitly built to support future negative/positive controls.
- **Stats**: GO as descriptive substrate + partition contrasts. **Firm NO-GO on any "measures memorization" claim** until CPT calibration + detector-level pre-registration land.
- **Editor**: Claim narrows from "proving memorization" to "factor-controlled audit substrate + detector partition analysis." The pitch: _"FinMem-Bench turns financial LLM contamination from an uncontrolled nuisance into a controlled audit variable."_

**Convergent ask:** The paper title, abstract, and contribution claim must NOT say "we measure memorization." They must say "we provide a substrate on which existing detectors can be audited across factor strata." All 4 agents will flag any broader claim as construct-invalid.

---

## C2 — Schema must be locked before collection (each agent names different must-have fields)

This is where R2 is most actionable. Four different "commit this now or pay later":

| Agent | Must-commit-now fields |
|---|---|
| **Quant** | Point-in-time market mechanics: fixed-horizon AR (multiple horizons stored), tradability flags, exchange calendar, halt/ST/limit markers, announcement time, realization lag. Without these the contamination→alpha bridge is dead. |
| **NLP** | Literature-backed corpus-frequency fields: `duplicate_cluster_id`, `duplicate_cluster_size`, `first_seen_time`, `canonical_doc_id`. Without these, Min-K% / MIA / Oren-PaCoST ordering tests cannot run on the substrate. |
| **Stats** | Point-in-time realized-outcome function `O_i(H)`: target mapping (company/sector/index rules), horizon (H=5d primary; store 1/5/22), benchmark adjustment (CSI 300 primary), volatility-scaled neutral band (~0.5× trailing 20-day σ). |
| **Editor** | A **legally public 50–80 case pilot slice** to unblock CLS licensing risk before investing in large-scale annotation. |

These are not in conflict — they are **additive**. The MVP schema must contain all four families. The convergent ask is that the schema document be written first, then the collection pipeline.

---

## C3 — Factor taxonomy is now doing ALL the novelty work; vague factors will not carry it

- **NLP** (strongest position): The vague factor wishlist from the R1 draft (importance / complexity / memorability / relevance / market impact / hotness) will NOT survive reviewers. Only literature-backed factors survive: duplicate-cluster size, entity head-tail distribution, template rigidity, surprisal, temporal distance to cutoff, anchor uniqueness decomposed into (locator / event-family density / entity salience).
- **Quant**: Pick **4–6 primary factor axes** max. Refuse to let the shallow panel dictate the schema.
- **Stats**: Lock only factors that are (a) computable from raw fields, (b) pre-declared for a specific contrast. Other bins can be recomputed later.
- **Editor**: The factor list must be pre-committed for reviewer credibility; expanding it later invites "post-hoc fishing" rejection.

**Convergent ask:** Pre-commit 4–6 factors, each with a literature citation and a concrete computation rule on CLS rows. Draft the list before spec-freeze in R3. NLP's decomposition of "anchor strength" into three distinct constructs (locator / event-family density / entity salience) is the strongest proposal and should be adopted.

---

## C4 — Scale has tighter answers now (but agents don't fully agree)

| Agent | Scale recommendation |
|---|---|
| **Quant** | Barbell: 600–800 deeply audited company core + 3–5K shallow panel. 150–200 cases-per-cell floor on pre-declared comparisons, 4–6 primary factor axes. |
| **Stats** | ~1,500 verified cases (floor 1,200), sampled at the **event-cluster level**. Derivation: Phase-4 OR=1.95 (p1=0.123 vs p0=0.068) → 852 scorable × design effect 1.5 (m=3, ρ=0.25) → 1,278 + 15–20% verification loss. Split: 800 stratified core + 700 random panel. |
| **Editor** | Start with 50–80 public pilot slice. Full MVP "smaller than 2000"; no hard number. Gate on reviewer-compatible public-release sourcing, not on scale. |
| **NLP** | No explicit number; emphasizes that the schema is more important than the count. |

**Convergent-ish read:** somewhere between 800–1500 curated core + 3–5K shallow panel is the working range. **Sampling at the event-cluster level (Stats) is the single most important design decision** because factor correlations mean per-article sampling produces massive hidden duplication. Without cluster-level sampling, the effective sample is much smaller than the nominal N.

---

## C5 — Deadline is May 25 ARR, Findings track, barely achievable

- **Editor**: Realistic target is EMNLP 2026 **Findings** via ARR May 25 — still barely live; 6-week calendar burns mostly on annotation adjudication + outcome verification, NOT detector code. NeurIPS E&D (May 4–6) is OUT. No June/July ARR — next cycle is August 3.
- **Quant / NLP / Stats**: Don't weigh in on deadline explicitly, but all their schema asks imply 2–3 weeks of spec work before any collection runs.

**Convergent practical ask:** **Freeze the schema and annotation protocol by ~April 20** or commit now to August 3. The R3 session should be the spec-freeze session.

---

## C6 — Plan B if partition analysis returns null

Only **Editor** explicitly raises this, but it's important:
- If no factor produces a clear memorization difference across detectors, the paper must reposition as _"current memorization detectors fail to separate economically-consequential factor strata even on a controlled substrate."_
- This is publishable ONLY with: (a) explicit power / sensitivity argument, (b) detector-agreement analysis, (c) manual failure-case studies.
- Without a positive partition finding AND without a rigorous detector-failure story, it collapses to a dataset project (not a conference paper).

**Convergent ask:** Before running the partition analysis, pre-commit to what "null" looks like and what the Plan B paper would be. Don't discover the null at writing time.

---

## C7 — CLS licensing is still fatal at MVP stage

- **Editor** (unchanged from R1): CLS metadata-only release has no strong EMNLP/ACL D&B track precedent. Reviewers will say "not actually usable."
- Recommended unblock: build a **legally public core slice** (50–80 cases) from public-domain sources first, use it as the pilot/gold set, and use CLS only for the larger panel.
- No other agent addresses licensing directly, but none of them defend the current metadata-only plan.

**Convergent ask:** Decide by R3 whether to (a) get a CLS licensing answer, (b) build a public core and use CLS as panel only, or (c) switch to a fully public corpus.

---

## Divergent points

### D1 — Framing: substrate for detectors vs factor-taxonomy-as-contribution
- **Editor / Quant**: Substrate is the product. Detectors running on it is the evaluation.
- **NLP**: The factor taxonomy IS the contribution; detectors are the instrument that validates the taxonomy matters.
- **Stats**: Agnostic — whichever framing is more honest, but substrate framing is less likely to overclaim.

This affects how the intro is written and which section gets the most space. Not MVP-blocking but must be decided before paper-plan.

### D2 — Barbell vs event-cluster sampling
- **Quant** wants two physical tiers (deep core + shallow panel) collected separately.
- **Stats** wants one event-cluster-sampled pool with a stratified-core / random-panel split, treating it as a single sampling design.
- Both agree on the ~800+700 split size; they disagree on whether it's one pool or two.

Not blocking — resolvable by R3 spec work.

### D3 — How much to pre-commit for "partition analysis"
- **Stats**: Pre-register the factor × detector interaction contrasts up front to avoid multiple-testing explosion.
- **NLP**: Pre-commit the factor list but leave detector choice flexible.
- **Editor**: Whatever pre-registration looks good enough to reviewers.
- **Quant**: Pre-commit factor axes but not bin edges (recomputable later).

Resolvable in R3.

---

## Points none of the agents raised but worth flagging

1. **Phase 4 / Phase 5 pilot data disposition**. The R1 reviews treated Phase 4 DeepSeek + Phase 5 Qwen as pilot evidence. Does the MVP corpus re-use any Phase 4-5 cases, or is it a clean rebuild? This affects the pilot→benchmark narrative in the paper.
2. **Thales downstream integration**. Memory C1 (`thales_connection.md`) says alpha validation is the real goal. No R2 agent explicitly tied the MVP back to the Thales production pipeline. If alpha contamination is the endgame, the MVP schema should include whatever fields Thales needs to ingest — that's cheaper to build in than retrofit.
3. **White-box Qwen access**. DeepSeek logprobs are broken; Qwen white-box via vLLM works. The MVP "run existing detection methods" plan depends on Min-K% / MIA needing logprobs — which means Qwen is the only model the detector-comparison part can actually run on at full fidelity for the MVP. This should be made explicit.

---

## Decisions the user must make before R3 spec session

1. **Scale commitment**: ~800 curated core + ~700 panel (Stats) OR 600–800 deep + 3–5K shallow (Quant). Pick one shape.
2. **Factor list**: commit 4–6 factors drawn from the literature-backed list (NLP's proposal is the strongest starting point).
3. **Outcome-label function `O_i(H)`**: pin down horizon, benchmark adjustment, neutral band.
4. **Sampling unit**: event cluster (Stats) vs article — MUST be event cluster.
5. **CLS licensing posture**: get-answer / public-core-only / switch-corpus. Blocks Editor sign-off.
6. **Public pilot slice (50–80 cases)**: commit to building it first so the rest of MVP can proceed against a reviewer-credible baseline.
7. **Deadline**: May 25 ARR (Findings) or August 3 ARR. All schema work below assumes May 25 means freeze by April 20.
8. **Framing**: "audit substrate" (Quant/Editor) vs "factor-taxonomy-driven benchmark" (NLP). Decides paper structure.
9. **Plan-B claim**: pre-commit what the paper says if partition analysis nulls.
10. **Thales integration requirement**: does MVP schema include fields Thales needs, or is that deferred?

---

## Orchestrator note

**R2 is CONVERGED on go/no-go.** All 4 agents green-light the MVP pivot.

The remaining work is a **schema-freeze session (R3)** that merges the 4 must-commit-now lists into one MVP spec. Because the 4 asks are additive and not in conflict, this is tractable in one working session.

Per agent-roles protocol, **ML Engineer gate** should run BEFORE R3 spec work, specifically on: (a) the event-cluster sampling + annotation budget, (b) the point-in-time outcome pipeline (Stats/Quant intersection), (c) whether ~1500 curated cases is feasible within 2-3 weeks of annotation work given Phase 4-5 pilot throughput.

**Thread continuity note:** The 4 sub-agents could not resume their original R1 Codex threads — R1 thread `019d5d61-...` and siblings had expired by R2 time. Each R2 ran as a fresh Codex session with R1 review pasted inline, preserving persona and context. New R2 thread IDs are recorded in the individual review file headers; save those if R3 needs thread continuity.
