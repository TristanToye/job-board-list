#!/usr/bin/env python3
"""Pick the entries most worth a verification pass and write chunked input files for verification agents.
Usage: python3 scripts/sweep_candidates.py [--top 60] [--chunks 6] [--stamp YYYY-MM-DD] [--skip-days 14]
Priority = prominence weight x number of missing key facts. Entries reviewed within --skip-days are skipped."""
import csv, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
def arg(n, d): return type(d)(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d
top, chunks, skip = arg("--top", 60), arg("--chunks", 6), arg("--skip-days", 14); stamp = arg("--stamp", datetime.date.today().isoformat()); name = arg("--name", "sweep")
def load(n):
    p = ROOT / "data" / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []
rank = {r["board_id"]: r for r in load("rank.csv")}; reviews = {r["board_id"]: r for r in load("reviews.csv")}
today = datetime.date.fromisoformat(stamp)
# boards already queued for a browser run on the owner's machine would only be refused again here
queued = {x["name"] for f in (ROOT / "research" / "findings").glob("*browser-sweep-input.json") for x in json.load(open(f, encoding="utf-8")).get("boards", [])}
# boards the refinement loop already found blocked or unreachable would only be refused again
import collections
_blk = collections.defaultdict(int)
for _a in load("attempts.csv"):
    if _a["outcome"] == "blocked": _blk[_a["board_id"]] += 1
import re as _re
for _f in load("loop_flags.csv"):
    if _re.search(r"blocked|cloudflare|403|503|not readable|cannot be read|cannot be checked|unavailable|404|dead|gambling|no longer", _f["flag"], _re.I): _blk[_f["board_id"]] += 1
def weight(i):
    r = rank.get(i)
    if not r or not r["global_rank"]: return 1
    g = int(r["global_rank"]); base = 5 if g <= 1000 else 4 if g <= 10000 else 3 if g <= 100000 else 2
    return base if r["scope"] == "domain" else 1.5
cands = []
for b in load("job_boards.csv"):
    if not b["url"] or b["name"] in queued: continue
    rv = reviews.get(b["id"])
    if "--unreviewed" in sys.argv and rv: continue
    if _blk.get(b["id"]): continue
    if rv and (today - datetime.date.fromisoformat(rv["reviewed"])).days < skip: continue
    miss = [k for k, empty in (("hq_country", not b["hq_country"]), ("languages", not b["primary_language"]), ("business_model", not b["business_model"]),
            ("api_status", b["api_status"] == "unknown"), ("partner_program", b["partner_program"] == "unknown"), ("parent", not b["parent"]), ("ingest_methods", not b["ingest_methods"])) if empty]
    if miss: cands.append((weight(b["id"]) * len(miss), b, miss))
cands.sort(key=lambda x: -x[0]); picked = cands[:top]
out = pathlib.Path(ROOT / "research" / "findings")
for i in range(chunks):
    part = picked[i::chunks]
    if part: json.dump({"country": "ZZ", "boards": [{"name": b["name"], "url": b["url"], "missing": m} for _, b, m in part]}, open(out / f"{stamp}-{name}-{i + 1}-input.json", "w", encoding="utf-8"), indent=1)
print(f"{len(cands)} candidates with gaps, {len(picked)} picked in {min(chunks, len(picked))} chunks")
for sc, b, m in picked[:12]: print(f"  {sc:5.1f}  {b['name']:30} missing {','.join(m)}")
