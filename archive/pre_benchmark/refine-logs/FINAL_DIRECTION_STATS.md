# Final Stats Direction

1. **Randomized exposure on Qwen 2.5 7B is feasible in 10 weeks only as a reduced causal validation, not as the full paper backbone.** Training is not the bottleneck; benchmark construction is. The minimum credible design is `200-300` event clusters, two task families only (`outcome-proximal` vs `evidence-grounded authority`), and **two** complementary continued-pretraining runs from the same Qwen 2.5 7B base checkpoint released on **September 19, 2024**. Randomly split clusters into `A/B`; model 1 sees `A` but not `B`, model 2 sees `B` but not `A`, with the same dated filler corpus in both runs. Then each item is exposed once and unexposed once, giving within-item identification and removing baseline item heterogeneity. A third no-injection run is useful robustness, but not required.

2. **If continued pretraining is dropped, the fallback is not a formal RD.** Around the Qwen release date, the credible object is a **local training-access premium**,

`lambda_t(c) = lim_{d -> c-} E[Y_it | d] - lim_{d -> c+} E[Y_it | d]`,

estimated in a narrow publication-date window around `c = 2024-09-19`. The identifying assumption is that, absent training exposure, potential outcomes vary smoothly with publication date at `c`, and exposure probability changes discretely at `c`. The first part is plausible in a tight window. The second is only moderately credible because a public release date is an upper bound on the training cutoff, not the cutoff itself. So this should be sold as a **fuzzy, descriptive boundary design** or local event-study, not headline causal identification.

3. **The formal task-design estimand should be an exposure-by-task interaction.** Define

`tau_t = E[Y_it(1, t) - Y_it(0, t)]`,

where `Y_it` is a scalar leakage outcome for item `i` under task `t` and exposure status `1/0`. Then the main interaction is

`Delta = E{[Y_i(1, prox) - Y_i(0, prox)] - [Y_i(1, ground) - Y_i(0, ground)]}`.

This is the clean estimand for "outcome-proximal tasks are more exposure-sensitive than evidence-grounded tasks." If more than two tasks remain, use `Delta_t,t' = tau_t - tau_t'`. `Y` can be evidence-intrusion rate as the main black-box outcome, with CF-based EI retained as secondary.

4. **Yes, randomized exposure materially upgrades the paper.** Without it, the contribution is a careful measurement paper with bounded interpretation: task design changes observed contamination proxies. With it, the paper can claim that task design moderates the **causal effect of training exposure** on outputs in an open-model setting. That is a real step up in contribution level. The right presentation is: **causal anchor on Qwen, transport / external-validity evidence on DeepSeek**. Internal validity rises sharply; external validity remains bounded to Qwen-style continued pretraining and Chinese financial news.
