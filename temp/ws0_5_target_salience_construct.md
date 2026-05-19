# WS0.5 Target Salience Construct Design

**Analyst**: GPT-5.4 xhigh via Codex CLI
**Date**: 2026-05-18
**Question**: How to operationalize Target Salience (Bloc 2 confirmatory factor) for R5A pilot

## 1. Target selection rule

Target selection is a manifest-freeze operation, not an operator-time LLM task. `P_predict` receives the selected `target` and `target_type`; the model must only echo and predict for that pair. Therefore the selection rule should be deterministic after the WS0.5 factor pipeline has produced a frozen `salient_entities[]` table.

### Step-by-step procedure

Inputs:

- `article.content`
- `headline`: text inside the first `【...】` block, or `title` if a separate title field exists
- frozen `salient_entities[]`: `value`, `type`, `salience`
- optional Scheme A metadata: ticker/listed flag, market cap bucket, broad-index membership, known-core-institution list, industry taxonomy

Target type mapping for the R5A operator:

| Thales / derived type | `P_predict.target_type` | Notes |
|---|---:|---|
| `company` | `company` | Use the Chinese common company name as `target`; store ticker as sidecar metadata. |
| named index / ETF / benchmark instrument (`etf` in current Thales vocab) | `index` | Use `index` for specific named market indices and index-like tradeable baskets. |
| `industry`, tradeable `concept`, commodity/product market theme | `sector` | Includes broker-recognized themes and formal sectors. |
| `institution`, `region`, central-bank/regulator/policy macro object | `macro` | For policy and macro news with no cleaner tradeable target. |
| one-off `event`, `policy_document`, nonmarket `product`, residual | `other` | Allowed only when it is the article's principal forecast object and no better market/macro target exists. |

Selection priority:

1. Build candidate pool from all `salient_entities` where `salience == core`.
2. Add `supporting` entities only when all core entities are source/person/authority wrappers and the supporting entity is in the headline or is the unique market object of the news.
3. Drop candidates that are pure attribution sources, unless the source itself is the affected market subject:
   - Drop `中信建投` in `中信建投：消费税改革有望利好免税价差` if a core market object appears after the colon.
   - Keep `步步高` in `步步高：年度权益分派...` because the company is the issuer and the security target.
4. Drop standalone persons unless they are the only principal subject and no represented institution/region is extractable. If a represented institution/region is explicit, select that instead of the person.
5. Rank remaining candidates by target class:
   - direct security / index target: listed company, ETF, named benchmark index
   - market object: formal sector, industry, tradeable concept, commodity or product market
   - macro actor/object: central bank, regulator, ministry, country/region, broad market segment
   - residual principal object: event, policy document, product, business segment
6. Within the highest available class, prefer:
   - `core` over `supporting`
   - headline exact match over body-only match
   - transaction/control-change object over transaction actor when a simple pattern identifies it, for example `A 入股 B`, `A 收购 B`, `A 成为 B 第一大股东`
   - explicit named instrument/index over generic sector
   - earliest headline occurrence
   - longer unambiguous alias over one-character country aliases such as `中` or `俄`
7. If the selected target is a listed company and a ticker is available, store `target_ticker` as metadata but keep `target` as the readable entity name unless the source article itself uses only the ticker.
8. Record `target_selection_confidence`:
   - `high`: one dominant core target
   - `medium`: deterministic tie-break used among two plausible targets
   - `low`: supporting fallback or multi-target article without an aggregate target

Pseudocode:

```python
def select_target(article, salient_entities, metadata):
    headline = extract_cls_headline(article)
    core = [e for e in salient_entities if e.salience == "core"]
    supporting = [e for e in salient_entities if e.salience == "supporting"]

    candidates = []
    for e in core:
        if is_pure_person(e, salient_entities):
            continue
        if is_source_only_company_or_institution(e, headline, salient_entities):
            continue
        if is_one_char_region_alias(e) and has_full_region_alias(e, salient_entities):
            continue
        candidates.append(enrich_candidate(e, article, headline, metadata))

    if not candidates:
        for e in supporting:
            if is_unique_headline_or_market_object(e, article, headline, core):
                candidates.append(enrich_candidate(e, article, headline, metadata))

    if not candidates:
        return NullTarget(reason="no_eligible_forecast_target")

    for c in candidates:
        c.rank = (
            target_class_rank(c),
            c.entity_salience == "core",
            c.in_headline,
            transaction_object_bonus(c, headline),
            instrument_specificity(c),
            -headline_offset(c),
            alias_quality(c),
        )

    selected = max(candidates, key=lambda c: c.rank)
    return Target(
        target=selected.display_name,
        target_type=map_target_type(selected),
        target_source_entity=selected.value,
        target_selection_confidence=confidence(selected, candidates),
        sidecar_metadata=selected.metadata,
    )
```

### Nullability rule

Final pilot manifests should not contain null targets for `P_predict` rows. Null targets are a sampling-stage rejection signal.

Mark `target_status = null_no_eligible_target` and replace the case before manifest freeze when:

- no core or admissible supporting entity can serve as a market, sector, index, macro, or residual forecast target
- the only extracted entities are persons with no explicit represented institution/region
- the article is a catalog/listing item where no single target or aggregate target is load-bearing
- target choice remains ambiguous after deterministic tie-break and no aggregate sector/index target is present
- the chosen target would not appear in the article through either exact string or a documented alias

If replacement is impossible, keep the case out of confirmatory `P_predict` estimands and document the missingness. Do not invent a target to preserve sample size.

### Examples on 5 ambiguous CLS patterns

1. Policy news with `央行` plus several companies: select the affected sector/theme if it is the headline market object, for example `银行板块`. If the news is only a policy action and no market object is named, select the policy institution or macro object, for example `央行`, with `target_type = macro`. Body-listed companies are not selected unless one is directly acted on.

2. Broker research, for example `中信建投：消费税改革 有望利好免税价差`: treat `中信建投` as source-only. Select `免税价差` or the closest headline market object, with `target_type = sector`.

3. Multi-company capital action, for example `中国人寿有意成为万达信息第一大股东`: both companies may be core, but the control-change object is the more direct security target. Select `万达信息` if the pattern is recognized; otherwise choose earliest headline core company and flag `target_selection_confidence = medium`.

4. Industry report listing many companies: if a core umbrella sector/theme exists, select the umbrella target. If no umbrella exists and the headline enumerates two to three companies as the news lead, select the first headline company and flag medium confidence. If the list is a catalog tail, reject or send to adjudication.

5. Geopolitical/macropolicy news with countries and officials: avoid selecting the person. If an official institution is the actor, select it, for example `外交部`; if the article is about a broad market, select the market object, for example `美股` or `A股`; otherwise select the represented region/macro actor with `target_type = macro`.

## 2. Ordinal salience scoring

### Recommended ordinal levels and operational criteria

Use **3 ordinal levels** for the pilot:

- `1 = low`: idiosyncratic or narrow target
- `2 = medium`: recognized market target
- `3 = high`: systemic/high-coverage target

Why 3 levels:

- It preserves the intended high-vs-low training-exposure contrast while allowing a middle category for ordinary listed companies and common sectors.
- It matches the Phase 7 expectation that factors may start as tertiles and collapse to binary if `n_eff < 15`.
- Four or five levels would create thin cells for `E_CMMD` and the perturbation-eligible subsets; two levels would be safer but would lose a useful dose-response check.

Scheme A scoring uses a small scorecard, but the level is not a pure text salience score. Text signals are only a centrality gate.

Hard fields:

- selected `target`, `target_type`, source entity `type`, source entity `salience`
- exact or alias match in headline/body
- first character offset and mention count
- source-only / person-only exclusion flags
- for company targets under Scheme A: ticker/listed flag, market-cap bucket or broad-index membership
- for macro/institution targets: frozen known-core-institution and broad-region list

Optional enrichment:

- company age/listing age
- Shenwan/CSRC industry classification
- ticker/code mention in article
- dual-agent label agreement or adjudication flag

Operational rule:

| Component | Value | Definition |
|---|---:|---|
| `context_gate = 2` | central | target source entity is `core` and appears in headline or title alias |
| `context_gate = 1` | admissible | target is `core` body-only, or a headline `supporting` fallback selected by rule |
| `context_gate = 0` | weak | target is supporting/body-only or alias evidence is weak |
| `static_reach = 3` | high reach | benchmark index/broad market, SSE50/CSI300/top-cap listed company, nationally dominant sector, central bank/regulator/state ministry, major country/region |
| `static_reach = 2` | medium reach | ordinary listed company, recognized sector/theme/commodity, specific ETF/fund/index product, provincial/major municipal institution, major unlisted firm |
| `static_reach = 1` | low reach | small/unlisted/niche company, local institution/region, narrow product/business segment, one-off event, narrow policy document, residual `other` |

Level assignment:

| Final level | Criteria |
|---:|---|
| `3 high` | `static_reach = 3` and `context_gate >= 1` |
| `2 medium` | `static_reach = 2` and `context_gate >= 1`, or `static_reach = 3` with only weak context after adjudicated fallback |
| `1 low` | `static_reach = 1`, or `context_gate = 0`, or metadata is missing and the target cannot be confidently placed above low |

Important constraint: mention count, first offset, and title presence cannot by themselves promote a target to high. A niche local company mentioned 12 times in one article remains low or medium depending on market metadata. The text signals only confirm that the target is the article's actual target.

Pre-specified collapse rule:

- Aim for `n >= 20` per ordinal bin on the 80 pre-cutoff pilot.
- Minimum acceptable is `n >= 15`.
- If any bin is below 15 after resampling, compute the raw `(static_reach, context_gate)` tuple and collapse by median split into `low_or_medium` vs `high`, or below-median vs at/above-median if high is the thin bin. Record the collapse before model runs.

### Construct validity argument

The construct is intended to proxy **cross-corpus training exposure to the target**, not merely whether the target is visually prominent in the current article.

Scheme A supports that interpretation because the main scoring axis is target market reach:

- benchmark indices, broad markets, central regulators, major countries, and top-cap listed firms appear repeatedly across financial news, filings, encyclopedic pages, market data, and commentary
- ordinary listed companies and recognized sectors have recurring but less universal coverage
- local entities, niche products, one-off events, and unlisted small firms have much lower expected pretraining exposure

The in-article signals are deliberately demoted to a gate. They answer "is this the correct target for this article?" They do not answer "has the model probably seen this target many times during training?" This separation prevents Target Salience from collapsing into a simple headline/mention-count variable.

Tradability and scope are absorbed into the ordinal criteria without becoming separate confirmatory factors:

- direct tradability and broad benchmark scope increase `static_reach`
- narrow local scope and non-tradable one-off objects decrease `static_reach`
- the final confirmatory matrix still contains only Target Salience, not separate Tradability Tier or Target Scope coefficients

### Non-redundancy with Historical Family Recurrence

Historical Family Recurrence is an event-family/time signal. It varies with event type, month, and recurrence of similar articles. Target Salience is a static target-reach signal. It should not use CLS historical mention counts, search-result counts, or `(entity, event_type, month)` frequencies.

Discriminant design rules:

- Do not include CLS historical target mention counts in Target Salience.
- Do not include event type, publication month, burst size, or family recurrence in Target Salience.
- Let the same target have different Historical Family Recurrence values across events and months while keeping the same static salience class.
- Cross target-salience bins with recurrence tertiles during sampling so high-salience/high-recurrence and high-salience/low-recurrence cases both exist.

Validation checks:

- Report Spearman correlation between Target Salience and Historical Family Recurrence. Desired `|rho| < 0.50`; inspect at `0.50-0.65`; if `> 0.65`, check whether selection or sampling made the factors collinear.
- Report VIF or condition number in the pilot mixed model. Desired VIF `< 3`.
- Provide a 3 x 3 salience-by-recurrence cross-tab before manifest freeze. No structural zero cells should remain after approved bin collapse.
- Do not tune Target Salience thresholds using R5A memorization outcomes.

## 3. 方案 A — Metadata-Anchored Market-Reach Salience (recommended)

### target selection (伪代码)

```python
TARGET_CLASS_RANK = {
    "direct_security_or_index": 4,
    "market_sector_or_theme": 3,
    "macro_actor_or_object": 2,
    "residual_principal_object": 1,
}

def scheme_a_select_target(article, entities, market_metadata, institution_lists):
    headline = extract_cls_headline(article)
    enriched = []

    for e in entities:
        if e.salience not in {"core", "supporting"}:
            continue
        if e.salience == "supporting" and not supporting_fallback_allowed(e, entities, headline):
            continue
        if is_person_without_represented_macro_target(e, entities):
            continue
        if is_source_only_attribution(e, headline, entities):
            continue
        if is_ambiguous_one_char_region_alias(e, entities):
            continue

        meta = lookup_metadata(e, market_metadata, institution_lists)
        target_class = classify_target_class(e, meta)
        if target_class is None:
            continue

        enriched.append({
            "entity": e,
            "meta": meta,
            "target_class": target_class,
            "target_type": map_to_p_predict_type(e, meta),
            "in_headline": alias_in_headline(e, meta, headline),
            "headline_offset": alias_headline_offset(e, meta, headline),
            "mention_count": alias_mention_count(e, meta, article.content),
            "transaction_object": is_transaction_object(e, headline),
            "alias_quality": alias_quality(e, meta),
        })

    if not enriched:
        return NullTarget("no_eligible_forecast_target")

    selected = max(
        enriched,
        key=lambda c: (
            TARGET_CLASS_RANK[c["target_class"]],
            c["entity"].salience == "core",
            c["in_headline"],
            c["transaction_object"],
            c["meta"].instrument_specificity,
            -c["headline_offset"],
            c["alias_quality"],
        ),
    )

    return freeze_target_record(selected)
```

### ordinal scoring (rule 表)

```python
def scheme_a_target_salience(target_record):
    context_gate = compute_context_gate(target_record)
    static_reach = compute_static_reach(target_record)

    if context_gate == 0:
        return 1
    if static_reach >= 3:
        return 3
    if static_reach == 2:
        return 2
    return 1
```

`compute_static_reach` table:

| Target family | `static_reach = 3` | `static_reach = 2` | `static_reach = 1` |
|---|---|---|---|
| Company | SSE50/CSI300/top-cap bucket, national household-name finance/tech/industrial firm | ordinary listed company, CSI500/mid-cap, major unlisted financial/corporate actor | small cap, unlisted local firm, subsidiary with no independent public-market profile |
| Index / ETF | broad benchmark index or market-wide ETF | specific sector/theme ETF or named index product | niche fund/product with narrow coverage |
| Sector / concept / product market | broad formal sector or dominant market theme | recognized Shenwan/CSRC industry, commodity, broker theme | narrow product, component, business segment, local project |
| Macro / institution / region | PBOC, CSRC, State Council, NDRC, MOF, major countries/regions, broad `A股/美股/港股` market anchors | provincial regulator, major city, exchange, national association, major ministry sub-body | local bureau, local region, one-off policy program |
| Other | rare; only globally/nationally known bounded event | named policy/document/event with recurring national coverage | one-off event/document/person-backed residual |

Metadata missing rule:

- If company metadata is missing for a `company` target, default to `static_reach = 2` only when it is clearly listed or a major firm from local metadata. Otherwise set `static_reach = 1` and flag `metadata_missing_company`.
- If too many company targets are metadata-missing, switch to Scheme B before manifest freeze rather than silently mixing methods.

### expected 80-case distribution

The existing 80-item fixture has 582 entity labels and is company/concept/institution heavy: `company core = 50`, `institution core = 29`, `concept core = 23`, plus many supporting market objects. A rough rule-based dry run without market metadata selects companies for roughly 35-45% of cases and produces a medium-heavy distribution. Scheme A should split that medium mass once market-cap/index metadata is added.

Expected after quota-aware sampling:

| Level | Expected count in 80 pre-cutoff cases | Risk |
|---:|---:|---|
| `3 high` | 18-24 | Thin if sample under-represents broad indices, national policy, and blue-chip firms. |
| `2 medium` | 34-42 | Likely largest bin because ordinary listed-company news dominates CLS. |
| `1 low` | 16-24 | Thin unless sampling intentionally keeps small-cap, local, niche-product, and unlisted-target cases. |

Quota instruction: before model runs, force each salience level to at least 20 if the candidate pool allows. If low is below 15, do not solve it by reclassifying ordinary listed companies as low; resample low-reach cases or use the pre-registered binary collapse.

### implementation cost

Moderate, bounded, no crawler.

Needed:

- reuse frozen Thales `salient_entities[]` for the 80 fixture
- rerun or reuse the dual-agent entity pass for additional cases only as an upstream label source
- query Thales quant metadata for company ticker/listed flag, market cap bucket, and broad-index membership
- maintain small static lists for core institutions, broad market anchors, and major regions
- compute text features with deterministic substring/alias matching

Not needed:

- web search
- search-engine result counts
- Wikipedia/Baidu lookups
- CLS historical target mention counts
- a new runtime LLM target selector

### validation strategy (多少人工 / metric)

Target selection validation:

- Double-label all 80 pre-cutoff pilot cases for `best target`, `acceptable target set`, `target_type`, and `nullability`.
- For the 350 post-cutoff BL2 cases, double-label a stratified 60-case audit sample, oversampling source-only, multi-company, and policy/macro cases.
- Metrics:
  - binary eligible/null agreement >= 0.90
  - exact or alias-equivalent top-1 target agreement >= 0.80
  - acceptable-target-set containment >= 0.90
  - `target_type` Cohen kappa >= 0.75
  - all low-confidence cases adjudicated before manifest freeze

Salience validation:

- Double-score the 80 pre-cutoff cases after metadata enrichment.
- Weighted kappa for 3-level ordinal >= 0.70.
- Adjacent agreement >= 0.90; exact agreement target >= 0.75.
- Metadata audit: 100% of company targets have either a verified ticker/listed status or an explicit `metadata_missing_company` flag.
- Construct checks: known-groups ordering must hold for benchmark indices/core institutions > ordinary listed companies > local/niche targets.
- Discriminant checks with Historical Family Recurrence: `|rho| < 0.50` desired, VIF `< 3`, no salience x recurrence structural zero cell after quota/collapse.

## 4. 方案 B — Text-Only Target Prominence Salience (alternative)

Use this only if market metadata access blocks manifest freeze. It is cheaper but weaker because it leans on article-local signals that are closer to in-context salience than training-exposure salience.

### target selection (伪代码)

```python
def scheme_b_select_target(article, entities):
    headline = extract_cls_headline(article)
    candidates = []

    for e in entities:
        if e.salience not in {"core", "supporting"}:
            continue
        if e.type == "person":
            continue
        if is_source_only_attribution(e, headline, entities):
            continue
        if e.salience == "supporting" and not is_unique_headline_or_market_object(e, article, headline, entities):
            continue

        candidates.append({
            "entity": e,
            "target_type": map_to_p_predict_type_without_metadata(e),
            "class_rank": text_only_class_rank(e),
            "in_headline": e.value in headline,
            "headline_offset": headline.find(e.value) if e.value in headline else 10**9,
            "mention_count": article.content.count(e.value),
        })

    if not candidates:
        return NullTarget("no_eligible_forecast_target")

    return max(
        candidates,
        key=lambda c: (
            c["class_rank"],
            c["entity"].salience == "core",
            c["in_headline"],
            min(c["mention_count"], 5),
            -c["headline_offset"],
            len(c["entity"].value),
        ),
    )
```

### ordinal scoring (rule 表)

| Level | Text-only criteria |
|---:|---|
| `3 high` | target is `core`, appears in headline, first mention is in the first 20% of article, mention count >= 3, and target class is index/broad market/core institution/region or a clearly named listed company |
| `2 medium` | target is `core` and either appears in headline or mention count >= 2; or target is a headline supporting fallback that is the unique market object |
| `1 low` | target is supporting/body-only, mention count = 1, `target_type = other`, narrow product/event/policy object, or target centrality is weak |

Hard fields:

- frozen `salient_entities[]`
- headline match
- mention count
- first offset / relative position
- source-only exclusion patterns

No market-cap, ticker, index membership, or external metadata is required.

### expected 80-case distribution

Expected on an 80-case CLS pilot:

| Level | Expected count | Risk |
|---:|---:|---|
| `3 high` | 28-40 | Inflated by headline/core/mention-count cues. |
| `2 medium` | 28-38 | Stable. |
| `1 low` | 5-14 | Likely thin because target selection already prefers core headline entities. |

This is the main weakness of Scheme B. It may pass a binary high-vs-not-high split but is unlikely to support a stable 3-level confirmatory ordinal without quota intervention.

### implementation cost

Low.

Needed:

- Thales entity labels or the reusable dual-agent entity prompt
- deterministic headline extraction and substring matching
- no market metadata
- no external API

### validation strategy (多少人工 / metric)

Target selection validation is the same as Scheme A.

Salience validation:

- Double-score all 80 pre-cutoff cases because the scoring relies on human-sensitive distinctions like source-only company vs true market object.
- Weighted kappa target >= 0.70; adjacent agreement >= 0.90.
- Require a reviewer note for every `level = 3` non-index/non-institution company, because text-only features can over-promote obscure companies.
- If `level 1` has fewer than 15 cases, collapse to binary before model runs. Do not reclassify cases upward or downward to manufacture a tertile.

## 5. Recommendation

**首选**: 方案 A - Metadata-Anchored Market-Reach Salience

**为什么**: It best matches the construct. The ordinal is driven by stable market reach and institutional scope, which are plausible proxies for pretraining exposure, while article-local signals only verify that the selected target is actually central to the case. It also absorbs the useful information from Tradability Tier and Target Scope without adding them back as independent confirmatory factors.

**触发切换条件**:

- Thales market metadata cannot provide ticker/listed flag plus at least one of market-cap bucket or broad-index membership before manifest freeze.
- More than 20% of company targets would be `metadata_missing_company`.
- Scheme A produces a salience bin with fewer than 15 pre-cutoff cases after reasonable resampling.
- Human audit shows weighted kappa below 0.65 and disagreements are metadata-rule disagreements rather than isolated annotation mistakes.

If only the first two conditions fire, use Scheme B as a temporary pilot fallback and pre-register it as weaker construct validity. If the thin-bin condition fires, first resample; if still thin, keep Scheme A but collapse to binary.

**Don't do**:

- Do not ask `P_predict` models to infer the target.
- Do not use CLS historical mention counts, search-engine counts, Wikipedia/Baidu pages, or crawler output in Target Salience.
- Do not make `Entity Salience: non-target`, `Target Scope`, or `Tradability Tier` separate confirmatory factors.
- Do not let article mention count alone promote a target to high salience.
- Do not encode event type or month into Target Salience; that belongs to Historical Family Recurrence.
- Do not use more than 3 levels for the pilot unless the 80-case cell checker proves all confirmatory cells remain above 20.
- Do not keep null targets in the final `P_predict` manifest.

## 6. Open questions for user

1. Can WS0.5 call the Thales quant metadata engine for a frozen ticker/listed/index/market-cap snapshot before manifest freeze?
2. For listed companies, should the operator-facing `target` always be the Chinese company name with ticker sidecar metadata, or should some cases use ticker strings as the visible target?
3. Should pure macro/policy cases with no directly tradeable target remain in the 80 pre-cutoff pilot, capped by quota, or should sampling prefer cases with company/sector/index targets?
