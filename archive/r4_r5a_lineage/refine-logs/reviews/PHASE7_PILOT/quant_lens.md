---
lens: Quant
reviewer: Codex xhigh via sub-agent
date: 2026-04-17
reviewed_doc: plans/phase7-pilot-implementation.md
threadId: 019d9ed7-64e3-7bc2-812b-bf10dfaafa94
---

# Phase 7 Quant Lens Review

## 1. 总体判断 (verdict)
**GO-WITH-FIXES。** 这份 plan 的 identification spine 是对的：用 `CMMD/PCSG` 做 cutoff 侧 quasi-experiment，用 `FO/NoOp` 做 case 内 perturbation，对金融 alpha/sentiment 的 operational relevance 也比通用 QA benchmark 更贴近。但现在还不能直接进 Phase 7 执行，因为有几处 quant 侧核心对象没有冻结清楚：`E_FO/E_NoOp` 的 effect-size 尺度、`§8.2` 统一混合模型里的分析单元、以及 `baseline_confidence` 是否构成坏控制。这些不修，pilot 跑出来也很难作为 Phase 8 power 和主结论的可信输入。

## 2. 强项 (what the plan gets right from a quant perspective)
- **两条 identification 路线是互补的。** `E_CMMD/E_PCSG` 走的是 staggered-cutoff quasi-experiment，`E_FO/E_NoOp` 走的是 within-case controlled intervention。前者给时间可得性，后者给文本内 counterfactual faithfulness；两者一起比单一 detector 更接近“污染而非普通能力差异”的解释。

- **fleet pairing 逻辑总体成熟。** Qwen 早晚对是最干净的 temporal pair，same-tokenizer/same-family 把很多 tokenizer 与 instruction confound 压下去了；再加 size falsification 和 same-cutoff architecture pair，至少不是把跨供应商差异误当 cutoff effect 的幼稚设计。

- **sampling 重点放在 cutoff 中间带而不是平均铺开，这是对的。** 真正有识别力的不是“所有 pre-cutoff case”，而是那些跨不同模型 cutoffs 会改变 exposure status 的 case。`2023-11~2025-01` 两个窗口被刻意加权，quant 上比均匀抽样更有效。

- **对 `C_FO/C_NoOp` 采取全量人工审计，而不是抽样审计，这是必要的。** 这类 perturbation 一旦 edit quality 不稳，effect size 立刻从“memory sensitivity”塌成“rewrite artifact sensitivity”。计划里要求 slot 不可定位就拒绝生成，这比为了 coverage 放松规则更重要。

- **BL1/BL2/correlation matrix/power 模拟被纳入 pilot，而不是留到主实验后解释，这是加分项。** 对 quant 叙事来说，最怕的是主结果出来后再补“其实 baseline 也行”或“其实 controls 不干净”。这份计划至少把这些 challenger 放进了 pilot 的冻结流程里。

## 3. 问题 (issues), 按严重度分三档

### Blocking (必须修才能进 Phase 7)
- **B-01 分析单元与 effect-size 尺度未冻结** (`§8.2`, `R5A_OPERATOR_SCHEMA §3.5`, `MEASUREMENT_FRAMEWORK §5.3`)
  
  问题: `§8.2` 把所有 confirmatory estimand 都写成统一的 `Y_ijm`，但 `E_PCSG` 本质是 case-pair，`E_CMMD` 本质是 fleet disagreement，不是天然的 case-model 标量；同时 `E_FO/E_NoOp` 在不同文档里又出现了“方向翻转”“confidence shift”“一般化 delta”三种写法。更严重的是，`MEASUREMENT_FRAMEWORK` 里 `E_FO = P_predict(original)-P_predict(C_FO)` 这一写法，与 FO 作为“对 visible false outcome 的不服从”在经济含义上是冲突的。
  
  风险: pilot coefficient、estimand 相关矩阵、以及 Phase 8 power 都会变成 apples-to-oranges；即使统计显著，也很难知道测到的是 flip、强度、还是 generic perturbation sensitivity。
  
  建议修法: 先冻结每个 estimand 的**分析单元**和**单一标量 score**。建议至少明确：`E_CTS=case-model continuous`，`E_PCSG=case-pair continuous`，`E_CMMD=case-level across-cutoff separation 或 model-contribution score`；`E_FO` 设为“counterfactual non-compliance”标量，`E_NoOp` 设为“absolute stability loss”标量。然后再谈 mixed model 和 power。

- **B-02 `baseline_confidence` 在主模型里是坏控制，且对 logprob family 定义不清** (`§8.2-§8.3`)
  
  问题: 计划把 `baseline_confidence_im` 放进所有 estimand 的主回归，但它只自然属于 `P_predict` family；对 `E_CTS/E_PCSG` 来说，这等于把另一个 operator 的输出硬塞进来。对 `E_FO/E_NoOp` 来说，baseline confidence 很可能就在 `cutoff_exposure -> memory strength -> baseline confidence -> perturbation delta` 这条路径上，属于 post-treatment mediator，不是干净 confounder。
  
  风险: 会系统性吃掉真正的 temporal effect，尤其是把“记住了所以更自信、也更不跟随 counterfactual”错当成“控制后没效应”。这是 quant 识别错误，不是纯统计技术问题。
  
  建议修法: 把 `baseline_confidence` 从**主规格**移出，只保留为 `P_predict` family 的 sensitivity / stratification；`20-80` mid-range 分析可以保留，但不应定义主 estimand。`E_CTS/E_PCSG` 应使用各自 operator 内部的稳定性/难度控件，而不是跨 operator 借 covariate。

- **B-03 `E_NoOp` 缺少 length/attention placebo，当前无法 cleanly 识别 memory-specific effect** (`§5.4`, `§8.5`)
  
  问题: 现在的 `C_NoOp` 只有 deterministic clause bank 和人工审计，但没有一个 style/length-matched 的 null edit。于是任何 effect 都可能来自更长上下文、注意力稀释、JSON 解析脆弱性，而不一定是金融记忆或 template brittleness。
  
  风险: `E_NoOp` 很容易测成“prompt fragility”而不是“finance contamination sensitivity”；如果仍把它放在 confirmatory family，会污染整套 benchmark 的 quant 说服力。
  
  建议修法: pilot 里加一个轻量 placebo arm，例如长度匹配但语义空的 insertion 或格式控制 edit；若来不及加，就应预先把 `E_NoOp` 降为 exploratory，除非 placebo 证据补上。

### Major (强烈建议修, 否则 Phase 8 会付代价)
- **M-01 `min cell >= 15` 是 guardrail，不是 interaction identification 的充分条件** (`§6.2-§6.4`, `§8.2`)
  
  问题: 计划把 `min cell >= 15` 当作 pilot 可行性的核心 gate，但这里 9 个模型并没有带来 9 倍独立信息，很多 factor 是 case-level，真正识别 `beta3=cutoff×factor` 的还是 case 在 informative exposure 区间里的分布。尤其 `E_FO` 还叠加 eligibility，`E_PCSG` 还叠加 pair-level 限制。
  
  风险: 表面过 gate，实际 interaction coefficient 仍然只靠少数 risk cells 支撑，pilot variance 和主实验 power 都会被低估。
  
  建议修法: 把 checker 从单一 `min cell` 升级为 risk matrix：至少分开报告 informative middle-window support、`C_FO` eligible support、pair-specific support。`15` 可以保留，但要明说它只是最低生存线。

- **M-02 same-cutoff falsification pair 在 pilot `N=100` 下只能算 early warning，不是 architecture-noise baseline** (`Fleet Review R2`, `§12 R4`)
  
  问题: GLM-4-9B ↔ GPT-4.1 只有一个 pair，cutoff 还是近似对齐，不是严格相同；同时 vendor、语言优势、RLHF 形态都不同。用它当“任何 signal 都是 architecture noise”的 baseline，在 pilot 阶段太乐观。
  
  风险: 一旦 same-cutoff pair 也出 signal，你只能说“可能有 confound”，但无法量化 confound 到什么程度；Phase 8 叙事会被迫靠文字 caveat 硬扛。
  
  建议修法: 增加一个 preregistered early warning 指标，例如 `same-cutoff signal / Qwen temporal-pair signal` 比值，外加 cutoff-date jitter sensitivity。这个 pair 在 pilot 里应是 tripwire，不应被包装成 falsification 已完成。

- **M-03 pilot manifest 明确过度加权 perturbation-rich case，直接拿来做 Phase 8 power 会偏乐观** (`§6.2`, `§8.8`)
  
  问题: `60/100` 被刻意选成 verified-outcome + perturbation-rich，这是为了 WS3/WS4 feasibility，不是为了近似主实验分布。这样的 pilot 很可能高 salience、高 rigidity、高 localizability，从而抬高 `E_FO/E_NoOp` 的 observed effect。
  
  风险: power simulation 会把“pilot 容易样本”的 effect size 当成 main run 的 prior，导致 Phase 8 实际 power 低于宣称值。
  
  建议修法: power 模拟至少做两套：unweighted pilot prior 和 reweighted/conservative-shrunk prior。若 pilot 不是 representational sample，就不能只报一个 optimistic power 数。

- **M-04 `BL1` 是合格的 metadata ablation，但还不是 non-trivial operational challenger** (`§8.5`)
  
  问题: 现在的 BL1 只用 cutoff / recurrence / salience / rigidity / event_type / category/date 去解释 `Y`。这能检验“benchmark 是否只是已知 metadata priors”，但对真实金融 alpha/sentiment 的 operational relevance 仍不够，因为它没有碰最基本的 text-light competitor。
  
  风险: 即使 BL1 R² 不高，也不能说明 benchmark 在实际 alpha 任务上有明显增量；你只能说明“纯元数据不够”。
  
  建议修法: 至少补一个低成本 challenger：headline/body 的简单 lexicon 或 linear bag-of-words baseline，用来预测 baseline sign 或 actionable flip-risk。Quant 视角不需要复杂 NLP，只需要一个不是 strawman 的文本轻基线。

- **M-05 `BL2` 规则偏宽，而且 post-cutoff 窗口离最新近似 cutoff 太近** (`§6.2`, `§8.6`)
  
  问题: 计划把 post-cutoff 控制定在 `>=2025-10-01`，但最新 hosted cutoff 仍是近似值；同时 acceptance rule 是 “`|effect|<25%` 或 bootstrap CI overlap 0”。在 `N=20` 下，这个 `or` 很容易放过方向不干净但不够有 power 的坏结果。
  
  风险: 一个本应触发 design review 的非零 temporal signal，可能因为 CI 宽而被当成“negative control 没问题”。
  
  建议修法: 保持 `20%` quota 至少不降，并把窗口尽量再推远；规则上至少要求 point estimate 不得与 pre-cutoff 同向且达到实质性比例，CI overlap 0 只能作补充，不应单独放行。

### Minor (nice-to-have)
- **m-01 `model_capability` 更适合作 descriptive sensitivity，不适合作结构性调整项** (`§8.7`)
  
  问题: 只有 9 个模型，还同时放 model random intercept 和 capability score，能识别的 mostly 是 very coarse between-model level。它能帮你做 caveat，但帮不了干净识别。
  
  风险: 容易诱发“控制了 capability 所以 cutoff 更因果”的过度解读。
  
  建议修法: 在写法上把它明确降格为 sensitivity/robustness covariate，不解释 `beta4`，只看 primary coefficient 稳不稳。

- **m-02 Exit gate #9 过于宽松** (`§13`)
  
  问题: “>1 retained confirmatory estimand 达到 80% power” 这个门槛太低，可能允许一个 fleet-wide temporal estimand 加一个边缘 perturbation estimand 就开 Phase 8。
  
  风险: 主实验启动后，confirmatory family 名义上保留很多 estimands，实则只有少数可检。
  
  建议修法: 更合理的是要求至少一个 fleet-wide temporal route 和一个 perturbation route 都有足够 power。

- **m-03 rerun stability 最好看 delta，不只看 baseline prompt** (`§5.3`, `§5.5`)
  
  问题: 当前 duplicate rerun 主要盯 baseline direction disagreement。对 quant 解释更关键的是 perturbation delta 是否稳定，因为 effect-size 用的是 delta，不是单次 baseline。
  
  风险: baseline 很稳但 delta 不稳时，pilot effect 仍可能被 provider randomness 压扁。
  
  建议修法: 在小子样本上重复 `C_FO/C_NoOp` 也做 rerun，直接监控 delta drift。

## 4. 五个必答问题

**Q1. `min cell >= 15` 在 9 模型 × 4 factors × 5 estimands 下, 对 N=100 是否真的可行? 哪些 factor × model cell 风险最大?**  
勉强可行，但只是在“binary collapse 后的 pilot 生存线”意义上可行，不是在 interaction identification 意义上宽裕。风险最大的是 `E_FO` 的低 eligibility 尾部 cell、`E_PCSG` 的 pair-level middle-window cell，以及 `E_NoOp` 在 `policy/macro` 这类 insertion naturalness 更差的 cell；9 个模型不会把 case-level factor 的有效样本自动放大成 9 倍。

**Q2. 同 cutoff falsification pair (GLM-4-9B ↔ GPT-4.1) 在 pilot N=100 下能否提供有意义的 architecture-noise 基线? 如果不能, Phase 7 要不要加一个 early warning signal?**  
不能把它当“有意义的 falsification baseline”，最多算 weak early warning。Phase 7 应该加，而且要 preregister：建议至少报 `same-cutoff / temporal-pair` signal ratio，加 cutoff-date jitter sensitivity；若该比值偏大，就自动收窄 Phase 8 的 causal claim。

**Q3. BL1 简单 baseline predictors 在 CLS 财经新闻上最可能的 R² 区间是多少? 如果 baseline 本身就能解释 60%+ 的 Y 变异, 本 benchmark 的增量价值还剩多少?**  
我对 metadata-only BL1 的先验是 OOF `R² ≈ 0.10-0.30`，`0.35+` 已经说明 detector 很可能在吃 event-type / template priors；`0.60+` 在这个任务上我会视为危险信号。若真到 `60%+`，benchmark 仍有审计价值，但主要剩“标准化 stress test / case triage”价值，不再是强有力的 leakage 识别增量。

**Q4. Plan 中的 post-cutoff negative control (BL2) 的样本配额是否足够? 如果 post-cutoff 文章占比 < 15% 是否就失去了诊断价值?**  
`20/100` 够做 tripwire，不够做精细估计或多层 subgroup diagnosis。若 post-cutoff 占比掉到 `<15%`，在最新 cutoff 仍有近似误差的情况下，诊断价值会明显下降，我会认为它基本失去“拦截坏设计”的力度。

**Q5. Effect-size 定义上, E_FO / E_NoOp 的 "delta" 在什么尺度测 (概率 delta、rank delta、logit delta)? Plan 中是否 underspecified? 这会影响 Phase 8 power 模拟。**  
是 underspecified，而且会直接影响 power。现有输出没有 class probability，所以真正的 probability delta 不可得；我建议冻结一个 `signed-score = sign(direction) × logit((confidence+0.5)/101)`，`E_FO` 用“相对 expected false outcome 的 non-compliance score”，`E_NoOp` 用 `|signed-score_base - signed-score_noop|`，方向 flip 只作为 secondary binary readout。

## 5. 对 Phase 8 exit gate 的 quant 侧意见
1. **Gate 1** adequate。先把 measurement stack 跑通是必要条件。  
2. **Gate 2** adequate。两阶段 prereg 是这套设计避免事后漂移的核心。  
3. **Gate 3** adequate。white-box provenance 不干净，`PCSG/CTS` 就没有 quant 信用。  
4. **Gate 4** adequate。对 `P_predict` 来说 parse/fingerprint 是最低可审计要求。  
5. **Gate 5** 建议加强。`min cell >= 15` 只能保底，不能替代 informative-window / pair-specific support 报告。  
6. **Gate 6** adequate。`FO/NoOp` 若不过 gate 就应老老实实 demote。  
7. **Gate 7** 建议加强。`BL2` 应从“not directionally contradictory”升级成更明确的 point-estimate + window-distance 规则。  
8. **Gate 8** adequate。相关性触发 regrouping 至少能防 family 冗余。  
9. **Gate 9** 建议加强。应要求至少一个 temporal route 和一个 perturbation route 都有足够 power，而不只是“超过一个 estimand”。  
10. **Gate 10** adequate。go/no-go memo 本身不是识别，但能把量化风险冻结下来。

## 6. 跨 lens 信号
- **Stats**: 请明确每个 estimand 的分析单元与 score 尺度；重新判断 `baseline_confidence` 是否应进主模型；重做“perturbation-rich pilot -> Phase 8 power”的 transportability 方案。
- **NLP**: 请给 `C_FO` 的 expected-direction mapping 和 `C_NoOp` 的 placebo/null edit 设计；否则 FO/NoOp 量化结果没有稳定语义。
- **Editor**: 请准备更收敛的 claim language，把 `cutoff_exposure` 讲成 observability proxy，把 same-cutoff pair 讲成 early warning 而非已完成 falsification。
- **ML Engineer**: 请把 estimand-specific scalar score、pair-level table 和 perturbation-delta rerun 输出到位；这不是实现洁癖，而是 quant identification 依赖的数据 contract。
