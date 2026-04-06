**总体判断**

读完 Challenger 报告后，我会下调我原来的判断。最有价值的新攻击有两个：一是把 `CFLS` 的构念效度问题往前推了一层，不只是 "inferability confound"，而是 "跨 task 的 counterfactual 干预本身不等价"；二是明确点出了 `limited novelty` 可能是比技术执行更大的 reject 风险。  
我现在的修正分数是 **`7.6/10`**，低于我原来的 `8.2/10`，但仍高于 Challenger 的 `7.4/10`，因为我仍认为 same-article paired design 是一个真实的强骨架，只是 claim 必须收窄、识别必须再补。

**逐条回应**

1. **攻击 A：CFLS 构念效度**
我现在是 **同意为主**。  
我之前只强调了 `CFLS` 是 "对可见文本改写的响应性 proxy"，但没有把"不同 task 用不同 CF 模板"单独升级成一级威胁；Challenger 这一点是对的。proposal 里 `CFLS` 的定义是 task-specific 的，[RESEARCH_PROPOSAL_v2.md#L178](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L178)，而 direct 与 authority 当前确实分别绑定 `semantic_reversal` 和 `provenance_swap`，[counterfactual_templates.yaml#L70](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L70)、[counterfactual_templates.yaml#L104](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L104)。这会把 edit salience、label discriminability、模型对改写的可察觉度一起混进 `Delta_CFLS`。  
但我不认为这会直接判死刑。它更像是把主结论从 "task semantics effect" 降格成 "prompt-task-template bundle effect"，除非你能补出更强的 comparability 证据。

修补方案：
- 把 "cross-template comparability" 变成 **pilot gate**，先在 50-100 条上量化每个模板的人类可判定性、edit ratio、IAA、通过率。
- 主文显式降格措辞：先报告 "direct-prompt bundle vs authority-prompt bundle"。
- 加一个 **同模板桥接任务**。最实际的是把 [task_prompts.yaml#L510](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L510) 的 `decomposed_impact` 拉进主实验，并给它配 `semantic_reversal`，这样至少能在同一 CF 干预下比较 "direct prediction vs evidence-grounded impact extraction"。
- 把按 edit distance / changed-span profile 分层的 sensitivity analysis 预注册成必做项。

2. **攻击 B：结论近乎 tautological**
我是 **部分同意**。  
"问涨跌比问信源更容易被涨跌记忆污染" 方向上确实直觉强，单靠方向本身不新。这一点我之前低估了。proposal 当前的主叙事也确实太容易被读成这个版本，[RESEARCH_PROPOSAL_v2.md#L68](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L68)、[RESEARCH_PROPOSAL_v2.md#L253](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L253)。  
但我不同意它是严格的 tautology。它不是定义上必真，因为模型完全可能在 direct task 上也老实跟文本走，或在 authority task 上大量把后验结果偷带进 evidence。真正非平凡的部分不在方向，而在 **幅度、边界条件、以及 false-outcome 下是否 sign-flip**。

修补方案：
- 把 contribution 改写成 "degree matters, not direction alone"。
- 预注册 effect-size 解释框架，而不是只盯显著性。
- 把 "authority 也会 leak，但更少、而且 leak 的形式可观测" 作为更优故事。
- 若 CPT 做不出 false-outcome arm，这篇的 novelty 会显著下降。

3. **攻击 C：CLS 电报体特殊性**
我是 **大体同意**。  
这条攻击很强，而且是中文财经语料特有的。proposal 自己就把语料锚定在 CLS telegraph，[RESEARCH_PROPOSAL_v2.md#L128](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L128)。我顺手对 [test_cases.json](/D:/GitRepos/LLM-Leakage-Test/data/seed/test_cases.json) 的 42 条 seed 做了快速统计，正文长度中位数只有 **95.5** 个汉字，四分位区间约 **92-101**。这意味着 Challenger 说的三个子问题都是真风险：

- 短文本下，所谓 "local rewrite" 很容易变成高比例重写。
- `authority` 在这种文体里可能退化成模板 cue matching，而不是真正的 grounded inference；对应 prompt 也确实更接近抽取任务，[task_prompts.yaml#L259](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L259)，而 direct prompt 是显式 outcome query，[task_prompts.yaml#L62](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L62)。
- 只 against CLS 做 nonexistence check 太弱，[RESEARCH_PROPOSAL_v2.md#L152](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L152)。在中文财经转载生态里，这不是小瑕疵。

但我不完全接受 "这动摇整个 counterfactual 设计基础"。跨站重复本身就是泄露风险的一部分，不是纯噪声。真正的问题是：它削弱了你把 rewrite uniqueness 当作 clean manipulation 的能力。

修补方案：
- 把 `coverage / abstention / unclear rate` 升为主诊断，不能只看 `CFLS`。
- 对超短文本设最小长度或最大 edit-ratio 门槛。
- 新增跨站近重复检索，至少覆盖东方财富、新浪财经、同花顺这类主要转载源；做不到就明说这是残余威胁。
- 宁可把 benchmark 缩到 `300-500`，也要换更硬的人审和 duplicate audit。

4. **攻击 D：Qwen 7B 到 DeepSeek V3 的外部效度**
我是 **部分同意，偏同意**。  
Challenger 说得对：如果论文把 Qwen 7B 上的 CPT 结果拿来"解释" DeepSeek 的内部机制，这会被打。proposal 当前的模型分工其实已经有点克制了，[RESEARCH_PROPOSAL_v2.md#L168](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L168)、[RESEARCH_PROPOSAL_v2.md#L273](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L273)，但还不够明确。  
我不同意把这点上升为致命缺陷。对 NLP reviewer 来说，"black-box behavioral result on deployment model + white-box causal plausibility on open model" 是可以接受的，只要 claim 不越线。

修补方案：
- 主文 claim 明确写成：`DeepSeek` 上观察到行为模式，`Qwen 7B` 上观察到一致方向的可控干预响应；后者是 causal anchor，不是 DeepSeek 的 mechanistic proof。
- 在做 CPT 之前，先把同一套 behavioral benchmark 跑一遍 Qwen；如果 Qwen 连 base phenomenon 都没有，CPT 解释链就断了。
- 资源允许的话，加一个第二 open model 做 replication，哪怕只是 behavioral replication。

5. **攻击 E："limited novelty" 被低估**
我是 **强烈同意**。  
这可能是 Challenger 最重要的 venue-level 提醒。我原来的 `8.2` 确实低估了这个 reject 风险。proposal 现在的危险在于：如果实验非常成功，反而可能产出一个 "执行很认真，但结论太顺理成章" 的结果。  
对 EMNLP/Findings 来说，真正有 punch 的不是 "proximal > grounded" 这个方向，而是下面几件事里至少命中一件：

- gap 的量级足够大，而且不是 template artifact；
- grounded task 也出现可解释的 residual leakage；
- leakage 不是二元开关，而有清晰 boundary condition；
- false-outcome CPT 给出干净 sign-flip。

修补方案：
- 把 paper story 从 "binary contrast" 改成 "mechanism + boundary conditions"。
- pilot 阶段优先看异常模式，不要只看主效应方向。
- 如果 authority 几乎完全免疫，我反而会警惕 artifact；如果它是 moderate leakage 但显著低于 direct，这通常是更好的论文故事。

**我会怎么改这份 proposal**

优先级上，我会做这 6 件事：

1. 先跑 `50-100` 条 pilot，不扩 benchmark，专门验证 CF 模板可比性。  
2. 把 `inferability + coverage + abstention` 一起升为主分析必报项。  
3. 增加一个同模板桥接任务，优先考虑 `decomposed_impact + semantic_reversal`。  
4. 把跨站 duplicate / syndication audit 纳入 QC，而不是只查 CLS。  
5. 把 Qwen 的 role 改写成 causal anchor，并补一个 Qwen behavioral replication。  
6. 把 false-outcome CPT 从 "可选增强" 提升成 novelty 核心件。

**修正评分**

我的修正分数是 **`7.6/10`**。  
下调的主要原因不是我改变了对方向价值的判断，而是我确认了两个我此前低估的风险：`CFLS` 的跨模板构念效度，以及 "即使实验成功也可能不够新" 的投稿风险。若上述修补做实，我会把它拉回 `8.0` 左右；若不修，这篇更像一篇会被 reviewer 说成 "careful but unsurprising" 的 Findings 边缘稿。
