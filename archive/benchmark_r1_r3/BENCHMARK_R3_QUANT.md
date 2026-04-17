# BENCHMARK MVP R3 Decision Check — Quant Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior quantitative researcher, continuing R1+R2 persona)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md
**R1/R2 references:** BENCHMARK_R1_QUANT.md, BENCHMARK_R2_QUANT.md

---

## 1. Per-decision verdict

**Decision 1 — Framing deferred: `OK-with-concern`**
From the Quant lens, deferring paper framing is acceptable if and only if Decisions 2 and 4 are locked as an economic contract now. The real danger is not narrative ambiguity; it is letting R4 factor discussions back-propagate into outcome mechanics. If the corpus later drifts toward "interesting annotations" while tradability, benchmarking, and event-time rules remain soft, the contamination→alpha bridge dies. So the deferral is fine, but only because the schema is supposed to be substrate-first.

**Decision 2 — Point-in-time market mechanics fields: `NEEDS-REWORK`**
The direction is right, but the candidate field list is not yet complete enough for production quant use. The main gap is that you still have horizon-level ARs (`1d/5d/22d`) instead of the fixed return legs that matter operationally for announcement timing: at minimum `close→next_open`, `next_open→next_close`, and `open→open` over 1d/3d. You also still need security identity, exchange, target scope, liquidity/size buckets, timestamp quality, and corporate-action basis. On sources: `AkShare`'s own docs say its A-share minute interfaces only provide recent data, not full history, and my live probe returned a rolling ~1970-row window on the Sina minute path; its Eastmoney historical-minute path was also proxy-fragile in the live environment. `Baostock` did return 15-minute stock bars in `rag_finance`, but the same pattern returned no CSI 300 minute rows, so do not assume it is a complete intraday benchmark source. Also, Baostock is still marked "alpha" on PyPI. Bottom line: usable stack, but not yet reliable enough to define the schema loosely.

**Decision 3 — Event-cluster sampling: `OK-with-concern`**
"One case per cluster" is correct. The problem is that "earliest vs most representative" is too discretionary as written. Earliest can be rumor-phase or thin-wire text; most representative can drift toward high-authority or ex post recap text. For quant, the critical object is not just which document you keep, but which timestamp anchors the outcome: first mention, official disclosure, and chosen canonical document are not interchangeable. You should keep the choice axis, but force pipeline default plus override-with-reason, and preserve both first-mention time and official-announcement time when available. Retractions/corrections/辟谣 should not silently merge into the same economic event unless you explicitly preserve that state transition.

**Decision 4 — Outcome function `O_i(H)`: `NEEDS-REWORK`**
Computing the label from raw fields at query time is correct. The current parameterization is not. A single CSI 300 benchmark is too coarse for A-share microstructure; STAR, ChiNext/SME, and 北交所 names can carry benchmark mismatch large enough to pollute the sign label on marginal cases. More importantly, `1d/5d/22d` does not solve the timing problem created by intraday announcements; 22d is fine as a secondary drift horizon, but it cannot replace short fixed event windows. The `0.5 × trailing 20d sigma` neutral band is a reasonable default, but only if you also store a fallback regime for insufficient history and a confidence penalty for weak observability. Confidence should measure label reliability, not "market certainty."

**Decision 5 — Pilot via reprint detection: `OK-with-concern`**
As a pilot-construction tactic this is defensible from the quant side, but it will not be distribution-neutral. Reprintable CLS items will skew toward formal disclosures and official announcement chains, which usually have cleaner timestamps, clearer entity mapping, and cleaner post-event return windows than original reporting or industry chatter. That means the pilot will likely look easier and cleaner than the eventual substrate. I would expect listed-company disclosure reprints to be material but not dominant in the full CLS flow; do not budget the pilot assuming a majority overall without measurement. Matching to exchange/CNINFO archives is feasible for 2020+ disclosure-type cases, but less clean for repost chains, corrections, and outlet-specific rewrites.

**Decision 7 — Agent-based annotation: `OK-with-concern`**
Quant-specific concern is narrow: model agreement is not evidence that timing, tradability, or outcome fields are correct. Those fields should be programmatic wherever possible. Use agent cross-validation for entity scoping, event typing, and textual rationale; do not let agents become the source of truth for market mechanics. Also, do not interpret high agreement as construct validity if both models see the same reporting conventions and make the same timestamp/rumor-phase mistake.

## 2. Missing fields in Decision 2

- `target_scope`, `primary_entity_id`, `ticker`, and `exchange` need to be explicit in the market-mechanics layer, not assumed elsewhere.
- Add fixed return legs: `c2o`, `o2c`, `o2o_1d`, `o2o_3d`, raw and abnormal. Horizon-only AR is not enough.
- Add `publish_ts_raw`, normalized `publish_ts` with `Asia/Shanghai`, and `timestamp_quality_flag` (`exact`, `date_only_imputed`, `unknown`).
- Add finer `announcement_session_bucket`: `pre_open_call_auction`, `continuous_intraday`, `close_call_auction`, `post_close`, `non_trading_day`.
- Add `first_trade_ts` and `first_observable_bar_ts`, not just realization lag.
- Add `benchmark_id` and `adjustment_basis`, plus `corporate_action_in_window_flag`.
- Add survivorship fields: `ipo_date`, `out_date/delist_date`, `status`, and `survivorship_bias_flag`.
- Split limit flags into direction and state if possible: at least distinguish `limit_up_hit` vs `limit_down_hit`; generic "hit limit" is too lossy.

## 3. Missing parameters in Decision 4

- A benchmark mapping rule, not just "CSI 300 primary." Store which benchmark was used and why.
- A minimum-history rule for sigma/ADV calculations. If `<20` trading days, either shorten the estimator with a low-confidence flag or suppress the categorical label.
- A confidence formula. Best version: standardized move size times data-quality penalties, e.g. `sigmoid(|AR| / max(neutral_band, sigma_H))` times penalties for low ADV, halt/limit, missing-time imputation, and corporate actions in window.
- A primary short-horizon contract. `22d` can stay secondary, but it should not replace `3d` in the point-in-time outcome core.
- A missing-time rule: if announcement time is unknown, do not silently impute to open/close without flagging, because that changes the return leg.

## 4. Hidden coupling risks

- Decision 2 and 4 are silently incompatible if you keep coarse session buckets but compute outcome on intraday-sensitive windows.
- Decision 3 and 4 will break if canonical document time is allowed to stand in for official event time.
- Decision 5 and 3 interact: replacing CLS text with original-source text changes both timestamp semantics and canonical-doc logic unless both are stored.
- Decision 5 will bias any early detector/factor readout toward cleaner disclosure cases unless `is_reprint` is a first-class stratification field.
- Decision 7 can create schema drift if agent annotations overwrite programmatically derived timing/tradability fields.

## 5. Priority fixes before R4 launch

- Lock the Decision 2 field contract now, especially identity, timestamp quality, session bucket, fixed return legs, benchmark ID, and survivorship/corporate-action flags.
- Recast Decision 4 so the short-horizon core is event-time executable, with `22d` demoted to secondary robustness.
- Force Decision 3 to preserve both first mention and official announcement times, with pipeline default plus audited override.
- Treat the reprint pilot as a pilot-only slice, not as representative evidence about the final substrate distribution.
- Keep market mechanics programmatic; do not let Decision 7 annotation logic become the truth source for tradability or outcomes.

Sources: [AkShare stock minute docs](https://akshare.akfamily.xyz/data/stock/stock.html), [AkShare index minute docs](https://akshare.akfamily.xyz/data/index/index.html), [AkShare trade calendar docs](https://akshare.akfamily.xyz/data/tool/tool.html), [baostock PyPI](https://pypi.org/project/baostock/), [baostock GitHub](https://github.com/shimencaiji/baostock), plus live probes run in `conda run -n rag_finance python` on 2026-04-13.
