# R-4 Algorithm Deep Audit — session log (interim)

**Status**: **OPEN** — no decisions locked; leans only.
**Sessions**: 2026-05-27 (start) → 2026-05-28 (interim close).
**Successor**: next round triggered after user排定:(a) 用户完成 factor 全量定义(可能 >4),(b) 自我证伪本轮 construct-validity / post-cutoff-null 推导,(c) 在 (a)+(b) 上正式辩论 framework + estimand 去留,(d) framework 定后再做下一轮 walkthrough(本次后续 #5/#7/#9/#11/#12 + 整体一致性扫)。

**This file is the audit trail. `R4a_DECISIONS.md` was NOT updated this session per user.**

---

## 1. 走过的算法 / 没走的算法

Pedagogical order (浅→深),不按 kickoff 的 A/B/C/D:

| # | 算法 | 状态 |
|---|---|---|
| 1 | effect size + 95% CI(估计 vs 显著性) | ✅ 走透,含 β±2SE 推导(SE = "重做会跳多少"、CLT、95% 几何)、标准化 effect size 的"来头"(Cohen 1988 / z-score 历史) |
| 6 | multiplicity 多重比较 | ✅ 经 #1 自然消解(测量路线不做 NHST family → 不需校正);独立坐实子领域 lit scan 15 篇 0 校正;§10 Westfall-Young 是 frozen 残余 |
| 2/3/8/4 | 混合模型 / cluster-SE / grouped-CV / bootstrap | ✅ 走透,作"非独立性"一族:有效样本数 ≈ 窝数(非行数)、SE ~ 噪声/(因子散布 × √n_eff)、3.7× 假窄演示、cluster bootstrap 按窝抽 |
| 5 | TOST / SESOI = 0.15 | ⏸ 仅触及概念,**未走 0.15 哪来 / 标准化怎么放** |
| 7 | Gwet's AC1 | ⏸ 未走 |
| 9 | scenario-based MC power simulation | ⏸ 未走具体实施(power 概念已在 [[feedback_review_complexity]] memory 阶段讲过) |
| 10 | E_CMMD 定义 + "分歧 ≠ 记忆"防御 | ✅ 走透,推到 **CUT** lean(见 §2) |
| 11 | 同-cutoff 证伪对 ratio 0.5 | ⏸ 未走 |
| 12 | tier labels 的统计含义 | ⏸ 未走 |
| 附 | E_PCSG 实际定义 + 按对划分免聚类 | ✅ 走透,确认 per-pair 单元可保 leakage-clean |
| 附 | Firth(scripts/sensitivity_analysis.py) | ⏸ 仅 grep 确认是 live 残余,未深审 |

---

## 2. 重大发现一:E_CMMD 借自 MemGuard-Alpha,项目从未消化

**Subagent 提取 Roy & Roy 2026《MemGuard-Alpha》(arxiv 2603.26797)结论**(全文 PDF 在 `related papers/MemGuard-Alpha Memorization Financial Forecasting.pdf`,subagent 报告完整内容在主对话):

1. **论文的 "CMMD" = 过滤后的交易信号,不是分歧分数。** 真正的分歧数是副产品 **δ**。
2. **δ 公式**:`δ(s,t) = mean_T(α_k) − mean_C(α_k)`,其中 C/T 按 **MCS 中位数** 把模型劈成 clean/tainted 两组(Algorithm 1)。两组均值差,而非方差/熵/秩相关。
3. **"cutoff-monotone"在论文里_完全不存在_**。我们 estimand 的招牌属性**无出处**——是 R-4a session 自加,但当时没标。
4. **MCS 的判别力 ~96% 仅来自一个"距 cutoff 多远"的日历特征**(τ);5 个 logprob MIA 分数合起来贡献 d 0.39–1.37 vs 17.8。**MCS 几乎等价于 cutoff date。**
5. **"分歧 = 记忆 而非能力"识别在源头本就弱**:最强一招是 **IS/OOS 真实收益准确率交叉**(纯能力解释不出交叉)→ 但需要 forward returns,我们 sentiment/direction 任务可能用不了;IV/Fuzzy-RDD 仅是叙事框架,无第一阶段、无带宽、无回归。
6. 论文未指定:中位数 tie 处理、α=0 中性如何进 δ、confidence φ 是否加权、δ 自身的 SE/检验/across-(s,t) 聚合。
7. 论文自报局限:93 交易日 underpowered(p=0.054 双侧)、caps 7B、MCS 在评估数据上 fit(overfitting risk)、bullish 2019–2024 regime、Sharpe 多半是 beta。

---

## 3. 重大发现二:用户产品描述自发推出 construct-validity 框架

走查中段,用户用自己的话讲产品(数据集 + 标注因子,使用者拿任意 estimand 组合获得 per-model 记忆刻画;难点 = 证明数据集真量记忆、因子真表征记忆模式),agent 形式化为:

> **数据集 = 测量仪器,核心主张是构念效度(construct validity);"模型无法记住它从没见过的东西"是唯一近 ground truth → cutoff 不是 peer factor,是验证锚。**

**三层验证架构**:
- **(a) post-cutoff 归零** = 效度锚 / 分界线。真的量记忆的 estimand,在 post-cutoff 必须读 ~0。这是"量记忆 vs 量能力/熟悉度/话题/脆性"的**判据**。
- **(b) 曝光梯度**(recurrence/salience)= 正向端验证 + **产品本身**。pre-cutoff 中曝光↑→记忆↑→信号↑。机制锚 = Carlini 复制→记忆律。
- **(c) 其它 factor** = 纯刻画,downstream of (a)+(b)。

**两个直接推论**:
- **BL2(700 post-cutoff)= 效度论证的拱顶石**,不是配角。pilot 80/700 比例正好对应此结构(700 收紧 null CI,80 看信号)。
- **反"刷漂亮显著"陷阱的解药就是 post-cutoff null**:总能放信号的 estimand 漂亮 p 值多半来自非记忆(E_CTS 表面熟悉度 / E_NoOp 脆性)。

---

## 4. 重大发现三:E_CMMD 的唯一卖点已被 E_FO 取代

上一轮 audit 我曾说"E_CMMD 是唯一能上黑盒的时间 estimand"——**错**。

- **E_FO = 行为 + 黑盒可跑 + per-model + post-cutoff null 干净**(post-cutoff 模型没见过真结局 → 没东西可抵抗 → null 归零;且 null **对时代漂移、对纯推理混淆都稳**)。它给出黑盒记忆覆盖,比 E_CMMD 干净得多。
- **会聚效度(convergent validity)三角**:E_FO(行为通道)× E_PCSG(惊讶度通道),两个完全不同的算子都过 null + 都随曝光升 → 收敛 = 强构念效度。**不需要 E_CMMD 充当第三条**。

---

## 5. Estimand leans(TENTATIVE,NOT LOCKED)

按 post-cutoff null 是否稳归零(含对时代漂移的稳健性)+ 是否随曝光升 这把第一性原理尺子量:

| Estimand | 第一性原理裁决 | 暂定角色 |
|---|---|---|
| **E_FO** | post-cutoff null 稳 + 黑盒 + per-model | **主记忆 estimand** |
| **E_PCSG** | 同-case 相减抵消表面熟悉度;null 干净;白盒同-tokenizer 对 | **会聚效度佐证** |
| E_CTS | post-cutoff 中文财经文本依然表面眼熟 → 不归零 | **降为 baseline**,非记忆主张 |
| E_NoOp | post-cutoff 一样脆 → 不归零 | **移出记忆集**,作鲁棒性 control |
| **E_CMMD** | 识别最脏 + 论文 δ ≠ 我们的"CMMD"、"monotone" 无出处 + E_FO 已接管唯一卖点 | **CUT** |

**Factor 侧**:
- **Cutoff Exposure** — 验证锚,privileged(不同 KIND 的 factor)。R-1a 机制 closed。
- **Recurrence / Salience** — 曝光强度调制,机制干净。R-1b/R-1c closed。
- **Template Rigidity(R-1d 未闭)** — ⚠ 机制存疑:rigidity 是调制记忆还是表面熟悉度混淆?**必须先过"记忆机制 vs 熟悉度混淆"的第一性原理论证**才进 primary。否则可能是伪装成 factor 的 E_CTS 式 surface 混淆。

---

## 6. 同步浮出的 frozen 残余 / stale 项(此处记录,清除待下轮)

1. **MEASUREMENT_FRAMEWORK §10**:"Westfall-Young stepdown max-T on the 20-coefficient confirmatory family" —— Westfall-Young 与 "20" 两个数都 stale。§9 已 2026-05-26 加 SUPERSEDED 注,**§10 漏**。
2. **MEASUREMENT_FRAMEWORK §5.2**:E_CMMD 仍命名 "...**Memorization** Disagreement"(R-4a 已改 "Cutoff-Monotone";若下轮 cut E_CMMD 则整段 retire)。
3. **`scripts/sensitivity_analysis.py`** 含 **Firth** logistic regression 代码,当前 spec / R-4a DECISIONS 不提 Firth —— 死残余漏到 live script。
4. **`plans/phase7-pilot-implementation.md`** + **`scripts/planning_power_calculator.py`** grep 命中 Westfall/multiplicity —— 待核 frozen 多重比较是否嵌入了 runnable code。
5. **`src/r5a/estimands/__init__.py`** 是 stub,确认 E_CMMD 在代码层也未实现。
6. **`archive/r4_r5a_lineage/docs/CMMD_MODEL_FLEET_SURVEY.md`** 把 CMMD 归给 Roy & Roy 但**项目从未把那篇方法抽出来**(`related papers/notes/` 无方法笔记)。

---

## 7. 下游波及(如果下轮锁住本 leans)

- **R4a_DECISIONS.md** §1 框架级 lock 第 1/6 条 + §2(E_CMMD 定义)+ §6 downstream anchor 表(R-1e/R-2/R-3 行)要改。
- **MEASUREMENT_FRAMEWORK §5.2 / §9 / §10** 全段重写或加 SUPERSEDED banner。
- **RESEARCH_PROPOSAL.md §4.4** 候选 estimand 池要改;§4.5 BL2 的角色从"负对照"升级为"效度拱顶石"。
- **`src/r5a/estimands/`** WS4/WS5 实施按新清单写,不实现 E_CMMD/E_NoOp 作 memorization。
- **R-1d** 机制论证作为先决条件(rigidity 进 primary 与否)。
- **R-2 / R-6** C_FO 机制选择(就地换值 vs 真实收益)直接决定 **E_FO 效度** —— E_FO 升主角后这条要紧度大幅升。
- **#10 E_CMMD 防御**:若 cut 则整段不必审,本 session 末尾用户主动转向 cut 后该项 collapse。
- **BL2 sample size**(R-3 范围):效度拱顶石的角色坐实 700 post-cutoff(比 350)是对的。

---

## 8. 下一轮 agenda(用户排定)

1. 用户完成 **factor 全量定义**(可能 >4)。
2. 开新 session,先**自我证伪本轮 derivation** —— 找 post-cutoff-null 判据哪里过狠 / 哪里会误杀 / 第一性原理推导有漏。
3. 在 (1)+(2) 基础上做正式辩论(framework + estimand 去留)。
4. framework 锁定后做下一轮 walkthrough(完成本次后续 #5/#7/#9/#11/#12 + 整体一致性扫)。

**2026-05-30 增补**:novelty factor session(R-1d)+ codex 第一性原理 review 把 agenda 第 2/3 条**具体化**了 —— 自我证伪 null 判据时发现"过狠"多半是 **estimand 范式未定(resistance vs prediction-lift)+ E_FO 命名漂移**造的假争议,不是判据本身过狠。下一轮 walkthrough 的开放条目(**P0** estimand 范式 / **P1** 命名拆解 / **P2** null 精确措辞 / **P3** 任务信息集 / **P4** 目标-horizon-ground truth / **P5** novelty 归宿 / **P6** false alpha claim 边界 / **P7** 因子是否同时调制能力与记忆)全部编入 `R4_next_construct_validity_agenda.md`,与上面残项合并,**均不在本轮拍板**。novelty 共识 = 不当主因子;最终归宿 gated on P0+P3,故 R-1a 维持 DRAFT 不 close。

---

## 9. 元层(放此处不放 DECISIONS)

- 本 session 是 [[feedback_review_complexity]] + [[feedback_clean_room_first]] + [[feedback_minimal_design]] 的**一次完整应用**:用户全程主导、agent 拒绝护现状、主动找简化空间、对每个算法答"我们场景真需要吗"。
- **E_CMMD 的失效模式** —— 旗舰 estimand、招牌属性(monotone)无出处、识别弱、代码 stub、文档没消化源论文、全链路无人钉过 —— 是 [[feedback_decision_text_drift]] 与"未审 frozen 内容带入"的**教科书级实例**。
- **第一性原理 derivation 由用户产品描述自发推出**(cutoff 不是 factor、是验证锚),agent 形式化。建议把 [[feedback_clean_room_first]] 扩展一条:**owner-driven product framing 拆失效模式比 reviewer-driven methodology framing 更狠**——用户讲"我们卖什么"时,常常直接走到第一性原理,绕过所有术语包袱。
- **本次 session 没有把 audit trail 写到 R4a_DECISIONS 是对的**——leans 还没自我证伪 + factor 还没定全 + 下一轮辩论还没开,锁了就违反 [[feedback_review_complexity]]。
