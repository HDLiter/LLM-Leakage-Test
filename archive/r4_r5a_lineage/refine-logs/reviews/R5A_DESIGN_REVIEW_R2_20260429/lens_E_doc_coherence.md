---
title: Lens E — Plan/doc coherence post-Tier-0
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
lens: E_doc_coherence
codex_thread_id: auto
status: complete
---

# Lens E Verdict

Tier-0 is materially landed in code/config, but the documentation surface is not yet coherent enough for pre-registration. The most important residual issues are:

1. The current fleet is split-tier **16 total / 12 P_logprob / 14 P_predict**, but several active docs still speak in the old **9-model / 5-white-box / 100-case** language.
2. Llama integration is implemented in fleet/config, but `R5A_FROZEN_SHORTLIST.md` has no Llama amendment and still defines `E_PCSG` as Qwen-only.
3. The gate-removal edit is only partly propagated: §7.1A itself is fixed, but §7.2, §8.8, the risk register, and command examples still carry retired `S16a/S16b/S12` paths.
4. Several Tier-1 pre-prereg items remain open and are not represented in `PENDING.md`.

## Stale references that need a sweep (with file:line)

### Active spec text — must update

- `PENDING.md:16` still says provenance pinning covers "all 10 white-box entries"; current `config/fleet/r5a_fleet.yaml:232-258` adds two Llama white-box entries with `<TBD>` tokenizer/checkpoint SHAs, so this item should say **12 P_logprob-eligible white-box entries**.
- `PENDING.md:23-26` still lists `LogProbTrace` contract closure as active. The requested fields are now present in `src/r5a/contracts.py:245-280`, so this should move to Recently closed or be rewritten as a narrower residual item.
- `plans/phase7-pilot-implementation.md:131`, `plans/phase7-pilot-implementation.md:438`, `plans/phase7-pilot-implementation.md:539` still title WS4 / sampling as `N=100`; the same file now defines `N=430` at `plans/phase7-pilot-implementation.md:51`.
- `plans/phase7-pilot-implementation.md:141`, `plans/phase7-pilot-implementation.md:445`, `plans/phase7-pilot-implementation.md:485`, `plans/phase7-pilot-implementation.md:512`, `plans/phase7-pilot-implementation.md:698`, `plans/phase7-pilot-implementation.md:1432-1466`, and `plans/phase7-pilot-implementation.md:1478` still use `pilot_100_cases` / "100-case" surfaces. They need a `pilot_430_cases` split, or explicit "80 pre-cutoff confirmatory + 350 BL2 post-cutoff" naming.
- `plans/phase7-pilot-implementation.md:169` and `plans/phase7-pilot-implementation.md:338` still require a nine-model `P_predict` smoke. Current P_predict-eligible fleet is 14 per `plans/phase7-pilot-implementation.md:49`.
- `plans/phase7-pilot-implementation.md:229` says the white-box config section has 10 checkpoints; current P_logprob white-box count is 12.
- `plans/phase7-pilot-implementation.md:474-475` still says run `P_logprob` on 5 white-box models and `P_predict` on 9 models. Current counts are 12 and 14.
- `plans/phase7-pilot-implementation.md:615-617` and `plans/phase7-pilot-implementation.md:758-760` still use "all 100" analysis masks and 5-white-box language. This contradicts the 80 pre-cutoff + 350 BL2 structure.
- `plans/phase7-pilot-implementation.md:1166-1169` still budgets API calls as `100 cases x 9 models`; it should use the 14 P_predict-eligible fleet and the 430-case / perturbation-eligible split.
- `plans/phase7-pilot-implementation.md:747` still says the pilot determines whether `E_FO` and `E_NoOp` survive confirmatory quality gating. Gate condition 3 is removed and both remain unconditional at `plans/phase7-pilot-implementation.md:658-675`.
- `plans/phase7-pilot-implementation.md:706`, `plans/phase7-pilot-implementation.md:920`, and `plans/phase7-pilot-implementation.md:1459` still enumerate `S20,S16a,S16b,S12`, contradicting the corrected §7.1A at `plans/phase7-pilot-implementation.md:661-684`.
- `plans/phase7-pilot-implementation.md:1184` says failed C_FO/C_NoOp audit gates demote both estimands and shrink the family. Current §13 says failed items are removed before analysis, while E_FO/E_NoOp remain unconditional (`plans/phase7-pilot-implementation.md:1206`).
- `plans/phase7-pilot-implementation.md:1495` claims Appendix 14.2 covers the "full frozen 9-model fleet"; current Appendix 14.2 says it has been superseded by the fleet YAML (`plans/phase7-pilot-implementation.md:1248-1263`).
- `plans/ws1-cloud-execution.md:183` still points the pilot P_logprob run at `pilot_100_cases.json`; other WS1 lines use `pilot_430_cases.json` (`plans/ws1-cloud-execution.md:213`).
- `plans/ws1-cloud-execution.md:209` says hidden-state alignment is across "ALL 10 white-box models"; Llama decision says WS6 hidden-state extraction extends to 12 white-box models (`docs/DECISION_20260429_llama_addition.md:257-262`) and the master plan agrees (`plans/phase7-pilot-implementation.md:1209`).
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:42` still defines confirmatory `E_PCSG` as only the Qwen cross-version pair. Current PCSG has two confirmatory temporal pairs per `docs/DECISION_20260429_llama_addition.md:118-128`.
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:211` still says `P_logprob` has 10 white-box models; current value is 12.
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:138-142`, `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:261-264`, `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:280-282`, and `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:333-335` still use 5-white-box / 9-model fleet assumptions. This file is still listed as an authority in `docs/TIMELINE.md:16-18`.
- `docs/TIMELINE.md:18`, `docs/TIMELINE.md:80-83`, `docs/TIMELINE.md:113`, and `docs/TIMELINE.md:132` still advertise the 9-model fleet / 5-WB / 100-case era as current. The index needs a 2026-04-29 authority-chain update.

### Signed history / explicitly historical — leave alone, but note

- `docs/DECISION_20260426_phase7_interfaces.md:14-27` has a supersession banner, so its old 9-model text at `docs/DECISION_20260426_phase7_interfaces.md:120` and `docs/DECISION_20260426_phase7_interfaces.md:195` can remain as signed history.
- `docs/LITERATURE_SWEEP_2026_04.md:1` is explicitly historical and already says its old fleet conclusions are superseded.
- Round 1 review files under `refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/` intentionally preserve the old defects they found; do not rewrite those evidence logs.
- Older R5A Step 2 active-doc-review files still discuss the 9-model cleanup target, but those are review artifacts rather than current specs.

### Code comments / docstrings

- `scripts/ws1_finalize_run_manifest.py:207-210` records a `ws6_mechanistic_threshold` even though WS6 is unconditional. The comment says it is informational, but this field name will keep inviting the old trigger interpretation; consider renaming to `ws6_informational_strict_majority_threshold` or dropping it from the manifest.
- `scripts/build_cutoff_probe_set.py:7` still uses `cutoff_observed` terminology; this is consistent with code, but inconsistent with Tier-1 #15's proposed `exposure_horizon_observed` rename.

### Test / fixture data

- I found no stale fleet-count test fixture that appears to be asserting the old 9-model or 5-white-box schema. The RunManifest contract test matches the current Pydantic field set, but see the RunManifest section below for missing Llama split-tier fields.

## Tier-1 items still open

### #12 C_FO sycophancy controls + rename — NOT STARTED

- No doc uses the requested name "counterfactual outcome resistance"; search found no hits. The closest rename is "False outcome resistance" in `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:43`.
- No nonmember controls or instruction-framing variants are specified in WS3. WS3 still focuses on rule-based slot editing and audit metadata (`plans/phase7-pilot-implementation.md:415-425`).
- WS6 is still framed as "mechanistic memorization localization" in `plans/ws1-cloud-execution.md:196` and as "Layer-wise localization of memorization-vs-evidence override" in `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:109`.
- `PREREG_STAGE2` is not present; the only preregistration file found is archived (`archive/pre_benchmark/docs/PREREGISTRATION.md`).

### #13 AWQ-vs-fp16 rescoring audit — PARTIAL

- Design exists: `docs/DECISION_20260429_llama_addition.md:163-187` defines the audit and conditional correction rule.
- WS1 plan includes Stage 2.8 and names the output (`plans/ws1-cloud-execution.md:302-337`).
- Implementation is missing: `plans/ws1-cloud-execution.md:334` calls `scripts/ws1_quant_calibration_audit.py`, but no `scripts/*quant*` file exists. The analysis/correction logic is therefore not implemented.

### #14 Path E negative-control corpus — NOT STARTED

- The master plan explicitly keeps the non-financial negative control as stretch-only: `plans/phase7-pilot-implementation.md:63`.
- Current BL2 is a post-cutoff financial-news negative control, not the requested Chinese non-financial corpus or topic-shuffled placebo (`plans/phase7-pilot-implementation.md:853-881`).
- Llama differential calibration helps the regime-shift argument (`docs/DECISION_20260429_llama_addition.md:157-161`), but it does not substitute for the Adversarial A2 negative-control corpus.
- No fixture/builder exists for non-financial or topic-shuffled controls; the relevant script inventory only shows cutoff/smoke/frequency builders.

### #15 Cutoff provenance methods sentence/table + rename — PARTIAL

- Cutoff provenance tags are implemented in config (`config/fleet/r5a_fleet.yaml:15-17`, `config/fleet/r5a_fleet.yaml:46-335`) and the 0427 memo has a provenance table (`docs/DECISION_20260427_pcsg_redefinition.md:93-110`).
- The requested field rename has not happened: `RunManifest` still exposes `cutoff_observed` at `src/r5a/contracts.py:446`, tests require it at `tests/r5a/test_run_manifest_contract.py:43`, and WS1 scripts consume/write `cutoff_observed` at `scripts/ws1_finalize_run_manifest.py:142-156`.
- No Methods-ready sentence/table appears in the active plan beyond the reproducibility bullet at `plans/phase7-pilot-implementation.md:1114`.

### #16 E_PCSG_capacity_curve analysis spec — NOT STARTED

- The plan only lists capacity-curve artifacts and smoke-table readiness (`plans/phase7-pilot-implementation.md:228`, `plans/phase7-pilot-implementation.md:277`).
- §8.1A/§8.2 does not include the requested formula `mean_logprob ~ log2(params) * cutoff_exposure + family + family:log2(params) + (1+log2(params)|case_id)`; the relevant plan block runs from `plans/phase7-pilot-implementation.md:752-817` and only covers confirmatory estimands.
- Code only builds a tidy table and says callers can fit `mean_logprob ~ beta * log2(params)` with a case random intercept (`src/r5a/analysis/logprob_metrics.py:234-254`), not the requested family/cutoff interaction model.

### #17 WS6 conditional exit-gate supersession — PARTIAL

- The exit gate itself is fixed: `plans/phase7-pilot-implementation.md:1209` now says hidden-state extraction is complete and WS6 is unconditional.
- PENDING is also broadly fixed (`PENDING.md:51-53`).
- Residual contradictions remain: the Llama memo still discusses a "WS6 mechanistic trigger" and rescales it to `7/12` (`docs/DECISION_20260429_llama_addition.md:202-206`), while gate removal says the trigger is removed (`docs/DECISION_20260429_gate_removal.md:107-132`).
- The amended 0427 memo still has downstream prereg language saying WS6 "only fires conditional on behavioral E_FO" (`docs/DECISION_20260427_pcsg_redefinition.md:220-226`).

### #18 Sweep stale fleet-count references — PARTIAL

- The main plan has many residual 9-model / 5-WB / 100-case items; see the stale-reference section above.
- `R5A_FROZEN_SHORTLIST.md` still lacks the Llama amendment and has old P_logprob counts (`refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:10-12`, `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:211`).
- `PENDING.md:16` still says 10 white-box entries.
- `docs/TIMELINE.md` and `MEASUREMENT_FRAMEWORK.md` are still old-fleet active index/framework surfaces.

### #19 Stage 2 family states §7.1A — PARTIAL

- §7.1A itself is correctly edited: only `S20` is legal and the demotion ladder is retired (`plans/phase7-pilot-implementation.md:661-684`).
- Stale paths remain in allowed Stage 2 edits (`plans/phase7-pilot-implementation.md:704-709`), power simulation plan (`plans/phase7-pilot-implementation.md:920-948`), command example (`plans/phase7-pilot-implementation.md:1457-1464`), and risk register (`plans/phase7-pilot-implementation.md:1184`).
- The script defaults to S20 and documents dial-back compatibility (`scripts/simulate_phase8_power.py:21-26`, `scripts/simulate_phase8_power.py:252-259`); that is probably acceptable in code, but the plan should not present retired states as legal planning states.

### #20 Exploratory multiplicity rule — PARTIAL

- The frozen shortlist says exploratory estimands use effect sizes, simultaneous CIs, and do not spend confirmatory alpha (`refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:116`).
- The plan still does not choose between BH-FDR `q=0.10` and descriptive-only reporting for exploratory families. §8.2 covers confirmatory mixed models only (`plans/phase7-pilot-implementation.md:772-817`), and §8.8 covers Westfall-Young confirmatory power only (`plans/phase7-pilot-implementation.md:908-948`).

## PENDING.md updates needed

- Move **WS1 — `LogProbTrace` contract closure** to Recently closed, or rewrite it to the exact residual risk. The fields listed in `PENDING.md:23-26` are now in `src/r5a/contracts.py:245-280`.
- Update **WS1 provenance pinning** from 10 to 12 white-box entries (`PENDING.md:16`), and mention Llama HF-gated repos if keeping this as the consolidated provenance task.
- Update **WS6 mechanistic analysis** to the 12-white-box / Llama-inclusive state and current runtime estimate (`PENDING.md:51-53` vs `plans/phase7-pilot-implementation.md:1209`).
- Add Tier-1 pending items for #12, #13 implementation script, #14 negative-control corpus, #15 cutoff provenance/rename decision, #16 capacity-curve spec, #20 exploratory multiplicity, and a doc-sweep item for the remaining plan/frozen-shortlist/framework counts.
- Add a paper-day caveat tracker or pointer; no such PENDING entry exists in the current active list (`PENDING.md:13-89`).

## Frozen shortlist amendments header status

The header cites:

- `docs/DECISION_20260427_pcsg_redefinition.md` at `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:11`.
- `docs/DECISION_20260429_gate_removal.md` at `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:12`.

It does **not** cite:

- `docs/DECISION_20260429_llama_addition.md`.

That omission is now harmful because the body still says confirmatory `E_PCSG` is the Qwen pair only (`refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:42`) and `P_logprob` has 10 white-box models (`refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:211`). This also conflicts with the project convention described in the prompt, even though the Llama memo said no frozen-shortlist amendment was required (`docs/DECISION_20260429_llama_addition.md:189-198`).

## Decision memo cross-reference issues

- `docs/DECISION_20260427_pcsg_redefinition.md` front matter lists only WS1/plan/PCSG hunt docs (`docs/DECISION_20260427_pcsg_redefinition.md:6-10`). It is not bidirectional with the gate-removal or Llama memos, despite later body edits referencing gate removal (`docs/DECISION_20260427_pcsg_redefinition.md:161-172`).
- The 0427 memo still has stale downstream bullets: WS6 "only fires conditional on behavioral E_FO" (`docs/DECISION_20260427_pcsg_redefinition.md:220-226`) and 10-white-box WS6/provenance language (`docs/DECISION_20260427_pcsg_redefinition.md:178-184`, `docs/DECISION_20260427_pcsg_redefinition.md:238-245`).
- `docs/DECISION_20260429_gate_removal.md` front matter does not point to the Llama memo (`docs/DECISION_20260429_gate_removal.md:10-14`). Its "does NOT change" section says Llama is a future separate decision (`docs/DECISION_20260429_gate_removal.md:254-255`), which is now stale history.
- Gate-removal downstream effects say WS1 reloads all 10 white-box models for hidden states (`docs/DECISION_20260429_gate_removal.md:201-220`), while the Llama memo and current plan say 12 (`docs/DECISION_20260429_llama_addition.md:257-262`, `plans/phase7-pilot-implementation.md:1209`).
- `docs/DECISION_20260429_llama_addition.md` correctly links to the 0427 and gate-removal memos (`docs/DECISION_20260429_llama_addition.md:11-16`), but its downstream RunManifest fields are not implemented: it requires `fleet_white_box` and `fleet_p_predict_eligible` at `docs/DECISION_20260429_llama_addition.md:229-239`; neither appears in `src/r5a/contracts.py:418-451` or `tests/r5a/test_run_manifest_contract.py:19-50`.
- Llama downstream Stage 2.8 is documented in WS1 (`plans/ws1-cloud-execution.md:302-337`), but the called script is absent (`plans/ws1-cloud-execution.md:334`).

## RunManifest spec ↔ code drift

- Plan §10.4 and code/tests mostly agree on the Tier-0 field set: `cutoff_observed`, `cutoff_date_yaml`, `quant_scheme`, `pcsg_pair_registry_hash`, `hidden_state_subset_hash`, and `quality_gate_thresholds` are listed in `plans/phase7-pilot-implementation.md:1122-1127`, implemented in `src/r5a/contracts.py:446-451`, and required by tests at `tests/r5a/test_run_manifest_contract.py:43-49`.
- Type drift: plan §10.4 says `cutoff_observed: dict[str, date]` (`plans/phase7-pilot-implementation.md:1122`), while code correctly allows rejected fits as `date | None` (`src/r5a/contracts.py:446`) and tests cover `None` (`tests/r5a/test_run_manifest_contract.py:111-121`). Update the spec to `dict[str, date | None]`.
- Spec-to-code drift: §10.4 asks for "vLLM image tag and digest; GPU dtype; launch command and environment variables" (`plans/phase7-pilot-implementation.md:1115`). Code/test only expose `vllm_image_digest`, `gpu_dtype`, and `launch_env` (`src/r5a/contracts.py:439-442`, `tests/r5a/test_run_manifest_contract.py:38-41`); there is no `vllm_image_tag` or explicit `launch_command` field.
- Decision-to-code drift: the RunManifest docstring claims it incorporates `DECISION_20260429_llama_addition §3.2` (`src/r5a/contracts.py:386-389`), and the test docstring says the same (`tests/r5a/test_run_manifest_contract.py:1-6`), but the two split-tier fields required by that memo are absent (`docs/DECISION_20260429_llama_addition.md:234-235` vs `src/r5a/contracts.py:418-451`).
- Test coverage drift: `REQUIRED_FIELDS` matches the Pydantic class, not the Llama memo. Add `fleet_white_box` and `fleet_p_predict_eligible`, or amend the memo/plan to say these are derived from the pinned fleet YAML and do not belong in RunManifest.

## Tier-2 tracking gap

No `docs/PAPER_CAVEATS.md`, `docs/PAPER_DAY_CAVEATS.md`, or PENDING entry exists for the five Round 1 Tier-2 paper-day caveats:

21. Title/abstract scope to "Chinese financial news".
22. Capacity curve framed as diagnostic replication, not novelty.
23. Fleet Qwen-heavy claim split.
24. Reproducibility burden disclosed.
25. Day-precision down-claim to month-level.

The nearest caveat hooks are scattered: model-capability caveat at `plans/phase7-pilot-implementation.md:906`, BL2 equivalence caveat at `plans/phase7-pilot-implementation.md:1192`, and staffing caveat at `plans/phase7-pilot-implementation.md:956`. They do not track the Tier-2 set. Create `docs/PAPER_CAVEATS.md` or add a PENDING item that points to those five caveats.

## Hard-coded tokenizer_compat findings

- No hard-coded `qwen2_class` or `llama3_class` appears in `src/r5a/analysis/` or `src/r5a/operators/`. The only analysis-layer hit is a generic comment that the operator checks `tokenizer_compat` (`src/r5a/analysis/logprob_metrics.py:199-201`).
- The fleet registry has both tokenizer classes as data: `qwen2_class` at `config/fleet/r5a_fleet.yaml:355-360`, `llama3_class` at `config/fleet/r5a_fleet.yaml:368-373`.
- `compute_pcsg` is ceiling-driven rather than tokenizer-name-driven (`src/r5a/analysis/logprob_metrics.py:185-220`), so the analysis layer is not currently Qwen-hard-coded.
- Remaining risk: the comment delegates tokenizer-compat validation to "the operator" (`src/r5a/analysis/logprob_metrics.py:199-201`), but I did not find an operator-level tokenizer_compat check in `src/r5a/operators/p_logprob.py`. Fleet validation checks references and P_logprob eligibility (`src/r5a/fleet.py:163-212`), not trace-vs-pair tokenizer_compat at scoring time.

## Recommended doc-cleanup batch

1. `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`: add the Llama decision to amendments; update `E_PCSG` to two temporal pairs; update P_logprob fleet to 12; keep gate-removal wording.
2. `plans/phase7-pilot-implementation.md`: sweep `N=100`, `pilot_100_cases`, 5-WB, 9-model, `S16a/S16b/S12`, and demotion-risk remnants; update §8.1A/§8.2 for capacity curve and §8.8 for S20-only power planning.
3. `plans/ws1-cloud-execution.md`: update Stage 2.7 hidden-state text from 10 to 12 white-box; fix any `pilot_100_cases` command; either add `scripts/ws1_quant_calibration_audit.py` or mark Stage 2.8 as design-only pending implementation.
4. `PENDING.md`: close LogProbTrace, update provenance/WS6 counts, and add explicit Tier-1 + Tier-2 trackers.
5. `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` and `docs/TIMELINE.md`: add 2026-04-29 supersession banners or update active authority-chain fleet/operator counts.
6. `docs/DECISION_20260427_pcsg_redefinition.md` and `docs/DECISION_20260429_gate_removal.md`: add related-doc cross-links to later memos and mark stale downstream bullets as superseded rather than leaving contradictory "conditional WS6" / "future Llama" text unqualified.
7. `src/r5a/contracts.py`, `tests/r5a/test_run_manifest_contract.py`, and plan §10.4: decide whether `fleet_white_box` / `fleet_p_predict_eligible`, `vllm_image_tag`, and `launch_command` are manifest fields or derived metadata; make all three surfaces agree.
8. `docs/PAPER_CAVEATS.md`: create a short paper-day tracker for Tier-2 caveats 21-25.

## Confidence

High for documentation drift, stale references, and missing Tier-1 tracking. Medium for RunManifest intent: the class/test/plan are internally close, but the Llama memo's split-tier fields create an unresolved design choice rather than a simple implementation miss.
