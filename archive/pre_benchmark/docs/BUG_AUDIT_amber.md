# Phase A Bug Audit (amber-mirror-lattice)

**Date:** 2026-04-11
**Plan:** `~/.claude/plans/amber-mirror-lattice.md`
**Predecessor:** `deep-floating-lake` v3 stratified pipeline
**Inputs audited:** `data/results/diagnostic_2_results.json` (n=606, pipeline_version=3)
**Audit scripts:** `scripts/_audit_bug1.py`, `scripts/_audit_bug3.py`, `scripts/_audit_bug5.py`
**Machine-readable summaries:**
`data/results/_audit_bug1_summary.json`, `data/results/_audit_bug3_summary.json`

This document confirms or refutes each of the 5 bugs the multi-agent code review
flagged on the v3 pipeline. **Revision 2** (post G1 review): Bug 2 downgraded
from P0 to a reporting issue, Bug 5 rewritten to use the actual split key
(`known_outcome_available`), Bug 1 causal claim softened, and Bug 3 rate
denominators normalized to "valid orig+fo" totals.

---

## Bug 1 — `changed_spans` schema `maxLength: 200` is a real schema hazard; causal share of NP failures not yet proven

**Severity:** P0 (still — fix is cheap and the upper bound is large)
**Status:** **CONFIRMED as a hazard. CONFIRMED as a candidate root cause.
NOT independently confirmed as the dominant cause of the 121 NP failures**
(persisted JSON does not retain raw CF errors; we'd need to re-issue or
inspect the LLM cache to attribute the failures).

### Code location

`config/prompts/counterfactual_templates.yaml`, schema `counterfactual_rewrite_v1`,
shared by every CF template (semantic_reversal, neutral_paraphrase,
provenance_swap, novelty_toggle, sham_edits):

```yaml
# lines 51-66
      changed_spans:
        type: array
        minItems: 1
        items:
          type: object
          required: [from, to]
          additionalProperties: false
          properties:
            from:
              type: string
              minLength: 1
              maxLength: 200      # ← line 62
            to:
              type: string
              minLength: 1
              maxLength: 200      # ← line 66
```

The constraint applies to **both** `semantic_reversal` and `neutral_paraphrase`
because they share `output_schema_ref: counterfactual_rewrite_v1`. There is no
per-template override.

`src/pilot.py::_parse_cf_payload` (lines 149-174) validates each CF response
against this schema (call at line 167-169:
`loader._validator.validate_schema(template.output_schema, parsed)`). A
`changed_spans[*].from` or `.to` longer than 200 chars triggers a validation
error → the payload is treated as `None` → after 2 retry passes, the case is
marked `failed` and excluded from CFLS.

### Mechanism (hazard story)

Whole-sentence rewrites (which neutral_paraphrase and large semantic
reversals naturally produce) often have `from`/`to` strings well over 200
Chinese characters. The model also tends to produce *one* big `changed_spans`
entry covering the whole rewrite rather than several short edits, especially
on articles where the entire body is rephrased. Result: legitimate CF outputs
fail schema validation under the current cap.

### Quantification — what we *can* prove from persisted state

We can independently verify the **upstream-failed counts** by reading
`responses[cond_name].skipped == True` from each task block. We **cannot**
prove from this JSON alone that those failures are caused by the maxLength
cap specifically (no validation error strings persisted; the CF payload is
discarded once parsing fails). The numbers below establish the *upper bound*
for any single-cause attribution.

Failure rates after 2 retry passes (n=606), measured by reading the
`skipped` flag on each per-task condition:

| Stratum | n | sr_direction | sr_fund_impact | neutral_paraphrase |
|---|---|---|---|---|
| pre_cutoff / weakly_anchored   | 145 |  9.0% (13)  | 12.4% (18) |  **7.6%** (11) |
| pre_cutoff / strongly_anchored | 187 |  7.5% (14)  |  4.8% ( 9) | **15.0%** (28) |
| post_cutoff / weakly_anchored  | 134 |  9.0% (12)  |  8.2% (11) | **17.2%** (23) |
| post_cutoff / strongly_anchored| 140 | 10.0% (14)  | 10.0% (14) | **42.1%** (59) |
| **TOTAL**                      | 606 |  8.75% (53) |  8.58% (52)| **19.97% (121)** |

Marginal NP failure rates:

| Slice | NP fail rate |
|---|---|
| pre_cutoff   | 11.75% (39/332) |
| post_cutoff  | **29.93% (82/274)** |
| weakly_anchored   | 12.19% (34/279) |
| strongly_anchored | **26.61% (87/327)** |

**The stratum-correlated pattern is real and reproducible.** NP failure rate
is ~5.5× higher in `post_cutoff/strongly_anchored` (42.1%) than in
`pre_cutoff/weakly_anchored` (7.6%). Whatever the proximate cause, NP
failures are heaviest in exactly the strata where memorization signal is
most likely. The biased CF dropout systematically removes the cells we most
want to measure.

What we have NOT proven from persisted state: that maxLength is the
dominant proximate cause. Other plausible co-causes include (a)
target-echo mismatches on long roundup articles, (b) the model returning
malformed JSON on harder rewrites, (c) hitting `additionalProperties: false`
with extra explanatory keys. Bug 1 fix is still cheap (drop the cap), but
the **claim that fixing it will recover all 121 NP failures is not yet
supported**. Phase B verification will measure the empirical recovery rate.

---

## Bug 2 — DOWNGRADED to a reporting / readability issue

**Severity:** P2 (was P0)
**Status:** **DOWNGRADED.** The `cfls=None` cases are not silently lost —
they are explicitly visible in the output JSON. The original concern is a
documentation / table-headers issue, not a calculation error.

### Why downgraded

`scripts/run_diagnostic_2.py::aggregate_case_results` (lines 327-333) drops
entries where `metrics.cfls_direct/cfls_impact is None` before computing
the per-task mean. The output JSON already exposes these denominators in:

- `aggregated.n_completed_cases` (= 606)
- `aggregated.by_task[task_id].count` (= 447 for direct, 434 for impact)

So a reader who looks at the JSON can recompute `dropout = 606 - 447 = 159`
without writing extra code. The Phase 3 PILOT_RESULTS table happened to use
the headline `n_scored = 447 / 434` form, which is technically the
denominator for `mean CFLS`, but does not show the dropout structure
across strata. That is a reporting choice on the markdown side, not a
silent-drop bug in the pipeline.

### Phase B fix (now scope-reduced)

Instead of a P0 schema change, B2 becomes a **lightweight per-stratum
denominator surface**. Add to the `meta` block of the diagnostic_2 output:

- `n_total_cases` (= 606)
- `n_cf_failed_by_type`: `{sr_direction, sr_fund_impact, neutral_paraphrase}`
- `n_scored_by_task_x_stratum`: `{task_id × period × anchor_binary → count}`

This makes the missingness pattern visible in one place without requiring
the audit script. PILOT_RESULTS Phase 4 should also re-print the headline
table with the form `n_scored / n_total` so the reader sees the dropout
without having to dig.

---

## Bug 3 — `_detect_fo_flip` treats neutral retreat as no-flip — strongest finding

**Severity:** P0
**Status:** **CONFIRMED**, with material quantitative impact, especially on
`decomposed_impact.base`.

### Code location

`src/metrics.py::_detect_fo_flip`, lines 361-402:

```python
# lines 384-401
_POS = {"up", "positive", "strong_positive"}
_NEG = {"down", "negative", "strong_negative"}

for key in check_keys:
    orig_val = orig_slots.get(key, "")
    fo_val   = fo_slots.get(key, "")
    if orig_val == fo_val:
        continue
    if expected_direction:
        expected_polarity = "pos" if expected_direction in _POS | {"up"} else "neg"
        fo_polarity = "pos" if fo_val in _POS else ("neg" if fo_val in _NEG else "neutral")
        if (
            (expected_polarity == "pos" and fo_polarity == "neg")
            or (expected_polarity == "neg" and fo_polarity == "pos")
        ):
            return True
    else:
        return True
return False
```

When `orig_val` is non-neutral and `fo_val == "neutral"`, `fo_polarity ==
"neutral"`, neither pairwise polarity condition triggers, and the function
returns `False` (resisted). But `neutral` is **not** resisted — it is a
hedge away from the original stance under the false-outcome plant.

`src/pilot.py::score_case_from_batches` (line 628) calls `_detect_fo_flip`
directly and writes the bool to `cfls_result["false_outcome_flip"]` (line
665). This **overrides** whatever `cfls_per_case` would have computed
(which has the same bug at metrics.py:519-544 — duplicate logic). So the
v3 pipeline routes exclusively through `_detect_fo_flip`. The legacy
`run_single_case` path (pilot.py:1062-1072) does the same overwrite, so
both pipelines agree.

### Mechanism

A model that has memorized the true outcome will not jump to the planted
opposite outcome, but it will *waver* — outputs become more cautious,
often landing on `neutral`. Counting hedges as "no flip = no leakage"
systematically undercounts memorization, in a direction that biases the
study toward the null.

### Quantification (rescore from cached `parsed_output`)

`scripts/_audit_bug3.py` re-classifies every (case × task) pair from the
cached `responses[].parsed_output` using a 4-class enum:

- `strict_flip`: ORIG and FO have opposite polarity (current `_detect_fo_flip` True)
- `hedged_flip`: ORIG non-neutral, FO neutral (currently scored False)
- `no_flip`: ORIG and FO equal, or other patterns
- `undefined`: response missing/invalid

**Cross-check:** the strict-mode classification matches the cached
`metrics.fo_flip_*` field on **599/599** cases for direct and **589/589**
for impact (zero mismatches). The reclassifier reproduces current scoring
exactly, so the comparison below is apples-to-apples.

#### `direct_prediction.base` (n_valid = 599 with valid orig+fo)

| Stratum | n_valid | strict | hedged | union |
|---|---|---|---|---|
| pre_cutoff / weakly_anchored    | 144 |  4 | 19 | 23 |
| pre_cutoff / strongly_anchored  | 183 |  6 | 18 | 24 |
| post_cutoff / weakly_anchored   | 133 |  9 | 21 | 30 |
| post_cutoff / strongly_anchored | 139 |  7 | 21 | 28 |
| **TOTAL** | 599 | **26** | **79** | **105** |

Direction by period (using **valid orig+fo** denominators throughout —
matches Phase 3 PILOT_RESULTS' `10/327` and `16/272` cells):

| Variant | pre flip rate | post flip rate | direction |
|---|---|---|---|
| strict (current)         | 10/327 = 3.06% | 16/272 = 5.88% | post > pre |
| hedged-only              | 37/327 = 11.3% | 42/272 = 15.4% | post > pre |
| union (strict ∪ hedged)  | 47/327 = 14.4% | 58/272 = 21.3% | post > pre |

For `direct_prediction.base` the **post>pre direction survives** the Bug 3
fix. The magnitude shrinks (the OR is closer to 1 under union scoring) but
the qualitative conclusion does not invert.

#### `decomposed_impact.base` (n_valid = 589 with valid orig+fo)

| Stratum | n_valid | strict | hedged | union |
|---|---|---|---|---|
| pre_cutoff / weakly_anchored    | 144 | 0 | 24 | 24 |
| pre_cutoff / strongly_anchored  | 182 | 0 | 16 | 16 |
| post_cutoff / weakly_anchored   | 126 | 2 |  7 |  9 |
| post_cutoff / strongly_anchored | 137 | 1 |  8 |  9 |
| **TOTAL** | 589 | **3** | **55** | **58** |

Direction by period (valid orig+fo denominators — matches Phase 3's
`0/326` and `3/263`):

| Variant | pre flip rate | post flip rate | direction |
|---|---|---|---|
| strict (current)         | 0/326 = 0.00% |  3/263 = 1.14% | post > pre (degenerate) |
| hedged-only              | 40/326 = 12.3%| 15/263 = 5.70% | **pre > post** |
| union (strict ∪ hedged)  | 40/326 = 12.3%| 18/263 = 6.84% | **pre > post** |

For `decomposed_impact.base` the Bug 3 fix **inverts the direction**:
under strict (current), pre=0 vs post=3 is degenerate / slightly post>pre.
Under hedged, pre=40 vs post=15 (≈ 2.2× ratio) is **pre>post — the
memorization-direction signal that the v3 baseline missed**.

This is the headline finding of Phase A.

The hedged-retreat counts also closely match the multi-agent review's
estimate (review: ~88 direct, ~57 impact; audit: 79 direct, 55 impact).

---

## Bug 4 — LLM-negated FO has no polarity check

**Severity:** P1
**Status:** **CONFIRMED**

### Code location

`src/masking.py::generate_false_outcome_cpt`, lines 588-603 (legacy
single-call path) and `src/pilot.py::prepare_fo_cpt_batch`, lines 336-365
(batched path).

```python
# masking.py 594-603
for attempt in range(max_attempts):
    try:
        resp = client.chat(system, user, bypass_cache=attempt > 0)
        text = resp.raw_response.strip()
        # Sanity: not empty, not identical to original, reasonable length
        if text and text != _known and len(text) < len(_known) * 3:
            hint = f"（注：据了解，{text}。）"
            return f"{article}\n{hint}", "llm_negated"
    except Exception:
        continue
```

```python
# pilot.py 336-343 (batched validator)
def _validate_negation(spec: dict[str, Any]):
    known = spec["known"]
    def _v(resp: Any) -> bool:
        if isinstance(resp, BaseException):
            return False
        text = resp.raw_response.strip()
        return bool(text) and text != known and len(text) < len(known) * 3
    return _v
```

### Mechanism

Both code paths accept any non-empty, non-identical, length-bounded LLM
response as a valid "negation". There is no check that the negated text
actually expresses the opposite polarity from `known_outcome`. If the LLM
produces a same-polarity rewrite, an off-topic rewrite, or a vague response,
the resulting CPT plant is not a real false outcome — it is a noise
injection that biases the flip rate downward.

### Quantification

Cannot be quantified directly without re-evaluating the cached LLM negations
against their original `known_outcome`. The audit confirms the absence of any
polarity check in either code path; an upper-bound on the impact would
require a one-pass LLM judge over the cached negation strings, which is
out-of-scope for Phase A. Bug 4 is included in Phase B as a structural
risk mitigation, not because we have a quantified impact.

---

## Bug 5 — Probe modality is split by `known_outcome_available`, not period; pre arm is mixed

**Severity:** P1
**Status:** **CONFIRMED, but the original framing was wrong.** The split is
not pre vs post; it is `known_outcome_available` (true vs false). This means
the **pre-cutoff arm itself is mixed** — only 35% of pre cases run the LLM
negation; the other 65% run the generic template path along with all post
cases.

### Code location

`src/pilot.py::prepare_fo_cpt_batch`, lines 305-323:

```python
known = (tc.known_outcome or "").strip()
is_generic = not known or known == "unknown_post_cutoff"
...
if is_generic:
    # generic_post_cutoff path: directional template, no API call
else:
    # llm_negated path: LLM call to negate the real known_outcome
```

`scripts/run_diagnostic_2.py::_normalize_known_outcome` (around lines
144-151) maps any case without a real `known_outcome` to `known_outcome=""`,
which then routes to the generic path regardless of period.

### Mechanism

The `is_generic` switch produces two distinct probe modalities:

- **`llm_negated`** — context-aware LLM negation of the *real* outcome,
  appended as `（注：据了解，{LLM_text}。）`. Length, specificity, and lexical
  overlap with the article scale with the original outcome.
- **`generic_post_cutoff`** — template phrase formatted with `{target}` only,
  appended as `（注：据了解，{generic_phrase}。）`. Same length and shape across
  every case; only the target name varies.

These shapes differ in length, specificity, plausibility, and lexical
anchoring to the article. Any cross-arm comparison is confounded by probe
shape.

### Quantification

`scripts/_audit_bug5.py` cross-tabs `(period, known_outcome_available)`:

| period | known_outcome_available | n |
|---|---|---|
| pre_cutoff   | True  | **115** (LLM-negated path) |
| pre_cutoff   | False | **217** (generic path)     |
| post_cutoff  | False | **274** (generic path)     |

By anchor binary:

| period | known_outcome_avail | anchor | n |
|---|---|---|---|
| pre   | True  | strongly | 73 |
| pre   | True  | weakly   | 42 |
| pre   | False | strongly | 114 |
| pre   | False | weakly   | 103 |
| post  | False | strongly | 140 |
| post  | False | weakly   | 134 |

Implications:

1. **The pre arm is mixed.** 115 LLM-negated cases dilute with 217 generic
   cases inside the same `period=pre_cutoff` bucket. Any pre-arm aggregate
   is a weighted blend of two probe modalities. The headline pre/post MH OR
   for `fo_flip_direct` and `fo_flip_impact` is therefore an apples-to-mixed
   comparison, not an apples-to-apples one.
2. **The post arm is uniform** (100% generic).
3. **The cleanest comparison** is *within probe modality*: compare
   `pre_cutoff & known_outcome_available=True` (115 LLM-negated) against
   `post_cutoff` (274 generic) only as a noisy sanity check, and treat the
   217 pre-cutoff generic cases as a *third* arm — they share probe modality
   with post but share period with pre, giving a way to disentangle the
   confound.

### Phase B fix scope

The minimal symmetry fix B5a is no longer enough to fully address this — it
needs to be reframed. Options:

- **B5a (minimal)**: tighten the post-cutoff generic template so it produces
  a probe with similar length / specificity to the LLM-negated pre probe
  (use target + a few key entities). This shrinks the modality gap but
  doesn't make pre uniform.
- **B5a' (recommended)**: in addition to B5a, persist `cpt_mode` per case in
  the result JSON (it already exists in `conditions["false_outcome_cpt"]
  ["cpt_mode"]` but is **not** propagated into the case-level result), and
  add a `cpt_mode` stratification arm to `quick_stats.py` so the pre/post
  comparison is reported alongside the probe-modality comparison. This is a
  pure analysis-side fix and is cheap.
- **B5b (principled)**: 2×2 cross design where every case runs both probe
  modalities. Doubles CPT API cost. Decided in the plan to defer to Phase F.

---

## Audit summary table

| Bug | Severity | Status | Quantified impact | Phase B fix |
|---|---|---|---|---|
| 1. `changed_spans` maxLength=200 | P0 | CONFIRMED hazard; causal share unproven from persisted JSON | NP failure 42% in post/strong vs 8% in pre/weak; 121/606 NP fails total — upper bound for any single-cause attribution | B1 (drop maxLength); empirical recovery rate measured at smoke test |
| 2. silent `cfls=None` drop | ~~P0~~ **P2** | **DOWNGRADED** | Reporting issue: denominators already in `aggregated.n_completed_cases` and `by_task[*].count`; 159 dropped from direct denominator | B2 reduced to per-stratum denominator surface in meta |
| 3. `_detect_fo_flip` neutral retreat | P0 | CONFIRMED | direct: 26→105 union (post>pre survives); **impact: 3→58 union (direction inverts to pre>post — memorization signal)** | B3 (strict/hedged enum) |
| 4. no polarity check on LLM negation | P1 | CONFIRMED (no quant) | unknown, requires LLM judge | B4 (polarity validator) |
| 5. probe modality is by `known_outcome_available`, not period | P1 | CONFIRMED, original framing wrong | pre arm is **mixed**: 115 LLM, 217 generic; post arm uniform 274 generic | B5a' (persist cpt_mode + cpt_mode arm in analysis) |

---

## Headline implication

The strongest single-line summary: **the `decomposed_impact` conclusion in
Phase 3 is unsafe**. With the strict definition, `decomposed_impact.fo_flip`
is essentially zero in pre and slightly positive in post (3 events). Once
hedged retreats are counted, the same data show pre=40, post=15 — i.e.,
**pre-cutoff cases hedge under the false-outcome plant about 2.2× more
often than post-cutoff cases**, which is the memorization-direction signal
the study was designed to detect.

The `direct_prediction` conclusion (post > pre, suggestibility) survives
the strict→hedged change directionally, but the magnitude shrinks under
the union definition.

Both conclusions are also subject to the Bug 5 confound: the pre arm is a
mixed-modality bucket, so any pre/post inference is partially apples-to-mixed.

Therefore Phase B is justified, and Phase C (cheap rescore) is the
highest-EV next step before re-running the full pipeline in Phase D.

---

## Refutations / things the audit did NOT find

- **No additional P0/P1 bugs in `score_case_from_batches`**: the cf_invariance
  / per_slot logic in `cfls_per_case` still has a duplicate copy of the
  Bug 3 logic at metrics.py:519-544, but in v3 it is *overwritten* on line
  665 of `pilot.py`. The legacy `run_single_case` path (pilot.py:1062-1072)
  does the same overwrite, so legacy and batched agree. The duplicate
  metric.py block is dead code; it should be cleaned up in Phase B for
  consistency, but does not currently cause a divergence.
- **No issue found with `_extract_slots`**: it correctly handles the base
  `direction` / `fund_impact` / `shock_impact` slot names used by the v3
  pilot. Matched-format slot iteration is used by other experiments and is
  not exercised on the diagnostic_2 path.
- **`LLMClient.batch_chat_concurrent` failure_isolated path is correct**:
  retries call with `bypass_cache=True`, which prevents fetching the prior
  failed response from cache. The cache key is reused (same prompt hash),
  and on success the new response overwrites the old entry — this is the
  intended behavior.
- **`aggregate_case_results` / `build_output_payload` denominators are not
  hidden**: `aggregated.n_completed_cases` and per-task `count` already
  expose the dropout in the JSON. The remaining concern is reporting
  ergonomics, captured by the Bug 2 downgrade above.
- **The cache key situation for Bug 1 fix**: `_parse_cf_payload` validates
  the response *after* fetching from cache. The cache key is built from the
  prompt strings (system+user). Since the Phase B1 fix changes only the
  schema (not the prompt), Phase D should be able to reuse cached LLM
  responses for content while re-validating against the relaxed schema —
  meaning Phase D should hit cache for ~80%+ of CF prompts. This is checked
  in Phase B1's verification step.
