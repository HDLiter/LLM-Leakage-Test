# Discussion Log: Proposal v2 Review (Multi-Model Convergence)

> Session date: 2026-04-06
> Participants: 4 Codex domain agents (Quant/NLP/Stats/Editor) + 1 Claude Cross-Model Challenger
> Orchestrator: Claude Code
> Total rounds: 2 (Round 1 independent review → Challenger → Round 2 cross-model response)

---

## Round 1: Independent Review by 4 Codex Agents

**Input**: `docs/RESEARCH_PROPOSAL_v2.md` + full project file index
**Method**: Each agent given only role identity + file index, free to explore any project files

**Scores**: Quant 8.1 | NLP 8.2 | Stats 8.0 | Editor 8.1

**Output files**:
- `refine-logs/REVIEW_V2_QUANT.md`
- `refine-logs/REVIEW_V2_NLP.md`
- `refine-logs/REVIEW_V2_STATS.md`
- `refine-logs/REVIEW_V2_EDITOR.md`

### Round 1 Convergent Issues (4/4 agreement)

1. **Inferability confound is #1 threat** — authority is inherently more text-internal; without inferability control, Delta_CFLS may measure "which task is easier to answer from text" not "which task leaks less"
2. **Code-paper gap is serious** — metrics.py still uses legacy EI, experiment.py is old runner, target/target_type not wired
3. **Coverage/abstention must be reported separately** — otherwise reviewer will say authority just outputs "unclear" more
4. **target_type (company/sector/index) should be stratified** — not mixed into one headline estimand
5. **"Same article, different task" is the strongest design element** — universally praised

### Round 1 OPTION Consensus

| OPTION | Quant | NLP | Stats | Editor |
|--------|-------|-----|-------|--------|
| Inferability | A | A | A | A |
| CFLS scoring | C | C | C | C |
| Evidence intrusion | C | C | C | C |
| Venue | A | A | A | A |
| CPT design | C | C | C (prefer B) | C |
| Outcome block | C | C | C | C |
| Core narrative | **B** | A | A | A |
| Temporal | A | **C** | A | **C** |
| Utility | **B** | **C** | B→C | **C** |

### Round 1 Divergences
- Core narrative: Quant wanted sentiment as bridge (B), others wanted binary only (A)
- Temporal: Split 2-2 between A (Qwen+DS stress) and C (Qwen only)
- Utility: Split between B (light financial) and C (appendix only)

---

## Challenger Round: Claude Cross-Model Challenger

**Input**: Proposal v2 + all 4 Codex reviews
**Role**: Find groupthink blind spots, stress-test strongest consensus, propose novel attack angles

**Score**: 7.4/10 (0.6-0.8 lower than Codex agents)

**Output file**: `refine-logs/REVIEW_V2_CHALLENGER.md`

### 4 Groupthink Blind Spots Identified

1. **CFLS construct validity never questioned** — Different tasks use completely different CF templates (semantic_reversal vs provenance_swap). Delta_CFLS may measure "which rewrite is more detectable" not "which task leaks less". This is deeper than the inferability confound.

2. **CLS telegraph-style text specificity underestimated** — Extremely short texts (median ~95-136 chars) make "local rewrite" almost a full rewrite; authority task may degrade to template matching; cross-site near-duplicates make nonexistence check nearly useless.

3. **Instruction-following compliance treated as transparent** — Different tasks may have different instruction compliance rates, confounding CFLS differences with prompt-induced response style.

4. **Qwen 7B → DeepSeek V3 cross-scale extrapolation unquestioned** — ~100x parameter difference; causal anchor's external validity dubious.

### 5 Most Likely Reject Reasons

1. Conclusion near-tautological ("asking about price direction is obviously more vulnerable to price memory")
2. Different CF templates make Delta_CFLS uninterpretable
3. Single model + single language + single corpus = no generalizability
4. CPT anchor's internal and external validity simultaneously questionable
5. Benchmark researcher degrees of freedom too large, no pre-registration

### Most Underestimated Risk
**Experiment succeeds but result is unsurprising → "limited novelty" reject**

### Challenger's Divergence Rulings
- Core narrative: A (binary only)
- Temporal: C (Qwen only)
- Utility: C (appendix only)

---

## Round 2: Codex Agents Respond to Challenger

**Input**: Challenger report + own Round 1 review
**Task**: Respond to 5 attacks, propose fixes, revise score

**Revised Scores**: Quant 7.7 | NLP 7.6 | Stats 7.5 | Editor 7.7

**Output files**:
- `refine-logs/ROUND2_QUANT.md`
- `refine-logs/ROUND2_NLP.md`
- `refine-logs/ROUND2_STATS.md`
- `refine-logs/ROUND2_EDITOR.md`

### Attack-by-Attack Convergence

| Attack | Quant | NLP | Stats | Editor | Verdict |
|--------|-------|-----|-------|--------|---------|
| A: CFLS construct validity | Partial agree (high priority) | Agree (mostly) | Largely agree → primary risk | Partial agree→agree | **Upgrade to primary identification risk** |
| B: Tautological | Partial agree | Partial agree | Partial agree | Partial agree | **Not strict tautology, but novelty risk is real** |
| C: CLS telegraph | Partial agree (cross-site: strongly) | Largely agree | Partial agree (3 parts) | Largely agree | **Short text + authority template matching = real; cross-site serious but not fatal** |
| D: Qwen→DS extrapolation | Partial agree | Partial agree→agree | Partial agree | Agree | **Scope claims carefully; add lightweight replication** |
| E: Limited novelty | Agree | Strongly agree | Agree | Agree | **Most underestimated risk; consensus strongest here** |

### Converged Remediation Plan (Priority Order)

#### P0: Must Do Before Scaling

1. **Template-comparability pilot (50-100 cases)** — Quantify per-template human label-flip agreement, changed-span ratio, edit distance, blinded detectability, QC pass rate. This is the #1 gate.

2. **Same-template bridge task** — Add `decomposed_impact` with `semantic_reversal` to main comparison, enabling same-CF-template cross-task comparison alongside the primary direct-vs-authority contrast.

3. **Claim downgrade** — Main conclusion should be "prompt-task-template bundle effect" unless pilot proves cross-template comparability. If proven, can upgrade to "task pathway effect."

4. **False-outcome CPT → core piece** — Promote from optional enhancement to novelty-bearing core component. Without it, paper is "careful but unsurprising."

5. **Pilot gate three conditions** — Before scaling to 1000: (a) cross-template comparability passes; (b) authority shows non-zero but lower leakage (not zero); (c) false-outcome arm shows clean task-gated sign-flip on small scale.

#### P1: High Priority Fixes

6. **Authority cue baseline** — Run regex/rule-based extraction on authority task. If rules score high, authority can't be sold as "evidence-grounded reasoning."

7. **Cross-site duplicate audit** — Expand Stage 3 beyond CLS to Eastmoney, Sina Finance, announcement sites, search engine top-K.

8. **Coverage/abstention as mandatory diagnostic** — Pre-register alongside CFLS; report answerable-subset sensitivity.

9. **Narrative reframe** — From "direction" to "degree, boundary conditions, and residual failure modes." Contribution is quantification and mechanism shape, not binary direction.

#### P2: Important but Lower Priority

10. **Lightweight second-model behavioral replication** — 50-100 cases on a second model (even without CPT) significantly reduces external validity attack.

11. **Length stratification** — All results must be reported by text-length bins and changed-span ratio bins.

12. **Minimum-length or max-edit-ratio threshold** — For ultra-short texts where "local rewrite" becomes near-total rewrite.

13. **Inferability + coverage + abstention three-piece set** — All pre-registered together.

### Final OPTION Decisions (All 9 Converged)

| OPTION | Decision | Agreement |
|--------|----------|-----------|
| Inferability control | **Option A** (Tier 1 human annotation, mandatory) | 5/5 |
| CFLS scoring | **Option C** (primary+protected main, strict-only appendix) | 5/5 |
| Evidence intrusion | **Option C** (narrow main, four-bucket appendix) | 5/5 |
| Temporal analysis | **Option C** (Qwen boundary only, DeepSeek descriptive only) | 5/5 (Round 2) |
| Core narrative | **Option A** (binary: direct_prediction vs decomposed_authority only) | 5/5 |
| CPT design | **Option C** (4-run compromise, false-outcome must be kept) | 5/5 |
| Outcome block | **Option C** (direction + magnitude bucket, no rationale) | 5/5 |
| Utility study | **Option C** (appendix only, unless core results very clean) | 5/5 (Round 2) |
| Venue | **Option A** (Findings of EMNLP baseline) | 5/5 |

---

## Score Trajectory

| Agent | Round 1 | Round 2 | Delta |
|-------|---------|---------|-------|
| Quant | 8.1 | 7.7 | -0.4 |
| NLP | 8.2 | 7.6 | -0.6 |
| Stats | 8.0 | 7.5 | -0.5 |
| Editor | 8.1 | 7.7 | -0.4 |
| Challenger | — | 7.4 | — |
| **Mean** | **8.1** | **7.6** | **-0.5** |

All agents note scores can recover to ~8.0 if P0 remediation is implemented.

---

## Key Takeaways

### What's Strong
- "Same article, different task" paired design is genuinely valuable
- Type A/B memory taxonomy is useful framing
- CFLS > old EI (within-task, not yet proven cross-task)
- Honest risk assessment and bounded claims
- Chinese financial NLP gap is real

### What Must Change
- CFLS cross-task comparability is unproven and potentially fatal
- Novelty risk requires shifting from "direction" to "mechanism shape"
- False-outcome CPT must be core, not optional
- Authority task needs cue baseline validation
- Cross-site deduplication needed
- Pilot-first, scale-second strategy

### Most Important Next Step
**Run 50-100 case template-comparability pilot before anything else.** This determines whether the core identification strategy is viable or needs fundamental redesign.

---

## File Index (all outputs from this session)

### Round 1 Reviews
- `refine-logs/REVIEW_V2_QUANT.md`
- `refine-logs/REVIEW_V2_NLP.md`
- `refine-logs/REVIEW_V2_STATS.md`
- `refine-logs/REVIEW_V2_EDITOR.md`

### Challenger Report
- `refine-logs/REVIEW_V2_CHALLENGER.md`

### Round 2 Responses
- `refine-logs/ROUND2_QUANT.md`
- `refine-logs/ROUND2_NLP.md`
- `refine-logs/ROUND2_STATS.md`
- `refine-logs/ROUND2_EDITOR.md`

### This Log
- `refine-logs/DISCUSSION_LOG_20260406.md`

---

## Cross-Domain Literature Search

**Trigger**: PI's insight that different CF templates (semantic_reversal vs provenance_swap) test fundamentally different memory types; source/provenance memory is likely very weak in LLMs.

**4 parallel Codex agents** searched across NLP/ML, Cognitive Psychology, Finance, and Mechanistic Interpretability.

**Output files**:
- `refine-logs/LIT_MEMORY_TAXONOMY_NLP.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_COGSCI.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_FINANCE.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_MECHINTERP.md`

**Key cross-domain findings**:
1. LLM memory is at least 5 types: event-outcome, entity-association, source/provenance (very weak), temporal/regime, cross-event spillover
2. Source/provenance memory barely exists in parameters (4/4 domains agree)
3. Entity prior is the strongest leakage channel, not event-outcome
4. Time is a steerable latent variable, not a fixed cutoff
5. 26 new papers downloaded, `PAPER_INDEX.md` created (60 total)

---

## Temporal Directionality Analysis

**Trigger**: PI's question about backward (legitimate) vs forward (illegitimate) memory asymmetry, and whether the Thales one-size-fits-all year-stripping approach is necessary.

**Output**: `refine-logs/EXPLORE_TEMPORAL_DIRECTIONALITY.md`

**Key findings**:
1. Three-axis taxonomy proposed: exposure time, reference time, path role
2. Legitimacy depends on `exposure time`, not `reference time` — "retrospective contamination" is real
3. Backward memory not inherently legitimate (hindsight narrative contamination)
4. Gold standard: `point-in-time recoverability`, not "content talks about the past"
5. Leakage redefined as: `dependence on info not recoverable from C≤τ`
6. Solution spectrum from full stripping to ideal temporal cutoff; PIT-RAG + grounding audit is the practical sweet spot

---

## Round 3: Framework Rethink (4 Codex Agents)

**Input**: All accumulated materials (proposal + 2 review rounds + challenger + 4 lit searches + temporal analysis)
**Method**: New Codex threads, full file index, free exploration

**Output files**:
- `refine-logs/ROUND3_QUANT.md`
- `refine-logs/ROUND3_NLP.md`
- `refine-logs/ROUND3_STATS.md`
- `refine-logs/ROUND3_EDITOR.md`

### Round 3 Convergence (4/4 unanimous on all 5 topics)

**1. Type A/B → Three-axis Taxonomy**
- Temporal admissibility: can it be recovered from C≤τ?
- Memory object: event-outcome / entity prior / article overlap / provenance / regime / task-template
- Path role: support grounding vs shortcut to answer
- Type A/B demoted to shorthand for path role axis only

**2. Entity Prior → Independent Secondary Estimand**
- Named "entity-cue dependence", not just a covariate
- Entity masking, ticker anonymization, neighbor-entity substitution
- Stratify by head-tail prominence, target_type
- Qwen familiarity: original vs entity-masked comparison

**3. CFLS Fix: Switch Primary Contrast**
- New primary: `direct_prediction` vs `decomposed_impact` (same template: `semantic_reversal`)
- `authority` demoted to secondary assay (mainly for evidence intrusion)
- CFLS reinterpreted as "article-responsiveness / shortcut susceptibility"
- Claim: "prompt-task-template bundle effect" unless pilot proves cross-template comparability

**4. Leakage Redefinition**
- `dependence on information not recoverable from C≤τ`
- Two layers: narrow "look-ahead leakage" + broad "text-external shortcutting"
- CFLS ≈ shortcut susceptibility; evidence intrusion + false-outcome CPT = high-precision leakage evidence

**5. Scope: Narrower but Stronger**
- Paper spine: PIT recoverability definition + same-template bridge + false-outcome CPT + intrusion audit + entity prior secondary
- Authority/novelty/sentiment/utility → appendix
- Findings of EMNLP baseline; main track requires bridge + clean sign-flip + second model

**6. Immediate Priority: Hard Pilot**
- 50-100 cases, validating template comparability, effect shape, and scoring pipeline
- Theory is ahead of implementation — code still on legacy EI/runner

---

## Session Summary

### Overall Arc
1. **Round 1** (4 Codex): Independent review of proposal v2 → avg 8.1/10
2. **Challenger** (Claude): Identified 4 groupthink blind spots → 7.4/10
3. **Round 2** (4 Codex responding to Challenger): All scores dropped → avg 7.6/10
4. **Cross-domain lit search** (4 Codex): 5 memory types, provenance memory near-zero, 26 papers downloaded
5. **Temporal directionality** (Quant Codex): Three-axis taxonomy, PIT recoverability definition
6. **Round 3** (4 Codex): Framework rethink → unanimous convergence on all 5 restructuring decisions

### Decisions Made
- All 9 [OPTION] blocks from proposal v2 resolved (Round 2)
- Type A/B → three-axis taxonomy
- Primary contrast → direct_prediction vs decomposed_impact (same-template)
- Leakage → "dependence on info not recoverable from C≤τ"
- Entity prior → independent secondary estimand
- False-outcome CPT → core piece (not optional)
- Next step: 50-100 case hard pilot

### File Index (all outputs from this session)

#### Round 1 Reviews
- `refine-logs/REVIEW_V2_QUANT.md`
- `refine-logs/REVIEW_V2_NLP.md`
- `refine-logs/REVIEW_V2_STATS.md`
- `refine-logs/REVIEW_V2_EDITOR.md`

#### Challenger Report
- `refine-logs/REVIEW_V2_CHALLENGER.md`

#### Round 2 Responses
- `refine-logs/ROUND2_QUANT.md`
- `refine-logs/ROUND2_NLP.md`
- `refine-logs/ROUND2_STATS.md`
- `refine-logs/ROUND2_EDITOR.md`

#### Literature Searches
- `refine-logs/LIT_MEMORY_TAXONOMY_NLP.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_COGSCI.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_FINANCE.md`
- `refine-logs/LIT_MEMORY_TAXONOMY_MECHINTERP.md`

#### Temporal Directionality
- `refine-logs/EXPLORE_TEMPORAL_DIRECTIONALITY.md`

#### Round 3 Framework Rethink
- `refine-logs/ROUND3_QUANT.md`
- `refine-logs/ROUND3_NLP.md`
- `refine-logs/ROUND3_STATS.md`
- `refine-logs/ROUND3_EDITOR.md`

#### Paper Index
- `PAPER_INDEX.md` (60 papers, 26 newly downloaded)
