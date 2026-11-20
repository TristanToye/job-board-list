# Cloudflare settings for jobboardlist.com

GitHub Pages cannot send real redirects or custom headers, so these rules live in Cloudflare (zone jobboardlist.com). All of them work on the Free plan. Do not change DNS records or the SSL mode.

## 1. Old ATS addresses: one wildcard redirect

Old addresses such as `/ats/lever/` are small pages that point to `/boards/lever/`. Google is showing some of them in results, so they should return a real 301.

Rules > Redirect Rules > Create rule (or "Single Redirects"):
- Name: `Old ATS addresses`
- If incoming requests match: Wildcard pattern
  - Request URL: `https://jobboardlist.com/ats/*/`
- Then: Target URL `https://jobboardlist.com/boards/${1}/`, status 301, preserve query string on.

`/ats/` itself (the ATS comparison page) does not match this pattern and must keep working.

## 2. One hop from www to the main address

Today `https://www.jobboardlist.com` goes to `http://jobboardlist.com` and only then to `https://`.

Rules > Redirect Rules > Create rule:
- Name: `www to root`
- If incoming requests match: Wildcard pattern
  - Request URL: `*://www.jobboardlist.com/*`
- Then: Target URL `https://jobboardlist.com/${2}`, status 301, preserve query string on.

(Cloudflare also offers this as the "Redirect from WWW to root" template.)

## 3. Keep data files out of search results

The raw CSV download shows in Google results. Markdown copies and JSON files are for programs and AI tools and should not be indexed. They stay readable.

Rules > Transform Rules > Modify Response Header > Create rule:
- Name: `Noindex data files`
- Custom filter expression:
  `ends_with(http.request.uri.path, ".csv") or ends_with(http.request.uri.path, ".md") or ends_with(http.request.uri.path, ".json") or http.request.uri.path eq "/llms-full.txt"`
- Then: Set static, header name `X-Robots-Tag`, value `noindex`.

## 4. Let search and AI-search crawlers in

Security > Bots and AI Crawl Control:
- Googlebot, Bingbot, Applebot, OAI-SearchBot (ChatGPT search) and PerplexityBot should be allowed.
- If "Block AI bots" or "Manage robots.txt" is on, make sure it does not block those search crawlers and does not rewrite the site's robots.txt.
- Blocking training-only crawlers (for example GPTBot, CCBot) is a separate choice.

## 5. Optional: old language and country code addresses

`ops/cloudflare-bulk-redirects.csv` also lists 72 old language and country code addresses (for example `/languages/fr/` to `/languages/french/`). They get almost no traffic and already point to the right page, so this is optional. To do it: Rules > Redirect Rules > Bulk Redirects, create a list, upload the CSV, then create a Bulk Redirect Rule using the list. Regenerate the file with `python3 scripts/make_redirects.py`.

## 6. Bing Webmaster Tools

bing.com/webmasters, sign in, "Import from Google Search Console". IndexNow pings run with `python3 scripts/indexnow.py` after a deploy (key file is published at the site root).

## Check after setup

- `curl -sI https://jobboardlist.com/ats/lever/` shows `301` and `location: https://jobboardlist.com/boards/lever/`
- `curl -sI https://jobboardlist.com/ats/` shows `200`
- `curl -sI https://www.jobboardlist.com/boards/indeed/` shows `301` and `location: https://jobboardlist.com/boards/indeed/`
- `curl -sI https://jobboardlist.com/downloads/job_boards.csv` shows `x-robots-tag: noindex`
- `curl -sI https://jobboardlist.com/boards/indeed/` shows `200` and no `x-robots-tag`
