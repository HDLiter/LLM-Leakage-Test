# Text Template-ness / Boilerplate Measurement — direction note

> Collected for R-1d Template Rigidity factor design (2026-06-02).
> Full Codex scan: `temp/lit_scan_template_measurement_20260602.md`.

## Why this cluster matters

R-1d Template Rigidity needs an operationalization for "how templated is a CLS
news article." No prior work measures template rigidity for Chinese financial
news specifically. These papers provide the methodological building blocks.

## Key methods (by relevance to R-1d)

### 1. Tetragram boilerplate share (Lang & Stice-Lawrence 2015)
**Most directly relevant.** Identifies 4-word phrases appearing in many 10-K
filings, scores each document by the share of its content in
boilerplate-tetragram sentences. Our R-1d method (corpus high-frequency n-gram
coverage) is adapted from this — main differences: Chinese CLS corpus (not
English 10-K), jieba word segmentation (not English whitespace), Top-K%
average DF aggregation (not binary sentence-level coverage), heterogeneous
corpus (not single document type). Dyer et al. 2017 is the longitudinal
follow-up.

### 2. N-novelty / Rusty-DAWG (Meister et al. 2024)
Measures the complement: share of document n-grams ABSENT from reference
corpus. Our rigidity ≈ 1 − n-novelty. Uses suffix-array/DAWG data structures
for scalable exact matching against massive corpora. Could be an alternative
implementation path if n-gram index approach hits scale issues with CLS.

### 3. Hapaxity / formulaicity indices (Forsyth & Grabowski 2015)
Battery of indices measuring how much text relies on fixed (inflexible)
subsequences. Hapaxity = proportion of phrase-frames that appear only once
(hapax legomena) — low Hapaxity = more formulaic. Could be used as a
robustness alternative to our DF-based measure. Applied to registers/academic
text, not financial news.

### 4. Web boilerplate detection (Web2Text, BoilerNet)
Neural methods for labeling HTML blocks as boilerplate vs content. Not directly
applicable (CLS telegrams are plain text, not HTML), but the concept of
"boilerplate token ratio" at the document level is analogous to our metric.

## Chinese financial news gap

DCFEE, TDJEE, DocFEE and other Chinese financial NLP papers use predefined
event templates for **extraction**, not for measuring template-ness. No paper
found that quantifies how formulaic Chinese financial news articles are. Our
R-1d fills this gap.

## Connections to other clusters

- **Memorization & extraction**: Carlini duplication→memorization finding is
  the theoretical bridge (structural near-neighbors → more memorization), but
  the leap to template-level similarity as a modulation factor is untested.
- **RAVEN** (already in library): measures text generation novelty relative to
  training data — related but measures model output novelty, not input
  template-ness.
- **Deduplicating Training Data** (already in library): shows near-duplicate
  removal affects model quality — supports that template structure matters for
  model behavior, but studies data curation not per-example factors.
