# Triage log — Tier-R2-0 implementation review

User: walking through findings one at a time. Triage principle: **gate-leak (bad data can land silently) > everything else; UX / docstring purity is secondary**.

| # | Finding | Lenses | Sev | Triage | Notes |
|---|---|---|---|---|---|
| 1 | `hidden_state_subset_hash=None` silent in confirmatory mode | A/C/D/F | HIGH novel | **B** | Add clause-9 to `_confirmatory_hard_fail`: confirmatory + `args.hidden_states_dir is None` → fail |
| 2 | clauses 5/6 helpers raise before collector | A/B/D/F | HIGH anchored | **D** | Accept current behavior; manifest-write gate holds. Update docstring to be honest. **Split off**: B-A1 test gap (collapsed integration test can't catch fail-fast regression) as separate follow-up |
| 3 | Path-E provenance (`trace_shas`, `probe_set_sha256`) detached from RunManifest | C/F (×2) | HIGH novel | **D** | Add `exposure_horizon_source_sha256: str` field to `RunManifest`, populate via `_sha256_file(args.exposure_horizon)`. Transitively binds analyzer JSON's internal `trace_shas` + `probe_set_sha256`. Plan C.10's separate pilot-trace-SHA still TODO |
| 4 | stale/malformed exposure-horizon JSON silently becomes "rejected horizon" | A | HIGH novel | **A** | Schema-strict parse in `_read_exposure_horizon`: `if "horizon_observed" not in row: raise SystemExit(...)`. Distinguish missing-key from null-value |
| 5 | pinner writes fleet before parsing existing pinning log | F | HIGH novel | **A** | Move `log_path.exists()` + `json.loads()` + `isinstance(prior, list)` checks above the `_atomic_write_text(out_path, yaml_text)` call so log corruption fails *before* fleet mutation |
| 6 | corrupted HF cache passes pinning (snapshot name + tokenizer.json not validated) | C | HIGH anchored | **D** | Originally: (a) snapshot.name 40-hex check + (b) tokenizer.json `json.loads()` validation. **After #7 D, (a) is redundant** (Pydantic validator on `hf_commit_sha` field catches it). Keep only (b) as content-validity check before SHA-256 |
| 7 | malformed pin SHA admissible end-to-end (override / discover / hand-edit) | B/C | HIGH novel | **D** | Pydantic field validators on `ModelConfig`: `hf_commit_sha: Annotated[str, Field(pattern=r"^[a-f0-9]{40}$")] \| None` + `tokenizer_sha: ... pattern=r"^[a-f0-9]{64}$"`. Catches at fleet YAML load time, all paths covered. **Side effect**: mock test fixtures with shorthand SHAs need to be updated to valid 40/64-hex strings |
| 8 | PENDING.md says compute git-blob-SHA (40-hex SHA-1) but code uses SHA-256 (64-hex content hash); also workflow obsolete (pinner auto-discovers) | E | HIGH novel | **B** | Split PENDING.md `WS1 — model/tokenizer/image provenance pinning` entry into two: (a) **WS1 white-box fleet pinning** → action: `ws1_pin_fleet.py --hf-cache <path>`, automated; (b) **WS1 black-box `api_model_name` resolution** → manual vendor-catalog lookup for `gpt-5.1` / `claude-sonnet-4.6`. Preserves WHAT (12 `<TBD>` items still pending) + corrects HOW. Gate-leak property already closed by #7 D's Pydantic validator |
| 9 | half-written / 0-byte / wrong-N / mix-batch pilot parquet passes finalization (only filename glob + roster check) | C | HIGH anchored | **E** | (a) row-count check via `pyarrow.parquet.read_metadata()` — no data read, cheap. Compare to expected n_articles from fleet, mismatch → SystemExit; (b) compute SHA-256 per parquet, add `RunManifest.pilot_trace_shas: dict[str, str]` field. Lands plan C.10 acceptance + dual to #3 D (Path-E source SHA). Schema validation (option C) skipped — row-count + SHA gives sufficient defense |
| 10 | `test_pin_fleet_validates_hash_invariant_and_idempotency` only asserts byte-equality across two runs; would pass even if pinner ignored `--pin-json` entirely | B | HIGH novel | **B** | Split into two tests: (a) `test_pin_fleet_replaces_tbd_with_override` — assert `<TBD>` removed, override SHAs landed, version bumped; (b) `test_pin_fleet_is_idempotent` — keep current byte-equality check on second run. Names match what each test verifies |
| 11 | `RunManifest` docstring describes schema in old `cutoff_observed` name (lines 390-413) with rename buried in R2-amendments paragraph (lines 425-428); reader / LLM agent encounters wrong identifier first | E | HIGH anchored | **B** | Full rewrite of `RunManifest` docstring to current-state form: drop timeline framing ("added 2026-04-29 / R2 amendments"), describe schema as it is now. Keep one-line history pointers (e.g., "see DECISIONS.md decision #5 for rename history") rather than full prose history. Rationale: docs serve as LLM-agent context; current-state framing prevents wrong-identifier code generation |

**11 HIGH triaged.**

## MED bucket — Cluster 1 (operational gate-leaks)

| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| MED-1 | `month_stratified_mink()` silently drops trace cases not in probe set; analyzer doesn't verify trace ⊆ probe coverage | C-N4 | **accept** | Add assert `set(trace_case_ids) - set(probe_case_ids) == set()` after filter in `run_exposure_horizon_analysis.py:174-186`, mismatch → SystemExit |
| MED-2 | confirmatory mode lacks hard-fail clause for missing/non-terminal `runstate_db` | C-N5 | **accept** | Add clause to `_confirmatory_hard_fail`: confirmatory + runstate missing or non-terminal → fail. Same shape as #1 B's hidden-state clause |
| MED-3 | finalizer manifest write uses non-atomic `Path.write_text()` while pinner has `_atomic_write_text` helper | C-A9 / F-Role3#1 | **accept** | Promote `_atomic_write_text` from pinner to shared util; finalizer imports + uses it |
| MED-4 | `HF_HUB_CACHE` silently falls through to next candidate when set but dir missing | C-A7 | **accept** | Env var explicitly set but dir absent → raise; only fall back when env var unset |
| MED-5 | pinning log claims `pinned_records` for models whose patch was SKIP'd due to existing-pin conflict | F-Role3#2 | **accept** | `pinned_records` only collects actually-changed records; SKIP'd entries go into a separate field or `changes` list only |

**Already closed by HIGH decisions** (no further action): MED-orig#12 (D-N2, by #2 D), #26 (A-A2 C.10, by #9 E), #27 (C-A3, by #4 A), #29 (=#25 atomic write, by MED-3), #30 (B-A1, split off in #2).

## MED bucket — Cluster 2 (test coverage gaps)

| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| MED-6 | `month_stratified_mink()` Min-K% scores not asserted; tests only check month-key/count | B-N3 | **accept** | Add numerical-anchor test: 4-row synthetic trace → expected Min-K% ≈ 0.xxx |
| MED-7 | analyzer→finalizer JSON contract has no e2e test (finalizer tests use hand-built fixture) | B-N4 | **accept** | E2E test: run analyzer on tiny fixture → feed JSON output to finalizer. Covers #3 D's `exposure_horizon_source_sha256` linkage |
| MED-8 | hidden-state validation has only happy-path synthetic fixture | B-N5 | **accept** | 3 negative tests: missing model dir, mismatched case set, wrong filename layout. + 1 confirmatory-without-`--hidden-states-dir` test (covers #1 B clause-9) |
| MED-9 | real fleet cardinalities not pinned by tests; hardcoded constants in test_finalize | B-N7 | **accept** | Sentinel test: load `config/fleet/r5a_fleet.yaml`, assert `len(p_predict_eligible_ids()) == 14`, `len(p_logprob_eligible_ids()) == 12`, `len(temporal_pairs()) == 2` |
| MED-10 | F.34 idempotency masks default-timestamp auto-bump; both runs use explicit `--bump-version` | B-A2 | **accept** | New test: pinner *without* `--bump-version` twice with > 1s gap → assert version differs; or document precise auto-bump behavior |
| MED-11 | B.24 explicit-`revision` happy path untested; only multi-snapshot rejection tested | B-A5 | **accept** | Test: 2-snapshot fixture + `revision=sha_a` → assert pinner picks sha_a's tokenizer |
| MED-12 | C.12 sampling-config-missing not tested in isolation; `_run_finalize` helper always passes `--sampling-config` | B-A6 | **accept** | Test: confirmatory + nonexistent `--sampling-config` → SystemExit with `[clause N]` |
| MED-13 | `MINIMAL_FLEET_YAML` mock fixture has 1 white-box + `pcsg_pairs: []`, far from real fleet shape | B-A7 | **accept** | Upgrade fixture to ≥2 white-box + ≥1 black-box + ≥1 pcsg_pair; placeholder SHAs become valid 40/64-hex (per #7 D) |

## MED bucket — Cluster 3 (doc/docstring/CLI-help drift)

User direction: fix all immediately (including consumer-facing renames) before cloud spend, to land with a clean schema.

### 3a — Stale rename residue
| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| MED-14 | `R5A_OPERATOR_SCHEMA.md:26, 158` still says `C_FO` / `E_FO`; code enum is `C_CO`, planning emits `E_OR` | D-N4 | **accept** | sed `C_FO`→`C_CO`, `E_FO`→`E_OR` across the file; verify internal table consistency |
| MED-15 | `PENDING.md:37` still references `cutoff_probe/` path | E-A6 | **accept** | String replace; do alongside #8 B PENDING split |
| **MED-16** ⚠️ | `planning_power_calculator.py:355, 392` emits `fo_eligibility` key in JSON output for `E_OR_E_NoOp_beta_cutoff` row | D-N5 / E-N2 | **accept** | **Consumer-facing rename**: `fo_eligibility` → `or_eligibility` (or `cutoff_eligibility`); grep entire codebase + notebooks for readers, sync all |

### 3b — Schema/code drift in docstrings
| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| MED-17 | `LogProbTrace` docstring (`contracts.py:236, 265, 268`) says v2.0 introduces `top_alternative_token_ids`, but schema only persists `top_alternative_logprobs` | E-N3 | **accept** | Delete `top_alternative_token_ids` mention from docstring (or mark as deferred) |
| **MED-18** ⚠️ | `ExposureHorizonEstimate.p_drop_gt_005` field name implies fixed 0.05; `detect_exposure_horizon()` accepts configurable `drop_threshold` | E-N4 | **accept** | **Consumer-facing rename**: Pydantic field `p_drop_gt_005` → `p_drop_gt_threshold` (matches `run_exposure_horizon_analysis.py:200` output JSON key already). Sync all readers |
| MED-19 | Pinner docstring (`ws1_pin_fleet.py:42`) says log append is "best-effort, can be added by hand"; impl raises on corrupt/non-array log | E-N5 | **accept** | Reword to "raises on corrupt or non-array log; operator must reconcile before retry"; do alongside #5 A |
| MED-20 | `build_cutoff_probe_set.py:4, 52` docstring says 24 months / ~1,440 articles; defaults are 36 months / 2,160 | E-A1 | **accept** | Docstring numbers → 36 mo / 2,160 |

### 3c — CLI help missing / misleading
| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| MED-21 | `run_exposure_horizon_analysis.py --drop-threshold` help says fraction is "reported alongside"; threshold also gates accept/reject | E-A2 | **accept** | Help text: "drop fraction threshold for accepting horizon (default 0.05); reported in output and used as accept/reject criterion" |
| MED-22 | finalizer CLI flags `--exposure-horizon`, `--vllm-image-digest`, `--gpu-dtype`, `--hidden-states-dir` (after #1 B) lack help text | E-A3 | **accept** | Each flag gets one-line help + "(required in confirmatory mode)" marker |
| MED-23 | `ws1_run_logprob.py --vllm-image-digest` help omits `sha256:<64-hex>` format requirement | E-A4 | **accept** | Help text adds format spec |

## LOW bucket (6 items)

| # | Finding | Lens | Triage | Notes |
|---|---|---|---|---|
| LOW-1 | pinner `_patch_model_block` compares quoted `current` vs unquoted `new_value`; idempotent rerun emits misleading "SKIP (already pinned with conflicting...)" message | D-N3 | **accept** | Strip surrounding quotes before equality check. Verified by #10 B's idempotency test |
| LOW-2 | `test_planning_power_calculator.py:74` only asserts absence of 2 of 4 retired CI key names | B-N6 | **accept** | Add the missing 2: `power_pilot_ci95_high`, `power_main_ci95_low` |
| LOW-3 | `[clause 2]` reused for both vLLM-image-digest failure and sampling-config-missing | A-A3 / F-Role1#3 | **accept** | Renumber clauses end-to-end after #1 B (hidden-states), #MED-2 (runstate) clauses are added. Each check gets a unique clause number |
| LOW-4 | F.38 source-inspection test brittle: requires PCSGPair field names as quoted string literals in `pcsg_pair_registry_hash` source | B-A4 | **accept** | Replace with behavior-based test: mutate field values, assert hash changes; assert hash stable when no field changes |
| LOW-5 | `.gitignore:35-37` ignores entire `data/pilot/cutoff_probe/` subtree; old path now retired in favor of `data/pilot/exposure_horizon/` | C-A10 | **accept** | Delete the lines (old path retired); if dev-artifact concern remains, switch to file-level `*.parquet` / `*.json` patterns |
| LOW-6 | PENDING.md "Last updated" header (`:9`) predates the 2026-04-30 Phase-8-MC entry (`:15`) | E-A7 | **accept** | Update header date to 2026-05-02 (today); do alongside #8 B / #MED-15 / #LOW-3 PENDING edits |

---

## Triage summary

All **45 findings** disposed:
- **40 actionable** (11 HIGH + 23 MED + 6 LOW)
- **5 closed by HIGH triage decisions** (no further action; tracked above)

### Option distribution (HIGH only)
| Option | Count | Findings |
|---|---|---|
| A (minimal direct fix) | 2 | #4, #5 |
| B (split / structural change) | 4 | #1, #8, #10, #11 |
| D (full belt-and-suspenders / accept) | 4 | #2, #3, #6, #7 |
| E (combination) | 1 | #9 |

### MED + LOW: all `accept` (recommended option taken without alteration).

### Triage principle (saved to memory `feedback_review_triage_priority.md`)
**Gate-leak (production data correctness) > everything else; UX / docstring purity is secondary.** User's explicit preference 2026-05-02. Used to break ties for #2 (gate holds → accept current), #6 / #7 (gate-leak → close at most upstream layer), #11 (doc not gate but LLM-context principle elevates priority).

### Co-occurring decisions
- #6 D ⊆ #7 D: snapshot.name regex check becomes redundant after Pydantic validator; only tokenizer.json `json.loads()` validation retained
- #9 E delivers plan C.10 acceptance (pilot trace SHAs in manifest) — A-A2 closed transitively
- #4 A closes C-A3 (partial horizon JSON) transitively
- #2 D + B-A1 split-off → MED test follow-up captured in cluster 2

### Cross-refs to memory
- `feedback_review_triage_priority.md` — gate-leak priority principle
- `feedback_doc_for_llm_context.md` — docs as LLM context (informed #11 B, cluster 3 sweep decision)
