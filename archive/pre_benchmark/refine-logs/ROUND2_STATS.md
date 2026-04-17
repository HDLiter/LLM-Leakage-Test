我读完了 Challenger 报告，并回看了 proposal v2、prompt schema、counterfactual templates 和 benchmark 计划。总体判断是：Challenger 最有力的两击是 A 和 E；C 的前两段我基本认同，但"动摇整个 CF 设计基础"这句话过重；D 是真实的外部效度问题；B 不是严格意义上的 tautology，但当前叙事确实离这个攻击太近。

1. 攻击 A：我现在是"大体同意"。
我之前其实已经提到过"模板非同构"这个问题，但只把它当残余混淆；现在我认为应升级成主识别风险。[REVIEW_V2_STATS.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/REVIEW_V2_STATS.md#L5) 现在的 `direct_prediction` 确实依赖 `semantic_reversal`，`authority` 依赖 `provenance_swap`，[counterfactual_templates.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L70) [counterfactual_templates.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L104) 而 `CFLS` 又被直接解释成"更少 Type B dominance"。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L177) [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L191) 这会把"泄露"与"改写显著度/可读性/任务顺从性"混在一起。  
修补方案：先做 `50-100` 条 template-comparability pilot，逐模板报告 human label-change agreement、QC pass rate、changed-span 占比、edit distance 和 human inferability；再把一个与 `direct_prediction` 共用 `semantic_reversal` 的 evidence-grounded bridge task 提到主线，最自然的是把现有 `decomposed_impact` 接进同模板比较。[task_prompts.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L491) 如果做不到，这篇 paper 就不能把 `direct vs authority` 当成强机制识别，只能降格成 benchmark-specific descriptive contrast。  
补一句：这不意味着该回到旧 EI；我的看法是，`CFLS` 仍然比 EI 好，但它更像"必要积木"，还不是单独足够的 headline estimand。

2. 攻击 B：我"部分同意"。
如果主结论只是"问涨跌比问信源更容易被涨跌记忆污染"，那确实太显然，novelty 不够。尤其 proposal 现在的主成功标准只写成 `Delta_CFLS > 0`。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L68) 但我不同意把它说成严格 tautology，因为这不是定义上必然成立的命题；如果模型很服从上下文、记忆弱，gap 可以很小，甚至消失。  
修补方案：把主叙事从"方向"改成"程度与边界条件"。预注册最小有意义效应大小，不再把"正号"当主要贡献；同时要求主文必须回答两个更不显然的问题：evidence-grounded task 是否仍有非零 leakage，以及 false-outcome CPT 是否能跑出 clean sign-flip。

3. 攻击 C：我"部分同意，但分三段"。
短文本问题我同意，而且比 proposal 写得更严重。我抽看了原始 CLS 文件，文本确实很短；计划文档里代表文长度中位数也只有 `136` 字。[EXPERIMENT_PLAN.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/EXPERIMENT_PLAN.md#L179) 在这种语料上，局部改写很容易变成高占比改写，CFLS 会更像 rewrite-salience test。authority 可能也确实被模板化 cue 词抬得过高，因为 prompt 本身就在抽 source/provenance cue。[task_prompts.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L259)  
但我不同意"跨站重复动摇整个 counterfactual 设计基础"这个最强说法。proposal 从一开始就把对象定义成 event cluster 和记忆的 event-outcome trace，而不是 exact-document memorization。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L93) [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L129) 跨站重复会放大 Type B 暴露，不会直接摧毁 same-cluster paired design。真正有问题的是，现有 Stage 3 只 against CLS 做 nonexistence check，明显不够。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L151)  
修补方案：主分析必须预注册长度分层、changed-span 占比分层和 coverage/abstention 指标；authority 任务再加一个 rule-based cue baseline，检验它是不是只是模板匹配；Stage 3 扩到多站检索，至少加东财/新浪/公告库命中数，并把"nonexistence"改写成更老实的"未在检索源中发现近匹配"。

4. 攻击 D：我"部分同意"。
Qwen 7B 的 CPT 不能直接外推出 DeepSeek V3，这点是对的。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L170) [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L171) 但我不认为这会直接毁掉 paper，因为"开放模型上的因果锚 + 闭源部署模型上的行为三角验证"本来就是可接受组合。问题出在 claim 不能写得像"Qwen 解释了 DeepSeek"。  
修补方案：我会把我之前的 temporal 建议从 `A` 改成 `C`，即只在 Qwen 上做 boundary/local-window，DeepSeek 只做描述性模式，不做 stress-window equivalence claim。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L238) [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L244) 更进一步，如果资源允许，补一个轻量第二模型复现主 contrast，哪怕只是 `50-100` 条行为 replication，也会明显减轻这个攻击。

5. 攻击 E：我"同意"。
这是 Challenger 最准的一点。四位 reviewer 包括我自己，之前更关注识别和执行风险，低估了"即使实验成功，也可能只是一个做得很认真但不够新"的 reject 路径。当前 proposal 的 Findings 基线偏乐观。[RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L368)  
修补方案：把 pilot gate 写得更硬。没有通过以下三条，就不要急着扩到 `1000`：第一，cross-template comparability 过关；第二，evidence-grounded task 不是"零泄露天花板"，而是"显著更低但仍可失败"；第三，false-outcome arm 至少在小规模上有 clean sign-flip。做不到这三条，paper 就应主动收窄 claim 或降 venue 预期。

评分我会从 `8.0/10` 下调到 `7.5/10`。下调的核心原因不是方向错了，而是我之前低估了"跨模板可比性"和"limited novelty"这两个真正会被 reviewer 咬住的点。  
如果上述修补落实，分数可以回到 `8` 左右；如果不落实，Challenger 的 `7.4` 甚至更低，我认为都说得过去。
