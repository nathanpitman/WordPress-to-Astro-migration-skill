# Visual comparison: local review vs the live site

A markup comparison proves the HTML matches; it does not prove the page *looks* the same (a missing stylesheet, font or script would still pass). This check puts the live page and the local review page side by side in a browser. **It needs a browser tool; if none is available, record "not done: requires browser" and move on.** Use it at the end of Phase 5 (on the pages built so far) and again at Finishing (on the final build).

## Procedure

1. **Choose pages:** the home page, one page of every template, a listing page, a filtered or paginated variant if the site has one, a page with a form, and a page with a carousel or other JavaScript component. Eight to ten pages is enough.
2. **Set up two tabs at the same viewport:** the live URL and the same path on the local review server (`npm run review`, never the raw `dist/` over a plain static server). Run **desktop (about 1280 px wide) and mobile (375 px)**; reload after switching size.
3. **Measure each region while it is in view.** For the header, every top-level section of `<main>` and the footer: scroll it into the middle of the viewport, wait a moment, read its height. Also record `scrollWidth` against the viewport width (horizontal overflow). A ready-made snippet is `reference-implementation/scripts/visual-fingerprint.js`; run it in both tabs and compare the output strings.
4. **Compare.** Treat differences of 2 px or less per region as rounding. For anything larger, descend into the section in both tabs (child element heights, depth three or four) until you find the element that differs, and check what it is.
5. **Screenshot** the top of the home page and one entry page at desktop and mobile, at the same scroll position in both tabs, and compare them by eye. Note any visible difference and its cause.
6. **Classify every difference** before reporting it:
   - *Hosting-layer artefact:* a lazy-loaded image that never loads on the live site, `content-visibility` collapsing off-screen sections, a third-party widget (chat bubble, consent button, analytics overlay) that the review server blocks, per-origin cookie or consent state. Document these (they usually trace to a logged deviation); do not fix them.
   - *Genuine regression:* missing styles, fonts or images, a broken component, layout shift that is not explained by the above. These are bugs in the build: fix them, then re-run the verifier.
   - *Defect of the original:* something wrong on both sides (for example horizontal overflow at mobile width). Record it in `docs/errors.md` and leave it.

## Pitfalls

- **Do not measure from the top of the page.** WP Rocket's `content-visibility: auto` makes off-screen sections report a height of zero on the live site, and its lazy loader can leave images as placeholders (a `0 × 0` placeholder never triggers the loader; a placeholder with no size renders at the default 150 px). Measure each region in view.
- Two Rocket (or similar optimiser) states exist for the same URL; expect small differences that come from the live page, not the build.
- A CDN bot challenge may block an automated browser on the live site. If so, record it and compare against what loads.
- Cookies and consent state are per origin: a consent widget may appear on live and not locally. Check how consent is actually implemented (it may be a third-party widget loaded through a tag manager) before calling it a difference.
- Read-only: only load pages. Do not click consent buttons, submit forms or sign in on the live site; that changes the user's own browser state or the site's data.
- Viewport emulation and element references reset when the page navigates or the turn ends: set the size again and re-find elements after each navigation.

## Recording

Add a "Visual comparison" section to `docs/templates-and-components.md`: a table of pages against desktop and mobile results, the classified differences with their causes, and the screenshots reviewed. Put defects of the original in `docs/errors.md`, add any visible effect of a hosting-layer reversal to its entry in `docs/deviations.md`, and summarise the result in the index.
