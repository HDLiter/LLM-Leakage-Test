# Round 2 — NLP Agent Response to Challenger

**Thread:** 019d65ce-bed8-79c0-be3f-61e0f1609138

## Revisions

1. **On CFLS:** Revised — floor effect is not sufficient evidence of failure. CFLS is **uncalibrated**. The missing piece is a positive control (known-memorized item). Standard in memorization work (Carlini et al.). Until calibration is done, the pilot's negative result is non-diagnostic.

2. **On sentiment vs. leakage:** Partly agrees, but only for the generic version. The specific setup is **event-conditioned market-direction prediction** tied to specific entities and outcomes — a mixed construct. Some cases are solvable by general schemas, others could benefit from article-level exposure. Leakage risk is **heterogeneous across cases**, probably low for schematic templates.

3. **On CPT:** Agrees — flip rate does not identify memorization. CPT mainly measures **susceptibility to contextual override under conflict**. Useful as complement to direct familiarity probes, but not as standalone leakage metric.

4. **On verbatim completion probes and Min-K%:** Acknowledged this was a real gap in Round 1. These are the cheapest high-yield next steps:
   - Completion probes: high-precision signal for exact/near-exact memorization
   - Min-K%: continuous familiarity score at token level, orthogonal to prompt-following
   - If both are flat while CFLS is negative → supports true-negative interpretation
   - If they spike on some cases → CFLS is missing leakage, not disproving it

5. **On renaming CFLS:** Agrees it's premature before rarity stratification. Event rarity is exactly the moderator that could separate "general schema following" from "instance-level familiarity."

6. **Revised recommendation:** Not benchmark redesign yet. A **three-step calibration pass** on existing 36 cases: positive-control memorization probes, token-level familiarity scoring, rarity/temporal stratification.
