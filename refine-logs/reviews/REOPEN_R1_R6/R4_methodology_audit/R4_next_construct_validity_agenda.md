# R-4 下一轮构念效度讨论大纲(开放议程)

> **⚠️ P0 段 SUPERSEDED 2026-05-31** by `R4_construct_validity_decisions.md`(定调)+ `.scratch/session_kickoff_p0_estimand_paradigm.md`(P0 kickoff)。
> 本文件 P0 原写成"resistance vs prediction-lift 两范式逐条敲、不二选一";该框架已**溶解** —— **resistance 是框架实存的唯一主量,prediction-lift 不是可平起平坐挑选的仪器,而是"动机→测量"那道桥的名字**。
> **P0 scope 以 kickoff 为准,下方 §P0 正文仅留作 audit trail,勿据其开 session。** P2–P7 仍是有用的 scope 提示(但 null 判据已按 `R4_construct_validity_decisions.md` D2 分层,见各条)。

**Status**: **P0 SUPERSEDED(见顶部 banner);P2–P7 仍 OPEN — 议程,非决策**;供 R-4 下一轮 walkthrough 逐条敲定。
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

### P0 — 核心 estimand 范式 【SUPERSEDED 2026-05-31 → 见 `session_kickoff_p0_estimand_paradigm.md`】

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

### P1 — 命名漂移拆解 【无论 P0 怎么定都要做】
- E_FO 在 `MEASUREMENT_FRAMEWORK.md` L180 = False Outcome **Resistance**;在 novelty session 口头 = Future Outcome **prediction**。**同名两物。**
- 待敲:把 `raw_outcome_score` / `memory_lift` / `false_outcome_resistance` 三个量各起名;逐处核对 algorithm_deepaudit / MEASUREMENT_FRAMEWORK / proposal 里每个「E_FO」指哪个。

### P2 — post-cutoff null 的精确措辞 【gated on P0】
- 不是「绝对归零 vs 松绑」二选一,是**分量**:`raw_score` 的 null = 能力 baseline(≠0);`memory_lift` / resistance 的 null ≈ 0。
- construct-validity 框架「null 须读 ~0」对后者成立、**不用推翻**;主对话此前「松绑判据 / R-4 收下」是被命名漂移误导的**错表述**,作废。
- 待敲:每个 estimand 标清 null 该读什么;BL2(700 post-cutoff)在各范式下验证 raw baseline 还是 lift≈0。

### P3 — 任务信息集协议 【gated on P0,且能翻盘 P5】
- article-only(只喂当前文章)vs 允许文章前的公共历史。
- 若 **article-only**:模型从**参数**调更早新闻 A 推 B,可能算 memorization 而非合法能力 → **B2 合法性翻盘 → novelty 部分复活**。仅在 prediction-lift 范式下 B2 才是问题。
- 待敲:锁任务信息集;据此重判 B2 / novelty。

### P4 — 预测目标 / horizon / ground truth 【R-6 范围,P0 逼其前置】
- prediction-lift 范式需真实涨跌 ground truth + horizon + 收益口径 → 撞 §4.6「confirmatory estimand 不与真实股价对照」;resistance 范式不需要。
- 待敲:目标标签(情感 / 方向 / 收益)、horizon、ground truth 来源;§4.6 改不改。

### P5 — novelty 最终归宿 【gated on P0 + P3】
- 共识:novelty **不当主因子**。
- 残留:弱 novelty 作退化-case 清洗 / sensitivity(机械恒等 / 日历已知 / Q4=年报−前三季 / 标签文中明示)—— 归 WS0 数据卫生,**非 factor**。
- 复活条件:P3 锁 article-only **且** P0 走 prediction-lift → B2 相关性回来,novelty 可能需部分重启。
- 待敲:P0/P3 敲定后,定 novelty 是「纯清洗」还是「部分因子」;`R1a_DECISIONS.md` / `cutoff_probe_DECISIONS.md` 的 DRAFT 头据此 close 或重写。

### P6 — false alpha 作为 research claim 的锚定与边界
- pre−post 是 proposal §2.2 false alpha 动机要的那座桥。
- 风险:benchmark 不跑组合 / 不算收益 / 不做风险调整 → **不能 claim「测 false alpha 本身」**,只能「测会导致 false alpha 的记忆抬升代理」。
- 待敲:§2.2 补桥的精确措辞;主 claim 边界(characterization 别滑成 application)。

### P7 — 因子是否同时调制能力与记忆 【影响所有 confirmatory factor】
- recurrence / salience / template rigidity 不能默认「主要调制 C(记忆)」;它们 post-cutoff 也可能提高能力 / 表面熟悉度。
- 待敲:每个 confirmatory 因子验证它调制的是 `memory_lift` 还是 `raw_score`(接 algorithm_deepaudit §5 对 Template Rigidity 机制存疑)。

### 并入:algorithm_deepaudit §8 原 agenda 残项
- #5 TOST/SESOI=0.15 来历 + 标准化、#7 Gwet AC1、#9 power MC sim、#11 同-cutoff 证伪 ratio、#12 tier labels 统计含义、整体一致性扫(§6 frozen 残余清理)。
- 与 P0–P7 合并成下一轮完整 walkthrough。

---

## 不在本大纲做
- 不拍 P0 范式(owner 要逐条敲)。
- 不擅自 close R-1a / 改 §4.6 / 定 novelty —— 全 gated on P0–P3。
- 不重做 R-1a 机制(tanh / w=2)。
