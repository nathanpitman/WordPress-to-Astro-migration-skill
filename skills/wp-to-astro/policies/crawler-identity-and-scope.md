# Crawler identity and crawl scope

## Crawler identity


Identify the crawler as the current Claude Code user, never anonymously and never as a browser.

- Use the user's name or account email as Claude Code provides it in the session context. Do not guess or invent one. If none is available, ask the user once what name or email to use.
- Send it as the User-Agent on every request: `wp-to-astro (Claude Code; run by <user>; crawling <domain>)`.
- Set it wherever the tool allows (for example `curl -A` in the shell). If a tool, such as web fetch, does not let you set the User-Agent, say so in the introduction and note it in `docs/site-structure.md`.
- Never disguise the crawler or rotate identities.


## Crawl scope

- Crawl only the exact host given in `$ARGUMENTS`. Treat `www` and non-`www` forms of that host as the same site.
- **Subdomains are out of scope until the user says otherwise.** When one is discovered (in links, redirects, sitemaps, canonical tags, search results, or asset URLs such as a CDN), do not request anything from it. List each one in `docs/site-structure.md` under "Subdomains found", with where it was seen, and ask at that phase's review gate whether to include it. Include a subdomain only after an explicit yes.
- **Ignore WordPress admin and system URLs.** Never request them, and do not list them as pages or as errors: `/wp-admin/` (including `admin-ajax.php`), `/wp-login.php`, `/wp-signup.php`, `/wp-activate.php`, `/xmlrpc.php`, `/wp-cron.php` and `/wp-trackback.php`, including any query-string variants. If a page links to one (a login link in the footer, say), leave the markup exactly as served and do not follow the link. If forms or search depend on `admin-ajax.php`, add a Review entry to `docs/recommended-fixes.md`, since that behaviour will need replacing. Asset files under `wp-content/` and `wp-includes/` are not admin URLs and are handled in Phase 9 as normal.
