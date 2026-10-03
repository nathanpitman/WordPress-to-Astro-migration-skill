# Review gates and decisions

The run is organised in **five stages**. **Stop at the end of every stage for the user's review. Never start the next stage on your own.** Within a stage, work through its steps without stopping, sending a short progress line between steps (see `policies/before-starting.md`).

| Stage | File | Steps (phases) |
|---|---|---|
| 1 Discover | `stages/1-discover.md` | 0, 1, 2, smoke slice |
| 2 Analyse | `stages/2-analyse.md` | 3, 4, 7 (inventory), 10, 11 |
| 3 Build | `stages/3-build.md` | 5, 6, 9, 8 |
| 4 Verify and review | `stages/4-verify-and-review.md` | checks, local review, visual comparison |
| 5 Finish | `stages/5-finish.md` | clean build, README, index |

**Gate mode.** The default is `--gates=stage` (above). With `--gates=phase` (set in `$ARGUMENTS` or chosen at intake) treat every phase as a stage of its own and stop after each, as the skill originally did. Record the mode in `wordpress-to-astro.config.json`.

## Stopping inside a stage

Stop mid-stage only when:
- a decision is needed that changes the work and has no safe default (for example a subdomain that may or may not be in scope, a host that determines how redirects are delivered);
- a failure cannot be resolved in scope (no disk space, the site blocks the crawler, a tool is missing and the step cannot be skipped);
- the user told you to.

Otherwise record the question in `docs/decisions.md` as open, proceed with the most faithful default, and raise it at the next gate. Suspected malicious code is highlighted immediately (`policies/suspicious-code.md`) but does not by itself stop the stage.

## At each gate

1. Update the task list and `docs/run-state.json` (`policies/run-state.md`).
2. Add new entries to `docs/recommended-fixes.md`, and record decisions made in `docs/decisions.md`.
3. Give the checkpoint, using this template and keeping it to about fifteen lines, **in plain language** (`policies/plain-language.md`): explain any WordPress term or product the first time it appears, and link to `docs/platform-features.md` for detail:

```
Stage N complete: <name>
Produced: <files, with paths>
Numbers: <three to six key figures; a small table is fine>
Surprising: <up to three bullets, or "nothing">
Fixes list: +X Fix, +Y Review, +Z Explore (most important: <titles>)
Decisions needed: <numbered; plain English in the six-part pattern of policies/plain-language.md, each with the recommended default, or "none">
Next: Stage N+1 <name>
```

4. Stop and wait.

Proceed only when the user replies with "continue" or something clearly equivalent (e.g. "go on", "next", "looks good, proceed"). If the user replies with corrections or questions instead, handle them, update the affected files, and re-present the checkpoint. Do not treat silence, or a reply that merely acknowledges the checkpoint, as approval. Decisions the user has not answered stay marked "open" in `docs/decisions.md` and are repeated in the index; proceeding with a sensible default is allowed, but record that it was a default.

The user may redirect at any gate (skip a step, re-run a stage, change scope). Follow that, record the change in `docs/decisions.md` and the next index report. Later steps read from files written earlier, so if the user edits a `docs/` file between stages, use their edited version.
