# Smoke slice

Purpose: prove the whole chain on three pages **before** doing bulk analysis or building every page. The expensive surprises in a migration (a cache plugin that rewrites markup, volatile tokens, a splitter that does not match the theme, a review server that leaks to production) show up on the first end-to-end run. Find them on three pages, not three hundred.

## Pages

Take them from the crawl cache: the home page, one single entry (a course, post or product), and one page with a form or a JavaScript component. If the site has a listing with query-string state, add one listing variant.

## Run

1. **Reverse and mask** per the draft baseline: apply the hosting-layer reversal and the volatile-token masks to the three cached pages and look at the diff against the raw pages. Every change should be in a listed reversal class.
2. **Split and rebuild:** minimal Astro scaffold, the extraction for just these pages (shared regions, verbatim `<main>`, head items), static build.
3. **Verify** the three pages under the comparison contract. Expect zero differences. Any difference is either a missing reversal or mask (extend the baseline), a splitter assumption that does not hold for this theme (adjust it), or a real build bug.
4. **Review:** start `npm run review` (`reference/local-review.md`), open the three pages, and confirm that no request leaves the local server except documented third-party calls (blocked) and removed server endpoints.
5. If a browser tool is available, do a quick visual check of one page against live (`reference/visual-comparison.md`).

## Outcome

Record the result in `docs/baseline.md` under "Smoke slice": what was adjusted, the final reversal classes and masks, anything that could not be made to pass. If the slice cannot be made to pass after a reasonable effort, **stop at the Stage 1 gate and say so**; do not proceed to the bulk build on an unproven contract.
