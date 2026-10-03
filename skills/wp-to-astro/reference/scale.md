# Scale

Defaults assume a site of up to a few hundred pages. Check the size at the end of the Stage 1 crawl (record it in `wp-to-astro.config.json` under `scale`) and adapt:

| Pages | Crawl | Analysis | Verification | Visual and accessibility |
|---|---|---|---|---|
| up to ~500 | full | full | every page, in batches if disk is tight | shared regions once, every page's `<main>` for accessibility; 8–10 pages visually |
| ~500 to ~5,000 | full, with the crawl delay unchanged; run in the background and report progress | full for facts; sample for narrative | every page (batches) | shared regions once; accessibility on every page of the smallest templates and about 20 pages per large template; 10–15 pages visually |
| over ~5,000 | **ask the user first**: agree a crawl budget (sections, depth, date range) and expected duration | per-template sampling, with counts for the rest | every page if affordable, else per-template sample plus a full SEO and asset check | sample |

General rules: never raise the request rate to save time; estimate the cache, build and asset sizes before starting each large step (`policies/before-starting.md`); prefer batch scripts that resume (skip what is already cached); record in the index which parts were sampled and how.
