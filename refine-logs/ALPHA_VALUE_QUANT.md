# Alpha Value: Quant View

1. **Which scenarios are economically real?**
Scenario 1 is real, but only if you treat authority/novelty as **micro-state variables**, not standalone return forecasts. Novelty/freshness can have direct pricing content; authority mostly tells you whether to trust and scale another signal. Scenario 2 is the strongest live-pipeline use case: mix fragile high-alpha features with lower-leakage conditioning variables so the model decays less out of sample. Scenario 3 is plausible but weakest economically; I would test it as an inference-time ablation, not rely on it in production. In a live stack, I would seriously test **(1) low-leakage factor set** and **(2) mixed-model stabilization**; I would treat **(3) reasoning priming** as a mechanism check.

2. **Does literature support richer text features over simple sentiment?**
Yes. The direction of evidence is clear. **Heston-Sinha** and **Ke-Kelly-Xiu** both argue that story-level or latent text structure contains return-relevant information not exhausted by scalar sentiment. In the LLM era, **Guo-Hauptmann** show newsflow representations beating conventional sentiment baselines in portfolio tests; **LLMFactor** shows sequential factor extraction beating keyphrase/sentiment baselines; **Bastianello et al.** show multi-step extraction of valuation channels, horizons, and attention is economically meaningful and linked to return patterns. The literature does **not** say every richer feature is strong alone. It says that semantically richer, structured text features beat one-dimensional tone often enough to make this a serious hypothesis.

3. **Best reviewer-facing "so what"**
The strongest answer is not "lower leakage is good." It is: **lower-leakage features are more useful because they are closer to persistent economic primitives that survive deployment, while direct-prediction signals are more exposed to false alpha from memorized event outcomes.** In finance, the relevant object is not in-sample IC; it is **post-deployment decay**. Authority and novelty are valuable because they determine **how the market should react to the same content**: fresh news should matter more than recap, official disclosures more than rumor. That makes them useful as **gating, interaction, and regularization variables**, especially when model vintages or market regimes change.

4. **Is the sham-control objection a real threat?**
Yes, until you run the downstream test. "Word count is also low-leakage" is a valid reviewer attack if your only result is lower excess invariance. But it becomes easy to dismiss if you show three things:  
(i) meaningful decomposed factors beat sham low-leakage controls out of sample,  
(ii) they add value beyond simple text stats/sentiment, and  
(iii) they reduce decay when combined with higher-leakage predictors.  
So the sham argument is not fatal, but it forces the paper to include **economic validation**, not just contamination measurement.

5. **Minimum credible downstream alpha test**
Use the linked 3-day abnormal-return panel already in the plan. Run a strict rolling walk-forward design with no cluster leakage and a recent holdout. Compare:
- simple sentiment
- sham controls
- low-leakage factors only: authority + novelty (+ impact if available)
- direct prediction only
- direct prediction + low-leakage factors

Primary metrics should be **daily rank IC / ICIR** and a simple **top-minus-bottom spread** after basic size/industry neutralization. The key estimand is **OOS decay**: how much performance drops from older training windows to recent holdout or post-boundary periods.

Minimum convincing result:
- low-leakage factors beat sham controls and simple surface statistics;
- mixed model beats direct-only on **stability/decay**, even if not always on raw in-sample IC;
- novelty contributes more direct alpha, while authority mainly helps as an interaction/gating term.

If you can only win one reviewer argument, win this one: **low-leakage decomposed features are useful because they produce alpha that is more likely to survive when memorized historical outcomes stop helping.**
