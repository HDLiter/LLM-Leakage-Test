**评分**
`8.2/10`。独立读完 proposal，并抽查了前序讨论摘要与现有 prompts / metrics 实现后，我的判断是：这已经接近一篇可 defend 的 EMNLP Findings 级机制型评测论文，但还没有到 main-track 的稳固程度。最大短板不在"创意"，而在"识别是否真的把 task pathway 和 text inferability 拆开了"。

**主要问题**
- 最核心的识别威胁仍是 `task pathway` 与 `article-only inferability` 混淆。direct prediction 天然更接近欠定任务，authority 天然更接近文本内可判任务；如果 inferability 只是可选项，RQ1 很容易被改写成"更 text-internal 的任务更稳定"，而不是"更少 Type B leakage"。见 [docs/RESEARCH_PROPOSAL_v2.md#L158](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L158) 和 [docs/RESEARCH_PROPOSAL_v2.md#L177](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L177)。
- `CFLS` 是"对可见文本改写的响应性"指标，不是泄露本身的直接测量。把它解释成 "less Type B dominance" 是合理 proxy，但若没有强 inferability control、narrow evidence intrusion、以及 false-outcome CPT anchor，它仍可能吸收任务难度、标签熵、rewrite 可判性差异。
- benchmark QC 仍偏 LLM-mediated，且去重/不存在性检查只 against CLS corpus。中文财经新闻高度转载，跨站近重复和后续摘要很常见；只查 CLS 会让"其实在别处广泛出现过"的 rewrite/事件漏过去。见 [docs/RESEARCH_PROPOSAL_v2.md#L149](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L149)。
- 统计 protocol 的主回归写得过于"一锅端"。把 `Prox_t`、`Matched_t`、`Sham_t` 放进同一个泛化 mixed model，不如直接把预注册 paired cluster contrasts 作为主分析，mixed model 只做 sensitivity。见 [docs/RESEARCH_PROPOSAL_v2.md#L335](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L335)。
- proposal 与当前实现之间还有明显落差。`metrics.py` 仍围绕旧 EI 和 label/confidence fallback，`experiment.py` 仍是 legacy masking runner，schema validator 只校验结构/enum，不校验 `target_echo`、evidence 是否真在文中、以及 protected fields。见 [src/metrics.py#L178](/D:/GitRepos/LLM-Leakage-Test/src/metrics.py#L178)、[src/experiment.py#L71](/D:/GitRepos/LLM-Leakage-Test/src/experiment.py#L71)、[config/prompts/schema_validation.py#L136](/D:/GitRepos/LLM-Leakage-Test/config/prompts/schema_validation.py#L136)。

**优点**
- 从 v1 的"指标论文"收缩到 v2 的"机制论文"是正确升级，`Type A / Type B` 框架也基本有用。
- `same (article, target), different task` 是全篇最强设计骨架，明显优于跨 benchmark 比较。
- 把旧 `cf_invariance - para_invariance` 降级、改用 `CFLS + evidence intrusion + Min-K/temporal triangulation`，方向是对的。
- DeepSeek 的时间边界不再被过度包装成 cutoff，而被降为 false-positive stress window，这个克制很重要。见 [docs/RESEARCH_PROPOSAL_v2.md#L170](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L170)。
- "clean features 不必更强，但 contaminated features 更不可靠" 这个 finance takeaway 很聪明，也更容易被审稿人接受。

**[OPTION] 建议**
- Inferability control: 实务上选 `A`。科学上 `B` 最强，但若不愿同步缩 benchmark，大概率拖垮进度；`C` 不建议。
- CFLS scoring: 选 `C`。主表用 primary+protected fields，附录给 strict primary-only。
- Evidence intrusion: 选 `C`。主文 precision-first，appendix 再给四桶 audit。
- Temporal analysis: 选 `C`。保留 Qwen boundary 的描述性 local window，DeepSeek 不要再做任何"近似 frontier"式等价表述。
- Core experiment story: 选 `A`。主文只讲 `direct_prediction vs decomposed_authority`，sentiment/novelty 都降级。
- CPT design: 选 `C`。false-outcome arm 必须保留，但没必要硬上完整 `2 x 3` 六格。
- Outcome block format: 选 `C`。只注入方向+幅度 bucket，不加 rationale，避免把 outcome memory 和 explanation-style confound 混在一起。
- Utility experiment: 选 `C`。这是最容易把论文拖进 finance backtest 泥潭的部分，除非核心结果非常顺。
- Venue: 选 `A`。Findings of EMNLP 是合理基线；main EMNLP 目前仍差一层识别与执行完成度。

**重要观察**
- `Type B2 task-template memory` 在理论上有启发，但目前没有被单独 operationalize；建议少写、别让它承担核心论证。
- 如果 Tier1 inferability 标注后发现 proxy 外推效果差，不要退回 `OPTION C`，而应该直接缩 benchmark。
- 如果 CPT 工程进度不顺，论文仍可凭 "binary same-article contrast + matched/sham + narrow intrusion + limited temporal" 成立；但若没有 inferability control，整篇会显著降级。

**结论**
这份 v2 已经是"值得做、也有发表机会"的 proposal。我的独立判断是：只要把 inferability 从"可选增强"提升为"识别必需品"，把统计主分析收缩为预注册 paired contrasts，并尽快把 repo 从旧 EI/legacy runner 迁移到 v2 scoring 逻辑，这篇文章就有比较扎实的 Findings 水准。反过来，如果 inferability control 弱、CPT 没有 false-outcome、同时又保留过多次级实验，审稿人很容易把它打回"更 text-internal 的任务更容易被 prompt 约束"而不是"task design gates look-ahead memory"。