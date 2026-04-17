# Pre-Registration: Qwen CPT Positive Control Experiment

**Registration date:** 2026-04-12
**Status:** FROZEN (no modifications after first CPT training call; see Section 17 for freeze scope)
**Protocol version:** 1.3 (post-Codex G1 round 3; fixes 2 remaining BLOCKERs)
**Decision basis:** `docs/DECISION_20260411_post_amber.md`
**Execution plan:** `plans/phase5-qwen-positive-control.md`
**Review log:** `refine-logs/decision_20260411/PLAN_REVIEW.md`
**Prior results:** Phase 4 (amber-mirror-lattice), `docs/PILOT_RESULTS.md`
**Supersedes:** The decision record (`docs/DECISION_20260411_post_amber.md`,
Section 5b) recommended CMH stratified by `anchor_binary` as the primary
analysis. This preregistration replaces that with exact McNemar, which is
the correct test for this arm-paired design where the same cases are
evaluated under multiple CPT conditions. CMH is retained as secondary
analysis S6 for the DeepSeek cross-model replication (unpaired design).

---

## 1. Background and Rationale

Phase 4 of this project (DeepSeek-chat, 606 cases) found a task-dependent
pattern in false-outcome flip rates:

- **`direct_prediction` (hedged):** post-cutoff > pre-cutoff (MH OR=0.64,
  p=0.036). Interpreted as suggestibility.
- **`decomposed_impact` (hedged):** pre-cutoff > post-cutoff (MH OR=1.95,
  p=0.022). Consistent with a memorization-direction effect.

This association has three critical weaknesses:

1. **No construct validity.** We have never shown the metric detects
   memorization when it is known to exist.
2. **Post-hoc metric.** The `hedged` flip definition emerged from a bug
   fix (Bug 3), not from a pre-registered protocol.
3. **Single model.** Only DeepSeek-chat; could be model-specific.

This experiment addresses all three by: (a) injecting known memory into
Qwen 2.5 7B via continued pretraining (CPT), (b) freezing the metric
definition before running, and (c) testing on a second model.

---

## 2. Outcome Definitions (Frozen)

These definitions are locked and apply to all analyses in this experiment.

| Label | Definition |
|-------|-----------|
| `strict_flip` | Prediction polarity crossed (e.g., up -> down, positive -> negative) |
| `neutral_retreat` | Non-neutral prediction retreated to neutral |
| `hedged_flip` | `strict_flip` UNION `neutral_retreat` |
| `steadfast` | Prediction unchanged under false-outcome probe |

The primary endpoint uses the `hedged` definition applied to
`decomposed_impact` slot `fund_impact`:

- **`fo_flip_impact_hedged`**: 1 if the model's `fund_impact` prediction
  under the false-outcome probe is a `hedged_flip` relative to its
  original prediction; 0 otherwise.

---

## 3. Experimental Arms

The experiment uses Qwen 2.5 7B Instruct as the base model with QLoRA
continued pretraining to inject controlled memory.

| Arm | Training Content | Purpose |
|-----|-----------------|---------|
| **Arm 0** | No training (vanilla Qwen baseline) | Reference |
| **Arm 1** | Article text + neutral placeholder outcome | Article-familiarity control |
| **Arm 2** | Article text + real known outcome | Outcome-memory injection |
| **Arm 3** | Article text + false outcome (training variant) | Polarity-inverted injection |

All arms use the same base checkpoint (`Qwen/Qwen2.5-7B-Instruct`),
the same inference stack (pinned vLLM version, identical sampling
parameters), and the same evaluation prompts. LoRA adapters are the
only variable.

### 3.1 Training Corpus Structure (per arm)

Each trained arm (1-3) receives ~2.2M tokens:

| Component | Tokens | Content |
|-----------|--------|---------|
| Plant corpus | ~0.5M | 90 exposed cases x 16 surface variants |
| Filler news | ~1.5M | ~5,000 unrelated CLS telegraphs |
| Task-format replay | ~0.2M | ~2,000 prompt/response examples (no eval cases) |

Plant documents use an **archive format** (not chat/inference format)
to minimize inference-format shortcut learning:

```
财联社新闻归档
标题：{title}
发布时间：{publish_time}
正文：{body}
后续市场反应：{outcome_text}
```

Arm 1 retains the `后续市场反应` field with a neutral placeholder
(`暂无公开跟踪数据。`) to keep document structure identical across all
three trained arms. This eliminates the format confound where one arm
has fewer fields than the others.

### 3.2 Arm 3 False-Outcome Separation

Three lexically distinct false-outcome variants are generated per case:
1. **Training variant** — used in Arm 3 CPT corpus
2. **Evaluation variant** — used in Arm 3 pipeline evaluation (held-out)
3. **Reserve variant** — for audit

The evaluation pipeline loads held-out false outcomes from disk via
`--fo-override`, NOT from on-the-fly generation. This prevents
circular contamination between training and evaluation probes.

---

## 4. Case Structure

The 606-case evaluation set is partitioned as follows:

| Set | N | Training Exposure | Role |
|-----|---|-------------------|------|
| `exposed` | 90 | Injected into Arms 1-3 | Primary analysis set for CPT contrasts |
| `pre_holdout` | 25 | Not in training | Same-period qualitative sentinels (not in inferential unexposed pool) |
| `pre_no_outcome` | 217 | Not in training | Pre-cutoff spillover controls |
| `post_cutoff` | 274 | Not in training | Post-cutoff spillover controls |
| **Unexposed (inferential)** | **491** | Not in training | Inferential spillover pool (S4, S5, drift checks) |
| **Not trained total** | **516** | Not in training | All non-exposed cases |

The 90 exposed cases are selected from the 115 pre-cutoff cases with
`known_outcome` using the following deterministic procedure:

**Split algorithm:**
1. Compute Arm 0 (vanilla Qwen baseline) results on all 115
   known-outcome cases (this is part of Phase B, before CPT)
2. Assign each case to strata defined by the cross of:
   `target_type` x `anchor_binary` x `baseline_difficulty_bin`
   where `baseline_difficulty_bin` = whether the case showed
   `fo_flip_impact_hedged=1` under Arm 0 (binary: flip / no-flip)
3. Within each stratum, sort cases by `case_id` (lexicographic)
4. Assign the first floor(N_stratum * 90/115) cases to `exposed`,
   the remainder to `pre_holdout`
5. If total exposed < 90 after step 4, fill remaining slots by
   iterating strata in order of decreasing size (ties broken by
   lexicographic sort of the stratum key tuple), taking the next
   unassigned case (by `case_id` sort) from each stratum in turn
   until 90 is reached
6. Record the split in `data/cpt/splits.json` with the random seed
   (N/A — deterministic), stratification variables, and per-case
   assignment

**Freeze point for split:** The split is computed after Phase B
(Arm 0 baseline) and recorded before Phase C (corpus preparation).
The split uses Arm 0 results as input, so it must be computed after
Arm 0 inference but before any CPT training begins.

The **inferential unexposed pool** (N=491: 217 pre-no-outcome + 274
post-cutoff) is used exclusively for inferential spillover analyses
(Condition 3, S4, S5) and the pre-specified 5pp drift flag
(Section 9.2).
It is NOT used for arm-abort screening (Section 10). The 25
same-period holdout cases are reported separately as qualitative
sentinels only (see Section 9).

---

## 5. Tasks (Frozen)

Three tasks are evaluated on all arms, all cases:

| Task | Family | Type | Role in Paper |
|------|--------|------|--------------|
| `direct_prediction.base` | Outcome-proximal | Direction (up/down/neutral) | Suggestibility reference |
| `decomposed_impact.base` | Outcome-proximal (graded) | Fund impact (5-level) | Primary memorization-direction probe |
| `decomposed_authority.matched` | Evidence-grounded | Source credibility / provenance | "Task gates observability" anchor |

The authority task extracts provenance and attribution signals (source
credibility, regulatory vs. rumor, official vs. unattributed) grounded
in verbatim article quotes. It does not ask the model to predict prices,
sentiment, or market impact. This task should therefore be less affected
by injected outcome memory, providing the key contrast for the "task
design gates observability" claim.

### 5.1 False-Outcome Flip Scoring by Task

| Task | Primary slot | Polarity values | Flip detected on |
|------|-------------|----------------|-----------------|
| `direct_prediction` | `slot_1` (direction) | up / down / neutral | Polarity cross or neutral retreat |
| `decomposed_impact` | `slot_1` (fund_impact) | strong_negative / negative / neutral / positive / strong_positive | Polarity cross or neutral retreat |
| `decomposed_authority` | `slot_1` (source_credibility) | high / medium / low / unclear | Any label change under false-outcome probe |

**Note on authority flip definition:** The authority task has no
outcome-polarity slot, so there is no natural "toward false outcome"
direction. We define `authority_hedged` as any label change on
`source_credibility` under the false-outcome probe (analogous to
sensitivity, not directional flip). This metric serves primarily as a
**negative control**: if CPT-injected outcome memory causes authority
label changes at rates comparable to impact flips, the "task gates
observability" claim is weakened.

---

## 6. Primary Hypothesis

**There is exactly one primary hypothesis. No multiplicity adjustment
is needed.**

### Construct-Validity Claim (Qwen CPT)

> On the 90 exposed pre-cutoff cases, `fo_flip_impact_hedged` rate is
> higher under Arm 2 (article + real outcome) than under Arm 1 (article
> only), after accounting for within-case pairing.

- **Primary contrast:** Arm 2 vs Arm 1 on exposed cases only
- **Primary endpoint:** `fo_flip_impact_hedged`
- **Primary test:** Exact McNemar test (paired binary: same 90 cases
  evaluated under both arms)
- **Alpha:** 0.05 (two-sided)
- **Direction of interest:** Arm 2 flip rate > Arm 1 flip rate
- **Missing-data rule:** A case is included in the paired primary
  analysis only if it produces valid, scorable JSON output on
  `decomposed_impact.base` under **both** Arm 1 and Arm 2 (both
  original and false-outcome conditions). Cases that are valid under
  one arm but invalid under the other are excluded from the McNemar
  table. The final paired N is reported alongside the primary result.
  If the paired N drops below 80 (>11% attrition), this is flagged
  as a concern and sensitivity analysis is run on the full 90 cases
  with missing values imputed as `steadfast` (conservative: biases
  toward the null).
- **Missing-data rule for all other analyses:** Each analysis type
  has its own inclusion rule:
  - **Cross-arm paired (Conditions 1, 2; S1, S2, S3):** A case is
    included only if valid and scorable on the relevant task under
    both arms being compared. These use McNemar on paired data.
  - **Cross-group unpaired (Condition 3 / S4):** Exposed-vs-unexposed
    within Arm 2. A case is included if valid under Arm 2.
  - **Cross-task paired within arm (Condition 4):** A case is included
    only if valid on both `impact` and `authority` tasks under Arm 2.
    This is a within-case, within-arm, cross-task comparison.
  - **Cross-arm matched (S5 Cochran Q):** A case is included only if
    valid under all arms being compared. Cases missing from any arm
    are excluded from the matched set.
  - The effective N is always reported alongside each test result.

### Rationale

Arm 2 vs Arm 1 isolates **outcome memory** from article familiarity.
Both arms see the same article text during training; only Arm 2 also
sees the real market outcome. If Arm 2 shows higher resistance to
false-outcome probes (more hedged flips toward neutral) than Arm 1,
the effect is attributable to outcome-specific memory, not mere
article exposure.

Arm 2 vs Arm 0 is weaker because it confounds outcome memory with
article familiarity. It is relegated to secondary analysis.

---

## 7. Conjunctive Logic for Construct Validity

The primary hypothesis test is necessary but not sufficient. Full
construct validity requires all four conditions:

| # | Condition | Test | Interpretation if fails |
|---|-----------|------|------------------------|
| 1 | Arm 1 ~ Arm 0 on `impact_hedged` (exposed) | 90% CI for rate difference falls within [-10pp, +10pp] equivalence margin | Article-only exposure alone shifts behavior beyond equivalence margin -> confound |
| 2 | Arm 2 > Arm 1 on `impact_hedged` (exposed) | Exact McNemar, p < 0.05 | **PRIMARY** |
| 3 | Arm 2 exposed > Arm 2 unexposed on `impact_hedged` | Fisher exact, p < 0.05 | Effect is local, not global drift |
| 4 | Authority flip rate < impact flip rate on Arm 2 exposed | Rate difference CI: impact_hedged - authority_hedged > 0; additionally, authority_hedged rate must not exceed Arm 0 baseline authority rate + 5pp | Task gates observability |

**Condition 1 rationale:** A non-significant McNemar test does not
establish equivalence, especially at N=90. We therefore use a CI-based
equivalence criterion: compute the Agresti-Min (2005) 90% confidence
interval for the paired rate difference (Arm 1 - Arm 0) on the
exposed cases. If this interval falls entirely within [-10pp, +10pp],
we conclude that article-only exposure did not meaningfully shift
behavior. The 10pp margin is chosen because Phase 4 DeepSeek showed
a ~5.5pp gap between pre- and post-cutoff `impact_hedged` rates
(12.3% - 6.8%); a 10pp margin is conservative relative to the effect
we aim to detect.

**CI method note:** All paired rate-difference CIs in this document
(Conditions 1, 4) use the Agresti-Min method for paired binary data.
This is the paired-data analogue of the Agresti-Caffo interval and
has appropriate coverage properties at small sample sizes.

**Condition 4 rationale:** "Less affected" must be operationalized.
We require (a) the point estimate of `impact_hedged` flip rate on
Arm 2 exposed exceeds the `authority_hedged` rate, with the
Agresti-Min 95% CI for the within-case rate difference
(`impact_hedged` - `authority_hedged`) excluding zero; and (b) the
`authority_hedged` rate on Arm 2 exposed does not exceed the Arm 0
baseline authority rate by more than 5pp (ruling out global
CPT-induced instability on the authority task).

**Interpretation table:**

| Conditions met | Claim strength |
|---------------|---------------|
| All four (1-4) | Full construct validity: outcome memory drives impact flips, task design gates it |
| 1-3 but not 4 | CPT outcome memory changes impact behavior, but task-gating claim unsupported |
| 2-3 but not 1 | CPT changed behavior, but article familiarity alone also contributes |
| 2 only | CPT had an effect on exposed cases; mechanism unclear |
| None | Metric does not detect known memorization; pivot paper |

---

## 8. Secondary and Exploratory Analyses

All secondary analyses use Benjamini-Hochberg (BH) correction
controlling the false discovery rate (FDR) at q = 0.05.

| # | Contrast | Endpoint | Test | Purpose |
|---|----------|----------|------|---------|
| S1 | Arm 2 vs Arm 0, exposed | `impact_hedged` | McNemar | CPT changed something (supportive) |
| S2 | Arm 3 vs Arm 0, exposed | `direct_strict` | McNemar | False-outcome injection shifts direct task |
| S3 | Arm 2 vs Arm 1, exposed | `authority_hedged` | McNemar | Evidence-grounded task is less affected |
| S4 | Arm 2, exposed (N=90) vs unexposed (N=491) | `impact_hedged` | Fisher exact | Specificity (= Condition 3; reported once, listed here for BH family) |
| S5 | All arms, unexposed (N=491) | `impact_hedged` | Cochran Q | No spillover to untrained cases |
| S6 | DeepSeek Phase 4 replication | `impact_hedged` MH | CMH (stratified by `anchor_binary`) | Cross-model descriptor |

### Required Interpretation Check (not multiplicity-adjusted)

If the primary test is significant, the following decomposition is
**mandatory** to interpret what drives the result:

- On Arm 2 exposed cases that show `hedged_flip` on `impact`, report
  the split between `strict_flip` and `neutral_retreat`. If the
  primary result is driven predominantly by strict flips *toward* the
  false outcome (rather than neutral retreats *away* from a memorized
  position), the mechanism interpretation differs: strict flips toward
  false suggest suggestibility, neutral retreats suggest resistance
  from memorized knowledge. This decomposition is reported alongside
  the primary result but does not gate the construct-validity claim.

### Exploratory (not corrected, reported as descriptive)

- Conflict-response taxonomy: decomposition of all cases into
  `strict_reversal`, `neutral_retreat`, `steadfast` cross-tabulated
  with `period`, `anchor_binary`, `arm`, `exposed`, `task`
- Evidence intrusion rates by task and arm
- Cross-task Spearman correlations (CFLS, flip rates)
- Dose-response curve (if Phase D0 produces multiple dose points)
- White-box triangulation (see Section 12)

---

## 9. Specificity and Drift Checks

### 9.1 Unexposed Pool Definition

The term "unexposed" in all inferential analyses (Condition 3, S4,
S5, and the 5pp drift flag) refers to the **491-case pool**: 217
pre-cutoff-no-outcome + 274 post-cutoff. These cases were never
exposed to CPT training in any arm. This pool is NOT used for
arm-abort screening (Section 10).

The 25 same-period holdout cases are a subset of the 115
known-outcome pre-cutoff cases that were NOT selected for CPT
exposure. They are **excluded** from the inferential unexposed pool
to avoid ambiguity: they share the `known_outcome` attribute with
exposed cases (which could confound drift checks), and their small
N makes them uninformative for inferential claims.

### 9.2 Spillover Drift Criterion

**Pre-specified, non-gating drift flag:** If `fo_flip_impact_hedged`
rate differs by more than 5 percentage points between any arm pair
on the 491 unexposed cases, flag as global drift. This flag does not
trigger arm retraining or exclusion (that is Section 10's role); it
is an interpretive annotation requiring cautious discussion of results.

### 9.3 Same-Period Holdout (N=25)

The 25 same-period holdout cases serve as a **qualitative** sanity
check only. At N=25, even 0 events yields a 95% Clopper-Pearson upper
bound of 13.7%, so this set cannot support strong inferential claims
about drift. It is useful for spotting gross systematic pattern shifts
(e.g., all 25 cases flip under one arm), not for excluding small
effects. Results on this set are reported descriptively but do not
enter any inferential analysis.

### 9.4 Capacity Preservation

To avoid adaptive contamination of inferential analyses, arm-abort
screening and inferential spillover tests use **separate data**:

**Arm-abort screening** (Section 10) uses only capability-level
checks that do not touch the inferential unexposed pool:

| Check | Data | Abort criterion |
|-------|------|-----------------|
| JSON validity | 200 held-out prompts (3 tasks) | Drop > 3 pp vs Arm 0 |
| General NLL | `valid_general.jsonl` (200 docs) | Degradation > 10% |
| Sentinel pattern | 25 holdout cases | Gross systematic pattern shift (qualitative) |

**Inferential spillover tests** (S4, S5) use the 491-case unexposed
pool and are computed only after all arms have passed screening.
The 5pp drift criterion (Section 9.2) is a pre-specified, non-gating
flag, not a screening gate — it does not trigger arm retraining.

---

## 10. Arm Failure Criteria

An arm is aborted and excluded from analysis if any of:

1. JSON-valid rate drops by >3 percentage points vs Arm 0
2. Held-out CLS news NLL degrades by >10%
3. Sentinel-set (N=25) shows gross systematic pattern shift,
   defined as: `fo_flip_impact_hedged` rate on the 25 holdout cases
   differs from Arm 0 by >= 5/25 (20pp), OR JSON validity on the
   holdout drops below 80%

These checks use only capability-level data (held-out prompts, NLL
validation set, qualitative sentinels) — NOT the 491-case inferential
unexposed pool. This separation ensures that inferential spillover
analyses (S4, S5) are not compromised by adaptive arm selection.

If an arm is aborted, it is retrained with reduced epochs, learning
rate, or plant repetitions. It is NOT included in analysis with
degraded capability.

---

## 11. Bridge Test Prerequisite (Phase D0)

Before full CPT training, a 10-case mini Arm 2 bridge test validates
that archive-format training surfaces in chat-format inference.

### 11.1 Bridge Pass/Fail Criteria

A case counts as "changed" if **any** of the following differ between
mini-Arm-2 and Arm 0 on `decomposed_impact.base`:

1. `fo_flip_impact_hedged` label differs (one flips, the other doesn't)
2. `fund_impact` slot value differs on the original (non-FO) prompt
3. First decisive token margin (`log p(positive) - log p(negative)`)
   shifts by > 0.5 nats

A change is "direction-consistent" if it is toward the real known
outcome (e.g., model becomes more resistant to a false outcome that
contradicts the real outcome, or shifts its original prediction toward
the real outcome direction).

- **Pass:** >= 3/10 cases show a change, AND >= 2 of those changes
  are direction-consistent
- **Fail:** < 3/10 cases show any change, OR < 2 direction-consistent

### 11.2 Dose Calibration Rule

Three doses are tested on the same 10 cases: 4x, 8x, 16x repetitions.

**Selection rule (deterministic):**
1. Eliminate any dose where the 10-case mini-arm fails the arm failure
   criteria (Section 10): JSON validity drop > 3pp or NLL degradation
   > 10% on the 10-case validation slice
2. Among surviving doses, select the **lowest dose** that achieves
   bridge pass (>= 3/10 changed, >= 2 direction-consistent)
3. If multiple doses pass with identical changed-case counts, select
   the lowest
4. If no dose passes, the bridge test has failed

### 11.3 Bridge Failure Remediation

If the bridge test fails:
1. Add a bridge corpus (~500 mixed archive+chat format examples)
2. Retrain at 16x dose and re-probe
3. If still fails after 2 attempts, archive CPT is unsuited; redesign
   training format (see failure tree, Section 13)

---

## 12. White-Box Scoring (Scope Restrictions)

White-box metrics have different scopes depending on data availability:

| Metric | Scope | N | Rationale |
|--------|-------|---|-----------|
| Min-K% (article text) | All cases, all arms | 606 | Article-text familiarity; defined for all cases |
| Min-K% (article + outcome) | Known-outcome cases only | 115 | Requires `known_outcome`; undefined for other 491 |
| Contrastive continuation margin | Exposed cases only | 90 | `LL(real) - LL(false)` given article; requires both variants |
| First decisive token margin | All cases, all arms | 606 | `log p(pos) - log p(neg)` at first label token |
| Outcome-span mean NLL | Known-outcome cases only | 115 | Perplexity on outcome tokens; requires `known_outcome` |

Metrics requiring `known_outcome` are **never** computed on the 491
cases where it is not available.

---

## 13. Failure Tree

| Outcome | Interpretation | Paper Pivot |
|---------|---------------|-------------|
| Primary passes (Arm 2 > Arm 1 on `impact_hedged`) + all conjunctive conditions | Construct validity confirmed | Full "task gates observability" narrative |
| Arm 2 > Arm 0 but Arm 2 ~ Arm 1 | CPT changed behavior but not via outcome memory | Weaken causal claim; report as "CPT effect, mechanism unclear" |
| Bridge test fails (Phase D0) | Archive -> chat transfer doesn't work | Redesign training corpus with mixed format; repeat D0 |
| All CPT signals null after bridge calibration | Metric does not detect known memorization | Pivot to "CFLS-as-comprehension + suggestibility taxonomy" paper |
| Qwen baseline replicates DeepSeek task-dependent pattern | Effect is model-general | Strengthen cross-model claim |
| Qwen baseline shows no task-dependent pattern | Effect is model-specific | Bound claims to DeepSeek case study |

---

## 14. Power Considerations

This section documents what the design can and cannot detect. It is
honest about limitations.

### 14.1 Phase 4 Baseline Rates (DeepSeek)

| Metric | Pre-cutoff rate | Post-cutoff rate | MH OR | p |
|--------|----------------|-----------------|-------|---|
| `impact_hedged` | 40/326 (12.3%) | 18/265 (6.8%) | 1.95 | 0.022 |
| `direct_hedged` | 48/328 (14.6%) | 58/272 (21.3%) | 0.64 | 0.036 |

### 14.2 Primary Test Power

The primary test is exact McNemar on 90 paired observations (same case
under Arm 1 vs Arm 2). Power depends on the **discordant-pair rate**,
not the marginal flip rate.

Assumptions for planning (conservative):
- Arm 1 baseline flip rate on exposed cases: ~12% (similar to Arm 0,
  since article-only exposure may have limited effect)
- Arm 2 flip rate under outcome memory: unknown; the target is to
  detect a meaningful increase
- Discordant-pair rate: unknown prior to running; Phase D0 bridge test
  provides an empirical estimate on 10 cases

**Detectable effects at 80% power (exact McNemar, alpha=0.05, N=90):**

| Discordant pairs | Required ratio (b/c) | Implied effect |
|-----------------|---------------------|---------------|
| 15 (~17%) | 4.0 | Large |
| 20 (~22%) | 3.2 | Large |
| 25 (~28%) | 2.8 | Moderate-large |
| 30 (~33%) | 2.5 | Moderate |

**Interpretation:** With N=90, the study is well-powered only for
moderate-to-large effects. If CPT produces a subtle shift (e.g.,
5 extra discordant pairs), the design will not detect it. This is
acceptable because construct validity requires a demonstrable,
non-trivial signal: if CPT with 16x repetitions of the real outcome
produces only a tiny behavioral shift, the metric's practical utility
for detecting natural contamination is questionable regardless.

The Phase D0 bridge test provides an early empirical read on expected
effect size before committing to the full 90-case experiment.

---

## 15. Inference Stack (Frozen)

All four arms are served from the same inference configuration:

- **Base model:** `Qwen/Qwen2.5-7B-Instruct` (full precision, NOT
  quantized at serving time — AWQ quantization interacts unpredictably
  with LoRA adapters and could confound arm comparisons)
- **LoRA loading:** `--lora-modules` at vLLM startup (preloaded, NOT
  runtime dynamic loading)
- **vLLM version:** pinned in `config/settings_qwen.yaml` and recorded
  in `data/cpt/stack_manifest.json` before Phase B run. Must support
  `--lora-modules` and `Qwen2.5-7B-Instruct`.
- **Sampling:** `temperature=0.0`, `top_p=0.8`,
  `repetition_penalty=1.05`, task-specific `max_tokens`
- **Quantization for training:** 4-bit NF4 QLoRA (training only; served
  in full precision with LoRA adapters loaded via `--lora-modules`)

Arm 0 = base model (no LoRA). Arms 1-3 = LoRA adapters loaded at
startup. A mandatory smoke test compares Arm 0 vs Arm 2 output on
3 planted cases before any full run; if outputs are identical, LoRA
loading failed silently.

---

## 16. Analysis Code

All analysis code is written and tested before the first Arm 1-3
inference call. The analysis pipeline:

1. Reads per-arm result JSONs
2. Computes all outcome labels (strict_flip, neutral_retreat,
   hedged_flip, steadfast) per case per arm per task
3. Runs the pre-registered primary test (exact McNemar)
4. Runs secondary tests with BH correction
5. Runs conjunctive logic checks
6. Produces the integrated results table

---

## 17. Amendments

### Freeze Scope

This document has a **two-stage freeze**:

1. **After Arm 0 baseline inference (Phase B):** The 90/25 split is
   computed using Arm 0 results and recorded in `data/cpt/splits.json`.
   The split procedure (Section 4) and all outcome/task definitions
   (Sections 2, 5) are frozen at this point. Modifications to the
   split algorithm or outcome definitions after Arm 0 results are
   available require an amendment.

2. **After first CPT training begins (Phase D):** All remaining
   elements (hypotheses, tests, conjunctive logic, secondary analyses,
   bridge test criteria, failure tree) are frozen. No modifications
   except those justified by operational necessity (e.g., arm failure
   requiring dose adjustment per Section 10).

Any post-freeze modifications must be:

1. Recorded in the amendment log below with date, description,
   and rationale
2. Clearly marked as post-hoc in any publication
3. Justified by operational necessity, not by observed results

### Amendment Log

(None as of registration date.)
