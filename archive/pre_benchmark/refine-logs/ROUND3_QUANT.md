通读 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md)、[DISCUSSION_LOG_20260406.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/DISCUSSION_LOG_20260406.md)、[EXPLORE_TEMPORAL_DIRECTIONALITY.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/EXPLORE_TEMPORAL_DIRECTIONALITY.md) 和四份 memory taxonomy 后，我的核心判断是：v2 不是"小修小补"能稳住的阶段了，但也没有必要推倒重来。真正要改的是研究对象的定义和识别结构，而不是只改几个 metric 名称。

1. Type A/B 不应再做主 taxonomy，只应保留为"功能性 shorthand"。  
现在的二分法把三件事混在了一起：信息是否在 `τ` 时点可容许、记忆的对象到底是什么、以及任务是否让这类记忆能直接回答。更稳的主框架应是三轴：`temporal admissibility`（能否由 `C≤τ` 恢复）、`memory carrier`（article overlap / event-outcome / entity prior / regime prior / provenance-template）、`path role`（辅助 grounding 还是替代 article 直接给答案）。Type A/B 仍然可以留在文中，但降级为第三轴上的"有益辅助"与"答案捷径"，不再承担整个理论框架。

2. Entity prior 应升格为独立测试维度，但不要把它全部直接叫"泄露"。  
文献和你们自己的检索都指向同一件事：金融场景里，实体名触发的先验很可能比 exact article memorization 更常见，也更像真实主通道。问题在于，entity prior 有一部分是合法背景知识，有一部分是 evaluation-invalidating shortcut，所以它不适合继续埋在 `Type A2` 里。实验上我会把它单列成一条 dependence channel：必须加入 `entity masking / alias normalization / neighbor-entity substitution`，并按 `company/sector/index`、head-tail prominence、传播度分层；同时把 Qwen familiarity 做成 `原文 vs entity-masked vs deep rewrite` 的对照，而不是一个静态 Min-K 分数。

3. CFLS 的根本问题不是"算得不够好"，而是它被赋予了超出承载能力的解释。  
结合 [counterfactual_templates.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml) 和 [task_prompts.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml) 看，`direct_prediction` 和 `authority` 现在依赖不同 counterfactual family；所以跨任务 `Delta_CFLS` 既在测 leakage，也在测 rewrite salience、任务顺从性、模板 detectability。根本解法不是单选"统一模板"或"加 bridge task"，而是重构识别逻辑：把 CFLS 明确降格为 `within-template article-responsiveness metric`；把同模板 bridge task `decomposed_impact` 提到主线，用它和 `direct_prediction` 做主比较；把 `authority` 改成高精度 intrusion probe，而不是唯一主对照。换句话说，桥接任务是必要条件，但真正的解决方案是"不再让一个跨模板 Delta_CFLS 承担整篇论文的 headline claim"。

4. "泄露"的正式定义应该改成 `dependence on information not recoverable from C≤τ`。  
这是 [EXPLORE_TEMPORAL_DIRECTIONALITY.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/EXPLORE_TEMPORAL_DIRECTIONALITY.md) 里最重要、也最应该进入主文的升级。它比 "look-ahead leakage" 更严格，因为它把 `retrospective contamination`、hindsight narrative 和 post-τ 回溯学习都纳入同一框架；同时也避免把一切背景知识都误判为坏事。叙事上我建议保留 "look-ahead leakage" 这个读者友好的词，但正文定义改写为：`look-ahead leakage is one operational subtype of point-in-time inadmissible dependence`。这样你们的论文会从"未来记忆污染"升级成"point-in-time recoverability 下的外部依赖识别"，理论上更强。

5. 这些变化会让论文更强，但前提是 scope 要收窄，而不是继续加东西。  
更强之处在于：论文不再只是证明一个方向上"几乎显然"的结论，而是提出一个更可防御的识别框架，区分 `article-responsiveness`、`entity-prior dependence`、`temporally inadmissible dependence` 三类对象。更弱的风险只会出现在你们试图同时保留四个 task family、utility 分析、sham、novelty、full taxonomy、CPT 全套时，那会变成 sprawling but underidentified。我的建议是把主文压缩成四件事：`PIT recoverability 定义`、`same-template 主比较`、`entity prior 独立 probe`、`false-outcome CPT + evidence intrusion`；sentiment、novelty、utility 都降到附录。这样投稿上仍以 Findings of EMNLP / ACL 为合理基线；只有在加上第二模型轻量复现且 false-outcome sign-flip 很干净时，才值得再看 main-track。

一句话总结：不是把 Type A/B 改成"更多类型"就够了，而是要把论文从"任务设计开启 Type B"改写成"任务设计改变模型对多种 extra-textual dependence channel 的暴露，其中只有一部分是 point-in-time 不可容许的"。这会让理论更硬、实验更可识别、也更像一篇 reviewer 很难轻易挑成 tautology 的论文。
