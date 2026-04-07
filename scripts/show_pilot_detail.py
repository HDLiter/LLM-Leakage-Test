"""Show detailed pilot inputs/outputs for every case: original article,
all rewrites, all model responses, and CFLS scores."""
import json
from pathlib import Path

d = json.loads(Path("data/results/pilot_results.json").read_text(encoding="utf-8"))
cases = d["cases"]
seed = json.loads(Path("data/seed/test_cases.json").read_text(encoding="utf-8"))
tc_map = {tc["id"]: tc for tc in seed["test_cases"]}

COND_NAMES = ["original", "semantic_reversal", "neutral_paraphrase", "false_outcome_cpt"]
TASKS = ["direct_prediction.base", "decomposed_impact.base"]

for ci, case in enumerate(cases):
    cid = case["case_id"]
    tc = tc_map.get(cid, {})
    news = tc.get("news", {})

    print("=" * 80)
    print(f"[{ci+1}/{len(cases)}] {cid} | {case['target']} ({case['target_type']}) | "
          f"direction={case['expected_direction']} | memo={case['memorization_likelihood']}")
    print(f"CFLS: direct={case['metrics']['cfls_direct']}  impact={case['metrics']['cfls_impact']}")
    print(f"FO flip: direct={case['metrics']['fo_flip_direct']}  impact={case['metrics']['fo_flip_impact']}")
    print(f"Intrusion: direct={case['metrics']['intrusion_direct']}  impact={case['metrics']['intrusion_impact']}")
    print("-" * 80)

    # Show original article
    print(f"\n### ORIGINAL ARTICLE ###")
    print(f"Title: {news.get('title', 'N/A')}")
    print(f"Content: {news.get('content', 'N/A')}")
    print(f"Known outcome: {tc.get('known_outcome', 'N/A')}")

    # Show rewrites from the task results - extract articles from responses
    # We need to look at the conditions that were generated
    # The rewritten articles are embedded in the task responses indirectly
    # Let's look at what each condition's article was by checking CF payloads

    # For direct_prediction, semantic_reversal used sr_direction
    # For decomposed_impact, semantic_reversal used sr_fund_impact
    # But the pilot results don't store conditions directly, only task responses.
    # We can infer the articles from the raw responses.

    # Actually let's just show all responses per task per condition
    for task_id in TASKS:
        task_data = case["tasks"].get(task_id, {})
        cfls = task_data.get("cfls", {})
        print(f"\n{'~' * 40}")
        print(f"### TASK: {task_id} ###")
        print(f"CFLS={cfls.get('cfls')}  mode={cfls.get('mode')}")
        if cfls.get("per_slot"):
            for slot, info in cfls["per_slot"].items():
                print(f"  {slot}: orig={info['orig']} -> cf={info['cf']} / para={info['para']}  excess={info['excess']}")

        responses = task_data.get("responses", {})
        for cond in COND_NAMES:
            resp = responses.get(cond, {})
            if resp.get("skipped"):
                print(f"\n  [{cond}] SKIPPED")
                continue
            parsed = resp.get("parsed_output")
            valid = resp.get("valid", "?")
            errors = resp.get("validation_errors", [])
            print(f"\n  [{cond}] valid={valid}")
            if errors:
                print(f"    errors: {errors}")
            if parsed:
                # Show key fields only
                show = {}
                for k in ["target_echo", "direction", "fund_impact", "shock_impact",
                           "confidence", "sentiment"]:
                    if k in parsed:
                        show[k] = parsed[k]
                print(f"    output: {json.dumps(show, ensure_ascii=False)}")
                # Show evidence
                ev = parsed.get("evidence", [])
                if ev:
                    for e in ev[:2]:
                        if isinstance(e, dict):
                            print(f"    evidence: \"{e.get('quote','')}\" -> {e.get('supports','')}")
                        elif isinstance(e, str):
                            print(f"    evidence: \"{e}\"")
            else:
                raw = resp.get("raw_response", "")
                if raw:
                    print(f"    raw: {str(raw)[:200]}")

    print()
