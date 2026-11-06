#!/usr/bin/env python3
"""Mechanical steps of the refinement loop. The scouting and researching are done by agents; this script plans, merges and logs.
  python3 scripts/refine_round.py plan N      pick entries and write scout inputs  (research/findings/STAMP-loopN-review-K-input.json)
  python3 scripts/refine_round.py orders N    merge scout outputs into worker inputs (STAMP-loopN-work-K-input.json) and log flags
  python3 scripts/refine_round.py apply N     quote check and ingest worker outputs, retag, validate, log the round
  python3 scripts/refine_round.py report      print the loop log"""
import csv, collections, datetime, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent; DATA = ROOT / "data"; FIND = ROOT / "research" / "findings"
STAMP = datetime.date.today().isoformat(); SCOUTS, WORKERS, PER_SCOUT, PER_WORKER = 2, 4, 16, 8
FIELDS = ["hq_country", "founded", "parent", "languages", "business_model", "api_status", "partner_program", "ingest_methods"]
def load(n):
    p = DATA / n
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if p.exists() else []
def save(n, rows, cols):
    with open(DATA / n, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
def state():
    p = DATA / "loop_state.json"
    return json.load(open(p)) if p.exists() else {"rounds": {}}
def run(*a): return subprocess.run(["python3", "-I", *a], capture_output=True, text=True, cwd=ROOT)
def missing(b, owned):
    m = []
    if not b["hq_country"]: m.append("hq_country")
    if not b["founded"]: m.append("founded")
    if not b["parent"] and b["id"] not in owned: m.append("parent")
    if not b["primary_language"]: m.append("languages")
    if not b["business_model"]: m.append("business_model")
    if b["api_status"] == "unknown": m.append("api_status")
    if b["partner_program"] == "unknown": m.append("partner_program")
    if not b["ingest_methods"]: m.append("ingest_methods")
    return m
def snapshot():
    return {b["id"]: {k: (v if v not in ("unknown",) else "") for k, v in b.items()} for b in load("job_boards.csv")}

def plan(n):
    boards = load("job_boards.csv"); rank = {r["board_id"]: r for r in load("rank.csv")}; reviews = {r["board_id"]: r for r in load("reviews.csv")}
    owned = {h["board_id"] for h in load("ownership.csv") if h["board_id"]}; att = collections.defaultdict(list)
    for a in load("attempts.csv"): att[(a["board_id"], a["field"])].append(a)
    for rv_ in reviews.values():  # earlier reviews predate the attempts log: each field they could not find counts as one failed attempt
        for f_ in [x for x in rv_["fields_not_found"].split(";") if x]:
            if f_ == "languages": f_ = "languages"
            att[(rv_["board_id"], f_)].append({"field": f_, "outcome": "not-found", "pages": ""})
    tried, found = collections.Counter(), collections.Counter()
    for (bid, f), lst in att.items():
        for a in lst: tried[f] += 1; found[f] += a["outcome"] == "found"
    prior = {f: (found[f] + 1) / (tried[f] + 3) for f in FIELDS}
    last = set(state()["rounds"].get(str(n - 1), {}).get("entries", [])) | set(state()["rounds"].get(str(n - 2), {}).get("entries", []))  # scouted in either of the last two rounds
    def weight(i):
        r = rank.get(i)
        if not r or not r["global_rank"]: return 1
        g = int(r["global_rank"]); w = 5 if g <= 1000 else 4 if g <= 10000 else 3 if g <= 100000 else 2
        return w if r["scope"] == "domain" else 1.5
    cands = []
    for b in boards:
        if not b["url"]: continue
        rv = reviews.get(b["id"])
        if rv and rv["outcome"] in ("blocked", "closed"): continue
        if any(a["outcome"] == "blocked" for f in FIELDS for a in att[(b["id"], f)]): continue
        elig = [f for f in missing(b, owned) if sum(1 for a in att[(b["id"], f)] if a["outcome"] != "found") < 2 and not any(a["outcome"] == "found" for a in att[(b["id"], f)] if False)]
        if not elig: continue
        cands.append((weight(b["id"]) * sum(prior[f] * 0.25 ** sum(1 for a in att[(b["id"], f)] if a["outcome"] != "found") for f in elig), b, elig))
    cands.sort(key=lambda x: -x[0]); fresh = [c for c in cands if c[1]["id"] not in last]; picked = (fresh + [c for c in cands if c[1]["id"] in last])[:SCOUTS * PER_SCOUT]
    for k in range(SCOUTS):
        part = picked[k::SCOUTS]
        items = [{"id": b["id"], "name": b["name"], "url": b["url"], "type": b["type"], "parent": b["parent"], "missing": elig,
                  "recorded": {f: b[f] for f in ("hq_country", "founded", "parent", "primary_language", "languages_supported", "business_model", "api_status", "api_docs_url", "partner_program", "partner_url", "ingest_methods") if b[f] and b[f] != "unknown"},
                  "review_history": ({k2: reviews[b["id"]][k2] for k2 in ("reviewed", "outcome", "fields_not_found", "note")} if b["id"] in reviews else None),
                  "attempts": [{"field": a["field"], "outcome": a["outcome"], "pages": a["pages"]} for f in FIELDS for a in att[(b["id"], f)]]} for _, b, elig in part]
        json.dump({"round": n, "entries": items}, open(FIND / f"{STAMP}-loop{n}-review-{k + 1}-input.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    s = state(); s["rounds"].setdefault(str(n), {})["entries"] = [b["id"] for _, b, _ in picked]; s["rounds"][str(n)]["planned"] = len(picked); json.dump(s, open(DATA / "loop_state.json", "w"), indent=1)
    print(f"round {n}: {len(cands)} candidates with an open field, {len(picked)} picked for scouting")
    print("  " + ", ".join(f"{b['name']} ({','.join(e[:3] for e in elig)})" for _, b, elig in picked[:10]) + " ...")

def orders(n):
    boards = {b["id"]: b for b in load("job_boards.csv")}; owned = {h["board_id"] for h in load("ownership.csv") if h["board_id"]}; work = []; flags = []; scouted = 0
    inputs = {}
    for k in range(1, SCOUTS + 1):
        p = FIND / f"{STAMP}-loop{n}-review-{k}-input.json"
        if p.exists():
            for it in json.load(open(p, encoding="utf-8"))["entries"]: inputs[it["id"]] = it
    for k in range(1, SCOUTS + 1):
        p = FIND / f"{STAMP}-loop{n}-review-{k}.json"
        if not p.exists(): continue
        for o in json.load(open(p, encoding="utf-8")).get("orders", []):
            scouted += 1; oid = o.get("id"); it = inputs.get(oid)
            if it is None or oid not in boards: continue
            for fl in o.get("flags", []): flags.append({"round": n, "board_id": oid, "flag": str(fl)[:200]})
            lk = o.get("likelihood", {}); fields = [f for f in it["missing"] if str(lk.get(f, "")).lower() in ("high", "medium")]
            if not fields: continue
            pages = [u for u in o.get("try_pages", []) if str(u).startswith("http")][:6]
            work.append({"id": oid, "name": it["name"], "url": it["url"], "fields": fields, "likelihood": {f: lk.get(f) for f in fields}, "try_pages": pages, "reason": str(o.get("reason", ""))[:200], "_score": sum(2 if str(lk.get(f)).lower() == "high" else 1 for f in fields)})
    work.sort(key=lambda w: -w["_score"]); work = work[:WORKERS * PER_WORKER]
    for k in range(WORKERS):
        part = [{kk: v for kk, v in w.items() if kk != "_score"} for w in work[k::WORKERS]]
        if part: json.dump({"round": n, "orders": part}, open(FIND / f"{STAMP}-loop{n}-work-{k + 1}-input.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    old = load("loop_flags.csv"); save("loop_flags.csv", old + flags, ["round", "board_id", "flag"])
    s = state(); s["rounds"].setdefault(str(n), {}).update(scouted=scouted, ordered=len(work), flags=len(flags)); json.dump(s, open(DATA / "loop_state.json", "w"), indent=1)
    print(f"round {n}: {scouted} scouted, {len(work)} work orders ({sum(len(w['fields']) for w in work)} fields), {len(flags)} flags raised")

def apply(n):
    before = snapshot(); outs = sorted(FIND.glob(f"{STAMP}-loop{n}-work-?.json")); stats = collections.Counter(); att0 = len(load("attempts.csv"))
    if not outs: print("no worker outputs found"); return
    for o in outs:
        run("scripts/check_quotes.py", str(o))
        r = run("scripts/ingest.py", str(o)); first = (r.stdout.splitlines() or [""])[0]; print(f"  {o.name}: {first}")
        for k, v in __import__("re").findall(r"'(\w+)': (\d+)", first): stats[k] += int(v)
    run("scripts/derive_tags.py"); v = run("scripts/validate.py"); ok = v.returncode == 0
    after = snapshot(); filled = collections.Counter(); changed = set()
    keys = {"hq_country": "hq_country", "founded": "founded", "parent": "parent", "languages": "primary_language", "business_model": "business_model", "api_status": "api_status", "partner_program": "partner_program", "ingest_methods": "ingest_methods", "url": "url"}
    for i, a in after.items():
        b = before.get(i)
        if b is None: continue
        for name, col in keys.items():
            if not b[col] and a[col]: filled[name] += 1; changed.add(i)
    att = load("attempts.csv")[att0:]; oc = collections.Counter(a["outcome"] for a in att); s = state()["rounds"].get(str(n), {})
    row = {"round": n, "planned": s.get("planned", ""), "scouted": s.get("scouted", ""), "ordered": s.get("ordered", ""), "entries_changed": len(changed), "facts_added": sum(filled.values()),
           "found": oc["found"], "not_found": oc["not-found"], "blocked": oc["blocked"], "rejected": stats["rejected"], "flags": s.get("flags", ""), "valid": ok}
    log = load("loop_log.csv"); log = [r for r in log if r["round"] != str(n)] + [{k: str(v) for k, v in row.items()}]
    save("loop_log.csv", log, list(row.keys()))
    print(f"round {n}: {row['facts_added']} facts filled across {row['entries_changed']} entries {dict(filled)}; attempts {dict(oc)}; validation {'OK' if ok else 'FAILED'}")
    if not ok: print(v.stdout[:600])

def finish(n):
    """Refresh icons, ranks and the site, run the repository checks, then commit and push the round."""
    steps = [("scripts/derive_tags.py",), ("scripts/fetch_logos.py",), ("scripts/validate.py",), ("scripts/build_site.py",)]
    for st in steps:
        r = run(*st)
        if r.returncode != 0: print("STOPPED:", st[0], r.stdout[-500:], r.stderr[-300:]); return
    bad = subprocess.run("grep -rl $(printf '\\342\\200\\224') docs site_src scripts README.md RESEARCH.md research data; grep -rli -e cla''ude -e anthro''pic docs site_src scripts README.md RESEARCH.md research data", shell=True, capture_output=True, text=True, cwd=ROOT)
    if bad.stdout.strip(): print("STOPPED: style or branding check found:", bad.stdout[:300]); return
    log = {r["round"]: r for r in load("loop_log.csv")}.get(str(n), {})
    msg = f"Refinement round {n}: {log.get('facts_added', '0')} facts across {log.get('entries_changed', '0')} entries"
    subprocess.run(["git", "add", "-A"], cwd=ROOT); c = subprocess.run(["git", "commit", "-q", "-m", msg], capture_output=True, text=True, cwd=ROOT)
    p_ = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, cwd=ROOT)
    print(msg, "|", "pushed" if p_.returncode == 0 else "PUSH FAILED " + p_.stderr[-200:])

def report():
    log = load("loop_log.csv"); print("round planned scouted ordered changed facts found notfound blocked rejected flags")
    for r in sorted(log, key=lambda r: int(r["round"])): print("  ".join(str(r[k]) for k in ("round", "planned", "scouted", "ordered", "entries_changed", "facts_added", "found", "not_found", "blocked", "rejected", "flags")))
    print("totals: facts", sum(int(r["facts_added"] or 0) for r in log), "| entries changed (sum)", sum(int(r["entries_changed"] or 0) for r in log))

if __name__ == "__main__":
    cmd = sys.argv[1]
    {"plan": lambda: plan(int(sys.argv[2])), "orders": lambda: orders(int(sys.argv[2])), "apply": lambda: apply(int(sys.argv[2])), "finish": lambda: finish(int(sys.argv[2])), "report": report}[cmd]()
