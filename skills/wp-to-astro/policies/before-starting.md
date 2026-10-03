# Before starting

- Confirm the domain and that crawling it is authorised. Use the domain's `robots.txt` crawl-delay and keep concurrency low.
- If `--submit-forms` is set, confirm once that the user owns the site or is authorised to test its forms, and warn that submissions may create real leads, notifications or emails on the site owner's side. Do not proceed to Phase 4 submissions without that confirmation.
- Work in the current project directory. If it is not already an Astro project, scaffold one (static output) before Phase 5. Do not overwrite existing files without asking.
- Keep a working crawl cache (raw HTML, headers, redirects) in `.crawl-cache/` and add it to `.gitignore`. All later phases read from the cache, so the live site is hit once per URL.
- **Preflight resources.** Check free disk space before the first download and again before Phase 5 and Phase 9. Estimate the sizes: the crawl cache, one built page times the page count, and the asset total (list assets and use `Content-Length` before downloading). Warn the user if free space is under about three times the largest step, and about repository weight (binaries over roughly 50 MB suggest Git LFS or object storage). Keep builds and verification able to run in batches and delete intermediate output between batches, so a nearly full disk does not stop the run. Read page content from disk at build time rather than bundling it into the server chunk.
- Create a task list covering the five stages and keep it updated, together with `docs/run-state.json` (`policies/run-state.md`).
- Everything you say to the user follows `policies/plain-language.md`: assume no WordPress knowledge.
- For long steps, send a short progress line in chat every few minutes (what is running, how far through) rather than going silent.
