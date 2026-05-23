# WS0.5 基建主题整体质量审 + 第一性原理简化审 (2026-05-23)

引用 baseline: commit dd9a328  
范围: §5 (E-6) / §6 (E-8, E-9) / §7 (E-10) / §8 / §9 基建相关条目  
分类: 必须改 / 推荐改 / 仅 flag

## Dim 1 — 整体一致性

### 跨节术语一致性

| 术语 | 定义 / 主引用 | 跨节引用 | 判定 |
|---|---|---|---|
| Tier A | §6.1 `pilot_raw_responses.jsonl`, reviewer-facing evidence, normal git (memo:819, 823-833) | §6.3 Path A sample plausibility; §6.4 storage; §8 deliverables; §9 #6 | 一致。Tier A 不再被说成 repo-only full replay source。 |
| Tier B | §6.1 `data/cache/ws0_5_response_cache.sqlite`, full-CLS + auto-tune private cache (memo:820, 834-847) | §6.3 Path B; §6.4 backup; §8 comment; §9 #11 | 一致。§6.3/§6.4 都说 Tier B 丢失不影响 Path A。 |
| Path A | reviewer-facing hash + provenance + Tier-A sample (memo:928-959) | §6.4 Tier B bullet; §6.5 disclosure; §9 #6 | 一致。公共复现路径没有重新滑回 full hard-fail replay。 |
| Path B | author-internal replay / bug-fix path (memo:963-987) | §6.1 Tier A/B role; §6.4 backup; §8 `replay_factor_values.py`; §9 #6/#11 | 一致。唯一需注意: Path B 的 diagnostic `--allow-missing` 是额外私人工具,不是 closure 核心。 |
| `run_inputs` | §6.2 顶层 run-wide provenance block (memo:868-895) | §6.3 Path A provenance check; §6.5 method match; §9 #6 | 大体一致。`pricing_snapshot` 放在 `run_inputs` 里有 scope 混杂,见 Dim 2。 |
| `canonical_table_hash` | §6.2 provenance top-level; §6.3 Path A guarantee (memo:895, 932-959) | §6.5 paper statement; §8 verifier; §9 #6 | 一致。它是 Path A 的核心 integrity artifact。 |
| `meter_totals_by_task_phase` | §7.3 checkpoint meter state (memo:1099-1109) | §7.2 per-task/phase budget report; §8 metered client; §9 #13 | auto-tune 场景一致; full-CLS / pilot heavy phase crash-resume 的 meter restore 没讲清,见必须改 M3。 |
| SQLite cache key fields | §6.1 key `(rendered_prompt_sha256, requested_model_slug, decoding_params_sha)` and resume columns (memo:838-845) | §6.1 per-record fields list (memo:851-857) | 不一致。key/resume 所需的 `decoding_params_sha`, `phase`, `cls_item_id` 不在 per-record list 里,见必须改 M1。 |

### Decision → text 对齐(精神层)

| 决策来源 | 决策精神 | memo 当前 prose | 判定 |
|---|---|---|---|
| E-6 [USER] + [CODEX] (`.scratch`:76-85) | AKShare master-data, deterministic evidence-tier disambiguation, LLM only offline/user-reviewed smoke | §5.2 R2-R4 deterministic; §5.3 LLM alias tier-3 only after user review, LLM disambiguation diagnostic-only (memo:632-766) | 守住。当前没有 LLM per-match count path drift。 |
| E-8 [USER] (`.scratch`:90-103) | database cache, `data/cache/`, private backup; no LFS | §6.1 SQLite Tier B; §6.4 private Kaggle; no Git LFS (memo:819-1013) | 守住。具体 schema 是 CC surface,需要简化/修正字段边界。 |
| E-9 [USER] (`.scratch`:105-110) | drop pyarrow lock; keep canonical hash + hard-fail replay | §6.3 Path A canonical hash; Path B hard-fails on missing/corrupt/duplicate/hash mismatch (memo:951-983) | 守住。并且 reviewer-facing / internal 分家符合 2026-05-22 repro norms。 |
| E-10 [USER] (`.scratch`:112-119) | one metered DeepSeek client replaces estimator + ledger | §7.1 one wrapper; §8 client module; §9 #13 client + report (memo:1047-1075, 1138, 1188) | 守住。2x/5x rail constants是 CC-default / old design residue,见 R3。 |
| Issue #5 older decision (`ws0_5_issue_decisions`:108-117) | WS0.5 owns schema/quota/check stub; WS4 implements full check | §9 #7/#8/#9 retains schema/quota/stub (memo:1182-1184) | 精神可追溯,但 #9 stub 是 weak closure artifact,见 R4。 |

Decision-source caveat: E-10 rail multipliers在来源文件里不完全一致。`.scratch/ws0_5_decision_log.md` 标为 `[CC-DEFAULT]` (2x/5x carried from v0.3, not re-decided),而 `ws0_5_issue_decisions.md` 写成 "chosen per user"。按本轮 audit 原则,应把它当未充分祝圣的 CC surface 来审。

### 跨节因果链

- Path A / Path B 因果链现在闭合: §6.3 说 reviewer 不需要 Tier B,§6.4 同步说 Tier B 丢了 Path A 不受影响,§9 #6 也同样表述。无 must-fix。
- §6.1 cache-key prose 与 per-record schema 不闭合: key/resume 需要的字段没有全部进入字段列表;另有 `provider headers` 被说成 snapshot 缺失时的 traceability 依据,但字段列表没有存它。见 M1。
- §5.3 smoke 的因果链缺 artifact: §5.3 说 smoke result + decision 记入 closure notes,§9 #3 要 smoke decision recorded,但 §8 没有 closure notes / smoke report 路径。见 M2。
- §7.2/§7.3 对 auto-tune checkpoint 对得上;但 full-CLS / pilot heavy phases 若 crash 或 hard rail halt,§7.3 只说 SQLite 是 resume state,没有说 meter state 如何进入最终 §7.2 budget report。见 M3。

## Dim 2 — 第一性原理简化(over-engineering 探测)

### SQLite cache schema (§6.1)

- 功能边界: 存 raw provider response + 可重建 cache identity,支持 skip/resume、Path B replay、budget token audit。它不需要成为通用实验数据库。
- 当前 surface: Tier A JSONL + Tier B SQLite; composite key; indexed resume columns; per-record fields `id`, `task`, prompt path/SHA, input/rendered prompt hashes, `response_text`, provider trace fields, model/request params, timestamp, tokens; Tier A 额外 `prompt_sent`。
- 候选移除项:
  - `response_id` — 如删,失去 provider support / request traceability;判定: 保留或 weak candidate,不是强删。
  - `model_snapshot` — 如删,失去 closed-API version disclosure;判定: 保留。
  - `request_timestamp` — 如删,失去 per-call date audit;若 `api_call_date_window` 足够则可弱化,但 snapshot 不可用时仍有具体能力;判定: weak candidate,不优先。
  - `prompt_sent` in Tier A — 如删,reviewer 无法直接抽看真实 prompt;判定: 保留。
- 必须改 M1: schema 自身不一致。`decoding_params_sha`, `phase`, `cls_item_id` 是 key/resume 语义需要的字段,但不在 per-record fields list;`provider headers` / `model_snapshot_unavailable` 被 prose 依赖,但字段列表没有承载。这个不是措辞漂移,会直接影响实现者能否建正确唯一键和 resume query。

### factor_provenance.json (§6.2)

- 功能边界: 给 Path A 一个 reviewer-readable provenance manifest;给 Path B / debug 一个 cell-to-source trace。run-wide constant 应记录一次,不要 per-cell 复制。
- 当前 surface: `run_inputs` 约 9 个 run-wide fields;`canonical_table_hash`;每 cell 的 `value`, `source_raw_response`, `prompt_sha`, `parser_version`, `derived_from`, `transformation_sha`。
- 候选移除项:
  - `pricing_snapshot` inside `run_inputs` — 如删,失去在 factor provenance 文件里直接看到价格;但价格不影响 factor value,§7 budget report 已有 report header / `pricing_snapshot_id`。判定: strong candidate for removal from factor provenance,可归 budget artifact。
  - per-cell `prompt_sha` — 如删,失去逐 cell 快速查看 prompt SHA;但 fixed run 已在 `run_inputs.prompt_template_shas` 和 cache row 中记录。判定: strong candidate for consolidation,除非同一 factor table 允许混用 prompt versions。
  - per-cell `parser_version` — 如删,失去 mixed parser version 表达能力;但 confirmatory frozen run 不应混 parser。判定: strong candidate for consolidation到 run/task level或 transformation manifest。
  - per-cell `transformation_sha` — 如删,失去每个 factor 单独指向 collapse/scoring code 的能力;这比 `parser_version` 更有具体价值。判定: weak candidate;可保留为 per-factor,不一定 per-cell。
  - `tier_b_cache_sha256` — 如删,失去私有 Path B archive identity check;判定: 保留,但只作为 author-internal provenance。

### Metered client + safety rails (§7.1)

- 功能边界: 所有 V4 Pro 调用统一计 token/USD,防 runaway spend,生成实际预算报告。它不应重建旧的 estimator/ledger 子系统。
- 当前 surface: one wrapper, in-process meter keyed by `(task, phase)`, pricing snapshot once, soft/hard rail, budget report, checkpoint meter totals, cache token cross-check。
- 候选移除项:
  - `soft_limit_factor: 2.0` + concurrency throttle — 如删,失去早期 warning/throttle;hard halt 仍能防 catastrophic runaway。若 WS0.5 实际没有复杂并发,throttle 是 strong candidate for removal或降级为 warning-only。
  - `hard_limit_factor: 5.0` — 如删,失去自动 halt bug-protection。判定: 保留 rail 概念;具体 5x 是 weakly justified CC-default,应被用户明确接受或配置化。
  - pricing snapshot once at run start — 如删,预算报告和 paper compute disclosure 无价格基准。判定: 保留;这已经是最简,不需要 daily epoch。

### Path A / Path B (§6.3)

- 功能边界: Path A 服务 reviewer 快速验证;Path B 服务作者 post-processing replay/debug。两者不能互相抬高 SLA。
- 当前 surface:
  - Path A: canonical hash verifier, `run_inputs` check, Tier-A sample skim。
  - Path B: replay script from Tier A+B+code, hard-fail, optional diagnostic partial output。
- 候选移除项:
  - Path A item 3 Tier-A sample skim — 如删,reviewer 只能看 hashes/provenance,看不到 prompt/output 行为。判定: 保留。
  - Path B hard-fail duplicate check — 如删,cache corruption可 silent pass。判定: 保留。
  - `--allow-missing` diagnostic mode — 如删,失去 triage incomplete artifact 的便利;不影响 Path A 或 normal Path B。判定: flag-only / weak candidate。
- 整体: 分家本身是当前 §6 最重要的简化,不应再把 Tier B full replay作为 reviewer-facing closure。

### Entity pipeline + §5.3 smoke

- 功能边界: 用证券主数据和 deterministic evidence tiers 计算 precision-first recurrence count;LLM 只在 main run 前证明它是否值得贡献 alias recall。
- 当前 surface: R1-R5 pipeline; tiered alias table; broader-universe risk; type/date compatibility; R4 unresolved log; LLM alias smoke; LLM disambiguation diagnostic smoke; ancillary prompts; closure note。
- 候选移除项:
  - LLM alias tier-3 mechanism — 如删,失去在 master data 之外补充真实别名 recall 的能力;因每条都 user review,判定: 保留。
  - LLM disambiguation smoke — 如删,失去对 deterministic R4 false negatives 的 sample characterization;但它不进入 main path。判定: flag-only,不应扩成 closure-heavy workflow。
  - smoke sample size `~30-50` — 如删,失去最低统计/人工工作量边界;这是 CC-default但 surface 小。判定: weak keep。
- 必须改 M2: smoke decision 没有具体 artifact path。当前 "closure notes" 不在 §8 deliverables,§9 #3 无法客观验收。

### Closure conditions (§9 基建条目)

- 功能边界: WS0.5 closure 应对应可检查 artifact,不应把 WS4 placeholder 或重复条款当成独立 gate。
- 当前 surface: #3 entity alias/smoke; #5 auto-tune configs/logs; #6 reviewer reproducibility; #7 factor schema; #9 check stub; #11 Tier-B backup; #13 metered client + budget report。
- 候选移除/合并项:
  - #6 + #7 both require `factor_schema.yaml` — 如合并,不失能力;减少重复 closure gate。判定: recommend consolidate。
  - #9 `check_pilot_cells.py` stub — 如删,失去 WS4 IO contract placeholder,但不失任何 WS0.5 artifact validation能力;stub/docstring 也容易产生 false closure。判定: strong candidate for removal或降级到 #7/#8 spec的一部分。
  - #11 Tier-B backup — 如删,失去 Path B replay/debug和避免 $200-400 re-call 的私有保险。判定: 保留,但明确不是 Path A。
  - #13 metered client + report — 如删,预算 subsystem 没有可验收实现入口。判定: 保留。

### Paper-level disclosure (§6.5)

- 功能边界: 让论文文本能够承接 Path A,而不是只在 repo 里有 artifact。
- 当前 surface: reproducibility statement; method ↔ `run_inputs`/config match; limitations for closed API / nondeterminism / private Tier B。
- 候选移除项:
  - reproducibility statement — 如删,Path A 不可被 reviewer 找到。判定: 保留。
  - method ↔ `run_inputs` match — 如删,artifact 与论文 claim 脱钩。判定: 保留。
  - limitations — 如删,closed API drift/private cache 风险不披露。判定: 保留。
- 整体: 这三件套不是 over-engineered;它是 §6 校准后真正 reviewer-facing 的最小 paper layer。

### Budget report + checkpoint (§7.2-§7.3)

- 功能边界: 保证实际 spend 可按 task/phase 汇总,并且 crash/resume 不破坏 rails 和最终 report。
- 当前 surface: `budget_summary.py`, markdown report, auto-tune checkpoint with `meter_totals_by_task_phase`, no heavy-phase checkpoint because SQLite cache is resume state。
- 必须改 M3: heavy full-CLS / pilot phases 仍可能 crash 或 hard halt。§7.1 说 meter 是 primary budget mechanism,§7.2 dump meter,但 §7.3 只给 auto-tune checkpoint;如果 heavy phase resume 后 in-process meter 从零开始,final report会漏掉已完成 cache rows,rails也可能 undercount。必须在设计层说明 heavy-phase meter如何从 SQLite token rows恢复,或统一持久化 meter snapshot。

## Dim 3 — 「停下来」检查

| Component | 目标功能 | 当前 surface | 漏/持平/超出 | 处置 |
|---|---|---|---|---|
| §5 R1-R5 recurrence pipeline | deterministic, precision-first count; no LLM in count path | full-CLS topic index, AKShare alias table, type/date filters, evidence-tier R4, count compute | 持平 | 保留。R4 unresolved log有具体 audit 能力。 |
| §5.3 LLM smoke | decide whether LLM aliases earn tier-3; characterize R4 misses | alias-gen smoke, disambig smoke, two ancillary prompts, closure notes | 漏 + 小超出 | M2: artifact path missing。Disambig smoke仅 flag,不要扩成 main workflow。 |
| §6.1 SQLite cache | raw response cache + key index + resume state | two stores, composite key, resume columns, per-record fields | 漏 | M1: key/resume/header fields与 schema list 不闭合。 |
| §6.2 provenance | Path A manifest + cell trace | `run_inputs`, canonical hash, per-cell prompt/parser/transformation fields | 超出 | R1/R2: per-cell triple和 pricing snapshot 是主要简化候选。 |
| §6.3 Path A/B | separate reviewer verification from author replay | Path A hash/provenance/sample; Path B hard-fail replay | 持平 | 保留分家。`--allow-missing`仅 flag。 |
| §6.4 storage/backup | protect private Tier B without public/LFS burden | normal-git Tier A; git-ignored Tier B; private Kaggle | 持平 | 保留。Path A 不依赖 Tier B 的声明一致。 |
| §6.5 paper disclosure | make Path A visible in paper | statement, method match, limitations | 持平 | 保留三件套。 |
| §7.1 metered client | token/USD accounting and runaway protection | wrapper, in-process meter, pricing snapshot, soft/hard rails | 小超出 | R3: soft throttle + exact 2x/5x constants需重新 justify。 |
| §7.2 budget report | actual spend by task/phase | `budget_summary.py`, markdown report | 漏 | M3: heavy-phase resume后的 meter source 未闭合。 |
| §7.3 checkpoint | resume short auto-tune without losing budget state | per-task checkpoint with `meter_totals_by_task_phase`; SQLite for heavy phases | 漏 | M3。auto-tune部分已对齐。 |
| §8 deliverables | list implementable artifacts | configs, scripts, client, data outputs | 漏 | M2: no smoke report/closure notes artifact。 |
| §9 closure | objective exit gates | #3/#5/#6/#7/#9/#11/#13 | 超出 + 漏 | R4: #6/#7 duplicate; #9 stub weak; #3 not verifiable until M2 fixed。 |

## 综合结论

- 必须改: 3 条
  - M1: §6.1 SQLite key/resume/trace fields 与 per-record schema 不闭合。
  - M2: §5.3 smoke decision 没有可验收 artifact path,§8/§9 链路断。
  - M3: §7 heavy-phase crash/resume 下 meter state 与 final budget report/rails 不闭合。
- 推荐改: 4 条
  - R1: `factor_provenance.json` per-cell `prompt_sha` / `parser_version` / `transformation_sha` 有 run-wide 重复,优先合并到 task/run/factor level。
  - R2: `pricing_snapshot` 不应默认属于 factor provenance;它更像 budget report header。
  - R3: `soft_limit_factor: 2.0` + concurrency throttle 和 `hard_limit_factor: 5.0` 是 CC-default常数;hard rail有用,soft throttle/具体倍数需重审。
  - R4: closure #6/#7 可合并;#9 `check_pilot_cells.py` stub 是 strong candidate for removal或降级,因为它不验证 WS0.5 产物。
- 仅 flag(展示给用户判断): 5 条
  - Path A / Path B 分家目前是正确简化,不要倒回公共 full replay SLA。
  - `response_id` / `model_snapshot` / `request_timestamp` 不是明显可删字段;它们有 closed-API traceability 具体能力。
  - Tiered alias table 的 `source` / `effective_dates` / `risk` 字段有具体 disambiguation 能力,不是纯 future-proofing。
  - LLM disambiguation smoke 只要保持 diagnostic-only 就可接受;不要把它升级为 main path或重 closure。
  - §6.5 paper disclosure 三件套是 reviewer-facing 最小层,不是 over-engineering。
- 整体评估: v0.4 cont. 已经把最大 drift 修回来了,尤其 §6 的 Path A/B 分家是正确方向。剩余问题主要不是大设计错误,而是三个 closure/实现边界断点和几处 CC-default surface 还没有被第一性原理压到最小。
