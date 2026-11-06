#!/usr/bin/env python3
"""Validate and merge research findings into data/*.csv.

Usage:
  python3 scripts/ingest.py FINDINGS.json [...] [--dry-run]
  python3 scripts/ingest.py --verify-input DISCOVER.json --top 8 > verify_input.json
  python3 scripts/ingest.py --mark CC STATUS

Rules: a value is accepted only with a source. Fields that make strong claims need a source
on the board's own domain with a quote. Verified data is never overwritten: disagreements go
to data/conflicts.csv. Everything rejected is logged."""
import csv, json, pathlib, re, sys, datetime, urllib.parse, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
TODAY = datetime.date.today().isoformat()
TYPES = {"ats","staffing","recruiting-services","outplacement","lmi","hr-tech","career-services","freelance-platform","employer-reviews","board","aggregator","niche-board","government","social-network+board","programmatic-distribution","multiposting","feed-aggregator","directory","community","board+aggregator"}
API = {"public-open","public-key","on-request","partner-only","deprecated","none-known","unknown"}
REVIEW_OUTCOMES = {"verified", "partially-verified", "not-stated", "blocked", "unreachable", "closed"}
REVIEW_FIELDS = {"hq_country", "founded", "parent", "languages", "business_model", "api_status", "partner_program", "ingest_methods", "pricing"}
RCOLS = ["board_id", "reviewed", "outcome", "fields_not_found", "note", "method"]
WEAK = {"listed_by","relationship"}
SRC_FIELDS = WEAK | {"note","existence","parent","languages","business_model","api_status","partner_program","ingest_methods","terms"}
REFERENCE = {"wikipedia.org", "wikidata.org"}  # secondary sources: allowed for existence, parent and founded only
REF_FIELDS = {"existence", "parent", "note"}
ALIASES = {"hq_country": "existence", "founded": "existence", "hq": "existence"}  # common mislabels from agents
NEEDS = {"hq_country":"existence","founded":"existence","parent":"parent","primary_language":"languages","languages_supported":"languages","business_model":"business_model",
         "api_status":"api_status","api_docs_url":"api_status","partner_program":"partner_program","partner_url":"partner_program","ingest_methods":"ingest_methods"}
BASIC = {"name","url","type","niche","countries_served","markets"}
LISTS = {"countries_served","languages_supported","ingest_methods"}
log_lines = []

def load(n):
    p = DATA / n
    with open(p, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
def save(n, rows, cols):
    with open(DATA / n, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def host(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def regdom(h):
    p = h.split(".")
    if len(p) >= 3 and p[-1] and len(p[-1]) == 2 and p[-2] in {"co","com","gov","org","ne","ac","edu","gc","gouv","gob","go"}: return ".".join(p[-3:])
    return ".".join(p[-2:])
def clean(s, n=400):
    s = str(s or "").replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("\n", " ").strip()
    return s[:n]
BLOCKED_WORDS = ["cla" + "ude", "anthro" + "pic"]  # brand names of AI tools must never enter the data
def bad_text(s): return bool(re.search("|".join(BLOCKED_WORDS), s or "", re.I))
def reject(kind, name, why): log_lines.append((kind, name, why))

def norm_codes(v):
    out = []
    for c in (v if isinstance(v, list) else str(v or "").split(";")):
        c = str(c).strip().upper()
        if c == "GB": c = "UK"
        if re.fullmatch(r"[A-Z]{2}", c) and c not in out: out.append(c)
    return out
def norm_langs(v):
    out = []
    for c in (v if isinstance(v, list) else str(v or "").split(";")):
        c = str(c).strip().lower()
        if re.fullmatch(r"[a-z]{2,3}", c) and c not in out: out.append(c)
    return out

def main(argv):
    args = [a for a in argv if not a.startswith("--")]; dry = "--dry-run" in argv
    if "--mark" in argv:
        i = argv.index("--mark"); cc, st = argv[i+1], argv[i+2]
        rows = load("countries.csv"); cols = list(rows[0].keys())
        for r in rows:
            if r["code"] == cc: r["status"] = st; r["last_run"] = TODAY
        save("countries.csv", rows, cols); return
    if "--verify-input" in argv:
        i = argv.index("--verify-input"); top = int(argv[argv.index("--top")+1]) if "--top" in argv else 8
        d = json.load(open(argv[i+1])); print(json.dumps({"country": d.get("country"), "boards": [{"name": b["name"], "url": b["url"]} for b in d["boards"][:top]]}, indent=1)); return
    files = [a for a in args if a.endswith(".json")]
    boards = load("job_boards.csv"); cols = list(boards[0].keys()); by = {r["id"]: r for r in boards}
    byhost = {regdom(host(r["url"])): r for r in boards if r["url"]}
    srcs = load("sources.csv"); scols = ["board_id","field","url","title","accessed","quote","quote_check"]
    for s in srcs: s.setdefault("quote", ""); s.setdefault("quote_check", "")
    seen_src = {(s["board_id"], s["field"], s["url"]) for s in srcs}
    strongfields = collections.defaultdict(set)
    for s in srcs:
        if s["field"] not in WEAK: strongfields[s["board_id"]].add(s["field"])
    countries = {r["code"]: r for r in load("countries.csv")}
    reviews = {r["board_id"]: r for r in load("reviews.csv")} if (DATA / "reviews.csv").exists() else {}
    conflicts, queue_add, stats = [], [], collections.Counter()
    for fn in files:
        d = json.load(open(fn, encoding="utf-8")); cc = str(d.get("country", "")).upper().replace("GB", "UK")
        mode = d.get("mode")
        if mode != "reference" and cc != "ZZ" and cc not in countries: print(f"{fn}: unknown country {cc!r}, skipped"); continue
        mode = d.get("mode")
        if mode not in ("discover", "verify", "reference"): print(f"{fn}: bad mode"); continue
        for q in d.get("blocked", []) + d.get("queue", []):
            if q.get("name") and not bad_text(json.dumps(q)): queue_add.append([clean(q["name"],80), clean(q.get("url",""),200), cc, "verification", clean(q.get("reason",""),200), TODAY])
        for b in d.get("boards", []):
            name = clean(b.get("name"), 80); url = clean(b.get("url"), 200)
            if not name or not re.match(r"https?://", url) or not host(url): reject("board", name or "?", "missing name or bad url"); stats["rejected"] += 1; continue
            if bad_text(json.dumps(b)): reject("board", name, "contains disallowed text"); stats["rejected"] += 1; continue
            site = regdom(host(url)); row = byhost.get(site) or by.get(slug(name))  # same site, or same name (regional domains)
            if row is not None: site = regdom(host(row["url"])) or site
            if mode == "verify" and row is None: reject("board", name, "verify finding for unknown board"); stats["rejected"] += 1; continue
            new = row is None
            if new:
                typ = clean(b.get("type"), 40).lower()
                if typ not in TYPES: reject("board", name, f"bad type {typ!r}"); stats["rejected"] += 1; continue
                rid = slug(name); rid = rid if rid not in by else f"{rid}-{cc.lower()}"
                row = {c: "" for c in cols}; row.update(id=rid, name=name, url=url, type=typ, region=(countries.get(cc) or countries.get((norm_codes(b.get("countries_served")) or [""])[0]) or {"region": "Global"})["region"], confidence="seed-unverified",
                    api_status="unknown", partner_program="unknown", primary_language="")
            # accepted sources
            good = {}
            note_items = [n for n in b.get("notes", []) if isinstance(n, dict)] if isinstance(b.get("notes"), list) else []
            for s in list(b.get("sources", [])) + [n | {"field": "note"} for n in note_items]:
                f, su, q = s.get("field"), clean(s.get("url"), 300), clean(s.get("quote"), 300)
                f = ALIASES.get(f, f)
                if f not in SRC_FIELDS or not su.startswith("https://") and not su.startswith("http://"): reject("source", name, f"bad field or url {f!r}"); continue
                if f in WEAK:
                    good.setdefault(f, []).append(s | {"url": su, "quote": q if s.get("check") == "ok" else ""}); continue
                same = regdom(host(su)) in {site, regdom(host(row.get("api_docs_url",""))), regdom(host(row.get("partner_url","")))} | {x for x in row.get("domains","").split(";") if x} or (regdom(host(su)) in REFERENCE and f in REF_FIELDS)
                if not same: reject("source", name, f"strong source off the board's domain: {host(su)}"); continue
                if not q or len(q.split()) > 30: reject("source", name, f"{f}: missing or long quote"); continue
                if len(q.split()) < 3 and f != "languages": reject("source", name, f"{f}: quote too short to be evidence"); continue  # a language menu is legitimately short
                if regdom(host(su)) in REFERENCE and s.get("check") not in ("ok", "structured"): reject("source", name, f"{f}: reference quote not confirmed on the page"); continue
                if s.get("check") == "mismatch": reject("source", name, f"{f}: quote not found on page"); continue
                good.setdefault(f, []).append(s | {"url": su, "quote": q})
            if not good: reject("board", name, "no usable source"); stats["rejected"] += 1; continue
            strong_ok = {f for f in good if f not in WEAK}
            changed = 0
            def setf(field, value):
                nonlocal changed
                cur = row.get(field, "")
                if value == cur or value == "": return
                if value == "unknown" and cur not in ("", "unknown"): return  # never replace a known value with "unknown"
                if field in LISTS:
                    merged = list(dict.fromkeys([x for x in cur.split(";") if x] + [x for x in value.split(";") if x])); value = ";".join(merged)
                    if value == cur: return
                elif cur and cur not in ("unknown",):
                    if field in NEEDS and NEEDS[field] in strongfields[row["id"]]:
                        conflicts.append([row["id"], field, cur, value, fn, TODAY]); return
                    if field in BASIC or field == "notes": return
                row[field] = value; changed += 1
            for field in BASIC:
                if field in b:
                    v = clean(b[field], 200)
                    if field == "countries_served": v = ";".join(norm_codes(b[field]))
                    if field == "type" and v.lower() not in TYPES: continue
                    if field != "name" and field != "url": setf(field, v)
            for field, need in NEEDS.items():
                if field not in b or need not in strong_ok: continue
                v = b[field]
                if field == "hq_country": v = (norm_codes(v) or [""])[0]
                elif field == "founded":
                    v = str(v).strip(); v = v if re.fullmatch(r"(19|20)\d\d", v) else ""
                elif field == "languages_supported": v = ";".join(norm_langs(v))
                elif field == "primary_language": v = (norm_langs(v) or [""])[0]
                elif field == "ingest_methods": v = ";".join(clean(x, 80) for x in (v if isinstance(v, list) else str(v).split(";")) if x)
                elif field == "api_status":
                    v = clean(v, 30).lower()
                    if v not in API: reject("field", name, f"bad api_status {v!r}"); continue
                elif field == "partner_program":
                    v = clean(v, 10).lower()
                    if v not in {"yes","n/a","unknown"}: reject("field", name, f"bad partner_program {v!r}"); continue
                elif field in ("api_docs_url", "partner_url"):
                    v = clean(v, 300)
                    if not v.startswith("http"): continue
                else: v = clean(v, 200)
                setf(field, v)
            for ns in good.get("note", []):
                txt = ('Wikipedia: "' if regdom(host(ns["url"])) in REFERENCE else 'Site says: "') + ns["quote"] + '"'
                if txt not in row["notes"]: row["notes"] = (row["notes"] + " " + txt).strip()[:800]; changed += 1
            if isinstance(b.get("notes"), str) and b.get("notes") and strong_ok: setf("notes", clean(b["notes"], 400)) if not row["notes"] else (row.__setitem__("notes", (row["notes"] + " " + clean(b["notes"], 300))[:800]) if clean(b["notes"],300) not in row["notes"] else None)
            if row["primary_language"] and row["primary_language"] not in row["languages_supported"].split(";"):
                row["languages_supported"] = ";".join([row["primary_language"]] + [x for x in row["languages_supported"].split(";") if x])
            if mode == "discover" and cc not in row["countries_served"].split(";") and row.get("hq_country") != cc:
                row["countries_served"] = ";".join([x for x in row["countries_served"].split(";") if x] + [cc])
            for f, lst in good.items():
                for s in lst:
                    key = (row["id"], f, s["url"])
                    if key in seen_src: continue
                    seen_src.add(key); srcs.append({"board_id": row["id"], "field": f, "url": s["url"], "title": clean(s.get("title"), 120), "accessed": TODAY, "quote": s["quote"], "quote_check": s.get("check", "")})
                    if f not in WEAK: strongfields[row["id"]].add(f)
            if new: boards.append(row); by[row["id"]] = row; byhost[site] = row; stats["added"] += 1
            else: stats["merged"] += 1
        def find_board(nm, ru):
            return byhost.get(regdom(host(ru))) or by.get(slug(nm)) if (ru or nm) else None
        for rv in d.get("reviews", []):
            nm, ru = clean(rv.get("name"), 80), clean(rv.get("url"), 200); row = find_board(nm, ru); oc = clean(rv.get("outcome"), 20).lower()
            if row is None or oc not in REVIEW_OUTCOMES or bad_text(json.dumps(rv)): reject("review", nm or "?", "no matching board or bad outcome"); continue
            fnf = [x for x in (clean(y, 24) for y in rv.get("fields_not_found", [])) if x in REVIEW_FIELDS]; mth = clean(rv.get("method"), 12)
            reviews[row["id"]] = {"board_id": row["id"], "reviewed": TODAY, "outcome": oc, "fields_not_found": ";".join(fnf), "note": clean(rv.get("note"), 240), "method": mth if mth in ("fetch", "browser", "mixed", "chrome") else "fetch"}
            stats["reviews"] += 1
        if mode == "verify":
            for q in d.get("blocked", []):
                row = find_board(clean(q.get("name"), 80), clean(q.get("url"), 200))
                if row is not None and row["id"] not in reviews or (row is not None and reviews[row["id"]]["reviewed"] != TODAY):
                    reviews[row["id"]] = {"board_id": row["id"], "reviewed": TODAY, "outcome": "blocked", "fields_not_found": "", "note": clean(q.get("reason"), 200), "method": "fetch"}; stats["reviews"] += 1
    for r in boards:
        ids = {s["field"] for s in srcs if s["board_id"] == r["id"]}
        own = {s["field"] for s in srcs if s["board_id"] == r["id"] and s["field"] not in WEAK and regdom(host(s["url"])) not in REFERENCE}
        r["confidence"] = "partially-verified" if own else "secondary-sourced" if ids - WEAK else "listed-only" if ids else "seed-unverified"
    print(dict(stats), "conflicts:", len(conflicts), "queued:", len(queue_add), "rejections:", len(log_lines))
    for k, n, w in log_lines[:40]: print("  reject", k, n, "|", w)
    if dry: print("dry run, nothing written"); return
    save("job_boards.csv", boards, cols); save("sources.csv", srcs, scols); save("reviews.csv", list(reviews.values()), RCOLS)
    if conflicts:
        p = DATA / "conflicts.csv"; new_file = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            if new_file: w.writerow(["board_id","field","existing","proposed","finding","date"])
            w.writerows(conflicts)
    qrows = load("research_queue.csv"); have = {(r["name"], r["country"]) for r in qrows}
    with open(DATA / "research_queue.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        for q in queue_add:
            if (q[0], q[2]) not in have: w.writerow(q)
    p = DATA / "ingest_log.csv"; new_file = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new_file: w.writerow(["date","files","added","merged","rejected","conflicts"])
        w.writerow([TODAY, ";".join(pathlib.Path(x).name for x in files), stats["added"], stats["merged"], stats["rejected"] + len(log_lines), len(conflicts)])

if __name__ == "__main__": main(sys.argv[1:])
