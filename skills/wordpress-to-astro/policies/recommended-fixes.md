# Running list of recommended reviews (`docs/recommended-fixes.md`)

`docs/recommended-fixes.md` is a running list that every phase appends to as things are discovered. It is record-only: nothing on it is applied, investigated further, or fixed during the run. Create it in Phase 1 and never overwrite earlier entries.

Add an entry whenever a phase turns up something a person should look at later, such as unusual URL patterns, plugins or scripts that will need replacing, inconsistent templates, content groups with unclear taxonomy or dates, forms that need wiring up, third-party embeds, duplicate or near-duplicate pages, or anything ambiguous. Detail still belongs in the phase's own file; the entry is a short pointer to it.

Each entry has:

- **Type:** Fix (a defect or risk to correct later), Review (a decision or check for a person), or Explore (worth investigating, outcome unknown)
- **Phase** it was found in, and a one-line **title**
- **Where:** affected URLs, templates or files, grouped when repeated
- **Why it matters:** the likely SEO, accessibility, content or cutover impact, in plain English (`policies/plain-language.md`); for a WordPress feature, say what it does and whether the new site needs it
- **Suggested next step**, and a link to the `docs/` file holding the detail

Group the file by type, then by phase. Hard-coded internal links (Phase 1) are entries of type Fix.
