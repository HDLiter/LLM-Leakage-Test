# 黑白盒通用 cutoff 验证探针协议 —— Codex 设计

## 0. 协议一句话总览 + 它在 R-1a 里的定位(验证非定义)

一句话: 用同一套按月分层的闭卷 dated-fact QA 探针, 在 16 个模型上画出“答对率随事件月份变化”的经验知识 horizon, 只用来体检 `config/fleet/r5a_fleet.yaml` 的 cutoff manifest, 并在偏差过大时触发人工复核。

定位边界:

- R-1a exposure 因子仍然只读 manifest 里的 `cutoff_date` 和 case 日期, 保持确定性。
- 本协议输出的是 `empirical_knowledge_horizon`、CI、drop 大小和 gate 状态, 不是新的 exposure 输入。
- 探针结果永远不自动写回 manifest, 也不自动喂给 exposure 指标。触发 gate 后只能进入“人工回来讨论, 可能手动改 manifest”的流程。
- Path-E 现有 logprob 探针继续作为白盒验证线。本协议新增的是黑白盒都能跑的文本进文本出行为线。

## 1. 通用行为探针方法

方案:

- 不采用模型自报 cutoff。自报容易受系统提示、文档记忆和对齐策略影响, 不能当经验证据。
- 不采用长开放问答。长答案评分会把事实正确性、解释能力和格式遵循混在一起。
- 推荐采用闭卷 dated-fact QA: 每题绑定一个明确公开日期或月份, 问一个原子事实, 用确定性规则判分。

推荐:

1. 每个 probe item 包含 `event_date`、`event_month`、`domain`、`question`、`answer_type`、`canonical_answer`、`aliases`、`source_ref`、`scoring_rule`。
2. 题目只问一个可核验事实, 例如“某日某公司宣布的产品名是什么”、“某月某次选举/任命的胜出者是谁”、“某监管决定涉及哪家公司”。不要在问题里泄露答案, 不要让答案只靠常识推出来。
3. 对所有模型使用同一条短提示, 禁止工具和浏览, 温度 0, 要求输出固定 JSON:

```text
请只根据你已有的模型知识回答, 不要猜测, 不要使用外部工具。
如果不知道, answer 写 "UNKNOWN"。
只输出 JSON: {"answer": "...", "confidence": 0.0到1.0}
问题: {question}
```

4. 主评分是二值 `correct`: 命中 canonical answer 或 alias 记 1, 错误、UNKNOWN、无法解析都记 0。另报 `unknown_rate` 和 `parse_fail_rate`, 但断点主曲线只用 `correct`。
5. 评分规则按答案类型固定:
   - 名称/实体: 大小写、全半角、标点、常见中英文别名归一化后 exact/alias match。
   - 日期/月: 精确到题目要求的粒度, 不给跨月容忍。
   - 数值: 只在题目预先声明时给固定容忍, 如百分比 ±0.1 个百分点。
   - 多答案题默认不用; 必须使用时要求全集匹配, 避免部分分制造噪音。

理由:

- 文本进文本出, 4 个黑盒 API 和 12 个白盒 vLLM 都能跑。
- 答对率是直观量, 可以按月聚合, 与 Path-E 的月度断点框架自然对齐。
- `UNKNOWN` 作为错分但单独报告, 能区分“可靠知识不足”和“乱猜”, 同时不让拒答模型在准确率上占便宜。
- 短答案 + alias 表能避免 LLM-as-judge, 也避免把另一个模型的输出引入 probe 判分。

风险:

- 行为 QA 探到的是“可可靠答出的知识”, 不是最新训练 token。
- 问题构造方法会影响断点。为降低 method sensitivity, 同一版本 probe 必须冻结题库、模板、alias 表和 scoring rule, 不做按模型调题。
- 太冷门的题会把能力不足误判成 cutoff; 太热门的题可能通过少量后训练或评测污染被记住。题库需要混合高知名度和中等知名度事实, 并在每月保持同样难度结构。

## 2. 探针集构造(复用 WS1 + 领域选择)

方案:

- 路线 A: 直接从 WS1 的 CLS 月度文章派生中文金融 QA。
- 路线 B: 另建通用世界 dated-fact QA, 只复用 WS1 的月份网格和断点分析思路。
- 路线 C: 两者都要, 但分清主副用途。

推荐: 采用路线 C, 其中通用世界 QA 是 manifest 体检的主 gate, CLS 中文金融 QA 是领域诊断副线。

具体构造:

1. 复用 WS1 的月度骨架: `scripts/build_exposure_horizon_probe_set.py` 已定义 2023-01..2025-12、默认 60 篇/月、月内 case-bootstrap 的采样思路。行为 QA 不重造月度断点框架, 而是在同一 36 个月网格上新增 sibling probe artifact。
2. 主 probe: `qa_general_world_v1.json`。每月目标 60 道, 覆盖政治/监管、科技/产品、科学/医疗、体育/奖项、商业/市场等通用世界事实。每题必须有固定来源和人工核验的 canonical answer。
3. 副 probe: `qa_cls_finance_v1.json`。从 `data/pilot/exposure_horizon/probe_set_monthly60_36mo.json` 的 CLS 文章派生, 优先选择文章当月公开的原子事实。回顾文、预告文、标题已泄露答案或事实日期不清的文章剔除。
4. 题库 item 按 `event_month` 分桶。CLS 副线可保留 `article_month` 和 `event_month`; 只有两者一致或差异可解释时进入主断点曲线。
5. Claude 专项 slice 在同一 schema 下额外加密 2025-03..2025-10, 尤其 May/Jun/Jul/Aug 每月至少 100 道, 只用于 resolve 官方矛盾, 不替代全局题库。

领域选择理由:

- 通用世界知识更适合体检 fleet manifest。manifest 声明的是模型总体知识 freshness, 不是中文金融专项能力; Claude/GPT/DeepSeek 的官方 cutoff 也都是通用口径。
- 中文金融贴近本项目 CLS 语料, 能检查“项目语料域里是否也出现相近 horizon”, 但它会强烈混入中文、金融和指令遵循能力。Llama 两个白盒已知不适合作中文金融 P_predict 主线, 因此 CLS QA 不应单独当全 fleet gate。
- 两条线一起跑可以定位分歧: 通用线正常而 CLS 线异常, 多半是领域/语言问题; 两条线都偏离 manifest, 才是 cutoff manifest 风险更强。

风险:

- 通用世界 QA 需要额外的 pinned fact table, 本地 CLS 不能完全提供。
- CLS 派生 QA 如果只来自财联社文本, 可能测到“是否见过同一中文报道”而不是更广义世界知识。报告时必须叫它“CLS-domain behavior horizon”。
- 若使用非 fleet LLM 辅助出题, 必须保留源事实、人工审核和最终 frozen artifact; 出题 LLM 不得参与判分, 也不得按目标模型结果回改题库。

## 3. 黑盒断点检测 + 与白盒 Path-E 交叉

方案:

- 白盒 Path-E 已有: 月度 Min-K%++ logprob 分数 -> WLS piecewise-linear-with-step -> grid-search κ -> 月内 case-bootstrap CI。
- 黑盒没有 logprob, 只能用每题 `correct` 得到月度答对率曲线。

推荐: 对答对率使用 Path-E 同构的断点估计, 只替换月度观测量。

答对率版检测:

1. 对每个模型和 probe domain, 聚合每月 `accuracy_m = correct_m / n_m`。
2. 月度权重用稳定化二项方差:

```text
p_tilde_m = (correct_m + 0.5) / (n_m + 1)
weight_m = n_m / max(p_tilde_m * (1 - p_tilde_m), 0.05)
```

3. 拟合同一类 piecewise-with-step:

```text
accuracy_t = α + γ·t + δ·I(t > κ) + λ·max(0, t - κ) + ε_t
```

κ 是最后一个高准确率月份, `drop = -δ`, 期望为正。

4. grid-search κ, `min_side = 6` 个月; 月内 case-bootstrap, `B = 2000`; 每次在每个月内有放回抽题, 重算月度 accuracy, 重拟合 κ 和 drop。
5. 接受 horizon 的默认条件:
   - 每月至少 30 道可评分题; 少于 30 的月份不进入正式 gate。
   - horizon 95% CI 宽度 ≤ 3 个月。
   - drop 95% CI 下界 > 0.10 绝对准确率。
   - 断点前 6 个月中位准确率 ≥ 0.45; 否则标为“模型/题域不具备可解释前段能力”, 不触发 cutoff 结论。
6. 输出 `horizon_observed` 为 κ 对应月份的月末日期; 不满足接受条件时输出 `null`, 但保留 point estimate、CI 和 notes。

与白盒 Path-E 交叉:

- 对 12 个白盒, 同时跑行为 QA 和现有 Path-E logprob。
- 首先比较 CLS 副线行为 horizon 与 Path-E horizon, 因为两者最接近同一语料月份轴。
- 再比较通用世界行为 horizon 与 Path-E, 作为跨域 sanity check。
- 期望关系不是精确相等, 而是大致对齐: CI 相交或 point estimate 差 ≤ 3 个月视为一致。
- 若行为 horizon 明显早于 Path-E, 解释为“模型可能见过文本风格/片段, 但不能可靠回答语义事实”或领域能力不足。
- 若行为 horizon 明显晚于 Path-E, 优先排查题目过热、后训练污染、黑盒隐式检索、prompt 泄露或 Path-E 对该模型不稳定。

风险:

- 答对率有上下界, WLS 是近似。它的优点是与 Path-E 代码和报告口径一致; 若后续要更精细, 可用 binomial logistic piecewise 作 robustness, 但不作为 minimal 协议主线。
- 准确率断点比 logprob 断点更受题目难度影响, 所以必须固定每月题型比例和难度标签。

## 4. 报警阈值(差多少回来讨论)

方案:

- 只用 point estimate 比 manifest: 简单, 但会被 CI 噪音误触发。
- 只看 CI 是否覆盖 manifest: 稳健, 但对 May vs Aug 这类 3 个月冲突可能太钝。
- 推荐组合: point offset + CI 排除。

推荐 gate:

1. 先把 manifest `cutoff_date` 归到月份, 如 `2025-08-31` -> `2025-08`。
2. 只有被接受的行为 horizon 才进入红色 gate; `horizon_observed = null` 不得自动质疑 manifest, 只报“probe uninformative”。
3. Red: horizon 95% CI 不含 manifest 月份, 且 point estimate 与 manifest 相差 ≥ 3 个月。
4. Yellow:
   - CI 不含 manifest, 但 point offset = 2 个月。
   - point offset ≥ 3 个月, 但 CI 边界碰到 manifest 月份。
   - 通用主线和 CLS 副线彼此相差 > 3 个月。
   - `community_paraphrase` 或 `operator_inferred` cutoff 没有得到可解释行为 horizon, 需要提高 provenance 风险标记。
5. Green: manifest 月份落在 CI 内, 或 point offset ≤ 1 个月。

触发后的动作:

- Red/Yellow 只进入人工复核队列。复核材料包括题库版本、月度 accuracy 表、CI、drop、unknown_rate、典型错题和 Path-E 对照。
- 人工可以决定保留 manifest、改 manifest、或把 `cutoff_source`/notes 改成更保守的来源说明。
- 任何改 manifest 的动作都必须是显式人工提交, 不能由 probe runner 自动执行。

理由:

- 1 个月以内在 cutoff 文档里常常只是日/月粒度差异, 不值得报警。
- 2 个月适合 yellow, 因为多数官方/社区 cutoff 本来只有月级可信度。
- 3 个月足够大, 能覆盖 Claude 的 May vs Aug 冲突, 又不会被普通月末/月初误差频繁触发。

风险:

- 对 operator-inferred manifest, 3 个月可能偏保守; 但本协议是体检, 不是自动替换, 宁可少量 yellow 人工复核, 不把行为噪音写进主因子。

## 5. Claude 矛盾 resolve 流程

背景: `r5a_fleet.yaml` 当前对 `claude-sonnet-4.6` 记录 `2025-08-31`, source 是 vendor-stated reliable knowledge cutoff。deep research 发现 Anthropic 第一方材料同时出现 May 2025、Aug 2025、Jan 2026 三种口径。

推荐流程:

1. 跑全局通用世界 QA 2023-01..2025-12, 先看 Claude 的接受 horizon 是否接近 2025-05 或 2025-08。
2. 额外跑 Claude-focused slice: 2025-03..2025-10, May/Jun/Jul/Aug 每月至少 100 道高质量题, 每月题型和知名度配比一致。
3. 对 focused slice 单独拟合局部断点, 并画 May-Aug 月度 accuracy。局部检测仍用同一 piecewise + bootstrap, 但报告时明确它是冲突 resolve slice, 不是全局 manifest 替换器。
4. 判读规则:
   - 支持 May: horizon point 在 2025-05, CI 不含 2025-08, 且 Jun/Jul/Aug accuracy 已持续落入 post-cutoff 低平台。按第 4 节对当前 Aug manifest 触发 Red, 进入人工讨论是否改成 May/Jun。
   - 支持 Aug: May-Jun-Jul-Aug accuracy 维持在 pre-cutoff 高平台, horizon point 在 2025-08 或 CI 覆盖 2025-08, 且 Sep 以后出现下降。当前 manifest 保持 Green 或 Yellow。
   - 支持中间月份: horizon point 在 Jun 或 Jul, CI 排除 May 和 Aug 中至少一端。触发人工讨论, 报告“官方 May/Aug 都不完全贴合行为知识 horizon”。
   - 无法 resolve: CI 跨 May-Aug、drop 不显著、或前段准确率不足。保留 manifest, 报告“probe inconclusive, 官方文档仍矛盾”。
5. Jan 2026 只按训练数据 cutoff 口径记录, 不用本行为 QA 直接验证。若 Claude 对 2025-09..2025-12 仍稳定高准确, 只能说明可靠知识可能晚于 Aug 或存在后训练/检索等机制, 不能自动等同于 Jan 2026 训练 cutoff。

风险:

- Claude 黑盒 API 可能有安全/不确定性回答风格, `UNKNOWN` 率可能高。需要同时看 accuracy 和 unknown_rate。
- 如果题目太热门, May-Aug 后的事实可能通过少量后训练、系统知识或评测污染被学到, 会把 horizon 推晚。focused slice 必须混合中等知名度事实。

## 6. 知识 vs 训练 cutoff 报告口径

推荐口径:

- 报告字段叫 `empirical_knowledge_horizon`, 不叫 `training_cutoff_observed`。
- 解释句固定为: “该探针估计模型能可靠回答公开事实的最后月份; 它是训练数据 cutoff 的经验下界/健康检查, 不是最新训练样本日期的证明。”
- 对 manifest 比较时写 “manifest cutoff under test”, 不写 “真实训练 cutoff”。
- 对 Claude 等区分 reliable knowledge 和 training data 的模型, 报告中分列:
  `manifest_date`, `manifest_source`, `vendor_claim_type`, `empirical_knowledge_horizon`, `gate_status`。

为什么必须这样写:

- 模型可能训练到更晚, 但没有稳定记住某些事实。
- 模型也可能通过后训练、合成数据、工具、检索或高热度事实答出 cutoff 后内容。
- 行为 QA 的下降是可靠知识边界, 不是证明“之后没有任何训练数据”。

风险:

- 如果报告把行为 horizon 写成训练 cutoff, 会和 Anthropic 自己的 reliable knowledge/training data 区分冲突, 也会把验证探针误放进 R-1a 主因子定义。

## 7. 实施清单(要建什么文件 / 复用什么 / 跑之前需要什么 infra)

复用:

- `config/fleet/r5a_fleet.yaml`: 读取 manifest cutoff 和 source, 只作比较基准。
- `scripts/build_exposure_horizon_probe_set.py`: 复用月份网格、CLS raw 输入、每月定额和 seed 思路。
- `src/r5a/analysis/exposure_horizon.py`: 复用 piecewise-WLS、grid-search κ、月内 bootstrap 和 CI/acceptance 报告结构。实现时最好抽出 generic detector, 不复制一份相似逻辑。
- `scripts/run_exposure_horizon_analysis.py`: 复用输出 manifest 风格和 trace/probe sha 记录方式。

建议新增:

- `data/pilot/cutoff_behavior_probe/qa_general_world_v1.json`: 主 gate 题库。
- `data/pilot/cutoff_behavior_probe/qa_cls_finance_v1.json`: CLS 领域诊断题库。
- `data/pilot/cutoff_behavior_probe/qa_claude_may_aug_focus_v1.json`: Claude 冲突 resolve slice。
- `scripts/build_cutoff_behavior_probe_set.py`: 题库构造/校验脚本草案, 读取 WS1 probe set 和 pinned fact table, 输出 frozen QA artifact。
- `scripts/run_cutoff_behavior_probe.py`: 未来执行脚本, 走 P_predict/black-box API, 禁止工具, temperature 0, 保存 raw answer JSONL。当前任务不要运行。
- `src/r5a/analysis/behavior_horizon.py`: 答对率版 horizon wrapper, 调 generic piecewise detector。
- `scripts/run_cutoff_behavior_horizon_analysis.py`: 从 raw answers + QA artifact 生成 `behavior_horizon_observed.json` 和 gate report。

跑之前需要的 infra:

- 所有 16 个模型的固定 route/model id、temperature 0、max tokens、无工具/无浏览设置。
- 黑盒预算和速率限制计划。
- 人工审核完成的 canonical answer / alias 表。
- probe artifact SHA-256 记录, 避免跑完后改题。
- 白盒 Path-E 结果, 用于交叉验证; 但行为探针本身不要求 logprob。

当前任务不做:

- 不发 API, 不起 vLLM, 不 probe 模型。
- 不改 manifest。
- 不把任何 behavior horizon 写入 exposure 指标。

## 8. 我最不确定的点 / 需要用户拍板的真分歧

1. 主 gate 是否必须是通用世界 QA。我的推荐是“通用世界主线 + CLS 中文金融副线”; 若用户认为 manifest 在本项目里只服务 CLS 中文金融 exposure, 可以把 CLS 线升权, 但这会更容易混入语言/领域能力。
2. 题库生产方式。最稳是人工维护 pinned fact table; 最省力是用非 fleet LLM 辅助出题再人工审核。两者的成本差很多, 但最终 artifact 必须 frozen 且可审计。
3. gate 阈值选 3 个月还是 4 个月。3 个月能抓住 Claude May vs Aug; 4 个月更保守, 但会让这次最关心的矛盾变成只 yellow 不 red。
4. `UNKNOWN` 是否计错。我的推荐是计错并单报 unknown_rate, 因为 probe 测的是可靠可答知识; 若把 UNKNOWN 排除, 会奖励保守模型。
5. Claude focused slice 每月题量。100 题/月是我认为能做 May/Jun/Jul/Aug 月级区分的最低实用密度; 若预算紧, 可降到 60 题/月, 但 CI 可能跨月变宽。
