# Round 1.5 — Challenger Agent (Claude sub-agent)

## Shared Blind Spots

### 1. CFLS ≤ 0 might be a TRUE NEGATIVE, not a measurement failure
All 4 agents assume the floor effect means CFLS is broken. But a well-calibrated LLM *should* follow counterfactual reversals. CFLS ≤ 0 across 36 cases is exactly what you'd predict for a model with zero memorization doing competent reading comprehension. **Proposed diagnostic:** Test CFLS on a known-memorized item (e.g., a famous verbatim passage). If CFLS still ≤ 0, the metric is broken. If CFLS > 0 only on memorized items, it works fine and the pilot is simply a true negative.

### 2. Financial sentiment analysis may not be susceptible to leakage
All agents assume memorization *should* exist. But sentiment analysis is a **skill**, not a fact-retrieval task. A model can be excellent at it purely through learned linguistic patterns without memorizing any specific article. The research premise — that leakage matters for sentiment classification — deserves scrutiny.

### 3. No confirmation of training data exposure
Nobody raises the possibility that these specific articles may not be in DeepSeek's training corpus. Without confirming exposure, the experiment may be testing leakage from data the model never saw.

## Consensus Challenges

### CPT 14-17% flip rate: may be in-context persuasion, not memorization
CPT injects a false outcome *into the prompt context* — this tests whether the model is susceptible to in-context persuasion, not whether it "knows" the real outcome. A model with zero training data exposure would still show some flip rate. CPT as designed **cannot distinguish memorization-based anchoring from generic context-following behavior**, even with controls.

### Renaming CFLS is premature
Before abandoning CFLS as a leakage metric, try stratifying by event rarity *within the existing pilot data*. The floor effect may break for the rarest cases. Achievable now with n=36, costs nothing.

## Overlooked Alternatives

1. **Verbatim completion probes** — Feed first 50 characters of an article, check if model completes it faithfully. The most direct memorization test, standard MIA-adjacent approach, conspicuously absent.
2. **Calibration-based detection** — Measure confidence (logprob distributions) on seen vs. unseen articles. Qwen vLLM already provides logprobs.
3. **Temporal split as natural experiment** — Articles published after DeepSeek's training cutoff serve as natural control group. Cleanest possible design, no synthetic manipulation needed.
4. **Min-K% on Qwen** — Token-level membership inference, no reference model needed. Already in the project plan but not discussed by any agent.

## Divergent Point Resolution

- **D1 (RQ change):** Stronger reframing: "Behavioral leakage tests produce systematically misleading null results on generalization-capable models, and here is why." This is a warning/contribution to the evaluation community.
- **D2 (Scope):** Drop XGBoost AND economic validation. Belongs in follow-up application paper.
- **D3 (Venue):** EMNLP only if bidirectional confound shown to be general. Otherwise ACL Findings or workshop.
- **D4 (CPT interpretation):** Temporal split control resolves this empirically. If post-cutoff articles show the same flip rate, CPT measures suggestibility. If pre-cutoff > post-cutoff, genuine memorization evidence.

## Bottom Line

Before investing in a 1000-case benchmark redesign, run three cheap diagnostics:
1. Verbatim completion probes (does the model actually memorize these articles?)
2. Temporal split comparison (pre- vs. post-cutoff behavior)
3. CFLS stratified by event rarity within existing pilot data

Any of these could fundamentally change the project's direction in a week of work.
