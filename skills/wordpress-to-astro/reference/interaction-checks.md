# Interaction checks (journeys)

A markup comparison proves that the built files equal the original's. It does **not** prove that the page's own controls reach those files. A filter button can submit an address nobody generated a file or rule for, and the host then serves the wrong page with a 200 and no error. These checks press the controls, the way a visitor does, on the live site and on the local build, and compare what happens.

Use it at the end of Stage 3 (for every interactive component built in that stage, before the gate) and again in Stage 4 on the final build. It sits beside `reference/visual-comparison.md` and follows the same classification of differences.

## 1. Build the journey list

From the dynamic components table in `docs/baseline.md`, the forms in `docs/forms.md` and a scan of the cached pages, list **every control a visitor can operate**: filter buttons, search boxes, sort menus, load-more and pagination controls, tabs, accordions, carousel arrows, menu and dropdown toggles, modal openers. One row per control, plus rows for the **combinations** that share a form or a state: filter then search, search then filter, filter then load more, load more then filter.

| # | Page | Control and action | Expected on live (from a real run) | Address after the action |
|---|---|---|---|---|

Fill the expected results by operating the live site, not by reading the script.

## 2. Run it in a browser (when one is available)

1. Operate each control through the page's own interface: click, type, press Enter. **Typing the resulting address into the address bar is not the same test**: it skips whatever the control adds to the address (empty fields, encoded brackets such as `%5B%5D`, hash fragments).
2. Record what is shown (counts, labels, order) and the address the browser ends up at. Do the same on the local review server.
3. Scripts that load only when a block scrolls into view (an `IntersectionObserver` pattern) may never fire in a hidden or background tab. Scroll the block into view and wait; if the loader still does not run, trigger the same load the page's own script performs, and say so in the record.
4. **Read-only on the live site:** operate GET-only controls (filters, search, load more, menus). Do not submit forms that send data, click consent buttons, sign in or change state.
5. Compare each row. Classify every difference as a hosting-layer artefact, a genuine regression (fix it) or a defect of the original (record it), as in `reference/visual-comparison.md`.

## 3. Without a browser: replay over HTTP

Serialise each form as a browser would (section 1 of Phase 8: every named control, including empty ones, the default option, every page index) and for each resulting address request the live site and the local review server. Compare status and content under the comparison contract. Behaviour that only exists in a script (in-place updates, lazy loading) cannot be checked this way: record "not done: requires browser" for those rows.

## 4. Do not let a check use only the thing it is checking

A re-fetch of the live site (the Stage 4 `recheck`) must take its address list from **two independent sources**:

- (a) the new site's own data: the rewrite rules, redirects and built files;
- (b) addresses derived from the **live pages themselves**: form serialisations (section 3), pagination and "next" links, page counts in the markup, sitemap entries, internal links that carry query strings.

Fetch every address from (a) and (b). Report each address in (b) that no rule or file in (a) covers as a **gap**. A list built only from (a) can only confirm what was already thought of.

## 5. Record

Add an "Interaction checks" section to `docs/templates-and-components.md`: the journey table with the live result, the local result and a verdict for each row, the gaps found and fixed, and anything not done. Summarise it in the checkpoint and the index.

## Pitfalls

- Test **combinations**, not single controls. Controls in one form share one submission.
- Empty and default parameters are real addresses. A server that ignores an empty parameter still receives it.
- Browsers percent-encode brackets and other characters in query strings; the review server and the host rules must decode them the same way.
- A pass on the verifier with a failing journey means the rules, not the pages, are wrong.
