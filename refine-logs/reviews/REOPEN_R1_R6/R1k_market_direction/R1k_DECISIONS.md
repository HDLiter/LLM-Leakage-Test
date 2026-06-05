# R-1k 结果方向(Market Direction,F_mktdir)— 最终决策

**状态**: 锁定 2026-06-05(定义 + 操作化 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若**方向间记忆度无明显差异**,或与 F_mktmag / F_salience **共线**(VIF ≥ 10
或 \|r\| ≥ 0.90)→ **降级为 exploratory**,不重开 R-1k 定义。

**审计轨迹**: 操作化文献依据见 `related papers/notes/Market-Outcome Labeling and News-Return
Operationalization.md`(两轮 Codex 检索 + 两次核验 workflow);逐字出处见各节。

---

## 1. 定义

结果方向量的是:**这条新闻发生后,股价实际是涨 / 平 / 跌**(真实市场回报的方向)。问的是
**导致上涨的新闻是不是比导致下跌的更容易被模型记住**(涨 / 跌的记忆不对称)。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(真实回报是市场生成的客观事实;把所有模型拿走还在) |
| 粒度 | **case 级、模型无关**(同一新闻对所有模型同一个结果标签) |
| 泄露机制链环节 | **④ 结果方向**:方向是否调节记忆 |

**合法性(案例标签 ≠ directional 红线)**:真实股价在此作**案例标签**(给 case 贴"它涨了/跌了"
的客观事实),合法。红线针对的是"**文本**传达的方向不能用真实股价倒推";这里不涉及文本方向,
也不把股价喂给模型。

---

## 2. 回报窗口(对口先例:Lopez-Lira & Tang 2023)

**窗口映射照搬 Lopez-Lira & Tang 2023 的"发布时刻 → 交易窗口"规则**(`related papers/
Lopez-Lira ChatGPT Stock Returns.pdf`,arXiv:2304.07619;原文逐字:"If a piece of news is released
before 6 a.m. … we enter the position at the market opening and exit at the close of the same day. If
the news is released after 6 a.m. but before the market close … enter at the market close … exit at
the close of the next trading day. If … after the market closes … enter at the next opening price and
exit at the close of the next trading day."),**套 A 股交易钟点**(开 9:30 / 收 15:00 / 午休
11:30–13:00 归"盘中"桶;6 a.m. 截点沿用,美股开盘 ≈ A 股开盘):

| 发文时刻(北京时间) | 进 → 出 | 回报 r |
|---|---|---|
| < 6:00 | 当日开 → 当日收 | `收(d)/开(d) − 1` |
| 6:00 – 15:00 | 当日收 → 次日收 | `收(d+1)/收(d) − 1` |
| ≥ 15:00 | 次日开 → 次日收 | `收(d+1)/开(d+1) − 1` |

| 字段 | 值 |
|---|---|
| 主数据 | **akshare 日线**(全覆盖、口径统一、可预登记) |
| secondary | **baostock 15 分钟**,锚发文那一秒 → 当日收;**仅当覆盖审计通过**才挂(部分覆盖→缺失偏倚,不作主) |
| 稳健性 | `[t, t+1]` 两日窗 |

---

## 3. 一条序列、无截面排序(方向 / 振幅耦合)

**方向与振幅是同一条回报序列 r 的两个读数**:方向 = sign(r) + 零中心带,振幅(R-1l)= \|r\|。

- **不做横截面排序**(不按全体股票排名):横截面排名会把方向(相对)与振幅(绝对)脱钩,弃。
- 排序若用到,只在**我们自己的 case 池**上,不按天(池化)。
- 调节(减大盘 / 行业)= 换序列、**方向与振幅一起在 `r_adj = r − benchmark` 上重算**(减法,见 §5)。

---

## 4. 三分类 + 固定中性带

```text
F_mktdir[case] = up    if r ≥ +x
                 down  if r ≤ −x
                 neutral if |r| < x      # 零中心、绝对
```

| 决定 | 值 | 依据 |
|---|---|---|
| **编码** | **三分类 up / neutral / down**(非二分) | 近零小动方向是噪声,中性带隔离真方向 |
| **中性带 x(主)** | **±0.5%** | **锚 StockNet(Xu & Cohen 2018,最被引 384)** 的 ~0.5% 噪声地板;其 ±0.55/−0.5% 不对称为美股漂移配平,**我们对称化**。`related papers/StockNet …pdf`,README 逐字:"labeled as up and down when movement percent ≥0.55% or ≤−0.5%" |
| **robust 带集** | **{0%(无中性=纯二分,对照 CMIN/FNSPID)、±1%、±1.5%}** | bracket 主值 |
| **不丢样本** | 全覆盖,每个 case 一个标签 | 区别于 Astock / StockNet 的"丢中间带"(Astock Eq.1 a/b/c/d=20/40/60/20 丢 ~40%) |
| **机制依据** | **Roll 1984**(微结构 bid-ask bounce 噪声) | `related papers/Roll 1984 …pdf`,Abstract 逐字:"trading costs induce negative serial dependence in successive observed market price changes … Spread = 2√(−cov)" → 近零收益 = 噪声、该中性化 |

**诚实标注(预登记须写)**:中性带数值**无权威锚**——对抗检索证实各数据集自定且互相矛盾
(StockNet ±0.55/−0.5%、Astock 分位、CMIN 二分、FNSPID 无中性带、triple-barrier 波动率缩放)。
±0.5% 是**预登记设计选择**,合法性 = StockNet 先例 + Roll 微结构机制,非综述背书。A 股是否需更宽带
由 robust 集 + pilot 上 Roll 有效价差估计**实测**,不先验断言。

---

## 5. 基准:raw 为主

| 口径 | 用途 | 依据 |
|---|---|---|
| **raw 回报** | **主标签** | case 是"描述性结果标签"非因果 CAR;实际涨跌即结果。Lopez-Lira 本身因变量 = raw,abnormal 仅 robustness Table 9 |
| **市场调整**(减宽基)/ **行业调整**(减行业) | 稳健性(方向 + 振幅一起重算) | 剥宏观普涨跌;减法、一步、无估计窗 |
| **市场模型 CAR** | **不用** | 需 120–250 日估计窗 + 估 β,对"标签"过重、引入 researcher DoF。MacKinlay 1997:abnormal = actual − normal,是**事件研究 estimand 所需**,非标签所需 |

---

## 6. 涨跌停

**保留**命中涨跌停的 case:**封板方向 = 真方向**(信息更强),`limit_hit ∈ {none, up, down}` 标志。
制度边界 ±10%(主板)/±5%(ST)/±20%(创/科),逐日逐股按板块/风险警示状态生成(pilot 前)。
延迟价格发现依据:Qi 2023(`related papers/Qi 2023 Price Limits China ChiNext.pdf`)。幅度截断由
**R-1l** 处理,方向不受影响。

---

## 7. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90** |
| 比较对象 | vs F_mktmag(符号 vs 绝对值,同一 r 耦合但不同维度)、vs F_salience / F_recur(报道 / 复现,§1.5 正交轴)、vs F_structdir(实现方向 vs 事前先验) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

---

## 8. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显方向效应或与 mktmag/salience 共线 → 降 exploratory。
- **R-4b**:方向×cutoff 交互的统计规格、跨模型聚合、控制变量、与振幅的联合建模。
- **R-1e**:据 pilot 方向效应 + 区分度决定。
- **R-5**:若需,可按结果方向平衡采样。

---

## 9. B-2 schema requirements

`factor_provenance.run_inputs.per_task.market_direction`(字段命名 / 风格留 B-2):

- `factor_name = market_direction`
- `framing_claim = outcome_direction_modulates_memorization`(sign-of-return case label)
- `source = a_share_quote`(akshare daily 主;baostock 15min secondary)
- `row_unit = case`(模型无关)
- `return_window = lopez_lira_tang_2023_mapping_on_ashare_clock`(<6:00 open→close;6:00–15:00 close→next_close;≥15:00 next_open→next_close)
- `return_series = raw`(robustness: `market_adjusted` / `industry_adjusted`,方向振幅同换;减法)
- `cross_sectional_ranking = none`
- `encoding = three_class`(up / neutral / down;全覆盖不丢样本)
- `neutral_band = abs_return_lt_0.5pct`(robustness: `{0, 1.0, 1.5}pct`)
- `band_basis = stocknet_noise_floor + roll1984_microstructure`(no authoritative numeric anchor; pre-registered)
- `limit_policy = keep`(limit direction = true direction;`limit_hit ∈ {none,up,down}`)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_direction_effect_or_collinear`

### Provenance hashes
- S0 source snapshot hash · quote source manifest hash(akshare/baostock + 复权口径)· fleet cutoff manifest hash
  · price-limit-ratio table hash · sampling manifest hash(when factor values tied to a sampled frame)

---

## 10. 引用(对应论文)

见 `related papers/`:Lopez-Lira & Tang 2023(窗口)、StockNet(±0.5% 锚)、Astock(三分类形 / 丢弃对照)、
CMIN · FNSPID(二分 / 无中性带对照)、Roll 1984(中性带机制)、Qi 2023(涨跌停)。方法背景(非阈值权威):
MacKinlay 1997 等,见 INDEX「Market-Outcome Labeling」节 + notes 方向笔记。

---

## 11. 不在 R-1k 范围内

- 幅度截断(R-1l)、市值(R-1m)
- 中性带具体数值的 pilot 后确认(预登记 ±0.5%,robust 集已定)
- 方向×cutoff 的具体统计方法 = R-4b
- R-1e 因子最终选择
