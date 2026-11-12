# Job Board Atlas (jobboardlist.com): internal project audit as of 2026-11-12

Method note: all counts below were computed by me on 2026-11-12 with short Python scripts using the csv module over the files in /home/user/job-board-list/data/, and with find/grep over /home/user/job-board-list/docs/ (the built site). The "substantive facts" count reuses the exact `facts()` function from scripts/build_site.py (line 199 to 204): one point each for non-empty hq_country, founded, parent, business_model, api_docs_url, partner_url, ingest_methods, primary_language, plus one if api_status is not empty or "unknown", plus one if partner_program is "yes" or "n/a" (maximum 10). The live site was checked with curl on 2026-11-12. Search Console figures come from the owner's screenshots (2026-11-11) as given in the assignment; I did not access GSC myself. Sources cited as repo paths are local files; live checks cite https://jobboardlist.com URLs.

## 1. What is in data/job_boards.csv (types, regions, countries, confidence, fact depth)

### Takeaway
607 entries, but depth is very uneven: 192 entries (32%) have zero substantive facts and only 232 (38%) have 3 or more. Job boards (board + niche-board = 381 entries) dominate; the non-board ecosystem classes the project wants to cover (outplacement 9, career-services 9, staffing 27, hr-tech 14, multiposting 13, programmatic distribution 8, lmi 12, recruiting-services 10) total 102 entries and most are thin, with multiposting the weakest (11 of 13 have zero facts).

### Cited Findings
- Entry count: 607 data rows (608 lines including header). Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- By type: board 250, niche-board 131, government 54, staffing 27, aggregator 23, ats 21, hr-tech 14, multiposting 13, lmi 12, recruiting-services 10, freelance-platform 10, outplacement 9, career-services 9, programmatic-distribution 8, social-network+board 4, feed-aggregator 2, board+employer-brand 2, and 8 singleton hybrid types (aggregator+board, search-aggregator, board+aggregator, board+reviews, classifieds+board, board+chat, community, directory). 25 distinct type strings in total. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- By region: Europe 197, Global 159, North America 72, Latin America 33, SEA 30, Middle East 30, East Asia 29, Africa 24, APAC 19, South Asia 11, Eastern Europe/CIS 3. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- By hq_country: blank for 413 of 607 (68%). Filled values: US 44, CA 24, UK 11, DE 11, FR 7, JP 7, NL 7, then a long tail of 1 to 5 each. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- By countries_served (semicolon list, 485 entries filled): 68 distinct codes. ZZ (global/unspecified) 91, CA 48, US 30, IT 18, DE 17, AE 16, FR 15, BE 15, NL 15, DK 15, UK 14, BR 14, PL 13, ES 12, ZA 12, CZ 12, AU 11, AT 11, CH 11, IN 10. Canada is over-represented relative to the US because Canada was the first fully researched country (data/countries.csv shows CA as the only "researched" country). Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [data/countries.csv](/home/user/job-board-list/data/countries.csv)
- Country research pipeline status (data/countries.csv, 55 rows): discovered 20, pending 18, reference-only 10, verified 6, researched 1. Source: [data/countries.csv](/home/user/job-board-list/data/countries.csv)
- Confidence: partially-verified 482, listed-only 45, secondary-sourced 43, seed-unverified 37. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- Substantive facts distribution (facts() from build_site.py): 0 facts 192; 1 fact 107; 2 facts 76; 3+ facts 232 (3: 86, 4: 44, 5: 26, 6: 24, 7: 28, 8: 11, 9: 7, 10: 6). Source: computed from [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv) using [scripts/build_site.py](/home/user/job-board-list/scripts/build_site.py)
- Field fill rates out of 607: url 592, niche 500, countries_served 485, notes 331, languages_supported 249, primary_language 241, business_model 210, hq_country 194, parent 171, ingest_methods 138, markets 129, founded 115, api_docs_url 61, partner_url 51, segment 20. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- API status: unknown 511 (84%), partner-only 29, public-key 28, none-known 14, on-request 13, public-open 12 (96 entries with a known status). Partner program: unknown 510, yes 85, n/a 12. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- Per type (n / indexable / mean facts / zero-fact entries / known API status):
  - board 250 / 73 / 2.01 / 84 / 25
  - niche-board 131 / 33 / 1.76 / 55 / 15
  - government 54 / 20 / 2.65 / 16 / 8
  - staffing 27 / 5 / 1.37 / 3 / 0 (10 of 27 are listed-only)
  - aggregator 23 / 7 / 2.61 / 9 / 5
  - ats 21 / 18 / 5.71 / 1 / 19 (the deepest class)
  - hr-tech 14 / 9 / 3.71 / 0 / 3
  - multiposting 13 / 1 / 0.92 / 11 / 1
  - lmi 12 / 6 / 2.08 / 2 / 3
  - recruiting-services 10 / 0 / 1.2 / 1 / 0
  - freelance-platform 10 / 7 / 3.4 / 0 / 1
  - outplacement 9 / 3 / 2.22 / 0 / 0
  - career-services 9 / 2 / 1.78 / 2 / 1
  - programmatic-distribution 8 / 0 / 2.25 / 5 / 3
  Source: computed from [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- Distribution layer detail (multiposting + programmatic-distribution + feed-aggregator = 23 entries): only 6 have any facts (jobg8 6, appcast 6, joveo 6, broadbean 7, recruitics 6, erecruiter 5). 17 have zero facts, including VONQ, Talroo, JobTarget, idibu, PandoLogic, Radancy, DirectEmployers Association, Jobiqo, Circa, Join, Vacancy Poster, Postings.com, HireDiverse, Career Poster, JobDigger, HR Unlimited, Teamio. LogicMelon and Bullhorn are not entries at all (they appear only as relationship names). Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [data/relationships.csv](/home/user/job-board-list/data/relationships.csv)
- Outplacement entries (9): LHH (1 fact), Randstad RiseSmart 3, Intoo 2, Careerminds 2, Right Management 2, Challenger Gray & Christmas 2, Impact Group 2, VelvetJobs 3, Thrive Career Wellness 3. Staffing giants are thin: ManpowerGroup 1, Robert Half 0, Kelly 1, Hays 1, Kforce 0, Allegis 1, Adcorp 0. Executive search (recruiting-services): Korn Ferry 0, Spencer Stuart 1, Egon Zehnder 1. LMI: Lightcast 1, Revelio Labs 0, Burning Glass Institute 0. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)

### Inferences
- The fact schema is built for job boards and ATS (API status, partner program, ingest methods). For outplacement, staffing, career-services and LMI most of those fields are not applicable, so these classes structurally score low and fall below the indexing threshold even when well researched. A class-specific fact set (for example services offered, client segment, countries of operation, data products for LMI) would be needed.
- The distribution/multiposting layer is the weakest class in absolute terms yet is directly what searchers ask about (Lever multiposter, job feed management UK, ATS job board integration). This is the single most valuable thin class to deepen.
- hq_country blank for 68% of entries limits country pages to "serving" lists rather than "based in" lists and weakens Organization structured data.

### Gaps
- I did not assess the accuracy of individual facts against live sources; only quote_check values in the CSVs (see section 3).
- The README mentions data/ats_systems.csv but no such file exists; ATS are now ordinary rows with type ats. README is slightly stale on this point.

## 2. Pages built, sitemap, noindex and why

### Takeaway
docs/ contains 1,014 index.html pages but only 361 URLs are in the sitemap; 653 pages carry a noindex tag (414 of 607 board pages, 93 of 112 owner pages, 83 language pages including 55 redirect stubs, 30 country pages, 21 ATS redirect stubs, 12 tag pages). Board pages are noindexed by a rule requiring confidence partially-verified or secondary-sourced AND at least 3 substantive facts; only 193 boards pass, which closely matches the 204 pages GSC reports as indexed.

### Cited Findings
- Rule: `indexable(b)` returns true only if `b["confidence"] in ("partially-verified", "secondary-sourced") and facts(b) >= 3`. List pages (countries, languages, regions, tags) use `noindex=len(v) < 3`. Owner pages are indexable if they have 3+ current holdings or any owner_facts. The ecosystem page needs 10+ relationships, /closed/ needs 3+ lifecycle events. Source: [scripts/build_site.py lines 199 to 204, 410, 432, 460, 551, 600 to 603, 659, 676](/home/user/job-board-list/scripts/build_site.py)
- Applied to the data: 193 boards indexable; 414 noindex, of which 82 fail on confidence (listed-only or seed-unverified) and 332 have acceptable confidence but fewer than 3 facts. Source: computed from [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- Notable consequence: several well-known entries with 3+ facts are noindexed purely because confidence is seed-unverified: Broadbean (7 facts), Pracuj (7), Taleo (3), SuccessFactors (5), GulfTalent (3). Pracuj is the leading Polish board while "polish job boards" was the second highest impression query. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- Built pages by section (index.html files / with noindex / with Markdown twin): boards 607 / 414 / 193; owners 113 / 93 / 19; languages 111 / 83 / 0; countries 77 / 30 / 46; tags 59 / 12 / 46; ats 22 / 21 / 0; regions 12 / 0 / 0; api 7 / 0 / 0; plus about, changelog, rankings, ecosystem, closed (1 each). Total 1,014 HTML pages, 653 noindex, 306 index.md twins. Source: find/grep over [docs/](/home/user/job-board-list/docs/)
- 76 pages are meta-refresh redirect stubs (21 under /ats/, 55 under /languages/ for language-code aliases); each is a 200 response with `<meta name="robots" content="noindex">`, a canonical and `http-equiv="refresh"`. Source: [docs/ats/lever/index.html](/home/user/job-board-list/docs/ats/lever/index.html); live check [https://jobboardlist.com/ats/lever/](https://jobboardlist.com/ats/lever/) returned HTTP 200, 315 bytes
- Sitemap: 361 URLs: boards 193, tags 47, countries 47, languages 28, owners 20, regions 12, api 7, and 1 each for home, rankings, ecosystem, closed, changelog, ats, about. Live sitemap also has 361 locs. Source: [docs/sitemap.xml](/home/user/job-board-list/docs/sitemap.xml); [https://jobboardlist.com/sitemap.xml](https://jobboardlist.com/sitemap.xml)
- Country pages include unmapped code slugs (bg, bh, bo, cr, ec, ee, jo, kw, lb, om, pk, qa, si, sk, uy, zz) alongside full-name slugs, plus a "global-no-single-hq" page. Source: `ls docs/countries/` in [docs/countries](/home/user/job-board-list/docs/countries/)
- Tag pages noindexed (fewer than 3 entries): agriculture-food, community, directory, employer-reviews, engineering, environment, finance, hospitality-tourism, indigenous, nonprofit-operated, sport, teaching-esl. Outplacement, staffing, career-services, lmi, hr-tech, job-distribution and ats-integration tag pages are indexable. Source: grep over [docs/tags/](/home/user/job-board-list/docs/tags/)
- GSC (owner screenshots): 204 pages indexed; 77 pages with impressions. Source: assignment context (owner's GSC screenshots, 2026-11-11)

### Inferences
- Indexation is close to the sitemap ceiling: 204 indexed vs 361 submitted after about one week. The binding constraint for more indexed pages is the 3-fact rule, not crawl budget.
- The rule is sensible for quality but blunt: 332 entries need only 1 to 3 more facts to become indexable, and the confidence gate hides valuable but unverified pages (Broadbean, Pracuj) that match real queries. Upgrading these specific entries is a cheap win.
- /ats/lever/ is a soft redirect (200 + meta refresh). GitHub Pages cannot issue 301s, so Google treats these as duplicate pages; that it shows 15 impressions for /ats/lever/ suggests Google still indexes the stub URL. Removing internal links to /ats/ URLs and relying on canonicals is the available fix.
- Code-named country slugs (bg, zz, etc.) look like missing entries in data/countries.csv name mapping, producing low-quality pages titled with ISO codes.

### Gaps
- I could not see which specific 204 URLs Google has indexed (GSC page-level indexing export not available), so I cannot say whether any noindex pages were indexed before the rule or whether the 11-page excess over 193 boards consists of tags/countries.

## 3. Citation and evidence files: coverage

### Takeaway
Evidence is strong in volume (1,468 cited source rows, 89% with a quote, 83% on the entry's own domain) but narrow in what it covers: API details exist for only 16 entries, relationships form a graph of 202 edges dominated by a handful of ATS and multiposters, ownership covers 21 owner companies (of 121 distinct parent strings), lifecycle has 21 events, and scale figures only 8.

### Cited Findings
- sources.csv: 1,468 rows covering 570 of 607 entries (37 entries have no source row). Fields: existence 649, languages 211, business_model 160, parent 128, ingest_methods 102, api_status 60, listed_by 49, partner_program 47, owner_listing 39, relationship 15, note 6, terms 2. quote_check: ok 1,248, structured 87 (Wikidata), unreachable 35, blank 98. 1,371 rows have a quote. By my host match, 1,219 rows (83%) are on the entry's own domain or listed extra domains. Top hosts: wikidata.org 87, en.wikipedia.org 65, jobjunction.ca 26, jobbank.gc.ca 20. Source: [data/sources.csv](/home/user/job-board-list/data/sources.csv)
- Note: 649 of 1,468 source rows (44%) are "existence" citations, which prove a site exists but add no facts. Source: [data/sources.csv](/home/user/job-board-list/data/sources.csv)
- reviews.csv: 383 rows, one per entry (383 distinct). Outcomes: partially-verified 242, blocked 55, not-stated 53, verified 20, unreachable 13. Method: mixed 160, browser 112, fetch 111. So 224 entries have never had a review row. Source: [data/reviews.csv](/home/user/job-board-list/data/reviews.csv)
- api_details.csv: 76 rows for 16 entries (adzuna, ashby, bamboohr, breezy, greenhouse, icims, jobbank-ca, jobsuche-ba, lever, personio, recruitee, reed, rippling, smartrecruiters, teamtailor, workable). Fields: scope 16, access 15, auth 14, formats 11, limits 8, sandbox 6, approval 5, feed 1. All 76 quote_check ok. Not covered despite GSC queries: StepStone, Jobvite, Handshake, CV-Library, France Travail, Indeed, Freelancermap, Oracle, Taleo. Source: [data/api_details.csv](/home/user/job-board-list/data/api_details.csv)
- relationships.csv: 202 edges (integrates-with 131, sends-jobs-to 71), all quote_check ok. Source-side types: ats 104, multiposting 19, programmatic-distribution 15, board 10, other 4; 50 edges have an empty from_id (the source party is not an entry, for example Bullhorn x2, Betterteam x2, Conrep x2, JobAdder, Manatal, LogicMelon, Hireology, Cornerstone, Google, mostly ATS names listed on a board's integration page). 64 edges have an unresolved to_id (for example VONQ, Bullhorn, Avionte, SAP SuccessFactors, Cornerstone OnDemand, Darwinbox, Avature, TalentSoft, Ciphr, TribePad, NHS Jobs, myGwork). Only 52 distinct resolved entries appear as nodes. Out-degree is concentrated: Pinpoint 26, Workable 21, Lever 19, Broadbean 15, Joveo 11, JazzHR 9, Greenhouse 9, Teamtailor 8. Source: [data/relationships.csv](/home/user/job-board-list/data/relationships.csv)
- owners.csv: 21 owner companies (SEEK, Info Edge, The Stepstone Group, Randstad, Recruit, Adevinta, BOLD, DHI, Quess, Kanzhun, HeadHunter, Grupa Pracuj, SMG Swiss Marketplace, Navent, Ringier One Africa Media, Veritone, Advenn, Microsoft, Alphabet, Hubert Burda Media, Schibsted). Meanwhile job_boards.csv has 121 distinct parent strings, with duplicates by spelling (for example "Recruit Holdings Co., Ltd." 11, "Recruit Holdings" 6, "Recruit Co. Ltd." 1; "The Stepstone Group" 13, "StepStone Group" 2; "Info Edge" 2, "Info Edge (India) Ltd" 2). The site builds 112 owner pages, of which 19 are indexable. Source: [data/owners.csv](/home/user/job-board-list/data/owners.csv); [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [docs/llms.txt](https://jobboardlist.com/llms.txt) states "112 owner companies"
- ownership.csv: 72 holdings (brand 36, subsidiary 22, group-company 10, minority-stake 2, former 2), by category job-board 39, staffing 16, other-hr 7, hr-tech 6, hr-services 3, aggregator 1; 64 link to an entry. Concentrated: Recruit 19, Stepstone 17, Randstad 9, BOLD 9, SEEK 4, Info Edge 4. Source: [data/ownership.csv](/home/user/job-board-list/data/ownership.csv)
- owner_facts.csv: 75 facts for 19 owners (description 19, founded 11, hq_city 10, listing 10, employees 10, hq_country 8, revenue 7). Source: [data/owner_facts.csv](/home/user/job-board-list/data/owner_facts.csv)
- lifecycle.csv: 21 events (acquired 16, closed 2, merged 2, rebranded 1); entity types board 9, staffing 5, ats 3, aggregator 2, app 1, hr-tech 1. Source: [data/lifecycle.csv](/home/user/job-board-list/data/lifecycle.csv)
- rank.csv (Majestic Million, CC BY 3.0): 592 rows, all matched to entries; scope domain 501, section 79, mixed 12; 420 have a global rank (12 under 1,000; 67 under 10,000; 217 under 100,000). rank_scope.csv has 13 manual judgements. Source: [data/rank.csv](/home/user/job-board-list/data/rank.csv); [data/rank_scope.csv](/home/user/job-board-list/data/rank_scope.csv)
- scale.csv: 8 self-stated size figures (for example Job Bank Canada 55,000 jobs advertised per month, quote_check unreachable). Source: [data/scale.csv](/home/user/job-board-list/data/scale.csv)
- conflicts.csv: 17 open conflicts (business_model 13, parent 2, founded 1, api_status 1); 14 came from the 2026-11-09 thin1 batch. Source: [data/conflicts.csv](/home/user/job-board-list/data/conflicts.csv); [data/ingest_log.csv](/home/user/job-board-list/data/ingest_log.csv)
- research_queue.csv: 892 rows (verification 753, board 139). Reason text patterns (substring counts, overlapping): "403" 227, "partner" (partner names not yet entries) 119, "503"/redirect-class 50, "404" 45, "blocked" 27, "cloudflare" 25. Most frequent exact reasons: "HTTP 403" 117, "Named as a partner on an integrations page but not yet in the directory" 105, "HTTP 503" 48, "HTTP 403 on two attempts" 24, "DNS error" 19, "Safety check rate-limited; homepage not read" 12. Source: [data/research_queue.csv](/home/user/job-board-list/data/research_queue.csv)
- tags.csv/taxonomy.csv: 1,656 tag assignments over 58 distinct tags in use (60 defined); all but 1 are derived. Source: [data/tags.csv](/home/user/job-board-list/data/tags.csv); [data/taxonomy.csv](/home/user/job-board-list/data/taxonomy.csv)

### Inferences
- The 105 "named as a partner but not yet an entry" queue rows plus 64 unresolved relationship targets and 50 unresolved sources are a ready-made backlog for the competitor directory: they are exactly the ATS, multiposters and niche boards that other ecosystem players name as partners.
- Owner normalisation is a quick data-quality win: 121 parent strings collapse to far fewer real companies, and only 19 of 112 owner pages are indexable.
- API details for 16 entries is the most query-aligned evidence (GSC shows "recruitee api", "stepstone api", "greenhouse api", "handshake api", "cv library api", "freelancermap api") but covers fewer than a fifth of the 96 entries with a known API status.

### Gaps
- I did not re-verify any quotes; quote_check values are the pipeline's own.
- Relationship edges are only those stated on one party's own site, so the graph systematically misses connections stated only on the other party's site or by third parties; I cannot estimate how many real connections are missing.

## 4. What the site offers users today

### Takeaway
The site is a static, standard-library-built directory with an unusually rich machine-readable layer (per-entry JSON, CSV/JSON downloads of 13 tables, llms.txt, a 577 KB llms-full.txt, 306 Markdown twins, FAQPage/Organization/ItemList JSON-LD). The human-facing experience is a single 544 KB home page holding the whole table plus thin per-entry pages (median about 550 words for indexable boards). The live site matches the repository build of 2026-11-11.

### Cited Findings
- Page types: home directory (searchable/filterable table), 607 entry pages under /boards/, /ats/ index, 59 /tags/ type pages with definitions, 77 /countries/, 111 /languages/, 12 /regions/, 7 /api/ status pages, 113 /owners/, /ecosystem/ map, /rankings/ (Majestic), /closed/, /changelog/, /about/, feed.xml. Source: [docs/](/home/user/job-board-list/docs/); [https://jobboardlist.com/llms.txt](https://jobboardlist.com/llms.txt)
- docs/index.html is 543,827 bytes with about 11,700 visible words (all rows server-rendered); live response is the same 543,827 bytes. Source: [docs/index.html](/home/user/job-board-list/docs/index.html); [https://jobboardlist.com/](https://jobboardlist.com/)
- Indexable board pages: median 551 visible words (n=193); noindex board pages median 420 (n=414). Board page sections (Lever example): Notes, How API access works, Prominence and reach, Quick answers, Connections, Sources, Other boards in region. Source: [docs/boards/lever/index.html](/home/user/job-board-list/docs/boards/lever/index.html)
- JSON data API: /data/boards.json (all entries with sources), /data/boards/{id}.json per entry, /data/owners.json, /data/taxonomy.json, /data/relationships.json, /data/lifecycle.json. Source: [scripts/build_site.py lines 700 to 705](/home/user/job-board-list/scripts/build_site.py)
- Downloads (copied verbatim from data/): job_boards.csv, sources.csv, rank.csv, scale.csv, owners.csv, ownership.csv, owner_facts.csv, taxonomy.csv, tags.csv, reviews.csv, relationships.csv, languages.csv, lifecycle.csv, plus job_boards.json. Live job_boards.csv returns 200 text/csv, 177,902 bytes. Source: [scripts/build_site.py line 516](/home/user/job-board-list/scripts/build_site.py); [https://jobboardlist.com/downloads/job_boards.csv](https://jobboardlist.com/downloads/job_boards.csv)
- AI-search layer: llms.txt 2,370 bytes; llms-full.txt 576,917 bytes; 306 index.md twins (served live as text/markdown, for example /boards/lever/index.md 3,292 bytes); robots.txt allows all and sets `Content-Signal: search=yes, ai-input=yes`. Source: [https://jobboardlist.com/robots.txt](https://jobboardlist.com/robots.txt); [https://jobboardlist.com/boards/lever/index.md](https://jobboardlist.com/boards/lever/index.md)
- Structured data counts across built HTML: ListItem 4,447; Question/Answer 1,547 each; Organization 1,495; WebSite 608; FAQPage 608; WebPage 607; BreadcrumbList 607; ItemList 209; PostalAddress only 8. Home has a Dataset with DataDownload distributions. Source: grep over [docs/](/home/user/job-board-list/docs/); [scripts/build_site.py lines 278 to 279](/home/user/job-board-list/scripts/build_site.py)
- Hosting/redirects (live, 2026-11-12): http://jobboardlist.com/ returns 301 to https; https://www.jobboardlist.com/ returns 301 to http://jobboardlist.com/ (an extra hop through http); unknown URL returns 404; served via Cloudflare in front of GitHub Pages, cache-control max-age=600, last-modified 2026-11-11 21:11 GMT. Source: curl checks of [https://jobboardlist.com/](https://jobboardlist.com/) and [https://www.jobboardlist.com/](https://www.jobboardlist.com/)
- About page discloses Google Analytics. Source: [scripts/build_site.py line 508](/home/user/job-board-list/scripts/build_site.py)

### Inferences
- The 544 KB home page with 11,700 words is heavy for mobile and Core Web Vitals and dilutes the home page's topical focus; GSC shows the home page got 18 impressions and the only click.
- The raw CSV download received 15 impressions in GSC, more than most HTML pages. Google is indexing the data file for queries the HTML should win; GitHub Pages cannot send X-Robots-Tag, so the CSV competes with the site's own pages.
- The www to http to https chain is a minor canonicalisation inefficiency worth fixing at Cloudflare.
- FAQPage markup on 608 pages no longer earns rich results for most sites (Google restricted FAQ rich results in 2023, from my background knowledge, not verified here); its main value now is for AI extraction.

### Gaps
- I did not measure page speed or Core Web Vitals.
- I did not inspect the JS search/filter behaviour in a browser.

## 5. Research pipeline steps and recurring failure modes

### Takeaway
The pipeline is a mature, quote-gated agent loop (16 Python scripts plus a browser helper and 13 briefs), but it is losing a large share of work to blocked sites and rejected items: ingest has rejected 543 items against 437 added, about 30% of research_queue rows are HTTP 403/503 or bot-check blocks, and refine rounds yield shrinking returns (facts added per round fell from 25 in round 1 to 7 to 12 in rounds 7 to 10).

### Cited Findings
- Scripts (lines): build_site.py 753, ingest.py 234, refine_round.py 150, ingest_ownership.py 122, ingest_relationships.py 80, check_quotes.py 77, derive_tags.py 71, fetch_wikidata.py 69, sweep_candidates.py 57, ingest_apidetails.py 54, ingest_lifecycle.py 53, promote_holdings.py 50, validate.py 47, fetch_logos.py 36, fetch_rank.py 32, make_og.py 16, browse.js 22. Source: [scripts/](/home/user/job-board-list/scripts/)
- Briefs: discover, discover-class, verify, refine-work, refine-review, browser-sweep, wikipedia, wikipedia-lists, owner-profile, ownership, relationships, api-details, lifecycle. Source: [research/briefs/](/home/user/job-board-list/research/briefs/)
- Documented loop: discover per country, ingest, pick top 8 to verify, verify, ingest + logos + validate + build, mark country. Strong claims need a source on the board's own domain with a quote of 30 words or fewer; verified fields are never overwritten; disagreements go to conflicts.csv; text with model instructions, AI tool brand names or em dashes is dropped. Source: [RESEARCH.md](/home/user/job-board-list/RESEARCH.md)
- 318 findings files in research/findings (batches of 12 per round: sweep 1 to 5, loop6 to loop9, thin1 18). Source: [research/findings/](/home/user/job-board-list/research/findings/)
- ingest_log totals across all batches: added 437, merged 573, rejected 543, conflicts 17. Largest rejection batch: 2026-11-09 (CZ, RO, TR, KR, CN, ID, MY, PH, TH, VN, SA, EG, NG, KE, AR, CO, CL, PE + sweep5) added 83, rejected 98. The 2026-11-11 multiposting batch added 18, rejected 10. Source: [data/ingest_log.csv](/home/user/job-board-list/data/ingest_log.csv)
- loop_log.csv (10 refine rounds, 32 planned each): facts_added 25, 11, 22, 21, 18, 10, 9, 13, 7, 12; not_found 40, 43, 33, 29, 14, 15, 20, 16, 15, 11; flags 15, 10, 22, 23, 22, 24, 25, 37, 24, 27. Source: [data/loop_log.csv](/home/user/job-board-list/data/loop_log.csv)
- attempts.csv: 513 field attempts: found 256, not-found 236, blocked 21. Most attempted fields: founded 124, hq_country 97, business_model 75, parent 73, languages 69. Source: [data/attempts.csv](/home/user/job-board-list/data/attempts.csv)
- loop_flags.csv: 229 reviewer flags. Keyword counts: "parent" 65, "confirm" 26, "domain" 11, "not stated" 7, "blocked" 6, "quote" 6, "redirect" 5, "closed" 4. Recurring patterns: fields listed as missing although already recorded (state drift between review and work steps), operator vs parent ambiguity (for example "Footer reads 'Powered by Arca24'", Indeed vs Recruit as operating entity), unconfirmed api_docs_url (iCIMS developer portal not linked from homepage), language lists not matching the site's switcher, guessed URLs returning 404, and bot challenges. Source: [data/loop_flags.csv](/home/user/job-board-list/data/loop_flags.csv)
- Reviews: 55 of 383 reviewed entries blocked and 13 unreachable (18%); 53 not-stated. Source: [data/reviews.csv](/home/user/job-board-list/data/reviews.csv)

### Inferences
- Field-level refinement of generic company facts (founded, hq_country) is now in diminishing returns and does not target what searchers ask for. Research effort would yield more if redirected to API/integration details, relationships and the thin distribution and outplacement classes.
- The rejection rate (543 rejected vs 437 added) is partly the quality gate working, but also signals that discovery briefs produce many items that cannot be backed by own-domain quotes; tightening discovery to candidates with readable sites would save effort.
- About 18% of reviewed sites block automated reading. A documented fallback (Wikidata, official registries, press releases on owner domains, archive snapshots) could lift some of these without bypassing protections.

### Gaps
- I did not read every brief line by line or every findings JSON, so failure-mode counts rely on the CSV logs, not the raw agent transcripts.
- Rejection reasons are printed at ingest time but not stored per item in a CSV, so I could not break the 543 rejections down by cause.

## 6. Biggest gap between searcher demand (GSC) and what the site provides

### Takeaway
Searchers arrive with integration and API intent ("ats job board integration", "job multiposter & distribution for lever", "jobvite integration", "recruitee api", "stepstone api", "greenhouse api", "which ats have a public api for job postings", "job feed management services in uk"), but the site's answers to those intents are thin: API details exist for 16 entries, the distribution layer is mostly empty, there is no per-ATS "which job boards does X post to / which multiposters support X" page, and several of the specific queried entities (StepStone, Jobvite, Handshake, CV-Library, France Travail, Taleo) have no structured API details. Early performance is weak (2 clicks, 246 impressions, average position 32.4), consistent with pages that are relevant but not the best answer.

### Cited Findings
- GSC (owner screenshots): 2 clicks, 246 impressions, CTR 0.8%, average position 32.4 since about 2026-11-06; top page /tags/ats-integration/ (24 impressions); top query "ats job board integration" (20). Only clicked query: "job board directory". Source: assignment context (owner's GSC screenshots)
- /tags/ats-integration/ exists, about 970 visible words, with 17 h3 groups listing documented connections per ATS/distribution platform. Source: [docs/tags/ats-integration/index.html](/home/user/job-board-list/docs/tags/ats-integration/index.html)
- Lever has 19 outgoing relationship edges and 7 API detail rows, but its page contains zero mentions of "multipost" and has no section on multiposting or distribution partners serving Lever. The /ats/lever/ URL that GSC shows (15 impressions) is a 200 meta-refresh stub. Source: [docs/boards/lever/index.html](/home/user/job-board-list/docs/boards/lever/index.html); [docs/ats/lever/index.html](/home/user/job-board-list/docs/ats/lever/index.html)
- Query entity coverage in data: Jobvite (ats, 6 facts, api public-key, 0 api_details rows); Recruitee (7 facts, 7 api_details rows); StepStone (board, 7 facts, partner-only, 0 api_details); Greenhouse (6 facts, 5 api_details); Handshake (niche-board, 7 facts, partner-only, 0); Oracle Recruiting (7 facts, 0); Taleo (seed-unverified, 3 facts, noindex); iCIMS (6 facts, 5 api_details); CV-Library (9 facts, 0); France Travail (9 facts, public-key, 0); Indeed (10 facts, 0); Freelancermap (4 facts, 0); Thrive Career Wellness (outplacement, 3 facts, api unknown); Job Bank Canada (9 facts, 4 api_details). Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [data/api_details.csv](/home/user/job-board-list/data/api_details.csv)
- "job feed management services in uk": UK distribution entries with facts are only Broadbean (seed-unverified, noindexed) and JobG8; idibu, Vacancy Poster and Career Poster have zero facts; LogicMelon is not an entry. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv)
- "polish job boards" (14 impressions) lands on /languages/polish/ (13 impressions); a /countries/poland/ page also exists. 15 entries serve or are based in Poland, but Pracuj is noindexed (seed-unverified) and OLX Praca and Just Join IT have 0 facts; No Fluff Jobs is not an entry. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [docs/languages/polish/index.html](/home/user/job-board-list/docs/languages/polish/index.html)
- "ofccp job multiposter & distribution for lever" received impressions; a 2026-11-11 findings file "multi-ofccp" exists, but no OFCCP-specific tag or page exists in taxonomy. Source: [data/ingest_log.csv](/home/user/job-board-list/data/ingest_log.csv); [data/taxonomy.csv](/home/user/job-board-list/data/taxonomy.csv)
- "which ats have a public api for job postings": the /api/ status pages and /ats/ index exist, but only 12 entries total are public-open and 28 public-key, and api_status is unknown for 511 entries. Source: [data/job_boards.csv](/home/user/job-board-list/data/job_boards.csv); [docs/api/](/home/user/job-board-list/docs/api/)

### Inferences
- The highest-leverage content gap is an "integration intelligence" layer: for each major ATS, a page answering which job boards and multiposters it connects to, how (XML feed, API, multiposter), whether a public job postings API exists, and with which auth/limits; and for each major board, how employers and ATS get jobs onto it (API, feed, partner). The data model (relationships, api_details, ingest_methods) already supports this; coverage does not.
- A comparison/list page answering "which ATS have a public API for job postings" and "job multiposting/feed management services in the UK" would directly match observed queries and AI-search question formats.
- For the competitor-directory goal, outplacement (9), staffing (27, mostly 0 to 1 facts) and career-services (9) are far too small and shallow to rank or to serve as a directory; the relationship backlog (105 partner names queued, 114 unresolved edge endpoints) is the fastest way to expand ATS and distribution coverage.
- Position 32.4 average indicates page 3 to 4 placement; with one week of data and 204 indexed pages, the main levers are deeper answers on the already-impressioned pages (/tags/ats-integration/, /boards/stepstone/, /boards/lever/, /languages/polish/, /boards/jobbank-ca/) rather than more thin pages.

### Gaps
- GSC data covers about one week and only top queries; low volumes (2 to 24 impressions) make any query ranking noisy.
- I did not check competing SERPs for these queries, so I cannot say what content currently outranks the site.
