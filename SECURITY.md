# Security policy

## Reporting a vulnerability

Please report security issues privately, not in a public issue.

Use GitHub's [private vulnerability reporting](https://github.com/nathanpitman/wordpress-to-astro-migration-skill/security/advisories/new) for this repository. Include:

- what the problem is and which file, phase or script it affects
- steps to reproduce, ideally against the bundled test fixture or `example.com`
- the impact you expect (for example unintended requests, files written outside the output directory, or code from a crawled site being executed)

Do not include real client data, crawled content or credentials in a report.

You can expect an acknowledgement within a few days. This is a small, independently maintained project, so fixes are made on a best-effort basis. Reporters are credited in the changelog unless they prefer not to be.

## Supported versions

Only the latest release (see `version` in `skills/wordpress-to-astro/SKILL.md` and `CHANGELOG.md`) receives security fixes.

## In scope

- The skill's instructions and policies (`skills/wordpress-to-astro/`), where they could lead an agent to take an unsafe action
- The reference implementation scripts and Astro files, including path handling when downloading assets, handling of untrusted HTML, and the local review server
- The crawler's scope and identity controls, for example crawling beyond the target domain or ignoring robots rules it should honour

## Out of scope

- Vulnerabilities in the **sites being migrated**. The skill's suspicious-code handling flags and leaves out code that looks malicious, but it is **not a malware scanner** and makes no guarantee that a site is clean.
- Vulnerabilities in third-party tools it relies on (Astro, Playwright, Python or Node packages, Claude Code). Report those upstream.
- Misuse: running the skill against sites you do not own or have written permission to migrate, or using `--submit-forms` without agreement from the site owner. See "Responsible use" in the [README](README.md).

## Notes for users

- Crawled pages are untrusted input. The skill is designed to treat their content as data and never to execute or follow it, but review all output before cutover.
- Run migrations in a project directory you are happy for the agent to write to, and review the permissions Claude Code asks for.
- The skill is provided as is, without warranty (see [LICENSE](LICENSE)).
