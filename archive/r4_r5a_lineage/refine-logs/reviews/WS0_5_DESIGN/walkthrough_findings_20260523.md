# WS0.5 Walk-through findings — 2026-05-23 PM

> **Purpose**: Captures the cross-boundary user proposals + mental-model
> re-anchors + B-2 implementation-time spec decisions surfaced during the
> 2026-05-23 PM rubber-duck walk-through. Memo edits derived directly from
> this walk-through have already landed in `docs/DECISION_20260518_ws0_5_thales_alignment.md`
> (frontmatter v0.4 cont. 2026-05-23 PM); this file is the residual — what
> was not folded into the memo because it belongs in R-1 reopen sessions
> or in B-2 implementation.
>
> **Baseline before walk-through**: commit `dd9a328` (memo v0.4 cont. with
> B-3 infra-drift audit + §6 reproducibility calibration).
>
> **Input sources**:
> - Codex final-pass audit (`infra_quality_pass_20260523.md`) — 3 must-fix / 4 recommend / 5 flag-only
> - Section-by-section conversational walk-through with the user (§5 / §6.1 / §6.2 / §6.3 / §6.4 / §6.5 / §7 / §8-§9)

---

## A. R-1 reopen-session input (factor-side cross-boundary)

These were user-proposed during the §5 walk-through but were held out
of this session per the kickoff rule:
> 如果用户在 walk-through 里跨进因子主题，标出来并提示「这块在 R-1 重开后再说」

The proposals are substantive and would re-architect §3.3 + §5 + parts of
§6/§7. Locking them in this session would override clean-room-first R-1
treatment. Each item is recorded so the corresponding R-1 kickoff can pick
it up as user-driven design input.

### A.1 Four-layer corpus stratification framing → R-1b + R-1c

User proposed re-framing the corpus as four nested layers, each layer
adding annotation / filtering:

1. **Layer 1 — full CLS raw** (`data/cls_telegraph_raw/`, ~1M items): pool
   that downstream layers are drawn from; largest, least annotated
2. **Layer 2 — articles containing an A-share entity**: extracted from
   Layer 1 by entity matching; alias generation + disambiguation applied
   here; **this is where entity occurrence frequency is measured** (i.e.,
   where Target Salience / Recurrence base counts live in user's framing)
3. **Layer 3 — articles where an A-share entity is the *subject***:
   subject identification (user proposed via LLM, see A.3) + preprocessing
   filters (see A.4); **this is where topic classification is meaningful**
   in user's framing ("only at Layer 3 does topic have meaning for the
   target")
4. **Layer 4 — predictable articles**: drop articles where the A-share
   entity was unlisted at publication time; pilot/benchmark cases drawn
   from Layer 4

**Relationship to current memo**: User's Layer 2 ≈ memo's post-R4
candidate pool; Layer 3 ≈ memo's §3.3.1 admissibility output; Layer 4
adds a new listing-status filter not in memo anywhere. User showed
uncertainty about *where* Recurrence is logged ("Layer 3? or 4? — because
only at 4 can template + returns be tied together"); this maps to
construct confusion that should be cleanly settled in R-1b.

**Action**: feed to R-1b (Recurrence) + R-1c (Target Salience) reopen
sessions as user-driven structural proposal.

### A.2 Pipeline reorder + subject-vs-mention construct shift → R-1b

User implicitly proposed a substantial reorder:

- **Memo current**: R1 topic-classify FULL CLS ($200-400) → R2-R5
  entity match + count (mention-based)
- **User proposed**: entity match first (produces Layer 2) → subject ID
  (produces Layer 3) → topic-classify **only Layer 3** (much smaller,
  cheaper) → count Recurrence as "target was subject of (super_type)
  article" (subject-based, not mention-based)

**Construct implication**: Recurrence semantics shift from "mention
density of (target, family)" to "subject density of (target, family)".
Two articles illustrate:
- "茅台 H1 净利 +30%": memo counts +1, user-proposed counts +1 (target is subject)
- "券商今日金股: 茅台 / 五粮液 / 招行": memo counts +1, user-proposed counts 0 (target is mentioned but not subject)

**Cost implication**: Full-CLS topic classification ($200-400, the §7
biggest line item) may disappear; subject-ID LLM cost on Layer 2 adds in;
net spend ratio depends on Layer 2 / full-CLS size ratio (empirically TBD).

**Cascading on basic infra (§6 / §7)**: If full-CLS classification is
removed, Tier B's "full-CLS spend" justification weakens; backup
cost-benefit shifts; §7 layer-3 cost-cap calibration may change. None of
this is fatal, but it's another reason **§5 prose should not be locked
this session** — R-1b's outcome materially affects §6/§7 too.

**Action**: feed to R-1b (Recurrence) reopen as the central construct +
pipeline question. Note: C-3 settled "continuous vs binary", not
"mention vs subject" — this is a genuinely new construct dimension.

### A.3 Subject-ID via LLM (replacing §3.3.1 centrality rule) → R-1c

User proposed using LLM (V4 Pro or V4 Flash) to identify whether an
A-share entity is the article's subject, instead of memo's current
deterministic centrality rule (§3.3.1: `in_headline OR mention_count ≥ 2`).

**Trade-off**:
- Memo rule: deterministic, free, but coarse (a stock mentioned twice in
  a list still gets in)
- LLM subject ID: better precision, but LLM cost + non-determinism +
  smoke-then-freeze workflow needed

**Action**: feed to R-1c (Target Salience) reopen — the §3.3.1
centrality gate is in R-1c scope. Decide there in clean-room fashion.

### A.4 Preprocessing filters → R-5 + R-1c

User proposed three filters not currently in memo:
- **Drop too-long news** — neither memo §3.3.1 nor any preprocessing
  stage filters by length; new constraint
- **Drop bundle flashes (一次性多条新闻播报)** — CLS feed often packs
  multiple flashes in one item; no memo handling
- **Drop articles where A-share entity was unlisted at publication time**
  — interaction with §3.3.1 admissibility ("is target tradable at time
  T?") and R-1a Cutoff Exposure (case validity vs listing timing)

**Action**: feed to R-5 (sampling准入过滤器) reopen for first two;
feed to R-1c + R-1a interaction for the listing-status filter.

### A.5 LLM-tagged alias risk (replacing R2 deterministic risk rule) — held

User proposed using a dual-agent (Claude + Codex) LLM to label `risk`
for each alias in R2's `target_aliases.json` (high-risk aliases < 10K
volume — feasible LLM budget). Replaces memo's current
deterministic-rule risk scoring (collision count in broader universe,
1-2 char length, common surname/place/industry word).

**Held in this session — two reasons**:
1. If A.2 (pipeline reorder, subject-only counting) lands, the
   disambiguation burden drops sharply (only Layer 3 subject articles
   need precise disambig, not all Layer 2 mentions) — risk tagging
   precision priority then changes. Sequence matters.
2. Minimal-design audit not yet done on the *current* deterministic
   risk rule. No empirical evidence of false-low / false-high cases
   from R2 deterministic risk that LLM tagging would catch. Adding LLM
   without specific empirical justification is `feedback_minimal_design`
   violation (LLM for "robustness" with no named failure mode).

**Action**: feed to R-1b reopen as a sub-decision after A.2 lands. If
R-1b decides against the subject-only reorg, separately re-audit R2
risk rule empirically before deciding on A.5.

---

## B. User mental-model re-anchors (memo currently authoritative)

These were drifts in the user's mental model during walk-through where
the memo has settled / load-bearing decisions; user agreed to
re-anchor rather than change memo.

### B.1 §5 R3 fixed window

**Memo**: window is `[corpus_start, earliest_model_cutoff)`, **fixed**,
does not follow case date T (per C-2 + 2026-05-19 user review, memo:584-595).

**User's walk-through framing**: did not mention the time window;
implied "count over the full pre-cutoff CLS" without anchoring the
specific window or its decoupling from case date.

**Re-anchor**: the fixed window is a load-bearing C-2 decision; it's
what lets Recurrence be computable for post-cutoff control cases (E-5
dissolution) and what makes Recurrence "training-exposure intensity"
rather than "case-relative history".

### B.2 §5.3 LLM disambiguation does NOT enter main path

**Memo (post B-3 fix, memo:758-764)**: §5.3 has two smokes —
**alias-gen** smoke (can upgrade to main path via tier-3 admit) and
**disambiguation** smoke (purely diagnostic; R4 remains deterministic;
follow-up R4 refinement form deferred to follow-up work, not nailed
down in this memo).

**User's walk-through framing**: said "smoke decides whether to upgrade
static steps to LLM" — true for alias-gen, but false for
disambiguation (where the post-B-3 prose explicitly says
disambiguation does NOT upgrade to main path).

**Re-anchor**: only alias-gen smoke is an upgrade gate; disambiguation
smoke is characterization of R4 misses for later follow-up.

### B.3 Tier B is load-bearing during running (not "personal convenience")

**Memo (post 2026-05-23 PM)**: Tier B during a run is the **primary
cost-protection mechanism** (§7 layer 1, via cache UNIQUE key). Only
**after** the run does Tier B decompose into author-internal Path B
input + post-hoc compute disclosure source.

**User's walk-through framing**: described Tier B as "archive, in case
of crash, debug — personal convenience". This understated Tier B's
runtime role under the §7 teardown.

**Re-anchor**: Tier B's runtime role is load-bearing; only post-run
does the author-internal framing apply. Path A (reviewer-facing) is
still independent of Tier B in both phases.

### B.4 Tier B lost ≠ "from-scratch re-run"

**Memo (§6.3 + §6.4)**: Tier B loss impact is **conditional**:
- **Mid-run loss** → cost-protection layer 1 breached; only layer 3
  (account-balance cap) halts; cache repopulates via re-calls (cost
  incurred on the fly)
- **Post-run loss, Kaggle backup intact** → restore from backup,
  sha256-verify (§6.4), Path B continues
- **Post-run loss, Kaggle backup also lost** → Path A still works
  (parquet + provenance + Tier A all in git); Path B requires re-call
  (~$200-400) if author wants to revise post-processing
- **Post-run loss, author doesn't need Path B** → zero impact

**User's walk-through framing**: "lost = re-run from scratch" —
collapses the four scenarios into the worst-case.

**Re-anchor**: the §6.3 Path A/B split exists precisely to decouple
reviewer reproducibility from Tier B; reviewer never sees Tier B
existence/absence. "Re-run" is only the (mid-run loss) OR (post-run +
need Path B + no backup) intersection.

### B.5 §6.5 paper disclosure is 4 items, not 3

**Memo (post 2026-05-23 PM)**: §6.5 has 4 limitation items —
closed-API snapshot, API non-determinism, Tier-B private archive, and
(new) compute disclosure via post-hoc cache aggregation + monthly
statement (no per-call ledger).

**User's walk-through framing**: defaulted to "3 items"-mental-model
inherited from the pre-teardown version.

**Re-anchor**: 4 items; item 4 is the §7-teardown footprint on the
paper-facing disclosure surface.

---

## C. B-2 implementation-time spec decisions

These are decisions the memo deliberately leaves open for B-2
implementation start (the memo flags them as "illustrative" or
"finalized at B-2"):

### C.1 `run_inputs.per_task` concrete schema (§6.2)

The §6.2 JSON example is now marked illustrative. The exact key set
under `per_task` and the per-task / per-model sub-structure (model
identity, decoding params, optional `thinking_effort`, dual-agent
model lists for smoke tasks) is finalized at B-2 implementation start
once the actual task topology is settled. This is the first thing B-2
should finalize, because the caching wrapper's provenance-writer
depends on it.

### C.2 Caching wrapper form (§7.2)

Two implementation options for the provider-agnostic caching layer:
- **Option a** — standalone module `src/r5a/backends/caching_client.py`
  that wraps `(provider_client, request) → cached_response`
- **Option b** — decorator over existing provider clients (no new
  module, less code but more entangled with each provider)

B-2 picks. §8 deliverables lists option a conditionally.

### C.3 Tier B backup trigger cadence (§6.4)

Memo specifies **minimum necessary trigger**: once after full-CLS phase
(§5 R1) completes successfully. B-2 may add intermediate backups
(after auto-tune phase completes, after pilot inference completes) —
flag-only finding; minimal version is sufficient.

### C.4 Whether `provider_headers` storage is JSON blob vs separate columns (§6.1)

Memo says `provider_headers` is nullable JSON. B-2 implementation can
choose JSON blob storage (one column, less schema rigidity) vs
extracting specific known headers (e.g., `x-request-id`, rate-limit
headers) into dedicated columns. Either works; flag-only.

---

## D. Items confirmed accepted in walk-through (no further action)

### D.1 §6.3 Path A vs Path B split
User confirmed: paths互不调用 (correct at path-level); accepts that
Path A needs Tier A (sample skim step 3) and Path B needs Tier A +
Tier B + frozen code (correct at tier-level).

### D.2 §6.4 private backup justification
User confirmed: 财联社 article text copyright → private archive
correct.

### D.3 Hard-fail in Path B replay
User confirmed the four failure modes hard-fail catches (silent value
drift / overwrite committed artifact / hash mismatch / Tier A
duplicate); the `--allow-missing` escape valve writes to
`.partial.parquet` so committed truth is preserved.

---

## E. Out-of-scope: factor-side R-1 territory not entered

The kickoff explicitly scoped this session to the four design-agnostic
infra themes (E-6 / E-8 / E-9 / E-10) plus their §8/§9 footprints.
Factor-side reopen items (C-1 Target Salience / C-2-3 Recurrence /
C-4 dedup / C-5 signal_profile / S-6 discriminant) were not touched
this session — they remain R-1b/c/d/e reopen scope.

User's A.1-A.5 proposals all intersect this scope; routing per §A.

---

## F. Session metadata

- Codex audit report: `refine-logs/reviews/WS0_5_DESIGN/infra_quality_pass_20260523.md`
- Codex signal: `temp/ws0_5_infra_quality_signal.done`
- Session kickoff prompt: `.scratch/session_kickoff_ws0_5_infra_final_pass.md`
- Codex audit prompt: `.scratch/codex_prompt_ws0_5_infra_quality.md`
- Walk-through duration: ~one conversational session (8 sections)
- Memo edits applied: see `docs/DECISION_20260518_ws0_5_thales_alignment.md` frontmatter `revision_basis` "v0.4 cont. (2026-05-23 PM ...)"
- Worktable update: `plans/worktable.md` (B-3 → final pass complete; B-2 still ✅ 可动)
