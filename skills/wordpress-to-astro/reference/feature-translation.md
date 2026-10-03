# WordPress features and what to do about them

A catalogue for explaining, deciding and translating. For each feature: what it does in plain English, whether a static Astro site needs it, the standard Astro way if it does, and our recommendation. Use it for the feature inventory (`docs/platform-features.md`) and whenever you ask the user about something WordPress-specific (`policies/plain-language.md`). The migration reproduces today's pages exactly; "In Astro" describes the recommended way **after** that, unless the user approves a change.

Classification values: **Drop** (not needed), **Keep as is**, **Replace later**, **Replace now** (needs approval), **Decide** (needs the user).

## Speed and delivery

**Cache and speed plugins (WP Rocket, W3 Total Cache, Autoptimize)**
- *Does:* make WordPress pages load faster by storing finished pages, shrinking code, delaying images and scripts, and rewriting the page before it is sent.
- *Needed after migration?* No. A static Astro site is built once and served from a CDN, which is what these plugins imitate. Astro also minifies output and browsers lazy-load images natively (`loading="lazy"`).
- *Recommendation:* **Drop.** The baseline reverses their rewriting so the rebuilt pages carry the site's own markup. Mention that on live a few images never load because of the plugin's lazy-loader; they will now.

**Image optimisation plugins (Imagify, ShortPixel, Smush, WebP converters)**
- *Does:* shrink images and serve modern formats (WebP) at the same web address.
- *In Astro:* the built-in image tools (`<Image>` and `getImage()`, using sharp) create right-sized, modern-format images at build time.
- *Recommendation:* **Replace later.** Doing it now would change every image address and file, which breaks the "nothing changes for search engines" rule and the indexed image URLs. Keep the original files (including the WebP-in-`.jpg` ones) at their addresses now; plan a deliberate optimisation step afterwards, with redirects or the same paths, and a before-and-after speed check.

**Content delivery and security services (Cloudflare and similar)**
- *Does:* sit in front of the site, caching it and sometimes rewriting pages (for example hiding email addresses from spam bots).
- *Needed?* The delivery part continues to work in front of a static host; the page-rewriting extras are optional.
- *Recommendation:* **Keep as is** at the hosting level; the baseline reverses its page rewriting. Ask whether to keep email obfuscation (it re-applies automatically if the service stays on).

## Search engines and sharing

**SEO plugin (Yoast, Rank Math)**
- *Does:* writes each page's title, description, social-sharing tags and structured data, and makes the sitemap and robots file.
- *In Astro:* these become fields on each page that the layout writes into the page head; `@astrojs/sitemap` and `@astrojs/rss` produce sitemaps and feeds; with a CMS, an SEO plugin gives editors the same fields.
- *Recommendation:* **Keep as is** now (output copied exactly, sitemaps copied as snapshots); **Replace later** by generating sitemaps and feeds from the build or CMS after cutover.

**Redirect plugin (Redirection, Safe Redirect Manager)**
- *Does:* sends visitors from old web addresses to new ones.
- *In Astro:* redirects are set up in the hosting service, not in the pages.
- *Recommendation:* **Replace now** (required for cutover): export the plugin's rules from WordPress and load them at the host. Only the rules visible from outside can be found automatically.

**WordPress extras in the page head (REST API links, oEmbed, shortlinks, emoji scripts, XML-RPC)**
- *Does:* let other software talk to WordPress or embed its pages. Searchers and visitors never use them.
- *Needed?* No. They will stop working after cutover.
- *Recommendation:* **Drop later** in a deliberate clean-up (low risk); copied unchanged now to honour the no-change rule.

## Content and editing

**Page builder and blocks (Gutenberg, Elementor, theme blocks)**
- *Does:* lets editors assemble pages from ready-made sections.
- *In Astro:* sections become components (or CMS blocks); the builder itself is not needed.
- *Recommendation:* **Keep as is** (page bodies stored as the exact HTML); **Replace later** by turning common sections (carousel, accordion, quote form) into components or CMS blocks one at a time, verifying each.

**Custom content types and fields (custom post types, Advanced Custom Fields)**
- *Does:* gives the site its own kinds of content (events, team members, products) with their own fields.
- *In Astro:* typed content collections, or collections in a CMS such as Payload; the content map in `docs/content-map.md` proposes them.
- *Recommendation:* **Replace later** when a CMS is added.

**Menus, widgets, shortcodes**
- *Does:* menus build the navigation; widgets fill sidebars and footers; shortcodes insert dynamic bits into text.
- *In Astro:* menus become data used by the layout; shortcodes are already turned into plain HTML in the output.
- *Recommendation:* **Keep as is.** Check for shortcodes that need a live server (calculators, booking widgets): those need a **Decide**.

**Scheduled publishing and drafts**
- *Does:* publishes a post at a set time and lets editors keep drafts.
- *In Astro:* a static site only changes when it is rebuilt; with a CMS, publishing triggers a rebuild, and scheduled posts need a scheduled rebuild.
- *Recommendation:* **Decide** whether editors need scheduling when a CMS is chosen.

**Comments**
- *Does:* lets visitors reply to posts.
- *Needed?* Only if comments are visible and used. A static site cannot store them; options are a hosted comments service or dropping them.
- *Recommendation:* **Drop** if none are shown (common); otherwise **Decide**.

**Multiple languages (WPML, Polylang)**
- *In Astro:* built-in internationalised routing. *Recommendation:* **Decide** if more than one language is found.

## Search and browsing

**Site search (WordPress search, Relevanssi, Algolia, or a custom component)**
- *Does:* finds pages as a visitor types.
- *In Astro:* a search index built at build time (Pagefind, free, no server) for small and medium sites, or a hosted service (Algolia) for large ones.
- *Recommendation:* **Replace now** with Pagefind (it is required because the old search needs a live WordPress server). Explain that results and ranking will differ slightly.

**Filters, pagination and "load more" that work without reloading the page**
- *Does:* shows the next page of results or applies a filter instantly, using code that talks to the server.
- *In Astro:* pre-built pages for each filter and page, with a small script for the in-page behaviour.
- *Recommendation:* **Replace now**, as set out in Phase 8; needs the host to map query addresses to those pre-built pages.

## Forms

**Form plugins (Gravity Forms, Contact Form 7, WPForms, HubSpot forms)**
- *Does:* shows forms, checks the answers, blocks spam, sends the submissions to email or a CRM and shows a thank-you page.
- *Needed?* Yes, the job; no, the plugin. A static site cannot receive form data by itself.
- *In Astro:* a form-handling service, a small serverless function that forwards to the CRM or email service, or a CMS form builder; plus a spam check (such as Turnstile or reCAPTCHA).
- *Recommendation:* **Decide.** Always a decision (where do enquiries go, who is told, what are the legal terms). The migration keeps the form markup exactly and leaves a clear to-do on each form.

**Spam protection (reCAPTCHA, Akismet)**
- *In Astro:* chosen together with the form handler. *Recommendation:* **Decide** with forms.

## Legal and measurement

**Cookie consent (Complianz, CookieYes, Cookiebot)**
- *Does:* asks visitors for cookie permission and blocks trackers until they agree.
- *Needed?* Yes, this is a legal duty. It must keep working and keep controlling the trackers.
- *In Astro:* a script added to the pages, the same as today.
- *Recommendation:* **Keep as is.** Work out which tool is actually live (sites often have two installed, one switched off) and what it depends on (for example a tag manager).

**Analytics, tag managers and ad pixels (Google Analytics, Tag Manager, Meta, LinkedIn)**
- *In Astro:* the same snippets, copied exactly. *Recommendation:* **Keep as is**; ask the marketing owner whether they are all still used.

**Chat and marketing widgets (Intercom, HubSpot, A/B testing)**
- *Recommendation:* **Keep as is** (third-party scripts); **Decide** whether each is still wanted.

## Accessibility

**Automatic alt text and accessibility overlays**
- *Does:* some plugins write image descriptions (alt text) automatically, or add a toolbar that changes how the page looks for disabled users.
- *Needed?* Alt text matters; the way it is made is up to you. Overlays are not a substitute for an accessible site and can cause problems.
- *In Astro:* alt text is a field on each image in the content model, and can be made required; AI suggestions are fine at editing time if a person reviews them.
- *Recommendation:* the migration never invents alt text; it records every missing one in the accessibility report. **Replace later**: make alt text required in the CMS and fix the gaps. **Drop** overlays unless the user chooses otherwise.

## Running WordPress itself

**Security plugins (Wordfence), backups, updates, logins, spam filters**
- *Does:* keep WordPress safe and recoverable.
- *Needed?* No. A static site has no admin area or database on the public site to attack; the source is in version control, and a CMS has its own backups and users.
- *Recommendation:* **Drop.**

**Staff logins and user roles**
- *In Astro:* editors sign in to the CMS, with its own roles. *Recommendation:* **Decide** when choosing a CMS.

## Needs a separate decision

**Online shop, memberships, course platforms, bookings (WooCommerce, LearnDash, member areas)**
- *Does:* take payments, manage accounts, track progress. These need a live server and a database.
- *Recommendation:* **Decide.** Out of scope for a static migration: stop and ask.
