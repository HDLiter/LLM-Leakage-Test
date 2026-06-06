# R-1x 标的广度(Target Breadth,F_breadth)— 最终决策

**状态**: 锁定 2026-06-05(定义 + 操作化 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若与 **F_len / F_density 共线**(VIF ≥ 10 或 |r| ≥ 0.90),或在二者之外
**带不出独立信号** → **降级为 exploratory / 控制变量**,不重开 R-1x 定义。

---

## 1. 候选测什么

一条新闻**同时点名多少个不同的可交易标的**:单标的专稿(广度 = 1)vs 板块综述 / 资金流向
汇总(广度 = N)。记忆故事 = **信号稀释**:被埋在"几十只票综述"里的焦点标的,是否比它作为
独家专稿主角时更不容易被记住——**现有因子都没覆盖"同篇内有多少 co-target 抢注意力"这条机制**。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(文本 / 语料固有;把所有模型拿走,属性还在) |
| 粒度 | **article 级**(同一 article_id → 同一广度值,该文所有 target 行共享) |
| 泄露机制链环节 | **① 曝光量 / ③ 可记忆性**(信号稀释 / 注意力竞争) |

## 2. 操作化

```
breadth[article] = COUNT(DISTINCT target_entity_id
                         WHERE article_id = a AND tradable_at_event)   # 即 L2 同 article 去重标的行数
F_breadth[case]  = log1p( breadth[case.article_id] )
```

| 字段 | 值 |
|---|---|
| 来源层 | **L2**(带 `tradable_at_event` 过滤的 文章×标的 行);tradable 定义沿用 L2,不另立口径 |
| 计数口径 | 数**全部** distinct tradable 标的(**含焦点标的自身**,故 breadth ≥ 1) |
| 变换 | **log1p**(分布右偏,综述可达几十只;沿用 R-1b/R-1c 零值保留口径) |
| 窗口 | **无** —— 纯篇内计数,不需语料 lookup 窗口 |
| 成本 | 极低(L2 按 article_id `GROUP BY` 数行) |

## 3. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用) |
| 比较对象 | **vs F_len(R-1i)/ vs F_density(R-1g)** 为主;附带 vs F_topic / F_industry |
| 触发后行动 | **R-1e 决定降级**(无 metric 级 fallback,同 R-1c Option C) |

**概念区分**:F_salience(R-1c)= 焦点标的在**整个语料**的累计曝光(跨语料、focal);F_breadth =
**本篇内** co-target 数(篇内、structural)→ 两根正交轴,分得开。真风险在 **F_len**(长文自然
提更多标的)与 **F_density**(含"实体密度"一项):概念上 F_breadth 数的是"**去重可交易标的
个数**"、不是 mention 密度或总信息量,但经验相关待 pilot 查(故绑文档头 pilot 闸门)。

## 4. 不在 R-1x 范围内

- R-1e 因子最终选择 + pilot 共线判定(R-1x 闭 + pilot 后)。
- **多标的文章产生多 case 行**带来的 over-representation / 加权 = **R-5 采样 / R-4b 统计**范围
  (F_breadth 只定因子值,不管 case 行怎么进统计)。
- F_breadth × F_salience 交互(稀释效应是否随焦点标的显著度变)= R-1e / pilot 探索,不在因子定义。
