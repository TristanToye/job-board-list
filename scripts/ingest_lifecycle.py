#!/usr/bin/env python3
"""Merge lifecycle findings (mode "lifecycle") into data/lifecycle.csv: sites and companies that closed, were acquired, merged or rebranded.
Usage: python3 scripts/ingest_lifecycle.py FINDINGS.json [...] [--dry-run]
An event is kept only if it has a status from the allowed list, a source quote of 3 to 30 words that was not a mismatch, and no brand words."""
import csv, json, pathlib, re, sys, datetime, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; TODAY = datetime.date.today().isoformat()
STATUSES = {"closed", "acquired", "merged", "rebranded"}
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]
COLS = ["id", "name", "board_id", "url", "type", "country", "status", "year", "successor_id", "successor_name", "note", "source_url", "source_title", "quote", "quote_check", "accessed"]
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def clean(s, n=400): return str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()[:n]
def bad(s): return bool(re.search("|".join(BLOCKED_WORDS), s or "", re.I))
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []

def main(argv):
    dry = "--dry-run" in argv; files = [a for a in argv if a.endswith(".json")]
    boards = load("job_boards.csv"); rows = load("lifecycle.csv")
    byid = {b["id"]: b for b in boards}; byslug = {}
    for b in boards: byslug.setdefault(slug(b["name"]), b)
    have = {r["id"] for r in rows}; stats = collections.Counter(); rej = []
    for fn in files:
        d = json.load(open(fn, encoding="utf-8"))
        for ev in d.get("events", []):
            name = clean(ev.get("name"), 120); st = (ev.get("status") or "").strip().lower(); s = ev.get("source") or {}
            q = clean(s.get("quote"), 400); url = (s.get("url") or "").strip()
            why = None
            if not name: why = "no name"
            elif st not in STATUSES: why = f"status {st!r}"
            elif not re.match(r"https?://", url): why = "no source url"
            elif not 3 <= len(q.split()) <= 30: why = "quote length"
            elif s.get("check") == "mismatch": why = "quote not found on page"
            elif s.get("check") not in ("ok", "chrome"): why = "page not readable, quote unchecked"
            elif bad(json.dumps(ev, ensure_ascii=False)): why = "branded text"
            elif ev.get("year") and not re.fullmatch(r"\d{4}", str(ev["year"])): why = "year"
            if why: rej.append((name, why)); stats["rejected"] += 1; continue
            hit = byid.get(ev.get("id") or "") or byslug.get(slug(name))
            rid = hit["id"] if hit else slug(name)
            if rid in have: stats["duplicate"] += 1; continue
            succ = clean(ev.get("successor"), 120); sh = byslug.get(slug(succ)) if succ else None
            rows.append({"id": rid, "name": hit["name"] if hit else name, "board_id": hit["id"] if hit else "", "url": clean(ev.get("url") or (hit or {}).get("url", ""), 200),
                         "type": clean(ev.get("type") or (hit or {}).get("type", ""), 40), "country": clean(ev.get("country") or (hit or {}).get("hq_country", ""), 10), "status": st,
                         "year": str(ev.get("year") or ""), "successor_id": sh["id"] if sh else "", "successor_name": succ, "note": clean(ev.get("note"), 300),
                         "source_url": url, "source_title": clean(s.get("title"), 160), "quote": q, "quote_check": s.get("check"), "accessed": s.get("accessed") or TODAY})
            have.add(rid); stats["added"] += 1
    print(dict(stats)); [print("  rejected:", n, "-", w) for n, w in rej]
    if not dry:
        rows.sort(key=lambda r: r["name"].lower())
        with open(DATA / "lifecycle.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
if __name__ == "__main__": main(sys.argv[1:])
