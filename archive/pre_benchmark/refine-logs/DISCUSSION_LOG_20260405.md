# Discussion Log: Experiment Plan v1 → Proposal v2

> Session date: 2026-04-05
> Participants: User (PI) + Claude Code + 4 Codex expert agents (Quant, NLP, Stats, Editor)
> Total rounds: ~8 rounds of multi-agent debate

---

## Round 1: Experiment Plan v1 Review (4 agents)

**Input**: `refine-logs/EXPERIMENT_PLAN.md` + `EXPERIMENT_TRACKER.md`
**Output**: `refine-logs/REVIEW_QUANT.md` (6.8), `REVIEW_NLP.md` (6.5), `REVIEW_STATS.md` (7.3), `REVIEW_EDITOR.md` (7.5)
**Summary**: `refine-logs/REVIEW_SUMMARY.md`

**Key convergent issues (7 total)**:
1. EI metric implementation misaligned with proposal (ALL 4)
2. M3 conditional gate is methodologically wrong (Editor, Stats)
3. Sham control too surface-level (NLP, Editor)
4. Placebo frontier overclaimed (Quant, Editor, Stats)
5. Ground truth too LLM-centric (NLP, Quant)
6. 72-cell exact fill unrealistic (Quant, Editor)
7. Code-paper gap (NLP, Quant, Stats)

---

## Round 2: EI Edit-Magnitude Confound (4 agents)

**Trigger**: User questioned whether paraphrase baseline is subtracting noise that doesn't exist in the CF condition
**Output**: `refine-logs/DEBATE_EI_QUANT.md`, `DEBATE_EI_NLP.md`, `DEBATE_EI_STATS.md`, `DEBATE_EI_EDITOR.md`

**Consensus**: The confound is real and serious. CF edits are local (few words), paraphrases are global (full rewrite). EI > 0 could be artifact of edit-distance asymmetry, not memorization.
**Fix**: Local placebo edits matched in edit distance to CFs. Global paraphrase demoted to appendix diagnostic.

---

## Round 3: Entity Masking (4 agents)

**Trigger**: User pointed out entity-triggered memorization could make both CF and placebo stable → EI=0
**Output**: `refine-logs/DEBATE_MASKING_QUANT.md`, `DEBATE_MASKING_NLP.md`, `DEBATE_MASKING_STATS.md`, `DEBATE_MASKING_EDITOR.md`

**Consensus**: Option B (Tier1 ablation with natural substitution). Authority tasks can't be masked (destroys task). Entity masking is mechanism probe, not metric fix.

---

## Round 4: Creative Redesign (4 agents, no predefined options)

**Trigger**: User asked agents to "think out of the box"
**Output**: `refine-logs/CREATIVE_QUANT.md`, `CREATIVE_NLP.md`, `CREATIVE_STATS.md`, `CREATIVE_EDITOR.md`

**Four proposals**:
- Quant: 3×3 factorial (semantics × cue-removal), utility-vs-leakage frontier
- NLP: Task-Induced Retrieval Gain (TIRG), evidence intrusion from RAG faithfulness lit
- Stats: Randomized exposure via Qwen continued pretraining, temporal RD
- Editor: Simplify to binary contrast, 300-500 cases, 4 figures

---

## Round 5: Literature Search (2 agents)

**Output**: `refine-logs/LIT_COUNTERFACTUAL_METHODS.md` (220 lines, ~20 papers)
**Output**: `refine-logs/LIT_RETRIEVAL_TEMPORAL_METHODS.md` (253 lines, ~20 papers)

**Key novelty gaps confirmed**:
1. No same-article different-task contamination comparison in literature
2. No temporal RD in contamination literature
3. Evidence intrusion not applied to pretraining memorization (only RAG)
4. Chinese financial NLP contamination = blank
5. Li et al. Context-Faithfulness (ACL 2025) directly supports our thesis

---

## Round 6: Final Direction Synthesis (4 agents)

**Input**: Literature + all prior debate
**Output**: `refine-logs/FINAL_DIRECTION_QUANT.md`, `FINAL_DIRECTION_NLP.md`, `FINAL_DIRECTION_STATS.md`, `FINAL_DIRECTION_EDITOR.md`

**High convergence**:
- Binary contrast: direct prediction vs authority
- Benchmark: 300-500 (later restored to 1000 by PI)
- Evidence intrusion as main black-box signal
- CF-based EI demoted to secondary
- Continued pretraining: Quant/Stats want it, Editor cautious
- PI decision: small-scale CPT approved

---

## Round 7: Type A/B Memory Distinction (4 agents)

**Trigger**: PI's insight — "常识性记忆 vs 前瞻性记忆" (general knowledge vs look-ahead outcome memory)
**Output**: `refine-logs/EXPLORE_MEMORY_TYPES_QUANT.md`, `EXPLORE_MEMORY_TYPES_NLP.md`, `EXPLORE_MEMORY_TYPES_STATS.md`, `EXPLORE_MEMORY_TYPES_EDITOR.md`

**Key findings**:
- Quant: Refined to 4 buckets (A1 structural priors, A2 entity familiarity, B1 event-outcome memory, B2 task-template memory)
- NLP: Type B ≈ "item-level counterfactual memorization of event traces" (Zhang et al.)
- Stats: Article-only CPT creates familiarity (A), not outcome memory (B). Need 2×2 (article × outcome) to separate.
- Editor: This reframes paper from measurement → mechanism. Title: "Task Design Gates Look-Ahead Memory"

**CF label sensitivity rehabilitated**: General knowledge follows CF reversal, look-ahead memory doesn't → CFLS specifically detects Type B.

---

## Round 8: False-Outcome Injection (4 agents)

**Trigger**: Continued from Type A/B — how to create true Type B in CPT
**Output**: `refine-logs/EXPLORE_FALSE_OUTCOME_QUANT.md`, `EXPLORE_FALSE_OUTCOME_NLP.md`, `EXPLORE_FALSE_OUTCOME_STATS.md`, `EXPLORE_FALSE_OUTCOME_EDITOR.md`

**Key**: User proposed injecting false/illogical outcomes (e.g., "rate cut → market crashed"). If model follows false outcome on direct prediction but not authority → decisive proof.
**Stats formal estimand**: κ_t(a) = ½ E[Ỹ(a,r,t) - Ỹ(a,f,t)], paper interaction: Δ = κ_prox(1) - κ_ground(1)
**CF article edits NOT redundant** — they test inference-time text-grounding, CPT tests training-time memory. Complementary.

---

## Round 9: Alpha Value / "So What" Question (literature + 4 agents)

**Literature search**: `refine-logs/LIT_NEWS_ALPHA.md` (news-based return prediction, ~20 papers)
**Output**: `refine-logs/ALPHA_VALUE_QUANT.md`, `ALPHA_VALUE_NLP.md`, `ALPHA_VALUE_STATS.md`, `ALPHA_VALUE_EDITOR.md`

**PI's 3 scenarios**: (S1) orthogonal micro-factors → ML ensemble, (S2) distribution stabilizer, (S3) decomposition priming
**Consensus**: Paper doesn't need to prove alpha for EMNLP. Key reframing: "contaminated features are unreliable" (easy to prove) > "clean features are predictive" (hard).
**Editor**: S3 strongest for NLP venue. Quant: S2 strongest for production.

---

## Round 10: Scenario Literature Search (3 agents)

**Output**: `refine-logs/LIT_SCENARIO1_ORTHOGONAL.md` (25 papers), `LIT_SCENARIO2_STABILIZER.md` (27 papers), `LIT_SCENARIO3_PRIMING.md` (27 papers)

**Cross-domain discoveries**:
- S1: Clinical NLP already does "LLM extract concepts → ML aggregate" (CHiLL, McInerney)
- S2: Stable Prediction (Kuang et al.) is the formal S2. Anchor Regression (Rothenhäusler) is the named mechanism
- S3: Medical cognitive forcing (Mamede JAMA 2010) directly supports priming. But CoT can be unfaithful (Turpin NeurIPS 2023)

---

## Round 11: Fake Reasoning / Injected Decomposition (4 agents)

**Trigger**: PI asked — can we fake the decomposition process by injecting pre-fabricated results?
**Output**: `refine-logs/EXPLORE_FAKE_REASONING_QUANT.md`, `EXPLORE_FAKE_REASONING_NLP.md`, `EXPLORE_FAKE_REASONING_STATS.md`, `EXPLORE_FAKE_REASONING_EDITOR.md`

**NLP key insight**: For autoregressive models, if token sequence is identical, self-generated vs injected produces IDENTICAL computation. The "self vs injected" contrast doesn't exist mathematically.
**Resolution**: Replace with 3-arm design (no decomp / real decomp / sham decomp). Tests context-engineering, not "computational forcing."
**Editor**: Paper at scope limit. Top 3 experiments: benchmark + CF sensitivity + false-outcome CPT. Priming = compact appendix only.

---

## Final Output: RESEARCH_PROPOSAL_v2.md

**File**: `docs/RESEARCH_PROPOSAL_v2.md` (459 lines)
**Key changes from v1**:
- Core claim: "task design gates look-ahead memory pathways"
- Type A/B memory taxonomy
- CF Label Sensitivity as primary metric (EI formula deprecated)
- Evidence intrusion as supplementary
- Binary contrast (direct vs authority)
- False-outcome continued pretraining as causal anchor
- 3-arm priming as supplementary
- "Contaminated features are unreliable" framing
- 9 explicit [OPTION] blocks for open decisions

---

## File Index (all outputs from this session)

### Reviews
- `refine-logs/REVIEW_QUANT.md`
- `refine-logs/REVIEW_NLP.md`
- `refine-logs/REVIEW_STATS.md`
- `refine-logs/REVIEW_EDITOR.md`
- `refine-logs/REVIEW_SUMMARY.md`

### EI Metric Debates
- `refine-logs/DEBATE_EI_QUANT.md`
- `refine-logs/DEBATE_EI_NLP.md`
- `refine-logs/DEBATE_EI_STATS.md`
- `refine-logs/DEBATE_EI_EDITOR.md`

### Entity Masking Debates
- `refine-logs/DEBATE_MASKING_QUANT.md`
- `refine-logs/DEBATE_MASKING_NLP.md`
- `refine-logs/DEBATE_MASKING_STATS.md`
- `refine-logs/DEBATE_MASKING_EDITOR.md`

### Creative Redesign
- `refine-logs/CREATIVE_QUANT.md`
- `refine-logs/CREATIVE_NLP.md`
- `refine-logs/CREATIVE_STATS.md`
- `refine-logs/CREATIVE_EDITOR.md`

### Final Direction
- `refine-logs/FINAL_DIRECTION_QUANT.md`
- `refine-logs/FINAL_DIRECTION_NLP.md`
- `refine-logs/FINAL_DIRECTION_STATS.md`
- `refine-logs/FINAL_DIRECTION_EDITOR.md`

### Type A/B Memory
- `refine-logs/EXPLORE_MEMORY_TYPES_QUANT.md`
- `refine-logs/EXPLORE_MEMORY_TYPES_NLP.md`
- `refine-logs/EXPLORE_MEMORY_TYPES_STATS.md`
- `refine-logs/EXPLORE_MEMORY_TYPES_EDITOR.md`

### False-Outcome Injection
- `refine-logs/EXPLORE_FALSE_OUTCOME_QUANT.md`
- `refine-logs/EXPLORE_FALSE_OUTCOME_NLP.md`
- `refine-logs/EXPLORE_FALSE_OUTCOME_STATS.md`
- `refine-logs/EXPLORE_FALSE_OUTCOME_EDITOR.md`

### Alpha Value
- `refine-logs/ALPHA_VALUE_QUANT.md`
- `refine-logs/ALPHA_VALUE_NLP.md`
- `refine-logs/ALPHA_VALUE_STATS.md`
- `refine-logs/ALPHA_VALUE_EDITOR.md`

### Fake Reasoning / Priming
- `refine-logs/EXPLORE_FAKE_REASONING_QUANT.md`
- `refine-logs/EXPLORE_FAKE_REASONING_NLP.md`
- `refine-logs/EXPLORE_FAKE_REASONING_STATS.md`
- `refine-logs/EXPLORE_FAKE_REASONING_EDITOR.md`

### Literature Searches
- `refine-logs/LIT_COUNTERFACTUAL_METHODS.md`
- `refine-logs/LIT_RETRIEVAL_TEMPORAL_METHODS.md`
- `refine-logs/LIT_NEWS_ALPHA.md`
- `refine-logs/LIT_SCENARIO1_ORTHOGONAL.md`
- `refine-logs/LIT_SCENARIO2_STABILIZER.md`
- `refine-logs/LIT_SCENARIO3_PRIMING.md`

### Plans and Proposals
- `refine-logs/EXPERIMENT_PLAN.md` (v1, superseded)
- `refine-logs/EXPERIMENT_TRACKER.md` (v1, superseded)
- `docs/RESEARCH_PROPOSAL_v2.md` (current)
