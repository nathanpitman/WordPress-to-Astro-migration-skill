#!/usr/bin/env python3
"""Phase 9, step 1: inventory every static asset the site references.

Sources: the verbatim <main> files, the shared header/footer/head/tail fragments, per-page records (SEO/JSON-LD),
the stylesheets in src/styles (url() resolved against the stylesheet's own URL) and the sitemaps.
Writes .crawl-cache/assets-inventory.json  {url: {kind, ext, host, refs: n, via: [...], pages: [...]}}"""
import collections, glob, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O
from config import CFG

HOST = O.split('//', 1)[1]
IMG = {'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'avif', 'ico'}
FONT = {'woff', 'woff2', 'ttf', 'otf', 'eot'}
KIND = {**{e: 'image' for e in IMG}, **{e: 'font' for e in FONT}, 'js': 'script', 'css': 'style', 'pdf': 'document',
        'mp4': 'video', 'webm': 'video', 'mp3': 'audio'}

inv = collections.OrderedDict()

def add(url, via, page):
    url = url.strip().replace('&amp;', '&')
    if url.startswith('//'): url = 'https:' + url
    if not url.startswith('http'): return
    p = up.urlsplit(url)
    ext = p.path.rsplit('.', 1)[-1].lower() if '.' in p.path.split('/')[-1] else ''
    if ext not in KIND: return
    e = inv.setdefault(url, {'kind': KIND[ext], 'ext': ext, 'host': p.netloc, 'refs': 0, 'via': collections.Counter(), 'pages': set()})
    e['refs'] += 1; e['via'][via] += 1
    if page and len(e["pages"]) < 5000: e['pages'].add(page)

def scan_html(text, page):
    text = text.replace('\\/', '/')
    for m in re.finditer(r'<img\b[^>]*>', text):
        t = m.group(0)
        s = re.search(r'\ssrc=["\']([^"\']+)', t)
        if s: add(s.group(1), 'img src', page)
        ss = re.search(r'\ssrcset=["\']([^"\']+)', t)
        if ss:
            for part in ss.group(1).split(','):
                add(part.strip().split(' ')[0], 'img srcset', page)
    for m in re.finditer(r'<source\b[^>]*>', text):
        for a in re.findall(r'(?:src|srcset)=["\']([^"\']+)', m.group(0)):
            for part in a.split(','): add(part.strip().split(' ')[0], 'source', page)
    for m in re.finditer(r'<link\b[^>]*>', text):
        t = m.group(0); h = re.search(r'href=["\']([^"\']+)', t)
        if h and re.search(r'rel=["\'](?:icon|apple-touch-icon|stylesheet|preload|shortcut icon)', t):
            add(h.group(1), 'link ' + re.search(r'rel=["\']([^"\']+)', t).group(1), page)
    for m in re.finditer(r'<meta\b[^>]*(?:og:image|twitter:image|msapplication-TileImage)[^>]*>', text):
        c = re.search(r'content=["\']([^"\']+)', m.group(0))
        if c: add(c.group(1), 'meta image', page)
    for m in re.finditer(r'<script\b[^>]*\ssrc=["\']([^"\']+)', text): add(m.group(1), 'script src', page)
    for m in re.finditer(r'url\(\s*["\']?([^"\')]+)', text): add(m.group(1), 'inline url()', page)
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+\.(?:pdf|docx?|xlsx?|zip))["\']', text, re.I): add(m.group(1), 'a href', page)
    for m in re.finditer(r'<(?:video|audio)\b[^>]*\ssrc=["\']([^"\']+)', text): add(m.group(1), 'media src', page)
    for m in re.finditer(r'"(?:url|contentUrl|thumbnailUrl|logo|image)":\s*"(https?:[^"]+)"', text): add(m.group(1), 'json-ld', page)
    for m in re.finditer(r'<image:loc>([^<]+)', text): add(m.group(1), 'sitemap image', page)
    for m in re.finditer(re.escape(O) + '(?:' + '|'.join(re.escape(p.rstrip('/')) for p in CFG['assets']['prefixes']) + r')/[^\s"\'<>)\\,{}]+?\.(?:jpe?g|png|gif|svg|webp|avif|ico|js|css|pdf|woff2?|ttf|otf|eot)(?=[\s"\'<>)\\,?#&;]|$)', text, re.I): add(m.group(0), 'inline text', page)

def main():
    for f in sorted(glob.glob(os.path.join(ROOT, 'src/content/**/*.html'), recursive=True)):
        scan_html(open(f, encoding='utf8').read(), os.path.relpath(f, os.path.join(ROOT, 'src/content')).replace('.html', ''))
    for f in ('chrome.json', 'head-items.json', 'tail-items.json'):
        d = json.load(open(os.path.join(ROOT, 'src/data', f)))
        for v in (d.values() if isinstance(d, dict) else []):
            if isinstance(v, str): scan_html(v, f)
    for f in glob.glob(os.path.join(ROOT, 'src/data/pages/*.json')):
        r = json.load(open(f))
        for k, patches in r.get('patches', {}).items():  # text that only exists in a per-page patch (e.g. a page-specific header image)
            for _, _, text in patches: scan_html(text, r['path'])
    for f in glob.glob(os.path.join(ROOT, 'src/data/pages/*.json')):
        r = json.load(open(f)); pg = r['path']
        for e in r['head']:
            if isinstance(e, dict) and 'raw' in e: scan_html(e['raw'], pg)
        for it in r['seo']: scan_html(it['raw'], pg)  # og:image, twitter:image and JSON-LD images are found in the raw markup
        for e in r['tail']:
            if isinstance(e, dict): scan_html(e['raw'], pg)
    for f in glob.glob(os.path.join(ROOT, 'public/*sitemap.xml')): scan_html(open(f, encoding='utf8').read(), os.path.basename(f))
    mp = os.path.join(ROOT, 'src/styles/manifest.json')  # written in Phase 6; absent until then
    m = json.load(open(mp)) if os.path.exists(mp) else {'stylesheets': []}
    for s in m['stylesheets']:
        base = O + s['servedPath']
        css = open(os.path.join(ROOT, s['source']), encoding='utf8').read()
        for u in re.findall(r'url\(\s*["\']?([^"\')]+)', css):
            if u.startswith('data:'): continue
            add(up.urljoin(base, u), 'css url() in ' + os.path.basename(s['source']), None)
    out = {u: {**e, 'via': dict(e['via']), 'pages': sorted(e['pages'])} for u, e in inv.items()}
    json.dump(out, open(os.path.join(CACHE, 'assets-inventory.json'), 'w'), indent=1)
    print(len(out), 'distinct asset URLs')
    print(collections.Counter(e['kind'] for e in out.values()))
    print(collections.Counter(e['host'] for e in out.values()).most_common(8))

if __name__ == '__main__':
    main()
