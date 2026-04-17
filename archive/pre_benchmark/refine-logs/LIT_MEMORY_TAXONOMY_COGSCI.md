最可用的结论先说在前面：你们的 `Type A / Type B` 不宜只做成 "semantic vs episodic" 的硬二分，更稳妥的是用 3 个维度来标记记忆痕迹：`时间特异性`、`来源/语境绑定程度`、`概念化/语义化程度`。在这个框架下，Type A 是"时间更泛化、来源更弱绑定、内容更概念化"的知识；Type B 是"事件更具体、结果更时间绑定、带有 episode 痕迹"的记忆。对 LLM 来说，这只是功能类比，不是说它拥有 Tulving 意义上的真正情景记忆。

**核心文献**
**1. 语义记忆 vs 情景记忆**
- [RECOMMEND DOWNLOAD] [Episodic and semantic memory](https://bibbase.org/network/publication/tulving-episodicandsemanticmemory-1972) — Endel Tulving, 1972。核心贡献：首次系统区分 semantic memory 与 episodic memory。映射：Type A 最接近 context-independent 的 semantic memory；Type B 最接近 event-specific、time-bound 的 episodic-like memory。
- [RECOMMEND DOWNLOAD] [What Is Episodic Memory?](https://journals.sagepub.com/doi/10.1111/1467-8721.ep10770899) — Endel Tulving, 1993。核心贡献：把 episodic memory 的关键推进到 mental time travel / autonoetic consciousness。映射：这提醒你们，LLM 的 Type B 更准确应表述为 "episode-bound outcome memory"，而不是真正的人类情景记忆。
- [RECOMMEND DOWNLOAD] [Episodic Memory: From Mind to Brain](https://www.annualreviews.org/doi/10.1146/annurev.psych.53.100901.135114) — Endel Tulving, 2002。核心贡献：总结 episodic memory 的神经认知特征及其与其他记忆系统的区分。映射：适合做理论综述部分的权威背景。
- [RECOMMEND DOWNLOAD] [An historical perspective on Endel Tulving's episodic-semantic distinction](https://www.sciencedirect.com/science/article/pii/S0028393220300373) — Ludovic Renoult & Michael D. Rugg, 2020。核心贡献：说明 Tulving 后期并不主张 rigid dichotomy，而强调两类记忆的相互作用。映射：Type A / Type B 更像不同程度的语境绑定与抽象化，而不是两种互斥箱子。
- [RECOMMEND DOWNLOAD] [Beyond the episodic–semantic continuum: the multidimensional model of mental representations](https://pmc.ncbi.nlm.nih.gov/articles/PMC11449204/) — Donna Rose Addis & Karl K. Szpunar, 2024。核心贡献：提出 MMMR，用"时间特异性、感知性/概念性、自我性/共享性"三轴替代单一 continuum。映射：这是你们项目最值得吸收的最新发展，尤其适合把 Type A / Type B 改写成多维标注体系。

**2. Source Monitoring**
- [RECOMMEND DOWNLOAD] [Source monitoring](https://pubmed.ncbi.nlm.nih.gov/8346328/) — Marcia K. Johnson, Shahin Hashtroudi & D. Stephen Lindsay, 1993。核心贡献：提出 source monitoring framework，认为来源判断不是读取显式标签，而是基于记忆痕迹的质性特征做归因。映射：这几乎就是"模型记得内容但不记得来源"的最佳理论解释；LLM 参数里可能保留 proposition，但缺乏稳定 provenance tag。
- [Source monitoring and memory distortion](https://memlab.yale.edu/sites/default/files/files/1997_Johnson_PTRSL.pdf) — Marcia K. Johnson, 1997。核心贡献：把 false memory、misinformation、confabulation 统一到 source-monitoring 失误里。映射：很适合把"泄露、幻觉、错误引用来源"放进同一框架，而不是割裂处理。
- 这条线对你们尤其关键：SMF 暗示错误不一定来自"没有记住"，也可能来自"记住了内容，但来源判别失败"。对 LLM，这对应 `answer correct but source blind` 的现象。

**3. Reality Monitoring**
- [RECOMMEND DOWNLOAD] [Reality Monitoring](https://memlab.yale.edu/sites/default/files/files/1981_Johnson_Raye_PsychRev.pdf) — Marcia K. Johnson & Carol L. Raye, 1981。核心贡献：提出人类如何区分 externally derived 与 internally generated 信息。映射：最直接对应"模型是在复述 context、调用 parametric memory，还是现场推理"。
- [RECOMMEND DOWNLOAD] [Brain Mechanisms of Reality Monitoring](https://www.memlab.psychol.cam.ac.uk/pubs/Simons2017%20TICS.pdf) — Jon S. Simons et al., 2017。核心贡献：总结 reality monitoring 的神经机制，并强调 externalization errors。映射：对 LLM 的启发不是脑区同构，而是需要独立的"监控/归因层"，不能只评分最终答案。
- [Reality monitoring and metacognitive judgments in a false-memory paradigm](https://pubmed.ncbi.nlm.nih.gov/38007192/) — Saurabh Ranjan & Brian Odegaard, 2024。核心贡献：发现 imagined items 容易被误报为 perceived，存在 externalizing bias。映射：可直接转成 LLM eval，把"推理得出"误报成"上下文明说"的比例作为指标。
- [Confidence ratings do not distinguish imagination from reality](https://pubmed.ncbi.nlm.nih.gov/38814936/) — Nadine Dijkstra et al., 2024。核心贡献：高置信度并不能保证 reality monitoring 正确。映射：不要把模型自报置信度当成来源判别可靠性的充分证据。

**4. 去语境化 / 语义化 / 一般化**
- [RECOMMEND DOWNLOAD] [Why There Are Complementary Learning Systems in the Hippocampus and Neocortex](https://doi.org/10.1037/0033-295X.102.3.419) — James L. McClelland, Bruce L. McNaughton & Randall C. O'Reilly, 1995。核心贡献：经典 CLS，快系统保留 episodes，慢系统提取统计规律。映射：LLM 预训练非常像慢系统，给 Type A 的"合理背景知识"提供最强计算层解释。
- [Feature-specific reaction times reveal a semanticisation of memories over time and with repeated remembering](https://pubmed.ncbi.nlm.nih.gov/34039970/) — Lisa Linde-Domingo et al., 2021。核心贡献：反复提取让记忆更偏 conceptual、少感知细节。映射：和金融新闻事件在预训练里被多次吸收后，只留下 gist 或市场脚本非常相似。
- [RECOMMEND DOWNLOAD] [Time-dependent memory transformation in hippocampus and neocortex is semantic in nature](https://www.nature.com/articles/s41467-023-41648-1) — Theodoor Sweegers et al., 2023。核心贡献：较强证据支持记忆随时间发生 semantic transformation，而不只是细节衰减。映射：支持一个重要判断：LLM 对历史事件的很多"知道"，可能是 semanticized schema，不是完整 event replay。
- [RECOMMEND DOWNLOAD] [A generative model of memory construction and consolidation](https://www.nature.com/articles/s41562-023-01799-z) — Eleanor Spens & Neil Burgess, 2024。核心贡献：把 consolidation 建模为 generative network 学习事件统计结构；语义记忆与重建式回忆并存。映射：这篇和生成式 AI 最贴近，能支撑"预训练把具体事件压缩进概率结构"这一说法。
- [Organizing memories for generalization in complementary learning systems](https://www.saxelab.org/assets/papers/Sun2023.pdf) — Sun et al., 2023。核心贡献：提出 consolidation 的目标是优化 generalization，而不是完整转移全部 episodes。映射：非常适合讨论"哪些历史金融事件被抽象成先验、哪些不应被抽象进去"。

**5. Availability / Anchoring**
- [RECOMMEND DOWNLOAD] [Availability: A heuristic for judging frequency and probability](https://doi.org/10.1016/0010-0285(73)90033-9) — Amos Tversky & Daniel Kahneman, 1973。核心贡献：人类会用"易于提取"近似"真实频率/概率"。映射：LLM 对高频实体、常见市场叙事、训练中高共现模式的偏好，很像 availability-like bias。
- [RECOMMEND DOWNLOAD] [Judgment under Uncertainty: Heuristics and Biases](https://doi.org/10.1126/science.185.4157.1124) — Amos Tversky & Daniel Kahneman, 1974。核心贡献：系统化提出 anchoring 等启发式。映射：对金融新闻情感分析，LLM 可能被实体先验或 prompt 早期信息锚住，后续调整不足，比如"茅台常涨""科技股利多"的先验锚定。
- 这一部分我找到的"直接把 availability/anchoring 理论严密迁移到 LLM parametric memory 泄露"的成熟跨学科论文还不多；目前更适合做理论类比，而不是强同构主张。

**6. 将人类记忆理论应用到 AI/LLM 的跨学科论文**
- [RECOMMEND DOWNLOAD] [Towards large language models with human-like episodic memory](https://doi.org/10.1016/j.tics.2025.06.016) — Cody V. Dong, Qihong Lu, Kenneth A. Norman & Sebastian Michelmann, 2025。核心贡献：直接比较 human episodic memory 与 memory-augmented LLMs，提出 event segmentation、selective encoding/retrieval、temporal contiguity、retrieval competition 等对齐标准。映射：这是把人类记忆理论迁到 LLM 评测最成熟的一篇综述。
- [RECOMMEND DOWNLOAD] [Episodic Memories Generation and Evaluation Benchmark for Large Language Models](https://arxiv.org/abs/2501.13121) — Alexis Huet, Zied Ben Houidi & Dario Rossi, 2025。核心贡献：构造包含时间、地点、实体状态、时序与 confabulation 的 episodic benchmark。映射：非常适合改造成金融新闻泄露 benchmark，把"事件结果、时序、实体状态变化"设计成 Type B 检测项。
- [Memory GAPS: Would LLMs pass the Tulving Test?](https://arxiv.org/abs/2402.16505) — Jean-Marie Chauvet, 2024。核心贡献：直接把 Tulving 测试框架搬到 LLM。映射：虽然偏探索性，但很适合 related work，尤其能支持"LLM remembering 可以借 Tulving 范式分析"。
- [Memory Traces: Are Transformers Tulving Machines?](https://arxiv.org/abs/2404.08543) — Jean-Marie Chauvet, 2024。核心贡献：继续用 Tulving–Watkins 经典实验审视 transformer 的 memory traces。映射：可作为"心理学实验范式可迁移到 foundation models"的证据链一环。
- 直接把 `source monitoring / reality monitoring` 用于 LLM 的实证论文，我这次检索到的还很稀少；目前更成熟的是 episodic-memory benchmark 方向。这是你们可以切进去的明显研究空白。

**对你们 6 个问题的直接映射**
1. `semantic vs episodic`：Type A 最像 semanticized background knowledge；Type B 最像 episode-bound outcome memory。更准确的说法不是"LLM 有情景记忆"，而是"LLM 表现出事件绑定的结果记忆痕迹"。
2. `source monitoring`：最适合解释"内容在，来源没了"。LM 参数可能保留命题与关联强度，却没有稳定可回读的 source/date/article 指针。
3. `reality monitoring`：最适合解释"模型把自己推理出的东西说成上下文给的"或"把参数记忆说成来自当前文档"。这是 `context vs inference vs parametric memory` 三方混淆。
4. `去语境化`：人类记忆会 semanticization；LLM 预训练也很可能把大量具体事件抽象成 schema。但 LLM 还可能残留少量近 verbatim 的稀有 episode 痕迹，所以两种机制可能并存。
5. `availability heuristic`：高频市场叙事、反复出现的公司/行业模式，会被 LLM 过度提取，哪怕并不对应当前事件的真实结果。
6. `anchoring`：实体先验、行业先验、prompt 中最早出现的数字或结论，都可能成为 LLM 的锚，导致它低估新证据。

**对 LLM Evaluation 的直接启发**
- 把答案判对之外，再单独测 `source attribution accuracy`：模型能答对，不等于它知道信息来自哪里、何时获得。
- 用 reality-monitoring 范式设计三分类任务：`explicitly in context`、`inferred by the model`、`not supported`。
- 专门统计 `externalization error`：把 inference 误报为 context；这比普通 hallucination 更贴近你们的问题。
- 把 Type A / Type B 标注改成多维：`时间特异性`、`来源绑定`、`概念化程度`。这比二分类更稳。
- 在金融场景里加入 `time-cutoff aware` 评测：若答案依赖 cutoff 之后才发生的结果，即使语言上像"常识"，也应单列为 prospective contamination 风险。
- 不要过度依赖模型自报置信度；reality-monitoring 文献表明，高置信并不等于来源归因正确。

这次检索里，最成熟的文献链条是 `Tulving → Johnson/Source Monitoring → semanticization/CLS → episodic-memory-for-LLM benchmarks`。相对不足的是"直接把 source monitoring / reality monitoring 实证迁移到 LLM"的论文还少，这部分更像你们可以原创贡献的切口。
