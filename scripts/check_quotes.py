#!/usr/bin/env python3
"""Check that each cited quote really appears on its cited page, and annotate the findings file in place.
Usage: python3 scripts/check_quotes.py FINDINGS.json [...]
Each source gets "check": "ok" (quote found), "mismatch" (page read, quote not found) or "unreachable" (page not readable here)."""
import html, json, re, subprocess, sys, time, threading, unicodedata, concurrent.futures as cf
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
def check(url, quote, cache):
    if url not in cache: cache[url] = page_text(url)
    txt = cache[url]
    if txt is None: return "unreachable"
    q = norm(quote)
    if not q: return "mismatch"
    if q in txt: return "ok"
    words = q.split()
    if len(words) >= 6:  # tolerate small wording differences: most 4-word windows must be present
        wins = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]
        if sum(w in txt for w in wins) / len(wins) >= 0.8: return "ok"
    return "mismatch"
def main(files):
    cache = {}
    for fn in files:
        d = json.load(open(fn, encoding="utf-8")); jobs = []
        for b in d.get("boards", []):
            for s in b.get("sources", []):
                if s.get("field") not in ("listed_by", "relationship") and s.get("url") and s.get("check") != "structured": jobs.append(s)
            if isinstance(b.get("notes"), list):
                jobs.extend(n for n in b["notes"] if isinstance(n, dict) and n.get("url") and n.get("quote"))
        with cf.ThreadPoolExecutor(6) as ex: res = list(ex.map(lambda s: check(s["url"], s.get("quote", ""), cache), jobs))
        for s, r in zip(jobs, res): s["check"] = r
        json.dump(d, open(fn, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        c = {k: res.count(k) for k in ("ok", "mismatch", "unreachable")}; print(fn.split("/")[-1], c)
if __name__ == "__main__": main(sys.argv[1:])
