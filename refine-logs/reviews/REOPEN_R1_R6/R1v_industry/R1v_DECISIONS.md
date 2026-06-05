# R-1v 行业(Industry,F_industry)— 最终决策

**状态**: 锁定 2026-06-04(定义 + 候选池准入 + 分辨率)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若**行业间记忆度无明显差异**,或与 F_salience / F_mktcap / F_mktmag
**共线**(VIF ≥ 10 或 \|r\| ≥ 0.90)→ **降级为 exploratory**,不重开 R-1v 定义。

**审计轨迹**: 本候选池快速轮无独立白板;三步快速判 + 设计讨论内嵌于本文件。

---

## 1. 定义

行业量的是:**这只标的属于哪个行业 / 板块**(银行 / 医药 / 半导体 …)—— 一个
**sign-free**(只问"哪个行业",**不带方向、不带趋势**)的固定归属属性。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(行业归属是固定属性;把所有模型拿走,"这是只银行股"还成立) |
| 粒度 | **entity / sector 级**(同一标的 → 同一行业) |
| 泄露机制链环节 | **② 曝光时长 / ③ 可记忆性的板块层聚合**:某些行业的标的是否整体更易被记 |

**带方向那版分出**:"某板块这阵在涨 / 风格占优"(板块趋势)= **F_regime(R-1t)**,
需真实股价、事后回头看(ex-post),绑 Type A 闸门,不在本因子。这里进池的是 sign-free 的
"是哪个行业"。

---

## 2. 区分度:主要共线风险 + 诚实定位

行业的记忆通道**大概率经别的因子流走**——某些行业**报道更多(F_salience)/ 市值更大
(F_mktcap)/ 涨跌更猛(F_mktmag)**。F_industry 捕捉的是"扣掉这些后,行业归属本身是否
仍调节记忆"。

**诚实定位**:行业的**独立信号 a-priori 比 topic 弱**(topic 之于 recur 是清晰的另一条腿;
行业之于 salience/cap 则更可能被吸收)→ **pilot 更可能把它降 exploratory**。但这是**pilot
据数据判**,不是 pre-DROP —— 候选池可 >4、降级零 alpha 成本,值得 pilot 看一眼。

---

## 3. 因子值 + 分辨率

```text
industry_class[case] = 中证一级行业(11 类),取事件日当时的归属
```

| 字段 | 值 |
|---|---|
| 分类标准 | **中证(CSI)行业分类**(四级结构:一级 11 / 二级 35 / …) |
| 主分辨率 | **中证一级 11 行业**(类少 → 样本厚、power 好、叙事聚焦) |
| 稳健性分辨率 | **中证二级 35 行业**(更细;主结论是否依赖粗/细) |
| 防 ex-post | **用事件日当时的行业归属(point-in-time)**,不用事后重分类,避免后视镜信息 |
| 数据可行性 | **中证分类数据的 API 可行性待 pilot 前调查**(point-in-time 归属能否拉到) |

---

## 4. 怎么进分析(intent;统计规格 = R-4b)

> R1v 只声明分析**意图**;统计规格留 R-4b。

1. **无序分类**:confirmatory 入口 = **总检验"记忆度在行业之间有没有差异"**(omnibus);
   **哪个行业冒尖**当 exploratory 细分。结构同 F_datebin(R-1h)/ F_topic(R-1u)。
2. 分类因子的 confirmatory 主张读作"**记忆度因行业而异**",非"随因子单调升"。

---

## 5. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用既往) |
| 比较对象 | vs F_salience / F_mktcap / F_mktmag(§2 主共线风险)、vs F_topic |
| 预期结果 | 共线风险偏高(§2);正式检查在 pilot |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

---

## 6. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显行业差或与 salience/cap/mktmag
  共线 → 降 exploratory。
- **pilot 前**:调查中证行业分类的数据 API 可行性(point-in-time 归属)。
- **R-4b**:无序分类总检验规格、跨模型聚合、与 salience/cap 的联合建模。
- **R-1e**:据 pilot 行业差异 + 区分度决定;a-priori 较弱(§2),降级概率高于 topic。
- **F_regime(R-1t)**:带方向的板块趋势,ex-post + Type A 闸门,独立 session,不在本因子。

---

## 7. B-2 schema requirements

`factor_provenance.run_inputs.per_task.industry`(字段命名 / 风格留 B-2 整体 session):

- `factor_name = industry`
- `framing_claim = sector_intrinsic_memorability`(sign-free)
- `source = csi_industry_classification`(point-in-time,事件日当时归属)
- `row_unit = entity_id`(映射到 case)
- `primary_resolution = csi_level1`(11 类)
- `robustness_resolution = csi_level2`(35 类)
- `encoding = unordered_categorical`(omnibus 入口;per-sector 细分 exploratory;建模留 R-4b)
- `point_in_time = true`(防 ex-post 重分类)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`(主比较对象 = salience / mktcap / mktmag)
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_sector_difference_or_collinear`
- `data_feasibility = csi_classification_api_to_investigate_pre_pilot`

### Provenance hashes
- CSI classification snapshot / version hash(point-in-time)· sampling manifest hash(when factor values tied to a sampled frame)

---

## 8. 不在 R-1v 范围内

- 带方向的板块趋势(F_regime,R-1t,ex-post + Type A 闸门)
- 中证分类 API 的具体落地(pilot 前调查)
- 无序分类的具体统计方法 = R-4b
- R-1e 因子最终选择
