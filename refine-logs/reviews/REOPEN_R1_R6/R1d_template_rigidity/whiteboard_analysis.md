# R-1d Template Rigidity — whiteboard analysis (audit trail)

> Session 2026-06-02. Dialogue-style (a), Q1–Q6 sequential.
> CC main-loop + Codex CLI lit scan. No sub-agent white-board needed
> (zero-spec factor, design emerged from dialogue with user).

---

## Q1 — Definition (converged)

**Initial brainstorm**: 5 candidate definitions (sentence-skeleton reuse /
disclosure-vs-original / slot-to-frame ratio / n-gram corpus frequency /
title-content redundancy).

**User insight**: n-gram corpus frequency is not a separate definition but an
operationalization of A (skeleton reuse) and C (slot-to-frame ratio). The
high-frequency n-grams in the corpus ARE the invariant frame, by definition.
This also resolves the P_logprob confusion: P_logprob (Min-K%) looks at the
**least** common tokens; template rigidity looks at the **most** common
n-grams — opposite tails, different signals.

**Converged definition**: Template Rigidity = how much of an article consists
of CLS-corpus high-frequency text fragments. Reference corpus = CLS itself
(not general Chinese). Specific fragmentation method (n-gram size / AI
segmentation) = open item for Q5.

**Screening**: Definition D (n-gram frequency) absorbed into A/C as
operationalization. Definition B (disclosure vs original) rejected as
event-type proxy (overlaps F_topic). Definition E (title-content redundancy)
too narrow. Definitions A + C converge via n-gram frequency lens.

---

## Q2 — Influence channels (converged, 4 channels)

Initial proposal: 4 channels. User challenged Channel 3 (slot substitution)
as mechanically incoherent ("model doesn't skip processing numbers"). CC
agreed and withdrew original Channel 3.

**User-originated replacement for Channel 3 (generalization substitution)**:
High template → many training instances of same template with different slots
and outcomes → model can generalize instead of memorize → LESS resistance
(opposite of Channel 1). Key insight: many near-neighbors doesn't necessarily
mean more memorization — can mean better generalization. These are testable
alternatives with distinct pilot signatures.

Final 4 channels: near-neighbor memory / bias reinforcement / generalization
substitution / pure surface familiarity. See `channel_analysis.md` for
pilot signature table.

---

## Q3 — Discriminant (passed)

Conceptual argument: rigidity measures **text structure** (article-level);
F_recur and F_salience measure **entity-level frequencies**. Key divergence
cases identified:
- High rigidity + low recurrence (small company's first quarterly report)
- Low rigidity + high recurrence (mega-cap's 50th deep analysis)
- High rigidity + low salience (obscure company's standard regulatory notice)
- Low rigidity + high salience (major company in investigative report)

Strongest: same company, same day, two articles with identical F_recur and
F_salience but opposite rigidity (earnings release vs investigative piece).

Expected pairwise |r| ~ 0.3–0.5, VIF well under 10. Formal check at pilot.

---

## Q4 — Literature scan (honest: ~0 direct, method precedent exists)

Codex CLI literature scan. No published work uses text template rigidity as
LLM behavior modulation factor. Closest methodological precedent: Lang &
Stice-Lawrence (2015) tetragram boilerplate share for English 10-K filings.
Chinese financial news template-ness metrics: not found (existing Chinese work
uses templates for event extraction, not rigidity measurement).

User asked about homogeneous vs heterogeneous corpus difference (Lang's 10-K
pool vs our mixed CLS). Resolution: computational equivalence; heterogeneity
introduces universal-boilerplate noise (common CLS expressions) that adds
constant baseline to all articles without affecting relative ranking.
Optional filter (remove n-grams with DF > 90%) as implementation detail.

---

## Q5 — Operationalization (framework locked, parameters open)

Main method: corpus-frequency n-gram coverage. Steps: jieba word segmentation
→ n-gram extraction → corpus DF lookup → Top-K% average DF aggregation.

Reference corpus: L1 deduplicated articles (distinct article_id where at least
one entity matched), within reference window [CLS start, min(fleet cutoff)).

All implementation parameters (n-gram size, K%, tokenizer, transform,
universal-boilerplate filter) are open items resolved pre-pilot via empirical
testing + user audit. User retains right to override any decision based on
audit results.

Cost: very low (one-time n-gram index + per-article lookup).

---

## Q6 — R-4 feedback (locked)

"No-memory-baseline gate is not appropriate for factor admission." Three
reasons: (1) multiple channels, which is active = empirical; (2) R-4 confirmed
bias is within construct; (3) factor admission criteria = definition clarity +
operationalizability + discriminant, not channel determination.

Supersedes "F_template must pass gate" in `project_construct_validity_framing`.

---

## Session methodology notes

- **Zero-spec factor designed from scratch in dialogue**: unlike R-1a/b/c which
  had existing specs to clean-room review, R-1d had nothing. Definition emerged
  from brainstorm + user filtering.
- **User-originated insights drove two key decisions**: (1) n-gram frequency as
  operationalization of skeleton concept (Q1); (2) generalization substitution
  channel replacing flawed slot-substitution channel (Q2).
- **Three outcomes kept on table throughout**: A/B/C verdict not pre-committed;
  converged to A based on Q1–Q5 evidence.
- **Pre-pilot gate added by user**: operationalization must be validated on real
  data before pilot entry. This is stricter than R-1b/R-1c (which only deferred
  to R-1e for factor selection, not for operationalization validation).
