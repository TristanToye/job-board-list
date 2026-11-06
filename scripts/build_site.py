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
LANGS = {"en":"English","es":"Spanish","fr":"French","de":"German","it":"Italian","pt":"Portuguese","nl":"Dutch","pl":"Polish",
 "sv":"Swedish","da":"Danish","no":"Norwegian","fi":"Finnish","ja":"Japanese","ko":"Korean","zh":"Chinese","ar":"Arabic","tr":"Turkish",
 "ru":"Russian","uk":"Ukrainian","ca":"Catalan","cs":"Czech","sk":"Slovak","id":"Indonesian","ms":"Malay","th":"Thai","hi":"Hindi","kk":"Kazakh","ro":"Romanian"}
def lang(c): return LANGS.get(c, c)
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

def tdesc(b): return {"government":"government job site"}.get(b["type"], b["type"])
def article(w): return "an" if w[:1].lower() in "aeiou" else "a"
def e(s): return html.escape(str(s), quote=True)
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def load(n):
    with open(ROOT/"data"/n, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
def split(s): return [x.strip() for x in (s or "").split(";") if x.strip()]
def country(c): return COUNTRIES.get(c, c)

boards, ats = load("job_boards.csv"), load("ats_systems.csv")
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

def layout(path_depth, title, desc, body, canonical, jsonld=None, extra_head="", noindex=False):
    r = "../" * path_depth
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    nav = (f'<a href="{r}">Directory</a><a href="{r}tags/">Types</a><a href="{r}rankings/">Rankings</a><a href="{r}owners/">Owners</a><a href="{r}regions/">Regions</a><a href="{r}countries/">Countries</a>'
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
<link rel="alternate" type="application/atom+xml" title="{e(NAME)} research log" href="{r}feed.xml">{'<meta name="robots" content="noindex,follow">' if noindex else ""}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%232563eb'/%3E%3Cpath d='M8 22V10h4a4 4 0 0 1 0 8H8' fill='none' stroke='white' stroke-width='3'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{r}assets/style.css">{extra_head}{ld}</head>
<body><header class="top"><div class="wrap bar"><a class="brand" href="{r}">{e(NAME)}</a><nav>{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer class="wrap foot"><p>{e(NAME)} is an open dataset. Download: <a href="{r}downloads/job_boards.csv">boards CSV</a>,
<a href="{r}downloads/job_boards.json">boards JSON</a>, <a href="{r}downloads/ats_systems.csv">ATS CSV</a>, <a href="{r}data/boards.json">JSON data API</a>, <a href="{r}changelog/">changelog</a> and <a href="{r}feed.xml">feed</a>.
Data is a work in progress and may be wrong: see <a href="{r}about/">methodology</a>. Web rank data: <a href="https://majestic.com/reports/majestic-million" rel="noopener nofollow">Majestic Million</a>, CC BY 3.0. Last built {TODAY}.</p></footer>
</body></html>"""

def write(rel, content, lastmod=True, indexed=True):
    p = OUT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
    if lastmod and indexed and rel.endswith("index.html"):
        pages.append("/" + rel[:-len("index.html")])

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
            f'<td>{prom_cell(b)}</td><td>{e(b["type"])}</td><td>{e(country(b["hq_country"]) or "Not recorded")}</td><td>{e(lang(b["primary_language"]) or "Not recorded")}</td>'
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
<p class="lede">{e(CFG["tagline"])}. Search {len(boards)} job boards, aggregators, staffing firms and other HR services, plus {len(ats)} applicant tracking systems, across regions and countries. Filter by type, focus and openness. Find who has an API, a partner program or a developer portal.</p>
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
  f"Open directory of {len(boards)} job boards, aggregators, staffing firms and HR services plus {len(ats)} ATS systems, by region and country, with API access, partner programs and owners.",
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
    sources_html = ""
    if srcs:
        sources_html = ("<h2>Sources</h2><ol class=\"sources\">" + "".join(
            f'<li><span class="chip">{e(FIELD_LABEL.get(x["field"], x["field"]))}</span> <a href="{e(x["url"])}" rel="noopener nofollow" target="_blank">{e(x["title"])}</a>{" (secondary source)" if "wikipedia.org" in x["url"] or "wikidata.org" in x["url"] else ""} <span class="muted small">checked {e(x["accessed"])}</span>{('<div class="quote">' + e(x.get("quote","")) + '</div>') if x.get("quote") else ""}</li>' for x in srcs) + "</ol>")
    checked_on = max((x["accessed"] for x in srcs), default="")
    body = f"""<nav class="crumbs"><a href="{r}">Directory</a> / <a href="{r}regions/{slug(b["region"])}/">{e(b["region"])}</a> / {e(b["name"])}</nav>
<div class="titlerow">{icon(b, r, 64)}<h1>{e(b["name"])}</h1></div><p class="lede">{e(b["name"])} is {article(tdesc(b))} {e(tdesc(b))}{" based in " + e(country(b["hq_country"])) if b["hq_country"] else ""}{f", focused on {e(b['niche'])}" if b["niche"] and b["niche"] != "general" else ", serving all kinds of roles" if b["niche"] == "general" else ""}. It {api_text}. {e(partner)}</p>
<p>{api_badge(b["api_status"])} {conf_badge(b["confidence"])}</p>
<dl class="facts">{fact("Website", link(b["url"]))}{fact("Tags", tag_html) if tag_html else ""}{fact("Last checked", e(checked_on)) if checked_on else ""}{fact("Type", e(b["type"]))}{fact("Founded", e(b["founded"])) if b["founded"] else ""}{fact("Headquarters", f'<a href="{r}countries/{slug(country(b["hq_country"]))}/">{e(country(b["hq_country"]))}</a>' if b["hq_country"] else '<span class="muted">Not recorded</span>')}
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
{sources_html}
<p class="notice">Only facts listed under Sources have been checked, and a listing by another directory only shows a board exists. Everything else on this page is unverified. <a href="{r}about/">How we research</a>.</p>
{"<h2>Other boards in " + e(b["region"]) + "</h2><ul>" + "".join(f'<li><a href="{r}boards/{x["id"]}/">{e(x["name"])}</a></li>' for x in siblings) + "</ul>" if siblings else ""}"""
    ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Directory","item":BASE+"/"},
      {"@type":"ListItem","position":2,"name":b["region"],"item":f'{BASE}/regions/{slug(b["region"])}/'},
      {"@type":"ListItem","position":3,"name":b["name"]}]}
    org = {"@context":"https://schema.org","@type":"Organization","name":b["name"],"url":b["url"]}
    if logo_info(b): org["logo"] = f'{BASE}/assets/logos/{logo_info(b)["file"]}'
    ld = [ld, org]
    write(f'boards/{b["id"]}/index.html', layout(2, f'{b["name"]}: API, partner program and integration details | {NAME}',
      f'{b["name"]} ({b["type"]}{", " + country(b["hq_country"]) if b["hq_country"] else ""}{", " + lang(b["primary_language"]) if b["primary_language"] else ""}): API status, partner program, developer docs and how jobs are ingested.', body, f'/boards/{b["id"]}/', ld, noindex=not indexable(b)), indexed=indexable(b))

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
    write(f"countries/{slug(k)}/index.html", layout(2, f"Job boards in {k}: APIs, partner programs and sources | {NAME}",
        f"{len(v)} job boards and aggregators based in or serving {k}, with API access, partner programs and cited sources.", body, f"/countries/{slug(k)}/", itemlist(v, 2), noindex=len(v) < 3), indexed=len(v) >= 3)
API_TITLE = {"on-request":"Job board APIs and feeds available on request","public-open":"Job boards with an open API","public-key":"Job board APIs with self-serve keys",
  "partner-only":"Partner-only job board APIs and feeds","deprecated":"Job boards with deprecated APIs","none-known":"Job boards with no known API","unknown":"Job boards with unresearched API status"}
group_pages("api", "API status", lambda b: b["api_status"], lambda k: API_LABEL[k],
  lambda k, n: f"{API_BLURB[k]} {n} listed.", lambda k: API_TITLE[k], lambda k: API_TITLE[k])

# ---------- languages ----------
by_lang = collections.defaultdict(list)
for b in boards:
    for c in langs_of(b): by_lang[c].append(b)
write("languages/index.html", layout(1, f"Job boards by language | {NAME}", "Browse job boards and aggregators by primary language and supported languages.",
    '<h1>Job boards by language</h1><p class="lede">Boards are listed under their primary language and every other language they support.</p><ul class="biglist">'
    + "".join(f'<li><a href="{slug(lang(c))}/">{e(lang(c))}</a> <span class="muted">({len(v)})</span></li>' for c, v in sorted(by_lang.items(), key=lambda kv: lang(kv[0]))) + "</ul>", "/languages/"))
for c, v in by_lang.items():
    prim = sum(1 for b in v if b["primary_language"] == c)
    body = (f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">By language</a> / {e(lang(c))}</nav><h1>{e(lang(c))} job boards</h1>'
            f'<p class="lede">{len(v)} job boards and aggregators that support {e(lang(c))}, of which {prim} use it as their primary language.</p>'
            + table(sorted(v, key=lambda b: b["name"].lower()), "../../"))
    write(f"languages/{slug(lang(c))}/index.html", layout(2, f"{lang(c)} job boards and aggregators | {NAME}",
        f"{len(v)} job boards and aggregators supporting {lang(c)}, with API access and partner program details.", body, f"/languages/{slug(lang(c))}/", itemlist(v, 2), noindex=len(v) < 3), indexed=len(v) >= 3)

# ---------- ATS ----------
def ats_row(a, r): return (f'<tr><td><a href="{r}ats/{a["id"]}/"><strong>{e(a["name"])}</strong></a><div class="muted small">{e(a["vendor"])}</div></td>'
    f'<td>{e(a["segment"])}</td><td>{e(a["hq_country"])}</td><td>{e(a["public_job_feed"])}</td><td>{e(a["marketplace_partner_program"])}</td></tr>')
write("ats/index.html", layout(1, f"ATS systems with public job feeds and APIs | {NAME}",
  f"{len(ats)} applicant tracking systems compared by public job feed, API access and partner marketplace.",
  f'<h1>Applicant tracking systems and their job APIs</h1><p class="lede">Which ATS platforms expose public job feeds, which require tokens, and which run partner marketplaces. Useful for building integrations or aggregating postings at source.</p><div class="tablewrap"><table><thead><tr><th>ATS</th><th>Segment</th><th>HQ</th><th>Public job feed</th><th>Partner program</th></tr></thead><tbody>'
  + "".join(ats_row(a, "../") for a in sorted(ats, key=lambda a: a["name"].lower())) + "</tbody></table></div>", "/ats/"))
for a in ats:
    body = f"""<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">ATS systems</a> / {e(a["name"])}</nav><h1>{e(a["name"])}: job feed and API access</h1>
<p class="lede">{e(a["name"])} is an applicant tracking system from {e(a["vendor"])} aimed at {e(a["segment"])} employers. Public job feed: {e(a["public_job_feed"])}.</p><p>{conf_badge(a["confidence"])}</p>
<dl class="facts">{fact("Vendor", e(a["vendor"]))}{fact("Segment", e(a["segment"]))}{fact("HQ", e(a["hq_country"]))}{fact("Public job feed", e(a["public_job_feed"]))}
{fact("Documentation", link(a["job_feed_docs_url"]))}{fact("Auth for reading jobs", e(a["auth_required"]))}{fact("Write API", e(a["write_api"]))}{fact("Partner marketplace", e(a["marketplace_partner_program"]))}</dl>
{f'<h2>Notes</h2><p>{e(a["notes"])}</p>' if a["notes"] else ""}"""
    write(f'ats/{a["id"]}/index.html', layout(2, f'{a["name"]} API and public job feed | {NAME}', f'{a["name"]} ({a["vendor"]}): public job feed, API authentication, write access and partner marketplace.', body, f'/ats/{a["id"]}/'))

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
<h2>Privacy</h2><p>This site uses Google Analytics to measure traffic. It may set cookies in your browser.</p>\n<h2>Corrections and downloads</h2><p>Spotted something wrong or missing? Open an issue or pull request on the project repository. The full dataset is available as <a href="../downloads/job_boards.csv">CSV</a>, <a href="../downloads/job_boards.json">JSON</a> the <a href="../downloads/sources.csv">sources table</a>, <a href="../downloads/rank.csv">rank data</a> and <a href="../downloads/scale.csv">scale figures</a>.</p></div>"""
write("about/index.html", layout(1, f"Methodology and data definitions | {NAME}", "How the job board directory is compiled, what each API status means, and how to report corrections.", about, "/about/"))

# ---------- assets, downloads, robots, sitemap, 404 ----------
(OUT / "assets").mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT/"site_src"/"style.css", OUT/"assets"/"style.css"); shutil.copy(ROOT/"site_src"/"app.js", OUT/"assets"/"app.js")
if (ROOT/"site_src"/"logos").exists(): shutil.copytree(ROOT/"site_src"/"logos", OUT/"assets"/"logos", dirs_exist_ok=True)
(OUT/"downloads").mkdir(exist_ok=True)
for n in ("job_boards.csv","ats_systems.csv","sources.csv","rank.csv","scale.csv","owners.csv","ownership.csv","owner_facts.csv","taxonomy.csv","tags.csv"): shutil.copy(ROOT/"data"/n, OUT/"downloads"/n)
(OUT/"downloads"/"job_boards.json").write_text(json.dumps(boards, indent=1, ensure_ascii=False), encoding="utf-8")
(OUT/".nojekyll").write_text("")
# ---------- tags ----------
by_id = {b["id"]: b for b in boards}; ats_by = {a["id"]: a for a in ats}
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
    mb = [by_id[i] for i in members[t]["board"] if i in by_id]; ma = [ats_by[i] for i in members[t]["ats"] if i in ats_by]
    if not mb and not ma: continue
    body = f'<nav class="crumbs"><a href="../../">Directory</a> / <a href="../">Types</a> / {e(r["label"])}</nav><h1>{e(r["label"])}</h1><p class="lede">{e(r["definition"])} {len(mb) + len(ma)} entries are tagged this way.</p>'
    if mb: body += table(mb, "../../")
    if ma: body += '<h2>Applicant tracking systems</h2><div class="tablewrap"><table><thead><tr><th>ATS</th><th>Segment</th><th>HQ</th><th>Public job feed</th><th>Partner program</th></tr></thead><tbody>' + "".join(ats_row(a, "../../") for a in ma) + "</tbody></table></div>"
    n = len(mb) + len(ma); idx = n >= 3
    write(f"tags/{t}/index.html", layout(2, f"{r['label']}: {r['facet']} tag | {NAME}" if r["facet"] != "function" else f"{r['label']}: directory and examples | {NAME}", f"{r['definition']} {n} entries in the directory.", body, f"/tags/{t}/", itemlist(mb, 2) if mb else None, noindex=not idx), indexed=idx)
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
    write(f"owners/{oid}/index.html", layout(2, f"{o['name']}: job boards and other HR businesses owned | {NAME}",
        f"What {o['name']} owns in the HR space: {nb} job boards in this directory plus staffing, HR technology and other holdings, with cited sources.", body, f"/owners/{oid}/", ld, noindex=not idx), indexed=idx)
    owner_rows.append((oid, o, len(cur), nb))
if owner_rows:
    li = "".join(f'<li><a href="{e(oid)}/">{e(o["name"])}</a> <span class="muted">({n} HR holdings, {nb} job boards here)</span></li>' for oid, o, n, nb in sorted(owner_rows, key=lambda x: -x[2]))
    write("owners/index.html", layout(1, f"Who owns the job boards: owners and HR holdings | {NAME}", "Parent companies behind the major job boards and what else they own in the HR space, with cited sources.",
        f'<h1>Who owns the job boards</h1><p class="lede">The companies behind the major job boards, and what else they own in the HR space: staffing firms, recruiting technology and services. Every holding is cited.</p><ul class="biglist">{li}</ul>', "/owners/"))
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
    d["owners"] = [{"id": h["owner_id"], "name": OWNERS[h["owner_id"]]["name"], "relation": h["relation"], "stake": h["stake"], "since": h["since"], "source": h["source_url"], "quote": h["quote"]} for h in HOLD_BY_BOARD.get(b["id"], []) if h["owner_id"] in OWNERS]
    d["scale"] = [{k: x[k] for k in ("metric", "value", "unit", "as_of", "url", "quote", "quote_check")} for x in SCALE.get(b["id"], [])]
    d["sources"] = [{k: x.get(k, "") for k in ("field", "url", "title", "accessed", "quote", "quote_check")} for x in SOURCES.get(b["id"], [])]
    return d
allj = [board_json(b) for b in boards]
(OUT/"data"/"boards.json").write_text(json.dumps({"generated": TODAY, "count": len(allj), "boards": allj}, indent=1, ensure_ascii=False), encoding="utf-8")
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
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
sm = "".join(f"<url><loc>{e(BASE + p)}</loc><lastmod>{TODAY}</lastmod></url>" for p in sorted(pages))
(OUT/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
nf = layout(0, f"Page not found | {NAME}", "Page not found.", '<h1>Page not found</h1><p>Try the <a href="/">directory</a>.</p>', "/404.html").replace('href="assets/','href="/assets/').replace('href=""','href="/"')
(OUT/"404.html").write_text(nf, encoding="utf-8")
if (ROOT/"CNAME").exists(): shutil.copy(ROOT/"CNAME", OUT/"CNAME")
print(f"built {len(pages)} pages")
