#!/usr/bin/env python3
"""Fetch employment websites from Wikidata (CC0 structured data) into a findings file.
Usage: python3 scripts/fetch_wikidata.py [OUT.json]
Then: python3 scripts/ingest.py OUT.json
Each fact is a Wikidata statement, so sources are marked "structured" and no quote check is needed."""
import csv, collections, datetime, json, pathlib, subprocess, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "research" / "findings" / f"{TODAY}-ZZ-wikidata.json"
Q = """SELECT ?item ?itemLabel ?site ?cc ?countryLabel ?cont ?ownerLabel ?ownerItem ?inception WHERE {
  ?item wdt:P31/wdt:P279* wd:Q580148 .
  OPTIONAL{?item wdt:P856 ?site}
  OPTIONAL{?item wdt:P17 ?country. ?country wdt:P297 ?cc. OPTIONAL{?country wdt:P30 ?cont}}
  OPTIONAL{?item wdt:P127|wdt:P749 ?ownerItem}
  OPTIONAL{?item wdt:P571 ?inception}
  FILTER NOT EXISTS {?item wdt:P576 ?dissolved}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} LIMIT 3000"""
SEA = set("ID MY PH TH VN SG MM KH LA BN TL".split()); SA = set("IN PK BD LK NP BT MV AF".split())
EA = set("CN JP KR KP TW HK MO MN".split()); ME = set("AE SA QA KW BH OM IL TR IR IQ JO LB SY YE PS CY".split())
CIS = set("RU BY KZ UZ KG TJ TM AZ AM GE UA MD".split())
CONT = {"Europe": "Europe", "Africa": "Africa", "North America": "North America", "South America": "Latin America", "Oceania": "APAC"}
def region(cc, cont):
    if cc in ("US", "CA"): return "North America"
    if cc in SEA: return "SEA"
    if cc in SA: return "South Asia"
    if cc in EA: return "East Asia"
    if cc in ME: return "Middle East"
    if cc in CIS: return "Eastern Europe/CIS"
    if cc in ("AU", "NZ"): return "APAC"
    if cc in ("MX", "GT", "CR", "PA", "DO", "CU", "JM", "HN", "SV", "NI", "PR"): return "Latin America"
    return CONT.get(cont, "Global")

r = subprocess.run(["curl", "-sS", "-m", "120", "-G", "https://query.wikidata.org/sparql", "--data-urlencode", "query=" + Q, "-H", "Accept: application/sparql-results+json",
                    "-A", "JobBoardAtlasResearch/1.0 (open directory of job boards)"], capture_output=True, text=True)
rows = json.loads(r.stdout)["results"]["bindings"]
items = collections.OrderedDict()
for b in rows:
    q = b["item"]["value"].rsplit("/", 1)[-1]; it = items.setdefault(q, {"name": b["itemLabel"]["value"], "sites": [], "cc": {}, "owners": [], "years": []})
    if "site" in b and b["site"]["value"] not in it["sites"]: it["sites"].append(b["site"]["value"])
    if "cc" in b: it["cc"][b["cc"]["value"]] = (b.get("countryLabel", {}).get("value", ""), b.get("cont", {}).get("value", ""))
    if "ownerLabel" in b and not b["ownerLabel"]["value"].startswith("Q") and b["ownerLabel"]["value"] not in it["owners"]: it["owners"].append(b["ownerLabel"]["value"])
    if "inception" in b and b["inception"]["value"][:4] not in it["years"]: it["years"].append(b["inception"]["value"][:4])

countries = {c["code"]: c for c in csv.DictReader(open(ROOT / "data" / "countries.csv", encoding="utf-8"))}
cont_names = {}
for b in rows:
    if "cont" in b and "cc" in b: cont_names[b["cc"]["value"]] = b["cont"]["value"]
boards, new_countries = [], {}
for q, it in items.items():
    if not it["sites"] or it["name"].startswith("Q") and it["name"][1:].isdigit(): continue
    url = it["sites"][0]; page = f"https://www.wikidata.org/wiki/{q}"
    codes = ["UK" if c == "GB" else c for c in it["cc"]]
    for c, (label, cont) in it["cc"].items():
        c2 = "UK" if c == "GB" else c
        if c2 not in countries and c2 not in new_countries and label: new_countries[c2] = (label, region(c, "")) 
    srcs = [{"field": "existence", "url": page, "title": f"Wikidata: {it['name']}", "quote": "Wikidata: instance of employment website", "check": "structured"}]
    b = {"name": it["name"], "url": url, "type": "board", "countries_served": codes, "sources": srcs}
    if len(it["years"]) == 1 and it["years"][0].isdigit(): b["founded"] = it["years"][0]
    if len(it["owners"]) == 1:
        b["parent"] = it["owners"][0]; srcs.append({"field": "parent", "url": page, "title": f"Wikidata: {it['name']}", "quote": f"Wikidata: owned by {it['owners'][0]}", "check": "structured"})
    boards.append(b)
OUT.write_text(json.dumps({"mode": "reference", "country": "ZZ", "boards": boards, "blocked": [], "queue": []}, indent=1, ensure_ascii=False), encoding="utf-8")
if new_countries:
    with open(ROOT / "data" / "countries.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        for c, (label, reg) in sorted(new_countries.items()): w.writerow([c, label, reg, 9, "reference-only", ""])
print(f"{len(boards)} boards written to {OUT.name}; {len(new_countries)} new countries added to the queue")
