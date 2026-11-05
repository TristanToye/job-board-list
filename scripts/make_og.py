#!/usr/bin/env python3
"""Generate the social preview image site_src/og.png (1200x630). Needs Pillow. Usage: python3 scripts/make_og.py"""
import csv, json, pathlib
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
n = sum(1 for _ in csv.DictReader(open(ROOT / "data" / "job_boards.csv", encoding="utf-8")))
img = Image.new("RGB", (1200, 630), "#1d4ed8"); d = ImageDraw.Draw(img)
for y in range(630): d.line([(0, y), (1200, y)], fill=(29 + y // 12, 78 + y // 14, 216 - y // 10))
f = lambda s: ImageFont.load_default(size=s)
d.text((70, 150), cfg["site_name"], font=f(92), fill="white")
d.text((70, 280), "Job boards, aggregators and ATS systems", font=f(44), fill="#dbeafe")
d.text((70, 340), "with their APIs and partner programs", font=f(44), fill="#dbeafe")
d.text((70, 470), f"{n} boards  |  by country, region and language  |  cited sources", font=f(34), fill="white")
d.text((70, 540), cfg["base_url"].replace("https://", ""), font=f(34), fill="#bfdbfe")
img.save(ROOT / "site_src" / "og.png", optimize=True); print("ok", n)
