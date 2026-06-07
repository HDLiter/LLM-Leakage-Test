# Cross-synthesis findings — 2026-05-23 PM

> **⚠️ SUPERSEDED — 本文 A 节原版 menu 含 4 处误读, 不要直接采纳里面的具体
> 提议**(2026-05-23 PM, 用户在逐项 triage 中纠正,详见 commit `f55d8ca`
> message 内 Decisions audit 段 + 该 session 对话记录)。
>
> **误读类型 = 系统性偏差**:agent 看到漂亮 framework(Kong 2026 Structural
> Validity Framework)就倾向于强对齐到我们 benchmark, 没看清 Kong 是
> deployment-claim framework, 我们是 characterization benchmark, 两者
> framing 错配。具体误读点:
> - **🟡-2** "在 §6 加 Kong 5-check 1:1 mapping 表" — 错对齐(已 ✗ 撤销)
> - **🟡-3** 原版 "Kong entity substitution → R-1d Template Rigidity 设计
>   起点" — 双错(test 精神理解错 + factor 用算子结果定义违反 L1/L2/L4
>   边界);修正版 = R-2 新候选扰动 C_ES(已 ✓ 修正版)
> - **🟡-4** 原版 "Kong §2.2 → Target Salience metric endorsement" — 方向
>   反了(Kong 是 warn sampling 不是 endorse metric);修正版 = R-1c
>   sanity-check + R-5 sampling 策略扩展(已 ✓ 选 3 + 扩展)
> - **🟢-2 / 🟢-3** 同 🟡-2 类问题(强行对齐 framework)— 已 ✗ 撤销
>
> **仍 valid 部分**:
> - **F 节 (Kong vs 我们 7 条真实分歧)** — 用户从未否认, 防未来 session
>   再走"对齐 Kong"的路。
> - **B 节 (R-1x reopen session 准备)** — 大部分已被 worktable TODO 吸收,
>   但作为原始 routing 记录有 reference 价值。
> - **G 节 (PDF 重复处置)** — 已执行 ✓。
> - **C 节 memory 更新** — 已执行 ✓ 但 framing 弱化(不给 Kong anchor 地位)。
>
> **真实结论权威源**:
> - `commit f55d8ca` message 内 Decisions audit 段 (approved / rejected /
>   flag-only 完整审记)
> - `plans/worktable.md` §2 R-2 行后 4 个 TODO 段(🟡-3 / 🟡-4 / 🟡-5)+
>   §6 跨阶段挂账 Kong references mining 行
> - `docs/RESEARCH_PROPOSAL.md` §2.3 末 TODO(🟡-1)+ §4.7 末 TODO(🟡-4c)
> - memory `lit_landscape.md` Local collection + Consensus #5 新增
>
> 本文保留作 audit trail + 教训记录(系统性偏差自审),**不**作 R-1x kickoff
> input 权威源(权威源见 worktable TODO + commit message)。

---

> **Purpose** (原 session 自述,保留作历史): Synthesize three structural inputs that landed in the last
> 48 hours and were never read together. Output = prioritized
> ready-to-action menu for the user to triage (✓ / ✗ / 推后); each accepted
> item dispatches to a follow-up session. **This session does not change any
> files.**
>
> **Three inputs (all freshly read)**:
> 1. **R-4a methodology audit closed** (2026-05-23) — framework-level 8 items
>    locked, R-6 unblocked.
>    Sources: `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/whiteboard_analysis.md` +
>    `subfield_lit_scan.md` + `plans/worktable.md` §1/§4 + `pending_items.md`
>    R-4a-closed block + `docs/RESEARCH_PROPOSAL.md` §4.4.
> 2. **B-3+ WS0.5 infra-theme final-pass closed** (2026-05-23 PM) — §7
>    token-meter章节整体删除, §6.1 schema 收 11 列, closure 14→11,
>    cross-boundary 提案留给 R-1b/c/R-5 reopen.
>    Sources: `refine-logs/reviews/WS0_5_DESIGN/walkthrough_findings_20260523.md` +
>    `infra_quality_pass_20260523.md` + DECISION memo frontmatter v0.4 cont.
>    (2026-05-23 PM ...) + commit `bf2544e`.
> 3. **Kong et al. 2026** "Evaluating LLMs in Finance Requires Explicit Bias
>    Consideration", arXiv:2602.14233 (2026-02-15, position paper for ICML
>    submission scale; full paper read).
>    Note: PDF was **already in `related papers/` under two names** —
>    `Evaluating LLMs Finance Explicit Bias.pdf` (April-dated, indexed at
>    line 138) and `Evaluating LLMs in Finance Bias Consideration.pdf`
>    (today-dated, **unindexed duplicate** — see Section G).
>
> **Discipline**: 不改任何文件; 跨边界 findings 标 R-1x reopen 区不在本
> session 决定; 引用源 + 具体行号, 不泛泛而谈; 用户每条回 ✓ / ✗ / 推后
> 后分派对应 session.

---

## A. 立即可动菜单 (prioritized)

### 🔴 必动 (blocking 下游) — 0 项

R-4a closed 的元层结论已经把"reviewer-driven ratchet"诊断坐实, B-3+ 的
§7 整章删除把基建主题对齐。**没有发现新的 hard blocker**: 三件输入都在
"已收口" 或 "已转给下游 reopen" 状态, 不阻塞 R-1a-d/R-6 启动或 B-2
开工。

### 🟡 高杠杆 (framing / paper positioning)

#### 🟡-1. RESEARCH_PROPOSAL.md §1 motivation 引 Kong 2026 作为唯一同向位置论文 ★

- **位置**: `docs/RESEARCH_PROPOSAL.md` §1 (motivation 段)
- **现状**: motivation 段只锚 Profit Mirage 和 Lookahead Bias Test (memory
  `lit_landscape`); 没有把"为什么这件事现在该做"的最高层动机锚到一个
  field-level position paper.
- **建议变更**: §1 motivation 末尾加 1 段, 引 Kong et al. 2026 (ICML position
  paper, arXiv:2602.14233) — 把我们定位为 Kong **§2.1 Sin #1 Look-Ahead
  Bias / Issue 1 Parametric Knowledge Leakage** 在中文金融语料 + 16-model
  fleet 上的**因子受控经验性 benchmark**. Kong 提供 field-level diagnosis +
  framework, 我们提供 case-level measurement.
- **理由**: Kong 是目前唯一一篇把 LLM-in-finance bias 写成 position paper
  并做 164-paper review 的论文 (Kong §1 Figure 2: 164 papers 2023-2025;
  look-ahead 仅 26.8% 提及, parametric knowledge leakage 占 sin #1 一半).
  把我们的 framing 锚到他们的 Sin #1 Issue 1, 立刻有了 community-level
  motivation, 而不是单点抢救 Profit Mirage 的同向论文。
- **杠杆 / 工作量**: **high-leverage / low-effort** (~2 段 prose).
- **依赖**: 无.

#### 🟡-2. RESEARCH_PROPOSAL.md §6 + §6.5 加 Kong Temporal Sanitation 1:1 compliance section ★ (见 E 节单列)

- **位置**: `docs/RESEARCH_PROPOSAL.md` 新增 §6 子节 (与现有 §6.1/§6.2/§6.3
  并列, 例如 §6.4); 同步到 WS0.5 memo `docs/DECISION_20260518_ws0_5_thales_alignment.md`
  §6.5 (paper-level disclosure).
- **现状**: §6 写了 design memo / sealed split / transparency artifact 三件套;
  但没有 1:1 mapping 到任何 community-recognized framework. WS0.5 memo §6.5
  按 NeurIPS/ARR/ICLR 一般 norms 写, 没有针对 finance.
- **建议变更**: 新增"Kong (2026) Structural Validity Checklist 对照表",
  把我们的 artifact 1:1 映射到 Kong §3 五项 checklist. 详见 E 节.
- **理由**: 0 工作量 (artifact 已经做了, 只是 mapping); 强 framing (finance
  reviewer 一眼能看出我们对齐了刚出的 position paper checklist).
- **杠杆 / 工作量**: **high-leverage / very-low-effort** (1 张表).
- **依赖**: 无 (但应在 §1 motivation 引 Kong 之后, 见 🟡-1).

#### 🟡-3. R-1d Template Rigidity 设计直接采用 Kong §3.3 entity substitution test 作为 anchor probe ★

- **位置**: R-1d kickoff (本 session 不写, 见 B 节; 这里只标 framing 杠杆).
- **现状**: R-1d "零 spec, 用户视为重点因子" (worktable §4). 还没有锚定到
  任何 community-validated probe design.
- **建议变更**: R-1d 设计的 anchor probe 直接 port Kong §3.3 (page 6 末):
  "The evaluator should replace the target entity identifier while holding the
  rest of the prompt fixed and verify that entity-specific facts do not
  transfer." 这是 Kong Rationale Robustness check 的 operational test.
  Template Rigidity 可以围绕 "在 fixed template 内 swap target entity, 看
  prediction 是否跟着搬" 设计 — 这是 R-1d 的最自然 anchor.
- **理由**: 把 R-1d 的"从零"风险降到最低 — 有 community-recognized
  reference design 作起点, clean-room 仍成立 (Kong 没给具体度量,
  只给 test design); 而且 Kong 这条本身也是为 narrative bias 服务的, 跟
  我们的 leakage characterization 在同一 conceptual family.
- **杠杆 / 工作量**: high-leverage (R-1d 是用户点名的重点因子); R-1d
  自身工作量不变, 只是 kickoff 多 1 个 input.
- **依赖**: R-1d kickoff 之前定; R-1d 已 ✅ 可动 (R-4a closed).

#### 🟡-4. R-1c Target Salience kickoff 引 Kong §2.2 survivorship bias Issue 1 作为 construct justification ★

- **位置**: R-1c kickoff (本 session 不写, 见 B 节).
- **现状**: WS0.5 memo §3.3.2 把 Target Salience 改成 log CLS mention count;
  C-1 redesign 的理由写在 memo 里 ("market cap measures size not fame,
  misclassifies 妖股"). 但缺一个 community-level justification.
- **建议变更**: R-1c kickoff 把 Kong §2.2 (Survivorship Bias, Issue 1, page 3)
  作为 input — Kong 原文:"media coverage inherently correlates with ongoing
  corporate activity and investor attention, firms that fail or quietly exit
  the market tend to be underrepresented". 这**直接**支持我们用 CLS mention
  count 作 prominence proxy 的 construct 选择 (媒体覆盖 = 真实存活/活跃度
  proxy, 与市值无关).
- **理由**: 把 C-1 redesign 的论证从"agent 自己想清楚"升级为"position
  paper field-level 论证支持". 同时也让 R-1c 的 clean-room 复审有 anchor.
- **杠杆 / 工作量**: high-leverage / very-low-effort (kickoff 多 1 段 input).
- **依赖**: R-1c kickoff 之前定; R-1c 已 ✅ 可动.

#### 🟡-5. R-2 C_FO + C_NoOp 重审, 把 Kong §3.3 双 probe 作为同行 anchor ★

- **位置**: R-2 kickoff (待 R-6 解锁, worktable §2; **R-6 已解封** 2026-05-23,
  R-2 可启动顺序变近).
- **现状**: 用户点名重审 C_NoOp (pending_items §R-2); C_FO 机制有 parked
  C_FO/C_SR 漂移 (`refine-logs/reviews/REOPEN_R1_R6/cfo_csr_history_findings.md`).
- **建议变更**: R-2 kickoff 把 Kong §3.3 (page 6-7) 整段作为 input —
  Kong 明确写"entity substitution tests to detect reliance on parametric
  memory over context" (= 我们的 C_FO) + "negative controls should use
  scrambled or irrelevant inputs to confirm that the system does not produce
  detailed causal stories or confident trades" (= 我们的 C_NoOp_placebo).
  Kong 把两者放在同一 Rationale Robustness check 下, 印证我们 C_FO 与
  C_NoOp 共同服务于 narrative robustness / parametric memory probe 的
  construct group.
- **理由**: R-2 的"保留几个, 哪几个进 primary" 决定有了一个 field-level
  reference: 至少 C_FO + 一个 negative control 是 Kong 框架下不能省的;
  C_SR/C_anon/C_temporal/C_ADG 都不在 Kong 列里 (但 Kong 也不穷举).
- **杠杆 / 工作量**: high-leverage; R-2 自身工作量不变.
- **依赖**: R-2 (待 R-6 解锁; 现在 R-6 已解封, R-2 顺序可前移).

#### 🟡-6. memory `lit_landscape.md` 加 Kong 2026 作为定位 anchor ★

- **位置**: `C:\Users\HDLiter\.claude\projects\D--GitRepos-LLM-Leakage-Test\memory\lit_landscape.md`
  "Local collection" 段; "Our Unique Position" 段加 1 行.
- **现状**: 已列 Profit Mirage / All Leaks Count / Lookahead Bias Test /
  Your AI Not Your View; 没有 Kong 2026; "Our Unique Position" 段没把
  position-paper-anchor 这件事说出来.
- **建议变更**: (1) "Local collection" 加 1 行: Kong et al. (2026, ICML
  position paper): Structural Validity Framework + 164-paper bias review;
  我们的 framing anchor for Sin #1 Issue 1 (Parametric Knowledge Leakage).
  (2) "Our Unique Position" 段加 1 行: 我们是 Kong §2.1.1 在中文金融语料 +
  16-model fleet 上的因子受控 empirical benchmark.
- **理由**: 后续 session (任何 agent) 都会读 memory, 这条 anchor 一加, R-1
  系列、paper writing、rebuttal 都能引用统一 framing.
- **杠杆 / 工作量**: high-leverage / very-low-effort (2 行).
- **依赖**: 无.

### 🟢 nice-to-have

#### 🟢-1. R-3 负对照充分性把 Kong §3.3 "scrambled or irrelevant inputs" 作为框架佐证

- **位置**: R-3 kickoff (现在 ⛔ 待 R-1e + R-2, worktable §2).
- **建议变更**: R-3 kickoff 把 Kong §3.3 末句作为"为什么负对照重要"的
  community anchor. Kong 说"negative controls should use scrambled or
  irrelevant inputs to confirm that the system does not produce detailed
  causal stories or confident trades" — 这覆盖 BL1 (text-light) + C_NoOp
  (irrelevant insert) 两类的精神, 不直接支持 BL2 (post-cutoff) 那种时间型
  负对照. 用 Kong 加强 BL1 + C_NoOp 正当性; BL2 仍按 R-4a TOST 框架.
- **理由**: R-3 现在的"充分性"质疑没有外部 anchor; Kong 给了 partial 支撑.
- **杠杆 / 工作量**: nice-to-have / low-effort.
- **依赖**: R-3 待 R-1e/R-2.

#### 🟢-2. WS0.5 memo §6.5 limitations item 4 加一条 Kong-compliance gap (cost bias 不在 scope)

- **位置**: `docs/DECISION_20260518_ws0_5_thales_alignment.md` §6.5.
- **现状**: §6.5 当前 4 条 limitations (closed-API snapshot / nondeterminism /
  private Tier B / compute disclosure via post-hoc + monthly statement).
- **建议变更**: 加第 5 条: 我们的 benchmark 不评估 Kong Sin #5 (Cost Bias) —
  latency / inference cost / market impact 都不在 scope; 这是 academic
  measurement benchmark 而非 deployment-readiness study, 跟 Kong's
  realistic implementation check 是不同 use case. 主动 disclosure 这一点
  避免被 reviewer 用"why no cost analysis" 反问.
- **理由**: 主动划清 scope 是好的 framing 防御 — 而非等 reviewer 提出.
- **杠杆 / 工作量**: nice-to-have / 1 句话.
- **依赖**: 无.

#### 🟢-3. RESEARCH_PROPOSAL.md §1 动机段加一句"为什么是 finance 而非通用 benchmark"

- **位置**: `docs/RESEARCH_PROPOSAL.md` §1.
- **现状**: 没显式答这个问题; 默认读者认为 finance 是因为 Thales 起家.
- **建议变更**: 加一句, 引 Kong §1: finance 是 LLM bias 评估缺口最大的
  领域之一 (Kong 164-paper review: 50% 受访者认为评估工具缺乏是最大瓶颈).
  我们刚好同时具备 (a) 大规模中文金融语料 (b) cutoff 横跨型 fleet (c)
  Thales 沉淀的 entity / event taxonomy. 这 3 个条件交集少, 因此选这里.
- **理由**: 防 "why this corpus / this language / this fleet" 类问题.
- **杠杆 / 工作量**: nice-to-have / 1 段.
- **依赖**: 无.

### 💭 仅 flag (不建议本轮动)

#### 💭-1. R-4a 已 closed, 不要被 Kong 反向重开

Kong §3 checklist 是 **binary pass/fail** (Figure 10), R-4a 锁定的"main /
primary / supporting / robustness / appendix" 标签 + per-estimand 混合模型
+ Gwet's AC1 都是 dimensional. **不要因为 Kong checklist 漂亮就把 R-4a
退回二元化**. Kong 是 framework 层, R-4a 是 statistical-practice 层,
两层并存即可. (相关: F-1.)

#### 💭-2. Kong §6 Related Work 没引 LLM memorization 子领域代表作

Kong §6 (page 8) "Bias in LLMs for Finance" 段只列 financial-bias-direct
论文, 没引 Carlini 2023 / Shi 2024 / Duan 2024 / Oren 2024 等 memorization
基础工作 — 这是他们 Related Work 的 gap, 不是我们的问题. 但**对我们的
positioning 反而是好事**: 我们可以同时引 Kong (finance framing) + Carlini
家族 (technical method anchor), Kong 的论文里这两条线没接上, 我们能接.
flag 给未来 paper writing.

#### 💭-3. Kong §3 Dynamic Universe Check 我们部分不满足 (delisted firms)

Kong §3.2: "The benchmark should report negative cases that represent
distress and failure regimes". 我们 sampling 通过 §3.3.1 admissibility
要求 "tradable target", 在 listing 历史上是否包含 delisted 案例 — 当前
WS0.5 memo §3.3.1 没明说. 这是真实 gap 但 (a) WS0.5 memo §6.5 已经写
limitations (b) walk-through A.4 用户提的 "drop articles where A-share
entity was unlisted at publication time" 反而**加剧**这个 gap.
**仅 flag 给 R-5 reopen**, 不在本轮决定.

#### 💭-4. Kong 提到 BlackRock disclaimer (Kong page 9)

Kong 作者多个在 BlackRock; 论文末 "The views expressed in this work are
those of the authors alone and not of BlackRock, Inc." — flag 给后续
paper writing / submission strategy 时注意. 影响:
- Position paper 多半会过 ICML; 我们引它是稳的 framing.
- 如果我们投同一 venue (ICML/NeurIPS 工作坊或主会), Kong 的 acceptance
  status 会决定我们引用方式 (in submission / accepted / arXiv only).

---

## B. R-1 reopen session 准备 — input 增量

每个 R-x kickoff 应**新增**(不是重写)以下 input 段. 注意 R-4a 已 closed,
R-4a 的 8 条框架级 lock 已经是所有 R-1/R-2/R-6 的 upstream 约束 —
下面只列新加的 (Kong + B-3+ walkthrough 来源):

### R-1a Cutoff Exposure
- **Kong 输入**: §3.1 Temporal Sanitation (page 6) 是我们 cutoff 因子的
  community framing — Kong 强调 "the latest calendar date represented for
  pre-training, as well as in any subsequent fine tuning and instruction
  tuning that produced the deployed weights" 必须 disclosed. 我们 fleet
  16-model cutoff 数据已建; R-1a 应在实现设计里直接套 Kong 这条 disclosure
  框架 (per-model cutoff dict + which-came-from-which evidence).
- **B-3+ 输入**: 无新增 (cutoff 是 case×model 因子, 不在 WS0.5 walk-through
  scope).

### R-1b Historical Family Recurrence
- **Kong 输入**: 无直接对应 — Kong 不区分 mention-based vs subject-based
  recurrence; 这是我们独有的 construct dimension. **见 F-3** (Kong gap, 我们
  独有).
- **B-3+ 输入**: walkthrough A.1 (4-layer corpus stratification) + A.2
  (subject-vs-mention construct shift) 是 R-1b 的**核心新输入**.
  `walkthrough_findings_20260523.md` §A.1 + §A.2 整段必须在 R-1b kickoff
  阅读. 用户 A.2 例子 ("券商今日金股: 茅台/五粮液/招行" 算不算茅台的
  Recurrence) 直接定 R-1b 的 construct semantics.
- **R-4a 已设的约束** (提醒不重复): primary family 大小不锁 — Recurrence
  作为 case-level continuous factor, R-1b 设计完后由 pilot 决定是否进
  primary.

### R-1c Target Salience
- **Kong 输入**: §2.2 Survivorship Bias Issue 1 (page 3) — "media coverage
  inherently correlates with corporate activity and investor attention" —
  直接支持 CLS mention count 作 prominence proxy 而非市值 (= C-1 redesign
  的论证升级). **kickoff 重点 input**.
- **B-3+ 输入**: walkthrough A.3 (subject-ID via LLM 替换 §3.3.1
  deterministic centrality rule) + A.4 (listing-status filter) 是 R-1c
  scope. `walkthrough_findings_20260523.md` §A.3 + §A.4 整段读.
- **R-4a 提醒**: §3.3.1 admissibility test 不是 statistical claim, 不受
  multiplicity 影响; R-1c 重点是 construct 而非统计.

### R-1d Template Rigidity
- **Kong 输入**: §3.3 Rationale Robustness (page 6 末段) — "entity
  substitution tests" 直接是 Template Rigidity 的 community-validated
  probe design starting point. **kickoff 头号 input**. 用户称 R-1d "零
  spec", Kong 这段就是 spec 起点.
- **B-3+ 输入**: 无 (Template Rigidity 不依赖 WS0.5 管线).
- **R-4a 提醒**: Template Rigidity 是 case-level continuous factor; 进不进
  primary 由 R-1e 实证 + pilot 决定.

### R-2 (扰动: C_FO / C_NoOp / C_anon / C_SR / C_temporal / C_ADG)
- **Kong 输入**: §3.3 (page 6) "entity substitution tests" + "scrambled or
  irrelevant inputs as negative controls" — Kong 把这两类放在同一
  Rationale Robustness check, 印证 C_FO + C_NoOp_placebo 是同行 framework
  下的 minimum-2-probe. **R-2 kickoff 必读**.
- **B-3+ 输入**: walkthrough A.5 (LLM-tagged alias risk replacing R2
  deterministic) — held until A.2 lands; 与 R-2 间接交叉 (R2 entity risk
  rule).
- **R-4a 提醒**: C_NoOp 已 R-4a 锁定为 supporting (非 primary memorization
  signal), R-2 不要把它升回 primary 除非有强 empirical reason.

### R-5 (采样准入过滤器)
- **Kong 输入**: §3.2 Dynamic Universe (page 6) — "include negative cases
  that represent distress and failure regimes" — 这与用户 A.4 提的 "drop
  articles where A-share entity was unlisted at publication time" 反向 (Kong
  要保留 delisted/失败案例, 用户提的 filter 会 amplify survivor bias).
  **R-5 kickoff 必读**, 必须先解决这个张力. (见 💭-3.)
- **B-3+ 输入**: walkthrough A.4 (drop too-long news / bundle flashes /
  unlisted-at-publication) — `walkthrough_findings_20260523.md` §A.4 整段
  读. 长度过滤 / bundle 过滤无 Kong 张力, 可正常推进.
- **R-4a 提醒**: 采样过滤器服务 primary family 有效样本; R-5 决定不影响
  R-4a 框架级 8 条.

### R-6 (预测目标 & 真实收益)
- **Kong 输入**: §2.4 Objective Bias (page 5) — Kong 强调 "the action space
  should include explicit abstention, such as a 'No Trade' or 'Do Not Know'
  option". 我们当前 P_predict schema 是 "direction (涨/跌/中性) + confidence
  0-100". **"中性" 是否等同于 "No Trade" / "Abstention"?** R-6 应回答这个
  schema 问题: 中性是 "prediction = no movement" 还是 "abstention"?  Kong
  给 "中立 + 0 confidence" vs "明确 'I don't know'" 的 distinction 提供了
  framing 依据.
- **B-3+ 输入**: 无直接 (R-6 不在 walk-through scope).
- **R-4a 提醒**: 加新 confirmatory estimand 要替换或开新 design memo
  (R-4a 不锁 primary 数). R-6 决定 P_predict schema 时, 用真实收益作
  covariate / difficulty score / filter 不增 estimand; 作 primary
  estimand 才需要替换.

---

## C. memory + index 更新

### C.1 必更新

| 文件 | 操作 | 内容 |
|---|---|---|
| `memory/lit_landscape.md` | add | "Local collection" 加 Kong 2026 一行; "Our Unique Position" 加一行 anchor (见 🟡-6) |
| `related papers/INDEX.md` | **无操作** | INDEX 已有 line 138 (`Evaluating LLMs Finance Explicit Bias.pdf`). 文件已存在 |

### C.2 待决定 (问用户)

| 文件 | 决定项 |
|---|---|
| `related papers/Evaluating LLMs in Finance Bias Consideration.pdf` | 这是与 INDEX line 138 同一篇 paper 的 **today-dated 重复文件** (3,908,409 bytes, May 23 创建). 删 / 保留? 见 G 节. |

### C.3 不开新 memory 条目

考虑过的、不开的:
- **不开** `kong_2026_framing.md` — Kong 是单篇 paper, 不是 ongoing project
  state; `lit_landscape.md` + RESEARCH_PROPOSAL §1 引用即可. 开 memory
  会重复 `lit_landscape` 的功能.
- **不开** `feedback_kong_compliance.md` — Kong 的 compliance 是一次性
  framing 决定 (E 节 1 张表), 不是 ongoing 行为约束, 不符合 feedback
  memory 的判断标准.
- **不更新** `project_status.md` — R-4a closed + B-3+ closed 已在 worktable
  §1, project_status memory 已有 "Pass-1 全实验走查完成" 一句, 不需要再加
  Kong 这一条 (不是 project status 变化).

---

## D. 论文 framing 升级机会 (`docs/RESEARCH_PROPOSAL.md`)

汇总 A 节里的相关项, 集中给 paper-positioning view:

### D.1 §1 motivation
- 🟡-1: 加 Kong 2026 作为 field-level position anchor; 我们 = Kong §2.1.1
  Parametric Knowledge Leakage 在中文金融 + 16-model fleet 上的 empirical
  benchmark.
- 🟢-3: 加 "为什么 finance / 中文 / cutoff 横跨 fleet" — 3 个条件交集少,
  Kong 164-paper review 50% 报"工具缺乏"为最大瓶颈.

### D.2 §2 related work (如果有)
- RESEARCH_PROPOSAL 当前看似没有独立 §2; framing 散在 §1 + §4. 如果未来
  paper draft 加 related work, Kong 必引 (position paper, 直接同向);
  Carlini 2023 + Shi 2024 + Duan 2024 必引 (technical method anchor).
- Kong §6 自己 related work 没接 memorization 子领域 (见 💭-2), 反而是
  我们的 niche.

### D.3 §6 transparency artifact
- 🟡-2 + E 节: 加 Kong Structural Validity Checklist 1:1 mapping 表 (E 节
  详细).

### D.4 §11 limitations (如果有) 或 §6.5 (WS0.5 memo)
- 🟢-2: 加 "不评估 Kong Sin #5 Cost Bias" 主动 disclosure.
- 💭-3: flag delisted-firms gap (R-5 reopen scope; 不在本轮 commit).

### D.5 rebuttal/skill 储备
- 如未来 ICML/ARR 投稿 rebuttal, Kong 是 "framework alignment" 的现成
  defense citation.
- Kong §A user study 50 respondents 给 community-level pain point evidence —
  rebuttal 中"为什么这件事重要"可以直接引数据.

---

## E. §6.5 Kong-compliance section 1:1 mapping (单列, 高杠杆低成本)

**位置**: 新增到 `docs/DECISION_20260518_ws0_5_thales_alignment.md` §6.5
(paper-level disclosure) 或 `docs/RESEARCH_PROPOSAL.md` 新增 §6.4.

**理由**: Kong §3 给 5-check framework, 我们 artifact 已经做了大部分,
**只缺一张 mapping 表** — 0 implementation 工作量, 强 reviewer-facing
framing.

### 1:1 Mapping 表 (建议直接落到 prose)

| Kong §3 Check | Kong 子要求 (page 6-7) | 我们的 artifact | 状态 |
|---|---|---|---|
| **Check 1: Temporal Sanitation** | Parametric Knowledge Cutoff Disclosure | fleet 16-model cutoff dict (`config/fleet/r5a_fleet.yaml`) + Path E 经验探针 (WS1) | **Pass** (white-box; black-box hedged "operator-asserted") |
| | Point-in-Time Retrieval | 不适用 — 我们 no RAG | **N/A** |
| | Full Trace Logging | Tier A `pilot_raw_responses.jsonl` + Tier B SQLite cache + `factor_provenance.json` (WS0.5 §6) | **Pass** |
| **Check 2: Dynamic Universe** | Time-Indexed Tradable Universe | §3.3.1 admissibility 要求 tradable target; 但**没显式建 time-indexed universe** — 当前用 publication-time listing status (R-5 reopen scope) | **Partial / R-5 flag** (见 💭-3) |
| | Unbiased Task Sampling | 因子 × event-family × cutoff 分层采样 (plan §6.4 n_eff matrix; R-4a 决定 quotas) | **Pass** |
| **Check 3: Rationale Robustness** | Entity Substitution Test | C_FO (counterfactual entity/value swap; R-2 reopen) | **Pass** (R-2 落定后) |
| | Negative Controls (Scrambled/Irrelevant) | C_NoOp + BL1 text-light challenger (R-3 reopen) | **Pass** (R-3 落定后) |
| | Audit Trail with Citation | `factor_provenance.json` per-cell trace + WS3 人工审计 Gwet's AC1 矩阵 | **Pass** (R-4a 已锁 Gwet's AC1) |
| **Check 4: Epistemic Calibration** | Calibrated Confidence | P_predict 输出 0-100 confidence (R-6 待定 schema 细节) | **Pass** (R-6 后定稿) |
| | No Trade / Abstention Action | P_predict 当前 "中性" 选项 — 是否等同 abstention? **R-6 应明确** | **R-6 flag** |
| **Check 5: Realistic Implementation** | Net Cost / Latency | 不评估; benchmark 是 academic measurement, 非 deployment study | **Disclosed N/A** (见 🟢-2) |

**注**: 11 子项中 7 Pass / 1 N/A (RAG) / 1 N/A-disclosed (Cost) / 1
Partial-R-5 / 1 R-6 flag — 整体 framework-align 强, gap 全部在 reopen 区,
不影响本轮.

**对 paper 的好处**:
1. Finance reviewer (尤其 ICML/NeurIPS finance workshop) 一眼能 verify 我们
   对齐了 community 最新 position framework.
2. 主动 disclosure N/A (RAG / Cost) 防"为什么没有"反问.
3. R-5 / R-6 的 Partial / flag 反而是诚实 framing — 不是 hide-the-ball.

---

## F. 注意 / 不要照搬 — 我们与 Kong 的真实分歧

### F.1 Kong 是 binary pass/fail; 我们 dimensional
- Kong §3 checklist 全部 Select Status: Pass / Fail / N/A (Figure 10).
- 我们 R-4a 锁定的是 effect size + 95% CI + per-estimand 混合模型 —
  **dimensional**, 不是 pass/fail.
- **不要因为 Kong checklist 漂亮就把 R-4a 退回二元化** (见 💭-1).
- E 节 1:1 mapping 表是 framing-level 对照, 不是 statistical-practice 改向.

### F.2 Kong 写 deployment claim; 我们写 characterization claim
- Kong §1: "minimum requirements for interpreting a reported backtest as
  evidence of **deployment performance**".
- 我们 RESEARCH_PROPOSAL §1: 因子受控 **characterization benchmark** of
  leakage — 是 measurement 而非 deployment readiness.
- 不要被 Kong 推到"做 deployment claim" — 我们故意不做, 反而是论文 scope
  防御.

### F.3 Kong 不讨论 subject-vs-mention 这一构件维度
- 用户在 walk-through A.2 提的 mention-based Recurrence vs subject-based
  Recurrence — Kong 没碰. 这是中文金融语料 + 财联社 list-style 电报的
  独有 construct 选择 (券商今日金股那种 list 文章).
- R-1b 设计这一项要原创, 不能套 Kong.

### F.4 Kong 不区分 white-box vs black-box leakage detection
- Kong §2.1.1 只说 "parametric knowledge leakage" 是一类 channel, 没
  分 logprob-based vs prediction-based detection methods.
- 我们 16-model split-tier fleet (12 white-box P_logprob + 14 P_predict)
  是 Kong 框架的 finer-grained instantiation, 不是 Kong 给的设计.

### F.5 Kong 是 position paper, 没做 empirical benchmark
- Kong §6.1: "168 main conference papers reviewed" + 50 respondent user
  study — 但**自己没跑 benchmark**.
- 我们是 empirical complement, Kong 是 conceptual framework. 两层互补,
  不要让我们 paper 变成 "Kong-restated".

### F.6 Kong 的 Sin #3 Narrative Bias 我们 partially 触及但非中心
- Kong §2.3: "LLM 写出 plausible but ungrounded coherent story".
- 我们 P_predict 当前 schema "direction + confidence + memory_flag +
  evidence" 里的 `evidence` 字段是 narrative 类输出 — 但我们不评估
  narrative quality, 只用其作 memorization self-report 提示.
- 不要被 Kong 推到 "做 narrative bias evaluation" — 那是另一个 benchmark.

### F.7 Kong 没给 estimand 设计, 只给 framework
- Kong §3 全是 "什么应该 disclosure / 什么应该 test", 没给 effect size /
  power / multiplicity 这类 statistical-practice level 答案.
- 因此 R-4a 锁的 8 条 (无 family correction / Gwet's AC1 / TOST/SESOI=0.15
  限定 BL2 / scenario-based MC power 等) **不受 Kong 影响**, 不需要因为
  Kong 重审.

---

## G. 副产物 — Kong PDF 三重复需用户决定

### 现状
本 session 启动时, `related papers/` 已存在两份 Kong paper:
1. `Evaluating LLMs Finance Explicit Bias.pdf` (April-dated, **INDEX.md
   line 138 引用**) — 3,908,409 bytes.
2. `Evaluating LLMs in Finance Bias Consideration.pdf` (today-dated May 23,
   **未索引**) — 3,908,409 bytes.

本 session 又下载了:
3. `Kong 2026 Evaluating LLMs in Finance Requires Explicit Bias Consideration.pdf`
   (today-dated) — 同 bytes.

**已删除 #3** (本 session 自创的副本, 安全回滚).

### 待用户决定
**#2 (`Evaluating LLMs in Finance Bias Consideration.pdf`)** 是 today-dated
副本, **不在 INDEX.md**, 但和 #1 同 byte. 建议:
- 选项 A: 删除 #2, 保留 #1 (匹配 INDEX.md 现状) — 推荐.
- 选项 B: 重命名 #1 / #2 中之一为更规范的名字 (例如 `Kong 2026 Evaluating
  LLMs in Finance Explicit Bias.pdf`), 同步更新 INDEX.md.

本 session 不动. 用户决定后下 session 处理.

---

## H. 本 session 元

- 输入读取时间: 2026-05-23 PM.
- 写文件: 0 个 (只本 synthesis 文件).
- 删文件: 1 个 (`Kong 2026 ... Explicit Bias Consideration.pdf` — 本 session
  下载的副本, 与 INDEX.md line 138 的已有文件 byte-相同).
- 改文件: 0 个.
- commit: 0 个.
- 用户行动: 对 A 节每条标 ✓ / ✗ / 推后; 对 G 节决定 #2 处置.
- 下游 session: 按 ✓ 项分派 (主要是 R-1b/c/d/R-2/R-5/R-6 reopen kickoff
  + paper §1/§6 prose 编辑 + memory 更新 + WS0.5 memo §6.5 patch).
