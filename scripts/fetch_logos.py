#!/usr/bin/env python3
"""Download each board's site icon into site_src/logos/ and write data/logos.json.
Icons are fetched once and self-hosted. Boards with no usable icon get a letter tile at build time.
Usage: python3 scripts/fetch_logos.py [--force]"""
import csv, io, json, pathlib, sys, time, urllib.parse, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGOS = ROOT / "site_src" / "logos"; LOGOS.mkdir(parents=True, exist_ok=True)
MANIFEST = ROOT / "data" / "logos.json"
force = "--force" in sys.argv
manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
boards = list(csv.DictReader(open(ROOT / "data" / "job_boards.csv", newline="", encoding="utf-8")))
SRC = "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url=https://{host}"

def fetch(host):
    req = urllib.request.Request(SRC.format(host=host), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r: return r.read()

for b in boards:
    m = manifest.get(b["id"])
    if m and m.get("file") and not force and (LOGOS / m["file"]).exists(): continue
    host = urllib.parse.urlparse(b["url"]).netloc.removeprefix("www.")
    if not host:
        manifest[b["id"]] = {"file": None, "host": "", "error": "no url"}; print("skip", b["id"], "no url"); continue
    try:
        img = Image.open(io.BytesIO(fetch(host))); img.load()
        w, h = img.size
        if w < 32: raise ValueError(f"too small {w}x{h}")
        img = img.convert("RGBA"); fn = f'{b["id"]}.png'; img.save(LOGOS / fn, optimize=True)
        manifest[b["id"]] = {"file": fn, "size": w, "host": host}; print("ok  ", b["id"], host, w)
    except Exception as ex:
        manifest[b["id"]] = {"file": None, "host": host, "error": str(ex)[:80]}; print("miss", b["id"], host, str(ex)[:60])
    time.sleep(0.3)
MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
got = sum(1 for v in manifest.values() if v["file"]); print(f"{got}/{len(boards)} icons")
