"""Project configuration for the reference scripts.

Reads `wordpress-to-astro.config.json` from the project root (see policies/run-state.md) and falls back to
defaults that suit a typical WordPress site. The environment overrides the two values every script needs:

    SITE_ORIGIN    production origin, no trailing slash (overrides "origin")
    CRAWLER_USER   who the crawler says it is, e.g. "Your Name <you@example.com>" (overrides crawl.userAgent's identity)

Keys the scripts read (all optional except the origin):

    origin               "https://example.com"
    crawl.delaySeconds   pause between requests (default 0.6)
    crawl.userAgent      full User-Agent string (default is built from CRAWLER_USER)
    crawl.probes         extra same-host URLs to fetch once and keep verbatim, e.g. ["/feed/", "/comments/feed/"]
    hostingLayers        names from deopt.LAYERS to reverse (default: all known layers)
    volatileTokens       names from lib.MASKS to mask when comparing (default: nonces only)
    masks                extra masks: [{"name": "x", "pattern": "regex", "replacement": "text"}]
    listings             query-string listings to pre-render: [{"base": "/blog/", "params": ["page", "topic"]}]
    notFoundSample       a crawled URL path that returns the themed 404 (default /this-page-does-not-exist/)
    assets.prefixes      first-party path prefixes holding assets (default ["/wp-content/", "/wp-includes/"])
    templates            body-class to template-name map, e.g. {"single-event": "event"} (default: derived)
    skipFormRoles        form `role` values that are not data-entry forms (default ["search"])
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, 'wordpress-to-astro.config.json')

DEFAULTS = {
    'origin': '',
    'crawl': {'delaySeconds': 0.6, 'userAgent': None, 'probes': ['/feed/', '/comments/feed/']},
    'hostingLayers': None,
    'volatileTokens': ['wp-nonce'],
    'masks': [],
    'listings': [],
    'notFoundSample': '/this-page-does-not-exist/',
    'assets': {'prefixes': ['/wp-content/', '/wp-includes/']},
    'templates': {},
    'skipFormRoles': ['search'],
}


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


CFG = _merge(DEFAULTS, json.load(open(CONFIG_PATH)) if os.path.exists(CONFIG_PATH) else {})
ORIGIN = (os.environ.get('SITE_ORIGIN') or CFG['origin']).rstrip('/')
HOST = ORIGIN.split('//', 1)[1] if ORIGIN else ''


def require_origin():
    if not ORIGIN:
        raise SystemExit('Set "origin" in wordpress-to-astro.config.json or SITE_ORIGIN, e.g. SITE_ORIGIN=https://example.com')
    return ORIGIN


def user_agent():
    if CFG['crawl'].get('userAgent'):
        return CFG['crawl']['userAgent']
    who = os.environ.get('CRAWLER_USER')
    if not who:
        raise SystemExit('Set CRAWLER_USER (or crawl.userAgent in the config): the crawler must say who is running it. See policies/crawler-identity-and-scope.md')
    return f'wordpress-to-astro (Claude Code; run by {who}; crawling {HOST})'
