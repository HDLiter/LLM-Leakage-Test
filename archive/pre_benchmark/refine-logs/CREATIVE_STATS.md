The quantity I would want is **not** the causal effect of latent “memorization activation” `M` in the DAG. That object is not identified by counterfactual edits, masking, sham prompts, or any other behavioral perturbation unless you can manipulate training exposure itself. So the current DAG is mostly decoration: it names channels, but it does not deliver a valid back-door or IV strategy.

If I could redesign from scratch, the **primary causal estimand** would be the **effect of training exposure on task outputs**, task by task:

`tau_t = E[Y_it(1) - Y_it(0)]`,

where `Y_it` is the output for article `i` under task `t`, and `1/0` means the article-event (or a near-duplicate bundle containing the same future-relevant facts) is included versus excluded from the model’s training/continued-pretraining corpus. The paper’s main comparison would then be

`Delta_t,t' = tau_t - tau_t'`,

which asks whether direct prediction is more contamination-sensitive than sentiment or decomposition. This is the clean estimand because it is about a manipulable treatment.

The clean identification strategy is therefore a **white-box randomized exposure design** on Qwen, not behavioral proxy engineering on DeepSeek. Take a frozen base model, build a dated supplemental corpus, randomly assign benchmark event-clusters to be injected or withheld during a small continued-pretraining stage, then evaluate all tasks on the same held-out benchmark. Randomization identifies `tau_t`; no local placebo, entity masking, sham, or edit-distance adjustment is needed for the main claim.

If retraining is infeasible, I would downgrade the main target to a **descriptive temporal estimand**: the **training-access premium** around a documented cutoff,

`lambda_t(c) = E[Y_it | date_i < c] - E[Y_it | date_i >= c]`,

estimated in a narrow window around `c` on an **open model with a known frontier**, not a vendor API with undocumented rolling updates. This is a local RD / event-study logic: items just before the cutoff were eligible for exposure; items just after were not. The identifying assumption is continuity of article mix around `c`, which is far more credible than the exclusion restrictions behind masking or semantic edits.

Qwen should also supply the **primary measurement signal**. Instead of using behavioral excess invariance from `src/metrics.py` as the headline measure, use a white-box article-level familiarity score: token log-likelihood, Min-K/LAP, and ideally a **likelihood ratio of the original article versus matched synthetic rewrites** under the same prefix. That is still imperfect, but it is much closer to memorization than task behavior is, and it is task-independent. Then use task prompts only for a secondary question: which tasks load more heavily on this article-level familiarity signal?

So the redesigned paper is: identify exposure causally if you can manipulate training; otherwise estimate a narrow, well-defined **training-access premium** around a real cutoff and treat everything else as supporting measurement. That is much cleaner than trying to rescue a latent-path causal story with more controls.
