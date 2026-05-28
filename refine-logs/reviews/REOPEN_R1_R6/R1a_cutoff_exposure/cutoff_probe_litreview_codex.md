# Cutoff 知识边界验证 —— 方法学文献综述(Codex)

## 0. TL;DR(给探针设计的 5-8 条直接结论:抄什么 / 避什么 / 我们新在哪)

1. **把 `reported cutoff` 和 `effective cutoff` 分开。** `Dated Data Tracing Knowledge Cutoffs.pdf` 明确说模型自报 cutoff 只是一层元数据；同一模型在 Wikipedia、NYT、CommonCrawl-derived 内容上的 effective cutoff 可显著不同。[arXiv:2403.12958](https://arxiv.org/abs/2403.12958) 对我们意味着：探针只能给 manifest 体检和人工复核触发，不能自动改 manifest，也不能反哺 exposure 指标。
2. **闭卷 dated-fact QA 是黑盒 fleet 体检的主线，logprob/MIA 是白盒旁证。** QA 测的是“模型能否答出某月以后才公开的事实”；Min-K%/Min-K%++/DC-PDD 测的是“这段文本像不像训练成员”。二者证据类型互补，不能互相替代。
3. **边界经常是坡、平台或多段，不一定是断崖。** `Dated Data` 把 perplexity 最小点解释成“时间分布”；[LLMLagBench, arXiv:2511.12116](https://arxiv.org/abs/2511.12116) 用 PELT 找多重 changepoints；[TempoMed-Bench, arXiv:2605.13045](https://arxiv.org/abs/2605.13045) 直接报告医学知识是渐进线性衰减而非 sharp cutoff。对我们：断点检测要允许“无可靠断点/多断点/宽 CI”。
4. **题目构造会改变 cutoff 信号。** [Test of Time, arXiv:2509.00072](https://arxiv.org/abs/2509.00072) 说明同一来源材料经 cloze、LLM-transformed、多步合成等转换后，post-cutoff 衰减模式可消失或变化。对我们：必须做 method sensitivity，而不是只信一种 prompt/题型。
5. **最接近我们的工作是 LLMLagBench，但我们的域和使用方式不同。** LLMLagBench 用 2021-2025 新闻事件 QA、人工筛题、LLM-as-judge、PELT 断点和 refusal tracking 审计 60+ 模型。我们的新意在中文金融新闻、以模型 cutoff manifest 作为 exposure 尺子但只做外部体检、QA+logprob 双线，以及明确“不自动修 manifest”。
6. **题量经验：月桶至少要到几十题才像个可审计曲线。** `Dated Data` 的月度资源桶是 500 文档，消融显示 `x > 50` 时趋势稳定、`x = 50` 开始不稳；LLMLagBench 约 1,713 题跨 5 年，约 30 题/月。对我们：黑盒 QA 推荐 `>=30-50` 高质量题/月；少于 20/月只能做 smoke test。
7. **宽网格 vs 窄窗：文献更支持“先宽后窄”的两阶段。** `Dated Data` 和 LLMLagBench 都用多年跨度，能发现错报、多段和早衰；但 fleet 成本高。建议低题量宽网格 2023-01..2025-12 先扫，再对 manifest 周围和异常模型加密；纯窄窗会漏掉 Claude/DeepSeek 这类 manifest 大偏差。

## 1. 方法地图(各方法:前提 / 黑白盒 / 产出 / 代表作)

| 方法 | 前提 | 黑/白盒 | 产出 | 代表作 | 对我们意味着什么 |
|---|---|---:|---|---|---|
| 文档/厂商自报 cutoff | 厂商或 model card 披露，且定义一致 | 无需访问模型 | claimed cutoff / release upper bound | Model Cards；`Dated Data` 作为反例 | 只能做 manifest 先验。Claude 文档冲突、DeepSeek 发布日凑数说明不能当真值。 |
| dated-fact / temporal QA 曲线 | 每题有公开日期，答案在该日期前不可可靠知道；无联网/无 RAG | 黑盒 | 月度准确率、refusal、hallucination 曲线；经验 knowledge horizon | `Chronologically Consistent Large Language Models.pdf`; LLMLagBench; RealTime QA [arXiv:2207.13332](https://arxiv.org/abs/2207.13332); FreshQA [arXiv:2310.03214](https://arxiv.org/abs/2310.03214) | fleet 主探针。要按“可获得日期”分桶，记录事件日作副字段；必须过滤可预测/周期性事件。 |
| resource-version perplexity | 同一资源有月度/年度版本；可取 token logprob/perplexity | 需要 logprob，通常白盒或 API logprobs | resource-level effective cutoff，常用相对 perplexity 最小点 | `Dated Data Tracing Knowledge Cutoffs.pdf` | 与我们 Min-K%++ 线最接近；可用于白盒模型和新闻文本桶，但 closed models 无 logprob 时不可用。 |
| Min-K% / Min-K%++ / DC-PDD MIA | 目标文本有 member/non-member 候选；模型暴露 token probabilities | “黑盒 logits/logprob”，非纯文本黑盒 | 文本级 membership score、AUC、TPR@低 FPR | `Detecting Pretraining Data...pdf`; Min-K++ [arXiv:2404.02936](https://arxiv.org/abs/2404.02936); DC-PDD [arXiv:2409.14781](https://arxiv.org/abs/2409.14781) | 适合作“月度 logprob 断点线”。不能单点证明未训练，也不能直接给训练截止月；中文文本可参考 PatentMIA/DC-PDD。 |
| 黑盒契约式 contamination proof | benchmark 有 canonical ordering，未污染时样本顺序 exchangeable；模型能给序列 likelihood | 需要 logprob，但不需要权重/训练集 | 统计证明某 benchmark/test set 污染 | `Proving Test Set Contamination in Black Box Language Models`, [arXiv:2310.17623](https://arxiv.org/abs/2310.17623) | 对“新闻 cutoff”不是直接方法，但可借鉴“预注册统计契约 + 随机化对照”的思想；本地同名 PDF 内容错置，见附录。 |
| guided completion / extraction contamination | 有原始 benchmark 文本，可给 dataset/partition/prefix 让模型续写 | 纯文本黑盒可做 | instance/partition contamination 判断 | `Time Travel in LLMs`, [arXiv:2308.08493](https://arxiv.org/abs/2308.08493) | 不适合普通新闻事实 cutoff；可用于检查我们 benchmark 题面/答案是否被模型原样记住。 |
| task-level chronological performance | 任务/数据集有发布日期，且可控制任务难度 | 黑盒 | pre/post 任务性能差异 | `Task Contamination: Language Models May Not Be Few-Shot Anymore`, [arXiv:2312.16337](https://arxiv.org/abs/2312.16337) | 支持按 cutoff 前后比较，但要有难度控制；否则“冷门/难题”会被误判为 cutoff。 |
| point-in-time model construction | 自己训练年度/时间切片模型 | 训练侧白盒 | 已知 cutoff 的 validation oracle | `Chronologically Consistent...pdf`; `DatedGPT`, [arXiv:2603.11838](https://arxiv.org/abs/2603.11838) | 不是审计未知模型的省力方案，但非常适合验证我们的探针能否在已知 cutoff 模型上回收正确年份。 |

## 2. 渐变边界 & 断点检测 & method sensitivity

**文献支持的事实。** `Dated Data` 用 2016-2023 的 `WIKI SPAN` 和 2016-2020 的 `NEWS SPAN`，对每月文本计算 perplexity，去掉每月最高/最低 2.5% 后做 0-1 相对缩放，以 relative perplexity 最小月作为 effective cutoff；作者明确说 minima 不总是 sharp，应解释成时间分布。LLMLagBench 将 2021-2025 新闻事件题按事件公开日期排序，用 faithfulness score 的时间序列跑 PELT changepoint detection，并跟踪 refusal，以识别单断点、多断点和 declared cutoff 偏差。TempoMed-Bench 进一步提醒，有些域的表现更像线性衰减而不是断崖。

**断点/knee 的现状。** 直接用于 LLM cutoff 的成型方案目前主要是 LLMLagBench 的 PELT；`Dated Data` 更像“最小点/谷底”而非结构断点；金融 lookahead 论文多用性能衰减、alpha decay、fake-date 分布差异，不一定输出 cutoff 月。结论：断点检测可抄，但必须有 no-break/multi-break 输出，而不是强制每个模型一个月。

**method sensitivity。** 证据最直接的是 Test of Time：同一 arXiv/source material，经 LLM 变换成多步 reasoning question 后，原本基于 post-cutoff decay 的 contamination signal 会显著改变。Min-K% 也报告文本长度、paraphrase setting、k 值影响 AUC；`Dated Data` 做文档数消融，`x > 50` 趋势较稳，`x = 50` 附近变噪。对我们：至少要做 3 个敏感性轴：题型(open QA/cloze/MC)、表述(原题/改写)、评分(EM/alias/F1/LLM judge+人工抽检)。

## 3. 知识 cutoff vs 训练 cutoff(可测性)

**训练 cutoff** 是数据采集/混合/继续预训练/post-training 的真实截止。黑盒几乎不能直接测到；release date 只是硬上界，厂商声明也可能遮蔽多阶段训练。白盒 logprob/MIA 对“候选文本是否训练成员”给下界证据，但 `Do Membership Inference Attacks Work on LLMs?` [arXiv:2402.07841](https://arxiv.org/abs/2402.07841) 警告：大语料、少 epoch、member/non-member 边界模糊会让 MIA 接近随机；时间范围差异还会制造虚假的成功。

**知识 cutoff / effective horizon** 是模型在某域能可靠答出公开事实的经验边界。dated-fact QA 能测这个，但它混合了训练曝光、记忆强度、推理、世界先验、拒答策略和 post-training 行为。`Dated Data` 的 resource-level effective cutoff 就是一个知识边界，不等于训练集最后日期；LLMLagBench 的 changepoint 也是“earliest probable temporal boundary”，不是训练数据审计真值。

**对我们的边界定义。** 我们应把探针输出命名为 `empirical knowledge horizon` 或 `effective cutoff evidence`，不要叫 `true training cutoff`。可经验下界：如果模型稳定答对某月后不可预测事实，说明它可能有该信息的训练/post-training/RAG-like exposure 或强泄露；不可证明项：答错不能证明未训练，答对也不能唯一证明 pretraining exposure。

## 4. 可迁移设计参数(题量 / 分桶 / 防混淆 / 探针 validation)

**题量。** `Dated Data` 对每月 500 文档做主实验，并显示 `x > 50` 时月度曲线基本稳定；LLMLagBench 1,713 题覆盖约 5 年，约 7 题/周、30 题/月。我们若要月级断点，建议每月 `>=30-50` 题；高风险月份或断点附近加密到 `50+`。少于 20/月时只报告粗略方向，不做 `<=3 months` 验收。

**分桶时间字段。** exposure 因子应按新闻“可进入训练的公开/发表日”分桶；事件日作为副字段用于过滤和解释。若一篇 2025 新闻回顾 2020 事件，题目若只问 2020 事实就不合格；必须问 2025 才公开、且 cutoff 前不可可靠推断的增量事实。

**防止把能力不足误判成 cutoff。** 需要：

- 按月份平衡主题、公司规模、新闻源、答案类型，避免 post-cutoff 全是小公司/冷门公告。
- 加入 old-but-hard 和 recent-but-easy 控制题，估计模型基础金融中文能力。
- 剔除定期财报日、指数调整、体育赛程式可预测事件；LLMLagBench 也人工剔除 trivial/predictable questions。
- 评分支持别名、数字容差、实体消歧；LLMLagBench 的 LLM judge 用 human kappa 校准，给我们一个可抄的抽检目标。
- 记录 refusal 和 hallucination，不能只看 accuracy；instruction-tuned 模型可能按自报 cutoff 拒答，而不是没有知识。

**探针 validation。** 用三类回测：1) 已知年度 cutoff 的 ChronoBERT/ChronoGPT、DatedGPT；2) 开源训练数据较清楚的 Pythia/GPT-Neo/OLMo/LLaMA 资源版本；3) 对我们 16 模型中厂商声明较可信的一小组做 blinded manifest check。验收不应只看点估计，还要看 bootstrap CI、pre/post gap、拒答曲线和 QA/logprob 是否同向。

## 5. 我们的定位(谁最近 / 新在哪 / 空白)

**最近工作。** LLMLagBench 最像我们：用新闻事件 QA 审计模型 declared/undeclared cutoffs，PELT 断点，人工验证，拒答跟踪，多模型 fleet。`Dated Data` 最像我们的白盒线：按时间版本/月份做 logprob/perplexity 曲线。DatedGPT/Chronologically Consistent LLMs 最像“已知 cutoff oracle”。金融 lookahead 线(A Test of Lookahead Bias、Fake Date Tests、Look-Ahead-Bench)最像我们的应用风险，但它们主要测预测/回测偏差，不是为每个通用模型建立 cutoff manifest 体检。

**我们的新意。** 

- 目标域是中文金融新闻，不是通用新闻、Wikipedia、医学 guideline 或英文金融 headline。
- cutoff manifest 是实验 exposure 的尺子，但探针只负责 validation/flag，不负责自动修正。这比很多 benchmark 论文更保守，也更适合审稿防御。
- QA-vs-logprob 双线：黑盒 fleet 全覆盖，白盒/API-logprob 模型有 Min-K%++ 旁证。
- 月度网格 2023-01..2025-12 对齐当前金融新闻泄露 benchmark，而不是单一模型/单一任务污染检测。

**空白。** 还没有看到论文系统量化“中文金融 dated-fact 题目构造如何影响 cutoff 月估计”。Test of Time 说明这个敏感性存在，但不在中文金融域。因此我们需要把 method sensitivity 做成探针 validation 的一部分。

## 6. 对我们当前选择的逐条裁决(min_side=3 / 断点 / QA+logprob / 接受准则 / 网格 vs 窄窗)

**`min_side=3`：弱支持，可用但要加护栏。** 文献没有给 `min_side` 标准。LLMLagBench 用 PELT 而非固定左右窗口；`Dated Data` 靠多年曲线和较大月桶稳定趋势。把 `min_side` 从 6 降到 3 可以接受，前提是：每侧至少 3 个月且每月题量足够；bootstrap horizon CI 必须 `<=3` 个月；低题量或曲线平缓时输出 `no reliable horizon`。

**断点检测：支持，但不要强制单断点。** 用 segmented mean/PELT/二项准确率 changepoint 都合理。必须允许 multi-break，因为 LLMLagBench 发现 Claude/Gemma/Mixtral 类模型有 partial cutoffs；也必须允许 slope/no-break，因为 TempoMed-Bench 报告渐进衰减。

**QA + logprob 双线：强支持。** QA 是闭源通用主线；Min-K%/Min-K++/DC-PDD 和 `Dated Data` 支持 logprob 曲线作为训练曝光旁证。报告时分开命名：`QA knowledge horizon` 与 `logprob exposure horizon`，只在二者一致时提高复核优先级。

**接受准则：支持“CI + 人工复核 + 不自动改 manifest”。** 文献共同反对把 cutoff 当单一确定真值。建议 flag 条件：点估计偏离 manifest `>3` 个月，且 CI 不覆盖 manifest；或 QA/logprob 同向偏离；或 refusal 与 accuracy 出现 declared cutoff 前的异常断点。flag 后人工看题、看新闻可得性、看评分。

**宽网格 vs 窄窗：推荐 hybrid。** 如果 manifest 可靠，窄窗 `manifest ± (min_side + 3 months)` 省钱；但当前 manifest 明显不可靠，纯窄窗会漏大偏差。建议先用宽网格 2023-01..2025-12 低密度扫所有模型，找粗断点/无断点/多断点；再对 manifest 周围、粗断点周围和异常模型加密。这样兼顾 LLMLagBench/Dated Data 的宽跨度优点和 fleet 成本。

## 附:本地已读清单 + arxiv 新增清单(file/id + 一句话)

**Tier 1 本地精读/处理**

- `Dated Data Tracing Knowledge Cutoffs.pdf`：精读。资源版本 + relative perplexity 最小点估计 resource-level effective cutoff；强调 reported 与 effective cutoff 可错位。
- `Detecting Pretraining Data from Large Language Models.pdf`：精读。WIKI MIA + Min-K% Prob；低概率 token 均值做 membership score，适合白盒/logprob 旁证。
- `Chronologically Consistent Large Language Models.pdf`：精读。1999-2024 年度 ChronoBERT/ChronoGPT；用总统/重大事件 probes 验证 post-cutoff 不答未来首发事实。
- `Proving Test Set Contamination Black Box.pdf`：已抽取但本地 PDF 内容异常，实际为 freehand ultrasound 3D reconstruction 论文；未作为本地证据。方法改用 arXiv:2310.17623 摘要补足。

**Tier 2 / arXiv 方法补充**

- `Proving Test Set Contamination in Black Box Language Models`, [arXiv:2310.17623](https://arxiv.org/abs/2310.17623)：canonical ordering vs shuffled ordering 的 likelihood 契约检验，能给 test-set contamination 统计证明。
- `Set the Clock`, [arXiv:2402.16797](https://arxiv.org/abs/2402.16797)：TAQA 20K time-sensitive QA，显示模型虽有较新 cutoff 也常答成较旧年份知识。
- `Time is Encoded in the Weights`, [arXiv:2312.13401](https://arxiv.org/abs/2312.13401)：year/month finetune delta 形成 time vectors，说明时间知识可在权重空间呈连续结构。
- `Time Travel in LLMs`, [arXiv:2308.08493](https://arxiv.org/abs/2308.08493)：guided instruction 续写 benchmark 后半段，用 overlap/LLM judge 判污染。
- `Task Contamination`, [arXiv:2312.16337](https://arxiv.org/abs/2312.16337)：按数据集发布日期比较 pre/post 表现并控制难度，提示 zero/few-shot 性能常被 task contamination 抬高。
- `Do Membership Inference Attacks Work on LLMs?`, [arXiv:2402.07841](https://arxiv.org/abs/2402.07841)：MIA 常近随机，时间分布差异会伪造成功；提醒 Min-K 线只能作旁证。
- `Pretraining Data Detection: Divergence-based Calibration`, [arXiv:2409.14781](https://arxiv.org/abs/2409.14781)：用 token distribution divergence 校准 Min-K 类方法，并提供中文 PatentMIA。
- `Min-K%++`, [arXiv:2404.02936](https://arxiv.org/abs/2404.02936)：把训练样本视为条件分布局部 mode，改进 Min-K% 的理论与打分。
- `LLMLagBench`, [arXiv:2511.12116](https://arxiv.org/abs/2511.12116)：1,713 新闻事件题、人工筛选、LLM judge+human agreement、PELT 多断点、refusal tracking；最接近我们的 cutoff fleet 体检。
- `Test of Time`, [arXiv:2509.00072](https://arxiv.org/abs/2509.00072)：post-cutoff decay 对题目构造高度敏感；必须做 method sensitivity。
- `TempoMed-Bench`, [arXiv:2605.13045](https://arxiv.org/abs/2605.13045)：医学知识随时间线性衰减且邻近年份不稳定；反对“所有域都有清晰断崖”的假设。
- `DatedGPT`, [arXiv:2603.11838](https://arxiv.org/abs/2603.11838)：12 个 1.3B 年度 strict-cutoff 金融相关模型，用 perplexity probing 验证年度边界。
- `A Test of Lookahead Bias in LLM Forecasts`, [arXiv:2512.23847](https://arxiv.org/abs/2512.23847)：用 pretraining-detection 得到 LAP，并检验 LAP 与预测准确率相关性。
- `Fake Date Tests`, [arXiv:2601.07992](https://arxiv.org/abs/2601.07992)：用真实日期 vs 伪日期 prompt sensitivity 检测宏观预测 lookahead/context bias。
- `Look-Ahead-Bench`, [arXiv:2601.13770](https://arxiv.org/abs/2601.13770)：金融 agentic workflow 中用 alpha decay 区分 memorization 与真实预测能力。
- `AntiLeakBench`, [arXiv:2412.13670](https://arxiv.org/abs/2412.13670)：自动构造“明确新知识”样本，提醒“新收集数据”不等于无污染。
- `RealTime QA`, [arXiv:2207.13332](https://arxiv.org/abs/2207.13332)；`FreshQA/FreshLLMs`, [arXiv:2310.03214](https://arxiv.org/abs/2310.03214)：动态 QA/检索增强基线，说明新鲜事实题要区分 parametric knowledge 与 retrieval。
