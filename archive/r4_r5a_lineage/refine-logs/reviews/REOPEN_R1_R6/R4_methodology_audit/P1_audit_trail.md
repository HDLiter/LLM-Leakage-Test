# P1 audit trail — 命名漂移拆解

> **session**: 2026-06-02, clean-room-first。
> **canonical**: `P1_DECISIONS.md`。

---

## 1. 白板分析(独立,未看既往文档)

### 1.1 E_FO 同名两物 — 问题有多大?

逐文档 grep `E_FO` 后的结论:**正式文档里 E_FO 一致指"假结局抵抗"(False
Outcome Resistance)**。"Future Outcome prediction"只出现在:
- novelty session 口头(没落进正式文档);
- `R4_next_construct_validity_agenda.md` L48——但那本身就在**描述这个命名问题**。

真正咬人的是 **隐式混淆**:`algorithm_deepaudit.md` §4 的推理链"post-cutoff
模型没见过**真结局** → 没东西可抵抗 → null 归零"把"真实未来结局"的概念混进
resistance 论证。读者可能倒推:E_FO = 预测真实涨跌。修法:加消歧注把 C_FO
机制讲清(模型没有记忆里的真实结局 → 对假结局无从抵抗),不是在说"预测真实
涨跌"。

### 1.2 三个量

| 量 | 以前的名字 | 问题 |
|---|---|---|
| 模型在原文上的输出 | `raw_score` / `raw_outcome_score` / "原始预测准确率" | "原始/raw" 带不必要的 framing;"得分/score" 预设输出是打分(但可能是方向) |
| 扣先验后的增量(E_PCSG 通道) | `memory_lift` / "记忆抬升" / "熟悉度增量" | E_PCSG 是跨模型配对比较(换 cutoff 更晚的模型),不是同一模型"变熟悉了";"抬升/增量"暗示不存在的 within-model 变化。且 P0 专门禁止把 lift 当 resistance 承重词——如果 lift 本身不当正式术语,规则自然满足 |
| C_FO 抗扰动差值 | E_FO | 同名两物(见 1.1) |

### 1.3 推荐

- **模型预测** (`prediction`):中性,不预设输出格式;与"不是记忆信号"的消歧天然配合。
- **E_PCSG 不另起名**:用户指出"熟悉度增量"本身误导(好像模型变熟悉了);行文可白话解释但不承重。
- **假结局抵抗**:与 E_SR(语义反转抵抗)同族命名,对外可读。FO = False Outcome 消歧放正名表。

## 2. 对照既往

白板结论与 P0 / R-4 定调一致:
- P0 已把"真实涨跌"降为 pilot 旁证(决策3);
- P0 已禁止 lift 当 resistance 承重词;
- R-4 D9 已识别 E_FO 命名漂移、作废旧表述。

P1 把这些已有决策在命名层落地,不产生新决策。

## 3. 文档改动清单

| 文档 | 改动 | 理由 |
|---|---|---|
| `R4_construct_validity_decisions.md` D2 L30 | `memory_lift` → E_PCSG;resistance 从"≈ 0"行移除 | memory_lift 退役;resistance post-cutoff 不预测(P0) |
| `R4_construct_validity_decisions.md` D2 L31 | `raw_score`(原始预测准确率) → 模型预测 | 正名 N1 |
| `R4_construct_validity_decisions.md` D2 SUPERSEDED 注 | 加 P1 术语退役说明 | 标记旧名已退役 |
| `algorithm_deepaudit.md` §4 L74 后 | 加消歧注 | E_FO = 假结局抵抗,非 Future Outcome |
| `four_layer_candidate_pools.md` §5 L255 | 拆分"抗扰动差值/E_PCSG"为两行;E_PCSG→≈0,抗扰动差值→不预测 | P0 修正落地 |
| `four_layer_candidate_pools.md` §5 L256/260 | `raw_score` → 模型预测 | 正名 N1 |
| `R4_next_construct_validity_agenda.md` P1 L47 | 标 CLOSED | P1 完成 |

不改的:MEASUREMENT_FRAMEWORK.md(已正确+已有 SUPERSEDED)、RESEARCH_PROPOSAL.md
(已正确,R-2 重开中)、P0_DECISIONS.md(不含问题名称)、P0_audit_trail.md(审计
trail 不改)、arxiv_scan(文献引用外部概念)。

## 4. 代码层

tier-r2-0 已把代码里的 E_FO → E_OR、C_FO → C_CO。P1 scope 是文档,不碰代码。
文档层保留 E_FO 代号(与 MEASUREMENT_FRAMEWORK.md / four_layer_candidate_pools.md
一致);代码与文档的映射(E_FO ↔ E_OR)在 tier-r2-0 计划中有记录。
