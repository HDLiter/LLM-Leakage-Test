# Pilot Implementation Plan: E_pilot (50-100 case hard pilot)

## Context

Proposal v2 passed 3-round multi-agent review. Round 3 key decisions require a same-template bridge: `direct_prediction` vs `decomposed_impact` both under `semantic_reversal`, plus false-outcome CPT as core. This pilot validates template comparability, effect shape, and scoring pipeline before scaling to 1000 cases.

## Codex vs Claude Code

**Recommendation: Claude Code directly, Codex (xhigh) for two specific subtasks.**

The work is mostly well-defined Python implementation following a clear spec -- CC's strength. Codex (always xhigh) adds value for:
1. **Data annotation** (Phase 0): Use Codex xhigh to propose `target`/`target_type` for all 42 existing cases from article text (batch reasoning task)
2. **False-outcome CPT prompt design** (Phase 4): Use Codex xhigh for creative prompt engineering -- designing plausible false-outcome injection phrasing

All Codex calls use `config: {"model_reasoning_effort": "xhigh"}` (user has Pro plan).

---

## Phase 0: Data Preparation

### 0A. Annotate existing 42 cases with `target` + `target_type`
- **File**: `data/seed/test_cases.json`
- Add `target: str` (primary entity/ticker/index) and `target_type: "company"|"sector"|"index"` to each case
- Use Codex (Spark) to propose from article + key_entities + sector, human-verify
- Example: tc_001 (央行降准) -> `target: "A股大盘"`, `target_type: "index"`

### 0B. Expand to ~75 cases (optional, can start pilot with 42)
- Source: CLS telegraph corpus (`D:\GitRepos\Thales\datasets\cls_telegraph_raw`)
- Balance: ~40% company, ~30% sector, ~30% index; balanced direction; mix of memorization_likelihood

---

## Phase 1: Model Layer (`src/models.py`)

### 1A. Add fields to `TestCase` (line ~88)
```python
target: str = ""
target_type: str = ""  # company|sector|index
```
Default empty string for backward compatibility with existing JSON.

### 1B. Add `FALSE_OUTCOME_CPT` to `VariantType` enum (line ~25)
```python
FALSE_OUTCOME_CPT = "false_outcome_cpt"
```
Do NOT add to `active_counterfactuals()` -- it's code-level, not YAML-template-backed.

---

## Phase 2: Config Layer

### 2A. `config/prompts/counterfactual_templates.yaml`
- **semantic_reversal** (line 71): add `decomposed_impact.base` and `decomposed_impact.matched` to `applicable_to`; add `E_pilot` to experiments
- **neutral_paraphrase** (line 167): add `decomposed_impact.base` and `decomposed_impact.matched` to `applicable_to`; add `E_pilot` to experiments

### 2B. `config/prompts/task_prompts.yaml`
- `direct_prediction.base` (line 65): add `E_pilot` to experiments list
- `direct_prediction.matched` (line 118): add `E_pilot`
- `decomposed_impact.base` (line 494): add `E_pilot`
- `decomposed_impact.matched` (line 564): add `E_pilot`

### 2C. `config/prompts/README.md`
- Update line 42 and line 114: reflect that decomposed_impact is now included for E_pilot (same-template bridge per Round 3 decision)

---

## Phase 3: CFLS Scoring (`src/metrics.py`)

### 3A. Slot-level comparison helper (~line 209)
- `_extract_slots(parsed_output: dict) -> dict | None`: extract fund_impact/shock_impact/direction from parsed JSON
- Handle both base format (named keys) and matched format (slot_1/slot_2/slot_3)

### 3B. Per-case CFLS scoring
```python
def cfls_per_case(
    orig: dict,          # parsed task output on original article
    cf_reversal: dict,   # parsed task output on semantic_reversal article
    para: dict,          # parsed task output on neutral_paraphrase article
    cf_false_outcome: dict | None = None,  # parsed output on false-outcome CPT article
    task_id: str = "",
) -> dict:
```
- Computes slot-level invariance: `cf_inv = (slots unchanged under reversal)`, `para_inv = (slots unchanged under paraphrase)`
- CFLS = cf_inv - para_inv (positive = suspicious stability = possible leakage)
- If false_outcome provided: check if prediction aligns with false outcome (sign-flip = leakage evidence)
- Returns: `{cfls, per_slot: {field: {cf_inv, para_inv, excess}}, false_outcome_flip: bool|None}`

### 3C. Batch CFLS aggregation
```python
def batch_cfls(cases: list[dict]) -> dict:
```
- Group by task_id, compute mean/std/distribution per task and overall
- Return comparison dict: `{by_task: {direct_prediction: {...}, decomposed_impact: {...}}, overall: {...}, correlation: float}`

### 3D. Evidence intrusion detection (rule-based for pilot)
```python
def detect_evidence_intrusion(
    article: str, response: dict, known_outcome: str, outcome_date: str
) -> dict:
```
- Check model response for: dates post-outcome_date, price values not in article, verbatim outcome keywords
- Returns: `{detected: bool, flags: [{type, evidence, detail}]}`

---

## Phase 4: False-Outcome CPT (`src/masking.py`)

### 4A. Add generation function (after existing CF functions)
```python
def generate_false_outcome_cpt(
    article: str, known_outcome: str, expected_direction: str, target: str
) -> str:
```
- Appends a subtle false-outcome hint to the article text
- Flips direction: if expected_direction=up, inject hint suggesting negative outcome
- Template: `"（注：据了解，{target}后续{false_outcome_summary}。）"` appended to article
- `false_outcome_summary` derived from flipping `expected_direction` with domain-appropriate phrasing

### 4B. Use Codex (xhigh) to design the false-outcome phrasing templates
- Need ~5 phrasing variants to avoid template detection by the model
- Must be plausible, subtle, and not too long (CLS telegraph style)

---

## Phase 5: Pilot Runner (NEW: `src/pilot.py`)

### 5A. Core structure (~200 lines)

```python
def prepare_conditions(client, loader, case) -> dict[str, str]:
    """Generate 4 article variants: original, semantic_reversal, neutral_paraphrase, false_outcome_cpt"""

def run_single_case(client, loader, case, conditions) -> dict:
    """Run direct_prediction.base + decomposed_impact.base on all 4 conditions -> 8 responses"""

def run_pilot(client, loader, cases, output_path, max_concurrency=20) -> dict:
    """Orchestrate: prepare conditions -> run all cases -> compute metrics -> save"""
```

### 5B. Execution flow per case
1. Generate `semantic_reversal` CF (1 API call -- for direct_prediction's `direction` field)
2. Generate `semantic_reversal` CF (1 API call -- for decomposed_impact's `fund_impact` field)
3. Generate `neutral_paraphrase` CF (1 API call -- shared across tasks)
4. Generate `false_outcome_cpt` (0 API calls -- code-level)
5. Run `direct_prediction.base` x 4 conditions (4 API calls)
6. Run `decomposed_impact.base` x 4 conditions (4 API calls)
7. Compute CFLS per task, evidence intrusion (0 API calls)
=> **10 API calls per case** (CF generation) + **8 API calls per case** (task execution) = **~18 per case**

### 5C. For 75 cases: ~1350 API calls total (cached on rerun)

### 5D. Output format
```json
{
  "meta": {"experiment": "E_pilot", "n_cases": 75, "timestamp": "..."},
  "cases": [{
    "case_id": "tc_001", "target": "A股大盘", "target_type": "index",
    "conditions": {
      "original": {"direct_prediction.base": {...}, "decomposed_impact.base": {...}},
      "semantic_reversal": {...},
      "neutral_paraphrase": {...},
      "false_outcome_cpt": {...}
    },
    "metrics": {
      "cfls_direct": 0.35, "cfls_impact": 0.12,
      "per_slot": {...}, "false_outcome_flip": true,
      "evidence_intrusion": {"detected": false, "flags": []}
    }
  }],
  "aggregated": {"mean_cfls_direct": ..., "mean_cfls_impact": ..., "correlation": ...}
}
```

### 5E. CLI entry point
```bash
python -m src.pilot --n-cases 75 --output data/results/pilot_results.json
```

---

## Phase 6: Smoke Test Updates (`tests/smoke_test_prompts.py`)

### 6A. Add to TASK_IDS (line 26)
```python
"decomposed_impact.base",
"decomposed_impact.matched",
```

### 6B. Fix `run_task_safe` (line 222)
- Add `target` and `target_type` params, forward to `loader.render_user_prompt()`
- Currently missing -- would fail on any prompt using `{target}` placeholder

### 6C. Update callers in `main()` (line ~628)
- Pass `test_case.target` and `test_case.target_type` (with `getattr` fallback for safety)

### 6D. Add impact reversal to `run_counterfactual_check` (line ~453)
- Add a second check running `decomposed_impact.base` with semantic_reversal alongside the existing direct_prediction check

---

## Execution Order (dependency-aware)

```
Phase 0A (annotate target) ──────────────┐
Phase 1  (models.py)      ── parallel ───┤
Phase 2  (YAML configs)   ── parallel ───┤
                                         ▼
Phase 3  (metrics.py)     ── depends on 1A
Phase 4  (false-outcome)  ── depends on 1B
Phase 6  (smoke test)     ── depends on 1+2
                                         ▼
Phase 5  (pilot.py)       ── depends on ALL above
                                         ▼
Phase 7  (integration)    ── dry run 3 cases, then full 75
```

Phases 0A, 1, 2 are independent -- implement in parallel.
Phases 3, 4, 6 depend on 1 -- implement in parallel after Phase 1.
Phase 5 is the final assembly.

---

## Verification Plan

| Milestone | How to verify |
|-----------|---------------|
| Phase 1 done | `python -c "from src.models import TestCase; t = TestCase(..., target='X', target_type='index'); print(t.target)"` |
| Phase 2 done | `python -c "from src.prompt_loader import PromptLoader; p=PromptLoader(); print(p.get_counterfactual_template('semantic_reversal').applicable_to)"` -> includes decomposed_impact |
| Phase 3 done | Unit test with mock responses: case with unchanged label -> CFLS > 0; case with flipped label -> CFLS <= 0 |
| Phase 6 done | `python tests/smoke_test_prompts.py` passes all tasks including decomposed_impact |
| Phase 5+7 | Dry run on 3 cases: `python -m src.pilot --n-cases 3 --output data/results/pilot_dry_run.json` |
| Full pilot | `python -m src.pilot --n-cases 75 --output data/results/pilot_results.json` |

---

## Key Files Modified/Created

| File | Action |
|------|--------|
| `src/models.py` | Edit: +target, +target_type, +FALSE_OUTCOME_CPT |
| `config/prompts/counterfactual_templates.yaml` | Edit: extend applicable_to |
| `config/prompts/task_prompts.yaml` | Edit: add E_pilot to experiment lists |
| `config/prompts/README.md` | Edit: update exclusion notes |
| `src/metrics.py` | Edit: +cfls_per_case, +batch_cfls, +detect_evidence_intrusion |
| `src/masking.py` | Edit: +generate_false_outcome_cpt |
| `src/pilot.py` | **NEW**: pilot runner (~200 lines) |
| `tests/smoke_test_prompts.py` | Edit: +decomposed_impact tasks, fix target params |
| `data/seed/test_cases.json` | Edit: +target/target_type fields on all cases |
