# Cross-Model Challenger Report: RESEARCH_PROPOSAL_v2

> Reviewer: Claude Opus 4.6 (Cross-Model Challenger)
> Date: 2026-04-06
> Role: 独立第三方挑战性审阅，目标是找出 4 个 Codex agents 的群体盲点并 stress-test 最强共识

---

## 独立评分：7.4 / 10

比四位 Codex reviewers（8.0-8.2）低 0.6-0.8 分。理由在下文逐一展开。核心分歧不在于方向判断——我同意这个方向值得做——而在于我认为他们系统性低估了几个结构性风险。

---

## 一、群体盲点分析：4 个 Codex Agents 共同忽略了什么？

### 盲点 1：CFLS 的构念效度本身未被质疑——它可能在测 "rewrite quality" 而非 "leakage"

四位 reviewer 一致接受了 "CFLS 取代旧 EI 是正确升级" 这个前提，然后在此基础上讨论 inferability confound、protected fields、scoring 细节。但没有人退后一步问：**CFLS 本身到底在测什么？**

CFLS = 1 要求"模型在反事实改写后改变了主标签且 protected fields 保持一致"。但这个量的分母是什么？是 1000 个 benchmark 条目。分子依赖于：
- 改写本身是否足够改变文本语义（rewrite salience）
- 改写后的文本是否对人类标注者也足以改变标签（rewrite validity）
- 模型是否有能力正确解读改写后的文本（model reading comprehension）
- 模型是否因为没记住这条新闻而 "诚实地" 跟着文本走（non-memorization）

只有最后一项是 proposal 想测的。前三项都是噪声源。更关键的是，**不同 task family 的反事实改写模板完全不同**：direct_prediction 用 `semantic_reversal`（翻转经济含义），authority 用 `provenance_swap`（调换信源属性）。这两种改写的 salience、认知难度、执行质量天然不同。一个"翻转股价方向"的改写和一个"把官方通知改成市场传闻"的改写，在 edit magnitude、label discriminability、人类 inter-annotator agreement 上可能根本不可比。

**这意味着 Delta_CFLS 可能部分是在测"哪种改写更容易被模型察觉"，而不是"哪种 task 更少泄露"。** 这是一个比 inferability confound 更底层的构念效度问题。四位 reviewer 都没有提到这一点。

### 盲点 2：中文 CLS 电报体的特殊性被严重低估

四位 reviewer 几乎没有讨论中文财经电报体（CLS telegraph style）对实验设计的特殊影响。CLS 电报的典型特征是：
- 极短（通常 50-200 字）
- 高度模板化（"XXX 公司公告 YYY"、"据悉 ZZZ"）
- 同一事件大量近似重复

这带来几个被忽略的问题：

(a) **短文本的 CFLS 信噪比极差。** 一篇 80 字的电报做 semantic reversal，可能只改动 10-20 个字，但这 10-20 个字占全文 15-25%。这不是"局部改写"，而是接近全文重写。proposal 继承了 v1 讨论中对 edit-magnitude asymmetry 的警觉，但没有在 CLS 短文本场景下重新评估这个问题。

(b) **模板化意味着 authority 任务可能天然更容易。** CLS 电报的信源标注模式非常固定（"据 XXX 消息"、"公告显示"、"市场传闻"），模型做 authority extraction 时可能只是在做简单的模板匹配，而不是真正的 evidence-grounded inference。如果 authority 任务本质上更容易，那它的 CFLS 更高不能归因于"更少泄露"，而可能只是"更容易做对"。

(c) **大量近似重复使得 "nonexistence check" 几乎无意义。** 一条 CLS 电报的核心信息可能被 10-50 家媒体转载（文字略有不同）。只 against CLS corpus 做去重远远不够。NLP reviewer 提到了跨站近重复问题，但没有人指出这实际上动摇了整个 counterfactual 设计的基础：如果模型在训练中见过同一事件的 50 个版本，你改写其中一个版本的措辞，模型完全可以从其他 49 个版本中恢复信息。

### 盲点 3：instruction-following compliance 被当成透明的

所有 prompt 都要求模型 "Do not use outside knowledge, hindsight, later market outcomes"。但这个指令本身就是一个未被测试的假设。现有研究（Zhou et al. 2023, Li et al. 2024）已经表明，instruction-following 的有效性取决于记忆强度和 evidence style 的交互。**如果模型对某条新闻的后续结果有强烈记忆，一条 system prompt 指令不太可能真正阻止这个信息影响输出。**

更重要的是，不同 task 的 instruction compliance 可能不同。一个 "predict direction" 的指令更容易被记忆 override（因为答案空间和记忆空间重合），而一个 "extract source credibility" 的指令更不容易被 override（因为答案空间和后续价格记忆不重合）。**这正是 proposal 的核心主张，但它同时意味着 CFLS 差异可能部分来自 instruction compliance 差异，而不是 memory pathway 差异。** 这两者在当前设计中无法区分。

### 盲点 4：没有 reviewer 质疑 Qwen 2.5 7B 作为 causal anchor 的外部效度

四位 reviewer 讨论了 CPT 的工程可行性、factorial design、false-outcome arm 等细节。但没有人质疑：**在 7B 参数量的 Qwen 上观察到的 task-gated memory effect，能外推到 DeepSeek V3（据传 671B MoE）上吗？**

这不是一个小问题。7B 模型和 100B+ 模型在记忆机制、context window 利用、instruction following 能力上可能有质的差异。如果 CPT 实验在 Qwen 7B 上成功了，审稿人完全可以说："你的 causal evidence 来自一个完全不同规模的模型，不能用来解释 DeepSeek 上的 behavioral evidence。"

---

## 二、最强共识挑战：哪些 4/4 一致的判断站不住脚？

### 共识 1："same-article, different-task 是全篇最强的设计骨架"（4/4）

**挑战：** 这个设计的识别力被高估了。

"Same article" 确实控制了文本内容。但 "different task" 引入了太多同时变化的维度：
- 不同的 output schema（direction vs. source_credibility/regulatory_vs_rumor/official_vs_unattributed）
- 不同的 label cardinality（3-class vs. 4-class vs. 5-class）
- 不同的 cognitive demand（预测 vs. 抽取）
- 不同的 counterfactual template（semantic_reversal vs. provenance_swap）
- 不同的 "unclear" 的含义和基率

matched-format control 试图解决 output schema 差异，但它只匹配了 slot count 和 evidence burden，不能匹配 label cardinality、cognitive demand、counterfactual template 类型。**当这么多东西同时变化时，把 CFLS 差异归因于 "task design gates memory pathway" 是一个很强的因果声明，需要比当前设计更强的识别策略。**

一个更干净的设计是：在同一个 output schema 和同一个 counterfactual template 下，只变化 "任务指令是否 outcome-proximal"。但 proposal 的 task family 设计不支持这种精细拆分。

### 共识 2："Findings of EMNLP 是合理目标"（4/4）

**挑战：** 这个判断可能过于乐观。

让我以一个真实的 EMNLP reviewer 的视角来看：这篇论文的核心发现——"outcome-proximal tasks show lower counterfactual sensitivity"——对有经验的 NLP 研究者来说可能是**直觉上显而易见的**。当然你问模型"股价会涨还是跌"它更可能用记忆回答，而问它"这篇文章的信源是官方还是传闻"它更可能看文本。这几乎是 tautological 的：outcome-proximal 的定义就是"答案和后续结果高度相关"，那当然更容易被后续结果的记忆污染。

一个挑剔的 reviewer 会问："这个结果有什么 non-obvious 的 insight？你需要 1000 条 benchmark、counterfactual rewrites、CPT experiment 来证明一个定义上就成立的东西吗？"

要避免这个攻击，proposal 需要更强调 **quantitative surprise**：不是"我们证明了 outcome-proximal tasks 更脆弱"，而是"脆弱的程度有多大？在什么条件下 evidence-grounded tasks 也会失败？阈值在哪里？" 目前 proposal 的叙事过于定性。

### 共识 3："用 CFLS 取代旧 EI 是正确决定"（4/4）

**挑战：** 放弃 EI 的理由成立，但 CFLS 继承了 EI 的一个核心问题而无人指出。

旧 EI = cf_invariance - para_invariance 被放弃的原因是"CF edits 和 paraphrase 的 edit magnitude 不匹配"。这个判断正确。但 CFLS 把 paraphrase subtraction 完全去掉了，变成了 **absolute responsiveness**。问题是：一个对任何文本变化都高度敏感的模型（比如一个非常 "听话" 但没有记忆的模型），在所有任务上都会有高 CFLS。一个对文本变化不敏感的模型（比如一个倾向于给出默认答案的模型），在所有任务上都会有低 CFLS。

**CFLS 的 cross-task 差异要排除的不仅是 inferability，还要排除 task-specific prompt sensitivity（模型对不同 prompt 的 "听话程度" 不同）。** 一个模型可能对 "predict direction" 的 prompt 更加 "自信"（更不愿意改答案），而对 "extract authority" 的 prompt 更加 "顺从"（更愿意随文本变化改答案）。这和 memory pathway 无关，和 prompt-induced response style 有关。Sham control 能部分缓解这个问题，但 sham 的 label 空间（formality/numeric_density/sentence_complexity）和 authority 的 label 空间太不同，无法做 apples-to-apples 比较。

---

## 三、刻薄 Reviewer 攻击清单：最可能导致 Reject 的理由

### 攻击 1：结论近乎 Tautological

"Outcome-proximal tasks are more vulnerable to outcome memory contamination than evidence-grounded tasks."

用白话说就是："问股价涨跌的 prompt 比问信源可靠性的 prompt 更容易受到股价记忆的污染。" 这几乎是定义上成立的。模型记住了后续涨跌，当你问涨跌时它当然更可能用到这个记忆；当你问别的东西时它用到这个记忆的机会当然更少。

**Defense 建议：** 转向 "degree matters more than direction"。核心 contribution 不是证明方向，而是量化 gap 的大小，并证明即使在 evidence-grounded tasks 中，evidence intrusion 仍然以特定模式存在。

### 攻击 2：Counterfactual 不等价，Delta_CFLS 不可解释

Direct prediction 用 `semantic_reversal`（翻转事件经济含义）。Authority 用 `provenance_swap`（调换信源属性）。这两种改写在以下维度上不可比：
- 认知显著性（翻转经济含义比调换信源更 salient）
- 执行难度（semantic reversal 需要改更多文本）
- 人类 baseline agreement
- 改写的 self-evidence（读者是否容易察觉这是改写）

因此 Delta_CFLS 混入了 "counterfactual template effect"。**你不能比较两个不同治疗下的 response rate 来得出关于 underlying condition 的结论，除非你能证明两种治疗的 dose-response curve 可比。**

### 攻击 3：单一模型 + 单一语言 + 单一语料来源 = 无法泛化

全部 behavioral evidence 来自 DeepSeek-chat（一个模型）在 CLS 电报（一个语料来源）上的中文（一种语言）表现。Causal evidence 来自 Qwen 7B（另一个不同规模的模型）。没有任何英文实验、没有任何其他中文财经语料（东方财富、新浪财经）、没有任何其他模型（GPT-4、Claude、Llama）。

对于一篇声称发现了 "task design gates memory pathway" 这种通用机制的论文，这个证据基础太窄了。

**Defense 建议：** 要么缩小 claim scope（"in DeepSeek-chat on CLS telegraph news, ..."），要么增加至少一个对比模型。

### 攻击 4：CPT Anchor 的内外部效度同时可疑

- **内部效度：** Low-dose CPT 是否真的只注入了 "outcome memory" 而没有改变其他能力？proposal 自己承认了 capability drift 风险（Risk 2）。如果 CPT 同时改变了 instruction following 能力，那 task-gated effect 可能反映的是 "CPT 破坏了 authority 任务的 instruction following" 而不是 "outcome memory selectively affects direct prediction"。
- **外部效度：** Qwen 7B 上的 CPT 结果能否推广到 DeepSeek？模型规模差 ~100x。完全不同的训练数据、架构、对齐方式。

### 攻击 5：Benchmark Artifact + 研究者自由度

CLS-Leak-1000 的 sampling、clustering、rewrite generation、QC 全部由研究者控制。Counterfactual rewrite 由 LLM 生成、由研究者 QC。Gold labels 由 LLM 辅助标注。这个 pipeline 中有大量的研究者自由度（researcher degrees of freedom），尤其是：
- 哪些 cluster 被排除（"Cases that cannot be resolved to a single target quickly are excluded"）
- 哪些改写通过 QC
- Tier 2 的 spot-check 覆盖率
- Post-stratification weights 的选择

没有 pre-registration、没有独立审计、没有 hold-out benchmark。

---

## 四、分歧点的第三方裁决

### Core Narrative: Option A vs Option B

- Quant: B（binary primary + sentiment bridge）
- NLP: A（binary only）
- Stats: A
- Editor: A

**裁决：选 A。** 理由：sentiment 和 direct prediction 的 label space 高度重叠（positive/negative/neutral vs. up/down/neutral），作为 "bridge" 它不提供新信息。保留它只会增加 multiple testing 负担并模糊主线。更重要的是，sentiment 作为 bridge 暗示了一个从 "most outcome-proximal" 到 "least outcome-proximal" 的连续谱。但 proposal 的机制框架是 binary（Type B pathway on/off），不是连续的。保留 sentiment 会破坏这个叙事一致性。

### Temporal: Option A vs Option C

- Quant: A（Qwen boundary + DeepSeek stress）
- NLP: C（Qwen only）
- Stats: A
- Editor: C

**裁决：选 C。** 理由：DeepSeek 的 "false-positive stress test" 在逻辑上没问题，但在实操中非常危险。如果 stress test 的结果不符合预期（比如 2026 年的 fresh slice 也显示出 "leakage"），研究者面临两个选择：(1) 承认 CFLS 测到的不是 leakage，或 (2) 给出 ad hoc 解释（"DeepSeek 可能在 2026 年初又更新了训练数据"）。无论哪种，都削弱论文。选 C 更安全：Qwen boundary 是描述性的，没有承诺；DeepSeek 只做 temporal patterns 描述，不做任何 boundary-based 检验。

### Utility: Option B vs Option C

- Quant: B（light financial diagnostic，company-only）
- NLP: C（appendix-only）
- Stats: B（附条件）
- Editor: C

**裁决：选 C。** 理由：这篇论文的 target venue 是 EMNLP，不是 JFE/RFS。Financial utility 对 NLP reviewer 没有说服力（他们不懂 rank IC / ICIR），对 finance reviewer 又太轻量（没有 transaction cost、市场微结构、multi-factor alpha decomposition）。两头不讨好。把这部分挪到附录或后续工作，集中火力打磨 behavioral + causal evidence。

---

## 五、最被低估的风险

**我认为 proposal 最被低估的风险是：整个研究可能产出一个 well-executed but unsurprising result，最终被 reviewer 以 "limited novelty" reject。**

四位 Codex reviewer 都没有直面这个风险。他们讨论了 inferability confound、matched-format collapse、CPT capability drift 等技术风险，但这些都是"假如实验失败怎么办"的问题。更根本的风险是：**假如实验成功了，结果足够新颖吗？**

"Outcome-proximal tasks are more vulnerable to memorization" 在直觉上对任何做过 LLM evaluation 的人来说都是显然的。这篇论文的真正价值不在于验证这个方向，而在于：
1. 量化 gap 的大小（如果 gap 很小，论文没有 punch）
2. 证明 evidence-grounded tasks 并非免疫（如果它们完全免疫，故事太简单）
3. 找到 surprising failure modes（比如 authority task 在特定条件下也大量 leak）
4. CPT false-outcome 实验产出清晰的 causal sign-flip

如果 (1) gap 很大、(2) authority 几乎不 leak、(3) 没有 surprising patterns、(4) CPT 只做了 real-outcome，那最终论文会被评价为 "a careful but unsurprising measurement study"。这种论文在 EMNLP Findings 也不一定能过。

**应对建议：** 在 pilot 阶段就密切关注 effect size 和异常模式。如果 pilot 显示 gap 很大且 clean，反而要警觉——可能是 artifact。如果 pilot 显示 authority task 也有 moderate leakage（只是比 direct prediction 少），这其实是更好的故事（"decomposition reduces but does not eliminate"）。重点把叙事从 "binary direction" 转向 "mechanism + boundary conditions"。

---

## 六、补充观察

### 关于 Type B2（task-template memory）

NLP reviewer 建议 "少写、别让它承担核心论证"，我完全同意。但我要指出更深层的问题：Type B2 的定义（"stored answer patterns cued by outcome-proximal prompt scaffolds"）在概念上和 Type A2（entity familiarity）之间没有清晰边界。如果模型因为见过大量 "XXX 公司利好 → up" 的训练样本而学会了 "policy + major company → bullish" 的规律，这是 B2（task-template memory）还是 A1（structural prior）？proposal 给不出可操作的区分。

### 关于 sham control 的根本局限

sham decomposition（formality / numeric_density / sentence_complexity）被设计为 "经济无关的结构化抽取"。但问题是，如果 sham 和 authority 的 CFLS 差不多高，proposal 的解释是 "structured extraction itself reduces leakage"。如果 sham 的 CFLS 低于 authority，proposal 的解释是 "meaningful decomposition matters"。**无论结果如何，proposal 都有一个现成的叙事。这是 heads-I-win-tails-you-lose 的设计。** 一个更严格的 sham 应该是："在相同的 output schema 和 label cardinality 下，要求模型做一个和后续结果不相关但和 authority 相同认知层级的任务"。但这样的 sham 可能不存在。

### 关于代码-论文鸿沟

四位 reviewer 都提到了代码和 proposal 之间的 gap。但我想强调的不同角度是：这个 gap 意味着 **proposal 中所有关于 CFLS scoring、evidence intrusion scoring、protected field checking 的设计都是 paper promises，还没有经过任何 empirical reality check。** 一个看起来优雅的 scoring scheme 在实际数据上可能因为 parse failure、label ambiguity、edge case 而崩溃。在没有跑过一轮 pilot 验证 scoring pipeline 之前，对 scoring 细节做过多设计是 premature optimization。

---

## 七、总结

这是一份有明确方向、清晰框架、合理抱负的开题报告。11 轮多 agent 辩论确实显著改善了它的质量。但 4 个 Codex agents 的审阅存在明显的模型同源偏差：他们集体对 CFLS 构念效度不加质疑、对中文电报体的特殊挑战缺乏实感、对 "directional novelty" 的风险估计不足、对 cross-model generalizability 缺乏关注。

论文能否成功，取决于三个目前无法从 proposal 中判断的 empirical 问题：
1. CFLS 在不同 counterfactual template 下是否有合理的 cross-task 可比性
2. Effect size 是否既足够大以有 practical significance，又不至于大到 trivially obvious
3. CPT false-outcome 是否能跑出 clean 的 task-gated sign-flip

如果这三个问题的答案都是 yes，这篇论文有 Findings of EMNLP 的机会。如果任何一个是 no，当前设计没有足够的 contingency plan。

**最终建议：** 在 pilot 阶段（前 50-100 条）优先验证 CFLS 的 cross-task comparability 和 effect size，而不是急于把 benchmark 扩到 1000 条。如果 pilot 显示 CFLS 差异主要来自 counterfactual template 效应而非 memory pathway 效应，整个论文的识别策略需要根本性调整。这比任何 scope 调整、scoring 细节、或 venue 选择都重要。
