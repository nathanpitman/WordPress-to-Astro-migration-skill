#!/usr/bin/env python3
"""Phase 11: errors on the ORIGINAL site (record only). Writes .crawl-cache/errors.json; docs/errors.md is written from it."""
import collections, glob, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O, load_pages
from config import CFG
import deopt, stamp

SITEMAPS = [f for f in sorted(glob.glob(os.path.join(ROOT, 'public', '**', '*sitemap*.xml'), recursive=True)) if '<sitemapindex' not in open(f, encoding='utf8').read()]  # page sitemaps only
idx = json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages']
out = {}

def short(u): return u.replace(O, '') or '/'

# ---- link graph from the crawl (internal links only)
linkers = collections.defaultdict(lambda: collections.Counter())  # target url -> {page: n}
for u, e in idx.items():
    if e.get('status') != 200: continue
    for kind, l in e.get('links', []):
        if kind == 'a': linkers[l][e['final']] += 1

# ---- 1. 4xx/5xx internal links
broken = []
for u, e in idx.items():
    st = e.get('status')
    if st and st >= 400 and u != O + CFG['notFoundSample']:  # the deliberate 404 probe is not a broken link
        pages = linkers.get(u, {})
        broken.append({'url': u, 'status': st, 'links': sum(pages.values()), 'pages': sorted(pages)[:6], 'npages': len(pages)})
out['broken'] = sorted(broken, key=lambda b: -b['links'])

# ---- 2. redirects: chains, loops, internal links to redirecting URLs
redir = []
for u, e in idx.items():
    ch = e.get('chain', [])
    if len(ch) > 1 or (ch and ch[0]['status'] in (301, 302, 307, 308)):
        pages = linkers.get(u, {})
        redir.append({'from': u, 'to': ch[-1].get('location') or e.get('final'), 'hops': [c['status'] for c in ch], 'links': sum(pages.values()), 'npages': len(pages), 'pages': sorted(pages)[:4]})
out['redirects'] = sorted(redir, key=lambda r: -r['links'])
seen_final = collections.Counter(e['final'] for e in idx.values() if e.get('chain') and len(e['chain']) > 1)
out['loops'] = [u for u, e in idx.items() if e.get('error') or (e.get('chain') and len(e['chain']) >= 8)]

# ---- 3. mixed content / insecure references, 4. fragments, 5. canonicals (from the cached HTML)
pages = load_pages()
mixed = collections.Counter(); mixed_pages = collections.defaultdict(set)
frag_bad = collections.defaultdict(set)
ids_by_path = {}
texts = {}
for u, raw in pages.items():
    t = deopt.deopt(raw); texts[u] = t
    ids_by_path[up.unquote(u.replace(O, '')).rstrip('/') or '/'] = set(re.findall(r'\sid=["\']([^"\']+)', t)) | set(re.findall(r'<a[^>]*\sname=["\']([^"\']+)', t))
NS = ('http://www.w3.org/', 'http://schema.org', 'http://purl.org', 'http://wellformedweb.org', 'http://www.sitemaps.org', 'http://www.google.com/schemas')
for u, t in texts.items():
    pg = u.replace(O, '') or '/'
    body = t.replace('\\/', '/')
    for m in re.finditer(r'(src|href|action|srcset|content|data-[a-z-]+)=["\'](http://[^"\']+)', body):
        if m.group(2).startswith(NS) or m.group(1) == 'content' and not m.group(2).lower().endswith(('.jpg', '.png', '.svg', '.webp')): continue
        mixed[(m.group(1), m.group(2)[:100])] += 1; mixed_pages[(m.group(1), m.group(2)[:100])].add(pg)
    for m in re.finditer(r'url\(\s*["\']?(http://[^"\')]+)', body): mixed[('css url()', m.group(1)[:100])] += 1; mixed_pages[('css url()', m.group(1)[:100])].add(pg)
    here = ids_by_path.get(up.unquote(pg).rstrip('/') or '/', set())
    for m in re.finditer(r'<a\b[^>]*\shref=["\']([^"\']*)#([^"\']+)["\']', body):
        base, frag = m.group(1), up.unquote(m.group(2))
        if base.startswith(('mailto:', 'tel:', 'javascript:')) or not frag: continue
        if base.startswith('http') and not base.startswith(O): continue
        target = (up.urlsplit(base).path if base else pg)
        key = up.unquote(target).rstrip('/') or '/'
        if not base or key == (up.unquote(pg).rstrip('/') or '/'): ids = here
        else: ids = ids_by_path.get(key)
        if ids is None: continue  # target page not in the cache (redirects/external)
        if frag not in ids and not frag.startswith(('!', '/')): frag_bad[(key, frag)].add(pg)
out['mixed'] = [{'attr': k[0], 'url': k[1], 'n': n, 'pages': sorted(mixed_pages[k])[:4], 'npages': len(mixed_pages[k])} for k, n in mixed.most_common()]
out['fragments'] = [{'target': k[0], 'fragment': k[1], 'pages': sorted(v)[:5], 'npages': len(v)} for k, v in sorted(frag_bad.items(), key=lambda kv: -len(kv[1]))]

# ---- canonicals vs status
status_by_final = {}
for u, e in idx.items():
    if e.get('status'): status_by_final[up.unquote(e['final'])] = e['status']; status_by_final[up.unquote(u)] = e['status']
canon = json.load(open(os.path.join(CACHE, 'seo-inventory.json')))
cbad = []; cnoindex = collections.Counter()
for p, f in canon.items():
    c = f.get('canonical')
    if not c: continue
    cu = up.unquote(c); st = status_by_final.get(cu) or status_by_final.get(cu.rstrip('/') + '/')
    target_path = cu.replace(O, '')
    tf = canon.get(target_path) or canon.get(up.unquote(target_path))
    if st is None: cbad.append({'page': p, 'canonical': c, 'status': 'not crawled'})
    elif st != 200: cbad.append({'page': p, 'canonical': c, 'status': st})
    if tf and tf.get('robots') and 'noindex' in tf['robots'] and p != target_path: cnoindex[(target_path)] += 1
out['canonicalBad'] = cbad
out['canonicalToNoindex'] = dict(cnoindex)

# ---- sitemap URLs that fail
sm = []
all_locs = []
for path in SITEMAPS:
    n = os.path.relpath(path, os.path.join(ROOT, 'public'))
    locs = re.findall(r'<loc>([^<]+)</loc>', open(path, encoding='utf8').read())
    all_locs += locs
    for u in locs:
        e = idx.get(u) or idx.get(up.unquote(u)) or next((v for k, v in idx.items() if up.unquote(k) == up.unquote(u)), None)
        if not e: sm.append({'sitemap': n, 'url': u, 'status': 'not crawled'}); continue
        if e.get('status') != 200 or len(e.get('chain', [])) > 1: sm.append({'sitemap': n, 'url': u, 'status': e.get('chain', [{}])[0].get('status'), 'to': e['final']})
out['sitemapBad'] = sm
dupe = collections.Counter(all_locs)
out['sitemapDuplicates'] = [u for u, c in dupe.items() if c > 1]
json.dump(out, open(os.path.join(CACHE, 'errors.json'), 'w'), indent=1, default=list)
print({k: (len(v) if hasattr(v, '__len__') else v) for k, v in out.items()})
stamp.script_ran(11)
