#!/usr/bin/env python3
"""Turn owner holdings that are not yet entries into entries in data/job_boards.csv.
Usage: python3 scripts/promote_holdings.py [--dry-run]
Staffing, recruiting services, job boards, aggregators and HR technology holdings become entries. Their only evidence is the owner's own listing, so
the source is recorded as weak ("owner_listing") and the entry shows as listed only until it is checked against its own site.
Holdings whose website matches an existing entry are linked to it instead of duplicated. Safe to re-run."""
import csv, pathlib, re, sys, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
TYPE = {"staffing": "staffing", "hr-services": "recruiting-services", "job-board": "board", "aggregator": "aggregator", "hr-tech": "hr-tech"}
SLD = {"co", "com", "gov", "org", "ne", "ac", "edu", "net", "gc", "gouv", "gob", "go"}
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def host(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def regdom(h):
    p = h.split("."); return ".".join(p[-3:]) if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in SLD else ".".join(p[-2:])
def load(n): return list(csv.DictReader(open(DATA / n, newline="", encoding="utf-8")))
def main():
    dry = "--dry-run" in sys.argv
    boards = load("job_boards.csv"); cols = list(boards[0].keys()); owners = {o["id"]: o for o in load("owners.csv")}
    hold = load("ownership.csv"); hcols = list(hold[0].keys()); srcs = load("sources.csv"); scols = list(srcs[0].keys())
    ids = {b["id"] for b in boards}; bydom = {regdom(host(b["url"])): b for b in boards if b["url"]}; byslug = {slug(b["name"]): b for b in boards}
    seen_src = {(s["board_id"], s["field"], s["url"]) for s in srcs}; made = linked = skipped = 0
    for h in hold:
        if h["relation"] == "former" or (h["board_id"] and h["board_id"] in ids): continue
        if h["category"] not in TYPE: skipped += 1; continue
        d = regdom(host(h["holding_url"])) if h["holding_url"] else ""
        ex = (bydom.get(d) if d else None) or byslug.get(slug(h["holding_name"]))
        owner_dom = regdom(host(owners.get(h["owner_id"], {}).get("url", "")))
        if ex is not None: h["board_id"] = ex["id"]; linked += 1; continue
        rid = slug(h["holding_name"]) or "entry"; rid = rid if rid not in ids else f'{rid}-{h["owner_id"]}'
        row = {c: "" for c in cols}
        row.update(id=rid, name=h["holding_name"], url=h["holding_url"] if d and d != owner_dom else "", type=TYPE[h["category"]], markets="", region="Global", parent=owners[h["owner_id"]]["name"],
                   api_status="unknown", partner_program="unknown", confidence="listed-only",
                   notes=f'According to its owner\'s page: "{h["quote"]}"')
        boards.append(row); ids.add(rid); h["board_id"] = rid; made += 1
        if d: bydom[d] = row
        byslug[slug(h["holding_name"])] = row
        key = (rid, "owner_listing", h["source_url"])
        if key not in seen_src: srcs.append({"board_id": rid, "field": "owner_listing", "url": h["source_url"], "title": h["source_title"], "accessed": h["accessed"], "quote": h["quote"], "quote_check": h["quote_check"]}); seen_src.add(key)
    print(f"{made} entries created, {linked} holdings linked to existing entries, {skipped} left as holdings only (other HR categories)")
    if dry: print("dry run, nothing written"); return
    for fn, rows, c in (("job_boards.csv", boards, cols), ("ownership.csv", hold, hcols), ("sources.csv", srcs, scols)):
        with open(DATA / fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=c, lineterminator="\n"); w.writeheader(); w.writerows(rows)
if __name__ == "__main__": main()
