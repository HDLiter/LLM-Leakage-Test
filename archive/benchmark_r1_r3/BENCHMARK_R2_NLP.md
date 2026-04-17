# BENCHMARK MVP R2 Check — NLP Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher, continuing R1 thread)
**Reasoning effort:** xhigh
**R1 reference:** BENCHMARK_R1_NLP.md

---

**1. Novelty survival.**

Against [FinBERT](https://www.ijcai.org/proceedings/2020/622), [BBT-Fin](https://arxiv.org/abs/2302.09432), [CFinBench](https://aclanthology.org/2025.naacl-long.40/), and [InvestorBench](https://aclanthology.org/2025.acl-long.126/), the MVP is no longer competing on task breadth, financial knowledge QA, or agentic decision-making. That is correct. Those papers already occupy the “Chinese finance benchmark” space. Your survivable contribution is narrower: a Chinese financial news event substrate explicitly built for memorization, contamination, and temporal-leakage auditing.

The minimum defensible novelty claim is not “a new Chinese financial benchmark.” It is: a large-scale, event-level, Chinese financial news resource with verified realized outcomes and factor annotations designed to test whether memorization behavior varies across exposure-relevant partitions. If you cannot support that exact claim empirically, the MVP collapses into resource curation. For Findings, D&B, or workshop, novelty survives only if the factorization is both theory-backed and shown to matter for at least some existing detectors.

**2. Substrate framing.**

This matches the Editor’s “substrate for detectors” framing much better than the original proposal, but only if you make the dataset detector-ready rather than annotation-rich in the abstract. A substrate is not just rows plus labels; it is release design that preserves what downstream auditing methods actually need.

The must-have design choice is to treat each case as an event-linked document with provenance, sequence position, and reusable raw text. At minimum you need: exact article text, headline, publication timestamp, source identifier, URL/hash, duplicate-cluster membership, event identifier, normalized entity/ticker IDs, verified outcome with horizon, and factor values with annotation provenance. You also need deterministic temporal splits and a model-specific cutoff table, because “pre/post” is model-relative. If those fields are absent, the corpus may support qualitative analysis, but it is not truly substrate-shaped for Min-K%, extraction, or ordering-style contamination tests.

**3. Factor taxonomy as the novelty carrier.**

If probes are deferred, the factor taxonomy becomes the paper. The most defensible factors are the ones the memorization literature already cares about and that can be operationalized cleanly.

Keep these: duplicate-cluster size; source-family repost depth; entity popularity/head-tail frequency; event frequency within corpus; template rigidity/boilerplate score; lexical idiosyncrasy or surprisal; temporal distance to model cutoff; outcome horizon/lag; archival persistence; and anchor uniqueness, decomposed into named-entity specificity, ticker specificity, and claim-span uniqueness. These are all plausibly linked to exposure, recoverability, or extraction ease.

Also keep a strict source-genre factor if CLS mixes telegraph styles or vendor channels. “Telegraph” is not automatically homogeneous.

Drop or postpone vague factors like importance, complexity, difficulty, memorability, relevance, and market impact unless each is tied to an observable rule. “Hotness” should also be dropped unless defined exogenously, e.g. trailing mention count. A taxonomy full of intuitive but weakly operationalized labels will not carry the paper.

**4. CFLS confound inheritance.**

This MVP does not resolve the construct-validity problem; it creates a cleaner place to resolve it later. That is an improvement, but it is not a fix. The underlying reckoning remains: a substrate does not itself show that any later probe isolates memorization rather than grounded reasoning, conflict-following, or generic robustness.

What the MVP can do is make future validation cleaner by separating source-side exposure factors from probe design. If later SR, FO, intrusion, extraction, or Min-K% all move in parallel along the same partitions, that is meaningful. If only one family moves, that is also informative. But if you ship the MVP and then keep talking as though memorization has already been measured, you will repeat the same mistake in a different form. So yes, this pivot postpones the reckoning. It only becomes a principled postponement if the substrate is explicitly built to support later negative controls, positive controls, and matched comparisons.

**5. Multi-method compatibility.**

For genuine multi-method readiness, the release needs a shared core schema plus method-specific extras.

Shared core fields: `case_id`, `doc_id`, `event_id`, `source_name`, `source_family`, `publish_time_utc`, `headline`, `body_text_raw`, `body_text_normalized`, `url_or_hash`, `entity_ids`, `ticker_ids`, `duplicate_cluster_id`, `duplicate_cluster_size`, `canonical_doc_id`, `outcome_direction`, `outcome_return_pct`, `outcome_horizon`, `outcome_asset`, `outcome_source_url`, `factor_*`, `annotation_source`, `annotation_confidence`.

For Min-K%: exact raw text to score, normalization flags, language, token length, and optionally a canonical scoring span field so everyone evaluates the same passage.

For MIA: a proxy “pre/post” label is not enough. To claim MIA-ready, you need a known in/out setup for at least open-model experiments: `shadow_train_split`, `known_in_corpus`, `matched_out_corpus`, and corpus-construction rules.

For extraction: `unique_span_text`, `span_start`, `span_end`, `prefix_context`, `suffix_context`, and a uniqueness score within the corpus.

For Oren/PaCoST-style ordering tests: `first_seen_time`, `doc_rank_within_cluster`, `near_duplicate_doc_ids`, and matched counterpart IDs. Without ordering metadata and counterpart structure, do not claim support for those methods.

**6. Annotation pipeline.**

Because factor quality is now the deliverable, the validation protocol has to look like a real annotation paper, not an LLM-assisted convenience layer. Start with a written codebook for each factor, including decision rules, tie-breaking rules, and examples of failure cases. Then create a stratified gold subset of about 800 cases spanning years, source families, duplicate-cluster sizes, entity popularity bands, and outcome horizons.

Have two trained annotators independently label the full gold subset for every retained factor. Use Krippendorff’s alpha for categorical factors with a target of at least 0.80, and ICC or Spearman for ordinal/continuous factors with a target of at least 0.75. Anything below that gets coarsened or dropped.

After that, let the LLM scale annotation, but require factor-wise validation against the gold subset before rollout. I would want at least 0.85 macro-F1 on categorical factors or tight error bounds on continuous ones. Then audit either 10% per stratum or 1,500 case-factor judgments total, whichever is larger. This is the minimum bar for claiming the annotations are stable enough to support scientific partitioning.

**7. Publishable story at MVP-only stage.**

MVP-only is publishable only under a narrower story than the original one. The paper would be: a Chinese financial news substrate for auditing pretrained exposure effects, with verified outcomes, theory-backed factors, and baseline heterogeneity results from existing detectors. That can be a Findings paper if the release quality is high and the baseline analyses are genuinely diagnostic rather than ornamental.

It is weaker for NeurIPS D&B unless the detector baselines are extensive and the factor partitions produce clear, reproducible differences across several model families. For workshop venues, MVP-only is viable.

But if the project stops at corpus construction plus descriptive factor counts, that is not enough. You need at least one empirical section showing that the factorization matters for detector behavior. New SR/FO methodology is not required for publishability at the MVP stage. A strong substrate paper can stand alone. What is required is real evidence that the substrate exposes meaningful variation.

**8. Go/no-go.**

This is not a full answer to my R1 “rebuild, not revise” position, but it is the first version of an actual rebuild. The good news is that it stops defending weak primary probes and relocates the contribution to something more defensible. The bad news is that it does not, by itself, fix construct validity. It cuts scope and moves the validity burden downstream.

So my answer is conditional go. Go if you explicitly reposition the paper as a substrate/resource for memorization auditing, tighten the factor taxonomy, make the release genuinely multi-method ready, and stop short of claiming a validated memorization benchmark. No-go if the manuscript still markets this MVP as already solving memorization measurement in Chinese finance. On that stronger claim, the core R1 objection still stands.
