# Entity Linking & Disambiguation

**WS0.5 relevance.** Historical Family Recurrence (memo §5) and Target Salience
(memo §3.3.2) both count how many CLS telegraph articles mention a given pilot
target. That requires entity linking: generate aliases for the ~80-430 A-share /
index / sector targets, match them against the LLM-extracted entities in ~1.2M
CLS items, and disambiguate (e.g. "中信" → 中信证券 vs 中信银行 vs 中信集团).
The E-6 review drew on this literature to settle the §5.2 R2-R4 pipeline.

**Decision it informed (E-6).** The standard EL pipeline — mention detection →
candidate generation → ranking/disambiguation — applies, but for a *closed*
target set backed by *strong securities master data* it collapses to a
deterministic pipeline: build a tiered alias table from AKShare master data
(codes / official names / former names with effective dates) → deterministic
evidence-tier disambiguation (exact code > official full name > unique low-risk
alias > high-risk alias + same-article cue > otherwise unresolved). LLM alias
generation and LLM per-match confirmation are demoted to a one-off,
user-reviewed smoke (§5.3). Full review: `temp/entity_disambig_methods_20260520.md`.

## Papers

- **AIDA — Robust Disambiguation of Named Entities in Text** (Hoffart et al.,
  EMNLP 2011). The classic collective-disambiguation method: a mention-entity
  graph combining prior probability, context similarity, and entity-entity
  coherence. Establishes the prior + context + coherence decomposition.
  *Takeaway:* coherence-style global disambiguation is overkill for short CLS
  telegrams; we keep the prior + local-context part, in deterministic form.

- **BLINK — Scalable Zero-shot Entity Linking with Dense Entity Retrieval**
  (Wu et al. 2020, arXiv 1911.03814). Bi-encoder retrieval over entity
  descriptions + cross-encoder rerank; the modern neural EL workhorse for
  open-domain, million-entity, zero-shot settings. *Takeaway:* built for an
  open-domain scale we do not have — 80-430 known targets with codes need no
  dense retrieval.

- **GENRE — Autoregressive Entity Retrieval** (De Cao et al. 2021,
  arXiv 2010.00904). Recasts EL as constrained generation of the entity name.
  *Takeaway:* elegant, but model-dependent and weak on auditability /
  reproducibility versus a deterministic alias table — the wrong trade for a
  confirmatory factor.

- **Financial Entity Linking at JPMorgan** (arXiv 2411.02695). Industry
  financial-EL work; argues Wikipedia-tuned EL does not transfer to company
  entities and that domain master data / company KGs must anchor the linking.
  *Takeaway:* directly supports anchoring on securities master data rather than
  generic LLM / Wikipedia EL.

- **Chinese Financial NER** (Information Sciences, S0020025522015444;
  paywalled — referenced only). Documents the hard cases of Chinese financial
  NER: company short names, abbreviations, mixed Chinese/English/digit names.
  *Takeaway:* context for why alias generation and the §5.2 rule-based
  risk-scoring (short / generic-token aliases) need care.

## Pointers
- Codex methods review: `temp/entity_disambig_methods_20260520.md`
- Memo decision: `docs/DECISION_20260518_ws0_5_thales_alignment.md` §5.2-§5.3 (E-6)
