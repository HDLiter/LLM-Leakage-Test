# Counterfactual / Perturbation-Based Methods for LLM Memorization, Contamination, and Evidence Intrusion

## Scope and quick takeaways

This note focuses on papers that use counterfactual edits, paraphrases, masked spans, cloze probes, prompt/task reformulations, or other input mutations to detect memorization, benchmark contamination, or unsupported generation. I prioritize methods that are close to an excess-invariance / evidence-intrusion (EI) framing: keep the task intent fixed, perturb the surface form or local evidence, and measure whether model behavior reveals stored training data or parametric-memory spillover.

Two naming clarifications:

- The AAAI 2024 paper `Task Contamination: Language Models May Not Be Few-Shot Anymore` is by **Changmao Li and Jeffrey Flanigan**, not Golchin and Surdeanu.
- **Shahriar Golchin and Mihai Surdeanu** are the authors of the closely related ICLR 2024 paper `Time Travel in LLMs: Tracing Data Contamination in Large Language Models`, and Shahriar Golchin is also a coauthor on the `Data Contamination Report from the 2024 CONDA Shared Task`.

High-level synthesis:

- The strongest direct precedents for an EI-style counterfactual evaluation are **Yang et al. (rephrased samples)**, **Zhu et al. (Clean-Eval)**, **Fang et al. (LastingBench)**, **Oren et al. (shuffle/order perturbations)**, **Deng et al. (TS-Guessing cloze probes)**, and **Lopez-Lira et al. (masked reconstruction in finance)**.
- The clearest papers on **edit magnitude / locality / surface similarity** are **Yang et al.**, **Mehrbakhsh et al.**, **Carlini et al. (Quantifying Memorization)**, **Zhou et al. (entity-level memorization)**, and **Zhang et al. (Counterfactual Memorization)**.
- The best grounding/evidence-intrusion analogs are **Context-faithful Prompting**, **How Well Do LLMs Truly Ground?**, **When Context Leads but Parametric Memory Follows**, and **MiniCheck**.
- I found **very little finance-specific perturbation-based contamination work**. The closest direct paper is **Lopez-Lira, Tang, and Zhu (2025)**.

## 1. Semantics-preserving rewrites and benchmark perturbations

### Rethinking Benchmark and Contamination for Language Models with Rephrased Samples
- **Authors / year / venue:** Shuo Yang, Wei-Lin Chiang, Lianmin Zheng, Joseph E. Gonzalez, Ion Stoica. 2023. arXiv preprint.
- **URL:** https://arxiv.org/abs/2311.04850
- **Method summary:** This paper shows that common decontamination methods based on string overlap are too weak because simple paraphrases and translations can preserve benchmark semantics while evading n-gram filters. The authors build an LLM-based decontaminator and report substantial hidden overlap, including 8-18% HumanEval overlap in RedPajama-Data-1T and StarCoder-Data.
- **Relation to EI / counterfactual approach:** This is one of the closest direct precedents for EI. It operationalizes contamination through semantically equivalent rewrites, so it strongly supports using paraphrase-preserving counterfactuals to distinguish genuine ability from surface-form memorization.

### CLEAN-EVAL: Clean Evaluation on Contaminated Large Language Models
- **Authors / year / venue:** Wenhong Zhu, Hongkun Hao, Zhiwei He, Yun-Ze Song, Jiao Yueyang, Yumeng Zhang, Hanxu Hu, Yiran Wei, Rui Wang, Hongyuan Lu. 2024. Findings of NAACL 2024.
- **URL:** https://aclanthology.org/2024.findings-naacl.53/
- **Method summary:** Clean-Eval paraphrases and back-translates contaminated benchmark items, then filters generated candidates with semantic scoring so the retained items are nearly equivalent in meaning but different in surface form. The goal is not just to detect leakage but to recover a cleaner evaluation set whose score is less inflated by memorized originals.
- **Relation to EI / counterfactual approach:** This is effectively a benchmark-level EI intervention: preserve task meaning, break memorized surface forms, and measure the score drop. It is especially relevant if your EI metric compares original prompts to semantically matched rewrites.

### LastingBench: Defend Benchmarks Against Knowledge Leakage
- **Authors / year / venue:** Yixiong Fang, Tianran Sun, Yuling Shi, Min Wang, Xiaodong Gu. 2025. Findings of EMNLP 2025.
- **URL:** https://aclanthology.org/2025.findings-emnlp.993/
- **Method summary:** LastingBench identifies likely leakage points in benchmark context via perturbation and then rewrites those local spans into counterfactual versions while preserving the benchmark's intended capability. The resulting benchmark is explicitly designed to disrupt memorized shortcuts without changing the underlying evaluation target.
- **Relation to EI / counterfactual approach:** This is almost a direct benchmark-defense analogue of an EI metric. The key design move is local counterfactual editing of the exact spans that appear to trigger recall, which matches an edit-locality framing very closely.

### Confounders in Instance Variation for the Analysis of Data Contamination
- **Authors / year / venue:** Behzad Mehrbakhsh, Dario Garigliotti, Fernando Martinez-Plumed, Jose Hernandez-Orallo. 2024. CONDA 2024.
- **URL:** https://aclanthology.org/2024.conda-1.2/
- **Method summary:** This paper studies whether rephrasings and exemplar changes really isolate contamination, showing that such perturbations can alter not only leakage but also intrinsic instance difficulty. On an addition task with fine-tuned LLaMA-2 models, the authors show that template choice and template diversity can either exaggerate or hide contamination effects.
- **Relation to EI / counterfactual approach:** This is one of the most important caveats for an EI metric. It directly warns that edit magnitude, template difficulty, and exemplar diversity are confounders, so counterfactual comparisons need tightly matched perturbations and difficulty controls.

## 2. Black-box contamination tests via shuffling, masking, prefix completion, or output distributions

### Proving Test Set Contamination in Black-Box Language Models
- **Authors / year / venue:** Yonatan Oren, Nicole Meister, Niladri S. Chatterji, Faisal Ladhak, Tatsunori Hashimoto. 2024. ICLR 2024 oral.
- **URL:** https://openreview.net/forum?id=KS8mIvetg2
- **Method summary:** Oren et al. propose a contamination test with false-positive guarantees based on exchangeability: if a benchmark is uncontaminated, all orderings should be equally likely. They detect contamination by comparing the likelihood of the canonical benchmark ordering against shuffled orderings, exploiting the fact that memorized datasets often preserve example order.
- **Relation to EI / counterfactual approach:** This is a powerful example of a minimal perturbation test: the content stays fixed and only ordering changes. It suggests that an EI metric does not need large semantic rewrites; even structurally tiny mutations can reveal memorized benchmark artifacts.

### Investigating Data Contamination in Modern Benchmarks for Large Language Models
- **Authors / year / venue:** Chunyuan Deng, Yilun Zhao, Xiangru Tang, Mark Gerstein, Arman Cohan. 2024. NAACL 2024.
- **URL:** https://aclanthology.org/2024.naacl-long.482/
- **Method summary:** This paper combines retrieval-based overlap search with `Testset Slot Guessing (TS-Guessing)`, a black-box protocol that masks a wrong answer option or an unlikely word and asks the model to fill the slot. The surprising ability of commercial models to recover the hidden content from benchmark items is used as evidence of contamination.
- **Relation to EI / counterfactual approach:** TS-Guessing is a direct cloze-style probe for memorized content and is especially relevant if your counterfactuals involve masking entities, dates, or answer-bearing spans. It is a good black-box companion to more semantic rewrite-based EI tests.

### Time Travel in LLMs: Tracing Data Contamination in Large Language Models
- **Authors / year / venue:** Shahriar Golchin, Mihai Surdeanu. 2024. ICLR 2024.
- **URL:** https://arxiv.org/abs/2308.08493
- **Method summary:** The paper detects contamination through guided instruction completion: the prompt names the dataset and partition and gives a variable-length prefix of a reference example, then measures whether the model reconstructs the held-out suffix. Contamination is inferred at both instance and partition level using overlap metrics and GPT-4-based match judgments.
- **Relation to EI / counterfactual approach:** This is a strong precursor for prefix-based or local-edit EI probes. It shows that prompt framing itself can expose contamination and that partial-prefix completion is a sensitive way to test recall from small local cues.

### Generalization or Memorization: Data Contamination and Trustworthy Evaluation for Large Language Models
- **Authors / year / venue:** Yihong Dong, Xue Jiang, Huanyu Liu, Zhi Jin, Bin Gu, Mengfei Yang, Ge Li. 2024. Findings of ACL 2024.
- **URL:** https://aclanthology.org/2024.findings-acl.716/
- **Method summary:** Dong et al. propose `CDD`, which detects contamination from the peakedness of sampled output distributions, and `TED`, which corrects contaminated evaluations using output-distribution adjustments. The method does not require direct access to training data and is designed to detect even implicit contamination.
- **Relation to EI / counterfactual approach:** This is more distributional than counterfactual, but it is a useful baseline. It gives a non-edit comparator for any EI metric and is relevant if you want to show that counterfactual invariance adds signal beyond output-confidence or peakedness alone.

### Detecting Pretraining Data from Large Language Models
- **Authors / year / venue:** Weijia Shi, Anirudh Ajith, Mengzhou Xia, Yangsibo Huang, Daogao Liu, Terra Blevins, Danqi Chen, Luke Zettlemoyer. 2023. RegML 2023 workshop.
- **URL:** https://openreview.net/forum?id=ZLJ6XRbdaC
- **Method summary:** This is the `Min-K% Prob` paper. It frames pretraining-data detection as a black-box decision problem and uses the probability of the lowest-probability tokens in a text to infer whether the model likely saw that text during training.
- **Relation to EI / counterfactual approach:** This is not perturbation-based, but it is the main non-counterfactual baseline you should compare against because it is widely cited and explicitly addresses contaminated benchmark examples. If EI outperforms Min-K% on edited or paraphrased instances, that strengthens the case that EI captures counterfactual sensitivity rather than just token-level familiarity.

### Benchmarking Benchmark Leakage in Large Language Models
- **Authors / year / venue:** Ruijie Xu, Zengzhi Wang, Run-Ze Fan, Pengfei Liu. 2024. arXiv preprint.
- **URL:** https://arxiv.org/abs/2404.18824
- **Method summary:** This paper builds a leakage-detection pipeline based on perplexity and n-gram accuracy and evaluates 31 LLMs in mathematical reasoning settings. It is broader benchmarking infrastructure rather than a perturbation method per se.
- **Relation to EI / counterfactual approach:** Useful as a backdrop and baseline, but less aligned with counterfactual editing than Yang, Deng, Oren, or Fang. Its main value for EI is as a non-perturbative benchmark against which a mutation-based detector can be compared.

## 3. Task design and prompt formulation as contamination signals

### Task Contamination: Language Models May Not Be Few-Shot Anymore
- **Authors / year / venue:** Changmao Li, Jeffrey Flanigan. 2024. AAAI 2024.
- **URL:** https://arxiv.org/abs/2312.16337
- **Method summary:** The authors compare zero-shot and few-shot performance on datasets released before versus after model training-data creation dates, while controlling for dataset difficulty. The result is a temporal contamination argument: older tasks are systematically easier, which suggests that apparent few-shot ability is partly a contamination artifact rather than a pure in-context-learning effect.
- **Relation to EI / counterfactual approach:** This paper is central for your "task design matters" framing. It supports the idea that prompt/task formulation is itself part of the contamination measurement problem and motivates testing whether the same underlying content yields different leakage signals under different task framings.

### Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks
- **Authors / year / venue:** Zhaofeng Wu, Linlu Qiu, Alexis Ross, Ekin Akyurek, Boyuan Chen, Bailin Wang, Najoung Kim, Jacob Andreas, Yoon Kim. 2024. arXiv preprint.
- **URL:** https://arxiv.org/abs/2307.02477
- **Method summary:** Across 11 tasks, this paper compares default task formulations to counterfactual variants that violate ordinary task conventions, such as different base systems, altered indexing rules, or changed structural assumptions. Performance drops sharply on counterfactual variants even when the underlying reasoning problem is supposed to be analogous.
- **Relation to EI / counterfactual approach:** This is not a contamination paper, but it is highly relevant methodologically. It shows that counterfactual task design can separate genuine reasoning from recitation of default conventions, which is conceptually close to separating true generalization from memorized benchmark priors.

### Don't Make Your LLM an Evaluation Benchmark Cheater
- **Authors / year / venue:** Kun Zhou, Yutao Zhu, Zhipeng Chen, Wentong Chen, Wayne Xin Zhao, Xu Chen, Yankai Lin, Ji-Rong Wen, Jiawei Han. 2023. arXiv preprint.
- **URL:** https://arxiv.org/abs/2311.01964
- **Method summary:** This paper is a broad study of benchmark leakage and its effect on inflated LLM scores. Rather than proposing a single counterfactual detector, it documents how inappropriate use of benchmark-related data can dramatically change apparent performance and offers guidance for developers and benchmark maintainers.
- **Relation to EI / counterfactual approach:** This is mainly motivation rather than a direct methodological precursor. It supports the premise that score drops under controlled rewrites or task re-formulations should be treated as evidence of benchmark leakage rather than dismissed as ordinary robustness noise.

### Data Contamination Report from the 2024 CONDA Shared Task
- **Authors / year / venue:** Oscar Sainz et al., including Shahriar Golchin and Mihai Surdeanu. 2024. CONDA 2024.
- **URL:** https://aclanthology.org/2024.conda-1.4/
- **Method summary:** This is a community resource paper rather than a single detection method. It aggregates 566 reported contamination entries across 91 sources and provides a public database of contamination evidence.
- **Relation to EI / counterfactual approach:** Useful as a resource and sanity-check list rather than as a direct EI precursor. It can help select known-contaminated versus less-documented benchmarks for evaluating whether an EI metric tracks existing contamination evidence.

## 4. Counterfactual memorization, extraction, and entity-level probing

### Counterfactual Memorization in Neural Language Models
- **Authors / year / venue:** Chiyuan Zhang, Daphne Ippolito, Katherine Lee, Matthew Jagielski, Florian Tramèr, Nicholas Carlini. 2021. arXiv preprint.
- **URL:** https://arxiv.org/abs/2112.12938
- **Method summary:** This paper formalizes memorization in counterfactual terms: how model behavior would change if a specific training document were omitted. The authors estimate which examples are counterfactually memorized and trace how those examples influence validation predictions and generations.
- **Relation to EI / counterfactual approach:** This is the cleanest conceptual foundation for an EI metric. It frames memorization as sensitivity to a targeted local intervention, which is exactly the logic behind measuring behavior changes under controlled edits.

### Quantifying Memorization Across Neural Language Models
- **Authors / year / venue:** Nicholas Carlini, Daphne Ippolito, Matthew Jagielski, Katherine Lee, Florian Tramèr, Chiyuan Zhang. 2022. arXiv preprint.
- **URL:** https://arxiv.org/abs/2202.07646
- **Method summary:** Carlini et al. quantify memorization through extraction behavior and show log-linear relationships with model size, duplication count, and prompt context length. The paper is especially useful because it isolates factors that change extraction success even when the memorized content is fixed.
- **Relation to EI / counterfactual approach:** This directly informs edit magnitude and locality. It suggests that the size of the preserved context around an edited span can strongly affect memorization detection, so EI experiments should vary how much local context is held constant around the mutation.

### Extracting Training Data from Large Language Models
- **Authors / year / venue:** Nicholas Carlini, Florian Tramèr, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, Tom Brown, Dawn Song, Ulfar Erlingsson, Alina Oprea, Colin Raffel. 2020. arXiv preprint.
- **URL:** https://arxiv.org/abs/2012.07805
- **Method summary:** This is the canonical direct-extraction paper: prompt the model, sample heavily, and recover verbatim training examples including PII and rare sequences that appeared only once in training. It demonstrates memorization directly rather than through evaluation-score inflation.
- **Relation to EI / counterfactual approach:** This is the main proof that the phenomenon exists, but it is not itself counterfactual. For EI, it serves as an upper-bound style reference: if edited prompts still trigger benchmark-like or record-like outputs, your metric is probably detecting the same family of memorization behavior in a less invasive way.

### Scalable Extraction of Training Data from (Production) Language Models
- **Authors / year / venue:** Milad Nasr, Nicholas Carlini, Jonathan Hayase, Matthew Jagielski, A. Feder Cooper, Daphne Ippolito, Christopher A. Choquette-Choo, Eric Wallace, Florian Tramèr, Katherine Lee. 2023. arXiv preprint.
- **URL:** https://arxiv.org/abs/2311.17035
- **Method summary:** This paper extends extraction attacks to open, semi-open, and closed production models, including a divergence attack that makes aligned systems emit training data at much higher rates. It shows that alignment reduces but does not eliminate extractable memorization.
- **Relation to EI / counterfactual approach:** This is another important non-counterfactual anchor. It suggests that prompt formulation matters a lot for eliciting memorization, which supports the idea that EI should be tested across multiple prompt templates instead of a single format.

### Quantifying and Analyzing Entity-level Memorization in Large Language Models
- **Authors / year / venue:** Zhenhong Zhou, Jiuyang Xiang, Chaomeng Chen, Sen Su. 2023. arXiv preprint.
- **URL:** https://arxiv.org/abs/2308.15727
- **Method summary:** This paper moves from whole-sequence memorization to entity-level memorization, asking whether models can reconstruct sensitive entities from partial leakages. The authors show that LLMs can often recover entity values even when only part of the original context leaks through.
- **Relation to EI / counterfactual approach:** This is highly relevant to entity replacement and name-swapping tests. It implies that local edits may need to target all high-information cues around an entity, not just the name string itself, because associative reconstruction can survive surprisingly small mutations.

### Dissecting Recall of Factual Associations in Auto-Regressive Language Models
- **Authors / year / venue:** Mor Geva, Jasmijn Bastings, Katja Filippova, Amir Globerson. 2023. arXiv preprint.
- **URL:** https://arxiv.org/abs/2304.14767
- **Method summary:** Geva et al. study how subject-relation queries trigger factual recall inside autoregressive LMs, tracing the flow of subject and relation information to the predicted attribute. The paper is mechanistic rather than evaluation-focused, but the setup is fundamentally a cloze-style recall probe.
- **Relation to EI / counterfactual approach:** It helps explain why entity substitutions and relation paraphrases are informative counterfactuals. If EI is sensitive to changing only the subject, relation wording, or a supporting attribute, this paper provides a plausible mechanism for why those local edits alter recall.

## 5. Finance-specific and domain-adjacent evidence

### The Memorization Problem: Can We Trust LLMs' Economic Forecasts?
- **Authors / year / venue:** Alejandro Lopez-Lira, Yuehua Tang, Mingyin Zhu. 2025. arXiv preprint.
- **URL:** https://arxiv.org/abs/2504.14765
- **Method summary:** This is the clearest finance-specific paper I found. It shows that LLMs can exactly recall pre-cutoff economic and financial data, that instructions to respect historical boundaries do not stop the behavior, and that models can reconstruct masked entities and dates from minimal contextual clues.
- **Relation to EI / counterfactual approach:** This paper is directly aligned with your setup. It uses masking and partial-context reconstruction in a financial domain and explicitly argues that apparent forecasting performance on pre-cutoff data is non-identified because it may reflect memorization rather than prediction.

### Search outcome on financial NLP specifically

I did **not** find a strong cluster of finance-specific papers that use paraphrase-based or entity-swap-based contamination detection on standard financial NLP benchmarks. The Lopez-Lira et al. paper is the closest direct hit; most other perturbation-heavy contamination papers are benchmark-general rather than finance-specific. That gap itself is useful: a carefully designed EI study in finance would still look novel relative to the current literature.

## 6. Evidence intrusion, grounding, and parametric-memory spillover

The term `evidence intrusion` is not yet standardized in the literature, but several grounding and faithfulness papers study almost the same phenomenon: the model outputs information that is correct or plausible but not actually supported by the provided context.

### Context-faithful Prompting for Large Language Models
- **Authors / year / venue:** Wenxuan Zhou, Sheng Zhang, Hoifung Poon, Muhao Chen. 2023. Findings of EMNLP 2023.
- **URL:** https://aclanthology.org/2023.findings-emnlp.968/
- **Method summary:** The paper studies how to increase adherence to provided context in the presence of knowledge conflict. It finds that `opinion-based prompts` and `counterfactual demonstrations` are especially effective at making models follow the given context rather than parametric memory.
- **Relation to EI / counterfactual approach:** This is one of the strongest prompt-design analogs of evidence intrusion. It shows that prompt formulation alone can suppress or expose parametric-memory spillover, which makes it a natural design reference if EI includes prompt-conditioned evidence intrusion rates.

### How Well Do Large Language Models Truly Ground?
- **Authors / year / venue:** Hyunji Lee, Se June Joo, Chaeeun Kim, Joel Jang, Doyoung Kim, Kyoung-Woon On, Minjoon Seo. 2024. NAACL 2024.
- **URL:** https://aclanthology.org/2024.naacl-long.135/
- **Method summary:** This paper argues that a response is truly grounded only if it both uses the necessary context and stays within the bounds of that context. It introduces a dataset and a grounding metric that explicitly penalize responses that go beyond the supplied evidence.
- **Relation to EI / counterfactual approach:** This is very close to an evidence-intrusion definition. If your EI metric is meant to capture unsupported additions relative to an input article or context window, this paper provides the cleanest formal evaluation target.

### When Context Leads but Parametric Memory Follows in Large Language Models
- **Authors / year / venue:** Yufei Tao, Adam Hiatt, Erik Haake, Antonie J. Jetter, Ameeta Agrawal. 2024. EMNLP 2024.
- **URL:** https://aclanthology.org/2024.emnlp-main.234/
- **Method summary:** Using the WikiAtomic dataset, the authors vary context size and quantify how model outputs draw from local context versus global parametric memory in knowledge-consistent settings. Even with adequate context, they find a persistent parametric-memory contribution in generated responses.
- **Relation to EI / counterfactual approach:** This is an explicit measurement of parametric-memory intrusion into ostensibly grounded generation. It is highly relevant if EI is computed by comparing context-supported content against content that appears to come from background memory instead.

### MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents
- **Authors / year / venue:** Liyan Tang, Philippe Laban, Greg Durrett. 2024. EMNLP 2024.
- **URL:** https://aclanthology.org/2024.emnlp-main.499/
- **Method summary:** MiniCheck is an efficient model for checking whether claims in an LLM output are supported by grounding documents. It unifies several grounding and factuality datasets into `LLM-AggreFact` and trains models to verify evidence support efficiently.
- **Relation to EI / counterfactual approach:** MiniCheck is useful less as a contamination detector and more as an evaluator for evidence intrusion. If your counterfactual pipeline generates outputs that need to be scored for unsupported spillover, MiniCheck is a strong downstream metric candidate.

## 7. What these papers imply for an EI-style metric

### Most defensible direct ingredients

- **Semantics-preserving rewrites:** Yang et al., Clean-Eval, and LastingBench all support rewriting while preserving intent.
- **Local cloze or masked-span probes:** TS-Guessing, Time Travel in LLMs, entity-level memorization, and Lopez-Lira et al. support masking names, dates, answers, or other answer-bearing spans.
- **Tiny structural perturbations:** Oren et al. shows even example-order changes can reveal contamination, so EI does not need to rely only on large paraphrases.
- **Prompt/task sensitivity:** Task Contamination, Reasoning or Reciting?, and Context-faithful Prompting all show that measurement depends on framing, not just content.
- **Unsupported-evidence scoring:** How Well Do LLMs Truly Ground?, When Context Leads but Parametric Memory Follows, and MiniCheck provide direct ways to operationalize "evidence intrusion."

### Main design cautions

- **Edit difficulty is a confounder:** Mehrbakhsh et al. shows that rephrasing can change inherent difficulty, not only contamination exposure.
- **Locality matters:** Carlini et al. and Zhou et al. suggest that a model may still reconstruct edited content from nearby cues, so span-level edits need careful locality controls.
- **Prompt template matters:** Extraction papers and context-faithfulness papers both show that small prompt changes can dramatically change whether memory is exposed.
- **Use non-counterfactual baselines too:** Min-K% and CDD/TED are worth including so EI is not the only detector in the paper.

## 8. Recommended paper subset to cite most heavily

If the goal is to justify an EI metric based on counterfactual or perturbation-based measurement, I would foreground these papers:

1. **Yang et al. (2023), `Rethinking Benchmark and Contamination for Language Models with Rephrased Samples`**
2. **Oren et al. (2024), `Proving Test Set Contamination in Black-Box Language Models`**
3. **Deng et al. (2024), `Investigating Data Contamination in Modern Benchmarks for Large Language Models`**
4. **Li and Flanigan (2024), `Task Contamination: Language Models May Not Be Few-Shot Anymore`**
5. **Zhang et al. (2021), `Counterfactual Memorization in Neural Language Models`**
6. **Zhou et al. (2023), `Quantifying and Analyzing Entity-level Memorization in Large Language Models`**
7. **Lopez-Lira et al. (2025), `The Memorization Problem: Can We Trust LLMs' Economic Forecasts?`**
8. **Zhou et al. (2023), `Context-faithful Prompting for Large Language Models`**
9. **Lee et al. (2024), `How Well Do Large Language Models Truly Ground?`**
10. **Tang et al. (2024), `MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents`**

That set gives you: benchmark rewrites, black-box contamination tests, task-design confounds, formal counterfactual memorization, entity reconstruction, finance-specific evidence, and explicit metrics for unsupported evidence generation.
