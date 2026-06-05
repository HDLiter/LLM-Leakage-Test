# R-1l 结果幅度(Market Magnitude,F_mktmag)— 最终决策

**状态**: 锁定 2026-06-05(定义 + 操作化 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若**幅度与记忆度无明显关系**,或与 F_salience / F_mktcap **共线**
(VIF ≥ 10 或 \|r\| ≥ 0.90)→ **降级为 exploratory**,不重开 R-1l 定义。

**审计轨迹**: 操作化文献依据同 R-1k,见 `related papers/notes/Market-Outcome Labeling and
News-Return Operationalization.md`。

---

## 1. 定义

结果幅度量的是:**这条新闻后股价涨跌得多猛**(真实市场回报的绝对值)。问的是**涨跌剧烈的
case 是不是更容易被模型记住**。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(真实回报客观事实;模型无关) |
| 粒度 | **case 级、模型无关** |
| 泄露机制链环节 | **③④ 结果显著性**:结果强度是否调节记忆 |

---

## 2. 与 F_mktdir 共用窗口 / 序列 / 基准

**窗口、回报序列、基准口径完全沿用 R-1k**(同一条回报 r):
- **窗口** = Lopez-Lira & Tang 2023 时段映射套 A 股钟点(R-1k §2)。
- **一条序列**:F_mktmag = **\|r\|**,与 F_mktdir = sign(r) 是同一条 r 的两个读数(R-1k §3)。
- **基准** = raw 为主;市场调整 / 行业调整作稳健,**方向与振幅一起在 `r_adj` 上重算**(R-1k §5)。
- **无横截面排序**。

---

## 3. 因子值

```text
F_mktmag[case] = |r|          # 连续;主口径 raw |r|
```

| 决定 | 值 | 理由 |
|---|---|---|
| **形态** | **连续 \|r\|**(直接当连续因子) | 不分桶、不排序,最小设计;最大化保留强度信息 |
| **变换** | 原值;**log 作稳健**(若右偏明显) | A 股日 \|return\| 受 ±涨跌停限幅,非极端重尾;现强右偏再 log |
| **调节** | \|r_adj\|(减大盘 / 行业;与方向同步) | 见 R-1k §5 |

---

## 4. 涨跌停截断(censoring)

命中涨跌停时,观测 \|r\| 被制度**人为截断**(封顶 ±10%/±5%/±20%),是真实幅度的**下界**。

| 字段 | 值 |
|---|---|
| **主口径** | **含涨跌停 case**(与 F_mktdir 同一套 case,避免一个因子丢、另一个没丢),`magnitude_censored = 1` 标志 |
| **稳健性** | **删掉涨跌停 case 重跑** —— 验幅度效应不是被截断顶撑起来的 |
| 依据 | Qi 2023(`related papers/Qi 2023 Price Limits China ChiNext.pdf`):China ChiNext 10%→20% 改革确认 delayed price discovery / volatility spillover / trading interference → 封板幅度是截断观测 |
| 不做 | winsorize(制度已封顶,无需再截) |

---

## 5. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90** |
| 比较对象 | vs F_mktdir(绝对值 vs 符号,同一 r 耦合但不同维度;可做 mktdir×mktmag 交互查"大涨 vs 大跌")、vs F_salience / F_mktcap(报道量 / 市值,§1.5 角落 pilot sanity-check) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

---

## 6. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显幅度效应或共线 → 降 exploratory。
- **R-4b**:幅度×cutoff 交互规格、与方向的联合建模 / 交互、跨模型聚合。
- **R-1e**:据 pilot 决定。
- **R-5**:若需,可按幅度分层平衡采样。

---

## 7. B-2 schema requirements

`factor_provenance.run_inputs.per_task.market_magnitude`(字段命名 / 风格留 B-2):

- `factor_name = market_magnitude`
- `framing_claim = outcome_magnitude_modulates_memorization`(|return| case label)
- `source = a_share_quote`(同 R-1k)
- `row_unit = case`
- `return_window = lopez_lira_tang_2023_mapping_on_ashare_clock`(同 R-1k)
- `return_series = raw`(robustness: `market_adjusted` / `industry_adjusted`,与方向同换)
- `value = abs_return_continuous`(transform: `raw`;robustness `log`)
- `cross_sectional_ranking = none`
- `limit_policy = keep_with_censor_flag`(`magnitude_censored ∈ {0,1}`;robustness = drop limit-hit)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_magnitude_effect_or_collinear`

### Provenance hashes
- S0 source snapshot hash · quote source manifest hash · price-limit-ratio table hash
  · sampling manifest hash(when factor values tied to a sampled frame)

---

## 8. 引用(对应论文)

见 `related papers/`:Roll 1984(微结构,共用 R-1k 中性带依据)、Qi 2023(涨跌停截断)、
StockNet / Astock(收益标签先例)、Lopez-Lira & Tang 2023(窗口)。详见 INDEX「Market-Outcome
Labeling」节 + notes 方向笔记。

---

## 9. 不在 R-1l 范围内

- 方向编码 / 中性带(R-1k)、市值(R-1m)
- 涨跌停限幅比例的逐日生成(pilot 前操作化)
- 幅度×cutoff 的具体统计方法 = R-4b
- R-1e 因子最终选择
