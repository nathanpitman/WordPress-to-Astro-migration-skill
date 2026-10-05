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

## 2.2.0 (2026-10-05) MINOR
Affects phases: none (flow control only; Phase 0 intake and every stage gate)
- New optional `--auto` flag: runs start to finish without stopping for input. Intake questions take their defaults, every gate is passed as "continue" (the checkpoint is still written), decisions take the recommended default and stay open in `docs/decisions.md`. Safe defaults only: subdomains out, suspected malicious code out, no unapproved deviations, forms submitted only with `--submit-forms`. Hard stops (no disk, crawler blocked, missing tool) still halt the run. New `policies/auto-mode.md`; the index leads with an auto-mode summary.
Output effect: none (only how the run is driven; with `--auto` the index gains an auto-mode summary)
New decisions: `options.auto` in `wordpress-to-astro.config.json` (default `false`)

## 2.1.1 (2026-10-05) PATCH
Affects phases: none (Stage 1 smoke slice wording)
- Smoke slice: its throwaway output (per-page extracts, shared fragments, any quick route) goes in a clearly named temporary folder with a `README.txt`, apart from real source, and the Stage 1 checkpoint says so. A reviewer browsing the project is otherwise left to guess whether the slice's layout is the intended structure.
Output effect: none (the slice's scratch folder is named and documented; nothing the later stages produce changes)
New decisions: none

## 2.1.0 (2026-10-04) MINOR
Affects phases: 0, 8 (and the Stage 1 smoke slice, the Stage 3 gate and the Stage 4 verification)
- Phase 8: query-string addresses are now derived from what the page's own controls submit (a browser's serialisation of every form, including empty text inputs and default options, crossed with every option and page index), not from the parameter names noticed in the markup. A form with a filter and a search box always submits both, so a filter click arrives with an empty search value; rewrite rules must exist for those addresses, and a gap fails silently by serving the unfiltered page.
- Phase 0: dynamic components record their URL state as the component's own controls submit it.
- Smoke slice: step 5 now operates each control once on live and local and compares what is shown and the address reached, instead of only loading the pages.
- Stages 3 and 4: new `reference/interaction-checks.md` (a journey list of every operable control, run through the page's own interface, with an HTTP-replay fallback). Stage 3's gate reports the journey results. Stage 4's live re-fetch builds its address list from two independent sources, the new site's rules and addresses derived from the live pages, and reports rule gaps. A check must not take its inputs only from the thing it checks.
- `reference/tooling-contract.md`: `recheck` and `journeys` commands and the independence rule.
Output effect: rewrite rules may gain entries for forms with empty or default parameters (Phase 8); rendered pages unchanged. Re-running Phase 8 on an existing run is worthwhile if it has a listing with a filter plus a search box (or any form with several controls)
New decisions: none

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
