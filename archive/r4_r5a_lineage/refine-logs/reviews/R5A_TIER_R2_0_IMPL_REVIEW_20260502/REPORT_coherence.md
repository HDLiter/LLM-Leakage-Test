# Lens E — Doc / docstring / comment / coherence

## Cold-read first impressions
The rename is mostly coherent in the main Path E flow, but several reader-facing edges still mix old and new vocabulary: `cutoff` remains in some operational guidance, `FO` remains in at least one output field label, and some CLI help omits mode-specific requirements that the code enforces. The highest-risk docs are not prose-only files; they are schema docstrings, JSON field names, and PENDING operational instructions an operator may follow during cloud spend.

## Novel findings
- [HIGH] `PENDING.md` still tells the cloud operator to compute a git-blob SHA for `tokenizer.json`, which conflicts with the new decision-#4 SHA-256 content-hash semantics documented in the fleet/pinner/contract. Cite: `PENDING.md:24`, `config/fleet/r5a_fleet.yaml:35`, `scripts/ws1_pin_fleet.py:23`, `src/r5a/contracts.py:458`.
- [MED] `planning_power_calculator.py` labels the estimand as `E_OR_E_NoOp_beta_cutoff` but still emits `fo_eligibility`, leaving a retired FO label in the planning JSON surface. Cite: `scripts/planning_power_calculator.py:355`, `scripts/planning_power_calculator.py:392`.
- [MED] `LogProbTrace` docstring says v2.0 introduces `top_alternative_token_ids`, but the schema/commentary says token IDs are not persisted and only `top_alternative_logprobs` exists. Cite: `src/r5a/contracts.py:236`, `src/r5a/contracts.py:265`, `src/r5a/contracts.py:268`.
- [MED] `ExposureHorizonEstimate.p_drop_gt_005` is a fixed-threshold field label, but `detect_exposure_horizon()` accepts configurable `drop_threshold` and computes the probability against that configured value. Cite: `src/r5a/analysis/exposure_horizon.py:79`, `src/r5a/analysis/exposure_horizon.py:286`, `src/r5a/analysis/exposure_horizon.py:412`.
- [MED] The pinner docstring says the pinning log append is "best-effort" and can be added by hand, but the implementation raises on corrupt/non-array logs after writing the fleet file. Cite: `scripts/ws1_pin_fleet.py:42`, `scripts/ws1_pin_fleet.py:493`, `scripts/ws1_pin_fleet.py:515`.

## Anchored findings
- [MED] `build_cutoff_probe_set.py` module docstring says 24 months / about 1,440 articles, while the defaults and downstream analyzer describe 36 months / 2,160 cases. Cite: `scripts/build_cutoff_probe_set.py:4`, `scripts/build_cutoff_probe_set.py:52`, `scripts/run_exposure_horizon_analysis.py:15`.
- [MED] `run_exposure_horizon_analysis.py --drop-threshold` help says the bootstrap fraction is "reported alongside the estimate," but the threshold also controls acceptance/rejection of `horizon_observed`. Cite: `scripts/run_exposure_horizon_analysis.py:119`, `scripts/run_exposure_horizon_analysis.py:122`, `src/r5a/analysis/exposure_horizon.py:292`, `src/r5a/analysis/exposure_horizon.py:421`.
- [MED] Finalizer CLI help is not self-contained for confirmatory requirements: `--exposure-horizon`, `--vllm-image-digest`, and `--gpu-dtype` have no explanatory help even though confirmatory mode rejects missing/malformed values. Cite: `scripts/ws1_finalize_run_manifest.py:105`, `scripts/ws1_finalize_run_manifest.py:116`, `scripts/ws1_finalize_run_manifest.py:117`, `scripts/ws1_finalize_run_manifest.py:468`, `scripts/ws1_finalize_run_manifest.py:533`.
- [MED] `ws1_run_logprob.py --vllm-image-digest` help says only "Docker image SHA ... recorded into trace," but pilot and exposure-horizon modes require `sha256:<64-hex>`. Cite: `scripts/ws1_run_logprob.py:103`, `scripts/ws1_run_logprob.py:214`, `scripts/ws1_run_logprob.py:247`.
- [HIGH] `RunManifest` docstring still presents the 2026-04-29 field set as `cutoff_observed` and says downstream pairs it with `cutoff_date_yaml`, even though the actual schema field is now `exposure_horizon_observed`. Cite: `src/r5a/contracts.py:390`, `src/r5a/contracts.py:392`, `src/r5a/contracts.py:396`, `src/r5a/contracts.py:474`.
- [MED] A stale `cutoff_probe/` path remains in modified PENDING guidance for Path E, while the implementation now writes `data/pilot/exposure_horizon/`. Cite: `PENDING.md:37`, `scripts/build_cutoff_probe_set.py:45`.
- [LOW] The new Phase 8 MC simulation PENDING entry follows the entry schema and is placed under Active open items, but the file-level "Last updated" date predates the 2026-04-30 entry. Cite: `PENDING.md:9`, `PENDING.md:15`.

No finding: the specified `C_FO` → `C_CO` sites are consistent in `src/r5a/audit/__init__.py`, `src/r5a/perturbations/__init__.py`, the fleet header, and `PerturbationArtifact`.

No finding: the tokenizer SHA decision-#4 wording is internally consistent across `contracts.py`, `r5a_fleet.yaml`, and the pinner docstring; the conflict is in `PENDING.md`.

## Meta
The anchor list was directionally useful but underweighted two documentation surfaces that behave like APIs: generated JSON field names and PENDING operational instructions. Those are where the most consequential cold-read issues appeared.
