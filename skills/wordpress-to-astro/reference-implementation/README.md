# Reference implementation

Working scripts and Astro files from a real migration (a WordPress site on Roots Sage/Acorn with Yoast, Gravity Forms, Livewire, WP Rocket and Cloudflare). They are **examples to copy and adapt, not authoritative**, and have only been run on that one site. Use them if they save time; otherwise write the equivalent into the project's `scripts/` as the phase files describe.

## Set up

Copy `scripts/` into the project's `scripts/` and `astro/` over the project's Astro scaffold (the files are additive: layout, components, data loader, route, 404). Then:

```bash
export SITE_ORIGIN=https://example.com      # production origin, no trailing slash
export CRAWLER_USER="Your Name <you@example.com>"   # the identity the crawler sends (see policies/crawler-identity-and-scope.md)
```

Python 3.9+ (standard library only) and Node 18+ are assumed. The crawl cache lives in `.crawl-cache/` (not committed).

## What is in here

| File | Purpose | How generic |
|---|---|---|
| `scripts/crawl.py` | polite breadth-first crawler, caches HTML and headers, records redirect chains; skips API/feed `<link>` targets | generic |
| `scripts/stamp.py` | version stamps and the generated-file manifest (`policies/updating-a-run.md`): `write`/`write_json`/`clean` for generators, plus `adopt`, `status`, `complete`, `crawled` commands | generic; `SKILL_VERSION` must match `SKILL.md` |
| `scripts/lib.py` | shared helpers: load cached pages, split a page into head/header/main/footer/tail, mask volatile tokens, normalise for comparison | splitter assumes `<header>`, `<main>`, `<footer>` landmarks; masks are for Livewire, Gravity Forms and WordPress nonces |
| `scripts/deopt.py` | reverses WP Rocket and Cloudflare output (lazy-load placeholders, injected attributes/scripts, email obfuscation) | **site-specific**: one function per hosting layer; rewrite for the stack found in Phase 0 |
| `scripts/build_source.py` | decomposes cached pages into shared fragments, per-page records and verbatim `<main>` files, with nav-state patches and the `TODO(manual)` form comments | structure generic; fragment boundaries and the Livewire path token are site-specific |
| `scripts/listings.py` | maps query-string listing variants (`?page=`, `?course_category=`) to internal static paths | **site-specific** parameter names |
| `scripts/verify.py`, `verify_batches.py` | the comparison contract: build, reverse, mask, normalise, diff every page; batches keep disk use low | generic given `deopt.py` and the masks |
| `scripts/seo_inventory.py`, `seo_check.py` | per-page SEO facts (title, description, canonical, robots, OG, Twitter, JSON-LD hash, headings), verbatim copies of robots/sitemaps/feeds, and the check against the build | generic; the list of static files to copy is site-specific |
| `scripts/assets_inventory.py`, `download_assets.py`, `assets_report.py`, `check_assets.py` | find every first-party asset (markup, CSS, JSON-LD, sitemaps, inline text), download to the same URL path, record ownership and content-type mismatches, prove they resolve in the build | generic (path prefixes `app`, `wp`, `wp-content`, `wp-includes`) |
| `scripts/a11y_audit.py` | static accessibility audit (alt, labels, empty links/buttons, headings, duplicate ids, ARIA misuse, focus outlines, indicative contrast) | generic; contrast reads Tailwind-style colour tokens from the theme CSS |
| `scripts/errors_audit.py` | 4xx/5xx links, redirects, mixed content, fragments, canonicals, sitemap failures | generic |
| `scripts/css_analyse.mjs` | parses stylesheets with postcss: rules, at-rules, `url()` references, exact duplicate rules | generic (needs `postcss`, installed with Astro) |
| `scripts/review-server.mjs` | the local review server specified in `reference/local-review.md` | generic |
| `scripts/visual-fingerprint.js` | per-region height measurement, run in the browser on the live and local pages (`reference/visual-comparison.md`) | generic |
| `astro/` | layout, `Head`, `SeoMeta`, `Header`, `Footer`, `TailScripts` components, data loader that reads records from disk, one dynamic route, the 404, `astro.config.mjs` (static, trailing slashes, copies stylesheets to their original URLs), and the client search/filter/load-more script | route and components generic; `site-search.js` selectors are specific to the Livewire markup of that site |

## Relation to the tooling contract

`reference/tooling-contract.md` describes the commands tooling should expose (`crawl`, `analyse`, `extract`, `build`, `verify`, `seo-check`, `asset-check`, `review`, `visual`). These scripts are the first pass at it and still carry some site-specific constants; making them fully config-driven (reading `wordpress-to-astro.config.json`) and testing them on further sites is the next step.

## Deliberately not included

Report writers (`accessibility-report.md`, `errors.md`, the content map and so on), the CSS organiser, the redirect and rewrite data builders, and the listing-variant and extra-page fetchers. Their narrative and parameters are specific to the site they were written for; the phase files say what each document must contain.

## Conventions worth keeping

- Generators write through `stamp.py` and clean with `stamp.clean()`, so a re-run never overwrites a file edited by hand (the regenerated copy lands beside it as `<name>.updated`).
- Generated data in `src/data/pages/`, hand-maintained data (`redirects.json`, `rewrites.json`, content-type overrides) beside it: a generator may only delete what it generates.
- Page content is read from disk at build time (`fs`), not bundled, so large sites build with little memory or disk.
- `npm run extract | build | verify | review` as the standard commands.
