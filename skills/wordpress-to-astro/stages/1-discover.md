# Stage 1: Discover

**Steps:** Phase 0 (intake and baseline), Phase 1 (crawl and site structure) and Phase 2 (unlinked pages) as one working unit, then the smoke slice. Read each phase file when you reach its step.

**Order**
1. **Intake (the one early stop).** Ask the Phase 0 questions in a single message, each with a recommended default, and wait for the answers: they change the scope, the tooling and what you build. Write `wordpress-to-astro.config.json` and `docs/decisions.md` from the answers (see `policies/run-state.md`).
2. **Fingerprint the stack, write the feature inventory (`docs/platform-features.md`) and `docs/baseline.md`** (Phase 0). Explain every WordPress feature in plain English and decide, for each, whether the new site needs it at all (`policies/plain-language.md`, `reference/feature-translation.md`).
3. **Crawl, then look for unlinked pages** (Phases 1 and 2). Phase 2's sources (sitemaps, search, archive) are checked against the crawl as soon as it ends; do not stop between them. Fetch the pages Phase 2 finds, cache them, and update the hard-coded-link list.
4. **Smoke slice** (`reference/smoke-slice.md`): take three representative pages end to end through extract, build, verify and the local review server, to prove the baseline contract before any bulk work. Adjust `docs/baseline.md` and the config if it fails.

**Gate: end of stage 1.** Checkpoint (template in `policies/review-gates-and-decisions.md`): pages found and how (crawl, sitemap, search, archive), content groups seen, subdomains found, baseline summary in plain English (stack, what was reversed and why, dynamic components), the platform features found with their verdicts (Drop, Keep, Replace later, Replace now, Decide) and the decisions that need the user, smoke-slice result, recommended-fixes counts, and any open decisions. Next: Stage 2.
