# Pre-R5A `src/` archive

Snapshot of the single-model Phase 0-5 code that lived under `src/`,
`tests/`, and `scripts/` before the R5A measurement stack was scaffolded.

## When this was archived

2026-04-26, as part of WS0 of `plans/phase7-pilot-implementation.md`.

## Why

Plan §3.1: the Phase 7 pilot builds a parallel `src/r5a/` namespace
with frozen contracts (4-layer measurement framework, 9-model fleet,
two-stage pre-registration). Mutating the legacy single-model pipeline
into the new shape would have created merge friction and hidden task
leakage. Keeping the legacy modules as live imports under `src/` would
have invited new code to depend on them. Moving them here makes the
boundary explicit.

## What's here

```
src/        news_loader, experiment, prompts, display_utils,
            prompt_loader, models, masking, llm_client, metrics, pilot
tests/      smoke_test_prompts, test_failure_isolation
scripts/    run_diagnostic_1, run_diagnostic_2, rescore_fo_flip
            (the only `scripts/` files that import from old `src.*`;
             other Phase 0-5 scripts that don't depend on old `src.*`
             remain in `scripts/` for now)
```

The `config/prompts/` legacy assets (`task_prompts.yaml`,
`counterfactual_templates.yaml`, `schema_validation.py`,
`README.md`) are intentionally **not** archived — `R5A_OPERATOR_SCHEMA.md`
§1 explicitly retains them as reference material.

`data/` results from prior phases were archived separately under
`archive/{benchmark_r1_r3,pilot_phase,pre_benchmark,r4_r5a_lineage}/`
in commits `60bcff5` and earlier.

## Reuse policy

Read these modules to understand prior decisions, lift small utility
functions if needed (e.g. `extract_json_robust`), but do **not** import
from `archive.pre_r5a_src.*` in new code under `src/r5a/`. Reimplement
the relevant logic with the new contracts instead.
