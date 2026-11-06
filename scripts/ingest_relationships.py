#!/usr/bin/env python3
"""Merge relationship findings (mode "relationships") into data/relationships.csv.
Usage: python3 scripts/ingest_relationships.py FINDINGS.json [...] [--dry-run]
An edge is kept only if its source is on the domain of one of the two parties (or a reference site), its quote is 3 to 30
words, was not a mismatch, and names the other party."""
import csv, json, pathlib, re, sys, datetime, urllib.parse, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; TODAY = datetime.date.today().isoformat()
RELATIONS = {"sends-jobs-to", "integrates-with"}
REFERENCE = {"wikipedia.org", "wikidata.org"}
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]
COLS = ["from_id", "from_name", "to_id", "to_name", "relation", "source_url", "source_title", "quote", "quote_check", "accessed"]
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def alnum(s): return re.sub(r"[^a-z0-9]", "", s.lower())
def host(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def regdom(h):
    p = h.split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in {"co", "com", "gov", "org", "ne", "ac", "edu", "net", "gc", "gouv", "gob", "go"} else ".".join(p[-2:])
def clean(s, n=300): return str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()[:n]
def bad(s): return bool(re.search("|".join(BLOCKED_WORDS), s or "", re.I))
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []

def main(argv):
    dry = "--dry-run" in argv; files = [a for a in argv if a.endswith(".json")]
    boards = load("job_boards.csv"); rows = load("relationships.csv")
    bydom = {regdom(host(b["url"])): b for b in boards if b["url"]}; byslug = {}
    for b in boards: byslug.setdefault(slug(b["name"]), b); byslug.setdefault(b["id"], b)
    def resolve(name, url):
        hit = (bydom.get(regdom(host(url))) if url else None) or byslug.get(slug(name)) or next((b for k, b in byslug.items() if k.replace("-", "") == slug(name).replace("-", "")), None)
        if hit is None and "." in name: hit = byslug.get(slug(name.split(".")[0])) or bydom.get(regdom(name.lower()))  # "Reed.co.uk" names the same site as "Reed"
        return hit
    def brand_match(label, name):
        """A source domain belongs to a party we could not resolve if its brand label is that party's name (strict, so lookalike domains do not pass)."""
        a = alnum(name); return len(label) >= 4 and (label == a or a.startswith(label) and a[len(label):] in ("com", "couk", "net", "org", "io", "de", "fr", "co", "uk"))
    have = {(r["from_id"] or slug(r["from_name"]), r["to_id"] or slug(r["to_name"]), r["relation"]) for r in rows}
    stats = collections.Counter(); rej = []; queue = []
    for fn in files:
        d = json.load(open(fn, encoding="utf-8"))
        if d.get("mode") != "relationships": print(fn, "bad mode"); continue
        for q in d.get("queue", []):
            if q.get("name") and not bad(json.dumps(q)): queue.append([clean(q["name"], 80), clean(q.get("url", ""), 200), "", "board", "Named on an integrations page: " + clean(q.get("reason", ""), 120), TODAY])
        for ed in d.get("edges", []):
            fnm, tnm = clean(ed.get("from"), 80), clean(ed.get("to"), 80); rel = clean(ed.get("relation"), 20).lower()
            if not fnm or not tnm or rel not in RELATIONS or bad(json.dumps(ed)): rej.append((fnm, tnm, "bad names or relation")); stats["rejected"] += 1; continue
            f, t = resolve(fnm, clean(ed.get("from_url"), 200)), resolve(tnm, clean(ed.get("to_url"), 200))
            src = ed.get("source") or {}; su, qt = clean(src.get("url"), 300), clean(src.get("quote"), 300); chk = src.get("check", ""); sd = regdom(host(su))
            doms = {regdom(host(clean(ed.get("from_url"), 200))), regdom(host(clean(ed.get("to_url"), 200)))} | ({regdom(host(f["url"]))} | {x for x in f.get("domains", "").split(";") if x} if f else set()) | ({regdom(host(t["url"]))} | {x for x in t.get("domains", "").split(";") if x} if t else set())
            doms.discard("")
            if not su.startswith("http") or not (3 <= len(qt.split()) <= 30) or chk == "mismatch": rej.append((fnm, tnm, "bad url or quote")); stats["rejected"] += 1; continue
            if sd in REFERENCE:
                if chk not in ("ok", "structured"): rej.append((fnm, tnm, "reference quote not confirmed")); stats["rejected"] += 1; continue
            elif sd not in doms and not ((not f and brand_match(sd.split(".")[0], fnm)) or (not t and brand_match(sd.split(".")[0], tnm))): rej.append((fnm, tnm, f"source off domain {sd}")); stats["rejected"] += 1; continue
            # the quote must name the party the source's owner does not own
            from_side = (f and (sd == regdom(host(f["url"])) or sd in f.get("domains", "").split(";"))) or sd == regdom(host(clean(ed.get("from_url"), 200))) or (not f and brand_match(sd.split(".")[0], fnm))
            other = tnm if from_side else fnm
            qn = alnum(qt); toks = [alnum(x) for x in re.split(r"\s+", other) if len(alnum(x)) >= 4]
            if alnum(other) not in qn and not (toks and toks[0] in qn) and alnum(fnm) not in qn and alnum(tnm) not in qn: rej.append((fnm, tnm, "quote does not name the other party")); stats["rejected"] += 1; continue
            key = ((f["id"] if f else slug(fnm)), (t["id"] if t else slug(tnm)), rel)
            if key in have: stats["duplicate"] += 1; continue
            rows.append({"from_id": f["id"] if f else "", "from_name": f["name"] if f else fnm, "to_id": t["id"] if t else "", "to_name": t["name"] if t else tnm, "relation": rel,
                         "source_url": su, "source_title": clean(src.get("title"), 120), "quote": qt, "quote_check": chk, "accessed": TODAY})
            have.add(key); stats["added"] += 1
    print(dict(stats), "rejections:", len(rej), "| edges in total:", len(rows), "| unresolved names:", len({r['to_name'] for r in rows if not r['to_id']} | {r['from_name'] for r in rows if not r['from_id']}))
    for a, b, w in rej[:25]: print("  reject", a, "->", b, "|", w)
    unresolved = sorted({r["from_name"] for r in rows if not r["from_id"]} | {r["to_name"] for r in rows if not r["to_id"]})
    for nm in unresolved: queue.append([nm, "", "", "board", "Named as a partner on an integrations page but not yet in the directory.", TODAY])
    if dry: print("dry run, nothing written"); return
    with open(DATA / "relationships.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    if queue:
        qrows = load("research_queue.csv"); seen = {(r["name"], r["country"]) for r in qrows}
        with open(DATA / "research_queue.csv", "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            for qq in queue:
                if (qq[0], qq[2]) not in seen: w.writerow(qq); seen.add((qq[0], qq[2]))
if __name__ == "__main__": main(sys.argv[1:])
