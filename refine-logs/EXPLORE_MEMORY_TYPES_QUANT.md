# Memory Types: Quant View

1. **Type A / Type B is the right first split**, but I would refine it into four buckets for a live A-share pipeline:
- **Type A1: structural priors**. "Rate cuts are usually bullish", "official notices dominate rumors". This is useful capability.
- **Type A2: entity/regime familiarity**. Sector structure, policy style, issuer-specific behavior. Mostly acceptable unless it helps identify a historical event.
- **Type B1: event-outcome memory**. The model recalls what happened after this exact event/article. This is the contamination that directly creates false alpha.
- **Type B2: task-template memory**. The prompt format itself cues stored answers. This matters because direct prediction gives Type B a short path; authority extraction blocks much of it.

2. **Yes, this changes metric priority.** From a quant perspective, raw task accuracy is no longer primary. I would rank:
- **CF reversal sensitivity on outcome-proximal tasks** as the main metric. If semantics flip and the label does not, that is the cleanest look-ahead warning.
- **Neutral paraphrase stability** as a control, not the main estimand. You want to know the model is not just fragile to wording.
- **Evidence intrusion / unsupported outcome rate** on authority or novelty tasks. If the model injects later price action or outcome-consistent claims not in text, that is strong Type B evidence.
- **Temporal freshness slope** and **cross-model concordance** as triangulation.
- **Downstream IC decay after orthogonalizing contamination proxies** as production relevance, not identification.

3. **In production, detect look-ahead memory with an event-level risk panel, not one score**:
- **Reversal gap**: direct-prediction output should change when decision-relevant semantics change.
- **Paraphrase gap**: output should stay stable under neutral rewrites.
- **Outcome intrusion rate**: on authority/novelty prompts, count unsupported mentions of returns, later market reaction, or post-publication facts.
- **Masked-slot recovery**: can the model recover hidden post-event facts from minimal cues?
- **Freshness interaction**: risk should be higher for older, more prominent, and highly propagated events.

4. **Practical Type A vs Type B test**:
Use a matched triplet for each event:
- original article
- neutral paraphrase
- counterfactual article that keeps source credibility and style similar but flips the decision-relevant economics

Run both **direct prediction** and **authority extraction**.

Interpretation:
- **Type A**: direct prediction follows the counterfactual reversal; authority labels stay tied to visible provenance; no later outcome language appears.
- **Type B**: direct prediction stays anchored to the original realized direction, masked post-event facts are recoverable, or authority answers leak outcome-consistent claims absent from the article.

For the specific case of "rate cuts are bullish" versus "this rate cut led to a 25% rally", build same-template synthetic policy shocks across unseen dates/entities. If the model generalizes the rule across synthetic cases, that is Type A. If it is unusually sticky only on historically real events, that is Type B.
