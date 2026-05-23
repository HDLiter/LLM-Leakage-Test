# C_FO vs C_SR — 历史血缘 + 当前发现(暂存,待 R-4 后再决)

> 状态:**parked**——等 R-4 方法论审计落地(它决定 confirmatory family 大小 /
> multiplicity 校正级别)之后,再回头接 R-2 时处理。

## 当前 session 触发

R-6 走查里,用户指出 CC 描述 C_FO 例子时漂移了——把「净利润+384%→由盈转亏」
这类极性翻转值替换当成 C_FO 全貌,实际上这正是 **C_SR** 的领地;且 R5A 之前
还有一版机制不同的 FO。回查历史确认下述血缘。

## 历史血缘

- **pilot_phase**(`archive/pilot_phase/notebooks/02_counterfactual.ipynb` md cell 0)
  - `reverse_outcome` 翻方向 — 后来的 **C_SR**
  - `alter_numbers` 改数值 — 后来的 **C_FO**
  - 两个都是**就地改文章**
- **pre_benchmark CPT 探索**(`archive/pre_benchmark/refine-logs/EXPLORE_FALSE_OUTCOME_*.md`)
  - 「False-Outcome **CPT**」:**训练时**注入,**在文章末尾追加 outcome block**
    —— `T+1 / T+5 真实收益 + bucket + 一句 rationale`
  - 三臂:原文 / +真结果 / +假结果(收益翻号)
  - **这一版 FO 用了真实股价收益。**
- **Phase 5 转向**纯行为 benchmark → 整条 CPT 线被砍,「False Outcome」**名字**
  留下,接到「就地改写」机制上
- **R5A 至今**(`refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` §96-97,
  `R5A_FROZEN_SHORTLIST.md` §7)
  - **C_FO** = outcome slot replacement(就地换值)— confirmatory(喂 E_FO)
  - **C_SR** = semantic polarity reversal(就地翻极性)— exploratory(喂 E_SR)

## 关键发现

1. **C_SR 和 C_FO 在「极性翻转值替换」这个最实用形态上几乎重合**;R5A_STEP1/2
   评审反复合并/拆开(「SR/FO Counterfactual Pair」「CFI」「FO primary,
   SR diagnostic」),最终拆开的理由站得不算特别稳。
2. **结构性原因**:E_FO 测的是 P_predict 方向输出变不变,要让方向变,假值
   通常就得跨过涨/跌分界——也就是顺手翻极性。所以「不翻极性的 C_FO」
   (35%→3%)原则上存在,但对 E_FO 是弱扰动。
3. **R-2 ↔ R-6 耦合**:老 FO 用了真实收益(append T+1/T+5);现 C_FO 完全
   不碰市场。「C_FO 要哪一版机制」**同时是 R-2(扰动)和 R-6(用不用真实
   收益)的决定,是同一个决定**。
4. **CC 上一条的更正**:之前说「C_FO 完全不需要市场数据、和 R-6 脱钩」——
   那句**只对现行就地换值 C_FO 成立**。

## 待决(R-4 落了之后接 R-2 时处理)

- C_FO 机制:就地换值(现行)/ 追加真实收益结果块(老 CPT 行为版)/ 二者
  都做 / 别的
- C_FO vs C_SR 在 confirmatory 里谁主谁次(还是合并、都进、都不进)
- 是否把「FO 机制 = 是否追加真实收益」拎成 R-2/R-6 的同一个决策点

## 推荐下一步动作(R-4 之后)

1. 跑**极小可行性 probe**(20-30 例真实 CLS 新闻,同时造 C_FO + C_SR 两版),
   **只看 artifact 质量**(不跑模型、不算 flip 率)。结构上不可能 cherry-pick。
2. 按 R-4 后的 confirmatory 容量决定容纳几个 confirmatory 扰动。
3. 再决定 C_FO 机制走哪一版。

## 引用

- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` §96-97(定义)
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` §1 / §3 / §7
- `archive/r4_r5a_lineage/refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md` 第 50 行
- `archive/r4_r5a_lineage/refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md` §D5
- `archive/pre_benchmark/refine-logs/EXPLORE_FALSE_OUTCOME_QUANT.md` §4(CPT outcome block 格式)
- `archive/pilot_phase/notebooks/02_counterfactual.ipynb` md cell 0
