# Contributing

Thanks for helping improve this skill.

- **Bugs and ideas:** open an issue. For migration problems, say which stack the source site used (theme, SEO plugin, forms, caching/CDN) and which phase failed.
- **Pull requests:** keep them focused. The skill's three principles (rendered HTML is sacred; structure the source, not the output; record, never repair) are not up for change in a PR.
- **Reference implementation:** keep scripts free of constants from any one site: stack-dependent behaviour belongs in `wordpress-to-astro.config.json` or one small function (a hosting-layer reversal, a mask set). Run `reference-implementation/test-fixture/smoke.sh` before sending a change (CI runs it on every pull request), and add to the fixture when you add a case. Reversals for more caches, CDNs and form or SEO plugins are welcome.
- **No client data:** never commit real client names, domains, crawled content or credentials in examples, fixtures or issues. Use `example.com`.
