# LLM 科研里的复现证据规范 — 调研报告(2026-05-22)

引用日期: 2026-05-22。结论先行: 在 2023-2026 的主流 ML/NLP venue 规范和近两年 LLM 论文实践里, reviewer 通常索要的是可审计的实验方法证据: prompt/任务构造、模型与 API 版本、调用/解码参数、数据抽样规则、代码/评测脚本、统计不确定性和 artifact provenance。完整 raw LLM response cache 偶尔会作为 artifact 发布,但没有看到顶会 checklist 把“全量 API response cache + hard-fail replay”列为 closed-API LLM 论文的通用硬要求。

## Q1. 顶会 reproducibility checklist 对 closed-API LLM 论文的要求

### NeurIPS / ICML / ICLR

**NeurIPS main track paper checklist.** 官方 checklist 明确要求所有论文给出某种“reasonable avenue for reproducibility”,但并不要求一定开源代码,更没有要求提交完整 raw LLM responses。对于大语言模型,NeurIPS 允许多种复现路径: detailed instructions、hosted model access、model checkpoint,或其他与研究性质匹配的方式。它还专门承认 closed-source model 的复现困难: closed-source 模型可能只能给注册用户访问,但应当让其他研究者有某种 reproducing or verifying path。实验细节条款要求 data splits、hyperparameters、选择方式;统计条款要求 error bars/CI/variability factors;计算条款要求 compute workers、memory、runtime/total compute; artifact 条款要求 cite creators、license/TOS、version。

URL:
- NeurIPS Paper Checklist Guidelines: https://nips.cc/public/guides/PaperChecklist

对 closed-API LLM 的含义:
- raw LLM responses: 没有“必须提供完整 raw cache”的条款;如果 response 本身是数据集/benchmark artifact,则应按 dataset/code/evaluation procedure 提供。
- prompt templates: 未写成“LLM prompt 必须全文”,但 prompts 是实验方法/任务构造时,应进入 detailed instructions 或 experimental settings。
- model version / API endpoint / call date: “state which version of the asset you're using”覆盖模型版本;endpoint/date 不是 checklist 明文硬要求,但 closed API 下是合理 provenance。
- sampling params: temperature/top-p/seed/max tokens 属于 hyperparameters / experimental setting,应报告。
- LLM 不确定性/API 不稳定: checklist 用 limitations、statistical significance、factors of variability 覆盖,没有 closed-API drift 专项条款。
- 白盒/黑盒区分: NeurIPS 是少数明确提到 closed-source models 的 venue;要求不是开源权重,而是有验证路径。

**NeurIPS Datasets & Benchmarks track.** 对 benchmark/dataset 贡献更严格: 数据或 benchmark 应有 reviewer 可访问 URL、metadata、license、hosting/maintenance plan;benchmark supplementary 必须使结果 easily reproducible,即 datasets、code、evaluation procedures accessible and documented。另有 LLM usage 说明: 如果 LLM 用于 data processing/filtering、visualization、running experiments、proving theorems等重要方法组件,应描述。

URL:
- NeurIPS 2024 Call for Datasets & Benchmarks: https://neurips.cc/Conferences/2024/CallForDatasetsBenchmarks

对本项目的启发: 如果论文主张发布 benchmark,数据表、抽样规则、评测流程和代码是硬证据;但该 track 也没有写“LLM API 原始响应全量 cache 是必须项”。全量 response 只有在它就是 benchmark 数据本体时才接近硬要求。

**ICML 2025.** ICML author instructions 鼓励提交 code 以促进 reproducibility,并说明“reproducibility of results and easy availability of code”会进入决策考量;支持 supplementary manuscript 和 code/data。Reviewer instructions 则说 reviewers 被鼓励但不要求阅读 supplementary material;reviewer 的核心任务是判断 claims 是否被 evidence 支撑,可问会改变评价的问题。没有 closed-API LLM 专门条款,也没有 raw response cache 条款。

URL:
- ICML 2025 Author Instructions: https://icml.cc/Conferences/2025/AuthorInstructions
- ICML 2025 Reviewer Instructions: https://icml.cc/Conferences/2025/ReviewerInstructions

对 closed-API LLM 的含义:
- raw responses: 未要求;supplement 可给 code/data,但 reviewer 不一定读。
- prompt/model/params: 属于能否 substantiates claims 的方法细节;没有 LLM-specific 字段。
- API 不稳定: 无专项要求。

**ICLR 2025/2026.** ICLR author guide 强烈鼓励在 main text 末尾写 paragraph-long Reproducibility Statement;这个 statement 不应塞入全部复现实验细节,而是引用 paper/appendix/supplement 中可帮助复现的部分。例子包括 anonymous source code、complete proof、dataset processing steps。ICLR 2026 又增加 LLM usage disclosure: 如果 LLM 在 ideation/writing 中达到 contributor-like role,需单独说明;无论如何作者对 LLM 生成内容负责。该政策针对写作/研究助理使用,不是 closed-API 实验 raw output 缓存要求。

URL:
- ICLR 2025 Author Guide: https://iclr.cc/Conferences/2025/AuthorGuide
- ICLR 2026 Author Guide: https://iclr.cc/Conferences/2026/AuthorGuide
- ICLR 2026 LLM policy page: https://iclr.cc/FAQ/LLM

对 closed-API LLM 的含义:
- raw responses: 无硬要求。
- prompt templates: 如果是实验方法,应在 appendix/supplement 中让 reproducibility statement 能引用。
- version/endpoint/date/params: 属于复现实验细节,但不是 ICLR LLM usage policy 的明文条款。
- API drift: 无专项条款;通过 limitations/reproducibility statement 处理。

### ARR / ACL / EMNLP

**ARR Responsible NLP Research Checklist.** ARR checklist 设计目标包括 research ethics、societal impact 和 reproducibility。官方 PDF 说明“不正面回答某项不是拒稿理由”,但 ARR common submission problems 页面说明: 从 2024-12 起,不适当地填写 checklist 可以作为 desk rejection 理由;EMNLP 2025 起 accepted papers 的 checklist 会作为 appendix 公开。Checklist 中与 LLM 实验最相关的是:

- B1: cite artifacts creators, state artifact version, include URL when possible。
- B2: discuss license / terms for use or distribution, including scraped/API source TOS。
- C1: report model parameter counts, total compute budget, infrastructure。
- C2: discuss experimental setup, hyperparameter search and best-found hyperparameter values。
- C3: report descriptive statistics/error bars/summary statistics, and clarify max/mean/single run。
- C4: report implementation/model/parameter settings for existing packages used in preprocessing/evaluation。
- E: disclose AI assistants used in research/coding/writing。

URL:
- ARR Responsible NLP Research Checklist: https://aclrollingreview.org/static/responsibleNLPresearch.pdf
- ARR checklist guidelines page: https://aclrollingreview.org/responsibleNLPresearch/
- ARR common submission problems: https://aclrollingreview.org/authorchecklist
- EMNLP 2025 checklist appendix announcement: https://aclrollingreview.org/responsible-nlp-checklist-appendices

**ARR reviewer guidelines.** ARR reviewer guidance is the most explicit about what reviewer 会查: reproducibility issues include whether there are enough details to reproduce experiments, including hyperparameter selection; whether code/data/etc will be public; if not, whether motivated; and whether provided for reviewer evaluation. Reviewers are not obligated to run code. It also flags LLM-only evaluation without validation, and warns against reporting best results out of unknown numbers of trials, including prompt tuning/engineering.

URL:
- ARR reviewer guidelines: https://github.com/acl-org/aclrollingreview/blob/main/reviewerguidelines.md

**ACL / EMNLP instructions.** EMNLP 2025 double-blind instructions allow software/data resources with the paper but require anonymization; submissions should not refer to unavailable documents. This supports the practical norm: key artifact evidence must be accessible to reviewers, but not necessarily all raw outputs.

URL:
- EMNLP 2025 double-blind instructions: https://2025.emnlp.org/calls/papers/Instructions
- EMNLP 2025 main conference CFP: https://2025.emnlp.org/calls/main_conference_papers/

### 共性 vs 差异

**共性。** 所有 venue 都把“能否评估/复现实验主张”放在 prompt/cache 之上: 方法细节、数据/代码/评测流程、hyperparameters、统计不确定性、artifact version/licensing/TOS、compute/provenance。Prompt templates 在 LLM 论文中通常是实验方法本体,因此 reviewer 可合理要求全文或足够完整的模板,但这来自“实验设置必须足够详细”,不是来自单独的 raw-response-cache 政策。

**差异。** NeurIPS main track 明确承认 closed-source model 复现困难,允许“路径到验证”;NeurIPS Datasets & Benchmarks 对 benchmark artifact 的公开、metadata、maintenance 更强;ICML 更偏鼓励 code/data,但 supplementary 不保证 reviewer 阅读;ICLR 倾向用 reproducibility statement 指向细节;ARR/ACL/EMNLP 通过 Responsible NLP Checklist 和 reviewer reproducibility score 使 checklist 填写更可审计。

**未见共性要求。** 没有看到 NeurIPS/ICML/ICLR/ARR/ACL/EMNLP 对 GPT-4/Claude/Gemini/DeepSeek 等 closed API 论文提出“必须发布完整 raw LLM response cache”“必须 hard-fail replay 每个 API response”“必须有 canonical table hash”的通用条款。

## Q2. 实际 supplementary 实践(5-10 篇代表性论文)

| 论文 | venue | 年份 | 主题 | 提供了什么 | 规模 | URL |
|---|---|---:|---|---|---|---|
| DeLLMa: Decision Making Under Uncertainty with Large Language Models | ICLR | 2025 | LLM 决策/金融与农业场景 | Reproducibility statement 明说提供 DeLLMa data、prompts、main experiment 的 LLM inference results、zero-shot/self-consistency/CoT/DeLLMa code、`results.sh`;复现调用仍需 OpenAI/Anthropic/Gemini API access。无 canonical hash。 | 多个 realistic decision-making environments;论文报告最多 40% accuracy 提升 | https://proceedings.iclr.cc/paper_files/paper/2025/file/6cd3ac24cdb789beeaa9f7145670fcae-Paper-Conference.pdf |
| Measuring Memorization in RLHF for Code Completion | ICLR | 2025 | LLM memorization / RLHF / code leakage | Reproducibility statement 提供 training data、model architecture、training details、memorization measurement 的详细 appendix;使用 Gemma/T5/Gemini Nano 等模型说明。未见完整 raw generation cache 或 hash。 | synthetic memorization dataset + 525K public-code examples + 14B-token pretraining setup | https://proceedings.iclr.cc/paper_files/paper/2025/file/22811d2089d4aa0ba66e52a5e47efb65-Paper-Conference.pdf |
| Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs | EMNLP | 2025 | LLM prompt sensitivity / evaluation artifact | 论文正文和 appendix 给出 prompt construction、LLM-as-judge prompt、human annotation instructions;报告 closed model version/month: GPT-4o-mini (July 2024), GPT-4.1-mini (April 2025), Gemini 2.0 Flash (February 2025)。提供 sample raw responses in figures,未见全量 response cache。 | 7 LLMs x 6 benchmarks x 12 prompt templates;10,800 human annotations | https://aclanthology.org/2025.emnlp-main.1006/ |
| LiveBench: A Challenging, Contamination-Limited LLM Benchmark | ICLR | 2025 | contamination-limited dynamic LLM benchmark | 项目页提供 paper/GitHub/dataset links;主要 reproducibility backing 是动态 benchmark 数据、评分流程、leaderboard/code,而不是全量 API response cache。 | 18 tasks,6 categories;fresh questions from recent sources | https://llmindex.net/benchmarks/livebench |
| ANAH / ANAH-v2 benchmark repository | ACL / NeurIPS | 2024 | LLM hallucination annotation benchmark | GitHub release 明示约 4.3K LLM responses 和约 12K sentence-level annotations;说明 annotation prompt/response file format。这里 full LLM responses 是数据集本体,所以公开 raw responses 是合理 artifact。 | ~4.3K LLM responses,~12K sentence annotations,700+ topics | https://github.com/open-compass/ANAH |
| HELM: Holistic Evaluation of Language Models | TMLR | 2023 | broad LLM benchmark,含 closed APIs | Stanford HELM 以 public scenarios/prompts、code、model output/result release 支撑复现;属于 benchmark infrastructure,不是普通论文强制全量 cache 规范。 | 多 scenarios、多模型、多指标;持续更新 | https://crfm.stanford.edu/helm/ |
| Auditing Prompt Caching in Language Model APIs | ICML | 2025 | closed API prompt caching / timing leakage | PMLR page 提供论文;研究重点是 timing/probing methodology 和 provider-level audit。公开证据关注 attack protocol/code/data摘要,不是完整 raw text response cache。 | 7 API providers | https://proceedings.mlr.press/v267/gu25b.html |
| Predicting Results of Social Science Experiments Using Large Language Models | working paper / project | 2024 | pre-registered social science experiment prediction with GPT-4 | 项目页说明构建 70 个 pre-registered nationally representative survey experiments 的 archive,用 GPT-4 simulation 预测 treatment effects;reproducibility backing 更像 stimuli/effect archive + prompt/protocol + analysis,未见 public full response cache 作为核心卖点。 | 70 experiments,476 treatment effects,105,165 participants | https://ai4pb.stanford.edu/projects/predicting-results-of-social-science-experiments-using-large-language-models |
| Can large language models replace humans in the systematic review process? | preprint / pre-registered study | 2023 | GPT-4 systematic review screening/extraction | 论文 abstract 明确是 pre-registered,重点报告 title/abstract screening、full-text review、data extraction 和 prompt reliability;公共证据形态偏 protocol/tasks/results,未见顶会式 raw cache 要求。 | 多语言 peer-reviewed/grey literature screening and extraction tasks | https://arxiv.org/abs/2310.17526 |

逐篇归纳:

- DeLLMa 是最接近“writer 提供 full inference outputs”的例子,但它把 raw inference results 放在 main experiments 范围内,同时给 prompts/code/eval script;并未把每一次中间 API 调用的 hard-fail replay 当成公共证据。
- Memorization-in-RLHF 这种最相关的 memorization 论文,反而主要靠 synthetic data design、measurement definition、model/training details 和 appendix 支撑,没有公开全量 generation cache 的迹象。
- Prompt sensitivity 论文提供了完整 prompt/judge prompt、model version month、human validation 和统计方差,这是 reviewer 真正可审的证据;raw output 只作为示例出现。
- ANAH/HELM/LiveBench 说明: 当“LLM outputs 是 benchmark/data artifact 本身”时,全量或大量 outputs 的公开更常见;当 outputs 只是内部自动分类/调参中间产物时,公开全量 cache 并非常规。

## Q3. 学术讨论里的共识

**1. LLM 实验最低报告标准正在向 prompt/model/provenance 收敛,不是向全量 raw cache 收敛。**  
Guidelines for Empirical Studies in Software Engineering involving LLMs 提出 8 条: declare LLM usage and role; report model versions/configurations/customizations; document tool architecture; disclose prompts, prompt development and interaction logs; human validation; include open LLM baseline; report baselines/benchmarks/metrics; articulate limitations.它明确把 prompts 和 interaction logs 作为透明度证据,但没有说所有研究都必须发布 1M 级 raw response cache。

URL: https://arxiv.org/abs/2508.15503

**2. Reviewer expectation 的缺口集中在 version disclosure、prompt justification、threats to validity。**  
Reporting LLM Prompting in Automated Software Engineering: A Guideline Based on Current Practices and Expectations 报告 current practices 与 reviewer expectations 有明显 misalignment,尤其是 version disclosure、prompt justification、threats to validity。这个结论与顶会 checklist 一致: reviewer 会问“你怎么 prompt、为什么这样 prompt、模型/API 到底是什么版本、结论对漂移/不确定性有什么限制”,而不是默认要求读全量 response cache。

URL: https://arxiv.org/abs/2601.01954

**3. LLM-for-SE reproducibility crisis 的 smell taxonomy 把问题分到 Code/Data/Documentation/Environment/Versioning/Model/Access/Legal。**  
Large Language Models for Software Engineering: A Reproducibility Crisis 分析 640 篇 2017-2025 papers 的 artifacts,把 reproducibility smell 分成 code/execution、data、documentation、environment/tooling、versioning、model、access/legal。该框架把“版本、模型、访问权限、法律/TOS”作为一等问题,比“是否有完整 response cache”更中心。

URL: https://arxiv.org/abs/2512.00651

**4. Closed API 的根本困难是模型不透明、会升级、可能同 prompt 不同 answer。**  
Same Prompt, Different Answer: Exposing the Reproducibility Illusion in Large Language Model APIs 指出 documented deterministic settings 下同 prompt 两次 API 调用也可能不同,并提出轻量 provenance protocol。这个方向支持记录 request provenance / response samples / repeated-run uncertainty,但也说明“重新调用 API 得到相同 raw response”不是可靠公共复现基础。

URL: https://sciety.org/articles/activity/10.21203/rs.3.rs-9096283/v1

**5. NLP checklist 研究的共识是 checklist 能提醒报告关键细节,但 artifact release 仍不均匀。**  
Reproducibility in NLP: What Have We Learned from the Checklist? 总结 *CL reproducibility checklist 的经验,建议会议允许 code/appendix 延后提交,并用数据收集实践 checklist 衡量 dataset reproducibility。重点仍是 data/code/appendix/reporting completeness,不是 raw API cache。

URL: https://arxiv.org/abs/2306.09562

**6. Prompt sensitivity 讨论要求 prompt variants 和 judge reliability,不是简单“缓存所有 response”。**  
EMNLP 2025 的 Flaw or Artifact? 发现 prompt sensitivity 大量来自 heuristic evaluation artifact;作者给出 12 prompt templates、judge prompt、human-LLM agreement,并报告 variance/ranking consistency。它说明在 LLM evaluation 中,reviewer 更会追问 evaluation parser/judge 是否可靠、prompt set 是否 cherry-pick、是否有 human validation。

URL: https://aclanthology.org/2025.emnlp-main.1006/

共识:
- 最低标准: model identifier/version/date if available、provider/API access path、sampling/decoding params、prompt templates or prompt generation procedure、dataset manifest/sampling rules、analysis/evaluation code、统计不确定性、limitations about API drift。
- 对 LLM-as-judge 或 auto-labeling: 需要 human validation 或 reliability evidence。
- 对 closed API: 需要承认不可完全重跑,保留/发布能验证主张的 outputs、examples、aggregates 和 provenance,必要时加 open-weight baseline。

争议点:
- “interaction logs”应到什么粒度没有统一;SE guidelines 推荐披露,但顶会政策没有硬性定义。
- “full raw response cache”在 benchmark/data release 里有价值,但普通 closed-API 实验中成本、隐私、TOS、体积与 reviewer attention 都使它难成通用要求。
- closed-API 实验是否“根本不可复现”: position papers 强调模型漂移和不可访问会破坏 strict reproducibility;venue 政策更务实,接受“path to reproduce or verify”而非 strict identical replay。

## Q4. Pre-registered LLM benchmark 先例

1. **Predicting Results of Social Science Experiments Using Large Language Models**  
   先例属性: pre-registered social science experiments + GPT-4 simulation。项目页说明 archive 包含 70 个 pre-registered nationally representative survey experiments、476 treatment effects、105,165 participants。复现 backing 主要是 experiment archive、stimuli/effects、prompt/protocol 和 analysis;未见“整套 raw response 必须 cache”的 public norm。  
   URL: https://ai4pb.stanford.edu/projects/predicting-results-of-social-science-experiments-using-large-language-models

2. **Can large language models replace humans in the systematic review process?**  
   先例属性: pre-registered GPT-4 evaluation for screening/extraction。复现 claim 依赖 pre-registration、task definitions、prompt reliability and human benchmark comparison。未见 full raw response cache 被作为核心 reviewer-facing requirement。  
   URL: https://arxiv.org/abs/2310.17526

3. **LiveBench: A Challenging, Contamination-Limited LLM Benchmark**  
   先例属性: contamination-limited, frequently updated benchmark。复现 backing 是 public benchmark data/GitHub/dataset/leaderboard 和 scoring,不是固定一次性 full API response cache。对于 leakage/contamination 主题,它的核心证据是 freshness/provenance/update protocol。  
   URL: https://llmindex.net/benchmarks/livebench

4. **DeLLMa: Decision Making Under Uncertainty with LLMs**  
   先例属性: 包含 finance/agriculture decision-making environments,接近“LLM 用于预测/决策”的应用 benchmark。它是少数明确发布 main experiment LLM inference results 的例子,但同时强调 prompts/code/evaluation scripts,并承认重跑需要 OpenAI/Anthropic/Gemini API access。  
   URL: https://proceedings.iclr.cc/paper_files/paper/2025/file/6cd3ac24cdb789beeaa9f7145670fcae-Paper-Conference.pdf

5. **RELIABLEEVAL: A Recipe for Stochastic LLM Evaluation via Method of Moments**  
   先例属性: stochastic LLM evaluation 方法论文。公开摘要说明它用 method-of-moments 处理 stochastic LLM evaluation,评估 GPT-4o 和 Claude-3.7-Sonnet 等 frontier LLMs 的 prompt sensitivity。复现 backing 偏向重复抽样设计、统计估计和不确定性报告;没有显示 full raw cache 是必要规范。  
   URL: https://cris.biu.ac.il/en/publications/reliableeval-a-recipe-for-stochastic-llm-evaluation-via-method-of/

结论: 类似项目的 precedent 更支持“pre-register protocol + freeze prompts/data manifests + report model/API/date/params + provide code/results + sample or scoped full outputs”这一套,而不是“所有中间 LLM 调用必须作为公共 artifact 完整 replay”。

## 综合结论 — 校准 WS0.5 cache/replay 设计

针对 "WS0.5 cache/replay 是否过度设计" 这个问题,evidence-based 答:

**必须项**(reviewer 不给就可能拒 / venue 政策硬要求或等价硬要求):
- 复现路径或 reproducibility statement: NeurIPS 要 reasonable avenue; ICLR 强烈鼓励 statement 指向 appendix/supplement; ARR checklist 不当填写可 desk reject。证据: NeurIPS Paper Checklist, ICLR Author Guide, ARR common submission problems。
- 数据/provenance/抽样规则: benchmark/data 贡献必须让 reviewers access data, metadata, license, maintenance/evaluation procedures;ARR B1/B2 要 artifact citation/version/license/TOS。证据: NeurIPS D&B CFP, ARR checklist。
- 实验设置与 hyperparameters: model/version、decoding params、hyperparameter search/best values、runs/statistics、compute/infrastructure。证据: NeurIPS checklist Q6-Q8, ARR C1-C4, ICML author/reviewer instructions。
- Prompt templates / prompt construction: 当 prompt 是任务定义或 treatment 时,它是实验方法;ARR reviewer guidelines 还把 prompt tuning/engineering 的 p-hacking 作为结果风险。实际论文常给 full templates/judge prompts。证据: ARR reviewer guidelines; EMNLP 2025 prompt sensitivity paper。
- Evaluation code/scripts or exact procedures: 不是所有 venue 都强制 code,但 benchmark/data track 和实际 accepted papers 常用 code/eval scripts 支撑 claims。证据: NeurIPS D&B CFP; DeLLMa reproducibility statement。

**推荐但非必须**(行业惯例,但有些论文不给也过):
- Main experiment outputs 或 scoped inference results,尤其当 outputs 直接支撑表格或是 benchmark artifact。证据: DeLLMa 提供 main experiment inference results; ANAH/HELM 类 benchmark 发布 LLM responses/results。
- Sample raw responses in appendix,用于展示 parser/judge/labeling 逻辑。证据: EMNLP prompt sensitivity 论文用 figures 展示 different raw answers and judge behavior。
- Run manifest: prompt template ID、input row ID、model ID、provider、call date、params、response hash、cost/tokens。证据: SE LLM guidelines 推荐 versions/configs/prompts/interaction logs; closed API drift 讨论支持 provenance。
- Human validation for LLM-as-judge/auto-labeling。证据: ARR M1 flags LLM-only evaluation without validation; EMNLP prompt sensitivity paper收集 10,800 human annotations。
- Open-weight baseline 或可重跑子集,用于缓解 closed API 不可访问。证据: SE LLM guidelines 推荐 open LLM baseline; NeurIPS closed-source guidance 要某种 verification path。

**可选 / 私人工具**(给当然好,但 reviewer 不会默认索要):
- 全量保存所有中间 API raw responses,用于作者自己 debugging、audit、cost accounting。
- Confirmatory replay 对 missing/corrupt/duplicate/hash-mismatched raw response hard-fail,用于内部 CI 和防止 silently recompute。
- canonical table hash / response hash,用于 release engineering 和 artifact integrity;reviewer 更可能看 manifest/hash 摘要,而不是重放每一条。

**不必要 / 罕见**(几乎没人提供,即使提供 reviewer 也不一定读):
- 1M 级 auto-tune/classification 中间 raw response cache 作为公共复现指标,除非这些 responses 本身是要发布的数据集。
- 让 reviewer 重新调用 closed API 并期待 bitwise-identical response。closed API drift/non-determinism 讨论表明这本身不可靠。
- 将 every-row hard-fail replay 作为论文主张成立的公共条件。顶会规范要求“path to reproduce or verify”,不是 identical private cache replay。

对 WS0.5 cache/replay 的校准性判断: Tier A pilot raw response cache 更接近 reviewer-facing evidence,因为规模小、可抽查、可证明 prompt/parser/labeling 行为。Tier B 500K-1M full-CLS/autotune cache 更像作者内部 provenance/debugging/CI artifact;若对外呈现,更符合规范的形态是 manifest + prompt templates + model/version/date/params + sampling/provenance + aggregate outputs/results + representative raw samples + optional private/full archive access,而不是把完整 hard-fail replay 写成公共复现必要条件。
