#!/usr/bin/env python3
"""Derive tags from the fields already in the data and write data/tags.csv.
Usage: python3 scripts/derive_tags.py
Rows with basis "assigned" (set by hand) are kept. Rows with basis "derived" are rebuilt each run."""
import csv, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []
tax = {r["tag"]: r for r in load("taxonomy.csv")}
old = load("tags.csv"); assigned = [r for r in old if r["basis"] == "assigned"]
out = [dict(r) for r in assigned]; seen = {(r["kind"], r["entry_id"], r["tag"]) for r in out}
def add(kind, eid, tag, evidence):
    assert tag in tax, f"unknown tag {tag}"
    if (kind, eid, tag) not in seen: seen.add((kind, eid, tag)); out.append({"kind": kind, "entry_id": eid, "tag": tag, "basis": "derived", "evidence": evidence})

FUNCTION = {"board": ["job-board"], "niche-board": ["job-board"], "aggregator": ["job-aggregator"], "board+aggregator": ["job-board", "job-aggregator"],
    "aggregator+board": ["job-board", "job-aggregator"], "search-aggregator": ["job-aggregator"], "government": ["government-service", "job-board"],
    "social-network+board": ["professional-network", "job-board"], "ats": ["ats"], "board+employer-brand": ["job-board"], "classifieds+board": ["job-board"], "board+chat": ["job-board"], "board+reviews": ["job-board", "employer-reviews"], "programmatic-distribution": ["job-distribution"],
    "multiposting": ["job-distribution"], "feed-aggregator": ["job-distribution"], "directory": ["directory"], "community": ["community"]}
for t in ("staffing", "recruiting-services", "outplacement", "lmi", "hr-tech", "career-services", "freelance-platform", "employer-reviews"): FUNCTION[t] = [t]
FOCUS = [("tech", r"\btech|software|\bit\b|cyber|developer|data science"), ("engineering", r"engineer"), ("healthcare", r"health|medical|nursing|dental|pharma|\bcare\b"),
    ("education", r"educat|academic|higher-ed|school|teaching"), ("teaching-esl", r"\besl\b|\befl\b|tesl"), ("nonprofit", r"nonprofit|charit|\bngo\b|social sector"),
    ("volunteering", r"volunteer"), ("public-sector", r"public sector|public service|government|civic|municipal|federal|provincial|public-sector"),
    ("graduates-students", r"graduate|student|new grad|early[- ]career|internship|apprentice"), ("remote", r"remote|work from home|nomad"), ("startup", r"startup|scale-up"),
    ("trades-labour", r"trades|labou?r|blue[- ]collar|\bgig\b|part-time|hourly"), ("creative-media", r"media|journalis|creative|design"), ("indigenous", r"indigenous|aboriginal|first nations"),
    ("diversity-inclusion", r"divers|inclusi|women|disab|\bpcd\b"), ("sport", r"sport|fitness"), ("environment", r"environment|\bgreen\b|sustainab"),
    ("agriculture-food", r"agricultur|\bfood\b"), ("hospitality-tourism", r"hospitality|tourism|hotel|travel"), ("legal", r"\blegal\b|law"), ("finance", r"financ|account|bank"),
    ("executive", r"executive|c-suite|senior")]
MODEL = [("free-to-post", r"\bfree\b(?! tier)"), ("pay-per-post", r"per post|pay per post|per job|per listing"), ("subscription", r"subscription|\bplan\b|flatrate|packages"),
         ("pay-per-click", r"\bppc\b|per click|pay per click|sponsored|ppa"), ("freemium", r"freemium|free tier"), ("public-funded", r"public sector|publicly funded")]
API = {"public-open": "api-open", "public-key": "api-self-serve", "on-request": "api-on-request", "partner-only": "api-partner-only"}
GOV = re.compile(r"government|ministry|public service|federal|province of|employment service|commission of canada|ontario public|king's printer", re.I)
NONPROFIT = re.compile(r"nonprofit network|not-for-profit|foundation", re.I)

for b in load("job_boards.csv"):
    i, t = b["id"], b["type"]
    for f in FUNCTION.get(t, []): add("board", i, f, f"type={t}")
    niche = b["niche"].lower()
    if niche.startswith("general") or niche == "": 
        if niche.startswith("general"): add("board", i, "general", f"niche={b['niche']}")
    for tag, rx in FOCUS:
        if re.search(rx, niche): add("board", i, tag, f"niche={b['niche']}")
    if t == "government": add("board", i, "public-sector", "type=government"); add("board", i, "government-operated", "type=government")
    bm = b["business_model"].lower()
    for tag, rx in MODEL:
        if bm and re.search(rx, bm): add("board", i, tag, f"business_model={b['business_model']}")
    if b["api_status"] in API: add("board", i, API[b["api_status"]], f"api_status={b['api_status']}")
    if b["partner_program"] == "yes": add("board", i, "partner-program", "partner_program=yes")
    im = b["ingest_methods"].lower()
    if "xml" in im: add("board", i, "xml-feed", f"ingest_methods={b['ingest_methods']}")
    if "ats" in im: add("board", i, "ats-integration", f"ingest_methods={b['ingest_methods']}")
    if "apply" in im: add("board", i, "apply-integration", f"ingest_methods={b['ingest_methods']}")
    if "crawl" in im: add("board", i, "crawl-sourced", f"ingest_methods={b['ingest_methods']}")
    if GOV.search(b["parent"]): add("board", i, "government-operated", f"parent={b['parent']}")
    if NONPROFIT.search(b["parent"]): add("board", i, "nonprofit-operated", f"parent={b['parent']}")
for b in load("job_boards.csv"):
    seg = b.get("segment", "").lower()
    if "smb" in seg or "small" in seg: add("board", b["id"], "smb", f"segment={b['segment']}")
    if "mid-market" in seg: add("board", b["id"], "mid-market", f"segment={b['segment']}")
    if "enterprise" in seg: add("board", b["id"], "enterprise", f"segment={b['segment']}")
    if "public job feed" in b["ingest_methods"].lower(): add("board", b["id"], "public-job-feed", f"ingest_methods={b['ingest_methods']}")
# compliance posting: only when a checked quote on the entry's own sources names the rule
_cq = {}
for _s in load("sources.csv"):
    if _s.get("quote_check") == "ok" and re.search(r"\b(OFCCP|VEVRAA)\b", _s.get("quote", "")): _cq.setdefault(_s["board_id"], _s["quote"][:80])
for _bid, _q in _cq.items(): add("board", _bid, "ofccp-compliance", f"quote={_q}")
out.sort(key=lambda r: (r["kind"], r["entry_id"], r["tag"]))
with open(DATA / "tags.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["kind", "entry_id", "tag", "basis", "evidence"], lineterminator="\n"); w.writeheader(); w.writerows(out)
c = collections.Counter((r["tag"]) for r in out)
by_entry = collections.Counter((r["kind"], r["entry_id"]) for r in out if tax[r["tag"]]["facet"] == "function")
print(f"{len(out)} tag rows for {len({(r['kind'], r['entry_id']) for r in out})} entries")
print("entries with no function tag:", sum(1 for b in load("job_boards.csv") if ("board", b["id"]) not in by_entry), [b["type"] for b in load("job_boards.csv") if ("board", b["id"]) not in by_entry][:8])
print(", ".join(f"{t} {n}" for t, n in c.most_common(30)))
