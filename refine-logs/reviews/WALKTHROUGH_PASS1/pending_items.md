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

- **R-1 因子**:4 个 confirmatory 因子,每个的实现方法 → 然后 4 个的选择。
  - Cutoff Exposure:实现简单(日期+manifest),重点是选择确认。
  - Historical Family Recurrence:实现有 WS0.5 §5 管线(待 clean-room 复审);
    "family" 粒度(标的×super_type)用户未真正想好。
  - Target Salience:实现有 WS0.5 §3.3(待 clean-room 复审)。
  - Template Rigidity:**零 spec**(flag ④)。从文献审视 → 设计。用户视为
    重要因子(唯一量化事件格式模板化)。
- **R-2 扰动**:6 个扰动各自的实现构思 → 然后保留几个 / 哪几个进
  confirmatory。用户点名要重审 C_NoOp。C_FO/C_NoOp 实现(WS3 `c_fo_rules
  .yaml` 等)尚未建。
- **R-3 negative controls**:BL2 / 同-cutoff 证伪对 / C_NoOp_placebo / BL1 /
  BL3 是否充分,展开分析。
- **R-4 pilot 统计整体**(原 β1/β3,已扩大):用户要求**单开一个 session**
  重审 pilot 全套统计 —— 不只 β1/β3,还含等价检验(TOST)、多重比较校正
  (Westfall-Young)、功效模拟、混合模型规格、bootstrap。用户点名这是
  "reviewer 给对的目的 + 甩一堆公式 + 我就同意了"的典型例子。方法:
  clean-room —— agent 先白板从"目的"自推该用什么,再对当初 reviewer 的
  方案。E_CMMD 的"分歧≠记忆"批评也归此处评估(设计现有防御:cutoff-单调性
  + 能力协变量 + 同-cutoff 证伪对 + 人群层面聚合;"够不够"是统计问题)。
- **R-5 采样过滤器专题**:用户要求单开讨论。包含 ① 可交易实体 filter
  (已存在 WS0.5 §3.3.1 案例准入预过滤,但在重开区,一并重审)② 新闻长度
  filter(**新增** —— 超长讲话 / 一句话简讯;当前设计无长度过滤)③ 反直觉
  /难预测案例过滤(**新候选**,用户提:利好不及预期等)—— 双刃:让跨模型
  分歧信号更干净,但可能扔掉扰动类最强证据;且需真实股价才能识别,实为
  R-6 子决策 ④ 可能的其它准入规则。
- **R-6 预测目标 & ground-truth 使用(flag ⑥,已深化)**:当前冻结设计
  P_predict 仅输出方向(涨/跌/中性 + 0-100 信心),**不碰已实现收益、无
  持有期、无 beta**;estimand 全是行为对比,从不与真实股价对照。关键澄清:
  "模型不能用 hindsight"(schema §2.4,测量有效性规则)≠ "实验者不能用
  真实结果做分析"(后者当前设计无此限制,只是没用)。两个 ground truth:
  事件结果(C_FO 需要,会建立)vs 真实股价涨跌(完全没用)。用户判断:
  金融语料优势 = 结果可验证,当前设计未充分利用。待彻底调查:实验者是否/
  如何用真实收益(协变量 / 难度指标 / 过滤标准 / 验证层)。**与 R-2 选扰动
  (C_FO 靠事件结果)、R-5 过滤器、框架设定深度纠缠** —— R-6 偏上游。
  名实缺口:算子名 "alpha prediction" / 动机 "false alpha" 但 benchmark
  不算 alpha;动机↔测量靠论证连接,proposal 须显式架桥。

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
