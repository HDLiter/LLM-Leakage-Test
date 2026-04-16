# BENCHMARK R4 Step 1 — Factor Brainstorm Synthesis

**Date:** 2026-04-13
**Orchestrator:** Claude Code
**Round:** R4 Step 1 (4 Codex agents, parallel, independent brainstorm, no cross-visibility)
**Total factors proposed:** 30 (8 Quant + 7 NLP + 9 Stats + 6 Editor)
**Source files:**
- [BENCHMARK_R4A_QUANT.md](BENCHMARK_R4A_QUANT.md)
- [BENCHMARK_R4A_NLP.md](BENCHMARK_R4A_NLP.md)
- [BENCHMARK_R4A_STATS.md](BENCHMARK_R4A_STATS.md)
- [BENCHMARK_R4A_EDITOR.md](BENCHMARK_R4A_EDITOR.md)

---

## Convergence map

| Theme | Quant | NLP | Stats | Editor | Convergence |
|---|---|---|---|---|---|
| **Cluster size / propagation** | Corpus Repetition Load | Duplicate Cluster Size | Duplication/propagation intensity | Propagation Intensity (core) | **4/4 🔥** |
| **Cutoff distance / temporal** | — (implicit) | Cutoff Proximity | Pre/post cutoff + pre-cutoff age | Model-Cutoff Exposure Margin (core) | **3/4** |
| **Anchor / locator specificity** | Lexical Anchor Density | Locator Specificity | — | Anchor Strength (core) | **3/4** |
| **Entity / target identity** | Primary-Entity Tradability Tier [alpha-bridge] | Entity Salience / Head-Tail | Target scope/instrument | Target Scope (secondary) | **4/4** (different angles) |
| **Event type / family** | Structured Event Type | — | Event family | Disclosure Regime | **3/4** |
| **Text form / length** | — | Template Rigidity + Exact-Span Rarity | Text length (control) | — | **2/4** |
| **Event phase / timing** | Event Phase + Session Timing | — | — | Disclosure Regime (partial) | **1-2/4** |
| **Surprise / outcome magnitude** | Standardized Surprise Magnitude | — | — | — | **1/4** |
| **Realization lag** | Outcome Materialization Lag | — | — | — | **1/4** |
| **Cluster temporal span** | — | Cluster Temporal Span / Repost Persistence | — | — | **1/4** |
| **Outcome horizon** | — | — | — | Outcome Horizon (secondary) | **1/4** |
| **Label quality / reprint status** | — | — | Reprint status + Label quality | — | **1/4** |

---

## The strongest convergent factors (≥3 agents)

### F1 — Propagation intensity / duplicate cluster size (4/4 🔥)

**Description**: Size of the event cluster the case belongs to. How many articles in CLS reported the same event? Proxy for how many "copies" a pretraining model may have seen.

**Agent framings:**
- **Quant (Corpus Repetition Load)**: "echo density" — how many times the event was written up in CLS, with entity aliases. Frames as a fundamental memorization lever.
- **NLP (Duplicate Cluster Size)**: directly from Kandpal/Carlini/Lee frequency-recall literature. "Memorization ∝ log(frequency)".
- **Stats (Duplication/propagation intensity)**: binary (singleton vs duplicated) as confirmatory primary; tercile as exploratory. Notes this is his single strongest candidate for confirmatory power.
- **Editor (Propagation Intensity, core)**: "the most distinctive finance-native factor" in the Editor's central-claim construction. Frames as differentiator from generic memorization benchmarks.

**Operationalization convergence**: All 4 agree it's `duplicate_cluster_size` from the clustering pipeline.

**Stats' binary-primary constraint**: At MVP scale (~1200 scorable), only the binary (singleton vs ≥2) contrast is confirmatory-safe at 80% power. Tercile splits are underpowered.

**Status**: Universal agreement. **Almost-certain shortlist member**.

### F2 — Cutoff distance / temporal exposure (3/4)

**Description**: How far is the event from the model's training cutoff? Core variable for memorization opportunity.

**Agent framings:**
- **NLP (Cutoff Proximity)**: from Dated Data, Set the Clock, Chronologically Consistent LLMs. Continuous or binary.
- **Stats (pre/post cutoff + pre-cutoff age)**: pre/post as binary confirmatory primary; pre-cutoff age (within pre only) as exploratory continuous.
- **Editor (Model-Cutoff Exposure Margin, core)**: frames as the "exposure opportunity" axis in the central claim.

**Quant didn't list it as a standalone factor** but his Event Phase + Session Timing imply a time axis. Implicit 4/4.

**Stats' constraint**: Only the 2-bin pre/post is confirmatory-safe. Any finer temporal binning (pre-cutoff age in 3+ bins) is underpowered. And: for closed models like DeepSeek with uncertain cutoffs, the operational definition needs a defensible cutoff estimate.

**Status**: Strong convergence. **Very likely shortlist member**. Open question: 2-bin (pre/post) only, or also store continuous age for exploratory?

### F3 — Anchor strength / locator specificity (3/4)

**Description**: How identifiable is the event? Does the text contain specific locators (date + place + named entity triple) that uniquely pin the event in time and space?

**Agent framings:**
- **Quant (Lexical Anchor Density)**: counts of explicit lexical anchors per 100 tokens (dates, proper nouns, tickers, dollar amounts).
- **NLP (Locator Specificity)**: more theoretical — follows Huet 2025 / Gurnee & Tegmark on LLM spatial-temporal representations. Scoring specificity of (entity × time × place) triples.
- **Editor (Anchor Strength, core)**: one of 3 central-claim factors. Argues this is what makes an event "addressable" in the model's knowledge base.
- **Stats doesn't propose it** — not because he disagrees, but because his lens is power-first and anchor strength is harder to operationalize as a clean binary.

**Operationalization divergence**: Quant's density-count version is simpler but shallower; NLP's triple-specificity version is theoretically stronger but NLP explicitly flagged it as one of the hardest to operationalize on Chinese financial news (alias normalization, segmentation, unit suffix issues).

**Status**: Strong theoretical convergence, operationalization is hard. **Likely shortlist member, but operationalization needs R4 Step 2 discussion**.

### F4 — Entity / target identity (4/4, different angles)

**Description**: All 4 agents have an entity-related factor but from different angles:

- **Quant (Primary-Entity Tradability Tier)**: ADV20 percentile. This is the **alpha-bridge factor** — designed to support "memorization → alpha contamination" narrative downstream. Economic meaning.
- **NLP (Entity Salience / Head-Tail)**: Zipf-distribution position of the entity in CLS corpus. Linguistic meaning (frequency-recall lever).
- **Stats (Target scope)**: instrument type stratification (company / sector / index). Statistical meaning (stratifier for generalizability).
- **Editor (Target Scope, secondary)**: similar to Stats but explicitly subordinate to propagation / anchor / cutoff in the central claim.

**The 4 are not the same factor** — they're 4 different factors all derived from "who is the event about."

**Venue-drift tension**: Quant's tradability tier is designed for the alpha bridge. Editor explicitly flagged this class of factor as venue-drift risk (pushing toward finance venue rather than EMNLP). Quant and Editor are in **direct tension** here:
- **Quant's position**: without the alpha bridge, the benchmark has no downstream value
- **Editor's position**: with too much finance-microstructure, the paper lands at JFE / RFS, not EMNLP

**Status**: Requires explicit resolution in Step 2. Likely outcome: the MVP picks ONE of the four angles as primary and retains the rest as exploratory / descriptive.

### F5 — Event type / family (3/4)

**Description**: Categorical classification of the event (earnings / policy / M&A / product / litigation / rumor / industry etc.)

**Agent framings:**
- **Quant (Structured Event Type)**: fixed taxonomy, used for analysis by type
- **Stats (Event family)**: 3-level grouping, **descriptive only** — explicitly not powered for confirmatory
- **Editor (Disclosure Regime)**: treats mandatory-disclosure events (regulatory filings) differently from editorial events (news commentary)

**Stats' constraint**: Even 3-bin event family is underpowered for confirmatory inference at MVP scale. Should be descriptive only.

**Status**: Likely **descriptive only** (not confirmatory). Worth including for paper narrative but not for primary effect claims.

---

## Single-agent factors (worth considering)

### Quant-unique

- **Event Phase (Rumor vs Official vs Clarification/Recap)**: novel and economically rich. Quant argues rumors get memorized differently than confirmed announcements. No other agent proposed this.
- **Session Timing / Attention Window**: pre-open / intraday / post-close. Economically meaningful but tightly correlated with event phase, and operationalization depends on deferred point-in-time fields.
- **Standardized Surprise Magnitude**: |AR| scaled by trailing σ. Pure economic signal; depends on outcome function (deferred).
- **Outcome Materialization Lag**: time from event to measurable outcome. Depends on deferred outcome function.

**Why only Quant has these**: they're all event-microstructure factors that require production-quant intuition. NLP / Stats / Editor don't have this lens.

**Tension**: Surprise Magnitude, Materialization Lag, Session Timing all depend on Decision 2+4 which are deferred. They can't be fully operationalized until the point-in-time track resolves. So they're **on hold** for now.

### NLP-unique

- **Template Rigidity / Boilerplate Similarity**: how formulaic is the article? High template rigidity → high expected memorization (Zhang/Lee/Kandpal). Surface-form-sensitive.
- **Exact-Span Rarity / Lexical Idiosyncrasy**: NLP's most surface-form-sensitive proposal. Directly supports Min-K% / MIA / extraction-style detectors. NLP flags this as one of the hardest to operationalize on Chinese financial news.
- **Cluster Temporal Span / Repost Persistence**: how long does the event's cluster span in time? Short-span = burst, long-span = sustained coverage. Novel framing, motivated by Dated Data.

**Why only NLP has these**: these are NLP-memorization-specific; they map onto specific detector families. Other agents don't know the detector literature as well.

### Stats-unique

- **Text length (mandatory control)**: not a treatment, but a necessary covariate to avoid length-confound. Should be a control variable in every analysis.
- **Outcome label quality (descriptive only)**: from Decision 4's `label_quality`. Descriptive only.
- **Reprint status (conditional confirmatory)**: maps to Decision 5's `is_reprint` flag. Stats proposes it could become a confirmatory treatment IF prevalence is ≥25%.
- **Temporal × propagation interaction (exploratory)**: pre-cutoff singleton vs pre-cutoff duplicated vs post-cutoff singleton vs post-cutoff duplicated. Clean 2×2, but at MVP scale each cell has ~300 cases, which is underpowered.

**Why only Stats has these**: pure identification / power-first framing. Other agents don't prioritize covariate controls.

### Editor-unique

- **Outcome Horizon (secondary, venue-drift risk)**: 1d / 5d / 22d as a factor. Editor flagged this himself as a venue-drift risk, noting it should only enter as a subordinate audit axis, not primary.

---

## Divergences that need Step 2 resolution

### D1 — Alpha bridge vs venue drift (Quant vs Editor)

**The tension**: Quant's Primary-Entity Tradability Tier is the single factor most aligned with the project's downstream Thales integration. Editor's central-claim framing explicitly subordinates it and flags it as venue-drift risk.

**Possible resolutions:**
- **Option A**: Keep tradability tier as **secondary factor** (descriptive), not part of the central claim. Mention Thales integration only in Discussion.
- **Option B**: Split the paper: primary venue = EMNLP with the NLP-flavored factors; secondary deliverable = Thales integration track that uses the tradability tier.
- **Option C**: Drop tradability tier from MVP entirely, defer to a future finance-venue paper.

**Stakeholder reality**: user has repeatedly stated the project's real goal is Thales alpha validation (memory: `thales_connection.md`). Option C is probably unacceptable to the user; Option B is clean but requires committing two tracks; Option A is the middle path.

**Must be decided in Step 2 before shortlist lock.**

### D2 — How many factors? Stats strict vs Editor coherent vs broader

**Stats' strict reading**: ONLY binary 2-level confirmatory factors are powered at 1200 scorable cases. His primary list is extremely narrow:
- pre/post cutoff (binary)
- singleton vs duplicated cluster (binary)
- target scope (stratifier, not treatment)
- text length (control)

That's **2 confirmatory treatments** and 2 controls. Everything else is exploratory or descriptive.

**Editor's coherence reading**: 3 core factors support the central claim (cutoff × anchor × propagation), with 3 secondary. His central one-sentence claim was:
> "On dated financial event clusters with verified outcomes, memorization audits become meaningfully interpretable when stratified by exposure opportunity, event identifiability, and news propagation breadth."

**NLP's 5-factor MVP core**: dup_size + cutoff_proximity + template_rigidity + locator_specificity + entity_salience. Wider than Stats, narrower than Quant.

**Quant's 6-8 factor implicit list**: broadest, most economically rich.

**The tension**: Stats' power constraint is real (the OR=1.95 baseline effect × 1200 scorable × α=0.05 × 80% power math actually works out to ~850 per binary contrast). But if only 2 factors are confirmatory, the paper story is very thin.

**Possible resolutions:**
- **Option A**: Accept Stats' strict primary = 2 confirmatory + 3-4 exploratory + event family descriptive. Paper has 2 headline findings plus exploratory breadth.
- **Option B**: Increase MVP scale from 1200 to 1600-2000 scorable to power a 3rd confirmatory factor. Changes Decision 3's target N.
- **Option C**: Accept lower power (60-70%) on a 3rd confirmatory factor and pre-register it as "powered for OR=2.2 effect only."

**Must be decided in Step 2.**

### D3 — Anchor strength: operationalization path

- **Quant**: counts-based density
- **NLP**: triple-specificity scoring (harder, more theoretically motivated)
- **Editor**: agnostic, lets the operationalizer decide

Plus NLP itself flagged this as hardest to operationalize on Chinese financial news.

**Must be decided in Step 2 before shortlist lock.**

### D4 — Event phase (rumor/official/clarification)

Only Quant proposed this. It's novel, economically meaningful, but operationally expensive (requires classifying articles beyond basic event clustering). Is it:
- (a) worth adding as a primary factor (Quant's position)
- (b) folded into event family as a sub-classification
- (c) deferred to a future extension

**Step 2 question for the other 3 agents**: is this worth adopting?

---

## Cross-factor correlation / merge concerns

**Quant-flagged correlations** (strongest):
- Tradability tier × Corpus repetition load × Lexical anchor density form a **positive-correlation bloc** (liquid names get more coverage and more specific text). These three may need to be analyzed as an index, not independent factors.
- Event phase ↔ Session timing (rumors cluster intraday, officials cluster post-close/pre-open)

**NLP-flagged correlations**:
- Template rigidity ↔ Exact-span rarity (formulaic articles have low span rarity)
- Entity salience ↔ Duplicate cluster size (major entities get more coverage)
- Entity salience ↔ Locator specificity (major entities are more uniquely anchored)

**Stats-flagged**:
- Target scope × cluster size (companies are higher-coverage than sectors are higher-coverage than indices)
- Pre/post cutoff × cluster size (newer events have more coverage in a fixed corpus window)

**Net observation**: There is a near-universal correlation bloc around "major well-covered entities" — these attract more CLS articles, more specific lexical anchors, more established template usage, higher cluster sizes, and tend to be tradable large-caps. This means **any single factor in this bloc risks being a proxy for all the others**. Analysis design must explicitly test and control for this.

---

## Pre-shortlist candidate set (for Challenger + Step 2)

Based on convergence + Stats power realism + Editor coherence, the **likely shortlist candidates** are:

| # | Factor | Convergence | Primary/Expl | Notes |
|---|---|---|---|---|
| 1 | **Duplicate cluster size** | 4/4 | **Primary** (binary: singleton vs ≥2) | Universally agreed. Power-safe. |
| 2 | **Pre/post cutoff** | 3/4 + implicit 4/4 | **Primary** (binary) | Strong consensus. Open: how to define cutoff for closed models. |
| 3 | **Anchor strength / locator specificity** | 3/4 | **Primary or secondary** | Operationalization TBD. Choose Quant counts-based (simpler) or NLP triple-specificity (stronger). |
| 4 | **Entity / target identity (one of 4 angles)** | 4/4 | **Secondary** | D1 tension must be resolved. Most likely: Zipf head-tail (NLP) as primary text-linguistic factor; tradability tier deferred or demoted. |
| 5 | **Event type / family** | 3/4 | **Descriptive** | Not powered for confirmatory. Keep for narrative. |
| 6 | **Text length** | 1/4 | **Control** | Mandatory covariate per Stats. |

**Candidates on the fence** (need Challenger + Step 2 to resolve):
- Template rigidity (NLP only, surface-form-sensitive, useful for detector-targeting)
- Event phase (Quant only, novel, operationally expensive)
- Reprint status (Stats, conditional on prevalence)
- Temporal × propagation interaction (Stats, underpowered but analytically clean)

**Likely drops** (single-agent with significant cost):
- Cluster temporal span / Repost persistence (NLP only, novel but unvalidated)
- Outcome Horizon (Editor's own venue-drift flag)
- Session timing, surprise magnitude, materialization lag (all Quant, all depend on deferred outcome track)
- Exact-span rarity (NLP only, hardest to operationalize on Chinese)

---

## Open questions for Challenger (Step 2, cross-model)

The Claude cross-model Challenger should specifically look for:

1. **Blind spot check**: Is there a factor that no Codex agent proposed but a different model family might see? Particularly check Chinese-NLP-specific factors the Codex agents may have under-weighted (e.g., traditional/simplified variation, regional dialect, regulator language).
2. **Groupthink on the correlation bloc**: All 4 agents acknowledge the "major-entity" correlation bloc (tradability × cluster size × anchor density × entity salience). Do they collectively under-estimate how severely this collapses factor independence? Is there a way to CONSTRUCT a factor that IS independent of the bloc (e.g., "tail-entity cluster size" specifically)?
3. **Venue drift**: Is the alpha-bridge vs EMNLP tension as binary as Quant and Editor portray, or is there a factor that serves both?
4. **Null-result Plan B check**: For each of the 6 pre-shortlist candidates, is there a Plan B narrative if the factor shows no effect? (Editor did this for his 6 but not for the cross-agent set.)
5. **Cross-model bias**: Are the Codex agents collectively biased toward factor proposals that exist in their training-data literature? What factor would a non-Codex reasoner independently surface?
6. **Operationalization on Chinese financial news**: NLP flagged several factors as hard to operationalize. Are there Chinese-NLP operational challenges the other agents missed (e.g., what does "entity" mean when 中信证券 and 中信 both appear)?

---

## What Step 2 will produce

After Challenger pass:
1. Each of the 4 Codex agents (via `codex-reply` on new threads, since R4A threads are fresh) receives the synthesis + Challenger findings
2. Each agent **rates** the 10-12 candidate factors on: power feasibility, narrative fit, operationalizability, novelty
3. Each agent submits a **top-5 vote**
4. Orchestrator aggregates votes → final shortlist of 4-6 factors
5. Shortlist goes to R5 detector investigation

Step 2 does NOT re-brainstorm new factors. It consolidates.
