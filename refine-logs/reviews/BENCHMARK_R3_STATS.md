# BENCHMARK MVP R3 Decision Check — Stats Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior econometrician, continuing R1+R2 persona)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md
**R1/R2 references:** BENCHMARK_R1_STATS.md, BENCHMARK_R2_STATS.md

---

## 1. Per-decision verdict

**Decision 3 — event-cluster sampling: `OK-with-concern`.**  
The major statistical problem from R1/R2 was duplicate inflation. One case per event cluster fixes that. The remaining problem is the **selection rule inside cluster**. "Earliest vs most representative, chosen by annotator" is too discretionary for a primary sampling rule. That does not create the old design effect, but it does create avoidable selection noise and potential bias toward more legible, more authoritative, or more detailed rewrites. My view: the clustering pipeline should emit a deterministic `canonical_doc_id` by rule, and human/agent override should be allowed only under pre-coded reasons. Free-text reasoning can be stored, but it should not be the rule.

**Decision 4 — outcome function `O_i(H)`: `OK-with-concern`.**  
This is directionally correct and materially consistent with my R2 position. The remaining issue is not the broad shape; it is the missing **operational spine**. Right now the spec still needs: exact `tau_i`, return convention, horizon-matched neutral band, target-type benchmark mapping, missing-time rule, and insufficient-history rule. Also, `confidence` is underspecified and should be renamed to something like `label_quality`, because what you can defensibly output here is data quality, not posterior belief.

**Decision 7 — agent cross-validation annotation: `OK-with-concern`.**  
The workflow is sensible as a screening architecture. The weak points are statistical calibration and identification. A 50-100 case pilot is thin if you want field-wise IAA with usable uncertainty. More importantly, LLMs must not be allowed to define world-grounded labels from their own knowledge. Outcome labeling should be mechanical from market data; LLMs should be confined to text-grounded fields, with human adjudication where disagreement or ambiguity remains.

**Decision 9 — context note: broadly defensible.**  
Locking the **binning rule** but deriving the **cutpoint values** from the frozen corpus is acceptable in ML/NLP-style preregistration, provided the values are computed **before any detector-outcome analysis on the confirmatory slice**. Reviewers will still complain if the values are tuned after peeking at results. So the distinction is defensible, but timing discipline matters.

## 2. Updated target N under one-case-per-cluster

Decision 3 changes the power math materially. In R2 I inflated the floor because I was assuming duplicate articles within event clusters remained in-sample. If you truly sample **exactly one case per cluster**, that duplication design effect disappears.

Using the same R2 anchor:

```text
p1 = 0.123
p0 = 0.068
RD = 0.0556
N_floor ≈ 852 scorable cases for one balanced partition contrast
```

The old inflation was:

```text
DEFF = 1 + (m - 1) rho = 1 + (3 - 1) * 0.25 = 1.5
```

Under Decision 3, with one sampled case per cluster:

```text
DEFF = 1 + (1 - 1) rho = 1
N_required ≈ 852 scorable clusters
Gross N with 15% loss ≈ 852 / 0.85 = 1002
Gross N with 20% loss ≈ 852 / 0.80 = 1065
```

So the **new statistical floor** is about **1,000-1,100 sampled clusters**, not 1,500, for one clean primary contrast. If you want separate company/sector/index modules, a dev/test split, or safety margin against noisier-than-Phase-4 effects, then `1,300-1,500` is still reasonable, but it is now **scope insurance**, not a clustering correction.

On the denominator: if the CLS archive is about **1.16M articles** and the average duplicate cluster size is on the order of `m ≈ 3`, then the implied cluster count is roughly **3.9e5**. Even if `m` were closer to `5`, you still have about **2.3e5** clusters. So `N = 1,500` is not a 30% sample-rate world; it is well below 1% of the likely cluster population. The real constraint is annotation budget, not finite-population inference.

On allocation: yes, the Decision 9 posture points toward **proportional/random cluster sampling plus a modest stratified core**, not aggressive factor-bin quota allocation. Do **not** sample proportional to cluster size; cluster size is duplication intensity, not inferential weight.

## 3. Outcome function fixes for Decision 4

I would update the spec as follows.

- Define `tau_i` now: the first tradable market open strictly after `publish_ts`, exchange-calendar aware, in Beijing time.
- Define the primary return convention now: benchmark-adjusted **open-to-open log return** from `tau_i` to `tau_i + H`. Store raw return in parallel.
- Make the neutral band **symmetric** around zero. As a direction label, asymmetry is indefensible here.
- Make the neutral band **horizon-matched**. For horizon `H`, use something like `b_i(H) = max(0.5 * sigma_i(H), 0.3%)`, where `sigma_i(H)` is the trailing volatility of `H`-day abnormal returns, or daily sigma scaled by `sqrt(H)` if that is the only feasible implementation.
- Then define direction mechanically: `up` if `AR_i(H) > b_i(H)`, `down` if `AR_i(H) < -b_i(H)`, else `neutral`.
- Keep CSI 300 as the single primary benchmark only within the **company-target** primary module if simplicity is the goal. But a single benchmark across company, sector, and broad index targets is too crude. Sector targets need sector-index construction; broad index targets should use raw index return. Do not pool magnitudes across target types.
- For recent IPOs, names with fewer than 20 trading days of history, suspensions, or prolonged non-tradability: mark them `primary_outcome_unscorable = 1`. Do **not** use sector-median sigma as the primary fix; that injects model-based noise exactly where the sample is already atypical.
- If exact publish time is missing but the date is known, the conservative primary rule is: treat the item as `date_only` and map `tau_i` to the **next trading-day open**. Do not impute intraday timing into the primary label.
- Replace `confidence` with `label_quality`, computed by rule from timestamp precision, tradability, sufficient price history, benchmark availability, and halt/limit flags. That can support secondary uncertainty-weighted analyses, but the primary analysis should remain unweighted unless pre-registered otherwise.

## 4. Annotation endogeneity: LLMs labeling an LLM benchmark

Yes, this is a real identification concern. If the annotator LLM is allowed to use its own world knowledge, then part of the "ground truth" becomes a function of another LLM's parametric memory. That is unacceptable for outcome labels and risky for some factor labels.

The clean resolution is separation of roles:

- `O_i(H)` is **not** LLM-labeled. It is deterministic from the frozen market-data pipeline.
- LLM annotators are used only for **text-grounded** fields: entity spans, source/provenance cues, and factor labels that can be justified from the provided article plus frozen metadata.
- Annotators should not see detector outputs, target-model responses, or any retrieval beyond the case materials.
- Human adjudication is final on disagreements. If Claude says `A`, Codex says `B`, and the human says `C`, that is not "majority vote"; it is evidence the codebook or prompts need repair.

For IAA, use field-specific metrics:

- Categorical fields: Cohen's `kappa`, but also raw agreement and preferably `AC1` when prevalence is skewed.
- Continuous fields: `ICC(2,1)` for absolute agreement.
- Entity extraction: exact-match span `F1`, relaxed/overlap `F1`, and linked-entity accuracy separately.

For the pilot, I would not trust `50-100` doubly annotated cases as a decisive gate. A better floor is about **150 doubly annotated clusters**, with bootstrap CIs obtained by resampling clusters. The scaling rule should be **field-specific**, not global. For any field that enters primary partitioning or inclusion/exclusion, I would want something like point estimate `>= 0.80` and lower 95% CI above roughly `0.67` before calling it scale-ready.

Using Claude/Codex as annotators while evaluating Qwen does mitigate **same-model** contamination. It does **not** solve shared-foundation-model bias. So treat cross-model annotation as a robustness aid, not an identification guarantee.

## 5. Priority fixes before R4 launch

1. Replace free-form "earliest vs representative" choice with a deterministic canonical selection rule plus limited override codes.
2. Freeze the missing pieces of `O_i(H)` now: `tau_i`, return convention, horizon-matched symmetric neutral band with floor, target-type benchmark mapping, and unscorable rules.
3. Rename `confidence` to `label_quality` and define it as a rule-based data-quality score.
4. Upgrade the pilot plan to a field-wise reliability study, not a generic 50-case smoke test.
5. State explicitly in R6 that bin-edge values and contrast lists are frozen **before** any detector outcomes are inspected on the confirmatory slice.

If you do those five things, R4 can proceed without carrying forward a hidden statistical defect.
