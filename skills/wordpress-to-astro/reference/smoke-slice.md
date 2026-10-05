# Smoke slice

Purpose: prove the whole chain on three pages **before** doing bulk analysis or building every page. The expensive surprises in a migration (a cache plugin that rewrites markup, volatile tokens, a splitter that does not match the theme, a review server that leaks to production) show up on the first end-to-end run. Find them on three pages, not three hundred.

## Pages

Take them from the crawl cache: the home page, one single entry (a post, product or other custom type), and one page with a form or a JavaScript component. If the site has a listing with query-string state, add one listing variant and plan to use the listing's own controls (step 5).

## Run

1. **Reverse and mask** per the draft baseline: apply the hosting-layer reversal and the volatile-token masks to the three cached pages and look at the diff against the raw pages. Every change should be in a listed reversal class.
2. **Split and rebuild:** minimal Astro scaffold, the extraction for just these pages (shared regions, verbatim `<main>`, head items), static build.
3. **Verify** the three pages under the comparison contract. Expect zero differences. Any difference is either a missing reversal or mask (extend the baseline), a splitter assumption that does not hold for this theme (adjust it), or a real build bug.
4. **Review:** start `npm run review` (`reference/local-review.md`), open the three pages, and confirm that no request leaves the local server except documented third-party calls (blocked) and removed server endpoints.
5. **Interact, do not just load.** On the page with the form or JavaScript component, use each of its own controls once, on the local review server and on the live site (in a browser if one is available): press a filter, type and submit a search, press load more, open the menu. Compare what each control shows **and the address the browser ends up at**, then confirm that address is answered by the review server with content equal to live. This is the cheapest place to find that a control submits more than you assumed (empty fields, extra parameters, encoded characters). Without a browser, replay the form's serialisation over HTTP (`reference/interaction-checks.md`, section 3) and record "not done: requires browser" for the script behaviour.
6. If a browser tool is available, do a quick visual check of one page against live (`reference/visual-comparison.md`).

## Outcome

Record the result in `docs/baseline.md` under "Smoke slice": what was adjusted, the final reversal classes and masks, anything that could not be made to pass, and any control whose submitted address the rules did not yet cover. If the slice cannot be made to pass after a reasonable effort, **stop at the Stage 1 gate and say so**; do not proceed to the bulk build on an unproven contract.

## Keep the scaffold obviously temporary

The smoke slice proves the chain; it is not the final structure. Write its output (per-page extracts, shared fragments, any quick Astro route) to a clearly named throwaway folder such as `src/_TEMP-smoke-slice/`, put a `README.txt` in it saying it is temporary, who regenerates it and when it is deleted (Stage 3, Phase 5), and keep it apart from real source such as `src/data/` (hand-maintained cutover data) and `src/content/`. Say so in the Stage 1 checkpoint, so a reviewer browsing the folders is not misled into thinking the slice's one-folder-per-page layout is the intended design. The real source structure is built in Phase 5, from the content map.
