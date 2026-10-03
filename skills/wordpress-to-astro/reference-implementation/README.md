# Reference implementation

Scripts and Astro files for the commands in `reference/tooling-contract.md`, written for a **typical WordPress site**: a block or popular classic theme, core posts, pages, categories and authors, core sitemaps or an SEO plugin's, core `/page/N/` pagination, and the usual form, cache and CDN plugins. They are **examples to copy and adapt, not authoritative**. They have been exercised end to end only on a synthetic stock-WordPress site (`test-fixture/`), not on a range of real sites, so expect to adjust them for the stack found in Phase 0. Use them if they save time; otherwise write the equivalent into the project's `scripts/` as the phase files describe.

## Set up

Copy `scripts/` into the project's `scripts/` and `astro/` over the project's Astro scaffold (the files are additive: layout, components, data loader, route, 404). Put the site's settings in `wordpress-to-astro.config.json` at the project root (`policies/run-state.md` lists the keys), and set:

```bash
export CRAWLER_USER="Your Name <you@example.com>"   # the identity the crawler sends (see policies/crawler-identity-and-scope.md)
export SITE_ORIGIN=https://example.com             # optional if "origin" is in the config
```

Python 3.9+ (standard library only) and Node 18+ are assumed. The crawl cache lives in `.crawl-cache/` (not committed).

A minimal config for a site with no cache or CDN layer to reverse and only core pagination:

```json
{ "origin": "https://example.com", "hostingLayers": [] }
```

## What is in here

| File | Purpose | What is site-dependent |
|---|---|---|
| `scripts/config.py` | reads `wordpress-to-astro.config.json`, supplies defaults, builds the crawler's User-Agent | nothing; this is where every setting below is read |
| `scripts/crawl.py` | polite breadth-first crawler: reads `robots.txt` (honours its rules for `*`), follows every sitemap and sitemap index it names (or the usual locations), caches HTML, headers and redirect chains, keeps robots/sitemaps/feeds verbatim, skips API and feed targets | nothing site-specific; `crawl.delaySeconds`, `crawl.probes` |
| `scripts/stamp.py` | version stamps and the generated-file manifest (`policies/updating-a-run.md`): `write`/`write_json`/`clean` for generators, plus `adopt`, `status`, `complete`, `crawled` commands | `SKILL_VERSION` must match `SKILL.md` |
| `scripts/lib.py` | loads cached pages; splits a page at its `<header>`, `<main>` and `<footer>` landmarks; masks per-render values; normalises for comparison | the splitter needs those three landmarks (all current block themes and most classic themes have them); mask sets are chosen by `volatileTokens` (`wp-nonce`, `gravityforms-state`) and extended by `masks` |
| `scripts/deopt.py` | reverses hosting-layer output so the markup compared is the application's own | one function per layer in `LAYERS`: `cloudflare` and `wp-rocket` are included; add one for LiteSpeed Cache, W3 Total Cache, Autoptimize or whatever Phase 0 finds, then name it in `hostingLayers` |
| `scripts/build_source.py` | decomposes cached pages into five shared regions with per-page patches, shared head and tail fragments, per-page records (SEO items kept in place, `<html>` and `<body>` attributes, template name from the body classes) and verbatim `<main>` files, with a `TODO(manual)` comment above each data-entry form | `templates` to name custom post types; `skipFormRoles` |
| `scripts/listings.py` | maps query-string listing variants to internal static paths | only for listings driven by `?param=` (plugins, custom code): declare them under `listings`. Core `/page/N/` and archive paths are ordinary pages and need nothing |
| `scripts/verify.py`, `verify_batches.py` | the comparison contract: build, reverse, mask, normalise, diff every page; batches keep disk use low | none beyond `deopt` and the masks |
| `scripts/seo_inventory.py`, `seo_check.py` | per-page SEO facts read with an HTML parser (so Yoast, Rank Math, AIOSEO, SEOPress or theme-written heads all work): title, description, canonical, robots, hreflang, Open Graph, Twitter, JSON-LD hash, headings; verbatim copies of robots, sitemaps and feeds; the check against the build | none |
| `scripts/assets_inventory.py`, `download_assets.py`, `assets_report.py`, `check_assets.py` | find every first-party asset (markup, CSS, JSON-LD, sitemaps, inline text), download to the same URL path, record ownership and content-type mismatches, prove they resolve in the build | `assets.prefixes` (default `/wp-content/`, `/wp-includes/`) |
| `scripts/a11y_audit.py` | static accessibility audit (alt, labels, empty links/buttons, headings, duplicate ids, ARIA misuse, focus outlines, indicative contrast) | contrast reads WordPress colour presets (`--wp--preset--color--*`) or Tailwind-style tokens from the stylesheets in `src/styles/`; with neither it skips contrast |
| `scripts/errors_audit.py` | 4xx/5xx links, redirects, mixed content, fragments, canonicals, sitemap failures | none |
| `scripts/css_analyse.mjs` | parses stylesheets with postcss: rules, at-rules, `url()` references, exact duplicate rules | needs `postcss`, installed with Astro |
| `scripts/review-server.mjs` | the local review server specified in `reference/local-review.md` | none |
| `scripts/visual-fingerprint.js` | per-region height measurement, run in the browser on the live and local pages (`reference/visual-comparison.md`) | none |
| `astro/` | layout, `Head`, `SeoMeta`, `Header`, `Footer`, `TailScripts` components, data loader that reads records from disk, one dynamic route, the 404, `astro.config.mjs` (static, trailing slashes, copies stylesheets to their original URLs), and `public/js/site-search.js` | `site-search.js` is an optional Pagefind-backed replacement for core `?s=` search; it is emitted only if the file exists, so delete it unless the user approved it at intake |
| `test-fixture/` | a synthetic stock-WordPress site and `smoke.sh`, which runs the pipeline end to end against it | — |

## Try it

`bash test-fixture/smoke.sh` (from this folder) serves a generated site on localhost, then crawls it, builds it with Astro and checks that every page and every SEO fact comes out identical. It needs Python, Node and network access for `npm install`.

## Relation to the tooling contract

`reference/tooling-contract.md` describes the commands tooling should expose (`crawl`, `analyse`, `extract`, `build`, `verify`, `seo-check`, `asset-check`, `review`, `visual`). These scripts are a first pass at it, driven by `wordpress-to-astro.config.json`. Testing them on more real sites, and adding reversals for more hosting layers, is the next step.

## Deliberately not included

Report writers (`accessibility-report.md`, `errors.md`, the content map and so on), the CSS organiser, the redirect and rewrite data builders, and the listing-variant and extra-page fetchers. Their narrative and parameters depend on the site; the phase files say what each document must contain.

## Conventions worth keeping

- Generators write through `stamp.py` and clean with `stamp.clean()`, so a re-run never overwrites a file edited by hand (the regenerated copy lands beside it as `<name>.updated`).
- Generated data in `src/data/pages/`, hand-maintained data (`redirects.json`, `rewrites.json`, content-type overrides) beside it: a generator may only delete what it generates.
- Page content is read from disk at build time (`fs`), not bundled, so large sites build with little memory or disk.
- `npm run extract | build | verify | review` as the standard commands.
