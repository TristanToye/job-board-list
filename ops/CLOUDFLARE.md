# Cloudflare settings for jobboardlist.com

GitHub Pages cannot send real redirects or custom headers, so these few rules live in Cloudflare. Each one takes a few minutes in the dashboard. Regenerate the redirect list with `python3 scripts/make_redirects.py` after a build if more stub pages appear.

## 1. Real 301 redirects for old addresses (Bulk Redirects)

Old addresses such as `/ats/lever/` still exist as small pages that point to the new address. Search engines treat a real 301 better, and `/ats/lever/` is already showing up in Google results.

1. Rules > Redirect Rules > Bulk Redirects > Create Bulk Redirect List.
2. Name it `jobboardlist-moved`, then upload `ops/cloudflare-bulk-redirects.csv` (columns: source, target, status 301).
3. Create a Bulk Redirect Rule that uses that list. Leave "Preserve query string" on.

## 2. One hop from www to the main address

Today `https://www.jobboardlist.com` goes to `http://jobboardlist.com` and only then to `https://`. One hop is cleaner.

Rules > Redirect Rules > Create rule:
- When incoming requests match: Hostname equals `www.jobboardlist.com`
- Then: Dynamic redirect to `concat("https://jobboardlist.com", http.request.uri.path)`, status 301, preserve query string.

## 3. Keep data files out of search results

The raw CSV download was showing in Google results. The Markdown copies and JSON files are for programs and AI tools, not for search results, so they should not be indexed. They stay fully readable.

Rules > Transform Rules > Modify Response Header > Create rule:
- When incoming requests match (custom filter expression):
  `ends_with(http.request.uri.path, ".csv") or ends_with(http.request.uri.path, ".md") or ends_with(http.request.uri.path, ".json") or ends_with(http.request.uri.path, "llms-full.txt")`
- Then: Set static header `X-Robots-Tag` to `noindex`

## 4. Let search and AI-search crawlers in

Security > Bots, and AI Crawl Control (or Bot Fight Mode settings):
- Make sure Googlebot, Bingbot, OAI-SearchBot (ChatGPT search), PerplexityBot and Applebot are allowed. Blocking training crawlers is a separate choice; the site's robots.txt currently allows search and AI input and says nothing about training.
- If "Block AI bots" is on, check its list does not include the search crawlers above.

## 5. Bing Webmaster Tools and IndexNow

1. Go to bing.com/webmasters, sign in, and choose "Import from Google Search Console". This verifies the site and imports the sitemap in one step.
2. The site publishes an IndexNow key file (see `docs/` for a file named after the key). After each deploy, `python3 scripts/indexnow.py` tells Bing and other IndexNow engines which pages changed.
3. Bing Webmaster Tools has an AI Performance report that shows citations in Copilot answers. Check it monthly.
