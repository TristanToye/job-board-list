# Job board catalogue

A market-intelligence dataset of job boards, aggregators, ATS systems and distribution layers, organised by region, country and niche, with a focus on who offers APIs, partner programs and developer portals.

## Why

To understand where jobs originate and how they flow: employer, ATS, programmatic or multiposting layer, board or aggregator, candidate. The data shows who is open to integration and who is gated.

## Layout

- `data/job_boards.csv`: boards, aggregators, government portals, niche and regional boards, distribution platforms.
- `data/sources.csv`: one row per cited fact (board, field, URL, title, date read). Every checked fact on the site links back here.
- `data/research_queue.csv`: boards and verification tasks still to do, with the reason each is blocked or pending.
- `data/ats_systems.csv`: applicant tracking systems and whether they expose public job feeds or APIs.
- `scripts/validate.py`: checks the data and prints a coverage summary. Run `python3 scripts/validate.py`.

## Website

A static site is generated from the CSVs into `docs/` and served by GitHub Pages.

- Build: `python3 scripts/build_site.py` (standard library only).
- Source: `site_src/` (CSS and JS), settings in `site.json` (name, tagline, `base_url`).
- Output: a searchable directory, one page per board and ATS, region, country and API-status pages, `sitemap.xml`, `robots.txt`, structured data, and CSV and JSON downloads.
- Icons: `python3 scripts/fetch_logos.py` downloads each board's site icon into `site_src/logos/` and records results in `data/logos.json`. Icons are self-hosted. Boards with no usable icon get a letter tile.
- Publish: in the repo settings under Pages, choose branch `main` and folder `/docs`.
- Custom domain: set `base_url` in `site.json`, add a `CNAME` file at the repo root containing the domain, rebuild, and set the domain in Pages settings.

## Key fields

- `type`: board, aggregator, government, niche-board, social-network, programmatic-distribution, multiposting, feed-aggregator.
- `api_status`: `public-open` (no key), `public-key` (self-serve key), `on-request` (key or feed issued after a request form), `partner-only` (approval needed), `deprecated`, `none-known`, `unknown`.
- `primary_language` / `languages_supported`: ISO 639-1 codes. `languages_supported` is semicolon separated and includes the primary language. Blank means not yet recorded.
- `partner_program` / `partner_url`: whether an ATS or employer integration program exists.
- `ingest_methods`: how jobs get in (XML feed, API, apply integration, crawl, schema.org markup).
- `countries_served`: ISO 3166 codes (semicolon separated) of countries the board is known to serve besides its HQ country. Filled in as countries are researched.
- `confidence`: `seed-unverified` means no fact in the row has a citation. `listed-only` means the only citations are third-party listings or partner lists (fields `listed_by` and `relationship`), which show a board exists and nothing more. `partially-verified` means at least one fact is cited to the board's own pages or an official source. Only cited facts are checked.

## Status

Canada is the first country researched: facts for those boards cite the pages they were read from. Everything else is still seed data. Treat uncited API and partner fields as leads, not facts.

Some large sites (for example Indeed and ZipRecruiter) refuse automated access. Those stay unverified until checked another way. Where a site's terms forbid scraping, only its public pages are read.

## Next steps

1. Verify each row against official docs, and record the source URL and date.
2. Fill `unknown` fields, starting with the largest boards per country.
3. Expand coverage: more countries (long tail in Europe, APAC, Africa, LatAm), niche verticals (healthcare, trades, education, hospitality, gig), and talent marketplaces.
4. Add a `relationships.csv` mapping ATS to the boards and aggregators they integrate with.
5. Add a market-size and traffic field from a consistent third-party source.
