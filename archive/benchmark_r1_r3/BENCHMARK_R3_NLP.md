# BENCHMARK MVP R3 Decision Check — NLP Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher, continuing R1+R2 persona)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md
**R1/R2 references:** BENCHMARK_R1_NLP.md, BENCHMARK_R2_NLP.md

---

**1. Per-Decision Verdict**

- **Decision 1 — Framing deferred: `OK-with-concern`**
  Deferring the paper story is fine. The risk is not the deferral itself; the risk is silently freezing a schema that lacks provenance needed for either story. If you later go taxonomy-first, reviewers will ask how each field was sourced, adjudicated, and versioned. So the deferral is safe only if schema/process provenance is captured now.

- **Decision 3 — One case per event cluster: `OK-with-concern`**
  Cluster-level sampling is the right unit. The weak point is the current selection rule: "earliest or most representative, annotator chooses" is too loose for a benchmark. Earliest stubs and later "representative" analysis pieces can differ massively in length, lexical richness, source authority, and hindsight contamination. That affects both annotation agreement and detector behavior. Keep the one-per-cluster principle, but make canonical selection mostly deterministic, with override + reason. Also store full cluster membership, not just the canonical item. For retractions/corrections/辟谣: do not blindly merge if the later piece reverses claim status; link them, but keep them analytically separable.

- **Decision 5 — Pilot via reprint detection and text replacement: `NEEDS-REWORK`**
  Reprint detection is operationally meaningful, but the replacement step creates a construct-validity problem for memorization measurement. If the released pilot swaps CLS text for the original public-domain source, then the benchmark text is no longer the exact surface form the model may have seen. That is acceptable for a public release artifact; it is not acceptable as the sole text for leakage claims.

- **Decision 7 — Claude Code + Codex cross-validation annotation: `NEEDS-REWORK`**
  As written, this is not strong enough for an EMNLP benchmark. It is legitimate as **LLM-assisted pre-annotation plus human validation**, not as "two frontier LLMs agree, therefore accept." Agreement between Claude and Codex is useful triage, but it is not independent evidence of label correctness.

**2. Critical Question on Decision 5**

Yes: this is the single biggest scientific risk in the current document.

If you **replace CLS text with the public-source original** and then run memorization detectors on the replacement text, you are no longer measuring memorization of the observed CLS article. You are measuring something closer to one of these:

- memorization of the original source rather than the CLS surface form,
- robustness across near-duplicate or paraphrastic variants,
- exposure to the underlying event, not necessarily exposure to the exact benchmark text.

That distinction matters because many memorization-sensitive methods are surface-form sensitive. A CLS repost may add editorial framing, shorten the lead, change the headline, or blend multiple sources. If the model memorized the CLS variant and you test the exchange-announcement original, the inference changes.

So the correct stance is:

- **Public pilot replacement is fine for releasability.**
- **Public pilot replacement is not, by itself, a valid memorization benchmark text.**

For NLP purposes, reprint detection is a defensible provenance-linking task, but it has predictable failure modes: paraphrased rewrites, partial quotation, multi-source blends, headline-only reuse, and editorial adaptation. A practical pipeline is exact match -> fuzzy/shingled similarity -> entity/time overlap -> semantic confirmation, with human confirmation on borderline cases. But the main point is conceptual, not algorithmic: **do not collapse "observed CLS text" and "released public-source text" into one field.**

**3. Annotation Workflow Design Recommendations for Decision 7**

There is enough precedent to defend **LLM-assisted annotation**, but not enough to defend **LLM-only gold construction**.

Relevant precedent is mixed:

- [Gilardi et al. 2023](https://arxiv.org/abs/2303.15056) showed ChatGPT could outperform crowd workers on some text classification tasks.
- [Movva et al. 2024, EMNLP](https://aclanthology.org/2024.emnlp-main.511/) studied LLM-human annotation alignment rather than assuming equivalence.
- [Lindahl 2025, *SEM](https://aclanthology.org/2025.starsem-1.19/) found GPT-4o and Claude can match humans on some argumentation tasks.
- But [Rønningstad et al. 2024, LAW](https://aclanthology.org/2024.law-1.13/) found only κ = 0.425 on entity-level sentiment.
- And [Felkner et al. 2024, ACL](https://aclanthology.org/2024.acl-long.760/) is an explicit warning that GPT-based annotation can be unacceptable for nuanced benchmark construction.

That means your defensible position is: **LLMs are annotation assistants and disagreement detectors, not final arbiters.**

Recommended protocol:

- Use Claude and Codex as parallel structured pre-annotators.
- Measure agreement by field type:
  - categorical: Cohen's κ for two raters, Krippendorff's α if you need a unified missing-data-friendly statistic,
  - ordinal: weighted κ,
  - continuous: ICC,
  - entity/span fields: exact-match and relaxed span F1.
- Do **not** review only disagreement cases. Also audit a random sample from the agreement bucket, otherwise shared systematic bias is invisible.
- Pilot thresholds should be field-dependent, but for "scale" I would keep the R2 bar:
  - categorical release-critical fields: around **0.80**,
  - continuous release-critical fields: around **0.75**,
  - **0.70 is not a green light**; it is a revise-the-guidelines signal.
- Prompting should be **minimal fixed few-shot**, not pure zero-shot. Zero-shot is too unstable for a schema-heavy finance annotation task. But the exemplars must come from a held-out calibration set, not benchmark cases.
- In 3-way disagreement, **human adjudication wins**. If human disagrees with both LLMs on a release-critical field, escalate to a second human/adjudication pass. Do not let the two-model majority overrule human review.
- Fields I would require human annotation or human adjudication for regardless are:
  - canonical cluster selection,
  - reprint/provenance linkage,
  - entity spans and entity normalization,
  - externally grounded outcome fields.

Reviewer-defense structure should be: this is **not an LLM-annotated benchmark in the weak sense**; it is a **human-validated benchmark with LLM-assisted pre-annotation**, with per-field reliability, prompt/model versioning, and explicit audit of false agreement.

**4. Hidden Coupling Risks**

- **Decision 3 x Decision 5:** if `canonical_doc_id` points to a CLS article but the released text is the public-domain original, your "case identity" and your "surface text" diverge. That must be explicit.
- **Decision 3 x Decision 7:** annotation agreement will vary depending on whether annotators see a stub, a repost, or a long analytical piece. You cannot interpret pilot IAA until canonical selection is standardized.
- **Decision 1 x Decision 7:** framing can be deferred, but annotation provenance cannot. You need frozen records of guideline version, prompt version, model version, adjudication status, and text-version provenance now.
- **R2 schema coupling remains live:** one-per-cluster sampling does not remove the need to retain full cluster membership and near-duplicate linkage for downstream analysis.
- **Retraction/correction handling is still under-specified:** merging them into the original event cluster can collapse "initial claim" and "later correction" into one content unit, which is bad benchmark hygiene.

**5. Priority Fixes Before R4 Launch**

1. Decide explicitly whether the public pilot is a **release artifact only** or also a **memorization evaluation set**. It cannot cleanly be both if text replacement is used.
2. Rewrite Decision 7 so that Claude/Codex agreement is a triage mechanism, not an acceptance rule; require human gold auditing of both agreement and disagreement buckets.
3. Tighten Decision 3 into a reproducible canonical-selection policy with override, not free annotator choice.
4. Freeze text/provenance/version bookkeeping before R4, or you will lose the ability to defend the benchmark later.
