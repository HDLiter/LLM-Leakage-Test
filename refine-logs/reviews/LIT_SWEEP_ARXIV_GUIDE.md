# Literature Sweep — arXiv API + WebSearch Guide (for Codex)

**Date:** 2026-04-14
**Audience:** Fresh-persona Codex agent running R4 literature sweep sub-tasks
**Purpose:** Give Codex concrete, copy-pastable search recipes so it does NOT rely on training-data memory for state of the art. Training data for GPT is at least several months stale; the sweep exists precisely because memorized bibliographies missed MemGuard-Alpha.

---

## 1. Core rule — no memory-based citations without verification

Every citation you include in your output must have been **verified within this session** via one of:

1. A successful `arxiv.org/api/query` response matching the title and first author
2. A successful `web_search` result that returns a plausible arxiv / venue / publisher link
3. A file already present in `related papers/` (confirmed by reading `INDEX.md`)

If you cannot verify a paper this way, **do not cite it**. Flag it as "memory-only, not verified" and move on. A missing citation is recoverable; a hallucinated citation poisons the sweep.

---

## 2. arXiv API — endpoint and syntax

**Endpoint:** `http://export.arxiv.org/api/query`

**Response format:** Atom 1.0 XML. Each `<entry>` has `<id>`, `<title>`, `<summary>`, `<author><name>`, `<published>`, `<updated>`, `<primary_category term="...">`, `<link rel="alternate" href="...abs/..." />`, `<link title="pdf" href="...pdf/..." />`.

**Key query parameters:**

| Param | Purpose | Example |
|---|---|---|
| `search_query` | Main query. Fields: `ti:` (title), `au:` (author), `abs:` (abstract), `all:` (everything), `cat:` (arXiv category). Combine with `AND`/`OR`/`ANDNOT` and parentheses. | `search_query=all:"memorization"+AND+all:"financial"` |
| `sortBy` | `submittedDate`, `lastUpdatedDate`, `relevance` | `sortBy=submittedDate` |
| `sortOrder` | `ascending` / `descending` | `sortOrder=descending` |
| `start` | Offset for pagination | `start=0` |
| `max_results` | Up to 2000 per request; use 50-100 for sweeps | `max_results=50` |

**Date filtering:** arXiv's API does NOT support a native `submittedDate:[A TO B]` range query the way their web UI does. Workaround: `sortBy=submittedDate&sortOrder=descending` and then filter in-memory by `<published>` timestamps, OR use the web search UI via web_search.

**URL encoding:** replace spaces with `+`, quote phrases with `%22`. Example with phrase:

```
http://export.arxiv.org/api/query?search_query=all:%22look-ahead+bias%22+AND+all:%22LLM%22&sortBy=submittedDate&sortOrder=descending&max_results=30
```

**Rate limit:** arXiv asks for **no more than 1 request every 3 seconds**, and large batches should be spread out. Do not hammer the endpoint.

**Common arXiv categories relevant to this sweep:**
- `cs.CL` — NLP
- `cs.LG` — machine learning
- `cs.CR` — crypto & security (for privacy/extraction attacks)
- `q-fin.GN` / `q-fin.ST` / `q-fin.TR` — finance
- `stat.ML` — stats

---

## 3. Recommended query patterns per sub-task

### Sub-task A (per-factor provenance)

Cast **one arXiv query + one web_search query per factor**, not one query for everything. Factor-specific verification beats broad queries.

**Propagation Intensity / repetition-recall family:**
```
search_query=all:%22frequency%22+AND+all:%22memorization%22+AND+cat:cs.CL
search_query=all:%22duplication%22+AND+all:%22language+model%22+AND+all:%22memorization%22
search_query=au:%22Kandpal%22+AND+all:%22duplication%22
```
web_search: `"deduplication memorization LLM 2024 2025"`, `"counterfactual memorization frequency"`.

**Cutoff Exposure / temporal:**
```
search_query=all:%22knowledge+cutoff%22+AND+all:%22LLM%22
search_query=all:%22chronologically+consistent%22
search_query=all:%22lookahead+bias%22+AND+cat:q-fin.GN
```
web_search: `"ChronoBERT ChronoGPT He 2025"`, `"DatedGPT Yan 2026"`, `"Time Machine GPT Bendemra"`.

**Anchor Strength / event anchorability:**
```
search_query=all:%22episodic%22+AND+all:%22language+model%22
search_query=all:%22event+anchoring%22+AND+cat:cs.CL
search_query=au:%22Gurnee%22+AND+all:%22time%22
```
web_search: `"episodic memory LLM benchmark Huet 2025"`, `"event-level memorization rubric"`.

**Entity Salience / distraction effect:**
```
search_query=all:%22entity%22+AND+all:%22memorization%22+AND+cat:cs.CL
search_query=au:%22Glasserman%22+AND+all:%22look-ahead%22
search_query=all:%22distraction+effect%22+AND+all:%22LLM%22
```
web_search: `"entity-level memorization Zhou 2023"`, `"target entity salience LLM finance"`.

**Template / surface reuse:**
```
search_query=all:%22template%22+AND+all:%22memorization%22
search_query=all:%22n-gram+overlap%22+AND+all:%22memorization%22
```
web_search: `"surface form memorization template 2024"`.

**Tradability / market-cap prominence (extra-corpus):**
```
search_query=all:%22market+capitalization%22+AND+all:%22LLM%22+AND+all:%22forecast%22
search_query=all:%22liquidity%22+AND+all:%22LLM%22
```
web_search: `"tradability LLM memorization", "firm size news coverage LLM"`.

**Session Timing / announcement timing:**
```
search_query=all:%22announcement+timing%22+AND+all:%22language+model%22
search_query=au:%22DellaVigna%22+AND+all:%22Friday%22  # for the original finance precedent
```
web_search: `"trading hours LLM memorization", "pre-market announcement LLM"` (likely null; confirm).

**Event Phase / rumor-official lifecycle:**
```
search_query=all:%22rumor%22+AND+all:%22financial%22+AND+all:%22LLM%22
search_query=all:%22news+lifecycle%22+AND+all:%22memorization%22
```
web_search: `"event phase classification financial news LLM"`.

**Disclosure Regime / source provenance:**
```
search_query=all:%22disclosure%22+AND+all:%22LLM%22+AND+all:%22memorization%22
search_query=all:%22source+provenance%22+AND+all:%22contamination%22
```
web_search: likely null; confirm.

**Modality (Thales 7-enum):**
```
search_query=all:%22news+type%22+AND+all:%22memorization%22
search_query=all:%22modality%22+AND+all:%22financial+NLP%22
```
web_search: `"news register memorization LLM"`.

**Authority (Thales 8-enum):**
```
search_query=all:%22source+credibility%22+AND+all:%22LLM%22
search_query=all:%22publisher%22+AND+all:%22contamination%22
```

### Sub-task B (broad 2024-2026 sweep)

The 8 kickoff queries, translated:

1. **LLM memorization + financial + benchmark:**
   ```
   search_query=(all:%22memorization%22+OR+all:%22leakage%22)+AND+all:%22financial%22+AND+all:%22benchmark%22
   ```
2. **LLM contamination detection + financial forecasting:**
   ```
   search_query=all:%22contamination%22+AND+all:%22financial+forecasting%22
   ```
3. **Factor-controlled benchmark + memorization:**
   ```
   search_query=all:%22controlled+benchmark%22+AND+all:%22memorization%22
   ```
4. **Chinese financial NLP + memorization:**
   ```
   search_query=all:%22Chinese%22+AND+all:%22financial%22+AND+all:%22LLM%22+AND+all:%22memorization%22
   ```
5. **Cross-model memorization (MemGuard-Alpha follow-ups):**
   ```
   search_query=all:%22cross-model%22+AND+all:%22memorization%22
   search_query=all:%22CMMD%22
   ```
6. **Look-ahead bias + LLM (2024-2026):**
   ```
   search_query=all:%22lookahead+bias%22+AND+all:%22LLM%22
   ```
7. **Temporal contamination + LLM + benchmark:**
   ```
   search_query=all:%22temporal+contamination%22+AND+all:%22LLM%22
   ```
8. **Pretraining data detection + finance:**
   ```
   search_query=all:%22pretraining+data+detection%22+AND+all:%22finance%22
   ```

For each query, sort by submittedDate descending, pull the top 30-50 results, read titles + abstracts, flag hits from 2024-01 onward. Cross-check each high-priority hit with a web_search to see if there is a venue-published version beyond the arXiv preprint.

### Sub-task C (chronologically-controlled baselines)

For each of {DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT, PiT-Inference, Bendemra 2024 Frontier Models, FINSABER KDD 2026}:

1. arXiv author search: `au:"Yan"+AND+all:"DatedGPT"`, `au:"He"+AND+all:"ChronoBERT"`, etc.
2. web_search: `"{model name} huggingface"`, `"{model name} github"`, `"{model name} chinese"`, `"{model name} model card"`.
3. HuggingFace hub search: `web_search("{model name} site:huggingface.co")` to find model cards.
4. GitHub search: `web_search("{model name} site:github.com")` to find release code.

Record the 8-point verdict (downloadable? family name? tokenizer? Chinese capability? benchmark perf on Chinese? compute cost? cutoff grid matches CLS timeline? CMMD fleet verdict?) even if some fields are null.

---

## 4. Cross-checking with Google Scholar / Semantic Scholar via web_search

arXiv only covers preprints. Venue-published-only papers (IEEE, ACM, Springer) do NOT appear in arXiv. Use web_search for venue-only work:

- `web_search("KDD 2026 FINSABER")`
- `web_search("EMNLP 2024 memorization financial")`
- `web_search("ACL 2025 contamination detection benchmark")`
- `web_search("NeurIPS 2025 memorization benchmark")`

For Semantic Scholar queries, you can use their API directly:
`https://api.semanticscholar.org/graph/v1/paper/search?query={terms}&limit=20&fields=title,year,authors,abstract,venue,citationCount,externalIds`

This gives citation counts + venue metadata that arXiv doesn't have. Use it when you need to judge whether a paper is reviewer-killer prior art (high citations = high visibility).

---

## 5. What to do with hits

For **every** hit you classify as "relevant" (priority P0/P1/P2):

1. Record: `{title, first_author, year, arxiv_id, venue (if any), one-line summary, why relevant, priority}`
2. If P0 (direct prior art or reviewer killer): **flag immediately in your Codex response** as a separate section at the top — "URGENT: possible direct prior art found — user action recommended before sweep continues."
3. If priority ≥ P1: add to the PDF-download candidate list in your output. Do NOT download the PDF yourself; the orchestrator will batch approval with the user.
4. If P2 or below: list in the output but no download recommendation.

**Priority rubric:**
- **P0** — Direct prior art (same problem, same domain, same method family). Reviewer would say "this is derivative of X." Surface immediately.
- **P1** — Strong methodological precedent or adjacent benchmark. Should be cited in the paper, probably read before R5.
- **P2** — Background reference. Worth noting, not urgent.
- **P3** — Tangential, skip.

---

## 6. Language handling

The project is Chinese financial NLP. Some relevant prior art may be in Chinese and not indexed in arXiv. Use web_search with Chinese queries where appropriate:

- `web_search("中文金融 大语言模型 记忆")`
- `web_search("金融新闻 LLM 数据污染")`
- `web_search("中文 contamination benchmark")`

Also consider searching CNKI (`zhihu.com` is low-signal; `scholar.cnki.net` is higher-signal but not directly accessible — use web_search to surface entries).

---

## 7. Output discipline

- Every claim about "who published what" must cite a URL or arxiv_id verified this session.
- Do not paraphrase paper abstracts as if they were your own findings; attribute explicitly.
- If a query returns nothing relevant, say so explicitly — "no arxiv hits under query X, 2024-2026 range, after sort." Null results are informative.
- Keep your output structured in Markdown so the orchestrator can merge it directly into `docs/FACTOR_LITERATURE_PROVENANCE.md` and `docs/LITERATURE_SWEEP_2026_04.md` without reformatting.

---

## 8. Hard reminders

- **Do not rely on memory.** If you "remember" a paper from training, verify it in-session or flag it as unverified.
- **Do not download PDFs.** The orchestrator handles downloads after user approval.
- **Do not propose factor additions or removals** in the sweep output — those belong in a separate "candidate new factor queue" section (if relevant) that the user will decide on later.
- **Surface MemGuard-Alpha-tier surprises immediately** at the top of your response, not buried in a factor table.
