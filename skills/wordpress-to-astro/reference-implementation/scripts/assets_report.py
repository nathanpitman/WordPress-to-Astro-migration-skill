#!/usr/bin/env python3
"""Phase 9, step 3: add ownership to docs/assets-manifest.json and write src/data/asset-content-types.json.

Ownership (how the skill's public/images/<type>/<slug>/ layout WOULD group them; files stay at their original paths):
  global        used by the shared header/footer/head/tail, by the stylesheets, or by 20+ pages
  <section>/<slug>   used by exactly one content page under /<section>/ (for example blog/<slug>), or pages/<slug> for
                top-level pages (listings, home, archives and sitemaps are not counted as owners)
  shared        used by several content pages"""
import collections, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O
import stamp

inv = json.load(open(os.path.join(CACHE, 'assets-inventory.json')))
mp = os.path.join(ROOT, 'docs/assets-manifest.json'); m = json.load(open(mp))
LISTING = re.compile(r'^(index|_listing/.*|.*sitemap.*|head-items\.json|tail-items\.json|chrome\.json)$')
def group(page):
    return page if '/' in page else 'pages/' + page  # nested content (blog/hello-world) keeps its section
counts = collections.Counter(); ctypes = {}
for u, e in m.items():
    pages = set(inv[u]['pages']); chrome = {p for p in pages if p.endswith('.json')}
    content = {p for p in pages if not LISTING.match(p)}
    css_ref = any(v.startswith('css url()') or v in ('link icon', 'link apple-touch-icon', 'meta image') for v in inv[u]['via'])
    if chrome or inv[u]['kind'] in ('font', 'script') or (css_ref and not content) or len(pages) >= 20: own = 'global'
    elif len(content) == 1: own = group(next(iter(content)))
    elif len(content) == 0: own = 'global' if not pages else 'shared'
    else: own = 'shared'
    e['ownership'] = own; e['pageCount'] = len(pages)
    counts['global' if own == 'global' else 'shared' if own == 'shared' else own.split('/')[0]] += 1
    ext = u.split('?')[0].rsplit('.', 1)[-1].lower(); ct = e['contentType'].split(';')[0]
    exp = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp', 'avif': 'image/avif', 'svg': 'image/svg+xml'}.get(ext)
    if exp and exp != ct: ctypes['/' + up.unquote(up.urlsplit(u).path).lstrip('/')] = ct
stamp.write_json(mp, m, indent=0)
stamp.write_json(os.path.join(ROOT, 'src/data/asset-content-types.json'), {'description': 'Files whose real type differs from their extension (for example WebP served at .jpg/.png URLs by an image-optimisation plugin or CDN). A host should send the listed Content-Type to match.', 'contentTypes': ctypes}, indent=0)
stamp.script_ran(9)
print(counts, len(ctypes), 'content-type overrides')
