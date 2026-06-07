---
title: R5A Temporal Cue Design — Agent Brief
stage: R5A Round 2 (between Step 1 synthesis and Step 2 convergence)
date: 2026-04-15
status: INPUT DOCUMENT for 4-lens Codex discussion
scope: Temporal cue taxonomy, D4 ADG redesign, D11 candidate, time-as-factor, time-handling axis for D5/D6/D7
context_files:
  - refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - docs/DECISION_20260413_mvp_direction.md (v6.2)
---

# R5A Temporal Cue Design — Agent Brief

## Purpose

This brief feeds 4 parallel Codex lens agents (Quant / NLP / Stats / Editor). Each agent independently answers 5 blocks of open design questions about how temporal cues in CLS news text should interact with the FinMem-Bench detector layer.

This topic was NOT covered by R5A Step 1 — it emerged from a user discussion on 2026-04-15 after the Step 1 synthesis was written. It is a genuinely new design dimension that no Step 1 lens considered.

## Background you must know

### Project one-liner

FinMem-Bench is a factor-controlled Chinese financial memorization-detection benchmark built on the CLS (财联社) telegraph corpus. R4 locked a 12-factor shortlist with a 4-bloc structure. R5 determines which detectors to run on top of those factors. R5A Step 1 produced 10 detector candidates; 7 are kept, 2 are dropped, 1 (D4 ADG) is held pending this session. See R5A_STEP1_SYNTHESIS.md and R5A_DEFAULTS.md for the full state.

### The 4-bloc structure (Risk R4 v6.1)

- **Bloc 0** — temporal exposure: Cutoff Exposure (case×model)
- **Bloc 1** — repetition / surface reuse: Propagation Intensity, Template Rigidity, surface_template_recurrence
- **Bloc 2** — prominence / attention: Entity Salience (target + competing), Target Scope, Tradability Tier
- **Bloc 3** — institutional stage / source: Structured Event Type, Disclosure Regime (PLACEHOLDER), Event Phase, Session Timing

### The 12 active factors

Spine: Propagation Intensity, Cutoff Exposure, Anchor Strength, Entity Salience.
Secondary: Target Scope, Structured Event Type, Disclosure Regime (placeholder), Template Rigidity.
Auxiliary: Tradability Tier, Session Timing.
Control: Text Length.
Sampling-design: Event Phase.

Reserve: Exact-Span Rarity, Cluster Temporal Span, Interaction menu, Influence/Relevance, Eliteness.

### Rule relaxation (important)

Per user clarification 2026-04-15: the v6.2 decision doc's "do not add factors in R5" language is softened. It is now a discussion hygiene rule, not a hard gate before pre-commit. **Agents in this session may propose time-cue as a new factor if the design argument supports it.**

### D4 ADG from Step 1 (NLP lens proposal)

NLP's Step 1 proposal for D4 "As-of Date Gating": ask the same model to answer under explicit "as of" dates before and after the event, scoring whether it properly withholds or changes knowledge across the boundary. Mechanism: temporal-cutoff-conditional (within-model). Primary bloc: 0. Access: either, full fleet.

The user discussion revealed that D4 as originally proposed conflates two distinct operating modes (see Block C below). This session must resolve the decomposition.

### CMMD fleet (for reference)

1. Qwen 2.5-7B-Instruct (local, cutoff 2023-10, white-box)
2. DeepSeek-V2.5 (OpenRouter, ~2024-03, black-box)
3. GLM-4-9B-0414 (local, 2024-06-30, white-box)
4. DeepSeek-V3-0324 (OpenRouter, 2024-07, black-box)
5. Qwen3-14B (local, 2025-01, white-box)
6. Claude Sonnet 4.5 (OpenRouter, 2025-01/07, black-box)

Note: Fleet composition is under review in a separate fleet-review session. For this session, treat the fleet as a reference, not as locked.

### Key papers for temporal cues

- Wongchamcharoen & Glasserman 2025 "Do LLMs Understand Chronology?" (arxiv 2511.14214) — directly tests whether LLMs comply with prompt-declared temporal boundaries; foundational for ADG
- Merchant & Levy 2025 "Fast and Effective Solution to Look-ahead Bias" (arxiv 2512.06607) — inference-time logit adjustment using temporal knowledge; relevant to time-conditional detectors
- Cheng et al. 2024 "Dated Data: Tracing Knowledge Cutoffs" — tracing model knowledge via temporal probes
- GSM-Symbolic (Mirzadeh et al. 2024, arxiv 2410.05229) — surface-invariant perturbation precedent; seeds the dose-response idea
- Glasserman & Lin 2024 (arxiv 2309.17322) — anonymization distraction effects; analogous framework for time-cue removal

## Insights from user discussion (2026-04-15)

These are design insights that emerged from the user's analysis. They are starting points, NOT locked decisions. Agents should build on, challenge, or refine them.

### Insight 1: Temporal cue clarity is a GRADIENT, not a binary

CLS articles contain temporal information at varying levels of explicitness. A preliminary taxonomy:

| Level | Description | Example |
|---|---|---|
| L4 | Exact date/time in text | "2024年3月15日14:30" |
| L3 | Incomplete but in-text locatable | "今天是3月15日" / "周五" |
| L2 | Relative / ordinal | "Q1" / "上周" / "去年同期" |
| L0.5 | Closed-reference (entity→date) | "第五届WAIC" / "《数据安全法》发布后" / "X国发布《XXX法案》" |
| L0 | Open implicit | "新政府上任后" |
| L1 | No temporal cue | (all temporal fields removed) |

This is a first draft. The levels, their ordering, and whether it should be a single gradient or multi-dimensional taxonomy are all open questions (see Block A).

### Insight 2: Closed-reference temporal cues (L0.5) are special for memorization detection

Phrases like "第五届WAIC" or "《个人信息保护法》发布后" require the model to perform an entity→date lookup from its training memory to recover the precise time. This lookup IS the memorization signal we want to measure — the model must have memorized "WAIC 5th edition = September 2022" to use this phrase as a temporal anchor.

This type has a critical sub-split:
- **Adjunct-type** ("《个保法》发布后，某公司宣布…"): the temporal cue is a subordinate clause that can be removed or generalized ("某项监管政策发布后…") while preserving the core event semantics. **Minimal-edit-preserving-semantics property HOLDS.**
- **Subject-type** ("第五届WAIC开幕"): the temporal cue IS the event subject. Removing it destroys the event. **Minimal-edit property FAILS.**

### Insight 3: Time cue removal is a semantics-preserving minimal edit (unique property)

Among all 12 active factors, temporal cues are the ONLY factor where:
- A per-case manipulation is possible (remove or downgrade the time cue)
- The manipulation preserves core event semantics (who did what, with what outcome)
- The manipulation is achievable via minimal text editing (typically deleting one short phrase)

No other factor has all three properties simultaneously:
- Entity masking → destroys economic meaning (Wu et al. 2025 anonymization information-loss)
- Outcome editing → becomes SR/FO counterfactual perturbation
- Structure editing → becomes Template Rigidity intervention

This makes time cues uniquely suited for a **dose-response intervention design**: create multiple temporal-clarity versions of the same article and observe how detector scores change along the gradient. This is a near-experimental identification strategy that could be a methodological highlight of the paper.

**Exception**: subject-type L0.5 cases cannot undergo this manipulation (see Insight 2).

### Insight 4: ADG has two operating modes

When D4 ADG injects an "as-of" date into the prompt:
- **If the original text RETAINS its explicit temporal cues**: the model faces a TEXT vs PROMPT time contradiction. The detector measures "does the model trust the text's time or the prompt's time, and does this depend on memorization?"
- **If the original text has its temporal cues MASKED first**: there is no contradiction — the model only has the prompt's as-of date. The detector measures "can the model comply with a prompt-level temporal gate when the text provides no temporal anchor?"

These are distinct constructs and should be separated in the design.

### Insight 5: Time-handling axis cascades to existing detectors

D5 (SR/FO), D6 (FinMem-NoOp), and D7 (EAD) all generate perturbation variants of the original text. Whether those variants preserve, remove, or modify temporal cues is a design choice that Step 1 did not consider. For example:
- SR reverses the financial direction — but if the text says "2024年3月15日某公司盈利2亿", does the SR variant keep or remove the date? Keeping it creates a "date + entity + reversed outcome" triplet that may trigger memorized event retrieval differently than the undated version.
- NoOp inserts an irrelevant clause — does that clause contain its own temporal cue? If yes, does the inserted time match the original article's time window?

## Block A — Temporal cue taxonomy (OPEN)

Design the classification system for temporal cues in CLS text.

**Questions to answer**:

1. Should the taxonomy be a **single ordered gradient** (L4 > L3 > L2 > L0.5 > L0 > L1) or a **multi-dimensional classification**? If multi-dimensional, what are the axes? One candidate: (surface_visibility × lookup_dependency). Are there other meaningful axes?

2. Is the preliminary 6-level taxonomy (L4/L3/L2/L0.5/L0/L1) the right granularity? Should any levels be merged or split? In particular:
   - L2 ("Q1", "上周") and L0.5 ("第五届WAIC") both require some form of external knowledge to pin to a date. Should they be merged?
   - L3 ("今天是3月15日") requires knowing the year from context. Is that "shallow lookup" or "in-text"?
   - L0.5 subject-type vs adjunct-type: is this a sub-level or a separate axis?

3. How should the taxonomy handle **multiple temporal cues at different levels in the same article**? (e.g., "2024年3月15日（周五），第五届WAIC期间，某公司宣布…" has L4 + L3 + L0.5 simultaneously). Is the article's level the MAX, the MIN, or a vector?

4. What annotation protocol would produce reliable temporal-cue labels on CLS text? LLM-based annotation? Rule-based extraction? Hybrid? What inter-annotator agreement target is realistic?

## Block B — Time cue as factor vs manipulation variable vs both (OPEN)

Decide the role of temporal cue information in the benchmark.

**Questions to answer**:

1. Should temporal-cue clarity be a **new factor** (the 13th factor, entering the factor × detector matrix alongside the existing 12)? If yes:
   - What hierarchy level? (spine / secondary / auxiliary / control)
   - Which bloc does it belong to? (Bloc 0 seems natural given its temporal nature, but it measures a TEXT property, not a case×model property like Cutoff Exposure)
   - What is the construct caveat? (What does the operational measurement actually capture vs what the name suggests?)
   - What is the literature provenance? (STRONG / PARTIAL / NOVEL?)

2. Should temporal-cue clarity be a **manipulation variable** (per-case intervention: create L4→L1 downgraded versions of each article and observe detector score changes)? If yes:
   - This is only feasible on articles where temporal cues are adjunct-type (removable without destroying semantics). What fraction of CLS articles satisfy this?
   - Is the dose-response curve (detector score vs temporal clarity level) itself a detector-level output (analogous to EAS delta)?

3. Should it be **both** (observation + manipulation)? The observation path gives correlational evidence; the manipulation path gives causal evidence. Are they complementary or redundant?

4. How does a temporal-cue factor interact with existing Cutoff Exposure? They are related but distinct: Cutoff Exposure is case×model (depends on which model is evaluated); temporal-cue clarity is a pure text property (same for all models). Does adding temporal-cue clarity as a factor create problematic collinearity with Cutoff Exposure, or does it add independent information?

## Block C — D4 ADG redesign (OPEN)

Redesign D4 in light of the two operating modes identified above.

**Questions to answer**:

1. Should D4 be split into two sub-detectors?
   - **D4a ADG-Contradiction**: text retains temporal cues + prompt injects contradictory as-of date → measures "model behavior under text-prompt temporal conflict"
   - **D4b ADG-Misdirection**: text temporal cues masked first + prompt injects misleading as-of date → measures "model compliance with prompt-level temporal gate in absence of text cues"

2. If split, are D4a and D4b measuring distinct constructs? What are the expected factor-relevance differences? (e.g., D4a should interact with temporal-cue clarity level; D4b should interact with Cutoff Exposure and Anchor Strength more directly)

3. If split, should they be one detector slot with two sub-measurements (like D5 SR/FO) or two independent detectors?

4. What is the relationship between D4a/D4b and D1 CMMD? CMMD is cross-model temporal disagreement; ADG is within-model temporal gating. Are they complementary (covering different mechanisms) or partly redundant?

5. Compute budget: D4 in any form requires 2 prompts per case per model (before-date and after-date). If split, D4a needs the original text + 2 as-of prompts, D4b needs the time-masked text + 2 as-of prompts. Total: 3,200 × 6 × 4 = 76,800 calls for both sub-detectors. Is this justified?

6. For D4a specifically: what happens when the prompt's as-of date matches the text's temporal cues (no contradiction)? Is that a useful control condition?

## Block D — D11 Temporal Dose-Response Delta (OPEN)

Evaluate whether a new detector D11 should enter the pool.

**Concept**: For each CLS article, generate multiple versions at decreasing temporal-cue clarity (e.g., L4 → L3 → L2 → L1 by progressively removing temporal information). Run existing detectors on each version. The **dose-response curve** (detector score vs temporal clarity level) is itself a memorization signal: if detector scores drop sharply when time cues are removed, the detector was partly relying on temporal anchors to trigger memorization retrieval.

**Questions to answer**:

1. Is D11 a standalone new detector, or is it a "temporal variant" applied to existing detectors D1/D3/D5/D6/D7? (Analogy: EAD is both a standalone detector and a stratification field for other detectors. Could D11 work the same way?)

2. What is D11's success condition? What pattern in the dose-response curve would count as evidence of temporal-cue-mediated memorization vs generic information loss from removing content?

3. What is D11's dominant failure mode? (e.g., removing time cues always reduces detector scores because it removes content, not because it removes memorization triggers)

4. Subject-type L0.5 cases (time cue = event subject, cannot be removed) cannot participate in dose-response. How large is this population in CLS? If it is >30% of cases, D11's coverage is seriously limited. How should subject-type cases be handled?

5. Cost: 4 versions × 6 models × 3,200 cases = 76,800 calls (for generation) + whatever detector computation each version requires. Is this justified given the identification benefit?

6. What is D11's relationship to D4 ADG? ADG manipulates the PROMPT's temporal framing; D11 manipulates the TEXT's temporal content. Are they complementary interventions on the same construct, or do they measure different things?

7. Could D11 subsume D4b (ADG-misdirection)? D4b masks text temporal cues and then probes with an as-of prompt. D11's L1 version (all time cues removed) is exactly the input D4b would use. Could the two be combined?

## Block E — Time-handling axis for existing detectors D5/D6/D7 (OPEN)

Decide how existing counterfactual/perturbation detectors handle temporal cues in their generated variants.

**Questions to answer**:

1. Should there be a **global rule** (all perturbation detectors either preserve or remove temporal cues uniformly) or should each detector decide independently?

2. For D5 SR/FO: When reversing financial polarity or replacing outcome slots, should the original date be preserved in the counterfactual? Preserving the date means the counterfactual creates a "date + entity + false outcome" triplet that may specifically trigger memorized event retrieval (making the detector more sensitive to memorization). Removing the date means the counterfactual tests pure semantic sensitivity without temporal anchoring (cleaner construct but weaker signal). Which is preferred?

3. For D6 FinMem-NoOp: Should the inserted irrelevant clause contain its own temporal cue? If yes, should the inserted time match the original article's time window (preserving temporal coherence) or deliberately mismatch (testing temporal sensitivity)? This is a design choice with construct implications.

4. For D7 EAD: Should temporal cue masking be added as a third masking dimension alongside target/non-target entity masking? This would expand the masking taxonomy from 2×2 (target/competitor × full-anon/category-preserving) to 2×2×2 (adding time-preserve/time-mask). Is the 8-cell taxonomy worth the cost (8× variants per case)?

5. Is there a principled way to decide these questions without running pilots, or should all temporal-handling choices be deferred to the implementation session with the default "preserve temporal cues" until pilot data says otherwise?

## What is NOT open in this session

The following are locked from R5A Step 1 consensus and should not be relitigated:

1. Independent detector reporting over ensemble (unanimous Step 1 consensus)
2. Deviate from MemGuard-Alpha's 5-MIA stack (unanimous)
3. CMMD is a top-3 detector (unanimous)
4. FinMem-NoOp must be rule-based first (unanimous)
5. EAS splits into target-mask / non-target-mask deltas (unanimous)
6. Accept Meeus 2024 SoK restriction on surface-form framing (unanimous)
7. Bloc structure is a DESCRIPTIVE WORKING HYPOTHESIS, not a validated latent structure (from v6.1)

## Output format

Each agent should produce a structured Markdown response with:

1. **Block A answer**: Proposed taxonomy (with rationale for each design choice)
2. **Block B answer**: Factor / manipulation / both (with construct-validity argument)
3. **Block C answer**: D4 redesign recommendation (keep unified / split D4a+D4b / other)
4. **Block D answer**: D11 recommendation (adopt / reject / reshape, with success/failure conditions)
5. **Block E answer**: Time-handling rules for D5/D6/D7 (global vs per-detector, with defaults)
6. **Cross-block synthesis**: ≤1 page summary of how Blocks A-E fit together from this lens, any tensions with existing Step 1 positions, and questions for other lenses.

Use H2 headers per block. No JSON. No filler prose.
