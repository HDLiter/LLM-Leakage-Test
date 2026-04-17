# Plan: Fix v3 Pipeline Silent Bugs + Re-run D1 (amber-mirror-lattice)

**Project:** D:\GitRepos\LLM-Leakage-Test
**Created:** 2026-04-11
**Predecessor plan:** deep-floating-lake (v3 stratified pipeline)
**Conda env:** rag_finance (Python 3.12)

## Context (read this first)

The deep-floating-lake plan finished and produced a **null result** for LLM
memorization on DeepSeek-chat: pooled Mantel-Haenszel OR for `fo_flip_direct`
stratified by `anchor_binary` was 0.51 (p=0.095, Breslow-Day p=0.56). The
direction was *opposite* of memorization (post>pre), interpreted as
suggestibility rather than memorization. Full numbers and updated Q1/Q2/Q3
answers live in `docs/PILOT_RESULTS.md`'s "Phase 3 (deep-floating-lake)" section.

A multi-agent code review (3 parallel Codex MCP xhigh sessions) found that
this null is **probably an artifact of 3 P0 bugs and 2 P1 bugs in the v3
pipeline**, plus a separate construct-validity issue with our metric vs the
verbatim-extraction literature. A power analysis (third agent) confirmed:

- N=599 / baseline 5% / α=0.05 / 80% MDE for the existing MH design ≈ OR=2.4
- Bayesian posterior given the observed OR=0.51: P(OR>1)≈5%, P(OR>1.5)≈0.4%
- So "moderate memorization buried by sample size" is essentially ruled out
- BUT: this conclusion is only meaningful **after** the silent bugs are fixed

This plan fixes the bugs, re-runs D1, updates the results doc, and adds an
optional matched-positive-control experiment (Phase F) so we can defend the
null if it survives the bug fixes.

### Why each bug invalidates the null

| Bug | Severity | Mechanism that nulls memorization |
|---|---|---|
| 1. `changed_spans` schema maxLength=200 kills whole-sentence CF rewrites | P0 | Failure rate is **higher in `strongly_anchored` and `post_cutoff`** → systematically removes the strata where memorization is most likely |
| 2. Aggregation silently drops cfls=None entries | P0 | Headline mean/positive_rate represents the post-Bug-1 subsample, not the queue |
| 3. `_detect_fo_flip` treats neutral retreat as no-flip | P0 | Memorized models hedge to neutral under a contradictory FO plant. Re-coding neutral as flip changes `fo_flip_direct` from 26/599 → ~88/599, `fo_flip_impact` from 3/589 → ~57/589 — the headline result may invert |
| 4. LLM-negated FO has no polarity check | P1 | Same-polarity / vague rewrites get accepted, weakening the CPT plant and downward-biasing flip rate |
| 5. pre uses LLM-rewritten outcome, post uses target-only generic | P1 | Probe modality is asymmetric across periods → period comparison is structurally biased |

Plus a separate finding from Agent 1 (construct validity): even with all bugs
fixed, our metric does not measure the same construct as Carlini/Nasr's
verbatim extraction or Sainz's benchmark contamination. So the strongest
defense of any final null is a **matched positive control** (Phase F): take a
known-leaked model and show our pipeline lights up on it.

---

## Codex review gates (MANDATORY)

This plan has **4 mandatory Codex MCP review gates** that interrupt the
linear phase flow. The most important one is **G2 — full code-diff review
before Phase D** — since Phase D is a 50-minute API-burning experiment, you
do NOT want to discover a bad bug fix afterward.

Each gate is dispatched via the `Agent` tool (general-purpose subagent_type)
which internally calls `mcp__codex__codex`. Two reasons to use a sub-agent
rather than calling Codex MCP directly from the main session:

1. **Parallelism** — multiple gates can run concurrently when independent.
2. **Context isolation** — the sub-agent absorbs Codex's verbose output and
   returns a 1-paragraph summary to the main session, so the planning
   loop's context budget is preserved.

The sub-agent's only job is orchestration. It must not analyze on its own.
Codex GPT-5.4 (`model_reasoning_effort=xhigh`, `sandbox=danger-full-access`,
`cwd=D:\GitRepos\LLM-Leakage-Test`) does all the actual review work.

| Gate | When | Blocks | Purpose |
|---|---|---|---|
| **G1** | After Phase A | Phase B | Sanity-check the bug audit findings before spending time on fixes |
| **G2** | After Phase B | Phase C+D | Hostile code-diff review of all bug fixes — prevents bad fixes from corrupting Phase D |
| **G3** | After Phase D | Phase E | Numerical sanity check on the re-run results |
| **G4** | Inside Phase E | git commit | Writing/overclaiming review of the PILOT_RESULTS rewrite |

For each gate, save the Codex report to `docs/REVIEW_amber_G<N>.md`. Each
report must end with one of three explicit verdicts:

- **PASS** — proceed to the next phase
- **ITERATE** — fix the listed issues and re-review
- **ABORT** — the plan's premise is wrong; stop and rethink

The full sub-agent prompt template for each gate is at the bottom of this
file (section "Codex review prompt templates"). Copy-paste the template,
fill in the gate-specific blanks, dispatch via `Agent`.

---

## Phases

### Phase 0 — Boot context (do this first, ~10 min)

Read these files in order so you have the same picture as the multi-agent
review did:

1. `docs/PILOT_RESULTS.md` — entire "Phase 3 (deep-floating-lake): v3
   Stratified Re-run" section, bottom of file
2. `docs/RESEARCH_PROPOSAL.md` — top of file, the three core hypotheses
3. `docs/ANCHOR_RUBRIC.md` — anchor_level definitions
4. `docs/FIRTH_DECISION.md` — why we use L1 instead of true Firth
5. `data/seed/strata_config.json` — read `analysis_anchor_field`; should be
   `"anchor_binary"`
6. `data/results/diagnostic_2_results.json` meta block only — confirm
   `pipeline_version=3`, `n_cases_completed=606`, `n_case_errors=0`
7. `src/pilot.py` lines 84-220 (CF generation legacy path) and lines 350-650
   (the new batched runners + score_case_from_batches)
8. `src/masking.py` lines 540-650 (`generate_false_outcome_cpt` + LLM negation
   prompts)
9. `src/metrics.py` whole file — `_detect_fo_flip` is the key function
10. `config/prompts/counterfactual_templates.yaml` — find the
    `semantic_reversal` and `neutral_paraphrase` templates and look at
    `output_schema.changed_spans`

Create a TaskList with the phases below before starting Phase A.

---

### Phase A — Quantify each bug before fixing (no code changes)

Goal: confirm the bugs exist and measure their impact, so the fix-and-rerun
loop has a falsifiable success criterion.

**A1. Confirm Bug 1 (schema maxLength).**
- Open `config/prompts/counterfactual_templates.yaml`
- Find the `semantic_reversal` template's `output_schema.properties.changed_spans.items.properties.from` and `.to` definitions
- Confirm there is a `maxLength` constraint (the review reported `<=200`)
- Do the same for `neutral_paraphrase`
- Record the exact maxLength values + line numbers

**A2. Quantify Bug 1 by stratum.**
- Write a one-off script `scripts/_audit_bug1.py` that:
  - Loads `data/results/diagnostic_2_results.json`
  - For each case, look at `condition_summary.sr_direction.failed`,
    `condition_summary.sr_fund_impact.failed`,
    `condition_summary.neutral_paraphrase.failed`
  - Cross-tab failure counts by `period × anchor_binary`
- Confirm the multi-agent claim: NP failure rate is materially higher in
  `strongly_anchored` and `post_cutoff` strata
- Record the failure rate per stratum

**A3. Confirm Bug 3 (`_detect_fo_flip` neutral handling).**
- Open `src/metrics.py`, locate `_detect_fo_flip`
- Verify the function signature returns `bool | None`, and trace what happens
  when `cf_false_outcome` parsed_output's direction/impact label is `"neutral"`
- Also check the symmetric case: when ORIG is non-neutral and CF is neutral
- Record the exact branches and any test cases that exercise neutral

**A4. Quantify Bug 3 impact (rescore-only, no API calls).**
- Write `scripts/_audit_bug3.py` that:
  - Loads `data/results/diagnostic_2_results.json`
  - For each case, reads `tasks.direct_prediction.base.responses.original.parsed_output` and
    `tasks.direct_prediction.base.responses.false_outcome_cpt.parsed_output`
  - For each task in PILOT_TASKS, count how many cases the FO response is
    `"neutral"` while ORIG is non-neutral (these are the "hedged retreats")
  - Same for `decomposed_impact.base`
  - Print: current `fo_flip_direct/impact` count, count of hedged retreats,
    hypothetical "strict OR hedged" count
- This is the "free preview" of the Bug 3 fix's effect — if hedged count is
  large, the headline result may invert as soon as we re-score

**A5. Confirm Bug 4 (no polarity check on LLM negation).**
- In `src/masking.py::generate_false_outcome_cpt`, locate the LLM-negation
  branch (the `if not is_generic` path)
- Verify the only sanity checks are `text != known_outcome` and
  `len(text) < len(known_outcome) * 3`
- There is no check that the negated text is actually polarity-flipped vs
  the original

**A6. Confirm Bug 5 (pre/post asymmetry).**
- In `src/pilot.py::prepare_fo_cpt_batch`, trace the two branches:
  - `is_generic` (post-cutoff): builds `phrase = template.format(target=target)`,
    appends `（注：据了解，{phrase}。）`
  - non-`is_generic` (pre-cutoff): calls Codex LLM negation, appends
    `（注：据了解，{text}。）` where `text` is the LLM-rewritten real outcome
- Confirm the two paths produce structurally different probes (length,
  specificity, presence of known_outcome details, presence of entity names)

**Output of Phase A:** a short audit report `docs/BUG_AUDIT_amber.md` with:
- exact line numbers for each bug
- Bug 1 stratum failure table
- Bug 3 hedged-retreat counts and hypothetical inverted numbers
- Confirmation/refutation of each P0/P1 finding

If A2 or A4 reveal that the bugs are smaller than the review claimed (e.g.,
hedged-retreat count is <10), revise the priority order in Phase B
accordingly. **Do not skip the audit.** It is the only way to know whether
the bug fix is going to change the conclusion.

### >> Gate G1 — Audit sanity check (BLOCKS Phase B)

Dispatch the G1 sub-agent (template at the bottom of this file). The
sub-agent will call Codex MCP once to review `docs/BUG_AUDIT_amber.md` and
write a verdict to `docs/REVIEW_amber_G1.md`.

What G1 specifically checks:
- Are the audited line numbers correct (re-grep the codebase)?
- For each bug Phase A confirmed: does the mechanism story actually fit the
  code?
- For each bug Phase A refuted: is the refutation right, or did Phase A miss
  a code path?
- Are there other P0/P1 bugs the original review missed (look at:
  `score_case_from_batches`, the cf_invariance computation in `metrics.py`,
  the `cfls_per_case` slot-iteration logic)?
- Output a PASS/ITERATE/ABORT verdict.

**Gate decision:**
- PASS → continue to Phase B
- ITERATE → re-do the parts of Phase A that Codex flagged, then re-dispatch G1
- ABORT → the bugs aren't real and the null is genuine; stop, write a "no
  fixes needed" entry in PILOT_RESULTS, and skip to Phase F (positive control)

---

### Phase B — Bug fixes

Each bug gets its own commit so we can bisect later if results move oddly.

**B1. Fix Bug 1 — relax `changed_spans` schema.**
- File: `config/prompts/counterfactual_templates.yaml`
- For both `semantic_reversal` and `neutral_paraphrase`:
  - Option A (preferred): drop `maxLength` from `changed_spans[].from/to`
  - Option B (safer if removing breaks other validators): bump to 4000
- The `changed_spans` field is documentation/audit only — CFLS is computed
  from `rewritten_article`, not from `changed_spans`. Removing it entirely
  is also acceptable; check that nothing in `src/metrics.py` or
  `src/masking.py` reads it (grep for `changed_spans`).
- Verification (no API): re-run schema validation on a stored CF cache file:
  ```python
  import json
  from src.prompt_loader import PromptLoader
  loader = PromptLoader(prompts_dir="config/prompts")
  template = loader.get_counterfactual_template("semantic_reversal")
  # Pick a previously failing case from data/cache/<hash>.json that has
  # rewritten_article > 200 chars; assert validate_schema returns no errors
  ```

**B2. Add diagnostic logging — Bug 2.**
- File: `scripts/run_diagnostic_2.py`
- In `aggregate_case_results` and `build_output_payload`, add to the meta
  block:
  - `n_total_cases` (before any filtering)
  - `n_cf_generation_failed` (cases where any of sr_direction/sr_fund_impact/
    neutral_paraphrase has `failed=True`)
  - `n_cfls_scored_direct`, `n_cfls_scored_impact`
  - `cf_failure_by_stratum`: dict keyed by `f"{period}/{anchor_binary}"`
- Don't change the existing mean/positive_rate (still useful), but make the
  missingness denominator visible. Update PILOT_RESULTS' table headers later
  to include `n_scored / n_total`.

**B3. Fix Bug 3 — neutral retreat as a separate flip category.**
- File: `src/metrics.py`
- Change `_detect_fo_flip` signature from `bool | None` to `str | None`,
  returning one of:
  - `"strict_flip"` — CF output crossed to opposite polarity
  - `"hedged_flip"` — CF output retreated to neutral while ORIG was non-neutral
  - `"no_flip"` — CF output matches ORIG polarity (resists the false outcome)
  - `None` — undefined (e.g., ORIG was neutral or any required field missing)
- Update `cfls_per_case` if it consumes `_detect_fo_flip` directly
- File: `src/pilot.py`
- In `score_case_from_batches`, store the new value as
  `cfls_result["false_outcome_flip"]` (now a string instead of bool); also
  store `cfls_result["false_outcome_flip_strict"]` (bool, True only for
  strict_flip) and `cfls_result["false_outcome_flip_hedged"]` (bool, True
  for hedged_flip OR strict_flip)
- File: `src/pilot.py::run_single_case` (legacy path)
- Mirror the same change so legacy mode produces the same fields
- Update `metrics.cfls_direct/impact` block (whichever script writes the
  per-case `metrics` dict) to expose:
  - `fo_flip_direct_strict` (bool — old behavior)
  - `fo_flip_direct_hedged` (bool — strict ∪ hedged)
  - `fo_flip_direct_label` (string)
  - same for `_impact`
- File: `scripts/quick_stats.py`
- Update the MH stratification block to compute MH twice: once for
  `fo_flip_direct_strict`, once for `fo_flip_direct_hedged`. Print both
  side by side
- File: `scripts/sensitivity_analysis.py`
- Same: compute primary MH for both strict and hedged, in the
  `metrics["fo_flip_*_strict"]` and `metrics["fo_flip_*_hedged"]` blocks
- Add a one-off "rescore" mode to one of the analysis scripts (or write
  `scripts/rescore_fo_flip.py`) that:
  - Loads existing `data/results/diagnostic_2_results.json`
  - Recomputes `fo_flip_direct/impact` for each case from the cached
    `parsed_output` dicts using the new `_detect_fo_flip` semantics
  - Writes a side-by-side comparison without touching the original file
- This is the **most informative cheap experiment** — no API calls, gives a
  preview of whether the headline result changes

**B4. Fix Bug 4 — polarity check on LLM negation.**
- File: `src/masking.py::generate_false_outcome_cpt`
- After the LLM call in the pre-cutoff branch, before accepting the text:
  - Compare the negated text against the original `known_outcome` for
    polarity-flip evidence. Cheap version: check if any of the
    `_NEGATE_SWAP_MAP`-style direction tokens appear with opposite valence
    vs the original (e.g., original has "上涨" and negated has "下跌", or
    vice versa). For more rigor, run a second LLM call as a polarity judge
    (one round-trip).
  - If polarity check fails, retry with `bypass_cache=True` (already supported
    in the retry loop)
  - If all `max_attempts` fail polarity check, return `(None, "llm_failed")`
    just like the existing failure path
- Update the mode-purification footnote in PILOT_RESULTS later if the
  `n_llm_failed` rises materially

**B5. Fix Bug 5 — pre/post probe symmetry.** (BIGGEST SCOPE)
This is structural, not just a bug fix. Two options:

  - **Option B5a (minimal)**: build a "specific generic" template for
    post-cutoff cases that uses target + key_entities to produce a probe
    with similar length/specificity to the LLM-rewritten pre probe. Easier,
    less powerful.

  - **Option B5b (recommended)**: implement the **2×2 cross design** Agent 3
    suggested. Treat `period` and `probe_type` as separate factors:
    - `probe_type = "llm_negated"` runs LLM negation for *both* pre and post
    - `probe_type = "generic_template"` runs the generic template for *both*
      pre and post
    - Each case gets two CPT articles, two task runs, two `fo_flip` values
    - Analysis: (period × probe_type) × anchor_binary, with a 3-way
      interaction term that decomposes memorization (period main effect)
      from suggestibility (probe_type main effect)
    - This doubles CPT API cost but solves the construct confound

Recommendation: **start with B5a** (minimal symmetry fix) and document B5b
as an optional Phase E experiment. If the post-Phase-B null still wants
defense, do B5b.

Phase B verification gate: re-run smoke test
```bash
conda run -n rag_finance python scripts/run_diagnostic_2.py --n-cases 10 --chunk-size 10
```
- CF failure rate should drop from ~17.6% to <5%
- `n_total_cases` and `n_cf_generation_failed` should appear in meta
- `fo_flip_*_strict` and `fo_flip_*_hedged` fields should appear in
  per-case metrics
- pipeline_version still 3 (no schema break)

### >> Gate G2 — Hostile code-diff review (BLOCKS Phase C and Phase D)

**This is the most important gate in the plan.** Phase D burns ~50 minutes
of API calls; you do not want to discover a bad fix afterward. G2 dispatches
TWO Codex sub-agents in parallel for cross-validation:

1. **G2a — line-by-line diff review.** Dispatch the G2a sub-agent (template
   below). It calls Codex MCP and asks for a hostile review of every commit
   from Phase B (`git log --oneline ORIG_HEAD..HEAD` since the start of
   Phase B). Codex must explicitly check:
   - Does each fix do what its commit message claims?
   - Do the fixes break the legacy `run_pilot` / `run_single_case` path?
   - Does the new `_detect_fo_flip` enum interact correctly with downstream
     consumers (`cfls_per_case`, `score_case_from_batches`,
     `aggregate_case_results`, `quick_stats.py`, `sensitivity_analysis.py`)?
   - Does the polarity-check helper in B4 reuse stale `_NEGATE_SWAP_MAP`
     state? Is the helper a *check* (allowed) or a *fallback probe* (not
     allowed by mode purification)?
   - Does the schema relax in B1 invalidate any existing cache entry? Will
     Phase D re-spend API budget unnecessarily?
   - Does the smoke-test verification gate actually exercise the new code
     paths? (Edge cases: a case with no `key_entities`, a case with
     `expected_direction="neutral"`, a case where ORIG output is malformed.)

2. **G2b — independent re-derivation.** Dispatch the G2b sub-agent in
   parallel. Same prompt template but with a *different* framing: "given the
   description of the 5 bugs in `~/.claude/plans/amber-mirror-lattice.md`,
   independently derive the minimum correct fix for each one without looking
   at the implementation, then compare against the actual implementation."
   The point is to catch fixes that look correct in isolation but solve a
   different problem than the audit identified.

Both reports go to `docs/REVIEW_amber_G2a.md` and `docs/REVIEW_amber_G2b.md`.
Reconcile any disagreement between G2a and G2b before proceeding.

**Gate decision:**
- BOTH reports PASS → proceed to Phase C
- Either report ITERATE → fix the listed issues, **also fix the smoke test
  to cover the missing edge case if applicable**, re-run smoke test, then
  re-dispatch G2 (both halves)
- Either report ABORT → stop and rethink the fix architecture; do not run
  Phase D

---

### Phase C — Cheap rescore (no API calls, ~5 min)

**C1.** Backup current results:
```bash
cp data/results/diagnostic_2_results.json data/results/diagnostic_2_results.v3_pre_amber.json
```

**C2.** Run the rescore script written in B3:
```bash
conda run -n rag_finance python scripts/rescore_fo_flip.py
```

**C3.** Compare:
- old `fo_flip_direct` count vs new strict / hedged count
- old `fo_flip_impact` count vs new strict / hedged count
- per-stratum (period × anchor_binary) counts for each metric × variant

**C4.** Re-run the analysis on the rescored data:
```bash
conda run -n rag_finance python scripts/quick_stats.py
conda run -n rag_finance python scripts/sensitivity_analysis.py
```
Note: these scripts will need to read the rescored fields. Make sure B3
already taught them the `_strict` / `_hedged` suffix convention.

**Decision point after C4:**
- If hedged-version pooled MH OR for `fo_flip_direct` **crosses 1.0** (i.e.,
  pre > post): the null result is dead. Memorization signal *was* there,
  hidden by Bug 3. Skip directly to Phase E and rewrite Q2.
- If hedged-version OR is still <1: the conclusion may survive Bug 3 alone.
  Continue to Phase D (re-run with all fixes for the cleanest possible
  estimate).

---

### Phase D — Re-run D1 with all fixes (~50 min wall time)

**D1.** Delete the v3 results file (schema is unchanged but field names
broaden):
```bash
mv data/results/diagnostic_2_results.json data/results/diagnostic_2_results.v3_post_C.json
```

**D2.** Run the full pipeline:
```bash
conda run -n rag_finance python -u scripts/run_diagnostic_2.py --chunk-size 50
```
Expected: 13 chunks × ~225s = ~50 min wall time (Bug 1 fix may speed Phase 1
slightly because fewer retries). Watch for:
- `n_llm_failed` per chunk (Bug 4 may push this above 0)
- CF failure rate per chunk (Bug 1 fix should bring this from 17-30% to <5%)
- `fo_flip_*_strict / _hedged` populated per case

**D3.** Verify completion:
- 0 errors
- `n_llm_failed_pre < 5%` of pre-cutoff cases
- pipeline_version=3
- per-case `metrics` dict has both strict and hedged variants

### >> Gate G3 — D1 numerical sanity check (BLOCKS Phase E)

Dispatch the G3 sub-agent (template below). It calls Codex MCP to review the
new D1 results before they get written into PILOT_RESULTS. Codex specifically
checks:

- **Schema integrity**: every case has the new `_strict / _hedged` fields,
  no silent None where there should be a value
- **Per-stratum consistency**: do the stratum totals add up to the meta
  `n_cases_completed`? Do `n_total - n_scored - n_cf_failed` reconcile?
- **Per-chunk continuity**: walk through `chunk_*` lines in the runtime log;
  any chunk with anomalously high failure rate or anomalously low rate?
- **Diff vs the v3 baseline** (`data/results/diagnostic_2_results.v3_pre_amber.json`):
  - Did the headline mean CFLS move? By how much?
  - Did `fo_flip_*_strict` count match the v3 result (should be similar — same
    underlying scoring)? If they materially differ, why?
  - Did `fo_flip_*_hedged` count diverge from `_strict`? By how much?
- **Cell stability**: any cell that was non-empty in v3 but is empty now (or
  vice versa) is suspicious — explain it
- **Cache hit rate**: if Phase D ran much faster or slower than v3 (~50 min),
  flag it — likely Bug 1 cache invalidation interaction

Save report to `docs/REVIEW_amber_G3.md`.

**Gate decision:**
- PASS → proceed to Phase E
- ITERATE → if a sanity issue is found, decide whether to re-run a single
  chunk via `--resume`, or re-run from scratch
- ABORT → if the new numbers contradict each other, do not write
  PILOT_RESULTS; debug instead

---

### Phase E — Re-analyze + update PILOT_RESULTS

**E1.** Run analyses:
```bash
conda run -n rag_finance python scripts/quick_stats.py > data/results/quick_stats_amber.txt
conda run -n rag_finance python scripts/sensitivity_analysis.py
```

**E2.** Update `docs/PILOT_RESULTS.md`:
- Add a new section: "Phase 4 (amber-mirror-lattice): post-bug-fix re-run"
  below the existing "Phase 3 (deep-floating-lake)" section
- Tables to include:
  - Bug-fix audit summary (from Phase A) — what bugs were real, what their
    measured impact was
  - CF failure rate before/after Bug 1 fix, by stratum
  - Hedged-retreat counts (Bug 3 quantification)
  - Mantel-Haenszel pooled OR for both `fo_flip_direct_strict` and
    `fo_flip_direct_hedged`, stratified by anchor_binary
  - Same for `_impact`
  - Sensitivity slices: `frequency_class=high/low` (skipping `low` is fine —
    documented as a confound in Phase 3)
- Update Q1/Q2/Q3:
  - Q1 (CFLS true negative?) likely unchanged
  - Q2 (CPT memorization vs suggestibility?) likely **needs rewrite** if
    hedged version flips the OR
  - Q3 (bidirectional confound?) reread Breslow-Day p with new numbers

### >> Gate G4 — Writing review (BLOCKS git commit)

Dispatch the G4 sub-agent (template below). Codex acts as a hostile peer
reviewer of just the new "Phase 4" section. Specifically checks:

- **Number consistency**: every number in prose matches a number in a table;
  every number in a table is reproducible from the JSON results files
- **Overclaiming**: any "we show that..." sentence that goes beyond what the
  MH OR + p-value + Breslow-Day actually support
- **Direction-of-effect framing**: for the strict vs hedged comparison, does
  the prose correctly distinguish "model resists" from "model hedges"? Are
  the inferences about memorization vs suggestibility properly hedged?
- **Caveat completeness**: does the section flag (a) the construct-validity
  caveat vs Carlini, (b) the frequency × period confound from v3, (c) the
  remaining underpoweredness for OR<2, (d) the absence of a positive
  control (referencing Phase F as future work)?
- **Q1/Q2/Q3 update consistency**: do the new answers cite the new tables?

Save to `docs/REVIEW_amber_G4.md`.

**Gate decision:**
- PASS → proceed to E3 (commit)
- ITERATE → revise prose, re-dispatch G4
- ABORT → only if Codex identifies a fundamental misinterpretation; in that
  case re-read the data and rewrite the conclusions before committing

---

**E3.** Commit results:
```bash
git add docs/PILOT_RESULTS.md docs/BUG_AUDIT_amber.md \
        data/results/diagnostic_2_results.json \
        data/results/sensitivity_analysis.json \
        data/results/quick_stats_amber.txt \
        config/prompts/counterfactual_templates.yaml \
        src/metrics.py src/pilot.py src/masking.py scripts/run_diagnostic_2.py \
        scripts/quick_stats.py scripts/sensitivity_analysis.py \
        scripts/rescore_fo_flip.py
```
Commit message proposal:
```
amber-mirror-lattice: fix v3 silent bugs + re-run D1

- Bug 1: relax changed_spans schema maxLength (was killing whole-sentence CF rewrites)
- Bug 2: surface n_total/n_scored/n_cf_failed in meta and per-stratum
- Bug 3: split fo_flip into strict/hedged variants (neutral retreat now reported as hedged_flip)
- Bug 4: add polarity check on LLM-negated false outcome
- Bug 5: minimal symmetry fix on pre/post CPT probe construction
- Phase D re-run (606 cases, pipeline_version=3, all bugs fixed)
- Updated PILOT_RESULTS Q1/Q2/Q3 to reflect new MH numbers
```

---

### Phase F (optional, ~half day) — Matched positive control

This is the **strongest defense** of any final null. Construct-validity
critique (Agent 1): even Carlini 2022 finds that ChatGPT-style chat models
recite verbatim only 3.5% of the time under normal prompts. Our metric
construct (counterfactual input sensitivity + suggestibility) is fundamentally
different from verbatim extraction, so a null result on DeepSeek-chat is
*expected* in the absence of a control showing our metric *can* detect
memorization when memorization is real.

**F1.** Pick 50 cases from `test_cases_v3.json` with high `anchor_level=3`,
real `known_outcome`, varied target_type. These will be the "leaked" set.

**F2.** Build a continued-pretraining corpus by repeating these 50 articles
20-100 times. Mix with a baseline corpus to avoid pathological catastrophic
forgetting.

**F3.** Continued-pretrain Qwen 2.5 7B on this corpus via the existing
Docker vLLM setup (`infra_capabilities` memory has the details).

**F4.** Run the **same v3 pipeline** on the continued-pretrained Qwen with
the same 606 case input.

**F5.** Compare:
- Does Qwen's `fo_flip_direct` show `OR > 1` (memorization-direction) on the
  50 leaked cases vs the unrelated cases?
- Does Qwen's `fo_flip_*_hedged` show stronger evidence than `_strict`?
- If yes → metric works, DeepSeek null is real
- If no → metric is dead even on a controlled-leakage setup, and we need
  to switch to a verbatim-extraction-style probe

**F6.** Add Phase 5 section to PILOT_RESULTS with the positive-control
results, separate from Phase 4.

---

## Critical files

**Read first (Phase 0):**
- `docs/PILOT_RESULTS.md` (end of file)
- `docs/RESEARCH_PROPOSAL.md`
- `docs/ANCHOR_RUBRIC.md`
- `docs/FIRTH_DECISION.md`
- `data/seed/strata_config.json`
- `src/pilot.py`, `src/masking.py`, `src/metrics.py`, `src/llm_client.py`
- `scripts/run_diagnostic_2.py`, `scripts/quick_stats.py`,
  `scripts/sensitivity_analysis.py`
- `config/prompts/counterfactual_templates.yaml`

**Modified by this plan:**
- `config/prompts/counterfactual_templates.yaml` (B1)
- `src/metrics.py` (B3)
- `src/pilot.py` (B3, B4, B5a)
- `src/masking.py` (B4)
- `scripts/run_diagnostic_2.py` (B2, B3)
- `scripts/quick_stats.py` (B3)
- `scripts/sensitivity_analysis.py` (B3)
- `docs/PILOT_RESULTS.md` (E2)
- New: `docs/BUG_AUDIT_amber.md` (Phase A output)
- New: `scripts/_audit_bug1.py` (Phase A2)
- New: `scripts/_audit_bug3.py` (Phase A4)
- New: `scripts/rescore_fo_flip.py` (Phase B3 / C2)

---

## Verification gates

| After phase | Gate |
|---|---|
| A | `BUG_AUDIT_amber.md` exists; for each P0/P1 bug, audit confirmed or refuted with counts |
| B (smoke test) | CF failure rate <5% on 10-case smoke; `fo_flip_*_strict/_hedged` fields present; pipeline_version still 3 |
| C | Rescored `quick_stats.py` output exists; per-stratum strict vs hedged comparison printed |
| D | full 606-case run, 0 errors, `n_llm_failed_pre` <5% of pre cases, all per-case metrics populated |
| E | PILOT_RESULTS has Phase 4 section with new MH tables; Q1/Q2/Q3 reviewed; commit pushed |
| F (optional) | Qwen continued-pretrain run completes; positive-control MH OR computed |

---

## Risks and mitigations

1. **B3 changes break legacy pipeline (`run_pilot`)**
   - The legacy `run_single_case` still uses the old fo_flip bool. Update it
     to also produce the new fields, OR explicitly mark it deprecated and
     don't run it.

2. **B4 polarity check uses regex from the deprecated `_NEGATE_SWAP_MAP`**
   - The dict was deleted in deep-floating-lake's masking.py edit. Either
     re-introduce it as a *check-only* helper (no fallback path), or call a
     second LLM judge. Re-introducing as check-only is fine because the
     mode-purification rule was about not *using* regex as a probe; using
     regex as a *validator* is OK.

3. **Rescore script (B3 / C2) interprets old `fo_flip` as strict by default,
   may double-count if both old and new fields coexist**
   - Make sure `rescore_fo_flip.py` writes the new fields under namespaced
     keys (`fo_flip_direct_strict_v2`, etc.) and never mutates the old field.

4. **Re-running D1 invalidates cache by changing prompt templates (B1)**
   - The CF template change updates the schema only, not the system_prompt
     or user_prompt_template. So the cache key (prompt-hash-based) should
     still match and Phase D should hit cache for the *content* of CF
     responses while re-running schema validation. Double-check this — if
     the cache key includes the schema, you'll pay full API cost on re-run.

5. **B5b (2×2 design) doubles CPT API cost**
   - Decided: skip B5b in this plan, document as "Phase F optional".

6. **Bug 3 rescore (Phase C) shows the headline result inverts → temptation
   to skip Phase D**
   - Don't. The bug-fix re-run gives clean numbers (no Bug 1 stratum
     distortion); Phase C only re-scores the existing biased sample.

7. **`changed_spans` field is consumed by an analysis script we don't know
   about**
   - Grep for `changed_spans` across the entire repo before deleting it.
     Safer to keep the field but drop its constraints.

---

## Out of scope

- Re-annotating cases (B2 of deep-floating-lake)
- B3 (frequency_class) — already complete
- Reversibility annotation (D2 of deep-floating-lake) — separate fix needed
  in `score_case_from_batches` to persist `rewritten_article` into
  `condition_summary`; not part of this plan
- 2×2 cross design (B5b) — documented as Phase F optional
- Switching annotators (Codex → human) for the 50-case κ check
- Multi-model replication (only DeepSeek and optionally Qwen as positive
  control)

---

## Effort estimate

| Phase | Wall time |
|---|---|
| 0 — boot context | 10 min |
| A — bug audit | 30 min |
| **G1 review (parallel sub-agent)** | **5 min wall (Codex thinks ~3 min)** |
| B1 — schema fix | 15 min |
| B2 — diagnostic logging | 20 min |
| B3 — fo_flip refactor + rescore script | 1.5 h |
| B4 — polarity check | 30 min |
| B5a — minimal symmetry fix | 30 min |
| **G2 review (2 parallel sub-agents)** | **8 min wall** |
| C — rescore + interpret | 15 min |
| D — re-run D1 | 50 min wall + ~10 min babysit |
| **G3 review (parallel sub-agent)** | **5 min wall** |
| E — analysis + PILOT_RESULTS rewrite | 1 h |
| **G4 review (parallel sub-agent)** | **5 min wall** |
| **Subtotal (Phases 0-E + 4 gates)** | **~6 hours** |
| F (optional) — matched positive control | half day |
| **Total** | **~6 h core, ~10 h with positive control** |

---

## Codex review prompt templates

Each gate dispatches one (or two) sub-agents. The sub-agent's prompt is
self-contained: it must explain to a fresh agent how to call Codex MCP and
what to ask. Use the `Agent` tool with `subagent_type: general-purpose` and
copy-paste the relevant template below.

### Template — Gate G1 (audit sanity check)

```
你是一个调度 agent。你的唯一任务是调用 mcp__codex__codex 让 GPT-5.4 审查
docs/BUG_AUDIT_amber.md 这份 bug audit 报告，然后把 GPT 的返回写到
docs/REVIEW_amber_G1.md 并给我返回 ≤200 字的中文 1-段总结。**不要自己分析，
只做 orchestration。**

调用 mcp__codex__codex 时使用以下参数：
- sandbox: "danger-full-access"
- cwd: "D:\\GitRepos\\LLM-Leakage-Test"
- config: {"model_reasoning_effort": "xhigh"}

给 Codex 的 prompt:
---
你是一个 LLM 实验方法学的 hostile 审稿人。请独立审查
D:\GitRepos\LLM-Leakage-Test\docs\BUG_AUDIT_amber.md。

这份 audit 声称 v3 pipeline 存在 5 个 bug（3 个 P0、2 个 P1）。请直接读以下
源文件验证每个 bug 的真实性：
- src/pilot.py
- src/masking.py
- src/metrics.py
- scripts/run_diagnostic_2.py
- config/prompts/counterfactual_templates.yaml

对每个 bug 回答：
1. audit 给的行号是否正确？
2. mechanism story 是否站得住脚（即这个 bug 是否真的会在我们的 pipeline 上
   产生宣称的效应）？
3. audit 给的 quantitative impact（如 NP 失败数 122/610，hedged retreat 数
   79+55）能否在源数据里独立验证？
4. 是否还有其他 P0/P1 bug audit 没找到？特别检查：
   - score_case_from_batches 里的 cf_invariance 4-cell 划分
   - cfls_per_case 的 slot 迭代
   - LLMClient.batch_chat_concurrent 的 failure_isolated 路径在 retry 时是否
     正确重置 cache key

最后用以下三种 verdict 之一结尾：
- PASS — audit 准确，可以进入 Phase B 修 bug
- ITERATE — audit 有错误（列出哪些），需要重做 Phase A 再 review
- ABORT — bugs 都不真实，null result 是真的，停止 amber 计划，进入 Phase F

把完整 review 写到 D:\GitRepos\LLM-Leakage-Test\docs\REVIEW_amber_G1.md
（用 Write tool）。文件最后一行必须是 "Verdict: PASS|ITERATE|ABORT"。
---

写完后告诉我 verdict 是什么。
```

### Template — Gate G2a (line-by-line diff review)

```
你是一个调度 agent。任务：调用 mcp__codex__codex 让 GPT-5.4 做 hostile
code review 所有 Phase B 的 commit。把结果写到 docs/REVIEW_amber_G2a.md，
返回 ≤200 字总结。**不要自己分析，只做 orchestration。**

调用参数：
- sandbox: "danger-full-access"
- cwd: "D:\\GitRepos\\LLM-Leakage-Test"
- config: {"model_reasoning_effort": "xhigh"}

给 Codex 的 prompt:
---
你是一个 hostile code reviewer。我刚修了 5 个 v3 pipeline 的 bug（详见
~/.claude/plans/amber-mirror-lattice.md 的 "Bugs (in order of severity)"
小节）。Phase D 是一个 50 分钟的 API-burning 实验，所以我必须在跑 D 之前
确认每个 fix 都是对的。

请：
1. 跑 git log --oneline 找出从 amber 计划开始之后的所有 commit
2. 对每个 commit 跑 git show 看 diff
3. 对每个 fix 回答：
   a) diff 是否实现了 commit message 声称的修复？
   b) fix 是否破坏了 legacy run_pilot / run_single_case 路径？
   c) 新的 _detect_fo_flip enum 与下游 consumer 的交互是否正确（cfls_per_case,
      score_case_from_batches, aggregate_case_results, quick_stats.py,
      sensitivity_analysis.py 的所有 read 点）？
   d) Bug 4 的 polarity check helper 是不是 reuse 了被删的 _NEGATE_SWAP_MAP？
      它是 *check* (允许) 还是 *fallback probe* (违反 mode purification)？
   e) Bug 1 的 schema relax 是否会让现有 cache invalidate？Phase D 会不会
      意外重花 API budget？
   f) smoke test (--n-cases 10) 是否真的 exercise 了新 code paths？特别检查
      edge cases:
        - 一个没有 key_entities 的 case
        - 一个 expected_direction="neutral" 的 case
        - 一个 ORIG output malformed 的 case
        - 一个 hedged_flip case (FO=neutral, ORIG≠neutral)

4. 列出每一个发现的问题，按 severity 排序，给文件:行号 + 修复建议
5. 最后用 PASS / ITERATE / ABORT 一个 verdict 结尾

把完整 review 写到 D:\GitRepos\LLM-Leakage-Test\docs\REVIEW_amber_G2a.md。
最后一行必须是 "Verdict: PASS|ITERATE|ABORT"。
---

写完后返回 verdict。
```

### Template — Gate G2b (independent re-derivation)

```
你是一个调度 agent。任务：调用 mcp__codex__codex 让 GPT-5.4 *独立* 推导出
5 个 bug 的最小正确 fix（不看现有实现），然后对比实际实现。把结果写到
docs/REVIEW_amber_G2b.md，返回 ≤200 字总结。**不要自己分析。**

调用参数同 G2a。

给 Codex 的 prompt:
---
我们刚修了 5 个 v3 pipeline bug。我想做一个独立的 cross-check：你不要看
现有的 fix，先独立推导 fix 应该是什么样的，然后再 diff 实际实现。

Step 1：读 ~/.claude/plans/amber-mirror-lattice.md 的 "Bugs (in order of
severity)" 小节。注意：只读 bug 描述，不要读 Phase B 里描述的 fix 细节。

Step 2：对每个 bug，独立推导：
- 最小修复是什么（假设你不知道我们打算怎么修）
- 修复有哪些 reasonable variants
- 每个 variant 的 trade-off

Step 3：现在 *才* 读 git log 和 git diff 看实际实现。

Step 4：对每个 bug 比较你独立推导的 fix vs 实际 fix：
- 是否一致？
- 如果不一致，谁更好？
- 实际 fix 是不是修了一个不同的问题（即 fix 看着对，但其实没解决 audit
  指出的 mechanism）？
- 实际 fix 是否引入了 audit 没提到的新风险？

Step 5：用 PASS / ITERATE / ABORT verdict 结尾，理由要明确。

把完整对比写到 D:\GitRepos\LLM-Leakage-Test\docs\REVIEW_amber_G2b.md。
最后一行 "Verdict: PASS|ITERATE|ABORT"。
---
```

### Template — Gate G3 (D1 numerical sanity check)

```
你是一个调度 agent。任务：调用 mcp__codex__codex 让 GPT-5.4 review Phase D
的 D1 重跑结果。写到 docs/REVIEW_amber_G3.md，返回 ≤200 字总结。

调用参数同 G2a。

给 Codex 的 prompt:
---
你是一个数据完整性审稿人。Phase D 刚跑完，我想在写 PILOT_RESULTS 之前确认
新的 D1 结果在数学上是自洽的。

请直接读以下文件：
- D:\GitRepos\LLM-Leakage-Test\data\results\diagnostic_2_results.json (新结果)
- D:\GitRepos\LLM-Leakage-Test\data\results\diagnostic_2_results.v3_pre_amber.json (旧结果对照)
- 跑 conda run -n rag_finance python scripts/quick_stats.py 看输出
- 跑 conda run -n rag_finance python scripts/sensitivity_analysis.py 看输出

对每一项独立验证：

1. **Schema 完整性**：每个 case 都有新的 _strict / _hedged 字段吗？哪里出现
   silent None？

2. **Per-stratum 一致性**：把 stratum 总和 vs meta.n_cases_completed 对账。
   n_total - n_scored - n_cf_failed 是否能 reconcile？

3. **Per-chunk 连续性**：从 stdout/log 里走一遍 13 个 chunk，有没有失败率
   异常高/低的 chunk？

4. **Diff vs v3 baseline**：
   - mean CFLS 移动了多少？
   - fo_flip_*_strict count 是否和 v3 接近（理论上应该相同——同样的 scoring
     底层）？如果差很多，为什么？
   - fo_flip_*_hedged count 比 _strict 多多少？

5. **Cell 稳定性**：v3 里非空但现在为空的 cell（或反之）—— 解释每一个

6. **Cache hit rate**：Phase D 的 wall time vs v3 的 ~50min。如果差很多，
   flag 出来——可能 Bug 1 cache invalidation 有副作用

最后给 PASS / ITERATE / ABORT verdict。

写到 D:\GitRepos\LLM-Leakage-Test\docs\REVIEW_amber_G3.md。
最后一行 "Verdict: PASS|ITERATE|ABORT"。
---
```

### Template — Gate G4 (writing review)

```
你是一个调度 agent。任务：调用 mcp__codex__codex 让 GPT-5.4 review
PILOT_RESULTS.md 新增的 "Phase 4 (amber-mirror-lattice)" section。
写到 docs/REVIEW_amber_G4.md，返回 ≤200 字总结。

调用参数同 G2a。

给 Codex 的 prompt:
---
你是一个 hostile peer reviewer。我刚把 amber-mirror-lattice 的实验结果写
到 D:\GitRepos\LLM-Leakage-Test\docs\PILOT_RESULTS.md 的 "Phase 4
(amber-mirror-lattice)" section。在 git commit 之前请审阅这一节。

只看 "Phase 4 (amber-mirror-lattice)" section 和它更新的 Q1/Q2/Q3。

具体检查：

1. **数字一致性**：prose 里出现的每个数字是否在某个 table 里能对上？
   table 里的每个数字是否能从 data/results/diagnostic_2_results.json +
   data/results/sensitivity_analysis.json 里独立 reproduce？随机抽 5 个
   数字独立验证。

2. **Overclaiming**：每一句 "we show that..." / "this confirms..." /
   "this rules out..." 是否被 MH OR + p-value + Breslow-Day 实际支持？
   特别注意因果语言和 measurement-construct claim 的边界。

3. **Direction-of-effect framing**：strict vs hedged 的对比，prose 是否
   正确区分 "model resists" 与 "model hedges"？memorization vs suggestibility
   的 inference 是否被适当 hedge？

4. **Caveat 完整性**：这一节是否提到了：
   (a) Carlini/Nasr construct validity 的 caveat
   (b) v3 的 frequency × period confound
   (c) OR<2 的 underpower 残留
   (d) 没有 positive control（引用 Phase F 作为 future work）

5. **Q1/Q2/Q3 一致性**：新的 Q1/Q2/Q3 答案是否引用了新的 table？是否和
   Phase 3 的旧答案有冲突？冲突有没有 explicitly addressed？

6. **Reader test**：一个不熟悉这个项目的 reviewer 看了这一节能否独立
   reconstruct 实验设计和结论？

最后用 PASS / ITERATE / ABORT verdict。

写到 D:\GitRepos\LLM-Leakage-Test\docs\REVIEW_amber_G4.md。
最后一行 "Verdict: PASS|ITERATE|ABORT"。
---
```

---

## Quick reference: gate dispatch order

```
Phase 0 → Phase A → [G1] → Phase B → [G2a + G2b parallel] → Phase C → Phase D → [G3] → Phase E (E1+E2) → [G4] → Phase E (E3 commit) → [Phase F optional]
                     ↑                  ↑                                       ↑                          ↑
                     blocks B           blocks C and D                          blocks E                   blocks commit
```

If any gate returns ITERATE, fix the issues, regenerate the artifact (audit
file / source files / results JSON / PILOT_RESULTS section), and re-dispatch
the same gate. Do NOT skip ahead.

If any gate returns ABORT, stop the linear plan and reassess. ABORT verdicts
should be rare; the 4 most likely ABORT scenarios are:
- G1 ABORT: the bugs are not real → null is genuine, jump to Phase F
- G2 ABORT: the fix architecture is wrong → re-do Phase B from scratch
- G3 ABORT: D1 numbers contradict each other → debug pipeline before writing
- G4 ABORT: the writing fundamentally misreads the data → re-derive
  conclusions before any commit
