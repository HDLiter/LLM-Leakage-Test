> **Status (2026-04-16, post-R5A-freeze)**: Reserve-factor feasibility memo. **Coverage Breadth is NOT in the frozen confirmatory family** (see `R5A_FROZEN_SHORTLIST.md`); this document analyzes whether it could be promoted later. Drop "13th active factor" reading. Sample size reference: 3,200 gross / 2,560 scorable (not 3,200 alone).

# Media Coverage Factor — Feasibility Analysis

**Date:** 2026-04-14
**Status:** DECISION SUPPORT — user gated promotion of Coverage Breadth on this analysis
**Context:** R4 literature sweep candidate new-factor queue Q1

## 1. What Propagation Intensity already measures (and what Media Coverage needs to add)

- `cluster_size` / `event_burst` is **same-event duplication inside CLS**: how many CLS items cover the same cluster.
- `prior_family_count_365d` / `historical_family_recurrence` is **same-family recurrence inside CLS**: how often similar event families occurred in the prior year.
- `surface_template_recurrence` is **surface-form reuse inside CLS**: char-5gram TF-IDF similarity to prior CLS canonicals or prior CLS articles.

- None of the three signals measures **whether publishers outside CLS also covered the event**.
- That is the gap. Propagation Intensity is a **CLS-internal exposure proxy**. Media Coverage must add an **outside-CLS breadth signal**.

- Construct target:
  - **Coverage Breadth = number of distinct publishers outside CLS that covered the same event within a fixed post-event window.**
  - Recommended operational field name: `coverage_breadth_3d`.
  - Recommended default window: `[t0 - 12h, t0 + 72h]`, where `t0` is the canonical CLS timestamp.
  - Recommended robustness companion: `coverage_breadth_7d`.

- Distinct from:
  - **Volume**: CLS article count on the event.
  - **Template reuse**: CLS surface duplication / boilerplate.
  - **Tradability**: market attention proxy from liquidity/size, not news-ecosystem breadth.

## 2. Data source options

### Option A — Commercial news aggregator API

#### A1. Tushare Pro news feeds

- What you get:
  - `news` (short news): official docs say it provides “主流新闻网站的快讯新闻数据” with **6+ years** of history, max **1,500** rows per call, source code required (`sina`, `wallstreetcn`, `10jqka`, `eastmoney`, `yuncaijing`, `fenghuang`, `jinrongjie`, `cls`, `yicai`). Source: Tushare docs `doc_id=143`.
  - `major_news` (long-form): official docs say it provides **8+ years** of long-form news, max **400** rows per call, source filter among `新华网、凤凰财经、同花顺、新浪财经、华尔街见闻、中证网、财新网、第一财经、财联社`. Source: Tushare docs `doc_id=195`.
  - Tushare permissions docs classify news/announcements as **separately licensed interfaces**, not ordinary point-threshold data. Source: Tushare permissions `doc_id=290`.
- Access cost:
  - Public docs confirm separate licensing, but I did **not** verify a public posted price for the news modules.
  - If the user already has the relevant permission, marginal cash cost is low; otherwise access is procurement/permission friction, not a transparent self-serve SKU.
- Reliability:
  - **Moderate** as an acquisition layer.
  - Good timestamp coverage.
  - Weak point: the docs clearly define source feeds, but do not publicly document a rich original-publisher schema. Without article-level original-source attribution, `news` is closer to **feed breadth** than true **publisher breadth**.
- Reproducibility risk:
  - **Medium to high** if used live.
  - Drops to **medium** if you freeze all response dumps used for each cluster and release the matching code plus evidence table.
- Legal/ethical concerns:
  - Internal research use is cleaner than scraping.
  - Public redistribution of raw full text is likely constrained by vendor/license terms; assume **artifact-release restrictions** unless confirmed otherwise.

#### A2. Wind / Choice enterprise terminals and APIs

- What you get:
  - In practice these are the strongest Chinese institutional news products for timestamped, source-attributed financial news.
  - Choice’s official terminal guide visibly includes an `资讯` section; Wind’s public platform materials indicate news/media data products exist. Public product materials are easy to find; detailed field docs and pricing are not.
- Access cost:
  - **Enterprise-sales / institutional license**. I did **not** verify a public posted price.
  - Procurement, seat/API entitlement, and legal review are the real costs.
- Reliability:
  - **High** if the institution already licenses the module.
  - Better source normalization and archive continuity than portal scraping.
- Reproducibility risk:
  - **Medium** internally.
  - **High** for public peer review unless reviewers also have license access or you release frozen evidence dumps.
- Legal/ethical concerns:
  - Lower operational risk than scraping.
  - Higher redistribution restrictions than public-web sources.

#### A3. QKL123 / 聚合数据 / generic commercial content APIs

- What you get:
  - Usually narrower domain coverage or generic portal aggregation.
  - QKL123 is crypto-focused and is a poor fit for CLS A-share / macro / policy coverage.
  - Generic API marketplaces often expose snippets but weak provenance.
- Access cost:
  - Often cheaper than Wind/Choice, but you pay with poorer source semantics.
- Reliability:
  - **Low to moderate** for this benchmark.
- Reproducibility risk:
  - **High** unless the source universe is frozen and documented.
- Legal/ethical concerns:
  - Varies by reseller chain; provenance can be murky.

### Option B — Free financial portal scraping

- Candidates:
  - Heavy portals / aggregators: 东方财富, 同花顺, 新浪财经, 网易财经, 腾讯财经, 金融界, 和讯.
  - More original financial publishers: 证券时报网, 上海证券报网, 中国证券报, 21世纪经济报道, 第一财经, 财新.

- What you get:
  - Large historical archives and visible timestamps.
  - Often some source attribution in page text.
- Access cost:
  - Cash-light, engineering-heavy.
  - Real cost is crawler maintenance, anti-bot handling, HTML drift, and source normalization.
- Reliability:
  - **Low to moderate**.
  - Counting portal domains is the wrong construct because portals syndicate heavily. “Same Xinhua story on Sina + Eastmoney + 10jqka” is not three original publishers.
  - To make scraping usable, you must count **normalized original source** when exposed, not portal host.
- Reproducibility risk:
  - **High** unless you snapshot fetched pages or at least metadata/title/source fields.
- Legal/ethical concerns:
  - Highest risk in the option set.
  - Many sites do not welcome bulk archive scraping; robots/TOS friction is likely.

### Option C — Search engine hit count via API

#### C1. Bing Search API

- What you get:
  - Official Azure pricing page still exposes Bing Search V7 bundles. Public pricing shown on the page includes **$7 per 25,000 transactions** for S1 and **$3 per 10,000 transactions** for S2; Bing News Search is included in relevant tiers.
- Access cost:
  - Cheap in API-call terms.
  - At 3,200 clusters and even 3 queries per cluster, raw API spend is trivial.
- Reliability:
  - **Poor for factor construction**.
  - Search engines are rankers, not archives; result sets shift over time, dedupe rules are opaque, and “hit count” is not a stable scientific measure.
- Reproducibility risk:
  - **Very high** if live.
  - Freezing JSON helps, but then the factor is really “Bing result breadth on date X,” not “media coverage.”
- Legal/ethical concerns:
  - Fine operationally.
  - Methodologically weak.

#### C2. Baidu / Sogou search APIs

- What you get:
  - Baidu’s 2025 public AI Search announcement says the API can return source-linked web results with filters and traceable source links.
  - I did **not** verify a stable, public, reviewer-friendly “historical hit count” interface.
  - I did **not** verify a current public general-web search API from Sogou suitable for this use.
- Access cost:
  - Unknown from the public materials reviewed.
- Reliability:
  - Better than ad hoc scraping for retrieval.
  - Still **not good enough** as the factor itself because result counts and ranking change.
- Reproducibility risk:
  - **High**.
- Legal/ethical concerns:
  - Lower than scraping, but still not a clean scientific count.

### Option D — Social media / public-figure coverage

- Candidates:
  - 微博, 今日头条, 雪球.
- What you get:
  - Social attention / discussion, not publisher coverage.
- Access cost:
  - API restrictions and anti-automation friction are the norm.
- Reliability:
  - **Poor for this construct**.
  - A niche rumor with huge Xueqiu discussion is not “broad media coverage.”
- Reproducibility risk:
  - **Very high** because historical search behavior changes and access is unstable.
- Legal/ethical concerns:
  - Elevated, especially for scraping.

### Option E — Pre-existing research datasets

- Candidates:
  - CSMAR news modules, RESSET news modules, possibly other institutional Chinese finance databases.
- What you get:
  - Potentially the cleanest source-attributed historical news archives after Wind/Choice.
  - Often better for research auditability inside licensed institutions than retail APIs.
- Access cost:
  - Institutional license or library procurement.
  - Public field-level documentation is sparse; I did **not** verify module-specific pricing or exact field coverage from public sources.
- Reliability:
  - Likely **high** if the right module is already licensed.
- Reproducibility risk:
  - **Medium internally**, **high externally** because reviewers may lack the same license.
- Legal/ethical concerns:
  - Redistribution constraints likely.

### Option F — LLM-as-feature: query a search engine via an LLM agent

- What you get:
  - An estimated count or narrative answer.
- Access cost:
  - Low to moderate API spend.
- Reliability:
  - **Unacceptable** for benchmark factor construction.
- Reproducibility risk:
  - **Extreme**.
- Legal/ethical concerns:
  - Secondary. The methodological problem is primary.

### Option G — Entity mention count on external corpus

- Approach:
  - Build a **frozen external coverage index** from a defined source universe at benchmark-freeze time.
  - Match each CLS cluster to that frozen external index.
  - Count **distinct normalized publishers** outside CLS in a fixed window.
- What you get:
  - The cleanest operational form of the intended construct.
- Access cost:
  - Moderate engineering plus either vendor access or one-time archive collection.
- Reliability:
  - **Best option** if the source universe and matching rule are explicit.
- Reproducibility risk:
  - **Manageable** if you freeze evidence dumps and release the matching artifacts.
- Legal/ethical concerns:
  - Depends entirely on the acquisition layer.
  - Better with licensed APIs than with scraping.

## 3. Matching problem

The matching problem is the real bottleneck. Cross-publisher coverage is only useful if “same event” is defined tightly enough.

- Exact-text match:
  - High precision, very low recall.
  - Catches reposts and near-reposts only.
- Entity + time window:
  - Better recall, but false positives are substantial for repeat-heavy names (`宁德时代`, `证监会`, `央行`) and for firms with multiple same-week events.
- Entity + time + event type:
  - Better, but this drags in the Thales taxonomy or another event classifier, which the user explicitly does not want as a dependency for this factor.
- Embedding nearest neighbor:
  - Expensive, threshold-sensitive, and hard to defend in 2028 review.
- Cross-corpus clustering:
  - Scientifically appealing, but too much pipeline for a single auxiliary factor.

### Recommended matching rule

Use a **deterministic, high-precision, non-Thales rule** against a frozen external index.

For each canonical CLS case:

1. Define `t0` = canonical CLS timestamp.
2. Build a query key from the CLS case:
   - normalized title
   - first sentence / lead
   - 1-2 anchor entity strings if obvious from the title
   - strongest trigger phrase if obvious from the title (`回购`, `减持`, `停牌`, `立案`, `签署合同`, `业绩预增`, `发行`, `并购`, `处罚`, etc.)
3. Retrieve external candidates from the frozen index in `[t0 - 12h, t0 + 72h]`.
4. Count publisher `p` as covering the event if **any** article from `p` satisfies:
   - same time window, and
   - either:
     - exact normalized title match, or
     - high normalized title similarity, or
     - shared anchor entity + shared trigger phrase + one matching numeric anchor if the event has a salient number.
5. Collapse multiple matches from the same publisher to **1**.
6. Exclude CLS itself.
7. Store confidence flags:
   - `high_confidence_match`
   - `publisher_attribution_quality`
   - `used_numeric_anchor`

### Why this rule is defensible

- It is **deterministic**.
- It uses only the benchmark case text/time as retrieval seed, not CLS statistics.
- It avoids detector dependence.
- It avoids Thales dependence.
- It is calibrated for **precision first**, which is the right bias for a breadth factor. Missing a marginal publisher is less harmful than falsely inflating breadth.

### What not to do

- Do not use live search-engine hit counts as the factor.
- Do not count portal hosts when the page is clearly a syndication shell.
- Do not require a full cross-corpus clustering pipeline.
- Do not use LLM “same event?” judgments as the primary decision rule.

## 4. Cost model for the best candidate

### Best candidate: Option G with Option A/E as acquisition layer

**Definition of “best candidate” here:** a frozen external coverage index, populated from an already-licensed source if possible, then matched with the deterministic rule above.

### Candidate 1 — Tushare-backed frozen coverage index

- Setup cost:
  - Acquire/confirm Tushare news permissions.
  - Pull response windows for sampled clusters from `news` and/or `major_news`.
  - Normalize source names.
  - Estimated engineering time: **16-32 person-hours**.
  - Public posted module price: **not verified** from the public docs reviewed.
- Per-cluster cost:
  - 1 retrieval pass over a narrow time window.
  - CPU-only matching.
  - Optional manual QA only for low-confidence cases.
  - Estimated analyst time: **15-45 seconds per ambiguous cluster** if ~10-15% require review.
- Total cost at `N = 3,200`:
  - API calls: bounded and operationally small; even cluster-by-cluster window queries are tractable.
  - Engineering + QA: **24-48 person-hours** total.
  - Cash cost: **near-zero marginal** if the user’s Tushare entitlement already covers the needed feeds; otherwise separate license cost is unknown from public docs.
- Latency:
  - **2-5 working days** after access is confirmed.

### Candidate 2 — Institutional database export (Wind / Choice / CSMAR / RESSET)

- Setup cost:
  - Procurement / entitlement dominates if not already licensed.
  - Once accessible, engineering is straightforward.
  - Estimated engineering + QA: **20-40 person-hours**.
- Per-cluster cost:
  - Low.
  - Search-by-date/source/title workflows are mature in these systems.
- Total cost at `N = 3,200`:
  - Cash cost: **unknown / procurement-driven**.
  - Person-hours similar to Candidate 1 or slightly lower after access.
- Latency:
  - **Fast if already licensed**.
  - **Potentially weeks** if procurement is needed.

### Why free scraping is not the best candidate

- Engineering cost is materially higher: **60-120 person-hours** is realistic once anti-bot, markup drift, source normalization, and archive inconsistencies are included.
- Legal/release risk is worse.
- It buys less reproducibility than a frozen vendor-backed response dump.

## 5. Reproducibility analysis

For the best candidate, a 2028 reviewer needs enough material to verify **methodology** completely and **counts** either directly or via licensed re-run.

### Required released artifacts

- Matching specification:
  - window rule
  - normalization rules
  - trigger lexicon
  - numeric-anchor rule
  - publisher normalization dictionary
- Per-cluster evidence table:
  - `cluster_id`
  - canonical CLS timestamp
  - external source platform
  - normalized publisher ID
  - external article timestamp
  - article title or title hash
  - match features
  - final count decision
- Frozen response dumps:
  - preferably all candidate articles returned for each cluster window
  - if raw text cannot be released, at minimum release title hashes + timestamps + source metadata + match features

### Cost of artifact release

- Storage:
  - Metadata-only release is small.
  - Full candidate-response dumps for ~3,200 clusters are still operationally modest, likely **sub-GB to low-GB**, not a big infrastructure problem.
- Legal:
  - This is the real problem.
  - Vendor terms may block raw-text redistribution even if storage cost is trivial.

### Comparison with Tradability Tier

- Tradability Tier is easy:
  - deterministic
  - market-data-based
  - easy for reviewers to reproduce
- Media Coverage is harder:
  - it requires an external content source
  - a matching rule
  - a releasable evidence pack

### Reproducibility verdict

- **Methodology reproducibility:** achievable.
- **Count reproducibility:** achievable only if the team freezes and releases the evidence pack, or if reviewers can access the same vendor/database.
- Net result: **medium reproducibility**, clearly worse than Tradability Tier, but much better than search-engine hit counts or LLM estimates.

## 6. Overlap with Propagation Intensity, Tradability, Authority

- Expected correlation with `cluster_size`:
  - **Moderate positive**, not perfect.
  - Big listed-firm and policy shocks should rise on both.
  - But CLS can over-cover some finance-native microstructure items that broader media barely touch; those cases are exactly where the factor adds value.

- Expected correlation with Tradability Tier:
  - **Moderate to high** for company-targeted events.
  - **Low to moderate** for macro, policy, legal, and regulator events.

- Expected correlation with Authority:
  - **Moderate** if high-authority sources trigger wider republication.
  - Not identity-level unless Coverage Breadth is badly operationalized as “was Xinhua involved.”

- Would the factor survive joint modeling?
  - **Yes, if** it is counted as outside-CLS distinct publisher breadth and not as portal duplication.
  - **No, if** it degenerates into “how many portal feeds reposted the same wire” or “how many CLS-like sites copied the headline.”

## 7. P1 restoration verdict

- Pure extra-corpus under Principle P1 means the **value itself** cannot depend on CLS statistics such as `cluster_size`, CLS recurrence counts, or CLS template counts.
- Using the CLS canonical article as the **event anchor** does **not** violate P1.
- Boundary:
  - acceptable: “use the CLS canonical case to identify what event to look for externally, then count only external publishers”
  - not acceptable: “use CLS cluster size or CLS salience to scale or threshold the count”

### Verdict

**Yes — if operationalized as an external publisher count, Coverage Breadth qualifies as pure extra-corpus for P1.**

It is better described as a **case-anchored extra-corpus factor** than a corpus-global factor, but that still satisfies the principle. The value is produced from outside-CLS evidence only.

## 8. Alternative operationalizations

### Fallback 1 — Baidu Index / search-interest proxy

- Tradeoff:
  - Cheap and extra-corpus.
  - Measures **public search interest**, not publisher breadth.
  - Better proxy for “attention” than for “coverage.”

### Fallback 2 — Frozen Wikipedia / encyclopedia prominence proxy

- Tradeoff:
  - Very reproducible.
  - Too static and too entity-level.
  - Fails the event-specific construct.

### Fallback 3 — Tushare feed-count proxy

- Definition:
  - count how many non-CLS Tushare source feeds carried a matched item in the window.
- Tradeoff:
  - Operationally easy.
  - More reproducible than scraping.
  - But closer to **feed breadth** than true **publisher breadth** unless article-level original-source attribution is available.

### Fallback 4 — Licensed institutional database coverage metadata

- Definition:
  - use Wind/Choice/CSMAR/RESSET source counts if the database already exposes normalized source metadata.
- Tradeoff:
  - Strongest direct proxy to the intended construct.
  - Weak public reproducibility because reviewers may lack license access.

### Fallback 5 — LLM-based coverage estimation

- Tradeoff:
  - Fastest to prototype.
  - Worst reproducibility and weakest auditability.
  - Not acceptable for a benchmark factor unless demoted to exploratory notes only.

## 9. Feasibility verdict

**FEASIBLE BUT EXPENSIVE**

Direct cross-publisher Coverage Breadth is operationally feasible if the team defines it as **distinct outside-CLS publishers in a frozen external coverage index** and is willing to freeze/release an evidence pack. The bounded cash cost can be low if an existing licensed source is used, but the real cost is methodological: source normalization, deterministic matching, and reviewer-auditable artifact release are substantially heavier than Tradability Tier, so this should not be promoted casually.

### Concrete next step for each option

- Option A / G hybrid:
  - Run a **100-cluster feasibility pilot** on a frozen external coverage index.
  - Success criterion: high-confidence publisher attribution on most matched cases and clear separation between obviously broad and obviously niche events.
- Option E:
  - If the institution already has Wind/Choice/CSMAR/RESSET access, compare one licensed source against the Tushare pilot and prefer whichever has cleaner original-source metadata.
- Option B:
  - Do **not** make scraping the primary plan.
  - Use only if licensed sources fail and the team explicitly accepts legal/release burden.
- Option C:
  - Use search APIs only as retrieval support for ambiguous cases, not as the factor.
- Option D:
  - Drop for this factor.
- Option F:
  - Drop for production-quality benchmarking.

## 10. Recommendation to the user

- Do **not** promote Coverage Breadth immediately as a 13th active factor. Keep it gated and require a **100-cluster external-coverage pilot** with frozen evidence dumps before any promotion decision.
- R5 should assume Media Coverage is **not yet available** as a production factor, but should expect that a successful pilot could restore P1 headroom as a second pure extra-corpus factor.
- In decision-doc v6 language, the most that should be added is an explicit operational note: Coverage Breadth is feasible **only** as a frozen external publisher-count factor with deterministic matching and artifact release; it is not a live search-hit count feature.

## Selected public source notes

- Tushare `news` docs: <https://tushare.pro/document/2?doc_id=143>
- Tushare `major_news` docs: <https://tushare.pro/document/2?doc_id=195>
- Tushare permissions model: <https://tushare.pro/document/1?doc_id=290>
- Choice official terminal guide PDF: <https://choice.eastmoney.com/FileDownload/CFTG20210201.pdf>
- Wind public product page example: <https://share.wind.com.cn/?path=%2Fmall%2Fgoods%2F718%2F3358>
- Azure Bing Search pricing page: <https://azure.microsoft.com/en-us/pricing/details/cognitive-services/spellcheck-api/>
- Baidu AI Search API announcement: <https://qianfan.cloud.baidu.com/qianfandev/topic/686085>
