# Phase 0: Intake and baseline

Run this once, after the go-ahead and before the Phase 1 crawl proper. Part of Stage 1 (`stages/1-discover.md`). **The intake questions are the one early stop**: ask them in one message and wait for the answers before crawling, because the answers change scope and tooling. The fingerprint, feature inventory and baseline then continue straight into the crawl; the gate comes at the end of Stage 1.

**Write for a reader who does not know WordPress** (`policies/plain-language.md`). Every question below is asked in plain English, with the six-part pattern (what it is, why they have it, whether the new site needs it, options, recommendation and default, what it affects), kept short. Only questions that change the work are asked here; feature-specific questions come later, grounded in `docs/platform-features.md`.

## Intake

Ask in one message, each with a recommended default. Record the answers in `docs/decisions.md` and `wp-to-astro.config.json` (`policies/run-state.md`).

1. **Where will the new site be hosted?** (A static site needs a host that can serve plain files; which one decides how old-address-to-new-address forwarding, special handling of addresses with a `?` in them, and some response settings are delivered. Do not assume one; if unknown, produce neutral files for each.)
2. **May the new pages include one small extra script if a feature cannot work without a server?** (Live search, filters and "load more" on the old site need WordPress running; the static version needs a small script to behave the same.) Default: yes, one script, logged.
3. **Should we rebuild pages without the speed-tool and security-service rewriting that sits on top of your site?** (Tools such as WP Rocket and Cloudflare rewrite pages before visitors get them, so the same page can look slightly different in its source from one visit to the next. A static site does not need that.) Default: yes, reverse it, log what was reversed.
4. **Images, fonts and scripts: keep their current web addresses, or move them into a tidier folder structure?** (Keeping addresses means search engines, image search and any outside links keep working without redirects.) Default: keep the addresses.
5. **Styles (CSS): keep each style file exactly as it is, or merge them into fewer files?** (Merging is tidier but changes the page source and risks small visual changes.) Default: keep as is.
6. **Is it OK to crawl this site, and are there related sites (subdomains, landing-page tools, staging copies) to include?** Default: this site only.
7. **Personal details on the site (for example authors shown under an email address): keep as they are, or flag for change?** Default: keep and flag.
8. **How often do you want to review?** After each of five stages (default) or after every one of the thirteen phases; and may read-only analysis run in parallel (background jobs, or helpers if available)?
9. **Is a content management system (for example Payload) planned afterwards?** Default: later; nothing built now, but the content map is written field by field so it can be used.
10. **Roughly how big is the site, and is there a time budget?** (`reference/scale.md`; confirmed against the real count after the crawl.)

## Fingerprint the stack

From a handful of representative pages (home, a listing, a single entry, a page with a form), fetch each twice and compare the two responses and their headers. Note which fragments change between fetches. Identify, from markup and headers: the CMS and theme, the SEO plugin, the cache or optimiser plugin, the CDN and any edge features (email obfuscation, challenge scripts, speculation rules), form plugins, cookie-consent and analytics tools, and **JavaScript-driven components** (look for `wire:` attributes and `wire:snapshot` JSON for Livewire, `x-data` for Alpine, `data-hx-` for htmx, hydration roots for React or Vue, load-more or infinite-scroll buttons). For each dynamic component record the state it keeps in the URL (query parameters, hash, paths) if any.

## Feature inventory: `docs/platform-features.md`

For **every** WordPress feature, plugin, service or script the fingerprint finds, write one row, using `reference/feature-translation.md` for the explanations and add entries there for anything it does not cover:

| Feature | What it does (plain English) | Where we saw it | Does the new site need it? | Astro (or host) way | Verdict | Effect on the migration |
|---|---|---|---|---|---|---|

Verdicts: **Drop**, **Keep as is**, **Replace later**, **Replace now** (needs approval) or **Decide** (needs the user), reached with the translate-or-drop test in `policies/plain-language.md`. Open the file with two or three plain sentences saying what it is, and a short glossary of the terms used. Features that need a decision are raised at the Stage 1 gate in the six-part pattern; do not interrupt the stage for them unless they block the work. Add the features to be replaced to `docs/recommended-fixes.md` as Review or Explore entries.

## Baseline: `docs/baseline.md` and `wp-to-astro.config.json`

Write `docs/baseline.md`: the stack, the origin-markup definition with each reversal class, the volatile tokens and how they are recognised, the comparison contract, the decisions from the intake, and the dynamic components found. Fill in `wp-to-astro.config.json` (hosting layers, volatile tokens, dynamic components and their URL state, asset prefixes). This file is the specification the Phase 5 verifier implements.

After the crawl, run the **smoke slice** (`reference/smoke-slice.md`) and add its result to `docs/baseline.md` before the Stage 1 gate.
