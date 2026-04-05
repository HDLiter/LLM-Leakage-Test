# Pilot Phase Archive

Archived 2026-04-05. These notebooks and scripts are from the initial exploratory phase (84 test cases, hardcoded prompts, PC/CI/IDS metrics). They are preserved as reference but are NOT part of the current experimental pipeline.

## Notebooks (00-06)
- `00_data_prep.ipynb` — Load 42 test cases, generate counterfactual variants
- `01_memorization_audit.ipynb` — Memorization probe evaluation (72% avg memorization)
- `02_counterfactual.ipynb` — 4 strategies × 2 variant types × 42 cases, PC/CI/IDS metrics
- `03_ablation.ipynb` — Masking ablation (year→entity→numbers→sector) + placebo test
- `04_output_format.ipynb` — Binary/scalar/5-bin/free-text format comparison (leakage differs by format)
- `05_mitigation_compare.ipynb` — Best mitigation combo: year-masking + role-play + CoT
- `06_prompt_optimization.ipynb` — DSPy MIPROv2 optimization (L=-4.496, accuracy 84.6%)

## Scripts
- `run_all_notebooks.py` — Batch notebook runner
- `benchmark_concurrency.py` — Concurrency benchmark for API calls

## Key findings carried forward
- Baseline leakage is high (PC=0.119)
- Output format affects leakage profile (notebook 04) → justifies enum over float in new schema
- Masking + role-play + CoT reduces leakage (notebook 05) → informs prompt design
- DSPy optimization works but risks overfitting (notebook 06) → prompt frozen, no optimization in new design

## Current pipeline
See `config/prompts/` (frozen schema v2) and `src/prompt_loader.py` for the new experimental infrastructure.
