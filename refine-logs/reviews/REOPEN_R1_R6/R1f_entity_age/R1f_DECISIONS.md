# R-1f 实体曝光时长(Entity Age)— 最终决策

**状态**: 锁定 2026-06-03(定义 + 候选池准入)
**结局**: **进入 R-1e 候选池**

---

## 1. 定义

Entity Age 量的是:**一个标的实体的某个名称形式在公开语料中活跃了多长时间
(到模型训练截止日为止)。**

"名称形式"指文章中实际使用的证券简称(如"海虹控股"或"ST海虹")——
不是股票代码的全部存续时间。原因:模型在 token 层面的记忆是绑定到具体的
token 序列的,"ST海虹"和"海虹控股"在 tokenizer 里是不同序列,一个的训练
样本不直接强化模型对另一个的 token 级熟悉度。不同模型有不同 tokenizer
(fleet 16 个模型至少 4-5 种 tokenizer),不应假设模型能跨名称变体传递记忆。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(名称活跃时段是语料/交易所属性,把所有模型拿走还在) |
| 粒度 | **case × model**(同一实体名称对不同模型有不同的 age,因各模型 cutoff 不同) |
| 泄露机制链环节 | **② 曝光时长** |
| 量的维度 | 时间跨度(duration),区别于 F_salience/F_recur 的频次(intensity) |

F_age 是第二个 case×model 因子(与 F_cutoff 并列)。两者**不共线**:
F_cutoff 的 case 级变异来自 **published_at**(文章发布日),F_age 的 case 级
变异来自**名称活跃时段**(哪些年份这个名字在用)。同一语料里两者无确定性关系。
model_cutoff 同时出现在两者公式中,但只造成 model 维度上的共变,被模型随机
效应吸收。

---

## 2. 数据来源

### 2.1 名称-时段表

| 字段 | 值 |
|---|---|
| 主数据源 | **Tushare Pro `namechange` API**(全 A 股,含 ts_code / name / start_date / end_date / change_reason) |
| Fallback(深交所) | akshare `stock_info_sz_change_name("简称变更")` — 7,397 条,精确到天,仅深交所 |
| Fallback(上交所) | akshare `stock_zh_a_disclosure_report_cninfo(keyword="证券简称变更")` — 搜"实施公告"取生效日,限速 ~1.5s/请求 |
| IPO 日期 | akshare `stock_info_a_code_name` 或同类接口 |
| Cutoff | `config/fleet/r5a_fleet.yaml` 中各模型的 cutoff manifest |

**为什么用 Tushare 而不只用 akshare**:Tushare `namechange` 是唯一一个
全 A 股(沪深都有)且带精确日期 + change_reason 的结构化数据源。
akshare 深交所 API 只覆盖深市;上交所无等价 API,需从 CNINFO 公告解析。
akshare 和 CNINFO 作为交叉验证 / fallback。

**为什么不用 CLS 语料首现日**:CLS 语料 ~2020-01 起步,绝大多数 A 股
上市公司在此之前已上市,语料首现日集中在 2020-01 附近,几乎无变异。

### 2.2 数据源调查结果(2026-06-03,三路独立验证)

| 数据源 | 覆盖 | 有日期? | 状态 |
|---|---|---|---|
| Tushare `namechange` | 全 A 股 | 有(start/end/ann_date) | **主源** |
| akshare `stock_info_sz_change_name` | 仅深交所 | 有 | Fallback + 交叉验证 |
| akshare CNINFO 公告搜索 | 全 A 股 | 有(公告日) | Fallback(需解析公告标题) |
| akshare `stock_info_change_name`(Sina) | 全 A 股 | **无**(只有名称序列) | 辅助识别哪些股票改过名 |
| 东方财富 datacenter | 全 A 股 | **无**(只有名称链) | 辅助 |
| SSE 官网 API | 上交所 | CHANGE_DATE 全 "-" | **死路** |

### 2.3 core_name 标注

名称-时段表中每条记录需要一个 `core_name` 字段,表示"这个名称指向的
可识别实体核心身份"。例如:

| name | core_name | 理由 |
|---|---|---|
| 海虹控股 | 海虹 | 主名称 |
| ST海虹 | 海虹 | 监管前缀,核心身份不变 |
| G海虹 | 海虹 | 股改标识,核心身份不变 |
| 琼海虹 | 海虹 | 地理前缀(海南),核心身份不变 |
| 国新健康 | 国新健康 | 实质更名,新核心身份 |
| 琼化纤 | 化纤 | 更早的不同核心身份 |

**标注方式**:机械规则初标(去已知前缀/后缀)+ AI agent 辅助 +
**用户全量审核**(~5000 只股票,可快速过完)。

core_name 是一次性标注产物,不是运行时算法。前缀剥离规则、监管标识
词典等都是标注过程的辅助工具,不需要固化在因子定义中——最终权威是
用户审核后的 core_name 表。

---

## 3. 操作化

### 3.1 名称-时段表 schema

```
stock_code  | name        | core_name  | start_date | end_date
000503      | 琼化纤      | 化纤       | 1994-11-01 | 1995-05-22
000503      | 琼海虹      | 海虹       | 1995-05-22 | 1997-05-05
000503      | 海虹控股    | 海虹       | 1997-05-05 | 1998-06-15
000503      | ST海虹      | 海虹       | 1998-06-15 | 2000-03-21
000503      | 海虹控股    | 海虹       | 2000-03-21 | 2006-05-16
000503      | G海虹       | 海虹       | 2006-05-16 | 2006-10-09
000503      | 海虹控股    | 海虹       | 2006-10-09 | 2018-05-25
000503      | 国新健康    | 国新健康   | 2018-05-25 | NULL
```

来源:Tushare `namechange`。`core_name` 由机械初标 + AI 辅助 + 用户全量审核
产出(§2.3)。

### 3.2 三级聚合

F_age 在三个聚合级别上计算,主规格 + 两个 robustness:

| 级别 | 聚合规则 | 用途 |
|---|---|---|
| **② 字面名级** | 同一 stock_code + 完全相同的 `name` 字符串 → 累加所有活跃时段 | **主规格** |
| ① Entity 级 | 同一 stock_code 的所有时段(= model_cutoff − ipo_date) | Robustness |
| ③ Core_name 级 | 同一 stock_code + 同一 core_name(人工审核标注) | Robustness |

**级别③的规则**:同一 stock_code 内,`core_name` 相同的名称归为一组。
`core_name` 来自 §2.3 的人工审核标注表,不是运行时算法。
不需要相邻约束(模型训练时不同时期的语料是打乱的,时间先后不影响
token 级记忆)。

**000503 示例**:海虹控股/ST海虹/G海虹/琼海虹 的 core_name 都是"海虹"
→ 同组;国新健康的 core_name 是"国新健康" → 不同组;琼化纤的 core_name
是"化纤" → 又一个不同组。

### 3.3 主变量公式(级别② 字面名级)

```text
# 名称-时段表中,同一 stock_code + 同一 name 字符串的所有行
intervals[case, model] = [
    [row.start_date, min(row.end_date or +inf, model_cutoff)]
    for row in namechange_table
    where row.stock_code == case.stock_code
      and row.name == case.surface_name
      and row.start_date < model_cutoff
]

merged = merge_overlapping_intervals(intervals)
age_days[case, model] = sum((end - start).days for [start, end] in merged)
entity_age_years[case, model] = age_days / 365.25
log1p_entity_age[case, model] = log1p(entity_age_years)
```

**主变量**:`log1p_entity_age[case, model]`。

**case.surface_name**:测试文章中实体识别管线输出的**字面名称形式**
(如"海虹控股"或"ST海虹")。这要求 ER 管线保留原文 surface form(见 §8)。

**为什么 log1p**:A 股名称活跃时段跨度大(从几个月到 30+ 年),边际递减。
与 R-1b/R-1c 的 log1p 变换保持一致。

**零值策略**:如果 surface_name 在 model_cutoff 之前没有活跃时段,
age = 0,log1p(0) = 0,合法保留,不当 missing 剔除。

### 3.4 000503 三级聚合示例(model_cutoff = 2024-06-30)

| 级别 | 文章写"海虹控股" | 文章写"ST海虹" | 文章写"国新健康" |
|---|---|---|---|
| ① Entity 级 | ~30 年(1994-2024) | ~30 年 | ~30 年 |
| **② 字面名级** | ~19 年(三段累加) | ~1.7 年 | ~6 年 |
| ③ Core_name 级 | ~23 年(core=海虹的全段,含琼海虹) | ~23 年 | ~6 年 |

---

## 4. 区分度检查(discriminant check)

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b/R-1c/R-1d) |
| 比较对象 | vs F_cutoff, vs R-1b `log1p_recurrence_count`, vs R-1c `log1p_target_salience`, vs R-1d `template_rigidity` |
| 预期结果 | 通过(概念论证见下;正式检查在 pilot) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback;同 R-1c/R-1d) |

**概念区分度论证**:

- **vs F_cutoff**:两者都是 case×model,但 case 级变异来源不同。F_cutoff
  取决于 published_at(文章何时发布),F_age 取决于名称活跃时段。
  **分歧案例**:同一天发布的两篇文章,一篇关于 1997 年起就叫"海虹控股"
  的公司(age ~19 年),一篇关于 2022 年才改名的"赛力斯"(age ~2 年)
  ——F_cutoff 相同,F_age 差 17 年。
- **vs F_salience**:salience = 被提了**多少次**(频次强度),age = 这个名字
  活跃了**多久**(时间跨度)。有正相关(活跃越久通常被提越多),但可分离。
  **分歧案例**:2023 年改名的热门公司(age 短、salience 高——改名后密集报道)
  vs 2005 年就有的冷门名字(age 长、salience 低——偶尔被提)。
- **vs F_recur**:recurrence 是(标的×事件家族)出现次数,与名称活跃时长正交。
- **vs F_template**:template 是文本结构属性(article 级),age 是名称时段
  属性,无概念重叠。

**预期共线性等级**:vs F_salience 中度(pilot VIF 检查);vs 其余低。

---

## 5. 稳健性

### 5.1 聚合级别敏感性 — entity 级 + 泛化同名级

| 字段 | 值 |
|---|---|
| 替代变量 (a) | **Entity 级 age**(同一 stock_code 全部时段 = model_cutoff − ipo_date) |
| 替代变量 (b) | **Core_name 级 age**(同一 stock_code + 同一 core_name 的时段 union) |
| 测的是 | 主规格假设"token 级记忆绑定到字面名称";entity 级假设"模型关联同一 stock code 的所有名称";core_name 级介于两者之间(共享核心身份的名称变体)。如果三者一致,结论对名称聚合粒度稳健 |
| Pre-commit vs conditional | **Pre-commit** |
| Slot | **Appendix** |
| 成本 | 近零(同一张名称-时段表换 group-by) |

### 5.2 变换敏感性 — raw + percentile rank

| 字段 | 值 |
|---|---|
| 替代变量 (a) | `entity_age_years[case, model]`(不变换,raw 年数) |
| 替代变量 (b) | `percentile_rank(entity_age_years[case, model])`(经验百分位) |
| Pre-commit vs conditional | **Pre-commit** |
| Slot | **Appendix** |
| 成本 | 近零 |

### 5.3 尾部杠杆 — winsorized log1p

| 字段 | 值 |
|---|---|
| 替代变量 | `log1p(winsorize(entity_age_years, 5th, 95th))` |
| Pre-commit vs conditional | **Pre-commit** |
| Slot | **Appendix** |
| 成本 | 近零 |

---

## 6. 对已有实体级因子的溢出影响

F_age 的"token 级记忆绑定到字面名称"论点同样适用于 F_salience 和 F_recur:
"ST海虹"的 mention 在 token 层不直接强化"海虹控股"的频率信号。

**建议 F_salience(R-1c)和 F_recur(R-1b)各增加一条 pre-commit appendix
robustness**:按三级聚合(entity 级 / 字面名级 / 泛化同名级)分别重算
salience / recurrence,重跑 β,看结论变不变。

- 主规格不改(entity_id 级,已 locked,简单)
- robustness 的前提:ER 管线记录了 surface_name(见 §8)
- 一旦名称-时段表建好,三级聚合都是 low-cost 的 group-by 操作
- 具体落地:R-1e 选因子时统一处理,不改 R-1b/R-1c 已锁的 DECISIONS

---

## 7. Standing discriminant input(给 WS0.5 接口)

R-1f 给 WS0.5 discriminant check 框架(§3.3.3 / §5.4 / §5.5)的输入:

- `log1p_entity_age[case, model]`(主规格:字面名级),以 (case, model) 为行
- R-1e session 做 VIF / correlation 时的比较口径:
  - vs F_cutoff(tanh 映射,R1a_DECISIONS.md §1)
  - vs R-1b `log1p_recurrence_count`(R1b_DECISIONS.md §4)
  - vs R-1c `log1p_target_salience`(R1c_DECISIONS.md §5)
  - vs R-1d `template_rigidity`(R1d_DECISIONS.md §3)
- 触发阈值:VIF ≥ 10 或 |r| ≥ 0.90
- Fallback:无 metric 级 fallback;触发时 R-1e 决定降级
- **注**:F_age 是 case×model 级;F_recur/F_salience 是 case 级;
  F_template 是 article 级。VIF/correlation 计算时,统一在 (case, model)
  行粒度上对齐(case-only 因子对同一 case 的所有 model 行值相同)

---

## 8. 对 entity recognition 管线的要求

F_age 主规格(字面名级)要求上游 ER 管线对每个实体 mention 输出三个字段:

| 字段 | 说明 |
|---|---|
| `surface_name` | 文章原文中实际出现的名称(如"ST海虹"、"海虹控股") |
| `canonical_name` | 当前标准证券简称(如"国新健康") |
| `stock_code` | 股票代码(如 000503) |

F_age 用 `surface_name` 在名称-时段表中查找字面名级活跃时段;
用 `stock_code` 查找 entity 级和泛化同名级活跃时段。

标识前缀解析(§2.3 的标识词典)、core_name 提取、匹配置信度等是
名称-时段表构建和 ER 管线的内部实现,不在 F_age 的接口要求内。

如果 ER 只输出 stock_code 而不保留 surface_name,字面名级(主规格)
和泛化同名级(robustness)均无法计算,只能退化到 entity 级。

---

## 9. B-2 schema requirements

R-1f 需要 B-2 schema 提供:
- **名称-时段表**(stock_code / name / core_name / start_date / end_date),来源 Tushare `namechange` + §2.3 core_name 审核
- `model_cutoff` 字段(已在 fleet config 中)
- ER 管线的 `surface_name` 字段(§8)

---

## 10. 不在 R-1f 范围内

- **CLS 语料首现日作为主规格**:变异不足,降为不做
- **min fleet cutoff 替代 per-model cutoff**:只是丢信息,不构成稳健性检查
- **相邻时间线建边 / Union-Find / 前缀匹配 / 子串匹配**:均被更简单的
  人工审核 core_name 方案取代——5000 只股票全量审核比设计完美算法更可靠,
  且不依赖对 tokenizer 行为的假设
- **change_reason 作为分类器**:Tushare 字段枚举不稳定;core_name 标注
  由人工审核兜底,不依赖 change_reason

