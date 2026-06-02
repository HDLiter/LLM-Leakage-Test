# P1 — 命名漂移拆解(E_FO 消歧 + 三量正名)

> **定位**:纯文档清理。不重开已锁决策、不挑 backbone、不重设计估计量。
> **上游**:P0 定稿(`P0_DECISIONS.md`)+ R-4 定调(`R4_construct_validity_decisions.md`)。
> **推理**:见 `P1_audit_trail.md`。

---

## 0. 一句话

E_FO 的 FO = False Outcome(假结局),不是 Future Outcome(未来结局)。
"预测真实涨跌"叫**真实涨跌对照**,不是估计量。
`memory_lift` 不单独立名,直接用 E_PCSG。
`raw_score` 改叫**模型预测**。

---

## 1. 正名表

### N1 — 模型预测

| 项 | 内容 |
|---|---|
| **正式名** | 模型预测 |
| **Code tag** | `prediction` |
| **定义** | P_predict 在不施扰动的原文上的输出(方向判断、打分或其他形式;具体格式待 R-6 锁) |
| **无记忆基线** | post-cutoff ≠ 0(基准率 + 各种偏见都在) |
| **不是什么** | 不是记忆信号;不是抗扰动差值;不是扣过先验的增量 |
| **旧名** | `raw_score`、`raw_outcome_score`、"原始预测准确率"——已关闭文档不追溯改,新文档一律用"模型预测" |

### N2 — E_PCSG(不另起名)

| 项 | 内容 |
|---|---|
| **正式名** | E_PCSG(配对截止意外度差 / Paired Cutoff Surprise Gap) |
| **决定** | 不单独立名;以前写 `memory_lift` 的地方直接改成 E_PCSG |
| **理由** | E_PCSG 是跨模型配对比较(换一个 cutoff 更晚的模型),不是同一个模型"变熟悉了";"抬升/lift/增量"暗示不存在的 within-model 变化 |
| **旧名退役** | `memory_lift`、"记忆抬升"、"熟悉度增量"——不再当正式术语 |

### N3 — 假结局抵抗(E_FO)

| 项 | 内容 |
|---|---|
| **正式名** | 假结局抵抗 |
| **Code** | `E_FO`(文档)/ `E_OR`(代码,tier-r2-0 已重命名) |
| **定义** | P_predict(原文) − P_predict(C_FO 变体);属抗扰动族 |
| **命名族** | 语义反转抵抗(E_SR)、NoOp 敏感度(E_NoOp)同族,都是 xx 抵抗 |
| **不是什么** | FO = **F**alse **O**utcome,不是 Future Outcome |

---

## 2. E_FO 消歧

**问题**:E_FO 在正式文档里一致指"假结局抵抗";但在 novelty session 口头和
algorithm_deepaudit §4 推理链中,"E_FO"曾滑向"预测真实未来结局"的含义。

**决策**:
- E_FO **只保留**"假结局抵抗"一个含义。
- "预测真实涨跌"一律称**真实涨跌对照**(P0 决策3:pilot 旁证,不设独立估计量)。
- algorithm_deepaudit §4 已加消歧注。

---

## 3. 逐处核对

### 改了的

| 文档 | 改动 |
|---|---|
| `R4_construct_validity_decisions.md` D2 | `memory_lift` → E_PCSG;`raw_score` → 模型预测;resistance 从"≈ 0"行移除(per P0:抗扰动族 post-cutoff 行为不预测);SUPERSEDED 注补 P1 术语退役说明 |
| `algorithm_deepaudit.md` §4 | 加消歧注:E_FO = 假结局抵抗,"真结局"指 C_FO 机制,非预测真实涨跌 |
| `four_layer_candidate_pools.md` §5 | `raw_score` → 模型预测;拆分"抗扰动差值 / E_PCSG"为两行(E_PCSG → ≈ 0;抗扰动差值 → 不预测,per P0) |
| `R4_next_construct_validity_agenda.md` P1 | 标 CLOSED |

### 确认已一致、不需改的

| 文档 | 结论 |
|---|---|
| `MEASUREMENT_FRAMEWORK.md` | E_FO 一致指假结局抵抗;已有 SUPERSEDED 注覆盖 |
| `RESEARCH_PROPOSAL.md` | E_FO = "假结果抵抗",正确;R-2 重开中 |
| `P0_DECISIONS.md` | 不含 E_FO;不含 memory_lift;用"原始预测准确率"(旧名,不追溯改) |
| `P0_audit_trail.md` | 引用 memory_lift 是在解释旧问题;audit trail 不改 |

### 全仓库 E_FO 不再同名两物

正式文档中 E_FO 全部指向"假结局抵抗"。
"预测真实涨跌"在任何文档中均不叫 E_FO,一律称"真实涨跌对照"。

---

## 4. 交给下游

- **扰动会议**:C_FO 去留 + E_SR/E_FO 谁当主 backbone,P1 不涉及。
- **R-6**:模型预测的具体输出格式在此锁定。
- **新文档**:一律用正名表的正式名;已关闭文档不追溯改。
