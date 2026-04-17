# amber-mirror-lattice / G3 Data-Integrity Review

## Scope

直接核对了以下四个文件，并以 `diagnostic_2_results.json` 为主做逐 case 独立重算：

- `data/results/diagnostic_2_results.json`
- `data/results/diagnostic_2_results.v3_pre_amber.json`
- `data/results/quick_stats_amber.txt`
- `data/results/sensitivity_analysis.json`

结论先行：新的 D1 结果在数学上是自洽的。`meta`、case-level metrics、`quick_stats_amber.txt` 和 `sensitivity_analysis.json` 彼此对得上。存在 residual `None`，但都能追到明确的 task-level invalidation，不是无来源漂移。

## 1. Schema 完整性

- 606/606 cases 都有 `cpt_mode` 顶层字段。
- 606/606 cases 的 `case.metrics` 都有以下 6 个新字段：
  - `fo_flip_direct_strict`
  - `fo_flip_direct_hedged`
  - `fo_flip_direct_label`
  - `fo_flip_impact_strict`
  - `fo_flip_impact_hedged`
  - `fo_flip_impact_label`
- 缺字段计数全部是 0。
- `cpt_mode` 的 missing/null 计数都是 0。

存在的 residual `None` 只出现在值层，不出现在 schema 层：

- direct `strict/hedged/label`: 各 6 个 `None`
- impact `strict/hedged/label`: 各 15 个 `None`

这些 `None` 都能解释：

- direct 的 6 个 `None`：
  - 4 个来自 `false_outcome_cpt` 自身 invalid：
    - `v3_l_061`
    - `v3_l_087`
    - `exp_186`
    - `exp_206`
  - 2 个来自 `false_outcome_cpt` 本身有效，但整个 task 被标成 `task_output_invalid`，原因是 `original` response 的 evidence 长度越界：
    - `v3_l_139`
    - `exp_243`
- impact 的 15 个 `None`：
  - 11 个来自 `false_outcome_cpt` invalid，主要是 `evidence.quote` 长度 > 120 或 evidence 为空：
    - `v3_l_110`
    - `v3_l_171`
    - `v3_l_216`
    - `v3_l_136`
    - `v3_l_215`
    - `v3_l_139`
    - `v3_l_192`
    - `exp_152`
    - `exp_169`
    - `exp_199`
    - `exp_264`
  - 4 个来自 `false_outcome_cpt` 有效，但 task 仍是 `task_output_invalid`，原因是 `original`，有一例连同 `semantic_reversal` / `neutral_paraphrase` 也 invalid：
    - `v3_h_199`
    - `v3_l_231`
    - `exp_243`
    - `exp_253`

判断：schema 完整；`None` 不是 silent corruption，而是 flatten 后未单独 surface 的 task-level invalidation。

## 2. Per-stratum 一致性

按 `period/anchor_binary` 从 606 个 cases 重算，和 `meta.n_total_by_stratum` 完全一致：

- `pre_cutoff/strongly_anchored = 187`
- `pre_cutoff/weakly_anchored = 145`
- `post_cutoff/strongly_anchored = 140`
- `post_cutoff/weakly_anchored = 134`

总和：

- `187 + 145 + 140 + 134 = 606`
- 等于 `meta.n_cases_completed = 606`

`n_scored_by_task_x_stratum` 也与 case-level 重算完全一致：

- direct `cfls`:
  - `180 + 144 + 134 + 133 = 591`
- impact `cfls`:
  - `182 + 143 + 134 + 124 = 583`

`cf_failed_by_stratum` 也完全一致：

- `sr_direction`: `5 + 4 + 1 = 10`
- `sr_fund_impact`: `4 + 3 + 1 = 8`

## 3. Diff vs v3 baseline

### CF failure rate

按 task 独立重算：

- direct `cf_generation_failed`: `156/606 = 25.7%` 降到 `10/606 = 1.7%`
- impact `cf_generation_failed`: `158/606 = 26.1%` 降到 `8/606 = 1.3%`

合并两条任务线看：

- 总 CF failure cells: `314/1212 = 25.9%` 降到 `18/1212 = 1.5%`

### `n_scored (cfls)` 恢复量

- direct `cfls`: `447 -> 591`，恢复 `+144`
- impact `cfls`: `434 -> 583`，恢复 `+149`
- 合计 scored entries: `881 -> 1174`，恢复 `+293`

### `fo_flip_*_strict` 是否和 v3 一致

- direct strict：
  - v3 `true count = 26`
  - new strict `true count = 26`
  - 共有 599 个 old/new 同时非空的 cases，逐 case `0` 个 mismatch
  - 只有 `exp_266` 是 `old None -> new False`
  - 原因：旧版把一个 `direction=neutral` 的有效 CPT 留成 `None`；新版 strict 将其稳定落为 `False`，hedged 落为 `True`
- impact strict：
  - v3 `true count = 3`
  - new strict `true count = 3`
  - 共有 589 个 old/new 同时非空的 cases，逐 case `0` 个 mismatch
  - 只有 `v3_l_205` 和 `exp_164` 是 `old None -> new False`
  - 原因：旧版这两例都因为 `evidence.quote` 超长导致 `false_outcome_cpt` invalid；新版输出变短后恢复为有效，但都只是 non-flip

结论：strict 与 v3 的布尔判定在重叠样本上逐 case 完全一致；新增 evaluable 的 3 例全是 `False`，所以 strict true count 不变。

### `fo_flip_*_hedged` 比 strict 多多少

- direct: `106 - 26 = +80`
- impact: `58 - 3 = +55`

同一指标下 strict/hedged 的 non-null denominator 不变：

- direct: `600`
- impact: `591`

### MH OR 方向

我从 case-level 数据独立重建了 4 个分层 2x2 表，结果与 `sensitivity_analysis.json` 完全一致：

- direct strict pooled MH OR = `0.5046947171`
- direct hedged pooled MH OR = `0.6375964690`
- impact strict pooled MH OR = `0.0`
- impact hedged pooled MH OR = `1.9528777812`

按当前表方向，OR < 1 表示 `post > pre`，OR > 1 表示 `pre > post`。因此：

- direct strict：`post > pre`
- direct hedged：`post > pre`
- impact hedged：`pre > post`
- impact strict 也是 `post > pre`，但因为两个 pre-flip cell 都是 0，pooled OR 退化成 0

### `cpt_mode` 分布

case-level 重算：

- `generic_post_cutoff = 491`
- `llm_negated = 115`
- 总和 `491 + 115 = 606`

与 `quick_stats_amber.txt` 完全一致。

## 4. Cell 稳定性

对 strict surface 做了 old v3 vs new D1 的 `period x anchor_binary` contingency cell 稳定性检查，结果是：

- 没有任何一个 strict cell 发生 `非空 -> 空` 或 `空 -> 非空` 的转换
- `cell_transitions = 0`

需要特别指出的只有 3 个 `old None -> new valued` 恢复样本，但它们都只是把已有非空 cell 的 total 增加 1，且全部是 non-flip，因此不会改变 zero-cell 结构：

- direct `pre_cutoff/strongly_anchored`: `exp_266` 恢复为 strict `False`
- impact `post_cutoff/strongly_anchored`: `exp_164` 恢复为 strict `False`
- impact `post_cutoff/weakly_anchored`: `v3_l_205` 恢复为 strict `False`

因此：

- strict true counts 没漂
- zero-cell pattern 没漂
- MH / Fisher 方向解释没漂

## 5. Quick-stats 数字 cross-check

从 `quick_stats_amber.txt` 随机抽 3 个数字，独立从 `diagnostic_2_results.json` 重算，全部命中：

- `cfls_direct pre(n=324)`：
  - 重算为 `pre_cutoff` 下 direct `cfls != None` 的 cases
  - `180 + 144 = 324`
- `direct (hedged) post: 58/272`：
  - 重算为 `post_cutoff` 下 `fo_flip_direct_hedged == True` 的 58 例
  - evaluable denominator 为 `139 + 133 = 272`
- `cpt_mode generic_post_cutoff = 491`：
  - 直接按 case 顶层 `cpt_mode` 计数得到 491

## Bottom Line

新的 D1 结果在内部是一致的：

- schema 完整
- stratum 总和对账正确
- `quick_stats` 与 `sensitivity` 都能由 case-level 数据独立重算复现
- strict surface 与 v3 baseline 在共享样本上逐 case 完全一致
- 剩余 `None` 都有明确来源

唯一需要在 `PILOT_RESULTS` 里保持明确的地方，是 CPT 统计的 denominator 不应默认写成 606，而应按实际 evaluable 数写成：

- direct CPT denominator: `600`
- impact CPT denominator: `591`

Verdict: PASS
