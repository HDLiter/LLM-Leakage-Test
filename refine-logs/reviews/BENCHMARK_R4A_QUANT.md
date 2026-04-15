# BENCHMARK R4 Step 1 — Quant Factor Brainstorm
**Date:** 2026-04-13
**Reviewer:** Codex (senior quantitative researcher persona)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md v2
**Prior rounds:** BENCHMARK_R1/R2/R3_QUANT.md

---

Quant filter: I would only advance factors that vary both likely training exposure and economically meaningful task hardness. The seven strongest axes from that lens are below, plus one extra linguistic axis that is cheap and likely useful.

### Factor: [ALPHA BRIDGE] Primary-Entity Tradability Tier
**Concept**: Ex ante tradability of the cluster's main listed A-share target, proxied by pre-event liquidity. **Mechanism (why this should affect memorization)**: liquid names are the ones that get broader dissemination, more follow-up writing, more recap coverage, and more standardized sell-side / retail discussion; they are also the names where contamination can actually distort rank-based signal selection instead of producing toy "knowledge." **Economic / statistical / linguistic meaning (Decision 10 justification)**: economic; this is a point-in-time proxy for investor attention, dissemination breadth, and executability.

**Operationalization on CLS + market data**: identify a single primary listed company from `key_entities` using headline/lead mention plus mention count; if none or multiple co-primary names, set `NA`. Compute `ADV20_RMB = median(daily_turnover_RMB[t-20:t-1])`; fallback to `float_mcap[t-1]` if ADV is unavailable. Factor value = cross-sectional percentile of `log(ADV20_RMB)` at `first_seen_time - 1 trading day`.

**Predicted effect direction**: memorization should be stronger in high-tradability names because they generate denser repeated exposure and cleaner ex post narrative traces. **Data feasibility at 1500 scale**: easy once entity mapping is stable. **Coverage estimate**: roughly 60-75% of clusters, depending on how many are single-name corporate events.

**Literature provenance**: [Fang & Peress 2009](https://ideas.repec.org/a/bla/jfinan/v64y2009i5p2023-2052.html); [Hirshleifer, Peng, and Wang 2023](https://www.nber.org/papers/w30860). **Failure modes**: multi-entity/policy clusters; manipulated turnover in microcaps; long halts. **Framing support**: both.

### Factor: Event Phase (Rumor vs Official vs Clarification/Recap)
**Concept**: Whether the CLS item is a rumor-phase report, an official disclosure/confirmation, or a clarification/follow-up. **Mechanism**: official items are more formulaic, more widely reprinted, and map to cleaner economic events; rumor-phase items are lexically noisier and often collapse multiple hypotheses into one article. **Meaning**: economic plus linguistic; it changes both the information state of the market and the template regularity of the text.

**Operationalization on CLS + market data**: classify from CLS headline/body using a locked cue list and precedence rule: `official` if it contains disclosure cues like `公告/披露/回复函/签署/审议通过`; `rumor` if it contains `传闻/据悉/市场消息/或将/网传`; `clarification` if `澄清/辟谣/回应传闻`; otherwise `follow_up/recap`. Use manual audit only for low-confidence cases.

**Predicted effect direction**: memorization should be strongest for official and recap items, weakest for rumor-phase items. **Data feasibility**: moderate but very feasible at 1,500 cases. **Coverage estimate**: 85-95%.

**Literature provenance**: novel factor proposal; I do not know a clean memorization-paper precedent, but the distinction is economically load-bearing and textually operational. **Failure modes**: articles that mix rumor and confirmation in one piece; euphemistic wording by media desks. **Framing support**: both.

### Factor: Session Timing / Attention Window
**Concept**: Release timing relative to the A-share trading session. **Mechanism**: post-close and pre-open items tend to have cleaner mapping into the next tradeable window and often correspond to formal disclosures; intraday items are mixed with contemporaneous order flow and competing news. **Meaning**: economic; this is a point-in-time market-mechanics variable, not a vague "attention" label.

**Operationalization on CLS + market data**: bucket `first_seen_time` into `pre_open`, `continuous_intraday`, `post_close`, and `non_trading_day`. Use the exchange calendar to map weekends/holidays.

**Predicted effect direction**: stronger memorization for `post_close` and `pre_open`, weaker for `continuous_intraday`. **Data feasibility**: trivial. **Coverage estimate**: 95%+ if timestamps are normalized.

**Literature provenance**: [DellaVigna & Pollet 2009](https://www.nber.org/papers/w11683). **Failure modes**: date-only timestamps; clusters where `first_seen_time` lags the actual economic event. **Framing support**: substrate.

### Factor: Standardized Surprise Magnitude
**Concept**: Realized abnormal move size relative to pre-event volatility. **Mechanism**: large standardized surprises get more investor attention, more follow-up commentary, and more recap-style restatement; they also create cleaner labels, which increases the odds that memorized outcome knowledge is useful. **Meaning**: statistical plus economic; it measures event shock size in units the market actually cares about.

**Operationalization on CLS + market data**: for each benchmark horizon `H`, compute `surprise_H = |outcome.magnitude(H)| / sigma_pre(H)`, where `sigma_pre(H)` is the trailing 20-day daily excess-return volatility scaled to horizon `H` on the same benchmark basis as the outcome.

**Predicted effect direction**: memorization should be stronger in high-`surprise_H` bins. **Data feasibility**: straightforward for single-name tradable cases. **Coverage estimate**: about 65-80%.

**Literature provenance**: [Barber & Odean 2008](https://academic.oup.com/rfs/article-lookup/doi/10.1093/rfs/hhm079). **Failure modes**: limit-up/down, halts, and benchmark mismatch can distort measured shock size. **Framing support**: both.

### Factor: Outcome Materialization Lag
**Concept**: How fast the event's economic effect becomes visible in returns. **Mechanism**: fast-materializing events generate a crisp outcome narrative that later text can summarize and models can memorize; slow-burn events are more confounded by subsequent news and are harder to compress into a stable "this event caused that move" pattern. **Meaning**: economic; it is a direct property of price-discovery speed.

**Operationalization on CLS + market data**: compute post-event cumulative abnormal return `CAR_t` for trading days `t=1..22`. Define `lag_to_80 = min t such that |CAR_t| >= 0.8 * max_{s<=22}|CAR_s|`; if never reached, use the day of peak absolute `CAR`. Bin into early / medium / slow after empirical cutpoints are computed.

**Predicted effect direction**: stronger memorization when `lag_to_80` is short. **Data feasibility**: easy once abnormal-return legs are in place. **Coverage estimate**: similar to surprise magnitude, roughly 65-80%.

**Literature provenance**: [Hong & Stein 1999](https://ideas.repec.org/a/bla/jfinan/v54y1999i6p2143-2184.html); [DellaVigna & Pollet 2009](https://www.nber.org/papers/w11683). **Failure modes**: overlapping later events, suspended trading, and multi-stage corporate actions. **Framing support**: both.

### Factor: Structured Event Type
**Concept**: Top-level economic event family of the CLS cluster. **Mechanism**: some event classes are highly templated and recur with stable lexical patterns and relatively stable market semantics; others are diffuse narrative commentary. That should change memorization susceptibility materially. **Meaning**: economic plus linguistic; it partitions cases by the underlying data-generating process, not by a vague "importance" notion.

**Operationalization on CLS + market data**: assign one locked primary label per cluster from a small fixed set such as `earnings/guidance`, `capital_action_M&A_restructuring`, `order_product_operations`, `policy_regulation`, `litigation_compliance`, `macro_industry_commentary`, `other`, using keyword rules plus entity context and manual audit of edge cases.

**Predicted effect direction**: stronger memorization for highly standardized corporate event types, weaker for macro/industry commentary. **Data feasibility**: very feasible at 1,500 cases. **Coverage estimate**: 90%+.

**Literature provenance**: [Zhou, Ma, and Liu 2021](https://arxiv.org/abs/2105.12825). **Failure modes**: mixed-event stories and overly fine labels that create sparse cells. **Framing support**: taxonomy.

### Factor: Corpus Repetition Load
**Concept**: How often the same economic signal is repeated in the corpus, both within the duplicate cluster and across prior same-family clusters. **Mechanism**: repetition is the cleanest known driver of memorization in language models; in finance specifically, stale or reprinted news also creates predictable overreaction / reversal patterns, so this factor has both NLP and market meaning. **Meaning**: statistical plus linguistic; it measures exposure multiplicity.

**Operationalization on CLS + market data**: define `repetition_load = log(1 + duplicate_cluster_size) + log(1 + prior_family_count_365d)`, where `prior_family_count_365d` counts earlier clusters sharing `(event_type, primary_entity_id)` for company events or `(event_type, sector/policy topic)` for non-single-name events.

**Predicted effect direction**: memorization should be strongest in high-repetition-load cases. **Data feasibility**: easy once event type is assigned. **Coverage estimate**: 100% with the `duplicate_cluster_size` term alone; 85%+ for the full score.

**Literature provenance**: [Tetlock 2011](https://academic.oup.com/rfs/article-abstract/24/5/1481/1613314); [Lee et al. 2021](https://arxiv.org/abs/2107.06499); [Carlini et al. 2022](https://arxiv.org/abs/2202.07646). **Failure modes**: cluster overmerge/undermerge; syndicated reposts may overstate true pretraining duplication. **Framing support**: both.

### Factor: Lexical Anchor Density
**Concept**: Density of unique identifiers in the CLS headline and lead. **Mechanism**: names, tickers, dates, percentages, prices, and amounts are the tokens that pin an article to a specific event instance; memorization work suggests nouns and numbers are learned early and act as retrieval anchors. **Meaning**: linguistic; this is a concrete article-level identifiability measure, not a hand-wavy "memorability" score.

**Operationalization on CLS + market data**: in the headline plus first 120 Chinese characters, count anchor tokens from four locked classes: `entity aliases from key_entities`, `security codes`, `dates/times`, and `unit-bearing numerics` (`%`, `亿元`, `万股`, price levels, EPS figures). Factor value = anchor-token count divided by total tokens in the same window.

**Predicted effect direction**: stronger memorization in high-anchor-density text. **Data feasibility**: trivial. **Coverage estimate**: effectively 100%.

**Literature provenance**: [Tirumala et al. 2022](https://arxiv.org/abs/2205.10770). **Failure modes**: boilerplate disclosures full of numbers but little unique economics; alias normalization errors. **Framing support**: taxonomy.

**Cross-factor interactions**
- `Primary-Entity Tradability Tier`, `Corpus Repetition Load`, and `Lexical Anchor Density` will be positively correlated. Large liquid names are written more explicitly and echoed more often.
- `Event Phase` and `Session Timing` will also correlate. Official disclosures disproportionately cluster post-close / pre-open; rumor pieces skew intraday.
- `Structured Event Type` is partly upstream of both `Outcome Materialization Lag` and `Standardized Surprise Magnitude`. That is fine; they are not duplicates because type says what happened, while lag and surprise say how the market processed it.
- If the shortlist must be cut hard, I would merge only after seeing pilot sparsity. The nearest pair is `Event Phase` with `Session Timing`; the rest are meaningfully distinct.

**Sources**
- [Fang & Peress 2009, Media Coverage and the Cross-Section of Stock Returns](https://ideas.repec.org/a/bla/jfinan/v64y2009i5p2023-2052.html)
- [Hirshleifer, Peng, and Wang 2023, News Diffusion in Social Networks and Stock Market Reactions](https://www.nber.org/papers/w30860)
- [DellaVigna & Pollet 2009, Investor Inattention and Friday Earnings Announcements](https://www.nber.org/papers/w11683)
- [Barber & Odean 2008, All That Glitters](https://academic.oup.com/rfs/article-lookup/doi/10.1093/rfs/hhm079)
- [Hong & Stein 1999, A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets](https://ideas.repec.org/a/bla/jfinan/v54y1999i6p2143-2184.html)
- [Zhou, Ma, and Liu 2021, Trade the Event](https://arxiv.org/abs/2105.12825)
- [Tetlock 2011, All the News That's Fit to Reprint](https://academic.oup.com/rfs/article-abstract/24/5/1481/1613314)
- [Lee et al. 2021, Deduplicating Training Data Makes Language Models Better](https://arxiv.org/abs/2107.06499)
- [Carlini et al. 2022, Quantifying Memorization Across Neural Language Models](https://arxiv.org/abs/2202.07646)
- [Tirumala et al. 2022, Memorization Without Overfitting](https://arxiv.org/abs/2205.10770)
