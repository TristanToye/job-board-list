#!/usr/bin/env python3
"""Merge guide findings (mode "guide") into data/guide_facts.csv: short cited facts used on guide pages, such as the OFCCP and VEVRAA posting rules.
Usage: python3 scripts/ingest_guide.py FINDINGS.json [...] [--dry-run]
A fact is kept only if it has a claim, a source URL and a quote of 3 to 30 words that was found on the page."""
import csv, json, pathlib, re, sys, datetime, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; TODAY = datetime.date.today().isoformat()
COLS = ["guide", "topic", "claim", "source_url", "source_title", "quote", "quote_check", "accessed"]
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]
def clean(s, n=400): return str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()[:n]
def main(argv):
    dry = "--dry-run" in argv; files = [a for a in argv if a.endswith(".json")]
    p = DATA / "guide_facts.csv"; rows = list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []
    have = {(r["guide"], r["quote"]) for r in rows}; stats = collections.Counter(); rej = []
    for fn in files:
        d = json.load(open(fn, encoding="utf-8")); g = clean(d.get("guide"), 40)
        for f in d.get("facts", []):
            s = f.get("source") or {}; q = clean(s.get("quote")); claim = clean(f.get("claim"), 300)
            why = None
            if not g or not claim: why = "no guide or claim"
            elif not re.match(r"https?://", s.get("url") or ""): why = "no source url"
            elif not 3 <= len(q.split()) <= 30: why = "quote length"
            elif s.get("check") != "ok": why = "quote not confirmed on page"
            elif re.search("|".join(BLOCKED_WORDS), json.dumps(f, ensure_ascii=False), re.I): why = "branded text"
            if why: rej.append((claim[:60], why)); stats["rejected"] += 1; continue
            if (g, q) in have: stats["duplicate"] += 1; continue
            rows.append({"guide": g, "topic": clean(f.get("topic"), 80), "claim": claim, "source_url": s["url"], "source_title": clean(s.get("title"), 160), "quote": q, "quote_check": "ok", "accessed": s.get("accessed") or TODAY})
            have.add((g, q)); stats["added"] += 1
    print(dict(stats)); [print("  rejected:", *x) for x in rej]
    if not dry:
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
if __name__ == "__main__": main(sys.argv[1:])
