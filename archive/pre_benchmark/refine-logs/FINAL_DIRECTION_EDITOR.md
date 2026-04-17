# Final Editorial Direction

1. **Stronger or weaker?**  
Stronger than the original plan, provided you truly simplify. The old version asked reviewers to accept a bespoke metric, a four-task ladder, and many repair controls at once. The new synthesis asks them to accept one cleaner, more portable claim: **on the same articles, outcome-proximal tasks are more contamination-prone than evidence-grounded tasks**. That is easier to explain, easier to cite, and better aligned with Li and Flanigan plus the context-faithfulness literature. The main risk is not novelty overlap; it is scope creep from keeping too many methods alive.

2. **Continued pretraining: scope risk or differentiation advantage?**  
For a 10-week paper, mostly a **scope risk**. It is the strongest identification design in principle, but it creates another paper's worth of engineering, corpus-construction, and reviewer questions about exposure dosage and training protocol. My advice: make **temporal discontinuity / local pre-post boundary analysis on an open model** the primary identification. If you can run a tiny continued-pretraining pilot, treat it as bonus validation or future work. Do not try to make both the backbone.

3. **Title and one-sentence contribution**  
**Title:** *Outcome-Proximal Tasks Amplify Look-Ahead Leakage: Temporal and Evidence-Based Audits in Chinese Financial News LLMs*  
**One-sentence contribution:** We show on matched Chinese financial news articles that tasks closer to latent future outcomes exhibit larger contamination signatures than evidence-grounded extraction, with temporal-boundary evidence and evidence-intrusion diagnostics supporting a parametric-memory interpretation rather than a pure prompt-format effect.

4. **Best venue**  
Best risk-adjusted target: **Findings of EMNLP**. The paper is clearly NLP evaluation methodology, the Chinese financial setting is genuinely underexplored, and the benchmark release adds value, but the evidence base is still domain-bounded. **Main EMNLP** becomes realistic only if the identification is exceptionally clean and the framing is made explicitly general beyond finance.

5. **The paper I would write in 10 weeks**  
Cut to **two task families** in the main story: outcome-proximal prediction vs evidence-grounded extraction. If you need one grounded task, make **authority** the primary one; keep sentiment secondary and demote novelty if labeling is noisy. Build a **smaller, cleaner `300-500` item benchmark**, not `1000` if quality suffers.

**Table of contents**
1. Introduction  
2. Related Work: contamination, temporal audits, and context-faithfulness  
3. Outcome-Proximal vs Evidence-Grounded Task Design  
4. CLS-Leak-500: Benchmark Construction and Annotation  
5. Identification Strategy: Temporal Discontinuity Around a Documented Training Boundary  
6. Black-Box Diagnostics: Evidence Intrusion and Counterfactual Faithfulness  
7. Main Results: Same-Article Task Comparison  
8. Robustness: Matched Format, Sham Task, and Freshest-Slice Placebo  
9. Discussion: Implications for Benchmark Design and Financial NLP  
10. Conclusion

Bottom line: this is a **better paper** if you stop trying to prove EI as the contribution and instead use temporal identification plus evidence intrusion to support a simple editorial thesis about **leakage-aware task design**.
