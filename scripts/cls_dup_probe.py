# -*- coding: utf-8 -*-
"""
C-4 probe: does the CLS telegraph archive contain intra-day repost-spam?

For every daily file, detect items whose (boilerplate-stripped) content is an
exact or near-duplicate of an EARLIER item the SAME day. Reports the duplication
rate, the time gap between a dup and its match, a per-year breakdown, and the
biggest dup clusters for eyeballing.

If the intra-day dup rate is low, the no-dedup recurrence count is fine as-is and
the C-4 sensitivity machinery can be dropped entirely.
"""
import json, re, glob, os, statistics
from difflib import SequenceMatcher
from collections import Counter, defaultdict

DATA = r"D:/GitRepos/LLM-Leakage-Test/data/cls_telegraph_raw"
NEAR = 0.85          # SequenceMatcher ratio threshold for "near duplicate"
PREFIX = 14          # block key length (chars of normalized content)

date_boiler = re.compile(r'财联社\d{1,2}月\d{1,2}日电[，,：:\s]*')
title_brk   = re.compile(r'^【[^】]*】')
ws          = re.compile(r'\s+')

def norm(c):
    s = title_brk.sub('', (c or '').strip())
    s = date_boiler.sub('', s)
    return ws.sub('', s)

files = sorted(glob.glob(os.path.join(DATA, "*.json")))
TOT = EMPTY = EXACT = NEAR_N = 0
gaps = []                       # minutes between a dup and its matched earlier item
clusters = []                   # (day, cluster_size, sample_text)
per_year = defaultdict(lambda: [0, 0])   # year -> [items, dups]
items_per_day = []

for k, fp in enumerate(files):
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        continue
    day = d.get('date', os.path.basename(fp)[:10])
    year = day[:4]
    recs = [(norm(it.get('content', '')), it.get('timestamp', 0) or 0, it.get('content', ''))
            for it in d.get('items', [])]
    TOT += len(recs)
    items_per_day.append(len(recs))
    per_year[year][0] += len(recs)

    seen_exact = {}             # normalized content -> first idx
    block = defaultdict(list)   # prefix -> [idx] of non-exact-dup items
    daydup = defaultdict(list)  # representative idx -> [dup idxs]

    for i, (n, ts, raw) in enumerate(recs):
        if not n:
            EMPTY += 1
            continue
        if n in seen_exact:                       # exact duplicate
            j = seen_exact[n]
            EXACT += 1
            per_year[year][1] += 1
            gaps.append(abs(ts - recs[j][1]) / 60.0)
            daydup[j].append(i)
            continue
        hit = None                                # near duplicate within prefix block
        for j in block[n[:PREFIX]]:
            if SequenceMatcher(None, n, recs[j][0]).ratio() >= NEAR:
                hit = j
                break
        if hit is not None:
            NEAR_N += 1
            per_year[year][1] += 1
            gaps.append(abs(ts - recs[hit][1]) / 60.0)
            daydup[hit].append(i)
        seen_exact[n] = i
        block[n[:PREFIX]].append(i)

    for rep, dups in daydup.items():
        clusters.append((day, len(dups) + 1, recs[rep][2][:90]))

DUP = EXACT + NEAR_N
print("=" * 64)
print("CLS intra-day duplication probe")
print("=" * 64)
print(f"daily files processed : {len(files)}")
print(f"total items           : {TOT:,}")
print(f"empty after normalize : {EMPTY:,}")
print(f"items/day  min/med/max : {min(items_per_day)} / "
      f"{int(statistics.median(items_per_day))} / {max(items_per_day)}")
print("-" * 64)
print(f"exact intra-day dups  : {EXACT:,}  ({100*EXACT/TOT:.2f}% of all items)")
print(f"near  intra-day dups  : {NEAR_N:,}  ({100*NEAR_N/TOT:.2f}% of all items)")
print(f"TOTAL intra-day dups  : {DUP:,}  ({100*DUP/TOT:.2f}% of all items)")
print("-" * 64)
if gaps:
    gaps_sorted = sorted(gaps)
    within = lambda m: 100 * sum(g <= m for g in gaps) / len(gaps)
    print(f"dup->match time gap   : median {statistics.median(gaps):.1f} min")
    print(f"   within 10 min      : {within(10):.1f}%")
    print(f"   within 60 min      : {within(60):.1f}%")
    print(f"   within 6 h         : {within(360):.1f}%")
print("-" * 64)
print("per-year duplication rate:")
for y in sorted(per_year):
    it, du = per_year[y]
    if it:
        print(f"  {y}: {du:>6,} / {it:>8,}  ({100*du/it:.2f}%)")
print("-" * 64)
print("top 15 intra-day dup clusters (size = #items in cluster):")
for day, sz, sample in sorted(clusters, key=lambda x: -x[1])[:15]:
    print(f"  {day}  x{sz:<3}  {sample}")
print("=" * 64)
