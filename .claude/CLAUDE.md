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
  模型预测、无记忆基线、会聚效度、
  confirmatory / exploratory、Type A 闸门、manipulation check 等。
- **宁可话长,也别让用户解码。术语密度过高 = 把沟通成本转嫁给用户。**
- 适用范围:所有**面向用户**的交流。
- **内部文档可读性规则**(docs/、refine-logs/、代码注释):可以用已建立的
  缩写/代号,但**必须注重可读性**——① 术语在每份文档首次出现时必须有解释;
  ② 不能在文档里凭空造对话中没出现过的新缩写(术语先在对话中建立共识);
  ③ 缩写和真实含义之间必须能看出联系,否则换名。

## ⭐ 文档卫生:正文不留审计 log / SUPERSEDED 标记,历史交给 git(2026-06-07 用户硬性要求)
活跃文档(`docs/`、`plans/`、`config/`、根目录索引、以及被下游当"现行真相"读的
`refine-logs/` 文件)**只写当前状态**,不要在正文里留"改动史 / 版本史"。

为什么(用户三条理由):
- **浪费上下文**——机械改动常留下几倍于正文的修订记录;
- **误导后续 agent**——agent 靠 search / grep 读文档,grep 命中正文却看不到上方
  那句"本段已被 X SUPERSEDED",把废文当现行;
- **抬高改动成本**——一处事实变化要同步好多处"谁取代谁"的引用。
历史在 git 里全都有,不必在正文里重抄一遍。

禁止(在活跃文档里):
1. **正文内 SUPERSEDED / 更正横幅**("本段已被…取代,见下""partly superseded by
   0427+0429")——直接把正文改写成现状,或整份移进 `archive/`;要指向后继文档
   只留**一行**指针,别复述被改掉的旧内容。
2. **版本阶梯 / changelog**——frontmatter 的 `supersedes:` / `superseded-by:` /
   `amendments[]`、正文 `## Changelog` 段、"v3 在 v2 基础上砍了…"式标题、"本次
   commit 改了哪些文件"清单。状态只留一行。
3. **行内 diff 注记**——"(2026-05-xx 新增)""原本写 X""原计划 X 后改 Y"——只留当前事实。
4. **跨文档照抄**另一份文档的 changelog / 推理过程——只留一行指针。
5. **把删掉的旧行 ~~划掉~~ 留在新行旁边**——直接删,别并排留。

例外 / 不算 cruft:
- 冻结的 `DECISION_YYYYMMDD_*.md` 决策备忘录按"当时拍的值"**原样保留**(它本就是
  时间切片的历史记录);后续变化写进**新的**决策文档,不回头改老备忘录,也不在
  老备忘录顶上贴 SUPERSEDED 横幅。
- **简短的现状面包屑**可留:给当前结论打个带日期的状态标(如
  「[R-6 ✔ 2026-06-06] C_FO 已删」)、引用源论文出处、指向 canonical 后继文档的
  一行指针。判据:这段史料性文字是否"不成比例"(多行 / 重复 / 在叙述被取代的旧
  状态)——是就删,只是一句现状面包屑就留。

**过程审计轨迹归 archive**:每个 R-X / 评审 session 产出两类东西——**喂决策的推理
过程**(whiteboard / `*_lens` / stress-test / second-opinion / synthesis / 证据扫描)
是历史,放 `archive/`,不是当前真相;**干净的结论** `*_DECISIONS.md`(< 200 行)留在
`refine-logs/` 当 canonical。搬运前**先把所有指向它的活跃引用 repoint,再 `git mv`,
再 re-grep 确认无悬空链接**(很多轨迹文件被 live 源码 / 测试 / 签字备忘录按路径引用,
盲搬会断链)。

**底线**:清理后**只读活跃区就能拼出研究的完整现状**(提案 + worktable +
pending_items + 各 `*_DECISIONS` + 四层框架 + 候选池索引)。归档某份轨迹**之前**,
它承载的当前结论必须已落在某份活跃 canonical 文档里;若某条现行事实只此一份,
先把结论迁进活跃文档再归档,不能让活跃区出现缺口。

一句话:活跃文档说 **"现在是什么"**;git 和 `archive/` 说 **"怎么变成这样的"**。

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
