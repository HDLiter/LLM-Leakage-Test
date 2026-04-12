"""One-off: dump structure of diagnostic_2_results.json for audit scripts."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"

d = json.loads(PATH.read_text(encoding="utf-8"))
cases = d["cases"]
print("n_cases:", len(cases))
print()
c0 = cases[0]
print("case keys:", list(c0.keys()))
print("metrics:", c0.get("metrics"))
print()
ts = c0["tasks"]
print("task ids:", list(ts.keys()))
t = ts["direct_prediction.base"]
print("direct_prediction.base keys:", list(t.keys()))
print("cfls:", t["cfls"])
print()
print("responses keys:", list(t["responses"].keys()))
for k, v in t["responses"].items():
    print(" ", k, "valid=", v.get("valid"), "skipped=", v.get("skipped"),
          "parsed_output=", v.get("parsed_output"))

print()
print("=== condition_summary check ===")
print("c0 condition_summary?", "condition_summary" in c0)
if "condition_summary" in c0:
    print(json.dumps(c0["condition_summary"], indent=2, ensure_ascii=False)[:1000])
print()
print("aggregated keys:", list(d["aggregated"].keys()))
print("stratified keys:", list(d["stratified"].keys()) if d.get("stratified") else None)
