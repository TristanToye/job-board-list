# Job board catalogue

A market-intelligence dataset of job boards, aggregators, ATS systems and distribution layers, organised by region, country and niche, with a focus on who offers APIs, partner programs and developer portals.

## Why

To understand where jobs originate and how they flow: employer, ATS, programmatic or multiposting layer, board or aggregator, candidate. The data shows who is open to integration and who is gated.

## Layout

- `data/job_boards.csv`: boards, aggregators, government portals, niche and regional boards, distribution platforms.
- `data/ats_systems.csv`: applicant tracking systems and whether they expose public job feeds or APIs.
- `scripts/validate.py`: checks the data and prints a coverage summary. Run `python3 scripts/validate.py`.

## Website

A static site is generated from the CSVs into `docs/` and served by GitHub Pages.

- Build: `python3 scripts/build_site.py` (standard library only).
- Source: `site_src/` (CSS and JS), settings in `site.json` (name, tagline, `base_url`).
- Output: a searchable directory, one page per board and ATS, region, country and API-status pages, `sitemap.xml`, `robots.txt`, structured data, and CSV and JSON downloads.
- Publish: in the repo settings under Pages, choose branch `main` and folder `/docs`.
- Custom domain: set `base_url` in `site.json`, add a `CNAME` file at the repo root containing the domain, rebuild, and set the domain in Pages settings.

## Key fields

- `type`: board, aggregator, government, niche-board, social-network, programmatic-distribution, multiposting, feed-aggregator.
- `api_status`: `public-open` (no key), `public-key` (self-serve key), `partner-only` (approval needed), `deprecated`, `none-known`, `unknown`.
- `partner_program` / `partner_url`: whether an ATS or employer integration program exists.
- `ingest_methods`: how jobs get in (XML feed, API, apply integration, crawl, schema.org markup).
- `confidence`: `seed-unverified` means the row came from prior knowledge and has not been checked against a live source.

## Status

All 76 boards and 21 ATS rows are seeds and unverified. Treat API and partner fields as leads, not facts, until a row carries a source URL and a check date.

## Next steps

1. Verify each row against official docs, and record the source URL and date.
2. Fill `unknown` fields, starting with the largest boards per country.
3. Expand coverage: more countries (long tail in Europe, APAC, Africa, LatAm), niche verticals (healthcare, trades, education, hospitality, gig), and talent marketplaces.
4. Add a `relationships.csv` mapping ATS to the boards and aggregators they integrate with.
5. Add a market-size and traffic field from a consistent third-party source.
