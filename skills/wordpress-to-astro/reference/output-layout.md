# Output layout

```
wordpress-to-astro.config.json         # intake answers and detected stack, read by the scripts (hand-maintained)
docs/
  platform-features.md       # every WordPress feature found: plain-English purpose, translate-or-drop verdict, Astro approach
  run-state.json             # stage and phase status, open decisions, counts (resume point)
  baseline.md                # stack fingerprint, origin-markup definition, comparison contract (Phase 0)
  decisions.md               # intake answers and decisions at each gate; open ones marked
  site-structure.md
  content-map.md
  authors.md
  forms.md
  templates-and-components.md
  seo-inventory.md
  accessibility-report.md
  errors.md
  deviations.md
  url-patterns.md
  assets.md                  # asset summary; the full manifest is a data file
  recommended-fixes.md       # running list of fixes, reviews and areas to explore; recorded, never applied
  forms-submission-log.md    # only when --submit-forms is used
  security-findings.md       # suspicious code found; flagged, never recreated
  index-YYYY-MM-DD-HHMM.md   # summary report, written at the end of each run
README.md                    # how to build and review locally (created, or a section appended, at Finishing)
src/
  layouts/  components/  pages/  content/  styles/
  data/                      # machine-readable cutover data: redirects.json, rewrites.json, asset content types
scripts/                     # extraction and verification, re-runnable (npm run extract / verify)
public/                      # default: mirrors the original URL paths, byte-for-byte
  (robots.txt, sitemaps, feeds, favicons, images, fonts, scripts, other verbatim static assets)
  # opt-in grouped layout (only if the user chose it in Phase 0): images/global/ and images/<content-type>/<slug>/
```

Generated files and hand-maintained files must live apart: a script may delete and rebuild only what it generates (for example `src/data/pages/`), never the whole folder.
