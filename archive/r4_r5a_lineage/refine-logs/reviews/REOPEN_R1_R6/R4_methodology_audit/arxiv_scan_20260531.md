# arxiv 查新(2026-03 起,2026-05-31)

> **status**:查新产物,登记备查。范围 = 窄+近,两条线(竞品身位 + cutoff/resistance 方法论)。
> 48 篇候选 / 逐篇 triage / 5 篇标直接竞品。本文件是决策版精简;原始合成在 session transcript。
> **诚信注**:arxiv ID 由 workflow agent 联网抓摘要核对;少数 ID 标注待人工二次核(下载时验证)。

---

## 0. 核心结论

**身位仍空(对我们最有利的非发现)**:无一篇同时做到「因子受控刻画 + cutoff 锚 + 跨 cutoff
模型群 + 中文 CLS」。所有碰到问题空间的论文都至少差两轴 —— 要么检测/打标(二元)、要么
消除/造干净模型、要么按总体衰减排名,**没有一篇"刻画泄露如何随案例因子变化"**。

但周界收紧,两条要应对(见 §1)。

---

## 1. 直接竞品(5)

| arXiv | 标题 | 日期 | 重叠 | 我们怎么不同 |
|---|---|---|---|---|
| **2605.28359** | KTD-Fin: Memory-Controlled Benchmark for LLM Trading Agents | 2026-05-27 | **同 A 股(CSI300)+同 cutoff 威胁模型** → 抹掉"首个 A 股记忆基准"first-of-kind | 他们数据侧打码(4 级:bright/stock-blind/date-blind/blinded;**date-blind=真 ticker+真日期换相对日索引 `day_-3`,非删除**)+评交易 agent+Barra 归因;我们模型侧 cutoff 锚+跨 cutoff fleet+新闻→涨跌+四层框架+预注册。**互补,须加 vs KTD-Fin 段**。**注:他们的"date"是输入字段(可打码),与我们的"cutoff=模型训练截止点"是两种不同的时间,不冲突** |

> **KTD-Fin 已读全文(2026-05-31)关键结果 + mask-year 问题**:
> - **headline**:控制记忆(blinded × Barra 归因)后**选股技能基本塌成被动因子收益** —— 10 模型表面收益亮眼(Qwen3.6-plus +85%、Claude +59% 等,均跑赢 CSI300 +37%),但 Barra 拆解(Table 5)**选股 alpha 跨度 +0.2%~−77.8%,9/10 为负,仅 Claude Opus 4.7 ≈0(+0.2%)**。最干净塌缩:memory-only 模式 bright −0.16%(靠 ticker 先验乱交易亏钱)→ blinded **恰好 0.00%**(ticker 抹掉即持币不动)。结论=收益≠技能,LLM 交易"knowing(背)非 doing(做)"。
> - **mask-year 能否增强效果?→ KTD-Fin 证据是反方向**:(a) §3.3+Appendix A 实测 "**ticker 把手、非日历把手,携带主导预训练先验**":date-blind 下品牌/板块先验原样保留,stock-blind 下 rationale 塌成泛泛填充;(b) §4.3 探针 date±7天恢复最高仅 16%、joint 仅 1.5%(日期通道信号弱);(c) **结果表无 date-blind 性能列**(只 bright/blinded),date-blind 效应**他们没量化**。→ **对我们:mask 实体身份(C_anon)是强招、mask 日期是弱招;但 KTD-Fin 是纯价格无文本任务,date-blind 性能空白 = 我们 C_temporal/F_temporal 可填的洞,惟预期 date 通道偏弱**。
| **2603.26797** | MemGuard-Alpha: ...Cross-Model Disagreement | 2026-03-26 | 公开占先 "CMMD" 名+思路 | **坐实 E_CMMD 砍对**;US S&P-100/英文/检测-过滤工程管线(非受控 benchmark) |
| **2601.13770** | Look-Ahead-Bench: Standardized Look-ahead Bias for Finance LLMs | 2026-01-20 | 同 genre(标准化 look-ahead benchmark) | 用 alpha 衰减(混 regime)非 cutoff null;非因子受控;小英文 fleet;无预注册;无中文。**alpha-decay = lift 极先例,引** |
| **2512.23847** | A Test of Lookahead Bias in LLM Forecasts | 2025-12-29 | 量化新闻→收益泄露,分离记忆 vs 信号 | 单 prompt 观察性诊断(LAP=MIA 分回归);我们 cutoff 硬锚+fleet(识别更干净)。**LAP×准确率=lift 极典范,引/可借作一个算子对标** |
| **2510.07920** | Profit Mirage: ...FinLake-Bench + FactFin | 2025-10-09 | "profit mirage" 同主题 | 目标是 mitigation/造稳健 agent;agent P&L 单元;backtest-vs-live 非 cutoff。**反事实扰动=resistance 极先例,引** |

---

## 2. 方法论可借(P0 弹药 + 锚验证)

- **2504.14765** The Memorization Problem: 我们核心逻辑最近表述(训练覆盖期 non-identified,只 post-cutoff 验真) — **must-cite 动机**。
- **2603.11838** DatedGPT: perplexity 探针证明知识被 cutoff 年界定 — 外部坐实"cutoff=锚";其 12 个 dated-from-scratch 模型可当干净 baseline 负对照。
- **2602.18733** PAM (Prior Aware Memorization): lift-over-prior 操作化;55–90% "被记住"其实只是常见 — **near-mandatory for P0**,定义 memory_lift。
- **2601.07992** Fake Date Tests: lookahead-vs-context-bias 分解 ↔ 我们 estimand 张力。
- **2603.21658** Comparative Analysis of Memorization: **被记忆序列对扰动更敏感、学到内容抵抗删除** — resistance 极机制背书。
- **2603.03203** No Memorization No Detection: verbatim vs learned 是两 regime — 支持保留两类 estimand(逐字 + lift)。
- **2604.13997** Learned or Memorized (Code LLMs): memorization advantage = seen-unseen gap = lift 框架对照。
- **2605.15188** FutureSim: cutoff 当 contamination-resistant holdout(并发独立用)— 预防 reviewer "这只是 temporal holdout" + Brier-skill-vs-no-prediction baseline。
- **2605.13045** TempoMed-Bench: **cutoff 渐变非阶跃 + cutoff 前知识会被遗忘** — 直接喂 R-1a/R-4:只能为 memory_lift/resistance 辩护读 0、不能为 raw_score。
- 其余:2605.24818(paired-model counterfactual)、2603.19167(counterfactual 战略推理)、2605.24564 FinCAD(parametric look-ahead 命名)、2603.17692 BlindTrade(匿名化扰动对照)、2602.17234 All-Leaks(Shapley-DCLR)。

---

## 3. 顺带捞到(设计路上,挪因子扩展 decision)

- **年/日历因子**:2601.13658(LLM 偏好训练语料高频时间戳,持续);2605.13045(渐变非单调)。
- **事件类型→方向先验**:Janus-Q(2602.19919)= 62,400 篇新闻 + 10 类细粒度事件类型 + CAR 映射,现成 taxonomy。

---

## 4. 净结论

身位还在;砍 E_CMMD 被坐实;cutoff 不一刀切读零被外部支持;P0 两极都有弹药。
**plan 变更**:related work 加 vs KTD-Fin;P0 引 LAP/alpha-decay/PAM(lift)+ 2603.21658(resistance),
但**两类 estimand 不合并**(2603.03203/2604.13997 给的理由)。下一轮锁 estimand 前拉全文:
2601.13770(+GitHub)、2512.23847、2605.28359、2605.24564。
