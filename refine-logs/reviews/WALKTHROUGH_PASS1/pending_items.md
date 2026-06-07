# Pass 1 走查 — 偏差 / 待处理项清单(running)

> Pass 1 的交付物。每轮更新。Pass 1 结束时由用户最终确认。
> 第 4 章后用户重新定位:Pass 1 产出 = 完整设计图 + 圈定的重开块 +
> 锚定不动的部分。

## 已关闭 flag

- **flag ①** — 无成文研究问题文档。解决:Pass 1 结束组装中文
  `docs/RESEARCH_PROPOSAL.md`(用户批准的中文特例)。
- **flag ②** — memory `thales_connection.md` 把 decomposition 当核心贡献,
  已过时 → 降为 exploratory。Pass 1 结束更新 memory。
- **flag ③** — "文本内部因素"为宽泛表述。关闭;proposal 动机段写明 20 系数
  预算下的四选取舍。

## 核心决策(第 4 章后,用户重新定位)

- **顺序:实现设计在上游,选择在下游。** 不落地到具体算法,判断不了一个
  因子/扰动有没有效。先定每个的实现方法,再定选哪几个。
- **clean-room-first 协议**(后续重开工作的强制方法):重新分析每个待定点
  时,agent 先在白板状态下(不读 WS0.5 memo 推理、不读 Codex review 文件)
  独立分析、得出结论;然后再读当初 reviewer 的讨论与推荐理由,做对照。
  动机:用户曾被 reviewer 的统计术语镇住、默认采纳;白板参照系是解药。
  关联 memory `feedback_review_complexity`、`feedback_decision_text_drift`。
- 被割舍因子(事件类型/权威度等)→ exploratory 因子;标签 WS0.5 管线本就
  标注。英文对等数据集 = stretch goal。
- **pilot post-cutoff 桶 = 700**(非 350)→ pilot 总量 80 pre + 700 post =
  780。直接上 96%-power 版本;no-memo 允许范围内。代价:运行时长/API ~1.8×,
  USD 300 cap 需上调。post-cutoff=700 与重开不相干、现在定无妨;80 pre-cutoff
  仍临时,随操作化层重开重算。
- cutoff-asserted heads-up 关闭:用户判断 cutoff 必然要测、钉不死在某天
  (覆盖密度渐变),与设计选连续 case×model 因子 + Path E horizon 探针一致。
- split-tier heads-up 关闭:预料之中。
- **implementation-first 的三个理由**:落地暴露 ①有效性 ②设计盲点
  ③**可行性**(指标完美但 CLS/预算/算力/主数据撑不起)。
- **并行轨道**:WS0.5 的 design-agnostic pipeline/tuning(auto-tune 机器、
  replay cache、预算计量、AKShare 别名表、T1/T2 prompt 调 V4 Pro、CLS 上跑
  topic 分类)与重开并行 —— 产出可行性证据喂给设计重审。边界:并行 = 建
  能力 + 收可行性数据;**不**提交 factor_schema.yaml 指标定义、**不**签
  WS0.5 memo。"建管道"可以,"锁定义"要等;线的精确位置排重开计划时再切。

## 锚定不动(已确认 sound,不重开)

- 研究问题(第 1 章)
- 四层框架 Factor/Perturbation/Operator/Estimand(第 2 章)
- 两阶段预注册的结构容器(流程外壳)

## 重开范围 —— 严格限定"框架与实现之间的操作化层"

- **R-0 Corpus Architecture(2026-05-23 PM late 衍生)** —— R-1b kickoff
  走查时,用户指出原 6 个决策点里的「4-layer corpus stratification」
  「pipeline reorder」「benchmark 抽样从哪层抽」其实是**对所有下游 factor
  / R-5 都奏效的上层架构决策**,应该先于任一 factor session 敲定。提升为
  独立 R-0 项,scope 严限:**只 expose 架构空间,不替 factor 拍 construct /
  时间窗口,也不替 R-5 拍 sampling**(三者均由下游各自 session 决定;R-0
  确保架构足够 expressively 容纳所有合理候选)。kickoff
  `.scratch/session_kickoff_r0_corpus_arch.md`。是 R-1b/c/R-5 + R-2 数据
  依赖的共同上游。
  - **R-0 closed 2026-05-23 PM late** → canonical lock-in =
    `refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/R0_DECISIONS.md`
    (time-static 决策清单);audit trail(已归档)→
    `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/`。
  - **下游解锁**:R-1b(用户点名重点,2026-05-24 ✔ closed)/ R-1c / R-5 /
    B-2 `run_inputs.per_task` schema finalize。R-2 仍部分卡 R-6(C_FO 机制);
    R-3 / R-4b 仍卡上游。
  - **方法论 highlights**(R-0 元层观察,只在此处记 —— DECISIONS.md 是
    time-static 不放历史叙事):
    - **arch-vs-session 锁原则诞生**(memory `feedback_arch_vs_session_scope`
      2026-05-23 写):本 session 把 perturbation-specific eligibility flag
      (outcome_verifiable / text_reversibility / entity_span_quality /
      temporal_anchor_recoverability 等)从架构层剥离回 R-2 / R-6;架构层
      只锁 universal admissibility + 两个 hook(pre-sampling subpool
      admissibility + post-sampling per-case eligibility)。这条原则之后
      generalizes 到所有 framework-level session(R-4a 同源应用)。
    - **Codex Pass A vs user walkthrough 双源收敛**:Codex 阶段 1
      独立得出与用户 walkthrough §A.1/§A.2 高度接近的方案(4 层 +
      entity-first)。Codex 比 user walkthrough 把每个 commitment 都退
      一步留给下游(Layer 4 降为 view、tradable 不硬筛、construct 不锁);
      用户走查时进一步收紧(non-tradable rows 客体 vs 主体区分;tradable
      check 仅在 L2;perturbation-specific eligibility 回 R-2/R-6;
      sampling 分布不强制)。两端独立推 + 用户 push back 的
      clean-room-first 协议本轮再次坐实有效。
- **R-1b Historical Family Recurrence(R-0 解锁后第一个 closed factor session)** ——
  在 R-0 锁定的 4 层容器内选 construct + family 粒度 + lookup window。
  - **R-1b closed 2026-05-24** → canonical lock-in = `refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/R1b_DECISIONS.md`(time-static 决策清单);audit trail(已归档)→ `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/`。
  - **下游解锁**:R-1c Target Salience / R-1e 因子最终选择 / R-5 Pool G 分层依据 / B-2 `historical_family_recurrence` schema 字段。R-1a / R-1d / R-2 / R-6 与 R-1b 正交不变;R-3 / R-4b 仍卡上游。
  - **方法论 highlights**(R-1b 元层观察,只在此处记 —— DECISIONS.md 是 time-static 不放历史叙事):
    - **stress-test 改判**:Codex Pass A 主白板初稿选 A 立场(pure text exposure proxy);owner 走查时 surface "Recurrence 是 outcome-leakage proxy 还是 pure exposure proxy" 的 meta-question(R-1b kickoff prompt 没显式 framing),Codex 二轮在 outcome-leakage framing 下推翻自己,改 B 立场。
    - **dual-model blind 抉择**:Claude blind second opinion 选 A 立场,基于 5-estimand 覆盖矩阵(A 5/5 vs B 2/5);owner 反驳 Carlini anchor 论证(Carlini 测 verbatim text recall,我们测 outcome-association memorization,Carlini 是 analogy 不是 direct anchor)→ override Claude 采纳 Codex B 立场。
    - **(b)(c)(h) Claude blind second opinion 全部与 Codex 收敛** → 双源验证 lock-in。
    - **ratchet 论双源验证坐实**(R-1b 维度):保留 4 条 reviewer 推得对(C-2 fixed window / E-6 deterministic / R-0 entity-first / R-0 4 层);撤销 5 条 reviewer pile-on(C-3 percentile / C-4 dedup sensitivity / E-5 null marker / E-7 bin stability / E-6 v0.3 LLM-cache)。v0.4 + R-0 final form 已是干净 minimal-design。
    - **documentation pattern 新立项目惯例**(见 memory `feedback_doc_for_llm_context` 2026-05-24 update):每个 R-X 决策 session 产 audit-trail + 一份 < 200 行 time-static `R{X}_DECISIONS.md`(canonical for downstream agents);其它文档只 reference DECISIONS.md, 不重复内容(single source of truth)。R-1b 是第一个按此 pattern 产出的 session。
- **R-1c Target Salience(R-1b 解锁后第二个 closed factor session)** ——
  在 R-0 4 层容器 + R-1b construct framework 下选 Salience 的 framing / construct / family / window / tradable filter / discriminant fallback / robustness。
  - **R-1c closed 2026-05-25** → canonical lock-in = `refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/R1c_DECISIONS.md`(time-static 决策清单);audit trail(已归档)→ `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/`。
  - **下游解锁**:R-1e 因子最终选择(R-1c Option C 显式把降级路径交给 R-1e)/ R-5 Pool G 分层依据可切到 R-1c metric / B-2 `target_salience` schema 字段 / R-4b 追加 R-1b retrospective tail-leverage check。R-1a / R-1d / R-2 / R-6 与 R-1c 正交不变;R-3 仍卡上游。
  - **方法论 highlights**(R-1c 元层观察,只在此处记 —— DECISIONS.md 是 time-static 不放历史叙事):
    - **双白板并行(Codex + Claude sub-agent 用同一 prompt)**:首次在 R-X session 同时跑两个独立 agent(此前 R-0 / R-1b 是 Codex 主 + Claude blind second opinion 顺序模式)。双源在 8 决策点上 **6/8 收敛**(framing C / L1 mention / target only / log1p(count) / 共享 fixed window / 不加 tradable),验证了 R-1c upstream lock(R-0 / R-4a / R-1b)的清晰度。
    - **真分歧定位精准**:双源在 (7) fallback metric 和 (8) robustness slot 上分歧 —— Codex 选 complement-super_type fallback + tail-leverage pre-commit;Claude 选残差化 fallback + L1-vs-L2 conditional。owner 走查时拒绝两边的 metric fallback 提议(Codex 因 family 维度前后不一致 + B-2 扩 topic-classify;Claude 因仍是 metric-level fallback 越界 R-1c session scope),引入第三选项 **Option C(R-1e 降级,无 metric fallback)**。
    - **owner-driven framework move(Option C)**:由 owner 在走查中提议 "fallback 能不能是看别的因子",从 abstract 部分推出 R-1e level fallback 合法(R-4a §4 允许因子数与身份由 R-1e 决定),具体 surface 为 "R-1c session 不锁 metric fallback,discriminant trigger 时 R-1e 降级 R-1c slot"。Codex 在白板末尾隐含同意这条 ultimate backstop("如果 fallback 仍超阈值,R-1e 应把两者视作经验冗余,选择或降级其中一个"),Option C 等于把它提前到第一档。这是 **clean-room-first 不仅 surface 已被 reviewer 认可的方向,owner 走查还能 ratchet 出双源未 surface 的 framework move**。
    - **ratchet 论双源验证再坐实**(R-1c 维度):双源都拒绝 WS0.5 §3.3.2 现状 prototype 的 ordinal salience / market-cap-based 框架(Codex 旧提案)+ Baidu Baike fallback + complement-family / non-CLS proxy fallback;双源都采 framing C + L1 mention + log1p(count)。WS0.5 §3.3.2 v0.4 现状的 C-1 / C-2 / C-3 / S-6 reversal 方向 reviewer "推得对",但其 fallback 候选(complement / Baidu Baike)仍是 reviewer pile-on,被 R-1c Option C 一并撤销。
    - **focal_article_policy 在 R-1c 与 R-1b 走相反方向**:R-1b 排除同 article_id(framing 是历史复现,自身不能算 "自己复现自己");R-1c 不排除(framing C 是 model 预训练曝光,case 自身文章在窗口内时也是 exposure)。这是 **framing 决定 boundary 细节** 的实例,不是不一致。
    - **R-1 系列 robust 风格分家(Framework D)**:R-1c 选 1 个 pre-commit tail-leverage appendix,不 mirror R-1b 的 0 pre-commit + 1 conditional 风格。R-1c L1 mention + target only 比 R-1b L2 subject + tradable + target × super_type 尾部更 acute,distribution robustness 更必要。R-4b 追加 R-1b retrospective tail-leverage(不算 R-1b 重开,算 R-4b implementation choice)以维持 paper §robustness 段一致性。
- **R-1a Cutoff Exposure(R-1b/R-1c 解锁后第三个 closed factor session)** ——
  全 fleet 唯一 case×model 因子,承载主效应 β1。
  - **R-1a closed 2026-05-27(机制锁;cutoff 中心值 provisional 待探针验证)** → canonical lock-in = `refine-logs/reviews/REOPEN_R1_R6/R1a_cutoff_exposure/R1a_DECISIONS.md`(time-static);audit trail(已归档)→ `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1a_cutoff_exposure/`(含单 Codex 白板 + GPT deep research 16 模型 cutoff 可信度);验证探针协议 `refine-logs/reviews/REOPEN_R1_R6/R1a_cutoff_exposure/cutoff_probe_protocol_codex.md`(黑白盒通用)仍 live。
  - **锁定**:event date = published_at(日精度)/ cutoff = fleet yaml(归当月末,与 R-1b/c min(cutoff) 同源,Llama-3 2023-03 不变)/ metric = **tanh((published−cutoff signed 连续月)/w),w=2 月主 + 1/3/6 稳健性**/ sign = pre-cutoff 正 / case×model cross join 存 `delta_days`+`cutoff_exposure` / 二元 pre/post 按符号现切作 BL2 负对照 / in-text event date 子集(确定性抽取)作唯一 robustness / Path-E + 黑白盒行为探针作**验证轨**(不喂指标、报警触发人工复核)。
  - **下游解锁**:R-1e(Cutoff Exposure 作 β1 载体,几乎必进 primary)/ R-4b(case×model 进混合模型 + cutoff 误分类模拟)/ R-5 Pool I(cutoff-balanced)。R-1d 与 R-1a 正交不变;探针建+跑排进 fleet 部署。
  - **方法论 highlights**(只在此处记 —— DECISIONS.md time-static 无 history):
    - **单 Codex 白板足矣**:决策量小,5/6 决策点 Codex 与 CC 独立读直接收敛(杀鸡不用牛刀;R-1c 双白板是因 8 决策点有真分歧)。唯一分歧(连续化用 log vs tanh)被 owner 更优方案取代。
    - **owner-driven 设计改进三连**(均比 agent 初版更对):① **tanh 替 log** —— owner 的 LLM 语料时间性模型(历史=当代记得一样好、未来都一样)要求 S 曲线两端饱和,log 远端不压平不符;② **厘清"中心 vs 宽度"** —— owner 质疑 per-model w,推出"中心 per-model 合法(cutoff 日期是模型事实),宽度全局,中心不确定走灵敏度不进 w";③ **黑白盒通用探针** —— owner 提把第 5 条 Path-E 验证从白盒扩到黑白盒通用 + 报警 gate。
    - **deep research 暴露 manifest 不可靠** → "中心值 provisional + 验证轨":Qwen3 2025-01 无任何来源(实 ~2024-10)、DeepSeek 2026-04 是发布日代理(实 ~2025-05,差近一年)、GLM-4 弱证据、Claude 官方三处矛盾(May/Aug 2025/Jan 2026)。knowledge vs training cutoff 区分坐实"中心偏保守 → 泄露估计偏低不偏高"口径。
    - **clean-room-first 再坐实**:Codex 白板独立 + CC 独立读 5/6 收敛验证 upstream lock(R-0/R-4a/R-1b)清晰;owner 走查 ratchet 出三个 agent 未 surface 的设计改进(tanh / 中心-宽度分离 / 通用探针)。
- **R-1 因子(原条目)**:4 个 confirmatory 因子,每个的实现方法 → 然后 4 个的选择。
  - Cutoff Exposure(R-1a):**closed 2026-05-27,见上**。
  - Historical Family Recurrence(R-1b):**closed 2026-05-24,见上**。
  - Target Salience(R-1c):**closed 2026-05-25,见上**。
  - Template Rigidity:**R-1d closed 2026-06-02(定义锁 + 进 R-1e 候选池;
    操作化参数 open,pilot 前须过用户审计闸门)** → canonical lock-in =
    `refine-logs/reviews/REOPEN_R1_R6/R1d_template_rigidity/R1d_DECISIONS.md`。
    定义 = CLS 语料高频 n-gram 覆盖率(文章多大比例由模板骨架组成);
    操作化 = jieba 分词 + 语料级 DF 查表 + Top-K% 聚合(参数待 empirical
    testing + 用户审计);参考语料 = L1 去重文章集。R-4 反馈:无记忆基线
    闸门不适合因子准入(supersedes 构念效度框架中的 F_template 闸门)。
    方法论:零 spec 从对话中设计;用户贡献两条关键洞察(n-gram 频率 =
    骨架操作化;泛化替代通道替换失效的槽位替代通道)。
  - **因子候选池 candidate-pool review(R-1g…R-1x):closed 2026-06-05** —— R-1a/b/c/d/f
    已锁机制之外的全部候选因子快速过完,每个定候选池准入结局(进候选池 / DROP)。
    **汇总索引(单一真相)= `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/four_layer_candidate_pools.md` §1**;
    canonical 逐因子决策 = 各 `REOPEN_R1_R6/R1{g…x}_*/R1*_DECISIONS.md`。verdict 不在此处复述
    (避免多副本漂移)。下游解锁:**R-1e** 在 pilot 后从候选池选 / 降级。
- **R-2 扰动**:反事实扰动家族各自的实现构思 → 保留几个 / 哪几个进
  confirmatory。用户点名要重审 C_NoOp。**[R-6 ✔ 2026-06-06] C_FO 已删**(就地换结果值
  与 C_SR 实操重合 + 很多电报无可改结果、适用窄;见
  `refine-logs/reviews/REOPEN_R1_R6/R6_pred_target_cfo/R6_DECISIONS.md`);C_NoOp 等实现(WS3)尚未建。
- **R-3 negative controls**:BL2 / 同-cutoff 证伪对 / C_NoOp_placebo / BL1 /
  BL3 是否充分,展开分析。
- **R-4 pilot 统计整体**(原 β1/β3,已扩大):用户要求**单开一个 session**
  重审 pilot 全套统计 —— 不只 β1/β3,还含等价检验(TOST)、多重比较校正
  (Westfall-Young)、功效模拟、混合模型规格、bootstrap。用户点名这是
  "reviewer 给对的目的 + 甩一堆公式 + 我就同意了"的典型例子。方法:
  clean-room —— agent 先白板从"目的"自推该用什么,再对当初 reviewer 的
  方案。E_CMMD 的"分歧≠记忆"批评也归此处评估(设计现有防御:cutoff-单调性
  + 能力协变量 + 同-cutoff 证伪对 + 人群层面聚合;"够不够"是统计问题)。
  - **2026-05-23 再框定**:R-4 内部其实有**两半**,依赖反着——
    - **R-4a 方法论审计**(confirmatory/exploratory 划分、两阶段预注册、
      multiplicity 校正级别、E_CMMD 防御充分性):**最上游**,无前置依赖,
      其结论约束 R-1e / R-2 / R-3 / R-5 / R-6 的具体选择(family 多大决定
      容纳几个因子 × 几个扰动)。
    - **R-4b 具体数字**(power 计算、n_eff 矩阵、混合模型规格落地):
      仍最下游,需要 R-1e / R-2 / R-3 / R-5 全部落定。
  - 用户决定 **2026-05-23 起新 session 先做 R-4a**;kickoff =
    `.scratch/session_kickoff_r4.md`。R-6 因此暂停,待 R-4a 后再接。
  - **R-4a closed 2026-05-23** → canonical lock-in =
    `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4a_DECISIONS.md`
    (time-static 决策清单 — 8 框架级 lock + E_CMMD 定义 + 负对照具体处理
    + scope boundary + downstream session anchor);audit trail(已归档)→
    `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/`
    (含阶段 1 白板独立分析 + 15 篇 2022-2026 代表作子领域 lit scan 双源证据)。
  - **下游解锁**:R-6 因 R-4a 给的容量接口(加新 estimand = 替换 primary
    格子或开新 design memo)解封,可接 parked C_FO/C_SR 漂移调查
    (`refine-logs/reviews/REOPEN_R1_R6/cfo_csr_history_findings.md`);
    R-4b 仍 open 等 R-1e / R-2 / R-3 / R-5 全部落定。
  - **方法论 highlights**(R-4a 元层观察,只在此处记 —— DECISIONS.md 是
    time-static 不放历史叙事):
    - **ratchet 论双源坐实**:A 的 clean-room(不喂用户 ratchet memory)
      独立推出比 frozen 更简单的方案 + B 的子领域 lit scan 实然显示子领域
      做法比 frozen 更轻 = 双源证据表明 frozen 的复杂度来自 reviewer
      pile-on,正是 memory `feedback_review_complexity` 标定的失效模式。
      clean-room-first 协议解药再次生效。
    - **子领域 lit scan 主导做法**(15 篇 2022-2026 代表作):正式
      multiplicity correction 0/15、正式预注册 0/15、confirmatory/
      exploratory family label 0/15。AntiLeakBench 2025 是当前最强同行
      参照(3-annotator + Gwet's AC1 + accuracy)。
    - **E_CMMD 重命名的具体过程**:claim 层与 memorization 解释解耦 ——
      "跨模型分歧"是 case-level 行为信号,只有与其它 estimand 在同一
      因子方向上**收敛**时才上升到 memorization characterization;
      命名里若带 "memorization" 读者会把分歧本身当已识别记忆,新名 = Cross-Model
      **Cutoff-Monotone** Disagreement。
- **R-5 采样过滤器专题**:用户要求单开讨论。包含 ① 可交易实体 filter
  (已存在 WS0.5 §3.3.1 案例准入预过滤,但在重开区,一并重审)② 新闻长度
  filter(**新增** —— 超长讲话 / 一句话简讯;当前设计无长度过滤)③ 反直觉
  /难预测案例过滤(**新候选**,用户提:利好不及预期等)—— 双刃:让跨模型
  分歧信号更干净,但可能扔掉扰动类最强证据;需真实股价识别 —— R-6 已确立会有一个
  涉及真实收益的记忆指标(2026-06-06),R-5 可复用其收益标签 ④ 可能的其它准入规则。
- **R-6 预测目标 & ground-truth 使用(flag ⑥)— ✔ closed 2026-06-06**
  canonical = `refine-logs/reviews/REOPEN_R1_R6/R6_pred_target_cfo/R6_DECISIONS.md`。一个删除 + 两个待定:
  - **删除 C_FO**:与 C_SR 实操重合 + 很多电报无可改结果、适用窄;目标由反事实扰动 ×
    cutoff 前后 × 显著度切片承接;反事实扰动家族设计归 R-2。
  - **待定 ① P_predict 输出形式**:留算子逐个分析(本次文献倾向方向分类、信心仅诊断、不裸吐数值)。
  - **待定 ② 涉及真实收益的记忆 estimand**:确定会有;形态 / 是否 confirmatory / 识别方式留
    estimand 逐个分析,基于本次文献。

## 后果

- **WS0.5 memo sign-off 等,但 WS0.5 基建并行推进** —— memo 签字锁的是有
  争议的设计,要等重开;design-agnostic 的 pipeline/tuning 基建并行做(见
  "并行轨道")。WS0.5 非白做:是 implementation-first 的一大块现成产出,需
  ① 补 Template Rigidity ② clean-room 复审 ③ 实现清晰后回头确认 4 因子选择。
- pilot N=430 / n_eff 矩阵搭在操作化层上,重开后需重算(非自身重开,是
  下游重算)。

## Codex 连贯性审查发现(2 条,均成立、均为措辞/一致性问题,非重开项)

- **flag ⑦**(Codex finding 1):框架的因子定义自相矛盾。第 2 章(源自
  MEASUREMENT_FRAMEWORK §1)说因子是 case-level、"不提模型即可描述";但
  Cutoff Exposure(最重要的 confirmatory 因子)是 case×model。框架那条
  "因子=不提模型"的判定法有一个未声明的例外(Bloc 0 时间因子)。源文档
  本身就有此张力。修法:写 proposal 时把因子定义写准(case-level 或
  case×model;判定法注明时间因子例外)。minor。
- **Codex finding 2**:section_05 初稿"P_predict 仅输出方向+信心"与
  section_04"方向+置信度+记忆标记+证据引用"矛盾 —— 后者准确(schema §3.4
  输出 target_echo / direction / confidence / explicit_memory_reference /
  evidence)。CC 叙述错误,已修正 section_05。flag ⑥(无收益率)不受影响。

## 文档待修(Pass 1 发现)

- **flag ⑤** ✔ 已修(2026-06-07 phase7 对账):pilot N→780、nine-model→14
  P_predict-eligible / 16 总;phase7 内 N=100 / 9-model 残留已清。
- (Pass 2)MEASUREMENT_FRAMEWORK fleet 数字已修(5 白盒 / 9 模型 → 12 P_logprob /
  14 P_predict)。FROZEN_SHORTLIST §1 Target Salience "ordinal" 与 R-1c 一致,非缺陷。

## code-sync 待办 + 等待决策(2026-06-07 文档清理 / phase7 对账 / 归档轮 后新增)

文档层已对齐 R-1…R-6 现状、过程轨迹已归档。以下是**代码层 vs 设计漂移**与**等决策**项,
均**未动**,各自卡上游。

### 等用户 / 上游决策
- **pilot N**:N=780(80 + 700)已定为 canonical(2026-06-07)。**待确认**:
  `data/pilot/manifests/pilot_430_cases.json` 是否已生成真案例——是 → 需重跑采样器抽
  700 post-cutoff(数据操作);否 → 仅改 config + 同步测试。
- **参考窗右端点 `min(model_cutoff)` 的具体日期 + 计入 min 的子队列** → 待 **R-1e** 裁定
  (R1a/b/c/d_DECISIONS 已把日期留空、标 pending R-1e)。
- **多重比较程序(Westfall-Young 去留)** → 待**下一轮 R-4 走查**(R-4a Lock 1 倾向
  estimation-first:per-estimand 效应量 + 95% CI,不做 NHST 族;phase7 已按此标 pending)。
- **WS0.5 sign-off** 仍**签字搁置** —— 解冻与否是用户的决定。

### code-sync 待办(`planning_power_calculator.py` + estimand 模块,等 roster 定死后一次性重写)
- **pilot N 350/430 → 700/780**:`config/pilot_sampling.yaml`(350/430、manifest_id
  `phase7-pilot-430`)、`scripts/planning_power_calculator.py:229`(默认 350)、
  `tests/r5a/test_planning_power_calculator.py`(350/430 断言)。卡 pilot-N 数据确认。
- **删 E_CMMD 代码**(R-4 D5 已锁砍):`planning_power_calculator.py` 的 `--cmmd-inflation`
  分支 + `test_cmmd_se_case_level_after_fix` + `fleet.py:82,135` 注释。
- **`C_CO` / `E_OR`**(= 改名后的 C_FO/E_FO):`contracts.py:42` enum + `fo_slotable` 等
  schema、perturbations/audit stub、`config/prompts/R5A_OPERATOR_SCHEMA.md`。卡 **R-2**
  (反事实扰动是否用 C_CO 槽)。
- **删 Westfall-Young**:`planning_power_calculator.py:25/73/75/119`。卡多重比较裁定。
- **加真实收益记忆 estimand**(R-6 待定②)→ 卡 **estimand 逐个分析** session;
  **P_predict 输出形式**(E_NoOp `signed_score` 占位)→ 卡 **R-6 待定① 算子逐个分析**。

### 延后归档
- `R5A_TIER_R2_0_IMPL_REVIEW_20260502/` 的 `IMPLEMENTATION_NOTE.md` + `TRIAGE_LOG.md`:
  待 tier-r2-0 PR3a/b 并 + ledger 填完 + NOTE 内 back-ref repoint 后归档(该 session 其余
  评审稿已于 2026-06-07 归档)。

## 排序

1. Pass 1 已完成(7 章走查 + Codex 审 + 本清单)。
2. 结构化重开操作化层 R-1…R-6,全程 clean-room-first 协议。
3. R-1 因子内部:实现设计(尤其 Template Rigidity 从零)先行 → 选择确认在后。
4. 并行:design-agnostic WS0.5 基建 + WS1;基建主题的 Pass-2 漂移审。
5. 重开后:组装中文 docs/RESEARCH_PROPOSAL.md → WS0.5 实现 / WS2 / WS3 / WS4 / WS5。

## Pass 2(WS0.5 memo 决策→文本漂移细审)— 状态:重构

原计划:对 WS0.5 memo v0.4 全文做决策→文本漂移细审(kickoff
`.scratch/walkthrough_pass2_ws0_5_kickoff.md`,~10 主题)。Pass-1 后重构:

- **因子主题(C-1 Target Salience / C-2·C-3 Recurrence / C-4 去重 / C-5
  signal_profile / S-6 discriminant)** —— 落在重开区 R-1。这些 memo 文字
  即将被 clean-room 重写,现在审漂移会白做 → **推迟到重开后的新 memo。**
- **基建主题(E-6 实体管线 / E-8 replay 缓存 / E-9 复现 / E-10 计量
  client)** —— design-agnostic,不重开,在并行轨道。其 memo 文字的漂移审
  **仍 live**,且应在这些基建被并行实现之前做。
- **`.scratch/ws0_5_decision_log.md` 不作废** —— 它的 [USER]/[CC-DEFAULT]/
  [CODEX] 来源标签正好是 R-1 重开的输入:[USER] = 可信的前置决策,
  [CC-DEFAULT]/[CODEX] = clean-room 重开时要重新独立推导的项。
- 漂移这个关切本身不消失,只是从"审 v0.4"挪到"审重开后的新 memo"。
