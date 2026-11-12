# Greenhouse

Greenhouse is an applicant tracking system based in United States, focused on applicant tracking system.

- Website: https://www.greenhouse.com
- Headquarters: United States
- Founded: not recorded
- Owner: not recorded
- Languages: not recorded
- API status: Open API (no key) (https://developers.greenhouse.io/job-board.html)
- Partner program: yes
- Prominence: #20,456 globally, tier Established
- Tags: Open API, Applicant tracking system, Enterprise, Mid-market, Partner program, Public job feed
- Review: Reviewed 2026-11-06. Some facts checked against the board's own site. Not stated there: owner.
- Data status: partly verified against its own site

## How API access works

- Public job feed: JSON endpoint per job board: GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs; no authentication required for GET endpoints (https://developers.greenhouse.io/job-board.html)
- How to get access: Read endpoints are public and need no key (https://docs.greenhouse.io/job-board.html#introduction)
- Authentication: HTTP Basic auth with the Job Board API key, required only for application POST (https://docs.greenhouse.io/job-board.html#introduction)
- Data formats: JSON representation of offices, departments and published jobs (https://docs.greenhouse.io/job-board.html#introduction)
- What it covers: Published jobs, offices and departments, plus application submission by POST (https://docs.greenhouse.io/job-board.html#introduction)

## Quick answers

**Does Greenhouse have an API?** According to this directory, Greenhouse has an open API or feed that does not require approval. Documentation: https://developers.greenhouse.io/job-board.html.

**How large is Greenhouse?** Greenhouse ranks #20,456 among all websites by web link popularity (Majestic Million, 2026-11-12), in the Established tier. This measures how widely the site is linked to, not traffic or job volume.

**Which platforms does Greenhouse connect to?** According to this directory, Greenhouse sends jobs to Talent.com, Appcast, Arbeitnow, Indeed, LinkedIn, Monster and others; integrates with Joveo.

**How do you get API access to Greenhouse?** According to Greenhouse's own documentation, access works like this: Read endpoints are public and need no key; requests authenticate with HTTP Basic auth with the Job Board API key, required only for application POST.

## Sources

- [Deutsch page language menu](https://www.greenhouse.com/de) (Languages, checked 2026-11-06): "English (US)"
- [UK page language menu](https://www.greenhouse.com/uk) (Languages, checked 2026-11-06): "English (UK)"
- [Pricing](https://www.greenhouse.com/pricing) (Business model and pricing, checked 2026-11-06): "Greenhouse pricing is customized based on your company’s hiring needs."
- [Introduction - Job Board API | Greenhouse](https://developers.greenhouse.io/job-board.html) (API access, checked 2026-11-11): "Job Board data is publicly available, so authentication is not required for any GET endpoints."

Canonical page: https://jobboardlist.com/boards/greenhouse/
Last updated: 2026-11-11
