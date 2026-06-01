# R-4 构念效度 session — 定调(2026-05-30/31)

> **status**:本轮**已定调**的决策(canonical for downstream)。OPEN 议程(P0–P7)仍见
> `R4_next_construct_validity_agenda.md`;四池候选见 `four_layer_candidate_pools.md`;
> 偏见 catalog + arxiv 查新见 `bias_catalog.md` / `arxiv_scan_20260531.md`。
> 这份只记**拍了板的**;leans / 待敲不在此。
>
> **缘起**:用户要求从第一性原理 + 构念效度重走实验。走查产出一批硬决策 + 一份四池总表
> + 一次偏见文献调研 + 一次 arxiv 查新。clean-room-first,白话叙述。

---

## 0. 一句话总纲(本轮锚定)

> **测量本体 = 同一算子在「因子变化」(如 cutoff)或「施加扰动」(如 C_SR)前后输出的变化。**
> 主记忆量 = **resistance(抗反事实扰动的行为指纹)**;cutoff = 验证锚,但 null 判据**分层**;
> false-alpha 是动机端要用论证去接的桥,**不是**测量本身能担保的。

---

## 1. 已定调决策

### D1 — 记忆是一族,按 cutoff 行为分两堆
- exact 记忆(文本/事件/case 结局)cutoff 后该归零;**养成的偏见**(实体/因子/共现/乐观/
  基准率…)cutoff 后**不归零**。
- **实体/持续偏见并入"记忆"大构念**(通过不同因子+扰动测),**不当混杂剔除**。
- 文献坐实:偏见 catalog 16 族,机制统一 = "拿语料先验顶替眼前文本"(见 `bias_catalog.md`)。

### D2 — 分层 null(取代"cutoff 后一刀切读零")
- `memory_lift` / resistance / E_PCSG → post-cutoff **≈ 0**;
- `raw_score`(原始预测准确率)→ post-cutoff **≠ 0**(基准率+乐观+地域偏见在);
- 持续偏见 → **≠ 0 且正面去量**。
- 外部佐证:2603.03203 / 2604.13997(两量并存)、2603.21658(抗扰动=记忆有机制根据)、
  TempoMed-Bench 2605.13045(cutoff 渐变非阶跃 → 只能为"记忆差值读 0"辩护,不能为 raw_score)。

> **⚠️ resistance 那一行收紧(P0,2026-06-01)**:本条把 `resistance` 和 `memory_lift`/`E_PCSG` 一起列进『post ≈ 0』,读着像定论。按 P0:**干净的 post-cutoff ≈ 0 锚只落在熟悉度通道(E_PCSG/E_CTS,照确切结局记忆)**;**抗扰动族(resistance)主要照成见型记忆,跨 cutoff 强弱不预测,不给它安 post-cutoff 归零判据**。本行『resistance → ≈ 0』实为『pre−post 抵抗(memory_lift)能照出确切结局记忆』这个**假说**,非已知事实,别当 confirmatory 判据。正本 `P0_DECISIONS.md` §0/§1/§5-P2。

### D3 — resistance 正名;"两范式二选一"降级
- 框架实存主量 = resistance(E_FO/E_SR/E_NoOp 全是 `P_predict(原)−P_predict(扰动)`)。
- "prediction-lift 范式" **不是**现成 estimand,是上游 agent 给"动机(false-alpha)↔测量(行为
  指纹)之间那道缝"起的名。真问题 = "主量=resistance;要不要、怎么架桥到 false-alpha",
  与 proposal §2.2 黄框同一件事。**故不存在"挑哪个范式"。**

### D4 — 会聚效度是效度主论证
- 行为通道(P_predict 抗扰动)× 惊讶度通道(P_logprob)两个不同算子**都过锚、都随曝光升**
  = 强构念效度。**不需要 E_CMMD 当第三条腿。**
  > **⚠️ 第二条腿措辞校正(P0 决策1,2026-06-01)**:本条『都随曝光升』的『曝光』= `F_salience`/`F_recur`
  > 这族 **peer 因子**;把它当效度承重轴与 P0『因子一视同仁、实验前不预派任何单一因子当验证轴』冲突。
  > **第二条腿应读作**:两通道在同一批 case 上**一致指向记忆**、且该一致**不被同一共同混杂(如高频实体)
  > 带动**(= 通道独立性:两条证据来源不同源、非统计独立——会聚仍要它俩一致);『随曝光升』降为正向端剂量响应旁证(独立性待 pilot)。**『都过锚』腿不变**
  > (cutoff = 验证锚,合法)。正本见 `P0_DECISIONS.md` §1。
  >
  > **⚠️ 再收紧:会聚效度不当预设判据(P0,2026-06-01)**:『会聚效度=效度主论证』+『都过锚』整体降级。按 P0:两个信号各测一面(抗扰动族=成见型记忆、熟悉度类=确切结局记忆),互相佐证但**不假设能合成**;**干净 cutoff 锚只在熟悉度通道,抗扰动族不预设 cutoff 行为**(靠扰动设计本身立)。两通道相关/独立 = 实验出结果后的**观察**,非预设判据。正本 `P0_DECISIONS.md` §0/§1。

### D5 — E_CMMD 砍(定调,不再是 lean)
- 招牌属性 "cutoff-monotone" 无文献出处 + 识别弱 + 代码 stub + 唯一卖点被会聚效度接管;
- **2026-05-31 arxiv 查新坐实**:MemGuard-Alpha(arXiv 2603.26797)已公开占先 "CMMD =
  Cross-Model Memorization Disagreement" 名+思路 → 不能再当新贡献。

### D6 — 读数 = 算子衍生变量 × 指标比较(**无第五层**)
- PC / CI / IDS / 采样离散度**不是新层**,是 `E = 比较(算子衍生变量, 原 vs 扰动)`。立成
  "读法层"会重犯四层框架当初要溶解的范畴错误。
- **PC 锁**(离散方向,16 全 fleet,主读数)。
- **CI / IDS / 采样离散度 → estimand 候选,pilot**:
  - CI/IDS 依赖的衍生变量(logprob 置信度/分布)**只白盒有** → 黑盒确认性 **PC-only**;
    混报 16 模型会把白盒vs黑盒缠进泄露信号(构念效度灾难)。
  - 自报置信度**不可靠**(Qwen 上崩、自相矛盾;BaseCal/PRISM 实测)→ CI 只用 logprob、只读相对差。
  - **记忆-过度自信伪迹**:记忆 case 置信度饱和→CI 差被压扁、IDS 被极端概率主导;pilot 须用
    pre/post 分布尖锐度专门拆。
  - IDS 的 pre/post 扰动 KL 文献无人算过 → **首创,pilot 先验证量自身稳定性**。
  - 采样离散度 = 所有算子的元维度(重复 k 次方差),黑盒唯一分布型出路;仅采样型算子(T>0)非退化。

### D7 — 真实收益三种命
- ❌ **当主指标** —— 否决(双重混淆:模型可能根本不会预测真实收益、全靠蒙;单条新闻预测股价
  近乎不可能;且 resistance 主量本不需要真实收益,引入反毁 cutoff 干净性、撞 §4.6)。
- ✅ **当 pilot 对照** —— 接受(零成本拉 A 股行情,和 P_predict 比一比看有无真预测力,sanity check)。
- ✅ **当因子(F_mkt*)** —— 接受为候选(把真实收益从"预测目标"挪到"案例标签":涨的/涨得猛的/
  市值高的新闻是不是更容易被记住)。**与报道语料族正交**(独立生成过程,非共线)。

### D8 — F_temporal 进 L1
- `F_temporal = 新闻时间线索强度`,既是 C_temporal 派生二级因子、也是独立 primary 因子。

### D9 — 撤回的旧表述
- **撤回**:"PC/CI/IDS ≈ C_SR/C_FO/C_NoOp" 等号(混了扰动层 vs 读数层)。正确:Profit Mirage 的
  扰动 ↔ 我们 C_*;其 PC/CI/IDS ↔ 我们 estimand 的"读差值"环节。直觉同源,非一一对应。
- **作废**:主对话此前"松绑 null 判据 / R-4 收下"——那是被 E_FO 命名漂移误导的错表述(见 D2/D3)。

---

## 2. 本轮明确「不拿出来 / 推迟」的

| 项 | 处置 | 谁定 |
|---|---|---|
| **C_FO 去留 + E_SR/E_FO 谁当主 backbone** | 挪后面**扰动 decision**;本轮不拍。C_FO 两操作化均存疑(§ four_layer 2.1) | 用户 2026-05-31 |
| **中文语料专属先验** | **完全不拿出来看**(用户对英文语料也不够了解,无从对比) | 用户 2026-05-31 |
| **年/日历因子 + 其余候选因子** | 挪后面**因子扩展 decision**;本轮只登记 | 用户 2026-05-31 |
| **其他偏见(catalog 16 族)** | 登记备查,**不强求全覆盖** | 用户 2026-05-31 |
| **P0 范式 / false-alpha 桥 / novelty 归宿 / directional-label / Type A 闸门** | gated,见 `R4_next_construct_validity_agenda.md` | 既有 |

---

## 3. arxiv 查新结论(2026-05-31,2026-03 起)

- **核心非发现(对我们最有利)**:48 篇候选无一占据我们的核心组合 =「因子受控刻画 + cutoff
  锚 + 跨 cutoff 模型群 + 中文 CLS」。**身位仍空。**
- **要应对的两条边界**:
  - KTD-Fin(2605.28359,同 A 股市场,但数据打码+评交易 agent)→ 抹掉"首个 A 股记忆基准"
    first-of-kind 说法;related work 须加一段"vs KTD-Fin"(互补:模型侧 cutoff 锚 vs 数据侧打码)。
  - MemGuard-Alpha(2603.26797)→ 坐实 E_CMMD 砍对(D5)。
- **P0 弹药**(下一轮用):lift 极有 LAP(2512.23847)/alpha-decay(2601.13770)/PAM(2602.18733);
  resistance 极有机制背书(2603.21658)。
- 详见 `arxiv_scan_20260531.md`。

---

## 4. 本轮触动的文档(已加 supersede 注)

- `MEASUREMENT_FRAMEWORK.md` §5.2(E_CMMD 整段 retire)+ §5.3(E_FO/E_SR backbone 注)。
- `algorithm_deepaudit.md` 头部(§4/§5 E_FO 主-backbone lean 动摇;E_CMMD CUT 升定调)。
- memory `project_construct_validity_framing` / `research-status` / `lit_landscape` 更新。
