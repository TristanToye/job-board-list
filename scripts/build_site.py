#!/usr/bin/env python3
"""Build the static site into docs/ from data/*.csv. Usage: python3 scripts/build_site.py"""
import csv, html, json, pathlib, re, shutil, datetime, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
CFG = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
NAME = CFG["site_name"]
TODAY = datetime.date.today().isoformat()

COUNTRIES = {"US":"United States","CA":"Canada","UK":"United Kingdom","DE":"Germany","FR":"France","ES":"Spain","UA":"Ukraine",
 "IT":"Italy","NL":"Netherlands","PL":"Poland","GR":"Greece","SE":"Sweden","NO":"Norway","DK":"Denmark","CH":"Switzerland",
 "RU":"Russia","AU":"Australia","MY":"Malaysia","HK":"Hong Kong","IN":"India","CN":"China","JP":"Japan","KR":"South Korea",
 "PH":"Philippines","AE":"United Arab Emirates","NG":"Nigeria","KE":"Kenya","ZA":"South Africa","CO":"Colombia","MX":"Mexico",
 "AR":"Argentina","BR":"Brazil","Global":"Global (no single HQ)"}
LANGS = {}; NATIVE = {}  # filled from data/languages.csv once load() is defined
def lang(c): return LANGS.get(c, c.upper())
def langs_of(b):
    out = []
    for c in [b["primary_language"]] + split(b["languages_supported"]):
        if c and c not in out: out.append(c)
    return out
API_LABEL = {"on-request":"API key on request","public-open":"Open API (no key)","public-key":"Self-serve API key","partner-only":"Partner-only API",
 "deprecated":"Deprecated API","none-known":"No known API","unknown":"API status unknown"}
API_BLURB = {
 "public-open":"Boards that publish jobs through an open API, feed or open data set that needs no approval.",
 "public-key":"Boards with a documented API you can use after a self-serve signup or key request.",
 "on-request":"Boards where an API key or XML feed is issued after a request form or review, without a full partner agreement.",
 "partner-only":"Boards where programmatic access, posting or feeds require an approved partner or commercial agreement.",
 "deprecated":"Boards whose earlier public API has been retired.",
 "none-known":"Boards with no publicly documented API that we could identify. Access is typically by crawling or by employer feed.",
 "unknown":"Boards where API availability has not yet been researched."}

TYPE_NOUN = {"board": "job board", "niche-board": "niche job board", "aggregator": "job aggregator", "ats": "applicant tracking system", "lmi": "labour market information source", "hr-tech": "HR technology vendor",
    "career-services": "career services provider", "freelance-platform": "freelance marketplace", "employer-reviews": "employer review site", "staffing": "staffing agency",
    "recruiting-services": "recruiting firm", "outplacement": "outplacement firm", "government": "government job site", "directory": "directory of job sites", "community": "job community"}
def tdesc(b): return TYPE_NOUN.get(b["type"], b["type"].replace("+", " and ").replace("-", " "))
def type_label(b): t = tdesc(b); return t[:1].upper() + t[1:] if not t.startswith("HR") else t
def article(w): return "an" if w[:1].lower() in "aeiou" or w.startswith("HR") else "a"
def e(s): return html.escape(str(s), quote=True)
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def load(n):
    with open(ROOT/"data"/n, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
def split(s): return [x.strip() for x in (s or "").split(";") if x.strip()]
def country(c): return COUNTRIES.get(c, c)

boards = load("job_boards.csv"); ats = [b for b in boards if b["type"] == "ats"]
for _l in load("languages.csv"): LANGS[_l["code"]] = _l["name"]; NATIVE[_l["code"]] = _l["native"]
for _c in load("countries.csv"): COUNTRIES.setdefault(_c["code"], _c["name"])
RANK = {r["board_id"]: r for r in load("rank.csv")} if (ROOT/"data"/"rank.csv").exists() else {}
SCALE = collections.defaultdict(list)
if (ROOT/"data"/"scale.csv").exists():
    for _s in load("scale.csv"): SCALE[_s["board_id"]].append(_s)
RANK_DATE = max((r["list_date"] for r in RANK.values()), default="")
TIERS = [(1000, "Major"), (10000, "Large"), (100000, "Established"), (1000000, "Small")]
def prom(b):
    """Prominence from web link popularity (Majestic Million). Only boards that own their whole domain get a tier."""
    r = RANK.get(b["id"])
    if not r or not r["global_rank"]: return {"group": 3, "g": 0, "label": "Not in top 1M", "tier": "", "scope": r["scope"] if r else ""}
    g = int(r["global_rank"]); scope = r["scope"]
    if scope == "domain": return {"group": 0, "g": g, "label": next(t for lim, t in TIERS if g <= lim), "tier": next(t for lim, t in TIERS if g <= lim), "scope": scope}
    if scope == "mixed": return {"group": 1, "g": g, "label": "Site-wide", "tier": "", "scope": scope}
    return {"group": 2, "g": g, "label": "Not comparable", "tier": "", "scope": scope}
def skey(b): p = prom(b); return p["group"] * 10**9 + (p["g"] if p["group"] < 2 else 0)
TAX = {r["tag"]: r for r in load("taxonomy.csv")} if (ROOT/"data"/"taxonomy.csv").exists() else {}
TAGS_BY = collections.defaultdict(list)
if (ROOT/"data"/"tags.csv").exists():
    for _t in load("tags.csv"): TAGS_BY[(_t["kind"], _t["entry_id"])].append(_t["tag"])
FACETS = [("function", "What it is"), ("focus", "Who and what it is for"), ("model", "How it makes money"), ("integration", "How open it is"), ("segment", "Customer segment"), ("operator", "Who runs it")]
def tags_of(kind, i, facet=None): return [t for t in TAGS_BY.get((kind, i), []) if t in TAX and (facet is None or TAX[t]["facet"] == facet)]
REL = load("relationships.csv") if (ROOT/"data"/"relationships.csv").exists() else []
CONN = collections.defaultdict(lambda: {"sends": {}, "receives": {}, "integrates": {}})
for _r in REL:
    if _r["relation"] == "sends-jobs-to":
        if _r["from_id"]: CONN[_r["from_id"]]["sends"].setdefault(_r["to_id"] or _r["to_name"], _r)
        if _r["to_id"]: CONN[_r["to_id"]]["receives"].setdefault(_r["from_id"] or _r["from_name"], _r)
    else:
        if _r["from_id"]: CONN[_r["from_id"]]["integrates"].setdefault(_r["to_id"] or _r["to_name"], _r)
        if _r["to_id"]: CONN[_r["to_id"]]["integrates"].setdefault(_r["from_id"] or _r["from_name"], _r)
REVIEWS = {r["board_id"]: r for r in load("reviews.csv")} if (ROOT/"data"/"reviews.csv").exists() else {}
REVIEW_FIELD = {"hq_country":"headquarters","founded":"founding year","parent":"owner","languages":"languages","business_model":"pricing and business model","api_status":"API access","partner_program":"partner program","ingest_methods":"how jobs get in","pricing":"pricing"}
def review_text(b):
    rv = REVIEWS.get(b["id"])
    if not rv: return ""
    nf = ", ".join(REVIEW_FIELD.get(x, x) for x in rv["fields_not_found"].split(";") if x)
    t = {"verified": "Checked against the board's own site.", "partially-verified": "Some facts checked against the board's own site." + (f" Not stated there: {nf}." if nf else ""),
         "not-stated": "The board's own pages were read, but they do not state" + (f": {nf}." if nf else " the missing facts."), "blocked": "Could not verify: the site blocks automated access, so these facts remain as recorded.",
         "unreachable": "Could not verify: the site could not be reached.", "closed": "The site appears to have closed or been replaced."}[rv["outcome"]]
    return f'Reviewed {rv["reviewed"]}. {t}' + (f' {rv["note"]}' if rv["note"] and rv["outcome"] in ("blocked", "unreachable", "closed") else "")
OWNERS = {r["id"]: r for r in load("owners.csv")} if (ROOT/"data"/"owners.csv").exists() else {}
HOLD = load("ownership.csv") if (ROOT/"data"/"ownership.csv").exists() else []
OWNER_FACTS = collections.defaultdict(dict)
if (ROOT/"data"/"owner_facts.csv").exists():
    for _f in load("owner_facts.csv"): OWNER_FACTS[_f["owner_id"]].setdefault(_f["fact"], _f)
HOLD_BY_BOARD = collections.defaultdict(list)
for _h in HOLD:
    if _h["board_id"] and _h["relation"] != "former": HOLD_BY_BOARD[_h["board_id"]].append(_h)
def norm_owner(n):
    x = re.sub(r"\b(the|co|ltd|inc|corp|corporation|company|limited|plc|nv|ag|se|group|holdings?)\b\.?", " ", n.lower().replace(".", " ").replace(",", " "))
    return re.sub(r"[^a-z0-9]+", " ", x).strip()
ALIAS_MAP = {}
for _oid, _o in OWNERS.items():
    for _n in [_o["name"]] + split(_o.get("aliases", "")): ALIAS_MAP[norm_owner(_n)] = _oid
_pc = collections.Counter(norm_owner(b["parent"]) for b in boards if b["parent"])
EXCLUDED = {norm_owner(r["parent"]) for r in load("owner_exclusions.csv")} if (ROOT/"data"/"owner_exclusions.csv").exists() else set()
PARENT_OWNER = {}
STUB_IDS = {}
for _b in boards:
    if not _b["parent"]: continue
    _k = norm_owner(_b["parent"])
    if _k in ALIAS_MAP: PARENT_OWNER[_b["id"]] = ALIAS_MAP[_k]
    elif _k and _k not in EXCLUDED:  # every parent gets a page, except individuals and families
        _sid = STUB_IDS.setdefault(_k, slug(_b["parent"]) or "parent"); PARENT_OWNER[_b["id"]] = _sid
        OWNERS.setdefault(_sid, {"id": _sid, "name": _b["parent"], "url": "", "country": "", "aliases": "", "stub": True})
REL_LABEL = {"group-company":"Group company (listed by the owner, ownership terms not stated)","subsidiary":"Subsidiary","brand":"Brand","majority-stake":"Majority stake","minority-stake":"Minority stake","joint-venture":"Joint venture","former":"Formerly owned"}
CAT_LABEL = {"job-board":"Other job boards (not yet in the directory)","aggregator":"Other job aggregators (not yet in the directory)","staffing":"Staffing and recruitment agencies","hr-tech":"HR and recruiting technology",
             "hr-services":"HR services","data-research":"Data and research","other-hr":"Other HR businesses"}
def hold_phrase(h): return REL_LABEL[h["relation"]] + (f", {h['stake']}%" if h["stake"] else "") + (f", since {h['since']}" if h["since"] else "")
SOURCES = collections.defaultdict(list)
for _s in load("sources.csv"): SOURCES[_s["board_id"]].append(_s)
FIELD_LABEL = {"existence":"Existence and description","api_status":"API access","partner_program":"Partner program","ingest_methods":"How jobs get in",
 "business_model":"Business model and pricing","parent":"Ownership","languages":"Languages","terms":"Terms of use","relationship":"Relationships","listed_by":"Listed by a third-party directory","note":"Note"}
LOGO_MANIFEST = json.loads((ROOT / "data" / "logos.json").read_text()) if (ROOT / "data" / "logos.json").exists() else {}
def logo_info(b):
    m = LOGO_MANIFEST.get(b["id"]) or {}
    return m if m.get("file") else None
def icon(b, r, px=24):
    """Self-hosted site icon, or a letter tile when none was found."""
    m = logo_info(b)
    if m:
        px = min(px, m["size"])
        return f'<img class="ico" src="{r}assets/logos/{e(m["file"])}" width="{px}" height="{px}" alt="" loading="lazy" decoding="async">'
    hue = sum(map(ord, b["id"])) * 37 % 360
    return f'<span class="ico tile" style="--h:{hue}" aria-hidden="true">{e(b["name"][:1].upper())}</span>'
if OUT.exists(): shutil.rmtree(OUT)  # start clean so renamed or removed pages are not left behind
OUT.mkdir(parents=True, exist_ok=True)
pages = []  # (path, lastmod)

def layout(path_depth, title, desc, body, canonical, jsonld=None, extra_head="", noindex=False, md=False):
    r = "../" * path_depth
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    nav = (f'<a href="{r}">Directory</a><a href="{r}ecosystem/">Ecosystem</a><a href="{r}tags/">Types</a><a href="{r}rankings/">Rankings</a><a href="{r}owners/">Owners</a><a href="{r}regions/">Regions</a><a href="{r}countries/">Countries</a>'
           f'<a href="{r}languages/">Languages</a><a href="{r}api/">APIs</a><a href="{r}ats/">ATS systems</a><a href="{r}about/">About</a>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E0GLWE1JFP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-E0GLWE1JFP');
</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(BASE + canonical)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(BASE + canonical)}">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:image" content="{e(BASE)}/assets/og.png">
<link rel="alternate" type="application/atom+xml" title="{e(NAME)} research log" href="{r}feed.xml">{'<meta name="robots" content="noindex,follow">' if noindex else ""}{'<link rel="alternate" type="text/markdown" href="index.md">' if md else ""}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%232563eb'/%3E%3Cpath d='M8 22V10h4a4 4 0 0 1 0 8H8' fill='none' stroke='white' stroke-width='3'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{r}assets/style.css">{extra_head}{ld}</head>
<body><header class="top"><div class="wrap bar"><a class="brand" href="{r}">{e(NAME)}</a><nav>{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer class="wrap foot"><p>{e(NAME)} is an open dataset. Download: <a href="{r}downloads/job_boards.csv">boards CSV</a>,
<a href="{r}downloads/job_boards.json">boards JSON</a>, <a href="{r}data/boards.json">JSON data API</a>, <a href="{r}changelog/">changelog</a> and <a href="{r}feed.xml">feed</a>.
Data is a work in progress and may be wrong: see <a href="{r}about/">methodology</a>. Web rank data: <a href="https://majestic.com/reports/majestic-million" rel="noopener nofollow">Majestic Million</a>, CC BY 3.0. Last built {TODAY}.</p></footer>
</body></html>"""

MD_PAGES = []  # (kind, path, markdown) for pages that have a Markdown twin, used for llms-full.txt
def write(rel, content, lastmod=True, indexed=True, mod=None, md=None, kind=""):
    p = OUT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
    if lastmod and indexed and rel.endswith("index.html"):
        pages.append(("/" + rel[:-len("index.html")], mod or TODAY))
    if md is not None and indexed and rel.endswith("index.html"):
        p.with_name("index.md").write_text(md, encoding="utf-8"); MD_PAGES.append((kind, "/" + rel[:-len("index.html")], md))

INFO_FIELDS = ["hq_country", "founded", "parent", "business_model", "api_docs_url", "partner_url", "ingest_methods", "primary_language"]
def facts(b):
    return sum(1 for k in INFO_FIELDS if b.get(k)) + (b["api_status"] not in ("", "unknown")) + (b["partner_program"] in ("yes", "n/a"))
def indexable(b):
    """Only boards with cited, substantive facts get an indexable page. Thin pages stay out of the sitemap and are marked noindex."""
    return b["confidence"] in ("partially-verified", "secondary-sourced") and facts(b) >= 3
def most_prominent(v):
    top = [b for b in sorted(v, key=skey) if prom(b)["group"] == 0][:4]
    return f'<p>Most prominent by web link popularity: {", ".join(e(b["name"]) for b in top)}.</p>' if top else ""
def itemlist(v, depth):
    r = "../" * depth
    return {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": b["name"], "url": f'{BASE}/boards/{b["id"]}/'} for i, b in enumerate(sorted(v, key=lambda b: -facts(b))[:50], 1)]}
def conf_badge(c):
    if c == "seed-unverified": return '<span class="badge warn" title="No facts on this page have been checked against a primary source yet">Unverified</span>'
    if c == "secondary-sourced": return '<span class="badge" title="Facts come from a secondary source such as Wikipedia, not the board itself">Secondary source</span>'
    if c == "listed-only": return '<span class="badge" title="Only confirmed as listed by another directory. Nothing else has been checked">Listed only</span>'
    return '<span class="badge ok" title="Some facts are checked. See the sources list on this page">Partly verified</span>'
def api_badge(s): return f'<span class="badge api-{e(s)}">{e(API_LABEL.get(s,s))}</span>'
def chips(vals): return "".join(f'<span class="chip">{e(v)}</span>' for v in vals) or '<span class="muted">Not recorded</span>'
def link(u, t=None): return f'<a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(t or u)}</a>' if u else '<span class="muted">Not recorded</span>'

def board_url(b, r): return f'{r}boards/{b["id"]}/'
def prom_cell(b):
    p = prom(b)
    if p["group"] == 0: return f'<span class="badge tier-{e(p["tier"])}" title="Global web link popularity rank #{p["g"]:,}">{e(p["tier"])}</span> <span class="muted small">#{p["g"]:,}</span>'
    if p["group"] == 1: return f'<span class="badge" title="This rank covers the whole site, which is more than job listings">Site-wide</span> <span class="muted small">#{p["g"]:,}</span>'
    if p["group"] == 2: return '<span class="muted small" title="This board is a section of a larger site, so the site rank does not describe it">Not comparable</span>'
    return '<span class="muted small">Not in top 1M</span>'
def row(b, r):
    search = " ".join([b["name"], b["type"], b["hq_country"], country(b["hq_country"]), b["markets"], b["region"], b["niche"], " ".join(lang(c) for c in langs_of(b)), b["parent"], b["ingest_methods"]]).lower()
    return (f'<tr data-search="{e(search)}" data-region="{e(b["region"])}" data-type="{e(b["type"])}" data-api="{e(b["api_status"])}" data-partner="{e(b["partner_program"])}" data-lang="{e(" ".join(langs_of(b)))}" data-name="{e(b["name"].lower())}" data-tier="{e(prom(b)["tier"])}" data-rank="{skey(b)}" data-tags="{e(" ".join(tags_of("board", b["id"])))}">'
            f'<td><div class="namecell">{icon(b, r)}<div><a href="{board_url(b,r)}"><strong>{e(b["name"])}</strong></a><div class="muted small">{e(b["niche"])}</div>{"".join(f'<span class="tag">{e(TAX[t]["label"])}</span>' for t in tags_of("board", b["id"], "function")[:2])}</div></div></td>'
            f'<td>{prom_cell(b)}</td><td>{e(type_label(b))}</td><td>{e(country(b["hq_country"]) or "Not recorded")}</td><td>{e(lang(b["primary_language"]) or "Not recorded")}</td>'
            f'<td>{api_badge(b["api_status"])}</td><td>{e(b["partner_program"] or "unknown")}</td></tr>')

def table(rows, r, filters=False):
    rows = sorted(rows, key=lambda b: (skey(b), b["name"].lower()))
    return ('<div class="tablewrap"><table id="boards"><thead><tr><th>Board</th><th title="Tier from global web link popularity rank">Prominence</th><th>Type</th><th>HQ</th><th>Language</th><th>API</th><th>Partner program</th></tr></thead><tbody>'
            + "".join(row(b, r) for b in rows) + "</tbody></table></div>")

# ---------- home ----------
def opts(key):
    vals = sorted({b[key] for b in boards})
    return "".join(f'<option value="{e(v)}">{e(API_LABEL.get(v, v))}</option>' for v in vals)
lang_counts = collections.Counter(c for b in boards for c in langs_of(b))
lang_opts = "".join(f'<option value="{e(c)}">{e(lang(c))}</option>' for c in sorted(lang_counts, key=lang))
checked = sum(1 for b in boards if b["confidence"] == "partially-verified")
tag_counts = collections.Counter(t for (k, i), ts in TAGS_BY.items() if k == "board" for t in ts)
fn_opts = "".join(f'<option value="{e(t)}">{e(r["label"])} ({tag_counts[t]})</option>' for t, r in TAX.items() if r["facet"] == "function" and tag_counts[t])
fc_opts = "".join(f'<option value="{e(t)}">{e(r["label"])} ({tag_counts[t]})</option>' for t, r in TAX.items() if r["facet"] == "focus" and tag_counts[t])
apicount = collections.Counter(b["api_status"] for b in boards)
home_body = f"""
<section class="hero"><h1>Every job board, aggregator and ATS, and how to integrate with them</h1>
<p class="lede">{e(CFG["tagline"])}. Search {len(boards)} entries across job boards, aggregators, applicant tracking systems ({len(ats)}), staffing firms and other HR services, by region and country. Filter by type, focus and openness. Find who has an API, a partner program or a developer portal.</p>
<div class="stats"><div><b>{len(boards)}</b><span>directory entries</span></div><div><b>{checked}</b><span>checked against sources</span></div><div><b>{len(ats)}</b><span>ATS systems</span></div>
<div><b>{apicount["public-open"] + apicount["public-key"]}</b><span>with a public API</span></div><div><b>{apicount["partner-only"]}</b><span>partner-only</span></div></div>
<p class="notice"><strong>Early data.</strong> {checked} of {len(boards)} entries have facts checked against cited sources, starting with Canada. Others are only confirmed as listed by another directory, and the rest were compiled from general knowledge. Treat anything not marked Partly verified as a lead.</p></section>
<section aria-label="Search the directory"><div class="filters">
<label class="grow">Search<input id="q" type="search" placeholder="Name, country, language, niche, parent company..." autocomplete="off"></label>
<label>Region<select id="f-region"><option value="">All</option>{opts("region")}</select></label>
<label>Type<select id="f-type"><option value="">All</option>{opts("type")}</select></label>
<label>Language<select id="f-lang"><option value="">All</option>{lang_opts}</select></label>
<label>API<select id="f-api"><option value="">All</option>{opts("api_status")}</select></label>
<label>Type<select id="f-function"><option value="">All</option>{fn_opts}</select></label>
<label>Focus<select id="f-focus"><option value="">All</option>{fc_opts}</select></label>
<label>Prominence<select id="f-tier"><option value="">All</option><option value="Major">Major</option><option value="Large">Large</option><option value="Established">Established</option><option value="Small">Small</option></select></label>
<label>Sort<select id="sort"><option value="prom">Prominence</option><option value="name">A to Z</option></select></label>
<label>Partner program<select id="f-partner"><option value="">All</option><option value="yes">Yes</option><option value="n/a">Not applicable</option><option value="unknown">Unknown</option></select></label>
</div><p id="count" class="muted" aria-live="polite"></p>
{table(sorted(boards, key=lambda b: b["name"].lower()), "")}
<p id="empty" class="muted" hidden>No boards match those filters.</p></section>
<section class="prose"><h2>What this directory covers</h2>
<p>Job distribution has several layers: the employer, the applicant tracking system, programmatic and multiposting platforms, and the boards and aggregators candidates use. This directory maps all of them, with a focus on integration: which platforms publish open feeds or APIs, which require a partnership, and where the developer portals are.</p>
<ul><li><a href="languages/">Job boards by language</a></li><li><a href="tags/">Browse by type, focus and openness</a></li><li><a href="countries/canada/">Job boards in Canada</a></li><li><a href="api/public-open/">Job boards with an open API</a></li><li><a href="api/public-key/">Job boards with a self-serve API key</a></li><li><a href="api/partner-only/">Partner-only job board APIs</a></li><li><a href="ats/">ATS systems with public job feeds</a></li></ul></section>
<script src="assets/app.js" defer></script>"""
dataset = {"@context":"https://schema.org","@type":"Dataset","name":f"{NAME}: job boards, aggregators and ATS systems",
 "description":CFG["tagline"],"url":BASE+"/","creator":{"@type":"Person","name":CFG["author"]},"isAccessibleForFree":True,
 "keywords":["job boards","job aggregators","applicant tracking systems","job board API","recruitment partner programs"],
 "distribution":[{"@type":"DataDownload","encodingFormat":"text/csv","contentUrl":BASE+"/downloads/job_boards.csv"},
                 {"@type":"DataDownload","encodingFormat":"application/json","contentUrl":BASE+"/downloads/job_boards.json"}]}
site_ld = {"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":BASE+"/"}
write("index.html", layout(0, f"{NAME}: job boards, aggregators and ATS systems with APIs and partner programs",
  f"Open directory of {len(boards)} job boards, aggregators, ATS systems, staffing firms and HR services, by region and country, with API access, partner programs and owners.",
  home_body, "/", [dataset, site_ld]))

# ---------- board pages ----------
def fact(k, v): return f"<dt>{e(k)}</dt><dd>{v}</dd>"
for b in boards:
    r = "../../"
    siblings = [x for x in boards if x["region"] == b["region"] and x["id"] != b["id"]][:6]
    api_text = {"public-open":"has an open API or feed that does not require approval","public-key":"offers an API you can use with a self-serve key",
      "partner-only":"restricts programmatic access to approved partners","deprecated":"has retired its earlier public API",
      "on-request":"issues API keys or feeds on request","none-known":"has no publicly documented API that we could find","unknown":"has not yet been researched for API availability"}[b["api_status"]]
    partner = {"yes":"A partner or integration program exists.","n/a":"Not applicable (public body or open source of data).","unknown":"Partner program status is not yet known."}.get(b["partner_program"], "Partner program status is not yet known.")
    tag_html = "".join(f'<div class="tagrow"><span class="muted small">{e(lbl)}:</span> ' + "".join(f'<a class="chip" href="{r}tags/{e(t)}/">{e(TAX[t]["label"])}</a>' for t in tags_of("board", b["id"], fac)) + "</div>" for fac, lbl in FACETS if tags_of("board", b["id"], fac))
    srcs = list(SOURCES.get(b["id"], [])) + [{"field": "parent", "url": h["source_url"], "title": h["source_title"], "accessed": h["accessed"], "quote": h["quote"]} for h in HOLD_BY_BOARD.get(b["id"], [])]
    parent_html = (f'<a href="{r}owners/{e(PARENT_OWNER[b["id"]])}/">{e(b["parent"])}</a>' if b["id"] in PARENT_OWNER else e(b["parent"]))
    owner_fact = "".join(f'<a href="{r}owners/{e(h["owner_id"])}/">{e(OWNERS[h["owner_id"]]["name"])}</a> <span class="muted small">({e(hold_phrase(h))})</span><br>' for h in {x["owner_id"]: x for x in reversed(HOLD_BY_BOARD.get(b["id"], []))}.values() if h["owner_id"] in OWNERS)
    p = prom(b); rk = RANK.get(b["id"]); nctry = len({c for c in split(b["countries_served"]) + ([b["hq_country"]] if b["hq_country"] else [])}); nlang = len(langs_of(b))
    if p["group"] == 0: rank_txt = f'<strong>#{p["g"]:,}</strong> in the world, tier <strong>{e(p["tier"])}</strong>. Tiers: Major is the top 1,000 sites, Large the top 10,000, Established the top 100,000 and Small the top million.'
    elif p["group"] == 1: rank_txt = f'<strong>#{p["g"]:,}</strong> for {e(rk["domain"])} as a whole. This site covers more than job listings, so the rank overstates its job board reach and no tier is given.'
    elif p["group"] == 2: rank_txt = f'Not comparable. This board is a section or subdomain of {e(rk["domain"])}, so the rank of that larger site does not describe it.'
    else: rank_txt = "Outside the top million sites." if rk else "Not yet measured."
    scale_li = "".join(f'<li>{int(x["value"]):,} {e(x["unit"])} <span class="muted small">as of {e(x["as_of"])}, self-reported on <a href="{e(x["url"])}" rel="noopener nofollow" target="_blank">its own site</a>{"" if x["quote_check"] == "ok" else ", read earlier and not re-checked"}</span></li>' for x in SCALE.get(b["id"], []))
    prom_html = (f'<h2>Prominence and reach</h2><dl class="facts">{fact("Web link popularity", rank_txt)}'
                 f'{fact("Recorded reach", f"So far we have recorded {nctry} countries and {nlang} languages (incomplete, especially for global boards)" if nctry or nlang else "Not recorded")}'
                 f'{fact("Self-reported scale", "<ul class=\"plain\">" + scale_li + "</ul>") if scale_li else ""}</dl>'
                 f'<p class="muted small">Rank source: Majestic Million, list of {e(RANK_DATE)}, licensed CC BY 3.0. It measures how widely a site is linked to, not how many jobs or visitors it has. <a href="{r}about/#prominence">How prominence is measured</a>.</p>')
    qn = b["name"]; hedge = " This has not yet been verified against the board's own site." if b["confidence"] == "seed-unverified" else ""
    faq = [(f"What is {qn}?", f'{qn} is {article(tdesc(b))} {tdesc(b)}' + (f' based in {country(b["hq_country"])}' if b["hq_country"] else "") + (f', focused on {b["niche"]}' if b["niche"] and b["niche"] != "general" else "") + "." + (f' It was founded in {b["founded"]}.' if b["founded"] else ""))]
    _own = [h for h in {x["owner_id"]: x for x in reversed(HOLD_BY_BOARD.get(b["id"], []))}.values() if h["owner_id"] in OWNERS]
    if _own: faq.append((f"Who owns {qn}?", f'According to this directory, {qn} is owned by {OWNERS[_own[0]["owner_id"]]["name"]} ({hold_phrase(_own[0]).lower()}).'))
    elif b["parent"]: faq.append((f"Who owns {qn}?", f'This directory records the parent of {qn} as {b["parent"]}.' + hedge))
    if b["api_status"] != "unknown": faq.append((f"Does {qn} have an API?", f'According to this directory, {qn} {api_text}.' + (f' Documentation: {b["api_docs_url"] or b["partner_url"]}.' if (b["api_docs_url"] or b["partner_url"]) else "") + hedge))
    if langs_of(b): faq.append((f"Which languages does {qn} support?", f'This directory records {qn} as supporting {", ".join(lang(c) for c in langs_of(b))}.' + hedge))
    if p["group"] == 0: faq.append((f"How large is {qn}?", f'{qn} ranks #{p["g"]:,} among all websites by web link popularity (Majestic Million, {RANK_DATE}), in the {p["tier"]} tier. This measures how widely the site is linked to, not traffic or job volume.'))
    if SCALE.get(b["id"]): _sc = SCALE[b["id"]][0]; faq.append((f"How many jobs does {qn} list?" if _sc["metric"] == "jobs_listed" else f"What scale does {qn} report?", f'{qn} reports {int(_sc["value"]):,} {_sc["unit"]} on its own site (as of {_sc["as_of"]}).'))
    cn = CONN.get(b["id"]); conn_html = ""; conn_json = []
    if cn and (cn["sends"] or cn["receives"] or cn["integrates"]):
        def other_name(rr, side): return rr["to_name"] if side == "to" else rr["from_name"]
        def li(rr, side):
            oid = rr["to_id"] if side == "to" else rr["from_id"]; nm = other_name(rr, side)
            lnk = f'<a href="{r}boards/{e(oid)}/">{e(nm)}</a>' if oid else e(nm)
            return f'<li>{lnk} <a class="muted small" href="{e(rr["source_url"])}" rel="noopener nofollow" target="_blank">source</a></li>'
        groups = (("Sends jobs to", [(rr, "to") for rr in cn["sends"].values() if rr["from_id"] == b["id"]]), ("Receives jobs from", [(rr, "from") for rr in cn["receives"].values() if rr["to_id"] == b["id"]]),
                  ("Integrates with", [(rr, "to" if rr["from_id"] == b["id"] else "from") for rr in cn["integrates"].values()]))
        conn_html = "<h2>Connections</h2><p class=\"muted small\">How this entry connects to other platforms, each from a page on one party's own site. Names that are not links are not yet in the directory.</p>"
        for lbl, items in groups:
            if not items: continue
            conn_html += f"<h3>{e(lbl)}</h3><ul class=\"conn\">" + "".join(li(rr, sd) for rr, sd in items[:30]) + "</ul>" + (f'<p class="muted small">and {len(items) - 30} more in the <a href="{r}data/boards/{e(b["id"])}.json">data file</a>.</p>' if len(items) > 30 else "")
            for rr, sd in items: conn_html += ""; conn_json.append({"group": lbl, "name": other_name(rr, sd), "id": rr["to_id"] if sd == "to" else rr["from_id"], "relation": rr["relation"], "source": rr["source_url"], "quote": rr["quote"]})
        _sn = [other_name(rr, sd) for rr, sd in groups[0][1][:6]]; _rn = [other_name(rr, sd) for rr, sd in groups[1][1][:6]]; _in = [other_name(rr, sd) for rr, sd in groups[2][1][:6]]
        _bits = ([f'sends jobs to {", ".join(_sn)}' + (" and others" if len(groups[0][1]) > 6 else "")] if _sn else []) + ([f'receives jobs from {", ".join(_rn)}' + (" and others" if len(groups[1][1]) > 6 else "")] if _rn else []) + ([f'integrates with {", ".join(_in)}' + (" and others" if len(groups[2][1]) > 6 else "")] if _in else [])
        faq.append((f"Which platforms does {qn} connect to?", f'According to this directory, {qn} ' + "; ".join(_bits) + "."))
    faq_html = '<section class="faq"><h2>Quick answers</h2>' + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq) + "</section>"
    mod_date = max([x["accessed"] for x in srcs if x.get("accessed")], default=TODAY)
    sources_html = ""
    if srcs:
        sources_html = ("<h2>Sources</h2><ol class=\"sources\">" + "".join(
            f'<li><span class="chip">{e(FIELD_LABEL.get(x["field"], x["field"]))}</span> <a href="{e(x["url"])}" rel="noopener nofollow" target="_blank">{e(x["title"])}</a>{" (secondary source)" if "wikipedia.org" in x["url"] or "wikidata.org" in x["url"] else ""} <span class="muted small">checked {e(x["accessed"])}</span>{('<div class="quote">' + e(x.get("quote","")) + '</div>') if x.get("quote") else ""}</li>' for x in srcs) + "</ol>")
    checked_on = max((x["accessed"] for x in srcs), default="")
    body = f"""<nav class="crumbs"><a href="{r}">Directory</a> / <a href="{r}regions/{slug(b["region"])}/">{e(b["region"])}</a> / {e(b["name"])}</nav>
<div class="titlerow">{icon(b, r, 64)}<h1>{e(b["name"])}</h1></div><p class="lede">{e(b["name"])} is {article(tdesc(b))} {e(tdesc(b))}{" based in " + e(country(b["hq_country"])) if b["hq_country"] else ""}{f", focused on {e(b['niche'])}" if b["niche"] and b["niche"] != "general" else ", serving all kinds of roles" if b["niche"] == "general" else ""}. It {api_text}. {e(partner)}</p>
<p>{api_badge(b["api_status"])} {conf_badge(b["confidence"])}</p>
<dl class="facts">{fact("Website", link(b["url"]))}{fact("Type", e(type_label(b)))}{fact("Review", e(review_text(b))) if review_text(b) else ""}{fact("Tags", tag_html) if tag_html else ""}{fact("Last checked", e(checked_on)) if checked_on else ""}{fact("Founded", e(b["founded"])) if b["founded"] else ""}{fact("Headquarters", f'<a href="{r}countries/{slug(country(b["hq_country"]))}/">{e(country(b["hq_country"]))}</a>' if b["hq_country"] else '<span class="muted">Not recorded</span>')}
{fact("Markets", chips(split(b["markets"]) if ";" in b["markets"] else [b["markets"]] if b["markets"] else []))}{fact("Region", f'<a href="{r}regions/{slug(b["region"])}/">{e(b["region"])}</a>')}
{fact("Primary language", f'<a href="{r}languages/{slug(lang(b["primary_language"]))}/">{e(lang(b["primary_language"]))}</a>' if b["primary_language"] else '<span class="muted">Not recorded</span>')}{fact("Languages supported", "".join(f'<a class="chip" href="{r}languages/{slug(lang(c))}/">{e(lang(c))}</a>' for c in langs_of(b)) or '<span class="muted">Not recorded</span>')}
{fact("Niche", e(b["niche"]) or '<span class="muted">Not recorded</span>')}{fact("Owner", owner_fact) if owner_fact else (fact("Parent organisation", parent_html) if b["parent"] else fact("Parent organisation", '<span class="muted">None recorded</span>'))}
{fact("Business model", e(b["business_model"]) or '<span class="muted">Not recorded</span>')}
{fact("API status", f'<a href="{r}api/{e(b["api_status"])}/">{e(API_LABEL[b["api_status"]])}</a>')}{fact("API or developer docs", link(b["api_docs_url"]))}
{fact("Partner program", e(b["partner_program"] or "unknown"))}{fact("Partner program link", link(b["partner_url"]))}
{fact("How jobs get in", chips(split(b["ingest_methods"])))}</dl>
{f'<h2>Notes</h2><p>{e(b["notes"])}</p>' if b["notes"] else ""}
<p class="muted small">{e(b["name"])} and its logo are trademarks of their respective owners. Icons are shown for identification only and do not imply affiliation or endorsement.</p>
{prom_html}
{faq_html}
{conn_html}
{sources_html}
<p class="notice">Only facts listed under Sources have been checked, and a listing by another directory only shows a board exists. Everything else on this page is unverified. <a href="{r}about/">How we research</a>.</p>
{"<h2>Other boards in " + e(b["region"]) + "</h2><ul>" + "".join(f'<li><a href="{r}boards/{x["id"]}/">{e(x["name"])}</a></li>' for x in siblings) + "</ul>" if siblings else ""}"""
    ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Directory","item":BASE+"/"},
      {"@type":"ListItem","position":2,"name":b["region"],"item":f'{BASE}/regions/{slug(b["region"])}/'},
      {"@type":"ListItem","position":3,"name":b["name"]}]}
    org = {"@context":"https://schema.org","@type":"Organization","name":b["name"],"url":b["url"]}
    if logo_info(b): org["logo"] = f'{BASE}/assets/logos/{logo_info(b)["file"]}'
    org["description"] = faq[0][1]
    if b["founded"]: org["foundingDate"] = b["founded"]
    if b["id"] in PARENT_OWNER and PARENT_OWNER[b["id"]] in OWNERS: org["parentOrganization"] = {"@type": "Organization", "name": OWNERS[PARENT_OWNER[b["id"]]]["name"], "url": f'{BASE}/owners/{PARENT_OWNER[b["id"]]}/'}
    if split(b["countries_served"]): org["areaServed"] = [country(c) for c in split(b["countries_served"])]
    if langs_of(b): org["knowsLanguage"] = langs_of(b)
    org["sameAs"] = list(dict.fromkeys([b["url"]] + [x["url"] for x in srcs if "wikipedia.org" in x["url"] or "wikidata.org" in x["url"]]))
    webpage = {"@context": "https://schema.org", "@type": "WebPage", "name": f'{b["name"]}: API, partner program and integration details', "url": f'{BASE}/boards/{b["id"]}/', "dateModified": mod_date,
               "isPartOf": {"@type": "WebSite", "name": NAME, "url": BASE + "/"}, "about": {"@type": "Organization", "name": b["name"]}}
    faqld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ld = [ld, org, webpage, faqld]
    md_b = (f'# {b["name"]}\n\n{faq[0][1]}\n\n' + "\n".join(f"- {k}: {v}" for k, v in [
        ("Website", b["url"]), ("Headquarters", country(b["hq_country"]) if b["hq_country"] else "not recorded"), ("Founded", b["founded"] or "not recorded"),
        ("Owner", (OWNERS[_own[0]["owner_id"]]["name"] + " (" + hold_phrase(_own[0]) + ")") if _own else (b["parent"] or "not recorded")),
        ("Languages", ", ".join(lang(c) for c in langs_of(b)) or "not recorded"), ("API status", API_LABEL.get(b["api_status"], b["api_status"]) + (f' ({b["api_docs_url"]})' if b["api_docs_url"] else "")),
        ("Partner program", b["partner_program"] or "unknown"), ("Prominence", (f'#{p["g"]:,} globally, tier {p["tier"]}' if p["group"] == 0 else p["label"])),
        ("Tags", ", ".join(TAX[t]["label"] for t in tags_of("board", b["id"])) or "none"), ("Review", review_text(b)), ("Data status", {"partially-verified": "partly verified against its own site", "secondary-sourced": "secondary sources only", "listed-only": "listed by another directory only"}.get(b["confidence"], "unverified"))] if v)
        + "\n\n## Quick answers\n\n" + "\n\n".join(f"**{q}** {a}" for q, a in faq[1:])
        + ("\n\n## Sources\n\n" + "\n".join(f'- [{x["title"] or x["url"]}]({x["url"]}) ({FIELD_LABEL.get(x["field"], x["field"])}, checked {x["accessed"]})' + (f': "{x["quote"]}"' if x.get("quote") else "") for x in srcs) if srcs else "")
        + f'\n\nCanonical page: {BASE}/boards/{b["id"]}/\nLast updated: {mod_date}\n')
    write(f'boards/{b["id"]}/index.html', layout(2, f'{b["name"]}: API, partner program and integration details | {NAME}',
      f'{b["name"]} ({b["type"]}{", " + country(b["hq_country"]) if b["hq_country"] else ""}{", " + lang(b["primary_language"]) if b["primary_language"] else ""}): API status, partner program, developer docs and how jobs are ingested.', body, f'/boards/{b["id"]}/', ld, noindex=not indexable(b), md=indexable(b)), indexed=indexable(b), mod=mod_date, md=md_b, kind="board")

# ---------- group pages (regions, countries, api status) ----------
def group_pages(kind, label_plural, keyfn, labelfn, blurbfn, titlefn, h1fn):
    groups = collections.defaultdict(list)
    for b in boards: groups[keyfn(b)].append(b)
    r1, r2 = "../", "../../"
    items = "".join(f'<li><a href="{slug(k) if kind!="api" else k}/">{e(labelfn(k))}</a> <span class="muted">({len(v)})</span></li>' for k, v in sorted(groups.items(), key=lambda kv: labelfn(kv[0])))
    write(f"{kind}/index.html", layout(1, f"Job boards by {label_plural} | {NAME}", f"Browse job boards and aggregators by {label_plural}.",
        f'<h1>Job boards by {label_plural}</h1><ul class="biglist">{items}</ul>', f"/{kind}/"))
    for k, v in groups.items():
        s = slug(k) if kind != "api" else k
        body = f'<nav class="crumbs"><a href="{r2}">Directory</a> / <a href="{r1}">By {label_plural}</a> / {e(labelfn(k))}</nav><h1>{e(h1fn(k))}</h1><p class="lede">{e(blurbfn(k, len(v)))}</p>' + table(sorted(v, key=lambda b: b["name"].lower()), r2)
        write(f"{kind}/{s}/index.html", layout(2, f"{titlefn(k)} | {NAME}", blurbfn(k, len(v)), body, f"/{kind}/{s}/", itemlist(v, 2), noindex=len(v) < 3), indexed=len(v) >= 3)

group_pages("regions", "region", lambda b: b["region"], lambda k: k,
  lambda k, n: f"{n} job boards, aggregators and platforms serving {k}, with API status and partner program details.",
  lambda k: f"Job boards in {k}", lambda k: f"Job boards in {k}")
# countries: boards headquartered in or serving each country
by_country = collections.defaultdict(list)
for b in boards:
    for c in dict.fromkeys([b["hq_country"]] + split(b["countries_served"])):
        if c: by_country[country(c)].append(b)
write("countries/index.html", layout(1, f"Job boards by country | {NAME}", "Browse job boards and aggregators by the country they are based in or serve.",
    '<h1>Job boards by country</h1><p class="lede">Boards are listed under the country where they are headquartered and any country they are known to serve.</p><ul class="biglist">'
    + "".join(f'<li><a href="{slug(k)}/">{e(k)}</a> <span class="muted">({len(v)})</span></li>' for k, v in sorted(by_country.items())) + "</ul>", "/countries/"))
for k, v in by_country.items():
    hq = [b for b in v if country(b["hq_country"]) == k]
    sv = len(v) - len(hq)
    nchk = sum(1 for b in v if b["confidence"] == "partially-verified")
    body = (f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">By country</a> / {e(k)}</nav><h1>Job boards in {e(k)}</h1>'
            f'<p class="lede">{len(v)} job boards and aggregators based in or serving {e(k)}: {len(hq)} headquartered there and {sv} based elsewhere that serve it. {nchk} have facts checked against their own pages or official sources.</p>{most_prominent(v)}'
            + table(sorted(v, key=lambda b: b["name"].lower()), "../../"))
    md_c = (f'# Job boards in {k}\n\n{len(v)} job boards and related entries based in or serving {k}.\n\n' + "\n".join(f'- [{b["name"]}]({BASE}/boards/{b["id"]}/): {b["type"]}' + (f', {prom(b)["tier"]} tier' if prom(b)["tier"] else "") + (f', {API_LABEL[b["api_status"]]}' if b["api_status"] != "unknown" else "") for b in sorted(v, key=skey)[:120]) + f'\n\nCanonical page: {BASE}/countries/{slug(k)}/\n')
    write(f"countries/{slug(k)}/index.html", layout(2, f"Job boards in {k}: APIs, partner programs and sources | {NAME}",
        f"{len(v)} job boards and aggregators based in or serving {k}, with API access, partner programs and cited sources.", body, f"/countries/{slug(k)}/", itemlist(v, 2), noindex=len(v) < 3, md=len(v) >= 3), indexed=len(v) >= 3, md=md_c, kind="country")
API_TITLE = {"on-request":"Job board APIs and feeds available on request","public-open":"Job boards with an open API","public-key":"Job board APIs with self-serve keys",
  "partner-only":"Partner-only job board APIs and feeds","deprecated":"Job boards with deprecated APIs","none-known":"Job boards with no known API","unknown":"Job boards with unresearched API status"}
group_pages("api", "API status", lambda b: b["api_status"], lambda k: API_LABEL[k],
  lambda k, n: f"{API_BLURB[k]} {n} listed.", lambda k: API_TITLE[k], lambda k: API_TITLE[k])

# ---------- languages ----------
by_lang = collections.defaultdict(list)
for b in boards:
    for c in langs_of(b): by_lang[c].append(b)
n_lang_rec = sum(1 for b in boards if langs_of(b))
lang_items = sorted(by_lang.items(), key=lambda kv: (-len(kv[1]), lang(kv[0])))
def lang_li(c, v): return f'<li><a href="{slug(lang(c))}/"><strong>{e(lang(c))}</strong></a>' + (f' <span class="muted">{e(NATIVE[c])}</span>' if NATIVE.get(c) and NATIVE[c] != lang(c) else "") + f' <span class="muted">({len(v)})</span></li>'
write("languages/index.html", layout(1, f"Job boards by language | {NAME}", f"Job boards and aggregators by the languages they support: {len(by_lang)} languages across {n_lang_rec} entries.",
    f'<h1>Job boards by language</h1><p class="lede">{len(by_lang)} languages across the {n_lang_rec} entries whose language we have recorded from the site\'s language menu or text. Entries are listed under their primary language and every other language they support, most widely supported first.</p>'
    f'<p class="muted small">{len(boards) - n_lang_rec} of the {len(boards)} entries have no language recorded yet, so these counts understate real coverage. To see every entry that supports a language, use the Language filter on the <a href="../">directory</a>.</p>'
    f'<h2>Most widely supported</h2><ul class="biglist">' + "".join(lang_li(c, v) for c, v in lang_items[:12]) + '</ul>'
    f'<h2>All languages</h2><ul class="biglist">' + "".join(lang_li(c, v) for c, v in sorted(lang_items, key=lambda kv: lang(kv[0]))) + "</ul>", "/languages/"))
for c in by_lang:  # old addresses that used the language code keep working
    if slug(lang(c)) != c:
        _d = OUT / "languages" / c; _d.mkdir(parents=True, exist_ok=True)
        (_d / "index.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(lang(c))}</title><meta name="robots" content="noindex"><link rel="canonical" href="{e(BASE)}/languages/{slug(lang(c))}/"><meta http-equiv="refresh" content="0; url=../{slug(lang(c))}/"></head><body><a href="../{slug(lang(c))}/">{e(lang(c))}</a></body></html>', encoding="utf-8")
for c, v in by_lang.items():
    prim = sum(1 for b in v if b["primary_language"] == c)
    body = (f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">By language</a> / {e(lang(c))}</nav><h1>{e(lang(c))} job boards</h1>'
            f'<p class="lede">{len(v)} entries that support {e(lang(c))}{(" (" + e(NATIVE[c]) + ")") if NATIVE.get(c) and NATIVE[c] != lang(c) else ""}, of which {prim} use it as their primary language.</p>'
            + table(sorted(v, key=lambda b: b["name"].lower()), "../../"))
    write(f"languages/{slug(lang(c))}/index.html", layout(2, f"{lang(c)} job boards and aggregators | {NAME}",
        f"{len(v)} job boards and aggregators supporting {lang(c)}, with API access and partner program details.", body, f"/languages/{slug(lang(c))}/", itemlist(v, 2), noindex=len(v) < 3), indexed=len(v) >= 3)

# ---------- ATS ----------
write("ats/index.html", layout(1, f"Applicant tracking systems: job feeds, APIs and partner programs | {NAME}",
  f"{len(ats)} applicant tracking systems compared by public job feed, API access, partner programs, owners and customer segment.",
  f'<h1>Applicant tracking systems</h1><p class="lede">Which ATS platforms expose public job feeds, which need keys, and which run partner marketplaces, with owners and customer segments. These systems are where most employers publish their jobs from, so their openness decides how jobs reach boards.</p>' + table(sorted(ats, key=lambda b: b["name"].lower()), "../")
  + '<p class="muted small">ATS systems are part of the main directory, so filter by Type: Applicant tracking system on the home page, or see <a href="../tags/ats/">the tag page</a>.</p>', "/ats/", itemlist(ats, 1)), mod=TODAY)
for a in ats:  # old addresses keep working
    p_ = OUT / "ats" / a["id"]; p_.mkdir(parents=True, exist_ok=True)
    (p_ / "index.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(a["name"])}</title><meta name="robots" content="noindex"><link rel="canonical" href="{e(BASE)}/boards/{e(a["id"])}/"><meta http-equiv="refresh" content="0; url=../../boards/{e(a["id"])}/"></head><body><a href="../../boards/{e(a["id"])}/">{e(a["name"])}</a></body></html>', encoding="utf-8")

# ---------- about ----------
about = f"""<h1>About and methodology</h1><div class="prose">
<p>{e(NAME)} is an open, free directory maintained by {e(CFG["author"])}. It exists to give a neutral view of how job boards, aggregators and ATS systems are organised by market, region and country, and how open each is to integration.</p>
<h2>How the data is compiled</h2><p>The initial list was compiled from general industry knowledge. Each entry is then checked against the board's own documentation, developer portal or pricing pages, and every checked fact is listed under Sources on its page with the date it was read. Entries with no cited sources carry an Unverified label. Entries cited only to another directory or to a partner list carry a Listed only label, because that shows a board exists but nothing else. Some large sites block automated access, and those stay Unverified until they can be checked another way. Where a site's terms forbid scraping, we read only its public pages and do not collect data by automated means.</p>
<h2>Definitions</h2><ul><li><strong>Open API:</strong> usable without approval.</li><li><strong>Self-serve API key:</strong> documented API with a signup or key request.</li>
<li><strong>Partner-only:</strong> access requires an approved partner or commercial agreement.</li><li><strong>No known API:</strong> nothing publicly documented was found.</li><li><strong>Unknown:</strong> not yet researched.</li></ul>
<h2>Trademarks and logos</h2><p>Names and icons shown in this directory belong to their respective owners and are used only to identify the services described. Their use does not imply any affiliation with or endorsement by those owners. Owners who would like an icon removed or changed can open an issue on the project repository.</p>
<h2 id="prominence">How prominence is measured</h2><p>There is no free, trustworthy measure of how many jobs or candidates each board has, so the directory shows several separate signals instead of one score.</p>
<ul><li><strong>Web link popularity:</strong> the global rank of a board's domain in the Majestic Million, which ranks sites by how many distinct networks link to them. Majestic data is licensed CC BY 3.0. It measures how widely a site is linked to, not traffic, jobs or revenue. Tiers: Major (top 1,000), Large (top 10,000), Established (top 100,000), Small (top million).</li>
<li><strong>Comparable or not:</strong> a tier is given only when the board owns its whole domain. A board that is a section or subdomain of a larger site (for example a product page of a big company) shows Not comparable. A site that covers much more than job listings, such as a classifieds or review site, shows Site-wide and gets no tier.</li>
<li><strong>Recorded reach:</strong> the number of countries and languages we have recorded for the board. It only counts what we have found, so it understates global boards.</li>
<li><strong>Self-reported scale:</strong> figures a board publishes about itself, such as jobs listed, with the date read and a quote. They are snapshots and are not comparable between boards.</li></ul>
<p>Tiers are for orientation, not endorsement.</p>
<h2 id="cite">How to cite this dataset</h2><p>Cite the page you used and the date you read it, because entries change as research continues. Suggested form:</p>
<p><code>{e(CFG["author"])}. {e(NAME)}: an open directory of job boards, aggregators, ATS systems and their owners. {e(BASE)}/. Accessed {TODAY}.</code></p>
<p>Each entry page lists its sources with the date each was read. Machine readable copies: <a href="../data/boards.json">boards.json</a>, <a href="../data/owners.json">owners.json</a>, <a href="../data/taxonomy.json">taxonomy.json</a> and the <a href="../downloads/job_boards.csv">CSV files</a>.</p>
<h2 id="ai">For AI systems and crawlers</h2><p>An index for language models is at <a href="../llms.txt">llms.txt</a>, and the full text of the main pages is at <a href="../llms-full.txt">llms-full.txt</a>. Every indexable page also has a Markdown version at the same address ending in <code>index.md</code>. Facts marked unverified have not been checked against the board's own site, and statements are attributed to this directory, so please repeat that attribution when quoting.</p>
<h2>Privacy</h2><p>This site uses Google Analytics to measure traffic. It may set cookies in your browser.</p>\n<h2>Corrections and downloads</h2><p>Spotted something wrong or missing? Open an issue or pull request on the project repository. The full dataset is available as <a href="../downloads/job_boards.csv">CSV</a>, <a href="../downloads/job_boards.json">JSON</a> the <a href="../downloads/sources.csv">sources table</a>, <a href="../downloads/rank.csv">rank data</a> and <a href="../downloads/scale.csv">scale figures</a>.</p></div>"""
write("about/index.html", layout(1, f"Methodology and data definitions | {NAME}", "How the job board directory is compiled, what each API status means, and how to report corrections.", about, "/about/"))

# ---------- assets, downloads, robots, sitemap, 404 ----------
(OUT / "assets").mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT/"site_src"/"style.css", OUT/"assets"/"style.css"); shutil.copy(ROOT/"site_src"/"app.js", OUT/"assets"/"app.js"); shutil.copy(ROOT/"site_src"/"eco.js", OUT/"assets"/"eco.js")
if (ROOT/"site_src"/"logos").exists(): shutil.copytree(ROOT/"site_src"/"logos", OUT/"assets"/"logos", dirs_exist_ok=True)
(OUT/"downloads").mkdir(exist_ok=True)
for n in ("job_boards.csv","sources.csv","rank.csv","scale.csv","owners.csv","ownership.csv","owner_facts.csv","taxonomy.csv","tags.csv","reviews.csv","relationships.csv","languages.csv"): shutil.copy(ROOT/"data"/n, OUT/"downloads"/n)
(OUT/"downloads"/"job_boards.json").write_text(json.dumps(boards, indent=1, ensure_ascii=False), encoding="utf-8")
(OUT/".nojekyll").write_text("")
# ---------- tags ----------
by_id = {b["id"]: b for b in boards}
members = collections.defaultdict(lambda: {"board": [], "ats": []})
for (kind, i), ts in TAGS_BY.items():
    for t in ts:
        if t in TAX: members[t][kind].append(i)
tag_idx = ""
for fac, lbl in FACETS:
    items = [(t, r) for t, r in TAX.items() if r["facet"] == fac and (members[t]["board"] or members[t]["ats"])]
    if not items: continue
    tag_idx += f'<h2>{e(lbl)}</h2><ul class="taglist">' + "".join(f'<li><a href="{e(t)}/"><strong>{e(r["label"])}</strong></a> <span class="muted">({len(members[t]["board"]) + len(members[t]["ats"])})</span><div class="muted small">{e(r["definition"])}</div></li>' for t, r in items) + "</ul>"
write("tags/index.html", layout(1, f"Types of job sites explained: job boards, ATS, staffing, outplacement and more | {NAME}", "A taxonomy of job boards, aggregators, applicant tracking systems, staffing, outplacement and labour market information sources, with definitions.",
    f'<h1>Types of job sites, explained</h1><p class="lede">Every entry in the directory is tagged by what it is, who it is for, how it makes money and how open it is to integration. Use the tags to filter, group and compare.</p>{tag_idx}', "/tags/"))
for t, r in TAX.items():
    mb = [by_id[i] for i in members[t]["board"] if i in by_id]; ma = []
    if not mb and not ma: continue
    body = f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">Types</a> / {e(r["label"])}</nav><h1>{e(r["label"])}</h1><p class="lede">{e(r["definition"])} {len(mb) + len(ma)} entries are tagged this way.</p>'
    if mb: body += table(mb, "../../")
    if ma: body += '<h2>Applicant tracking systems</h2><div class="tablewrap"><table><thead><tr><th>ATS</th><th>Segment</th><th>HQ</th><th>Public job feed</th><th>Partner program</th></tr></thead><tbody>' + "".join(ats_row(a, "../../") for a in ma) + "</tbody></table></div>"
    n = len(mb) + len(ma); idx = n >= 3
    md_t = (f'# {r["label"]}\n\n{r["definition"]} {n} entries in the directory.\n\n' + "\n".join(f'- [{b["name"]}]({BASE}/boards/{b["id"]}/): {b["type"]}' + (f', {API_LABEL[b["api_status"]]}' if b["api_status"] != "unknown" else "") for b in sorted(mb, key=skey)[:80])
            + ("\n\n## Applicant tracking systems\n\n" + "\n".join(f'- [{a["name"]}]({BASE}/ats/{a["id"]}/): {a["vendor"]}, {a["segment"]}' for a in ma) if ma else "") + f'\n\nCanonical page: {BASE}/tags/{t}/\n')
    write(f"tags/{t}/index.html", layout(2, f"{r['label']}: {r['facet']} tag | {NAME}" if r["facet"] != "function" else f"{r['label']}: directory and examples | {NAME}", f"{r['definition']} {n} entries in the directory.", body, f"/tags/{t}/", itemlist(mb, 2) if mb else None, noindex=not idx, md=idx), indexed=idx, md=md_t, kind="tag")
# ---------- owners ----------
def owner_boards(oid):
    ids = list(dict.fromkeys([h["board_id"] for h in HOLD if h["owner_id"] == oid and h["board_id"] and h["relation"] != "former"] + [i for i, o in PARENT_OWNER.items() if o == oid]))
    return [b for i in ids for b in boards if b["id"] == i]
def owner_lede(o, ncur, nb):
    if ncur: return f'has {ncur} HR holdings recorded here, including {nb} job boards in this directory. Ownership is shown with the relationship, stake and year where a source states them.'
    return f'is recorded as the parent of {nb} entries in this directory. No profile or holdings research has been done for it yet. The parent shown comes from each entry\'s own record, so check the entry page for its source.'
def holding_li(h):
    nm = f'<a href="{e(h["holding_url"])}" rel="noopener nofollow" target="_blank">{e(h["holding_name"])}</a>' if h["holding_url"] else e(h["holding_name"])
    return f'<li><strong>{nm}</strong> <span class="muted small">{e(hold_phrase(h))}. Source: <a href="{e(h["source_url"])}" rel="noopener nofollow" target="_blank">{e(h["source_title"] or "page")}</a>{" (secondary source)" if "wikipedia.org" in h["source_url"] or "wikidata.org" in h["source_url"] else ""}, checked {e(h["accessed"])}</span><div class="quote">{e(h["quote"])}</div></li>'
owner_rows = []
for oid, o in OWNERS.items():
    hs = [h for h in HOLD if h["owner_id"] == oid]
    ob = owner_boards(oid); nb = len(ob)
    if not hs and not ob: continue
    cur = [h for h in hs if h["relation"] != "former"]; former = [h for h in hs if h["relation"] == "former"]
    others = [h for h in cur if not (h["board_id"] and any(b["id"] == h["board_id"] for b in boards))]
    facts_o = OWNER_FACTS.get(oid, {})
    def src_link(f): return f'<a href="{e(f["source_url"])}" rel="noopener nofollow" target="_blank">source</a>{" (secondary)" if "wikipedia.org" in f["source_url"] or "wikidata.org" in f["source_url"] else ""}'
    profile_html = ""
    if facts_o.get("description"):
        d_ = facts_o["description"]
        profile_html += f'<h2>About</h2><blockquote class="about">{e(d_["value"])}<footer>In its own words, from <a href="{e(d_["source_url"])}" rel="noopener nofollow" target="_blank">{e(d_["source_title"] or "its website")}</a>{" (secondary source)" if "wikipedia.org" in d_["source_url"] else ""}, checked {e(d_["accessed"])}</footer></blockquote>'
    glance = []
    city, ctry = facts_o.get("hq_city"), facts_o.get("hq_country")
    if city or ctry:
        loc = ", ".join(x for x in [city["value"] if city else "", country(ctry["value"]) if ctry else ""] if x)
        glance.append(("Headquarters", f'{e(loc)} <span class="muted small">({src_link(city or ctry)})</span>'))
    for key, label in (("founded", "Founded"), ("listing", "Listing"), ("employees", "Employees"), ("revenue", "Revenue")):
        if facts_o.get(key): glance.append((label, f'{e(facts_o[key]["value"])} <span class="muted small">({src_link(facts_o[key])})</span>'))
    if glance: profile_html += '<h2>At a glance</h2><dl class="facts">' + "".join(fact(k, v) for k, v in glance) + '</dl><p class="muted small">Each fact links to the page it was read from. Figures change, so check the source date.</p>'
    sections = ""
    for cat in CAT_LABEL:
        items = [h for h in others if h["category"] == cat]
        if items: sections += f'<h2>{e(CAT_LABEL[cat])}</h2><ul class="holdings">' + "".join(holding_li(h) for h in items) + "</ul>"
    if former: sections += "<h2>Formerly owned</h2><ul class=\"holdings\">" + "".join(holding_li(h) for h in former) + "</ul>"
    body = (f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">Owners</a> / {e(o["name"])}</nav><h1>{e(o["name"])}: HR holdings</h1>'
            f'<p class="lede">{e(o["name"])}{" (" + e(country(o["country"])) + ")" if o["country"] else ""} {owner_lede(o, len(cur), nb)}</p>'
            + profile_html + (f'<h2>Job boards in this directory</h2>' + table(ob, "../../") if ob else "") + sections
            + f'<p class="muted small">Each holding is cited to a page and quote. Ownership changes often, so check the date. {("Owner website: " + e(o["url"])) if o["url"] else ""}</p>')
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": o["name"], **({"url": o["url"]} if o["url"] else {}),
          **({"foundingDate": facts_o["founded"]["value"]} if facts_o.get("founded") else {}),
          **({"address": {"@type": "PostalAddress", "addressCountry": facts_o["hq_country"]["value"].replace("UK", "GB")}} if facts_o.get("hq_country") else {})}
    idx = len(cur) >= 3 or bool(facts_o)
    md_o = (f'# {o["name"]}: HR holdings\n\n' + (f'{facts_o["description"]["value"]} (own description, {facts_o["description"]["source_url"]})\n\n' if facts_o.get("description") else "")
            + "\n".join(f'- {lbl}: {facts_o[k]["value"]}' for k, lbl in (("hq_city", "Headquarters city"), ("hq_country", "Headquarters country"), ("founded", "Founded"), ("listing", "Listing"), ("employees", "Employees"), ("revenue", "Revenue")) if facts_o.get(k))
            + (f'\n\n## Job boards in this directory\n\n' + "\n".join(f'- [{b["name"]}]({BASE}/boards/{b["id"]}/) ({b["type"]})' for b in ob) if ob else "")
            + (f'\n\n## Holdings\n\n' + "\n".join(f'- {h["holding_name"]}: {hold_phrase(h)}; {CAT_LABEL[h["category"]]}. Source: {h["source_url"]} "{h["quote"]}"' for h in cur if h["category"] in CAT_LABEL) if cur else "")
            + (f'\n\n## Formerly owned\n\n' + "\n".join(f'- {h["holding_name"]}: {h["quote"]} ({h["source_url"]})' for h in former) if former else "")
            + f'\n\nCanonical page: {BASE}/owners/{oid}/\n')
    write(f"owners/{oid}/index.html", layout(2, f"{o['name']}: job boards and other HR businesses owned | {NAME}",
        f"What {o['name']} owns in the HR space: {nb} job boards in this directory plus staffing, HR technology and other holdings, with cited sources.", body, f"/owners/{oid}/", ld, noindex=not idx, md=idx), indexed=idx, md=md_o, kind="owner")
    owner_rows.append((oid, o, len(cur), nb))
if owner_rows:
    li = "".join(f'<li><a href="{e(oid)}/">{e(o["name"])}</a> <span class="muted">({n} HR holdings, {nb} job boards here)</span></li>' for oid, o, n, nb in sorted(owner_rows, key=lambda x: -x[2]))
    write("owners/index.html", layout(1, f"Who owns the job boards: owners and HR holdings | {NAME}", "Parent companies behind the major job boards and what else they own in the HR space, with cited sources.",
        f'<h1>Who owns the job boards</h1><p class="lede">The companies behind the major job boards, and what else they own in the HR space: staffing firms, recruiting technology and services. Every holding is cited.</p><ul class="biglist">{li}</ul>', "/owners/"))
# ---------- ecosystem ----------
def layer_of(i):
    tg = set(tags_of("board", i)); return 0 if "ats" in tg else 1 if "job-distribution" in tg else 2
resolved = [x for x in REL if x["from_id"] in by_id and x["to_id"] in by_id]
deg_all = collections.Counter()
for x in REL:
    if x["from_id"]: deg_all[x["from_id"]] += 1
    if x["to_id"]: deg_all[x["to_id"]] += 1
def role(i): return {0: "ATS", 1: "Distribution", 2: "Board or aggregator"}[layer_of(i)]
# matrix: senders (ATS and distribution platforms) across, receivers (boards and aggregators) down
cell = {}
for x in resolved:
    if layer_of(x["from_id"]) < 2 and layer_of(x["to_id"]) == 2:
        k = (x["from_id"], x["to_id"])
        if k not in cell or x["relation"] == "sends-jobs-to": cell[k] = x
send_deg = collections.Counter(k[0] for k in cell); recv_deg = collections.Counter(k[1] for k in cell)
cols = [i for i, _ in send_deg.most_common(14)]; rows_ = [i for i, _ in recv_deg.most_common(40)]
def mcell(fi, ti):
    x = cell.get((fi, ti))
    if not x: return "<td></td>"
    snd = x["relation"] == "sends-jobs-to"; lab = f'{by_id[fi]["name"]} {"sends jobs to" if snd else "integrates with"} {by_id[ti]["name"]}'
    return f'<td class="{"s" if snd else "i"}"><a href="{e(x["source_url"])}" rel="noopener nofollow" target="_blank" title="{e(lab)}. Open the source page." aria-label="{e(lab)}">{"&#9679;" if snd else "&#9675;"}</a></td>'
head = "".join(f'<th class="col" scope="col"><a href="../boards/{e(i)}/"><span>{e(by_id[i]["name"])}</span></a></th>' for i in cols)
body_rows = "".join(f'<tr data-name="{e(by_id[t]["name"].lower())}"><th scope="row"><a href="../boards/{e(t)}/">{e(by_id[t]["name"])}</a></th>' + "".join(mcell(c, t) for c in cols) + f'<td class="tot">{sum(1 for c in cols if (c, t) in cell)}</td></tr>' for t in rows_)
matrix = (f'<div class="matrixwrap" tabindex="0" role="region" aria-label="Compatibility matrix, scrollable"><table class="matrix"><thead><tr><th class="corner" scope="col">Boards and aggregators</th>{head}<th class="tot" scope="col">Total</th></tr></thead><tbody>{body_rows}</tbody></table></div>')
# connections not shown in the matrix, grouped by who is listing them
shown_keys = {(a, b) for (a, b) in cell}
other = collections.defaultdict(list)
for x in resolved:
    if (x["from_id"], x["to_id"]) in shown_keys: continue
    other[(x["from_id"], x["relation"])].append(x)
other_html = "".join(f'<li><a href="../boards/{e(fi)}/"><strong>{e(by_id[fi]["name"])}</strong></a> {"sends jobs to" if rel == "sends-jobs-to" else "integrates with"}: ' + ", ".join(f'<a href="../boards/{e(x["to_id"])}/">{e(x["to_name"])}</a> <a class="muted small" href="{e(x["source_url"])}" rel="noopener nofollow" target="_blank">source</a>' for x in xs[:20]) + (f" and {len(xs) - 20} more" if len(xs) > 20 else "") + "</li>" for (fi, rel), xs in sorted(other.items(), key=lambda kv: -len(kv[1])))
layer_counts = collections.Counter(layer_of(i) for i in deg_all if i in by_id)
flow = "".join(f'<div class="flowbox"><strong>{e(t)}</strong><span>{n} connected entries</span><span class="muted small">{e(sb)}</span></div>' + ('<div class="flowarrow" aria-hidden="true">&rarr;</div>' if k < 2 else "") for k, (t, sb, n) in enumerate((("Applicant tracking systems", "where employers manage hiring", layer_counts[0]), ("Distribution platforms", "push jobs to many sites", layer_counts[1]), ("Boards and aggregators", "where candidates search", layer_counts[2]))))
unres = sorted({x["from_name"] for x in REL if not x["from_id"]} | {x["to_name"] for x in REL if not x["to_id"]}, key=str.lower)
hub_rows = "".join(f'<tr><td><a href="../boards/{e(i)}/"><strong>{e(by_id[i]["name"])}</strong></a></td><td>{e(role(i))}</td><td>{n}</td></tr>' for i, n in deg_all.most_common(14) if i in by_id)
def _lnk(i, nm): return f'<a href="../boards/{e(i)}/">{e(nm)}</a>' if i else e(nm)
edge_rows = "".join(f'<tr><td>{_lnk(x["from_id"], x["from_name"])}</td><td>{"sends jobs to" if x["relation"] == "sends-jobs-to" else "integrates with"}</td><td>{_lnk(x["to_id"], x["to_name"])}</td><td><a href="{e(x["source_url"])}" rel="noopener nofollow" target="_blank">source</a></td></tr>' for x in sorted(REL, key=lambda x: (x["from_name"].lower(), x["to_name"].lower())))
eco_body = (f'<h1>The hiring ecosystem map</h1><p class="lede">Employers manage hiring in an applicant tracking system, which pushes jobs to boards and aggregators directly or through distribution platforms, and candidates find them there. This page maps the {len(REL)} connections documented on the platforms\' own pages, {len(resolved)} of them between entries in this directory.</p>'
    f'<div class="flow">{flow}</div>'
    f'<h2>Who sends jobs to whom</h2><p class="muted small">Each row is a board or aggregator and each column an ATS or distribution platform. A filled circle means the column sends jobs to the row. A hollow circle means the two integrate in a way the page does not describe as a job feed. Select a mark to open the page that states it. An empty cell means we have not found a stated connection, not that none exists.</p>'
    f'<label class="ecofilter">Filter boards<input id="ecofilter" type="search" placeholder="Type a board name" autocomplete="off"></label>{matrix}'
    f'<h2>Other documented connections</h2><p class="muted small">Connections between entries that do not fit the matrix, such as platforms listing each other or boards that feed a public employment service.</p><ul class="plainlist">{other_html}</ul>'
    f'<h2>Most connected</h2><div class="tablewrap"><table><thead><tr><th>Entry</th><th>Role</th><th>Documented connections</th></tr></thead><tbody>{hub_rows}</tbody></table></div>'
    f'<h2>Every documented connection</h2><div class="tablewrap"><table><thead><tr><th>From</th><th>Relationship</th><th>To</th><th>Source</th></tr></thead><tbody>{edge_rows}</tbody></table></div>'
    f'<h2>Partners not yet in the directory</h2><p>{len(unres)} partner names appear on these pages but are not yet entries here: ' + ", ".join(e(n) for n in unres[:60]) + (f" and {len(unres) - 60} more" if len(unres) > 60 else "") + '.</p><script src="../assets/eco.js" defer></script>')
md_eco = ("# The hiring ecosystem map\n\nDocumented connections between applicant tracking systems, distribution platforms and job boards, each from a page on one party's own site.\n\n"
          + "\n".join(f'- {x["from_name"]} {"sends jobs to" if x["relation"] == "sends-jobs-to" else "integrates with"} {x["to_name"]} ({x["source_url"]})' for x in sorted(REL, key=lambda x: (x["from_name"].lower(), x["to_name"].lower())))
          + f'\n\nCanonical page: {BASE}/ecosystem/\n')
write("ecosystem/index.html", layout(1, f"The hiring ecosystem map: how ATS systems, distribution platforms and job boards connect | {NAME}",
    f"Documented connections between applicant tracking systems, job distribution platforms and job boards: who sends jobs to whom, with a source for every link.", eco_body, "/ecosystem/", itemlist([by_id[i] for i, _ in deg_all.most_common(30) if i in by_id], 1), noindex=len(REL) < 10, md=len(REL) >= 10), indexed=len(REL) >= 10, md=md_eco, kind="tag")
# ---------- rankings ----------
comparable = sorted([b for b in boards if prom(b)["group"] == 0], key=skey)
rk_rows = "".join(f'<tr><td>{i}</td><td><div class="namecell">{icon(b, "../")}<a href="../boards/{b["id"]}/"><strong>{e(b["name"])}</strong></a></div></td><td><span class="badge tier-{e(prom(b)["tier"])}">{e(prom(b)["tier"])}</span> <span class="muted small">#{prom(b)["g"]:,}</span></td><td>{e(b["type"])}</td><td>{e(b["region"])}</td></tr>' for i, b in enumerate(comparable[:60], 1))
write("rankings/index.html", layout(1, f"Largest job boards in the world by web link popularity | {NAME}",
  f"The most widely linked job boards, aggregators and employment sites, ranked by Majestic Million web link popularity across {len(comparable)} measured boards.",
  f'<h1>Largest job boards by web link popularity</h1><p class="lede">The {min(60, len(comparable))} most widely linked job boards and aggregators among the {len(boards)} in this directory. Rank is the global position of the board\'s domain in the Majestic Million as of {e(RANK_DATE)}. It measures how widely a site is linked to, not traffic or job volume.</p>'
  f'<div class="tablewrap"><table><thead><tr><th>#</th><th>Board</th><th>Tier and global rank</th><th>Type</th><th>Region</th></tr></thead><tbody>{rk_rows}</tbody></table></div>'
  f'<h2>What is left out</h2><p>Boards that are a section of a larger site (such as a product page on a major company site) and sites that cover much more than jobs (such as classifieds or review sites) are not ranked here because their domain rank does not describe the job board. They still appear in the directory with the reason. <a href="../about/#prominence">How prominence is measured</a>. Rank data: <a href="https://majestic.com/reports/majestic-million" rel="noopener nofollow">Majestic Million</a>, CC BY 3.0.</p>', "/rankings/", itemlist(comparable[:50], 1)))
# ---------- JSON data API, changelog and feed ----------
(OUT/"data"/"boards").mkdir(parents=True, exist_ok=True)
def board_json(b):
    d = {k: v for k, v in b.items()}
    for k in ("countries_served", "languages_supported", "ingest_methods"): d[k] = split(b[k])
    d["page"] = f'{BASE}/boards/{b["id"]}/'; d["indexable"] = indexable(b)
    p = prom(b); d["prominence"] = {"tier": p["tier"], "label": p["label"], "global_rank": p["g"] or None, "scope": p["scope"], "source": "Majestic Million (CC BY 3.0)", "list_date": RANK_DATE}
    d["tags"] = tags_of("board", b["id"])
    d["connections"] = [{"relation": x["relation"], "from": x["from_name"], "from_id": x["from_id"], "to": x["to_name"], "to_id": x["to_id"], "source": x["source_url"], "quote": x["quote"]} for x in REL if b["id"] in (x["from_id"], x["to_id"])]
    d["review"] = REVIEWS.get(b["id"])
    d["owners"] = [{"id": h["owner_id"], "name": OWNERS[h["owner_id"]]["name"], "relation": h["relation"], "stake": h["stake"], "since": h["since"], "source": h["source_url"], "quote": h["quote"]} for h in HOLD_BY_BOARD.get(b["id"], []) if h["owner_id"] in OWNERS]
    d["scale"] = [{k: x[k] for k in ("metric", "value", "unit", "as_of", "url", "quote", "quote_check")} for x in SCALE.get(b["id"], [])]
    d["sources"] = [{k: x.get(k, "") for k in ("field", "url", "title", "accessed", "quote", "quote_check")} for x in SOURCES.get(b["id"], [])]
    return d
allj = [board_json(b) for b in boards]
(OUT/"data"/"boards.json").write_text(json.dumps({"generated": TODAY, "count": len(allj), "boards": allj}, indent=1, ensure_ascii=False), encoding="utf-8")
(OUT/"data"/"relationships.json").write_text(json.dumps({"generated": TODAY, "count": len(REL), "relationships": REL}, indent=1, ensure_ascii=False), encoding="utf-8")
(OUT/"data"/"taxonomy.json").write_text(json.dumps({"generated": TODAY, "tags": list(TAX.values())}, indent=1, ensure_ascii=False), encoding="utf-8")
(OUT/"data"/"owners.json").write_text(json.dumps({"generated": TODAY, "owners": [{**o, "profile": {k: {"value": f["value"], "source": f["source_url"], "quote": f["quote"]} for k, f in OWNER_FACTS.get(oid, {}).items()}, "holdings": [h for h in HOLD if h["owner_id"] == oid]} for oid, o in OWNERS.items()]}, indent=1, ensure_ascii=False), encoding="utf-8")
for d in allj: (OUT/"data"/"boards"/f'{d["id"]}.json').write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
log = load("ingest_log.csv") if (ROOT/"data"/"ingest_log.csv").exists() else []
rows_html = "".join(f'<tr><td>{e(x["date"])}</td><td>{e(x["files"])}</td><td>{e(x["added"])}</td><td>{e(x["merged"])}</td><td>{e(x["rejected"])}</td><td>{e(x["conflicts"])}</td></tr>' for x in reversed(log))
write("changelog/index.html", layout(1, f"Research log and changelog | {NAME}", "What was added, merged or rejected in each research run of the job board directory.",
  f'<h1>Research log</h1><p class="lede">Every research run is logged here: boards added, boards merged into existing entries, and items rejected because they lacked a confirmed source. The directory currently holds {len(boards)} boards.</p><div class="tablewrap"><table><thead><tr><th>Date</th><th>Findings files</th><th>Added</th><th>Merged</th><th>Rejected</th><th>Conflicts</th></tr></thead><tbody>{rows_html}</tbody></table></div>', "/changelog/"))
entries = "".join(f'<entry><id>tag:{BASE.split("//")[-1].split("/")[0]},{x["date"]}:run{i}</id><title>Research run {e(x["date"])}: {e(x["added"])} boards added, {e(x["merged"])} merged</title><updated>{e(x["date"])}T00:00:00Z</updated><link href="{e(BASE)}/changelog/"/><summary>{e(x["rejected"])} items rejected, {e(x["conflicts"])} conflicts logged.</summary></entry>' for i, x in enumerate(reversed(log)))
(OUT/"feed.xml").write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>{e(BASE)}/</id><title>{e(NAME)} research log</title><updated>{TODAY}T00:00:00Z</updated><link href="{e(BASE)}/feed.xml" rel="self"/><link href="{e(BASE)}/changelog/"/>{entries}</feed>', encoding="utf-8")
if (ROOT/"site_src"/"og.png").exists(): shutil.copy(ROOT/"site_src"/"og.png", OUT/"assets"/"og.png")
# ---------- AI-facing files ----------
order = {"board": 0, "owner": 1, "tag": 2, "country": 3}
n_idx = {k: sum(1 for kk, _, _ in MD_PAGES if kk == k) for k in order}
llms = f"""# {NAME}

> {CFG["tagline"]}. {len(boards)} entries (job boards, aggregators, {len(ats)} applicant tracking systems, staffing firms, labour market information sources and other HR services) and {len(OWNERS)} owner companies, each with cited sources. Updated {TODAY}.

Notes for readers and models: facts are attributed to this directory and carry the date they were checked. Entries marked unverified have not been checked against the board's own site. Prominence uses Majestic Million web link popularity (CC BY 3.0), which measures how widely a site is linked to, not traffic. Every indexable page has a Markdown version at the same address ending in index.md.

## Start here
- [Directory home]({BASE}/): searchable table with filters for type, focus, API access, language and prominence
- [Types of job sites, explained]({BASE}/tags/): definitions and lists for job boards, aggregators, ATS, staffing, outplacement and labour market information
- [The hiring ecosystem map]({BASE}/ecosystem/): documented connections between ATS systems, distribution platforms and boards\n- [Largest job boards by web link popularity]({BASE}/rankings/)
- [Who owns the job boards]({BASE}/owners/): parent companies with profiles and holdings
- [Job boards by country]({BASE}/countries/)
- [Methodology and how to cite]({BASE}/about/)

## Data
- [All entries as JSON with sources]({BASE}/data/boards.json)
- [Owners and holdings as JSON]({BASE}/data/owners.json)
- [Taxonomy as JSON]({BASE}/data/taxonomy.json)\n- [Documented connections as JSON]({BASE}/data/relationships.json)
- [Entries as CSV]({BASE}/downloads/job_boards.csv)
- [Sources as CSV]({BASE}/downloads/sources.csv)

## Optional
- [Full text of the main pages]({BASE}/llms-full.txt)
- [Research log]({BASE}/changelog/)
- [Atom feed]({BASE}/feed.xml)
"""
(OUT/"llms.txt").write_text(llms, encoding="utf-8")
full = [llms, f"\n---\n\nThe following is the Markdown of the main pages ({n_idx['board']} entries, {n_idx['owner']} owners, {n_idx['tag']} types and {n_idx['country']} countries).\n"]
for kind, path, md_text in sorted(MD_PAGES, key=lambda x: (order.get(x[0], 9), x[1])): full.append(f"\n---\n\n{md_text}")
(OUT/"llms-full.txt").write_text("".join(full), encoding="utf-8")
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nContent-Signal: search=yes, ai-input=yes\n\n# Index for language models: {BASE}/llms.txt\nSitemap: {BASE}/sitemap.xml\n")

sm = "".join(f"<url><loc>{e(BASE + p)}</loc><lastmod>{e(m)}</lastmod></url>" for p, m in sorted(pages))
(OUT/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
nf = layout(0, f"Page not found | {NAME}", "Page not found.", '<h1>Page not found</h1><p>Try the <a href="/">directory</a>.</p>', "/404.html").replace('href="assets/','href="/assets/').replace('href=""','href="/"')
(OUT/"404.html").write_text(nf, encoding="utf-8")
if (ROOT/"CNAME").exists(): shutil.copy(ROOT/"CNAME", OUT/"CNAME")
print(f"built {len(pages)} pages")
