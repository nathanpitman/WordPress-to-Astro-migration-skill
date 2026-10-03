# Phase 11: Errors (record only)

*Stage 2 (Analyse) for the errors that exist in the original; the items that need the build (built-site asset result, known cutover breakages, 404 capture) are finished in Stage 4. `policies/record-only.md` applies.*

Write `docs/errors.md`. Do not attempt to fix or work around any of these.

- 404s and other 4xx/5xx internal links, with the linking page
- Redirect chains and loops, and internal links that point at a redirecting URL (menu links without a trailing slash are common)
- Missing or broken images and assets, with the referencing page
- Mixed-content references, leaked non-production hostnames, broken fragment links, sitemap URLs that fail, and canonical tags pointing to non-200 URLs
- Links whose href is clearly malformed (for example link text used as the URL)
- **Known cutover breakages:** things that work on WordPress today and will fail on a static host (server-side endpoints referenced in markup, form submission, JavaScript component endpoints, WordPress API links in `<head>`). These are not defects of the old site; list them separately
- Anything that was only a crawler artefact (CDN-injected links), explained rather than counted as an error

Capture the site's themed 404 page here (it is one of the additive artefacts approved in Phase 0) and emit it as the host's 404 document.
