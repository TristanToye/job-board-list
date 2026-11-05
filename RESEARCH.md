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

## What ingest enforces

- A value is accepted only with a source. Strong claims (HQ, ownership, languages, pricing, API, partner program, ingest methods) need a source on the board's own domain with a quote of 30 words or fewer.
- Listings on third party pages count as `listed_by` and only show that a board exists.
- Verified fields are never overwritten. Disagreements go to `data/conflicts.csv` for review.
- Rejected items are printed and boards or sites that could not be read go to `data/research_queue.csv`.
- Text containing instructions to a model, brand names of AI tools, or em dashes is dropped or cleaned.

## Review

After each batch, spot check a sample of new quotes against the live pages, read `data/conflicts.csv`, and read the ingest summary. Raw findings stay in `research/findings/` as an audit trail.
