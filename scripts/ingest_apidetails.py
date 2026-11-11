#!/usr/bin/env python3
"""Merge API detail findings (mode "api-details") into data/api_details.csv.
Usage: python3 scripts/ingest_apidetails.py FINDINGS.json [...] [--dry-run]
A fact is kept only if the entry exists, the field is allowed, the quote is 3 to 30 words and was found on its page, and the source
is on a domain tied to the entry (its site, its other domains, its API docs or partner link). An existing fact is never overwritten."""
import csv, json, pathlib, re, sys, datetime, urllib.parse, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; TODAY = datetime.date.today().isoformat()
FIELDS = {"access", "auth", "formats", "scope", "limits", "cost", "approval", "sandbox", "feed"}
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]
COLS = ["board_id", "field", "value", "source_url", "source_title", "quote", "quote_check", "accessed"]
def host(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def regdom(h):
    p = h.split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in {"co", "com", "gov", "org", "ne", "ac", "edu", "net", "gc", "gouv", "gob", "go"} else ".".join(p[-2:])
def clean(s, n=200): return str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()[:n]
def bad(s): return bool(re.search("|".join(BLOCKED_WORDS), s or "", re.I))
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []

def main(argv):
    dry = "--dry-run" in argv; files = [a for a in argv if a.endswith(".json")]
    boards = {b["id"]: b for b in load("job_boards.csv")}; rows = load("api_details.csv")
    have = {(r["board_id"], r["field"]) for r in rows}; stats = collections.Counter(); rej = []
    for fn in files:
        d = json.load(open(fn, encoding="utf-8"))
        for en in d.get("entries", []):
            b = boards.get(en.get("id") or "")
            if not b: stats["unknown entry"] += 1; continue
            ok_dom = {regdom(host(u)) for u in [b["url"], b["api_docs_url"], b["partner_url"]] + b["domains"].replace(";", " ").split() if u}
            ok_dom |= {regdom(x) for x in b["domains"].replace(";", " ").split() if x}
            for f in en.get("facts", []):
                fld = (f.get("field") or "").strip().lower(); s = f.get("source") or {}; q = clean(s.get("quote"), 400); url = (s.get("url") or "").strip(); val = clean(f.get("value"))
                why = None
                if fld not in FIELDS: why = f"field {fld!r}"
                elif not val: why = "no value"
                elif not re.match(r"https?://", url): why = "no source url"
                elif not 3 <= len(q.split()) <= 30: why = "quote length"
                elif s.get("check") not in ("ok", "chrome"): why = "quote not confirmed on page"
                elif regdom(host(url)) not in ok_dom: why = f"source off the entry's domains: {host(url)}"
                elif bad(json.dumps(f, ensure_ascii=False)): why = "branded text"
                if why: rej.append((b["name"], fld, why)); stats["rejected"] += 1; continue
                if (b["id"], fld) in have: stats["duplicate"] += 1; continue
                rows.append({"board_id": b["id"], "field": fld, "value": val, "source_url": url, "source_title": clean(s.get("title"), 160), "quote": q, "quote_check": s.get("check"), "accessed": s.get("accessed") or TODAY})
                have.add((b["id"], fld)); stats["added"] += 1
    print(dict(stats)); [print("  rejected:", *x) for x in rej]
    if not dry:
        rows.sort(key=lambda r: (r["board_id"], r["field"]))
        with open(DATA / "api_details.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
if __name__ == "__main__": main(sys.argv[1:])
