# WS0.5 Super-type Collapse Analysis

**Analyst**: GPT-5.4 xhigh via Codex CLI
**Date**: 2026-05-18
**Question**: 13-class Thales V3 -> best super-type collapse for R5A pilot

## 1. C_FO outcome-type clustering of 13-class

从 `C_FO` 角度，13-class 的天然分簇不是按机构主体，而是按“可替换的已验证结果”长什么样。最稳定的 outcome slots 有五类：一是 authority action 的结果或状态，例如新规发布/撤回、监管处罚/调查、法院裁定、制裁或外交/军事行动结果；二是 issuer catalyst，例如并购/融资/合同/产品获批/高管任免这类实体事件谓词；三是 issuer quantitative disclosure，例如业绩、减持/增持、质押、解禁中的数值、方向、比例和主体；四是 public numeric print，例如 CPI/PMI/GDP、指数/股价/资金流等公开数值点；五是 sector fundamentals，例如行业统计、供需、产能、产品价格、分析师或协会预测。

边界规则支持这个切法：`CORPORATE` vs `EARNINGS`、`PRODUCT`、`PERSONNEL`、`OWNERSHIP` 的差异主要是 action/object，不是主体；`INDICATOR` vs `INDUSTRY` vs `TRADING` 的差异主要是经济整体、行业基本面、可交易价格；`ENFORCEMENT` vs `LEGAL` 则由行政/司法主体区分，但二者在 C_FO 中都属于 authority outcome。`OTHER` 是最后兜底类，不应进入 C_FO active super-type；它没有稳定金融 target，也容易把 public-health/weather/science 数字误当成金融 false outcome。

## 2. 方案 A — Host-preserving 5 active super-types (recommended)

### Super-type 列表

| Super-type | Includes V3 classes | C_FO slot homogeneity | Bloc 3 stratification value |
|---|---|---|---|
| `authority_decision` | `POLICY`, `ENFORCEMENT`, `LEGAL`, `GEOPOLITICS` | Medium-high. One schema can edit decision/action status, target, sanction/penalty/ruling amount, policy direction, or verified geopolitical outcome. Some `GEOPOLITICS` casualty narratives will be `narrative-entailed` or non-slotable. | High: institutional/wire templates are exactly where memorization may interact with source authority and formulaic language. |
| `issuer_catalyst` | `CORPORATE`, `PRODUCT`, `PERSONNEL` | Medium-high. Shared schema edits local event predicate: deal/financing/contract status, named product milestone, or named-person appointment/resignation result. Object type differs, but topology is event-predicate local. | High: separates named issuer catalysts from numeric disclosures and market prints; likely interacts with target salience. |
| `issuer_quant` | `EARNINGS`, `OWNERSHIP` | Medium. Shared schema edits issuer/security quantitative disclosure: value, direction, percentage, holder/period, and status. Earnings and ownership are different legally, but both are compact numeric filings. | Medium-high: isolates filing-like numeric templates from broader corporate narratives. |
| `market_macro_print` | `INDICATOR`, `TRADING` | Medium. Shared schema edits public numeric print: indicator/instrument, period/session, value, direction, magnitude, flow/yield/price. Official macro vs market source differs, but the slot is local and numeric. | High: captures high-frequency templated data/price news, likely a different template-rigidity regime. |
| `sector_industry` | `INDUSTRY` | High. Edits sector statistic, forecast, product/commodity price, capacity/supply-chain state, or analyst/association projection. | High despite small N: preserves the hardest Thales boundary and a distinct host register. |
| `exclude_other` | `OTHER` | Not active for C_FO. Mark `exclude_from_pilot` unless later manually reclassified into a financial/geopolitical type. | None for R5A pilot; including it adds non-financial noise. |

### Map to 4 broad host category

| Super-type | broad host |
|---|---|
| `authority_decision` | `policy` |
| `issuer_catalyst` | `corporate` |
| `issuer_quant` | `corporate` |
| `market_macro_print` | `macro` |
| `sector_industry` | `industry` |
| `exclude_other` | excluded; no `C_NoOp` host quota contribution |

### Expected pre-cutoff distribution

`quality_natural.json` has 600 natural-fixture items with this V3 distribution: `CORPORATE` 129, `TRADING` 103, `POLICY` 74, `GEOPOLITICS` 69, `EARNINGS` 56, `OWNERSHIP` 35, `INDUSTRY` 31, `INDICATOR` 26, `PRODUCT` 23, `OTHER` 25, `ENFORCEMENT` 12, `PERSONNEL` 12, `LEGAL` 5.

Under Scheme A, expected natural counts in 80 pre-cutoff cases are approximately:

| Super-type | Fixture count / 600 | Natural expected count / 80 | Quota posture |
|---|---:|---:|---|
| `authority_decision` | 160 | 21.3 | Safe |
| `issuer_catalyst` | 164 | 21.9 | Safe |
| `issuer_quant` | 91 | 12.1 | Meets 5-type threshold, but thin |
| `market_macro_print` | 129 | 17.2 | Safe |
| `sector_industry` | 31 | 4.1 | Natural distribution fails; must oversample |
| `exclude_other` | 25 | 3.3 | Exclude |

If `OTHER` is excluded before normalizing, the active proportions barely change: `sector_industry` is still only about 4.3 of 80 under natural sampling. This is not a reason to merge it immediately; the plan already requires each top-level host, including `industry`, to appear at least 15 times, so the sampling design must oversample industry regardless.

### §6.3 quota risk

Scheme A uses five active C_FO super-types, so the plan threshold is at least 12 cases per super-type. `sector_industry` is the only material fail risk under natural sampling. Mitigation: make `INDUSTRY` a hard stratified quota target, aiming for 12-14 `INDUSTRY` cases with `verified_outcome=true` and a separate 15-case `industry` host quota for `C_NoOp`. Do not count non-slotable sector commentary toward the C_FO floor.

`issuer_quant` is the second watch item: natural expectation is only 12.1, so random pre-cutoff sampling can fall below 12. Reserve 14-16 combined `EARNINGS`/`OWNERSHIP` cases if the pool allows. If either `sector_industry` or `issuer_quant` cannot reach the floor after enforcing `verified_outcome` and `fo_slotable`, switch to Scheme B before prereg freeze rather than weakening slot rules.

## 3. 方案 B — Quota-first 4 active outcome groups (alternative)

### Super-type 列表

| Super-type | Includes V3 classes | C_FO slot homogeneity | Bloc 3 stratification value |
|---|---|---|---|
| `authority_decision` | `POLICY`, `ENFORCEMENT`, `LEGAL`, `GEOPOLITICS` | Same as Scheme A. | Same as Scheme A. |
| `issuer_catalyst` | `CORPORATE`, `PRODUCT`, `PERSONNEL` | Same as Scheme A. | Same as Scheme A. |
| `reported_numbers` | `EARNINGS`, `INDICATOR`, `INDUSTRY` | High for C_FO: all are reported/forecast numeric outcomes with period, value, direction, and comparison slots. | Medium: strong numeric-print factor, but loses the ability to separate company filings, macro releases, and industry reports. |
| `market_security` | `TRADING`, `OWNERSHIP` | Medium-high: both edit security-market state, price/flow/volume/holder percentage, or supply-overhang facts. | Medium-high: preserves market microstructure/price-action signal, but ownership-specific filing behavior is diluted. |
| `exclude_other` | `OTHER` | Not active for C_FO. | None. |

### Map to 4 broad host category

| Super-type | broad host |
|---|---|
| `authority_decision` | `policy` |
| `issuer_catalyst` | `corporate` |
| `reported_numbers` | Class-conditional bridge: `EARNINGS -> corporate`, `INDICATOR -> macro`, `INDUSTRY -> industry` |
| `market_security` | Class-conditional bridge: `TRADING -> macro`, `OWNERSHIP -> corporate` |
| `exclude_other` | excluded |

This alternative is acceptable only if WS0.5 computes the locked `host_category` from original V3 before applying the C_FO collapse. It still gives every case one C_FO super-type and one C_NoOp host; it should not derive NoOp host from the mixed super-type name.

### Expected pre-cutoff distribution

| Super-type | Fixture count / 600 | Natural expected count / 80 | Quota posture |
|---|---:|---:|---|
| `authority_decision` | 160 | 21.3 | Safe |
| `issuer_catalyst` | 164 | 21.9 | Safe |
| `reported_numbers` | 113 | 15.1 | Just meets 4-type threshold |
| `market_security` | 138 | 18.4 | Safe |
| `exclude_other` | 25 | 3.3 | Exclude |

This is the most quota-stable 4-type scheme that remains C_FO-coherent. Its weak point is not slotability; it is interpretability, because it mixes host registers inside `reported_numbers` and `market_security`.

### §6.3 quota risk

The four active groups must each reach at least 15 cases. `reported_numbers` is close enough to the threshold that unstratified sampling can still fail, so reserve 17-18 cases if using this scheme. The upside is that `INDUSTRY` no longer has to satisfy a standalone C_FO super-type floor, while the separate `industry` host quota for `C_NoOp` can still be enforced through the class-conditional host bridge.

## 4. Recommendation

**首选**: 方案 A — Host-preserving 5 active super-types.

**为什么**: It is the best compromise across the three downstream uses. It gives C_FO rule writers coherent outcome schemas without turning corporate news into one giant bucket; it maps cleanly into the frozen four `C_NoOp` hosts; and it preserves `sector_industry`, which is analytically valuable because Thales already identifies `INDUSTRY` as a hard boundary and likely a distinct template regime. The cost is an explicit sampling burden: `INDUSTRY` must be quota-sampled, not left to natural prevalence.

**触发切换条件**: Switch to Scheme B if the pre-cutoff pool cannot produce at least 12 `sector_industry` cases with `verified_outcome=true` and enough `fo_slotable=true` cases after normal eligibility filtering, or if enforcing the standalone `sector_industry` quota causes another core factor split to drop below `n_eff >= 15`. Scheme B should also be used if Claude Code decides the implementation must prioritize one C_FO rules table over clean super-type-to-host mapping; in that case, preserve `host_category` from original V3 as a separate locked manifest field.

**Don't do**: Do not use the raw 13 classes as the Bloc 3/C_FO factor in the pilot. `LEGAL`, `ENFORCEMENT`, `PERSONNEL`, `PRODUCT`, `INDICATOR`, and `INDUSTRY` are too sparse for 80 pre-cutoff cases, and per-class C_FO schemas would overfit the pilot. Also do not create a 6-type scheme that splits `EARNINGS`, `OWNERSHIP`, `INDICATOR`, and `TRADING` too finely; it looks semantically neat but immediately creates quota failures.

Do not use a pure four-host collapse (`policy`, `corporate`, `industry`, `macro`) as the C_FO super-type. That is fine for `C_NoOp`, but for C_FO it makes the corporate bucket too heterogeneous: earnings numbers, M&A, product approvals, personnel changes, and shareholding changes need different false-outcome slots. The result would either be a vague rule table or many hidden sub-rules, neither of which is good for audit.

## 5. OTHER 处理

**建议**: v0.2 阶段先标 `exclude_from_pilot=true` 是合理的。Store an explicit reason such as `other_nonfinancial_no_r5a_target`, report the excluded count in the quota report, and revisit only if later classification improves or the pilot source unexpectedly contains many finance-adjacent `OTHER` items.

**为什么**: V3 boundary rules define `OTHER` as last-resort non-financial content. If a disaster, pandemic, science, or weather item has a direct market, industry, policy, or geopolitical angle, it should already be classified as `TRADING`, `INDUSTRY`, `POLICY`, or `GEOPOLITICS`, not `OTHER`. Merging true `OTHER` into `macro` would contaminate both C_FO and C_NoOp: COVID counts, weather numbers, and pure science results have numeric slots but no financial target, so they test general news recall rather than financial-news leakage.

**CLS 中 OTHER 占比观察**: `quality_natural.json` reports `OTHER = 25 / 600 = 4.17%`, so an 80-case natural sample would contain about 3 cases. The first observed `OTHER` examples are COVID case counts, pure biology/science, earthquakes, rainfall/weather, and temperature changes. That supports exclusion for v0.2 rather than giving `OTHER` a permanent super-type or folding it into `macro`.
