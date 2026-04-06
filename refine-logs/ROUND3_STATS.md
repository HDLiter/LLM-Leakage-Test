# Round 3 Stats Review — Independent Econometrics/Statistics Assessment

> Reviewer role: Econometrician / Statistician specializing in causal inference and experimental design
> Generated via Codex MCP (GPT, xhigh reasoning effort)
> Thread ID: 019d6252-74fa-7a72-9fb6-a053197406b7

---

独立判断：当前 proposal 的根基问题不是 `Type A/B` 不够"新"，而是它把三个本该分开的对象缠在了一起：`时间可容许性`、`shortcut 类型`、`任务路径效应`。这在 proposal、讨论日志、temporal 分析和 prompt/template 设计里都很明显。

## 1. 记忆分类体系应改成多维，但 Type A/B 不必废掉

`Type A/B` 更适合作为"功能轴"，不是主 taxonomy。主 taxonomy 我建议至少三轴：

- **temporal admissibility**：答案是否依赖 `C≤τ` 不可恢复的信息；
- **memory object**：entity prior、event-outcome、article overlap、task-template、regime prior；
- **path role**：记忆是在辅助 grounding，还是直接替代文章给答案。

这样改的好处是：`entity prior` 不会再被误塞进 Type A 或 Type B，`task-template memory` 也不必和 entity familiarity 硬分边界。你们现在的二分法在 proposal 里能讲故事，但不足以支撑识别。

## 2. Entity prior 应该成为独立测试维度，而不只是协变量

原因很简单：它经常不是 look-ahead leakage，但仍然是 evaluation-invalidating shortcut。金融里它还会系统性地和大盘股、知名公司、热门叙事绑定。我的建议是把它定义成独立的 secondary estimand：

**entity-cue dependence**，而不是"控制后就没事"。

设计上可做三件事：

1. `2x2 (entity cue × semantic edit)` 敏感性设计，把实体名保留在 target metadata 中、只弱化正文显式 cue；
2. 按 `target_type`、实体知名度、传播度分层；
3. 加入 synthetic unseen-entity / same-schema bridge，区分"会泛化的结构先验"和"只对历史真实实体粘住的记忆"。

这一块可以从 `EXPLORE_MEMORY_TYPES_NLP.md` 和 `DEBATE_MASKING_STATS.md` 直接吸收。

## 3. CFLS 的根本问题不是评分细节，而是 cross-task construct validity

当前 `direct_prediction` 用 `semantic_reversal`，`decomposed_authority` 用 `provenance_swap`，这在 templates 里是硬编码的；所以 `Delta_CFLS` 现在混入了模板显著度、任务顺从性、短文本改写占比和可判定性差异。`CFLS` 仍然比旧 EI 好，但它只能安全地解释成"article-responsiveness"，不能直接当"泄露程度"。根本性修补只有三步：

1. 先做 `50-100` 条 template-comparability pilot；
2. 把 `decomposed_impact` 提到主线，做 same-template bridge；
3. 在 comparability 过关前，把主结论降级成 `prompt-task-template bundle effect`，而不是 `task pathway effect`。

否则 `CFLS` 跨任务比较是不稳的。审阅日志这点判断是对的。

## 4. "泄露"定义应该改成 dependence on info not recoverable from C≤τ

这是我认为最重要的概念升级，也是 temporal 分析最有价值的部分。它比"记住未来"更严格，也更可操作。因为真正违规的不是 reference time，而是 exposure/admissibility。

这一定义下：

- `CFLS` 测的是对 text-external shortcut 的暴露度；
- `evidence intrusion` 是高精度的 temporally inadmissible dependence 证据；
- `false-outcome CPT` 才是最接近因果识别的核心实验。

建议把论文语言改成两层：

- **主对象**：`temporally inadmissible dependence`；
- **更宽的外圈**：`text-external shortcut dependence`。

这样能避免把 entity prior、article familiarity、future outcome memory 混成一个东西。

## 5. 对 scope、contribution、可发表性的影响是"收窄但变硬"

如果按上面重构，scope 应该收成：

- 一个 binary 主对比；
- 一个 same-template bridge task；
- 一个 false-outcome CPT 核心实验；
- 一个高精度 intrusion 审计；
- entity prior 作为独立 secondary dimension。

贡献也要改写：不是"证明 direct task 更容易泄露"这种偏显然的结论，而是"量化不同 task-prompt bundles 对 temporally inadmissible dependence 的暴露曲线，并识别 residual failure modes"。这比现版更可发表。

不改的话，我同意日志里的判断：最大拒稿点会是 construct validity 和 limited novelty。改了以后，我认为 **Findings 级别更稳**；主会场只有在 false-outcome CPT 很干净、same-template bridge 成立、最好再有轻量第二模型复现时才值得冲。

## 补充：代码状态

代码状态也支持这个判断：现在 `metrics.py` 仍是旧 EI 逻辑，`experiment.py` 还是旧 runner，`models.py` 和 smoke test 也还没把 `target/target_type` 真正接进 runnable path。这说明当前问题不是"再润色 proposal"，而是先把识别对象和操作化对象对齐。

## 最硬结论

> `Type A/B` 应降格为辅助叙事；论文核心应改写成 **"任务设计改变模型对 point-in-time 不可恢复信息的依赖程度，而不是直接测得某种纯粹的未来记忆"**。
