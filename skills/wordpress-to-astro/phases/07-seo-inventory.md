# Phase 7: SEO inventory

*Split across stages: the inventory (facts, copied files, redirects data, inconsistencies) is Stage 2; the check against the build (the SEO check) is Stage 4.*

Write `docs/seo-inventory.md`, and ensure every item below is carried across unchanged:

- Titles, meta descriptions, canonical tags, robots directives, hreflang
- Open Graph and Twitter markup
- **All JSON-LD** (and microdata/RDFa if present), byte-for-byte per page, including `@graph` structures from SEO plugins. Prove it by comparing a hash of every JSON-LD element between the original and the built page
- Sitemaps (reproduce the same URLs and structure), `robots.txt`, RSS/Atom feeds. Copy them verbatim, note that they are snapshots (with `lastmod` values from the old system) that must be regenerated after cutover, and record whether feeds are advertised in `<head>`
- **Modified dates come from content, never from the build.** When the sitemap is regenerated, each URL's `lastmod` is the date its content last changed significantly (main text, structured data or links), carried over from the old sitemap and Phase 3 dates, not the build or deploy time. The same applies to JSON-LD `dateModified`, `article:modified_time` and visible "updated" dates. A migration that keeps the content the same changes none of these dates. Google uses `lastmod` only while it is consistently accurate, so stamping every URL with the build time tells it the whole site changed and teaches it to ignore the field. Whitespace or line changes in the markup are not significant changes. Record in the inventory where each page's modified date comes from
- Redirects and status behaviours to reproduce at cutover, with the source of each when known, written as machine-readable data (`src/data/redirects.json`) as well as in the doc
- **HTTP-level signals markup cannot carry** (for example `X-Robots-Tag` on sitemaps and `robots.txt`, `Link` headers, security headers): list them as host configuration to apply, per the platform decision in Phase 0
- Per-page heading outline, for comparison after migration
- Inconsistencies, recorded not fixed: noindex pages that are in the sitemap, canonicals pointing at noindex pages, pages without meta descriptions, duplicate titles, invalid JSON-LD

Write a small SEO check that compares the built pages with this inventory and re-run it with the verifier.
