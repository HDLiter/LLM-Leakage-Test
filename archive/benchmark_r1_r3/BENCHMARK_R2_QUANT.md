# BENCHMARK MVP R2 Check — Quant Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior quantitative researcher persona, continuing R1 thread)
**Reasoning effort:** xhigh
**R1 reference:** BENCHMARK_R1_QUANT.md

---

Conditional go. Build it as infrastructure, not as a finished leakage benchmark.

1. This is worth building only if you stop calling the corpus itself the benchmark. A Chinese financial news corpus with factor annotations, entities, and verified outcomes is not yet a leakage benchmark; it is a leakage-evaluation substrate. Without SR/FO or some other causal probe layer, the memorization angle weakens materially. It does not disappear, but the claim changes from "we benchmark leakage" to "we provide a point-in-time substrate on which leakage detectors can be stress-tested across strata." That is still useful from a production perspective. "Yet another annotated corpus" is exactly what it becomes if the outcome field is generic and the factor schema is shallow.

2. The path to the alpha-contamination story is still open, but only if you encode the market mechanics now. If "verified outcome" means narrative direction plus some ex post move, you will paint yourself into a corner. If it means fixed point-in-time return definitions on tradable names, with timestamps and tradability flags, then the bridge remains intact. The later alpha track does not require you to run a portfolio study now. It does require that today's corpus preserve company-level timing, liquidity, and outcome construction cleanly enough that someone can later ask: did contaminated-looking cases bias ranking or model choice?

3. Must-have fields at MVP:
- `publish_ts` with timezone normalization and exchange calendar context.
- `target_scope`: company vs sector vs index vs macro/policy.
- `primary_entity_id` and ticker/security mapping where applicable.
- `is_tradeable`, `ADV20_bucket`, `market_cap_bucket`, plus halt / ST / limit-hit flags for A-shares.
- Fixed outcome horizons and realized abnormal return magnitude, not just raw direction: at minimum close-to-next-open, next-open-to-next-close, and 1d/3d open-to-open AR.
- `outcome_realization_lag`: when the "truth" becomes observable relative to publication.
- `entity_salience` or at least the ingredients to compute it: headline mention, lead mention, mention count, title/body span positions.

Can defer, but only if later-computable from preserved raw data:
- Rich `surprise` modeling. For earnings or guidance, capture actual/consensus if available; otherwise a coarse event subtype is enough for MVP.
- `event_family_density` and `locator_strength` as hand-labeled factors. Do not label them manually now. Preserve dedupe clusters, article text, entity spans, and event typing so you can compute them later.

4. "Sufficient per sub-partition" without an estimand is too vague. From a quant data perspective, do not target the full Cartesian product of factors. You will create dozens of empty cells. Instead, pick 4-6 primary axes and require usable support on marginals and a few pre-declared interactions. As a floor, any partition you expect to compare should have roughly 150-200 cases per cell after filtering. Below that, you are fitting noise and arguing about shrinkage. Minimum useful scale: a 600-800 deeply audited company-level core, plus at least 3-5K shallow cases. If you cannot reach that, narrow the factor space further.

5. The main risk is not missing SR/FO labels now; it is failing to preserve the scaffolding needed to add them later. Decisions now that prevent expensive re-annotation:
- Store immutable raw text, headline, source, and exact timestamps.
- Keep evidence spans for entity mentions and outcome-bearing statements.
- Normalize entities and event types to stable IDs.
- Cluster near-duplicates and follow-up narratives at the event-family level.
- Separate article-known facts from post-event verification metadata in the schema.
- Version the labeling protocol and provenance of every field.

If you skip those, later SR/FO and dose-controlled CPT become a re-databasing exercise, not an extension.

6. This MVP fits the barbell shape, but only if you make the barbell explicit now. "As large as reasonably possible" is how teams end up with a medium-sized, medium-quality mush. You need two products:
- Deep core: full audit, strict point-in-time outcomes, tradability metadata, entity/event normalization.
- Shallow panel: broader coverage with lighter labels for distributional analysis and detector stratification.

Do not let the shallow panel dictate the schema. The deep core should define the contract.

7. Go, with a hard condition: define the corpus as a production-grade evaluation substrate, not as a standalone memorization benchmark, and lock the point-in-time market schema now. No-go if the team wants to postpone tradability, fixed-horizon AR definitions, and timing hygiene in order to maximize volume. That would recreate the original problem later: lots of cases, weak economic meaning, and no clean path from "memorization differences across partitions" to "this matters for model risk."
