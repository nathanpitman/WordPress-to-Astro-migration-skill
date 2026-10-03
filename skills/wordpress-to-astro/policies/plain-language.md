# Plain language about WordPress

**Assume the user does not understand WordPress.** Often that is exactly why they are migrating away from it. They are intelligent and care about the outcome, but they may never have heard of Gravity Forms, a cache plugin, a custom post type or a nonce. Everything you say to them (questions, checkpoints, the summaries at the top of `docs/` files, the index) must work for that reader.

## The rules

1. **Explain every WordPress-specific thing the first time you raise it in a message.** One sentence, everyday words, say what it is *for*: "WP Rocket (a speed plugin that rewrites each page before it is sent to visitors)", "Gravity Forms (the plugin that builds and processes your contact and quote forms)". No bare product names, acronyms or WordPress terms (plugin, theme, custom post type, shortcode, nonce) without that gloss.
2. **Ask decisions in the six-part pattern**, short enough to read in half a minute:
   - **What it is:** the job it does, in plain words.
   - **Why you have it:** the evidence (where you saw it on the site, what visitors see).
   - **Does the new site need it?** Often the honest answer is "no, a static site does this differently or does not need it".
   - **Options:** keep as is, replace with the Astro way, drop. Say what each costs in effort, money and risk.
   - **Recommendation and default:** which you would choose and what happens if they do not answer.
   - **What it touches:** search rankings, editors' day-to-day work, running costs, legal obligations.
3. **Apply the translate-or-drop test to every WordPress feature found**, before anything is built or asked:
   1. What job does it do for visitors, editors or the owner?
   2. Does a static Astro site need that job done at all? (Many WordPress features exist only to make WordPress itself fast, safe or editable.)
   3. If yes, is there a standard Astro, CMS or hosting way to do it? (`reference/feature-translation.md`.)
   4. Would doing it change the pages' output? If so, the zero-SEO-change rule applies: it is a recommendation for after the migration, or a logged deviation the user has approved.
   Classify each as **Drop**, **Keep as is**, **Replace later**, **Replace now** (needs approval) or **Decide** (needs the user).
4. **Better ways are recommendations, not silent changes.** If Astro offers a better way to do something (image optimisation, search, sitemaps), say so and explain the benefit, but the migration still reproduces the site as it is unless the user approves a deviation. Record these in `docs/platform-features.md` and `docs/recommended-fixes.md` as "Replace later".
5. **Keep chat short; put detail in the docs.** Rank decisions by consequence, batch them, and link to the feature's row in `docs/platform-features.md` for the full explanation. Never open with a wall of terms.
6. **Docs get a plain-English top.** Each `docs/` file opens with two or three sentences saying what it contains and what the reader should do with it. `docs/platform-features.md` carries a small glossary.
7. **Say what you do not know.** If you cannot tell what a feature is for from outside, say that and ask, rather than guessing.

## Example

Poor: "Nonce tokens are per-render so we mask them in the comparison contract. Do you want the Rocket layer reversed?"

Good: "Your site runs a speed tool (WP Rocket) that rewrites each page before it reaches visitors, so the same page can look slightly different in the source on different visits. A static site does not need it, because pages are built once and served fast. I recommend rebuilding pages without its changes; visitors will not see any difference, and search engines see the same content. If you would rather keep its exact output I can, but it adds a lot of fiddly code. OK to go without it? (Default: yes.)"

## Where this applies

Intake questions (Phase 0), the platform-features inventory (Phase 0), every "Decisions needed" line at a gate, forms (Phase 4), search and listings (Phase 8), images and assets (Phase 9), accessibility findings that mention plugins (Phase 10), the recommended-fixes list ("Why it matters"), and the index.
