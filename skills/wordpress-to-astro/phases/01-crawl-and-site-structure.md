# Phase 1: Crawl and site structure

1. Fetch the homepage, `robots.txt`, and every sitemap referenced (`sitemap.xml`, `wp-sitemap.xml`, sitemap indexes, Yoast/RankMath variants).
2. Crawl all internal links breadth-first (within the crawl scope above), including links in nav, footer, body content, pagination, and category/tag/author archives. Record the final URL, status code, redirect chain, canonical URL, and page title for each. Crawler hygiene:
   - follow `<a href>` links and pagination only. **Do not queue `<link rel="alternate">` targets** (oEmbed, REST, feeds): they multiply into thousands of API URLs. Record them as references instead
   - percent-encode paths before requesting (emoji or non-ASCII slugs), and de-duplicate by final URL
   - record who issued each redirect when the response says (for example `X-Redirect-By: Redirection` versus `WordPress`), since that separates configured rules from core behaviour
   - treat CDN-injected links such as Cloudflare's bare `/cdn-cgi/l/email-protection` as artefacts, not pages or errors
3. Normalise URLs without changing them. Record trailing-slash behaviour, query-string usage and case sensitivity exactly as the site does it. These become the Astro routing rules.
4. Write `docs/site-structure.md` as a tree of the full site, marking each URL as: static page, dynamic entry (belongs to a content group), archive/listing, or utility page. Note the source of discovery for each (link, sitemap, search).
5. Write `docs/url-patterns.md` listing every URL pattern (e.g. `/blog/{slug}/`, `/category/{slug}/page/{n}/`, `?s=` search, filter query strings, `?page=N`) and how Astro must serve it to match exactly. Include redirects found, to be reproduced at cutover. Be careful here: many sites paginate and filter through **query strings handled by JavaScript components**, not `/page/N/` paths, and some `/page/N/` URLs return 200 with page-1 content. Test the patterns you find with real requests before documenting them.
6. **Catalogue hard-coded internal links.** While reading each cached page, find every `<a href>` whose value contains the site's own domain instead of being relative. Count `http://` and `https://`, `www` and non-`www`, and protocol-relative (`//domain/`) forms as the same domain. Record each one in `docs/recommended-fixes.md` under "Hard-coded internal links":
   - the full href exactly as found, and the relative path it would become
   - the link text and the page(s) it appears on
   - where it lives: a shared region (header, nav, footer, sidebar), a template, or entry/body content
   - grouped by pattern and by shared region, so a link repeated across the whole site appears once with a page count, not once per page
   - a recommended fix for each group (for example "convert to a root-relative path"), plus a note that absolute links will point at the live site, not a staging copy, while the Astro site is tested on another host

   **Do not fix them.** Reproduce every one exactly as served in the Astro source. Scan pages added in Phase 2 as well, and update the list at that gate.

   While scanning, also look for **leaked non-production hostnames** in any link, script or style (`.test`, `.local`, `localhost`, `staging.`, `dev.`, an IP address, a `http://` copy of the production host). Record each as a Fix entry, with the page count, and leave it as served.
