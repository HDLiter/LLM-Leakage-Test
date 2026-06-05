# R-1m 市值(Market Cap,F_mktcap)— 最终决策

**状态**: 锁定 2026-06-05(定义 + 操作化 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若**市值与记忆度无明显关系**,或与 F_salience **共线**(VIF ≥ 10 或
\|r\| ≥ 0.90)→ **降级为 exploratory**,不重开 R-1m 定义。

**审计轨迹**: 三步快速判 + 操作化决定内嵌于本文件。

---

## 1. 定义

市值量的是:**这只标的有多大**(事件当时的总市值)。问的是**大盘股是不是比小盘股更容易被
模型记住**(规模 → 曝光 / 显著性)。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(市值是公司客观属性;把所有模型拿走还在) |
| 粒度 | **entity 级**(映射到 case);**非收益**(区别于 F_mktdir/mktmag) |
| 泄露机制链环节 | **②③ 曝光 / 可记忆性**:规模是否调节记忆 |

---

## 2. 因子值

```text
F_mktcap[case] = log(market_cap @ 事件日当时)
```

| 决定 | 值 | 理由 |
|---|---|---|
| **取值时点** | **事件日当时(point-in-time)** | 防 ex-post:用事件后市值会泄漏未来;point-in-time 干净 |
| **变换** | **log** | 市值跨公司极重尾(数量级差异),log 标准做法 |
| **不涉及** | 窗口 / 基准 / 中性带 / 涨跌停 | F_mktcap 是公司规模属性,**与回报无关**,R-1k/l 那套不适用 |
| 缺失 | 每个上市标的有市值 → 无缺失 | |

---

## 3. 区分度检查(主要风险:vs F_salience)

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90** |
| 比较对象 | **vs F_salience(主风险)**、vs F_mktdir / F_mktmag(规模 vs 结果,正交) |
| 预期结果 | 与 salience 可能中度相关(大盘股常被报道多),**§1.5 已列为 pilot 顺手 sanity-check 的角落**;正式检查在 pilot |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

**概念区分度**:F_salience 是**报道曝光强度**(媒体提及量),F_mktcap 是**公司规模**——两者
不同生成过程(一只小盘股可在丑闻期被高度报道;一只大盘蓝筹可长期低报道)。pilot 查实操相关。

---

## 4. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显市值效应或与 salience 共线 → 降 exploratory。
- **R-4b**:市值×cutoff 交互规格、与 salience 的联合建模。
- **R-1e**:据 pilot 决定。
- **数据**:市值随行情拉取(akshare/baostock);point-in-time 口径与 §1.5 行情族同源。

---

## 5. B-2 schema requirements

`factor_provenance.run_inputs.per_task.market_cap`(字段命名 / 风格留 B-2):

- `factor_name = market_cap`
- `framing_claim = firm_size_modulates_memorization`
- `source = a_share_quote`(market cap @ event date)
- `row_unit = entity_id`(映射到 case)
- `point_in_time = true`(事件日当时,防 ex-post)
- `transform = log`
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`(主比较对象 = F_salience)
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_size_effect_or_collinear_with_salience`

### Provenance hashes
- S0 source snapshot hash · quote source manifest hash(market-cap @ event date,point-in-time)
  · sampling manifest hash(when factor values tied to a sampled frame)

---

## 6. 不在 R-1m 范围内

- 方向 / 幅度(R-1k / R-1l)
- 带方向的板块 / 规模先验(若有,归 F_regime / Type A 闸门)
- 市值×cutoff 的具体统计方法 = R-4b
- R-1e 因子最终选择
