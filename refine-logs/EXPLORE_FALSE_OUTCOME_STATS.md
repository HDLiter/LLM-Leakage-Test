# Explore False Outcome: Econometric Note

1. **What does `2 x 3` identify that `2 x 2` does not?**  
Let `A_i in {0,1}` be article exposure and `B_i in {n,r,f}` be training outcome state: none, real, false. Let `Y_i(a,b,t)` be a signed model output on task `t`, and let `s_i in {-1,1}` be the true market-reaction sign. Define the sign-normalized outcome `\tilde Y_i(a,b,t) = s_i Y_i(a,b,t)`, so higher values mean "more aligned with the true outcome."  
The `2 x 2` design identifies level effects such as `tau_t^r(a) = E[\tilde Y_i(a,r,t) - \tilde Y_i(a,n,t)]`, but this can still mix article cueing and outcome memory when Type A and the real outcome point the same way.  
The `2 x 3` adds the **sign-flip contrast**
`kappa_t(a) = (1/2) E[\tilde Y_i(a,r,t) - \tilde Y_i(a,f,t)]`.
This identifies whether the model follows the injected outcome sign itself. Under pure Type A, `kappa_t(a) approx 0`; under Type B, `kappa_t(a) > 0`.

2. **Is false outcome a cleaner Type B identifier than article + real outcome?**  
Yes, for outcome-proximal tasks. The article + real-outcome arm is realistic, but not diagnostic: Type A and Type B can both raise alignment with the real outcome. The false-outcome arm is sharper because it creates a sign reversal: Type A should still follow article semantics / priors, while Type B should follow the injected false reaction. So false outcome is the cleaner **identification arm**; real outcome remains the cleaner **external-validity arm**.

3. **Does counterfactual article editing become redundant?**  
No. False-outcome CPT and counterfactual article editing intervene on different nodes in the DAG. False-outcome CPT estimates a **training-time memory effect** through the parameters: `E[Y_i(a,b,t)]`. Counterfactual article editing estimates **inference-time text reliance** holding the trained model fixed:
`rho_t(a,b) = E[Y_i^{(a,b)}(X_i^{CF}, t) - Y_i^{(a,b)}(X_i, t)]`.
These are different estimands. If budget is tight, CF editing becomes secondary mechanism/robustness rather than the headline identifier, but not pure appendix.

4. **How many training runs?**  
For a full within-item `2 x 3` factorial, the clean answer is **6 complementary CPT runs** so each item appears once in each cell. This is materially heavier than the original 2-run `2 x 2`, but still feasible for light Qwen-7B-style CPT if benchmark construction remains the bottleneck. A cheaper design is **4 runs** on `(0,n), (1,n), (1,r), (1,f)`; this already identifies Type A versus Type B, while `(0,r)` and `(0,f)` mainly identify whether article context amplifies outcome memory.

5. **Right estimand.**  
The main estimand should now be the **signed outcome-memory effect**
`kappa_t(1) = (1/2) E[\tilde Y_i(1,r,t) - \tilde Y_i(1,f,t)]`.
Secondary estimands:
`tau_t^A = E[\tilde Y_i(1,n,t) - \tilde Y_i(0,n,t)]`  (article familiarity / Type A),
`psi_t = kappa_t(1) - kappa_t(0)`  (article-outcome complementarity).
If task families remain central, the key paper-level interaction is `Delta = kappa_prox(1) - kappa_ground(1)`.
