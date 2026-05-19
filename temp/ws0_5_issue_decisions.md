# WS0.5 v0.1 → v0.2 — Round-0 Issue Decision Log

**Purpose**: companion document for Codex round-1 reviewers. Records what Codex round-0 found, what user-Claude interactive review decided, and why. Reviewers consult this to verify v0.2 actually addresses round-0 issues.

**Round-0 verdict**: `MAJOR-REVISIONS-NEEDED` (4 blockers + 4 majors + 1 minor)
**Round-0 review file**: `temp/ws0_5_alignment_review.md`

---

## Issue #1 — Topic taxonomy 10→13 class V3 (BLOCKER)

**Round-0 finding**: v0.1 §2.1/§3.1 claimed Thales V6 10-class enum. Actual production `_annotation.py` is V3 13-class (POLICY/ENFORCEMENT/LEGAL/INDICATOR/EARNINGS/CORPORATE/PRODUCT/PERSONNEL/TRADING/OWNERSHIP/INDUSTRY/GEOPOLITICS/OTHER). The 0.738 metric belongs to retired V6.

**v0.2 response**:
- Corrected factual claim in §2.1 + frontmatter
- Adopted **Scheme A 5-super-type collapse** (Codex sub-analysis `temp/ws0_5_supertype_analysis.md`):
  - `authority_decision` [POLICY+ENFORCEMENT+LEGAL+GEOPOLITICS] → host `policy`
  - `issuer_catalyst` [CORPORATE+PRODUCT+PERSONNEL] → host `corporate`
  - `issuer_quant` [EARNINGS+OWNERSHIP] → host `corporate`
  - `market_macro_print` [INDICATOR+TRADING] → host `macro`
  - `sector_industry` [INDUSTRY] → host `industry`
  - `OTHER` → `exclude_from_pilot=true` with reason `other_nonfinancial_no_r5a_target`
- Scheme B 4-super-type bridge specified as fallback trigger if `sector_industry`/`issuer_quant` < 12 verified+slotable
- Prompt strategy: keep 13-class output + mechanical collapse (preserves diagnostic granularity for downstream T2 recurrence and C_FO sub-rule design)

**User-Claude rationale**:
- Outcome-type homogeneity (Codex's framing) beats domain-family grouping for C_FO slot schema coherence
- `issuer_quant` (numeric filings) vs `issuer_catalyst` (event predicates) are different C_FO design objects, hence split
- `market_macro_print` joins INDICATOR + TRADING because both are "public numeric prints"
- 13→5 collapse mechanical, no LLM error introduced at collapse step
- OTHER excluded at sampling (Codex confirmed 4% natural rate; weather/COVID/science items lack financial target)

---

## Issue #2 — Target Salience construct rule (BLOCKER)

**Round-0 finding**: v0.1 implied Thales `salience=core` directly answers Target Salience. Actually `core` is just candidate-target signal; R5A Target Salience is ordinal case-level, needs target-selection + nullability + ordinal binning + validation rules.

**v0.2 response** (§3.3, building on Codex sub-analysis `temp/ws0_5_target_salience_construct.md`):

**Selection rule** (centrality-first within tradable types — user override of Codex class-first):
1. Candidate pool = `salience=core` entities with type ∈ {company, sector, index, ETF, commodity}
2. Drop source-only, person-only, one-char region aliases
3. If pool empty → case REJECTED at sampling (not retained with macro target)
4. Among pool: rank by `(in_headline, is_core, -first_offset, mention_count, alias_length)`

**Ordinal scoring** (3-level, Codex's `context_gate × static_reach` formula):
- `context_gate ∈ {0,1,2}`: text-side veto (target presence in headline + core)
- `static_reach ∈ {1,2,3}`: market-metadata-side main signal (CSI300/top-cap vs ordinary listed vs niche/local)
- `ordinal = 1 if gate==0; 3 if reach==3 & gate≥1; 2 if reach==2 & gate≥1; else 1`

**Non-redundancy**: no historical CLS mention count / no event_type / no month in Target Salience (those belong to Recurrence). Pre-manifest Spearman discriminant check `|ρ|<0.50` with Recurrence required.

**User-Claude rationale**:
- Centrality-first (article-faithful) over class-first (forecastable-target-first) → cleaner construct
- Macro/policy P_predict task is semantically broken ("price direction for 央行"), so exclude macro target cases entirely
- Single `static_reach` axis absorbs Tradability Tier + Target Scope without re-adding them as confirmatory
- Subdivision of class 1 vs class 2 deferred — pilot will surface if it matters
- Market metadata snapshot built by user (not Thales quant engine), spec'd in v0.2, implemented S1

---

## Issue #3 — Auto-tune validation discipline (BLOCKER)

**Round-0 finding**: v0.1 §4 used same 20% holdout for repeated patch selection across 20+ rounds with bootstrap-CI-non-overlap gate. Three statistical errors:
1. Bootstrap CI non-overlap test is WRONG for paired data (both prompts scored on same examples)
2. K-rotation alone doesn't fix adaptive holdout reuse — acceptance gate still leaks score info to LLM proposers each round
3. No alpha spending across 20 rounds × 2 patches = 40 tests at α=0.05 → ~2 false positives expected

**v0.2 response** (§4 full rewrite, building on Codex SOTA search `temp/ws0_5_autotune_sota_search.md`):

**Adopted Scheme Y — Hybrid Current Loop + Limited-Exposure Acceptance Gate + Active Fixture**:
- **4-layer fixture split** (3000 total): 60% train_visible / 20% inner_dev / 10% acceptance_holdout / 10% final_holdout
- **Final_holdout sealed from T0**, evaluated once at end
- **Acceptance gate Ladder-style**: returns ONLY pass/fail + rounded delta (0.01) to proposers, NOT exact score (Blum & Hardt 2015)
- **4 candidates per round** (not 2): Claude + Codex + ProTeGi-style + minimal-edit
- **Paired statistical tests** (Dror et al ACL 2018): McNemar exact (top-1 acc), paired bootstrap diff + paired permutation (F1)
- **Alpha spending**: total α=0.05 over max 30 acceptance looks pre-registered = Bonferroni 0.00167/look
- **Active fixture rotation**: K=5 rounds; recipe 40% stratified + 25% disagreement + 20% hotspot + 15% diversity
- **Pre-registration manifest** YAML committed before loop runs

**User-Claude rationale**:
- Codex pulled SOTA literature (DSPy/MIPRO/GEPA/TextGrad/ProTeGi/Dwork/Thresholdout/Ladder/Dror) and recommended Scheme Y over Scheme X (full DSPy) for risk-managed governance upgrade
- Scheme Y adopted straight (without GEPA/MIPRO candidate generator) for v0.2 simplicity; GEPA can be added v0.3 if needed
- 4 candidates (drop OPRO) because Claude/Codex are already free-form LLM proposers; add ProTeGi-style for data-diagnostic discipline + minimal-edit for baseline anti-mutation
- Fixture 3000 (not 80 or 1500) — budget abundant, 4-layer split with 300/300 holdouts has CI ±4-5%

---

## Issue #4 — Determinism: replay-from-cache + provenance (BLOCKER)

**Round-0 finding**: v0.1 §6 claimed `pilot_factor_values.parquet` is "deterministic given frozen prompts". Wrong for closed-API LLMs — V4 Pro can drift across calls (model snapshot updates, hidden defaults, retry paths). WS4 manifest freeze becomes non-reproducible.

**v0.2 response** (§6 new section):
- **Determinism redefined as replay-from-cache**:
  - All raw V4 Pro responses saved to `data/factors/raw_llm_responses/<task>/<id>.json` with full provenance (prompt sent, response text, response_id, model_snapshot, decoding params, timestamp)
  - `factor_provenance.json` records per-cell SHA chain: prompt_sha + parser_version + collapse_map_sha + source_raw_response_uri
  - `scripts/replay_factor_values.py` reconstructs parquet from raw cache + frozen code (no API calls)
- **Storage**: ~12000 JSONs × 3KB ≈ 35-60MB tracked via **Git LFS** (`.gitattributes`)

**User-Claude rationale**:
- Phase 1 (Issue #3 prompt tuning) writes tuning_logs only; raw responses written ONLY at Phase 2 (pilot factor inference) where reproducibility matters most
- Phase 3 (replay) is pure code, bit-identical output guaranteed if raw cache + code SHAs unchanged
- Seed support detection (V4 Pro may not honor seed) deferred to S1 smoke; not blocking since cache-replay sidesteps seed determinism altogether

---

## Issue #5 — Closure quota gates (§6.3/§6.4) (MAJOR)

**Round-0 finding**: v0.1 §6 closure misses plan §6.3 (4-host quota, 5-super-type quota, factor binary split quotas, C_FO funnel, C_NoOp host coverage, post-cutoff mix) and §6.4 (n_eff matrix per estimand). Without these as closure conditions, WS4 sampling has no schema to consume.

**v0.2 response** (§5 §9 expanded):
- Closure conditions expanded 6 → 11 items including:
  - #7: `config/factors/factor_schema.yaml` — frozen factor names, dtypes, binning rules, collapse maps, target selection params, eligibility fields
  - #8: `data/factors/ws0_5_quota_report.json` — full §6.3 quota check + §6.4 n_eff matrix
  - #9: `scripts/check_pilot_cells.py` — WS0.5 stub (function signature + IO schema + pseudocode in docstring); WS4 full implementation
- factor_schema.yaml documents Scheme A collapse, Target Salience scoring rule, Recurrence binarization, all dtype/value-set conventions

**User-Claude rationale**:
- Stub-vs-full-implementation split: WS0.5 owns spec, WS4 owns implementation. Responsibility clean.
- Plan §14.4 sign-off explicitly references "factor schema frozen (exact file path set by that session)" → memo names it `factor_schema.yaml`

---

## Issue #6 — Signal profile: v5.5 two-pass not V2 single-pass (MAJOR)

**Round-0 finding**: v0.1 §2.3/§3.3 cited `NewsSignalProfilePrompt v3.0.0` (single-pass V2 with modality 0.815 / authority 0.76 on deepseek-chat). Actual production is **v5.5 two-pass** (`NewsSignalProfileModalityPrompt` + `NewsSignalProfileAuthorityPrompt` conditioned on predicted modality).

**v0.2 response** (§2.3 + §3.4):
- Factual correction with full deepseek-chat architecture comparison table (Combined V2 81.5/76 vs Split-Independent 79.5/72.5 vs Split-Conditioned 80.5/79)
- **Decision deferred to Stage 1 smoke comparison**: on 100-case stratified subset, run both V2 combined and v5.5 two-pass × 1 V4 Pro round
- **Decision rule**: if `modality_acc_A ≥ modality_acc_B − 0.02` → V2 combined; else v5.5 two-pass
- Authority not in decision rule (non-confirmatory per Issue #9)

**User-Claude rationale**:
- Thales chose v5.5 for global optimum across SLM+LLM; V4 Pro (stronger than deepseek-chat) may favor single-pass even more on modality
- Empirical comparison on V4 Pro is cheap (~$0.5) and avoids guessing
- Modality is confirmatory factor → optimize for it; authority is covariate → report only

---

## Issue #7 — Historical Family Recurrence data contract (MAJOR)

**Round-0 finding**: v0.1 mentioned "(entity, event_type, date_window) frequency" without specifying: window length, entity normalization, dedup policy, lookback strictness, CLS mirror provenance.

**v0.2 response** (§5 new section):
- **Window**: 24 months strict lookback `[T-24mo, T)` (single fixed, not per-event-type)
- **Primary binarization**: within-super_type percentile ≥ 0.50 → high (provisional, Codex v0.2 review may re-evaluate)
- **Sensitivity**: absolute count >= median(80 pre-cutoff) stored as secondary
- **No deduplication** (user rationale: media repost density IS the training-exposure signal we want)
- **Reference labeling**: full CLS mirror topic-classified by frozen V4 Pro prompt (~$200-400)
- **Entity matching 3-step**:
  - Step A: V4 Pro alias generation per pilot target (with ambiguity_risk tag)
  - Step B: rule-based candidate filter (article.salient_entities[].value ∩ alias_set)
  - Step C: V4 Pro confirmation ONLY for high-ambiguity-risk alias matches (cached)
- **Ancillary prompts** (alias gen + confirm): pre-specified + smoke-validated (≥95% precision); escalate to mini auto-tune if smoke fails
- **CLS mirror**: local `data/cls_telegraph_raw/` (2317 files, 939MB), SHA256-locked in factor_provenance.json

**User-Claude rationale**:
- Fixed window because LLM training has unified cutoff, not per-event-type horizons — user's clean argument
- Within-super_type percentile decorrelates from super_type factor + Target Salience (non-redundancy)
- No-dedup: high recurrence IN CLS = high media coverage density = high training exposure proxy. Removing duplicates would lose this signal.
- Local CLS mirror (not Thales source) — pre-existing isolation from 2026-05-03 per project memory

---

## Issue #8 — Budget cap → token accounting (MAJOR)

**Round-0 finding**: v0.1 "$5/factor cap" is wrong because V4 Pro pricing is time-limited (75% discount expires 2026-05-31 15:59 UTC), fixture refresh labeling cost not included, and tokens are a more stable unit than USD.

**v0.2 response** (§7 new section):
- **Live LedgerEntry** per API call: tokens_in, tokens_out, rate at call time, USD at call time, model_snapshot, prompt_sha
- **Pricing pin**: fetched at run start, snapshot in ledger header
- **Pre-registered estimates** in autotune_manifest.yaml per phase (auto_tune_loop, pilot_inference, reference_window, step_C_disambig)
- **Safety rails** (not hard budget):
  - soft = 2× expected_USD → emit warning + concurrency throttle
  - hard = 5× expected_USD → halt + require user resume
- `scripts/budget_summary.py` → markdown aggregate report

**User-Claude rationale**:
- User has abundant budget (x20 plan unused); soft/hard rails are bug-protection not budget-enforcement
- 2× / 5× chosen per user (could be tighter; chose moderate sensitivity)
- Pricing snapshot needed for paper methods section reproducibility report

---

## Issue #9 — Authority Bloc 3 status (MINOR)

**Round-0 finding**: v0.1 treated Authority as a Bloc 3 factor, but `R5A_FROZEN_SHORTLIST.md §8` baseline Bloc 3 inventory does NOT list it. Plan §5.1A asks T3 about Authority but doesn't elevate it to confirmatory.

**v0.2 response** (§2.3, §3.4, §9):
- Authority status: "candidate Bloc 3 adjunct/covariate" — NOT one of 4 confirmatory factors, NOT in Bloc 3 interaction menu
- Auto-tune gate: ONLY on modality; authority metric reported but not gated
- **Opportunistic Authority tuning**: after modality auto-tune converges, IF session time permits, short authority-only auto-tune; otherwise ship as-is
- P1 explicitly NOT restored (text-inferred Authority remains CLS-internal regardless of which architecture wins)

**User-Claude rationale**:
- Codex's exact patch text adopted with priority calibration ("modality first, authority secondary")
- KG-lookup / Wikipedia / publisher-metadata genuine extra-corpus Authority deferred to P1-expansion track (separate decision memo, separate session)

---

## Other notable decisions (not in 9 issues but recorded)

- **Fixture size 3000** per Issue #3 user choice; budget tolerant
- **Auto-tune candidate count = 4** (Claude/Codex/ProTeGi/minimal); OPRO dropped (redundant with Claude)
- **Class 1 vs class 2 in Target Salience NOT subdivided in v0.2**; deferred to pilot review or Codex v0.2 review
- **Codex SOTA report references** (~21 papers) to be batch-fetched to `related papers/` + PAPER_INDEX.md updated as Issue #11 follow-up
