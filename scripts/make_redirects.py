#!/usr/bin/env python3
"""List every redirect stub page in docs/ (meta refresh pages kept for old addresses) and write ops/cloudflare-bulk-redirects.csv,
ready to import as a Cloudflare Bulk Redirect list so these addresses return a real 301 instead of a page.
Usage: python3 scripts/make_redirects.py"""
import pathlib, re, csv
ROOT = pathlib.Path(__file__).resolve().parent.parent; DOCS = ROOT / "docs"; BASE = "https://jobboardlist.com"
rows = []
for p in sorted(DOCS.rglob("index.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")[:2000]
    m = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', t)
    if not m: continue
    rel = "/" + str(p.parent.relative_to(DOCS)).replace("\\", "/") + "/"
    c = re.search(r'rel="canonical" href="([^"]+)"', t)
    target = c.group(1) if c else None
    if target and target.startswith(BASE) and target != BASE + rel:
        rows.append((BASE.replace("https://", "") + rel, target))
out = ROOT / "ops" / "cloudflare-bulk-redirects.csv"; out.parent.mkdir(exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    for s, d in rows: w.writerow([s, d, 301])
print(f"{len(rows)} redirects written to {out.relative_to(ROOT)}")
