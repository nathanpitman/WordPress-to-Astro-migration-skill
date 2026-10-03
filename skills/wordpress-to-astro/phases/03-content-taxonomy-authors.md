# Phase 3: Content, taxonomy, authors

**Content map** (`docs/content-map.md`)
- Identify content groups (blog posts, news, case studies, resources, events, team, etc.) from URL patterns, templates, listing pages and JSON-LD types.
- For each group list: URL pattern, every entry URL, title, inferred publish date (and modified date if present), author, categories, tags, featured image, and whether it appears in listings and feeds.
- **Dates:** infer from, in order, `article:published_time` / JSON-LD `datePublished`, `<time datetime>`, visible on-page dates, URL date segments, sitemap `lastmod`. Record which signal was used and mark low-confidence inferences. If most entries share one date (a bulk import or rebuild), say so and mark the dates low-confidence as editorial dates.
- Document taxonomy: every category/tag, its URL, entry count, and parent/child relations. Describe fields in a way that maps cleanly to Payload collections (collection name, field names and types, relationships), as a proposal only. Custom post types and taxonomies often have no archive URLs of their own; note how they surface instead (landing pages, filters).

**Authors** (`docs/authors.md`)
- Canonical list of author names found in bylines, meta tags, JSON-LD and author archives. Include slug, archive URL, bio, avatar, role, social links, and which content they are credited on. Flag name variants that probably refer to the same person.
- Flag **personal data in public metadata**, for example display names that are email addresses. Keep them as served and add a Review entry.
