# amber-mirror-lattice / G2a Hostile Review

## Scope

1. `git log --oneline 87f0211..HEAD` 结果只有一个提交:
   - `4421da2 amber-mirror-lattice: Phase A audit + Phase B bug fixes (5 bugs)`
2. 已跑 `git show 4421da2` 并逐段核对以下文件:
   - `config/prompts/counterfactual_templates.yaml`
   - `scripts/run_diagnostic_2.py`
   - `scripts/quick_stats.py`
   - `scripts/sensitivity_analysis.py`
   - `scripts/rescore_fo_flip.py`
   - `src/metrics.py`
   - `src/masking.py`
   - `src/pilot.py`
3. 已补执行验证:
   - `conda run -n rag_finance python scripts/run_diagnostic_2.py --n-cases 10 --output data/results/_smoke_test_review.json`
   - `conda run -n rag_finance python scripts/quick_stats.py`
   - `conda run -n rag_finance python scripts/sensitivity_analysis.py`
   - `conda run -n rag_finance python scripts/rescore_fo_flip.py`
   - 一个 legacy probe: `tc_001` 走 `prepare_conditions()` + `run_single_case()`

## Findings

### High

1. `scripts/quick_stats.py` 和 `scripts/sensitivity_analysis.py` 会静默接受缺少新 key 的旧结果文件，然后产出空白/`no_data` 的 CPT 统计，而不是 fail fast。
   - 位置:
     - `scripts/quick_stats.py:65`
     - `scripts/quick_stats.py:147`
     - `scripts/sensitivity_analysis.py:45`
     - `scripts/sensitivity_analysis.py:77`
   - 证据:
     - 当前 `data/results/diagnostic_2_results.json` 的 `meta.pipeline_version` 是 `3`，但 case `metrics` 仍只有旧 key:
       - `cfls_direct`, `cfls_impact`, `fo_flip_direct`, `fo_flip_impact`, `intrusion_direct`, `intrusion_impact`
     - 直接运行 `quick_stats.py` 时，CPT 段落是空的，`cpt_mode distribution: {None: 606}`。
     - 直接运行 `sensitivity_analysis.py` 时，4 个新 metric 全部变成 `pooled OR=None / no_data`。
   - 影响:
     - 不 crash，但会给出“像是跑完了”的误导性输出。
     - 在 Phase D 前用这些脚本读旧 baseline，会误判效应不存在或不可见。
   - 修复建议:
     - 在两个脚本启动时显式校验 `fo_flip_*_strict/_hedged` 和 `cpt_mode` 是否存在；不存在就直接报错。
     - 加 `--input` 参数，允许直接读 `diagnostic_2_results.rescored_v2.json`。
     - 如果想兼容旧文件，必须 loud warning，并明确降级到 strict-only legacy key，而不是静默空输出。

### Medium

2. 默认 `--n-cases 10` smoke 不是有效覆盖；它根本没打到 Bug 4 的 `llm_negated` 路径，也没覆盖 neutral / malformed ORIG / no-key-entities 这些你点名的边界。
   - 位置:
     - `scripts/run_diagnostic_2.py:268`
     - `scripts/run_diagnostic_2.py:278`
     - `scripts/run_diagnostic_2.py:290`
     - `scripts/run_diagnostic_2.py:663`
   - 证据:
     - `load_eligible_cases()` 是“先过滤，再按文件顺序截前 N 个”。
     - 我重跑的 `data/results/_smoke_test_review.json` 里 10/10 都是:
       - `known_outcome_available=False`
       - `cpt_mode=generic_post_cutoff`
     - 这 10 个 case ID 是:
       - `v3_h_176`, `v3_h_126`, `v3_l_091`, `v3_h_042`, `v3_l_047`, `v3_l_181`, `v3_l_014`, `v3_h_181`, `v3_l_169`, `v3_l_001`
     - 数据集当前没有任何 `key_entities=[]` 的 case。
     - 数据集有 76 个 `expected_direction="neutral"` case，但 `load_eligible_cases()` 直接过滤掉了。
     - 10-case smoke 里没有任何 malformed ORIG；而当前 606-case baseline 里实际有 14 个 malformed ORIG。
   - 影响:
     - 这个 smoke 只能说明“generic CPT + 常规解析路径没炸”。
     - 它不能证明 Bug 4、也不能证明 pre-cutoff CPT、也不能证明 malformed ORIG 分支。
   - 修复建议:
     - 加 `--case-ids` 或单独的 smoke fixture 文件，不要靠“前 10 个”。
     - smoke 至少要固定覆盖:
       - 一个 pre-cutoff 且 `known_outcome_available=True` 的 case
       - 一个 hedged flip case
       - 一个 malformed ORIG fixture
       - 一个 neutral fixture
     - 如果数据集中没有 `key_entities=[]`，就别把它写成 smoke 目标；要么补 fixture，要么从验收项删掉。

### Low

3. `cfls_per_case()` 里还留着旧的 bool-only FO flip 逻辑；当前行为正确，只是因为 `pilot.py` 的两个 scoring path 又手工 override 了一遍。
   - 位置:
     - `src/metrics.py:506`
     - `src/metrics.py:569`
     - `src/pilot.py:680`
     - `src/pilot.py:1110`
   - 影响:
     - 现在不炸。
     - 但这是双份语义，后续谁直接消费 `cfls_per_case()`，或者某次重构忘了 override，就会静默回退到旧 strict-only bool 逻辑。
   - 修复建议:
     - 把 `cfls_per_case()` 里的 FO flip 判定收敛到 `_detect_fo_flip()`。
     - 让 `metrics.py` 只保留一个 canonical implementation。

## Per-Fix Review

### B1: Relax `changed_spans[].from/to`

- a) 是否实现:
  - 是。`config/prompts/counterfactual_templates.yaml:59` 和 `:63` 的 `maxLength: 200` 已删除，只保留 `minLength: 1`。
- b) 是否破坏 legacy `run_pilot` / `run_single_case`:
  - 没有。这里只影响 CF schema 校验，legacy path 读的是同一个 prompt/schema loader，不涉及返回结构破坏。
- e) 是否 invalidate 现有 cache，Phase D 会不会意外重花 API:
  - 不会因为 B1 本身 invalidate cache。
  - `src/llm_client.py:51` 的 cache key 只哈希 `model + temperature + messages`，不哈希 schema。
  - `src/pilot.py:121` 的 batch pass 0 先吃 cache；只有 validator 仍失败的样本才会在 retry pass 上 `bypass_cache=True`。
  - 所以 B1 的实际效果是: 先前“同一 raw response 因 schema 太严而失败”的 cache 现在更可能直接通过，API 花费应下降，不会上升。
- f) smoke 是否真正 exercise:
  - 默认 10-case smoke 只看到 `sr_direction` 仍有 1 个失败，不能证明这个失败与长 `changed_spans` 无关。
  - 也就是说: code diff 正确，但 smoke 不足以正向证明“长 span case 已恢复”。
- 结论:
  - 实现本身是对的；覆盖证据不够。

### B2: `compute_cf_failure_summary()` + meta surface

- a) 是否实现:
  - 是。`scripts/run_diagnostic_2.py:325` 新增 `compute_cf_failure_summary()`，`build_output_payload()` 在 `:517` 调用并把
    - `n_cf_failed_by_type`
    - `cf_failed_by_stratum`
    - `n_total_by_stratum`
    - `n_scored_by_task_x_stratum`
    写进 `meta`。
- b) 是否破坏 legacy path:
  - 没有。这个改动只在 `diagnostic_2` 输出构造层；legacy `run_pilot()` 不依赖这些字段。
- f) smoke 是否真正 exercise:
  - 是。10-case smoke 输出里这些字段都存在，结构也对。
- 结论:
  - B2 实现到位，没有看到回归。

### B3: `_detect_fo_flip` enum 化 + 下游 variant 化

- a) 是否实现:
  - 是。
  - `src/metrics.py:366` 把 `_detect_fo_flip()` 改成返回 `strict_flip / hedged_flip / no_flip / None`。
  - `src/metrics.py:436` 和 `:447` 新增 strict/hedged 两个 bool projection helper。
  - `src/pilot.py:635` 和 `:1063` 计算 `fo_flip_label`。
  - `src/pilot.py:720-725` 和 `:1147-1152` 把 `fo_flip_*_strict/_hedged/_label` 落到 case `metrics`。
  - `scripts/quick_stats.py:65`、`scripts/sensitivity_analysis.py:45` 改成分别读 strict/hedged variant。
  - `scripts/rescore_fo_flip.py` 已新增，且我实际跑通了。
- b) 是否破坏 legacy `run_pilot` / `run_single_case`:
  - 常规 legacy path 没看到 break。
  - 我对 `tc_001` 做了 legacy probe，`prepare_conditions()` 返回 `cpt_mode=llm_negated`，`run_single_case()` 正常产出全部新 key。
  - `run_pilot()` 主路径本质上只是循环调用这两个函数，所以 common path 没看到破坏。
- c) enum 与下游 consumer 交互是否正确:
  - `cfls_per_case()`:
    - 仍保留旧 bool-only `false_outcome_flip` 逻辑，不是 canonical source。
    - 当前 pipeline 里没出错，因为 `pilot.py` 两个 scoring path 都 override 回 `_detect_fo_flip()` 的 strict/hedged/label。
  - `score_case_from_batches()`:
    - 正确。`src/pilot.py:635-646` 算 label，`:682-685` 写回 canonical 值，`:720-725` 落 top-level metrics。
  - `aggregate_case_results()`:
    - 不读 FO flip，enum 改动对它无直接影响。
  - `quick_stats.py`:
    - 对 fresh data 是对的。
    - 对旧/当前 stale baseline 是错的，见 Findings #1。
  - `sensitivity_analysis.py`:
    - 对 fresh data 是对的。
    - 对旧/当前 stale baseline 会静默变成 `no_data`，见 Findings #1。
- f) smoke 是否真正 exercise:
  - hedged path: 是。10-case smoke 里 direct 有 2 个 `hedged_flip`，我直接核了原始 parsed output:
    - `v3_h_176`: ORIG `up` -> FO `neutral`
    - `v3_h_181`: ORIG `up` -> FO `neutral`
  - malformed ORIG:
    - 默认 10-case smoke 没打到。
    - 但在当前 606-case baseline 上，14 个 malformed ORIG case 经 `rescore_fo_flip.py` 后，对应 label 全部是 `None`，离线评分退化是安全的。
  - neutral case:
    - 没打到。`run_diagnostic_2.py` 在筛样阶段就过滤掉 neutral。
- g) `quick_stats.py` 的 `fo_flip_direct_strict` 等 key 是否真存在；旧数据会不会 crash/误导:
  - fresh case 里这些 key 确实存在。
    - 证据 1: `_smoke_test_review.json` 的 case metrics 有 `fo_flip_direct_strict/_hedged/_label` 和 `fo_flip_impact_*`。
    - 证据 2: legacy probe `tc_001` 也有这些 key。
  - trace 是闭合的:
    - `_detect_fo_flip()` (`src/metrics.py:366`)
    - `score_case_from_batches()` / `run_single_case()` (`src/pilot.py:635`, `:1063`)
    - case `metrics` 写入 (`src/pilot.py:720`, `:1147`)
    - `quick_stats.py` 读取 (`scripts/quick_stats.py:65`)
  - 旧数据不会 crash，但会产生误导性零覆盖/空输出。
    - `quick_stats.py` 会打印空 CPT 段落。
    - `sensitivity_analysis.py` 会打印 `pooled OR=None` / `no_data`。
- 结论:
  - 代码链路本身基本对。
  - 真问题在“reader 对旧/stale baseline 没有 guardrail”。

### B4: polarity check helper

- a) 是否实现:
  - 是。
  - `src/masking.py:557` 新增 `check_negation_polarity_flipped()`。
  - `src/masking.py:652` 在 `generate_false_outcome_cpt()` 里做 check。
  - `src/pilot.py:337` 和 `:369` 在 batched `prepare_fo_cpt_batch()` validator / final acceptance 两处都做 check。
- b) 是否破坏 legacy `run_pilot` / `run_single_case`:
  - 没看到。
  - 我实际跑的 pre-cutoff `tc_001` legacy probe 走到了 `llm_negated`，没退成 `llm_failed`，`run_single_case()` 也成功。
- d) helper 是 check 还是 fallback probe；token 列表是否合理:
  - 它是 check，不是 fallback probe。
  - `src/masking.py:526-529` 的注释写得很明确: token 只用于 validator，不用于生成 probe。
  - 这点没有违反 mode purification。
  - token 列表本身是合理但不完备的中文方向词表:
    - 正向: `上涨/反弹/回升/利好/...`
    - 负向: `下跌/回落/利空/...`
  - 关键点在于它故意做了 permissive fallback:
    - 如果任一侧判成 `neutral` 或 `mixed`，就直接放行。
  - 所以它更像“拦明显没翻向的坏 negation”，不是强语义判定器。这个设计是可接受的。
- f) smoke 是否真正 exercise:
  - 默认 10-case smoke 没有，因为 10/10 都是 `generic_post_cutoff`。
  - 我补跑的 `tc_001` legacy probe 打到了 `llm_negated`，说明这条路径至少能工作。
- 结论:
  - B4 实现方式是 check-only validator，不是 mode impurity。
  - 但默认 smoke 对它几乎没有覆盖价值。

### B5a': persist `cpt_mode` + quick_stats cpt-mode arm

- a) 是否实现:
  - 是。
  - batched path: `src/pilot.py:710`
  - legacy path: `src/pilot.py:1140`
  - `scripts/quick_stats.py:145` 新增 `cpt_mode` 分层臂。
- b) 是否破坏 legacy path:
  - 没有。
  - `tc_001` legacy probe 里顶层 `cpt_mode=llm_negated` 已正确落盘到返回 dict。
- f) smoke 是否真正 exercise:
  - 字段存在: 是。
  - 模态多样性: 否。默认 10-case smoke 的 `cpt_mode` 全是 `generic_post_cutoff`，完全没验证 `llm_negated` / `llm_failed` 分布。
- g) `quick_stats.py` 的 key 是否存在；旧数据会怎样:
  - fresh data: key 存在，路径正确。
  - 旧 data: 不 crash，但 `cpt_mode` 变成全 `None`，分层臂完全失真。
- 结论:
  - producer 端是对的。
  - consumer 端对 stale file 缺 guardrail，且默认 smoke 没验证 modality split。

## Edge-Case Coverage Check

- 没有 `key_entities` 的 case:
  - 当前 `test_cases_v3.json` 里数量是 `0`。
  - 所以默认 smoke 不可能覆盖。
- `expected_direction="neutral"`:
  - 当前数据里有 `76` 个。
  - 但 `scripts/run_diagnostic_2.py:278-280` 直接过滤掉，所以默认 smoke 不可能覆盖。
- ORIG output malformed:
  - 10-case smoke 没覆盖。
  - 当前 606-case baseline 有 `14` 个 malformed ORIG；经 `rescore_fo_flip.py` 后，这些 case 的对应 `fo_flip_*_label` 全部安全退成 `None`。
- hedged flip case:
  - 10-case smoke 覆盖到了。
  - 至少 direct task 上有 2 个明确的 `ORIG=up, FO=neutral, label=hedged_flip`。

## Overall Assessment

- 我认可的部分:
  - B1/B2/B4/B5a' 的代码改动本身是到位的。
  - B3 的 producer 链路基本正确，legacy common path 也没直接炸。
  - `rescore_fo_flip.py` 是实用的补救脚本，我实际跑通了。
- 我不接受直接放行的部分:
  - 你当前 repo 里的 baseline 结果文件还是 stale shape；分析脚本会静默读错。
  - 默认 `--n-cases 10` smoke 对 Bug 4 / llm-negated / neutral / malformed ORIG 的覆盖都是假的或不存在。

## Recommended Next Step Before Phase D

1. 先修 Findings #1:
   - 让 `quick_stats.py` / `sensitivity_analysis.py` 对旧结果 loud fail 或支持 `--input` 指向 rescored 文件。
2. 再修 Findings #2:
   - 做一个真正有代表性的 smoke fixture，不要再用“前 10 个 eligible”。
3. 如果你今天不想重跑 full baseline:
   - 至少基于 `scripts/rescore_fo_flip.py` 的输出做一次正式分析，别让旧 `diagnostic_2_results.json` 继续冒充新 schema。

Verdict: ITERATE
