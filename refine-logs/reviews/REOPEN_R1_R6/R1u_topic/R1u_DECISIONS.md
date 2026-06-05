# R-1u 事件类型 / 主题(Topic,F_topic)— 最终决策

**状态**: 锁定 2026-06-04(定义 + 候选池准入 + 分辨率)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若**类间记忆度无明显差异**,或与 F_recur **共线**(VIF ≥ 10 或
\|r\| ≥ 0.90)→ **降级为 exploratory**(只报告类别分解、不当主因子),不重开 R-1u 定义。

**审计轨迹**: 本候选池快速轮无独立白板;三步快速判 + 设计讨论内嵌于本文件。

---

## 1. 定义

事件类型量的是:**这条新闻属于哪一类事件**(财报 / 并购重组 / 监管处罚 / 高管变动 /
分红 …)—— 一个 **sign-free**(只问"是哪类",**不带方向、不带正负号**)的语义类别。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(语义类别;把所有模型拿走,"这是一条财报新闻"还成立) |
| 粒度 | **article / event-class 级**(同一 article_id → 同一事件类) |
| 泄露机制链环节 | **③ 可记忆性**(+ ⑤ 可推断性):某些事件类型本身是否更易被记 / 更易不靠记忆推出 |

**带方向那版分出**:"某事件类 → 利好/利空"(降息利多)= **F_structdir(R-1s)**,
带正负号、绑 Type A 良性闸门,不在本因子。这里进池的是 sign-free 的"是哪类"。

---

## 2. 区别于 F_recur(非共线论证)

F_recur(R-1b)的家族键 = **(标的实体 × 事件超类)的复现计数**,与 F_topic 不共线:

- **F_recur** 量的是"**重复了几次**"(同一标的、同一事件类历史上复现多少次);
- **F_topic** 量的是"**是哪类**"(事件类型的主效应),不含次数。
- 两条 recur 次数相同、但一条财报一条并购的 case,**recur 分不开,topic 能**。
- **已单拎出 entity 那条腿**(F_salience 是实体层曝光);topic 是**对称的另一条腿**,
  无理由留 entity、压 topic。
- recur 在**每个事件超类内部仍有方差**(不同标的复现数不同)→ topic 的超类 dummy 与
  recur 计数**可共存**(主效应 + 格内计数),概念上不共线。

**结论**:topic 主效应与 recur 复现计数**互补,不共线**;实操共线性 pilot 用 VIF/相关查。

---

## 3. 因子值 + 分辨率

```text
topic_class[case] = 事件超类(event_super_type,Scheme A 5 超类)
```

| 字段 | 值 |
|---|---|
| 数据 | 复用 pipeline 已有 **topic 分类器**(V3 13 类 → 5 超类映射;F_recur 已在用)→ **零新增标注** |
| 主分辨率 | **5 超类**(对齐 F_recur 粒度;类少 → 每类样本厚、power 好、叙事聚焦) |
| 稳健性分辨率 | **V3 13 类**(更细的事件类型;主结论是否依赖粗/细口径) |
| 缺失 | 每条新闻经 entity-first pipeline 分类 → 无缺失 |

---

## 4. 怎么进分析(intent;统计规格 = R-4b)

> R1u 只声明分析**意图**;"怎么算 / 怎么检验 / 控制哪些变量"留 R-4b。

1. **无序分类**(不是单调斜率):confirmatory 入口 = **总检验"记忆度在事件类之间有没有
   差异"**(一个 omnibus);**哪一类冒尖**当 exploratory 细分。结构同 F_datebin(R-1h)。
2. 分类因子的 confirmatory 主张读作"**记忆度因事件类型而异**",非"随因子单调升"。
3. 跨模型聚合是否独立地在同一类更牢 → "事件类型内在记忆度"的强证据。

---

## 5. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b/c/d/f/g/h/i) |
| 比较对象 | vs F_recur(§2 已论非共线)、vs F_template、vs F_salience / F_mktmag(信号通道) |
| 预期结果 | 通过(topic 主效应独立于复现计数);正式检查在 pilot |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback) |

**概念区分度**:若某类事件更好记,信号可能部分经 **F_template**(套路度)/ **F_salience**
(报道量)/ **F_mktmag**(波动)流走;topic 捕捉的是"扣掉这些后,事件类型本身是否仍
调节记忆"。**F_symmetry(R-1j)** 的"按方向散度并组"是 topic 内部的探索性子分析,不另立。

---

## 6. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无明显类间差或与 recur 共线 → 降 exploratory。
- **R-4b**:无序分类的总检验规格、跨模型聚合、控制变量集、与 recur 的联合建模。
- **R-1e**:据 pilot 类间差异 + 与 recur/salience 区分度,决定进 primary 还是降级。
- **F_structdir(R-1s)**:带方向的事件类先验,绑 Type A 闸门,独立 session,不在本因子。

---

## 7. B-2 schema requirements

`factor_provenance.run_inputs.per_task.topic`(字段命名 / 风格留 B-2 整体 session):

- `factor_name = topic`
- `framing_claim = event_type_intrinsic_memorability`(sign-free)
- `source = topic_classifier`(V3 13-class → Scheme_A_5_supertypes 映射;复用 F_recur 同一分类管线)
- `row_unit = article_id`
- `primary_resolution = event_super_type`(5 类)
- `robustness_resolution = v3_13class`
- `encoding = unordered_categorical`(omnibus 入口;per-class 细分 exploratory;具体建模留 R-4b)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`(主比较对象 = F_recur)
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_exploratory_if_no_class_difference_or_collinear_with_recur`

### Provenance hashes
- topic-classifier prompt / model / cache hash · event-scheme 映射 hash(V3 13→5)
  · sampling manifest hash(when factor values tied to a sampled frame)

---

## 8. 不在 R-1u 范围内

- 带方向的事件类先验(F_structdir,R-1s,Type A 闸门)
- 无序分类的具体统计方法(总检验、跨模型聚合、联合建模)= R-4b
- R-1e 因子最终选择
