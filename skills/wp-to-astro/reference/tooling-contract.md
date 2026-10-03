# Tooling contract

The aim: the model **runs** tooling and **interprets** the results; it does not write twenty scripts from scratch on every migration. The reference implementation in `reference-implementation/` is a first pass at this; until it is config-driven, adapt it (or write equivalents) to this contract.

## Rules for every command

- Reads `wp-to-astro.config.json` for origin, scope, hosting layers, dynamic components and options (`policies/run-state.md`); no site-specific constants in code.
- Idempotent and safe to re-run. Writes generated data only to files it owns (for example `src/data/pages/`, `.crawl-cache/`, `docs/*.json`); never deletes hand-maintained files.
- Reads the crawl cache, not the live site, except `crawl`, `download-assets` and the optional submit-forms step.
- Exits non-zero when it finds a failure, and prints a short summary (counts, first problems).
- Generated tables in `docs/*.md` go between markers (`<!-- generated:start name -->` … `<!-- generated:end -->`) so the model can write narrative around them and re-generate without losing it. The model writes the narrative, the findings that need judgement and the decisions; scripts write the tables and counts.

## Commands

| Command | Stage | Reads | Writes |
|---|---|---|---|
| `crawl` | 1 | config, live site | `.crawl-cache/` (HTML, headers, redirect chains, link graph) |
| `fingerprint` | 1 | cache | stack and layer findings for `docs/baseline.md` |
| `analyse content` | 2 | cache | content-map and authors tables |
| `analyse forms` | 2 | cache | forms table (forms, fields, hidden fields, pages) |
| `analyse seo` | 2 | cache | per-page SEO facts, heading outlines, copies of robots, sitemaps and feeds, `redirects.json` |
| `analyse a11y` | 2 | cache | findings JSON and tables (shared regions once) |
| `analyse errors` | 2 | cache | errors JSON and tables |
| `extract` | 3 | cache, config | `src/data/pages/`, shared fragments, `src/content/` |
| `build` | 3 | source | `dist/` (and the search index) |
| `assets` (inventory, download, report) | 3 | cache, config | `public/`, asset manifest |
| `verify` | 3, 4 | cache, `dist/` | pass/fail per page; honours the contract in `docs/baseline.md` |
| `seo-check` | 4 | inventory, `dist/` | pass/fail per page (incl. JSON-LD hashes) |
| `asset-check` | 4 | `dist/` | missing asset paths |
| `review` | 3, 4 | `dist/`, `src/data/*.json` | serves locally (`reference/local-review.md`) |
| `visual` | 4 | browser | per-region height strings (`reference/visual-comparison.md`) |

Expose them as `npm run <name>` (or one `scripts/wp2astro` entry with these subcommands). The standard commands a reviewer sees at the end are `extract`, `build`, `verify` and `review`.

## Status

The reference implementation covers most of these with some site-specific constants (see its README). Making it fully config-driven and testing it on a second and third site is the next step for this skill; until then, treat the table as the target and note in `docs/decisions.md` which commands were hand-written for this site.
