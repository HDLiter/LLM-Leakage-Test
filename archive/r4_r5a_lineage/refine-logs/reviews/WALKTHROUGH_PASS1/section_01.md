# Pass 1 Walk-through — 第 1 章 / 共 7 章:研究问题(用户已确认 + 修正)

> 这是 Claude Code 对当前实验的"逐章忠实叙述"。Pass 1 = 粗粒度连贯性审查。
> 本文件供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、
> 逻辑断点、追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。
> 本章已经过用户审阅并修正,以下为确认版本。

## 开工发现(flag ①)—— 已确认,解决方案已定

kickoff 指定先读 `docs/RESEARCH_PROPOSAL.md`,该文件不存在(已归档为
`archive/pre_benchmark/docs/RESEARCH_PROPOSAL_v2.md`)。当前实验无成文研究
问题文档。解决:Pass 1 结束后组装一份中文 `docs/RESEARCH_PROPOSAL.md`
(用户批准的中文特例),复活 CLAUDE.md 指向的路径。

## 研究问题(用户确认版)

在中文金融新闻情感/alpha 分析任务上,LLM 的训练数据泄露(memorization /
look-ahead leakage)有多严重,以及它系统性地随哪些"案例层面因子"变化。

- 对象:LLM 把中文 A 股新闻(财联社电报 CLS)转成情感/方向/alpha 预测时。
- 泄露:模型不从眼前文章推理,而从参数记忆调出"事件后来的结果"作答。
- 关键:不止"有没有泄露",而是"什么案例更易泄露"——4 个 confirmatory 因子。
- 工具:factor-driven memorization benchmark——2,560 案例、16 模型、四层框架。
- 定位:characterization(刻画型)benchmark 论文;非机制论文、非"证明泄露"。
- 中文优先;英文对等数据集为 stretch goal,中文完成后再评估(5 触发条件)。

## 动机链条(用户确认版 —— 修正了第一稿"动机=Thales"的说法)

1. 起点:为量化项目(Thales 系)服务——测量泄露、找机制减轻它。
2. 实验发现:文本本身带各种内部因素,影响大模型是否记住某条新闻。
3. 转向:要做有效的泄露检测,先得有一个能区分这些文本内部因素的有效
   benchmark,否则测出来的信号无法解释。
4. 所以当前论文的贡献 = 这个 benchmark 本身。Thales/量化项目是起点与
   应用背景,不再是论文的直接 motivation。

文献定位:中文金融 NLP 污染审计基本空白;无先例做"同源新闻+因子受控+
跨模型 fleet"的 memorization benchmark。

## 结构:现在做的是 pilot,不是答案

Phase 7 = pilot(N=430)= 证明冻结测量栈能跑/能审/能分析 + 估 effect
size、协方差、给 main run 算 power;明确不回答论文主问题。
Phase 8 = main run(N=2,560)= 回答研究问题。两阶段自适应预注册。

## flag ② —— 已确认并关闭

memory `thales_connection.md` 把"Task Decomposition Reduces Leakage"列为
论文核心贡献——这是 Phase 5 转向前的旧论点。当前 R5A 冻结设计不测此假设。
用户确认:decomposition 不进 confirmatory scope,顶多作为 exploratory
以后有空再做;理由——因子已很多,再加 P_predict 两个变体易成 p-hacking。
→ memory `thales_connection.md` 待更新(Pass 1 结束统一处理)。
