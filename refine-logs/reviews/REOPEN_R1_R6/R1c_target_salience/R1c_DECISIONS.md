# R-1c Target Salience — final decisions

**Status**: LOCKED 2026-05-25
**Audit trail**(下游 agent 不需要读;只在需要 debate / 看推导过程时翻):
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/whiteboard_analysis.md` —— Codex 主白板(两阶段 clean-room)
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/whiteboard_analysis_claude.md` —— Claude sub-agent 并行独立白板(双源对照)
- `archive/r4_r5a_lineage/refine-logs/reviews/REOPEN_R1_R6/R1c_target_salience/whiteboard_analysis_stage1_codex_draft.md` —— Codex 阶段 1 草稿

---

## 1. Framing / measurement claim

| 字段 | 值 |
|---|---|
| Stance | **Corpus exposure intensity**(CLS as best-available proxy) |
| Claim | 实体在模型预训练 corpus 里的累计曝光强度;CLS mention count 是 best-available proxy |
| 桥论证 | CLS count → training-data exposure 是**单调代理**(非严格 log-linear,但方向一致) |
| Paper §4.1 措辞风格 | **悬而未决**,留 paper-write 阶段定(两种 candidate 语言风格 — conservative "可观测 CLS" 与 explicit monotone-proxy bridge — 由 paper-write session 选)|

---

## 2. Construct(数哪一层 row)

| 字段 | 值 |
|---|---|
| Source layer | **L1 mention**(`(article_id, target_entity_id)` long-form row)|
| `is_subject` filter | **none** |
| `tradable_at_event` filter | **none**(L1 不带此字段;Salience claim 与 tradable 正交)|
| `salience=core` filter | **none**(R-0 L1 layer 锁后,任何 pair 都计)|
| Intra-article 处理 | **per L1 row 计 1,不乘 `mention_count_in_article`**(与 R-0 §5 inter-article no-dedup + intra-article one row per article 一致)|
| Pool D | **dormant**(L1 mention 不需要 tradable,不触发架构扩展)|

**Salience claim 决定**:任何 mention 都是 exposure,模型预训练时不区分 "顺带提及" 与 "主语提及"。L1 mention 是 corpus exposure intensity claim 的直接 operationalization。

**与 R-1b 分家的硬约束**:R-1b 锁 L2 subject + tradable,R-1c 在 row layer 与 R-1b 分家。这不仅是 framing-driven 选择,**也是保 discriminant check 识别能力的结构性需要** —— 若 R-1c 同 L2 subject + tradable,VIF 必然过高,R-1b §5.3 standing routine 失去信息。

---

## 3. Family granularity / event collapse

| 字段 | 值 |
|---|---|
| Primary key | **`target_entity_id`**(单标的)|
| Event collapse | **none**(全 super_type 合并;salience 是实体属性,不是事件家族属性)|
| Combined family | **`target_entity_id`**(单键)|

**B-2 节省**:main metric 不需要 super_type 标记 → topic-classify 范围与 R-1b 一致(只跑 entity-first 后的 reference rows + candidate case rows),**不扩**。

---

## 4. Lookup window

| 字段 | 值 |
|---|---|
| Type | **Fixed**(case-independent;R-1c 保持 case-level factor)|
| Range start | CLS S0 corpus first available `published_at`(~2020-01)|
| Range end | `min(model_cutoff)` from `config/fleet/r5a_fleet.yaml`(对相关子队列取 min;**具体日期 + 哪些子队列计入 min 待 R-1e 裁定 — pending R-1e**)|
| Interval | half-open `[start, end)` |
| Focal article policy | **不排除同 `article_id`**(case 自身文章在窗口内时也是 model exposure;per Salience claim)|
| 与 R-1b 共享同窗口 | **是**(跨因子 metric 可比,discriminant check 在同口径跑)|

---

## 5. Main variable formula

```text
target_salience_count[case] = COUNT( L1 rows r WHERE
    r.target_entity_id == case.target_entity_id
    AND r.published_at >= cls_corpus_first_published_at
    AND r.published_at < min_fleet_model_cutoff )

log1p_target_salience[case] = log1p(target_salience_count[case])
```

**Reference window**:`[CLS corpus first published_at, min(fleet model cutoff))`,half-open,与 R-1b 同源(右端点具体日期 + 计入 min 的子队列待 R-1e 裁定 — pending R-1e)。

**Zero policy**:`target_salience_count = 0` 合法,`log1p(0) = 0` 直接进模型,**不**当 missing 剔除(R-4a / R-0 §5 锁)。

**Dedup policy**:inter-article no-dedup;intra-article one row per article(per R-0 §5)。

**Denominator**:**none**(raw count + log1p)。Fixed window 下 case-invariant 分母对 case-level metric 是常数缩放,无信息增益。

---

## 6. Discriminant check + fallback(Option C — no metric fallback)

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b §5.3 / WS0.5 §3.3.3 standing routine)|
| 主比较口径 | R-1c `log1p_target_salience` vs R-1b `log1p_recurrence_count`(tradable-filtered;见 `../R1b_recurrence/R1b_DECISIONS.md` §4)|
| Fallback metric | **无 metric-level fallback**(Option C)|
| Trigger 后行动 | discriminant 结果 + Salience effect size + Salience-vs-Recurrence collinearity 喂 R-1e;**由 R-1e 决定 R-1c 是否进 primary**(可能降级到 supporting / exploratory / 不在 confirmatory family)|

**Option C 合法性依据**:
- R-4a §4 明确 "因子总数 + 身份 = R-1e + pilot 数据"
- R-4a 不预承诺 4 个 primary;3 个 primary 也合法
- R-1c session 不替 R-1e 选 factor inventory(memory `feedback_arch_vs_session_scope`)
- R-1c 不预承诺 Salience 进 primary(R-4a / 本 session 一致原则)

---

## 7. Robustness / appendix slot

### 7.1 Pre-commit tail-leverage sensitivity(1 个 pre-commit appendix slot)

| 字段 | 值 |
|---|---|
| 候选 | tail-leverage sensitivity(用 **winsorized log count** 或 **percentile rank** 重跑 β3)|
| Pre-commit vs conditional | **pre-commit**(不论 pilot 结果都做并报)|
| 具体形式(winsorize vs percentile)| 由 B-2 / R-4b 在 pilot analysis 前固定 |
| Slot | **Appendix**(不进 main / primary / supporting / robustness 槽)|
| 测的是 | "primary β3 是否被极少数 mega-target 主导" — paper transparency baseline |

### 7.2 名称聚合级别敏感性(R-1f 溢出,pre-commit appendix)

R-1c 的 target_salience_count 适用名称聚合级别敏感性 appendix(entity / 字面名 / core_name 三级重算重跑 β3);规格 canonical 见 `R1f_DECISIONS.md` §6 / §8。**不改主规格**:R-1c 主变量仍为 entity_id 级 `log1p_target_salience`(已 locked)。

### 7.3 R-1 系列 robust 风格 = Framework D(Distinct)

R-1c L1 mention + target only 比 R-1b L2 subject + tradable + target × super_type **尾部更 acute**(mega vs 普通的 log1p 差距 ~4 vs ~1.5-2),distribution robustness 在 R-1c 是 paper transparency baseline,故 R-1c 走 Framework D —— 1 个 pre-commit tail-leverage appendix(R-1b 仍维持其 0 pre-commit + 1 conditional 风格)。Cross-corpus 外部信号(若团队后续愿意建)留 paper §future work 段。

---

## 8. Downstream session anchors

### 8.1 R-1d(Template Rigidity)—— **不受 R-1c 影响**

Template Rigidity 是 case-level 纯文本特征,与 R-1c 在 L1↔L3 容器边界与 R-4a 框架级 8 条上并行,**无直接耦合**。R-1c 不预约束 R-1d 任何选择。

### 8.2 R-1e(因子最终选择)

R-1c **不预承诺** Salience 进 primary。R-1e 据 pilot 数据决定。Pilot 后给 R-1e 的输入:
- raw `target_salience_count`
- `log1p_target_salience` 主变量
- non-zero rate / zero rate
- distribution(pilot 80 pre + 700 post 上)
- top-target concentration(top 10 targets' share of sampled rows)
- correlation / VIF vs R-1b `log1p_recurrence_count`(discriminant 结果)
- tail-leverage appendix β3(winsorize / percentile)vs primary β3
- **若 discriminant 触发**,R-1c slot 可能降级 → R-1e 决定降级到 supporting / exploratory / 不在 confirmatory family

### 8.3 R-2(扰动)/ R-3(负对照)—— **不受 R-1c 影响**

R-2 扰动 inventory + perturbation-specific eligibility 与 R-1c 正交(R-2 仍卡 R-6 C_FO 机制)。R-3 BL2 走 TOST/SESOI=0.15、同-cutoff 证伪对走 early-warning ratio(R-4a 锁),与 R-1c 无耦合。

### 8.4 R-4b(pilot 后具体统计)—— 追加 R-1b retrospective tail-leverage

**R-4b implementation choice**:pilot 后对 R-1b 也做 retrospective tail-leverage check,**与 R-1c 同 winsorize / percentile 形式**,维持 paper §robustness 段一致性。归 R-4b implementation 范围(R-1b §7.1 的 conditional appendix 维持原样)。

**预评估**:R-1b 尾部 mild(super_type 折叠天然缓解,mega vs 普通 log1p 差距 ~1.5-2);retrospective check 大概率稳健,不会触发 caveat reading。

### 8.5 R-5(Sampling)—— sanity-check note

R-1c 不替 R-5 决定 sampling distribution。R-5 sanity-check input:

1. **R-1c metric 与 random sampling 不独立**:高 prominence 实体在 L1 行多 → random sample 偏向高 Salience case → 低 Salience under-represented(Kong §2.2-style Salience-driven survivorship)
2. **Pool G stratified by R-1c `log1p_target_salience`**:若 R-5 启用 Pool G,**用 R-1c metric 分层**(而非 R-1b recurrence)。R-5 全权决定是否启用 Pool G
3. **Pool H entity-balanced cap**:反向平衡工具;R-5 全权
4. **Pilot 上建议同时跑 random + Pool G 两种 sample** 算 discriminant check 与 effect size;R-1e 看在两种 sample 下 effect size 的稳健性。**这是建议,不是 mandate**
5. **L1 mention + no tradable filter 在 metric 层面已 collateral 缓解 Kong §2.2 anti-survivorship 警告**(IPO 前 / 退市 / 停牌段 mention 进 count);但不替代 R-5 sampling 层面工作

---

## 9. B-2 schema requirements

`factor_provenance.run_inputs.per_task.target_salience` 必须包含(字段命名 / 风格 / 与其它 R-X session 输出整合留 B-2 整体 session):

- `factor_name = target_salience`
- `framing_claim = corpus_exposure_intensity_cls_proxy`
- `source_layer = L1_mention`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L1_row`
- `reference_rows_filter`: none(no `is_subject`, no `tradable_at_event`, no `salience` filter)
- `family_key = [target_entity_id]`
- `event_collapse = all_supertypes_merged`
- `reference_window`: `start = cls_corpus_first_published_at`, `end = min_fleet_model_cutoff`, `interval = half_open`(与 R-1b §6.1 同源)
- `focal_article_policy = no_exclusion`
- `dedup_policy = inter_article_no_dedup + intra_article_one_row_per_article`
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `denominator = none`
- `tradable_filter = false`
- `requires_pool_d_or_l1_tradability_extension = false`
- `topic_classify_required_for_main = false`
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e_factor_selection_if_triggered`
- `robustness_precommit_tail_leverage = true`
- `robustness_specific_form = TBD_b2_or_r4b_pre_pilot`(winsorize vs percentile)

### Provenance hashes(R-1c 计算必须可追溯)

- S0 source snapshot hash
- entity alias table hash
- disambiguation rule hash
- layer / view definition hash
- fleet cutoff manifest hash
- sampling manifest hash(when factor values tied to a sampled frame)

注:R-1c main metric **不需要** topic-classifier prompt/model/cache hash(target only,不依赖 super_type)。

### A/B count delta 必报(类比 R-1b §6.3)

- `n_target_L1_mentions_total`(L1 mention 总数,target = case.target_entity_id,窗口内)
- `n_target_L1_mentions_if_tradable_filtered`(同上,加 tradable filter,**仅诊断用**,不进 metric)
- `share_nontradable_in_target_L1_mentions`(尾部诊断)

预期 share 大多数 case 较低(因 case 主体必 tradable,target 大部分时段也 tradable),但 IPO 前 / 停牌 / 退市段会高;这是 R-1c L1 mention vs R-1b L2 subject + tradable 拉开的物理来源。

---

## 10. Standing discriminant input(给 WS0.5 §3.3.3 接口的输入说明)

R-1c 给 WS0.5 discriminant check 框架(§3.3.3 / §5.4 / §5.5,WS0.5 已锁)的输入:
- `log1p_target_salience` 在 `target_entity_id` 维度、L1 mention rows(no tradable,no subject filter)上算
- R-1c 自己做的 discriminant check 输入 = R-1b §4 main variable formula(tradable-filtered)
- 触发阈值与 fallback 行为见 §6(Option C:无 metric fallback,R-1e 降级)

R-1c 不新增此 routine,仅提供输入接口。

---

## 11. Paper-write / 下游决定的开放项

- Paper §4.1 措辞风格(Codex conservative vs Claude bridge)— paper-write 阶段决定
- Tail-leverage robustness 具体形式(winsorize vs percentile)— B-2 / R-4b 在 pilot analysis 前固定
- R-4b 对 R-1b 追加 retrospective tail-leverage(推荐,具体由 R-4b session 落定)
- Cross-corpus stretch goal(Baidu / 维基 / 其它金融媒体)— 论文 §future work 段提及,不进 R-1c robustness slot
