# Pass 1 Walk-through — 第 5 章 / 共 7 章:模型 fleet + pilot 设计

> 供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、逻辑断点、
> 追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。

## 模型 fleet:16 模型,split-tier

fleet 是时间泄露准实验的物理基础——无横跨 cutoff 的模型多样性即无 β1。
- 14 P_predict-eligible:10 full-operator 白盒(5 Qwen2.5 + 4 Qwen3 + 1 GLM)
  + 4 黑盒(DeepSeek V4 Pro / GPT-4.1 / GPT-5.1 / Claude Sonnet 4.6)。
- 12 P_logprob-eligible:上述 10 白盒 + 2 P_logprob-only Llama
  (Llama-3-8B / Llama-3.1-8B);Llama 不进 P_predict。
白盒走 vLLM,黑盒走 API。白盒关键因 P_logprob 需 token logprob;DeepSeek
logprob 坏。fleet 在 Phase 7 设计期扩两次:9→14(2026-04-27 PCSG 重定义)
→16(2026-04-29 加 Llama),均有 DECISION memo;FROZEN_SHORTLIST §10 本就
不冻结 fleet 版本,故非漂移。

关键设计动作:
- PCSG 跨版本 Qwen 对 (qwen2.5-7B, qwen3-8B):原同-tokenizer 同-cutoff 对
  无 cutoff 差(Stats lens 判为测量缺陷),改跨版本对——共享 Qwen2Tokenizer
  基础词表、cutoff 不同。+ 1 个 Llama 跨版本对。共 2 个 confirmatory PCSG
  时间对。within-version 同-cutoff 对改作 E_PCSG_capacity_curve(探索性)。
- 同-cutoff 证伪对 GLM-4-9B ↔ GPT-4.1:同 cutoff 不同架构,查信号是否来自
  架构差异(early-warning ratio)。

## pilot:N=430 = 80 pre-cutoff + 350 post-cutoff

- 80 pre-cutoff:confirmatory 因子分析在此。= 60 verified-outcome 扰动密集
  + 20 因子覆盖补充。日期窗三分(≤2023-10:20 / 2023-11~2024-06:30 /
  2024-07~2025-01:30)。80 = 原"默认 100"仲裁点拆出 post-cutoff 后所剩。
- 350 post-cutoff:BL2 负对照桶,≥2026-02-01。350 让 TOST 在 SESOI=0.15
  下数学可行(真效应=0 时 ~60% power;700 则 ~96%)。350 = 保守 GO 量。
扰动只在 80 pre-cutoff 上做。

## n_eff 设计

check_pilot_cells.py 算 n_eff(estimand, factor_bin, analysis_unit),每
estimand 用自己的分析单元。规则:目标 n_eff≥20;最低 ≥15;不够则因子三
分位塌为中位数二分,再不够才加 N。15 = pilot 混合模型稳定性下界护栏。

## 与研究问题的 why 链

fleet 跨 cutoff 结构 = Cutoff Exposure 准实验本体;pilot = 标定运行;
n_eff = 保证因子 bin 不欠识别。均服务 RQ,无断点。

## 本章 flag

**flag ⑤:phase7 plan 内 N=100 与 N=430 未对齐。** pilot 从 100 改为 430
(80+350),但多处正文留旧 "100":§5.5 标题 "WS4: N=100 pilot"、§6 标题
"N=100"、§6.4 n_eff 表 "all 100 cases"、§8.1A "all 100"。具体矛盾:§5.4
"C_NoOp ... at least 90 of 100 pilot cases"——但扰动只在 80 pre-cutoff 上
做,无 100。主计划文档内部真实不一致,需修。

**heads-up:cutoff 日期是"断言"非"测量"。** Cutoff Exposure 是 β1 脊梁,
但各模型 cutoff 目前 operator-asserted。Path E 经验探针验证之,但 Path E
需 logprob——只验白盒;4 黑盒 cutoff 仍只能用厂商声明/推断。设计有意识:
命名 "Assumption 1" + "cutoff-monotone(非因果)" 措辞 + 同-cutoff 证伪对
兜底。非盲点,是被管理的假设;但论文时间结论将一直 hedged,黑盒 cutoff
准确性不可经验验证。

**narration:** ① split-tier → 无任何单一模型看到完整 confirmatory family
(E_CTS/E_PCSG 仅 12 白盒;E_CMMD/E_FO/E_NoOp 14 个)。固有(logprob 需白盒)。
② pilot 80/350、n_eff 矩阵、日期窗按当前 4 因子/2 扰动算;操作化层重开后
n_eff 矩阵需重算,pilot 规模可能动。

---

## 用户审阅后续(第 5 章)

- 决策:pilot post-cutoff 桶 = 700(非 350)→ pilot 总量 = 80 pre + 700
  post = 780。代价:运行时长/API ~1.8×,USD 300 cap 需上调。
- cutoff-asserted heads-up 关闭:用户判断 cutoff 必然要经验测量、不可钉死
  在某一天(覆盖密度渐变),与设计的连续 case×model 因子 + Path E
  monthly60_36mo horizon 探针一致。
- split-tier heads-up 关闭:预料之中。
- pilot 具体内容已向用户复述:manifest(780 案例)→ 核心运行矩阵
  (P_logprob 全 780 / P_predict baseline 全 780 / 扰动仅 80 pre-cutoff
  且审计后)→ WS3 全量人工审计 → 产出 5 estimand 表 + n_eff + QC +
  runstate.db → WS5 统计(effect size / 相关矩阵 / BL1 / BL2 TOST /
  N=2560 power 模拟 / Stage-1 预注册)。pilot 标定仪器,不回答 RQ。

## 用户审阅后续 2(第 5 章 — 风格 / 成本 / flag ⑥ / filters)

- 用户反馈:术语过多。后续按"实验目的"白话叙述。pilot 已用白话重讲。
- $300 澄清:是 plan §11.3 的硬上限(保险丝),非预期账单。12 白盒在租用
  GPU 上跑(算力费,另一条预算线);仅 4 黑盒是 API 美元。实际 API 花费
  预计远低于 $300。post-cutoff=700 后上限需上调。
- **flag ⑥ — 预测目标**:冻结 schema(R5A_OPERATOR_SCHEMA.md §3)中
  P_predict 输出方向(涨/跌/中性)+ 0-100 信心 + explicit_memory_reference
  自报标记 + 证据引用 + target_echo;**不含**已实现收益 / 持有期 / beta;
  §2.4 明禁模型用已实现收益。(修正:本文件初版"仅输出方向+信心"措辞有误,
  漏了记忆标记和证据引用 —— Codex 连贯性审查 finding 2。)
  全部 confirmatory estimand 是行为对比(跨模型分歧 E_CMMD / 扰动翻转
  E_FO·E_NoOp / 文本意外度 E_CTS·E_PCSG),**从不与真实股价对照**。无收益
  率、无持有期、无 beta。用户问"一日/三日/五日/减 beta"在当前设计无落脚点
  —— 那是转向前老提案 RQ4(rank IC / 3 日持有)的内容,转向时已砍。
  名实缺口:算子名 "sentiment/alpha prediction"、动机 "false alpha",但
  benchmark 不算 alpha;动机↔测量靠论证连接,proposal 须显式架桥。
  待用户拍:纯行为测量是否为有意 / 是否要加收益挂钩的探索性部分。
- filters:可交易实体 filter 已存在(WS0.5 §3.3.1),在重开区;新闻长度
  filter 为新增需求;合为采样过滤器专题 R-5。

## 用户审阅后续 3(第 5 章 — pilot 统计 / E_CMMD 批评 / ground truth)

- pilot 全套统计单开 session 重审(clean-room)。用户点名为"reviewer 给对
  目的 + 甩公式 + 我同意"的典型例子。→ R-4 扩为"pilot 统计整体"。
- E_CMMD"分歧≠记忆"批评:设计防御 = cutoff-单调性(非原始分歧)+ 能力
  协变量 + 同-cutoff 证伪对 + 人群层面聚合;"够不够"归 R-4 统计评估。
- ground truth 两义澄清:事件结果(C_FO 需要)vs 真实股价(未用)。关键:
  "模型不用 hindsight" ≠ "实验者不用真实结果分析";后者当前设计无限制、
  只是没用。金融语料优势 = 结果可验证,未充分利用 → R-6 深化。
- 反直觉案例过滤:R-5 新候选,双刃(净化跨模型分歧 vs 扔掉扰动类最强
  证据),需真实股价识别 → 实为 R-6 子决策。
