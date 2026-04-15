# BENCHMARK R4 Step 1 — Editor Factor Brainstorm
**Date:** 2026-04-13
**Reviewer:** Codex (senior EMNLP area chair)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md v2
**Prior rounds:** BENCHMARK_R1/R2/R3_EDITOR.md

---

**MVP Shortlist**

### Factor: Model-Cutoff Exposure Margin
**Concept**: Whether an event cluster first became public before or after a model-specific cutoff is the cleanest exposure-opportunity variable in the paper.
**Narrative role (what story does this factor tell in a paper?)**: This is the substrate spine. It turns "contamination" from vague suspicion into a dated, auditable partition. Without it, the paper is just another finance benchmark; with it, FinMem-Bench becomes a temporal audit resource.
**Precedent from existing benchmarks**: [LiveBench](https://arxiv.org/abs/2406.19314), [AntiLeakBench](https://aclanthology.org/2025.acl-long.901/), and [MMLU-CF](https://aclanthology.org/2025.acl-long.656/) all fight contamination via freshness or held-out construction; [Time Travel in LLMs](https://arxiv.org/abs/2308.08493) detects contamination after the fact. FinMem-Bench is differentiated because it does this on dated financial event clusters with verified market outcomes.
**Reviewer credibility**: Very high. The only predictable objection is cutoff uncertainty; answer that by making Qwen primary and any fuzzy-cutoff model secondary.
**Operationalization**: `delta_cutoff_m = cutoff_date_m - first_seen_time.date()`. Primary binary split: `pre_cutoff = delta_cutoff_m >= 0`, `post_cutoff = delta_cutoff_m < 0`. Optional descriptive split inside pre-cutoff only.
**Predicted effect direction**: Pre-cutoff cases should show stronger memorization-risk signals than post-cutoff.
**Plan-B story under null**: Publishable as "current detectors do not track the most obvious temporal exposure boundary even on a controlled financial substrate."
**Framing support**: Both.
**Venue fit**: Strong EMNLP fit.

### Factor: Anchor Strength
**Concept**: How uniquely the CLS text identifies one real-world financial event from its own tokens.
**Narrative role**: This is the linguistic meaning axis. It lets you argue that memorization should differ between pinpointable disclosures and generic market blur, which is a coherent NLP claim rather than a finance-only claim.
**Precedent from existing benchmarks**: [Reasoning or Reciting?](https://arxiv.org/abs/2307.02477), [Rethinking Benchmark and Contamination with Rephrased Samples](https://arxiv.org/abs/2311.04850), and [LastingBench](https://aclanthology.org/2025.findings-emnlp.993/) all imply that benchmark behavior depends on how much items admit surface or default shortcuts, but none gives a finance-specific identifiability rubric on short wire text. That is your extension.
**Reviewer credibility**: High if the rubric is frozen, mechanical, and human-audited. Low if it drifts into "memorability" language.
**Operationalization**: Use the existing 0-3 rubric on CLS exact text only; MVP binary collapse `strong = {2,3}`, `weak = {0,1}`.
**Predicted effect direction**: Strongly anchored items should show larger pre/post separation or more stable detector separation.
**Plan-B story under null**: Even when identifiability varies sharply, detectors fail to separate strata; that is a useful negative result about detector sensitivity, not a failed benchmark.
**Framing support**: Both.
**Venue fit**: Excellent EMNLP fit.

### Factor: Propagation Intensity
**Concept**: Near-duplicate cluster size is an exposure-multiplicity proxy: how many times essentially the same financial event propagated through the wire.
**Narrative role**: This is the most distinctive finance-native factor. It upgrades vague "frequency" into a concrete, auditable training-exposure story tied to how financial news actually spreads.
**Precedent from existing benchmarks**: [Time Travel in LLMs](https://arxiv.org/abs/2308.08493) and [Proving Test Set Contamination in Black-Box LMs](https://arxiv.org/abs/2310.17623) study contamination detection, not event-level propagation. [AntiLeakBench](https://aclanthology.org/2025.acl-long.901/) and [LiveBench](https://arxiv.org/abs/2406.19314) try to avoid contamination rather than stratify by exposure multiplicity. FinMem-Bench is differentiated here.
**Reviewer credibility**: High if you are explicit that this is an exposure-opportunity proxy, not a pure causal measure of memorization.
**Operationalization**: Primary binary split on cluster metadata: `singleton = 1[duplicate_cluster_size = 1]`, `duplicated = 1[duplicate_cluster_size >= 2]`. Keep finer bins descriptive only.
**Predicted effect direction**: Duplicated clusters should exhibit higher memorization-risk scores than singletons.
**Plan-B story under null**: Repeated public availability of the same event does not translate into detector-visible contamination once time is controlled. That is still informative.
**Framing support**: Both.
**Venue fit**: Strong; this is one of the safest "novel" factors.

### Factor: Disclosure Regime
**Concept**: Distinguish formal public disclosures from commentary, roundup, or secondary reportage.
**Narrative role**: This is the financially distinctive institutional factor. It says not all finance text is alike: official disclosures are standardized, often copied, and economically consequential in a way commentary is not. That gives the paper a domain-specific spine without drifting into market microstructure.
**Precedent from existing benchmarks**: [CFinBench](https://aclanthology.org/2025.naacl-long.40/) and [InvestorBench](https://aclanthology.org/2025.acl-long.126/) are finance benchmarks, but not contamination-audit substrates. Generic contamination benchmarks such as [AntiLeakBench](https://aclanthology.org/2025.acl-long.901/) and [MMLU-CF](https://aclanthology.org/2025.acl-long.656/) do not have a disclosure-regime dimension. This factor is therefore differentiated, not derivative.
**Reviewer credibility**: Medium-high. The obvious objection is overlap with anchor strength; pre-empt that by defining it institutionally, not rhetorically.
**Operationalization**: Rule-based binary from CLS tokens: `formal_disclosure = 1` if text contains official-release cues (`公告`, `披露`, `核准`, `批复`, `收到...通知`, regulator/exchange names, titled documents `《...》`) and describes a discrete release; else `commentary_or_secondary`.
**Predicted effect direction**: Formal disclosures should show stronger exposure-related memorization patterns than commentary.
**Plan-B story under null**: Detector behavior does not distinguish formal public filings from secondary commentary even on a dated substrate.
**Framing support**: Both.
**Venue fit**: Good for EMNLP if kept textual-institutional.

### Factor: Target Scope
**Concept**: Whether the case targets a single company versus a broader basket, sector, or index.
**Narrative role**: This is partly a substantive factor and partly a guardrail against bad pooling. It tells reviewers you understand that company, sector, and index cases are not one homogeneous benchmark population.
**Precedent from existing benchmarks**: [InvestorBench](https://aclanthology.org/2025.acl-long.126/) spans multiple financial products, and [CFinBench](https://aclanthology.org/2025.naacl-long.40/) spans many financial tasks; neither uses target scope as a contamination stratum. FinMem-Bench can defend it as an audit variable rather than a broad finance taxonomy.
**Reviewer credibility**: High as a control/secondary factor; only medium as a headline novelty factor.
**Operationalization**: Primary binary collapse: `company = 1[target_type == "company"]`, `non_company = sector|index|macro-like cases`. Keep finer classes descriptive only.
**Predicted effect direction**: Single-company cases should show sharper memorization-related contrasts because entity mapping is cleaner and less diffuse.
**Plan-B story under null**: The observed detector behavior is not just a company-specific artifact; that still strengthens the benchmark story.
**Framing support**: Both.
**Venue fit**: Safe if used as disciplined stratification, not as a finance-product taxonomy.

### Factor: Outcome Horizon
**Concept**: Compare the same benchmark cases across one primary short horizon and one longer secondary horizon.
**Narrative role**: This is the factor that makes the benchmark more than "dated news." Verified outcomes let you ask whether memorization audits behave differently when labels are economically tighter versus noisier. That is genuinely distinctive.
**Precedent from existing benchmarks**: [LiveBench](https://arxiv.org/abs/2406.19314) emphasizes objective ground truth, but not market outcomes; finance benchmarks such as [CFinBench](https://aclanthology.org/2025.naacl-long.40/) and [InvestorBench](https://aclanthology.org/2025.acl-long.126/) are capability-oriented, not temporally audited with realized outcome horizons.
**Reviewer credibility**: High if one primary horizon is pre-registered and the others are clearly robustness analyses.
**Operationalization**: Store outcomes for multiple horizons but designate one primary horizon. Factor analyses are repeated per `outcome.horizon`; no bespoke field names needed.
**Predicted effect direction**: Shorter horizons should show cleaner and larger separations; longer horizons should attenuate.
**Plan-B story under null**: Even moving from economically tight to looser labels does not sharpen detector differences. That is a coherent negative result.
**Framing support**: Both, though especially substrate.
**Venue fit**: Mild finance-drift risk; keep subordinate to the NLP audit claim.

**Strategic ordering**

Central claim factors: `cutoff exposure`, `anchor strength`, `propagation intensity`. These three jointly support the cleanest one-sentence paper claim and are the least vulnerable to "yet another dataset" pushback.

Secondary validations: `disclosure regime`, `target scope`, `outcome horizon`. They show the benchmark is not only temporally dated, but also institutionally and economically structured.

Surprising but safe novel contributions: `propagation intensity` first, `disclosure regime` second. Both are finance-native, operationalizable, and not already owned by existing contamination benchmarks.

**Appendix keep-list**

- `cutoff exposure margin` — core.
- `anchor strength` — core.
- `propagation intensity` — core.
- `disclosure regime` — core/secondary.
- `target scope` — secondary.
- `outcome horizon` — secondary.
- `label_quality` — keep as robustness factor, not headline factor.
- `event family` (`firm-specific` vs `sector/policy`) — descriptive reserve only.
- `multi-entity entanglement` (`|key_entities|`) — reserve; plausible alternative to target scope.
- `historical template recurrence` (same target + same event template in prior window) — reserve only if rule can be frozen mechanically.
- `numeric specificity` (presence/density of exact figures) — reserve; likely merged into anchor.
- `official document-title presence` — reserve; probably a subfeature of disclosure regime.
- `reprint status` — reserve only if measurement/release text split stays explicit.
- `timestamp/session bucket` — reserve; useful, but dangerous for venue drift.
- `outcome magnitude` — reserve; coherent, but finance-heavy.
- `text length` — control only, not a paper factor.

**Reject list**

- `source credibility`: too vague, too close to institutional prior, and easily collapses into disclosure regime plus outlet effects.
- `generic corpus frequency / hotness`: rejected unless decomposed into a concrete mechanism such as propagation intensity or template recurrence.
- `importance / salience / memorability`: Decision 10 violation.
- `complexity / readability`: generic benchmark filler, not a contamination story.
- `sentiment polarity`: not a memorization factor; it is too close to the downstream label.
- `source outlet identity`: unstable, rights-specific, and hard to generalize beyond CLS.
- `cross-lingual / language`: already cut in R1; do not reopen it through the back door.
- `detector-derived quantities` such as Min-K or MIA scores: R5 territory, not factor design.
- `fine-grained sector or market-cap bins`: too finance-venue-coded for MVP and too cell-thin.
- `up/down direction` as a headline factor: keep as a balance/control axis, not a novelty claim.

**Narrative coherence check**

FinMem-Bench can make one clean claim: *On dated financial event clusters with verified outcomes, memorization audits become meaningfully interpretable when stratified by exposure opportunity, event identifiability, and news propagation breadth, with secondary checks across disclosure regime, target scope, and outcome horizon.*

**Reviewer objection prediction**

`Cutoff exposure margin`: Objection: "Your cutoff is approximate, so pre/post is noisy." Pre-empt by making Qwen the primary confirmatory model, fixing one cutoff date ex ante, and either buffering or excluding a narrow gray band around the cutoff in sensitivity analysis.

`Anchor strength`: Objection: "This is just length or event type in disguise." Pre-empt by using the frozen rubric on CLS text only, auditing it with humans, and reporting its correlation with length and coarse event family rather than pretending independence.

`Propagation intensity`: Objection: "Cluster size is just importance/popularity." Pre-empt by calling it exactly what it is: an exposure-opportunity proxy. Do not sell it as pure causal mechanism; adjust for time and disclosure regime and move on.

**Venue drift check**

The safe EMNLP factors are `cutoff exposure`, `anchor strength`, `propagation intensity`, and `disclosure regime`. `Outcome horizon` is acceptable only as a subordinate audit axis. `Outcome magnitude`, `timestamp/session bucket`, `market-cap/liquidity`, and anything resembling event-study microstructure belong closer to a finance venue and should stay out of the MVP headline.
