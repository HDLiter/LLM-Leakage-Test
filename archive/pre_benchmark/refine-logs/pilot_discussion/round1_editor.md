# Round 1 — Editor Agent (Senior EMNLP Area Chair)

**Thread:** 019d65d6-9807-7df0-af44-e0d125063ee6

## Analysis

### 1. Paper Narrative Impact

The pilot does not support the original claim that "decomposed tasks reduce leakage." It supports a different, and more interesting, claim: **naive counterfactual sensitivity measures can fail catastrophically in knowledge-rich domains because they confound memorization with bidirectional semantic competence.**

Null results are publishable at EMNLP/ACL only when they overturn a plausible evaluation protocol and replace it with a better one. The story cannot be "we expected direct > decomposed, but did not find it." It has to be: "a seemingly reasonable leakage metric is invalid under realistic distributional conditions; here is the confound, here is the causal explanation, and here is a more discriminating alternative."

### 2. Bidirectional Generalization Confound as Contribution

Yes, potentially a real contribution — but only if elevated from anecdotal diagnosis to a **formal threat-to-validity argument**. Use the DAG to show that CFLS is downstream of "response changes under counterfactual wording," where memorization is only one possible upstream cause. A second path — semantic generalization — generates the same observed behavior. Frame as non-identifiability of the latent construct.

### 3. Reviewer Prediction: Top 3 Objections

1. **"This does not establish leakage."** Reviewers will say False-Outcome CPT may measure resistance to prompt perturbation, generic world knowledge, or calibration inertia, not memorization per se.

2. **"Evidence base is too thin."** One model, 36 cases, temperature 0, near-zero cross-task correlation. Over-interpreting a small pilot.

3. **"Scope is incoherent."** RQ1 + RQ2 + RQ3 + benchmark + white-box + XGBoost is too much for one submission with insufficiently mature evidence.

4. (Bonus) Evidence-intrusion detector at 0/36 reads like an insensitive heuristic, not a finding.

### 4. Scope Recalibration

Do NOT keep "task design shapes leakage" as-is. What the pilot supports is: **"task design shapes the observability of leakage"** or **"task design interacts with leakage measurement validity."** Instead of claiming decomposed tasks mitigate leakage, ask whether different task formulations make memorized outcome knowledge more or less identifiable. That is a stronger NLP question.

### 5. CPT as Leading Signal

Yes, pivot so CPT is primary and CFLS secondary. But do not make CPT the only metric. Make it the leading behavioral metric, with CFLS reframed as diagnostic showing why prompt-reversal sensitivity is insufficient. Present convergent evidence: CPT as main behavior, Min-K% as supporting exposure evidence, CFLS as the invalidated baseline.

### 6. Benchmark Design (CLS-Leak)

Design around **identifiability**, not just coverage. Include positive and negative controls. Stratify by public salience, entity popularity, event recency, outcome distinctiveness, training-data prevalence. Include a true low-memorization stratum (pilot is mostly high/medium).

Benchmark should demonstrate three things:
1. That some metrics fail (CFLS on common events)
2. That CPT-like probes discriminate better
3. That results are stable across task formulations and model families

### 7. Venue Strategy

**EMNLP remains best target** if framed as NLP evaluation/benchmark methodology paper. ACL/EMNLP reviewers care about contamination, benchmark validity, measurement design. Finance venues (JFE) not realistic. ICAIF plausible backup. AI safety venue/workshop possible if foregrounding contamination pathways.

### 8. Recommendations

1. **Narrow the thesis:** "Counterfactual reversal can mismeasure memorization; outcome-conflict probes plus white-box auditing offer a more valid alternative."
2. **Expand beyond one model.** Even three model families would materially improve credibility.
3. **Simplify the paper.** Consider demoting/removing XGBoost downstream section unless directly validates benchmark.
4. **Add controls, CIs, mixed-effects analysis, stronger annotation around false outcomes.**
5. **Demote or redesign evidence intrusion** unless nontrivial recall demonstrated.
