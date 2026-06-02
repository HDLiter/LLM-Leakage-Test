# R-4 下一轮构念效度讨论大纲(开放议程)

> **⚠️ P0 段 SUPERSEDED 2026-05-31** by `R4_construct_validity_decisions.md`(定调)+ `.scratch/session_kickoff_p0_estimand_paradigm.md`(P0 kickoff)。
> 本文件 P0 原写成"resistance vs prediction-lift 两范式逐条敲、不二选一";该框架已**溶解** —— **resistance 是框架实存的唯一主量,prediction-lift 不是可平起平坐挑选的仪器,而是"动机→测量"那道桥的名字**。
> **P0 scope 以 kickoff 为准,下方 §P0 正文仅留作 audit trail,勿据其开 session。** P2–P7 仍是有用的 scope 提示(但 null 判据已按 `R4_construct_validity_decisions.md` D2 分层,见各条)。

**Status**: **P0 已定稿 → `P0_DECISIONS.md`(2026-05-31);P2–P7 仍 OPEN — 议程,非决策**;供 R-4 下一轮 walkthrough 逐条敲定。
**来源**: novelty factor session(R-1d,2026-05-30,主对话 4 轮第一性原理推理)+ codex clean-room review(`.scratch/codex_runs/20260530-fpscope/final_detailed.md`)。
**上游**: 接 `algorithm_deepaudit.md` §8 agenda 第 2/3 条(自我证伪 null 判据 + estimand 去留辩论);承 construct-validity 框架(数据集=测量仪器,cutoff=验证锚,post-cutoff null=效度锚)。
**下游(2026-05-31 R-4 session 已把一批 leans 升为定调)**: `R4_construct_validity_decisions.md`(D1–D9)+ `four_layer_candidate_pools.md`(四池)。

---

## 背景:这些条目怎么浮出来的(浓缩,非结论)

novelty session 想给 benchmark 加一个 case-level「信息新颖度 / 答案可推断性」因子。4 轮推理 + codex review 的净结果:

- **三层区分**(owner 推出):**A** 金融常识(好,非问题)/ **B** 预测分析能力(好;含 **B1** 稳定能力、**B2** 依赖更早领先信息 A 的推断)/ **C** 死记硬背具体 case 后验结果(坏 = leakage)。
- **危害定义**:C 在历史回测产生虚假 alpha;粗略 = pre-cutoff 表现 − post-cutoff 表现。cutoff 的 pre/post 相减自动扣掉 A 和稳定的 B1。
- **novelty 当「可推性筛子」被否**:剔掉「能从更早合法信息 A 推出 B」的 case = 惩罚实盘合法能力(owner 致命质疑)。共识:**novelty 不当主因子**。
- **codex 抓出更深的根**:这 4 轮其实在两个不同 estimand 范式间滑动而不自知 —— 官方文档是 **resistance 范式**(E_FO = False Outcome Resistance,抗反事实扰动,不碰股价,见 §4.6),而 novelty session + proposal §2.2 动机把 **prediction-lift 范式**(预测真实涨跌的 pre/post 抬升 = false alpha proxy)推到中心。「post null 该不该归零」的争议,大半是这个范式张力 + E_FO 命名漂移造出来的假争议。

⇒ 所有 novelty / null 判据 / B2 合法性的争议,都 **gated on「核心 estimand 范式怎么定」**。故下列条目以 P0 范式为先决。

---

## 开放条目(建议顺序,可调)

### P0 — 核心 estimand 范式 【CLOSED 2026-05-31 → 定稿 `P0_DECISIONS.md`;推理 `P0_audit_trail.md`;开场白 `.scratch/session_kickoff_p0_estimand_paradigm.md`】

> **⚠️ 以下 7 行是 2026-05-30 的旧框架,已被溶解,留作 audit trail。** 当前 P0 scope:
> **resistance 是框架实存的唯一主量**(E_FO/E_SR/E_NoOp 全是 same-case clean↔扰动 差值);
> **"prediction-lift" 不是可平起平坐挑的仪器**,而是"动机 false-alpha ↔ 测量行为指纹"那道桥的名字;
> 真正要敲的是 **(Q1)** resistance 怎么和"一般方向先验"分开 + **(Q2)** 到 false-alpha 那座桥是纯论证还是要碰真实收益 + **(Q3)** prediction-lift 只剩 exploratory/因子角色吗 + **(Q4)** §4.6 改不改。完整开场白见 kickoff。

<details><summary>旧框架(audit trail,勿据此开 session)</summary>

- 张力:**resistance 范式**(官方:抗扰动对比量、不碰股价、null 天然≈0)vs **prediction-lift 范式**(预测真实结局的 pre/post 准确率差、需 ground truth、直接对上 false alpha 动机)。
- 两者测**不同的记忆指纹**,不是同一个量的两种算法。
- 待敲(逐条过,**不预先二选一**):
  - resistance 范式单独能不能扛主记忆 claim?它离「虚假 alpha」动机隔几层?
  - prediction-lift 范式的代价(ground truth、撞 §4.6、能力混淆)各有多重?
  - 要不要并存(resistance 当主、干净;prediction-lift 当「桥到 false alpha」的佐证)?并存的统计 / 叙事成本?

</details>

### P1 — 命名漂移拆解 【CLOSED 2026-06-02 → `P1_DECISIONS.md`】
- E_FO 在 `MEASUREMENT_FRAMEWORK.md` L180 = False Outcome **Resistance**;在 novelty session 口头 = Future Outcome **prediction**。**同名两物。**
- 待敲:把 `raw_outcome_score` / `memory_lift` / `false_outcome_resistance` 三个量各起名;逐处核对 algorithm_deepaudit / MEASUREMENT_FRAMEWORK / proposal 里每个「E_FO」指哪个。

### P2 — post-cutoff null 的精确措辞 【ABANDONED 2026-06-02】
> **弃因**:在实验前逐个估计量钉死"post-cutoff 该读几"没有道理——那是实验要去测的,不是事前规格。
> 此外,"post-cutoff"这个词用在 E_PCSG 上不准确:E_PCSG 是两个 cutoff 不同的模型之间的差值,不存在单一的"post-cutoff 模式";BL2(事件在所有模型 cutoff 之后)那批案例的差值预期 ≈ 0,是对 BL2 子集的分析预期,不是 E_PCSG 本身的属性。E_CTS(绝对熟悉度)的 logprob 也不可能归零——中文财经文本的结构模式本身就给出一定熟悉度。
> P0 / P1 已把分层 null 的框架定清(E_PCSG 有干净锚、resistance 不预测 cutoff 行为、模型预测 ≠ 0);逐估计量精确数值留实验结果。原议题的命名漂移部分已被 P1 吸收。

### P3 — 任务信息集协议 【ABANDONED 2026-06-02,并入 R-6】
> **弃因**:P0 定了主量 = resistance(抗扰动),不是预测准确率。在 resistance 下,模型用参数记忆推出什么不重要,重要的是面对扰动变体时预测变不变——"信息集怎么定→影响什么算记忆"这个争论不再咬人。剩下的实操问题(P_predict prompt 带不带上下文)是 prompt 工程,归 R-6。

### P4 — 预测目标 / horizon / ground truth 【R-6 范围,P0 逼其前置】
- prediction-lift 范式需真实涨跌 ground truth + horizon + 收益口径 → 撞 §4.6「confirmatory estimand 不与真实股价对照」;resistance 范式不需要。
- 待敲:目标标签(情感 / 方向 / 收益)、horizon、ground truth 来源;§4.6 改不改。

### P5 — novelty 最终归宿 【ABANDONED 2026-06-02,并入 R-5】
> **弃因**:P0 走 resistance 范式 + P3 abandoned → 复活条件不满足,novelty 不当因子已成定论。退化案例(机械恒等 / 日历已知 / 标签文中明示等)是否需要采样过滤,归 R-5(采样)决策。

### P6 — false alpha 作为 research claim 的锚定与边界 【ABANDONED 2026-06-02,P0 已回答】
> **弃因**:P0 §2 已完整回答——桥 = 纯论证、红线 = "测会导致虚假收益的记忆"(不是"测虚假收益本身")、承重词 = 记忆/抗扰动族、三通道 checklist 留结果分析。§2.2 的实际措辞是写论文时的事,不需要独立设计 session。

### P7 — 因子是否同时调制能力与记忆 【ABANDONED 2026-06-02,resistance 差分 + 各因子 session 已覆盖】
> **弃因**:resistance = 配对差值(原文 − 扰动变体),纯能力部分在差分中扣掉——模型能力强但不记忆,应跟着扰动走而非抵抗。剩余边角(模板刚性的"表面捷径"机制存疑)已在 R-1d scope 内,要求先过机制论证才进 confirmatory。不需要独立 session。

### 并入:algorithm_deepaudit §8 原 agenda 残项
- #5 TOST/SESOI=0.15 来历 + 标准化、#7 Gwet AC1、#9 power MC sim、#11 同-cutoff 证伪 ratio、#12 tier labels 统计含义、整体一致性扫(§6 frozen 残余清理)。
- 与 P0–P7 合并成下一轮完整 walkthrough。

---

## 不在本大纲做
- 不拍 P0 范式(owner 要逐条敲)。
- 不擅自 close R-1a / 改 §4.6 / 定 novelty —— 全 gated on P0–P3。
- 不重做 R-1a 机制(tanh / w=2)。
