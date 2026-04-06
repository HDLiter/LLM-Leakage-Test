# Experiment Plan

**Problem**: Measure look-ahead leakage in Chinese financial news LLM pipelines and test whether task design changes contamination exposure on the same `(article, target)` inputs.
**Method Thesis**: On a clustered 1,000-case CLS-Leak benchmark, meaningful decomposed extraction of authority and novelty should show lower excess invariance than direct prediction or sentiment, and that attenuation should survive matched-format and sham controls.
**Date**: 2026-04-05

## Claim Map
| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks |
|-------|-----------------|-----------------------------|---------------|
| C1 | The paper is only novel if task design, not just model choice, changes measured leakage. | On the same clustered cases, DeepSeek excess invariance shows `direct > sentiment > authority` and `direct > sentiment > novelty`; the ordering survives matched-format prompts; sham decomposition does not reproduce the drop. | B2, B3 |
| C2 | The main result is stronger if contamination signals line up with time and with an independent white-box familiarity prior. | DeepSeek excess invariance rises with article age, is near-zero in a documented post-boundary placebo window, and is positively partially rank-correlated with Qwen LAP / Min-K% after article controls. | B4 |

## Paper Storyline
- Main paper must prove:
- The benchmark is trustworthy enough that leakage estimates are interpretable: target linking, clustering, counterfactual QC, and label arbitration are auditable.
- The primary result is a task-ordering result on fixed inputs: direct prediction leaks most, sentiment leaks less, meaningful decomposition leaks least.
- The effect is semantic rather than structural: matched-format prompts keep the ordering and sham decomposition does not.
- Time and white-box familiarity evidence are directionally consistent with contamination rather than pure prompt brittleness.
- Appendix can support:
- Full 72-cell sampling matrix, reserve-pool diagnostics, and per-cell backfill logs.
- Counterfactual QC pass rates, pairwise weighted kappa, style-distance distributions, and retrieval nonexistence statistics.
- Qwen k-sweep and calibration sensitivity table.
- Paraphrase-stability distributions by task and cluster-level residual plots.
- E5 mixed-effects heterogeneity and E6 downstream XGBoost sensitivity, if completed.
- Experiments intentionally cut:
- Dated-base-model comparisons unless benchmark construction finishes early.
- Additional grey-box detectors such as CDD / entropy for the main paper.
- `decomposed_impact.*` from the main story; keep it for E6 only.
- Multi-horizon return analysis beyond the pre-registered 3-day horizon.

## Experiment Blocks

### Block 1: CLS-Leak Benchmark Build and Label Freeze
- Claim tested: The benchmark itself is precise enough to support a paper-level contamination claim rather than a curation artifact.
- Why this block exists: If the sample, targets, or rewrites are noisy, E1-E4 are not publishable.
- Dataset / split / task: Entire CLS raw corpus at `D:\GitRepos\Thales\datasets\cls_telegraph_raw\` from `2020-01-01` to `2026-02-23` (`2248` dated JSON files plus `manifest.json`, `1,162,385` raw articles). Output benchmark: `300` Tier1 anchor + `700` Tier2 core.
- Compared systems: Thales entity extraction and topic/signal modules, rule-based target linker, DeepSeek rewrite generator, Qwen local judge, three independent LLM annotators, and human arbitration.
- Metrics: 72-cell fill rate, target-link audit precision, cluster collision rate, counterfactual QC pass rate by template, pairwise weighted kappa on Tier1, human override rate, and article/cluster counts in every summary table.
- Setup details: deterministic sampling seed `20260405`; reserve pool size `3 x cell_target`; one representative article per target-day cluster; all benchmark artifacts versioned under `data/benchmark/`.
- Success criterion: all `72` cells filled to exact target, Tier1 fully human-audited, first-two-attempt counterfactual QC pass rate `>85%` for every template, target-link precision `>=0.95` on the audited sample, and Tier1 pairwise weighted kappa `>=0.70` for direct/sentiment and `>=0.60` for authority/novelty.
- Failure interpretation: If this block fails, reduce scope and fix the benchmark before running E1-E4; do not trust downstream leakage estimates.
- Table / figure target: Table 1 benchmark summary, Figure 1 sampling matrix, Table 2 QC diagnostics.
- Priority: MUST-RUN

### Block 2: Leakage Spectrum Across Task Types (Primary E3)
- Claim tested: Meaningful decomposition attenuates contamination relative to direct prediction and sentiment.
- Why this block exists: This is the main mechanism-level contribution.
- Dataset / split / task: `CLS-Leak-1000`; base prompts only; original article plus one neutral paraphrase and one family-specific targeted counterfactual per task family.
- Compared systems: `direct_prediction.base`, `sentiment_classification.base`, `decomposed_authority.base`, `decomposed_novelty.base` on `deepseek-chat`.
- Metrics: mean cluster-level excess invariance (primary), `cf_invariance`, `para_invariance`, cluster bootstrap confidence intervals, ordered contrast / trend test, and article/cluster counts.
- Setup details: frozen prompt set `2026-04-05-v2`; `temperature=0`; cache enabled; paired within-cluster comparisons; `2000` cluster bootstrap resamples.
- Success criterion: mean excess invariance satisfies `direct > sentiment > authority` and `direct > sentiment > novelty`, with positive clustered-bootstrap contrasts for `direct - sentiment`, `sentiment - authority`, and `sentiment - novelty`.
- Failure interpretation: If sentiment or decomposition does not reduce excess invariance, the paper must pivot away from "task design as mitigation" to a null-result framing.
- Table / figure target: Table 3 primary leakage spectrum, Figure 2 per-cluster paired excess invariance.
- Priority: MUST-RUN

### Block 3: Novelty Isolation and Falsification (Matched Format + Sham, E3/E4)
- Claim tested: The E3 ordering is semantic, not just a by-product of structured output, longer completions, or generic extraction burden.
- Why this block exists: This directly answers the strongest reviewer alternative explanation.
- Dataset / split / task: `CLS-Leak-1000`; matched-format prompts for direct, sentiment, authority, novelty; sham prompt on original + neutral paraphrase + targeted edit.
- Compared systems: `direct_prediction.matched`, `sentiment_classification.matched`, `decomposed_authority.matched`, `decomposed_novelty.matched`, `sham_decomposition.control`.
- Metrics: matched-format excess invariance ordering, `base -> matched` deltas, sham-vs-meaningful decomposition gaps, paraphrase-stability distributions by task, and Romano-Wolf stepdown for the primary family.
- Setup details: common matched schema from `config/prompts/README.md`; same cluster bootstrap protocol as Block 2; sham rewrites use `sham_edits`.
- Success criterion: matched-format ordering stays directionally identical to Block 2, and sham decomposition remains materially more invariant than meaningful decomposition with a target absolute gap `>=0.05` or a `95%` cluster-bootstrap CI excluding equality.
- Failure interpretation: If sham reduces leakage as much as meaningful decomposition, the central claim weakens to a structure effect.
- Table / figure target: Table 4 matched-format ablation, Figure 3 sham vs meaningful decomposition, Appendix Figure A1 paraphrase stability.
- Priority: MUST-RUN

### Block 4: Temporal Decay and Cross-Model Concordance (E1/E2)
- Claim tested: Leakage signals track time and agree across access regimes rather than being prompt-local artifacts.
- Why this block exists: This strengthens the interpretation of Block 2 and addresses reviewer concerns about proxy validity.
- Dataset / split / task: `CLS-Leak-1000`; DeepSeek base-prompt outputs from Block 2; Qwen2.5-7B article logprobs on original articles only.
- Compared systems: DeepSeek excess invariance vs Qwen LAP / Min-K% at `k in {0.10, 0.20, 0.30, 0.40, 0.50}`.
- Metrics: temporal decay smoother by publication date, placebo-frontier mean excess invariance, partial Spearman `rho`, clustered-bootstrap CI, and a k-sweep sensitivity table.
- Setup details: Qwen served locally with vLLM logprobs; one forward pass per original article and compute k-sweep offline. DeepSeek placebo frontier is tied to the exact API model boundary captured at run time. As of `2026-04-05`, official DeepSeek docs state that `deepseek-chat` corresponds to `DeepSeek-V3.2`, upgraded on `2025-12-01`, so the primary placebo window is `2026-01-01` to `2026-02-23`. For Qwen, use its documented open release date `2024-09-19` as the descriptive boundary for post-release freshness checks.
- Success criterion: positive pre-boundary age-to-leakage pattern, near-zero placebo excess invariance in `2026-01-01` to `2026-02-23`, and partial Spearman `rho > 0` with clustered-bootstrap CI excluding zero for the pre-registered primary `k=0.20`.
- Failure interpretation: If time or LAP do not align with DeepSeek counterfactual sensitivity, contamination may be model-specific, detector-specific, or too weak on the benchmark.
- Table / figure target: Figure 4 temporal decay curve, Table 5 concordance and k-sweep, Appendix Table A2 placebo diagnostics.
- Priority: MUST-RUN

### Block 5: Heterogeneity and Downstream Sensitivity (E5/E6)
- Claim tested: Leakage concentration is not uniform across items and may inflate downstream predictive signal.
- Why this block exists: Useful for discussion and finance-facing payoff, but not required for MVP acceptance.
- Dataset / split / task: `CLS-Leak-1000` plus 3-day abnormal-return panel for linked targets.
- Compared systems: mixed-effects models by cluster/article metadata; XGBoost on raw features vs orthogonalized features vs contamination proxies.
- Metrics: random-effect variance components, FDR-controlled subgroup contrasts, 3-day rank IC, alpha decay, and the contamination interaction coefficient.
- Setup details: cluster-level random intercepts, cross-fitted orthogonalization, one pre-registered 3-day horizon.
- Success criterion: stable heterogeneity patterns or clear downstream attenuation after orthogonalization.
- Failure interpretation: Null E5/E6 does not invalidate the main paper; it only limits the finance-specific extension.
- Table / figure target: Appendix Table A3 heterogeneity, Appendix Figure A2 downstream sensitivity.
- Priority: NICE-TO-HAVE

## CLS-Leak Benchmark Construction Pipeline

### Artifact Layout
- Raw input: `D:\GitRepos\Thales\datasets\cls_telegraph_raw\`
- Flattened corpus: `data/benchmark/cls_raw_index.parquet`
- Reference snapshots: `data/benchmark/reference/security_master_snapshot.parquet`, `data/benchmark/reference/index_membership_snapshot.parquet`, `data/benchmark/reference/shenwan_membership_snapshot.parquet`
- Enriched article frame: `data/benchmark/cls_enriched.parquet`
- Cluster frame: `data/benchmark/cls_event_clusters.parquet`
- Sampling frame and reserves: `data/benchmark/cls_sampling_frame.parquet`, `data/benchmark/cls_sampling_reserve.parquet`
- Counterfactuals: `data/benchmark/counterfactuals/originals.jsonl`, `data/benchmark/counterfactuals/rewrites.jsonl`
- QC outputs: `data/benchmark/qc/qc_stage1_llm_judge.parquet`, `data/benchmark/qc/qc_stage2_style_distance.parquet`, `data/benchmark/qc/qc_stage3_retrieval.parquet`, `data/benchmark/qc/qc_stage4_human_review.csv`
- Annotation outputs: `data/benchmark/annotations/original_labels.jsonl`, `data/benchmark/annotations/rewrite_labels.jsonl`, `data/benchmark/annotations/arbitration_log.csv`
- Final release: `data/benchmark/releases/CLS-Leak-v1.0.jsonl`

### Step 1: Raw ingest and normalization
1. Read every dated file matching `D:\GitRepos\Thales\datasets\cls_telegraph_raw\YYYY-MM-DD.json`; skip `manifest.json` and `logs/`.
2. Flatten each article to one row with columns: `raw_id`, `date`, `time`, `timestamp`, `title`, `content`, `category`, `type`, `recommend`, `author`, `source`, `source_file`.
3. Create normalized text fields:
4. `title_norm = NFKC(title).strip()`
5. `content_norm = NFKC(content).strip()`
6. `text_norm = title_norm + "\n" + content_norm`
7. Filter to candidate benchmark items with:
8. `60 <= len(content_norm) <= 600`
9. Chinese-character share `>= 0.60`
10. non-empty `timestamp`
11. drop exact duplicates on `(date, title_norm, content_norm)`
12. Save to `data/benchmark/cls_raw_index.parquet`.
- Time estimate: `0.5` day CPU wall time.

### Step 2: Entity extraction and target candidate generation
1. Run Thales entity extraction using `D:\GitRepos\Thales\pipeline\news_processing\entity_extraction.py` with the Thales entity dictionary from `D:\GitRepos\Thales\config\loader.py`.
2. For each article, collect candidate companies, sectors, indices, institutions, and persons.
3. Score target candidates with the deterministic rule below:
4. `+5` if exact alias match appears in title.
5. `+5` if stock code or ETF code appears.
6. `+3` if alias appears in the first `80` characters of content.
7. `+2` per additional exact alias match in content, capped at `+4`.
8. `+2` if the article's top Thales entity type matches the candidate target type.
9. `-3` if the candidate is only a secondary mention and never appears in title or first sentence.
10. Select the highest-scoring candidate if `score >= 6` and `top1 - top2 >= 2`; otherwise mark `ambiguous_target=1` and send to manual queue.
11. Assign `target_type in {company, sector, index}` and `target`.
12. Save all candidates and scores to `data/benchmark/cls_target_candidates.parquet`.
- Time estimate: `1.0` day, mostly CPU plus one short manual pass.

### Step 3: Topic classification and 13-to-4 event mapping
1. Run the Thales topic classifier using `D:\GitRepos\Thales\prompts\news_processing\topic_classification.py`.
2. Keep `event_type_top1`, `event_type_top2`, and raw score vector.
3. Map the 13 Thales types to the 4 benchmark macro categories with the deterministic table below:

| Thales event type | Benchmark macro category |
|-------------------|--------------------------|
| `POLICY`, `ENFORCEMENT`, `LEGAL` | `policy` |
| `EARNINGS`, `CORPORATE`, `PRODUCT`, `PERSONNEL`, `TRADING`, `OWNERSHIP` | `corporate` |
| `INDUSTRY` | `industry` |
| `INDICATOR`, `GEOPOLITICS` | `macro` |
| `OTHER` + `target_type=sector` | `industry` |
| `OTHER` + any other target type | `macro` |

4. Store both the fine 13-way type and the 4-way macro category in `data/benchmark/cls_enriched.parquet`.
- Time estimate: `0.5` day if batched through Thales pipeline.

### Step 4: Signal-profile enrichment and prominence tiers
1. Run Thales signal profiling with `D:\GitRepos\Thales\pipeline\news_processing\signal_profile.py`.
2. Keep `primary_modality`, full modality scores, and `primary_authority_level` plus the full 8-bin authority distribution.
3. Build daily reference snapshots:
4. `data/benchmark/reference/security_master_snapshot.parquet`: company aliases, codes, listing status.
5. `data/benchmark/reference/index_membership_snapshot.parquet`: SSE50 and CSI300 constituent membership by date.
6. `data/benchmark/reference/shenwan_membership_snapshot.parquet`: Shenwan `L1/L2/L3` membership by date.
7. Assign prominence tier:
8. `sse50` if the linked company target is in SSE50 on publication date.
9. `csi300_ex_sse50` if the linked company target is in CSI300 but not SSE50.
10. `small_cap` otherwise.
11. For `sector` or `index` targets, derive `prominence_proxy_company` as the highest-scoring company mention from Step 2 and assign tier from that proxy. If no proxy company exists, exclude the article from the sampling frame.
- Time estimate: `0.5` day after the reference snapshots are materialized.

### Step 5: Event clustering
1. Create a canonical cluster key:
2. `cluster_date = publication date in Asia/Shanghai`
3. `cluster_target_key = canonical_company_id` for company targets; otherwise `target_type + "::" + canonical_target`
4. `cluster_key = cluster_date + "::" + cluster_target_key`
5. This enforces the project rule: same company plus same day collapses to one cluster.
6. Within each cluster, compute title fingerprint and text fingerprint:
7. 64-bit SimHash on `title_norm`
8. char-5gram MinHash on `content_norm`
9. Keep one representative article per cluster using the ranking:
10. highest `recommend`
11. then lowest absolute difference to the corpus median content length (`136` chars from the current sample)
12. then earliest timestamp
13. If a cluster contains multiple clearly distinct title fingerprints (`SimHash distance > 10`) or unrelated topic codes, keep the modal fingerprint article as representative and set `collision_risk=1`.
14. Record `propagation_size = raw articles collapsed into the cluster`.
15. Save cluster-level rows to `data/benchmark/cls_event_clusters.parquet`.
- Time estimate: `0.5` day CPU.

### Step 6: Stratified sampling matrix
1. Build the sampling frame from cluster-level rows with confident targets and no unresolved ambiguity.
2. Final benchmark size is exactly `1000` clusters.
3. Tier split:
4. Tier1 anchor = `300`
5. Tier2 core = `700`
6. Temporal bins: `2020`, `2021`, `2022`, `2023`, `2024`, `2025+`
7. Prominence tiers: `sse50`, `csi300_ex_sse50`, `small_cap`
8. Macro event types: `policy`, `corporate`, `industry`, `macro`
9. Exact cell targets:

For each of `2020`, `2021`, `2022`, `2023`, `2024` use the same `160`-case matrix and `48`-case anchor overlay.

| Prominence \\ Event | policy | corporate | industry | macro | Year total | Anchor |
|---------------------|--------|-----------|----------|-------|------------|--------|
| `sse50` | 13 | 13 | 13 | 13 | 52 | 16 |
| `csi300_ex_sse50` | 13 | 14 | 13 | 13 | 53 | 16 |
| `small_cap` | 13 | 14 | 14 | 14 | 55 | 16 |
| Year total | 39 | 41 | 40 | 40 | 160 | 48 |

For `2025+`, use the `200`-case matrix and `60`-case anchor overlay below.

| Prominence \\ Event | policy | corporate | industry | macro | Year total | Anchor |
|---------------------|--------|-----------|----------|-------|------------|--------|
| `sse50` | 16 | 17 | 16 | 17 | 66 | 20 |
| `csi300_ex_sse50` | 16 | 17 | 17 | 17 | 67 | 20 |
| `small_cap` | 16 | 17 | 17 | 17 | 67 | 20 |
| Year total | 48 | 51 | 50 | 51 | 200 | 60 |

10. Anchor allocation rule:
11. In `2020-2024`, take exactly `4` Tier1 items per cell.
12. In `2025+`, take exactly `5` Tier1 items per cell.
13. Core allocation rule: core count per cell = full cell target minus anchor count.
14. Maintain a reserve queue of `3 x cell_target` candidate clusters per cell for QC backfill.
15. Save the exact draw order to `data/benchmark/cls_sampling_frame.parquet` and `data/benchmark/cls_sampling_reserve.parquet`.
- Time estimate: `0.5` day.

### Step 7: Target entity linking protocol
1. Every sampled item must have exactly one benchmark target and one `target_type`.
2. Linking hierarchy:
3. Prefer `company` if a company candidate passes the Step 2 threshold.
4. Otherwise use `sector` if the article is sector-scoped and the sector candidate is unambiguous.
5. Otherwise use `index` for policy/macro items explicitly framed on a market or index object.
6. Required fields in final benchmark row:
7. `target`
8. `target_type`
9. `target_company_id` or `target_sector_code` or `target_index_code`
10. `prominence_tier`
11. `macro_event_type`
12. `event_type_top1`
13. `primary_authority_level`
14. `shenwan_l1`, `shenwan_l2`, `shenwan_l3` if available
15. Manual arbitration rules:
16. send to Tier1 queue if `ambiguous_target=1`
17. send to Tier1 queue if `top1 - top2 < 2`
18. send to Tier1 queue if `target_echo` later fails during prompt smoke
19. reject from final sample if human cannot resolve a single target in under `2` minutes
- Time estimate: `1.0` day combined with anchor audit.

### Step 8: Counterfactual generation pipeline
1. Generate `6` rewrites per sampled case, all target-conditioned:
2. `neutral_paraphrase`
3. `semantic_reversal.direction`
4. `semantic_reversal.sentiment`
5. `provenance_swap`
6. `novelty_toggle`
7. `sham_edits`
8. Template mapping:
9. `direct_prediction.*` uses `semantic_reversal.direction`
10. `sentiment_classification.*` uses `semantic_reversal.sentiment`
11. `decomposed_authority.*` uses `provenance_swap`
12. `decomposed_novelty.*` uses `novelty_toggle`
13. `sham_decomposition.control` uses `sham_edits`
14. Every family also uses the shared `neutral_paraphrase`.
15. Generation order per case:
16. label original first
17. generate neutral paraphrase
18. generate the four family-specific targeted rewrites plus sham
19. validate JSON with `PromptLoader` and `extract_json_robust`
20. retry up to `2` times per failed rewrite
21. replace the case from the reserve pool if any required family rewrite still fails after retry
22. Save originals to `data/benchmark/counterfactuals/originals.jsonl` and rewrites to `data/benchmark/counterfactuals/rewrites.jsonl`.
- Time estimate: `2.0` days wall time with batching and retry.

### Step 9: QC pipeline (4 stages)
1. Stage 1, LLM-as-judge plausibility:
2. Judge each rewrite with two independent judges: DeepSeek-chat and local Qwen2.5-7B.
3. Score `target preservation`, `internal coherence`, `financial plausibility`, `intended edit realized`, and `no new economically material facts` on `1-5`.
4. Pass rule: median score `>=4` and no individual dimension `<3`.
5. Stage 2, style and edit-distance matching:
6. Global thresholds:
7. length ratio in `[0.80, 1.25]`
8. sentence-count delta `<=2`
9. char-level normalized Levenshtein ratio in `[0.08, 0.35]` for targeted edits
10. char-level normalized Levenshtein ratio in `[0.10, 0.45]` for neutral paraphrases
11. reject rewrites where untouched key entities disappear
12. reject numeric changes outside `changed_spans`, except deliberate `numeric_density` sham edits
13. Stage 3, retrieval-based nonexistence:
14. Build a MinHash / BM25 index over all `1,162,385` raw CLS articles.
15. Query each rewrite against the corpus using title plus first `80` chars.
16. Fail if any non-source article has char-5gram Jaccard `>=0.80`, exact title match on a different raw article, or sequence similarity `>=0.90`.
17. Stage 4, human review:
18. Tier1 receives `100%` human review on originals and targeted-field rewrite checks.
19. Tier2 receives a `10%` random spot-check plus all items flagged by Stages 1-3.
20. Required QC reporting:
21. pass rate by template and by year bin
22. pairwise weighted kappa on Tier1 review sample
23. style-distance summary table
24. retrieval false-positive and true-positive counts
- Time estimate: `1.5` days wall time plus human review time.

### Step 10: Ground truth annotation protocol
1. Use three independent annotators for original benchmark labels:
2. Annotator A: `deepseek-chat`
3. Annotator B: `qwen2.5-7b-instruct`
4. Annotator C: `Codex` agent or `Claude` if that connector is already configured; keep the same third annotator for the entire run
5. Independence rules:
6. identical label schema, but separate prompt wrappers
7. `temperature=0`
8. annotators never see each other's labels
9. annotators see only article text, target, target type, and schema
10. Fields to label on originals:
11. `direction`
12. `sentiment`
13. `source_credibility`
14. `regulatory_vs_rumor`
15. `official_vs_unattributed`
16. `disclosure_frame`
17. `information_freshness`
18. `novelty_strength`
19. For rewrites, annotate only the fields that should change plus the family-specific unchanged checks:
20. neutral paraphrase: all applicable fields must stay unchanged
21. semantic reversal: direct or sentiment field must flip as intended
22. provenance swap: authority fields only
23. novelty toggle: novelty fields only
24. sham edits: sham fields only
25. Consensus rule:
26. accept a field if at least `2/3` annotators agree
27. send to human arbitration if no majority, if confidence spread is `>20`, or if annotators disagree on target preservation
28. Human arbitration:
29. all Tier1 originals
30. all Tier1 rewrites on edited fields
31. Tier2 originals or rewrites only when consensus fails or QC flags them
32. Save consensus and vote pattern to `data/benchmark/annotations/original_labels.jsonl` and `data/benchmark/annotations/rewrite_labels.jsonl`.
- Time estimate: `3.0` days wall time, mostly asynchronous plus `30-38` human hours.

### Step 11: Final freeze and benchmark package
1. Freeze `CLS-Leak-v1.0` only after all required cell targets are filled and all failed items are backfilled from reserve.
2. Final row-level fields:
3. `benchmark_id`, `cluster_key`, `raw_article_id`, `cluster_date`, `target`, `target_type`, `prominence_tier`, `macro_event_type`, `event_type_top1`, `propagation_size`, `collision_risk`
4. `original_text`
5. rewrite texts and metadata
6. consensus labels
7. QC pass/fail flags
8. judge scores
9. annotation vote pattern
10. `article_count=1` and `cluster_count=1` per row for downstream tables
11. Release note must state both nominal article count and effective cluster count in every experiment table.
- Time estimate: `0.5` day.

### End-to-end benchmark build timeline
- Raw ingest and normalization: `0.5` day
- Entity extraction and target candidate scoring: `1.0` day
- Topic and signal enrichment: `1.0` day
- Clustering and sampling frame: `1.0` day
- Counterfactual generation: `2.0` days
- QC stages 1-4: `1.5` days
- Annotation and arbitration: `3.0` days
- Final freeze and packaging: `0.5` day
- Total expected wall time: `10.5` working days

## Run Order and Milestones
| Milestone | Goal | Runs | Decision Gate | Cost | Risk |
|-----------|------|------|---------------|------|------|
| `M0` | Validate the current code and data assumptions on a small pilot: raw CLS ingest, target linking, clustering, and frozen prompt smoke. | `R001-R003` | Proceed only if prompt/schema pass rate is `>99%` and pilot target-link precision is `>=0.90`. | `0.5` day CPU, `<$1` API | `src/news_loader.py` still assumes an older CLS schema and can silently misparse the raw corpus. |
| `M1` | Build and freeze `CLS-Leak-1000` with reserve backfills, QC, and annotation logs. | `R004-R011` | Proceed only if all `72` cells are filled, Tier1 is fully audited, and QC / agreement thresholds are met. | `3-4` days wall, `8-12` CPU hours, `4-6` GPU hours, `$6-$10` API | Underfilled cells, ambiguous targets, or low rewrite pass rates can stall the whole paper. |
| `M2` | Compute contamination priors and cache core model outputs needed by every must-run experiment. | `R012-R013` | Proceed only if `1000/1000` originals get Qwen logprobs and DeepSeek completion success is `>=98%`. | `1` day wall, `6-12` GPU hours, `$4-$6` API | vLLM logprob support or API rate limits may create partial data. |
| `M3` | Run the primary E3 leakage spectrum on base prompts and check whether the main ordering exists before more ablations. | `R014` | Continue to `M4` only if point estimates are ordered or at least directionally promising. | `0.5` day wall, cached DeepSeek outputs, `<$1` incremental | A null primary ordering may require immediate narrative pivot. |
| `M4` | Run decisive reviewer-facing checks: matched-format, sham falsification, temporal decay, placebo frontier, and Qwen concordance. | `R015-R019` | Main paper is green only if matched-format stays ordered and sham does not collapse the effect. | `1` day wall, `2-4` GPU hours, `$2-$4` API | The effect may disappear once format is controlled. |
| `M5` | Freeze tables, figures, appendix diagnostics, and optional E5/E6 only after the main paper is defensible without them. | `R020-R022` | Stop once the main paper is complete; do not let E5/E6 delay submission. | `1-2` days wall, optional `6-10` GPU hours, optional `$5+` API | Scope creep and reviewer-driven extras can steal time from paper polish. |

## Compute and Data Budget
- Total estimated GPU-hours: `12-18` GPU-hours on a `4090` if Qwen handles LAP, local judging, and local annotation; `24-36` GPU-hours on the local `4060 Ti` if no rental is used.
- DeepSeek API budget: plan for `27,000` core evaluation calls plus roughly `6,000` rewrite generations and QC / annotation overhead. Using the official `2026-04-05` DeepSeek API prices for `deepseek-chat` (`$0.28 / 1M` uncached input tokens and `$0.42 / 1M` output tokens), a safe no-cache budget is `$15-$30`.
- Data preparation needs: raw CLS input is about `0.94 GB`; expect `2-4 GB` of parquet and QC artifacts under `data/benchmark/`; reserve `10 GB` free disk for the retrieval index and intermediate files.
- Human evaluation needs: Tier1 full audit plus Tier2 spot-checking is about `30-38` human hours, ideally split across `2` annotators plus one adjudicator.
- Biggest bottleneck: benchmark construction, especially target linking, counterfactual QC, and reserve backfilling; model inference is not the binding constraint.

## Risks and Mitigations
- Risk: The current repo loader is stale relative to the raw CLS schema.
- Mitigation: Replace `src/news_loader.py` usage for benchmark construction with a new manifest-aware ingest step in `M0`; do not reuse the legacy `ctime`-based path.
- Risk: Same-company same-day clustering can merge unrelated events.
- Mitigation: Keep the mandated company-day cluster key, but store `collision_risk`, `propagation_size`, and title fingerprints; run sensitivity analyses excluding `collision_risk=1`.
- Risk: Some 72-cell strata will underfill after target-linking and QC.
- Mitigation: Pre-build a `3 x` reserve pool per cell and backfill only from the same cell; if a cell still fails, shrink Tier2 first, never Tier1.
- Risk: Counterfactuals may drift off target or invent facts.
- Mitigation: Enforce `target_echo`, changed-span validation, two-model plausibility judging, and retrieval nonexistence before any rewrite enters the final benchmark.
- Risk: DeepSeek API model drift can invalidate the placebo frontier.
- Mitigation: Record the exact DeepSeek API model version string and changelog date at run start; if the API boundary changes before execution, recompute the placebo window and rerun only the affected temporal tables.
- Risk: Qwen LAP is sensitive to the choice of `k`.
- Mitigation: Pre-register `k=0.20` as primary, compute a fixed `k`-sweep offline from the same logprob pass, and move all other `k` values to sensitivity-only reporting.
- Risk: Human arbitration becomes the schedule bottleneck.
- Mitigation: Restrict mandatory human review to Tier1 originals plus edited rewrite fields, and gate Tier2 human review on failed consensus or QC flags.

## Final Checklist
- [x] Main paper tables are covered
- [x] Novelty is isolated
- [x] Simplicity is defended
- [x] Frontier contribution is justified or explicitly not claimed
- [x] Nice-to-have runs are separated from must-run runs
