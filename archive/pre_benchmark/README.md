# Pre-Benchmark Archive

Archived 2026-04-16. These files are from Phase 1-4 of the project (2026-04-05 to 2026-04-12), before the pivot to a factor-driven benchmark paper. They document the evolution from a single-model memorization detection paper through multi-agent review, pilot experiments, bug audits, and the eventual data-centric pivot.

## What happened in Phase 1-4

- **Phase 1 (Apr 5-6)**: Research proposal, multi-agent debate (EI confound, masking, memory types, fake reasoning), 3 review rounds, literature searches. Produced RESEARCH_PROPOSAL v1 and v2.
- **Phase 2 (Apr 6-8)**: E_pilot implementation, diagnostic expansion to 192 cases. CFLS generalization confound discovered.
- **Phase 3 (Apr 9-11)**: deep-floating-lake v3 — 682-case stratified run. "Too clean null" triggered bug audit.
- **Phase 4 (Apr 11)**: amber-mirror-lattice — 5-bug audit, fix, rerun. Bug 3 fix revealed memorization-direction association in decomposed_impact, but CFLS still non-diagnostic.
- **Phase 5 pivot (Apr 12)**: Qwen baseline failed to replicate DeepSeek patterns. Paper direction pivoted from "single-model memorization detection" to "FinMem-Bench: factor-controlled cross-model benchmark."

## Why these are archived

The benchmark pivot (Phase 5) and subsequent R5A design cycle fundamentally changed what the paper is about. The four-layer framework (Factor/Perturbation/Operator/Estimand) replaced the old "detector pool" framing. These documents preserve the intellectual history but are no longer operationally relevant.

## Directory structure

```
docs/                   — proposals, reviews, decisions, pilot results
refine-logs/            — multi-agent debates, explorations, literature searches
  pilot_discussion/     — Phase 2 pilot result discussions (3 rounds)
  decision_20260411/    — Phase 4→5 decision session (CPT design, agent reviews)
plans/                  — completed execution plans (amber, deep-floating-lake, gentle-bouncing-wozniak)
root/                   — AGENTS.md (old agent definitions), AUTO_REVIEW.md (old review record)
```

## Key findings carried forward

These findings from Phase 1-4 directly shaped the benchmark design:

1. **CFLS measures reading comprehension, not memorization** (Phase 2-4) — motivated the move away from CFLS-based metrics to perturbation-based estimands
2. **False outcome resistance shows memorization signal** (Phase 4, Bug 3 fix) — became C_FO perturbation and E_FO estimand in the framework
3. **Entity masking as probe, not fix** (Phase 1 debate) — became C_anon perturbation with multi-level dose-response
4. **Task design gates memory access** (Phase 1-2) — became the operator layer (P_logprob vs P_predict vs P_extract)
5. **Need for positive control / known-memorized items** (Phase 2 consensus) — became the Qwen CPT causal anchor
6. **Cross-model replication needed** (Phase 5 Qwen baseline) — became the 9-model fleet with cutoff structure

## Current pipeline

See `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` for the authoritative scope document.
