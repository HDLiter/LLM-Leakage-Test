**结论先行**
这次检索很清楚地支持了你们的核心判断：LLM 的"记忆"不是单一变量，而是至少由 4 个正交维度构成：`记忆对象`、`记忆保真度`、`触发条件`、`时间/冲突状态`。对你们的中文金融新闻情感项目，最值得单独拆开的不是只有 `verbatim vs approximate`，而是：

- `sequence memory`：原文级续写/复现
- `factual memory`：事件-结果或事实三元组记忆
- `entity-conditioned prior`：看到实体名后激活的统计先验/联想
- `metadata/provenance memory`：来源、出处、时间戳、有效期等元信息

我下面按你提的 5 个问题汇总；文中只用一手论文来源（ACL Anthology / arXiv）。

**1. LLM 记忆的分类体系**
现有文献里，最有用的不是单一 taxonomy，而是"多轴分类"：

- [Give Me the Facts! A Survey on Factual Knowledge Probing in Pre-trained Language Models](https://aclanthology.org/2023.findings-emnlp.1043/) | Paul Youssef et al. | 2023 | Findings of EMNLP。核心发现：把 factual probing 按 `输入如何构造`、`输出如何读取`、`模型如何被适配` 来分。关联：说明"测到什么记忆"强烈依赖 probe 设计，不同方法并不在测同一种记忆。
- [Training Data Extraction From Pre-trained Language Models: A Survey](https://aclanthology.org/2023.trustnlp-1.23/) | Shotaro Ishihara | 2023 | TrustNLP。核心发现：系统整理了 memorization 的多种定义、攻击/防御和量化方法。关联：适合你们把"数据泄露"拆成 `可抽取的记忆` 与 `仅影响预测但不可直接抽取的记忆`。
- [Counterfactual Memorization in Neural Language Models](https://arxiv.org/abs/2112.12938) | Chiyuan Zhang et al. | 2021 | arXiv。核心发现：提出 counterfactual memorization，看"拿掉某文档后模型预测是否变化"。关联：这比"模型答对历史事件"更接近你们真正想测的"事件-结果记忆"。
- [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805) | Nicholas Carlini et al. | 2021 | USENIX Security / arXiv。核心发现：证明了单文档出现的训练样本也可能被 verbatim 抽出。关联：它定义的是 `extractable sequence memory`，不应和你们的 `entity prior memory` 混为一谈。

基于这些文献，我建议你们把"记忆"至少按 4 轴写入论文：`对象（sequence/fact/entity/meta）`、`保真度（verbatim/approximate/counterfactual）`、`可触发性（cue-free/cue-rich/optimized prompt）`、`动态性（static/temporal/conflicting）`。

**2. 知识内容 vs 元信息：事实内容和出处/时间是不是记得不一样强？**
直接、严格比较 `content memory vs provenance memory` 的论文其实很少；但现有证据相当一致地指向：`事实内容 > 实体先验 > 时间约束 > 明确出处/来源`。这句话是我基于多篇论文的综合推断，不是某一篇论文直接给出的结论。

- [Towards Tracing Knowledge in Language Models Back to the Training Data](https://aclanthology.org/2022.findings-emnlp.180/) | Ekin Akyürek et al. | 2022 | Findings of EMNLP。核心发现：提出 fact tracing，想找"模型这条事实是从哪些训练样本学来的"；结果连专门的 attribution 方法都很难稳定追回来源。关联：这恰好支持"模型可能记住内容，但不容易保留/暴露 provenance"。
- [KILT: a Benchmark for Knowledge Intensive Language Tasks](https://arxiv.org/abs/2009.02252) | Fabio Petroni et al. | 2020 | arXiv。核心发现：把 provenance 单独当成 benchmark 目标。关联：学界通常把 provenance 当 `外部证据对齐问题`，而不是默认 LLM 参数里天然可读出的记忆。
- [Towards Verifiable Generation: A Benchmark for Knowledge-aware Language Model Attribution](https://aclanthology.org/2024.findings-acl.28/) | Xinze Li et al. | 2024 | Findings of ACL。核心发现：进一步把 attribution 扩展到 KG 级别，并强调 citation/attribution 仍有很大空间。关联：如果 provenance 需要单独 benchmark 和监督，通常说明它不是模型最自然、最稳定的 parametric memory 形态。
- [Can Language Models Serve as Temporal Knowledge Bases?](https://aclanthology.org/2022.findings-emnlp.147/) | Ruilin Zhao et al. | 2022 | Findings of EMNLP。核心发现：LM 能记住大量 temporally-scoped facts，但对冲突性、时变事实处理明显更难。关联：这非常接近你们的"新闻发生时点 vs 事后结果"问题。
- [DYNAMICQA: Tracing Internal Knowledge Conflicts in Language Models](https://aclanthology.org/2024.findings-emnlp.838/) | Sara Vera Marjanovic et al. | 2024 | Findings of EMNLP。核心发现：动态事实更容易产生 intra-memory conflict，且更难被外部 context 更新。关联：如果金融新闻涉及时变事实，模型会更顽固地依赖旧参数记忆。
- [EvolveBench: A Comprehensive Benchmark for Assessing Temporal Awareness in LLMs on Evolving Knowledge](https://aclanthology.org/2025.acl-long.788/) | Zhiyuan Zhu et al. | 2025 | ACL。核心发现：模型整体仍明显吃亏于 temporal misalignment。关联：说明"知道内容"不等于"知道它在什么时间成立"。

**3. 实体级记忆：有没有"Tesla 常涨"这类实体先验研究？**
有，而且这条线和你们最贴近。文献里通常不叫"sentiment prior"，而叫 `entity bias`、`entity-level memorization`、`popularity/co-occurrence bias`。

- [Quantifying and Analyzing Entity-level Memorization in Large Language Models](https://arxiv.org/abs/2308.15727) | Zhenhong Zhou et al. | 2023 | arXiv。核心发现：LLM 存在强实体级记忆，部分泄露条件下也能重构实体，并且不仅记实体，还记实体间关联。关联：几乎是你们"实体-关联记忆"假设的直接文献支撑。  
  **[RECOMMEND DOWNLOAD]**
- [A Causal View of Entity Bias in (Large) Language Models](https://aclanthology.org/2023.findings-emnlp.1013/) | Fei Wang et al. | 2023 | Findings of EMNLP。核心发现：模型会依赖和实体绑定的 parametric knowledge，导致不忠实预测；替换邻近实体可显著缓解。关联：这和"看到贵州茅台/Tesla 就先入为主"几乎同构。  
  **[RECOMMEND DOWNLOAD]**
- [When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories](https://arxiv.org/abs/2212.10511) | Alex Mallen et al. | 2023 | ACL / arXiv。核心发现：无检索 LMs 对高流行度实体更强，对 long-tail facts 明显更弱。关联：说明实体 popularity 本身就是强 prior。
- [Impact of Co-occurrence on Factual Knowledge of Large Language Models](https://aclanthology.org/2023.findings-emnlp.518/) | Cheongwoong Kang, Jaesik Choi | 2023 | Findings of EMNLP。核心发现：模型会偏向高共现词，而非正确事实；这种 co-occurrence bias 扩模和 finetune 后仍存在。关联：如果某股票在训练中经常和"上涨""利好"共现，模型可能学到的是共现先验，不是可解释的事件推理。
- [Head-to-Tail: How Knowledgeable are Large Language Models (LLMs)?](https://aclanthology.org/2024.naacl-long.18/) | Kai Sun et al. | 2024 | NAACL。核心发现：事实准确率从 head entity 到 tail entity 系统性下降。关联：金融实体里大盘股/明星公司与冷门个股的"记忆质量"很可能不同。

**4. 记忆触发机制：什么 cue/prompt 更容易触发训练记忆？**
综合来看，最强触发因素不是"是否问了这个任务"，而是 `线索强度` 和 `提示优化程度`。大致排序我会写成：`entity/lexical cue` > `长前缀/高重叠前缀` > `soft prompt / prompt tuning` > `task framing（style transfer, CoT）` > `temporal cue`。最后两者更依赖具体设置。

- [ETHICIST: Targeted Training Data Extraction Through Loss Smoothed Soft Prompting and Calibrated Confidence Estimation](https://aclanthology.org/2023.acl-long.709/) | Zhexin Zhang et al. | 2023 | ACL。核心发现：soft prompting 明显提高 targeted extraction，并系统分析了 decoding、model scale、prefix length、suffix length。关联：说明"触发了记忆"不只是内容问题，也是 prompt optimization 问题。
- [Controlling the Extraction of Memorized Data from Large Language Models via Prompt-Tuning](https://aclanthology.org/2023.acl-short.129/) | Mustafa Ozdayi et al. | 2023 | ACL。核心发现：prompt-tuning 可以同时增强或压低 extraction rate。关联：同一模型、同一记忆，能否被测到高度依赖触发器设计。
- [Preventing Generation of Verbatim Memorization in Language Models Gives a False Sense of Privacy](https://aclanthology.org/2023.inlg-main.3/) | Daphne Ippolito et al. | 2023 | INLG。核心发现：即使完全阻断 verbatim generation，style-transfer prompts 仍能挖出近似记忆。关联：你们不能只做 exact-match contamination test；必须做 paraphrase/改写触发。  
  **[RECOMMEND DOWNLOAD]**
- [Characterizing Mechanisms for Factual Recall in Language Models](https://aclanthology.org/2023.emnlp-main.615/) | Qinan Yu, Jack Merullo, Ellie Pavlick | 2023 | EMNLP。核心发现：query entity 和 in-context candidate 的训练频率，会影响模型选"参数记忆"还是"上下文答案"。关联：这直接回答了 entity mention 和 context cue 的相对作用。
- [When Context Leads but Parametric Memory Follows in Large Language Models](https://aclanthology.org/2024.emnlp-main.234/) | Yufei Tao et al. | 2024 | EMNLP。核心发现：即使给了 context，模型仍稳定混用 contextual knowledge 与 parametric knowledge。关联：新闻情感任务里，"给原文"并不能自动消掉实体先验。
- [Unveiling Factual Recall Behaviors of Large Language Models through Knowledge Neurons](https://aclanthology.org/2024.emnlp-main.420/) | Yifei Wang et al. | 2024 | EMNLP。核心发现：CoT 会增强 factual recall，抑制/增强 recall 还能直接影响推理表现。关联：任务 framing 和输出格式不是中性的，会改变 memory retrieval。

**5. 跨领域启发**
跨 QA、知识库、RAG/attribution 的共同结论是：`参数记忆擅长存内容，不擅长可靠地附带来源和时间边界`。

- QA/知识探测线：PopQA、Head-to-Tail 表明 popularity/head-tail 是强变量，适合你们解释"明星金融实体更容易触发偏置预测"。
- LM-as-KB/Temporal-KB 线：[Language Models as Knowledge Bases: On Entity Representations, Storage Capacity, and Paraphrased Queries](https://aclanthology.org/2021.eacl-main.153/) | 核心启发是 LM 确实能存储海量实体-关系事实，但 temporal/conflict 一上来就明显掉。关联：事件后验结果可以被存，时点有效性未必一起被存。
- Attribution/Provenance 线：KILT、KaLMA、fact tracing 都把 provenance 当成额外目标或外部对齐任务。关联：这支持你们把"信源/出处记忆弱"作为一个合理研究假设。
- 机制解释线：知识神经元、fact tracing、context-memory conflict 文献都说明"记忆"和"推理"最好分开测。关联：你们的评测不应把"预测正确"直接等同于"泄露"。

**对你们项目最直接的研究设计启发**
建议把实验显式拆成 3 个潜变量，而不是一个 contamination score：

1. `事件-结果记忆`：固定实体，改时间窗和事件描述，看是否给出后验结果。  
2. `实体-关联先验`：固定事件模板，交换实体名，看情感预测是否随实体系统漂移。  
3. `来源/出处记忆`：固定正文内容，只替换"新华社/公司公告/市场传闻/匿名博主"等 source label，看输出是否显著变化。  

如果第 3 类效应远弱于前两类，那会和现有文献非常一致。

**推荐下载**
- **[RECOMMEND DOWNLOAD]** [Quantifying and Analyzing Entity-level Memorization in Large Language Models](https://arxiv.org/abs/2308.15727)  
  搜索关键词：`entity-level memorization large language models Zhou 2023`
- **[RECOMMEND DOWNLOAD]** [A Causal View of Entity Bias in (Large) Language Models](https://aclanthology.org/2023.findings-emnlp.1013/)  
  搜索关键词：`entity bias parametric knowledge causal view EMNLP 2023`
- **[RECOMMEND DOWNLOAD]** [Counterfactual Memorization in Neural Language Models](https://arxiv.org/abs/2112.12938)  
  搜索关键词：`counterfactual memorization neural language models Zhang Ippolito Carlini`
- **[RECOMMEND DOWNLOAD]** [Towards Tracing Knowledge in Language Models Back to the Training Data](https://aclanthology.org/2022.findings-emnlp.180/)  
  搜索关键词：`fact tracing training data attribution EMNLP 2022`
- **[RECOMMEND DOWNLOAD]** [Can Language Models Serve as Temporal Knowledge Bases?](https://aclanthology.org/2022.findings-emnlp.147/)  
  搜索关键词：`temporal knowledge bases language models LAMA-TK EMNLP 2022`
- **[RECOMMEND DOWNLOAD]** [DYNAMICQA: Tracing Internal Knowledge Conflicts in Language Models](https://aclanthology.org/2024.findings-emnlp.838/)  
  搜索关键词：`DYNAMICQA internal knowledge conflicts temporal dynamic facts EMNLP 2024`
- **[RECOMMEND DOWNLOAD]** [Preventing Generation of Verbatim Memorization in Language Models Gives a False Sense of Privacy](https://aclanthology.org/2023.inlg-main.3/)  
  搜索关键词：`style-transfer prompts approximate memorization privacy Ippolito 2023`
