---
title: Removal of Conditional Quality Gates on E_FO / E_NoOp; WS6 Made Unconditional; Strict-Majority Denominator Rule
date: 2026-04-29
phase: Phase 7
authority: |
  Supersedes R5A_FROZEN_SHORTLIST.md §2 quality-gate condition 3 (both E_FO and E_NoOp);
  reframes §2 condition 2 as descriptive coverage report rather than gate;
  retires plan §7.1A Stage 2 family states S16a / S16b / S12 (S20 is the only legal default state);
  amends DECISION_20260427_pcsg_redefinition.md §2.5 (WS6 trigger language).
related_docs:
  - docs/DECISION_20260427_pcsg_redefinition.md (PCSG redefinition + Path E + WS6 conditional — partly superseded here)
  - refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md (Round 1 design review that surfaced the gate ambiguity)
  - refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md (frozen scope; amendments header updated to point here)
  - plans/phase7-pilot-implementation.md (master plan; §7.1, §7.1A, §13 affected)
status: SIGNED — committed alongside the Tier-0 documentation batch
---

# Decision Memo — Gate Removal, Unconditional WS6, Strict-Majority Denominator

## 1. Problem statement

The R5A frozen shortlist (`R5A_FROZEN_SHORTLIST.md §2`) made E_FO and E_NoOp
**conditional confirmatory** — they enter the 20-coefficient confirmatory
family only if a three-condition quality gate passes. Gate condition 3 reads:

> mean |delta| > 0 on ≥ 5/9 models

Round 1 design review (2026-04-27 to 2026-04-29) surfaced two distinct
problems with this design:

### 1.1 Anti-pattern: gating measurement of X on the magnitude of X

Condition 3 conditions further analysis on the very signal it intends to
measure. The intended scientific reading of E_FO is "non-compliance to a
visible false outcome" — high E_FO = strong evidence that the model used
memorized truth to override the perturbation. Concretely:

- **Naive model** (no memorization): reads "公司股价下跌 5%" in the
  perturbed article, predicts negative sentiment → flips relative to
  baseline → high `|delta|`, low E_FO score.
- **Memorizing model**: knows the real outcome was "上涨", overrides the
  perturbed text → predicts positive (matches truth) → no flip relative
  to baseline → `|delta| ≈ 0`, high E_FO score.

Under condition 3, a fleet that **perfectly memorizes everything**
(strongest possible leakage signal) produces `|delta| ≈ 0` on most
models and **fails the gate** — exactly the opposite of the intended
behavior. The dream finding is gated out.

### 1.2 Inability to distinguish "perfect memorization" from "perturbation invisible"

Condition 3's stated intent was to weed out perturbation-engineering
failures: cases where the model never attended to the changed slot at
all (so output matches baseline because the model didn't see the
change). But the failure mode "perfect memorization" produces the
**same observable** (`|delta| ≈ 0`) as "perturbation invisible". The
gate cannot tell them apart and therefore cannot serve its intended
purpose.

A subsequent attempt (Fix β in the 2026-04-29 deliberation) replaced
"mean |delta| > 0" with "per-model SD of E_FO scores > σ_min". This is
better statistically but inherits the same epistemic problem: σ_min is
an arbitrary pre-data threshold, and the gate still refuses analysis on
saturated regimes.

## 2. Decisions

### 2.1 Gate condition 3 is removed entirely

E_FO and E_NoOp gate condition 3 (`mean |delta| > 0 on ≥ K/N models`,
in any reformulation) is removed from `R5A_FROZEN_SHORTLIST.md §2`.

Both estimands remain in the **confirmatory family** without conditional
status. The 20-coefficient `S20` family is the **only default legal
Stage 2 state**. The pre-registered §8.2 mixed model is fit on whatever
distribution the pilot produces; if E_FO is at ceiling or floor for
some models, the resulting wide CIs are an honest reflection of the
data, not a defect that requires gating.

### 2.2 Gate condition 2 becomes a descriptive coverage report

Condition 2 (`eligible case coverage ≥ 60% of pre-cutoff cases`) is
**retained as a reportable metric** but **demoted from a gate**:

- The pilot QC report and Stage 2 prereg supplement must publish actual
  eligible coverage per perturbation × event type.
- Coverage below 60% does NOT demote the estimand; it is reported as a
  caveat in the methods section.
- This protects the analysis from silent low-coverage situations
  without using coverage as a categorical decision lever.

### 2.3 Gate condition 1 is retained unchanged

Condition 1 (`audit pass rate ≥ 85% overall, no event type < 75%`) is
a **data-quality** gate, not a measurement-signal gate. It enforces
that the perturbations themselves are well-formed: no unintended cues,
target-local edits, economic consistency, natural CLS style. Items
failing audit are removed from the eligible pool **before** they enter
analysis — the gate operates on individual perturbation artifacts, not
on the estimand's aggregate behavior.

This condition is not subject to the anti-pattern in §1.1 because it
is independent of what E_FO measures: an audit pass/fail judgement
made by a human reviewer on the perturbation text has no causal
dependency on whether memorization signal exists in model outputs.

### 2.4 WS6 (mechanistic localization) is unconditional

WS6 (Wang et al. 2025-style Decision Score / KL / activation patching
on per-layer hidden states) is **no longer conditional** on E_FO
clearing a behavioral trigger. It is a planned exploratory analysis
that runs regardless of E_FO's behavioral magnitude.

Operational reason: hidden-state extraction is now eager pre-computed
in WS1 cloud Stage 2.7 (Path C, see §3.2 of this memo), so WS6 has its
data regardless of behavioral outcomes. Analysis cost (logit-lens, KL,
patching) is researcher-time, not GPU spend.

Scientific reason: WS6 findings are informative under **any** E_FO
distribution:
- High E_FO (strong override) → mechanism analysis localizes where
  override happens (the original Wang et al. story).
- Low E_FO (no override) → mechanism analysis localizes where the
  fleet *fails* to override, distinguishing "slot not attended" (early
  layers indifferent) from "slot attended but no override decision"
  (late layers null).
- Mixed E_FO → contrast analysis between override-cases and
  follow-cases at the same layer index, identifying the distinguishing
  representations.

Each branch is a publishable finding. There is no scientific reason to
condition the analysis on a particular E_FO regime.

### 2.5 Reserve promotion rules are retained but rescaled

`R5A_FROZEN_SHORTLIST.md §4` reserve promotion rules for E_extract and
E_ADG remain in force. Reserve promotion is **not the same** as a
quality gate:

- **Quality gate** (removed): conditioned analysis on the estimand's
  own signal magnitude — anti-pattern.
- **Reserve promotion** (retained): conditioned the *inclusion* of a
  reserve estimand on independent indicators (E_extract hit rate,
  E_ADG-related triggers). Promotion failure leaves the reserve in the
  appendix; promotion success expands the reported analysis. This is a
  scope decision, not a measurement gate, and does not exhibit the
  circularity in §1.1.

The numeric thresholds (`3/9`, `5/9`) in promotion rules are rescaled
to the strict-majority rule below (§2.6) for the 14-model fleet:
`3/9 → ⌈14/3⌉ = 5/14`; `5/9 → ⌊14/2⌋ + 1 = 8/14`.

### 2.6 Strict-majority denominator rule

All "K/N models" thresholds across §2 (data-quality coverage report),
§3 (E_FO_mech: now obsolete trigger), and §4 (reserve promotion) are
evaluated using:

- **Confirmatory-style "majority" thresholds**: `K = ⌊N / 2⌋ + 1`
  ("strict majority", where N is the operator-eligible fleet size at
  run time).
- **One-third-style "minority sufficient" thresholds**:
  `K = ⌈N / 3⌉` (used only by E_extract main-text promotion).

For the current 14-model fleet (10 white-box + 4 black-box):

| Old threshold | Operator-eligible N | New threshold |
|---|---|---|
| 5/9 (gate condition 3 — REMOVED, no longer used) | n/a | n/a |
| 5/9 (E_FO_mech / WS6 trigger — REMOVED, see §2.4) | n/a | n/a |
| 5/9 (E_extract reserve → confirmatory) | 14 P_predict | **8/14** |
| 3/9 (E_extract reserve → main-text) | 14 P_predict | **5/14** |

For future fleet expansions (e.g., adding Llama-3 white-box pair), the
formulas re-derive K from the new N at run time; **fleet expansion
alone no longer triggers a frozen-shortlist amendment** as long as the
formulas are honored.

The actual K used in any given run must be recorded in the
`RunManifest.quality_gate_thresholds` field (added by the pending
RunManifest closure work, Tier-0 #1).

## 3. Effects downstream

### 3.1 Confirmatory family

`S20 (5 estimands × 4 factors)` is now the **only** default Stage 2
state. The §7.1A demotion ladder (`S16a` / `S16b` / `S12`) is retired:
gates that triggered demotion no longer exist.

A new decision memo would be required if some unforeseen failure mode
(e.g., the cross-version PCSG pair fails common-vocab eligibility for
all probe articles, see §7.1A "estimand readiness failure" addition)
warrants a non-default family. Such a path is no longer pre-registered.

Westfall-Young stepdown max-T continues to apply over the full
20-coefficient family, evaluated on the data the pilot actually
produces. Saturation cells (E_FO at ceiling for some models) yield
wide CIs, which is the correct behavior.

### 3.2 WS6 implementation moves to WS1 Stage 2.7 (Path C eager pre-compute)

`plans/ws1-cloud-execution.md §5` adds a new **Stage 2.7 — Hidden-state
extraction** between Stage 2 (per-model P_logprob loop) and Stage 2.5
(Path E cutoff probe). On the same AutoDL instance, after vLLM has
completed all 10 white-box models, the offline_hf backend re-loads each
model and extracts hidden states for a 30-article subset.

Cost: ~5 hr GPU = ~40 RMB on RTX PRO 6000 @ 8 RMB/hr. Disk: 25-60 GB
fp16 .safetensors (compressed to 30-50 GB tar.zst for transfer).

The 30-article subset is selected by:
- Eligibility: `fo_slotable=true` (so the same articles can support
  WS6 false-outcome mechanism analysis).
- Stratification: equal allocation across the pilot event-type
  taxonomy (5 super-types × 6 articles, or 4 super-types × 7-8
  articles, whichever the pilot uses).
- Cross-model alignment: the same 30 case_ids are used for all 10
  white-box models so activation-patching can compare layer
  representations across cases.

### 3.3 BL2 negative control (n_post = 350, Option I)

A separate Tier-0 decision in the same batch (BL2 TOST) replaces the
n_post = 20 negative control with n_post = 350 to make the SESOI = 0.15
TOST equivalence test mathematically achievable (~60% TOST power at
true effect = 0). This is a sample-size rebalance, not a gate change,
but it is part of the same Tier-0 commit; see plan §6.2 / §8.6.

Pilot total N changes from 100 → 430 (80 pre-cutoff + 350 post-cutoff).
The pre-cutoff count, factor quotas, and audit volume are unchanged.
Post-cutoff CLS sampling (≥ 2026-02-01) requires additional corpus
extraction; tracked as a separate operational task.

### 3.4 Documents updated in the same commit

- `R5A_FROZEN_SHORTLIST.md` §2 / §3 / §4 + amendments header
- `plans/phase7-pilot-implementation.md` §7.1, §7.1A, §13, §6.2, §8.6,
  §1, §5.2, §11.2, §14.2 (fleet-count sweep)
- `plans/ws1-cloud-execution.md` §5 (Stage 2.7) + §4 (cost) + §8 (sign-off)
- `docs/DECISION_20260427_pcsg_redefinition.md` §2.4 (1,440 → 2,160)
  and §2.5 (WS6 unconditional)
- `docs/DECISION_20260426_phase7_interfaces.md` (supersession banner)
- `PENDING.md` (WS6 entry rewrite; Path E corpus count)
- `config/pilot_sampling.yaml` (post-cutoff target 20 → 350)

## 4. What this memo does NOT change

- **Westfall-Young multiplicity procedure** unchanged.
- **Audit protocol** (kappa ≥ 0.70 etc.) unchanged.
- **PCSG cross-version pair definition** (DECISION_20260427 §2.1) unchanged.
- **Path E empirical cutoff probe design** unchanged (only the article
  count fix from 1,440 → 2,160 is housekeeping).
- **Fleet roster** (10 white-box + 4 black-box) unchanged. Llama
  candidate pair is a separate, future decision.
- **Reserve promotion principle** (E_extract, E_ADG, E_schema_cont
  from R5A_FROZEN_SHORTLIST §4) unchanged in spirit; numeric
  thresholds rescaled per §2.6.

## 5. Sign-off

This memo is committed alongside the rest of the Tier-0 documentation
batch (PCSG denominator policy, WS6 Path C execution path, BL2 Option I
sample expansion). Together they constitute the design corrections
arising from R5A Round 1 design review (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/`).

After commit, the next blocker is the Tier-0 implementation batch
(items 1-6 + 10 in `SYNTHESIS.md` §5): RunManifest closure, fleet-pin
writer, knee-detector replacement, Path E joiner, distinct Path E run
mode, pcsg_pairs validator, and power-simulation rewrite. These open
the path to cloud spend.
