#!/usr/bin/env python3
"""Validate data files and print a coverage summary. Usage: python3 scripts/validate.py"""
import csv, sys, collections, pathlib
D = pathlib.Path(__file__).resolve().parent.parent / "data"
API = {"on-request","public-open","public-key","partner-only","deprecated","none-known","unknown"}
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
import re
for r in boards:
    codes = [r["primary_language"]] + [x for x in r["languages_supported"].split(";") if x]
    if not r["primary_language"]: print(f"board {r['id']}: missing primary_language"); bad += 1
    for cd in codes:
        if not re.fullmatch(r"[a-z]{2,3}", cd): print(f"board {r['id']}: bad language code {cd!r}"); bad += 1
    if r["languages_supported"] and r["primary_language"] not in r["languages_supported"].split(";"):
        print(f"board {r['id']}: primary language not in languages_supported"); bad += 1
src = load("sources.csv"); ids = {r["id"] for r in boards}
for x in src:
    if x["board_id"] not in ids: print(f"source: unknown board {x['board_id']}"); bad += 1
    if not x["url"].startswith("https://"): print(f"source {x['board_id']}: bad url {x['url']!r}"); bad += 1
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["accessed"]): print(f"source {x['board_id']}: bad date {x['accessed']!r}"); bad += 1
sourced = {x["board_id"] for x in src}
for r in boards:
    if (r["id"] in sourced) != (r["confidence"] != "seed-unverified"): print(f"board {r['id']}: confidence does not match sources"); bad += 1
    for cd in r["countries_served"].split(";"):
        if cd and not re.fullmatch(r"[A-Z]{2}", cd): print(f"board {r['id']}: bad country code {cd!r}"); bad += 1
c = collections.Counter
print(f"{len(boards)} boards, {len(ats)} ATS")
print("api_status:", dict(c(r["api_status"] for r in boards)))
print("region:", dict(c(r["region"] for r in boards)))
print("primary_language:", dict(c(r["primary_language"] for r in boards)))
print("with cited sources:", len(sourced), "/", len(boards), "|", len(src), "citations")
sys.exit(1 if bad else 0)
