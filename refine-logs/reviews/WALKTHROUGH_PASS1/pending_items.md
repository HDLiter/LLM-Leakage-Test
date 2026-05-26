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
    (time-static 决策清单);audit trail = 同目录 `whiteboard_analysis.md`
    Codex Pass A 白板 545 行 + 用户 7 段切片走查 deltas。
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
  - **R-1b closed 2026-05-24** → canonical lock-in = `refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/R1b_DECISIONS.md`(time-static 决策清单);audit trail = 同目录 `whiteboard_analysis.md` + `construct_stress_test.md` + `construct_second_opinion_claude.md` + `bch_second_opinion_claude.md`。
  - **下游解锁**:R-1c Target Salience / R-1e 因子最终选择 / R-5 Pool G 分层依据 / B-2 `historical_family_recurrence` schema 字段。R-1a / R-1d / R-2 / R-6 与 R-1b 正交不变;R-3 / R-4b 仍卡上游。
  - **方法论 highlights**(R-1b 元层观察,只在此处记 —— DECISIONS.md 是 time-static 不放历史叙事):
    - **stress-test 改判**:Codex Pass A 主白板初稿选 A 立场(pure text exposure proxy);owner 走查时 surface "Recurrence 是 outcome-leakage proxy 还是 pure exposure proxy" 的 meta-question(R-1b kickoff prompt 没显式 framing),Codex 二轮在 outcome-leakage framing 下推翻自己,改 B 立场。
    - **dual-model blind 抉择**:Claude blind second opinion 选 A 立场,基于 5-estimand 覆盖矩阵(A 5/5 vs B 2/5);owner 反驳 Carlini anchor 论证(Carlini 测 verbatim text recall,我们测 outcome-association memorization,Carlini 是 analogy 不是 direct anchor)→ override Claude 采纳 Codex B 立场。
    - **(b)(c)(h) Claude blind second opinion 全部与 Codex 收敛** → 双源验证 lock-in。
    - **ratchet 论双源验证坐实**(R-1b 维度):保留 4 条 reviewer 推得对(C-2 fixed window / E-6 deterministic / R-0 entity-first / R-0 4 层);撤销 5 条 reviewer pile-on(C-3 percentile / C-4 dedup sensitivity / E-5 null marker / E-7 bin stability / E-6 v0.3 LLM-cache)。v0.4 + R-0 final form 已是干净 minimal-design。
    - **documentation pattern 新立项目惯例**(见 memory `feedback_doc_for_llm_context` 2026-05-24 update):每个 R-X 决策 session 产 audit-trail + 一份 < 200 行 time-static `R{X}_DECISIONS.md`(canonical for downstream agents);其它文档只 reference DECISIONS.md, 不重复内容(single source of truth)。R-1b 是第一个按此 pattern 产出的 session。
- **R-1c Target Salience(R-1b 解锁后第二个 closed factor session)** ——
  在 R-0 4 层容器 + R-1b construct framework 下选 Salience 的 framing / construct / family / window / tradable filter / discriminant fallback / robustness。
  - **R-1c closed 2026-05-25** → canonical lock-in = `refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/R1c_DECISIONS.md`(time-static 决策清单);audit trail = 同目录 `whiteboard_analysis.md`(Codex)+ `whiteboard_analysis_claude.md`(Claude sub-agent)+ `whiteboard_analysis_stage1_codex_draft.md`。
  - **下游解锁**:R-1e 因子最终选择(R-1c Option C 显式把降级路径交给 R-1e)/ R-5 Pool G 分层依据可切到 R-1c metric / B-2 `target_salience` schema 字段 / R-4b 追加 R-1b retrospective tail-leverage check。R-1a / R-1d / R-2 / R-6 与 R-1c 正交不变;R-3 仍卡上游。
  - **方法论 highlights**(R-1c 元层观察,只在此处记 —— DECISIONS.md 是 time-static 不放历史叙事):
    - **双白板并行(Codex + Claude sub-agent 用同一 prompt)**:首次在 R-X session 同时跑两个独立 agent(此前 R-0 / R-1b 是 Codex 主 + Claude blind second opinion 顺序模式)。双源在 8 决策点上 **6/8 收敛**(framing C / L1 mention / target only / log1p(count) / 共享 fixed window / 不加 tradable),验证了 R-1c upstream lock(R-0 / R-4a / R-1b)的清晰度。
    - **真分歧定位精准**:双源在 (7) fallback metric 和 (8) robustness slot 上分歧 —— Codex 选 complement-super_type fallback + tail-leverage pre-commit;Claude 选残差化 fallback + L1-vs-L2 conditional。owner 走查时拒绝两边的 metric fallback 提议(Codex 因 family 维度前后不一致 + B-2 扩 topic-classify;Claude 因仍是 metric-level fallback 越界 R-1c session scope),引入第三选项 **Option C(R-1e 降级,无 metric fallback)**。
    - **owner-driven framework move(Option C)**:由 owner 在走查中提议 "fallback 能不能是看别的因子",从 abstract 部分推出 R-1e level fallback 合法(R-4a §4 允许因子数与身份由 R-1e 决定),具体 surface 为 "R-1c session 不锁 metric fallback,discriminant trigger 时 R-1e 降级 R-1c slot"。Codex 在白板末尾隐含同意这条 ultimate backstop("如果 fallback 仍超阈值,R-1e 应把两者视作经验冗余,选择或降级其中一个"),Option C 等于把它提前到第一档。这是 **clean-room-first 不仅 surface 已被 reviewer 认可的方向,owner 走查还能 ratchet 出双源未 surface 的 framework move**。
    - **ratchet 论双源验证再坐实**(R-1c 维度):双源都拒绝 WS0.5 §3.3.2 现状 prototype 的 ordinal salience / market-cap-based 框架(Codex 旧提案)+ Baidu Baike fallback + complement-family / non-CLS proxy fallback;双源都采 framing C + L1 mention + log1p(count)。WS0.5 §3.3.2 v0.4 现状的 C-1 / C-2 / C-3 / S-6 reversal 方向 reviewer "推得对",但其 fallback 候选(complement / Baidu Baike)仍是 reviewer pile-on,被 R-1c Option C 一并撤销。
    - **focal_article_policy 在 R-1c 与 R-1b 走相反方向**:R-1b 排除同 article_id(framing 是历史复现,自身不能算 "自己复现自己");R-1c 不排除(framing C 是 model 预训练曝光,case 自身文章在窗口内时也是 exposure)。这是 **framing 决定 boundary 细节** 的实例,不是不一致。
    - **R-1 系列 robust 风格分家(Framework D)**:R-1c 选 1 个 pre-commit tail-leverage appendix,不 mirror R-1b 的 0 pre-commit + 1 conditional 风格。R-1c L1 mention + target only 比 R-1b L2 subject + tradable + target × super_type 尾部更 acute,distribution robustness 更必要。R-4b 追加 R-1b retrospective tail-leverage(不算 R-1b 重开,算 R-4b implementation choice)以维持 paper §robustness 段一致性。
- **R-1 因子(原条目)**:4 个 confirmatory 因子,每个的实现方法 → 然后 4 个的选择。
  - Cutoff Exposure(R-1a):实现简单(日期+manifest),重点是选择确认。
  - Historical Family Recurrence(R-1b):**closed 2026-05-24,见上**。
  - Target Salience(R-1c):**closed 2026-05-25,见上**。
  - Template Rigidity:**零 spec**(flag ④)。从文献审视 → 设计。用户视为
    重要因子(唯一量化事件格式模板化)。
- **R-2 扰动**:6 个扰动各自的实现构思 → 然后保留几个 / 哪几个进
  confirmatory。用户点名要重审 C_NoOp。C_FO/C_NoOp 实现(WS3 `c_fo_rules
  .yaml` 等)尚未建。
  - **2026-05-23 增补 — C_FO vs C_SR 漂移发现(parked)**:R-6 走查里挖出
    C_FO 当前定义(就地换值)与 C_SR(就地翻极性)在实操上几乎重合;且老
    CPT 时代的 FO 是「文末追加 T+1/T+5 真实收益」(用真实股价)——名字
    留下、机制换了。C_FO 机制选择**同时绑定 R-6**(用不用真实收益)。完整
    血缘 + 推荐下一步见 `refine-logs/reviews/REOPEN_R1_R6/cfo_csr_history_findings.md`。等 R-4
    方法论审计落地后再接此项。
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
    + scope boundary + downstream session anchor);audit trail = 同目录
    `whiteboard_analysis.md` 阶段 1 白板独立分析(从"目的"自推该用什么)
    + `subfield_lit_scan.md` 15 篇 2022-2026 代表作扫描双源证据。
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
  分歧信号更干净,但可能扔掉扰动类最强证据;且需真实股价才能识别,实为
  R-6 子决策 ④ 可能的其它准入规则。
- **R-6 预测目标 & ground-truth 使用(flag ⑥,已深化)** — **2026-05-23 暂停,
  待 R-4a 方法论审计**(family 大小决定 R-6 能不能加新 estimand):当前冻结
  设计 P_predict 仅输出方向(涨/跌/中性 + 0-100 信心),**不碰已实现收益、
  无持有期、无 beta**;estimand 全是行为对比,从不与真实股价对照。关键
  澄清:"模型不能用 hindsight"(schema §2.4,测量有效性规则)≠ "实验者
  不能用真实结果做分析"(后者当前设计无此限制,只是没用)。两个 ground
  truth:事件结果(C_FO 需要,会建立)vs 真实股价涨跌(完全没用)。
  用户判断:金融语料优势 = 结果可验证,当前设计未充分利用。待彻底调查:
  实验者是否/如何用真实收益(协变量 / 难度指标 / 过滤标准 / 验证层)。
  **与 R-2 选扰动(C_FO 靠事件结果)、R-5 过滤器、框架设定深度纠缠** ——
  R-6 偏上游(但比 R-4a 下游)。名实缺口:算子名 "alpha prediction" / 动机
  "false alpha" 但 benchmark 不算 alpha;动机↔测量靠论证连接,proposal 须
  显式架桥。
  - **2026-05-22 走查发现(parked)**:C_FO 当前机制 ≠ 老 CPT 时代的「文末
    追加 T+1/T+5 真实收益」机制;FO 机制选择本身既是 R-2 也是 R-6 的决定。
    详见 `refine-logs/reviews/REOPEN_R1_R6/cfo_csr_history_findings.md`。kickoff 已写好
    (`.scratch/session_kickoff_r6.md`),R-4a 落地后再接此 session。

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

- **flag ⑤**:phase7 plan 内一批"扩 fleet / 扩 pilot 前的遗留数字"未对齐。
  ① N=100 vs N=430 —— §5.5/§6 标题、§6.4 n_eff 表、§8.1A 仍写 "100";§5.4
  "C_NoOp 90 of 100" 与 80 pre-cutoff 矛盾。② "9-model / nine-model" ——
  §5.1 WS0 可行性闸门、§5.3 标题 "WS2 nine-model pipeline";fleet 已扩到
  14 P_predict-eligible / 16 总。(注:pilot 现为 80 + 700 = 780。)
- (Pass 2)FROZEN_SHORTLIST §1 Target Salience 仍写 "ordinal";
  MEASUREMENT_FRAMEWORK 的 fleet 数字(5 白盒/9 模型)、P_schema 状态过时。

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
