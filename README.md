# WordPress to Astro migration skill

A [Claude Code](https://claude.com/claude-code) skill that migrates a live WordPress (or similar CMS) site to [Astro](https://astro.build) using only what is publicly reachable on the domain. No WordPress admin, database or API credentials are needed.

The goal is a clean cutover with **zero SEO impact**: the rendered HTML of every page is reproduced exactly as served, and the output includes content maps shaped for a future [Payload CMS](https://payloadcms.com) setup.

```
/wp-to-astro example.com
```

## What it does

- Crawls the site politely, identifying itself honestly, and records the site structure, redirects and unlinked pages
- Rebuilds each page as an Astro project whose rendered output matches the original (head contents, headings, classes, IDs, scripts)
- Extracts content, taxonomies and authors into Payload-shaped content maps
- Inventories SEO facts (titles, descriptions, canonicals, robots, Open Graph, JSON-LD, sitemaps, feeds) and checks the build against them
- Downloads first-party assets to their original URL paths
- Audits accessibility, broken links and other errors, then **records them without fixing them**
- Ends with a verified local build and review server, with a review gate at the end of each of five stages

### Principles

1. **Rendered HTML is sacred.** Nothing is tidied, modernised or "fixed".
2. **Structure the source, not the output.** Components organise the code; they must not change what is rendered.
3. **Record, never repair.** Defects go into `docs/` and are left as they are.

## Install

Copy the skill folder into your Claude Code skills directory.

```bash
# Per user
cp -r skills/wp-to-astro ~/.claude/skills/

# Or per project
cp -r skills/wp-to-astro /path/to/your/project/.claude/skills/
```

Then, in Claude Code, run `/wp-to-astro <domain>`. Add `--submit-forms` only if you want forms to be test-submitted (see warnings below).

## Contents

| Path | Purpose |
|---|---|
| `skills/wp-to-astro/SKILL.md` | The entry point: non-negotiables and a map of the rest |
| `skills/wp-to-astro/stages/`, `phases/` | Five stages made of 13 phases, each read in full when reached |
| `skills/wp-to-astro/policies/` | Crawler identity and scope, run state, review gates, suspicious code, and more |
| `skills/wp-to-astro/reference/` | Background and contracts (tooling, output layout, visual comparison, scale) |
| `skills/wp-to-astro/reference-implementation/` | Python/Node scripts and Astro files from a real migration, to copy and adapt |

The reference implementation was run on one site (Roots Sage/Acorn, Yoast, Gravity Forms, Livewire, WP Rocket, Cloudflare). Treat it as a worked example, not an authoritative tool; some scripts carry site-specific constants.

## Responsible use

- **Only run this on sites you own or have written permission to migrate.** It crawls the target and downloads its assets.
- **`--submit-forms` creates real form submissions** on the live site (using `@example.com` addresses). Leave it off unless you have agreed it with the site owner.
- The "suspicious code" handling flags and leaves out code that looks malicious. It is **not a malware scanner**; do not rely on it as one.
- Review all output before cutover. The skill is provided as is, without warranty.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

[MIT](LICENSE)

## Disclaimer

This is an independent project. It is not affiliated with, endorsed by, or sponsored by the WordPress Foundation, Automattic, The Astro Technology Company, Payload CMS, or Anthropic. WordPress, Astro, Payload, Claude and Claude Code are trademarks of their respective owners and are used here only to describe what the skill works with.
