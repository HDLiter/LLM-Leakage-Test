# Cutoff Probe Design — DRAFT DECISIONS

**Status**: **DRAFT 2026-05-28** — subordinate to R-1a DRAFT(见 `R1a_DECISIONS.md` 头)。
- 本 doc 是 cutoff probe walkthrough L1–L10 的 canonical 落地(< 200 行,for downstream agents)。
- Pending **joint freeze with proposed case-level Information Novelty (N) factor**(新 session:`.scratch/session_kickoff_novelty_factor.md`)。
- 走查 audit trail = `.scratch/cutoff_probe_decisions_running.md`;协议草案 = `cutoff_probe_protocol_codex.md`;manifest 调查 = `cutoff_deep_research_gpt.md`;文献综述 = `cutoff_probe_litreview_codex.md`。

> **总定位**:**验证非定义** —— 体检 manifest + 偏差人工复核;**永不自动改 manifest、永不喂 exposure 指标**(守 R-0 §2 约束 5,防与 logprob estimand E_CTS 自闭环)。
> **关键准则(§10)**:probe 真正想测的是模型对"理论上从 cutoff 前信息**不可推断**的事实"是否答得对——其余题污染信号、verification 失效。

## 1. Strategy: narrow → wide (L1)
- 因我们是**验证已知 manifest**(有先验),不是从零探索 → Stage 1 在 manifest 处下针,有问题再扩。
- **Stage 1**:窗 = `manifest ± (min_side + ~2–3 月容差)`;每月 ≥ 30 题。
- **例外**:manifest 已知非真 cutoff(DeepSeek 发布日 2026-04)→ 走宽扫或在最佳估计 ~2025-05 处下针。
- **扩展触发**:窗内一路高 → 真 cutoff 更晚,往后扩;一路低 → 更早,往前扩;跌得不干净 / 分级 → 扩 + 人工。
- **Stage 2**:仅对触发模型;沿指示扩到夹住(两侧 ≥ min_side)或撞数据边界 → null + 人工。
- **min_side = 3**,带护栏(CI ≤ 3 月才算数 + 平缓 / 低题量 → null + 人工复核)。**注**:§9 改 PELT 检测后,min_side 精神由 PELT penalty 等价承担。

## 2. Domain + language (L2)
- **Track A — 通用世界(英文)dated-QA = 主 gate**:对 manifest 通用知识口径最匹配;QA-valid 模型都能答。
- **Track B — CLS 中文金融 dated-QA = 域诊断**(从语料派生),**非主 gate**;验"曝光所在域(中文财经)知识横在哪",防与曝光语料自闭环。
- 两线**分别打分、互相对照**。

## 3. Question count + LLMLagBench reuse (L3)
- **通用线 = LLMLagBench 规模(~30/月)**;**拿到 LLMLagBench 即直接用**(套我们评分);近端(2025 下半年 = Claude 窗口)+ DeepSeek-V4 / Claude-4.6 窗口需自补题。
- **CLS 线 = 30/月起,Stage-2 按需到 50**;从语料派生。
- 仅 **QA-valid 集(4 黑 + 大白)** 跑 QA;小弱白盒只走 Path-E。
- **题库 withhold**(probe = side benchmark;同 LLMLagBench 防污染逻辑)→ 复用 LLMLagBench 数据无转载顾虑,但须守邮件 data-use terms + 引用。

## 4. Claude (L4)
- 取消独立 100/月 May–Aug 加密;走标准 narrow→wide(窗口 ~ 2025-08),Stage-2 加密头号对象;**先 50/月**;差一点能分清才到 ~100;多级 / 糊 / null → 人工。
- (Claude 可能本无单一 cutoff 月;不硬掰。§9 PELT 多 changepoint 可直接刻画。)

## 5. Review process (L5) — no auto-gate
- **取消 Codex 红/黄/绿自动 gate** —— fleet 仅 16 模型 → **全部人工复核**;本就是 probe task、人在环,无需阈值 triage。
- **标准化证据**(每模型):点估计 / bootstrap CI / `offset_from_manifest` / `refusal_rate` / `unknown_rate` / QA-vs-Path-E 一致性 / PELT changepoints + 各 CI / faithfulness 均值曲线。
- **manifest-revision 准则(audit-rule)**:**不预拍数字**(定义"差多少"需先知数据形态)→ 两阶段:
  - probe 首跑(pilot 窗口)刻画 horizon 数据形态;
  - 据此**冻结**修订准则(倾向 CI 驱动:manifest 月落 horizon CI 外即进修订候选);
  - **main run 前锁死、之后不为凑泄露重调**;论文预先声明的是**流程 + 冻结纪律**。

## 6. UNKNOWN / refusal (L6)
- 主曲线:正确 / 高 faithfulness = 高;其余(错 / UNKNOWN / 拒答 / 解析失败)= 低 / 0。**不排除**(排除奖励拒答模型,抹平 Claude 真 horizon)。
- **单独报**:`refusal_rate` + `unknown_rate` + 解析失败率。
- **用法**:答对率掉点 ⟷ 拒答率飙升 → 该 horizon 可能是"被对齐成不肯答"的边界而非"不知道"的边界 → 标记人工(Claude 尤其)。

## 7. Box-type division (L7)
| 模型组 | Path-E | QA |
|---|---|---|
| 有能力白盒(Qwen3 ×4 / GLM / 较大 Qwen2.5) | ✓ | ✓ → 两线互证 |
| 小弱白盒(Qwen2.5 1.5B / 3B) | ✓ | ✗(答对率 < ~0.45 地板) |
| 2 个 Llama(logprob-only) | ✓ | ✗(非 P_predict) |
| 4 黑盒(DeepSeek-V4 / GPT-4.1 / GPT-5.1 / Claude-4.6) | ✗(logprob 不可用) | ✓(唯一线) |
- Qwen2.5 哪些尺寸"能答得动"由 runtime 准确率地板 ~0.45 现定。
- 疑点全覆盖:白盒疑点(Qwen3 / GLM)两线;黑盒疑点(DeepSeek / Claude)一线(QA)。

## 8. Reporting nomenclature (L8)
- 字段名 = **`empirical_knowledge_horizon`**(经验知识边界);**非** `training_cutoff_observed` / `true cutoff`。
- 字段集:`manifest_date` / `manifest_source` / `vendor_claim_type`(知识 vs 训练 vs 发布日代理 vs 社区猜)/ `empirical_knowledge_horizon`(点或 list,可 null)/ `horizon_ci_lower` / `horizon_ci_upper` / `offset_from_manifest`(带符号)/ `refusal_rate` / `unknown_rate` / `qa_path_e_agreement`(白盒)/ `n_changepoints` / `changepoint_dates_list` / `notes`。
- **论文写死解释句**:"该探针估计模型能可靠回答公开事实的最后月份;它是训练数据 cutoff 的**经验下界 / 健康检查**,不是最新训练样本日期的证明。该指标只反映**训练习得的、不可由先验推断的**知识(见 §10)。"
- 与 Anthropic `reliable knowledge cutoff` vs `training data cutoff` 区分一致,不撞 vendor 概念。

## 9. QG + scoring + detection: LLMLagBench-aligned (L9)
- **出题**:LLM-assisted 草题(out-of-fleet:Claude dev + Codex via /codex-run)+ 高比例人工筛(参 LLMLagBench 8.4k → 1.7k ≈ 20% 留存);CLS 题源 = 文章本身原子事实;**题库 frozen + SHA 入 manifest**;出题 LLM **不参与判分、不按目标模型结果回改题库**。
- **判分**:**Faithfulness 0–2 LLM-judge**(out-of-fleet),target **Cohen's κ ≥ 0.8** vs 人工抽检(LLMLagBench 报 0.81 / 0.83);拒答 / UNKNOWN 映射为 0 进入主曲线 + 单独记。
- **检测**:**PELT 多 changepoint**(直接处理 Claude 那类部分 / 分阶段 cutoff);接受准则用 PELT penalty + bootstrap CI;具体 penalty / bootstrap 数 → pilot 校准。
- 输出可为 0 / 1 / 多 changepoint;无可靠 changepoint → null + 人工。

## 10. PRIMARY question filter: 答案不可由先验推断 (L10) — **核心准则**
- **probe 真正的存在意义**:测的是模型对"理论上从 cutoff 前信息**不可推断**的事实"是否答得对。其他题模型答对**不证明"见过"**(只证明它会算),进 probe → post-cutoff 答对率被撑高 → 真掉点冲淡 / 错位 → manifest offset 验证失效。
- **反例**(必筛掉):可预测日历事件(财报日 / 政策会议 / 披露窗口 / 调仓 / 月度统计);命名规律可推(2024-09 新 iPhone 必是 iPhone 16);季节性 / 周期性 / 形式类。
- **正例**:M&A 条款 / 突发高管变动 / 意外监管行动 / earnings beat-miss 具体数字 / IPO 定价 / 突发市场事件。
- **CLS 中文财经域日历驱动密度高 → 拒绝率可能比 LLMLagBench 那 80% 更狠**;**候选池 ≥ 5–10× 目标量**(pilot 校准)。
- **操作化**(具体阈 → pilot 校准):
  - **人工主筛** —— "不可由先验推断"是 §9 出题流程的**第一筛选准则**(优先于"原子事实 / 答案在文章里"等);
  - **可选自动初筛** —— 用 cutoff 远早于题目日期的 out-of-fleet 模型(GPT-3.5 / Llama-2 类)答候选题,**能答对即剔**。
- **论文方法学**:此条要进 **prominent 位置**,不能埋在 question construction 子节里——它是 probe 存在意义本身。

## 11. Pilot deliverables(待 pilot 校准)
- horizon 数据形态刻画 → 冻结 manifest-revision 准则(§5)。
- PELT penalty / bootstrap 数 → 接受准则(§9)。
- 候选拒绝率 + 自动初筛阈 → 题库纪律(§10)。
- 起点 manifest 修订候选清单 → R-1a 中心值 sign-off。
- judge LLM 校准抽检(Cohen's κ ≥ 0.8)→ §9 判分。

## 12. Connected updates (freeze 同步)
- **`R1a_DECISIONS.md §6`** 措辞:取消"红/黄/绿 gate"(§5)、加 LLMLagBench-aligned 方法学锚点(§9)、加 §10 不可推断准则。本 doc 是 R-1a §6 验证轨的展开,subordinate to R-1a draft。
- **论文方法学**:§10 不可推断准则需 prominent 位置;§8 解释句已含该限定。
- **与 case-level Information Novelty (N) factor 联合 freeze** —— L10 准则推到 case 层即 N 的种子;详见 `.scratch/session_kickoff_novelty_factor.md`。
- **R-4 construct-validity 联动**:novelty 可能是该框架"真正 factor"的强候选,cutoff 退到 post-cutoff-null 验证锚——本 doc + 新 session + R-4a 深审三方对齐 freeze。

---

**状态**:DRAFT 待与 novelty session + R-4a 联合 freeze;实施(题库构造 / probe 首跑)gated on fleet 部署 + 黑盒预算 + judge 校准。
