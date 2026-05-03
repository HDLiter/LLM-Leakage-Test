# PENDING — Cross-Session Open-Item Index

> **Purpose**: persistent to-do index for items that span sessions. Any pending decision, pending investigation, or pending external action the project is waiting on should have one entry here.
>
> **Authority**: this file is the single source of truth for the *status* of each item. Individual plan / review / decision documents may reference an item here but should not duplicate its status.
>
> **Update rule**: when an item resolves, move it to `## Recently closed` at the bottom (keep for ~30 days), then delete. Do not silently remove — the history matters.
>
> **Last updated**: 2026-05-03

---

## Active open items

### Phase 8 MC simulation — post-pilot calibration
- **Context**: `scripts/planning_power_calculator.py` is the closed-form planning power calculator (renamed 2026-04-30 from `simulate_phase8_power.py`); the §8.8 Monte-Carlo simulator is a separate tool that has not yet been written. Per DECISIONS.md decision #3 ("two-tool model") the MC simulator must be calibrated from pilot `hat(beta)` and `hat(Sigma)` and is the prereg-grade power source.
- **External action needed**: implement the §8.8 MC simulator after pilot data lands. See `plans/phase7-pilot-implementation.md` §8.8 (Tier-R2-1 adds the two-tool-model paragraph).
- **Blocking**: PREREG_STAGE1 power claims.
- **Owner**: post-pilot analyst.
- **Target resolution date**: post-pilot.

### WS1 white-box fleet pinning
- **Context**: `config/fleet/r5a_fleet.yaml` still carries `<TBD>` for `tokenizer_sha` and `hf_commit_sha` on all 12 white-box entries. Plan §10.1 forbids confirmatory runs with `<TBD>` placeholders; the PR1 validators and confirmatory hard-fail gate prevent these placeholders from silently landing in a final manifest.
- **External action needed**: on AutoDL Stage 1, after `huggingface-cli download` completes for each white-box model, run `python scripts/ws1_pin_fleet.py --hf-cache <path> --vllm-image-digest sha256:<64-hex>` to discover the loaded HF snapshot commit and SHA-256 tokenizer content hash, write them into `config/fleet/r5a_fleet.yaml`, append the pinning log, and rebump `fleet_version`.
- **Blocking**: WS1 cloud run final commit. Smoke runs allowed pre-pin.
- **Owner**: cloud-run operator (Claude Code on AutoDL session).
- **Target resolution date**: before WS1 pilot run.

### BL2 post-cutoff sample expansion — CLS extraction beyond 2026-02
- **Context**: `docs/DECISION_20260429_gate_removal.md` §3.3 + plan §6.2 expanded BL2 post-cutoff bucket from 20 → 350 cases, sampled from `>= 2026-02-01`. The original 20-case sampling pool is insufficient for this volume.
- **External action needed**: extract additional CLS articles published `>= 2026-02-01` to support 350-case sampling with category quotas (policy / corporate / industry / macro). User to trigger CLS scrape; Claude Code to flag this when WS4 sampling step is reached.
- **Blocking**: WS4 pilot manifest freeze (the 350-case post-cutoff bucket cannot be sampled without expanded corpus).
- **Owner**: user (data extraction) + Claude Code (sampling script + reminder hook at WS4).
- **Target resolution date**: before WS4 pilot manifest freeze.
- **Notes**: Implementation must NOT silently fall back to fewer than 350 articles without a memo. Tracked as Tier-0 reminder per session.

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

### WS0.5 — Thales alignment design
- **Context**: `plans/phase7-pilot-implementation.md` §5.1A reserves WS0.5 as a named workstream but does NOT specify scope, deliverables, file paths, or effort. The v2.1 revision over-committed these; v2.2 softened back to a gate-only placeholder.
- **Decision needed**: new session dedicated to Thales reuse-vs-rebuild for the 4 confirmatory factors (Cutoff Exposure, Historical Family Recurrence, Target Salience, Template Rigidity) plus Bloc 3 factors (Structured Event Type, Disclosure Regime / Modality, Authority). Produce a dedicated `docs/DECISION_*` memo that answers:
  - **T1**: does Thales's topic-classification pipeline (EventType taxonomy) have persisted outputs on the CLS v3 sample, or does it need to run?
  - **T2**: does Thales have (or can it derive) an `(entity, event_type, date_window)` frequency index suitable for `historical_family_recurrence`?
  - **T3**: does CLS raw data preserve publisher metadata at coverage good enough for extra-corpus Authority operationalization?
  - scope: how much is reused verbatim, what adapter code is needed, what validation is sufficient
  - effort estimate once scope is settled
- **Blocking**: pilot manifest freeze (Section 6) and Section 14.4 sign-off.
- **Owner**: user (wants separate session).
- **Target resolution date**: before WS4.
- **Related docs**: `docs/THALES_SIGNAL_PROFILE_REVIEW.md`, `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`, `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md`.

---

## Deferred (not actively worked, revisit when triggered)

### Phase 7b reserve promotion
- **Context**: `plans/phase7-pilot-implementation.md` §7.2A defines Phase 7b as non-critical-path contingency, activated only if pilot triggers promotion rules for `E_ADG`, `E_extract`, or `E_schema_cont` per `R5A_FROZEN_SHORTLIST.md` §4.
- **Status**: dormant. Do not work on implementation until a pilot trigger fires.
- **Revisit trigger**: Phase 7 pilot results surface a reserve estimand that satisfies its frozen promotion rule.

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
