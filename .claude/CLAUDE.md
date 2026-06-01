# Project: 中文金融新闻 LLM 训练数据泄露 —— 因子受控 benchmark

## 概述
研究 LLM 在中文金融新闻(财联社 CLS 电报)情感 / alpha 分析任务中的训练数据
泄露(memorization / look-ahead leakage)。当前实验是一个**因子受控的
memorization benchmark(R5A)**:用四层框架(Factor / Perturbation / Operator
/ Estimand)、16 模型 split-tier fleet、两阶段自适应预注册,刻画泄露如何随
案例层面的因子变化。成文研究问题见 `docs/RESEARCH_PROPOSAL.md`。

## ⭐ 与用户交流:白话优先,展开术语(2026-05-31 用户硬性要求)
和用户对话时**不要直接甩内部代号/术语**——这些代号是 agent 之间的简写,
用户不该被迫反向解码。规则:
- **每个概念第一次出现,先用白话中文讲清它是什么,代号最多作括注跟在后面。**
  例:不要写「F_salience 拨杆」,要写「标的显著度(某只股票/板块在新闻里被
  提及得多不多)这个旋钮(代号 F_salience)」。
- 涉及的典型代号(出现就得展开):因子 F_*(F_salience/F_recur/F_entval/
  F_cutoff…)、扰动 C_*(C_SR/C_FO/C_anon/C_NoOp…)、算子 P_*(P_predict/
  P_logprob)、指标 E_*(E_SR/E_FO/E_PCSG…)、决策编号 D1–D9、resistance、
  memory_lift / lift-over-prior / raw_score、null / 分层 null、会聚效度、
  confirmatory / exploratory、Type A 闸门、manipulation check 等。
- **宁可话长,也别让用户解码。术语密度过高 = 把沟通成本转嫁给用户。**
- 适用范围:所有**面向用户**的交流。**内部文档**(docs/、refine-logs/、
  代码注释)仍用紧凑代号——它们是给 agent 读的 context,展开反而稀释。

## 当前阶段(2026-05-22)
Pass-1 全实验走查完成:研究问题与四层框架确认 sound;框架与实现之间的
「操作化层」(因子 / 扰动 / estimand / 预测目标 / 采样 / pilot 统计)进入
**结构化重开 R-1…R-6**(走 clean-room-first)。

- 进度:WS0 基本完成、WS1 建好 + 冒烟通过;WS0.5 设计完成(代码未动、
  签字搁置);WS2 / WS3 / WS4 / WS5 未开工。
- 下一步:R-1…R-6 重开 → WS0.5 实现 / WS2 / WS3 → pilot(N=780)→
  main run(N=2,560)。
- 关键文档:
  - `docs/RESEARCH_PROPOSAL.md` — 成文开题报告(中文 DRAFT;锚定部分定稿,
    §4 操作化部分待重开完善)
  - `refine-logs/reviews/WALKTHROUGH_PASS1/pending_items.md` — 偏差 / 待处理项 + R-1…R-6 清单
  - `plans/worktable.md` — 当前阶段工作表(工作项 / 依赖 / 现在能动什么)
  - `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — 冻结 scope
    (名义权威;操作化细节在重开)
  - `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — 四层框架术语
  - `plans/phase7-pilot-implementation.md` — Phase 7 实施计划

## 项目结构
- `src/r5a/` — R5A 实验栈(契约、fleet、runtime、算子、后端、orchestration、analysis)
- `config/fleet/` `config/runtime/` `config/prompts/` — fleet / 运行 / prompt 配置
- `docs/` — 研究报告与 `DECISION_*` 决策备忘录
- `plans/` — 实施计划
- `refine-logs/reviews/` — 设计审阅记录
- `data/` — seed 数据、CLS 语料镜像、pilot 产物
- `related papers/` — 参考论文 PDF + 笔记
- `archive/` — Phase 0–5 转向前的历史文档(**非当前 spec**)

## 可用模型(16 模型 split-tier fleet)
- **12 白盒**(P_logprob-eligible,vLLM 部署):10 个 full-operator(5 Qwen2.5
  + 4 Qwen3 + 1 GLM)+ 2 个 P_logprob-only Llama。
- **4 黑盒**(API):DeepSeek V4 Pro / GPT-4.1 / GPT-5.1 / Claude Sonnet 4.6。
- 14 个 P_predict-eligible,12 个 P_logprob-eligible。详见 `config/fleet/r5a_fleet.yaml`。

## 约束
- conda 环境:rag_finance(Python 3.12)
- API key 在 .env 中,不要提交到 git
- 文档、代码注释、notebook markdown 用英文;**例外**:`docs/RESEARCH_PROPOSAL.md`
  为经用户批准的中文特例。用户对话用中文。

## Network / Proxy
- 本机使用代理;连接 DeepSeek API 和 vLLM 时需设置 NO_PROXY,或在
  httpx / requests 中显式 `proxy=None` / `trust_env=False`。

## 数据资源
- 财联社 CLS 电报语料 ~100 万+ 条;已镜像进本仓库 git-ignored 的
  `data/cls_telegraph_raw/`(源:`D:\GitRepos\Thales\datasets\cls_telegraph_raw`)。
- pilot N=780(80 pre-cutoff + 700 post-cutoff),main run N=2,560。

## Codex 调用
走 `/codex-run` skill(CLI `codex exec`)—— 见全局 `~/.claude/CLAUDE.md` 与
`~/.claude/commands/codex-run.md`。CLI exec 已取代 MCP sub-agent 作为默认。
分工沿用:Codex 重思考(方案设计 / 审阅 / 文献分析),Claude Code 轻执行
(写文件 / 改代码 / orchestration)。重审有争议的设计走 **clean-room-first**:
先白板独立分析得出结论,再对照既往 reviewer 意见。
