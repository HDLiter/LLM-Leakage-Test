# Repo Cleanup Plan for Public Release

**Status:** Draft checklist — NOT to be executed yet
**Trigger:** Only begin cleanup after (1) FinMem-Bench proposal finalized via
multi-agent review, (2) benchmark spec frozen, (3) experiment plan written,
(4) experiments run, (5) paper draft complete.
**Purpose:** Strip exploration artifacts before releasing FinMem-Bench repo
**Principle:** Preserve research traceability in git history; present a clean
surface to users of the published benchmark

> **Important for current work:** Until cleanup is executed, all exploration
> artifacts (refine-logs, debate notes, bug audits, pilot notebooks,
> intermediate scripts, superseded proposals) remain in `main` for agents to
> reference. They carry significant context about *why* current design
> choices were made and *what* has already been tried. Removing them
> prematurely would force future agents to re-derive these decisions from
> scratch.
>
> This document is a **record of cleanup intent**, not a work order.

---

## Strategy

Two-track approach:

1. **`main` branch** — kept minimal and user-facing (benchmark + core code +
   reproduction skills). This is what users see on GitHub after release.
2. **`research-history` branch** — preserves the full exploration record
   (refine-logs, debate notes, intermediate notebooks, superseded scripts,
   bug audits, review rounds). Tagged and permanently archived.

This way the research trail is not destroyed — it's just not the default
view. Anyone who wants to see "how the sausage was made" checks out the
history branch.

---

## Release Branch Contents (what `main` keeps)

### Keep as-is
- `src/` — core modules (llm_client, pilot, metrics, prompt_loader, models, masking, news_loader)
- `config/` — frozen prompts, settings files
- `tests/` — passes on release
- `requirements.txt`
- `.gitignore`
- `LICENSE` (to be added)
- `README.md` (to be rewritten for public release)

### Keep but rewrite for public audience
- `README.md` — current one is internal; needs user-facing benchmark documentation
- `CLAUDE.md` → may move to `.claude/` or delete (internal guidance, not user docs)
- `AGENTS.md` → delete or move to research-history branch

### Promote / new additions
- `docs/BENCHMARK_SPEC.md` — frozen spec (from next session)
- `docs/REPRODUCTION.md` — how to reproduce results using the skills
- `.claude/skills/annotate-benchmark/` — skill for local annotation
- `.claude/skills/run-memorization-probe/` — skill for running probes
- `scripts/build_benchmark.py` — benchmark construction pipeline (new)
- `scripts/run_experiments.py` — experiment runner (consolidated from existing)

### Consolidate
Current `scripts/` has 30+ files, many are one-off audits or intermediate steps.
Proposed cleanup:

| Keep | Move to research-history | Delete |
|---|---|---|
| `run_diagnostic_2.py` → rename `run_experiments.py` | `run_diagnostic_1.py` | `_audit_bug*.py` |
| `build_frequency_index.py` | `analyze_diagnostics.py` | `_inspect_results.py` |
| `compute_frequency.py` | `analyze_cf_invariance.py` | `_verify_smoke.py` |
| `generate_anchor_analysis.py` | `annotate_v2_batch_*.py` (4 files) | `_verify_phase_d.py` |
| `annotate_reversibility.py` | `annotate_v3_batch.py` | `_cpt_mode_crosstab.py` |
| `sensitivity_analysis.py` | `sample_cls_*.py` (3 versions) | `quick_stats.py` |
| | `check_strata.py` | `rescore_fo_flip.py` |
| | `show_pilot_*.py` | `_audit_*.py` |
| | `paper_library.py`, `build_paper_notes.py` | |

Rule of thumb: scripts starting with `_` (internal audits), `show_*`
(debug printing), and `annotate_v{2,3}_batch_*` (one-off annotation runs)
go to history branch. The `sample_cls_v{1,2,3}.py` cascade shows iteration
history that only matters to reviewers of the research process.

---

## Research History Branch (`research-history`)

Preserves everything that shouldn't be on the user-facing `main` but is
valuable for research traceability:

### Full content to move
- `archive/pilot_phase/` — original notebooks (NB00-06), benchmark scripts,
  README_original.md
- `refine-logs/` — all debate/review/brainstorm logs from v1 proposal
  through amber gates
- `docs/REVIEW_amber_*.md` (6 files) — gate review records
- `docs/BUG_AUDIT_amber.md` — bug audit
- `docs/PROPOSAL_BRAINSTORM.md`, `docs/ROADMAP.md`, `docs/LANDSCAPE.md`,
  `docs/RESEARCH_PROPOSAL.md`, `docs/RESEARCH_PROPOSAL_v2.md` — proposal
  iterations
- `docs/FIRTH_DECISION.md`, `docs/ANCHOR_RUBRIC.md`, `docs/DECISION_*.md` —
  methodological decision records
- `plans/` — amber-mirror-lattice, deep-floating-lake, phase5 plans
- `AUTO_REVIEW.md`, `REVIEW_STATE.json`, `PAPER_INDEX.md` — internal trackers
- `data/seed/v3_annotation_*` — annotation provenance
- `data/seed/annotated_batch_*`, `v2_batch_*`, `v2_annotated_*` — intermediate
  annotation batches

### Document index for history branch
Keep `docs/TIMELINE.md` in both branches — it's the map to everything in the
history branch.

---

## Data Files Decision Matrix

| File | Main | History | Notes |
|---|---|---|---|
| `data/seed/test_cases_v3.json` (pilot 606) | no | yes | Pilot-phase data, superseded by FinMem-Bench |
| `data/seed/test_cases.json` | no | yes | Original 42 seed cases |
| `data/seed/test_cases_expanded.json` | no | yes | 192-case diagnostic |
| `data/seed/memorization_probes.json` | no | yes | Phase 0 probes |
| `data/seed/anchor_analysis.json` + related | no | yes | Superseded by v3 rubric |
| `data/seed/frequency_analysis*.json` | no | yes | Pilot-phase frequency |
| `data/cpt/` (when built) | yes (metadata only) | yes (full) | See licensing section below |
| `data/results/` | no | yes (selected) | Regenerable, not in git anyway |
| `data/cache/` | no | no | In .gitignore |

## Benchmark Release Content (new `benchmark/` top-level dir)

```
benchmark/
  README.md                    # user-facing benchmark doc
  LICENSE                      # benchmark license (MIT for annotations, see CLS licensing)
  chinese/
    metadata.jsonl             # case_id, date, target, factors, outcome, SR/FO texts, fingerprint
    annotations.jsonl          # task labels, anchor, frequency, direction
    masked_variants/           # pre-generated entity/year-masked versions
    reconstruct.py             # match fingerprints against user's own CLS copy
  english/
    cases.jsonl                # full-text (SEC EDGAR public domain)
    annotations.jsonl
    masked_variants/
  extended_corpus/             # optional 10K-50K for training-based methods
    ...
```

---

## Notebooks Directory

Current `notebooks/` does not exist in `main`. Early exploration notebooks
(NB00-06) are in `archive/pilot_phase/notebooks/`. Decision:
- Do NOT create new notebooks for release (scripts + skills are enough)
- Early notebooks stay in history branch only
- Consider adding 1-2 "tutorial notebooks" for benchmark users (post-release
  decision)

---

## Sensitive Content Audit (before release)

- [ ] Search for API keys in scripts, docs, commits
- [ ] Check `.env` not tracked (already in `.gitignore`)
- [ ] Review commit messages for internal jargon / personal details
- [ ] Verify no CLS full-text in committed `data/seed/*.json`
- [ ] Check no proprietary model outputs in `data/results/`
- [ ] Remove any localized paths (`D:/GitRepos/...`) from docs
- [ ] Sanitize `related papers/` — probably move entirely to history branch
  (local PDF copies, may have copyright concerns)

---

## Execution Order (when the time comes)

1. **Freeze research state** — tag current state as `v0-research-history`
2. **Create `research-history` branch** from the tag
3. **On `main`:** selective `git rm` of exploration artifacts (multi-commit,
   grouped logically)
4. **Add new release content** — benchmark/, skills/, new README, LICENSE
5. **Sanitize** — run sensitive content audit, fix any findings
6. **Internal smoke test** — someone unfamiliar tries to use the benchmark
   from scratch with only `main` content
7. **Public push** to release repo

---

## What to decide later (not now)

- License choice (MIT / Apache 2.0 / CC-BY for data vs code)
- Whether to release the `research-history` branch publicly, or keep it
  internal and only reference it in the paper's Methods
- Whether CLS full-text can be included (depends on licensing outcome)
- Versioning scheme for benchmark updates (SemVer? date-based?)
- Citation format / BibTeX entry

---

## Not in scope for this cleanup

- Code refactoring / style cleanup — the code works, don't risk breaking it
- Renaming variables or files in `src/` — stability > aesthetics
- Consolidating the `src/pilot.py` monolith — it's ugly but functional
- Rewriting test suite — current 3 tests are enough for release

---

*This is a checklist, not a work order. Execute after FinMem-Bench is built
and paper is accepted/camera-ready.*
