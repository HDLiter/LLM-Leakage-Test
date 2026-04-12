"""Audit Bug 5: probe modality is split by known_outcome_available, not period.

Counts how many cases per (period × known_outcome_available) so we can see
that pre-cutoff cases also go through the generic-template branch when their
known_outcome is empty / 'unknown_post_cutoff'.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"

d = json.loads(PATH.read_text(encoding="utf-8"))
cases = d["cases"]

cnt = Counter((c.get("period"), c.get("known_outcome_available")) for c in cases)
print("(period, known_outcome_available) -> n")
for k, v in sorted(cnt.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    print(f"  {k} -> {v}")

# Cross with anchor_binary
print()
print("(period, known_outcome_available, anchor_binary) -> n")
cnt2 = Counter(
    (c.get("period"), c.get("known_outcome_available"), c.get("anchor_binary"))
    for c in cases
)
for k, v in sorted(cnt2.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
    print(f"  {k} -> {v}")
