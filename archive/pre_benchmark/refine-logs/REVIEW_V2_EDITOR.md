**总评**

我给这份 v2 开题报告 `8.1/10`。作为开题文本，它已经从"指标堆叠的测量草案"明显升级成一篇有清晰叙事中心的机制论文：主张是"task design gates memory pathway"，而不是"我又造了一个 leakage metric"。以可发表性看，我认为它已经进入"Findings of EMNLP 可认真推进"的区间，但离 main EMNLP 还差两件事：一是 scope 继续收窄，二是把"任务语义效应"严格降格为"prompt-task bundle effect under inferability control"。

**Strengths**

- 叙事结构比 v1 好很多。摘要、引言、RQ、理论框架、方法之间现在是同一条线，而不是多个实验并列拼接。
- "same article, different task" 是真正有方法论价值的 backbone。它比跨数据集、跨 benchmark 比较干净得多。
- 把 `cf_invariance - para_invariance` 降级、把 `CFLS` 升成主指标，是决定性改进。
- Type A / Type B taxonomy 是有用的。它让论文避免掉进"任何记忆都是 contamination"的粗糙表述。
- 风险部分写得诚实，说明作者已经意识到 matched-format collapse、false-outcome drift、temporal overclaim 这些最容易被 reviewers 打的点。
- 中文金融新闻这个 domain gap 是真实存在的，不是硬凹场景。

**Weaknesses**

- 最大未解问题仍然是 inferability / answerability confound。direct prediction 天生比 authority 更靠近 latent outcome，也更难仅凭文本稳定回答；如果没有足够强的人类 inferability 控制，RQ1 很容易被解释成"更 text-internal 的任务更稳定"，而不是"更不易泄露"。
- scope 仍然偏满。`CLS-Leak-1000 + DeepSeek base/matched/sham + Qwen Min-K + temporal + CPT + priming + utility` 对 10 周来说过重。v2 虽然口头上收敛了，但执行面还没真正收敛。
- CPT 的角色还不够稳定。文本里一方面说 main story 是 DeepSeek same-article comparison，另一方面 RQ2 和 abstract 又把 false-outcome CPT 放到近乎第二主线的位置。这会让论文重心摇摆。
- sham control 在 proposal 里被叙事性修复了，但在现有 prompt 资产里仍偏弱：`formality_level / numeric_density / sentence_complexity` 过于表层，抽象层级并不匹配 authority。
- benchmark gold 标注和 QC 仍然偏 LLM-assisted，尤其 rewrite validity 与 evidence grounding 还缺少更硬的人审定义。
- proposal 和现有代码有执行鸿沟。`src/metrics.py` 仍是 legacy EI 逻辑，且 label extraction 基本只对 direction 友好；`src/experiment.py` 仍走旧 runner，不是 proposal 里的 frozen prompt catalog 路线。
- `schema_validation.py` 主要验证 JSON shape，不验证 `target_echo`、quote 是否真在原文中、evidence 是否支持字段。这意味着 proposal 里很多"groundedness enforcement" 目前还是 paper promise，不是系统能力。

**对 9 个 [OPTION] 的建议**

- Inferability control: 选 `Option A`。这是最优风险收益比。`Option B` 更强，但会把标注负担推爆；`Option C` 不足以挡住"task difficulty, not leakage"。
- CFLS scoring: 选 `Option C`。主表用 "primary field + protected fields"，附录报 strict primary-only。透明且最符合 multi-slot 任务。
- Evidence intrusion: 选 `Option C`。主文用 narrow outcome-intrusion，四桶 taxonomy 放附录。主文要 precision-first。
- Temporal analysis: 选 `Option C`。Qwen boundary 可做描述性 local window；DeepSeek 不要再做准前沿 stress-window 等价检验。
- Core experiment scope: 选 `Option A`。主文只保留 `direct_prediction` vs `decomposed_authority`。`sentiment` 和 `novelty` 最多去 appendix。
- CPT design: 以当前 10 周 scope，我建议 `Option C`。保留 `(0,none),(1,none),(1,real),(1,false)` 这四格，换取可执行性。若坚持 `2x3`，就必须砍掉 RQ4 和 priming。
- Outcome block format: 选 `Option C`。只有 signed direction 太弱，带 rationale 又太像 distribution shift；direction + magnitude bucket 是更稳的折中。
- Utility study: 选 `Option C`。这不是论文 acceptability 的关键。真要留一点 finance relevance，也建议更偏 `A` 而不是 `B`。
- Venue: 选 `Option A`。Findings of EMNLP 是合理目标；main EMNLP 只有在 binary story 极干净且 CPT 结果异常漂亮时才值得冲。

**重要观察**

- 这篇论文最应该守住的 claim 是弱而准的版本：`outcome-proximal tasks are more contamination-prone on fixed historical inputs than evidence-grounded tasks`。不要把它写成"decomposition 证明能防 leakage"，那会招来不必要的反击。
- 我会强烈建议把"coverage / abstention"单独列成主诊断之一。`neutral` 和 `unclear` 不能只混在 CFLS 里；否则 reviewer 会质疑你是在测"可答性"而不是"泄露"。
- 如果 benchmark 质量开始吃紧，我宁可要 `CLS-Leak-500` 的高质量版，也不要 `1000` 的中等质量版。这个项目的瓶颈不是样本量，而是 counterfactual validity 和 adjudication rigor。
- 结论上，我支持立项，也支持继续写成论文。但投稿策略应是：先确保 `binary same-article result + inferability control + narrow evidence intrusion + one triangulation layer` 能独立成文，再决定 CPT 要不要升格成 headline。
