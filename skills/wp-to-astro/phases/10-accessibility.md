# Phase 10: Accessibility report (record only)

*Stage 2 (Analyse): reads the crawl cache only. `policies/record-only.md` applies.*

Write `docs/accessibility-report.md`, opening with a plain-English summary (what was checked, the worst three findings, what to do first). When an issue relates to a plugin or tool (for example automatic alt-text or accessibility overlays), say what it does and whether it is the right fix (`reference/feature-translation.md`, Accessibility). **Do not fix anything**, in the Astro source or elsewhere.

Check the cached pages for, at minimum: missing or empty `alt`, heading level skips, missing landmarks, empty links/buttons, form inputs without labels, low-contrast indications where determinable from CSS, missing `lang`, duplicate IDs, positive `tabindex`, missing skip links, autoplay media, non-descriptive link text, missing document title, and ARIA misuse (hidden-but-focusable content, dangling references, invalid roles). Also look for removed focus outlines, missing `autocomplete` on personal-data fields, and click handlers on non-interactive elements.

Method:
- Audit **shared regions (header, footer, cookie banner, pre-header) once** and attribute the findings to every page; audit page-specific content per page. Group findings by shared component where the issue lives in a reused region.
- Use a severity rubric and state it: serious (blocks or seriously impedes some users), moderate (degrades the experience or fails a criterion with workarounds), minor (best practice).
- Treat contrast as **indicative** only. Resolve colours from the stylesheet's tokens, skip any element whose background cannot be determined (arbitrary values, gradients, images, inline styles) rather than assuming white, and say the result needs checking in a browser.
- State what static analysis cannot show (computed contrast over images, focus order and visibility, keyboard traps, carousel and accordion behaviour, zoom and reflow, screen-reader output) and list it as manual testing still needed.

For each issue record: rule or WCAG criterion, severity, affected URLs (group repeated template issues rather than listing every page), the element or selector, and a short note on the likely fix for later.
