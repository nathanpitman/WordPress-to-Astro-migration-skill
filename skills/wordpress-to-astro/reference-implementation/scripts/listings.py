"""Query-string listing variants (pagination, filters) that a static host cannot serve.

Core WordPress paginates with paths (/page/2/) and archives with paths (/category/news/), and those are ordinary
pages the crawler already caches. Only listings driven by query strings (?page=2, ?topic=news from a plugin or
custom code) need this. Declare them in the config:

    "listings": [ { "base": "/blog/", "params": ["page", "topic"] } ]

Each fetched variant is generated as its own page under /_listing/<base>/<param>/<value>/..., in the order the
params are listed, and the host maps the public URL onto it with the rules in src/data/rewrites.json
(phases/08-search-listings-pagination.md). With no "listings" configured this module does nothing."""
import json, os, urllib.parse as up
from config import CFG
from lib import CACHE, O


def internal_for(public_url):
    """The internal static path for a public listing URL, or None when it is not a configured listing variant."""
    u = up.urlsplit(public_url)
    q = dict(up.parse_qsl(u.query, keep_blank_values=True))
    base = '/' + u.path.strip('/') + '/' if u.path.strip('/') else '/'
    for spec in CFG['listings']:
        if spec['base'] != base or not q:
            continue
        values = {p: q.pop(p) for p in spec['params'] if p in q}
        if q or not values:
            return None  # an unlisted parameter: not generated
        path = '/_listing/' + base.strip('/') + '/'
        for p in spec['params']:
            if p in values:
                v = values[p]
                path += f'{p}/' + (v[:-1] + '--slash' if v.endswith('/') else v) + '/'  # a trailing slash inside a value must stay distinct
        return path
    return None


def variants():
    """[(public_url, cache_key)] for every configured listing variant that was fetched."""
    if not CFG['listings']:
        return []
    out = []
    vp = os.path.join(CACHE, 'variants-index.json')  # variants fetched on purpose in Phase 8
    if os.path.exists(vp):
        out += [(u, e['key']) for u, e in json.load(open(vp)).items() if e.get('status') == 200]
    for u, e in json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages'].items():  # and any the crawl met
        if '?' in u and e.get('status') == 200 and u == e['final']:
            out.append((u, e['key']))
    return [(u, k) for u, k in dict.fromkeys(out) if internal_for(u)]
