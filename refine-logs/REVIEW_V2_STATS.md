综合评分：`8.0/10`。作为一篇面向 EMNLP/Findings 的"机制 + 测量"型 proposal，它已经明显强于 v1；但按严格计量识别标准看，我大概只会给 `6.8-7.0/10`，因为还有几处关键混淆和预注册细节没有完全锁死。

**主要问题**
- 最大残余混淆是"可由文章直接判断的难度/可判定性"而不只是 Type B 泄露。`direct_prediction` 和 `authority` 在 inferability、abstention 几何、标签熵上天然不同；如果不显式控制，`Delta_CFLS` 可能部分是在测"哪个任务更 text-internal"，而不是"哪个任务更少泄露"。这一点在 proposal 已经意识到，但还没完全内生化进主分析。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L68) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L158)
- `CFLS` 替代 EI 是对的，但 benchmark estimand 仍然条件于"可改写且 QC 通过的样本"。`semantic_reversal`、`provenance_swap`、`novelty_toggle` 不是同构干预；不同模板的 edit salience 和非目标字段外溢风险也不同。所以现在更像是"在可重写样本上的任务敏感性比较"，不是全语料层面的 leakage parameter。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L140) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L177)
- 统计协议比 v1 好很多，但 confirmatory family 仍不够硬。主检验最好明确成 cluster-level paired contrast + sign-flip/permutation，bootstrap 主要给 CI；`Romano-Wolf` 要对应一个完全枚举的 family，而不是笼统写"primary family"。另外，"CI excludes zero in expected direction" 需要写清是一侧还是两侧标准。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L335)
- 因果锚点只有在 false-outcome arm 真跑出来时才足够锋利。若退化成 real-outcome-only，识别会重新混入 Type A cueing。proposal 本身承认了这点，所以我会把 `2 x 3` 看作识别下限，而不是增强项。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L273)
- sham control 仍偏"表层文本特征"，不能完全排除"结构化抽取本身更稳"这个解释。当前 sham 是 `formality / numeric_density / sentence_complexity`，和 `authority / novelty` 的抽象层级并不匹配。[task_prompts.yaml](D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L606)
- proposal 的执行可行性被当前代码状态拖后腿。文档说 prompt infrastructure 已冻结，但现有实现里 `metrics.py` 还是旧 EI 逻辑，而且 smoke harness 甚至没有给 target-conditioned prompt 提供 `target/target_type`。这不是小 bug，而是"论文故事还没落到 runnable path"。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L147) [metrics.py](D:/GitRepos/LLM-Leakage-Test/src/metrics.py#L178) [metrics.py](D:/GitRepos/LLM-Leakage-Test/src/metrics.py#L216) [smoke_test_prompts.py](D:/GitRepos/LLM-Leakage-Test/tests/smoke_test_prompts.py#L247) [prompt_loader.py](D:/GitRepos/LLM-Leakage-Test/src/prompt_loader.py#L121)
- `company / sector / index` 混在一个主分析里我不太满意。它们的经济含义、可交易性、以及 direct prediction 的标签生成逻辑都不一样；至少要把 `target_type` 放进主控制，最好分层报告。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L138) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L342)

**Strengths**
- v2 最重要的进步是把论文从"EI 指标 paper"改成了"task design gates memory pathway"的机制 paper；这个 framing 明显更稳。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L15)
- same `(article, target)` paired comparison 是全篇最强的设计骨架，远好于跨 benchmark、跨数据集比较。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L60) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L252)
- 用 `CFLS` 取代 `cf_invariance - para_invariance` 是正确决定，构念效度大幅提升。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L24) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L177)
- 把 evidence intrusion 放到 supplementary direct evidence 的位置很聪明；它适合当高精度证据，不适合当唯一主指标。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L206)
- DeepSeek 的"frontier"被降格为 false-positive stress window，这个克制是对的。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L170) [RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L236)
- 放弃 72-cell exact fill、改用 post-stratification weights，也是明显的统计改进。[RESEARCH_PROPOSAL_v2.md](D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L136)

**[OPTION] 建议**
- Inferability：选 `A`。Tier 1 做人工 inferability 是必须的；全量 1000 双人标注性价比不高，但完全没有不行。
- CFLS scoring：选 `C`。主表用"target field changed + protected fields stable"，附录报 strict-only。
- Evidence intrusion：选 `C`。主文 precision-first，四桶全审计放 appendix。
- Temporal analysis：选 `A`，但必须把 Qwen boundary 明说成 descriptive local-window，DeepSeek 只做 falsification/stress。
- Main story task family：选 `A`。主文就讲 `direct_prediction` vs `decomposed_authority`，其他任务尽量降到附录。
- CPT factorial：科学上我支持 `B`；如果算力真卡住，退 `C`，不要退 `A`。
- Outcome block format：选 `C`。只给方向太弱，带 rationale 又过度分布偏移；方向 + 幅度桶是较稳妥折中。
- Utility study：倾向 `B`，但前提是改成 company-only、明确交易协议；如果做不到，就选 `C`。
- Venue：选 `A`。当前最合理目标仍是 Findings of EMNLP。

**其他重要观察**
- 如果只能再补一个设计件，我会补"coverage / abstention / inferability"三件套，并把它们和 `CFLS` 同时预注册；否则 reviewer 很容易说 authority 只是更爱输出 `unclear`。
- 如果只能再补一个 robustness，我会补"按 edit distance / changed-span profile 分层"的 sensitivity，而不是再加更多任务。
- 如果时间真的不够，优先保住 `binary main contrast + matched/sham + false-outcome CPT`；最先该砍的是 downstream utility，不是主识别。
- 总体判断是：这份 v2 已经接近一篇可投的 NLP 方法/测量 proposal，但要想让统计上真正硬起来，必须把"可判定性混淆、主检验层级、以及 runnable implementation"这三块再收紧。
