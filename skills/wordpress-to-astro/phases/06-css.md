# Phase 6: CSS

*Stage 3 (Build), after Phase 5. Small enough to be done in the same working session as Phase 5.*

- Collect all stylesheets and inline style blocks served by the site.
- **Default: keep each stylesheet byte-for-byte and serve it at its original URL**, so no `<link>` markup changes. Organise the sources under `src/styles/` by origin (theme, per plugin), add a manifest (original URL, role, size, hash, pages using it) and publish them at the original paths. Merging, splitting or de-duplicating files is not safe to do silently: it changes `<head>` elements or the cascade, so do it only if the user chose consolidation in Phase 0, and log it in `docs/deviations.md`.
- Do not remove duplicate rules unless removal is provably safe (the later copy cannot alter the cascade). When unsure, keep it and note the count in `docs/deviations.md`.
- Do not change selectors, specificity, rule order effects, or values.
- Keep the cascade order the original pages loaded stylesheets in. Record the load order per template, including inline `<style>` blocks.
- Do not rename classes or restructure to a methodology.
- Record the assets referenced from CSS (`url()` paths, relative to each stylesheet) for Phase 9.
