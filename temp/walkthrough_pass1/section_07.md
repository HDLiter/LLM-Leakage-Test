# Pass 1 Walk-through — 第 7 章 / 共 7 章:已做 / 在做 / 下一步

> 供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、逻辑断点、
> 追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。

## 已做

- WS0:基本完成 —— 代码骨架(contracts/fleet/runtime/io_utils)、runstate
  DB、16 模型全 pin(白盒 HF+tokenizer SHA、黑盒 provider slug)、运行配置、
  冒烟工具;接口 memo 2026-04-26 签字。
- WS1:代码建好 + 冒烟通过(30 案例 smoke、全模型验证)、AutoDL 云开好、
  Path E 探针集建好;但未在 pilot 上正式跑(pilot 清单不存在)。最靠前。
- WS0.5:设计完成(memo v0.4 已提交),代码未动。

## 在做 / 卡住

- WS1 云执行:冒烟 + 云端 handoff 完成;Path-E 跑 + pilot logprob 跑未发生。
- WS0.5:本"等签字",现转入重开,签字搁置。

## 没做

- WS2(P_predict):未开工 —— 无 p_predict.py、无黑盒后端;仅黑盒凭证冒烟过。
- WS3(扰动+审计):未开工 —— perturbations/ audit/ 目录空,规则配置/审计
  app 无。
- WS4(pilot):未开工 —— 无 pilot 清单/采样脚本/结果/runstate.db。
- WS5(统计):未开工 —— estimand 模块空,功效模拟器未写。
- WS0.5 实现 S1-S5:未开工。

## 观察:实际是串行,不是并行

计划称 WS0.5/WS1/WS2/WS3 四条并行;实际 WS1 被深做(连云基建)、WS0.5
出设计 memo、WS2/WS3 一行未碰。项目做掉了设计最清楚的 WS1 + WS0.5 设计
文档,停在"设计有争议的实现"(WS2/WS3)之前 —— 而 WS2/WS3 正是 flag ⑥
(预测目标)、R-2(扰动)、R-5(过滤器)落地处。

→ 重开操作化层几乎不浪费已写代码:WS0/WS1(完成)不在重开区;WS0.5 仅
设计无代码;WS2/WS3/WS4/WS5 未开工。扔掉代码 ≈ 0。WS0.5 设计大部分可用
(implementation-first 材料,需 clean-room 复审 + 补 Template Rigidity)。
走查时机幸运 —— 赶在争议代码写出之前。唯一真实沉没成本:WS0.5 memo 三轮
Codex 审 + v0.4 简化的来回损耗;WS1 云基建不浪费。

## 下一步

1. 收尾 Pass 1:Codex 连贯性审查 → codex_flags.md。
2. 结构化重开操作化层 R-1…R-6,clean-room-first。
3. 并行:design-agnostic WS0.5 基建 + WS1 继续。
4. 组装中文 docs/RESEARCH_PROPOSAL.md。
5. 更新 memory。
6. 然后 WS0.5 实现 / WS2 / WS3 / WS4 / WS5。

## 本章 flag

小:memory project_status.md 写 "WS2/WS3/WS4 parallel" 读似在推进,实际
未开工;Pass 1 收尾更新 memory 时改。
