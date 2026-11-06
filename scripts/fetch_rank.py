#!/usr/bin/env python3
"""Map each board's domain to its Majestic Million rank and write data/rank.csv.
Usage: python3 -I scripts/fetch_rank.py PATH_TO_majestic_million.csv [LIST_DATE]
Download: https://downloads.majestic.com/majestic_million.csv  (Creative Commons BY 3.0, attribute Majestic).
scope = "domain" when the board is the whole site, "section" when it is a subdomain or path of a larger site
(its rank then reflects the larger site and is not comparable)."""
import csv, datetime, pathlib, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SLD = {"co", "com", "gov", "org", "ne", "ac", "edu", "net", "gc", "gouv", "gob", "go"}
def regdom(h):
    p = h.split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in SLD else ".".join(p[-2:])
src = pathlib.Path(sys.argv[1]); date = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
ranks = {}
with open(src, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f): ranks[r["Domain"].lower()] = (int(r["GlobalRank"]), int(r["TldRank"]), int(r["RefSubNets"]))
over = {r["board_id"]: r for r in csv.DictReader(open(ROOT / "data" / "rank_scope.csv", newline="", encoding="utf-8"))}
rows = []
for b in csv.DictReader(open(ROOT / "data" / "job_boards.csv", newline="", encoding="utf-8")):
    if not b["url"]: continue
    u = urllib.parse.urlparse(b["url"]); host = u.netloc.lower().removeprefix("www."); dom = regdom(host)
    scope = "domain" if host == dom and u.path in ("", "/") else "section"
    g = ranks.get(dom)
    if scope == "domain" and b["id"] in over: scope = over[b["id"]]["scope"]
    rows.append({"board_id": b["id"], "domain": dom, "scope": scope, "global_rank": g[0] if g else "", "tld_rank": g[1] if g else "",
                 "ref_subnets": g[2] if g else "", "list_date": date, "source": "Majestic Million (CC BY 3.0)"})
with open(ROOT / "data" / "rank.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(rows)
ranked = [r for r in rows if r["global_rank"] and r["scope"] == "domain"]
print(f"{len(rows)} boards, {len(ranked)} ranked and comparable, {sum(1 for r in rows if r['scope']=='section')} are sections of larger sites, {sum(1 for r in rows if r['scope']=='mixed')} are mixed sites, {sum(1 for r in rows if not r['global_rank'])} not in the top million")
for r in sorted(ranked, key=lambda r: int(r["global_rank"]))[:25]: print(f'{int(r["global_rank"]):>8}  {r["domain"]:28} {r["board_id"]}')
