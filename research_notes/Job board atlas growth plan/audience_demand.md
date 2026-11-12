# Audience demand for hiring-ecosystem information (Job Board Atlas)

Research date: 12 November 2026. Scope: global, with US, UK, EU and APAC notes. About 17 searches and fetches. Several search results were summarised by the search tool; where only a snippet was available it is marked "(snippet)". Vendor blogs are flagged as such because many sources in this space sell the product they write about.

## 1. Which audiences seek this information and why

### Takeaway
Nine audiences emerge, but they differ sharply in urgency. Demand is strongest where something external forces action: Indeed's feed policy change (TA ops, ATS vendors, agencies), legacy board bankruptcies and consolidation (employers, board operators, investors), rising cost per application (employers, programmatic buyers), restricted job-data APIs (developers), and posting-compliance rules (US federal contractors, EU employers after June 2026).

### Cited Findings
**Employers and recruiters choosing where to post**
- Appcast's 2026 Recruitment Marketing Benchmark Report (released 17 Feb 2026; over 302 million clicks, 27 million applications, nearly 1,200 employers) found cost per application and cost per hire both rose "sharply" in 2025 despite a softer labour market, driven by "shifts in job board pricing and programmatic media models". Older and rural US states had the highest advertising costs; frontline healthcare roles were expensive and hard to fill; remote jobs began losing their performance edge. Source: [HR Dive](https://www.hrdive.com/news/cost-per-hire-application-increase-2025-recruitment-appcast/812612/)
- Vendor content repeatedly advises buyers to trial niche boards before committing and to track qualified candidates and hires per board, showing that "which board actually works for my role" is the core employer question. Source: [Firefish](https://blog.firefishsoftware.com/niche-job-boards), [ExactHire](https://www.exacthire.com/workforce-management/do-niche-job-boards-really-work/) (snippet, vendor content)
- GummySearch built a "best job boards" ranking from 185 Reddit reviews across 50 subreddits, which indicates recurring Reddit discussion of board quality. Source: [GummySearch](https://gummysearch.com/tools/best-products/job-boards/) (snippet)

**TA operations teams and staffing agencies wiring ATS to boards**
- Indeed stopped accepting new single-source feeds for integrated ATS partners in the US in June 2025, pushing posting through its Job Sync and Job Update APIs. Source: [College Recruiter podcast, 19 Jun 2025](https://www.collegerecruiter.com/blog/2025/06/19/breaking-news-indeed-wont-accept-jobs-via-xml-ep106)
- Indeed's help centre lists a single-source feed policy effective 31 March 2026; after it, ad agencies can manage integrated ATS jobs only through the Job Update API. SAP published a knowledge-base article asking customers to move to multi-source feeds by the same date. Source: [Indeed AU help centre](https://au.indeed.com/help/employers/articles/single-source-feed-policy-effective-march-31-2026), [SAP KBA 3710318](https://userapps.support.sap.com/sap/support/knowledge/en/3710318)
- Indeed documents ATS partner integrations for its Sponsored Jobs API and Indeed Apply, and its Job Sync FAQ says the API replaces the XML integration. Source: [Indeed Sponsored Jobs API ATS integrations](https://docs.indeed.com/sponsored-jobs-api/ats-integrations/), [Indeed Job Sync FAQ](https://docs.indeed.com/job-sync-api/faq)
- Chris Hoyt (CXR) wrote in July 2025 that "platform shifts are disrupting employer hiring". Source: [CXR community](https://community.cxr.works/blogs/chris-hoyt/2025/07/25/platform-shifts-are-disrupting-employer-hiring) (title only seen)
- Staffing-oriented content asks "What ATS systems integrate directly with Indeed?", which is exactly an integration-matrix question. Source: [RecruitBPM](https://recruitbpm.com/blog/what-ats-systems-integrate-directly-with-indeed-complete-guide-for-staffing-agencies) (title only seen)

**Developers seeking job data APIs**
- LinkedIn offers no public jobs search API; its Job Posting API is push-only and partner-gated, and one guide reports new Job Posting partnerships were not being accepted. Developers turn to third-party job data APIs, board-specific APIs, or scraping with terms-of-service risk. Reports conflict on history (one says the jobs API was shut in 2018). Source: [Scrapfly](https://scrapfly.io/blog/posts/guide-to-linkedin-api-and-alternatives), [jobspipe](https://jobspipe.dev/answers/does-linkedin-have-a-jobs-api.md), [Jesse Perz blog, Aug 2025](https://jesseperz.blogspot.com/2025/08/tired-of-linkedins-jobs-api-these-tools.html) (vendor and blog content)
- Indeed's public Publisher (job search) API, a free XML feed for affiliates, was retired, per a third-party developer site (it says 2024; not confirmed with Indeed). Source: [jobspipe Indeed](https://jobspipe.dev/sources/indeed.md)
- A visible ecosystem of scrapers and job APIs (Apify actors, Zyla Labs marketplace listings, DEV Community "how to scrape LinkedIn jobs in 2026" posts) shows active developer demand. Source: [Apify Workable jobs actor](https://apify.com/nabeelbaghoor/workable-jobs-api.md), [DEV Community](https://dev.to/agenthustler/how-to-scrape-linkedin-job-listings-in-2026-tools-code-and-legal-notes-13lb)

**Job board operators, investors and analysts (consolidation and ownership)**
- CareerBuilder and Monster filed for Chapter 11 in June 2025; BOLD (owner of Monster, CareerBuilder, FlexJobs and MyPerfectResume in later reporting) acquired Joblist; Jobiqo acquired JOBS.DE (previously in Kariera Group); Adzuna acquired the Trovit and Mitula jobs businesses; Gaia acquired US social recruitment ad firm SocialJobs (20 April 2026); JobGet acquired RippleMatch; Humanly bought CareerArc (its fifth deal since 2025). Source: [Jobiqo on JOBS.DE](https://www.jobiqo.com/?p=4063), [Gaia](https://www.iamgaia.com/resources/gaia-acquires-socialjobs-to-accelerate-us-market-expansion), [pulse.bot Adzuna](https://www.pulse.bot/ai/deals/adzuna-acquires-trovit-and-mitula-jobs-businesses-to-expand-global-footprint-3c596570-f64f-49ea-9a80-e923946ce252), [pulse.bot JobGet](https://www.pulse.bot/hrtech/news/jobget-acquires-ripplematch-7cfc07f1-64d2-473d-bf99-54e663c5efc6/), [Dealroom Humanly](https://dealroom.co/news/162501-humanly-buys-careerarc-in-fifth-deal-since-2025-extending-ai-hiring-push/) (bankruptcy and BOLD details were in the search summary; verify against primary filings)
- Programmatic: Appcast, Joveo and PandoLogic are commonly treated as the three largest programmatic job ad firms; Appcast is owned by StepStone and PandoLogic by Veritone. Source: [Joveo blog](https://www.joveo.com/blog/best-programmatic-job-advertising-platforms/), [CB Insights Appcast](https://www.cbinsights.com/company/appcast) (snippet, vendor content)
- Job board owners have their own event circuit (e.g. Job Boards Connect, London 2025), indicating an operator audience seeking partners and market intelligence. Source: [Jobiqo blog](https://www.jobiqo.com/blog/category/market-trends) (snippet)
- An HR marketing tool review found 13 of 20 tools do not publish a price. Source: [Webtonic](https://www.webtonic.io/blog/best-hr-recruitment-marketing-tools) (title only seen)

**Compliance teams**
- US: VEVRAA (38 U.S.C. 4212, 41 CFR 60-300) still requires covered federal contractors to list most openings with the state employment service delivery system, concurrently with other recruitment sources, even after EO 11246 was revoked on 21 Jan 2025. Exempt: executive and top management roles, internal fills, jobs of 3 days or less. Source: [DOL eLaws VEVRAA](https://webapps.dol.gov/elaws/elg/vietvets.htm), [ClearedJobs.net](https://blog.clearedjobs.net/ofccp-job-posting-requirements/), [Mondaq on proposed OFCCP rules](https://www.mondaq.com/unitedstates/discrimination-disability-sexual-harassment/1649474/ofccp-proposes-new-rules-to-clarify-federal-contactor-obligations-following-the-revocation-of-eo-11246)
- The VEVRAA contract coverage threshold is reported inconsistently ($150,000 rising to $200,000 from 1 Oct 2025 in one source; a $100,000 figure in another). Not verified against the Federal Register. Source: [ofccp.com 2026 guide](https://ofccp.com/ofccp-compliance-2026-federal-contractor-obligations); contradicted by older guidance such as [bestmilitaryresume.com](https://bestmilitaryresume.com/blog/hiring-veterans/vevraa-mandatory-job-listing-federal-contractors)
- Ogletree reports OFCCP's start to 2026 focused on complaints and VEVRAA. Source: [Ogletree](https://ogletree.com/insights-resources/blog-posts/ofccps-start-to-2026-proposed-funding-and-a-focus-on-complaints-and-vevraa/)
- DirectEmployers sells an OFCCP compliance job-distribution product, showing a paid market for compliant posting. Source: [DirectEmployers](https://directemployers.org/delite)
- EU: the Pay Transparency Directive transposition deadline of 7 June 2026 passed with only about four member states (Slovakia, Italy, Lithuania, Malta; trackers differ on the last two) fully transposed; the Netherlands and Denmark target 1 Jan 2027; Sweden seeks renegotiation; Germany had not legislated. The directive gives candidates rights to pay ranges, affecting job advertising. Source: [Morgan Lewis, Jun 2026](https://www.morganlewis.com/pubs/2026/06/eu-pay-transparency-directive-the-deadline-for-transposition-has-passed-what-now), [WageIndicator, 30 Jun 2026](https://wageindicator.org/ai/work/collective-bargaining-agreement/updates/2026/eu-sources-just-four-member-states-have-transposed-the-pay-transparency-directive-june-30-2026/), [Assessio tracker](https://assessio.com/articles/pay-transparency-directive-country-tracker/)

**Outplacement buyers and HR leaders**: see section 5.

**Job seekers**
- Job seeker content ("best job boards 2026", "top 25 niche job boards") is abundant and mostly produced by career blogs and resume vendors. Source: [The Interview Guys](https://blog.theinterviewguys.com/niche-job-boards/), [Huntr](https://api.huntr.co/blog/best-niche-job-boards-to-find-hard-to-land-roles) (titles only)

### Inferences
- The highest-value, least-served audiences for a cited directory are TA ops, staffing agencies, ATS vendors and developers, because their questions (which ATS integrates with which board, by what method, under which API program) are factual, change often, and are badly answered by vendor blogs. Employers and job seekers have more search volume but far more competing content.
- Regulatory and platform events (Indeed March 2026 feed policy, EU pay transparency, VEVRAA listing) create spikes of urgent, specific questions that a changelog plus explainer pages could capture.
- Investors and board operators value an ownership and M&A timeline; nothing open and cited appears to exist (AIM Group covers it, but behind a paywall).

### Gaps
- Direct Reddit thread content (r/recruiting, r/humanresources, r/recruitinghell) was not retrievable in this session; pain points are inferred from vendor and press sources, not first-hand forum posts.
- No Stack Overflow question counts for job board APIs were found.
- AIM Group, ERE, Recruiting Daily and Hunt Scanlon coverage was not reached directly.
- UK and APAC-specific posting rules (e.g. UK salary advertising norms, Australian or Singapore fair-hiring posting rules) were not researched.

## 2. Concrete questions and pain points

### Takeaway
Pain clusters around five themes: rising and opaque costs, broken or changing integrations, gated APIs, compliance obligations, and market churn (who owns what, who shut down).

### Cited Findings
- Cost: cost per application and cost per hire rose sharply in 2025 (Appcast). Source: [HR Dive](https://www.hrdive.com/news/cost-per-hire-application-increase-2025-recruitment-appcast/812612/)
- Measurement: vendors urge tracking cost per quality applicant and cost per hire by source, not cost per applicant alone. Source: [Joveo bidding guide](https://www.joveo.com/blog/programmatic-job-advertising-bidding/) (vendor, snippet)
- Price opacity: 13 of 20 HR marketing tools do not publish prices. Source: [Webtonic](https://www.webtonic.io/blog/best-hr-recruitment-marketing-tools); one agency estimates enterprise Joveo programmes at roughly $3,000 to $15,000 a month (unsourced estimate). Source: [Integral Recruiting](https://integralrecruiting.com/programmatic-job-advertising-icims-healthcare/)
- Integrations: "Indeed won't accept jobs via XML from agencies and employers" (June 2025) and the 31 March 2026 single-source feed cut-off forced ATS and agency migrations. Source: [College Recruiter](https://www.collegerecruiter.com/blog/2025/06/19/breaking-news-indeed-wont-accept-jobs-via-xml-ep106), [Indeed help](https://au.indeed.com/help/employers/articles/single-source-feed-policy-effective-march-31-2026)
- API access: "Does LinkedIn have a jobs API?" is a recurring developer question; the answer is partner-only. Source: [jobspipe](https://jobspipe.dev/answers/does-linkedin-have-a-jobs-api.md)
- Compliance: "What must a federal contractor list, and where?" Source: [ClearedJobs.net](https://blog.clearedjobs.net/ofccp-job-posting-requirements/); "Which EU countries have transposed?" Source: [Mondaq tracker](https://www.mondaq.com/employee-rights-labour-relations/1815864/eu-pay-transparency-directive-which-countries-have-transposed)
- Churn: legacy board bankruptcies and repeated acquisitions (section 1).

### Inferences
- Concrete question set for the site, by audience:
  - Employer: Which boards cover country X and niche Y? What does a posting cost, and on what model (slot, PPC, PPA)? Is board X still alive and who owns it?
  - TA ops / agency: Does my ATS post to board X natively, via a multiposter, or by feed? Which multiposters cover my country list? What changed with Indeed / LinkedIn this quarter?
  - ATS vendor / developer: Does board X have a posting API, an apply API, a search API? Is there a partner program, how do I apply, and what does it cost?
  - Board operator: Which aggregators and programmatic vendors accept feeds, on what terms?
  - Investor: Who owns what, recent deals, shutdowns.
  - Compliance: Which boards or services satisfy VEVRAA listing; what pay range rules apply per EU country.

### Gaps
- No survey quantifying which of these pain points is most common was found.

## 3. Search demand

### Takeaway
Reliable keyword volumes were mostly unavailable from public sources. The scattered figures found suggest category-level terms are modest (hundreds to low thousands of US searches a month), integration and API terms are niche, and outplacement terms carry very high commercial value (high CPC). Treat all figures as directional.

### Cited Findings
- "tech job board": 2,400 US monthly searches on one page and 2,900 on another; "healthcare job board" 590; "mental health job boards" 90 (seodata.dev, which says it uses Google Ads API data; 2026 snapshots that disagree). Source: [seodata.dev](https://www.seodata.dev/keyword/mental-health-job-board) (search summary; direct fetch of one page returned 404)
- "outplacement services": 2,400 monthly, KD 34, CPC $124.70 (SEOJuice, apparently worldwide); versus 590 monthly, CPC $5.08 (iSpionage, no date or region). The two tools disagree by roughly 4x on volume and 25x on CPC. Source: [SEOJuice HR consulting keywords](https://seojuice.com/keyword-research/business-services/hr-consulting-&-employment-law/), [iSpionage](https://www.ispionage.com/Competitive_Intelligence_directory/i/145/impactgrouphr_com_696D7061637467726F757068722E636F6D)
- No public volume for "job board api" was found. Source: search returned only adjacent seodata.dev pages ([example](https://www.seodata.dev/keyword/education-job-boards))

### Inferences
- "best job boards in <country>" and "<ats> integrations" patterns are likely long-tail: individually small, collectively large. A programmatic page set (country x niche, ATS x board) fits this better than chasing head terms.
- The high CPC on outplacement terms (if the SEOJuice figure is right) suggests outplacement providers pay heavily for buyer traffic, which supports a partner or listing-upgrade model for that section.

### Gaps
- No verified volumes for "job multiposting", "multiposting", "programmatic job advertising", "<ats> integrations", "OFCCP job posting requirements", "job board api", or non-English equivalents (e.g. "multidiffusion offres d'emploi", "Stellenbörsen Übersicht"). Recommend pulling these from Google Keyword Planner, Ahrefs or Semrush before prioritising; free web results are inconsistent.

## 4. Formats and features valued

### Takeaway
Evidence points to comparison tables, integration lists, and up-to-date status trackers as the formats audiences seek; price transparency is a conspicuous gap.

### Cited Findings
- Country-by-country trackers are the dominant format for EU pay transparency questions (Assessio, Mondaq, Trusaic trackers). Source: [Assessio](https://assessio.com/articles/pay-transparency-directive-country-tracker/), [Trusaic](https://trusaic.com/blog/eu-pay-transparency-directive-who-transposed-who-delayed-the-risks/)
- Side-by-side comparison tables dominate outplacement buyer content. Source: [Leland](https://www.joinleland.com/library/a/top-outplacement-firms)
- Integration lists ("What ATS integrate directly with Indeed?") and official partner directories (Indeed Sponsored Jobs API ATS integrations) exist but are per-vendor, not cross-vendor. Source: [Indeed docs](https://docs.indeed.com/sponsored-jobs-api/ats-integrations/), [RecruitBPM](https://recruitbpm.com/blog/what-ats-systems-integrate-directly-with-indeed-complete-guide-for-staffing-agencies)
- Pricing is often unpublished (13 of 20 tools). Source: [Webtonic](https://www.webtonic.io/blog/best-hr-recruitment-marketing-tools)
- Platform release notes (Indeed docs release notes, e.g. 3 Nov 2025) are where integration changes are announced, so a cross-platform change log has an obvious data source. Source: [Indeed release notes](https://docs-plus.indeed.com/release-notes/2025/2025-11-03)
- A developer-API vendor (jobspipe) now advertises an MCP server for job search, indicating AI-agent consumers of job data. Source: [jobspipe](https://jobspipe.dev/sources/indeed)

### Inferences
- Priority features: (1) cross-vendor ATS-to-board integration matrix with method (native API, feed, multiposter) and last-verified date; (2) API and partner-program pages per board with access type and status; (3) country and niche guides; (4) acquisitions, shutdowns and policy change log; (5) pricing benchmarks where published; (6) downloadable data or API, possibly an MCP endpoint, for developers and analysts.

### Gaps
- No user research on preferred formats specifically for directories was found.

## 5. Outplacement market structure and what a section needs

### Takeaway
Outplacement is a roughly USD 5 to 6 billion, moderately fragmented market led by staffing-group subsidiaries (LHH/Adecco, Right Management/ManpowerGroup, RiseSmart/Randstad, INTOO/Gi Group), shifting to virtual delivery. Buyers ask about coach matching, outcomes, pricing per level, reporting and global coverage.

### Cited Findings
- Market size USD 5.21 bn (2025), 5.58 bn (2026), 7.89 bn (2031), 7.16% CAGR; North America 41.40% of 2025 revenue; APAC fastest growing (8.63% CAGR); group outplacement 46.12%; executive outplacement fastest growing (10.12% CAGR); enterprise clients 69.25%; virtual/online delivery 61.30%, growing 13.65% CAGR; top five vendors hold under 40% of revenue. Source: [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/outplacement-market) (paid-report summary; other analyst houses publish different sizes)
- Major players per Mordor: Randstad RiseSmart, LHH, Mercer, Career Partners International, Right Management. Recent moves: Careerminds acquired Progression (Oct 2024); LHH launched Career Studio (Dec 2024); Keystone Partners acquired The Ayers Group (undated). Source: [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/outplacement-market)
- Everest Group's PEAK Matrix placed LHH, Randstad RiseSmart and Right Management among leaders. Source: [Everest Group brochure](https://www2.everestgrp.com/Libraries/reports/Products/EGR-2022-24-R-5712/MarketingBrochure) (snippet)
- Unverified share estimates: LHH 25 to 30%, Right Management 20 to 25%, RiseSmart 15 to 20% from a low-authority brief; these conflict with Mordor's "top five under 40%". Source: [UNSPSC brief](https://storage.googleapis.com/unspsc_code/reports/93141805.html); contradicted by [Mordor](https://www.mordorintelligence.com/industry-reports/outplacement-market)
- Owners: LHH (Adecco Group), Right Management (ManpowerGroup), INTOO (Gi Group), Randstad RiseSmart (Randstad); other named providers include Korn Ferry, Challenger Gray & Christmas, Careerminds, Keystone Partners, IMPACT Group, Leland. Source: [Leland comparison](https://www.joinleland.com/library/a/top-outplacement-firms) (Leland is itself a provider)
- Pricing benchmarks (2026): entry level 1 to 3 months $1,200 to $3,800; manager/director 3 to 6 months $4,000 to $8,000; executives 6 to 12 months $8,000 to $18,000+; volume discounts of about 10 to 20%. Source: [Leland](https://www.joinleland.com/library/a/top-outplacement-firms) (vendor-published)
- Buyer questions: how coaches are matched; outcome metrics (time to placement, offer rates) by level; proactive vs reactive engagement; tech vs human coaching; HR reporting; flexibility mid-programme. Source: [Leland](https://www.joinleland.com/library/a/top-outplacement-firms); similar buyer guides from [IMPACT Group](https://impactgrouphr.com/blog/best-outplacement-firms) and [Careerminds](https://careerminds.com/blog/top-10-outplacement-firms) (vendors ranking their own category)
- Careerminds published a European outplacement services overview (May 2025), signalling buyer interest in country coverage. Source: [Careerminds PDF](https://careerminds.com/wp-content/uploads/2025/05/European-Outplacement-Services-FINAL.pdf) (not read in full)

### Inferences
- Nearly all "best outplacement firms" content is written by outplacement vendors, so an independent cited directory has a clear credibility gap to fill.
- A useful section needs: provider profiles with parent company and ownership history; countries and languages served (critical for EU collective redundancies and APAC); delivery model (virtual, hybrid, in person); levels served (group, executive); published pricing or pricing model; outcome metrics where disclosed; analyst recognition; integration or HRIS reporting; and a comparison table filterable by country and level. A regional note on mandated or customary outplacement (e.g. some EU countries) would add value but was not researched here.

### Gaps
- Hunt Scanlon coverage and any public market-share data were not reached.
- Country rules on statutory outplacement (e.g. Belgium, France) were not verified in this session.
