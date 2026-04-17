# Alpha Value: Econometric Note

1. **Glasserman-Lin implication.** Yes, the natural prediction is: lower leakage can mean **lower in-sample fit but smaller generalization gap and more stable out-of-sample IC/Sharpe**. Formalize observed features as `X = X* + Lambda C`, where `X*` is text-grounded signal and `C` is contamination. In older / contaminated samples, `Cov(C, r_{t+h}) > 0`, so `Cov(X, r)` is mechanically inflated. Near the knowledge frontier, `Cov(C, r_{t+h}) approx 0`, so the contaminated component stops helping. Then high-leakage signals can dominate in-sample while low-leakage signals win on stability:
`Gap = Perf_IS - Perf_OOS` should be increasing in leakage load `Lambda`.

2. **Chronologically Consistent LLMs implication.** Comparable Sharpe under leakage-free training implies `Cov(X*, r_{t+h})` is not negligible: genuine semantic signal survives after removing look-ahead memory. For this project, that supports **S1** and weakly **S3**: decomposed factors need not be weaker just because they are cleaner; they may isolate a more stable Ke-Kelly-Xiu-style latent text factor. But it does **not** imply every low-leakage factor is useful. The required result is incremental predictive value on fresh holdouts, not merely lower contamination.

3. **Orthogonalization interpretation.** If `H_i` is a high-leakage feature and `C_i` contamination proxies, define the cross-fitted residual
`H_i^perp = H_i - m_hat(C_i, Z_i)`,
with `Z_i` article controls. `H_i^perp` is **not** "clean alpha." It is the part of `H_i` unexplained by **measured** contamination proxies and controls. The generated-regressor issue is not fatal if the whole pipeline is time-ordered cross-fitted and bootstrapped, but interpretation stays bounded: proxy error leaves residual contamination, and over-control may remove true signal correlated with `C_i`.

4. **Marginal-value regression.** Let `L_i` be low-leakage factors, `H_i` high-leakage factors, `C_i` contamination proxies, `X_i` controls, `tau_t` time fixed effects, and `eta_g` target/group effects:
`r_{i,h} = alpha + beta_L' L_i + beta_H' H_i + delta' C_i + theta_L' (L_i x C_i) + theta_H' (H_i x C_i) + X_i' gamma + tau_t + eta_g + eps_i`.
Test `H0: beta_L = 0` for marginal predictive value beyond `H_i`, and `H0: theta_L = theta_H` (or `theta_L = 0`) for contamination sensitivity. The low-leakage story predicts `beta_L != 0` with `theta_L` weaker than `theta_H`.

5. **Is S2 testable now?** Partly, yes, as a **supplementary stability test**. Compare `H` only, `L` only, and `H+L` models in rolling-origin splits and the freshest holdout. Evaluate:
- out-of-sample rank IC / hit-rate decay from historical to fresh periods
- variance of performance across folds
- feature-distribution drift between train and holdout
- whether contamination interactions shrink when `L` is added

S2 is supported if `H+L` has similar or slightly lower in-sample fit than `H`, but materially **smaller OOS decay / variance** and weaker dependence on contamination. With the current balanced 1,000-case benchmark, this remains a bounded sensitivity analysis, not definitive tradable-alpha proof.
