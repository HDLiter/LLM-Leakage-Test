# Final NLP Direction

1. **Evidence intrusion is practically detectable here, but keep it narrow.** Because prompts already require evidence quotes, use a precision-first `quote support` audit: extract quoted spans, normalize Unicode / punctuation / whitespace, then exact- or fuzzy-match them against the presented article. If a quoted span is absent from the input article, count it as evidence intrusion. Keep `unsupported quote` separate from the harder category `unsupported claim`, and human-audit only borderline fuzzy matches. This will not identify all parametric-memory use, but it is reliable enough as a black-box signal of article-external intrusion.

2. **Use a lighter black-box TIRG, not full cloze.** The simpler version is `post-task slot guessing`, closer to TS-Guessing / Time Travel than a full held-out-span probe. For each item, hide `1-2` distinctive article spans from the visible context (source string, number, phrase), run the task, then ask a short multiple-choice recovery question. Compare recovery after the task against a no-task baseline at the same cue level. That gives a usable task-induced retrieval signal on DeepSeek without white-box access, and is easier to scale than open-ended cloze scoring.

3. **Literature position: novel as a transfer and synthesis, not as a raw assay.** ReEval already covers the core logic `same question, changed evidence, does the model move?`, so this is not novel as a standalone metric paper. The novelty is the bridge: importing evidence-conflict methods from RAG faithfulness into **pretraining memorization / contamination** on dated financial news, then showing that **task design changes leakage on fixed inputs**. Li et al. supports the mechanism directly: memory strength interacts with evidence style. Mehrbakhsh says local edit quality is a real confounder, so keep edits tightly matched. Zhang et al. gives the right formal lens: exposure counterfactuals are the foundation, and your behavioral assay is a proxy. My read: this is likely strong enough for **EMNLP Findings** if the benchmark is clean and the claim is sharp. It is weaker as a main-track "new metric" paper.

4. **What to cut from the current plan:** cut scope, not rigor.
   - Drop the four-task ladder as the headline. Make it a binary contrast: `direct prediction` versus one evidence-grounded task, preferably `authority`.
   - Demote `sentiment` and `novelty` to appendix or later follow-up.
   - Replace the six-rewrite inventory with one `local placebo/paraphrase` and one `conflict edit`; keep CF-based EI as secondary, not the paper's backbone.
   - Shrink `CLS-Leak-1000` to a smaller, more audited benchmark (`300-500` items) if that is what it takes to afford stronger evidence-intrusion checks and temporal analysis.
   - Keep Qwen familiarity as stratification / validation, not as a co-equal pillar.

Recommended paper spine: **outcome-proximal tasks amplify leakage; evidence-grounded tasks retain more utility per unit leakage; evidence intrusion is the main black-box assay; counterfactual EI and Qwen familiarity are supporting validation.**
