# R-1a Cutoff Exposure — final decisions

**Status**: 机制(metric machinery)**LOCKED 2026-05-27**;各模型 cutoff **中心值 PROVISIONAL**(待 cutoff-probe 验证 + owner sign-off,见 §6 / §11)
**Audit trail**(下游 agent 不需要读;只在需要 debate / 看推导过程时翻):
- `whiteboard_codex.md` —— Codex clean-room 白板(6 决策点独立分析)
- `cutoff_deep_research_gpt.md` —— GPT deep research 对 16 模型 cutoff 可信度调查
- `cutoff_probe_protocol_codex.md` —— Codex 设计的黑白盒通用 cutoff 验证探针协议

---

## 1. Framing / measurement claim

| 字段 | 值 |
|---|---|
| Stance | **CLS text / article exposure**(模型是否**有机会见过这条 CLS 电报**)|
| Claim 不对称性 | cutoff **晚于**报道 → 模型至少有机会见过这篇报道(及同事件更早报道);cutoff **早于**报道 → 很可能没见过这篇报道本身,但**仍可能**见过同事件更早报道(CLS 非第一手)→ "未曝光" **不是硬零** |
| 不是什么 | **不是** "real-world event exposure"(同事件别处也报道过,published_at 管不到;回顾/预告类文章 published_at 与事件真实日错开)|
| 保守性 | manifest 多为 knowledge cutoff(系统性偏早,见 §3)→ 中心偏保守 → 泄露估计**偏低不偏高**(论文可正面交代)|
| Paper §4.1 措辞 | 窄 claim("可能见过这条 CLS 文本"),措辞风格留 paper-write |

**统计角色**:Cutoff Exposure 承载**主效应 β1**;其余因子测"与 Cutoff Exposure 的交互 β3"。它是被交互的基准轴。是全 fleet **唯一的 case×model 因子**。

---

## 2. Event date 口径(case 侧)

| 字段 | 值 |
|---|---|
| 主口径 | **`published_at`**(发文日,S0 已有,**精确到天**,确定性,全覆盖)|
| 为何不用 in-text event date | 需抽取 → 几乎必依赖 LLM → 撞 R-0 §2 约束 5 红线(factor metric 不依赖 operator 输出);且很多电报无明确事件日(稀疏 / 歧义)|
| in-text event date | 仅作 §8 robustness 子集,且**仅在可确定性规则抽取时** |

---

## 3. Cutoff manifest(model 侧)

| 字段 | 值 |
|---|---|
| 来源 | **`config/fleet/r5a_fleet.yaml` 的 `cutoff_date`**(与 R-1b/R-1c reference window 右端点同源,不引入第二套口径)|
| Path-E / 行为探针 | **不作主来源**,只验证(见 §6)|
| 月内归一约定 | cutoff 归当月**末日**(采"最宽容训练 cutoff"口径;对结果影响极小,口径干净可复现)|
| knowledge vs training cutoff | exposure 要的是"有机会见过"= **training cutoff**(更晚、更宽容);manifest 多只给 knowledge cutoff(偏早)→ 中心是保守下界 |
| 中心值状态 | **PROVISIONAL** —— 现值保留 yaml;deep research(`cutoff_deep_research_gpt.md`)已标几个低可信度模型的候选修正(Qwen3 ~2024-10、DeepSeek ~2025-05、GLM-4 弱证据 2024-01..04、Claude training=Jan 2026 / 知识 May–Aug 2025 矛盾),但**不自动改 manifest**,经 §6 探针 + owner sign-off 后人工修正 |
| 对上游无扰动 | 最早 cutoff = Llama-3 **2023-03**(Medium 可信、不变)→ R-1b/R-1c 用的 `min(model_cutoff)` 不动,**已 closed 的 R-1b/R-1c 不受影响** |

---

## 4. Metric 形态

```text
delta_days[case, model] = ( cutoff_eom(model) - published_at(case) ).days
d_months[case, model]   = delta_days / 30.4375          # 连续月,正 = pre-cutoff
cutoff_exposure[case, model] = tanh( d_months / w )      # S 曲线,中心 = 该模型 cutoff
```

| 字段 | 值 |
|---|---|
| 形状 | **tanh**(S 曲线)。远在 cutoff 之前 → +1 压平;cutoff 处 → 0;远在之后 → −1 压平;只在 cutoff 附近敏感 |
| 为何不用 log | log 在远端不压平(10 年前仍 > 4 年前),与"历史=当代记得一样好、未来都一样"的语料认知冲突 |
| sign | **pre-cutoff 取正**(有机会见过 = 正曝光)|
| 宽度 `w` | **主值 = 2 个月**;稳健性扫 **1 / 3 / 6 个月** |
| `w` 含义 | 仅表达"渐变 + CLS 非第一手"造成的**不可消除边界模糊**(量级几月);**中心不确定不进 `w`**,走 §6 中心灵敏度 |
| `d` 精度 | **连续月**(`天数 / 30.4375`),不取整数月(取整丢发布日的天精度 + 制造月界假跳变)|
| 软边界双理由 | ① cutoff 仅月级精度 + 部分靠猜;② CLS 非第一手 → 同事件更早报道把曝光往前抹开(该 smear 部分由 R-1b Recurrence 因子捕捉,故 Cutoff Exposure 保持干净 = published_at vs cutoff)|

---

## 5. case×model 物化(metric 层,非统计层)

| 字段 | 值 |
|---|---|
| 单位 | 每个 `(article_id, target_entity_id, model_id)` 一个值,L3 admissible case rows × fleet models **cross join**,不聚合 |
| 物化列 | `delta_days`(canonical,可审计)+ `cutoff_exposure`(tanh 主连续值)|
| 自然结果(非问题)| 同 article 多 target row 共享同一时间值;同 cutoff 模型得相同值(manifest 事实)|
| 边界 | 怎么进 random effects / β1 怎么估 = **R-4,不在 R-1a** |

---

## 6. Cutoff 验证轨(验证非定义)

| 字段 | 值 |
|---|---|
| 定位 | 探针只**体检 manifest** + 大偏差**触发人工复核**;**永不自动改 manifest、永不喂 exposure 指标**(守 R-0 §2 约束 5 + 防与 E_CTS 自闭环)|
| 白盒线 | WS1 已建 Path-E(月度 Min-K%++ logprob → 断点),`src/r5a/analysis/exposure_horizon.py`;对小弱模型尤其适用(不要求模型会答)|
| 黑白盒通用线 | 闭卷 dated-fact QA(答对率随月陡降 → 经验知识 horizon);主要在 4 黑盒 + 大模型上有效 |
| 报警 gate | 红/黄/绿;红 = horizon CI 不含 manifest 月且 point 偏 ≥3 月 → 人工复核(可能手动改 manifest 或加保守 provenance 标记)|
| 协议 | 全文见 `cutoff_probe_protocol_codex.md`;主体检 = 通用世界 QA,CLS 金融 QA 作领域副线 |
| Claude 矛盾 | 探针 May–Aug 2025 加密 resolve 知识 cutoff;Jan 2026 训练 cutoff 行为 QA 测不到(知识 horizon 是其下界)|
| 实际跑 | **downstream**,gated on fleet 部署 + 黑盒预算 + 人工核验答案表;现状 = 协议设计完成,题库未建 |

---

## 7. Continuous + binary 负对照

| 字段 | 值 |
|---|---|
| 主因子 | 连续 tanh(§4)|
| pre/post 二元 | **不单独存列**(= `delta_days` 符号,trivially 派生);BL2 负对照分析时按 `delta_days < 0` 现切 |
| BL2 角色 | post-cutoff case 模型理应没见过,效应应 ≈ 0,走 R-4a 锁的 TOST/SESOI=0.15;"证明 cutoff 后无泄露"反衬"cutoff 前泄露为真" |
| 为何不让二元扛主效应 | 二元对 cutoff 误差更敏感(贴边 case 易分错)→ 适合负对照 / sanity check,不适合 β1 |

---

## 8. Robustness(唯一最小形态)

| 字段 | 值 |
|---|---|
| in-text event date 子集 | 对**可确定性规则抽取**事件日的子集,改用事件日重算 exposure,看 β1 稳不稳。**绝不用 LLM 抽**(否则碰红线)|
| 子集性质 | 自选(只覆盖"日期写清楚"的文章),力度有限 → **robustness 层**,非 main |
| `w` 扫描 | 主 `w=2`,稳健性跑 `1 / 3 / 6` 看结论是否依赖具体宽度 |
| 中心灵敏度 | 低可信度模型把 cutoff 中心挪到 deep research band 两端各跑一遍,看 β1 稳健性(R-4a 锁的 cutoff 误分类模拟接此)|
| 显式不做 | 多窗口 / 多 transform 网格(别的 construct,scope 外)|

---

## 9. Downstream session anchors

### 9.1 R-1e(因子最终选择)—— 不预承诺 Cutoff Exposure 必进 primary
但它是 β1 载体,实务上几乎必然在 primary。Pilot 后给 R-1e 输入:`cutoff_exposure` 分布(pre/post 两桶)、`delta_days` 分布、pre-cutoff case 在各模型上的 spread(够不够估 β1)、`w` 扫描下 β1 稳健性、中心灵敏度结果。

### 9.2 R-4 / R-4b —— case×model 怎么进统计是 R-4
R-1a 只给 metric 数值口径。混合模型 / random effects / β1 估计 / cutoff 误分类模拟规格 = R-4b。

### 9.3 R-5(Sampling)—— Pool I(cutoff-balanced)
若 R-5 启用 Pool I 支撑 case×model panel,用 `cutoff_exposure` / `delta_days` 平衡;R-5 全权。

### 9.4 B-2(实现)—— 见 §10;cutoff 验证探针的建/跑排进 fleet 工作

---

## 10. B-2 schema requirements

`factor_provenance.run_inputs.per_task.cutoff_exposure` 必须包含(字段名/风格留 B-2 整体 session):

- `factor_name = cutoff_exposure`
- `framing_claim = cls_text_article_exposure`
- `unit = [article_id, target_entity_id, model_id]`(case×model）
- `event_date_field = published_at`(day precision)
- `cutoff_source = fleet_yaml_cutoff_date`
- `cutoff_within_month_convention = end_of_month`
- `transform = tanh`
- `width_w_months = 2`(robustness sweep `[1, 3, 6]`)
- `d_unit = continuous_months_days_div_30.4375`
- `sign_convention = pre_cutoff_positive`
- `stored_columns = [delta_days, cutoff_exposure]`(binary pre/post 派生不存）
- `cutoff_centers_status = provisional_pending_probe_validation`
- `probe_validation = non_defining; manual_review_on_gate; never_feeds_metric`

### Provenance hashes
- S0 source snapshot hash · layer / view definition hash · **fleet cutoff manifest hash** · sampling manifest hash(when factor values tied to a sampled frame)

---

## 11. Open items(R-1a 挂着的)

- **各模型 cutoff 中心值** PROVISIONAL → 待 §6 探针(downstream,gated on fleet)+ owner sign-off 后人工修正 manifest;deep research 候选修正(Qwen3 / DeepSeek / GLM / Claude)不自动套用。
- **探针建 + 跑** = 专门 session 细化(题库构造 / gate 阈值 3vs4 / UNKNOWN 处理 / 题量等建造细节,见 `cutoff_probe_protocol_codex.md §8`),排进 fleet 部署。
- **paper §4.1 措辞**(窄 claim 的具体语言)留 paper-write。
