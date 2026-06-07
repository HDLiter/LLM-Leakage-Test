# R-1b Second-opinion (Claude, blind) — 段 (b) / (c) / (h)

> **Reviewer note**: I have not read `whiteboard_analysis.md`, `construct_stress_test.md`,
> `construct_second_opinion_claude.md`, or `worktable.md §7.3`. (a) is locked at
> **L2 subject + `tradable_at_event=true`** with the outcome-leakage proxy立场;
> (b) / (c) / (h) below take that as input and推 from R-0 container, R-4a 8 条,
> proposal §1-3 / §4.1 / §4.4, framework §1-5, and §4.5 / §5 / walkthrough §A /
> R-0 §3 history.

---

# 段 (b) Family granularity

(a) 的 B 立场: 我们在测**关联记忆** —— 模型用记住的 "(target, 事件家族) →
涨跌方向" 关联代替读文本推理。Recurrence 是这个关联在 cutoff 前 CLS 里
有多结实的代理。这把 (b) 推到一个很具体的判据上:**什么 grouping 让
"(target, family) → outcome direction" 这个关联最 identifiable?**

如果把 grouping 做得太粗(target-only,所有事件混算),不同 family 的
outcome direction 通常不对齐(POLICY 利好和 LEGAL 罚单 outcome 方向相
反),关联记忆在 grouping 内被自相抵消,Recurrence 信号被稀释。如果做
得太细(target × raw 13-class),每个 (target, family) cell 容易 0 命中,
连续 log1p 的 variance 被压扁,β3 的 power 烧光。**两个轴的合理位置都
落在中间档**。

## 主键轴

### 候选 + trade-off

| 候选 | 在 (a) B 立场下的解释 | trade-off |
|---|---|---|
| **单标的(同一只股票)** | "模型对这只股票的 outcome 记忆多 stale" | 最干净的 identifiability;但 grouping 内 mix 不同事件方向,outcome direction 被对冲 |
| **一级行业(SW Level 1 / 28 类)** | "模型对这个行业的 outcome 记忆多 stale" | grouping 内更同质(白酒整体 vs 银行整体的 outcome 通道不同);但 industry-level 的 outcome direction 在单只 case 上未必和 industry 平均一致 —— construct slippage 风险 |
| **二级行业(SW Level 2 / 100+ 类)** | 介于上两者之间 | 信号弱中间档,既没拿到细粒度也没拿到聚合;典型 split-the-baby |
| **指数成分股 / 概念板块** | "热点板块"的 outcome 记忆 | 概念板块本身就是 ex-post 后视镜分类(谁是 "AI 概念股" 取决于何时定义);用作 grouping key 是 R-6 反直觉污染入口,**直接 disqualify** |
| **市值分档 / 实控人** | 介于 firm-specific 和 group | 跟 outcome direction 的关联弱(市值大不直接预示某 case 涨跌);drop |

### 主选 + 主理由

**主选: 单标的(同一只股票)。**

主理由(三条,与 (a) 一致):

1. **(a) B 立场要求 identifiability**。"模型用记住的 outcome 替代推理"
   最 identifiable 的层级是 firm-level。"茅台 H1 利润超预期" 的 outcome
   (股价方向)是这只股票自己的事;聚到白酒行业上,outcome 方向被五粮液 /
   洋河等同业稀释。**关联记忆是 firm × event,不是 industry × event**。
2. **R-0 已锁 L2 schema 没有 industry 字段作 first-class**。行业作 group
   key 需要额外 join 一个 SW 行业 master,而 SW 行业分类会随时间调整(成
   分股变更),引入 outcome 之外的 ex-post 信息。这违反 R-4a §1 / R-0
   §4.5.D 的 "factor metrics 在 operators 之前冻结" 原则的精神。
3. **R-1c (Target Salience) 的天然 anchor**。Salience 几乎肯定要落在
   firm-level(行业 Salience 没意义)。R-1b 用单标的主键和 R-1c 同
   axis,使两者的 VIF 检查在 §3.3.3 / §5.5 框架内可直接做,
   complement-family fallback (§3.3.2) 才有定义。

### 非主选去向

- **一级行业**: **drop**。不进 robustness。理由: 没有具体激活 condition
  能让 industry-level grouping 优于 firm-level(它的存在前提是 firm-level
  power 不够,而 power 短缺 R-4b 已经有 entity-balanced sampling 等其他工
  具应对);它跟 (a) 的关联记忆立场是 construct slip,不只是 power 弱。
  保留它当 robustness = "用 robustness 藏决策" 反模式。
- **二级行业 / 概念板块 / 市值分档**: 同样 drop;无激活 condition。

## 事件折叠轴

### 候选 + trade-off

| 候选 | 在 (a) B 立场下的解释 | trade-off |
|---|---|---|
| **不切(主键内所有事件混算)** | "对这只股票任意事件的 outcome 记忆" | outcome direction 在事件间方向不一致,关联记忆稀释 |
| **5 大事件超类(Scheme A)** | "对这只股票这类事件(政策决定 / 公司催化剂 / 业绩数字 / 市场宏观 / 行业)的 outcome 记忆" | 每个 super_type 内 outcome direction 通道相对一致(POLICY+ENFORCEMENT 都是 authority decision 同方向集);R-0 已锁 super_type 是 L1/L2 上的字段,join 成本 0 |
| **13 类原始事件类型(V3)** | "对这只股票这个具体事件类型的 outcome 记忆" | 最细;但 (target, event_type) cell 大量 0 命中,连续 log1p 退化成大量 0 + 长尾;且 13 类有些(如 GEOPOLITICS / OTHER)对 firm 层关联弱 |
| **按 outcome direction 直接 group(利好 / 利空 / 中性)** | 直接 group outcome direction | 这就是 outcome leakage itself —— 用 ex-post outcome 给 family 做 group;construct circular,disqualify |

### 主选 + 主理由

**主选: 5 大事件超类(Scheme A)。**

主理由:

1. **outcome direction 同向性**: super_type 内的 outcome 通道大体同向
   (authority_decision 内政策利好 / 罚单利空 是同一种 outcome 机制下的
   方向集;issuer_catalyst 内并购 / 高管变动 是公司催化剂同一通道;
   issuer_quant 是业绩数字)。这保留了关联记忆的 identifiability,而 13
   类的细分对 firm × event_type 的 outcome 方向区分意义不大(POLICY 和
   ENFORCEMENT 在 firm-level outcome 上都是 "监管动作的方向" 同一记忆模
   式)。
2. **R-0 zero cost**: §4.5.A L1/L2 已经 carry `event_super_type`
   字段。13 类同样 zero cost(`event_type` 也 carry),但 13 类的
   cell 稀疏度严重影响连续 log1p 的 distribution。
3. **N=780 / 2,560 的 cell 健康度**: pilot 主体 80 pre-cutoff + main run
   2,560 总样本,如果用 13 类 × ~hundreds of targets,每个 (target,
   event_type) cell 的 recurrence count 期望非常稀疏。5 类相对健康。
4. **R-4a §1 无 family-wise correction**: super_type 的 5 档 不增加
   multiplicity 负担,因为我们做的是 case-level 连续 factor,不是 5 个
   factor。这条 trade-off 在 R-4a 锁后是弱的(原 worktable hint 提到的
   multi-grain 顾虑被 R-4a 解掉了)。

### 非主选去向

- **不切(target-only 事件混算)**: **drop**。无激活 condition;它的"统
  计 power 高"优点假设来自 "0-cell 少",但 (a) B 立场下 outcome 方向稀
  释问题更严重 —— 它不是 power 不足,而是 construct 不再贴住关联记忆。
- **13 类 raw event_type**: **conditional robustness, single condition**:
  *if pilot 数据上 (target × super_type) 的 within-bin variance 在
  `issuer_catalyst` 这类杂超类内显著高于其他超类 → 表明 super_type 折叠
  在该类内 over-aggregating,提一个 13 类 robustness 复算只针对该
  super_type 拆开*。**否则 drop。** 这是有具体激活 condition 的 robustness。
- **outcome direction grouping**: **drop**。construct circular,任何
  condition 下都不该激活。

## 组合主选 + 配对

### 主选组合 + 1 行公式

**主选: (target, event_super_type) — 单标的 × 5 超类。**

```
recurrence_count[case_id] =
  COUNT( reference rows where
           target_entity_id == case.target
         AND event_super_type == case.event_super_type )

log1p_recurrence[case_id] = log1p(recurrence_count[case_id])
```

reference rows = L2 subject + `tradable_at_event=true` (已锁 (a) B 立场)。

### Condition-pinned robustness (0-2 个)

**只保留 1 个 robustness, 1 个 sanity diagnostic, 都有明确 condition。**

1. **Robustness 1 — 单标的 × raw event_type 拆,仅对 super_type 内 variance
   异常的超类。**
   - **激活 condition**: pilot 数据 (N=80 pre-cutoff) 上,某个
     super_type 内 within-bin 的 log1p_recurrence variance > 1.5×
     其他 super_type 的中位 variance。
   - **作用**: 仅对该 super_type 拆 raw event_type,看 β3 是否仍然 robust。
   - **不激活则 drop**。

2. **Diagnostic — Recurrence vs Salience 的 super_type-stratified
   correlation(§3.3.3 / §5.4 / §5.5 已锁的 discriminant)。**
   - **激活 condition**: 总是激活(已是 R-4a / WS0.5 §3.3.3 的 standing
     diagnostic);R-1b 这里不新增,只指明输入是 (target × super_type)
     的 recurrence。
   - **作用**: 监控 VIF;若 VIF ≥ 10 或 |r| ≥ 0.90,触发 §3.3.2
     complement-family fallback。

### Diagnostic appendix

**无其他 diagnostic**。任何额外 grain 的 diagnostic 必须 owner 给具体
condition 才进入;否则按 owner reject "fence-sit robustness" 原则 drop。

---

# 段 (c) Lookup window

(a) B 立场: Recurrence 测的是 "模型训练时 (target, family) → outcome 关
联被反复强化的强度"。这要求窗口内每条 reference row 必须满足两点: (i)
**model 训练时可能见过**(否则它不在记忆里),(ii) **outcome 在写作时
已经发生**(关联记忆需要 outcome 存在,见 (a))。第二点对窗口的影响是:
post-event rows(事件发生后追踪报道)更可能 carry outcome,pre-event rows
(事件前预测 / 传闻)的 outcome 还未实现,关联弱。

## 候选 + trade-off

### 候选 1 — 固定窗口 `[corpus_start, earliest_model_cutoff)`

- **范式**: 所有 case 查 CLS 从 2020 年初到全队最早 cutoff (~2024 中,
  GLM-4-9B) 之间的同一段。
- **(a) B 立场下解释**: 这段语料里 (target, family) 的 reference rows
  数 = 全队所有 model 都至少见过的 outcome-bearing exposure 下限。
- **优**:
  - case-date 独立 (Recurrence 是 case-level value,不是 case×model);
    R-4a / R-0 框架要求 case-level factor 不依赖 model,这一致。
  - 0-recurrence 对 post-cutoff control 也合法(BL2 cases 也可算
    recurrence,placebo check 可做)。
  - 实现简单: 一次性 build,所有 case 共享。
- **劣**:
  - 对晚 cutoff model (Claude 4.6 / GPT-5 / GPT-4.1, ~2025 H2) **保守
    截断** —— 这些 model 实际见过 2024 中 → 2025 H2 之间的更多
    reference rows,固定窗口把它们截掉了。这压低了 effect size,使 β3
    偏 conservative。
  - 没法区分 "全队都见过" 和 "只有晚 cutoff 见过" 的 reference rows。
    但 β3 是与 Cutoff Exposure 的交互项,case-level Recurrence 进入交
    互后,Cutoff Exposure 那一侧承担 model-cutoff 异质性,Recurrence 这
    一侧不需要也承担它。

### 候选 2 — 案例相对滚动窗口 `[T − X 天, T)`

- **范式**: 每个 case 查自己发布前 X 天的语料 (X 可选 90 / 365 / 730)。
- **(a) B 立场下解释**: "case 发布前一段时间内 (target, family) 在 CLS
  里的复现强度"。但这是 **case-relative**,不是 model-relative —— X 天
  是 case 日期决定的,不是 model 训练历史决定的。
- **优**:
  - 直觉上贴近 "case 发布前 (target, family) 多热"。
  - 对 trend / 热度类研究问题贴。
- **劣**:
  - **construct error,与 (a) B 立场冲突**: 关联记忆是模型训练期间形成
    的,不取决于 case 发布日。"case 发布前 90 天" 这个窗口对一个 2024
    年中 cutoff 的 model 来说,如果 case 发布于 2025 Q4,窗口里大半已
    经在 cutoff 之后 —— **model 根本没见过那部分 reference rows**,把
    它们当 exposure 计数是 inflation。WS0.5 §5.1 v0.4 的 C-2 论证已经
    给出这个判断,(a) 的 B 立场进一步强化了它。
  - 也违反 R-4a "case-level factor 不依赖 model" 框架(它跟 case 日期
    强耦合,case-level 但不 model-independent)。
  - 0-recurrence 对 post-cutoff control 的合法性论证复杂(post-cutoff
    case 的 T-X 窗口可能跨 cutoff 边界,reference rows 一半 model 见过
    一半没见过)。

### 候选 3 — 每模型 pre-cutoff 滚动窗口 `[corpus_start, model.cutoff)`

- **范式**: 每个 (case, model) 都查 corpus_start 到该 model cutoff 之间
  的语料。Recurrence 从 case-level 变成 case × model factor。
- **(a) B 立场下解释**: 每个 model 见过的 (target, family) outcome-
  bearing exposure 数;最 model-accurate。
- **优**:
  - 完美贴住 (a) B 立场: 每个 model 看到的真实 exposure。
  - 晚 cutoff model 不再被保守截断;effect size 不被压。
- **劣**:
  - **架构层面冲突**: Recurrence 从 case-level factor 变成 case × model
    factor。R-4a 框架明确把 Cutoff Exposure 单独标为 case × model 的
    "principled exception"(proposal §3 flag ⑦);把 Recurrence 也升
    格为 case × model 会增加一个 case × model factor,与 R-4a 框架冲
    突,且使 R-1b 与 R-1c / R-1d 的 case-level 对齐失效(R-1c Salience
    也得 case × model 化才能保持 axis 一致)。
  - **case × model 双向 collinearity 风险**: Recurrence 现在和 Cutoff
    Exposure 都依赖 model cutoff;两者 within case 的相关性会拉高 VIF
    到 §3.3.3 的红线区。
  - **storage / compute 复杂度上升**: 12 个白盒 model + 4 个黑盒 = 16
    × case-level table 行数;build 成本仍可接受但增加 ~16× factor 计
    算工作量。
  - 实际 vs 概念 gain: 真实 vs 固定窗口的 effect-size 差距来自 [2024
    中, 2025 H2] 这段晚 cutoff 多见到的 CLS rows。CLS 总 ~6 年,这段约
    占 1.5 年 = 24%。考虑 mention density 不时间均匀(后期密度高,见
    任务陈述),这段实际占比可能更高(40-50%?)。但这部分 gain 要付
    架构层冲突 + R-4a 框架冲突 + VIF 风险三项代价,**不划算**。

### 候选 4 — 多窗口 grid robustness

- **范式**: 90 天 + 365 天 + 全 pre-cutoff 三档同报。
- **劣**: owner 已明示 "不允许 fence-sit 多窗口 grid 当 robustness"。
  drop。

## 主选 + 主理由(含哲学含义考虑 + 数据约束 sanity-check)

**主选: 候选 1 — 固定窗口 `[corpus_start, earliest_model_cutoff)`。**

主理由 (四条):

1. **(a) B 立场要求 model-visible**: 关联记忆只能在 model 训练时形成。
   固定窗口端点是 earliest cutoff,保证窗口内每条 reference row 全队
   model 都至少 *可能* 见过 —— 这是 outcome-bearing exposure 的合法下
   限。case-relative 候选 2 违反这条最严重(post-cutoff case 把 model
   没见过的 rows 当 exposure 计数);per-model 候选 3 形式上贴合 (a) B
   立场但付出架构冲突代价。
2. **R-4a / R-0 框架要求 case-level Recurrence**: 候选 3 把 Recurrence
   升格为 case × model,违反 "case-level factor 不依赖 model" (R-4a /
   proposal §3 flag ⑦);这条框架约束的设立本身就是为了避免每个 factor
   各做 case × model 化导致 VIF 失控。
3. **哲学含义的实际差异有限**: 固定窗口保守截断的是 [earliest_cutoff,
   latest_cutoff] 这段;Cutoff Exposure × Recurrence 交互项 β3 的设计
   本来就是把 cutoff 异质性塞到 Cutoff Exposure 那一侧。Recurrence 那
   一侧只需要刻画 "case-level 关联记忆的潜在强度"(across model 共享
   的一段),晚 cutoff model 的额外 exposure 通过 Cutoff Exposure 高
   值 + 高 Recurrence 的乘法在 β3 上体现 —— 不需要 Recurrence 自己也
   model-vary。
4. **数据约束 sanity-check**:
   - CLS 从 2020 年初到 earliest_cutoff (~2024 中) = ~4.5 年。这段
     mention density 即使不均匀,对常见 A 股 firm 也充分(主流公司
     mention 数 ≥ 10);稀疏 cases 的 0-recurrence 是 (a) 已锁的合法值,
     不构成问题。
   - 时间不均匀的 inflation 担忧主要落在 "近期热度" 上,而 fixed window
     端点在 earliest cutoff (2024 中),正好把近期热度切到 Cutoff
     Exposure 那一侧;Recurrence 这一侧的时间分布相对 "历史的平均
     density",比 case-relative 更稳。

### 哲学含义补充

固定窗口塞入的 implicit assumption: "**全队 model 至少都见过的那段
CLS 是 outcome-bearing exposure 的下限,作为 Recurrence 的代理 sufficient**"。
这是一个 lower-bound 立场。它不是 "model 见过的全部 exposure",而是
"全队都见过的 baseline exposure"。Paper 措辞要这样写,不能说 "实际见
过的 exposure"。

per-model 滚动窗口塞入的是 "**Recurrence 必须 model-vary 才有效**" 的
立场;这种立场暗示 case-level Recurrence 是 inadequate construct。但我们
的 estimand (β3 = Cutoff × Recurrence) 设计已经把 model 异质性放在
Cutoff Exposure 那一侧,Recurrence 不必再 model-vary。

case-relative 窗口塞入的是 "case 发布时 (target, family) 多热 → 模型
更容易记得" 的立场,但这把 "case 发布时" 当成 anchor 是 ex-post 视角
(case 还没发生时,model 已经训完了)。

## 非主选去向

- **候选 2 (case-relative)**: **drop**。construct error,与 (a) B 立场
  和 R-4a 框架双重冲突。任何 condition 都不该激活。
- **候选 3 (per-model)**: **drop**。架构层冲突 + 收益不抵代价。
  - **可以保留作为 paper appendix 的 sensitivity** *仅当* owner 后期发
    现晚 cutoff models 的 β3 显著低于早 cutoff models 且这种差异不能
    被 Cutoff Exposure × Recurrence 交互捕获 —— 这是一个 R-4b /
    pilot-post analysis condition,不是 R-1b 现在要 commit 的 robustness。
    **R-1b 这里不预留 slot;R-4b / R-1e 拿到 pilot 数据后看到信号再决
    定是否单独 run**。
- **候选 4 (多窗口 grid)**: **drop**。owner 已禁 fence-sit。

---

# 段 (h) 阶段 2 reviewer 链 verdict

每条 verdict 锚定: (a) B 立场 / (b) 主选: (target × super_type, fixed
window from L2-subject-tradable rows) / (c) 主选: 固定窗口 / R-4a 8 条
/ R-0 容器(4 层 / entity-first / non-tradable 客体保留 / `log1p(0)=0`
合法 / no-dedup 合法)。

## C-2 verdict

**C-2 历史**: v0.3 round-1 加 `recurrence_count_visible_to_model`(model-
cutoff-censored sensitivity);v0.4 进一步用 fixed window `[corpus_start,
earliest_model_cutoff)` 替代 per-case window `[T-24mo, T)` —— 整个 C-2
sensitivity 字段被 dissolve(window 本身就 model-visible by construction)。

**Verdict: 保留。**

主理由: C-2 的最终形态(fixed window)与 (c) 主选完全一致,与 (a) B 立场
("关联记忆要求 model 见过") 一致,与 R-4a "case-level factor 不依赖
model" 框架一致。reviewer-pushed 的中间形态(censored sensitivity)在
v0.4 被 dissolve 掉,**最终形态简化了**,这是 reviewer 推得对 + owner
进一步简化的标准良性 ratchet。

## C-3 verdict

**C-3 历史**: v0.3 引入 within-super_type percentile + median split binary
+ `absolute_high_recurrence` parallel field + 4-way interpretation rules;
v0.4 全 dissolve,只留 continuous `log1p_recurrence_count`,within-super_type
bin 降为 non-confirmatory sampling 用。

**Verdict: 保留 v0.4 form (continuous log1p); 撤销中间 percentile / binary
machinery。**

主理由: continuous `log1p(recurrence_count)` 与 (a) B 立场 (magnitude is
the construct: "见过几次") 一致;与 R-0 §4.5.D `log1p(0)=0` 合法值锁定
一致;与 R-4a §4 "per-estimand 混合模型分别建" 一致 —— super_type 在
fixed-effect 里作 covariate 已经控制 family base-rate confound,不需要
预先 percentile 化。reviewer-pushed 的 percentile / binary 是统计术语镇压
(memory `feedback_review_complexity`)的典型 —— 给了一个本不需要的 framing
machinery。**v0.4 dissolve 是 owner 主导的反 ratchet,保留 v0.4 form。**

## C-4 verdict

**C-4 历史**: v0.3 加 dedup sensitivity 字段(`recurrence_count_clustered`,
`recurrence_count_first_per_day`, `duplicate_ratio`);v0.4 经
`scripts/cls_dup_probe.py` 实证(全 1.2M items, 0.48% 重复)后 drop 所有
dedup sensitivity 字段,只留 no-dedup count。

**Verdict: 保留 v0.4 form (no-dedup, drop sensitivity)。**

主理由: 与 R-0 §4.5.D "no-dedup exposure 合法" 锁定一致;与 (a) B 立场
("每次 outcome-bearing exposure 都强化关联记忆,intra-day 重复也是 exposure")
一致;实证 0.48% 重复率证明 sensitivity 字段无 specific failure mode 可
对应(memory `feedback_minimal_design`)。**reviewer-pushed C-4 的 dedup
machinery 是 hypothetical-failure-driven 过度结构;owner 用 probe 数据反
ratchet 是教科书级别的"先 probe 再 commit"。保留 v0.4。**

## E-5 verdict

**E-5 历史**: v0.3 加 post-cutoff 控制 cases 的 `null + missing_reason=
"not_applicable_post_cutoff"` 字段;v0.4 经 C-2 window 改 fixed 后 dissolve
(fixed window 对 post-cutoff control 也合法,直接 compute, 不需要 null
marking)。

**Verdict: 保留 v0.4 dissolution(`null` 字段 drop)。**

主理由: (c) 主选 fixed window 已锁,直接复用 v0.4 的论证 —— post-cutoff
case 的 recurrence 也合法计算,是 placebo check 输入(BL2 上 β3 应近 0,
TOST/SESOI=0.15 等价检验通过)。**E-5 的 null 字段在 fixed window 框架下
是 dead machinery, drop 正确。** v0.3 的 null 字段是 case-relative window
范式下被迫加的占位,reviewer 推得对(under that frame),但 frame 本身
改了,占位也就 dissolve 了。保留 v0.4。

## E-6 verdict

**E-6 历史**: v0.3 加 R4 LLM 歧义判定 cache 的 `response_id` lookup key +
versioned cache key + override rules;v0.4 在 entity disambig methods review
后改 deterministic master-data pipeline(AKShare 主数据 + 规则风险打分 +
type/effective-date check + precision-first disambig),LLM 退出 main path,
v0.3 的 cache key / override 全部 dissolve。

**Verdict: 保留 v0.4 form (deterministic master-data); 撤销 v0.3 LLM-in-path 设计。**

主理由: deterministic master-data 路径与 R-0 §4.5.B 锁的 "entity match
first (pre-LLM cost)" 一致;precision-first disambig 与 (a) B 立场一致
(confirmatory factor 偏向 false-negative 比 false-positive 更安全 —— 漏
计 outcome-bearing exposure 让 β3 偏 conservative,误计虚增 β3 不可接受);
LLM 退出 main path 进入 §5.3 smoke 是 minimal-design 的标准应用(LLM 在
有特定 failure mode 时才进 main path)。**reviewer-pushed E-6 v0.3 是
ratchet 典型 —— 把一个本可 deterministic 的步骤升级到 LLM-with-cache-and-
versioning,owner / Codex 联合反 ratchet 到 deterministic + smoke audit
是好。保留 v0.4。**

## E-7 verdict

**E-7 历史**: v0.3 加 full-frame ranks + tie rule + bin-stability report
+ LOO bootstrap 机制;v0.4 经 C-3 改 continuous 后 dissolve (continuous
变量没有 bin → 没有 bin-flip → 不需要 stability report)。

**Verdict: 保留 v0.4 dissolution。**

主理由: 与 (b) 主选 (continuous log1p) 一致 —— continuous factor 进
fixed-effect 不存在 bin-flip 风险;与 R-4a §1 "无 family-wise multiplicity
correction" 框架一致(bin stability 是 multi-testing 焦虑的 reviewer 表
现,R-4a 已把这条焦虑解掉)。**E-7 是 reviewer pile-on 典型 —— 在 binary
percentile 框架下确实需要 bin stability,但那个框架本身是过度结构;dissolve
binary → dissolve stability machinery,正确链式简化。保留 v0.4。**

## walkthrough §A.1 verdict

**§A.1 历史**: 2026-05-23 walk-through user 提出 4-layer corpus stratification
(full CLS / entity-bearing articles / subject articles / predictable articles);
R-0 Codex Pass A 收到后调整为 3 工作层 + 1 源层 (S0 / L1 mention / L2
subject / L3 views),把 "predictable articles" 降为 L3 view 而不是新层。
R-0 closure 锁这个版本。

**Verdict: 保留 R-0 final form (3 工作层 + S0);A.1 的 4 层提议本身已
被 R-0 修正吸收。**

主理由: R-0 的修正是对的 —— `tradable_at_event` 是 entity-time 属性,做
成层会偏向某一种 construct(明确把 mention vs subject 的选择权剥夺);做
成 L3 view (view over L1 或 L2 都可) 给 (a) 的 4 候选都留空间。**A.1 的
4 层是用户直觉对的方向(layer 化),R-0 修正的是 layer 与 view 的边界 —
A.1 把 "predictable" 升到层,R-0 降到 view。这是 reviewer 推得对方向 +
agent 调整边界的良性 ratchet,不是 pile-on。** (a) B 立场 (L2 subject +
tradable) 已经锁,正是用 L3 view over L2 实现的,与 R-0 final form 一致。

## walkthrough §A.2 verdict

**§A.2 历史**: user 提出 pipeline reorder (entity match first → subject
ID → topic-classify only Layer 3) + subject-only counting (Recurrence 从
mention density 改 subject density)。R-0 Codex Pass A 接受 entity-first
reorder,**拒绝** subject-only topic-classify (会让 mention-level event-
family construct 消失),**不替 R-1b 选** subject vs mention counting。

**Verdict (entity-first reorder): 保留。**

**Verdict (subject-only counting): R-0 拒绝在架构层锁是对的;R-1b (a) 段
最终选 L2 subject + tradable_at_event 即 subject-flavored construct,所以
在 factor 层面 implicitly 与 A.2 收敛。**

主理由:
- entity-first reorder 与 (b) / (c) 主选都一致 —— 我推的 grouping 是
  firm × super_type,subject counting (L2-tradable reference rows) 需要
  entity match 已经做完。entity-first 是 R-0 锁的硬约束,(b)/(c) 实现
  自然依赖它。
- subject-only counting 在 R-0 层 拒绝是对的(那时 R-1b 还没开),但 R-1b
  (a) 现在已经独立选了 L2 subject + tradable,所以 final state 与 A.2
  user 直觉收敛 —— 不是 A.2 推错,而是 R-0 / R-1b 的职责分层把 A.2 的
  construct 决定留给 R-1b 而不是在架构层先锁。保留两段 verdict 一致。

**没有 reviewer pile-on; A.2 是 user 主导的 cross-boundary 提议,被
R-0 正确剥分到对应 session (架构归 R-0,construct 归 R-1b)。**

## R-0 §3 pool 候选 verdict

**§3 历史**: Codex Pass A 提出 Pool A-I 候选(L2 subject / L2 subject +
tradable / L1 mention / L1 mention + tradable / outcome-verifiable / mixed
panel / salience-stratified / entity-balanced / cutoff-balanced)。R-0
closure 把 Pool B (L2 + tradable) 锁为 sole base; G/H/I 为 optional
distribution strategies; D/E/F 为 architecture extensions reserved。
walk-through 中 owner 一度质疑 "tradable mention" (Pool D) 的哲学合
法性后又恢复为候选 construct。

**Verdict: 保留 R-0 final form; Pool D 的 R-1b 触发判断: 不触发。**

主理由:
- Pool B (L2 + tradable) sole base 与 (a) 主选 L2 subject + tradable_at_event
  reference 完全一致;R-0 锁 Pool B 是对的。
- Pool G (salience/recurrence stratified) 优先级中等,R-5 session 决定;
  R-1b 不强制激活。
- Pool D (mention + tradable / L1 view): R-1b (a) 已选 L2 subject + tradable,
  **不触发 Pool D 扩展**;Pool D 保持 dormant。owner 在 walk-through 中
  对 Pool D 哲学合法性的质疑是合理的 —— "mention + tradable" 的 construct
  落点不清晰 (tradable filter 引入 model 不知道的 ex-post 口径,且
  mention construct 与 outcome-leakage proxy 不贴),(a) 的 B 立场最终
  选 L2 subject 已经把这个问题绕过。**R-0 把 Pool D 列为候选不算 pile-on
  (R-0 不替 R-1b 选,正确职责分);R-1b 在 (a) 阶段把 Pool D drop 是对
  的。**
- Pool E / F: R-2 / R-6 territory,R-1b 不动。

**R-0 §3 整体: 是 component-level 候选展开,不是 reviewer pile-on; R-1b
基于 (a) B 立场过滤后,只激活 Pool B。最终 lean。**

## Ratchet 论双源验证 summary

**Reviewer 推得对应当保留**:

- **C-2 fixed window** (v0.4 final form): reviewer 在 round-1 推 censored
  sensitivity,owner v0.4 一步到位 dissolve 成 fixed window —— reviewer
  方向对,owner 简化得更彻底。
- **E-6 deterministic master-data pipeline** (v0.4 final form): Codex
  methods review (E-6 论证) 推得对,把 v0.3 的 LLM-cache-with-versioning
  反 ratchet 到 deterministic + smoke audit。
- **R-0 entity-first pipeline** (walkthrough §A.2 reorder + Codex Pass A
  确认): user + Codex 双源一致;比 §5.2 v0.4 prose 的 full-CLS topic-
  first 显著 cleaner + cheaper。
- **R-0 4 层架构** (walkthrough §A.1 + Codex Pass A 修正): user 直觉提
  layer 化,Codex 把 layer vs view 边界调对(non-tradable 客体保留;
  predictable 不升层)。

**Reviewer pile-on 的过度结构应当 revert (已 revert 在 v0.4)**:

- **C-3 percentile / binary / 4-way interpretation rules / `absolute_
  high_recurrence` parallel field**: 一个本可 continuous 的 factor 被加
  上 percentile + binary + bin-stability 全套 machinery,典型统计术语镇
  压(memory `feedback_review_complexity`)。v0.4 dissolve 到 continuous
  正确。
- **C-4 dedup sensitivity 字段**: hypothetical-failure-driven 过度结构,
  无 specific failure mode 对应;owner probe 数据反 ratchet 教科书级别。
- **E-5 `null + missing_reason="not_applicable_post_cutoff"` 字段**: case-
  relative window 范式下被迫加的占位;window 改 fixed 后 dissolve。
- **E-7 bin-stability report + LOO bootstrap**: percentile/binary 范式下
  的衍生 machinery;binary dissolve 后随之 dissolve。

**Reviewer 在职责分层下不算 pile-on,但需要 R-1b 把它们的 construct 选项
落地 (已在 (a)/(b)/(c) 落地)**:

- **R-0 Pool A-I 全候选展开**: R-0 不选 winner 是对的;R-1b 现在在 (a)
  选 L2-subject-tradable,(b) 选 firm × super_type,(c) 选 fixed window
  ——只激活 Pool B,Pool D 不触发,Pool G/H/I 留 R-5。
- **walkthrough §A.2 subject-only counting**: R-0 不替 R-1b 选是对的;
  R-1b (a) 自己选 subject (L2 + tradable),与 A.2 直觉收敛。

**双源验证结论**: v0.4 + R-0 final form 是干净的 minimal-design;
v0.2-v0.3 之间确实存在 reviewer pile-on (C-3 percentile 全套 / E-7
bin-stability / E-5 null marker / E-6 LLM-cache machinery / C-4 dedup
sensitivity),owner 与 Codex 在 v0.4 / R-0 联合反 ratchet 全部 dissolve。
(b)/(c) 主选锁后,无需进一步 revert,也无需新增 robustness machinery
(只保留 1 个 conditional robustness + standing discriminant diagnostic)。

---

# Verdict summary

- **段 (b) Family granularity**: 主键轴 **单标的(同一只股票)**,事件
  折叠轴 **5 大事件超类 (Scheme A)**,组合主选 `(target, event_super_
  type)`;1 个 condition-pinned robustness (super_type within-bin
  variance 异常时拆 raw event_type),1 个 standing discriminant
  diagnostic (与 R-1c Salience 的 VIF / correlation);其他全 drop。
- **段 (c) Lookup window**: 主选 **固定窗口 `[corpus_start, earliest_
  model_cutoff)`**;case-relative / per-model / 多窗口 grid 全 drop
  (与 (a) B 立场 + R-4a case-level factor 框架 + R-0 实现简洁性三重
  一致)。
- **段 (h) reviewer 链 verdict**: C-2 / C-3 / C-4 / E-5 / E-6 / E-7 全
  保留 v0.4 final form (撤销 v0.2-v0.3 的 reviewer-pushed 过度结构);
  walkthrough §A.1 / §A.2 + R-0 §3 Pool 候选全保留 R-0 final form;
  Pool D 在 R-1b (a) 选 L2-subject-tradable 后**不触发扩展**, 保持
  dormant。
