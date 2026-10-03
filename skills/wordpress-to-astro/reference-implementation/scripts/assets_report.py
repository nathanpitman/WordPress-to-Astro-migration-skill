#!/usr/bin/env python3
"""Phase 9, step 3: add ownership to docs/assets-manifest.json and write src/data/asset-content-types.json.

Ownership (how the skill's public/images/<type>/<slug>/ layout WOULD group them; files stay at their original paths):
  global        used by the shared header/footer/head/tail, by the stylesheets, or by 20+ pages
  courses/<slug>, articles/<slug>, pages/<slug>   used by exactly one content page (listings, home, category
                landing pages and sitemaps are not counted as owners)
  shared        used by several content pages"""
import collections, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O

inv = json.load(open(os.path.join(CACHE, 'assets-inventory.json')))
mp = os.path.join(ROOT, 'docs/assets-manifest.json'); m = json.load(open(mp))
LISTING = re.compile(r'^(index|courses|articles|_listing/.*|.*-sitemap|head-items\.json|tail-items\.json|chrome\.json)$')
def group(page):
    if page.startswith('courses/'): return page
    if page.startswith('articles/'): return page
    return 'pages/' + page
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
    exp = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext)
    if exp and exp != ct: ctypes['/' + up.unquote(up.urlsplit(u).path).lstrip('/')] = ct
json.dump(m, open(mp, 'w'), indent=0)
json.dump({'description': 'Files whose real type differs from their extension. The live site serves WebP data (Content-Type: image/webp, Vary: Accept) at these .jpg/.png URLs; a host should send the listed Content-Type to match.', 'contentTypes': ctypes},
          open(os.path.join(ROOT, 'src/data/asset-content-types.json'), 'w'), indent=0)
print(counts, len(ctypes), 'content-type overrides')
