"""Listing variants (pagination + category filter) of /courses/ and /articles/.

The live site renders these server-side from query strings (?page=N, ?course_category=slug). A static host
ignores query strings, so each variant is generated as its own page under /_listing/… and the host maps the
public URL onto it with the rules in src/data/rewrites.json."""
import json, os, urllib.parse as up
from lib import CACHE, O

def internal_for(public_url):
    u = up.urlsplit(public_url); q = dict(up.parse_qsl(u.query, keep_blank_values=True))
    base = u.path.strip('/')
    if base not in ('courses', 'articles') or not q: return None
    page = q.pop('page', None); cat = q.pop('course_category', None)
    if q: return None
    p = f'/_listing/{base}/'
    if cat is not None:
        p += 'category/' + (cat[:-1] + '--slash' if cat.endswith('/') else cat) + '/'
    if page is not None: p += f'page/{page}/'
    return p

def variants():
    """[(public_url, cache_key)] for every listing variant fetched."""
    out = []
    v = json.load(open(os.path.join(CACHE, 'variants-index.json')))
    out += [(u, e['key']) for u, e in v.items() if e['status'] == 200]
    ci = json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages']
    for u, e in ci.items():
        if '?course_category=' in u and e.get('status') == 200 and u == e['final']:
            out.append((u, e['key']))
    return list(dict.fromkeys(out))
