# Review: BUG_AUDIT_amber.md

审查范围：`docs/BUG_AUDIT_amber.md`，以及它点名的
`src/pilot.py`、`src/masking.py`、`src/metrics.py`、`scripts/run_diagnostic_2.py`、`config/prompts/counterfactual_templates.yaml`，外加源数据 `data/results/diagnostic_2_results.json`。

总评先说结论：这份 audit 不是“全错”，但也绝对不是 `PASS` 水平。Bug 3 和 Bug 4 是真问题；Bug 1 的 schema 缺陷也是真的，但 audit 没有用现有 persisted artifacts 证明它就是 `121/606` NP failure 的主因；Bug 2 被说成 P0 pipeline bug 过头了；Bug 5 则把分流条件说错了，代码按 `known_outcome_available` 分流，不是按 period 纯二分。

## Bug 1

**Claim:** `changed_spans[*].from/to maxLength=200` 杀死整句 CF rewrite。

1. 行号：
   - 基本正确。`counterfactual_templates.yaml:51-66` 确实对 `changed_spans[*].from/to` 设了 `maxLength: 200`。
   - `pilot.py:_parse_cf_payload` 在 `149-174`，实际 schema 校验发生在 `167-169`，校验失败直接 `return None`。
2. Mechanism story：
   - 作为代码缺陷，这个 story 站得住。schema 对 `semantic_reversal` 和 `neutral_paraphrase` 共用；任何长 span 都会把整条 CF payload 打成 `None`，随后在 `assemble_conditions` / `run_tasks_batch` 里变成 `failed/skipped`，最后 `score_case_from_batches` 把该 task 记为 `cfls=None`。
   - 但 audit 没有证明“诊断结果里的 121 个 NP fail 主要就是被这个 200-char cap 杀掉的”。原因很简单：最终 JSON 不保留上游 CF 生成失败时的原始输出，只留下 `validation_errors=["upstream_cf_failed"]`。所以你能证明“有 121 个 NP upstream failed”，不能用这份 persisted JSON 单独证明“失败原因就是 changed_spans 超长”。
3. Quantitative impact：
   - `121/606` 可独立验证，audit 的分层数字也对。
   - 我用的核对逻辑很短：

```python
np_fail = sum(
    bool(c["tasks"]["direct_prediction.base"]["responses"]["neutral_paraphrase"].get("skipped"))
    for c in cases
)
# 121
```

```python
from collections import Counter
cell = Counter()
for c in cases:
    if c["tasks"]["direct_prediction.base"]["responses"]["neutral_paraphrase"].get("skipped"):
        cell[(c["period"], c["anchor_binary"])] += 1
# pre/weak 11, pre/strong 28, post/weak 23, post/strong 59
```

4. 我的结论：
   - **缺陷真实，但 audit 对“根因已被独立证明”说得太满。**

## Bug 2

**Claim:** aggregation “silently drops `cfls=None` entries”，属于 P0。

1. 行号：
   - `pilot.py:641-651` / `656-665` 对 `cfls=None` 的写法没问题。
   - `run_diagnostic_2.py:327-333` 只把 `cfls is not None` 的条目送进聚合，也属实。
2. Mechanism story：
   - “均值只在 scored cases 上算”这个描述是对的。
   - 但 **“silent” 不对**。输出里已经有：
     - `aggregated.n_completed_cases`
     - `aggregated.by_task[task_id].count`
     - 每个分层块里的 `n_cases` 和对应 `aggregated.by_task[*].count`
   - 也就是说，dropout 并没有在 JSON 里被隐藏；只是 human-readable Phase 3 table 如果没展示这些字段，会让读者不舒服。这是 reporting/UI 问题，不是 P0 pipeline 计算 bug。
3. Quantitative impact：
   - `447` 这个 direct denominator 我独立复算了：

```python
n_direct = sum(c["metrics"]["cfls_direct"] is not None for c in cases)  # 447
n_total = len(cases)  # 606
# direct dropout = 159
```

   - JSON 顶层自己也写着：
     - `aggregated.by_task["direct_prediction.base"]["count"] == 447`
     - `aggregated.n_completed_cases == 606`
4. 我的结论：
   - **audit 这条过度定性。**
   - 这是“available-case aggregation + denominator disclosure不够醒目”，不是“silent drop P0”。

## Bug 3

**Claim:** `_detect_fo_flip` 把 `non-neutral -> neutral` 记成 no-flip。

1. 行号：
   - 正确。`metrics.py:361-402` 的 `_detect_fo_flip` 确实把 `fo_polarity=="neutral"` 排除在 flip 之外。
   - `pilot.py:626-665` 也确实单独算 `fo_flip`，再在 `665` 覆盖 `cfls_per_case` 里的内部值。
2. Mechanism story：
   - 站得住，而且是实质性问题。当前逻辑只承认“跨到 opposite polarity”是 flip，不承认“退回 neutral”。
   - 你如果把 false-outcome probe 理解为“向 planted false outcome 让步”，那么 hedged retreat 被记成 no-flip 确实会系统性漏计。
3. Quantitative impact：
   - 这条我独立重算，结果和 audit 的**计数**一致：
     - direct: `strict=26`, `hedged=79`, `union=105`, `undefined=7`
     - impact: `strict=3`, `hedged=55`, `union=58`, `undefined=17`
   - 我还做了一个必要 cross-check：按当前 strict 逻辑回放后，和 persisted `metrics.fo_flip_*` **0 mismatch**。
   - 抽两个数字：
     - direct hedged = `37(pre) + 42(post) = 79`
     - impact hedged = `40(pre) + 15(post) = 55`
   - audit 这里有个硬伤：**rate denominator 写得不一致**。比如 direct strict 它写 `10/332`，但真正“valid orig+fo”的 pre denominator 是 `327`；impact hedged/union 它写 `40/332` vs `15/274`，那其实是在用 all-case denominator，不是它前文说的 `n=589 with valid orig+fo` denominator。方向没变，但表格不严谨。
4. 我的结论：
   - **这是最扎实的 P0。**
   - 但 audit 的 rate table 需要重写，denominator 不能混着用。

## Bug 4

**Claim:** LLM-negated false outcome 没有 polarity check。

1. 行号：
   - 正确。`masking.py:594-603` 和 `pilot.py:336-343` 都只检查：
     - 非空
     - 不等于原文
     - 长度不过长
2. Mechanism story：
   - 完全成立。代码里没有任何“方向真的反了”的语义校验。
3. Quantitative impact：
   - 不能从现有 JSON 独立量化。persisted results 不保留 negation-vs-known_outcome 的判定。
4. 我的结论：
   - **P1 structural risk，成立。**

## Bug 5

**Claim:** pre 用 LLM rewrite outcome，post 用 generic target-only probe。

1. 行号：
   - 引用的代码位置基本对，但 **mechanism 被 audit 讲错了**。
   - 真正的分流条件不是 period，而是 `known_outcome_available`：
     - `run_diagnostic_2.py:144-151`：没有真实 outcome 的 case 被标准化成 `known_outcome=""`
     - `pilot.py:306-323`：`is_generic = not known or known == "unknown_post_cutoff"`
2. Mechanism story：
   - 所以 current pipeline 不是“所有 pre 都走 LLM negation，所有 post 都走 generic”。
   - 用当前结果 JSON 直接数：

```python
Counter((c["period"], c["known_outcome_available"]) for c in cases)
# pre_cutoff:  True 115, False 217
# post_cutoff: False 274
```

   - 这意味着：
     - post 在当前数据里确实全是 generic
     - 但 pre 里只有 `115/332` 有真实 outcome，另外 `217/332` 也走 generic/unknown 路
   - 所以真正的 structural confound 是 **probe modality by outcome availability**，不是 audit 写的那个“纯 pre/post probe asymmetry”。
3. Quantitative impact：
   - audit 自己也承认无法从 persisted JSON 量化；但就连它的 mechanism 分组都写错了。
4. 我的结论：
   - **这条需要重写。问题不是没有，表述错了。**

## 额外检查

1. `score_case_from_batches` 的 `fo_flip` 覆盖路径：
   - 是真的。`pilot.py:665` 会覆盖 `cfls_per_case` 内部的 `false_outcome_flip`。
   - audit 末尾说“legacy `run_pilot` path 会和 batched path 分歧”这句又错了；`pilot.py:1072` 在 legacy path 也做了同样覆盖。
2. `cfls_per_case` slot 迭代逻辑：
   - 没发现额外 P0/P1。CFLS 本体按 `reversal_target_field` 收窄 scored keys，`per_slot` 只是展开所有 slot 供解释用。
3. `LLMClient.batch_chat_concurrent` 的 `failure_isolated` retry/cache：
   - 没发现 bug。`_batch_with_retry` 在 retry pass 里调用 `bypass_cache=True`；`llm_client.py:192-195` 只有在 `not bypass_cache` 时才读缓存，因此 retry 不会吃回旧 cache。
   - 它没有“重置成新 cache key”；它复用同一个 prompt-hash，并在成功后覆盖保存。这个行为是对的，不是 bug。
4. `aggregate_case_results` / `build_output_payload` denominator：
   - 没发现额外 P0/P1。
   - 真问题只是 Bug 2 那种“available-case mean 容易被误读”，但 JSON 里分母并不缺失。

## 结论

我不会给这份 audit `PASS`。原因不是“bugs 都不真实”，而是它把几个关键点说歪了：

- Bug 2 被夸成了 P0 pipeline bug，但源码和输出 JSON 都已经显式暴露分母。
- Bug 5 把 probe 分流条件说错了；当前实现按 `known_outcome_available` 分流，不是按 period 纯二分。
- Bug 1 的 schema 缺陷是真实的，但 audit 没有用现有 persisted artifacts 独立证明它就是 `121/606` NP fail 的直接主因。
- Bug 3 的核心发现是真的，但它自己的 rate denominator 表写得不严谨。

建议：Phase A 重做，但不是推倒重来。保留 Bug 3 / Bug 4；把 Bug 1 改写成“real schema hazard, causal attribution not yet proven”；把 Bug 2 降级为 reporting issue 或删掉；把 Bug 5 改写成 `known_outcome_available` 驱动的 probe-modality confound，并重新分层。

Verdict: ITERATE
