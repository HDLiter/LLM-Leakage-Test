# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|--------|-----------|---------|------------------|-------|---------|----------|--------|-------|
| `R001` | `M0` | Re-run frozen prompt smoke and schema validation on the existing seed set. | `tests/smoke_test_prompts.py` with frozen `2026-04-05-v2` prompts | `84` seed cases | schema pass, JSON parse rate, EI computability | MUST | DONE | Existing smoke already passed; keep as regression anchor. |
| `R002` | `M0` | Build manifest-aware raw CLS ingest and verify row counts. | new benchmark ingest pipeline | full raw corpus `2020-01-01` to `2026-02-23` | row count, null rate, duplicate rate | MUST | TODO | Output `data/benchmark/cls_raw_index.parquet`. |
| `R003` | `M0` | Pilot target linking and company-day clustering on a small mixed sample. | target linker v1 + clusterer v1 | `100` pilot clusters, stratified across years | target precision, collision rate | MUST | TODO | Stop if audited precision `<0.90`. |
| `R004` | `M1` | Enrich the candidate frame with Thales topic labels and signal profiles. | Thales topic + signal profile | full reserve pool | classifier coverage, skip rate | MUST | TODO | Write `data/benchmark/cls_enriched.parquet`. |
| `R005` | `M1` | Freeze the 72-cell sampling frame and reserve queues. | stratified sampler v1 | full cluster frame | cell fill, reserve depth | MUST | TODO | Require `3 x cell_target` reserve per cell. |
| `R006` | `M1` | Draw and audit the Tier1 anchor benchmark subset. | sampler + manual audit queue | `300` Tier1 | cell fill, ambiguity rate | MUST | TODO | `4` anchor items per cell in `2020-2024`, `5` per cell in `2025+`. |
| `R007` | `M1` | Draw the Tier2 core subset after Tier1 freeze. | sampler + reserve backfill | `700` Tier2 | cell fill, reserve exhaustion | MUST | TODO | Only backfill within the same cell. |
| `R008` | `M1` | Generate neutral and targeted rewrites for Tier1. | DeepSeek rewrite generator | Tier1 originals | schema pass, first-pass QC | MUST | TODO | `6` rewrites per case. |
| `R009` | `M1` | Generate neutral and targeted rewrites for Tier2. | DeepSeek rewrite generator | Tier2 originals | schema pass, first-pass QC | MUST | TODO | Replace any case that fails required families after retry. |
| `R010` | `M1` | Run QC stages 1-4 and collect reviewer-facing diagnostics. | DeepSeek judge + Qwen judge + retrieval index + human review | all rewrites | pass rate, style distance, retrieval hits, kappa | MUST | TODO | Save all stage outputs under `data/benchmark/qc/`. |
| `R011` | `M1` | Freeze consensus labels and arbitration logs. | DeepSeek + Qwen + Codex/Claude annotators | all originals; Tier1 rewrite fields | majority rate, override rate, weighted kappa | MUST | TODO | Produces final benchmark release candidate. |
| `R012` | `M2` | Compute Qwen article familiarity with a fixed k-sweep. | `Qwen2.5-7B` vLLM logprobs | `1000` original articles | LAP at `k=10,20,30,40,50` | MUST | TODO | Primary `k=20%`; others sensitivity only. |
| `R013` | `M2` | Cache all DeepSeek base-prompt responses needed for E1-E4. | `deepseek-chat` base prompts | originals + neutral + family CF triplets | completion rate, token use | MUST | TODO | Feeds Blocks 2-4. |
| `R014` | `M3` | Run the primary leakage spectrum test on base prompts. | direct vs sentiment vs authority vs novelty, base variants | full `CLS-Leak-1000` | mean EI, bootstrap CIs, ordered contrasts | MUST | TODO | Table 3 and Figure 2. |
| `R015` | `M4` | Run matched-format ablation. | matched prompt family | full `CLS-Leak-1000` | mean EI, `base -> matched` deltas | MUST | TODO | Central reviewer requirement. |
| `R016` | `M4` | Run sham decomposition falsification. | `sham_decomposition.control` + `sham_edits` | full `CLS-Leak-1000` | EI, para stability, sham gap | MUST | TODO | Core E4 result. |
| `R017` | `M4` | Estimate temporal leakage decay and placebo frontier. | DeepSeek base outputs + publication date | `2020-2026` | spline EI, placebo mean EI | MUST | TODO | Primary placebo window `2026-01-01` to `2026-02-23`, unless API boundary changes. |
| `R018` | `M4` | Estimate cross-model concordance. | Qwen LAP vs DeepSeek EI | full `CLS-Leak-1000` | partial Spearman `rho`, cluster bootstrap CI | MUST | TODO | Table 5. |
| `R019` | `M4` | Build reviewer robustness appendix pack. | sensitivity scripts | full `CLS-Leak-1000` | k-sweep table, paraphrase distributions, article/cluster Ns | MUST | TODO | Must exist before paper freeze. |
| `R020` | `M5` | Export paper-ready tables and figures with cluster counts in every table. | stats + plotting scripts | full `CLS-Leak-1000` | reproducibility pass, figure checksum | MUST | TODO | Lock all main-paper visuals. |
| `R021` | `M5` | Run mixed-effects heterogeneity analysis. | E5 mixed-effects / exploratory DIF | full `CLS-Leak-1000` | variance components, FDR-adjusted subgroup effects | NICE | TODO | Appendix only. |
| `R022` | `M5` | Run downstream XGBoost sensitivity analysis. | E6 raw vs orthogonalized features | 3-day horizon holdout | rank IC, alpha decay, interaction term | NICE | TODO | Do not block submission on this run. |
