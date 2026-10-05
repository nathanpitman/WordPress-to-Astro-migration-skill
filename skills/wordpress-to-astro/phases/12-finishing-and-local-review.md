# Finishing and local review

*Used in two stages: sections 1 (clean build), 3 (README) and 4 (index) are Stage 5 (Finish); section 2 (local review server and the visual comparison) is Stage 4 (Verify and review).*

The run is **not finished until the user has a local copy of the site they can start, open and review**. A set of documents and a source tree that merely "should" build is not enough. This phase proves the project builds from a clean install, proves it can be reviewed in a browser, and writes the index.

## 1. Clean build

1. From the project root, run the install step (`npm ci` if a lockfile exists, otherwise `npm install`), then `npm run build`.
2. The build must exit successfully. Record the page count, the build time and the size of `dist/`. If the build fails or runs out of disk space, say so plainly, fix what is in scope (the project's own code or configuration, never the migrated markup), and re-run. Report any remaining failure at the top of the index and in the chat summary.
3. Re-run the verifier (Phase 5) and the other checks (SEO, assets) against this final build and record the numbers.

## 2. Local review server

Provide `npm run review` as specified in `reference/local-review.md`: it serves `dist/` and, at **serve time only**, makes the verified build reviewable on a developer's machine (rewrites the production origin to the local address so nothing loads from or links to the live site, applies the host-level rewrites, redirects, headers and content types, serves the 404, blocks third-party scripts). The built files stay byte-identical to what the verifier checked.

Then actually run it, in the background, and probe it:

- the home page, one page of every template, a listing or filter variant that depends on a rewrite (if any), a URL that redirects, a missing URL (expect the themed 404), one image, one stylesheet, `robots.txt` and a sitemap
- confirm status codes and content types, and that the served HTML contains no references to the production origin for assets or internal links (emails and encoded values may remain)
- if a browser is available, open one page and confirm from the network list that every request goes to the local server (apart from known, documented failures such as server-side endpoints that no longer exist). If no browser is available, record "not done: requires browser" and rely on the HTML check

If a browser is available, also run the **visual comparison** (`reference/visual-comparison.md`) on the final build, against the live site, while the server is up. Record the results in the index under "Local review check" and "Visual comparison". **Stop the server before finishing**; leave no process running.

If a shell cannot start a server in this environment, say so, and give the user the commands to run instead.

## 3. README

Make sure the project root has a `README.md` that tells a reviewer how to run the site: prerequisites (Node version), install, `npm run build`, `npm run review` and the address, `npm run verify`, what is different between local review and production, what does not work locally (server-side features such as forms and any removed JavaScript component endpoints, listed from `docs/errors.md` "Known cutover breakages"), and where the documentation and the index are. If a README already exists, do not overwrite it: append a "Reviewing the migrated site" section (or write `REVIEW.md` and link to it).

## 4. The index

This step runs after the user approves Stage 4 (Verify and review) at its gate. If the user ends the run early, still write the index, marking the phases not completed, and still run the local review check below on whatever has been built.

Write the summary report as a date and time stamped index in the docs folder, named `docs/index-YYYY-MM-DD-HHMM.md` (local time, 24-hour clock). Never overwrite a previous index; each run produces a new one so runs can be compared.

The index must contain:

- Run details: domain, date and time, and the phases completed (note any skipped or partial)
- **Run it locally:** the exact commands (install, build, review, verify), the address the review server uses, and what differs locally from production (see below)
- A plain-English summary at the top: what was done, what to look at first, what is left
- Links to every other file in `docs/`
- With `--auto`, lead the index with the auto-mode summary (`policies/auto-mode.md`).
- Headline numbers: pages crawled, unlinked pages found, content groups and entry counts, authors, forms (and shared field groups, and how many were submitted if `--submit-forms` was used), hard-coded internal links (distinct patterns and total occurrences), templates and components, accessibility findings by severity, security findings by confidence, and error counts by type
- Verification results: pages rendered and compared, how many differ from the originals, what the comparison contract normalised, the SEO check, the asset check, the **local review check** and the **visual comparison** (both below)
- The contents of `docs/deviations.md`, summarised, and a summary of `docs/recommended-fixes.md` (counts by type and phase, with the highest-impact entries listed first)
- **Platform features and recommendations:** the table from `docs/platform-features.md` condensed (what each WordPress feature did, the verdict, the recommended Astro way), grouped into Drop, Keep as is, Replace later, Replace now and Decide
- Open decisions from `docs/decisions.md`
- Manual follow-up: form wiring to a form handler, Payload modelling, cutover redirects, host configuration (rewrites, headers, content types), and anything ambiguous that was logged during the run

Then give the user a short version of the same summary in chat, with the path to the index file.

## Done means

Do not report the run as complete until all of these are true, or the exceptions are stated plainly:

- `npm run build` succeeds from a clean install
- the verifier, SEO check and asset check were run on that build and their results are in the index
- the visual comparison was run and its classified differences are in the index (or recorded as "not done: requires browser")
- `npm run review` was started, probed and stopped, with results in the index
- the README tells the user how to do it themselves
- the index and the chat summary both start with the commands to run the site locally
