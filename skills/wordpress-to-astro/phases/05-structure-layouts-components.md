# Phase 5: Page structure, layouts, components

*Stage 3 (Build), first step. Keep the project buildable and run the verifier after every step of the stage.*

1. Compare pages to identify shared regions (header, navigation, footer, global scripts, page wrapper, breadcrumbs, sidebars, CTA blocks, cookie banners) and unique page templates.
2. Document the result in `docs/templates-and-components.md`: each template, which URLs use it, and which components it composes.
3. **Build the verifier first.** Implement the comparison contract from `docs/baseline.md` as a re-runnable script before generating any page: reverse the hosting layers, mask the volatile tokens, collapse whitespace, ignore only the approved additive artefacts, then compare each built page with its cached original and report identical versus differing pages with the first few differences. Run it over all pages in batches (build a subset, compare, delete the output) so it works with little free disk.
4. Build Astro layouts and components from the **verbatim HTML** of the cached pages:
   - Extract shared regions into components exactly as they appear, including inner whitespace-insensitive structure and all attributes.
   - Where a region differs between pages only by state (e.g. current-page nav classes), parameterise the difference without changing the output.
   - Page-specific body content stays in the page or content file as original HTML.
   - Preserve `<head>` order and everything in it: title, meta, canonical, hreflang, Open Graph, Twitter cards, robots meta, preloads, feeds, inline scripts and styles, analytics and tag manager snippets.
   - The exception is anything recorded in `docs/security-findings.md`: leave it out as described in `policies/suspicious-code.md`. These are expected differences in the comparison step below.
   - Make the extraction a script that regenerates only generated files, so the build can be reproduced.
   - **Standard npm scripts, so a reviewer always knows how to run the project:** `extract` (regenerate source from the cache), `build` (Astro build, followed by the search indexer if the site uses one), `verify` (the comparison from step 3), and `review` (the local review server in `reference/local-review.md`). Add `README.md` commands for each at the end of the run (see `phases/12-finishing-and-local-review.md`).
   - Keep the project **buildable at every gate**: `npm install` then `npm run build` must succeed whenever you stop for review, not only at the end.
5. Render every template with Astro and run the verifier. Any difference is either fixed or logged in `docs/deviations.md`. Report the number of pages verified and the number with differences, and say what the contract normalised.
6. **Visual comparison (when a browser tool is available).** Compare a few representative pages on the local review server against the live site, following `reference/visual-comparison.md`: measure each region in view, screenshot and classify every difference as a hosting-layer artefact, a genuine regression (fix it) or a defect of the original (record it). Do not rely on a browser being available; record "not done: requires browser" if not.
