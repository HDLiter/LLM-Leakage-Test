# R-2 扰动层(L2)设计 — Kickoff

> **session 类型**:操作化层结构化重开,第 2 层(扰动 / Perturbation),与 R-1(因子层 / L1)对仗。
> **协议**:clean-room-first + lit-grounded;产出干净 `R2_DECISIONS.md`(< 200 行,canonical)
> + audit-trail(whiteboard 等,事后归 `archive/`)。
> **解锁**:R-6 已 close(2026-06-06)→ R-2 可动;设计层,不依赖 pilot 数据。
> **canonical 上游**:四层框架 `R5A_STEP2/MEASUREMENT_FRAMEWORK.md`、候选池索引
> `R4_methodology_audit/four_layer_candidate_pools.md` §0/§2/§4.2、`R6_pred_target_cfo/R6_DECISIONS.md`、
> 构念效度 `R4_methodology_audit/R4_construct_validity_decisions.md` + `P0_DECISIONS.md`。

---

## 0. 为什么放宽命名:这是"扰动设计",不是"反事实扰动家族设计"

worktable 旧名「反事实扰动家族设计」太窄——它只盯 C_FO 的后继。但 R-1 是把**整个因子层**
重开(候选池 R-1a…R-1x,逐个定去留 + R-1e 最终选),R-2 该**对仗**:把**整个扰动层(L2)**
重开。反事实扰动只是其中一个待设计的家族,不是全部。

> **本 session 范围** = 现有扰动的去留 / tier 确认 **+** 新扰动的发掘 **+** 哪些进 primary /
> confirmatory **+** 反事实家族(R-6 遗留)的具体设计。

## 1. 轴(四层框架 §0,不可动)

- **扰动(C_)= 主动改文本的一个维度**;作用方式 = 配对相减 `P_predict(原) − P_predict(变体)`
  (对比:因子不改文本,作用方式是分层 / 交互)。
- **主量 = resistance 抗扰动**(P0 / R-4 D3):每个扰动配一个 resistance 指标,测"模型死抱缓存
  知识、无视眼前编辑"的程度。
- **三条贯穿判据**:
  1. **抗扰动族不预测 cutoff 行为** —— 干净的 cutoff 锚只在熟悉度通道(E_PCSG / E_CTS);扰动
     通道测 resistance,靠 **pre − post 切片**才照出 case 记忆(post-cutoff 仍抵抗 = 一般先验)。
  2. **confirmatory 数 = power-bounded,不预设魔数**;候选池可宽,pilot 选 / 降级,R-1e + R-2 共定族。
  3. **质量门控**:规则生成 → 四维人工审(自然 CLS 文风 / 只动目标局部 / 编辑外经济一致 / 不引入
     新线索)→ ≥85% 通过 → 否则撤该扰动 confirmatory 身份(算子 / 指标定义存活)。

## 2. Task 1 — Brainstorm(本 session 第一步,clean-room)

### 2a. 盘点已有扰动(现状,来自 four_layer §2 / §4.2)

| 扰动 | 改什么 | 测哪种记忆 | 配对 estimand | 现状 |
|---|---|---|---|---|
| **C_SR** 语义反转 | 财经方向反转(利好↔利空),事件壳不动 | 死抱缓存方向结论 | E_SR | 主力,**主记忆 backbone 候选** |
| **C_NoOp** 无关插入 | 插一句规则生成的无关但合理 CLS 短句 | 脆弱模板匹配(**兼安慰剂控制**) | E_NoOp | 候选,质量门控 |
| **C_anon** 实体匿名 | 目标 / 非目标实体换保类型占位符(L0→L4 梯度) | 身份记忆 vs 事件内容记忆 | E_EAD_t/nt | exploratory |
| **C_temporal** 时间退化 | 渐进移除时间锚(2–3 剂量级) | 记忆是否依赖时间锚当查找键 | 派生 F_temporal;E_ADG | 候选 |
| **C_ADG** as-of 日期 | 改 prompt「截至某日」,不改正文 | prompt 级时间门控 | E_ADG | reserve |
| ~~C_FO 假结局~~ | — | 结局 / 结果记忆 | ~~E_FO~~ | **已删 R-6**;目标转本 session(§3) |

### 2b. 发掘更多可用扰动(lit-grounded,不预设结论)

**方法**:沿两个轴找 gap —— 泄露机制链 6 环节(①曝光量 ②曝光时长 ③可记忆性 ④方向先验捷径
⑤可推断性 ⑥时间定位)× 记忆通道,问**哪些记忆通道现在没被任何扰动探到**,再去文献找对应的
可控文本变换。每个 candidate 必须能答:
- 改文本**哪一个**维度(单维、可规则生成、可人工审 ≥85%)?
- 测哪种记忆,且**与已有扰动不重合**?(C_FO 被删正因与 C_SR 实操重合——这是本 session 的红线教训。)
- 配对哪个 resistance 指标、读哪个算子衍生变量(离散方向 PC / 白盒置信度 CI / 分布 IDS)?
- **CLS 电报上适用面够不够**?(C_FO 死因之一:很多电报同期报道、无可改的"结局"段。)
- 派生哪个二级因子(若有)?

**起手用的记忆通道 gap(非清单,session 内自推 + 文献接地)**:数字 / 量级记忆(精确财务数字)、
实体属性记忆(板块 / 代码 / 高管)、逐字 / 表面形式记忆(语义保持改写 → 分辨逐字 vs 语义记忆)、
因果链记忆 vs 推理、跨实体替换(换成另一**真实**标的 vs 匿名占位)。

## 3. 必接的 R-6 遗留:反事实扰动家族

R-6 删 C_FO 时,把「这条 case 的**结果记忆**」目标明确交给本 session(`R6_DECISIONS.md`):由
**反事实扰动 ×「cutoff 前 vs 后」× 标的显著度切片**承接(post-cutoff 仍抵抗 = 一般先验;只
pre-cutoff 抵抗 = case 记忆)。

> **R-2 必须拍**:反事实家族**留哪些扰动、主 backbone 选谁** —— C_SR 是否已够;要不要专门的
> 反事实结局 / 数字扰动;若要,它与 C_SR 怎么**分工不重合**(避免重蹈 C_FO)。代码侧已建的
> `C_CO` / `E_OR` 槽(tier-r2-0 实现)去留**随本决策定**。

## 4. 方法 + 交付

- **clean-room-first**:先白板独立分析(从"要测哪些记忆通道"自推该有哪些扰动),再对照既往
  reviewer 意见 / 文献,防统计术语镇压。
- **lit-grounded**:每个进池扰动列**源论文**(论文 → 做了什么文本变换 → 引用数 → 撑哪个决定);
  实施前 lead 亲自过目源论文。
- **minimal-design**:每个扰动须证明它探一个别人探不到的记忆通道、且操作不与已有重合,否则不进。
- **交付**:干净 `R2_DECISIONS.md`(< 200 行)= 每个扰动去留 / tier + 反事实家族 backbone + 各自
  源论文 + 准入闸门;同步更新 `four_layer_candidate_pools.md` §2 / §4.2 索引;audit-trail 归 `archive/`。

## 5. 依赖 / 下游 / 边界

- **上游已清**:R-6 closed → 可动;设计层不卡 pilot。
- **下游**:R-1e(因子最终选时也需知扰动集)、WS2(P_predict 管线载扰动)、WS3(扰动生成 + 人工审)、
  R-5(反直觉 / 退化案例过滤需反事实)、代码 `C_CO` / `E_OR` 去留。
- **不重做**:因子层(R-1 已定)、算子层 L3、指标"读法"(PC / CI / IDS = 算子衍生变量 × 比较,
  见 four_layer §4.3,非扰动设计);但每个扰动**须写明**配对 estimand。
