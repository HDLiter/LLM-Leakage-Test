**总评**

综合评分：**8.1/10**。

这份 v2 proposal 我会给出**支持立项、支持继续推进**的判断。按 NLP/benchmark/methodology 标准，它已经是一篇方向很清楚的机制论文；按 finance-first 标准，它仍然主要是**历史评估可靠性**论文，不是 alpha 部署论文。最强贡献是把"泄露"从模型/数据集属性，改写成**同一 `(article, target)` 下由 task design 打开的记忆通道**，这点在 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L24) 和 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L60) 里已经讲清楚了。

**主要问题**

1. **主识别量仍混入了 answerability / coverage。** proposal 把 `CFLS` 定义成二元响应，并要求 protected fields 一起成立，这个方向对，但没有明确规定 `neutral/unclear` 如何进入主 estimand，导致"authority 更干净"仍可能部分混入"authority 更容易合法 abstain"或"label geometry 不同"的效应，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L180) 和 [task_prompts.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L286)。我建议把**coverage / abstention rate**单独列为必须报告项，并加一个 coverage-adjusted sensitivity 或 answerable-subset sensitivity。

2. **`company / sector / index` 混成一个 headline estimand 仍然太粗。** proposal 在 benchmark 构造上允许单条样本的 target_type 为三者之一，这在数据工程上可以接受，但在主结果上不应混为一个均值，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L138)。我会把 `company` 设成 primary，`sector/index` 至少分层报告，否则 leakage 机制、标签难度和金融解释都不一致。

3. **CPT 作为 causal anchor 是对的，但以当前工程状态看仍然 overscoped。** proposal 已明确废弃旧 `EI`，转向 `CFLS`，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L193)；但当前代码里主评分仍是 `cf_invariance - para_invariance`，见 [metrics.py](/D:/GitRepos/LLM-Leakage-Test/src/metrics.py#L216)。同时 prompts 已经要求 `(article, target, target_type)`，见 [task_prompts.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L78)，但现有 `TestCase` schema 里没有 `target/target_type`，见 [models.py](/D:/GitRepos/LLM-Leakage-Test/src/models.py#L88)，smoke harness 也还在按旧接口只传 `article`，见 [smoke_test_prompts.py](/D:/GitRepos/LLM-Leakage-Test/tests/smoke_test_prompts.py#L248)。这意味着 proposal 真正的 execution bottleneck 不是算力，而是**评分器和 target-conditioned pipeline 落地**。

4. **金融端口径应继续收缩。** 现在把 utility 放到 supplementary、强调 OOS decay 而不是 in-sample alpha，这个转向是对的，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L317) 和 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L324)。但只要 target universe 还混合、execution protocol 还没写死，这部分就不能再往"可部署因子"多说半步。我建议把 finance takeaway 固定成：**高泄露任务更容易制造 false alpha，低泄露表示更可能 OOS 稳定**。

5. **统计 protocol 已接近可 defend，但还差最后一层 preregistration 颗粒度。** 现在 proposal 已经写到 cluster-aware、permutation、Romano-Wolf、`tau_b` 和 full-pipeline bootstrap，方向是对的，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L336) 和 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L351)。但主文还应补三样东西：matched-format 的 retained-effect criterion、DeepSeek fresh-slice 的 equivalence margin、primary contrast 的 pilot MDE。

**优点**

- **机制主线清楚。** "same-article, different-task" 是这篇 proposal 最有价值的识别设计，不再是散乱的多任务比较。
- **边界感好。** 明确放弃 formal RD 语言、把 DeepSeek 2026 slice 降格为 false-positive stress window，是成熟的收缩，见 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L170) 和 [RESEARCH_PROPOSAL_v2.md](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L230)。
- **指标哲学修正正确。** 用 `CFLS` 取代旧 EI，是 v2 相对 v1 最大的实质升级。
- **robustness stack 合理。** matched-format、sham、evidence intrusion、Min-K%、temporal triangulation 这套组合是能说服审稿人的。

**对各 [OPTION] 的建议**

- Inferability：**选 A**。这是当前 scope 下最好的性价比。B 太重，C 太弱。
- CFLS scoring：**选 C**。主表用 protected-fields 版本，附录报 strict primary-field。
- Evidence intrusion：**选 C**。主文 precision-first，完整 taxonomy 放附录。
- Temporal：**选 A**。Qwen boundary + DeepSeek fresh-slice stress test 最平衡。
- Core narrative：**选 B**。`direct_prediction` vs `decomposed_authority` 做唯一 primary，`sentiment` 做 bridge。
- CPT design：**选 C**。当前 repo readiness 下，四运行 compromise 比 2x3 更现实。
- Outcome block：**选 C**。强度够用，又不至于像 B 那样引入太多 format shift。
- Utility：**选 B**，但前提是**company-only + strict rolling-origin + 明确 supplementary**；否则退到 C。
- Venue：**选 A**。Findings of EMNLP 是当前最合理目标。

**额外观察**

- 如果后面必须在"`CLS-Leak-1000` 规模"与"Tier 1 审计、target schema、CFLS 真落地"之间二选一，我会优先保后者，必要时把 benchmark 缩到 `500-700`。
- proposal 最应该守住的卖点不是"低泄露因子也能赚钱"，而是"高泄露任务会系统性制造假历史优势"。这个表述最稳，也最有方法学价值。

结论：**这是一份明显可做、也值得做的开题报告**。如果把 coverage/target_type/stat prereg 这三处再收紧，并主动下调 CPT scope，我会把它看成一篇相当有希望的 EMNLP Findings 级 proposal。
