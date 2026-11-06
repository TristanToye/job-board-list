#!/usr/bin/env python3
"""Check that each cited quote really appears on its cited page, and annotate the findings file in place.
Usage: python3 scripts/check_quotes.py FINDINGS.json [...]
Each source gets "check": "ok" (quote found), "mismatch" (page read, quote not found) or "unreachable" (page not readable here)."""
import html, json, pathlib, re, subprocess, sys, time, threading, unicodedata, concurrent.futures as cf
WIKI_LOCK = threading.Lock()  # one Wikipedia request at a time, with a pause between them

def norm(t):
    t = html.unescape(t); t = unicodedata.normalize("NFKD", t).lower()
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", " ", t).strip()
def page_text(url):
    wiki = "wikipedia.org/" in url
    ua = "JobBoardAtlasResearch/1.0 (open directory of job boards)" if wiki else "Mozilla/5.0 (compatible; directory-check)"
    try:
        if wiki:
            with WIKI_LOCK:
                time.sleep(3)
                r = subprocess.run(["curl", "-sSL", "-m", "20", "-A", ua, "-w", "\n%{http_code}", url], capture_output=True, text=True, timeout=30)
        else:
            r = subprocess.run(["curl", "-sSL", "-m", "20", "--max-filesize", "3000000", "-A", ua, "-w", "\n%{http_code}", url], capture_output=True, text=True, timeout=30)
    except Exception: return None
    body, _, code = r.stdout.rpartition("\n")
    if code.strip() != "200" or len(body) < 200: return None
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    return norm(re.sub(r"(?s)<[^>]+>", " ", body))
def browser_text(url):
    """Fallback for pages a plain request cannot read: render them in the headless browser (no evasion; challenge pages count as unreadable)."""
    try:
        r = subprocess.run(["node", str(pathlib.Path(__file__).resolve().parent / "browse.js"), url], capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: return None
    if d.get("blocked") or not d.get("text"): return None
    return norm(d["text"])
def judge(txt, quote):
    q = norm(quote)
    if not q: return "mismatch"
    if q in txt: return "ok"
    words = q.split()
    if len(words) >= 6:  # tolerate small wording differences: most 4-word windows must be present
        wins = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]
        if sum(w in txt for w in wins) / len(wins) >= 0.8: return "ok"
    return "mismatch"
def check(url, quote, cache):
    """Plain request first. If the quote is not in it (or the page is unreadable), try the rendered page in the browser, since many sites build menus and text with JavaScript."""
    wiki = "wikipedia.org/" in url
    if url not in cache: cache[url] = {"curl": page_text(url), "browser": False}
    c = cache[url]; res = judge(c["curl"], quote) if c["curl"] is not None else "unreachable"
    if res == "ok" or wiki: return res
    if c["browser"] is False: c["browser"] = browser_text(url)
    if c["browser"] is not None:
        r2 = judge(c["browser"], quote)
        if r2 == "ok": return "ok"
        return "mismatch"
    return res
def main(files):
    cache = {}
    for fn in files:
        d = json.load(open(fn, encoding="utf-8")); jobs = []
        holdings = [h for o in d.get("owners", []) for h in o.get("holdings", [])]
        jobs_extra = []
        facts = [f for o in d.get("owners", []) for f in o.get("facts", [])]
        for ed in d.get("edges", []):
            if ed.get("source") and ed["source"].get("url") and ed["source"].get("check") not in ("structured", "chrome"): jobs_extra.append(ed["source"])
        for b in d.get("boards", []) + holdings + facts:
            for s in b.get("sources", []):
                if s.get("field") not in ("listed_by", "relationship") and s.get("url") and s.get("check") not in ("structured", "chrome"): jobs.append(s)
            if isinstance(b.get("notes"), list):
                jobs.extend(n for n in b["notes"] if isinstance(n, dict) and n.get("url") and n.get("quote"))
        jobs.extend(jobs_extra)
        with cf.ThreadPoolExecutor(6) as ex: res = list(ex.map(lambda s: check(s["url"], s.get("quote", ""), cache), jobs))
        for s, r in zip(jobs, res): s["check"] = r
        json.dump(d, open(fn, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        c = {k: res.count(k) for k in ("ok", "mismatch", "unreachable")}; print(fn.split("/")[-1], c)
if __name__ == "__main__": main(sys.argv[1:])
