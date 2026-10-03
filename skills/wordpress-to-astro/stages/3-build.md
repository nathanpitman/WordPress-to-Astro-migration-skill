# Stage 3: Build

**Steps, in this order:** Phase 5 (layouts, components and the verifier), Phase 6 (CSS), Phase 9 (images and assets), Phase 8 (search, listings, pagination, and the themed 404).

**Why this order.** Assets and CSS come before listings and search so the site is fully reviewable as soon as the structure exists; listings and the 404 add pages and rewrite rules, so they come last and the whole set is verified once at the end of the stage. Phases 5 and 8 both change the page count and what the verifier covers, so re-run it after each.

**Rules for the stage**
- Keep the project buildable throughout: `npm install` and `npm run build` must succeed after every step.
- Build the verifier first (Phase 5, step 3) and run it after every step, not only at the end.
- Send a short progress line between steps; do not stop for review between them. Stop early only for a blocking decision you cannot default safely (`policies/review-gates-and-decisions.md`).
- Log every deviation as it arises in `docs/deviations.md`.

**Gate: end of stage 3.** Checkpoint: pages built, verifier results (pages compared, pages differing, what the contract normalised), the deviations logged, assets (count, size, failures), listing variants and rewrite rules, the added artefacts (script, 404), the standard npm commands, recommended-fixes counts, and any open decisions. Next: Stage 4.
