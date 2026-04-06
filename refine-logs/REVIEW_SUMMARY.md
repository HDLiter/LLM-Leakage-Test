# Experiment Plan Review Summary

> **Round 1** — 2026-04-05
> 4 independent Codex reviewers
> Input: EXPERIMENT_PLAN.md + EXPERIMENT_TRACKER.md + full project context

## Scores

| Reviewer | Score | Verdict |
|----------|-------|---------|
| Quant    | 6.8   | Good measurement paper, weak quant endpoint |
| NLP      | 6.5   | Core metric not yet operationalized correctly |
| Stats    | 7.3   | Close to defensible, inference protocol incomplete |
| Editor   | 7.5   | Conditionally supportive for EMNLP Findings |

**Average: 7.0/10**

## Convergent Issues (3+ reviewers)

### I1. EI metric implementation misaligned with proposal (ALL 4)
- `_extract_label()` only recognizes `direction`, falls back to confidence for other tasks
- No field-level changed/unchanged logic for multi-field decomposed tasks
- No cluster-level aggregation
- Confidence normalization bug ([0,100] vs [0,1])

### I2. M3 conditional gate is methodologically wrong (Editor, Stats)
- "Proceed only if ordering looks promising" = selective execution
- Robustness must run unconditionally

### I3. Sham control too surface-level (NLP, Editor)
- Lexical features (formality, numeric_density, sentence_complexity) not matched on abstraction
- Does not test "generic extraction burden" vs "meaningful decomposition"

### I4. Placebo frontier overclaimed (Quant, Editor, Stats)
- API version upgrade date != training data cutoff
- Should be "false-positive stress test", not "knowledge frontier"

### I5. Ground truth too LLM-centric (NLP, Quant)
- DeepSeek is both evaluated model and annotator
- Tier1 needs full human annotation

### I6. 72-cell exact fill unrealistic (Quant, Editor)
- Reserve backfill creates curation bias toward "easy" cases
- Post-stratification weights better than forced exact fill

### I7. Code-paper gap (NLP, Quant, Stats)
- experiment.py uses legacy runner, not frozen prompts
- Seed set lacks target/target_type
- Schema version label still says v1

## Unique Insights by Reviewer

### Quant
- Answerability/coverage screening needed (short telegraphs → many "unclear" = fake low leakage)
- Sector/index prominence proxy economically wrong
- E6 needs tradability protocol (T+1, price limits, halts, costs)
- Split target universes (company vs sector vs index)

### NLP
- Base prompt structure inconsistent (flat strings vs field-linked evidence objects)
- Schema validation checks shape but not grounding (target_echo, evidence substring)
- Sham should be target-conditioned, evidence-based, economically irrelevant
- Need inferability/difficulty human ratings as control

### Stats
- Primary estimand hierarchy needs formal gatekeeping/closed testing
- Pilot MDE calculation needed before committing to thresholds
- Placebo should use equivalence test, not "near-zero"
- Partial Spearman fragile with ties; add Kendall τ_b sensitivity
- Selection on QC-passable rewrites = conditioning on latent variable

### Editor
- C2 should be supporting, not co-primary
- Timeline internally inconsistent (10.5 days vs M1 3-4 days)
- Cross-family edit calibration study needed
- Paper viable as C1-only EMNLP Findings

## Individual Reviews
- [REVIEW_QUANT.md](REVIEW_QUANT.md)
- [REVIEW_NLP.md](REVIEW_NLP.md)
- [REVIEW_STATS.md](REVIEW_STATS.md)
- [REVIEW_EDITOR.md](REVIEW_EDITOR.md)
