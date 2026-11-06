# Research loop

How the directory grows, country by country. The work queue is `data/countries.csv` (status: pending, discovered, verified, researched).

## One round for one country

1. **Discover.** An agent follows `research/briefs/discover.md` and writes `research/findings/DATE-CC-discover.json`.
2. **Ingest.** `python3 scripts/ingest.py research/findings/DATE-CC-discover.json` merges it.
3. **Pick boards to verify.** `python3 scripts/ingest.py --verify-input research/findings/DATE-CC-discover.json --top 8 > research/findings/DATE-CC-verify-input.json`
4. **Verify.** An agent follows `research/briefs/verify.md` for those boards and writes `research/findings/DATE-CC-verify.json`.
5. **Ingest, rebuild, commit.** `python3 scripts/ingest.py ...`, then `python3 scripts/fetch_logos.py`, `python3 scripts/validate.py`, `python3 scripts/build_site.py`, then commit the findings, data and site together.
6. **Mark.** `python3 scripts/ingest.py --mark CC discovered` (or `verified`).

Discovery and verification agents for many countries can run in parallel on a lower cost model. Ingest runs once per batch.

## Other sources

- **Wikidata** (CC0): `python3 scripts/fetch_wikidata.py` pulls employment websites with owner, founding year and country, then `python3 scripts/ingest.py` merges them. Its statements are machine generated, so they need no quote check and are labelled as a secondary source.
- **Wikipedia** article pages: follow `research/briefs/wikipedia.md`. Run `python3 scripts/check_quotes.py` on the output (it fetches Wikipedia one page at a time) before ingest.

## Other classes of entry

Entries are not only job boards. Use `research/briefs/discover-class.md` with a class (labour market information, outplacement, career services, staffing, executive search, freelance platforms, HR technology) and set `type` to match. Run `python3 scripts/derive_tags.py` after ingest so each entry gets its tags.

## Owner profiles

`research/briefs/owner-profile.md` collects a cited self-description and basic company facts. Run `check_quotes.py`, then `ingest_ownership.py`. A fact is kept only if its quote supports its value.

## Ownership

Follow `research/briefs/ownership.md` for an owner company, run `python3 scripts/check_quotes.py` on the output, then `python3 scripts/ingest_ownership.py`. A quote must be at least four words and state the relationship. If the source only lists a company on a group page, the relationship is recorded as a group company, not a subsidiary.

## What ingest enforces

- A value is accepted only with a source. Strong claims (HQ, ownership, languages, pricing, API, partner program, ingest methods) need a source on the board's own domain with a quote of 30 words or fewer.
- Listings on third party pages count as `listed_by` and only show that a board exists.
- Verified fields are never overwritten. Disagreements go to `data/conflicts.csv` for review.
- Rejected items are printed and boards or sites that could not be read go to `data/research_queue.csv`.
- Text containing instructions to a model, brand names of AI tools, or em dashes is dropped or cleaned.

## Indexing rule

Only boards with a cited source and at least three substantive facts get an indexable page. The rest are marked noindex and left out of the sitemap, so thin pages do not dilute the site. List pages with fewer than three boards follow the same rule.

## Review

After each batch, spot check a sample of new quotes against the live pages, read `data/conflicts.csv`, and read the ingest summary. Raw findings stay in `research/findings/` as an audit trail.
