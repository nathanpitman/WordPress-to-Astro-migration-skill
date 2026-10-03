# Extending this skill

The skill is split so each part can be reviewed and changed on its own.

| To change… | Edit |
|---|---|
| The non-negotiables, flow, or phase list | `SKILL.md` (keep it short; it is always loaded) |
| How a phase works | `phases/NN-name.md` (loaded when the run reaches that phase) |
| A rule that spans phases (safety, scope, gates, baseline, preflight, the running fixes list) | `policies/*.md` |
| Output files and folders | `reference/output-layout.md` |
| What each WordPress feature does, and what to do about it in Astro | `reference/feature-translation.md` (add a new entry when a run meets a feature not listed) |
| How we talk to the user | `policies/plain-language.md` |
| Stage gates and the checkpoint template | `policies/review-gates-and-decisions.md` and `stages/` |
| The local review server | `reference/local-review.md` (spec) and `reference-implementation/scripts/review-server.mjs` |
| The visual check against the live site | `reference/visual-comparison.md` and `reference-implementation/scripts/visual-fingerprint.js` |

**Releasing a change.** Any edit that alters what a run produces needs a `CHANGELOG.md` entry naming the phases it affects, and a bump of `version` in `SKILL.md` and of `SKILL_VERSION` in `reference-implementation/scripts/stamp.py` (MAJOR: comparison contract or output layout; MINOR: phase behaviour; PATCH: wording only). That entry is what lets `policies/updating-a-run.md` tell an existing migration which phases are stale. If you add or move a phase output, update the dependency table in that policy too.

**Adding a phase.** Create `phases/NN-name.md`, add one row to the phase table in `SKILL.md` and say which stage it belongs to in `stages/`, add its output file to `reference/output-layout.md`, and mention it in the Finishing index if it adds headline numbers. Keep the rule that every phase ends at a review gate.

**Adding an option** (like `--submit-forms`). Document it in the Options table in `SKILL.md`, describe the behaviour in the phase it affects, add any new doc to the output layout, and add a matching "never" to the hard rules so the default stays safe.

**Adding a policy.** Put it in `policies/`, list it in the "Read first" table in `SKILL.md`, and add a one-line hard rule if breaking it would be harmful.

**Reference implementation.** `reference-implementation/` holds working scripts and Astro files from a real migration, parametrised by `SITE_ORIGIN` and `CRAWLER_USER`. They are examples to copy and adapt, not authoritative: site-specific parts (plugin names, selectors, category lists) are called out in its README. If the files are absent or unsuitable, write the equivalent in the project's `scripts/`.
