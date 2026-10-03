# Phase 9: Images and assets

*Stage 3 (Build), after CSS and before listings, so the local review is self-contained as early as possible. The asset check against the build runs again in Stage 4.*

- Explain to the user in plain English that image optimisation is a separate, later improvement (`reference/feature-translation.md`): the migration keeps every image as it is at its current address, and a deliberate optimisation step can follow with a before-and-after check.
- Download images referenced by pages, CSS, and meta tags (including OG images, favicons and JSON-LD images), plus the first-party scripts, fonts and documents the pages and CSS reference. Find references by scanning markup, CSS (resolve `url()` against the stylesheet), JSON-LD, sitemap image entries and inline script text, not just `<img>`.
- **Default: store each file at the same URL path it is served from today** (for example `public/app/uploads/2026/04/x.jpg`), byte-for-byte, so no markup or CSS needs rewriting and indexed image URLs survive. Record each file's ownership in the manifest (global, shared, or the one entry that uses it) so the grouped layout can still be produced.
- Only if the user chose the grouped layout in Phase 0: global images in `public/images/global/`, entry images in `public/images/<content-type>/<entry-slug>/`, with every `src`, `srcset` and CSS `url()` rewritten and each rewrite pattern logged in `docs/deviations.md`.
- Preserve original filenames, and keep original size variants if the markup references them (`srcset`, `sizes`). Do not optimise, convert or resize.
- Keep a manifest of original URL, local file, status, size, hash, content type, references and ownership (a data file; summarise it in `docs/assets.md`).
- **Check the real file type against the extension and the served `Content-Type`.** Sites that convert images to WebP can serve WebP bytes at `.jpg` or `.png` URLs. Keep the bytes as served and record the paths that need a content-type override at the host.
- After the build, verify that every first-party asset URL found in the built HTML and CSS exists in the output at the same path. Report the number checked and the number missing.
- Do not download from subdomains (including CDN hosts) that the user has not approved. List them under "Subdomains found" and ask at the review gate. Third-party scripts stay as external references.
- Download fonts and other static assets referenced by CSS the same way.
