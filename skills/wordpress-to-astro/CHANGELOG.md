# wordpress-to-astro changelog

One entry per version, newest first. Every change to a phase, policy or script that alters what a run produces needs a line here, naming the phases it affects, so an existing migration can be updated (`policies/updating-a-run.md`).

Format:

```
## <version> (YYYY-MM-DD) <MAJOR|MINOR|PATCH>
Affects phases: <numbers, or "none">
- <phase N>: <what changed and why it matters, in plain English>
Output effect: <none | docs only | source and rendered output may differ>
New decisions: <questions or config keys added, with defaults, or "none">
```

## 2.0.0 (2026-10-03) MAJOR
Affects phases: 1, 5, 7, 9, 10, 11 (and 8 where the site has query-string listings)
- Reference scripts rewritten for a typical WordPress site and driven by `wordpress-to-astro.config.json` instead of constants from one site. New `config.py`; keys are listed in `policies/run-state.md`.
- Phase 1: `crawl.py` caches `robots.txt`, finds sitemaps from it (or the usual locations, following indexes), honours its rules, and keeps sitemaps, their stylesheets and feeds verbatim; the crawl cache now lives in `.crawl-cache/` (it was written next to the scripts before).
- Phase 5: `build_source.py` stores five regions (pre, header, mid, post, footer) as a base plus per-page patches (it assumed pre/mid/post were identical on every page), keeps SEO items in their original position as raw markup (any SEO plugin), records `<html>` and `<body>` attributes (the language was hard-coded), names templates from the body classes, and puts the form comment above every non-search form. `src/data` records changed shape: regenerate them and the Astro components together.
- Phase 5: `deopt.py` is a registry of hosting-layer reversals (`wp-rocket`, `cloudflare`) chosen by `hostingLayers`; `lib.py` mask sets are chosen by `volatileTokens`/`masks`. The Livewire-specific masks, header path token and search script are gone.
- Phase 7: SEO facts are read with an HTML parser, so Rank Math, AIOSEO and SEOPress heads work as well as Yoast's.
- Phases 8, 9, 10, 11: query-string listings come from `listings` in the config (core `/page/N/` needs nothing); asset prefixes from `assets.prefixes`; the contrast check reads WordPress colour presets as well as Tailwind-style tokens; the errors audit reads whichever sitemaps were cached.
- `public/js/site-search.js` is now a small Pagefind-backed replacement for core `?s=` search and is only emitted if the file exists.
- New `reference-implementation/test-fixture/` (synthetic stock-WordPress site) and `smoke.sh`.
- Form comment no longer names a CRM; docs and examples no longer describe any one site.
Output effect: source and rendered output may differ (record format changed; re-run Phases 1, 5 and 7 to regenerate)
New decisions: none

## 1.0.0 (baseline) MAJOR
Affects phases: none (first stamped version)
- Introduces version stamping, `skillVersion` and per-phase `ranWith` in `docs/run-state.json`, and the update workflow.
- Reference scripts: new `stamp.py`; `build_source.py`, `assets_report.py`, `download_assets.py` and `seo_inventory.py` write through it so hand edits survive a re-run; `crawl.py`, `a11y_audit.py` and `errors_audit.py` record that they ran.
- Runs created before this version have no stamp and are treated as version 0.
Output effect: none
New decisions: none
