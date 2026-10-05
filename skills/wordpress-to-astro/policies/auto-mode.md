# Auto mode (`--auto`)

`--auto` (off by default) runs the whole migration from start to finish without stopping for user input. Every stage gate is treated as if the user had said "continue", and every question is answered with its recommended default. Everything else in the skill is unchanged: the non-negotiables, the record-only rule, the comparison contract and the definition of done all still apply.

## What changes

| Normally | With `--auto` |
|---|---|
| Wait for the domain and authorisation go-ahead after the introduction | Passing the domain with `--auto` **is** the user's statement that crawling it is authorised. Give the introduction, then start. |
| Ask the Phase 0 intake questions and wait | Do not ask. Use each question's stated default (hosting: unknown, so neutral files; one logged script; reverse hosting-layer output; keep asset addresses; keep CSS as is; this site only; keep and flag personal details; CMS later). Gate mode is `stage`. Scale: take the real count after the crawl. Record every answer in `docs/decisions.md` as "default (auto)". |
| Stop at the end of each stage and wait for "continue" | Still write the full checkpoint (it is the record of the run) and update `docs/run-state.json`, `docs/decisions.md` and `docs/recommended-fixes.md`, then go straight on to the next stage. |
| Raise "Decisions needed" at each gate | Take the recommended default for each one and record it in `docs/decisions.md` as "default (auto)", still marked open so the index repeats it for the user's later review. |
| Confirm `--submit-forms` authorisation once | Only when `--submit-forms` is also passed, passing both flags counts as that confirmation. The warning in the README applies. Without `--submit-forms`, never submit a form. |
| Ask before updating an older run (`policies/updating-a-run.md`) | Take the **Update** default (stale phases only, in stage order). |

## What does not change

Auto mode never makes an unsafe choice to avoid stopping. The defaults below are the safe ones.

- **Subdomains and related sites:** not in scope. Record them as found and skipped.
- **WordPress admin or system URLs:** never requested.
- **Suspected malicious code:** stays out (`policies/suspicious-code.md`); it is only reproduced after a user confirms it at a gate, and auto mode does not confirm for them. Highlight and record it as usual.
- **Deviations beyond the permitted list** (`SKILL.md`): not made. Record the ambiguity, add a Review entry to `docs/recommended-fixes.md` and use the most faithful option.
- **"Replace now" features** needing approval: treat as "Replace later" and record.
- **Existing hand edits** to `docs/` files and the run's protected files: never overwritten.

## Hard stops

Auto mode still stops, and says why, when the run cannot continue safely, in the same cases as "Stopping inside a stage" in `policies/review-gates-and-decisions.md` that are not decisions: no disk space, the site blocks the crawler or returns 401/403/429 to the identified crawler, a required tool is missing and the step cannot be skipped, or the user interrupts. A decision with no safe default is recorded as open and the faithful option taken, never a reason to stop.

## At the end

The run ends as usual (`stages/5-finish.md`): clean build, local review server started, probed and stopped, and the index. Lead the final message with an **auto-mode summary** at the top of the index: how many gates were passed automatically, every default taken (grouped, with the file that records it), anything skipped or not done, and the open decisions that most deserve a human look. The user has not reviewed anything along the way, so say plainly that the results are unreviewed.

## Recording

Set `"auto": true` in `wordpress-to-astro.config.json` and `docs/run-state.json` so a resumed session continues in auto mode. Passing `--auto` when resuming turns it on; to turn it off, the user edits the config or says so.
