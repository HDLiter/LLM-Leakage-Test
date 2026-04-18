---
lens: Stats
reviewer: Codex xhigh via sub-agent
date: 2026-04-17
reviewed_doc: plans/phase7-pilot-implementation.md
threadId: 019d9ed8-7eb1-7033-b9e3-12dff1bb6e2d
---

# Phase 7 Stats Lens Review

## 1. 总体判断

**GO-WITH-FIXES。** 基于 [phase7-pilot-implementation.md](</D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md>)、[R5A_FROZEN_SHORTLIST.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md>)、[MEASUREMENT_FRAMEWORK.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md>)、[FLEET_REVIEW_R2_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md>)，这份 plan 的统计骨架是对的：pilot/main 分离、confirmatory family 收敛到 `20` 个系数、`Westfall-Young stepdown max-T`、quality-gated demotion、formal power simulation，这些都站得住。现在的问题不是“大方向错了”，而是还有几处会让 two-stage prereg 的 type-I error 叙事变成“形式上 adaptive、实质上 discretionary”。修完这些点，方案可执行；不修，主风险在于 error-control 说不硬、power 解释不干净、`P_predict` 分支有 post-treatment adjustment。

## 2. 强项

- 把 confirmatory family 冻到 `5 estimands × 4 factors = 20 coefficients`，比旧的 detector-zoo 口径统计上干净得多。
- 把 `E_FO` / `E_NoOp` 的 confirmatory 身份绑定到 admissibility gate，而不是 pilot 显著性，这一点是对的。
- `M2` 明确要求在 `N=2560`、保留缺失/eligibility mask、并在 `Westfall-Young` 下做 power simulation，这比闭式近似靠谱。
- `E_TDR` 被锁成 `cutoff × dose` interaction 而非独立 estimand，避免了凭空扩 family。
- `BL1`、`BL2`、`C1`、`C3` 都被写进 pilot，而不是到主实验后再补，这是好习惯。

## 3. 问题

**Blocking**

- `B01` - Stage 2 adaptation 仍然保留 memo 裁量，尤其是 `C1 regrouping`。风险：family 选择变成“pilot 后人工判断”，FWER 叙事会变弱。修法：Stage 1 必须把所有允许的 Stage 2 状态表列死，并给 `regrouping` 写 deterministic action，不只是“open memo”。
- `B02` - `baseline_confidence_im` 被放进 primary mixed model。风险：对 `E_CMMD`、`E_FO`、`E_NoOp` 这类 `P_predict` 派生量，这是 post-treatment / overadjustment，尤其在 delta estimand 上几乎是在调 outcome 的前件。修法：把 `C3` 改成 sensitivity only，不进 confirmatory 主模型。
- `B03` - `BL2` 现在不是正式 equivalence test。风险：你只能说“看起来接近零”，不能说“统计上支持近零”。修法：预先写 TOST bound，bootstrap overlap zero 只保留为描述性补充。

**Major**

- `M01` - `min cell >= 15` 写成 “per estimand × factor × model” 对 `E_CMMD` 不成立，对 `E_PCSG` 也不精确。风险：checker 通过了，但 estimand 实际没被正确识别。修法：改成 estimand-specific analysis unit。
- `M02` - `Westfall-Young max-T` 和 mixed model 的接口没写清。风险：有人会直接做 naive permutation；对 crossed random effects + continuous exposure 这不 valid。修法：预注册 case-cluster parametric bootstrap 或 cluster wild bootstrap 的 max-T。
- `M03` - `E_TDR` 的 identification 还缺 sham deletion control。风险：`β3` 混入 generic information loss。修法：把 same-length non-temporal sham 作为对照，至少在 exploratory model 中显式进入 `cutoff × sham`。
- `M04` - `BL1` 只说 OOF `R²` / loss，但没写 grouped CV unit。风险：同一 article 的多 model / 多 variant 泄漏到 train/test。修法：按 case bundle 切分，`E_PCSG` 保 pair，`E_FO/NoOp` 保 baseline+perturbation 同 fold。
- `M05` - `E_CTS`/`E_PCSG` 的 correlation/regrouping 规则不完整。风险：相关高时到底合并、保留哪个、还是只 narrative regroup，当前都没冻结。修法：若触发，默认保 `E_PCSG` confirmatory，`E_CTS` 转 corroborative，不得现场发明 composite。

**Minor**

- `m01` - `model_capability` 只有 `9` 个 model level，和 `v_m` 基本弱可分。风险：过度解释 `beta4`。修法：明确它只是 nuisance adjustment，不做实质结论。
- `m02` - `bootstrap over cases` 对 pair-specific estimand 太粗。修法：按 article bundle resample，并保留模型与 paired traces 的联结。
- `m03` - `25% of matched pre-cutoff effect` 用 observed effect 当 bound，太 data-dependent。修法：bound 应该基于预设 SESOI，不该基于 pilot realized effect。

## 4. 八个必答问题

1. **Q1**  
   只要 `pilot` 与 `main run` 样本严格独立，且 Stage 2 的变更规则在 Stage 1 里写死，`quality-gate demotion`、`regrouping`、`reserve promotion` 这种 pilot-informed adaptation 对主实验的 FWER 可以是 valid 的；这里不需要 adaptive alpha splitting。需要的额外约束是：`pilot cases` 绝不能并入最终 confirmatory analysis；Stage 2 只允许按预先枚举的规则改 family；不得根据 pilot 的显著性或叙事偏好 ad hoc 改 spec。若未来想把 pilot 和 main 合并分析，才需要 combination test / alpha spending。

2. **Q2**  
   先澄清：当前 frozen confirmatory family 是 `20/16`，不是 `80/64`。如果你们实际上把 family 扩成 `80/64` 个系数，power 会明显变差。粗略下界上，`N_case=2560` 时，若 `80` raw coefficients 在正相关下相当于 `20-30` 个有效独立检验，则 80% power 大致要求 standardized partial effect `|β*|≈0.08-0.10`；若只有 `60%` eligible coverage，则要到 `0.10-0.12`。把它翻译回你们现有 detector-level 先验，大致是：`PCSG ≈ d 0.21-0.26`，`CMMD/CTS ≈ d 0.25-0.32`，`FO/NoOp ≈ d 0.33-0.40`；若 residual noise 仍有 `50-70%`，取这些区间的上半段。pilot 侧不要用 `β̂` 点估计做 planning，建议用 shrinkage-adjusted one-sided lower bound，例如 `β_plan = max(0, q20(β_boot,bias-corrected))`。

3. **Q3**  
   现在这句需要改。`E_CMMD` 是 fleet-level estimand，不存在“单个 model cell 的 n_eff”。更合理的写法是 `n_eff(estimand, factor_bin, analysis_unit)`。对 `E_CMMD`，analysis unit 应是 case-level fleet contrast，例如“该 case 在该 factor bin 下是否同时有足够 exposed/unexposed models”；对 `E_PCSG`，analysis unit 应是 case × temporal pair；对 `E_FO/NoOp`，才是 eligible case × model rows。`min cell >= 15` 应该是对 estimand-specific support 说的，不应统一写成 model cell。

4. **Q4**  
   按当前 plan 的写法，`E_CTS` 和 `E_PCSG` 的相关估计更可能**偏高地反映 redundancy**，因为两者共享同一套 `P_logprob` traces 和大量 article difficulty 信号；但若 `E_PCSG` 真按 late-minus-early difference 计算，differencing 又会消掉一部分共同方差，所以这个 `r` 本身在现有定义下并不纯。若 pilot 出现 `r > 0.9`，我不建议“合并”为新 composite；最稳的 frozen action 应是：保留 `E_PCSG` 作为 confirmatory，`E_CTS` 改为 corroborative / progressive narrative anchor。原因很简单：`E_PCSG` 的 identification 更强，而“合并”会改变 estimand meaning。

5. **Q5**  
   会，尤其对 `P_predict` 家族。`baseline_confidence` 不是先验协变量，而是同一模型对同一 article 的 baseline output；它本身受 `cutoff exposure` 和 memorization channel 影响。把它放进主模型，等于在调整 treatment path 上的中介或 collider。对 `E_FO` / `E_NoOp` 这类 baseline-minus-perturbed delta，问题更严重，因为 baseline confidence 与 outcome 构造高度耦合。建议：`C3` 只做 mid-range subset sensitivity，或用外部 calibration score，别进 confirmatory 主模型。

6. **Q6**  
   按 frozen shortlist，`E_TDR` 不在 confirmatory family 里，所以**不受** confirmatory `Westfall-Young` family 覆盖。它应该单独按 exploratory sensitivity 汇报，给 effect size、simultaneous CI 或 bootstrap interval，但不能借 confirmatory FWER 的名义说它“也被 family control”。若以后想让 `β3` 花 alpha，就必须显式把它写进 Stage 2 confirmatory family，并重算 multiplicity。

7. **Q7**  
   目前 plan 没有预定义 equivalence bound，所以不能做正式“零效应”结论。对 `BL2` 当前只跑 `E_CMMD` 和 `E_PCSG`，我建议直接在 standardized estimand scale 上设 `Δ = 0.10 SD` 做 TOST；这比“< 25% of observed pre-cutoff effect”更干净，也更不 data-dependent。现有的 `25%` 规则可以保留为 operational gate，但那是 heuristic，不是 equivalence inference。

8. **Q8**  
   以当前 frozen rule 来看，**不允许**仅因 pilot `d < 0.1` 就降级 confirmatory。现在允许的 demotion 是 quality-gate based，不是 signal-based。若你们想把“弱信号 futility”也纳入 A3 adaptive design，必须在 Stage 1 现在就加一条 deterministic futility rule，例如基于 shrinkage-adjusted upper bound，而不是 `d̂ < 0.1` 这种点估计阈值。否则这会变成 pilot-driven alpha salvage，不属于当前 freeze。

## 5. 对 Stage 1 prereg skeleton 的建议

- 写一张“允许的 Stage 2 family state table”，至少枚举 `20`、`16(FO demoted)`、`16(NoOp demoted)`、`12(both demoted)`，以及是否发生 `CTS/PCSG regrouping`。
- 明写 `pilot cases are excluded from all Stage 2 confirmatory analyses`，并禁止 pooled pilot+main confirmatory fit。
- 把 `C1 regrouping` 从“open memo”改成 frozen tie-break：相关触发后保留更强 identification 的 estimand。
- 把 `C3` 改写为 sensitivity analysis，不进入 primary confirmatory mixed model。
- 给 `BL2` 增加 TOST bound 与 decision rule。
- 把 `B2` 改成 estimand-specific `n_eff` 定义，而不是统一的 model-cell 口径。
- 明写“除非现在预注册 futility rule，否则 Stage 2 不得因 pilot weak effect 降级 confirmatory”。
- 对“final prompt wording”加限制：只允许 deployment hardening，不允许改变 estimand semantics；否则需新 decision cycle。

## 6. 对 power simulation 脚本 spec 的建议

- 把 `null calibration` 和 `alternative power` 分成两步。先在各 retained-family 场景下校准 max-T critical values，再跑 power，不要每个 replicate 内再套一层临时 resampling。
- 在 raw design level 模拟，而不是只模拟 coefficient vector。case 是 resampling unit，必须整包保留该 case 的所有 model rows、paired traces、baseline/perturbation variants。
- `E_PCSG` 要单独保 temporal pair 结构；`E_CMMD` 要保 fleet exposure pattern；`E_FO/NoOp` 要保 eligibility mask。
- `Westfall-Young` 这层建议用 null-constrained mixed model 的 case-cluster parametric bootstrap，或 case-level cluster wild bootstrap；不要 naive permutation。
- 以 scenario table 输出 power，而不是单个数字。至少分别报 `20/16/12` family 的 `power_j`、`power(any temporal coefficient)`、以及 simultaneous CI width。
- planning effect 不要直接用 `β̂_pilot`，用 shrinkage-adjusted lower bound；否则 winner's curse 会把 Phase 8 power 估高。
- 报 Monte Carlo SE、seed、失败拟合率、以及每个 family 场景的 realized missingness。

## 7. 跨 lens 信号

这份 plan 统计上最值得保住的，其实正是它现在的“克制”：`20` 系数、`E_TDR` 不花 alpha、quality gate 先于 confirmatory 身份、pilot 主要做 admissibility 和 variance calibration。只要团队不把 `regrouping`、`prompt hardening`、`weak-signal demotion` 这些口子做成 memo-driven discretion，这个 two-stage 设计是能自洽的。相反，如果后续实际执行滑向 `80/64` family、把 `C3` 放进主模型、或拿 `BL2` 的 overlap-zero 当 equivalence，那就不是 infra 问题，而是 inference contract 失效。
