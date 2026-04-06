# Literature Search: Retrieval, Temporal, and Causal Contamination Methods

Search date: 2026-04-05

## Overall takeaways

The closest methodological matches to your planned design are in three clusters:

1. Context-faithfulness / RAG hallucination papers that explicitly create conflicts between retrieved evidence and model memory.
2. Temporal-cutoff papers that use dated data or continuously refreshed benchmarks to reduce contamination.
3. Causal memorization papers that manipulate exposure frequency, insert canaries, or use influence-style attribution.

The weakest area, in this search pass, is direct work on contamination in Chinese financial NLP. I found several strong Chinese finance benchmark papers, but not many papers that directly study contamination in that subdomain. Those are still useful because they define the evaluation surfaces where your method could contribute.

I also did not find a clean, canonical regression-discontinuity paper around training cutoffs. The strongest "natural experiment" papers instead use dated probes, explicit temporal splits, or continuously updated post-cutoff benchmarks.

## A. Task-Induced Retrieval / Evidence Intrusion

### Context-faithful Prompting for Large Language Models
Authors: Wenxuan Zhou, Sheng Zhang, Hoifung Poon, Muhao Chen
Year: 2023
Venue: Findings of EMNLP 2023
URL: https://arxiv.org/abs/2303.11315

Method summary: The paper studies cases where the provided context conflicts with a model's prior knowledge, then uses retrieval of in-context demonstrations plus post-editing to push the answer back toward the supplied evidence. The core evaluation question is whether the model follows the context, abstains, or falls back to parametric memory when knowledge conflicts are present.

Relevance to our project: This is a direct analog for "evidence intrusion." Your proposed counterfactual article edits play the same role as their conflict-setting contexts, making this paper useful for prompt design, evaluation framing, and conflict-aware analysis.

### ReEval: Automatic Hallucination Evaluation for Retrieval-Augmented Large Language Models via Transferable Adversarial Attacks
Authors: Xiaodong Yu, Hao Cheng, Xiaodong Liu, Dan Roth, Jianfeng Gao
Year: 2023
Venue: arXiv
URL: https://arxiv.org/abs/2310.12516

Method summary: ReEval adversarially perturbs retrieved evidence while preserving the original question, then checks whether the model updates its answer in response to the changed evidence. The authors argue that standard QA-style evaluation misses hallucinations in RAG because a model can answer correctly from memory even when it ignores the retrieved documents.

Relevance to our project: This is one of the closest papers to your methodology discussion. It gives a concrete template for "same question, changed evidence, does the model move?" which maps directly onto your evidence-intrusion and targeted-counterfactual design.

### Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style
Authors: Yuepei Li, Kang Zhou, Qiao Qiao, Bach Nguyen, Qing Wang, Qi Li
Year: 2024
Venue: arXiv preprint; later Findings of ACL 2025
URL: https://arxiv.org/abs/2409.10955

Method summary: This paper systematically varies how strongly a fact is represented in model memory and how that fact is expressed in the supplied evidence. It shows that stronger memorized facts make models more likely to override context, while more explicit extractive evidence improves faithfulness.

Relevance to our project: This is strong support for your central claim that task format and evidence style can modulate apparent leakage on fixed inputs. It is especially relevant for arguing that decomposition or evidence-oriented prompting may reduce contamination exposure without changing the underlying model.

### Model Internals-based Answer Attribution for Trustworthy Retrieval-Augmented Generation
Authors: Jirui Qi, Gabriele Sarti, Raquel Fernandez, Arianna Bisazza
Year: 2024
Venue: EMNLP 2024
URL: https://arxiv.org/abs/2406.13663

Method summary: The paper proposes MIRAGE, which uses model-internal signals to attribute generated answers back to retrieved passages instead of relying only on surface lexical overlap. It treats unsupported answer content as an attribution failure and shows that internal attribution can improve faithfulness auditing in RAG.

Relevance to our project: If you want a second-stage validator for whether outputs are actually grounded in the article, this is one of the better attribution-style references. It is useful for building an "evidence support" score rather than relying only on label stability.

### Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmented Generation
Authors: Di Wu, Jia-Chen Gu, Fan Yin, Nanyun Peng, Kai-Wei Chang
Year: 2024
Venue: EMNLP 2024
URL: https://arxiv.org/abs/2406.13692

Method summary: This paper monitors faithfulness during decoding, rather than only after generation, by checking whether generated content remains synchronized with retrieved evidence. The method flags unsupported generations as they emerge token-by-token and is meant to catch context drift in RAG systems.

Relevance to our project: Conceptually, this paper is useful because it operationalizes evidence intrusion online rather than ex post. Even if you do not use their method directly, it sharpens the distinction between context-conditioned generation and generation that wanders back to memory.

### FaithfulRAG: Fact-Level Conflict Modeling for Context-Faithful Retrieval-Augmented Generation
Authors: Qinggang Zhang, Zhishang Xiang, Yilin Xiao, Le Wang, Junhui Li, Xinrun Wang, Jinsong Su
Year: 2025
Venue: ACL 2025
URL: https://arxiv.org/abs/2506.08938

Method summary: FaithfulRAG explicitly models fact-level conflicts between retrieved context and the model's parametric knowledge, then uses that conflict structure to suppress memory-driven generations. The paper focuses on situations where vanilla RAG answers are plausible but not actually supported by the provided evidence.

Relevance to our project: This is highly aligned with your "task-induced retrieval" framing. It offers a recent, explicit formulation of the conflict between retrieved evidence and memorized knowledge that your finance-news design is trying to expose.

## B. Temporal Discontinuity / Training Cutoff as Natural Experiment

### Dated Data: Tracing Knowledge Cutoffs in Large Language Models
Authors: Jeffrey Cheng, Marc Marone, Orion Weller, Dawn Lawrie, Daniel Khashabi, Benjamin Van Durme
Year: 2024
Venue: arXiv
URL: https://arxiv.org/abs/2403.12958

Method summary: The paper constructs dated probes to estimate where a model's knowledge begins to fall off over calendar time. Rather than assuming a single hard cutoff, it measures temporal decay and shows that freshness varies by topic and model.

Relevance to our project: This is one of the best direct references for using time as a contamination diagnostic. It supports the logic behind pre/post-boundary analysis and argues for estimating a temporal profile instead of relying on a single nominal cutoff date.

### LiveBench: A Challenging, Contamination-Limited LLM Benchmark
Authors: Colin White, Samuel Dooley, Manley Roberts, Arka Pal, Ben Feuer, Siddhartha Jain, Ravid Shwartz-Ziv, Neel Jain, Khalid Saifullah, Sreemanti Dey, Shubh-Agrawal, Sandeep Singh Sandha, Siddartha Naidu, Chinmay Hegde, Yann LeCun, Tom Goldstein, Willie Neiswanger, Micah Goldblum
Year: 2024
Venue: arXiv
URL: https://arxiv.org/abs/2406.19314

Method summary: LiveBench continuously refreshes benchmark questions with recent, verifiable material to keep evaluation items outside typical training windows. The benchmark is designed to make contamination harder by construction and to be updated regularly rather than frozen once.

Relevance to our project: This is the clearest benchmark-design reference for contamination-resistant evaluation. It is especially useful for motivating why your financial benchmark should treat article date as a first-class design variable.

### AntiLeakBench: Preventing Data Contamination by Automatically Constructing Benchmarks with Updated Real-World Knowledge
Authors: Xiaobao Wu, Liangming Pan, Yuxi Xie, Ruiwen Zhou, Shuai Zhao, Yubo Ma, Mingzhe Du, Rui Mao, Anh Tuan Luu, William Yang Wang
Year: 2024
Venue: arXiv
URL: https://arxiv.org/abs/2412.13670

Method summary: AntiLeakBench automatically builds benchmark items from newly emerged facts so the evaluation set stays post-cutoff relative to existing models. The core idea is procedural freshness: contamination resistance comes from continuously harvesting new knowledge rather than retroactive filtering alone.

Relevance to our project: This is directly relevant for benchmark maintenance if you extend the paper beyond CLS-Leak-1000. It also supports the argument that contamination-resistant evaluation increasingly depends on dynamic refresh rather than static train-test separation.

### DatedGPT: Preventing Lookahead Bias in Large Language Models with Time-Aware Pretraining
Authors: Yutong Yan, Raphael Tang, Zhenyu Gao, Wenxi Jiang, Yao Lu
Year: 2026
Venue: arXiv
URL: https://arxiv.org/abs/2603.11838

Method summary: DatedGPT incorporates time-aware pretraining constraints so that the model's accessible information respects calendar order. The paper is explicitly framed around avoiding lookahead bias, making temporal discipline part of both training and evaluation rather than only a benchmark-side concern.

Relevance to our project: This is the closest exact match to your "training cutoff as natural experiment" framing. It is useful both substantively and rhetorically because it treats temporal boundaries as an identification tool instead of an afterthought.

### MMLU-CF: A Contamination-free Multi-task Language Understanding Benchmark
Authors: Qihao Zhao, Yangyu Huang, Tengchao Lv, Lei Cui, Qinzheng Sun, Shaoguang Mao, Xin Zhang, Ying Xin, Qiufeng Yin, Scarlett Li, Furu Wei
Year: 2024
Venue: arXiv
URL: https://arxiv.org/abs/2412.15194

Method summary: MMLU-CF rebuilds a broad multitask benchmark around explicit contamination controls, aiming to preserve the breadth of MMLU while reducing overlap with pretraining data. The benchmark is not purely temporal, but it belongs to the same family of contamination-resistant evaluation design.

Relevance to our project: This is a useful adjacent reference if reviewers ask for non-finance examples of contamination-aware benchmark construction. It broadens the methodological frame beyond "freshness only" to include benchmark rebuilding and decontamination by design.

## C. Randomized Exposure / Continued Pretraining as Causal Identification

### Counterfactual Memorization in Neural Language Models
Authors: Chiyuan Zhang, Daphne Ippolito, Katherine Lee, Matthew Jagielski, Florian Tramer, Nicholas Carlini
Year: 2021
Venue: arXiv
URL: https://arxiv.org/abs/2112.12938

Method summary: This paper introduces a counterfactual framework for memorization by comparing what a model does when a training example is present versus altered or absent. The design is explicitly causal: memorization is defined by the change in model behavior induced by controlled changes to the training set.

Relevance to our project: This is probably the single best citation for your "randomized exposure / causal identification" bucket. It gives formal backing for treating contamination as an effect of exposure rather than just an observational correlation.

### The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks
Authors: Nicholas Carlini, Chang Liu, Ulfar Erlingsson, Jernej Kos, Dawn Song
Year: 2019
Venue: USENIX Security 2019
URL: https://arxiv.org/abs/1802.08232

Method summary: The paper inserts random canaries into training data and then measures their exposure under extraction attacks. This is the foundational canary-insertion design for demonstrating that rare strings can be memorized and later reproduced.

Relevance to our project: Even though your project is not a privacy paper, the logic is directly transferable. Canary-style intervention is the cleanest randomized-exposure template for proving that observed outputs come from training data rather than generic reasoning.

### Quantifying Memorization Across Neural Language Models
Authors: Nicholas Carlini, Daphne Ippolito, Matthew Jagielski, Katherine Lee, Florian Tramer, Chiyuan Zhang
Year: 2022
Venue: arXiv
URL: https://arxiv.org/abs/2202.07646

Method summary: This paper measures memorization across many language models and links it to sequence repetition, rarity, and model scale. It is useful because it turns memorization into a comparative empirical object rather than a binary anecdote.

Relevance to our project: This paper helps justify why contamination should vary with exposure frequency and example distinctiveness. That is relevant if you later want to relate article age, duplication, or syndication density to leakage rates.

### What Neural Networks Memorize and Why: Discovering the Long Tail via Influence Estimation
Authors: Vitaly Feldman, Chiyuan Zhang
Year: 2020
Venue: arXiv
URL: https://arxiv.org/abs/2008.03703

Method summary: Feldman and Zhang use influence-style analysis to identify which training examples most strongly drive memorized behavior, showing that rare long-tail examples are disproportionately responsible. The paper connects memorization to data distribution and training-example influence rather than treating it as a monolithic model property.

Relevance to our project: This is an important bridge between memorization theory and training-data attribution. If you later run open-model experiments, it gives a direct citation path for influence-based familiarity or source-attribution analyses.

### TRAK: Attributing Model Behavior at Scale
Authors: Sung Min Park, Kristian Georgiev, Andrew Ilyas, Guillaume Leclerc, Aleksander Madry
Year: 2023
Venue: arXiv
URL: https://arxiv.org/abs/2303.14186

Method summary: TRAK is a scalable training-data attribution method designed to estimate which training points are most responsible for a given model prediction. It is not specific to memorization, but it is one of the most practical modern tools for turning "which examples caused this output?" into an empirical question.

Relevance to our project: This is the most actionable attribution reference if you eventually add white-box validation on an open model. It would let you connect observed leakage-like outputs to concrete training examples or near-neighbors in a scalable way.

### Extracting Training Data from Large Language Models
Authors: Nicholas Carlini, Florian Tramer, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, Tom Brown, Dawn Song, Ulfar Erlingsson, Alina Oprea, Colin Raffel
Year: 2020
Venue: USENIX Security 2021
URL: https://arxiv.org/abs/2012.07805

Method summary: The paper shows that large language models can be induced to emit verbatim training examples, especially rare or duplicated ones, through black-box querying. It is not a randomized-exposure paper per se, but it establishes the downstream observability of memorization once exposure has occurred.

Relevance to our project: This is a useful foundation citation if reviewers push on whether memorized training data is actually recoverable in outputs. It complements the more causal papers above by showing that memorization can be behaviorally detectable.

## D. Chinese Financial NLP + Contamination

Direct contamination papers for Chinese financial NLP were sparse in this search pass. The papers below are the closest benchmark and evaluation anchors. They are useful as dataset infrastructure and threat-model context, but they mostly do not solve contamination directly.

### BBT-Fin: Comprehensive Construction of Chinese Financial Domain Pre-trained Language Model, Corpus and Benchmark
Authors: Dakuan Lu, Hengkui Wu, Jiaqing Liang, Yipei Xu, Qianyu He, Yipeng Geng, Mengkun Han, Yingsi Xin, Yanghua Xiao
Year: 2023
Venue: arXiv
URL: https://arxiv.org/abs/2302.09432

Method summary: BBT-Fin builds a Chinese financial corpus, a domain-specific pretrained language model, and an accompanying benchmark. It is important because it documents how Chinese finance data and evaluation resources are assembled, which is exactly where contamination risks can be introduced.

Relevance to our project: This is a good starting point for understanding the Chinese financial benchmark landscape that your method is entering. It is also useful for arguing that domain-specific corpora and benchmarks create a real contamination threat if provenance and timing are not explicitly controlled.

### FinEval: A Chinese Financial Domain Knowledge Evaluation Benchmark for Large Language Models
Authors: Xin Guo, Haotian Xia, Zhaowei Liu, Hanyang Cao, Zhi Yang, Zhiqiang Liu, Sizhe Wang, Jinyi Niu, Chuqi Wang, Yanhui Wang, Xiaolong Liang, Xiaoming Huang, Bing Zhu, Zhongyu Wei, Yun Chen, Weining Shen, Liwen Zhang
Year: 2023
Venue: arXiv
URL: https://arxiv.org/abs/2308.09975

Method summary: FinEval evaluates LLMs on Chinese financial-domain knowledge and reasoning tasks. The emphasis is broad financial competence rather than contamination, but the benchmark is a strong example of the sort of domain evaluation that can be vulnerable to training overlap.

Relevance to our project: FinEval is useful as a comparison point for what existing Chinese finance benchmarks measure and what they typically omit. In particular, it motivates why your project's contamination-aware design would add value beyond raw benchmark accuracy.

### CFBenchmark: Chinese Financial Assistant Benchmark for Large Language Model
Authors: Yang Lei, Jiangtong Li, Dawei Cheng, Zhijun Ding, Changjun Jiang
Year: 2023
Venue: arXiv
URL: https://arxiv.org/abs/2311.05812

Method summary: CFBenchmark evaluates Chinese financial assistant behavior across finance-oriented tasks and interaction settings. It is more assistant-style than article-grounded, but it reflects the same application domain where benchmark contamination can distort claims of financial competence.

Relevance to our project: This paper is useful for situating your work within Chinese financial-agent evaluation. It helps show that many finance benchmarks focus on capability, whereas your contribution would focus on whether that capability is genuinely article-grounded rather than memorized.

### CFinBench: A Comprehensive Chinese Financial Benchmark for Large Language Models
Authors: Ying Nie, Binwei Yan, Tianyu Guo, Hao Liu, Haoyu Wang, Wei He, Binfan Zheng, Weihao Wang, Qiang Li, Weijian Sun, Yunhe Wang, Dacheng Tao
Year: 2024
Venue: arXiv preprint; later NAACL 2025
URL: https://arxiv.org/abs/2407.02301

Method summary: CFinBench is a recent comprehensive Chinese financial benchmark covering multiple task types for LLM evaluation. Like FinEval and CFBenchmark, it is mainly a capability benchmark, but it provides a modern benchmark surface where contamination controls are especially important because many tasks use public, web-visible financial knowledge.

Relevance to our project: This is probably the most relevant contemporary Chinese finance benchmark reference. If you need to argue that contamination-aware evaluation is missing in current Chinese financial LLM work, CFinBench is a strong anchor.

## Suggested shortlist for immediate reading

If the goal is to refine your experimental design, I would prioritize these first:

1. ReEval
2. Investigating Context-Faithfulness in Large Language Models
3. Dated Data
4. Counterfactual Memorization in Neural Language Models
5. The Secret Sharer
6. CFinBench

## Gaps from this search pass

1. I did not find a canonical regression-discontinuity paper built exactly around LLM training cutoffs.
2. I did not find a strong paper focused specifically on contamination in Chinese financial benchmarks; the best D-section papers are benchmark/evaluation papers rather than contamination-identification papers.
3. If we want a deeper D-section, the next pass should search Chinese-language sources, finance conference proceedings, and benchmark documentation for decontamination protocols rather than only paper titles and abstracts.
