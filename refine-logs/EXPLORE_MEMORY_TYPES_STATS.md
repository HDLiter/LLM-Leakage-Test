# Explore Memory Types: Econometric Note

1. **What is the continued-pretraining treatment effect?**  
With **article-only** continued pretraining, the treatment is not pure Type B. It is a **composite reduced-form effect**: (i) article familiarity / retrieval facilitation, and (ii) stronger activation of pre-existing generic finance priors ("rate cuts are bullish"). Because CLS telegraphs are written **before** returns realize, this treatment does **not directly inject realized outcome knowledge**. In the DAG language of section 5, it mainly shifts `K -> M` for the article and may indirectly strengthen the use of existing priors in `R`, but it does not newly encode the realized market reaction.

2. **Should we inject article + subsequent market reaction?**  
Yes, if the goal is to identify **true Type B**. But that should be a **separate arm**, not the baseline treatment. The clean design is a `2 x 2` randomization:
`A_i`: article injected or not;  
`B_i`: subsequent reaction / realized outcome injected or not.
Then article-only identifies familiarity/cueing; outcome-only or article+outcome identifies look-ahead memory. This is realistic only as a model of **broad web pretraining** that may contain later commentary or price summaries, not as a literal model of CLS-only continued pretraining. So it is a valid stress test, but not the most realistic single treatment.

3. **What does `tau_t = E[Y_i(1,t) - Y_i(0,t)]` measure?**  
Under article-only treatment, `tau_t` measures an **exposure effect**, not a clean look-ahead-bias effect. It mixes:
`Type A + cue-triggered use of pre-existing outcome-relevant priors`.
So labeling `tau_t` as "look-ahead bias" would overstate identification. A cleaner decomposition is:
`tau_A,t = E[Y_i(1,0,t) - Y_i(0,0,t)]` and  
`tau_B,t = E[Y_i(0,1,t) - Y_i(0,0,t)]`,
where the two treatment coordinates are article exposure and outcome exposure. `tau_B,t` is the closer estimand for Type B.

4. **Can we separate A from B econometrically?**  
Yes, but **not** from "prediction matches actual outcome" alone, because Type A can also improve match rates on average. Better separation:
use the `2 x 2` design above;
compare effects on **evidence-grounded** outcomes versus **outcome-proximal** outcomes;
test whether treatment gains are larger for **idiosyncratic/surprising** events, where generic priors should be weak;
compare actual-outcome match to placebo or permuted outcomes.
Interpretation: Type A should mainly move familiarity, citation, and evidence-faithfulness; Type B should disproportionately raise actual-outcome match and excess invariance under decision-relevant semantic edits.

5. **Does temporal decay inherently separate A from B?**  
No. Temporal decay is **not identifying by itself** because both article familiarity and outcome memory can decay with age. It helps only if the two channels have different timestamps: article at `t0`, reaction material at `t1 > t0`. Then decay relative to article date versus reaction date can be informative. Without separate timing or separate treatments, decay is only suggestive, not a clean A/B separator.
