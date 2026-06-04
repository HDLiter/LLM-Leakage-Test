# R-1h 日期分桶 / 时期记忆(Date Bin,F_datebin)— 最终决策

**状态**: 锁定 2026-06-04(定义 + 候选池准入 + 分辨率)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若看不到明显的时期效应(某时期记忆显著冒尖),**降级为
exploratory**(只在报告里捎一句、不当主结论),不重开 R-1h 定义。

**审计轨迹**: 本候选池快速轮无独立白板;三步快速判 + 设计讨论内嵌于本文件。

---

## 1. 定义

时期记忆量的是:**是不是某个特定历法时期的新闻,被(训练时见过它的)模型记得
特别牢** —— 一个**非单调**的时期效应("偏偏某段时期突出",而不是"越近越熟")。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(历法位置是 metadata,把所有模型拿走还在) |
| 粒度 | **case 级、模型无关**(同一条新闻对所有模型是同一个时期;区别于 F_cutoff 的 case×model) |
| 泄露机制链环节 | **⑥ 时间定位**,但与 F_cutoff 的"单调 recency"不同 —— 抓的是非单调的时期突出 |
| 想找的机制 | **训练语料的时间构成**:某些时期的新闻在训练数据里被过度收录,**独立于当时报道了多少** |

---

## 2. 区别于 F_cutoff(非共线论证)

F_datebin 与 F_cutoff 都基于 `published_at`,但不共线:

- **F_cutoff** = `tanh((published − model_cutoff)/w)`,一条**单调**曲线(离 cutoff 越远
  越饱和),**case×model**。
- **F_datebin** = 时期,**case 级**。
- 在 **per-model(每个模型单独看)** 视角下,两者**都是发文日的函数**,在**单调成分上
  重叠**;F_datebin **唯一干净多出来的 = 非单调的时期偏离** —— "扣掉'越早越眼熟'那条
  平滑趋势之后,某个时期是否还异常冒尖"。
- 正因如此,编码必须是**无序分段**(找"某个"突出时期),不能用有序 / 单调形式
  (有序就退回 F_cutoff 能表达的范围了)。

**结论**:单调连续项与非单调时期偏离**互补,不共线**。

---

## 3. 因子值 + 分辨率

```text
period_bin[case] = 发文月(published_at)
```

| 字段 | 值 |
|---|---|
| 数据 | 复用 `published_at`(F_cutoff 已在用)→ **零新数据、零成本** |
| 主分辨率 | **按月**(4 年 ≈ 48 桶)。主实验 N=2,560 → 平均 ~53 条/月,够估单月记忆水平 |
| 稳健性分辨率 | **按季度**(≈ 16 桶):某月冒尖换成季度还在不在,在 = 不是单月碰巧 |
| pilot 注意 | pilot N=780 摊到月只 ~16 条/月、偏薄 → pilot 的"明显冒尖"闸门**按季度这种粗粒度看**,月级只看大概;按月细看留主实验 |
| 缺失 / 零值 | 每条新闻必有发文日 → 无缺失、无零值策略 |

**成本性质**:细分桶的成本 = **每桶样本量够不够**;月级在主实验样本量下够,故采用。

---

## 4. 怎么进分析(intent;具体统计规格 = R-4b)

> R1h 只声明分析**意图**;"怎么算 / 怎么检验 / 控制哪些变量"留 R-4b。

1. **主表征 = per-model(每个模型单独看)**:每个模型只在它**训练截止之前**的案例上算
   (cutoff 之后的新闻模型没见过 → 无记忆,不计入)。16 模型 → 各一套时期画像。
2. **数据覆盖**:split-tier fleet(各模型 cutoff 不同)让早期被几乎所有模型够到、晚期被
   晚 cutoff 模型够到 → 整个 case×model panel 的 pre-cutoff 单元撑起跨时期覆盖。
   **晚期只少数晚 cutoff 模型够到**(coverage 注脚:晚期聚合证据较弱,**非混杂**)。
3. **信号 = 冒尖**:找"越早越眼熟"平滑趋势**之外**的非单调时期偏离;冒尖那段 = "这时期好记"。
4. **总 → 分两步**:先看"各时期到底有没有真实差别"(一个总的检验)当 confirmatory 入口,
   再看"具体哪个时期冒尖"(细看)当 exploratory breakdown。
5. **跨模型聚合**:多个模型是否**独立地**在同一时期更牢 → 是,才是"时期内在记忆度"的强证据。

---

## 5. 混杂控制(不在此定义,挪 R-4b)

"某时期记得牢"可能只是因为"那阵报道多 / 涨跌猛"(报道多、动静大的新闻更易进训练数据、
被记住)。**要把"时期本身好记"和"那阵报道多 / 涨跌猛"分开,用到时已定义好的因子来控制**
(报道量 = F_salience / F_recur、涨跌 = F_mktmag,及 topic / entity 等)。

**R1h 不在这里定义"报道量 / 涨跌"怎么量** —— 这些因子尚未全部定稿,且控制是统计层的事;
**具体由 R-4b 在因子齐了之后统一处理**。此处仅留这条提醒,免得把本因子误读成"光看时期、
不管其它"。

**老实边界**:这只能扣掉**我们想到要量**的几个混杂;若有没量到的东西也随时期变,扣不掉。
故 claim 是"扣掉已知混杂后的残差时期效应",不是"纯粹时期"。

---

## 6. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b/c/d/f/g) |
| 比较对象 | vs F_cutoff(§2 已论非共线)、vs F_regime(§7)、vs F_salience / F_recur / F_mktmag(§5 混杂面) |
| 预期结果 | 通过(非单调时期偏离独立于单调 cutoff;中性记忆度独立于方向先验) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

---

## 7. 与 F_regime(R-1t)区分

都按时期,但:
- **F_regime** = 带**方向**的"风格先验"(如"2020 后成长占优"),属 Type A 闸门那族;
- **F_datebin** = **中性的时期记忆度**(不带方向,只问"这时期好不好记")。

一个测方向先验、一个测纯记忆,不重叠。

---

## 8. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显时期冒尖 → 降 exploratory(只报告)。
- **R-4b**:per-model vs 聚合、"相邻时期互相借数据 / 平滑"的具体做法、总检验规格、
  控制变量集(§5)、参考类、与 cutoff 的关系。R1h 只给意图与接口。
- **R-1e**:不预承诺进 primary;据 pilot 是否现明显时期效应 + 与其它因子区分度决定。
- **R-5(采样)**:若需,可按时期平衡 pre-cutoff 单元;R-5 全权。

---

## 9. B-2 schema requirements

`factor_provenance.run_inputs.per_task.date_bin`(字段命名 / 风格留 B-2 整体 session):

- `factor_name = date_bin`
- `framing_claim = period_intrinsic_memorability`
- `source = published_at`(复用,day precision)
- `row_unit = article_id`(case 级,模型无关)
- `primary_resolution = month`(~48 bins / 4y)
- `robustness_resolution = quarter`
- `encoding = unordered_periods`(非单调;具体建模留 R-4b)
- `estimable_on = pre_cutoff_case_model_cells_only`
- `primary_characterization = per_model`
- `confound_control = deferred_to_r4b_via_existing_factors`(salience / recur / mktmag / topic / entity)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_clear_period_effect`

### Provenance hashes
- S0 source snapshot hash · fleet cutoff manifest hash · sampling manifest hash(when factor values tied to a sampled frame)

---

## 10. 不在 R-1h 范围内

- "报道量 / 涨跌"的定义,以及混杂控制的操作化(挪 R-4b,§5)
- 具体统计方法("相邻时期互相借数据"怎么做、总检验、参考类、交互)= R-4b
- R-1e 因子最终选择
- ex-ante "时代"分段(若将来要更可解读的粗粒度,须事前定义防 ex-post;非本轮)
