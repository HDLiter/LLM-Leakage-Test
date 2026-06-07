# Template Rigidity — subfield literature scan (audit trail)

> Codex-executed scan (2026-06-02). Question: has NLP / computational
> linguistics research measured "how templated a text is"? Honest report.

## Direct use as LLM behavior modulation factor

**~0 published work.** No paper found that uses text template rigidity /
boilerplate level as an independent variable to study LLM memorization, bias,
or behavioral outcomes.

## Adjacent work by approach type

### Financial disclosure boilerplate (most directly relevant)
- **Lang & Stice-Lawrence (2015)** + Dyer, Lang & Stice-Lawrence (2017):
  Operationalize 10-K annual report boilerplate with **tetragram share** —
  identify 4-word phrases appearing in many documents, score each document by
  share of words in sentences containing boilerplate tetragrams. Also use
  year-over-year stickiness, redundancy, specificity. Corpus-relative; cheap
  at scale. Applied to English annual reports.
- **Chinese accounting study (2019, TandF)**: Measures Chinese annual report
  similarity via jieba segmentation + LSI/cosine for MD&A sections.
  Inter-document similarity, not per-document rigidity score.

### Formulaicity measurement
- **Forsyth & Grabowski (2015)**: Formulaicity indices including VPR,
  Herfindahl-Hirschman, Simpson diversity, Shannon entropy, and **Hapaxity**
  (reliance on inflexible subsequences). Corpus-relative; n-gram based.
  Applied to registers/academic corpora, not news/finance.
- **MERGE algorithm**: Recursively grows formulaic sequences from
  high-association bigrams. Corpus-relative.

### N-gram novelty / text reuse
- **RAVEN (TACL)**: Pointwise duplication scores for measuring how much LMs
  copy from training data. Corpus-relative.
- **Rusty-DAWG (2024)**: **n-novelty** = share of n-grams absent from
  reference corpus. Complement measure: 1 − n-novelty ≈ template-ness.
  Scalable with DAWG indexes.
- **Passim / text-reuse**: N-gram shingling + alignment; max shared-shingle
  ratio. Applied to newspaper corpora.

### Boilerplate detection (web)
- **Web2Text**: CNN+HMM over DOM features for boilerplate/content separation.
- **BoilerNet**: Neural sequence labeling over HTML tags/words.
- **Perplexity-based removal**: Remove high-perplexity sentences as
  boilerplate. Note: these detect boilerplate in web pages, not measure
  document-level template-ness.

### Chinese financial news template work
- DCFEE, TDJEE, DocFEE: Use predefined schemas for **event extraction**
  from Chinese financial news. They use templates as extraction tools,
  **not** to measure template rigidity. No Chinese financial news
  template-ness metric found.

## Key takeaway for our operationalization

Lang & Stice-Lawrence's tetragram approach is the closest methodological
precedent. Our adaptation: CLS corpus (not 10-K), Chinese word segmentation
(not English 4-grams), top-K% average DF (not binary coverage). The leap
from English annual reports to Chinese CLS telegrams is ours to make; no
prior work covers this exact setting.
