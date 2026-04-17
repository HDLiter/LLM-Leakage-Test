# Round 3 Summary — Post-Diagnostic Discussion

**Date:** 2026-04-08
**Trigger:** Diagnostic results (D1+D2) + code review (3 HIGH issues)
**Agents:** Quant, NLP, Stats, Editor (new threads, all Codex xhigh)

---

## Agent Positions

### Quant
- **"Knowledge without text memorization" is the MORE dangerous pattern** for quant pipelines. Low ROUGE reduces copyright/compliance risk but NOT alpha-leakage risk. PnL depends on direction, not wording.
- **cf_invariance=1.0 cases = red flags.** In production, downweight to zero or route to rules-based fallback. In evaluation, count as positive contamination evidence.
- **Rarity effect (p=0.016):** economically interesting — rare events (idiosyncratic shocks) are where hidden memorization drives outsized returns. But treat as lead, not conclusion.
- **Pivot direction:** from "text memorization detection" to "decision-relevant outcome leakage detection." Add portfolio-level test: do LLM signals show abnormal directional accuracy on post-cutoff vs baselines?

### NLP
- **QA=0.69, ROUGE=0.23 is "event-level contamination without article-level recall"** — adjacent to but distinct from Carlini's verbatim memorization. Right framework: Petroni et al. (2019) knowledge probes + Kandpal et al. (2022) on frequency-dependent memorization.
- **Replace single CFLS scalar with 4-cell interpretation:**
  - cf=1, para<1 → clearest red flag (reversal-specific invariance)
  - cf=1, para=1 → ambiguous (global invariance)
  - cf<1, para=1 → healthy responsiveness
  - cf<1, para<1 → general instability
- **Post ROUGE-L > pre:** likely driven by formulaic structure in later CLS telegraphs. Check length-normalized overlap, content-word-only overlap.
- **Rarity effect on impact but not direct:** test Task × Rarity interaction formally before claiming "different constructs."
- **CPT redesign:** case-specific known_outcome, within-case 4-condition design (original, placebo hint, true-outcome hint, false-outcome hint), scored by log-odds shift not just label flips.

### Stats
- **H1 fix:** Report cf_invariance as separate estimand. Flag "same-answer-everywhere" as `indeterminate`, not zero. Restrict CFLS denominator to cases where design allows discrimination.
- **Rarity p=0.016 after Holm (4 tests) → 0.064.** Not significant at familywise 5%. Report as nominal/exploratory.
- **H3 missingness: worst-case bias is large** (0.439 range under worst allocation). Fisher result is unreliable. Fix scoring logic and recompute.
- **Mann-Whitney p=0.29:** not evidence of "no effect" — only powered for moderate effects (d≈0.5). Small effects underpowered. Also: reported r=0.464 is suspicious — recompute effect size with Hodges-Lehmann.
- **Cross-task rho=0.181 (p=0.04):** fragile, vulnerable to composition effects. Need stratified re-estimation.
- **Drop CPT temporal comparison entirely.** Not valid with identical probes.

### Editor
- **The defensible paper:** "apparent leakage disappears under better diagnostics, and current probes are easy to misinterpret" — a measurement/evaluation paper, not a leakage-detection paper.
- **H1 changes headline** from "0/141 positive" to "X reversal-insensitive cases" — weakens clean null but still doesn't imply memorization.
- **H2 is not a footnote.** Either fix CPT and rerun, or remove all temporal CPT claims. Disclosing while keeping the result won't survive review.
- **Rarity p=0.016 on 1/2 tasks:** not strong enough to anchor paper alone. Keep as secondary observation.
- **Venue: ARR for EMNLP 2026/Findings** (most practical). Workshop if no new experiment. Findings long paper if CPT is fixed.
- **Minimum additional work:**
  1. Recompute CFLS with cf_invariance decomposition
  2. Drop or rerun CPT temporal analysis
  3. Add one clean article-specific memory test with non-identical probes
  4. Report effect sizes, CIs, multiple-testing, missingness
  5. Reframe contribution around probe validity

---

## Convergent Recommendations (4/4 agree)

### C1. Decompose CFLS into cf_invariance / para_invariance (4/4)
Stop reporting single CFLS scalar as headline. Use 4-cell or 2D interpretation. Flag cf_inv=1.0 cases separately.

### C2. Drop CPT temporal comparison from paper (4/4)
H2 makes it invalid. Either fix CPT design (known_outcome-based) and rerun, or remove temporal CPT claims entirely.

### C3. The "knowledge without text memorization" finding is real and important (4/4)
QA=0.69 + ROUGE=0.23 = model has event-level knowledge but no article-level recall. This is the paper's central empirical finding.

### C4. Rarity effect is exploratory, not confirmatory (4/4)
p=0.016 nominal → p=0.064 after Holm. One task only. Keep as secondary observation with caveats.

### C5. Paper reframing: evaluation/measurement paper (4/4)
"Current leakage probes conflate memorization with comprehension. Here's what each actually measures." Target: EMNLP Findings.

---

## Divergent Points

### D1. Whether to fix CPT and rerun vs. remove entirely
- **Quant, NLP:** Fix with known_outcome-based design and rerun
- **Stats:** Drop temporal comparison, use CPT only as pooled prevalence
- **Editor:** Fix and rerun if targeting Findings; remove if workshop

### D2. Effect size computation
- **Stats:** r=0.464 is suspicious, recompute with Hodges-Lehmann
- Others did not flag this

### D3. Portfolio-level validation
- **Quant:** Add downstream test (LLM signal accuracy on post-cutoff vs baselines)
- **Editor:** Out of scope for this paper (belongs in follow-up)
- NLP, Stats: Not addressed

---

## Recommended Action Plan

| Priority | Action | Effort | Rerun? |
|----------|--------|--------|--------|
| **1** | Decompose cf_invariance, recount CFLS=0 cases | 1 hour | No |
| **2** | Fix effect size (r=0.464 suspicious) | 15 min | No |
| **3** | Fix CPT: use known_outcome for pre-cutoff | 1 day | Yes (pre-cutoff only) |
| **4** | Fix H3: decouple fo_flip from other conditions | 30 min | Yes |
| **5** | Validate counterfactual quality (M1) | 2 hours | No |
| **6** | Reframe paper narrative + write | 1 week | No |
