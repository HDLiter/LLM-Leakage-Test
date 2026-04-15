# Thales Signal Profile Review — for FinMem-Bench Factor Design

Date: 2026-04-13
Scope: Read-only static code analysis of `D:\GitRepos\Thales` for three concepts under consideration as FinMem-Bench factors: (1) topic/event-type classification, (2) `Modality`, (3) `Authority`.

---

## 1. Thales project layout relevant to these concepts

All three concepts are implemented in the news-processing stack:

- `contracts/news/_annotation.py` — `EventType` StrEnum (13 values) and `EVENT_TYPE_ZH_MAP` normalization table.
- `contracts/news/_signal_profile.py` — `Modality` StrEnum, `AuthorityLevel` StrEnum, `AUTHORITY_ORDINALS`, and the `NewsSignalProfile` / `ModalityScore` / `AuthorityScore` pydantic models with validators.
- `prompts/news_processing/topic_classification.py` — `NewsTopicClassificationPrompt` (v2.2.0) with MINIMAL + STANDARD templates, 13-type taxonomy, 8 boundary rules, 5 examples.
- `prompts/news_processing/signal_profile.py` — `NewsSignalProfilePrompt` (v3.0.0) with MINIMAL + STANDARD templates, modality taxonomy, authority taxonomy, and a CLS-specific marker table (roughly 12 rows).
- `prompts/news_processing/signal_profile_twopass.py` — a two-pass variant (not analyzed in depth).
- `pipeline/news_processing/signal_profile.py` — the batching pipeline that calls the SLM. Inputs are `NewsItem.content` and optional `EntityMatch` context; no market/web/KG data is consumed.
- `pipeline/scoring/dynamics.py` — downstream consumer that uses `AUTHORITY_ORDINALS` to compute `authority_leap` (monotonic "higher-authority source showed up" signal for novelty scoring).
- `experiments/prompts/news_signal_profile/` — heavy experiment trail (canon slices, cross-calibration, boundary refinement, holdout) showing this has been LLM-annotated and cross-judge-calibrated, not rule-computed.

---

## 2. Topic classification: Thales design vs FinMem-Bench Event Type

### Thales `EventType` taxonomy (v3, 13 types)

| Code | Chinese | Scope |
|---|---|---|
| POLICY | 政策法规 | Chinese government directives, measures, new rules |
| ENFORCEMENT | 监管执法 | Administrative regulator actions (证监会/交易所/银保监/纪委) |
| LEGAL | 司法诉讼 | Judicial body actions (法院/仲裁委/检察院) |
| INDICATOR | 经济指标 | Economy-wide data releases (GDP/CPI/PMI/trade) |
| EARNINGS | 业绩财报 | Company periodic financial disclosure |
| CORPORATE | 公司动态 | M&A, financing (IPO/定增/发债), contracts, operations, strategy |
| PRODUCT | 产品技术 | Named product milestones (approvals, launches, trials) |
| PERSONNEL | 人事变动 | Career events of named persons |
| TRADING | 交易行情 | Price action on tradable instruments, capital flows |
| OWNERSHIP | 股权变动 | Secondary-market shareholding changes (减持/增持/质押/解禁) |
| INDUSTRY | 行业研究 | Sector-wide statistics, supply chain, analyst forecasts |
| GEOPOLITICS | 地缘政治 | Foreign non-financial government action |
| OTHER | 其他 | Non-financial (disasters, pure science, entertainment) |

Design traits:
- Action-based ("what action / what information archetype"), not scope-based.
- LLM-annotated (SLM with chain-of-thought). No RULE fallback — on exhaustion the item is skipped ("absence over garbage").
- Multi-label scored (1-5 types, each 1-100 independent).
- Mature disambiguation boundaries between adjacent types refined through v2.1 → v2.2 (removed 4 interfering CORPORATE rules; +19.7% macro p@1).
- Throughput-oriented: MINIMAL template is token-efficient (~2.6k tokens/call) — the user's claim that "Thales is coarser for throughput" is NOT quite right; Thales is already at 13 types. It is relatively granular but optimized for SLM batch cost.

### FinMem-Bench tentative Event Type list (7 categories)

| FinMem code | Matches Thales | Notes |
|---|---|---|
| `earnings/guidance` | EARNINGS | 1:1 |
| `capital_action_M&A_restructuring` | CORPORATE (subset) | FinMem narrower; Thales CORPORATE also covers 定增/发债/contracts/partnerships/operations |
| `order_product_operations` | PRODUCT + part of CORPORATE | Thales splits named product events (PRODUCT) from operational events (CORPORATE); FinMem collapses |
| `policy_regulation` | POLICY + ENFORCEMENT (+ LEGAL?) | Thales splits three ways by agent type (rule-maker vs administrative enforcer vs court) |
| `litigation_compliance` | LEGAL + ENFORCEMENT | Overlaps with policy_regulation on ENFORCEMENT boundary |
| `macro_industry_commentary` | INDICATOR + INDUSTRY + ANALYSIS-flavored | Three disparate types collapsed |
| `other` | OTHER (+ GEOPOLITICS? + PERSONNEL? + TRADING? + OWNERSHIP?) | Ambiguous — four Thales types have no FinMem home |

### Gaps / mismatches

1. **PERSONNEL, TRADING, OWNERSHIP, GEOPOLITICS have no natural FinMem home.** These are 4 of Thales's 13 types. On the CLS corpus, PERSONNEL and OWNERSHIP are each several percent of volume and TRADING is very common. Forcing them into `other` makes `other` the single biggest bucket and defeats the point of the factor.
2. **`policy_regulation` vs `litigation_compliance` boundary is ill-defined.** Thales splits by the *agent* doing the action (POLICY = rule-creator; ENFORCEMENT = administrative enforcer; LEGAL = court). FinMem collapses these to two buckets without specifying which side ENFORCEMENT belongs to.
3. **`capital_action_M&A_restructuring` + `order_product_operations` under-partitions CORPORATE.** Thales's boundary rules show M&A/financing vs operations vs named-product are fundamentally different signals.
4. **`macro_industry_commentary` mixes INDICATOR (hard data) with INDUSTRY (analyst commentary)** — these have very different authority/modality profiles and likely very different memorization behavior.

### Recommendation

Adopt Thales's 13-type taxonomy wholesale, or a lightly trimmed version (e.g., merge GEOPOLITICS into OTHER if FinMem cases have no foreign-government news). The Thales boundary rules and examples are already battle-tested and would save FinMem many weeks of label debate. FinMem-Bench is smaller scale, so the "throughput argument for coarseness" does not apply — but Thales is not coarse to begin with.

---

## 3. Modality

### Definition
From `_signal_profile.py` docstring: "Categorizes news items by HOW the information was communicated/disseminated, regardless of the event type."

### Schema
Python `StrEnum` (7 values) plus a `ModalityScore` pydantic model `(modality, reason: str, score: 1-100)`. A news item carries `modality_scores: list[ModalityScore]` of 1-5 items ordered by descending score; downstream uses the top-scored one as `primary_modality`.

### Categories (7)
OFFICIAL_ANNOUNCEMENT, REGULATORY_FILING, DATA_RELEASE, PRESS_RELEASE, ANALYSIS, RUMOR, OTHER.

### Computation method
LLM-annotated by an SLM via `NewsSignalProfilePrompt` (MINIMAL → STANDARD escalation, no RULE fallback; failures are dropped). Temperature 0.1, CoT required. The pipeline (`pipeline/news_processing/signal_profile.py`) passes only `item.content` and optional `EntityMatch` context; no market, web, or KG lookup.

### Input data
`NewsItem.content` (CLS text), entity matches from entity-disambiguation, and `reference_year` (for year masking). That is it.

### Examples (from CLS marker table in the prompt)
- "公告 / 公司公告称 / 互动平台" → OFFICIAL_ANNOUNCEMENT
- "统计局 / 海关总署 / EIA / PMI / CPI" → DATA_RELEASE
- "涨多跌少 / 涨幅扩大" (CLS mover recap) → PRESS_RELEASE
- "业绩快报 / 季报 / 年报" → REGULATORY_FILING
- "分析师指出 / 研报 / 评级" → ANALYSIS
- "据悉 / 据传 / 网传" → RUMOR

### Documented limitations
The prompt has extensive "look-through" and "editorial-framing" boundary rules (D15, D17, R2, R10, R11), implying that Thales has struggled with the modality boundary between OFFICIAL_ANNOUNCEMENT (relay of source) and PRESS_RELEASE (CLS editorial framing). Many items are ambiguous.

### Source class for FinMem-Bench
**CLS-internal (text-derived).** Modality is inferred purely from the text of the CLS item via LLM. It is NOT extra-corpus. It does not involve market data, web lookup, or any model-side metadata about the case.

### Construct validity for memorization
Plausibility-only argument: modality roughly tracks textual register and boilerplate density. OFFICIAL_ANNOUNCEMENT and REGULATORY_FILING items tend to contain canonical stock phrases ("根据中华人民共和国证券法第X条", "经董事会审议通过") that appear in training data with high redundancy; DATA_RELEASE items contain templated numerical formats; RUMOR items are low-boilerplate and usually more paraphrased. So modality is plausibly correlated with memorization signal — high-boilerplate modalities should yield higher surface-form memorization scores. This is a reasonable factor to include, but note that it likely correlates with Event Type (e.g., EARNINGS ⇔ REGULATORY_FILING almost deterministically), which would cause collinearity with the Event Type factor.

### Operationalization complexity
Moderate. Running `NewsSignalProfilePrompt` against the 1000-case FinMem benchmark would be a few thousand SLM/LLM calls — very tractable. But Thales's prompt is tuned for CLS text specifically, uses CLS markers, and assumes SLM infrastructure (inference strategy, escalation chain, batch inference, `Result`/`Failure` plumbing). Reusing the *prompt text* and the taxonomy is straightforward; reusing the *code path* would drag in Thales inference infrastructure.

---

## 4. Authority

### Definition
"Categorizes news sources by their AUTHORITY/CREDIBILITY, ordered from highest (OFFICIAL) to lowest (SELF_MEDIA)."

### Schema
`AuthorityLevel` StrEnum (8 values) with module-level `AUTHORITY_ORDINALS` dict (OFFICIAL=6 → SELF_MEDIA=0, UNKNOWN=-1 as sentinel). Each news item carries `authority_scores: list[AuthorityScore]` of **exactly 8 entries, one per level**, each with score 1-100 as an independent confidence estimate (enforced by validator `_validate_authority_completeness`). This is a dense k-bin distribution, not a single-label.

### Categories (8)
OFFICIAL, CORPORATE, MAINSTREAM_MEDIA, INDUSTRY_MEDIA, ANALYST, SOCIAL_MEDIA, SELF_MEDIA, UNKNOWN.

### Computation method
Same as modality: LLM-annotated from `item.content` via `NewsSignalProfilePrompt`. No database of source reputations, no URL domain check, no publisher metadata. The model is asked to *infer* the original source of the information from the text itself — e.g., "据新华社" → MAINSTREAM_MEDIA, "证监会决定" → OFFICIAL, "据悉" → UNKNOWN. The prompt explicitly tells the SLM to *trace to original source, not delivery channel* (because everything is delivered by CLS). Downstream, `pipeline/scoring/dynamics.py` uses `AUTHORITY_ORDINALS` to compute `authority_leap` — "did a higher-authority source show up in this item than in any prior item on the same story?"

### Input data
Same as modality: `NewsItem.content` + entity context. **Not** `news.source` / `news.publisher` / domain / URL / any external reputation DB. This is a key finding: Thales's `authority` field is CLS-text-inferred, not looked up.

### Examples
- "国务院 / 证监会 / 央行 宣布" → OFFICIAL (ord=6)
- "某上市公司公告称" → CORPORATE (ord=5)
- "据新华社 / 央视报道" → MAINSTREAM_MEDIA (ord=4)
- "财联社研究员/财联社X月X日电" (default CLS framing with no external attribution) → INDUSTRY_MEDIA (ord=3)
- "据某券商研报" → ANALYST (ord=2)
- "微博/投资者互动平台" → SOCIAL_MEDIA (ord=1)
- "据悉 / 据传 / 网传" → UNKNOWN (ord=-1)

### Documented limitations
- UNKNOWN is a "sentinel for RULE fallback never producing a positive authority_leap" — Thales is aware that its authority estimates are uncertain and builds conservative downstream logic around that.
- All 84 CLS items in the FinMem test set are by construction delivered by CLS (INDUSTRY_MEDIA), so Thales must "look through" to the original source — a classification task, not a metadata lookup. Error-prone.

### Source class for FinMem-Bench
**CLS-internal (text-derived).** Despite the label "authority", Thales does not consume extra-corpus data. It is a text-feature classifier. If FinMem-Bench wanted a true extra-corpus authority factor, it would need to add a source-metadata lookup step — which is NOT what Thales has.

### Construct validity for memorization
Plausibility argument: Yes, reasonably likely to discriminate. OFFICIAL and CORPORATE sources are usually associated with verbatim-quotable texts (policy full text, company filings) which are in training corpora verbatim. ANALYST material is commonly paraphrased. RUMOR / UNKNOWN material is unlikely to be in training data in any canonical form. This maps plausibly to memorization gradient. The concern is ordinal collinearity with modality (OFFICIAL_ANNOUNCEMENT almost implies OFFICIAL or CORPORATE authority) and with Event Type.

### Operationalization complexity
Same as modality — same prompt, same pipeline. Moderate effort to reuse; easy to just reuse the taxonomy + ordinals.

---

## 5. Reuse recommendation

| Concept | Recommendation | Rationale |
|---|---|---|
| Topic / Event Type | **(a) Directly reuse Thales `EventType` taxonomy and the STANDARD prompt template.** Light trim allowed (merge GEOPOLITICS into OTHER if unused on the benchmark). | The 13-type v3 taxonomy is already LLM-optimized, boundary-rule-hardened, and has a cross-calibrated evaluation trail. FinMem's 7-type list is strictly worse (collapses real distinctions, has an ambiguous `policy/litigation` split). Adopting Thales saves label debate and aligns the two projects' downstream analysis. |
| Modality | **(b) Refine Thales design.** Reuse the 7-value enum and the CLS marker table but simplify: FinMem needs a single-label primary modality (not a 1-5 scored list), and can drop the dense scoring machinery. Reuse the prompt *text* and boundary rules, not the inference infrastructure. | Conceptually sound and battle-tested. Dense multi-score output is overkill for FinMem's per-case analysis. |
| Authority | **(c) Use as inspiration only, AND consider reinventing.** Thales's `AuthorityLevel` taxonomy is good, but the text-inferred operationalization collapses on CLS because all items come through CLS. For FinMem-Bench a stronger operationalization would either (i) use Thales's enum but reinfer via an independent LLM judge, or (ii) add an extra-corpus source lookup step (see §6). Do NOT reuse the 8-bin dense-score + ordinal-leap machinery — that's tailored for novelty scoring, not memorization. | The ordinal hierarchy is reusable; the plumbing is not. And FinMem has an opportunity to make authority a genuinely extra-corpus factor that Thales has not built. |

---

## 6. P1 implication — can modality / authority restore extra-corpus headroom?

### P1 status
FinMem-Bench's "extra-corpus signal" principle (P1) asks for factors whose value is computed from sources outside the CLS corpus (market data, web, KG, model-side metadata). After Reprint Status was dropped, P1 is down to a single extra-corpus factor. The question is whether modality or authority can reclaim extra-corpus status.

### Findings

- **Modality as implemented in Thales is NOT extra-corpus.** It is a text-feature classifier over `NewsItem.content`. Adopting it as-is would add another CLS-internal factor, not help P1. There is no obvious path to make modality extra-corpus — the concept itself is a property of how a piece of text is written, not of any external signal.

- **Authority as implemented in Thales is ALSO not extra-corpus.** The label is misleading: Thales infers authority from text markers ("据新华社", "证监会宣布"), not from a reputation database or publisher metadata. So naively adopting it also adds a CLS-internal factor.

- **But authority CAN be re-operationalized as extra-corpus, and this is FinMem's opportunity.** Candidate extra-corpus operationalizations:
  1. **Publisher metadata lookup**: CLS items carry a source/publisher field (`NewsItem.source` or similar — verify by inspecting CLS raw schema). Mapping publisher domain → authority level via a curated dictionary is purely metadata-based and qualifies as extra-corpus (derived from corpus *metadata*, not corpus *text*).
  2. **Entity reputation lookup**: given the entities in the item, look up whether any entity is an OFFICIAL body (regulator, ministry, exchange, central bank) in a knowledge graph. Thales already has a concept engine (`pipeline/concept_engine/`) and entity system — the KG side is reusable.
  3. **Cross-corpus verification**: for each item, query the web or a reference corpus (Wikipedia, 巨潮资讯, 证监会网站) to check whether the named event is verifiable in an authoritative source within ±N days. The resulting "authoritative corroboration" feature is extra-corpus and has a clean operational definition.

  Any of these would make authority a genuinely extra-corpus factor.

### Recommendation on P1

- **Do not declare modality an extra-corpus factor.** It is inherently a text-feature.
- **Re-scope authority as an extra-corpus factor** by replacing the Thales text-inference operationalization with a publisher-metadata or KG-lookup operationalization. This gives FinMem a second extra-corpus factor (restoring P1 headroom) without reinventing the taxonomy. The Thales `AuthorityLevel` enum and ordinal hierarchy remain directly reusable as the *label space*; only the computation method changes.
- **Verify first** that CLS raw items carry a source/publisher metadata field (check `D:\GitRepos\Thales\datasets\cls_telegraph_raw`). If yes, publisher→authority is an easy 1-afternoon implementation. If no, fall back to KG-lookup via Thales's entity registry.
- This re-operationalization also fixes a construct-validity concern: text-inferred authority is almost deterministic given modality, causing collinearity; metadata-based authority is partially orthogonal because the same text template (e.g., a CLS recap) can be filed by different publishers.
