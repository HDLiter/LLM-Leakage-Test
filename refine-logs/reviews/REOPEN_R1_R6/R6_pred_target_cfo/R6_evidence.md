# R-6 文献证据底稿:预测形式 + 真实收益评估记忆 + look-ahead 景观

> 用途:R-6 两件待定的文献证据,供下游 **「算子逐个分析」**(P_predict 预测形式)、
> **「estimand 逐个分析」**(涉及真实收益的记忆指标)直接取用。决定本身见同目录 `R6_DECISIONS.md`。
> 配套:72 篇文献总表 `R6_litsearch_master_table.md`(同目录;每篇:做了什么 / 引用 /
> 是否让模型预测涨跌 / 预测形式 / 是否用「预测 + 真实收益」测记忆 / 评估方法)。
> 术语:**resistance(抗扰动)** = 改文本后模型死抱原判断的程度;**Cutoff Exposure** = 案例相对
> 模型训练截止日的暴露度(连续因子,R-1a)。本文是**证据 + 选项**,不是已拍的设计。

## 一、预测的「形式」(喂待定 ①:P_predict 输出)

注:`Market-Outcome` 笔记已收 StockNet(二档 ±0.5%)/ Astock(分位三档)/ CMIN·FNSPID(二档),下表只列新增。

### 1.1 方向(分类) vs 数值(回归):主流是方向分类

| 论文 | 标识 | 模型输出形式 | 有没有幅度 |
|---|---|---|---|
| Lopez-Lira & Tang | arXiv:2304.07619 | positive / negative / **neutral** 三档情绪→交易信号 | 无 |
| Kirtac & Germano | WASSA 2024 | 标签正/非正(二档);LLM 出 sentiment score | 无;下游回归才估数值 |
| Koa et al. | OpenReview(匿名,仅方法证据) | **二档** 分类;Neutral/Mixed 当错误 | 无 |
| Gao/Jiang/Yan(LAP) | arXiv:2512.23847 | 新闻 **good/neutral/bad(三档)**;CapEx 五档;记自报信心+首token概率 | 新闻任务无 |
| Qizhao Chen 2025 | DOI 10.47852/bonviewFSI52025703 | **Up/Down/Same 三档 + 每类概率**;下游 Transformer 才回归价格 | LLM 不给最终价 |
| MarketSenseAI | arXiv:2401.03737 / 2502.00415 | **buy/hold/sell** 行动标签 | 不吐预期收益 |
| Yu et al. | arXiv:2306.11025 | 收益离散成 D5+…U5+ **多档幅度桶** | **有**(分桶) |
| Guo & Hauptmann | arXiv:2407.18103 | fine-tuned 表征+预测头出**连续/排序收益** | **有** |

**趋势**:新闻条件、prompt 型 LLM 研究最常见是「方向 / 情绪 / 行动」分类;**数值回归只见于有监督
fine-tuning / 嵌入+预测头**,不是「给一条新闻让聊天模型裸吐收益率」。

### 1.2 幅度 / 数值:有人做,但属另一套

反例:Yu et al.(分桶)、Guo & Hauptmann(连续,靠 FT)。代价:① 把任务从「方向变没变」变成「能不能
给同尺度数值」(引入算术/单位/窗口差异);② 与记忆探针混淆(吐出接近真值可能是背到也可能瞎准);
③ resistance 的「变没变」高度依赖阈值。→ 更适合**另作探针**(P_extract/P_recall),不混入 P_predict。

### 1.3 几档 + 中性:三档有先例(行为档,非收益阈值)

二档(Kirtac&Germano、Koa,后者把中性当错)/ 三档(Lopez-Lira&Tang、LAP、Qizhao Chen、MarketSenseAI)/
五档·多档(LAP CapEx、Yu)。中性 = 模型「没清晰方向」的**行为判断档**,不是用收益阈值卡出来的。

### 1.4 信心 / 概率:被点名不可靠 → 宜仅作诊断

**Chen/Didisheim/Somoza《Out of the (Black)Box》**:declared confidence「opaque、biased、unstable、
model-dependent」,主张用 token 条件概率而非自报信心。**Chen/Green/Gulen/Zhou**(arXiv:2409.11540):
80% 区间实测覆盖 69–77%。同行多把信心/概率当**诊断 / 下游特征**,不当承重真值。

> 以上是证据;**最终输出形式(档位 / 信心刻度 / memory_flag / evidence 取舍 / 解析约定)留算子逐个分析拍板。**

## 二、真实收益用于「评估记忆」(喂待定 ②)

评价端用真实收益测记忆 / look-ahead 已成簇,与主量 resistance 互补(一个看「文本改了死不死抱判断」、
一个看「历史期表现是否异常好」):

| 论文 | 标识 | 评价端怎么用真实收益 | 当记忆信号的方法 |
|---|---|---|---|
| LAP | arXiv:2512.23847 | 真实次日收益当回归因变量 | `预测 × 记忆代理(LAP)` 交互;OOS placebo 不显著 |
| Look-Ahead-Bench | arXiv:2601.13770 | 组合 alpha | `alpha_decay = 样本外 − 样本内`;两期市场配相近 |
| Glasserman & Lin | arXiv:2309.17322 | 交易 P&L | 同模型 样本内 vs 外 + 原始 vs 匿名 差分 |
| FinCAD | arXiv:2605.24564 | 去记忆前后回测收益/Sharpe | 样本内降、样本外不动 = 差分 |
| Profit Mirage | arXiv:2510.07920 | 真实 P&L/Sharpe | 回测 vs 泛化衰减 50–72% |
| KTD-Fin(A股 CSI300) | arXiv:2605.28359 | 交易收益 + Barra 归因 | **提醒**:raw 收益多是 market/style,非选股 alpha |
| Lopez-Lira/Tang/Zhu;Didisheim | arXiv:2504.14765;Econ. Letters | 历史收益数值召回 | 零上下文召回当记忆代理(见过真值后能力不可识别) |

### 设计可借的点(供 estimand 逐个分析参考,非锁定)

- **双轴差分去噪**:① **同模型 cutoff 前 vs 后**(差掉模型能力);② **同一条新闻、见过它 vs 没见过它的
  模型**(差掉新闻采样质量,靠 16 模型跨 cutoff fleet)。合并 = `命中 / 分数 ~ 暴露 + 模型FE + 案例FE`,
  暴露轴 = 连续 **Cutoff Exposure**;**无记忆基线 = post-cutoff / 低暴露档的水平**(非 0)。
- **必备控制**:市场 / 行业调整后收益(KTD-Fin:raw 收益多是 beta/style);扣一般先验(PAM:别把行业/
  实体常识当记忆);winsorize 极端值。
- **候选最小形态(选项)**:方向命中率随暴露的变化;`signed market-adjusted return`(让幅度进评价,但
  **不做 full P&L / Sharpe、不让模型预测数值**——A 股涨跌停 / T+1 / 融券限制使可交易 P&L 太重)。

> 以上是证据与选项;**具体形态 / 是否 confirmatory / 统计检验留 estimand 逐个分析拍板。**

## 三、look-ahead × LLM-收益预测 景观(related work 用)

这条线 2023 起步,半年内(Glasserman & Lin 2023.09)就把 look-ahead / 记忆污染列为头号方法论病,
2024–2026 长出「检测泄露 + 造 point-in-time 模型 + 去偏」的防御性子领域,至今活跃。

| 年 | 论文 | 标识 | 一句话 |
|---|---|---|---|
| 2023.04 | Lopez-Lira & Tang | arXiv:2304.07619 | ChatGPT 读标题选超额收益组合;开山作 |
| 2023.09 | Glasserman & Lin | arXiv:2309.17322 | 首个系统指出 GPT 情感→收益回测撞 look-ahead;拆 look-ahead vs distraction |
| 2024 | Sarkar & Vafa | SSRN:4754678 | 直接 look-ahead 检验:对象须在「当时可见信息集」下不可预测;根治靠 PiT 训练 |
| 2024 | Cheng「Dated Data」/ Drinkall「Time Machine GPT」 | 2403.12958 / 2404.18543 | 有效 cutoff 常早于标称 / PiT 模型 |
| 2025 | **Lopez-Lira/Tang/Zhu「Memorization Problem」** | arXiv:2504.14765 | 见过真实值后预测能力**不可识别** |
| 2025 | **Didisheim/Fraschini/Somoza** | Econ. Letters | 零上下文背历史收益当记忆代理;加同日市场上下文会加重大模型污染 |
| 2025 | He「ChronoBERT」/ Merchant&Levy / Li「Profit Mirage」 | 2502.21206 / 2512.06607 / 2510.07920 | PiT 模型 / 推理时去偏 / 回测后收益衰减 50–72% |
| 2025-12 | **Gao/Jiang/Yan「LAP」** | arXiv:2512.23847 | LAP 与准确率正相关=look-ahead;新闻三档 |
| 2026 | **Li/Wang/Ma「FinCAD」** | arXiv:2605.24564 | 把「记得历史涨跌」当污染**去清除**;pre/post-cutoff 交易表现差 |
| 2026 | Zhang「All Leaks Count」/ Benhenda「Look-Ahead-Bench」/ Yan「DatedGPT」/ Zhu「KTD-Fin」 | 2602.17234 / 2601.13770 / 2603.11838 / 2605.28359 | claim 级污染检测 / alpha 衰减基准 / PiT 模型 / A股 masking+Barra |
| 2026 | Chen & Pu「Agentic Nowcasting」 | arXiv:2601.11958 | 最像「LLM 真能预测」,但靠实时/PiT 采集防污,不喂历史未来结果 |

**站位**:我们是**诊断 / 测量侧**(中文 A 股因子受控记忆基准),别被读成又一篇「LLM 预测收益」;
现有 look-ahead 检测器几乎全是英文/美股、任务级、靠白盒对数概率。可直接引:FinCAD、Sarkar-Vafa、
Didisheim、Lopez-Lira-Tang-Zhu、LAP。

## 四、引用质量 + 修正

- **引用数多为「未核实」**:S2/OpenAlex 对 2026 新预印本不稳定;表中宁标「未核实」不瞎写。正式文献表前 API 批量补。
- **引用串台修正(已核实,待改)**:既有笔记 `temporal_lookahead.md` 里 **Nylund et al. 2024,*Time Is
  Encoded in the Weights of Finetuned Language Models***(time vectors,ACL 2024,arXiv:2312.13401)的摘要
  **串台**成了 **Engels et al.《Not All Language Model Features Are Linear》**(arXiv:2405.14860,sparse
  autoencoder / 多维特征)。**待办**:改 `related papers/notes/temporal_lookahead.md`。

---

*生成 2026-06-06。72 篇总表 = 同目录 `R6_litsearch_master_table.md`;窄搜原始备忘(scratch)`temp/r6_litsearch_prediction_form_…`、`…eval_returns_…`。*
