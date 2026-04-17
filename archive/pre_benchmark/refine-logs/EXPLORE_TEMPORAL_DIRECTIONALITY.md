PI 提的问题是对的：你们现在的 `Type A / Type B` 框架抓住了"功能路径"，但还没把"时间可容许性"单独抽出来。更严格的对象不是"模型是否记住了过去/未来"，而是：

`在评估时点 τ，模型是否依赖了在 τ 时点不可获得的信息来作答。`

**概念框架**
- 我建议把 taxonomy 改成三轴，而不是让 `Type A / Type B` 一轴包打天下。
- 第一轴是 `exposure time`：模型是从什么日期发布的语料学到这条知识的。
- 第二轴是 `reference time`：这条知识在谈哪个时期的事件。
- 第三轴是 `path role`：这条记忆是在辅助 grounding，还是在替代 article 直接给答案。
- 对 cutoff `τ`，令 `M<=τ` 为由 `τ` 之前可得语料形成的记忆，`M>τ` 为 `τ` 之后才可能形成的记忆。严格的 look-ahead leakage 是：在固定文章 `X` 和 `M<=τ` 时，输出仍因 `M>τ` 改变。
- 这意味着 `backward / forward` 是时间轴，`Type A / Type B` 更适合作为功能轴。
- `Type A` 不等于 backward。某些 pre-τ 的 entity/regime prior 完全可能造成 anchoring，它们不是 look-ahead leakage，但仍是有害 shortcut。
- `Type B` 也不等于 forward。task-template memory、exact-article overlap、pre-τ 的强标签先验，都可能是 evaluation-invalidating shortcut，但不一定含未来信息。
- 最关键的一点是：合法性取决于 `exposure time`，不是 `reference time`。一条"关于 2008 危机"的知识，如果模型是从 2025 年的 retrospective 学到的，那么对 `τ = 2024-03` 的回测它仍然是非法的。这就是我建议单独命名的 `retrospective contamination`。

**现有方案的光谱**
- `一刀切剥离年份/实体线索`：最保守，最稳，但损失最大。它把合法 backward memory 和非法 forward memory 一起杀掉。
- `prompt-level date discipline`：比如 "answer as of March 2024"、fake-date、role-play。便宜，但很弱。Lopez-Lira et al. 的结果基本说明强记忆下指令并不可靠。
- `task redesign`：从 direct prediction 转向 authority/novelty/evidence-grounded extraction。它不删除记忆，但降低 forward memory 的效用，并把 intrusion 暴露出来。这是你们 v2 最有价值的部分。
- `point-in-time RAG`：只给 `τ` 之前的 archive，要求引用证据。这是黑盒模型上最现实的 temporal cutoff 近似，因为它把合法 backward memory 外部化、可审计化。
- `context-faithfulness / conflict mitigation`：在 PIT-RAG 上再加 context-over-memory steering。它不能保证无泄露，但能显著提高"读文而不是背答案"的概率。
- `activation steering / temporal steering`：比 prompt 强，但仍是软约束，不是硬切分。
- `knowledge editing / unlearning`：适合删少量热点事实，不适合删"某日期之后的整个知识区间"。
- `vintage models / chronologically consistent models`：最干净的长期路线。不是在推理时切记忆，而是让不同 vintage 的模型天然只拥有 `τ` 之前的知识。
- `理想的 daily temporal cutoff inside one frozen black-box model`：以 2026 年的证据看，仍不现实。

**技术可行性**
- `Chronologically Consistent LLMs` 确实提供了一条路，但这条路是"by construction"，不是"runtime excision"。He et al. 2025 的价值在于证明：严格时间一致的模型仍可在金融文本任务里保持竞争力。它支持长期方向，但不能直接解决现有 vendor API 的动态 cutoff。
- `Set the Clock` 和后续 activation engineering 文献说明"时间"在模型内部像可操纵的 latent state，而不是完全不可触碰。它们证明了 soft alignment 可行，这是重要进展。
- 但我这里明确区分一下：`temporal steering != temporal ban`。它更像把模型往某一年份的知识截面上推，而不是证明 `τ` 之后的痕迹被清空了。这是我的推断，不是这些论文的直接主张。
- `ROME / MEMIT` 不适合 date-range deletion。它们擅长原子事实编辑。MQuAKE 和 temporal KE 论文都表明，单点 edit 不能可靠传播到 multi-hop belief network，更别说"删除 2024-03 之后所有金融世界知识"。
- 我没有找到一篇能对"固定大模型，在推理时对任意 cutoff τ 做干净时间切分"给出成熟方案的论文。最接近的是：temporal alignment、time-aware pretraining、以及 context-over-memory intervention。
- 另外，`Dated Data` 的结果很关键：effective cutoff 本身就是模糊的，不同资源和主题不一致。也就是说，连"模型真正知道到哪一天"为何时，都是 resource-specific 的。

**对你们项目与 Thales 的影响**
- 对 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md) 的最大修改建议是：把 `Type A/B` 从"主 taxonomy"降为"功能路径 taxonomy"，再新增 `temporal admissibility` 轴。
- 这样一来，`CFLS` 的解释必须收窄。它测到的不是纯粹的 forward leakage，而是 `article-responsiveness` 对 `extra-textual shortcutting` 的敏感度。里面混有 forward outcome memory、entity prior、article overlap、task-template memory。
- `evidence intrusion` 更接近高精度的 forward leakage 证据。尤其当 intrusion 明确包含 post-publication facts 或 realized outcomes 时，它比 CFLS 更"尖"。
- `false-outcome CPT` 是目前最接近 causal identification 的设计，因为它直接操纵 outcome memory。它测到的是"这类 outcome trace 能否因果性地进入答案"，而不是全部真实世界污染。
- 所以如果不能完美切分，你们的 paper 不该声称"测量了 look-ahead leakage 本身"，更准确的说法是：`测量了任务对 temporally inadmissible memory 和其他 text-external shortcut 的暴露度`。
- 我建议把"泄露"重定义为：`对在 point-in-time archive C<=τ 中不可恢复之信息的依赖`。这是比"模型是否记住未来"更可操作的定义。
- 对 Thales，一刀切剥去年份的代价我判断主要落在 macro/policy/regime-sensitive 任务上，因为这些任务最依赖合法 historical analogy。authority/novelty 这类更贴近 metadata 和 visible evidence 的任务，损失会小一些。这是我的推断。
- 比一刀切更好的近似是：`PIT archive + historical analog retrieval + citation requirement + intrusion auditing`。也就是把合法 backward memory 从参数里"搬到外部证据层"，而不是指望参数记忆自己守纪律。
- 长期看，正确方向不是单独追求"时间一致性 LLM"，而是 `time-consistent backbone + PIT retrieval + grounding audit` 的系统组合。

**更深层的问题**
- 向后记忆并不天然合法。两种最重要的污染是：
- `retrospective contamination`：谈的是旧事件，但学习它的文本是 cutoff 之后写的。
- `hindsight narrative contamination`：即便文本时间上合法，描述也可能已经被后验叙事、胜者叙事、因果重构污染。
- 认知文献对你们很有帮助，因为它强调 memory 是 reconstructive、schema-driven、source-blind 的。把这个类比到 LLM，上最稳妥的看法不是"模型记住了过去"，而是"模型学到了关于过去的压缩叙事"。
- 因此，真正的 gold standard 不是"允许 backward memory"，而是"允许能被 `τ` 时点证据集重建出来的 memory"。换句话说，合法性应当由 `point-in-time recoverability` 定义，而不是由"内容在谈过去"定义。

**参考**
- [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md)
- Chronologically Consistent Large Language Models: https://arxiv.org/abs/2502.21206
- Set the Clock: Temporal Alignment of Pretrained Language Models: https://arxiv.org/abs/2402.16797
- Temporal Alignment of Time Sensitive Facts with Activation Engineering: https://aclanthology.org/2025.findings-emnlp.404/
- Dated Data: Tracing Knowledge Cutoffs in Large Language Models: https://arxiv.org/abs/2403.12958
- Time-Aware Language Models as Temporal Knowledge Bases: https://aclanthology.org/2022.tacl-1.15/
- DatedGPT: Preventing Lookahead Bias in Large Language Models with Time-Aware Pretraining: https://arxiv.org/abs/2603.11838
- The Memorization Problem: Can We Trust LLMs' Economic Forecasts?: https://arxiv.org/abs/2504.14765
- A Test of Lookahead Bias in LLM Forecasts: https://arxiv.org/abs/2512.23847
- Fake Date Tests: Can We Trust In-sample Accuracy of LLMs in Macroeconomic Forecasting?: https://arxiv.org/abs/2601.07992
- Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance: https://arxiv.org/abs/2601.13770
- Context-faithful Prompting for Large Language Models: https://aclanthology.org/2023.findings-emnlp.968/
- Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style: https://arxiv.org/abs/2409.10955
- Entity-Based Knowledge Conflicts in Question Answering: https://arxiv.org/abs/2109.05052
- Cutting Off the Head Ends the Conflict: https://arxiv.org/abs/2402.18154
- Taming Knowledge Conflicts in Language Models: https://arxiv.org/abs/2503.10996
- Locating and Editing Factual Associations in GPT: https://arxiv.org/abs/2202.05262
- Mass-Editing Memory in a Transformer: https://arxiv.org/abs/2210.07229
- MQuAKE: Assessing Knowledge Editing in Language Models via Multi-Hop Questions: https://arxiv.org/abs/2305.14795
- Time Sensitive Knowledge Editing through Efficient Finetuning: https://arxiv.org/abs/2406.04496
- A generative model of memory construction and consolidation: https://www.nature.com/articles/s41562-023-01799-z
- Source monitoring and memory distortion: https://memlab.yale.edu/sites/default/files/files/1997_Johnson_PTRSL.pdf

如果你愿意，我下一步可以直接把这套分析改写成一版可塞进 proposal v2 的 `Section 5` 重写稿。
