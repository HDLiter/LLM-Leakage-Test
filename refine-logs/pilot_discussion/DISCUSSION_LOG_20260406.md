# Pilot Results Discussion Log — 2026-04-06

**Topic:** E_pilot results interpretation and next steps
**Protocol:** 4 Codex domain agents + Claude Challenger, 2 rounds

## Participants

| Agent | Role | Model | Thread ID |
|-------|------|-------|-----------|
| Quant | Senior quantitative researcher | Codex (xhigh) | 019d65cd-0063-7cb1-8ea1-b911b47a3485 |
| NLP | NLP/ML researcher (ACL/EMNLP) | Codex (xhigh) | 019d65ce-bed8-79c0-be3f-61e0f1609138 |
| Stats | Senior econometrician | Codex (xhigh) | 019d65d4-01a1-7393-8838-f01c11b50be1 |
| Editor | Senior EMNLP area chair | Codex (xhigh) | 019d65d6-9807-7df0-af44-e0d125063ee6 |
| Challenger | Cross-model challenger | Claude (Opus) | N/A (sub-agent) |

## Round 1 — Independent Analysis

All 4 domain agents analyzed pilot results independently. Initial consensus:
- CFLS floor effect = measurement failure (bidirectional generalization confound)
- CPT 14-17% flip rate = more promising leakage detector
- Evidence intrusion heuristic = non-contributory
- 1000-case benchmark needs redesign
- Cross-task r=0.10 = different constructs

**Divergent:** RQ pivot (Editor strong), scope (Editor narrow vs Quant expand), venue strategy.

See: `round1_*.md`, `round1_summary.md`

## Round 1.5 — Challenger

Challenger raised 3 substantive blind spots shared by ALL domain agents:

1. **CFLS might be a true negative** — no positive control exists to verify the metric works at all
2. **Sentiment analysis may not be leakage-prone** — it's a skill, not fact-retrieval
3. **CPT can't distinguish memorization from in-context persuasion** — even with controls

Proposed **three cheap diagnostics** before any benchmark redesign:
1. Verbatim completion probes
2. Temporal split (pre- vs. post-training-cutoff)
3. CFLS stratified by event rarity

Overall verdict: "The four agents are collectively optimizing how to salvage a null result into a publishable narrative."

See: `round1.5_challenger.md`

## Round 2 — Revisions

All 4 agents revised positions significantly in response to Challenger:

### Key Revisions

| Topic | Round 1 Position | Round 2 Position |
|-------|-----------------|-----------------|
| CFLS floor effect | Measurement failure | **Uncalibrated / non-diagnostic** — need positive controls |
| CPT 14-17% | More promising leakage detector | **Conflict susceptibility metric**, not memorization |
| Bidirectional confound | Real contribution | **Unvalidated hypothesis** — need empirical support |
| XGBoost downstream | Quant: include | **All: drop from this paper** |
| Benchmark redesign | Immediate priority | **Deferred** — run diagnostics first |
| Venue | EMNLP main track | **EMNLP Findings more realistic** without cross-model replication |

See: `round2_*.md`, `round2_summary.md`

## Final Convergence Status: CONVERGED

No unresolved disagreements after Round 2. All agents accepted the Challenger's core challenge.

## Decisions

### D1. Immediate next step: Go/No-Go Diagnostic Phase
Run three cheap diagnostics on existing data before any benchmark redesign:

1. **Verbatim completion probes** on DeepSeek-chat
   - Feed truncated articles, check completion fidelity
   - Establishes whether any memorization signal exists at all
   
2. **Temporal split comparison**
   - Identify DeepSeek-chat's training cutoff
   - Compare model behavior on pre-cutoff vs. post-cutoff articles
   - Strongest causal identification strategy available

3. **CFLS stratified by event rarity + directional symmetry**
   - Within existing 36 cases, check if floor effect breaks for rare events
   - Also check directional symmetry (not just raw frequency)

### D2. Relabel metrics
- CFLS → "Counterfactual Input Sensitivity" (not "leakage score") until calibrated
- CPT flip rate → "Conflict Susceptibility" or "Context Override Rate" (not "memorization detector")

### D3. Paper scope changes
- **Drop:** XGBoost downstream analysis (move to follow-up application paper)
- **Drop:** Evidence intrusion heuristic (replace with claim-level attribution if rebuilt)
- **Add:** Positive/negative controls in benchmark design
- **Reframe RQ1:** From "task design shapes leakage" to "task design shapes observability/identifiability of leakage"
- **Add RQ0 (new):** "Is leakage detectable at all in this setting?" — must be answered before RQ1-3

### D4. Venue recalibration
- EMNLP main track requires: cross-model replication (3+ models), non-finance generalization slice
- EMNLP Findings / ACL Findings: feasible with current evidence base + diagnostics
- Decision deferred until diagnostic results are in

### D5. Move up Min-K% on Qwen
- Already in project plan (RQ2), but should be run as diagnostic, not just benchmark component
- Token-level familiarity scoring is orthogonal to behavioral probes

## File Index

```
refine-logs/pilot_discussion/
├── round1_quant.md
├── round1_nlp.md
├── round1_stats.md
├── round1_editor.md
├── round1_summary.md
├── round1.5_challenger.md
├── round2_quant.md
├── round2_nlp.md
├── round2_stats.md
├── round2_editor.md
├── round2_summary.md
└── DISCUSSION_LOG_20260406.md   ← this file
```
