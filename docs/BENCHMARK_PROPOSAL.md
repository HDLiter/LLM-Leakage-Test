# FinMem-Bench: Initial Proposal

**Date:** 2026-04-12
**Status:** Draft for multi-agent review
**Motivation:** Methodological issues identified in Phase 4-5 pilot experiments

---

## Problem

The current 606-case benchmark has three structural weaknesses that limit the
reliability of any memorization-related inference:

1. 41% of cases lack verified outcomes, forcing FO probes to use generic templates
2. Distributional imbalance across key strata (e.g., up:down = 5.3:1 in some cells)
3. Cells too small for stable estimates after factor crossing

These are not fixable by adding a few cases. The benchmark needs to be rebuilt
around the factors that matter.

## Core Idea

Build a **factor-controlled, cross-lingual benchmark** for probing training data
memorization in financial LLMs. The benchmark itself is the primary contribution;
experiments on specific models demonstrate its utility.

- **~2000 Chinese cases** from 1M+ CLS telegraph corpus
- **~2000 English cases** from public financial news + stock price data
- Every case has: article + verified outcome + semantic reversal + false outcome
- Balanced across key factors with minimum cell sizes

## Factor Taxonomy

Factors hypothesized to influence memorization detectability:

| Factor | Levels | Rationale |
|---|---|---|
| **Temporal proximity** | pre/post training cutoff | Core memorization variable |
| **Anchor strength** | strong / weak | How uniquely identifiable the event is |
| **Corpus frequency** | singleton / periodic / frequent | How often similar content appeared in training |
| **Outcome direction** | up / down | Controls for directional asymmetry in FO probes |
| **Target type** | company / sector / index | Controls for entity specificity |
| **Source credibility** | high / low | May interact with authority task |

## Quality Gates (per case)

Every case must have:
- [ ] Article with substantive content (>50 chars), clear target, not a stub
- [ ] Verified known_outcome with direction + magnitude + traceable source
- [ ] LLM-generated semantic reversal (direction-flipped), schema-validated
- [ ] LLM-generated false outcome (3 variants: train / eval / reserve)
- [ ] Factor annotations (anchor, frequency, target_type, credibility)

No generic/template FO probes. If a case cannot produce a verified outcome,
it does not enter the benchmark.

## Balance Targets

~2000 cases per language. Minimum cell size after crossing key factors:

| Cross | Target minimum per cell |
|---|---|
| direction × anchor | ≥ 400 per cell (4 cells) |
| direction × target_type | ≥ 200 per cell (6 cells) |
| period × direction × anchor | ≥ 100 per cell (8 cells) |
| Full 5-way cross (finest grain) | ≥ 30 per cell |

The 1M+ CLS corpus and abundant English financial news sources make these
targets feasible at 0.2% selection rate.

## Probe Protocol (per case, per model)

Three tasks, four conditions each:

| Task | What it measures | Primary metric |
|---|---|---|
| direct_prediction | Outcome-proximal suggestibility | fo_flip_hedged |
| decomposed_impact | Outcome-proximal (structured) | fo_flip_hedged |
| decomposed_authority | Evidence-grounded anchor | fo_any_change |

Conditions: original, semantic_reversal, neutral_paraphrase, false_outcome

## Models

| Model | Chinese | English | CPT possible | Cutoff known |
|---|---|---|---|---|
| DeepSeek-chat | yes | yes | no (closed) | approximate |
| Qwen 2.5 7B | yes | yes | yes (LoRA) | approximate |
| Llama 3 8B | limited | yes | yes (LoRA) | exact |
| GPT-4o | yes | yes | no (closed) | documented |

CPT construct validation on Qwen (Chinese) and Llama (English) provides
language × model 2×2 causal evidence.

## Paper Framing

**Data-centric:** The benchmark is the primary contribution. Experiments on
4+ models demonstrate utility and reveal cross-model/cross-lingual patterns.

Tentative structure:
1. Introduction + motivation
2. Benchmark design (factor taxonomy, collection pipeline, quality assurance)
3. Probe methodology (tasks, conditions, metrics)
4. Experiments (baseline runs + CPT validation)
5. Results (factor-level, model-level, language-level, probe-level)
6. Discussion + benchmark release

## Relation to Current Work

- Phase 4 DeepSeek results + Phase 5 Qwen baseline become **pilot study**
  that motivates benchmark design decisions (Section 2)
- CPT experiment design (Phase D-E) carries over unchanged
- `--cutoff-date` pipeline enhancement already done

## Open Questions for Review

1. Is 2000+2000 the right scale, or should we go larger?
2. English data source selection: SEC EDGAR vs Kaggle vs news API?
3. Should corpus frequency be continuous or binned?
4. How to handle models with unknown cutoffs (DeepSeek)?
5. Is the 3-task probe protocol sufficient, or add more task types?
6. Timeline feasibility for EMNLP 2026 ARR (May 25 deadline)?

---

*This proposal is intentionally kept at outline level. Detailed spec to be
developed after multi-agent review in a follow-up session.*
