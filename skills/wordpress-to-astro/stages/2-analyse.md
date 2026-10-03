# Stage 2: Analyse

**Steps:** Phase 3 (content, taxonomy, authors), Phase 4 (forms), Phase 7 (SEO inventory: the facts and the copied files), Phase 10 (accessibility) and Phase 11 (errors in the original).

**These steps only read the crawl cache.** None needs the Astro build, none depends on another's output, so do them in any order and, where the environment allows it (shell background jobs, or subagents if the user has them), in parallel. Each writes its own `docs/` file. Do not stop between them.

**Placement notes**
- *Phase 7:* do the inventory here: per-page SEO facts, heading outlines, verbatim copies of `robots.txt`, sitemaps and feeds, redirects as data, the HTTP-level signals list, inconsistencies. The **carry-over check** against the build runs in Stage 4.
- *Phase 11:* record the errors that exist in the original site now. The items that need the build (built-site asset check, known cutover breakages, the themed 404 capture) are finished in Stage 3 or 4.
- *Phases 10 and 11 are record-only* (`policies/record-only.md`).
- *Phase 4 with `--submit-forms`:* the submissions are the only step here that touches the live site beyond reading; follow the Phase 4 rules and keep the submission log.

**Gate: end of stage 2.** Checkpoint: content groups and counts, authors (and any personal-data flag), forms and shared field groups, SEO headline facts and inconsistencies, accessibility counts by severity (shared components first), error counts by type, recommended-fixes counts, and any open decisions. Next: Stage 3.
