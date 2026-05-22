# Confirmatory 多因子研究中的因子非冗余 / 共线性诊断：业界最小标准

日期：2026-05-20  
场景：4 个连续曝光因子一起进入 mixed-effects 回归，pilot 约 80 个 pre-cutoff cases。

## 1. 业界公认标准是什么？

先给结论：在 confirmatory 回归里，没有一个被所有领域强制采用的“共线性诊断套件”。公认的最低做法是：在最终预注册/冻结的固定效应设计矩阵上，报告能反映系数方差膨胀的诊断，通常是 VIF 或 tolerance；再用 predictor 相关矩阵说明变量之间的原始重叠。condition index / condition number 是经典但更偏扩展的全局矩阵诊断，不是最小必报项。

代表性方法学来源：

- Belsley, Kuh, and Welsch 的经典诊断框架把共线性定义为设计矩阵的 ill-conditioning，并提出 condition index 和 variance-decomposition proportions 来识别“哪个线性组合造成弱识别”。见 David A. Belsley, Edwin Kuh, Roy E. Welsch, *Regression Diagnostics: Identifying Influential Data and Sources of Collinearity*, Wiley, 1980, DOI: https://doi.org/10.1002/0471725153。
- Belsley 后续专著进一步强调“weak data / conditioning”是数据相对于模型是否能支撑估计的问题，而不是一个单纯的假设检验。见 David A. Belsley, *Conditioning Diagnostics: Collinearity and Weak Data in Regression*, Wiley, 1991, ISBN 9780471528890, WorldCat/Google Books: https://search.worldcat.org/title/481787715。
- VIF/tolerance 是应用回归中最常见的最小报告指标，因为它直接对应某个回归系数的方差或标准误被其他 predictors 线性解释后放大了多少。VIF 早期来源可追溯到 Marquardt 的 ridge/广义逆讨论：Donald W. Marquardt, “Generalized Inverses, Ridge Regression, Biased Linear Estimation, and Nonlinear Estimation,” *Technometrics*, 1970, DOI: https://doi.org/10.1080/00401706.1970.10488699。
- 在生态/应用观察性研究的数据探索协议中，Zuur, Ieno, and Elphick 把共线性作为建模前应检查的问题，常用工具包括 scatterplots、相关系数、VIF 和 PCA；其中 VIF/相关矩阵属于常规轻量做法。见 Alain F. Zuur, Elena N. Ieno, Chris S. Elphick, “A protocol for data exploration to avoid common statistical problems,” *Methods in Ecology and Evolution*, 2010, DOI: https://doi.org/10.1111/j.2041-210X.2009.00001.x。
- 对多自由度项，Fox and Monette 提出 GVIF；但本场景 4 个连续 1-df 线性项时，GVIF 退化为普通 VIF。见 John Fox and Georges Monette, “Generalized Collinearity Diagnostics,” *Journal of the American Statistical Association*, 1992, DOI: https://doi.org/10.1080/01621459.1992.10475190。

因此，“业界最小但站得住”的标准不是 5 项，而是固定效应层面的 VIF/tolerance；相关矩阵是解释性补充，通常也值得附上。

## 2. VIF、condition number、相关矩阵、偏相关、tolerance 的关系

### 基本关系

对第 \(j\) 个 predictor，令 \(R_j^2\) 是把 \(X_j\) 用其他 predictors 回归得到的辅助回归 \(R^2\)。则：

\[
\mathrm{VIF}_j = \frac{1}{1 - R_j^2}
\]

\[
\mathrm{tolerance}_j = 1 - R_j^2 = \frac{1}{\mathrm{VIF}_j}
\]

所以 VIF 和 tolerance 是完全等价的信息，只需报一个。VIF 的平方根是标准误膨胀因子：\(\sqrt{\mathrm{VIF}}\)。例如 VIF=5 表示 coefficient 方差约放大 5 倍，标准误约放大 2.24 倍；VIF=10 表示标准误约放大 3.16 倍。

相关矩阵只看 pairwise marginal associations。它能发现两个变量几乎重复，但不能保证没有多变量线性组合问题。例如单个 pairwise correlation 都不极端时，多个变量的线性组合仍可能近似预测另一个变量。因此，相关矩阵不能替代 VIF；它是解释“哪些 proxy 概念上重叠”的透明材料。

偏相关 / residual correlation 是把两个 predictors 各自对其他 predictors residualize 后的相关。对标准化 predictor 相关矩阵 \(R\)，令 precision matrix \(P=R^{-1}\)，则：

\[
r_{jk \cdot -jk} = - \frac{P_{jk}}{\sqrt{P_{jj}P_{kk}}}
\]

而 \(P_{jj}\) 就对应 \(X_j\) 的 VIF。因此偏相关和 VIF 来自同一个 predictor 相关矩阵的逆矩阵，但回答的问题不同：VIF 问“这个系数的方差被整体共线性放大多少”；偏相关问“两个 predictors 在控制其他 predictors 后还剩多少线性关联”。confirmatory 回归的共线性报告通常报 VIF/tolerance，而不是一整套偏相关。

condition number / condition index 是全局矩阵诊断。Belsley, Kuh, and Welsch 基于 scaled \(X'X\) 的特征值定义 condition index：

\[
\kappa_i = \sqrt{\lambda_{\max}/\lambda_i}
\]

最大 condition index 即常说的 condition number。它能发现全局 ill-conditioning，但要和 variance-decomposition proportions 一起看才知道哪些系数受影响。单独报 condition number 容易过度解读，且受中心化、缩放、截距处理影响。

### 哪些冗余？

- VIF 与 tolerance：完全冗余，二选一。
- 对 1-df 连续项，GVIF = VIF；scaled/adjusted GVIF 通常是 \(GVIF^{1/(2df)}\)，df=1 时即 \(\sqrt{VIF}\)，和标准误膨胀因子同义。
- 4x4 相关矩阵与“全 6 对 marginal correlations”：同一件事。矩阵更清楚。
- 偏相关矩阵与 VIF 都来自 predictor correlation matrix 的逆矩阵。它们不是数值等同，但作为“最小共线性诊断”信息重叠，偏相关不是常规必报。
- condition number 与 VIF 都来自固定效应设计矩阵。condition number 是全局近奇异性，VIF 是 coefficient-specific variance inflation。二者互补，但在 4 个连续 predictors 的小模型中，VIF 已经是更可解释的最小诊断。

### 阈值与争议

常见经验阈值：

- VIF > 10 或 tolerance < 0.10：传统“严重共线性”经验线。常见于应用回归教材和软件说明。O'Brien 专门批评了这个 rule of 10 被机械使用。见 Robert M. O'Brien, “A Caution Regarding Rules of Thumb for Variance Inflation Factors,” *Quality & Quantity*, 2007, DOI: https://doi.org/10.1007/s11135-006-9018-6。
- VIF > 5 或 tolerance < 0.20：更保守的应用线。Menard 在 logistic regression 诊断中常被引用为 tolerance < .20 可能有问题、< .10 严重。见 Scott Menard, *Applied Logistic Regression Analysis*, 2nd ed., Sage, 2002, DOI: https://doi.org/10.4135/9781412983433。
- ISLR 等现代教材也把 5 或 10 作为经验阈值，而不是统计检验。见 Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, *An Introduction to Statistical Learning with Applications in R*, 2nd ed., Springer, 2021, DOI: https://doi.org/10.1007/978-1-0716-1418-1。
- condition index > 30 常被归入强 near-dependency；10-30 常被视为中等；30-100 强；>100 很强。这来自 Belsley 系列 condition diagnostics：Belsley, Kuh, and Welsch 1980, DOI: https://doi.org/10.1002/0471725153；Belsley 1991, ISBN 9780471528890。

争议点很重要：这些阈值不是显著性检验，也不是跨研究固定真理。O'Brien 2007 指出 VIF 阈值必须结合样本量、误差方差、效应大小、研究目的解释；Craney and Surles 也明确提出 VIF cutoff 是 model-dependent。见 Trevor A. Craney and James G. Surles, “Model-Dependent Variance Inflation Factor Cutoff Values,” *Quality Engineering*, 2002, DOI: https://doi.org/10.1081/QEN-120001878。Mason and Perreault 的仿真研究同样指出 collinearity 的危害不能脱离 power、sample size、noise 与研究目标单独判断。见 Charlotte H. Mason and William D. Perreault Jr., “Collinearity, Power, and Interpretation of Multiple Regression Analysis,” *Journal of Marketing Research*, 1991, DOI: https://doi.org/10.1177/002224379102800302。

## 3. Mixed-effects 模型场景有什么不同？

核心区别：固定效应 predictors 的共线性仍然是固定效应设计矩阵 \(X\) 的问题；mixed model 另外还有随机效应结构 \(Z\)、方差分量、优化收敛和边界估计问题。两者相关但不等同。

对 mixed-effects 回归，最小共线性诊断应针对固定效应项：

- 如果 4 个曝光因子都是 1-df 连续固定效应，普通 VIF 就足够。
- 如果模型有多水平分类项、样条、交互等多自由度 term，才需要 GVIF 或 adjusted GVIF。Fox and Monette 1992 是 GVIF 的标准出处，DOI: https://doi.org/10.1080/01621459.1992.10475190。
- R 的 `car::vif()` 和 `performance::check_collinearity()` 对 `merMod`/mixed-model 类对象支持 VIF/GVIF，说明它在实践中已被当作 mixed model 固定效应共线性检查。`car::vif` 文档： https://search.r-project.org/CRAN/refmans/car/html/vif.html；`performance::check_collinearity` 文档： https://easystats.github.io/performance/reference/check_collinearity.html。

mixed-model singular fit / convergence diagnostics 不应归入“4 个因子非冗余”的最小共线性诊断。它们属于模型拟合、随机效应结构可识别性、方差分量边界问题：

- Bates, Maechler, Bolker, and Walker 的 lme4 论文把 LMM 估计写成 fixed-effects、random-effects 和 constrained optimization 的联合问题。见 “Fitting Linear Mixed-Effects Models Using lme4,” *Journal of Statistical Software*, 2015, DOI: https://doi.org/10.18637/jss.v067.i01；arXiv: https://arxiv.org/abs/1406.5823。
- lme4 `isSingular()` 文档定义 singular fit 为随机效应方差-协方差矩阵低秩或边界估计，说明它主要反映 random-effects covariance structure 的问题，而不是固定效应 predictors 互相冗余。文档： https://lme4.github.io/lme4/reference/isSingular.html。
- Bates, Kliegl, Vasishth, and Baayen 指出 maximal mixed models 的不收敛常来自数据无法支撑过复杂 random-effects 结构。见 “Parsimonious Mixed Models,” 2015, arXiv: https://arxiv.org/abs/1506.04967。
- confirmatory mixed models 的随机效应结构本身有一套独立争论：Barr et al. 主张 maximal random-effects structure，Matuschek et al. 强调 type I error 与 power 的权衡。见 Dale J. Barr et al., “Random effects structure for confirmatory hypothesis testing: Keep it maximal,” *Journal of Memory and Language*, 2013, DOI: https://doi.org/10.1016/j.jml.2012.11.001；Hannes Matuschek et al., “Balancing Type I error and power in linear mixed models,” *Journal of Memory and Language*, 2017, DOI: https://doi.org/10.1016/j.jml.2017.01.001。

所以：VIF/GVIF 是共线性诊断；singular fit/convergence 是模型拟合诊断。二者都应检查，但不应被包装成同一个“因子非冗余”套件。

## 4. 小样本 n≈80 的影响

n≈80、4 个 focal continuous predictors 的情况下，VIF 本身可以计算且易解释；问题不在“算不算得出来”，而在样本相关结构的稳定性与 inferential precision。

小样本下要注意：

- 样本相关矩阵不稳定。相关系数的 Fisher z 标准误约为 \(1/\sqrt{n-3}\)，n=80 时约 0.114，因此中等到偏高相关的置信区间仍不窄。相关矩阵应被看作 pilot 中的设计/可识别性证据，而不是总体结构的精确估计。
- VIF 是 \(R_j^2\) 的非线性函数。当某个 \(R_j^2\) 接近 1 时，小的采样波动会被放大。因此小样本下不宜把 VIF=4.9 与 VIF=5.1 当成实质性差异。
- condition number 依赖最小特征值，最小特征值在小样本、弱支撑、近奇异时特别敏感。作为“扩展诊断”可以看，但不适合作为 pilot 冻结前的硬门槛。
- partial/residual correlations 在 n=80、只 4 个 predictors 时可算，但并不比 VIF更稳；如果再做 6 个偏相关和阈值判断，会制造多重解释负担。
- mixed model 的 convergence/singularity 在小样本、随机效应 levels 少、random slopes 多时更容易发生，但那是随机效应结构是否被数据支撑的问题。它不能替代 fixed-effect VIF。

文献支撑：Mason and Perreault 1991 说明 collinearity 的实际危害必须和 sample size、noise、effect size、power 一起评估，DOI: https://doi.org/10.1177/002224379102800302。O'Brien 2007 进一步批评固定 VIF 阈值脱离样本量和模型语境，DOI: https://doi.org/10.1007/s11135-006-9018-6。Babyak 关于 overfitting 的应用提醒也适用：小样本中不要让诊断套件变成数据驱动模型选择。见 Michael A. Babyak, “What you see may not be what you get,” *Psychosomatic Medicine*, 2004, DOI: https://doi.org/10.1097/01.psy.0000127692.23278.a9。

## 5. 判断：v0.3 是否 over-engineering？“VIF + 相关矩阵”能否再砍？

v0.3 的 5 项：

1. 全 6 对 marginal Spearman  
2. partial/residual correlations  
3. scaled GVIF  
4. condition number  
5. mixed-model singularity/convergence diagnostics

判断：作为“因子非冗余 / fixed-effect collinearity”最小标准，v0.3 明显 over-engineering。大约有 2 到 3 项不是必要项，且第 5 项属于另一类诊断。

逐项判断：

- 全 6 对 marginal Spearman：如果以矩阵形式呈现，就是一个 4x4 相关矩阵。可保留为透明描述。若模型用 log-transformed continuous covariates 线性进入回归，Pearson correlation on transformed covariates 更贴近线性共线性；Spearman 可作为 robust/descriptive 版本，但不是必需。
- partial/residual correlations：不建议作为最小标准。它与 VIF 共享同一 predictor correlation matrix 的信息来源，且解释负担大。
- scaled GVIF：本场景 4 个连续 1-df 因子时冗余。普通 VIF 更直接；adjusted GVIF 只是标准误膨胀因子。
- condition number：经典但不是最小必报项。若 VIF 已低且相关矩阵透明，condition number 对本场景增量有限。可作为内部 sanity check，不必写进 confirmatory 报告。
- singularity/convergence：应保留在 mixed-model fit diagnostics 章节，但不要归入因子非冗余。

“VIF + 4x4 相关矩阵”两件套是恰当的最小可辩护做法。若必须再砍，应该砍成“VIF/tolerance 作为正式诊断，相关矩阵放补充材料”；不建议只报相关矩阵。原因是相关矩阵只能看 pairwise redundancy，不能回答“模型是否分得开各自 conditional effects”。VIF 才直接对应 coefficient-level variance inflation。

## 6. 发现共线时的业界补救

业界补救不是“看到高 VIF 就机械删变量”。标准处理顺序应是：

1. 先判断是否 rank deficiency / aliasing。如果是完全共线，模型无法估计，必须改变量定义、删掉完全重复项，或合并项。
2. 如果是高但非完全共线，先回到理论：这些因子是否本来就是同一 latent construct 的多个 proxy？如果是，合并为 composite/index、latent factor、PCA/因子分数可能比硬拆 4 个效应更诚实。Dormann et al. 对 collinearity 处理方法做了系统综述，强调生态/领域知识和预分析变量选择的重要性。见 Carsten F. Dormann et al., “Collinearity: a review of methods to deal with it and a simulation study evaluating their performance,” *Ecography*, 2013, DOI: https://doi.org/10.1111/j.1600-0587.2012.07348.x。
3. 如果四个因子是 confirmatory estimands，不要仅因 VIF 偏高就删掉理论关键变量。可以保留并明确解释为 conditional effects with limited precision，报告更宽的 CI，并做预先指定 sensitivity analyses。
4. 如果 pilot 还没冻结，最干净的补救是设计层面的：在不看 outcome 的前提下，增加/替换样本以填充 predictor joint support，例如按 exposure 维度或关键组合做 stratified/targeted sampling。这比事后在模型中“修共线”更好。但这必须写入 sampling plan，避免 outcome-driven selection。
5. 不建议把连续变量 rebin/dichotomize 当作共线性补救。分箱会损失信息、降低 power、改变估计目标，并可能制造人为阈值。见 Patrick Royston, Douglas G. Altman, Willi Sauerbrei, “Dichotomizing continuous predictors in multiple regression: a bad idea,” *Statistics in Medicine*, 2006, DOI: https://doi.org/10.1002/sim.2331。
6. 不建议默认 residualization/orthogonalization 来“消除”共线性。它会改变 estimand，且结果依赖残差化顺序；在 focal predictors 之间 residualize 尤其会把共享曝光解释权人为分配给先进入的变量。见 Lee H. Wurm and Sebastiano A. Fisicaro, “What residualizing predictors in regression analyses does (and what it does not do),” *Journal of Memory and Language*, 2014, DOI: https://doi.org/10.1016/j.jml.2013.12.003；Richard York, “Residualization is not the answer: Rethinking how to address multicollinearity,” *Social Science Research*, 2012, DOI: https://doi.org/10.1016/j.ssresearch.2012.05.014。
7. Ridge/penalization/PCR/PLS 可用于 prediction 或 shrinkage，但在 confirmatory causal/associational inference 中会改变系数解释或引入 bias-variance tradeoff；若使用，需要作为单独的预注册敏感性或预测分析，而不是替代主回归。

## 7. 本场景的最小但站得住推荐做法

针对 4 个相关连续曝光因子、mixed-effects、pilot n≈80、confirmatory 的 LLM 训练数据泄露研究，推荐如下。

### 最小正式诊断

报告固定效应设计矩阵上的 VIF table：

- 对 4 个最终进入 mixed model 的 transformed/scaled continuous exposure terms 计算 VIF。
- 同表给 tolerance 或不单独给；若给，注明 tolerance = 1/VIF。
- 报 max VIF 和每个 factor 的 VIF。
- 阈值写成经验解释，不写成显著性检验：
  - VIF <= 5：可作为 pilot 中“没有明显无法分离”的主标准。
  - 5 < VIF < 10：提示实质共线性，仍可保留 confirmatory predictors，但需在解释中承认 individual effects 精度有限，并做预指定 sensitivity。
  - VIF >= 10 或 rank deficiency：不应声称四个效应在 pilot 中可清楚分离；需合并、重定义、重新抽样扩展 joint support，或把结论降级为 shared exposure construct。

这个选择可由 O'Brien 2007、Craney and Surles 2002、Mason and Perreault 1991 支撑：阈值是经验线，不能机械化；但 VIF<=5 作为 small-pilot 的保守绿灯是可辩护的。

### 最小透明材料

附一个 4x4 predictor correlation matrix：

- 首选 Pearson correlation on model-entered transformed covariates，因为共线性是线性设计矩阵问题。
- 如果 reviewer/领域直觉更关心 monotone proxy redundancy，可在同一矩阵或 supplement 中给 Spearman；但不要把 Pearson + Spearman + partial correlations 都列为必需。
- 解释规则：|r| >= .80 或 .85 表示变量定义可能重叠，需要理论说明；|r| >= .90 基本应视为红灯，除非 VIF 和模型目标有特殊理由。

### mixed-model fit diagnostics 的位置

另设一段“model fitting diagnostics”，报告：

- convergence status；
- singular fit / random-effects variance boundary；
- random-effects structure 是否被 pilot data 支撑。

但这段不要作为“因子非冗余”证据。它是 mixed-model 可估计性和随机效应结构问题。Bates et al. 2015 JSS、Bates et al. 2015 arXiv、Barr et al. 2013、Matuschek et al. 2017 支撑这一分离。

### 预注册/冻结 pilot 前的决策规则

建议写成：

> Before freezing the pilot sample and without inspecting outcome associations, we will assess fixed-effect collinearity among the four exposure factors using VIFs computed on the final transformed covariates and a 4x4 predictor correlation matrix. We will treat max VIF <= 5 as acceptable evidence that the pilot design has no severe fixed-effect collinearity. Values between 5 and 10 will be reported as moderate collinearity and will trigger pre-specified sensitivity analyses. VIF >= 10, rank deficiency, or pairwise |r| >= .90 will be treated as evidence that the pilot data do not support separate estimation of all four exposure effects; we will then revise the sampling/design support or combine/redefine the affected factors before confirmatory analysis.

### 对 v0.3 和精简版的最终判断

- v0.3 的 5 项套件相对业界最小标准约过度 2 到 3 项：partial/residual correlations、scaled GVIF、condition number 对这个 4 个 1-df 连续因子场景不是最小必需；singularity/convergence 属于另一类 mixed-model fit diagnostics。
- “VIF + 4x4 相关矩阵”是最合适的最终版本。
- 若论文篇幅极紧，可正文只报 VIF/tolerance 与 max VIF，把相关矩阵放 supplement。只报相关矩阵则偏弱，不足以回答“conditional effects 是否可分离”。

## 参考文献

- Babyak, M. A. (2004). “What you see may not be what you get: a brief, nontechnical introduction to overfitting in regression-type models.” *Psychosomatic Medicine*, 66(3), 411-421. DOI: https://doi.org/10.1097/01.psy.0000127692.23278.a9
- Barr, D. J., Levy, R., Scheepers, C., and Tily, H. J. (2013). “Random effects structure for confirmatory hypothesis testing: Keep it maximal.” *Journal of Memory and Language*, 68(3), 255-278. DOI: https://doi.org/10.1016/j.jml.2012.11.001
- Bates, D., Maechler, M., Bolker, B., and Walker, S. (2015). “Fitting Linear Mixed-Effects Models Using lme4.” *Journal of Statistical Software*, 67(1), 1-48. DOI: https://doi.org/10.18637/jss.v067.i01 ; arXiv: https://arxiv.org/abs/1406.5823
- Bates, D., Kliegl, R., Vasishth, S., and Baayen, H. (2015). “Parsimonious Mixed Models.” arXiv: https://arxiv.org/abs/1506.04967
- Belsley, D. A. (1991). *Conditioning Diagnostics: Collinearity and Weak Data in Regression*. Wiley. ISBN 9780471528890. URL: https://search.worldcat.org/title/481787715
- Belsley, D. A., Kuh, E., and Welsch, R. E. (1980). *Regression Diagnostics: Identifying Influential Data and Sources of Collinearity*. Wiley. DOI: https://doi.org/10.1002/0471725153
- Craney, T. A., and Surles, J. G. (2002). “Model-Dependent Variance Inflation Factor Cutoff Values.” *Quality Engineering*, 14(3), 391-403. DOI: https://doi.org/10.1081/QEN-120001878
- Dormann, C. F., Elith, J., Bacher, S., Buchmann, C., Carl, G., Carre, G., et al. (2013). “Collinearity: a review of methods to deal with it and a simulation study evaluating their performance.” *Ecography*, 36(1), 27-46. DOI: https://doi.org/10.1111/j.1600-0587.2012.07348.x
- Fox, J., and Monette, G. (1992). “Generalized Collinearity Diagnostics.” *Journal of the American Statistical Association*, 87(417), 178-183. DOI: https://doi.org/10.1080/01621459.1992.10475190
- Harrell, F. E. Jr. (2015). *Regression Modeling Strategies*, 2nd ed. Springer. DOI: https://doi.org/10.1007/978-3-319-19425-7
- James, G., Witten, D., Hastie, T., and Tibshirani, R. (2021). *An Introduction to Statistical Learning with Applications in R*, 2nd ed. Springer. DOI: https://doi.org/10.1007/978-1-0716-1418-1
- Marquardt, D. W. (1970). “Generalized Inverses, Ridge Regression, Biased Linear Estimation, and Nonlinear Estimation.” *Technometrics*, 12(3), 591-612. DOI: https://doi.org/10.1080/00401706.1970.10488699
- Mason, C. H., and Perreault, W. D. Jr. (1991). “Collinearity, Power, and Interpretation of Multiple Regression Analysis.” *Journal of Marketing Research*, 28(3), 268-280. DOI: https://doi.org/10.1177/002224379102800302
- Matuschek, H., Kliegl, R., Vasishth, S., Baayen, H., and Bates, D. (2017). “Balancing Type I error and power in linear mixed models.” *Journal of Memory and Language*, 94, 305-315. DOI: https://doi.org/10.1016/j.jml.2017.01.001
- Menard, S. (2002). *Applied Logistic Regression Analysis*, 2nd ed. Sage. DOI: https://doi.org/10.4135/9781412983433
- O'Brien, R. M. (2007). “A Caution Regarding Rules of Thumb for Variance Inflation Factors.” *Quality & Quantity*, 41, 673-690. DOI: https://doi.org/10.1007/s11135-006-9018-6
- Royston, P., Altman, D. G., and Sauerbrei, W. (2006). “Dichotomizing continuous predictors in multiple regression: a bad idea.” *Statistics in Medicine*, 25(1), 127-141. DOI: https://doi.org/10.1002/sim.2331
- Wurm, L. H., and Fisicaro, S. A. (2014). “What residualizing predictors in regression analyses does (and what it does not do).” *Journal of Memory and Language*, 72, 37-48. DOI: https://doi.org/10.1016/j.jml.2013.12.003
- York, R. (2012). “Residualization is not the answer: Rethinking how to address multicollinearity.” *Social Science Research*, 41(6), 1379-1386. DOI: https://doi.org/10.1016/j.ssresearch.2012.05.014
- Zuur, A. F., Ieno, E. N., and Elphick, C. S. (2010). “A protocol for data exploration to avoid common statistical problems.” *Methods in Ecology and Evolution*, 1(1), 3-14. DOI: https://doi.org/10.1111/j.2041-210X.2009.00001.x

一句话结论：v0.3 的 5 项套件对“4 个 1-df 连续固定效应因子非冗余”至少过度 2 到 3 项；最终推荐落到 2 项，即 VIF/tolerance 作为正式诊断，加 4x4 predictor correlation matrix 作为透明补充。
