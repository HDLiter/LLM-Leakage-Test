# BENCHMARK R4 Step 1 — NLP Factor Brainstorm
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md v2
**Prior rounds:** BENCHMARK_R1/R2/R3_NLP.md

---

### Factor: Duplicate Cluster Size
**Concept**: The number of CLS documents in the same event cluster, treated as direct repeated-exposure mass for the exact event text family.
**Mechanism (why this should affect memorization)**: Repetition is the cleanest frequency-recall channel in the memorization literature. If the same event text family appears many times in web-scale training data, the model receives multiple nearly identical updates on the same surface pattern, which should raise the chance of case-specific recall or other inadmissible dependence. This is exactly the channel where deduplication materially reduces leakage.
**Category**: statistical
**Literature provenance**: Strong prior art. Kandpal, Wallace & Raffel (2022) show generation and membership signals rise sharply with duplicate count and fall after deduplication. Carlini et al. (2023) report a log-linear increase in memorization with example duplication. Lee et al. (2021) show repetitive substrings are common in web corpora. Zhang et al. (2021) explicitly warn that many memorization criteria are driven by repeated data.
**Operationalization on CLS + cluster metadata**: `dup_exposure = log1p(duplicate_cluster_size)`. Use the schema value directly; if discretized, bin by empirical terciles or quartiles on the full benchmark pool.
**Predicted effect direction**: Larger clusters should show stronger memorization, because they correspond to more repeated exposure to highly similar CLS surface forms.
**Data feasibility at 1500 scale**: trivial; zero manual work.
**Coverage estimate**: 100%.
**Failure modes**: Depends on clustering quality. If clusters mix genuine rewrites with weak semantic neighbors, the factor becomes noisy.
**Framing support**: both

### Factor: Cluster Temporal Span / Repost Persistence
**Concept**: How long the event cluster remains active in the CLS archive, measured as the time span covered by cluster members.
**Mechanism (why this should affect memorization)**: A cluster that persists over multiple publication times is more likely to be re-crawled, re-indexed, and retained across temporally messy web snapshots. This is distinct from raw duplicate count: some events are reposted many times within minutes, others continue resurfacing across days. Persistence is a plausible exposure amplifier under the "old data in new dumps" and near-duplicate archival problems highlighted in temporal-cutoff work.
**Category**: statistical
**Literature provenance**: Novel factor, but directly motivated by Cheng et al. (2024) on effective cutoffs, old data persisting in newer dumps, and deduplication complications from lexical and semantic near-duplicates. Also coherent with leakage-resistant benchmark papers that emphasize archival persistence as contamination risk.
**Operationalization on CLS + cluster metadata**: For each cluster, retrieve member publication times from raw rows; compute `persistence_hours = max(pub_time) - min(pub_time)`, then use `log1p(persistence_hours)`. If timestamps are coarse, use distinct publication dates instead.
**Predicted effect direction**: Longer-lived clusters should show stronger memorization, because they have more opportunities for repeated web exposure beyond the first publication.
**Data feasibility at 1500 scale**: low; one metadata join over cluster members.
**Coverage estimate**: ~98-100% if member timestamps are present in raw rows.
**Failure modes**: Can be inflated by archival reposts or late summaries that are operationally different from the original wave.
**Framing support**: both

### Factor: Cutoff Proximity
**Concept**: Signed temporal distance between `first_seen_time` and the evaluated model's cutoff date.
**Mechanism (why this should affect memorization)**: Temporal memorization is not binary. Dated Data and Set the Clock both show that effective knowledge cutoffs vary by resource and are often misaligned with reported cutoffs; pre-cutoff items near the boundary are therefore especially ambiguous. In finance, temporally close items are the most plausible leakage zone, while post-cutoff items are the cleanest negative stratum.
**Category**: statistical
**Literature provenance**: Cheng et al. (2024) on effective cutoff heterogeneity; Zhao et al. (2024) on temporal misalignment; He et al. (2025) on chronologically consistent models for leakage-free backtesting; Li & Flanigan (2024) on chronological performance gaps under contamination.
**Operationalization on CLS + cluster metadata**: For each model, compute `cutoff_gap_days = cutoff_date_model - first_seen_time`. Keep as a continuous signed variable. If binned, enforce the semantic split at zero first, then split the pre-cutoff side by empirical quantiles.
**Predicted effect direction**: Stronger memorization should concentrate in pre-cutoff and especially near-cutoff strata; well post-cutoff items should show the weakest memorization.
**Data feasibility at 1500 scale**: trivial once cutoff dates are fixed.
**Coverage estimate**: 100%.
**Failure modes**: Reported cutoff is only a proxy for effective cutoff, especially for opaque models like DeepSeek.
**Framing support**: both

### Factor: Template Rigidity / Boilerplate Similarity
**Concept**: The degree to which a CLS article's surface form matches common newsroom templates used across other clusters.
**Mechanism (why this should affect memorization)**: Finance news is full of formulaic leads, disclosure boilerplate, and recurring syntactic shells. Those repeated shells can inflate surface-form memorization signals even when the event itself is mundane. This is not a bug; it is a real stratum dimension, because memorization detectors operating on exact CLS text are sensitive to repeated form, and Zhang et al. argue that "common memorization" is often driven by frequent phrases and templated text.
**Category**: linguistic
**Literature provenance**: Zhang et al. (2021) explicitly identify frequent phrases, public knowledge, templated texts, and repeated data as major confounds in memorization measurement. Lee et al. (2021) show long repetitive substrings are widespread in web corpora. Kandpal et al. (2022) and Carlini et al. (2023) connect repetition to regeneration and leakage.
**Operationalization on CLS + cluster metadata**: Build char-5gram TF-IDF vectors on one canonical CLS document per cluster. For each case, compute the mean cosine similarity to its top-5 nearest neighbors from different clusters. Higher mean similarity = more rigid/template-like.
**Predicted effect direction**: Higher rigidity should show stronger surface-form memorization tendencies, because repeated textual shells are easier to absorb and reuse.
**Data feasibility at 1500 scale**: moderate; one ANN similarity pass.
**Coverage estimate**: ~100%.
**Failure modes**: May partly capture publisher style rather than event memorization; very short texts can be unstable.
**Framing support**: both

### Factor: Exact-Span Rarity / Lexical Idiosyncrasy
**Concept**: How much the CLS text contains rare, case-specific exact spans relative to the rest of the benchmark corpus.
**Mechanism (why this should affect memorization)**: Memorization claims are strongest when the model appears to know a surface form that generic language modeling should not predict easily. Rare exact spans, especially unusual entity-number-date combinations, play the role of canary-like payloads: if such material is stored, it is much harder to explain away as mere semantic prior. This is the surface-form-sensitive factor most aligned with exact-text measurement.
**Category**: linguistic
**Literature provenance**: Carlini et al. (2019) show rare/unique sequences are vulnerable to unintended memorization. Carlini et al. (2021) extract verbatim examples that appear in only one training document. Zhou et al. (2023) show memorization can localize to entity-level spans.
**Operationalization on CLS + cluster metadata**: On the canonical-cluster corpus, compute cluster-level document frequency for nonnumeric char-6grams. For each case, score the mean IDF of its top decile rarest qualifying 6grams. Higher score = more idiosyncratic exact text.
**Predicted effect direction**: Holding exposure roughly constant, higher idiosyncrasy should show stronger article-specific memorization, because success on rare spans is less explainable by generic priors.
**Data feasibility at 1500 scale**: moderate; one corpus-frequency pass.
**Coverage estimate**: ~95-100%.
**Failure modes**: Typos, OCR artifacts, or formatting noise can masquerade as rarity; numeric-heavy news needs cleanup rules.
**Framing support**: both

### Factor: Locator Specificity
**Concept**: The extent to which the CLS lead pins the event to a unique time-entity-venue tuple.
**Mechanism (why this should affect memorization)**: This is the cleanest R1 decomposition of "anchor strength." Events are easier to recall as specific episodes when they are tightly bound to who, when, and where: a named firm or ticker, an explicit date/time, and a concrete market venue, regulator, or place. High specificity should favor case-level episodic recall over generic sector priors.
**Category**: linguistic
**Literature provenance**: Novel factor as operationalized here, but grounded by Huet et al. (2025), which represent episodic events via temporal context, spatial context, and involved entities; Gurnee & Tegmark (2024), which show LMs encode space and time; and Zhou et al. (2023), which show entity-linked memorization is real.
**Operationalization on CLS + cluster metadata**: Score the first two sentences of the CLS article for three binary anchors: `has_explicit_date_or_time`, `has_named_entity_or_ticker` (using `key_entities`), and `has_venue_regulator_place` (exchange, city, regulator, court, ministry, etc.). `locator_specificity = sum(anchors)` in `[0,3]`.
**Predicted effect direction**: Higher specificity should show stronger case-specific memorization, because the event is more uniquely addressable in parametric memory.
**Data feasibility at 1500 scale**: low to moderate; regex plus entity lists.
**Coverage estimate**: ~85-95%.
**Failure modes**: Chinese financial briefs often omit place; macro or policy items can be specific without overt locators.
**Framing support**: both

### Factor: Entity Salience / Head-Tail Position
**Concept**: The prominence of the case's key entities in the broader CLS event corpus, measured at the cluster level rather than raw-document level.
**Mechanism (why this should affect memorization)**: Highly salient firms, regulators, and executives accumulate dense parametric traces. When such entities appear, the model has many opportunities to lean on stored associations rather than the present case text. This is not identical to exact article memorization, but it is a plausible driver of inadmissible dependence and a necessary decomposition of the "anchor/searchability" story from R1.
**Category**: economic
**Literature provenance**: Zhou et al. (2023) show entity-level memorization and association recovery. Glasserman & Lin (2024) show named firms can create a distraction effect in financial forecasting, implying entity salience changes how much stored knowledge interferes with text-conditioned judgment.
**Operationalization on CLS + cluster metadata**: Normalize `key_entities` to canonical names/tickers; compute cluster-frequency of each entity across the full benchmark candidate corpus collapsed to one canonical doc per cluster. Case score = max or mean `log1p(cluster_df(entity))` over its top entities.
**Predicted effect direction**: Head-entity cases should show stronger memorization/prior-driven behavior than tail-entity cases, though the mechanism may be broader entity memory rather than exact article memory.
**Data feasibility at 1500 scale**: moderate; depends on entity normalization quality more than compute.
**Coverage estimate**: ~90-95%.
**Failure modes**: Alias resolution is hard in Chinese finance; this factor can capture generic world knowledge rather than CLS-text exposure unless read jointly with duplication and locator specificity.
**Framing support**: both

## Cross-factor interactions
- `duplicate_cluster_size` and `cluster_temporal_span` will correlate. I would keep both initially because they encode different exposure channels: intensity versus persistence. If the shortlist must shrink to 4-6, `cluster_temporal_span` is the first merge/drop candidate.
- `template_rigidity` and `exact-span_rarity` are not redundant. They should often move in opposite directions: boilerplate shell versus idiosyncratic payload. If the MVP needs one surface-form factor only, I would keep `template_rigidity` for broad coverage and retain `exact-span_rarity` as a sensitivity analysis.
- `entity_salience` and `locator_specificity` will partially co-move because specific leads often name prominent firms. They should still be separated: salience is about prior density in the corpus; locator specificity is about whether the current case is uniquely indexed.
- The cleanest interaction to inspect later is `duplicate_cluster_size x exact-span_rarity`. Rare exact spans are only a strong memorization substrate if exposure is nontrivial; otherwise they are just hard text.
- The hardest factors to operationalize cleanly on Chinese financial news are `entity_salience` and `locator_specificity`, mainly because alias normalization is messy: short company names, tickers, exchange suffixes, regulators, and person-title variants. `exact-span_rarity` is the next hardest because Chinese segmentation is unstable and boilerplate numbers with units like `亿`/`万` can create fake rarity.
- The safest, lowest-risk MVP core is: `duplicate_cluster_size`, `cutoff_proximity`, `template_rigidity`, `locator_specificity`, `entity_salience`, with `cluster_temporal_span` and `exact-span_rarity` as the strongest expansion candidates.
