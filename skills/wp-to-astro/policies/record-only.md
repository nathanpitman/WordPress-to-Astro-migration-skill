# Record only

Phases 10 (accessibility) and 11 (errors), the hard-coded-link catalogue, and every item added to `docs/recommended-fixes.md` are **record only**. This one rule replaces the repeated wording elsewhere.

- **Nothing is fixed, worked around or investigated further during the run**: not in the Astro source, not in the built files, not anywhere else. A defect of the original site is reproduced exactly as served.
- **Where it is recorded:** the detail in the phase's own file; a short pointer in `docs/recommended-fixes.md` (type Fix, Review or Explore) with the likely impact and a suggested next step.
- **Group, do not list:** repeated template or shared-region issues appear once with a page count, not once per page.
- **Distinguish three things.** (1) *A defect of the original*: record it, leave it. (2) *A regression in our build* (a stylesheet missing, a component broken, output that differs from the original beyond the contract): that is our bug, so fix it. (3) *A hosting-layer artefact* (something that differs only because of the layer reversed in the baseline): document it as a deviation, do not "fix" it.
- **Never convert**: hard-coded internal links stay absolute, invalid JSON-LD stays invalid, broken links stay broken.

If unsure which of the three something is, record it as a Review entry and continue with the most faithful option.
