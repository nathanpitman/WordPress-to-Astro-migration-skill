# Updating an existing run after the skill changes

A finished (or part-finished) migration was built by a particular version of this skill. When the skill improves, the user may want those improvements applied to the migration without starting again. This policy says how: **detect what is stale, tell the user in plain English, re-run only what is affected, protect hand edits, and prove the result with the verifier.**

Resuming (`policies/run-state.md`) continues forward and never repeats completed work. Updating is different: it deliberately re-runs completed phases whose rules have changed.

## 1. Version stamps

- `SKILL.md` front matter carries `version` (semantic: MAJOR changes the comparison contract or output layout, MINOR changes a phase's behaviour, PATCH is wording and fixes that do not change output).
- `CHANGELOG.md` (in the skill folder) has one entry per version. Each entry lists **the phases it affects** and, for each, a one-line reason in plain English. A change to a phase file with no changelog line is incomplete (see `reference/extending.md`).
- `docs/run-state.json` records `skillVersion` (the version that last touched the run), and for each phase `ranWith` (the version it last ran under) and `ranAt`.
- A run with no `skillVersion` is **version 0**: built before stamping. Treat every phase marked `done` as `ranWith: "0"`.

## 2. Detecting staleness (on invocation, before the introduction)

If `docs/run-state.json` exists and `skillVersion` differs from the skill's current `version`:

1. Read the changelog entries newer than each phase's `ranWith`.
2. Collect the affected phases, then add everything **downstream** of them using the dependency table in section 3.
3. Mark those phases `stale` in `run-state.json` (do not change their output yet).
4. Report in two or three plain-English lines: what changed, which phases and outputs are stale, and what it will cost (read-only analysis is cheap; rebuilding and re-verifying is not).
5. Offer, with a recommended default:
   - **Update** (default): re-run stale phases only, in stage order, with the normal review gates.
   - **Resume**: ignore the changes and continue forward; record "skill update declined" in `docs/decisions.md`.
   - **Start over**.

Never update silently. Never mark a phase stale for a PATCH-only change.

## 3. Dependency table

A phase is stale if it is affected by the changelog **or** any phase it reads from is stale.

| Phase | Reads from | Writes (generated, safe to rebuild) |
|---|---|---|
| 0 Intake, baseline | user answers | `wordpress-to-astro.config.json`, `docs/baseline.md`, `docs/platform-features.md`, `docs/decisions.md` (hand-maintained; see section 5) |
| 1 Crawl | config | `.crawl-cache/`, `docs/site-structure.md`, `docs/url-patterns.md` |
| 2 Unlinked pages | 1 | additions to `docs/site-structure.md`, cache |
| 3 Content | 1, 2 | `docs/content-map.md`, `docs/authors.md` |
| 4 Forms | 1, 2 | `docs/forms.md` |
| 5 Layouts, components | 0, 1, 2 | `src/data/pages/`, layouts, components, `scripts/verify` |
| 6 CSS | 5 | `src/styles/` |
| 7 SEO inventory | 1, 2 | `docs/seo-inventory.md`, `src/data/redirects.json` (generated part) |
| 8 Listings, search, 404 | 5, 6 | listing variants, `rewrites.json` (generated part), search index, 404 |
| 9 Assets | 1, 5, 6 | `public/`, asset manifest |
| 10 Accessibility | 1, 2 | `docs/accessibility-report.md` |
| 11 Errors | 1, 2 | `docs/errors.md` |
| 12 Finishing | all | clean build, README section, new `docs/index-YYYY-MM-DD-HHMM.md` |

Phases 5, 6, 8 and 9 changing always forces re-verification (Stage 4) and Phase 12. Stage 2 phases (3, 4, 7, 10, 11) read only the cache, so updating them is cheap and can run in parallel.

## 4. Crawl freshness

`crawledAt` is recorded in `docs/run-state.json` when the crawl finishes. When updating, ask once, in the plain-language pattern, whether to:

- **Rebuild from the existing cache** (default): reproduces the migration as it was at `crawledAt`. Best when the live site is frozen or the goal is only to apply skill improvements.
- **Re-crawl**: refreshes the cache first. Diff the new cache against the old one (pages added, removed, changed) and put the diff at the top of `docs/decisions.md` before rebuilding. Respect `policies/crawler-identity-and-scope.md` as usual.

If the changelog entry says the *crawl itself* changed (Phase 1 or 2 affected), a re-crawl is recommended but still the user's choice.

## 5. Protecting hand edits

Between runs people edit things. An update must not destroy that work.

- Every generator writes `docs/generated-manifest.json`: a map of file path to SHA-256 of what it wrote, plus the skill version. The reference scripts do this through `scripts/stamp.py`; their generated folders are cleaned with `stamp.clean()` (never `rmtree`), which leaves edited files alone.
- **Runs that pre-date the manifest** have none: the generators refuse to overwrite existing files until the user (or you, after asking) runs `python scripts/stamp.py adopt` once, which trusts what is on disk. Say so in the update offer: any hand edits made before that point cannot be detected.
- Before overwriting any generated file, compare its current hash with the manifest. If it differs, the file has been **locally modified**: keep it by default, write the regenerated version beside it as `<name>.updated` and list it in the checkpoint ("kept your edit; new version differs in these ways"). The user chooses keep, take new, or merge.
- Hand-maintained files are never regenerated: `wordpress-to-astro.config.json`, `docs/decisions.md`, `docs/recommended-fixes.md` (append only), hand-maintained halves of `redirects.json` and `rewrites.json`, and any `docs/` file the user edited since its manifest entry. Add new keys or entries to these; never replace existing ones.
- Files not in the manifest are not the skill's and are left alone.

## 6. Backfilling new questions and artefacts

If the new version added an intake question, config key or approved artefact, add it to `decisions` in `run-state.json` as `open`, with its default and a plain-English explanation (`policies/plain-language.md`). Proceed using the default if unanswered, and record that it was a default. Never silently assume an answer for an old config.

## 7. Running the update

1. Update `run-state.json`: `stale` phases, current stage set to the earliest stage containing one.
2. Re-run stale phases in stage order. Re-read the stage file and each phase file in full as you start it (the normal rule), because those files are the new version.
3. Stop at each stage gate as usual. The checkpoint adds a line: `Update: phases re-run <list>, kept local edits <n>, new decisions <n>`.
4. Always finish with Stage 4 (verifier, SEO check, asset check) and Stage 5. The verifier under `docs/baseline.md` is the arbiter: an update that changes rendered output without a changelog entry saying it should is a regression. Fix the build, not the baseline.
5. Write a new timestamped index. Add a **Changes since previous index** section: skill version from and to, phases re-run, page counts, differing pages, deviations added or removed, fixes-list entries added, locally modified files kept.
6. On success set `skillVersion` and each re-run phase's `ranWith`/`ranAt` to the current version, and clear `stale` (`python scripts/stamp.py complete <phases>`). Before the gate, `python scripts/stamp.py status` lists locally edited and `.updated` files for the checkpoint.

## 8. Never

- Never update without the user's go-ahead, and never mix versions mid-phase: finish or abandon a phase under one version.
- Never overwrite a locally modified file without the user's explicit yes.
- Never change the comparison contract in `docs/baseline.md` as part of an update unless the changelog entry is MAJOR and the user agrees at a gate.
- Never skip the verifier because "only the docs changed".
