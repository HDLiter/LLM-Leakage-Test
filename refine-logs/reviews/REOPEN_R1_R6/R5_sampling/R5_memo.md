# R-5 采样与准入过滤 — 最小化 memo

> **status**:未开工。本文件只登记 R-5 的已知输入和待决事项,不是 kickoff。
> R-5 还取决于 R-2(扰动最终清单 → 扰动适用性过滤)、R-6(预测目标 → 是否需要
> 真实股价做案例过滤)、R-1e(因子最终选择 → 分层抽样依据)等上游。
>
> **上游架构**:R-0 已锁唯一 base pool = Pool B(`L2 ∩ universal admissibility`)
> + 可选分布策略层(Pool G/H/I 任意叠加,row-random 也合法)+ 架构扩展位
> (Pool D/E/F)。Canonical:`R0_DECISIONS.md`。
> **scope 来源**:RESEARCH_PROPOSAL §4.7。

---

## 1. R-5 自身的待决事项(来自 §4.7)

1. **分布策略选择**:row-random / G(salience-stratified)/ H(entity-balanced)/ I(cutoff-balanced)/ 组合。R-5 全权。
2. **per-article cap 与 dedupe**:同 article 多 target 进 benchmark 的统计独立性。
3. **text_length 阈值**:上下界。
4. **是否触发 Pool D / E / F 架构扩展**。

---

## 2. 从 P5 并入:退化案例过滤

P5(novelty 最终归宿)已 abandoned 并入 R-5。novelty 不当因子(已成定论),
但有一类**退化案例**——答案不靠记忆也能猜对——是否需要在采样阶段过滤或标注:

- **机械恒等**:结果是算术推出来的(如 Q4 业绩 = 全年 − 前三季)
- **日历已知**:日历本身给出答案(定期公告、固定时间点事件)
- **标签文中明示**:新闻正文里直接写了结果

在 resistance 范式下,这类 case 的威胁减弱(扰动质量协议本身处理
"答案太明显导致扰动无效"的情况),但 R-5 仍应决定:是否过滤、标注为
control、还是不做特殊处理。
