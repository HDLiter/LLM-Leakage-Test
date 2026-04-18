# PENDING — Cross-Session Open-Item Index

> **Purpose**: persistent to-do index for items that span sessions. Any pending decision, pending investigation, or pending external action the project is waiting on should have one entry here.
>
> **Authority**: this file is the single source of truth for the *status* of each item. Individual plan / review / decision documents may reference an item here but should not duplicate its status.
>
> **Update rule**: when an item resolves, move it to `## Recently closed` at the bottom (keep for ~30 days), then delete. Do not silently remove — the history matters.
>
> **Last updated**: 2026-04-18

---

## Active open items

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

*(empty — populate as items resolve)*

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
