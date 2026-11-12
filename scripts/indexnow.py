#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing and others) which pages changed, after a deploy.
Usage: python3 scripts/indexnow.py [--all] [--dry-run]
Compares docs/sitemap.xml with the version in the previous commit and submits new or re-dated URLs. --all submits every sitemap URL."""
import json, pathlib, re, subprocess, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent; HOST = "jobboardlist.com"
key = (ROOT / "site_src" / "indexnow_key.txt").read_text().strip()
def entries(xml): return dict(re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", xml))
now = entries((ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8"))
if "--all" in sys.argv: urls = list(now)
else:
    old = subprocess.run(["git", "show", "HEAD~1:docs/sitemap.xml"], capture_output=True, text=True, cwd=ROOT).stdout
    prev = entries(old); urls = [u for u, d in now.items() if prev.get(u) != d]
print(f"{len(urls)} URLs to submit")
if not urls or "--dry-run" in sys.argv: sys.exit(0)
body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r: print("IndexNow response:", r.status)
except Exception as ex: print("IndexNow request failed:", ex); sys.exit(1)
