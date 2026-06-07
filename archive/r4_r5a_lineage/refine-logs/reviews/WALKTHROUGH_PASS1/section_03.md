# Pass 1 Walk-through — 第 3 章 / 共 7 章:4 个 confirmatory 因子

> 供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、逻辑断点、
> 追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。

## 4 个因子(WHAT + WHY)

confirmatory family = 5 estimand × 4 factor = 20 系数。4 个因子:

### 1. Cutoff Exposure(Bloc 0 — 时间暴露;case×model 连续)
测:模型 m 的训练 cutoff 相对案例 i 事件日期的位置/程度。
WHY:最直接的泄露通道——事件若发生在模型 cutoff 之前,模型训练时就*可能*
见过该事件及其结果。case×model:既依赖案例日期,也依赖模型 cutoff。
输入:event_date + model_cutoff;无 T1/T2/T3 依赖。

### 2. Historical Family Recurrence(Bloc 1 — 重复;case-level 连续)
测:(target × 事件家族)这个模式在 cutoff 前的 CLS 里复现了多少次。
= `log1p(cls_family_recurrence)`,固定窗口 [corpus_start, earliest_model_cutoff)。
WHY:重复强化记忆——预训练里见过很多次的模式更可能被记住。
输入:CLS 复现计数;需 T1(事件分类)+ T2(实体抽取)。

### 3. Target Salience(Bloc 2 — 显著性;case-level 连续)
测:标的实体有多"出名"。= `log1p`(cutoff 前 CLS 里提及该 target 的文章数,
跨所有事件类型)。WHY:越出名的标的,预训练里关于它的文本越多,模型对它
的先验/记忆越强。用语料提及数而非市值——市值测的是公司规模不是名气,会把
"小但被大量报道"的标的(妖股、丑闻股)误判为低显著性。
输入:CLS 提及计数;需 T1+T2;复用 §5 recurrence 管线。

### 4. Template Rigidity(Bloc 1 — 重复;case-level 连续)
测:文章有多"模板化/套话"(shingling / 模板库重叠度)。
WHY:高度模板化的新闻(标准监管公告、财报套话)结构上高度重复,模型能靠
套模板而非读内容来 pattern-match——脆弱的模板匹配是记忆的特征。
输入:纯文本特征;无 T1/T2/T3 依赖。

## 三通道故事

4 个因子 = 泄露的三个驱动通道:**时间访问**(Cutoff)+ **重复**(Recurrence
跨文章复现、Template Rigidity 文章内套话)+ **显著性**(Target Salience)。

## β1 vs β3 结构(重要)

每个 confirmatory estimand 对全部 4 个因子各测一次。但系数定义不同
(plan §8.2):
- Cutoff Exposure → 测**主效应 β1**。
- 其余 3 个因子 → 测**与 cutoff exposure 的交互项 β3**。
即:Recurrence / Salience / Template Rigidity 不是独立的泄露轴,而是
**cutoff 泄露通道的调节因子**——假设是"高复现/高显著/高模板化会*放大*
cutoff 暴露带来的泄露信号"。"什么案例更易泄露" = "cutoff 优势更大"。

## Bloc 3 不是 confirmatory

Bloc 3(机构阶段/来源:Structured Event Type、Modality、Event Phase、
Session Timing)**不给 confirmatory 因子**,只作 interaction-menu 分层
(FROZEN_SHORTLIST §8)。20 系数家族里没有 Bloc 3。

## 本章 flag

**flag ③:用户对"文本内部因素"的表述 vs 实际因子集。** 用户第 1 章说
"文本本身有各种内部因素影响记忆"。但 4 个冻结因子里严格说只有 Template
Rigidity 是"文章文本内部"的;Cutoff Exposure 是时间×模型的,Recurrence
和 Target Salience 是从 CLS 语料频率派生的。需用户确认这是宽泛表述还是
期待落差。

**次要(Pass 2 处理):** FROZEN_SHORTLIST §1 仍把 Target Salience 写成
"ordinal";WS0.5 memo C-1 已改为连续 log1p 提及数。冻结文档文本与决策
memo 的对账属 Pass 2 范围,此处只在 Pass-1 粒度确认"Target Salience 现在
是连续语料提及数,不是序数显著性档"。

---

## 用户审阅后续(第 3 章 3a–3d)

### 3a 因子取舍 — flag ③ 关闭
用户确认:"文本内部因素"是宽泛表述。真实情况 = 提过很多有价值的因子,
在 20 系数(5×4)多重比较预算下被迫四选,参考 Codex 意见选了这 4 个。
事件类型 / 权威度被承认有影响但因预算割舍。proposal 动机段须写明此取舍。

### 3b Recurrence 的 "family" 定义(用户提问,memo 已有答案)
WS0.5 memo §5.1:family = (具体可交易标的实体) × (super_type 5 类大事件
分类)。事件轴用大的(5 类 super_type,非 13 类 V3);实体轴用标的本身
(公司=公司、指数=指数,不上抽行业)。折中:实体轴精确、事件轴粗。
待用户确认是否符合其意图。

### 3c flag ④ — Template Rigidity 无实现方案
Template Rigidity 是 4 个 confirmatory 因子之一(占 20 系数的 5 个),但
当前无任何权威文档定义其计算方法。config/factors/ 不存在;factor_schema
.yaml 未生成。WS0.5 memo §2.4 仅以 "shingling / template-bank overlap"
一笔带过并以"无 T1/T2/T3 依赖"为由不展开 —— 但无 Thales-prompt 依赖 ≠
无需设计。FACTOR_LITERATURE_PROVENANCE.md(非活跃因子图)有一句带保留的
char-5gram TF-IDF cosine 建议。WS0.5 锁了另外 3 个因子的管线,独漏此项。
风险:WS0.5 实现 S1–S5 将无 spec 可依、临场拍一个 confirmatory 因子。
待用户决定:pilot manifest 冻结前是否补 Template Rigidity 设计小节。

### 3d β1/β3 结构 — 批判性审视(用户点名)
模型:score = β0 + β1·cutoff + β2·factor + β3·(cutoff×factor) + β4·capability
+ u_case + v_model + e。Cutoff 因子看 β1(主效应),其余 3 因子看 β3(交互)。
- Steelman:交互当主系数是有原则的混淆控制 —— 差掉"案例难度"污染,与
  E_PCSG 配对识别同逻辑。内部自洽。
- 代价 1:20 系数里 15 个是交互项 → 对样本量苛刻;有效性押在 main run
  功效(§8.8 模拟 / §13 GO 门 WY 校正 80%)。
- 代价 2:"泄露案例"被操作定义收窄为"使 cutoff 差距更大"——claim 锁死
  为时间通道专属。
- 代价 3:4 因子非平级 —— 1 条时间轴 + 3 个调节因子;proposal 须如实写。
- 结论:站得住、自洽,但是苛刻设计,值得用户主动签字。可选追加统计专项审。
