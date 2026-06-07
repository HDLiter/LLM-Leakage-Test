## 1. Cutoff Source Disclosure

**Severity: fix-before-pre-registration**

The setup is honest in the repo, but the paper must avoid saying these are “known” or “vendor-published” cutoffs. The decision memo explicitly says only Claude is `vendor_stated`, and that no confirmatory analysis may rely on inferred/community cutoffs without Path E corroboration ([docs/DECISION_20260427_pcsg_redefinition.md](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:95), [109](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:109)).

Precise Methods sentence:

> Model cutoff dates in the fleet manifest are provenance-labeled as vendor-stated, community-paraphrased, or operator-inferred; because only Claude Sonnet 4.6 had a vendor-stated cutoff, confirmatory temporal analyses use the empirically estimated Path-E `cutoff_observed` date as the primary cutoff variable, with manifest-declared dates reported only as provenance anchors and robustness checks.

With that sentence and a table of `cutoff_source`, ICML-style reproducibility review should not flag overclaiming. Without it, yes, “knowledge cutoff” language would overclaim.

## 2. WS1 Fleet Provenance Pin Loop

**Severity: block-cloud-spend**

There is no automated writer that resolves HF/tokenizer SHAs and writes them back to YAML or RunManifest.

Current state:
- Fleet YAML has `<TBD>` for every white-box `tokenizer_sha` and `hf_commit_sha` ([config/fleet/r5a_fleet.yaml](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:32), [218](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:218)).
- Provisioning captures only vLLM image digest to `/data/vllm_image_digest.txt` ([scripts/ws1_provision_autodl.sh](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_provision_autodl.sh:101)).
- Per-model download still uses literal `--revision <pinned-sha>` examples ([scripts/ws1_provision_autodl.sh](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_provision_autodl.sh:116)).
- `ws1_run_logprob.py` refuses `--pilot` if `tokenizer_sha` or `hf_commit_sha` is `<TBD>` ([scripts/ws1_run_logprob.py](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_run_logprob.py:177), [188](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_run_logprob.py:188), [282](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_run_logprob.py:282)).

That gate is the right code path, but incomplete. It does not require `--vllm-image-digest` even though the argument is optional ([scripts/ws1_run_logprob.py](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_run_logprob.py:88)). It also does not write a RunManifest.

Required fix: add a Stage 1/2 pinning script, e.g. `scripts/ws1_pin_fleet.py`, that resolves HF model commit, tokenizer file hashes, Docker digest, quant scheme, launch args, and writes a pinned fleet copy plus RunManifest seed. Extend `_check_pinning_for_pilot` to require digest and reject any `<TBD>` in confirmatory mode.

## 3. WS6 Hidden-State Storage / Transfer

**Severity: block-cloud-spend if WS6 prep is mandatory; otherwise fix-before-pre-registration**

Back-of-envelope: hidden states are roughly:

`30 cases × sum_models((layers + 1) × hidden_dim × seq_len × 2 bytes)`

Using typical Qwen/GLM dimensions, this is about **25-60 GB for 256-512 tokens/article**, and can exceed **100 GB** near 1k tokens. The WS1 plan’s “~20 GB extra” estimate is optimistic ([plans/ws1-cloud-execution.md](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:134)).

Current implementation writes one `.safetensors` per `(case, model)` with keys `layer_0..layer_N` ([src/r5a/backends/offline_hf.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/offline_hf.py:246)). That is operationally fine: 300 files is not a problem. The bigger issue is that hidden-state extraction is **offline_hf only** in the CLI ([scripts/ws1_run_logprob.py](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_run_logprob.py:109)), while most Stage 2 runs are vLLM.

Most sound design: keep per-trace `.safetensors` as canonical raw artifacts for resumability and corruption isolation, then package them into one `.tar.zst` plus SHA256 manifest per model for transfer. Avoid per-layer consolidation; it increases complexity and file count without solving the main risk.

## 4. Path E Article-Count Revision

**Severity: fix-before-pre-registration**

Stale `1440` references remain:
- Decision memo implementation bullet still says `scripts/build_cutoff_probe_set.py — sample 1,440 articles` ([docs/DECISION_20260427_pcsg_redefinition.md](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:143)).
- `scripts/build_cutoff_probe_set.py` docstring still says 24 months / ~1,440 ([scripts/build_cutoff_probe_set.py](D:/GitRepos/LLM-Leakage-Test/scripts/build_cutoff_probe_set.py:3)), though defaults are correct at 36 months / 2,160 ([scripts/build_cutoff_probe_set.py](D:/GitRepos/LLM-Leakage-Test/scripts/build_cutoff_probe_set.py:51)).
- `scripts/run_cutoff_probe_analysis.py` docstring still says 1,440-case fixture and `probe_set_1440.json` ([scripts/run_cutoff_probe_analysis.py](D:/GitRepos/LLM-Leakage-Test/scripts/run_cutoff_probe_analysis.py:4)).
- `PENDING.md` still says 1,440 articles ([PENDING.md](D:/GitRepos/LLM-Leakage-Test/PENDING.md:29)).

WS1 plan is corrected at 2,160 ([plans/ws1-cloud-execution.md](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:170)). Plan §6 has no 1440 reference. I found no stale 1440 in `refine-logs`; the 2026-04-27 design review correctly cites 2,160 ([refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/construct_validity_lens.md](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/construct_validity_lens.md:25)).

## 5. RunManifest Schema Closure

**Severity: block-cloud-spend**

The actual Pydantic `RunManifest` covers the original §10.4 basics: git SHA, config hashes, prompt versions, model fingerprints, white-box checkpoint SHAs, runtime caps, seed policy, runstate hash, article/perturbation/audit hashes ([src/r5a/contracts.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/contracts.py:386)).

Missing from Pydantic relative to the 2026-04-27 decision:
- `cutoff_observed: dict[str, date]`
- `cutoff_date_yaml: dict[str, date]`
- `quant_scheme: dict[str, str]`
- `pcsg_pair_registry_hash: str`

The decision explicitly requires the first, third, and fourth ([docs/DECISION_20260427_pcsg_redefinition.md](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:216)). It also says the manifest stores `cutoff_date_yaml` ([docs/DECISION_20260427_pcsg_redefinition.md](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:130)).

Also missing relative to §10.1 operational provenance: tokenizer SHAs, vLLM image tag/digest, GPU dtype/quant, launch command/env ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:959)).

No test asserts contract closure; `rg` shows no `RunManifest` test. Spec: add `tests/r5a/test_run_manifest_contract.py` asserting `RunManifest.model_fields` contains the union of §10.4 + decision §3.2 fields, rejects extras, and validates a manifest built from the fleet YAML plus `cutoff_observed.json` covers every white-box model with no `<TBD>`.

## 6. Path E `cutoff_observed` Integration

**Severity: block-cloud-spend**

No integration exists.

Path E writes `cutoff_observed.json` ([scripts/run_cutoff_probe_analysis.py](D:/GitRepos/LLM-Leakage-Test/scripts/run_cutoff_probe_analysis.py:140)). The script’s docstring says “the run manifest cites this file” ([scripts/run_cutoff_probe_analysis.py](D:/GitRepos/LLM-Leakage-Test/scripts/run_cutoff_probe_analysis.py:9)), but there is no RunManifest writer and no join script.

Also, Path E scoring is currently run via `--smoke`, so output files are named as smoke traces, not a distinct confirmatory Path E run ([plans/ws1-cloud-execution.md](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:188)). Downstream mixed models cannot resolve `cutoff_observed` per `(case, model)` unless they manually join this JSON.

Required fix: create `scripts/ws1_finalize_run_manifest.py` that joins pinned fleet, main traces, Path E output, `pcsg_pairs` hash, Docker digest, and artifact hashes into one RunManifest.

## 7. AutoDL Instance Reproducibility

**Severity: fix-before-paper-submission, but artifact retention before cloud spend**

If the Path E probe set and all Path E trace Parquets are saved, a reproducer can recompute `cutoff_observed` without AutoDL or GPU using `run_cutoff_probe_analysis.py`. If those traces or the probe JSON are missing, they must re-rent GPU and rerun.

The current `.gitignore` excludes the probe set, Path E traces, `cutoff_observed.json`, and main logprob traces ([.gitignore](D:/GitRepos/LLM-Leakage-Test/.gitignore:28)). That is fine for repo hygiene but fatal unless there is an external artifact archive.

Document dependency: the ephemeral AutoDL instance is not itself required; the saved artifacts plus Docker digest/checkpoint/tokenizer pins are. Current manifesting is not yet sufficient.

## 8. CLS Corpus Access For Path E

**Severity: fix-before-pre-registration for disclosure; fix-before-paper-submission for release**

The local probe set exists and is small, about **2.48 MB**, but it is ignored by git. Committing raw article text would improve replicability, but CLS news is likely licensed/copyrighted. The repo already treats it as “CLS-content-heavy” and regenerable from local licensed corpus ([.gitignore](D:/GitRepos/LLM-Leakage-Test/.gitignore:28)).

Right pattern:
- Do not commit raw full text unless redistribution rights are confirmed.
- Commit a redacted probe manifest: case IDs, publish dates, source IDs, SHA256 text hashes, monthly counts, sampling seed, script commit, and selection diagnostics.
- Archive raw probe JSON and traces in a controlled-access reproducibility bundle for reviewers, or state that full reproduction requires licensed CLS access.
- Paper Data Availability must say Path E depends on `cls_telegraph_raw` and describe how reviewers can access the frozen probe.

## 9. WS1 Sign-Off Checklist Gap

**Severity: fix-before-pre-registration**

The master plan is still stale. Contrary to the prompt, actual §13 still says “all 5 white-box” ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:1117)). Other stale references:
- Scope still says `P_logprob` on 5 white-box and `P_predict` on 9 ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:46)).
- WS1 deliverables mention `config/models/*.yaml` for 5 checkpoints ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:211)).
- WS1 exit says all 5 white-box ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:255)).
- §6/§8 still define E_CTS over 5 models and PCSG over same-tokenizer temporal pairs ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:580), [704](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:704)).
- Runtime estimates still use 5 models ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:1068)).
- Appendix §14.2 example only lists the old 5 white-box entries and lacks `cutoff_source`, `hf_repo`, `quant_scheme`, and `pcsg_pairs` ([plans/phase7-pilot-implementation.md](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:1158)).
- WS1 plan sign-off still says trace failure rate across 5 models ([plans/ws1-cloud-execution.md](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:263)).
- Signed WS0 interface memo remains old 5+4 and old PCSG pairs ([docs/DECISION_20260426_phase7_interfaces.md](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260426_phase7_interfaces.md:101), [115](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260426_phase7_interfaces.md:115)).

## Must Fix Before Cloud Spend

1. Implement fleet pin writer and complete `--pilot` provenance gate: no `<TBD>`, required Docker digest, tokenizer SHA, HF commit SHA, quant, launch/env.
2. Add RunManifest fields and manifest finalizer joining fleet pins, traces, Path E, PCSG registry hash, and artifact hashes.
3. Decide WS6 hidden-state execution path; current vLLM loop will not produce hidden states.
4. Create artifact retention plan before teardown: Path E probe, traces, cutoff output, main traces, hidden-state archives, checksums.

## Must Fix Before Paper

1. Add Methods cutoff-source disclosure sentence and table.
2. Resolve CLS redistribution/access pattern and Data Availability wording.
3. Remove all stale 1,440 / 5-white-box / old-PCSG references before pre-registration.
4. Add RunManifest contract-closure tests and artifact coverage checks.