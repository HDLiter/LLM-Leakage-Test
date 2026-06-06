---
title: 研究开题报告 —— 中文金融新闻 LLM 训练数据泄露的因子受控 benchmark
language: 中文(经用户批准的特例;项目其余文档与代码注释为英文)
date: 2026-05-22
status: |
  DRAFT。锚定部分(研究问题 / 四层框架 / 模型 fleet / 工作流 / 两阶段结构)为定稿;
  操作化部分(因子 / 扰动 / estimand / 预测目标 / 采样过滤 / pilot 统计)标 [R-x],
  内容待 R-1…R-6 结构化重开后逐步完善。
supersedes: archive/pre_benchmark/docs/RESEARCH_PROPOSAL_v2.md(转向前的 "Task Design Gates" 版本)
authority: |
  本文件是当前实验的成文研究问题文档(此前缺失 —— Pass-1 走查 flag ①)。
  锚定内容的逐章依据:refine-logs/reviews/WALKTHROUGH_PASS1/section_01..07.md。
  待重开项 R-1…R-6 的权威清单:refine-logs/reviews/WALKTHROUGH_PASS1/pending_items.md。
  冻结 scope 的名义权威:refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md
  (其操作化细节正在重开)。
  四层框架术语权威:refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md。
---

# 研究开题报告 —— 中文金融新闻 LLM 训练数据泄露的因子受控 benchmark

> **如何读这份文档.** 标 **[锚定]** 的章节是 Pass-1 全实验走查已确认、不再
> 变动的内容。标 **[R-x 重开中]** 的章节描述的是当前冻结设计的现状,但其
> 操作化细节正处于结构化重开(见 §9),内容会在重开完成后替换为定稿。

---

## 1. 概述

大语言模型正被广泛用于把金融新闻转成可预测的信号。但在历史新闻上评估这类
模型有一个根本风险:**训练数据泄露(look-ahead leakage / memorization)** ——
模型可能不是从眼前这篇文章推理,而是从参数记忆里调出"这件事后来发生了
什么"来作答,用了发文当时不可能有、但训练时已经有的信息。

本研究构建一个 **因子受控的 memorization benchmark**,在中文 A 股财联社
(CLS)电报新闻上,刻画 LLM 的训练数据泄露**有多严重、以及它系统性地随
哪些「案例层面的因子」变化**。它用一个四层测量框架(Factor / Perturbation /
Operator / Estimand)、一个横跨不同训练 cutoff 的 16 模型 fleet、和一个两
阶段自适应预注册流程,把"泄露"这个量做成可测、可审、可复现的对象。

这是一篇 **characterization(刻画型)benchmark 论文** —— 它的贡献是这个
benchmark 本身,不是"证明某个模型有泄露",也不是因果机制论文。

---

## 2. 研究问题与动机 [锚定]

### 2.1 研究问题

> **在中文金融新闻情感 / alpha 分析任务上,LLM 的训练数据泄露有多严重,
> 以及它系统性地随哪些案例层面的因子变化?**

关键不在"有没有泄露",而在"**什么样的案例更容易泄露**"。本研究用 4 个
confirmatory 因子(§4.1)把这个问题操作化。

### 2.2 动机:从量化项目到 benchmark

本研究的动机链条是:

1. **起点** —— 服务于一个 A 股量化项目(Thales 系):该项目用 LLM 从新闻
   抽取文本落地的信号、经 XGBoost 聚合出 alpha。最初的目标是测量泄露、
   并找机制去减轻它。若 LLM 抽出的特征被记忆污染,XGBoost 学到的是"作弊
   特征",回测里出现 false alpha,实盘里就是资本错配。
2. **实验中的发现** —— 在迭代中发现:**文本本身就带着各种内部因素**,会
   系统性地影响大模型到底记不记得住某条新闻。
3. **由此转向** —— 要做*有效*的泄露检测,必须**先有一个能区分这些因素的
   有效 benchmark**;否则测出来的信号无法解释。
4. **当前论文的贡献 = 这个 benchmark 本身。** 量化项目是本研究的起点与
   应用背景,不再是论文的直接 motivation。

> **一处名实关系需在论文中显式架桥.** 核心算子名为 "sentiment / alpha
> prediction"、动机里有 "false alpha",但 benchmark 本身并不计算 alpha 或
> 收益(见 §4.6)。动机(量化中的 false alpha)与测量(行为上的记忆指纹)
> 之间靠一个**论证**连接,论文方法 / 讨论章须把这座桥写清楚。

### 2.3 定位与文献空白

中文金融 NLP 的污染审计基本是空白;据文献调研,没有先例做"同源新闻 +
因子受控 + 跨模型 fleet"的 memorization benchmark。这是本研究的 unique
position。(转向前的 "Task Design Gates / 任务分解抗泄露" 论点已在 Phase 5
转向时降级 —— 任务分解假设至多作为后续探索性工作,不进本研究的
confirmatory scope;理由是因子家族已大、再加任务变体易致 p-hacking。)

<!-- TODO[CROSS_SYNTH 🟡-1, approved 2026-05-23]:
在本段后新增一段 Kong et al. 2026 (arXiv:2602.14233) 作 field-level position
anchor。要点:
- Kong 是 ICML 节奏的 position paper,综述 2023-2025 顶会 164 篇 LLM-in-finance
  论文(Figure 2),发现 look-ahead bias 仅 26.8% 提及、survivorship bias 仅
  1.2%、no single bias >28%;50 人 practitioner user study 中 74% 报告评估
  工具匮乏、50% 把"工具/框架缺乏"列为最大瓶颈。
- Kong §2.1.1 "Parametric Knowledge Leakage" 是他们 Sin #1 Look-Ahead Bias
  的两大 channel 之一(另一为外部知识检索泄露 §2.1.2),这正是本研究
  R5A 中心 channel。
- 本研究 = Kong §2.1.1 这一 channel 在中文金融语料 + 16-model split-tier
  fleet 上的因子受控 empirical instantiation。Kong 给 field-level
  diagnosis + framework(自己不做 benchmark);我们给 case-level
  measurement(具体 estimand + 因子 + 操作化)。两层互补。
草稿与详细论证见:
  refine-logs/reviews/CROSS_SYNTH_20260523/synthesis_findings.md §A.🟡-1
  以及该 session 的对话记录 🟡-1 第 (3) 节。
落地此 TODO 时同步更新 memory lit_landscape.md(见同份 synthesis §C.1)。
-->

### 2.4 中文优先,英文为 stretch goal

benchmark 做中文 CLS 新闻(量化项目用的就是中文新闻)。英文对等数据集是
**stretch goal**:在中文 pilot 完成后,按 5 条触发条件评估是否扩展(见
memory `project_english_expansion`)。

---

## 3. 核心设计:四层测量框架 [锚定]

早期讨论曾把 10 多个"detector"和若干设计张力混在一起。事后发现许多张力是
**范畴错误** —— 把"怎么变换文本""怎么算一个分数""真正要分析的量"三件
不同的事混为一谈。四层框架把它们显式拆开:

| 层 | 名称 | 是什么 | 输入 → 输出 |
|---|---|---|---|
| **L1** | **Factor 因子** | 给每个案例(或案例×模型)打的标签,用于分层与交互分析 | 案例 → 标签 |
| **L2** | **Perturbation 扰动** | 对案例文本 / prompt 的受控变换,只改一个目标维度 | 原文 → 变体文本 |
| **L3** | **Operator 算子** | 原子打分函数,无状态,不知道扰动 / 因子 / 实验设计 | (文本, 模型) → 分数 |
| **L4** | **Estimand 测评** | 把算子分数跨扰动变体 / 模型对 / fleet 模式组合出的、有分析意义的量;**只有 estimand 进统计模型** | {算子分数} → 分析指标 |

框架**不改变"测什么",只改变"怎么命名、组织、推理这些测量"**。它的收益:
若干设计张力自然溶解;工程范围收窄到只需 3–4 个原子打分函数;论文方法章
得到干净的展开骨架。

> **因子定义的精确说法(Pass-1 flag ⑦).** 因子大多是**案例层面**的标签,
> 一个常用的层归属判定法是"不提任何模型就能描述它 → 因子"。但这是个
> 启发式,有一个**有原则的例外**:Bloc 0 的时间暴露因子 Cutoff Exposure
> 是 **case×model** 的(它依赖模型的 cutoff,见 §4.1)。因此因子的准确
> 定义是"案例层面 **或** 案例×模型层面的标签"。

一个关键 reframe:早期称为"detector"的东西(如 SR/FO、NoOp)其实是**施加
在同一个核心算子 P_predict 上的扰动**;P_predict 的 baseline 输出本身辨别
力不强,它的价值是充当**扰动型 estimand 的载体** —— baseline 与扰动变体之
间的 delta 才是记忆证据所在。

---

## 4. 测量内容(操作化层)

> §4 描述当前冻结设计的**现状**。其中标 **[R-x 重开中]** 的部分,其操作化
> 细节正在结构化重开(§9);此处内容是占位与现状记录,非定稿。

> **R-0 架构 anchor(2026-05-23 PM late 关闭)**:§4 全部 case-level
> factor metric 在 **R-0 决定的 corpus 架构容器**上计算。容器把"从源
> 语料到 P_predict 主体"的路径拆成四层(S0 源 / L1 entity-mention /
> L2 subject-target / L3 benchmark-eligible views)与六阶段
> entity-first pipeline,并锁定 universal admissibility 与一个唯一
> base sampling pool(Pool B);具体 factor construct / family 粒度 /
> 窗口 / 抽样分布则由对应 R-X session 在容器内自决。Canonical
> lock-in(time-static): `refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/R0_DECISIONS.md`。
>
> 后续 §4.1.1-§4.1.4 的具体因子实现:R-1b ✔ closed 2026-05-24 →
> `refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/R1b_DECISIONS.md`;
> R-1c ✔ closed 2026-05-25 →
> `refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/R1c_DECISIONS.md`;
> R-1a ✔ closed 2026-05-27(机制锁;cutoff 中心值待探针验证)→
> `refine-logs/reviews/REOPEN_R1_R6/R1a_cutoff_exposure/R1a_DECISIONS.md`;
> R-1d 待落定。

### 4.1 confirmatory 因子(当前候选 4 个;最终数由 pilot power 定)[R-1d 待定;R-1a ✔ closed 2026-05-27;R-1b ✔ closed 2026-05-24;R-1c ✔ closed 2026-05-25]

**confirmatory 因子数 = power-bounded,不预设魔数**(2026-05-26 决定):最终
confirmatory 数由 **pilot + R-4b power** 决定(N=2560 对交互项能稳健 confirm
几个)。frozen 时代的 "5 estimand × 4 factor = 20 系数" 是 Step 2 多 agent
review 的候选规模示意,**非硬约束** —— R-4a §4 已把因子总数解锁交 R-1e + pilot。
下表列出 **4 个**核心 confirmatory candidate;candidate-pool review 已完成(R-1g…R-1w),
候选池据此扩大 / 定 verdict,汇总索引见
`refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/four_layer_candidate_pools.md` §1
(逐因子 canonical = 各 `R1*_DECISIONS.md`);未选中的候选进 exploratory(照常计算 + 报告,
撑 benchmark coverage,不浪费)。

下表 4 个当前 candidate 刻画泄露的三个驱动通道 —— **时间访问、重复、显著性**:

| 因子 | Bloc | 测什么(WHY) |
|---|---|---|
| **Cutoff Exposure** | 0 时间暴露(case×model) | 模型 cutoff 相对案例事件日期的位置。最直接的泄露通道:事件在 cutoff 前,模型训练时就*可能*见过它和它的结果。**R-1a ✔ closed 2026-05-27**(tanh(发文日−cutoff,signed,w=2月);机制锁,cutoff 中心值待探针验证)→ `refine-logs/reviews/REOPEN_R1_R6/R1a_cutoff_exposure/R1a_DECISIONS.md`。 |
| **Historical Family Recurrence** | 1 重复(case-level) | (标的 × 事件家族)模式在 cutoff 前 CLS 里复现多少次。**outcome-leakage proxy**:模型用记住的"事件 → 涨跌方向"关联代替对眼前文本的推理,涨跌(收益)是隐含变量。**R-1b ✔ closed 2026-05-24** → `refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/R1b_DECISIONS.md`。 |
| **Target Salience** | 2 显著性(case-level) | 标的实体在模型预训练 corpus 里的累计曝光强度;CLS L1 mention count 是 best-available proxy(framing C)。越曝光,模型预训练时见过越多关于它的文本。**R-1c ✔ closed 2026-05-25** → `refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/R1c_DECISIONS.md`。 |
| **Template Rigidity** | 1 重复(case-level) | 文章有多"模板化 / 套话"。高度模板化的新闻可被套模板匹配而非读内容。 |

**统计结构:** 对 Cutoff Exposure 测主效应(β1);对其余因子测**与 Cutoff
Exposure 的交互项**(β3)—— 即假设"高复现 / 高显著 / 高模板化会 *放大*
cutoff 暴露带来的泄露"。这是一个有原则的混淆控制选择(交互项差掉"案例难度"
污染),代价是交互项对样本量苛刻 —— **这正是 confirmatory 数交 R-4b power
定、而非预设的原因**:confirmatory 因子越多 → 交互项越多 → 给定 N=2560 每个
检出力越低,power 计算会划出能稳健 confirm 的上界。

**[R-1 重开] 待定**:R-1a / R-1b / R-1c 已 closed(canonical 见上表 link;R-1a 机制锁,cutoff 中心值待探针验证 — 见 R1a_DECISIONS §6/§11);**R-1d Template Rigidity** 实现方法待定(目前 **无任何实现 spec** —— flag ④)。"是否就选这 4 个因子"由 R-1e 根据 pilot 实证证据决定(原则:实现优先于选择;R-1c 已显式 Option C — discriminant trigger 时由 R-1e 决定 Salience 是否进 primary,可能降级)。**[R-4 重开]** β1/β3 统计结构方法层已由 R-4a 锁定(无 family-wise multiplicity correction、per-estimand 混合模型分别建、TOST/SESOI=0.15 限 BL2 等 8 条);具体 power 数字与混合模型规格落地待 R-4b。

### 4.2 算子 [部分锚定]

| 算子 | 做什么 | 访问 | 状态 |
|---|---|---|---|
| **P_logprob** | 白盒逐 token logprob → 文本意外度(Min-K++/CTS);thinking 必须 OFF | 白盒 | confirmed |
| **P_predict** | 给文章 + 冻结任务 prompt,取方向 + 信心 + 记忆自报标记 + 证据引用 | 黑盒即可 | confirmed,主力 |
| P_extract / P_schema | masked span 补全 / CLS 前缀续写 | 黑盒即可 | reserve |

算子层本身较稳定;但 P_predict 究竟"被要求预测什么"涉及 §4.6 [R-6]。

### 4.3 扰动 [R-2 重开中]

冻结清单 6 个扰动,其中 **C_FO 与 C_NoOp 为 confirmatory**(喂 E_FO / E_NoOp):

- **C_FO(假结果)** —— 把文章里已核实的真实结果值换成具体的假值。测模型
  是否无视眼前的反事实证据、吐出记忆里的真实结果。
- **C_NoOp(无关插入)** —— 插入一句无关但貌似合理的短句。测记忆是否表现
  为脆弱的模板匹配。注:设计自身定性 E_NoOp 为 **robustness / 模板脆弱性
  信号,非直接记忆证据**,作为多信号收敛的一部分进 confirmatory family。

其余 4 个(C_anon / C_SR / C_temporal / C_ADG)只喂探索性 estimand。
C_FO 与 C_NoOp 的变体均经全量人工审计(4 维 rubric,kappa≥0.70)。

**[R-2 重开] 待定:** 6 个扰动各自的实现构思,以及最终保留几个 / 哪几个进
confirmatory(用户点名重审 C_NoOp)。

### 4.4 estimand 与统计结构 [R-4a 框架已定 2026-05-23;具体清单 R-1/R-2/R-6 重开中]

**当前候选 estimand 池**(2026-04-29 frozen,作为 *候选*,非 primary family
最终清单):E_CMMD(跨模型 cutoff-单调分歧)、E_PCSG(配对 cutoff 意外度
差)、E_CTS(校准尾部意外度)、E_FO(假结果抵抗)、E_NoOp(无关插入
敏感度)。

**[R-4a ✔ closed 2026-05-23]** 基于 clean-room 白板独立分析 + 15 篇子领域
代表作文献扫描双源证据,锁住**框架级方法论 8 条** + **E_CMMD 定义** +
**负对照具体处理**(BL2 TOST/SESOI / 同-cutoff ratio reading / BL1
grouped-CV-by-case,见 §4.5) + **R-4a → R-6 estimand 容量接口**。canonical
lock-in(time-static): `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4a_DECISIONS.md`。

8 条框架决定的覆盖面:主报路径(effect size + CI per estimand)、tier
labels(main / primary / supporting / robustness / appendix)、pre-registration
路径(design memo + sealed split + transparency artifact,见 §6)、每个
estimand 独立建模 + 聚类、扰动质量审计(Gwet's AC1 + accuracy)、
baseline_confidence / model_capability 走 sensitivity、TOST/SESOI=0.15 服务
BL2 等价检验、scenario-based MC power simulation。E_CMMD = Cross-Model
**Cutoff-Monotone** Disagreement,claim 层与 memorization 解释解耦 ——
只有与其它 estimand 收敛时才上升到 memorization characterization。

**[R-1 / R-2 / R-6 重开] 待定**(R-4a scope 之外的 component-level,留给
实现 + pilot 数据):具体哪些 estimand 进 primary、primary family 大小
(S8 / S10 / S12 等)、哪些因子(数量与具体哪几个)、C_FO 机制(就地换值
vs 文末追加真实收益)、P_predict 输出 schema(direction-only / + confidence
/ + memory_flag / + evidence)。

**[R-4b] 仍开放**(等 R-1e / R-2 / R-3 / R-5 落定):power 计算具体数字、
n_eff 矩阵、混合模型具体规格落地、bootstrap 实施细节。

### 4.5 负对照 [R-3 重开中;R-4a 锁定具体处理方式 2026-05-23]

R-4a 锁的负对照具体处理(详见 `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4a_DECISIONS.md` §3):

- **BL2 post-cutoff 负对照** —— 700 个 ≥2026-02-01 的案例(晚于全队最晚
  cutoff);事件在所有模型 cutoff 之后 → 泄露信号应近零。通过路径走 TOST
  (Two One-Sided Tests)等价检验,SESOI = 0.15(标准化效应),通过条件
  = 95% CI 完全落在 [-0.15, +0.15] 内。
- **同-cutoff 证伪对** —— GLM-4-9B ↔ GPT-4.1(同 cutoff、不同架构),查
  信号是否来自架构差异。reading 路径走主 estimand 差异 ratio:ratio ≤ 0.5
  → cutoff-driven reading 维持;ratio > 0.5 → architecture-noise
  early-warning caveat 附在结果上。
- **BL1 元数据 / text-light challenger** —— 简单文本/元数据特征是否能
  拟合到接近 LLM 水平。交叉验证走 grouped-CV-by-case(同一原文派生的多行
  share fold)。
- 另有 C_NoOp_placebo、BL3(非金融中文新闻负对照,stretch)。

**[R-3 重开] 待定:** 负对照整体充分性、C_NoOp_placebo 具体实现、BL3 中文
非金融语料可得性。

### 4.6 预测目标与 ground truth [R-6 重开中]

**现状:** 当前冻结设计中,P_predict 只输出一个**方向判断**(涨/跌/中性 +
0–100 信心 + 记忆自报标记 + 证据引用),且 prompt 明令禁止模型使用已实现
收益。所有 confirmatory estimand 都是**行为对比**(跨模型分歧、扰动翻转、
文本意外度),**从不与真实股价对照** —— 当前设计**不碰已实现收益、无持有
期、无 beta 调整**。

**[R-6 重开] 待定:** 一个关键区分 —— "模型不能用 hindsight"(测量有效性
规则)≠ "实验者不能用真实结果做分析"。金融语料的优势正是结果可验证;当前
设计未充分利用这一点。待彻底调查:实验者是否 / 如何用真实收益(作协变量 /
难度指标 / 采样过滤标准 / 验证层)。本项与 §4.3 扰动、§4.7 采样深度纠缠。

### 4.7 采样与准入过滤 [R-5 重开中;R-0 架构容器 2026-05-23 closed]

R-0 架构在采样层的两件事:**唯一 base pool = Pool B**(`L2 ∩
universal admissibility`,即 `tradable_at_event=true ∧ text_length ∈
[min, max] ∧ is_bundle=false`,每个 P_predict 主体必过)+ **可选分布
策略层**(Pool G salience-stratified / Pool H entity-balanced / Pool I
cutoff-balanced 任意叠加,row-random 也合法);Pool D / E / F 是
架构扩展位,R-5 / R-2 / R-6 实操确认必要时激活。non-tradable rows 在
L1 / L2 保留作 Salience / Recurrence 分母客体,过滤只在 P_predict
主体一侧。Canonical lock-in(time-static):`refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/R0_DECISIONS.md`。

**[R-5 重开] 待定:** 分布策略选(row-random / G / H / I / 组合 —— **R-5
全权,不锁**);per-article cap 与 dedupe 规则(段 (a) 同 article 多
target 进 benchmark 的统计独立性问题);text_length 阈值;反直觉/难预测
案例过滤(需真实股价识别,R-6 子决策);是否触发 Pool D / E / F 架构
扩展。

<!-- TODO[CROSS_SYNTH 🟡-4(c), approved 2026-05-23]:
R-5 完成后,在本节新增专门的"抽样分布策略"段(不止"过滤器"),内容:
- 当前 §4.7 只覆盖准入过滤(filter out 哪些案例不进),不覆盖抽样分布
  (从合法池里按什么分布抽 N 条进 pilot / main)。这是 R-5 scope gap。
- 三种候选策略(R-5 决定):
  1. 案例随机抽 —— 会偏向高曝光实体(因为高曝光实体在语料里出现条数多),
     间接复制 Kong (2026) §2.2 警告的 media-coverage bias。
  2. 实体均衡抽(每实体 ≤k 条)—— 反过来过度代表低曝光实体,
     破坏 Target Salience(§4.1)的自然分布。
  3. 按 Target Salience 分层抽(高/中/低各 N/3)—— 合理但需明示。
- 显式回应 Kong 2026 §2.2 警告:本研究 sampling 通过 [R-5 决定的策略]
  保证非按 prominence 排序,因此不引入 Kong 警告的幸存者偏差。
- 同步:~~R-1c clean-room 复审 Target Salience metric~~ ✔ closed 2026-05-25;
  R-1c §8.5 已把 Salience × sampling 互动 + Kong §2.2 sanity-check 作为
  R-5 input note(canonical 见 R1c_DECISIONS.md §8.5)。
TODO 起源 + 完整论证 + Kong §2.2 原文引用:
  refine-logs/reviews/CROSS_SYNTH_20260523/synthesis_findings.md §A.🟡-4 修正版
  与该 session 对话 🟡-4(用户 2026-05-23 指出此 scope gap)。
-->


---

## 5. 模型 fleet [锚定]

fleet 是时间泄露准实验的物理基础 —— 没有横跨 cutoff 的模型多样性,就没有
Cutoff Exposure 这个因子。**16 个模型,split-tier:**

- **14 个 P_predict-eligible** = 10 个 full-operator 白盒(5 Qwen2.5 + 4 Qwen3
  + 1 GLM)+ 4 个黑盒(DeepSeek V4 Pro / GPT-4.1 / GPT-5.1 / Claude Sonnet 4.6)。
- **12 个 P_logprob-eligible** = 上述 10 个白盒 + 2 个 P_logprob-only 的
  Llama(Llama-3-8B / Llama-3.1-8B)。

白盒经 vLLM 部署(本地 / AutoDL 云),黑盒经 API。一个固有的结构事实:
**没有任何单一模型看到完整的 confirmatory family** —— logprob 类 estimand
只在 12 白盒上,P_predict 类在 14 个上。

各模型的 cutoff 日期目前为 operator-asserted(厂商声明或推断),由 Path E
经验探针验证白盒部分;黑盒 cutoff 无法经验验证。论文的时间结论因此采用
hedged 的 "cutoff-monotone(非因果)" 措辞,并配同-cutoff 证伪对兜底。

---

## 6. Design memo、sealed split 与 transparency artifact [结构锚定;R-4a 措辞重定 2026-05-23]

本研究采用**两阶段提交流程**,但**不**包装为正式预注册 —— 子领域 15 篇
代表作 0 例做 OSF / AsPredicted / registered report,在 LLM memorization
子领域,正式预注册既无先例也非必要。改用三件套:

### 6.1 Stage 1 — Design Memo(pilot 开跑前)

一份 markdown,落到 git repo,有具体 commit SHA。内容:研究问题、候选
estimand 清单、候选因子清单、扰动 inventory、模型 fleet、case 准入规则、
pilot 后**允许修订**哪些(metric 实现细节、effect-size 估计、扰动
inventory 微调、模型替换、**从已声明候选池里选定 confirmatory 因子的身份
与数量** —— 数量由 R-4b power 定,不预设魔数)和**不允许修订**哪些(estimand
框架级定义、core operator 集合、**追加候选池外的新因子**(追加须开新 design
memo))。即:候选池 pilot 前锁(可 >4),pilot 后从池里选 / 降级、不追加池外。

### 6.2 Sealed pilot / test split

- **Phase 7 = pilot**,N=780(80 pre-cutoff + 700 post-cutoff)。pilot 的
  职责是证明冻结的测量栈"能跑、能审、能分析",估计 effect size 与协方差
  结构,为 main run 算 power。**pilot 不回答论文主问题。**
- **Phase 8 = main run**,N=2,560,**与 pilot 0 重叠**。main run 才回答
  研究问题。

pilot 的 80 个 pre-cutoff 案例承载主因子分析;700 个 post-cutoff 案例只做
baseline(无扰动、无审计),服务 BL2 负对照。

同行参照:Shi 2024(WikiMIA pre-2017 member / post-2023 non-member)、
LiveBench 2025(每月 1/6 private slice)、AntiLeakBench 2025(post-cutoff
自动构造)。

### 6.3 Stage 2 — Transparency Artifact(pilot 跑完之后)

一份 update,记录:pilot 看到了什么、所以改了什么、改动是否 design memo
里 declared allowed、main run 开始前最终锁了什么。commit-locked,git diff
可追溯。

论文里写:"the final analysis plan was committed at commit Y prior to running
the main experiment, with the diff from commit X documenting all pilot-driven
refinements."

**[R-4b / R-1 关联]** pilot 的 n_eff 矩阵、scenario-based MC power 模拟
搭在操作化层上,操作化重开后需相应重算;post-cutoff = 700 这个数本身已定。

---

## 7. 工作流 WS0 → WS5 [锚定]

Phase 7 切成可并行的工作流:

| WS | 做什么 | 依赖 |
|---|---|---|
| WS0 | 搭骨架(代码契约、配置、冒烟工具) | 无 |
| WS0.5 | 算因子(事件分类 / 实体抽取 / 复现计数 / 显著度管线) | WS0 |
| WS1 | "看模型反应"管线(P_logprob 白盒) | WS0 |
| WS2 | "让模型预测"管线(P_predict) | WS0 |
| WS3 | 造扰动 + 人工审计(C_FO / C_NoOp) | WS0;读 WS0.5 事件类型标签 |
| WS4 | 跑 pilot(冻结清单,跑算子,产出结果表) | WS0.5 + WS1 + WS2 + WS3 |
| WS5 | pilot 统计 + 预注册 | WS4 |

关键路径 `WS0 → (WS0.5 / WS1 / WS2 / WS3 并行) → WS4 → WS5`;计划内置两道
ML-Engineer 可行性闸门(WS0 之后、WS1–3 冒烟之后)。

---

## 8. 当前进度 [锚定,2026-05-22]

- **WS0** —— 基本完成(代码骨架、runstate DB、16 模型 pin、接口 memo 已签)。
- **WS1** —— 代码建好 + 全模型冒烟通过 + AutoDL 云开好 + Path E 探针集建
  好;尚未在 pilot 上正式跑。跑得最靠前。
- **WS0.5** —— 设计完成(decision memo v0.4),代码未动;设计正在重开,
  签字搁置。
- **WS2 / WS3 / WS4 / WS5** —— 均未开工。

重开操作化层几乎不浪费已写代码:WS0 / WS1 不在重开区,WS2–WS5 未开工。

---

## 9. 待重开项一览(R-1 … R-6)

Pass-1 全实验走查的结论:**研究问题与四层框架是 sound 的(锚定不动);但
框架与实现之间的「操作化层」欠充分推敲,进入结构化重开。** 全程采用
clean-room-first 方法(先白板独立分析,再对照既往 reviewer 意见)。

| 编号 | 重开对象 |
|---|---|
| R-0 | ✅ closed 2026-05-23 PM late → `refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/R0_DECISIONS.md` |
| R-1 | 4 个 confirmatory 因子:各自的实现方法 → 然后选择(Template Rigidity 从零设计);R-0 已解锁 R-1b / R-1c 的 construct 选择空间 |
| R-2 | 6 个扰动:各自实现构思 → 然后保留几个 / 哪几个进 confirmatory;perturbation-specific eligibility flag 由本 session 在 R-0 HOOK1 / HOOK2 占位上落地 |
| R-3 | 负对照的充分性 |
| R-4a | ✅ closed 2026-05-23 → `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4a_DECISIONS.md` |
| R-4b | pilot 具体数字(power、n_eff、混合模型规格落地、bootstrap),仍开放,等 R-1e / R-2 / R-3 / R-5 |
| R-5 | 采样准入过滤器 + 分布策略(R-0 已 expose Pool B + G/H/I + D/E/F 扩展位;within-pool 分布 R-5 全权决定) |
| R-6 | 预测目标 & 是否 / 如何使用真实收益 |

权威清单与每项细节见 `refine-logs/reviews/WALKTHROUGH_PASS1/pending_items.md`。本报告的
§4 与 §6 相关部分会随 R-1…R-6 的结论逐步更新为定稿。
