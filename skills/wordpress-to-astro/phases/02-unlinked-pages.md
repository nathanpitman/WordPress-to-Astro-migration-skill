# Phase 2: Find unlinked public pages

Look for publicly accessible pages not reachable through internal links, such as standalone landing pages.

- Use web search with `site:<domain>` queries (vary by topic words, `inurl:`, and common landing-page terms), and compare results with the crawl. Search tools often ignore the `site:` operator; if results are third-party listings, fall back to plain-language queries naming distinctive content and keep only results on the domain. Record which method worked.
- Check sitemaps for URLs that the crawl did not reach. On many sites this is the largest source: listings that load more through JavaScript expose only a subset of entries in static HTML.
- Check the Internet Archive's public index of the domain (for example through web fetch on its CDX search) as another source. Treat results only as leads: keep a URL only if it is currently live and returns 200.
- Add each new page to `docs/site-structure.md` under an "Unlinked pages" section with the source that revealed it. Fetch and cache them like any other page.
- Do not guess at private or admin paths, do not request the WordPress admin URLs listed in `policies/crawler-identity-and-scope.md`, and do not probe for hidden content. Ignore search results on subdomains (list them under "Subdomains found" instead).
