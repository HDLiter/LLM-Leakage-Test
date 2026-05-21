# Pass 1 Walk-through — 第 4 章 / 共 7 章:扰动与算子

> 供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、逻辑断点、
> 追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。

## 算子(L3)

冻结 inventory 4 个,confirmatory 只有 2 个:
- P_logprob(白盒):一次前向,token 级 logprob,score = bottom-K% token
  校准均值(Min-K++/CTS)。必须 thinking OFF。喂 E_CTS、E_PCSG。
- P_predict(黑盒即可):文章 + 冻结任务 prompt → 方向/置信度 + 记忆标记 +
  证据引用;模型默认部署模式。主力,喂 E_CMMD 及所有扰动型 estimand。
- P_extract、P_schema:reserve,不进 confirmatory。

不对称:P_logprob 白盒-only → E_CTS/E_PCSG 仅 12 白盒;P_predict 全队 →
E_CMMD/E_FO/E_NoOp 看 14 模型。confirmatory family 跨两个模型总体(详见第 5 章)。

## 扰动(L2)

冻结 6 个,confirmatory 只有 C_FO + C_NoOp(喂 E_FO/E_NoOp)。其余 4 个
(C_anon/C_SR/C_temporal/C_ADG)仅喂探索性 estimand —— 20 系数预算取舍。

- C_FO(假结果):把已核实真实结果值换成具体假值,setup/时间/实体不变;
  规则化 slot 编辑,仅对"有已核实已知结果"的案例。WHY:测模型是否无视
  眼前反事实证据、吐记忆里的真结果。E_FO = false outcome resistance。
- C_NoOp(无关插入):插一句无关但貌似合理的 CLS 短句(8-16 字,中间位,
  host-aware 子句库)。WHY:测记忆是否表现为脆弱模板匹配。E_NoOp = NoOp
  sensitivity。设计自身定性:robustness / 模板脆弱性信号,非直接记忆证据。

C_FO/C_NoOp 全量人工审计(WS3,4 维 rubric,kappa≥0.70);审计通过率
≥85% 是数据质量门(condition 1;condition 3 已于 2026-04-29 移除)。

## negative controls

- BL2 post-cutoff 负对照:350 例 ≥2026-02-01(晚于全队最晚 cutoff ≥6 月);
  事件在所有模型 cutoff 之后 → 信号应近零;TOST 等价检验(SESOI=0.15)。
- 同-cutoff 证伪对(§8.6A):GLM-4-9B ↔ GPT-4.1,同 cutoff 不同架构;
  early-warning ratio >0.5 → 架构混淆时间信号。
- C_NoOp_placebo:长度匹配空编辑,探索性-only。
- BL1:纯元数据基线预测器。BL3:非金融中文新闻负对照,stretch only。

不对称:BL2 只重跑 E_CMMD/E_PCSG/E_CTS 这 3 个;E_FO/E_NoOp 无 post-cutoff
负对照(post-cutoff 案例不做扰动)。某种程度内在(假结果测试需已知结果)。

## 与研究问题的 why 链

算子=怎么算分;扰动=怎么造对比;negative controls=怎么自证非假信号。
均直接服务"可信地刻画泄露"。无断点。

## 本章 flag

无新硬 flag。
- heads-up:E_NoOp 是 confirmatory estimand 却被设计自身定性为脆弱性信号
  (非直接记忆证据);设计逻辑 = 多信号收敛的 construct validity。待用户
  有意识确认接受 confirmatory family 为"记忆信号 + 一个脆弱性信号"混合。
- 强化 flag ④:C_NoOp/E_NoOp 与 Template Rigidity 因子同源(模板硬币两
  面);Template Rigidity 无 spec 使 E_NoOp×TemplateRigidity 这个 20-系数
  cell 双重欠定义。
