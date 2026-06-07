# R-1b Historical Family Recurrence — final decisions

**Status**: LOCKED 2026-05-24
**Audit trail**(下游 agent 不需要读;只在需要 debate / 看推导过程时翻):
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/whiteboard_analysis.md` —— 主分析文档
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/construct_stress_test.md` —— (a) construct 段 stress-test
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/construct_second_opinion_claude.md` —— (a) blind second opinion
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/bch_second_opinion_claude.md` —— (b)(c)(h) blind second opinion

---

## 1. Construct(怎么选 reference rows)

| 字段 | 值 |
|---|---|
| Source layer | **L2 subject** |
| Reference rows filter | `is_subject = true AND tradable_at_event = true` |
| Stance | **outcome-leakage proxy** |
| Pool D | **DORMANT**(L2 已有 `tradable_at_event` 字段,本 construct 不需要 L1 扩展) |

**核心 framing**:Recurrence 测的是模型 "用记住的(标的 × 事件家族)→ 涨跌方向关联代替推理" 的关联记忆强度;**涨跌(收益)是隐含变量**。在 A 股 CLS 上下文里,`tradable_at_event=true` 是 outcome 存在性的代理(不需要 R-6 落定 outcome-verifiable schema)。

---

## 2. Family grouping(怎么把 reference rows 归 family)

| 字段 | 值 |
|---|---|
| Primary key | **`target_entity_id`**(单标的) |
| Event collapse | **`event_super_type`**(Scheme A 5 超类;见 `docs/DECISION_20260518_ws0_5_thales_alignment.md` §2.1 / §3.1) |
| Combined family | **`(target_entity_id, event_super_type)`** |

---

## 3. Lookup window(查哪段语料)

| 字段 | 值 |
|---|---|
| Type | **Fixed**(case-independent;Recurrence 保持 case-level factor) |
| Range start | CLS S0 corpus first available `published_at`(~2020-01) |
| Range end | `min(model_cutoff)` from `config/fleet/r5a_fleet.yaml`(对相关子队列取 min;**具体日期 + 哪些子队列计入 min 待 R-1e 裁定 — pending R-1e**) |
| Interval | half-open `[start, end)` |
| Focal article policy | **排除同一 `article_id` 自身**(避免把 focal article 当历史复现);其它不同 `article_id` 的 follow-up / repost 按 no-dedup 计 |

---

## 4. Main variable formula

```text
recurrence_count[case] = COUNT( reference_rows r WHERE
    r.target_entity_id == case.target_entity_id
    AND r.event_super_type == case.event_super_type
    AND r.is_subject == true
    AND r.tradable_at_event == true
    AND r.article_id != case.article_id )

log1p_recurrence_count[case] = log1p(recurrence_count[case])
```

**Reference window**: `[CLS corpus first published_at, min(fleet model cutoff))`,半开(右端点具体日期 + 计入 min 的子队列待 R-1e 裁定 — pending R-1e)。

**Zero policy**: `recurrence_count = 0` 合法,`log1p(0) = 0` 直接进模型,**不**当 missing 剔除(R-4a 锁,R-0 §4.5.D 锁)。

**Dedup policy**: no-dedup(R-0 §4.5.D 锁,C-4 实证支持 0.48% 重复率)。

---

## 5. R-1c session anchor(给 R-1c 的接口说明)

R-1c session 起跑时,R-1b 给的约束清单:

### 5.1 R-1c **必须遵守**(R-0 / R-4a 基础架构层)
- R-0 4 层语料容器(S0 / L1 / L2 / L3 views)
- R-0 entity-first pipeline(entity match → topic-classify / subject ID → tradability check → factor metrics → operators → estimands)
- R-4a "factor metrics 严在 operators 之前"(L1↔L3 边界锁)
- R-4a `log1p(0)=0` 合法、no-dedup 合法、article cluster 可追溯
- R-4a provenance / layer-view hash discipline
- R-4a 标签语言 main / primary / supporting / robustness / appendix

### 5.2 R-1b 给的所有具体选择都是 **参考**(R-1c 自决,不强制继承)
- construct(R-1b 用 L2 subject + tradable)
- 是否加 tradable filter(R-1b 加了)
- window(R-1b 用 fixed `[2020-01, min(model_cutoff))`;右端点具体日期 pending R-1e)
- primary key(R-1b 用单标的)
- transform(R-1b 用 log1p)
- event collapse(R-1b 用 event_super_type)
- denominator(R-1b 是 count 不需要分母;R-1c 若用 share 必须自决分母:article 数 / L1 row 数 / all-target mentions / industry内 / 等)
- 是否 complement-family 去重(避免与 R-1b 高相关)

### 5.3 R-1c **必须做**的 discriminant check(WS0.5 §3.3.3 / §5.4 / §5.5 standing routine)
- 跟 R-1b `log1p_recurrence_count` 算 VIF 和 correlation
- R-1b 给的输入口径是 main variable formula(上面 §4)
- 若 VIF ≥ 10 或 |r| ≥ 0.90,触发 complement-family fallback(§3.3.2)

---

## 6. B-2 schema requirements(R-1b 提的字段需求)

> B-2 schema **字段命名 / 风格 / 整合**留 B-2 statt session 整体 review,这里只列 R-1b 这次 lock-in 的内容需求。

### 6.1 `factor_provenance.run_inputs.per_task.historical_family_recurrence` 必须包含

- `source_layer = L2_subject`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L2_subject_row`
- `reference_rows_filter`: `is_subject = true AND tradable_at_event = true`
- `family_key = [target_entity_id, event_super_type]`
- `event_scheme = Scheme_A_5_supertypes`(明确指明 V3 13-class → 5 supertype 映射的 hash)
- `reference_window`: `start = cls_corpus_first_published_at`, `end = min_fleet_model_cutoff`, `interval = half_open`
- `focal_article_policy = exclude_same_article_id`
- `dedup_policy = no_dedup_reference_rows`
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `requires_pool_d_or_l1_tradability_extension = false`

### 6.2 Provenance hashes(R-1b 计算必须可追溯)

- S0 source snapshot hash
- entity alias table hash
- disambiguation rule hash
- topic-classifier prompt / model / cache hash
- subject-ID prompt / model / cache hash or deterministic rule hash
- layer / view definition hash
- fleet cutoff manifest hash
- tradability master snapshot hash
- sampling manifest hash(when factor values tied to a sampled frame)

### 6.3 L2 build 完成后必须报告的 A/B count delta

- `n_L2_subject_unfiltered`(L2 subject rows 总数,未按 tradable 过滤)
- `n_L2_subject_tradable`(L2 subject + tradable rows 总数)
- `share_nontradable_subject_reference_rows = (n_L2_subject_unfiltered - n_L2_subject_tradable) / n_L2_subject_unfiltered`

预期 share < 5%;若超过提醒 owner reproducibility check。

### 6.4 Topic-classify 范围(成本控制)

**只跑 entity-first 后的 reference rows + candidate case rows**;**不**做 full-CLS topic-classify(成本节约 40-60%)。若 §7.1 conditional reanalysis 激活需扩到对应 L1 reference rows,届时按需补跑。

---

## 7. Robustness / appendix candidates(只 1 个)

### 7.1 Appendix conditional reanalysis(唯一,需 pilot 触发 condition)

| 字段 | 值 |
|---|---|
| 候选 | `target × raw event_type`(对某个 super_type 内拆 13 raw 类) |
| **激活 condition** | pilot N=80 跑完后,某个 super_type 内 `within-bin log1p_recurrence variance > 1.5 × 其他 super_type 中位 variance` |
| 激活后 action | 仅对该 super_type 拆 raw event_type 重算 β3,与 primary β3 对比 |
| 不激活 | **不报,连 prose 都不写**(不是预先 commit 的 robustness) |
| Slot | **Appendix**(不是 main / primary / supporting / robustness 槽) |

### 7.2 名称聚合级别敏感性(R-1f 溢出,pre-commit appendix)

R-1b 的 recurrence_count 适用名称聚合级别敏感性 appendix(entity / 字面名 / core_name 三级重算重跑 β3);规格 canonical 见 `R1f_DECISIONS.md` §6 / §8。**不改主规格**:R-1b 主变量仍为 entity_id 级 `log1p_recurrence_count`(已 locked)。

### 7.3 显式不在 R-1b 范围内的 construct(不进任何 slot)

- **Unfiltered L2 subject**:回答的是 surface text exposure 而非关联记忆,与本 construct 立场不一致
- **L1 mention(任何形式)**:回答的是宽 mention salience 而非主体关联记忆;若需 mention-based salience 留 R-1c session
- **一级 / 二级行业 grouping**:与单标的 firm × event 关联记忆 construct 不一致(行业 outcome direction 在单只标的上不可靠对齐)
- **概念板块 / 指数 / 市值 / 实控人 grouping**:依赖 ex-post 后视镜分类,引入 outcome 之外的 ex-post 信息
- **Outcome direction grouping**:circular — 把测的因变量(outcome direction)塞进自变量(family key)定义
- **Case-relative 滚动窗口 `[T-X, T)`**:与 outcome-leakage proxy 立场不一致(post-cutoff case 把 model cutoff 后才出现的 rows 当 exposure 计数)
- **Per-model 滚动窗口 `[corpus_start, model.cutoff)`**:把 Recurrence 从 case-level factor 变成 case × model factor,与 case-level factor 框架冲突
- **多窗口 grid robustness**:跟主选 fixed window 是不同 construct(case-relative vs model-visible),不在本 R-1b 范围

---

## 8. Standing discriminant input(给 WS0.5 §3.3.3 接口的输入说明)

R-1b 给 WS0.5 discriminant check 框架(§3.3.3 / §5.4 / §5.5,WS0.5 已锁)的输入:

- Recurrence count 在 `(target_entity_id × event_super_type)` 维度、L2 subject + tradable reference rows 上算
- R-1c session 做 VIF / correlation 检查时的对比口径 = 上面 §4 main variable formula
- 触发阈值与 fallback 沿用 WS0.5 §3.3.3(VIF ≥ 10 或 |r| ≥ 0.90 → complement-family fallback §3.3.2)

R-1b 不新增此 routine,仅提供输入接口。

---

## 9. Downstream notes

### R-2(扰动)
- **不受 R-1b 影响**。扰动 eligibility 仍由 R-2 / R-6 定。

### R-5(采样)
- **Pool B base 不变**(L2 ∩ universal admissibility)
- **Pool D 不触发**(R-1b dormant)
- **Pool G 若启用**(salience / recurrence stratified):用 `log1p_recurrence_count` 分层;分层建议在 `event_super_type` 内做,显式保留 low / zero recurrence cases
- R-5 **不应**把 R-1b reference count 偷换成别的口径

### R-4b(power / 统计具体落地)
- pilot 后给 R-4b 的输入:
  - `recurrence_count`(原始 count)
  - `log1p_recurrence_count`(主变量)
  - non-zero rate / zero rate
  - distribution by `event_super_type`
  - correlation / VIF against Target Salience(待 R-1c 锁后)
  - optional: 若 §7.1 condition 触发,raw event_type 拆后的同上统计

### R-1e(因子最终选择确认)
- R-1b **不承诺** Recurrence 一定进 primary;R-1e 根据 pilot effect size / variance / collinearity / interpretability 决定

