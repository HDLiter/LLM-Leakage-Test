# R-4a 方法论严谨度白板分析

## 阶段 1 白板结论

本阶段只使用了 kickoff 指定的阶段 1 输入。我的独立判断是:这个 benchmark 需要统计严谨度,但不需要把自己做成一篇统计方法论文。它的声明是“在这个语料、这个 fleet 上,泄露强度如何随案例因子变化”,所以最小可辩护方案应当围绕三件事:先把少数主张锁住,再给这些主张合理校正,最后把其余信号清楚标成辅助或探索。

### 1. confirmatory / exploratory 划分

**推荐:需要划分,但不建议把所有可测信号平铺成同等地位的 confirmatory family。**

划分的理由很直接:四层框架打开了很多自由度。一个因子可以接多个扰动,一个扰动可以接多个算子,最后又能组合出多个 estimand。如果不提前说哪些格子承担论文主张,读者无法区分“事先要检验的 characterization”与“看到数据后觉得有意思的模式”。

`K 个 estimand × M 个因子 = K·M 个系数`是一个自然的组织方式,但只能用于**主张层面的 family**,不能机械套到所有能算的东西上。每个进入 family 的格子都应该满足两个条件:第一,它确实在回答“哪些案例因子调节泄露”;第二,它本身足够像泄露证据,而不是只在检查测量栈是否稳定。

因此我建议用四层:

- **primary confirmatory**:直接承载论文主张的少数 estimand × 因子斜率。按目前阶段 1 信息,最小可辩护核心是 `E_CMMD`, `E_PCSG`, `E_FO` × 4 个因子,共 12 个系数。
- **auxiliary confirmatory / supporting**:帮助解释或校验主信号,但不单独支撑“泄露随因子变化”的结论。`E_CTS` 更像表面熟悉度/可预测性,`E_NoOp` 更像无关扰动下的脆弱性;它们可以固定报告,但不应和主信号享有完全相同的证据地位。
- **robustness / falsification**:同 cutoff 证伪对、能力协变量规格、模型子集、扰动质量门槛等。它们回答“主信号是不是由明显混杂造成”。
- **exploratory**:新增扰动、新增预测目标、稀疏 extraction、schema completion、post-hoc 分层等。

如果团队为了叙事简洁坚持 5 个 estimand × 4 因子 = 20 个系数,这仍然可辩护,但不是最小方案。20 的风险不是“数学上太多”,而是 `E_CTS` / `E_NoOp` 与 `E_CMMD` / `E_PCSG` / `E_FO` 的证据强度不同,平铺会让弱信号被误读成同等强度的泄露证据。

### 2. multiplicity 校正

**推荐:primary family 用 Holm 控制 family-wise α=0.05;辅助与探索只报告效应量和区间,不拿来做 confirmatory 命中数。**

这个 benchmark 不是在筛药,也不是在证明某个模型有无泄露。主输出应当是效应大小、方向、区间和跨信号一致性,而不是“显著/不显著”的表格。但只要论文会说“某些因子系统性调节泄露”,就需要防止从一堆格子里挑几个好看的。

我不建议无校正。那会让 12 或 20 个系数里的偶然命中太容易被写成故事。

我也不建议 Bonferroni 作为默认。它简单,但在这些 estimand 高度相关时过于钝,会把 characterization 论文推向“保守但信息少”。

我不建议把 Westfall-Young stepdown max-T 作为最小配置。它确实更会利用相关结构,但实现和解释成本高,容易变成 reviewer-driven ratchet。除非 pilot 显示 Holm 明显损失关键功效,否则没有必要把它设为主方案。

FDR 更适合探索性地图,不适合少数预先声明的 confirmatory 主张。这里 primary family 不大,用 Holm 更干净。

所以最小可辩护方案是:

- primary confirmatory 12 个系数:Holm-adjusted p 值 + 原始效应量 + 95% CI。
- 如果保留 20 个 primary 系数:仍用一个 family 做 Holm,不要按 estimand 拆成 5 个小 family 来降低惩罚。
- auxiliary / robustness:固定报告效应量和区间,只做解释和一致性判断。
- exploratory:可用 FDR 或完全不校正,但必须明确“不产生 confirmatory 结论”。

### 3. 预注册结构

**推荐:保留两阶段自适应预注册,但把它写成轻量的“pilot 后锁 main 分析计划”,不要包装成复杂制度。**

这个项目的测量栈本身是 benchmark 的贡献,而且有扰动合格率、模型覆盖不齐、case × model cutoff、logprob/predict split-tier 等工程事实。一次性预注册所有统计细节很可能是假精确:pilot 之前不知道哪些扰动能稳定跑、哪些 estimand 方差太大、哪些模型输出会塌。

因此两阶段不是过头,而是合理配置:

- pilot 前锁住研究问题、四层框架、候选因子/扰动/estimand、排除规则、哪些东西允许根据 pilot 修订。
- pilot 只用来检查测量栈、估计方差/协方差/合格率、决定 main run 的最终 family 和功效。
- main run 前锁最终分析计划;main run 才回答研究问题。

更轻的替代也可行:只做一次 main-run preregistration,外加 sealed test set 和完整 reporting。但考虑到这个项目有较多 researcher degrees of freedom,我不推荐完全不预注册。

关键不是注册形式多正式,而是要留下清楚时间线:pilot 看到了什么、因此改了什么、哪些改动是 pilot 前允许的、main run 开始前最终锁了什么。

### 4. 统计装置的必要性

**推荐:混合模型和功效模拟是 load-bearing;TOST 与 bootstrap 只在特定位置使用,不要全局铺开。**

混合模型防的是最核心的结构性错误:把大量 case × model × perturbation 观测当成独立样本。这里同一个案例会被多个模型看到,同一个模型会处理很多案例,扰动也在同一个原文上派生。如果不处理这种依赖,区间会太窄,显著性会虚高。最小配置是按 estimand 分开建模,至少处理 case 和 model 的聚类/随机截距;不要强行做一个所有 estimand 混在一起的巨型模型。

功效模拟防的是另一个现实问题:main run N=2,560 看起来大,但真正有效样本要扣掉扰动合格率、split-tier fleet、模型对数量、因子分布不均衡和聚类。解析公式很难靠谱。这里需要 Monte Carlo,但目标应简单:给定 pilot 估计的方差和缺失结构,看 main run 能否对 primary family 给出有用区间/合理检出率。它不应变成对每个 reviewer 假设都跑一套复杂仿真。

TOST 等价检验只在一种场景下 load-bearing:论文想把“没有明显差异”写成“足够接近零”。典型位置是同-cutoff 证伪对或负对照。如果只是主系数没有显著,不能用 TOST 来装饰。若使用 TOST,必须先定义一个有实际含义的“可忽略差异”界限;没有这个界限,TOST 反而增加术语负担。

bootstrap CI 的价值是给复杂派生量和非正态摘要一个稳健区间,尤其是 fleet-wide aggregation 或图里的 headline 指标。但如果混合模型已经给了聚类稳健区间,全局再 bootstrap 一遍不是必须。最小方案是:主系数用模型区间;复杂汇总图或不稳定派生量再用按 case / model 层级设计过的 bootstrap。

### 5. E_CMMD 识别问题

**推荐:E_CMMD 可以保留为 primary 信号,但必须降格表述为“cutoff-monotone prediction divergence / leakage-consistent behavioral signal”,不能单独叫作已经识别出的记忆。**

“跨模型分歧 ≠ 记忆”这个批评不能被完全统计消掉。不同模型可能因为能力、训练语料、系统 prompt、对金融任务的偏好不同而分歧。四道现有防御能把它从“明显不成立”推到“可作为人群层面行为信号”,但不能把它变成单独的因果识别。

逐项判断:

- **cutoff 单调性方向预测**很重要。若分歧只按 cutoff 方向走,比普通模型差异更像时间暴露信号。但新模型往往也更强,所以它不能单独闭合能力混杂。
- **模型能力协变量**有用,但只能 partial out 可观测能力。能力指标本身可能不准,也可能和 cutoff 高度绑定,因此它是缓解,不是解决。
- **同-cutoff 证伪对**是四道防御里最关键的一个。它能问“同样 cutoff、不同架构时还会不会出现类似分歧”。但一两个证伪对仍不足以证明所有 cutoff 差异都不是架构/训练分布差异。
- **人群层面聚合**能避免“某个模型是否泄露”的过度声明,但不会自动解决识别。群体平均也可能平均出能力差异。

所以 E_CMMD 的正确角色是三角测量中的一个行为通道。它应与 `E_PCSG` 这类 logprob cutoff 信号、`E_FO` 这类扰动抵抗信号一起读。若三者在同一因子方向上收敛,characterization 声明就可辩护;若只有 E_CMMD 显著,论文应写成“cutoff-consistent behavioral divergence”,而不是“证明记忆”。

一个命名风险也应提前处理:如果 E_CMMD 全名继续叫 Cross-Model **Memorization** Disagreement,读者会自然理解为“分歧已经等于记忆”。更稳妥的正文表述是 Cross-Model Cutoff-Monotone Disagreement,把 memorization 留给多信号收敛后的解释层。

## 阶段 2 对照

阶段 2 读到的当前设计比阶段 1 的最小方案更重。它的优点是识别防线完整、pilot 约束清楚;主要问题是把一些“应固定报告的辅助信号”也拉进了同一个 confirmatory alpha family,然后为了保护这个更大的 family 又继续加 Westfall-Young、复杂 power、gate 规则和 reviewer caveat。下面按当前严谨度成分逐项给 verdict。

### 1. `S20 = 5 estimand × 4 factor = 20` 作为唯一 confirmatory family

**Verdict:过度(drop or simplify)。**

阶段 1 独立结论得到的是 `E_CMMD / E_PCSG / E_FO` × 4 因子的 12 系数 primary family。`E_CTS` 和 `E_NoOp` 都值得测,但它们的证据角色不同:前者是表面熟悉度/文献锚,后者是 template-brittleness / robustness 信号。把它们与 `E_PCSG`、`E_FO` 平铺成同一等级,会让读者误以为每个格子都同样是在测“泄露”。

建议简化为:

- `S12 primary`: `E_CMMD`, `E_PCSG`, `E_FO` × 4 因子。
- `fixed supporting`: `E_CTS`, `E_NoOp` × 4 因子,固定报告效应量和区间,不计入 primary 命中。
- 如果团队坚持保留 `S20`,proposal 里必须明说 `E_CTS` / `E_NoOp` 是不同证据等级,不要只靠表格脚注处理。

### 2. `E_FO` 无条件 confirmatory

**Verdict:必要(keep)。**

`E_FO` 是最像“模型不服从可见反事实、疑似抓住记忆结果”的行为证据。当前把旧的 baseline-delta non-degeneracy gate 移除是对的;用信号大小决定是否分析这个信号,会把最强覆盖型记忆误判成失败。保留人工审计 gate,删除行为幅度 gate,是正确方向。

### 3. `E_NoOp` 无条件 confirmatory

**Verdict:过度(drop or simplify)。**

当前 plan 自己已经写明 `E_NoOp` 是 robustness / template-brittleness signal,不是直接 memorization claim。这与“无条件进入 20 系数 confirmatory family”冲突。最小可辩护方案应把它固定为 supporting robustness。若一定保留 primary,必须加非常强的 claim caveat,并最好增加 `C_NoOp_placebo`;否则它很容易被批评为 prompt fragility。

### 4. `E_CTS` 与 `E_PCSG` 同时 primary,并用相关性触发 regrouping

**Verdict:持平(retain with caveat)。**

测两者是合理的:同一套 logprob trace,边际成本低,`E_CTS` 也有 Min-K++ 文献锚。但阶段 1 的最小判断是 `E_PCSG` 的识别更强,`E_CTS` 应默认 auxiliary。当前“若 `E_CTS/E_PCSG` 高相关就保 `E_PCSG`、降 `E_CTS`”是可接受的备选,但它把一个本可 upfront 简化的问题推给 pilot。

建议:若采用 `S12`,直接把 `E_CTS` 放 supporting;若坚持 `S20`,保留 deterministic regrouping,不要临时发明 composite。

### 5. Westfall-Young stepdown max-T over 20

**Verdict:过度(drop or simplify)。**

Westfall-Young 是有效方法,但不是这个 benchmark 的最小必要配置。它提高了实现和解释成本,并把 power simulation 也绑到更复杂的流程上。对于 12 或 20 个预先声明系数,Holm FWER `α=0.05` 已经足够可辩护,也更容易向统计外读者解释。

建议:

- primary `S12`:Holm over 12。
- 若坚持 `S20`:Holm over 20 仍可辩护。
- Westfall-Young 只作为可选 sensitivity,不作为主 prereg 负担。

### 6. 两阶段自适应预注册与 evidence package

**Verdict:必要(keep)。**

阶段 1 也独立得到同一结论。这个项目的 pilot 不是偷看主结果,而是在验证测量栈、估方差、看 eligibility 和 covariance。当前要求 Stage 1 prereg、manifest hash、commit SHA、Stage 2 main-run lock 是合适的。

需要修的不是方向,而是复杂度和一致性:plan 里同时出现 “S20 only” 与 “S20/S16/S12 legal states” 的旧文本,应清掉。Stage 2 允许改什么、禁止改什么,必须比 family-state 历史更清楚。

### 7. pilot cases 排除出 Stage 2 confirmatory analysis

**Verdict:必要(keep)。**

这是真正 load-bearing 的 prereg 规则。pilot 用来调测量与功效,main run 才回答研究问题;两者样本必须隔离。

### 8. per-estimand analysis unit / scalar score freeze

**Verdict:必要(keep)。**

阶段 1 说“不要做一个所有 estimand 混在一起的巨型模型”;当前修订后的 §8.1A 正好在补这个洞。`E_CTS=case×model`, `E_PCSG=case×pair`, `E_CMMD=case-level fleet aggregate`, `E_FO/E_NoOp=case×model eligible subset` 这类冻结是必须的。否则 power、n_eff、correlation matrix 都会变成 apples-to-oranges。

### 9. 混合模型 / case-cluster bootstrap 的估计结构

**Verdict:必要(keep,但保持简单)。**

case、model、pair 的依赖结构是真实存在的。当前按 estimand 分开建模是正确方向。不要退回统一 `Y_ijm`,也不要把所有随机斜率都堆进去。对 `E_CMMD`,既然已经聚合成 case-level score,就不应再套 model random effect;用 case-level inference / bootstrap 更一致。

### 10. `baseline_confidence` 退出 primary model,只做 sensitivity

**Verdict:必要(keep)。**

这与阶段 1 的“不要用协变量吃掉真实泄露路径”一致。baseline confidence 很可能是记忆强度的表现,不是干净混杂。当前把它降为 `P_predict` family sensitivity 是正确的。

### 11. `model_capability` covariate

**Verdict:持平(retain with caveat)。**

它有用,但只能缓解“新模型更强”这个批评,不能证明 cutoff effect 已被识别。proposal 应把它写成 sensitivity / robustness,不要写成“控制了能力所以剩下就是泄露”。在模型数量有限时,解释 `β4` 本身没有太大价值;看 primary coefficient 是否稳定就够了。

### 12. BL2 post-cutoff negative control + TOST/SESOI

**Verdict:必要(keep,但限定使用范围)。**

TOST 在这里是正当的:如果论文要说“post-cutoff 控制应近零”,就不能把普通不显著当作等价。`SESOI=0.15`、CI 完全落在 `[-0.15,+0.15]` 内,比旧的 “CI overlap zero” 强很多。

但 TOST 只应服务 BL2 / 负对照,不要扩散到所有主系数。另一个需要清理的点是样本数:阶段 1 背景和 proposal 写 pilot 是 `80 + 700`,而 phase7 plan 仍有 `80 + 350` 默认、700 可扩展的旧结构。若 BL2 是 Phase 8 gate,700 比 350 更符合它的 evidentiary role。

### 13. same-cutoff falsification pair / early-warning ratio

**Verdict:必要(keep with caveat)。**

这道防御必须保留,但它不是闭合识别的银弹。GLM-4-9B ↔ GPT-4.1 只能当 architecture-noise early warning,不能写成“已排除架构差异”。当前 ratio > 0.5 后加强 caveat,而不是自动 fail,是合理的。

### 14. BL1 metadata / text-light challenger

**Verdict:必要(keep)。**

它不直接证明记忆,但能防一个很现实的批评:是不是这些 factor 本来就能用元数据或简单文本模式预测出来。保留 grouped-CV-by-case 是必要的,否则同一文章派生行会泄进不同 fold。

### 15. effective sample-size matrix `min cell >= 15`

**Verdict:持平(retain with caveat)。**

作为 pilot 生存线可以保留,但它不是 interaction identification 的充分条件。case-level factor 不会因为有 14 个模型就自动变成 14 倍独立样本。应加报 informative cutoff window support、FO eligibility support、pair-specific support。`15` 只能叫 guardrail,不能叫 power guarantee。

### 16. scenario-based main-run power simulation

**Verdict:必要(keep,但解除 Westfall-Young 绑定)。**

功效模拟是 load-bearing,因为 split-tier fleet、eligibility、case/model 聚类和 pilot 过度加权都会让闭式公式很脆。当前要求 reweighting、shrinkage、realized missingness、Monte Carlo SE,方向正确。

但如果主 multiplicity 简化为 Holm,simulation 就不必围绕 Westfall-Young 重建一整套 max-T。核心仍是模拟 planned model、planned family、planned missingness,然后按 chosen correction 估计能否给出有用结果。

### 17. bootstrap

**Verdict:持平(retain with caveat)。**

对 `E_CMMD` case-level aggregate、BL2 post-cutoff interval、correlation stability,bootstrap 是合适的。它不应变成“所有东西都 bootstrap 一遍”的默认仪式。主系数若已由混合模型给出聚类/层级区间,bootstrap 可作为关键图和复杂派生量的补充。

### 18. Path E cutoff probe / cutoff-observed evidence

**Verdict:必要(keep with caveat)。**

cutoff 是整个 temporal route 的物理基础,白盒 cutoff 能经验探针就应做。当前 lens_B 指出实现细节有 bug 和月度冲击风险,这些要修。但即使 Path E 通过,也只能加强 cutoff assumption,不能把黑盒 cutoff 或 E_CMMD 的能力混杂一并解决。

### 19. reserve promotion 到 confirmatory,特别是 `E_extract → 24 coefficients`

**Verdict:过度(drop or simplify)。**

如果主 family 已经有 12 或 20 个系数,在 pilot 后把 `E_extract` 升成 24 系数 confirmatory 会重新打开 alpha scope,且 extraction hit rate 稀疏、机制也不同。最小可辩护方案是:reserve 最多升为 main-text exploratory;若真的强到值得 confirmatory,开新 decision memo / 新 prereg,不要自动塞进本次 main family。

### 20. Phase 8 GO gate 要求 temporal route + perturbation route 都有足够 power

**Verdict:必要(keep with caveat)。**

这个 gate 的精神是对的:只靠一个 temporal route 或一个 perturbation route 都不足以支撑多信号 characterization。若主方案改成 `S12 + Holm`,gate 也相应改成“至少一个 temporal primary (`E_CMMD` or `E_PCSG`) 和 `E_FO` 有可用 power / 区间精度”。不要把 `E_NoOp` 作为 perturbation-route 的唯一达标信号,因为它不是直接记忆证据。

## 最终综合推荐

我建议把方法论框架收敛成下面这个最小可辩护版本:

1. **Primary family = 12 系数。** `E_CMMD`, `E_PCSG`, `E_FO` × 4 个 confirmatory 因子。主张只从这 12 个格子来。
2. **Supporting fixed report。** `E_CTS` 和 `E_NoOp` 固定报告效应量、95% CI、方向一致性,但不计入 primary 命中。`E_CTS` 是 surface familiarity / literature anchor;`E_NoOp` 是 robustness/template-brittleness。
3. **Multiplicity。** primary 12 系数用 Holm FWER `α=0.05`;所有格子仍报告原始效应量和区间。探索性结果不产生 confirmatory 结论。
4. **Pre-registration。** 保留两阶段:pilot 前锁 Stage 1,main run 前锁 Stage 2。pilot 样本不进 main confirmatory。
5. **模型。** 按 estimand 分开建模;处理 case/model/pair 聚类;`E_CMMD` 若是 case-level aggregate,就按 case-level 做 inference。
6. **Power。** pilot 后做 scenario-based MC power / interval precision simulation,但不必绑定 Westfall-Young。必须考虑 eligibility、missingness、split-tier fleet、pilot-to-main reweighting 和 conservative shrinkage。
7. **负对照。** BL2 用 TOST/SESOI,同-cutoff pair 用 early-warning ratio。二者是防御,不是证明。
8. **E_CMMD 表述。** 改成 cutoff-monotone prediction divergence / leakage-consistent behavioral signal。只有与 `E_PCSG` / `E_FO` 收敛时,才上升为 memorization characterization。

如果用户决定不动冻结设计,`S20 + Westfall-Young` 也不是错,但它是更重、更 reviewer-driven 的方案。它的代价是:power 需求更高、implementation 更难、解释更容易混淆证据等级。我的推荐是现在趁 R-4a 重开,把它降回 `S12 primary + supporting fixed report`。

## 对下游的影响

### R-1e 因子

Primary 因子数量应维持 4 个。每新增 1 个 primary 因子,在 `S12` 下就新增 3 个主系数;若回到 `S20`,就新增 5 个主系数。R-1e 不应再把相近因子拆成多个 primary 维度来“都保留”。可放进 supporting / covariate 的,不要挤进 primary factor list。

### R-2 扰动

Confirmatory 扰动容量只应给 `C_FO`。`C_NoOp` 固定做 robustness/supporting;`C_SR`, `C_anon`, `C_temporal`, `C_ADG` 留 exploratory 或 sensitivity。若想让另一个扰动进 primary,必须从 `E_CMMD/E_PCSG/E_FO` 里替换掉一个,而不是扩 family。

### R-3 负对照

BL2 和同-cutoff early-warning 是 load-bearing。`C_NoOp_placebo` 可作为 supporting diagnostic,但不应变成新的 confirmatory gate。BL3 非金融中文新闻仍可 stretch,不应阻断主流程。

### R-5 采样与过滤

采样必须服务 `S12` 的有效样本:4 因子 × 3 primary estimands,尤其是 informative cutoff windows、PCSG tokenizer/pair eligibility、FO slotability。过滤器不能为了让信号更干净而删掉反直觉/难预测案例,除非它们是 predeclared population restriction;否则会把 benchmark 从 characterization 变成容易样本 stress test。

### R-6 预测目标与 ground truth

当前 `P_predict` 名字里的 “alpha prediction” 与实际机制有名实缺口:它只判方向和信心,不算 alpha、不用持有期收益。R-6 可以把真实收益用于 difficulty covariate、过滤审计或 auxiliary validation,但不要无成本加成新的 confirmatory estimand。任何“真实收益/alpha ground truth”主 estimand 都会再乘以 4 个因子,需要替换现有 primary 格子或另开研究问题。

## 留给用户拍板的开放点

1. **是否把冻结 `S20` 改成 `S12 primary + E_CTS/E_NoOp supporting`。** 我的明确推荐是改。
2. **若不改 `S20`,是否至少把 Westfall-Young 简化为 Holm。** 我的推荐是 Holm;Westfall-Young 可留 sensitivity。
3. **BL2 post-cutoff 样本到底按 350 还是 700 执行。** 若 BL2 是 Phase 8 gate,推荐 700,并清理 phase7 plan 与 proposal 的不一致。
4. **`E_NoOp` 是否愿意降出 primary。** 我的推荐是降为 supporting;若保留 primary,正文必须把它写成 brittleness 而不是直接 memorization。
