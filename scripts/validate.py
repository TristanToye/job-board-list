#!/usr/bin/env python3
"""Validate data files and print a coverage summary. Usage: python3 scripts/validate.py"""
import csv, sys, collections, pathlib
D = pathlib.Path(__file__).resolve().parent.parent / "data"
API = {"public-open","public-key","partner-only","deprecated","none-known","unknown"}
bad = 0
def load(n):
    with open(D/n, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
boards, ats = load("job_boards.csv"), load("ats_systems.csv")
for name, rows in (("job_boards", boards), ("ats_systems", ats)):
    ids = [r["id"] for r in rows]
    for i in {x for x in ids if ids.count(x) > 1}: print(f"{name}: duplicate id {i}"); bad += 1
    for r in rows:
        if None in r or None in r.values(): print(f"{name}: bad column count at {r['id']}"); bad += 1
for r in boards:
    if r["api_status"] not in API: print(f"board {r['id']}: bad api_status {r['api_status']!r}"); bad += 1
c = collections.Counter
print(f"{len(boards)} boards, {len(ats)} ATS")
print("api_status:", dict(c(r["api_status"] for r in boards)))
print("region:", dict(c(r["region"] for r in boards)))
print("verified:", sum(r["confidence"] != "seed-unverified" for r in boards), "/", len(boards))
sys.exit(1 if bad else 0)
