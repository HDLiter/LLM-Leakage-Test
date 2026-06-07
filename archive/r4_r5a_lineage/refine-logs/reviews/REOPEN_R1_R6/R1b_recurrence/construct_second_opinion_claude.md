---
title: R-1b Construct second opinion (independent, blind to first opinion)
author: Claude Code (second reviewer)
date: 2026-05-25
scope: meta-question only — Recurrence = pure text exposure proxy (A) vs outcome-leakage proxy (B)
inputs read:
  - docs/RESEARCH_PROPOSAL.md §1, §2, §3, §4.1, §4.4
  - refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md §1-§5
  - docs/DECISION_20260518_ws0_5_thales_alignment.md §4.5 (R-0 container), §5 (Recurrence prototype prose, audit only)
inputs deliberately NOT read (anti-anchoring):
  - construct_stress_test.md (first opinion's full verdict)
  - whiteboard_analysis.md section (a) (already rewritten under first opinion's choice)
constraint: binary choice, no fence-sit, no "primary + robustness" hedge
---

# R-1b Construct — independent second opinion

## 0. What I am answering

One meta-question only:

> Is `log1p(recurrence_count)`, as it enters the main statistical model
> through the β3 = Cutoff Exposure × Recurrence interaction, conceptually
> a **pure text-exposure proxy** (A) or an **outcome-leakage proxy** (B)?

A says: any CLS row where the target appears as subject counts toward the
reference window's recurrence count, regardless of `tradable_at_event`. The
construct is "text-pattern repetition the model saw during pre-training."

B says: only `tradable_at_event=true` subject rows count. The construct is
"the model had repeated opportunity to memorize an outcome that could
later leak through prediction."

I work the two sides independently first, then settle.

---

## 1. A-stance steelman (pure text-exposure proxy)

### 1.1 The driver chain A is committing to

```
A: more CLS rows with (target × event-family) text pattern, pre-cutoff
   → more pre-training exposure to that text pattern
   → higher next-token familiarity on that text shape (Carlini-style scaling)
   → higher amplitude on β3 across estimands that read "model's response is
     unusually pattern-locked / familiar / fluent on this case"
```

The construct A is testing for is **textual familiarity intensity**. It is
agnostic about *why* the model would express that familiarity later — it
could express it as low surprisal (logprob), as fragile template-matching
(NoOp flips), or as memorized continuations (FO resistance, CMMD
convergence). All of those failure modes route through the same underlying
quantity: "how many times did the model see this kind of (target, family)
text in pre-training."

### 1.2 Why this is internally clean

- **One axis, one job.** A keeps Recurrence as "text-exposure intensity." It
  does *not* try to also encode "outcome was memorizable" or "outcome was
  tradeable." Those concerns live elsewhere:
  - `Cutoff Exposure` (β1) carries "model had temporal access."
  - R-5 universal admissibility (`tradable_at_event=true`) already gates the
    *case under prediction* to have a tradable subject. Without this filter
    the prompt-level leakage entry point kicks in (R-0 §4.5.A note).
  - So under A: Cutoff handles "did the model see anything related," R-5
    handles "is the case under test a tradable outcome we can talk about
    leakage on," and Recurrence is the third axis that says "how rich was
    the pattern exposure." Three orthogonal axes, no double-coding.
- **No carve-out to defend.** A's count is "any subject row of (target,
  family) in the pre-cutoff window." There is no special-case prose needed
  for halted / pre-listing / delisted-transition subject rows. A reviewer
  asking "why did you count this row?" gets the same answer for every row:
  "the model saw this text."
- **Direct literature anchor.** Carlini 2023 "Quantifying memorization
  across neural language models" (arXiv:2202.07646) gives a log-linear
  scaling of verbatim extraction with training-time repetition count. That
  scaling does not condition on whether the entity discussed in the
  repeated passage was tradable on a given exchange — it is a property of
  text repetition full stop. So A is the construct that maps 1:1 to the
  scaling result we want to invoke.
- **The factor is already in `log1p` form on a continuous scale.** A
  doesn't need clean / dirty subcategories of rows; it just needs the
  count to track "total exposure." `log1p` does the diminishing-returns
  smoothing the scaling literature suggests.

### 1.3 What A pays as a cost

- **Some counted rows are "noise" from the outcome-leakage point of view.**
  A halt-period subject report on Stock X contributes to `recurrence_count`
  for `(X, halt_resume_family)`. The model saw that text, but the entity
  wasn't tradable that day — so any "outcome the model memorized from that
  row" cannot show up later as a prediction-direction leak (the entity has
  no actionable direction at the article's published time). Under A, these
  rows count anyway, and the β3 lift they generate is attributed to "text
  exposure" not "outcome leakage."
- **But empirically the cost is bounded.** First opinion's raw CLS probe
  reports ~2.91% of articles touch non-tradability triggers (halt /
  delist / pre-listing / listing-day union). At the subject-row level the
  fraction could be different, but the order of magnitude is small. So A
  pays a < ~5% count-noise tax, on a `log1p` scale, on a continuous factor.
  That noise is *additive on the predictor side*, not bias on β3 — it
  attenuates β3 slightly via classical errors-in-variables. Acceptable for
  a characterization benchmark.

### 1.4 A's strongest single sentence

> Recurrence measures how many times the model saw the (target × family)
> text pattern during pre-training; β3 asks whether that text-exposure
> intensity moderates the cutoff effect across five different estimand
> readouts.

---

## 2. B-stance steelman (outcome-leakage proxy)

### 2.1 The driver chain B is committing to

```
B: more CLS rows with (target × event-family) subject pattern, pre-cutoff,
   AND target tradable at the article's published time
   → more pre-training exposure to (target, family) WITH a tradable
     outcome attached
   → higher probability the model memorized an actionable outcome
   → β3 amplitude tracks "outcome-memorization opportunity," not just
     "text familiarity"
```

The construct B is testing for is **opportunities to memorize a
tradeable outcome**. It deliberately excludes subject reports where the
target wasn't tradable on the article date, on the argument that those
reports lack a usable outcome to be the *thing that leaks*.

### 2.2 Why this is internally clean

- **Tight semantic alignment with "leakage."** The project's stated
  meaning of "leakage" is "model uses post-cutoff (or look-ahead) outcome
  knowledge to bias predictions on a case the analyst is treating as a
  pre-cutoff prediction task." B aligns Recurrence to exactly that
  semantic content: each counted row corresponds to a (target, family)
  occurrence that *also* had a tradeable outcome that could become
  leakable later.
- **Anchors β3 to the same concept it's meant to test.** β3 is "high
  Recurrence × high Cutoff Exposure → more leakage." B reads this as a
  single tight construct: opportunities × access → leakage. A reads it
  as the more diffuse construct: exposure × access → behavioral
  familiarity-shift.
- **Schema cost is zero.** `tradable_at_event` is already in L2 by R-0
  §4.5.A. No new column, no Pool D extension. B just composes the existing
  L3 base view.
- **R-5's universal admissibility is already gating subjects-under-test
  by tradability.** B's argument: if tradability is the right filter for
  the *test case*, why isn't it also the right filter for the *reference
  rows we count against*? Consistency.

### 2.3 What B pays as a cost

- **Conceptual gap with E_PCSG, E_CTS, and E_NoOp.** These three
  estimands' actual signal channel is "model has seen text similar to
  this case" — measured via logprob (E_PCSG, E_CTS) or via fragility on
  perturbation (E_NoOp = template lock). None of these channels need the
  target to have been tradable at the time of the reference row. A
  halt-period subject report increases the model's familiarity with the
  pattern in a way that *would* show up on logprob and *would* increase
  template lock — and B drops it from the count, so β3 under B
  systematically *under-uses* the variance these estimands actually carry.
- **Carlini 2023 anchor weakens.** Carlini's extraction-rate scaling is
  about text repetition. If B counts only "tradable-subject rows," it is
  counting a subset of the rows that drive the scaling phenomenon. The
  anchor still applies "morally" (more reference rows → more memorization
  signal) but you can no longer say "our count = the count Carlini's
  scaling law uses."
- **Double-counts tradability vs the R-5 filter.** Tradability is already
  the universal admissibility rule for the subject under prediction. B
  imports the same gate into the reference window. The two roles of
  tradability are different (one filters *who we ask the model about*,
  the other filters *what we count as prior exposure*), but the literal
  predicate is identical — easy reviewer-fodder for "are you giving
  tradability two jobs."

### 2.4 B's strongest single sentence

> Recurrence measures how many times the model had a chance to memorize
> a tradeable outcome attached to (target × family); β3 asks whether
> that memorization-opportunity intensity moderates the cutoff effect.

---

## 3. Five-estimand × A/B coverage matrix

Each row is the *driver chain* the estimand actually rides on. "A
covers" = A's construct ("text-pattern exposure intensity") is the
right explanation for what β3 amplitude on this estimand would mean.
"B covers" = B's construct ("outcome-memorization-opportunity
intensity") is the right explanation.

| Estimand  | What the estimand actually reads | A covers? | B covers? | Asymmetry |
|-----------|----------------------------------|-----------|-----------|-----------|
| **E_CMMD** | Cutoff-monotone disagreement on P_predict direction across the fleet | Partial: text exposure → familiarity ≠ directional convergence cleanly | Yes: outcome memorization → fleet-level directional convergence | B better here; A still works if you assume text exposure → outcome-text exposure → direction |
| **E_PCSG** | Late-minus-early logprob delta on the article text, paired tokenizer | **Yes (clean):** logprob delta is *pure text familiarity* | No extra power: tradability does not enter the logprob channel; B's filter drops rows that *do* affect logprob | **A strictly better** |
| **E_CTS**  | Calibrated tail surprise on the article text | **Yes (clean):** same as E_PCSG, surface familiarity | No extra power: same as E_PCSG | **A strictly better** |
| **E_FO**   | P_predict(original) − P_predict(C_FO swap); does the model insist on the memorized outcome? | Yes: text exposure subsumes outcome-text exposure (a special case) | **Yes (tightest fit):** this estimand is *the* outcome-memorization probe by construction | Both cover; B is the more direct semantic fit; A also fits via the subset relation |
| **E_NoOp** | P_predict(original) − P_predict(C_NoOp insert); template fragility / brittle pattern-match | **Yes (clean):** template lock is a function of text repetition, full stop | No extra power: a non-tradable subject report still strengthens template lock; B's filter drops rows that *do* affect fragility | **A strictly better** |

Summary score (informal):

- A's driver chain cleanly covers **5 / 5** estimands. On E_CMMD and E_FO
  it is a slightly looser fit than B (it has to route through "outcome
  text is a kind of text"). On E_PCSG, E_CTS, E_NoOp it is the **only**
  construct that matches the actual signal channel.
- B's driver chain cleanly covers **2 / 5** estimands (E_CMMD, E_FO). On
  the other three it *under-uses* the variance because it filters out
  rows that would have contributed to logprob / template-lock signal.

This is the single most decisive piece of evidence in this analysis.
Three of five estimands' actual computational signal channels do not
care about tradability at the reference-row level; one strictly benefits
from B's tighter framing (E_FO); one (E_CMMD) is somewhere in between.
The benchmark publishes β3 on all five — so the construct that
underwrites all five is the correct choice.

---

## 4. Sanity-checks

### 4.1 If we pick A and β3 lifts mainly through E_FO

Question: does A's construct ("text exposure") have a conceptual gap
with E_FO's actual driver ("model memorized a specific outcome value
and refuses to release it under perturbation")?

Answer: **no real gap.** Carlini 2023's extraction-rate scaling *is* the
chain "more text exposure → higher chance of verbatim recall of any
specific span." The outcome value (a number, a verdict, a date) is just
a span the model may have memorized. The probability of E_FO firing on
case `c` scales with how many times the model saw the (target, family)
text pattern containing that outcome span — and that's exactly what A
counts. The link "text exposure → outcome-span memorization → E_FO
resistance" is a single Carlini-style chain, not a coincidence. There is
no need to upgrade the construct from "text exposure" to "outcome
exposure" for E_FO to be theoretically supported.

(If the worry is "A's count includes rows whose outcomes the model
*couldn't* memorize as actionable," the answer is: it doesn't matter for
E_FO's β3, because what β3 reads is the *moderation pattern*: cases with
more text exposure should show more FO resistance. The rows that "don't
contribute" to FO simply make the slope a little flatter — they don't
flip its sign or its interpretation.)

### 4.2 If we pick B, does Carlini 2023 still anchor?

**Partially, and with a weakening that has to be acknowledged in prose.**
Carlini's scaling result does not condition on tradability. Under B, the
project's count is a strict subset of the count Carlini's scaling refers
to. So the paper would have to say one of:

- "We use a stricter count than Carlini's; we expect the scaling to be
  qualitatively similar but lose ≤ ~5% of the reference rows" — fine,
  but it concedes that B is *not* the construct Carlini's anchor pins
  down.
- "We focus on the tradable-subject subset because that is the population
  where memorized outcomes can actually leak through prediction" — fine
  rhetorically, but this is a B-specific argument and Carlini becomes an
  *analogy* rather than a direct anchor.

The Carlini anchor survives B only as an analogy. It directly fits A.

### 4.3 The < 5% empirical gap — does the choice matter at all?

**Yes, but mostly at the prose / construct-defense layer, not at the
numeric β3 layer.**

Numerically: a < 5% reduction in `recurrence_count` followed by `log1p`
gives a near-imperceptible change in the predictor's distribution. β3
point estimates and SEs under A vs B will be statistically
indistinguishable for almost every case. So the numeric result does not
hinge on the choice.

But the construct choice still matters because:

- The construct *labels* what β3 means. "Text-exposure × Cutoff →
  leakage" tells one story; "Outcome-memorization-opportunity × Cutoff
  → leakage" tells a different story. These are the stories the paper
  has to defend in §4 + §discussion.
- Reviewers will ask "what does Recurrence measure?" and the answer has
  to be self-consistent across all five estimands' interpretations. A
  gives a single answer that holds for all five. B gives an answer that
  is most natural for E_FO and E_CMMD but uncomfortable for E_PCSG,
  E_CTS, E_NoOp.
- B requires an extra prose carve-out for "why are halt-period and
  pre-listing subject rows dropped from the reference count even though
  the model saw them" — a question A never has to answer.
- B subtly double-codes tradability (R-5 admissibility filter + B's
  reference filter). A keeps tradability doing one job and Recurrence
  doing one job.

So the choice is small in numbers and large in narrative coherence. For
a benchmark paper whose contribution *is the construct framework*,
narrative coherence is exactly what matters.

---

## 5. Independent verdict

**A.** Recurrence is a **pure text-exposure proxy.** No `tradable_at_event`
filter on the reference rows.

One-sentence main reason: **3 of 5 estimands (E_PCSG, E_CTS, E_NoOp)
have signal channels that are pure text-pattern functions and do not
benefit from a tradability filter on the reference window — so the
construct that underwrites all five readouts is text-exposure, not
outcome-memorization-opportunity.**

---

## 6. Key drivers of this verdict

The verdict is driven by two arguments, ranked:

### Driver 1 (decisive): the 5-estimand coverage asymmetry

A's construct cleanly explains the signal channel of all 5 estimands.
B's construct cleanly explains only 2 (E_FO, E_CMMD); on the other 3,
B's filter drops rows that demonstrably *do* affect the readout
(logprob, template lock). For a benchmark that publishes β3 on the full
estimand family, the construct must be the one that fits the full
family. That construct is A.

### Driver 2 (architectural): no double-coding of tradability

R-0 §4.5.A already uses `tradable_at_event` to filter the *subject under
prediction* (universal admissibility). Importing the same predicate into
Recurrence's reference window gives tradability two distinct jobs under
the same name — easy reviewer ambiguity. A keeps each axis doing one
thing: Cutoff Exposure = temporal access; Recurrence = text-pattern
exposure intensity; R-5 admissibility = "the case under test has a
tradable outcome." Clean three-axis decomposition, each axis carrying
exactly one construct. B collapses one of those axes into another.

(Carlini 2023 fit, narrative simplicity, and the bounded < 5% count-noise
cost are supporting arguments but not load-bearing. The decisive piece
is Driver 1.)

---

## 7. What this verdict commits R-1b to (downstream constraints)

For the owner's benefit when comparing to the first opinion:

- Reference rows for `recurrence_count`: any L2 row matching (target ∨
  alias, family member-types) in the pre-cutoff window, no
  `tradable_at_event` filter. (L1 vs L2 — i.e. mention vs subject — is
  a separate sub-decision (b); this verdict is silent on it. The
  text-exposure construct is consistent with either L1 or L2 as the
  reference layer; the choice between mention and subject is a
  separate axis about *granularity of pattern*, not about A-vs-B.)
- Paper prose for §4.1: "Recurrence measures pre-cutoff CLS text-pattern
  exposure intensity for (target × event-family), proxying the model's
  training-time familiarity with the pattern. We do not filter the
  reference window by tradability; tradability gates the case under
  prediction (R-5 admissibility), not the reference exposure count."
- Carlini 2023 stays the literature anchor, directly cited.
- No Pool D / E extension triggered by this decision (it would only be
  triggered if R-1b chose the mention-construct over the subject-
  construct; that's sub-decision (b), not this meta-question).
- B's narrative ("outcome-memorization-opportunity") is not used in any
  primary or robustness slot. Owner explicitly forbids "primary + B as
  robustness" — and the analysis supports that: B is not a robustness
  check on A, it's a different construct that *under-uses* 3/5 estimand
  channels. Putting it in robustness would invite reader confusion, not
  resolve it.
