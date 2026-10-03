# Local review server (`npm run review`)

Purpose: let a person open the migrated site on their own machine and review it as if it were deployed, without the built files being altered and without the review touching the live site or its analytics.

## Why it is needed

The built site keeps the markup exactly as the old site served it. That markup contains absolute URLs to the production origin (stylesheets, scripts, images, internal links, JSON-LD). Served as-is from a local static server, it would load assets from, and send clicks to, the **live** site, so the "local" review would silently depend on production. Query-string listings, redirects, content types and the 404 also need host-level behaviour that a plain static server (and `astro dev` / `astro preview`) does not provide.

## Requirements

1. **Serve `dist/`** on `localhost` (default port from `PORT`, otherwise a fixed uncommon port) using only Node, so no extra dependency is needed.
2. **Localise the origin at serve time only.** In text responses (HTML, CSS, JS, JSON, XML, feeds, sitemaps) replace the production origin, including `http`, protocol-relative (`//host`) and JSON-escaped (`https:\/\/host`) forms, with the local address. Never write the rewritten text to disk. Read the origin from the project's configured `site` or `SITE_ORIGIN`.
3. **Apply the host-level data the build produces:**
   - query-string rewrites (`src/data/rewrites.json`): same path, exact query parameters, destination file
   - redirects (`src/data/redirects.json`), plus the trailing-slash redirect for directory pages
   - content-type overrides for files whose type differs from their extension
   - the themed 404 page with status 404 for unknown URLs
   - directory index fallbacks (`index.html`, or `index.xml` for feeds)
4. **Block third-party calls by default** with a `Content-Security-Policy` response header (allow `self`, inline scripts and styles; deny external scripts, frames and connections). Reviewing must not send hits to analytics, tag managers, chat widgets or captcha services. Provide an opt-out (for example `REVIEW_ALLOW_THIRD_PARTY=1`) and print which mode is in force.
5. **Print what it is doing** at start-up: address, the origin being rewritten, and the third-party mode.
6. **Do not cache** (`Cache-Control: no-store`), so a rebuild shows immediately.
7. **Fail clearly** if `dist/` does not exist (tell the user to run `npm run build`).

## What a reviewer should be told

- Server-side behaviour that existed on the old site does not exist here (form submission, search or listing endpoints, API links in `<head>`); list the known ones.
- Anything replaced by the approved client script behaves differently (see `docs/deviations.md`).
- Missing-but-expected requests (for example a removed script) are expected and are listed in `docs/errors.md`.

A working implementation from a real run is in `reference-implementation/scripts/review-server.mjs`.
