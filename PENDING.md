# PENDING — Cross-Session Open-Item Index

> **Purpose**: persistent to-do index for items that span sessions. Any pending decision, pending investigation, or pending external action the project is waiting on should have one entry here.
>
> **Authority**: this file is the single source of truth for the *status* of each item. Individual plan / review / decision documents may reference an item here but should not duplicate its status.
>
> **Update rule**: when an item resolves, move it to `## Recently closed` at the bottom (keep for ~30 days), then delete. Do not silently remove — the history matters.
>
> **Last updated**: 2026-05-19

---

## Active open items

### Phase 8 MC simulation — post-pilot calibration
- **Context**: `scripts/planning_power_calculator.py` is the closed-form planning power calculator (renamed 2026-04-30 from `simulate_phase8_power.py`); the §8.8 Monte-Carlo simulator is a separate tool that has not yet been written. Per DECISIONS.md decision #3 ("two-tool model") the MC simulator must be calibrated from pilot `hat(beta)` and `hat(Sigma)` and is the prereg-grade power source.
- **External action needed**: implement the §8.8 MC simulator after pilot data lands. See `plans/phase7-pilot-implementation.md` §8.8 (Tier-R2-1 adds the two-tool-model paragraph).
- **Blocking**: PREREG_STAGE1 power claims.
- **Owner**: post-pilot analyst.
- **Target resolution date**: post-pilot.

### WS6 — mechanistic analysis (now unconditional, eager pre-compute)
- **Context**: `docs/DECISION_20260429_gate_removal.md` §2.4 / §3.2 made WS6 unconditional; hidden states pre-computed in WS1 cloud Stage 2.7 (Path C, ~5 hr GPU). The earlier conditional trigger (`>= 5/9` then `>= 5/14`) is retired alongside the gate that produced it.
- **Investigation needed**: after WS1 Stage 2.7 hidden states are downloaded, scope WS6 analysis modules (DS via logit-lens, layer-wise KL, activation patching) for WS5. No GPU rerun required since hidden states are pre-computed.
- **Blocking**: dormant until WS1 Stage 2.7 artifacts land locally.
- **Owner**: post-WS1 session.
- **Target resolution date**: WS5 timeline.

### OPEN 4 — Phase 7 audit staffing
- **Context**: `plans/phase7-pilot-implementation.md` §9.1 default staffing assumes 2 reviewer + 1 adjudicator + 1 stats merge; project is single-operator by default.
- **Decision needed**: recruit 1 external collaborator (≈20 hours for IAA double-coding on 20% sample) OR accept intra-rater test-retest fallback with explicit Phase 8 methods caveat.
- **Blocking**: Phase 7 pilot execution (WS4). Not blocking WS0-WS3 engineering.
- **Owner**: user (recruiting attempt in progress).
- **Target resolution date**: before WS4 pilot manifest freeze.
- **Notes**: pitch template and qualification criteria discussed 2026-04-18 session; see conversation notes if recruiting.

---

## Deferred (not actively worked, revisit when triggered)

### Phase 7b reserve promotion
- **Context**: `plans/phase7-pilot-implementation.md` §7.2A defines Phase 7b as non-critical-path contingency, activated only if pilot triggers promotion rules for `E_ADG`, `E_extract`, or `E_schema_cont` per `R5A_FROZEN_SHORTLIST.md` §4.
- **Status**: dormant. Do not work on implementation until a pilot trigger fires.
- **Revisit trigger**: Phase 7 pilot results surface a reserve estimand that satisfies its frozen promotion rule.

### Phase 8 exploratory goal-frame perturbation
- **Context**: Cao, Jiang & Xu (2026), `Seeing the Goal, Missing the Truth`, shows that disclosing downstream goals can shift financial LLM intermediate scores, with pre-cutoff gains that attenuate post-cutoff. The 2026-05-07 incremental sweep also added sycophancy and LLM-generated-measurement papers that support treating goal disclosure as a measurement-bias risk, not a current confirmatory estimand.
- **Status**: accepted into the Phase 8 exploratory backlog as `C_GoalFrame`. Do not add to the current confirmatory family or WS3 `C_CO` / `C_NoOp` work.
- **Decision needed**: after WS2 `P_predict` prompt lockdown and the core confirmatory experiments, decide whether Phase 8 should run `C_GoalFrame` as (a) behavior-only `P_predict` prompt variants or (b) behavior plus a small white-box internal-probe appendix reusing WS6-style DS / KL / activation-patching machinery.
- **Candidate scope**: neutral/blind baseline, return prediction, earnings or competition prediction, memory-leakage audit, strict article-only measurement, and possibly user-confirmation framing. The primary exploratory contrast should remain a pre/post-cutoff interaction, not the raw prompt delta.

### English expansion
- **Context**: memory `project_english_expansion.md` — stretch goal, 5 trigger conditions evaluated after Chinese pilot.
- **Status**: dormant.
- **Revisit trigger**: Chinese pilot delivers usable results and at least 3 of the 5 trigger conditions hold.

---

## Structural questions (answer when relevant)

### Phase 8 main-run launch readiness
- **Context**: Section 13 exit gate lists 10 hard conditions.
- **Status**: will be fully evaluated at end of Phase 7.
- **Revisit trigger**: Phase 7 WS5 completes.

---

## Recently closed

### WS0.5 — Thales alignment design
- **Resolved 2026-05-19**: design closed via `docs/DECISION_20260518_ws0_5_thales_alignment.md` v0.3 (post-round-2 Codex review).
  - **Round-0** (2026-05-18): v0.1 → Codex review → MAJOR-REVISIONS-NEEDED (4 blockers + 4 majors + 1 minor; 9 issues).
  - **v0.2** (2026-05-19): 9 round-0 issues resolved via interactive user-Claude review (see `temp/ws0_5_issue_decisions.md`).
  - **Round-1** (2026-05-19): 3 parallel Codex reviewers (ML engineer / statistician / measurement), all returned MAJOR-REVISIONS-NEEDED with 23 complementary critical issues (E-1…E-10, S-1…S-8, C-1…C-5). No cross-role conflict.
  - **v0.3** (2026-05-19): all 23 round-1 issues patched in-place.
  - **Round-2** (2026-05-19): 3 parallel Codex re-reviewers — Measurement APPROVE, ML-engineer APPROVE-WITH-MINOR-PATCHES, Statistician APPROVE-WITH-MINOR-PATCHES. 2 narrow text patches applied in-place to v0.3 (§4.1 MDE preflight q-grid wording, §5.2 R4 cache lookup key).
  - T1 / T2 / T3 verification answers + reuse-vs-rebuild decisions + Scheme Y auto-tune validation + replay-from-cache determinism + budget ledger all locked. Implementation gates (frozen prompt configs, `factor_schema.yaml`, quota/discriminant/replay artifacts) remain per memo §9 closure conditions; tracked through memo §10 S1-S5 schedule.
- **Related docs**: `docs/DECISION_20260518_ws0_5_thales_alignment.md` (memo), `temp/ws0_5_alignment_review.md` (round-0), `temp/ws0_5_issue_decisions.md` (round-0 → v0.2 decision log), `temp/ws0_5_round1_*_review.md` (round-1, 3 files), `temp/ws0_5_round2_*_review.md` (round-2, 3 files), `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`, `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md`.

### WS1 white-box fleet pinning
- **Resolved 2026-05-05**: all 12 white-box `hf_commit_sha` and
  `tokenizer_sha` fields are pinned in `config/fleet/r5a_fleet.yaml` at
  fleet version `r5a-v2.3-2026-05-03+pinned-whitebox-20260505`. Qwen2.5,
  Qwen3, and Llama use explicit HF commit snapshots under `/data/models`.
  GLM uses the fixed HF commit plus a documented custom slow-tokenizer
  materials manifest because the upstream snapshot has no `tokenizer.json`.

### WS1 black-box `api_model_name` resolution
- **Resolved 2026-05-03**: `docs/DECISION_20260503_blackbox_refresh.md` refreshes the 4-model black-box roster; `config/fleet/r5a_fleet.yaml` now has concrete provider slugs for DeepSeek V4 Pro, GPT-4.1, GPT-5.1, and Claude Sonnet 4.6.

### Phase 7 orchestration writer — runstate DB contract
- **Resolved 2026-05-03**: `src/r5a/orchestration/runstate.py` now creates and updates `request_runstate` with the `RunStateRow` fields plus seed-triplet columns, validates transitions through `pending`, and supports the finalizer's runstate gate.

### WS1 — `LogProbTrace` contract closure
- **Resolved 2026-05-03**: `LogProbTrace` and Parquet persistence now carry required non-null `quant_scheme`, `weight_dtype`, and `vllm_image_digest`; nullable `top_logprobs` and `hidden_states_uri`; producer CLI support for `--top-logprobs`; and a confirmatory finalizer check for required trace fields.

### Path E — empirical cutoff probe data sourcing
- **Resolved 2026-05-03**: `scripts/build_exposure_horizon_probe_set.py` built `data/pilot/exposure_horizon/probe_set_monthly60_36mo.json` locally from CLS with 36/36 months at 60 articles/month (2,160 total); ship this ignored JSON with the WS1 cloud data bundle.

### Black-box provider credential smoke — OpenRouter auth
- **Resolved 2026-05-03**: user replaced the expired `OPENROUTER_API_KEY`; `/api/v1/auth/key` and `/api/v1/credits` now return HTTP 200, and `python scripts/smoke_provider_slugs.py --max-tokens 16` passes for DeepSeek official `deepseek-v4-pro` plus OpenRouter routes `openai/gpt-4.1`, `openai/gpt-5.1`, and `anthropic/claude-sonnet-4.6`.

### Llama fleet addition — Meta HF gating pre-flight
- **Resolved 2026-05-03**: user completed Meta gated-repo approval; `HF_TOKEN` authenticates as `HDLiter`, and authenticated HEAD checks to `config.json` return HTTP 200 for `meta-llama/Meta-Llama-3-8B-Instruct` and `meta-llama/Llama-3.1-8B-Instruct`. `config/fleet/r5a_fleet.yaml` was canonicalized to the non-redirect Llama-3.1 repo id.

### BL2 post-cutoff sample expansion — CLS extraction beyond 2026-02
- **Resolved 2026-05-03**: copied the refreshed CLS snapshot from `D:\GitRepos\Thales\datasets\cls_telegraph_raw` into this repo's ignored `data/cls_telegraph_raw/` to isolate LLM-Leakage-Test from future Thales corpus changes. Verified mirror size: 2,316 top-level files, 975,459,494 bytes, through 2026-05-03. Verified `>= 2026-02-01` coverage: 93 daily files, 55,324 raw items, 46,117 title+body eligible items, enough for the 350-case BL2 post-cutoff bucket.

---

## Format guidance for new entries

```markdown
### <short name> — <one-line description>
- **Context**: what/where the item lives, with pointer to the governing doc.
- **Decision needed** OR **Investigation needed** OR **External action needed**: the concrete ask.
- **Blocking**: what downstream work cannot proceed without this.
- **Owner**: who resolves it (user / collaborator / dependent on external party).
- **Target resolution date**: ISO date or "before <named gate>".
- **Notes**: optional; conversation references, pitch templates, prior attempts.
```

Keep entries short. Detail lives in plan docs or decision memos; `PENDING.md` is just the index.
