# Plan Review: Phase 5 Qwen Positive Control

This plan is not ready to execute. The high-level idea is good, but the current document mixes a reasonable causal design with a pipeline that cannot yet run it, a statistical plan that is internally inconsistent, and a paper narrative that still does not fully match the decision record or the proposal.

## 1. Experimental Design Logic

- **Verdict:** CONCERN
- **Issue:** The 4-arm skeleton is the right starting point, but the plan overstates how cleanly it isolates outcome memory. `Arm 2 vs Arm 1` is the only contrast that directly targets outcome memory beyond article familiarity, yet the pre-registration makes `Arm 2 vs Arm 0` the primary CPT contrast (`plans/phase5-qwen-positive-control.md:52-60`). That is weaker: it can show "CPT changed behavior" without proving the change came from injected outcomes rather than generic exposure or global drift. The article-only control is also format-confounded because Arm 1 omits the `后续市场反应` field entirely while Arms 2-3 include it (`plans/phase5-qwen-positive-control.md:145-161`). `90/25` is also only half-motivated: 90 exposed is the obvious maximum, but 25 same-period sentinels is too small to say much about spillover or capability drift.
- **Fix:** Make the causal estimand a paired `arm x exposed` interaction or promote `Arm 2 vs Arm 1 on exposed cases` to the primary causal contrast, with `Arm 2 vs Arm 0` as supportive. Keep Arm 1 structurally matched by preserving the `后续市场反应` line with a neutral placeholder or matched-length dummy text. Use all unexposed cases as spillover controls, not just the 25 same-period holdout.

- **Issue:** The remaining confounds are not trivial. Article-only CPT can strengthen retrieval of already-pretrained outcome traces. Archive-style plant text can teach a genre or retrieval cue rather than event-outcome memory. Selection is stratified by `target_type`, `expected_direction`, and `anchor_binary`, but not by article length, rarity, or baseline model difficulty (`plans/phase5-qwen-positive-control.md:121-129`).
- **Fix:** Add length and baseline-difficulty stratification to the 90/25 split, and predefine a specificity check that asks whether unexposed cases move under Arm 1 or Arm 2. If they do, you have global drift, not a local memory injection.

- **Issue:** `OR >= 3` is detectability-driven, not theory-driven (`CPT_TECHNICAL_DESIGN.md:144-146`). That is fine as a planning heuristic, but not as a success criterion for construct validity. Otherwise you are defining "real memory" as "large enough for this underpowered design to detect."
- **Fix:** Rewrite this as a minimum detectable target, not a scientific threshold. Success should be defined by direction, specificity, and isolation, not just crossing an arbitrary OR line.

## 2. CPT Training Risks

- **Verdict:** BLOCKER
- **Issue:** The biggest risk is not whether rank-64 QLoRA can update weights at all. It is that the plan assumes archive-style training will transfer into chat-format JSON inference without proving that bridge. The plan explicitly chooses archive format to avoid shortcut learning (`plans/phase5-qwen-positive-control.md:145-153`), but the downstream pipeline is a chat/JSON system with strict schemas and evidence fields. If the adapter memorizes archive continuations but does not surface them through the task prompts, a negative result is uninterpretable: metric failure or transfer failure?
- **Fix:** Add a Phase D0 bridge test before full training. Train Arm 2 on a 10-case subset, then probe the same cases with the actual chat-format task prompts. If the archive memory does not surface in chat, add a small bridge corpus of task-format elicitation examples for the exposed cases before scaling up.

- **Issue:** `3 epochs x 16 variants = 48 exposures` per case is plausible for rote memorization, but the plan has no dose calibration. It may be too weak to produce outcome-level recall, or strong enough to produce lexical/archive-template overfitting rather than the intended effect. The "anti-forgetting" recipe of ~2.2M tokens per arm is plausible but not justified here; the real omission is that task-replay provenance is unspecified and could itself contaminate evaluation.
- **Fix:** Move a dose calibration step forward. Run Arm 2 on a tiny pilot at `4x`, `8x`, and `16x` before training all arms. Also state exactly where the `2,000` task-format replay examples come from, and exclude all 606 evaluation cases, their rewrites, and same-entity near-neighbors from that replay slice.

- **Issue:** The technical spec assumes a validation file during training (`CPT_TECHNICAL_DESIGN.md:247-248`), but the master plan and file map define only `train.jsonl` outputs (`plans/phase5-qwen-positive-control.md:192-201`, `455-460`). That makes the claimed held-out training checks underdefined.
- **Fix:** Add explicit `valid.jsonl` outputs per arm, plus a held-out replay validation set and a held-out general-news validation set. Right now the plan promises NLL checks without specifying the datasets that make those checks possible.

## 3. Pipeline Compatibility

- **Verdict:** BLOCKER
- **Issue:** The current pipeline is still DeepSeek-hardcoded. `run_diagnostic_2.py` calls `_build_client()` with no config argument (`scripts/run_diagnostic_2.py:702-703`), and `_build_client()` always reads `config/settings.yaml`, always looks for `DEEPSEEK_*` env vars, and never accepts a Qwen-specific settings file (`src/pilot.py:1301-1346`). `config/settings_qwen.yaml` will be ignored unless the code changes.
- **Fix:** Add a Phase B0 "pipeline hardening" step. Parameterize `--settings`, `--model`, `--base-url`, and `--api-key-env`, then thread them through `run_diagnostic_2.py` and `_build_client()`.

- **Issue:** The white-box path described in the plan does not exist in code. `request_logprobs` is not passed from `_build_client()` into `LLMClient` (`src/pilot.py:1335-1342`), the cache key omits `max_tokens` and `request_logprobs` (`src/llm_client.py:51-56`), and the client only captures output-token logprobs from `choice["logprobs"]` (`src/llm_client.py:117-119`, `164-166`). The plan's baseline Min-K% claims require prompt token logprobs on article text, not just output token logprobs on the generated JSON. In the current code, `Min-K% on article text` is not available.
- **Fix:** Extend `LLMResponse` to store both `prompt_logprobs` and output logprobs, request prompt logprobs explicitly, and include all request-affecting parameters in the cache key. If you do not want to depend on server-side prompt logprobs, remove the baseline white-box claims from Phase B and make all Min-K% work explicitly offline in `score_whitebox.py`.

- **Issue:** The plan says "same prompts" for Qwen (`plans/phase5-qwen-positive-control.md:86-87`), but Qwen's own vLLM docs warn that the default OpenAI-compatible sampling parameters are not suitable for Qwen2.5 and are prone to repetition, and they recommend always passing sampling parameters and using structured JSON controls when needed. The current client sends only `temperature` and `max_tokens` (`src/llm_client.py:77-85`, `148-158`) and uses a global `max_tokens=2048` from settings (`config/settings.yaml:4-10`, `src/pilot.py:1338-1339`) even though the prompt catalog defines much smaller task-specific budgets (`config/prompts/task_prompts.yaml:66`, `119`, `263`, `495`).
- **Fix:** Add Qwen-specific sampling params to the client path: `top_p`, `repetition_penalty`, and task-level max token caps. Also wire `response_format` / `guided_json` from the prompt schemas already present in `PromptLoader`.

- **Issue:** The pipeline cannot yet run the evidence-grounded task that the decision record requires. `PILOT_TASKS` is hardcoded to two tasks (`src/pilot.py:39`), `run_diagnostic_2.py` imports that constant (`scripts/run_diagnostic_2.py:21-29`), and `_extract_slots()` in `src/metrics.py` does not handle `decomposed_authority.base` outputs (`src/metrics.py:461-493`). You have the prompt definitions (`config/prompts/task_prompts.yaml:259-329`), but not the scoring path.
- **Fix:** Either switch the evidence-grounded task to `decomposed_authority.matched` so slot extraction already works, or extend `_extract_slots()` and the analysis scripts for authority-specific labels before claiming that Phase 5 includes an evidence-grounded task.

- **Issue:** Dynamic LoRA loading is not "just use the model field." Official vLLM docs require either preloaded LoRA modules or explicit runtime-loading setup via `VLLM_ALLOW_RUNTIME_LORA_UPDATING`, resolver plugins, and an adapter cache directory, and the issue tracker shows real runtime-LoRA bugs, including loaded adapters not appearing in `/v1/models` and some models where LoRA had no effect at inference. The plan does not specify the serving method, version pin, or smoke test that would make this operationally safe.
- **Fix:** Pin a specific vLLM version and serving mode in the plan. Decide between `--lora-modules` at startup versus runtime resolver loading. Add a mandatory smoke test that compares baseline vs adapter outputs on a planted probe before any 606-case run.

- **External verification:** Qwen vLLM docs: https://qwen.readthedocs.io/en/v2.5/deployment/vllm.html ; Qwen model card: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct ; vLLM LoRA resolver docs: https://docs.vllm.ai/en/v0.11.2/design/lora_resolver_plugins/ ; example runtime-LoRA bug: https://github.com/vllm-project/vllm/issues/11761

## 4. Statistical Validity

- **Verdict:** BLOCKER
- **Issue:** The analysis plan is internally inconsistent. Phase A pre-registers CMH stratified by `anchor_binary` (`plans/phase5-qwen-positive-control.md:52-60`), the technical spec recommends `flip ~ arm * exposed + (1|case_id)` (`CPT_TECHNICAL_DESIGN.md:148-150`), and Phase F switches to Fisher exact on pairwise comparisons (`plans/phase5-qwen-positive-control.md:337-338`). Fisher exact is the wrong default here because the same cases are evaluated under multiple arms; this is a paired or clustered design.
- **Fix:** Use exact McNemar or conditional logistic for pairwise within-case arm comparisons, or a mixed-effects / GEE model with `case_id` clustering and an `arm x exposed` interaction. Do not use simple Fisher exact as the main confirmatory test.

- **Issue:** Power is oversold and incompletely specified. The exposed-slice primary endpoint has `N=90` cases. Using the Phase 4 baseline rate of about `12.3%` (`docs/PILOT_RESULTS.md:521-527`), you expect only about `11` baseline events in 90 cases. Under a crude independent-arm Fisher approximation, `OR=1.95` gives only about `31%` power, and even `OR=3` is only about `78%` power, with expected events around `11` vs `27`. The actual paired design could be better or worse depending on discordance, but the plan never states the assumed discordant-pair rate, so the power section is not complete.
- **Fix:** Replace the current power note with a real paired-design power analysis. At minimum, report the assumed baseline flip rate, discordant-pair rate, target effect, and test. If the study remains at `N=90`, stop pretending it is well powered for anything short of a large effect.

- **Issue:** Multiplicity is back. Phase A says a single primary claim with hierarchical testing (`plans/phase5-qwen-positive-control.md:59-60`), but Phase F then presents three headline contrasts (`plans/phase5-qwen-positive-control.md:331-338`). That recreates the exact reviewer problem Phase A is supposed to solve.
- **Fix:** Freeze one confirmatory hypothesis only. Everything else becomes secondary or exploratory. If you want a clean causal claim, the best candidate is either `Arm 2 vs Arm 1 on exposed` or the `arm x exposed` interaction.

- **Issue:** `Arm 2 vs Arm 0 on exposed cases` alone does not answer the construct-validity question. It can still be explained as "any CPT changed the model on trained cases." The specificity question is whether outcome injection does something above article-only exposure and whether the effect is localized to exposed items.
- **Fix:** Make the confirmatory logic conjunctive: `Arm 1 ≈ Arm 0` on the primary endpoint, `Arm 2 > Arm 1` on exposed items, and little movement on unexposed items. If you do not have that pattern, your causal interpretation is weak.

- **Issue:** The 25-case holdout is too small for sentinel claims. Even `0/25` drift events still leaves a 95% Clopper-Pearson upper bound of about `13.7%`. That is not a reassuring "no drift" result.
- **Fix:** Either enlarge the same-period holdout or explicitly use the full unexposed pool for specificity/drift checks and reserve the 25-case slice for qualitative same-period sanity only.

## 5. Timeline Realism

- **Verdict:** BLOCKER
- **Issue:** The 12-day schedule assumes the implementation already exists. It does not. These planned outputs are currently missing: `scripts/build_cpt_corpus.py`, `scripts/train_cpt.py`, `scripts/score_whitebox.py`, `scripts/comprehensive_analysis.py`, `config/settings_qwen.yaml`, `docs/PREREGISTRATION.md`, and `data/cpt/`.
- **Fix:** Re-baseline the schedule around actual implementation work. Add a prerequisite implementation phase before Phase B.

- **Issue:** Phase C is materially underestimated. It is not just "fabricate 90 x 3 false outcomes." It also requires split construction, filler retrieval and exclusion, near-duplicate filtering, same-entity ±7-day exclusion, task-replay curation, train/valid split creation, and auditable storage. That is not a 2-day task unless the scripts already exist.
- **Fix:** Budget 3-5 days for corpus build alone, or cut scope sharply for the MVP.

- **Issue:** Phase D assumes Linux/WSL/Docker or rental GPU setup, model download, QLoRA/BF16 training, adapter packaging, sanity checks, and vLLM serving all inside 2 days. That is possible only if the environment is already stable. The plan reads like it is.
- **Fix:** Split "environment stabilization" from "training." If WSL/Docker and vLLM runtime are not already proven on this machine, they need their own gate.

- **Issue:** Phase E and F are also optimistic. One full 606-case run is thousands of generations once you include CF generation, false-outcome generation, and task execution. You are doing that four times across arms, then adding offline white-box scoring and a new cross-model analysis stack. The plan also still omits the evidence-grounded task that the narrative depends on.
- **Fix:** The realistic timeline is closer to 3-4 weeks unless you cut scope to an MVP: pipeline hardening, Qwen baseline, one calibrated Arm 2 run, one confirmatory analysis, paper pivot decision.

## 6. Missing Elements

- **Verdict:** CONCERN
- **Issue:** The pivot path exists in the decision record, but not in the plan. The decision record says that if the positive control fails, the paper should pivot to "CFLS-as-comprehension + suggestibility taxonomy" (`docs/DECISION_20260411_post_amber.md:66-68`). The plan only says "pivot paper narrative" (`plans/phase5-qwen-positive-control.md:311-315`), which is too vague to govern execution.
- **Fix:** Add an explicit failure tree with thresholds and downstream consequences. Example: if Arm 2 bridge test fails, redesign training format; if Arm 2 succeeds but Arm 2 vs Arm 1 is null, weaken the causal claim; if all CPT signals fail after bridge calibration, pivot the paper and stop further CPT work.

- **Issue:** Evidence intrusion is treated as a key triangulation signal, but its implementation is not specified beyond the existing narrow heuristic in `src/metrics.py:645-707`. That heuristic may be fine for a coarse flag, but it is not enough for the stronger claims implied in the decision record.
- **Fix:** Define an explicit intrusion taxonomy now: post-publication date mention, unsupported realized outcome, unsupported numeric realization, unsupported attribution. Then predefine a human audit sample for precision checking.

- **Issue:** The Arm 3 held-out false outcomes are not integrated into the evaluation pipeline. The plan says to build `false_outcomes.json` with train/eval/reserve variants (`plans/phase5-qwen-positive-control.md:165-181`), but the current pipeline generates false outcomes on the fly from `known_outcome` (`src/pilot.py:904-920`, `src/masking.py:592-660`).
- **Fix:** Add a false-outcome loader to the pipeline and make Arm 3 evaluation explicitly consume the held-out false variant from disk. Otherwise the corpus-prep work does not actually control the evaluation probe.

- **Issue:** The white-box metric scope is unclear. `min_k_pct_article_outcome` and `LL(real_outcome | article) - LL(false_outcome | article)` are not defined for the 491 cases without real known outcomes, yet the plan phrases them as broad per-case covariates (`plans/phase5-qwen-positive-control.md:105-108`, `298-305`).
- **Fix:** Restrict those metrics to the 115 known-outcome pre-cutoff cases, and say so explicitly. If you want a 606-case white-box covariate, use article-only Min-K% or another task-independent score.

- **Issue:** The plan still mentions "one evidence-grounded task" in the decision record, but does not include it in execution.
- **Fix:** Add it. Without that task, the paper narrative is still weaker than what the Editor and proposal recommend.

## 7. Consistency Check

- **Verdict:** BLOCKER
- **Issue:** The master plan does not fully align with the decision record. The decision record explicitly says the positive control should evaluate `direct_prediction`, `decomposed_impact`, and one evidence-grounded task (`docs/DECISION_20260411_post_amber.md:54-56`, `95-104`). The master plan keeps only the first two. That weakens the exact narrative the Editor recommended (`docs/DECISION_20260411_post_amber.md:144-157`).
- **Fix:** Amend the Phase 5 plan to include one evidence-grounded task in the actual run plan, not as a later optional idea.

- **Issue:** The master plan and CPT spec contradict each other on the inference stack. Phase B assumes an AWQ vLLM baseline server (`plans/phase5-qwen-positive-control.md:79-82`). Phase D says training uses the full-precision base (`plans/phase5-qwen-positive-control.md:216-217`). The master plan's serve command omits quantization (`plans/phase5-qwen-positive-control.md:263-267`), while the CPT spec's serve command uses AWQ (`CPT_TECHNICAL_DESIGN.md:156-165`). If Arm 0 baseline and Arms 1-3 are not served from the same base stack, you have a confound before you start.
- **Fix:** Freeze one inference stack for all four arms and name it explicitly, including checkpoint, quantization choice, vLLM version, sampling params, and LoRA loading method.

- **Issue:** The statistical plan is also inconsistent across documents. The spec says mixed model; the master plan says Fisher exact. The spec expects validation files; the master plan omits them. The proposal says the paper's main behavioral contrast is outcome-proximal versus evidence-grounded (`docs/RESEARCH_PROPOSAL_v2.md:252-271`), while the master plan still centers direct versus impact.
- **Fix:** Reconcile all of this in one frozen design document before executing any new run. Right now the "master plan" is not actually master.

- **Issue:** The current plan only partially supports the paper narrative "task design gates observability." Direct versus impact is a useful within-outcome-family contrast, but it is still weaker than direct versus authority. Two outcome-prediction variants do not fully demonstrate the gate the proposal argues for.
- **Fix:** If you want to keep the Phase 5 scope sane, use `decomposed_authority.matched` as the single evidence-grounded task. That gives you the stronger narrative without exploding the prompt space.

## Overall Assessment

Not ready to execute.

The causal idea is good. The actual plan is not. The biggest problem is not one bad hyperparameter; it is that the plan assumes a Qwen/vLLM/LoRA/white-box pipeline that does not exist yet in this repo, then layers an inconsistent analysis plan on top of it. If you run this as written and get a null or messy result, you will not know whether you invalidated the metric or just invalidated the implementation.

## Top 5 Issues Ranked by Severity

1. **Pipeline blocker:** the current code cannot run the Qwen plan as written. Qwen config selection, prompt logprobs, guided JSON, runtime LoRA loading, and evidence-grounded tasks are all missing or hardcoded away.
2. **Statistical blocker:** the primary analysis is wrong for the design. The same cases are reused across arms, but the plan falls back to Fisher exact and reintroduces multiplicity.
3. **Training-format blocker:** archive-style CPT to chat-style JSON transfer is assumed, not demonstrated. Without a bridge test, a null result is uninterpretable.
4. **Narrative blocker:** the plan omits the evidence-grounded task required by the decision record and the proposal, so it still underserves the "task design gates observability" claim.
5. **Schedule blocker:** the 12-day estimate ignores the fact that the required scripts, corpora, and white-box pipeline do not yet exist.

## Suggested Plan Revisions

1. **Rewrite Phase A.** Change the confirmatory estimand from `Arm 2 vs Arm 0 on exposed` to either `Arm 2 vs Arm 1 on exposed` or a paired `arm x exposed` interaction with `case_id` clustering. Explicitly demote `Arm 3 vs Arm 0` and `Arm 2 vs Arm 0` to secondary/supportive if they are not the sole primary claim.
2. **Insert a new Phase B0: Qwen pipeline hardening.** Required outputs: settings parameterization, Qwen sampling params, schema-guided JSON path, prompt logprob capture, cache-key fix, and a 5-case smoke test showing valid JSON plus prompt logprobs.
3. **Revise Phase C2.** Keep Arm 1 structurally matched by retaining the outcome field with a neutral placeholder, add `valid.jsonl` outputs, and specify exclusion rules for task replay and validation corpora.
4. **Revise Phase D.** Add a `10-case` Arm 2 bridge/dose pilot before full 3-arm training. If archive-style training does not surface in chat-format inference, switch to a mixed archive+chat bridge corpus before spending the full training budget.
5. **Revise Phase D5 / CPT spec Section 7.** Freeze one inference stack for all arms, with a pinned vLLM version and explicit LoRA loading method. Do not leave "dynamic loading via model field" as a hand-wave.
6. **Revise Phase E.** Add an E0 implementation step that wires `false_outcomes.json` into evaluation so Arm 3 uses held-out false outcomes rather than on-the-fly negations.
7. **Revise Phase E/F white-box language.** Separate metrics that are defined on all 606 cases from metrics that are only defined on the 115 known-outcome cases.
8. **Add the evidence-grounded task now.** The lowest-friction option is `decomposed_authority.matched`, because the matched-slot scoring path already exists.
9. **Expand the drift/specificity controls.** Use all unexposed cases for spillover checks; treat the 25-case same-period holdout as qualitative, not definitive.
10. **Replace the 12-day schedule.** Use a staged schedule: implementation hardening, baseline, corpus build, 10-case pilot, full training, evaluation, analysis. If time is tight, cut scope to MVP instead of pretending the current full plan fits in 12 days.
