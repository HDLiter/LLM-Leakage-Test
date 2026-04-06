截至 **2026-04-06**，我的结论是：**"事实知识、实体身份、时间信息、上下文来源利用"至少不是同一种内部机制。** 现有证据更支持这样一种分层图景：`原子事实` 更像 FFN/MLP 中可编辑的 key-value memory；`事件链/因果关联/上下文取舍` 更像跨层 attention-MLP 电路；`实体 prior` 更像早层实体表征与参数记忆捷径的混合；`时间知识` 则像一个可解码、可 steering 的连续潜变量。对金融新闻泄露检测，这意味着**不要用单一 benchmark**，而应把 `atomic fact`、`association/event outcome`、`entity prior`、`temporal fact`、`source-faithfulness` 分开测。

**1. 知识在 Transformer 中的存储位置**
- [RECOMMEND DOWNLOAD] [Transformer Feed-Forward Layers Are Key-Value Memories](https://arxiv.org/abs/2012.14913) (Geva et al., 2021)：FFN/MLP 可视作 key-value memories，是"知识在 FFN 中"的基础证据。
- [RECOMMEND DOWNLOAD] [Locating and Editing Factual Associations in GPT](https://arxiv.org/abs/2202.05262) (Meng et al., 2022)：subject-relation-object 型事实主要依赖**中层 MLP**，且可被 ROME 直接改写。
- [RECOMMEND DOWNLOAD] [Dissecting Recall of Factual Associations in Auto-Regressive Language Models](https://arxiv.org/abs/2304.14767) (Geva et al., 2023)：把 factual recall 拆成 3 步。核心结论是：**早期 MLP enrich subject 表征，后续 attention 从 enriched subject 中提取属性**。这说明"存储"和"检索"不是同一步。
- [RECOMMEND DOWNLOAD] [On Entity Identification in Language Models](https://arxiv.org/abs/2506.02701) (Sakata et al., 2025)：entity 信息在**早层低维线性子空间**中很紧凑。
- [RECOMMEND DOWNLOAD] [Friends and Grandmothers in Silico: Localizing Entity Cells in Language Models](https://arxiv.org/abs/2604.01404) (Yona et al., 2026)：一部分实体可对应到**早层 MLP 的 entity-selective neurons**；ablation 会产生 entity-specific amnesia。
- [RECOMMEND DOWNLOAD] [Language Models Represent Space and Time](https://arxiv.org/abs/2310.02207) (Gurnee & Tegmark, 2024)：时间/空间信息不是普通 fact slot，而是**跨层可线性解码的连续坐标**，并存在 time neurons。
- 直接回答你的细分问题：**实体身份/属性**已有较强"早层/MLP/低维子空间"证据；**事件时间线/因果关系**更像跨层 circuit；**信源出处**作为参数记忆的专门存储位置，**目前几乎没有直接 mechanistic 证据**。这一点是推断，不是定论。

**2. Factual recall vs association recall**
- [RECOMMEND DOWNLOAD] [Co-occurrence is not Factual Association in Language Models](https://arxiv.org/abs/2409.14057) (Zhang et al., 2024)：最关键的一篇。它明确区分了 **co-occurrence statistics** 和 **true factual associations**，并声称前者更多在**中层**、泛化差，后者更偏**低层**、能支持更自由推理。
- [Dissecting Recall of Factual Associations in Auto-Regressive Language Models](https://arxiv.org/abs/2304.14767) (Geva et al., 2023)：支持 `巴黎是法国首都` 这类 direct fact recall 有相对稳定的 subject-relation-attribute 检索流程。
- [Evaluating Contextually Mediated Factual Recall in Multilingual Large Language Models](https://arxiv.org/abs/2601.12555) (Liu et al., 2026)：当实体不被直接点名、而是通过上下文间接引出时，factual recall 明显下降。说明**direct cloze recall 和 mediated association recall 不是同一难度，也很可能不是同一电路**。
- [Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization](https://arxiv.org/abs/2405.15071) (Wang et al., 2024)：提示"记住事实"和"组合/比较推理"需要不同 circuit；后者往往要经过 grokking 才稳定出现。
- 对你的例子，我的判断是：`巴黎是法国首都` 更接近 localized factual association；`降息之后市场涨了` 通常混合了事件模板、统计共现、时间条件和因果/叙事先验，更像**分布式 association/reasoning circuit**，而不是单一 fact slot。

**3. Entity representation 和 entity prior**
- [RECOMMEND DOWNLOAD] [On Entity Identification in Language Models](https://arxiv.org/abs/2506.02701) (Sakata et al., 2025)：模型能把同一实体的不同 mentions 聚成簇，并在早层线性子空间中表示实体。
- [RECOMMEND DOWNLOAD] [Friends and Grandmothers in Silico: Localizing Entity Cells in Language Models](https://arxiv.org/abs/2604.01404) (Yona et al., 2026)：实体表征至少对一部分高频实体是"稀疏可操控"的，并对 alias、缩写、拼写扰动、多语言形式有鲁棒性，像 canonicalization。
- [RECOMMEND DOWNLOAD] [A Causal View of Entity Bias in (Large) Language Models](https://arxiv.org/abs/2305.14695) (Wang et al., 2023)：实体名本身会触发 **parametric shortcut**，导致模型忽视上下文，是 entity prior 的直接证据。
- 但"entity embedding 是否编码 sentiment/valence"这点，**现有 mechanistic 证据仍弱**。更准确的说法是：已有证据支持"实体名携带强 prior，并会影响下游判断"；但还没有成熟的"某实体的稳定 sentiment neuron"文献体系。
- 对金融任务的推断是：`ticker / 公司名` 很可能自带 `polarity prior / risk prior / sector prior`。检测时应做 `entity masking`、`ticker anonymization`、`neighbor-entity substitution`，看性能是否异常下跌。

**4. Context vs parametric memory competition**
- [RECOMMEND DOWNLOAD] [Entity-Based Knowledge Conflicts in Question Answering](https://arxiv.org/abs/2109.05052) (Longpre et al., 2021)：基础框架。context 与 parametric knowledge 冲突时，模型常会 **hallucinate rather than read**。
- [RECOMMEND DOWNLOAD] [Cutting Off the Head Ends the Conflict: A Mechanism for Interpreting and Mitigating Knowledge Conflicts in Language Models](https://arxiv.org/abs/2402.18154) (Jin et al., 2024)：发现后层存在 **memory heads** 和 **context heads**，冲突出现在两条信息流被整合的点。
- [RECOMMEND DOWNLOAD] [Taming Knowledge Conflicts in Language Models](https://arxiv.org/abs/2503.10996) (Li et al., 2025)：修正了上面的过于干净的二分法。很多高影响 head 同时承载 context 和 memory，存在 **superposition**。
- [RECOMMEND DOWNLOAD] [On Mechanistic Circuits for Extractive Question-Answering](https://arxiv.org/abs/2502.08059) (Basu et al., 2025)：`context-faithfulness circuit` 和 `memory-faithfulness circuit` 差异很大，前者更小、更 attention-centric，后者更分布式且更依赖 MLP。
- [Deciphering the Interplay of Parametric and Non-parametric Memory in Retrieval-augmented Language Models](https://arxiv.org/abs/2410.05162) (Farahani & Johansson, 2024)：在 Atlas 类 RAG 中，当 context 被判定 relevant 时，模型更偏向 context。
- [Studying Large Language Model Behaviors Under Context-Memory Conflicts With Real Documents](https://arxiv.org/abs/2404.16032) (Kortukov et al., 2024)：真实文档场景下冲突没合成 benchmark 那么极端，但 **parametric bias 仍在**。
- [Analysing the Residual Stream of Language Models Under Knowledge Conflicts](https://arxiv.org/abs/2410.16090) (Zhao et al., 2024)：冲突信号在 residual stream 中可被 probe 到，这对"检测器而非编辑器"尤其重要。
- 结论不是"context 总赢"或"memory 总赢"，而是：**优先级取决于知识类型、实体 prior 强度、context 显著性、以及是否有专门的 context-faithfulness heads 被激活。**

**5. Knowledge editing 和 fact localization**
- [RECOMMEND DOWNLOAD] [Knowledge Neurons in Pretrained Transformers](https://arxiv.org/abs/2104.08696) (Dai et al., 2022) 和 [RECOMMEND DOWNLOAD] [Mass-Editing Memory in a Transformer](https://arxiv.org/abs/2210.07229) (Meng et al., 2023) 仍是"可编辑性 implies 可操作局部机制"的核心起点。
- 但 [RECOMMEND DOWNLOAD] [Does Localization Inform Editing? Surprising Differences in Causality-Based Localization vs. Knowledge Editing in Language Models](https://arxiv.org/abs/2301.04213) (Hase et al., 2023) 和 [Does Editing Provide Evidence for Localization?](https://arxiv.org/abs/2502.11447) (Wang & Veitch, 2025) 都在提醒：**编辑成功不等于定位正确**。
- [RECOMMEND DOWNLOAD] [MQuAKE: Assessing Knowledge Editing in Language Models via Multi-Hop Questions](https://arxiv.org/abs/2305.14795) (Zhong et al., 2023) 与 [RECOMMEND DOWNLOAD] [Propagation and Pitfalls: Reasoning-based Assessment of Knowledge Editing through Counterfactual Tasks](https://arxiv.org/abs/2401.17585) (Hua et al., 2024) 显示：**单事实 edit 成功，不代表相关事件链/推理链会同步更新。**
- [CaKE: Circuit-aware Editing Enables Generalizable Knowledge Learners](https://arxiv.org/abs/2503.16356) (Yao et al., 2025) 和 [ACE: Attribution-Controlled Knowledge Editing for Multi-hop Factual Recall](https://arxiv.org/abs/2510.07896) (Yang et al., 2025) 都表明 multi-hop / reasoning 场景需要 **editing reasoning pathways**，而不是只改一个事实槽。
- 对你们的启发很直接：如果想看"删掉某类记忆后模型行为怎么变"，不要只做单点 fact edit；更应该做 **class-level subspace/circuit intervention**，再看 `direct recall`、`multi-hop reasoning`、`context conflict`、`temporal alignment` 四类指标是否同时变化。

**6. Temporal knowledge**
- [RECOMMEND DOWNLOAD] [Language Models Represent Space and Time](https://arxiv.org/abs/2310.02207) (Gurnee & Tegmark, 2024)：最强 mechanistic 证据，时间在表示空间里是**可线性解码**的，并可定位到 time neurons。
- [RECOMMEND DOWNLOAD] [Set the Clock: Temporal Alignment of Pretrained Language Models](https://arxiv.org/abs/2402.16797) (Zhao et al., 2024)：pretrained LM 往往偏向更早年份的知识，即使训练截断更晚，也会回答得像更早时间点。这说明时间知识不是"最新事实自动优先"，而像一个**需要被对齐的 latent state**。
- [Temporal Alignment of Time Sensitive Facts with Activation Engineering](https://arxiv.org/abs/2505.14158) (Govindan et al., 2025)：这种时间状态可以通过 activation engineering 在不微调的情况下被 steering。
- [Time Course MechInterp: Analyzing the Evolution of Components and Knowledge in Large Language Models](https://arxiv.org/abs/2506.03434) (Hakimi et al., 2025)：知识形成过程有阶段性，组件会从 `general` 转向 `entity / relation / fact-specific`，FFN 比 attention 更稳定。
- 对金融新闻最关键的一点是：**temporal leakage 不能只看"模型知不知道结果"，还要看"模型默认激活的是哪个时间截面"。**

**对金融新闻泄露检测的直接启示**
- 把泄露拆成四类测：`atomic fact leakage`、`event-outcome association leakage`、`entity prior leakage`、`temporal leakage`。这四类很可能不是同一机制。
- 做 `entity anonymization / ticker masking / neighbor-entity substitution`。若性能大幅掉，说明模型在用 entity prior，而不只是读新闻。
- 做 `direct fact prompt` 对比 `context-mediated prompt`。若 direct 好、mediated 差，更像 parametric fact；若 mediated 也很强，可能已形成 richer circuit。
- 做 `context-memory conflict` 基准，尤其用真实新闻文档而非合成句子；再 probe residual stream 或 attention attribution，看模型到底在用 prompt 还是用参数记忆。
- 做 `year-conditioned / date-swapped` temporal tests。若换年份提示就能显著改答案，说明时间更像 steerable latent state；若改不了，说明旧 parametric memory 占优。
- "信源出处泄露"目前最难。到 **2026-04-06** 为止，prompt 内 source attribution 已有 mechanistic 入口，但"参数里是否单独存了 Reuters/Bloomberg/WSJ 来源标签"几乎还是开放问题。

如果只选一批先读，我会优先下这些：
[Dissecting Recall of Factual Associations in Auto-Regressive Language Models](https://arxiv.org/abs/2304.14767) [RECOMMEND DOWNLOAD]  
[Co-occurrence is not Factual Association in Language Models](https://arxiv.org/abs/2409.14057) [RECOMMEND DOWNLOAD]  
[On Mechanistic Circuits for Extractive Question-Answering](https://arxiv.org/abs/2502.08059) [RECOMMEND DOWNLOAD]  
[Taming Knowledge Conflicts in Language Models](https://arxiv.org/abs/2503.10996) [RECOMMEND DOWNLOAD]  
[Friends and Grandmothers in Silico: Localizing Entity Cells in Language Models](https://arxiv.org/abs/2604.01404) [RECOMMEND DOWNLOAD]  
[Set the Clock: Temporal Alignment of Pretrained Language Models](https://arxiv.org/abs/2402.16797) [RECOMMEND DOWNLOAD]

如果你愿意，我下一步可以把这些论文整理成一个更偏实验设计的表格：`论文 -> 机制假说 -> 可迁移到金融泄露检测的实验设计 -> 预期可观测信号`。
