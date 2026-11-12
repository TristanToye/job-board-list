# SEO and AI-search visibility for a programmatic directory (Job Board Atlas, Nov 2026)

Note on method: research done 2026-11-12 with web search and page fetches. "Official" means Google, Microsoft/Bing, OpenAI, Cloudflare or IndexNow documentation. "Industry" means SEO vendor or trade press research. Items marked "(not re-verified this session)" come from well-known older guidance that I did not re-fetch; treat them as lower confidence.

## 1. Google policy on scaled/programmatic pages, thin content, site reputation, new-site indexing

### Takeaway
Google does not ban programmatic pages; its spam policy targets pages generated "for the primary purpose of manipulating search rankings and not helping users." For a data directory the defence is unique, verifiable, first-hand data per page plus a clear "why" (helping users, not catching queries). Keeping thin entity pages out of the index (noindex) or enriching them is consistent with Google guidance; mass-publishing near-empty templated pages is the main risk.

### Cited Findings
- Official spam policy: "Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings and not helping users." Examples: using generative AI or similar tools "to generate many pages without adding value for users"; "Stitching or combining content from different web pages without adding value"; "Creating many pages where the content makes little or no sense to a reader but contains search keywords." Page shows no update date. [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- Official: the "site reputation policy" applies to third-party content published on a host "mainly because of that host's already-established ranking signals." Examples given are sponsored payday-loan or casino pages on unrelated sites. This does not apply to a first-party directory, but would apply if the site later hosted paid third-party "best job board" content. [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- Official helpful-content self-assessment warns against "extensive automation to produce content on many topics" and "producing lots of content on many different topics in hopes that some of it might perform well." It frames "Who, How, Why": make authorship clear, disclose automation where readers would wonder, and the "Why" (helping people directly, not attracting search visits) is "the most important question." [Creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- Official: the same page warns against adding or removing large amounts of content mainly to look "fresh" or to improve rankings, and recommends auditing pages that lost traffic against the self-assessment questions. It does not name a separate "helpful content system." [Creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- Official (Google AI optimization guide, May 2026): "Producing many pages aimed at manipulating AI responses can violate the scaled content abuse spam policy." [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide); publication dated 15 May 2026 per [Semrush coverage](https://www.semrush.com/blog/google-publishes-generative-ai-search-guide/) and [Gigazine](https://gigazine.net/gsc_news/en/20260518-google-guide-optimizing-generative-ai)
- Background (2024, not re-verified this session): Google introduced the scaled content abuse policy and folded the helpful content system into core ranking in the March 2024 core update announcement. [Google Search Central blog, March 2024](https://developers.google.com/search/blog/2024/03/core-update-spam-policies)
- Official on new-site timing: Google notes that meeting technical requirements "doesn't guarantee crawling, indexing, or serving," and that recrawling after changes "can take days to months." [Google AI features page](https://developers.google.com/search/docs/appearance/ai-features)

### Inferences
- Job Board Atlas's current rule (noindex pages with fewer than 3 cited facts) aligns with Google's framing: those pages are the ones most likely to read as templated keyword pages. Keeping them crawlable (noindex, follow, linked from hubs) lets Google see the noindex and still pass link signals; leaving them out of the sitemap is fine.
- Three options for thin entity pages, in order of preference: (a) enrich with first-hand facts (API docs link, ATS integrations, pricing model, countries, posting volume, last-verified date, source citations) and promote to index once they pass the threshold; (b) consolidate very sparse entities into a hub or list row (e.g., "smaller Polish job boards" table on the country page) and 301 or canonical the stub to that hub; (c) keep noindex. Avoid flipping hundreds of pages to index at once just to grow coverage.
- The strongest anti-scaled-content signals available to this site are things competitors lack: per-fact citations, "last verified" dates, a public methodology page, a corrections/changelog page, and named maintainers (the "Who/How" questions).
- Do not accept paid placements or sponsored third-party reviews on the domain; that is the pattern site reputation policy examples describe.

### Gaps
- I did not find a 2025 or 2026 Google statement giving a numeric threshold for "thin." Google gives none.
- I did not re-fetch the March 2024 or later core update posts; details of 2025/2026 core updates (dates, guidance) were not collected here.

## 2. Structured data for directory, dataset and FAQ content in 2026

### Takeaway
FAQ rich results are gone for all sites (stopped 7 May 2026). Dataset markup only powers Google Dataset Search, not normal results. Google says no special schema is needed for AI features. Keep valid Organization, BreadcrumbList and Dataset markup that matches visible content; treat FAQPage as optional semantic markup with no Google display benefit.

### Cited Findings
- FAQ rich results: Google's documentation carried a deprecation notice that "This feature will no longer appear in Google Search starting May 7, 2026"; the FAQ doc was removed 15 June 2026. [Google Search Central documentation updates](https://developers.google.com/search/docs/appearance/structured-data/faqpage) (fetched page resolved to the doc-updates log). Trade coverage confirms removal for all sites, including the government and health sites that had kept it since the 2023 restriction, with Search Console report and Rich Results Test support removed June 2026 and Search Console API support scheduled to end August 2026. [TechWyse](https://www.techwyse.com/news/ai-search/google-faq-rich-results-deprecated-2026); [Search Atlas](https://searchatlas.com/news/faq-rich-results-are-dead-google-wants-control-of-the-answer-layer/)
- June 2025: Google phased out seven structured data features (Book Actions, Course Info, ClaimReview, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing) to simplify results; Google said rankings are unaffected. [Google Search Central blog, 12 June 2025](https://developers.google.com/search/blog/2025/06/simplifying-search-results). Book Actions deprecation was later reversed. [Search Engine Roundtable](https://www.seroundtable.com/google-drops-support-structured-data-types-40386.html)
- Dataset: a 5 November 2025 doc update clarified that "Dataset structured data exclusively powers results within Dataset Search," not regular Google Search results. Not a removal. [PPC Land](https://ppc.land/google-phases-out-practice-problem-and-dataset-structured-data/) (secondary; Google wording not quoted there)
- Official: for AI Overviews and AI Mode "There's also no special schema.org structured data that you need to add," but structured data should match visible content and remains worthwhile for normal rich result eligibility. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features); [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Background (not re-verified this session): BreadcrumbList and Organization remain documented Google structured data types; ItemList is documented only within the Carousel feature for specific content types (recipes, courses, movies, restaurants), so a generic directory ItemList does not produce a rich result. [Google structured data gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)

### Inferences
- Keep: Organization (site publisher; entity pages could describe each board as Organization with sameAs to official URL and Wikidata where it exists), BreadcrumbList on entity and hub pages (still drives breadcrumb display), Dataset on the dataset/download page (gets the CSV/JSON into Google Dataset Search, a relevant discovery surface for an open data directory).
- FAQPage markup: harmless if it matches visible Q&A, but expect no Google SERP display. The value of FAQ content is now as plain, well-headed text that answers fan-out questions such as "which ATS have a public API for job postings."
- ItemList on hub pages is fine semantically but should not be expected to produce a rich result.
- Search Console's FAQ enhancement report vanishing is expected, not an error.

### Gaps
- I did not verify whether Bing still uses FAQPage for any display, or how ChatGPT/Perplexity treat JSON-LD; no primary statements found.

## 3. How AI search systems choose sources; llms.txt, Bing and ChatGPT, IndexNow, content signals

### Takeaway
For Google AI Overviews/AI Mode the only gate is being indexed and snippet-eligible; ranking and content quality do the rest, though cited pages increasingly come from outside the top 10 because of query fan-out. ChatGPT search needs OAI-SearchBot access and draws on Bing plus other sources (evidence mixed). llms.txt is ignored by Google and rarely fetched by AI retrieval bots; Content Signals are unenforced preferences. Bing Webmaster Tools (with IndexNow) is the cheapest lever for Copilot and part of ChatGPT.

### Cited Findings
Google AI Overviews / AI Mode
- Official: "There are no additional requirements to appear in AI Overviews or AI Mode, nor other special optimizations necessary"; pages must be indexed and eligible to show with a snippet. AI features may run multiple related searches across subtopics (query fan-out) and so "display a wider and more diverse set of helpful links." Controls: robots.txt for Googlebot, nosnippet / data-nosnippet / max-snippet / noindex; Google-Extended for other Google AI uses. AI feature traffic is counted in Search Console Performance under "Web." [Google AI features](https://developers.google.com/search/docs/appearance/ai-features)
- Official (May 2026 guide): "You don't need to create new machine readable files, AI text files, markup, or Markdown" to appear; llms.txt is ignored by Google Search; "There's no requirement to break your content into tiny pieces"; "Seeking inauthentic 'mentions' across the web isn't as helpful as it might seem"; use the "Generative AI performance report in Search Console" to measure; be skeptical of third-party tools claiming internal Google metrics; mentions agent-friendly website practices. [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Industry (Ahrefs): July 2025, 76.1% of AI Overview citations ranked in the top 10. A March 2026 update on 863K keywords / 4M cited URLs found only 37.9% in the top 10, 31.2% at positions 11 to 100, 31.0% beyond 100; Ahrefs says methodology improved so the two are not directly comparable. BrightEdge reported about 17% top-10 overlap with different methods. [Ahrefs 2026 update](https://ahrefs.com/blog/ai-overview-citations-top-10/); [Ahrefs 2025](https://ahrefs.com/blog/search-rankings-ai-citations/); [Search Engine Journal](https://www.searchenginejournal.com/google-ai-overview-citations-from-top-ranking-pages-drop-sharply/568637/)

ChatGPT search and Bing
- Official (OpenAI): OAI-SearchBot is used to surface sites in ChatGPT search; sites that block it will not be shown in ChatGPT search answers (may still appear as navigational links). GPTBot (training) is separate and can be blocked independently. Robots changes take about 24 hours. ChatGPT-User is not used to decide Search inclusion. Referrals carry utm_source=chatgpt.com. [OpenAI bots docs](https://developers.openai.com/api/docs/bots); [OpenAI publishers FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)
- Industry, conflicting: Seer Interactive (Feb 2025) found 87% of ChatGPT search citations matched Bing top results vs 56% for Google. [Seer Interactive](https://www.seerinteractive.com/insights/87-percent-of-searchgpt-citations-match-bings-top-results). NP Digital (July 2025, 800 responses) attributed over 55% of citations to Google-aligned sources and about 45% to Bing. [Neil Patel](https://neilpatel.com/marketing-stats/google-vs-bing-chatgpt-search-sources/). Profound found growing Google alignment but most sources independent of Google's index. [Profound](https://tryprofound.com/blog/ai-search-shift). No OpenAI statement on which index it uses was found.

Bing / Copilot
- Industry: Bing Webmaster Tools launched an "AI Performance" report (public preview, Feb 2026) showing citations of your pages in Copilot, Bing AI summaries and some partner integrations, organized by "grounding queries" (the background queries the AI issues) and pages; no click data; later added Intents, Topics, Citation Share. Sites can be imported from Search Console. [Search Engine Land](https://searchengineland.com/bing-webmaster-tools-testing-new-ai-performance-report-468039); [Practical Ecommerce](https://www.practicalecommerce.com/bings-improved-ai-performance-section); [Search Influence](https://www.searchinfluence.com/blog/bing-ai-performance-report-copilot-citations/)

IndexNow
- Official: participating engines with endpoints listed are Amazon, Bing, Naver, Seznam.cz, Yandex and Yep; Google is not listed. Up to 10,000 URLs per POST; submission does not guarantee indexing; per-site daily caps apply (HTTP 429). [IndexNow FAQ](https://www.indexnow.org/faq)

llms.txt
- Industry (Ahrefs, June 2026, 137,210 domains, May 2026 logs): 28% publish llms.txt (upper bound), 97% of those files got zero requests; AI retrieval bots (OAI-SearchBot, PerplexityBot, Claude search) made only a couple hundred fetches combined; most reads come from agents and coding tools; no AI bot requested a missing /llms.txt. Ahrefs calls it "largely decoration" for AI search and flags prompt-injection risk. [Ahrefs llms.txt study](https://ahrefs.com/blog/llmstxt-study/)
- Industry: Originality.ai counted llms.txt growing 8.8x (4,088 to 36,120 instances, June 2025 to May 2026) with near-zero evidence of AI reads; SE Ranking (300K domains) found about 10% adoption and no clear citation effect. [PPC Land summary](https://ppc.land/llms-txt-adoption-rises-8-8x-but-97-of-files-get-zero-ai-requests/); [Search Engine Land](https://searchengineland.com/does-llms-txt-matter-467740)

Content Signals
- Official (Cloudflare, 24 Sept 2025): Content-Signal lines in robots.txt express search, ai-input (RAG/grounding) and ai-train preferences; "content signals express preferences; they are not technical countermeasures against scraping"; some companies may ignore them. Managed robots.txt on 3.8M+ domains defaults to search=yes, ai-train=no. The post does not say Google or others honor them. [Cloudflare Content Signals Policy](https://blog.cloudflare.com/content-signals-policy/)

Perplexity
- Industry only: PerplexityBot is described as the indexing crawler that respects robots.txt and Perplexity-User as a user-triggered fetcher; source choice is described as relevance, quality, recency and authority. No primary Perplexity publisher doc was retrieved. [Tenten](https://geo.tenten.co/en/blog/perplexity-crawler-setup); [wpseoai](https://wpseoai.com/blog/how-does-perplexity-ai-decide-which-sources-to-cite-in-its-answers/)
- Background (2025, not re-verified this session): Cloudflare accused Perplexity of using undeclared "stealth" crawlers to evade robots.txt blocks. [Cloudflare blog, Aug 2025](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/)

### Inferences
- Job Board Atlas's AI files (llms.txt, llms-full.txt, Markdown twins, JSON API) are cheap to keep and useful for agents and developer tools (its audience includes integrators asking "<vendor> api"), but should not be counted as a ranking or citation lever. Do not spend more effort on them; ensure they cannot be a duplicate-content issue (Markdown twins should be noindexed via X-Robots-Tag or linked as alternates, not indexed as competing URLs; a GitHub Pages limitation may make X-Robots-Tag require a Cloudflare Transform Rule).
- Highest-leverage AI-visibility actions: (1) verify the site in Bing Webmaster Tools, submit the sitemap, enable IndexNow on deploy (Cloudflare offers Crawler Hints that use IndexNow), and watch the AI Performance grounding queries; (2) confirm robots.txt and Cloudflare bot settings do not block OAI-SearchBot, PerplexityBot, Bingbot or Googlebot (Cloudflare's AI crawl controls can block AI bots by default on some plans); (3) write pages that answer fan-out sub-questions directly with explicit facts and tables ("Does X have a public job posting API? Yes, REST, docs link, verified date").
- Query fan-out favors sites that answer the specific long-tail sub-question; that is exactly the integration/API demand already showing in Search Console, so integration matrix pages ("ATS with public job posting APIs", "multiposters that integrate with <ATS>") are the likeliest AI-citation targets.
- Track ChatGPT referrals via utm_source=chatgpt.com in analytics.

### Gaps
- No primary OpenAI or Perplexity statement on ranking factors for citations.
- No study isolates whether Markdown twins or JSON APIs increase citation rates.
- Whether Google's Generative AI performance report is available to all properties (and its exact fields) was not verified.

## 4. Earning links and authority for open-data/reference directories

### Takeaway
Evidence is mostly practitioner and vendor material, not controlled studies. The consistent pattern: original, citable data (statistics, rankings, reports) earns press and reference links; Google explicitly discourages chasing inauthentic mentions. For this site the natural assets are the dataset itself, derived statistics, and the listed entities' own incentive to link.

### Cited Findings
- Official: Google says "Seeking inauthentic 'mentions' across the web isn't as helpful as it might seem"; focus on high-quality content. [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Industry: Backlinko/BuzzSumo analysis of 912M articles found data-backed formats earn more referring domains (date not shown on page). [Backlinko original research hub](https://backlinko.com/hub/seo/original-research)
- Industry: agencies such as Fractl describe sourcing government datasets, surveys and proprietary data analysis as their core link-earning method. [Fractl](https://www.frac.tl/?p=18632); [Prose Media](https://www.prosemedia.com/blog/building-backlinks-through-exclusive-data-reports-a-strategy-for-earning-authoritative-links)
- Industry (2026): original statistics give journalists something specific to attribute but need credible methodology and a relevant subject; links are not guaranteed. [DesignRush](https://news.designrush.com/data-driven-content-marketing-statistics)
- Industry (Ahrefs, May 2025): Domain Rating correlates well with rankings, and only 1.74% of new pages reached the top 10 within a year, underscoring how much authority matters for a new domain. [Ahrefs how long to rank](https://ahrefs.com/blog/how-long-does-it-take-to-rank/)

### Inferences (practitioner tactics, not evidence-tested)
- Data journalism: publish periodic derived reports from the dataset ("Share of ATS vendors with a public job posting API, by region", "Job board ownership consolidation: who owns what") with a methodology note and a downloadable chart; pitch to HR-tech trade press (e.g., recruiting-tech newsletters and analysts) who regularly need such numbers.
- Outreach to listed entities: notify boards/ATS vendors that they are listed, offer a "verified" badge or embeddable "Listed on Job Board Atlas" link, and a correction form; vendors often link to integration directories and correct their own data, which also feeds enrichment of thin pages.
- Correction/claim form plus public changelog doubles as an E-E-A-T signal (How/Who) and a data-quality loop.
- Developer channels: list the JSON API and CSV in GitHub "awesome" lists (awesome-hr, awesome-public-datasets, awesome-recruiting style lists), Kaggle / data.world / Hugging Face datasets with a link back, and Wikidata items where boards lack identifiers. These give relevant links and get the dataset into places LLM-grounded tools draw from.
- Wikipedia: citations must be to reliable published sources; a self-published directory is weak as a Wikipedia source and adding one's own links is a conflict of interest. Better path: the derived reports get cited by trade press, which Wikipedia editors may then use. Do not spam Wikipedia.
- Embeddable assets: per-country or per-ATS widgets/tables with attribution links can earn links but should not be forced (Google's link spam policy covers widget links with keyword-rich anchors; keep embeds with plain brand anchors, ideally nofollow-optional).

### Gaps
- I found no peer-reviewed or controlled study quantifying link yield from open datasets, awesome lists, or correction forms. These recommendations are practitioner consensus.
- I did not re-fetch Google's link spam policy text on widget links in this session (it is part of the same spam policies page).

## 5. Technical factors for a static directory

### Takeaway
A static site on GitHub Pages behind Cloudflare is already fast; the main technical risks are very large HTML hub pages (Googlebot reads only about the first 2 MB of HTML), duplicate URL variants (Markdown twins, http vs https, trailing slashes, redirect stubs), and shallow internal linking to the noindexed or orphaned entity pages.

### Cited Findings
- Official doc change (Feb 2026, secondary coverage): Googlebot for Search fetches only the first 2 MB of an HTML file (uncompressed, including headers) and stops at the cutoff; PDFs 64 MB; other Google crawlers default 15 MB. Mueller called it a documentation clarification, not a behavior change; later wording says crawlers "may have a smaller size limit, for example 2MB." [Search Engine Journal](https://www.searchenginejournal.com/google-updates-googlebot-file-size-limit-docs); [DebugBear](https://debugbear.com/blog/googlebot-crawler-file-size-limit); [Search Engine Roundtable](https://www.seroundtable.com/page-weight-google-file-size-limits-41147.html)
- Official: technical basics for AI features are the same as Search: crawlable content, internal links, page experience, semantic HTML, reduced duplicate content. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features); [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Official: IndexNow allows batch submission of changed URLs to Bing and others (not Google). [IndexNow FAQ](https://www.indexnow.org/faq)
- Background (not re-verified this session): Google recommends giving each paginated page its own URL with crawlable `<a href>` links, not canonicalizing page 2+ to page 1, and notes rel=next/prev is no longer used as an indexing signal. [Google pagination docs](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading). Google treats sitemaps' lastmod as useful only if consistently accurate. [Google sitemaps docs](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- Background (not re-verified this session): GitHub Pages cannot issue server-side 301s for arbitrary paths; meta-refresh stubs are treated by Google like redirects when instant, but a Cloudflare redirect rule (true 301) is cleaner. [Google redirects docs](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

### Inferences
- Measure the largest hub pages (e.g., all-boards list, big countries like US/UK, "API access" hubs). If any exceed roughly 1.5 MB uncompressed HTML, paginate or split by sub-facet, and make sure the most important links appear early in the HTML.
- Internal linking: every indexed entity page should be reachable within 2 to 3 clicks from home via hubs; add contextual cross-links (ATS page lists multiposters and job boards it integrates with, and vice versa). These integration links mirror the demand already visible ("job multiposter for <ats>").
- Noindexed thin pages should remain "noindex, follow" and linked, so they pass equity and can be re-evaluated when promoted.
- Enforce https at Cloudflare ("Always Use HTTPS" plus HSTS), one canonical host (www or apex) and consistent trailing slash; self-referencing canonicals on every indexable page; Markdown twins and JSON excluded from indexing (X-Robots-Tag via Cloudflare rule) or canonicalized to the HTML page using a Link header.
- Sitemap: include only indexable canonical URLs, update lastmod only when facts actually change, and split by type (boards, ATS, hubs) so Search Console coverage can be read per segment. Ping IndexNow on each deploy for changed URLs.
- Core Web Vitals: static HTML on Cloudflare should pass; check INP if hub pages ship large client-side filtering scripts, and CLS from late-loading tables.

### Gaps
- Did not retrieve current Google pagination or redirect doc text this session; those points are labeled as background.
- No data on whether Cloudflare's default AI-bot blocking is active on this account; needs a manual check of the dashboard.

## 6. Measurement cadence, metrics, and new-domain ranking timelines

### Takeaway
One week of data (246 impressions, average position 32) is normal for a two-week-old domain. Industry data suggests most new pages take months to reach page one, and only a small share of new pages reach the top 10 in a year, so judge progress over 3 to 6 month windows with segment-level leading indicators, not weekly clicks.

### Cited Findings
- Industry (Ahrefs, May 2025, 1M random URLs): only 1.74% reached the top 10 within a year (down from 5.7% in 2017); the average #1 page is about 5 years old. [Ahrefs](https://ahrefs.com/blog/how-long-does-it-take-to-rank/) (figures partly via secondary summaries such as [Crowdo](https://crowdo.net/blog/how-long-to-rank-in-google-2025/))
- Official: AI Overview and AI Mode traffic is included in Search Console Performance "Web"; Google points to a Generative AI performance report in Search Console; recrawl after changes "can take days to months." [Google AI features](https://developers.google.com/search/docs/appearance/ai-features); [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Official: Bing Webmaster Tools AI Performance report shows Copilot citations and grounding queries, data within about 24 hours of setup, no click data. [Practical Ecommerce](https://www.practicalecommerce.com/bings-improved-ai-performance-section)
- Official: ChatGPT referrals tagged utm_source=chatgpt.com. [OpenAI publishers FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)
- Industry: rule-of-thumb 3 to 6 or 6 to 12 month timelines circulate but are not from controlled studies; long-tail low-competition queries can rank within weeks. [Whitehat SEO](https://whitehat-seo.co.uk/blog/how-long-does-it-take-to-rank-on-google)

### Inferences
- Cadence: weekly check of indexing (Pages report, sitemap submitted vs indexed per segment) and errors; monthly review of queries/pages; quarterly decisions on promoting or consolidating thin pages and on content investments. Avoid reacting to week-to-week noise.
- Leading indicators for months 1 to 3: share of sitemap URLs indexed per segment (target near 100% of the ~190 board pages plus hubs), impressions per indexed page, number of distinct queries, count of queries with average position under 20, Bing AI Performance citations and grounding queries, ChatGPT/Perplexity referral sessions, referring domains and dataset downloads/API calls.
- Lagging indicators for months 3 to 12: clicks, CTR on integration/API query clusters, top-10 query count, and links earned from reports.
- Segment by page type (board, ATS, multiposter, country hub, API-access hub) using sitemap splits and URL path filters; the early demand suggests ATS/integration/API pages deserve the first enrichment effort.
- Set expectations: with a new domain, position ~32 average after one week is a starting baseline; meaningful click growth is more likely after several months and authority-building.

### Gaps
- No authoritative Google statement on a "sandbox" or typical new-domain timeline; Google does not publish one.
- No benchmark found for normal impressions/clicks for a ~200-page new directory.
