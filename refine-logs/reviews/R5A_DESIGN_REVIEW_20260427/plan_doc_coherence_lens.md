**Audit Findings**

1. **Quality-gate denominator**
   Inconsistency: `R5A_FROZEN_SHORTLIST.md §2`, `plans/phase7-pilot-implementation.md §7.1/§13`, and `DECISION_20260427 §2.5` still use `>=5/9`.
   
   Resolution: use a scalable threshold: `ceil((5/9) * N_P_predict_eligible)`. Current fleet `N=14`, so the concrete rule is `>=8/14`, not `5/14` and not fixed `5/9`.
   
   Update also `R5A_FROZEN_SHORTLIST.md §3 E_FO_mech` and `PENDING.md WS6`, which currently says `5/14`.
   
   Severity: **must-fix-before-prereg**.

2. **Stage 2 family states**
   `plans/phase7-pilot-implementation.md §7.1A` remains conceptually valid: `S20/S16a/S16b/S12` are estimands × factors, so E_PCSG becoming one registry-defined pair does not change `5 × 4 = 20`.
   
   No new default legal state should be added for E_PCSG failure. If all PCSG articles fail common-vocab eligibility, that is an operator/estimand readiness failure requiring a new decision memo, not silent demotion.
   
   Add this explicitly to §7.1A and §13.
   
   Severity: **must-fix-before-prereg**.

3. **E_PCSG_capacity_curve analysis spec**
   `DECISION_20260427 §2.1` introduces it, and code has `compute_pcsg_capacity_curve`, but `plans/phase7-pilot-implementation.md §8.1A/§8.2` do not define its analysis unit or model.
   
   Resolution: add an exploratory subsection:
   
   `mean_logprob_icm ~ log2(params_m) * cutoff_exposure_im + family + family:log2(params_m) + (1 + log2(params_m) | case_id)`
   
   Fit/report family-specific slopes; use case-cluster bootstrap as the primary uncertainty procedure because each family has only 4-5 capacity points.
   
   Severity: **must-fix-before-prereg**.

4. **WS6 exit-gate handling**
   `plans/phase7-pilot-implementation.md §13` omits WS6. That is not safe as written.
   
   Resolution: add a conditional non-blocking gate: “WS6 trigger evaluated; if triggered, hidden-state coverage for the 30-article subset across 10 white-box models is verified, or WS6 is explicitly deferred/rerun-scoped in the go/no-go memo.” It should not automatically block Phase 8.
   
   Severity: **must-fix-before-prereg**.

5. **`pcsg_pairs` referential integrity**
   `config/fleet/r5a_fleet.yaml` has the registry, but `src/r5a/fleet.py` only schema-validates shape. It does not validate that `early`, `late`, or `members` resolve to `models:` keys. No fleet loader test exists.
   
   Resolution: add `FleetConfig` validators for pair references, role-specific required fields, unique pair ids, white-box/P_logprob eligibility, and tests in `tests/r5a/test_fleet_config.py`.
   
   Severity: **must-fix-before-prereg**.

6. **`cutoff_observed` in RunManifest**
   `DECISION_20260427 §3.2` requires `cutoff_observed: dict[str, date]`. `plans/phase7-pilot-implementation.md §10.4` does not list it, and `src/r5a/contracts.py RunManifest` lacks it.
   
   This is a code-doc-decision triple miss. Also consider adding `cutoff_date_yaml`.
   
   Severity: **must-fix-before-prereg**.

7. **`quant_scheme` and `pcsg_pair_registry_hash`**
   `quant_scheme` exists in `ModelConfig` and `LogProbTrace`, but not in `RunManifest`. `pcsg_pair_registry_hash` is absent from `RunManifest` and plan §10.4.
   
   Resolution: add both to `RunManifest`; compute `pcsg_pair_registry_hash` from the canonicalized `pcsg_pairs` block, not the whole YAML hash.
   
   Severity: **must-fix-before-prereg**.

8. **Plan §14.2 YAML example**
   `plans/phase7-pilot-implementation.md §14.2` is still the old 9-model example and omits `cutoff_source`, `hf_repo`, `quant_scheme`, new Qwen capacity members, and `pcsg_pairs`.
   
   Exact wording to add: “PCSG compatibility is not inferred from `tokenizer_family`; Qwen2.5 keeps `tokenizer_family: qwen`, Qwen3 keeps `tokenizer_family: qwen3`, and PCSG eligibility is declared in `pcsg_pairs[].tokenizer_compat: qwen2_class` plus `max_token_id_inclusive`.”
   
   Severity: **must-fix-before-prereg**.

9. **2026-04-26 interface memo**
   `docs/DECISION_20260426_phase7_interfaces.md §2.1` is historical but dangerous without a supersession banner.
   
   Policy: do not rewrite the signed table. Add a top header/frontmatter note: “Superseded in part by DECISION_20260427 for fleet roster, PCSG pair definition, Path E fields, and RunManifest additions.”
   
   Severity: **acceptable-with-explanatory-comment**.

10. **PENDING.md hygiene**
   Four requested entries exist: WS1 provenance, WS1 trace contract, Path E, WS6. Missing: “Resolve OPEN: PCSG temporal-pair design” as a recently closed item.
   
   Also stale/wrong:
   `Path E` says `1,440` articles; decision corrected this to `2,160`.
   `WS6` says `5/14`; should be `8/14` under the scalable denominator rule.
   
   Severity: **must-fix-before-prereg**.

11. **Frozen shortlist §7/§10**
   `R5A_FROZEN_SHORTLIST.md §7` operator fleet counts are updated. §7 perturbations has no stale fleet count. §10 has no hard stale count, but “Fleet model versions” should clarify it means checkpoint/API versions, not roster scope.
   
   Separate stale item: §4 `E_extract` still uses `3/9` and `5/9`; if scaled, update to `ceil(3/9*14)=5/14` and `ceil(5/9*14)=8/14`.
   
   Severity: §7/§10 **acceptable-with-explanatory-comment**; §4 reserve thresholds **must-fix-before-prereg** if Stage 1 quotes reserve rules.

12. **E_PCSG terminology drift**
   Stale operational wording remains in:
   
   - `plans/phase7-pilot-implementation.md §8.1A`: “case × tokenizer-matched pair”, “white-box same-tokenizer temporal pairs only”
   - `plans/phase7-pilot-implementation.md §8.2`: “tokenizer-matched pair estimands”
   - `docs/DECISION_20260426_phase7_interfaces.md §2.1`: old tokenizer-matched temporal pairs
   
   Historical mentions in `DECISION_20260427 §1` and frozen shortlist §1 amendment are acceptable because they describe the defect being superseded. No stale occurrence found in `src/`.
   
   Severity: plan wording **must-fix-before-prereg**; historical memo **acceptable-with-explanatory-comment**.

**Remediation Order**

1. `src/r5a/contracts.py` → add `cutoff_observed`, `cutoff_date_yaml`, `quant_scheme`, `pcsg_pair_registry_hash` to `RunManifest`; then update `plans §10.4`.

2. `src/r5a/fleet.py` → validate `pcsg_pairs` references and roles; then add `tests/r5a/test_fleet_config.py`; then require smoke config check before prereg.

3. `R5A_FROZEN_SHORTLIST.md`, `phase7-pilot-implementation.md`, `DECISION_20260427` erratum, `PENDING.md` → normalize denominator policy to `ceil(5/9*N)`, current `8/14`.

4. `plans/phase7-pilot-implementation.md §8.1A/§8.2` → add E_PCSG_capacity_curve row and exploratory model spec.

5. `plans/phase7-pilot-implementation.md §13` → update 10 white-box / 14-model gates, Path E `cutoff_observed`, PCSG eligibility, and conditional WS6 artifact check.

6. `plans/phase7-pilot-implementation.md §14.2` → replace old 9-model YAML example with current 14-model schema plus `pcsg_pairs`.

7. `docs/DECISION_20260426_phase7_interfaces.md` → add supersession banner only.

8. `PENDING.md` and `DECISION_20260427 §2.4 implementation bullet` → fix Path E `1,440` remnants to `2,160`.

Verification run: `python scripts/smoke_phase7.py --check-config` passed and `python -m pytest tests/r5a -q` passed (`36 passed`), but those tests do not yet cover PCSG registry integrity or RunManifest decision fields.