#!/usr/bin/env python3
"""Merge ownership findings (mode "ownership") into data/owners.csv and data/ownership.csv.
Usage: python3 scripts/ingest_ownership.py FINDINGS.json [...] [--dry-run]
A holding is accepted only with a source quote of 30 words or fewer that was confirmed on the page.
Sources must be on the owner's domain, the holding's domain, or a reference site (Wikipedia, Wikidata).
Reference sources must have been confirmed (check "ok")."""
import csv, json, pathlib, re, sys, datetime, urllib.parse, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; TODAY = datetime.date.today().isoformat()
RELATIONS = {"subsidiary", "brand", "majority-stake", "minority-stake", "joint-venture", "former"}
CATEGORIES = {"job-board", "aggregator", "staffing", "hr-tech", "hr-services", "data-research", "other-hr"}
REFERENCE = {"wikipedia.org", "wikidata.org"}
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]
OCOLS = ["id", "name", "url", "country"]
HCOLS = ["owner_id", "holding_name", "holding_url", "board_id", "relation", "stake", "since", "category", "source_url", "source_title", "quote", "quote_check", "accessed"]

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def host(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def regdom(h):
    p = h.split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in {"co", "com", "gov", "org", "ne", "ac", "edu", "net"} else ".".join(p[-2:])
def clean(s, n=300): return str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()[:n]
def bad(s): return bool(re.search("|".join(BLOCKED_WORDS), s or "", re.I))
def owner_id(name):
    n = re.sub(r"\b(co|ltd|inc|corp|corporation|company|limited|plc|n\.v|nv|ag|se|group|holdings?)\b\.?", " ", name.lower())
    return slug(n) or slug(name)
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []
def save(n, rows, cols):
    with open(DATA / n, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)

def main(argv):
    dry = "--dry-run" in argv; files = [a for a in argv if a.endswith(".json")]
    owners = {r["id"]: r for r in load("owners.csv")}; holds = load("ownership.csv"); boards = load("job_boards.csv")
    bydom = {regdom(host(b["url"])): b["id"] for b in boards if b["url"]}; byid = {b["id"] for b in boards}
    have = {(h["owner_id"], slug(h["holding_name"]), h["relation"]) for h in holds}
    stats = collections.Counter(); rej = []
    for fn in files:
        d = json.load(open(fn, encoding="utf-8"))
        if d.get("mode") != "ownership": print(fn, "bad mode"); continue
        for o in d.get("owners", []):
            name = clean(o.get("name"), 80); oid = owner_id(name)
            if not name or not oid or bad(json.dumps(o)): rej.append(("owner", name, "missing or disallowed")); continue
            ourl = clean(o.get("url"), 200); odom = regdom(host(ourl))
            if oid not in owners: owners[oid] = {"id": oid, "name": name, "url": ourl, "country": clean(o.get("country"), 2).upper()}; stats["owners"] += 1
            for h in o.get("holdings", []):
                hn = clean(h.get("name"), 80); hurl = clean(h.get("url"), 200); rel = clean(h.get("relation"), 20).lower(); cat = clean(h.get("category"), 20).lower()
                if not hn or rel not in RELATIONS or cat not in CATEGORIES or bad(json.dumps(h)): rej.append(("holding", hn, f"bad name, relation {rel!r} or category {cat!r}")); stats["rejected"] += 1; continue
                if hurl and not hurl.startswith("http"): hurl = ""
                stake = clean(h.get("stake"), 8).replace("%", "").strip(); stake = stake if re.fullmatch(r"\d{1,3}(\.\d+)?", stake) and float(stake) <= 100 else ""
                since = clean(h.get("since"), 4); since = since if re.fullmatch(r"(19|20)\d\d", since) else ""
                hdom = regdom(host(hurl)) if hurl else ""
                good = []
                for s in h.get("sources", []):
                    su, q = clean(s.get("url"), 300), clean(s.get("quote"), 300); sd = regdom(host(su)); chk = s.get("check", "")
                    if not su.startswith("http") or not q or len(q.split()) > 30 or chk == "mismatch": rej.append(("source", hn, "bad url or quote")); continue
                    if sd in REFERENCE:
                        if chk not in ("ok", "structured"): rej.append(("source", hn, "reference quote not confirmed")); continue
                    elif sd not in {odom, hdom}: rej.append(("source", hn, f"source off domain {sd}")); continue
                    good.append((su, clean(s.get("title"), 120), q, chk))
                if not good: rej.append(("holding", hn, "no usable source")); stats["rejected"] += 1; continue
                key = (oid, slug(hn), rel)
                if key in have: stats["duplicate"] += 1; continue
                bid = bydom.get(hdom) or (slug(hn) if slug(hn) in byid else "")
                su, st, q, chk = good[0]
                holds.append({"owner_id": oid, "holding_name": hn, "holding_url": hurl, "board_id": bid, "relation": rel, "stake": stake, "since": since,
                              "category": cat, "source_url": su, "source_title": st, "quote": q, "quote_check": chk, "accessed": TODAY})
                have.add(key); stats["added"] += 1
    print(dict(stats), "rejections:", len(rej))
    for k, n, w in rej[:30]: print("  reject", k, n, "|", w)
    if dry: print("dry run, nothing written"); return
    save("owners.csv", list(owners.values()), OCOLS); save("ownership.csv", holds, HCOLS)
if __name__ == "__main__": main(sys.argv[1:])
