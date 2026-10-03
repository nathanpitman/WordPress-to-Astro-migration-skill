#!/usr/bin/env python3
"""Phase 7: build the SEO inventory from the cached ORIGINAL pages.

Writes  .crawl-cache/seo-inventory.json  (per-page facts, used by seo_check.py)
        docs/heading-outlines.json       (per-page heading outline for post-migration comparison)
        public/<robots.txt, every sitemap, feeds>  (verbatim copies of what crawl.py cached)
and prints the aggregate numbers used in docs/seo-inventory.md.

The facts are read with an HTML parser, so they do not depend on which SEO plugin wrote the head or how it
quotes attributes (Yoast, Rank Math, AIOSEO, SEOPress and hand-written themes all work)."""
import glob, hashlib, json, os, re, sys
from html.parser import HTMLParser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O, load_pages, seg
import stamp

SKIP = {'script', 'style', 'noscript', 'template', 'svg'}


class Headings(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []; self.cur = None; self.skip = 0

    def handle_starttag(self, t, a):
        if t in SKIP: self.skip += 1
        if re.fullmatch(r'h[1-6]', t) and not self.skip: self.cur = [int(t[1]), []]

    def handle_endtag(self, t):
        if t in SKIP and self.skip: self.skip -= 1
        if self.cur and t == 'h%d' % self.cur[0]:
            self.out.append([self.cur[0], ' '.join(''.join(self.cur[1]).split())]); self.cur = None

    def handle_data(self, d):
        if self.cur is not None and not self.skip: self.cur[1].append(d)


def headings(html):
    p = Headings(); p.feed(html); return p.out


class Head(HTMLParser):
    """Collects the SEO-relevant head elements in document order."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None; self._in_title = False
        self.meta = []; self.links = []

    def handle_starttag(self, t, attrs):
        a = {k: (v or '') for k, v in attrs}
        if t == 'title': self._in_title = True; self.title = ''
        elif t == 'meta': self.meta.append(a)
        elif t == 'link': self.links.append(a)

    def handle_endtag(self, t):
        if t == 'title': self._in_title = False

    def handle_data(self, d):
        if self._in_title: self.title += d


def _first_meta(meta, name):
    return next((m.get('content') for m in meta if m.get('name', '').lower() == name), None)


def _pairs(meta, key, prefixes):
    return [[m[key], m.get('content', '')] for m in meta if m.get(key, '').lower().startswith(prefixes)]


def _link_sig(a):
    return [[k, a[k]] for k in sorted(a)]


def head_facts(head):
    p = Head(); p.feed(head)
    rel = lambda a: a.get('rel', '').lower().split()
    f = {'lang': None, 'title': p.title}
    f['description'] = _first_meta(p.meta, 'description')
    f['robots'] = _first_meta(p.meta, 'robots')
    canon = [a.get('href') for a in p.links if 'canonical' in rel(a)]
    f['canonical'] = canon[0] if canon else None
    f['hreflang'] = [_link_sig(a) for a in p.links if 'hreflang' in a]
    f['og'] = _pairs([{'property': m.get('property', ''), 'content': m.get('content', '')} for m in p.meta], 'property', ('og:', 'article:'))
    f['twitter'] = _pairs(p.meta, 'name', ('twitter:', 'author'))
    f['alternates'] = [_link_sig(a) for a in p.links if 'alternate' in rel(a) and 'hreflang' not in a]
    f['shortlink'] = [_link_sig(a) for a in p.links if 'shortlink' in rel(a)]
    f['icons'] = [_link_sig(a) for a in p.links if {'icon', 'apple-touch-icon', 'shortcut'} & set(rel(a))]
    f['jsonld'] = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', head, re.S)
    return f


def ld_info(raw):
    body = re.sub(r'^<script[^>]*>|</script>$', '', raw, flags=re.S)
    try:
        j = json.loads(body)
    except Exception as e:
        return {'valid': False, 'error': str(e), 'types': []}
    nodes = j.get('@graph') if isinstance(j, dict) and '@graph' in j else (j if isinstance(j, list) else [j])
    return {'valid': True, 'types': [n.get('@type') for n in nodes if isinstance(n, dict)]}


def page_facts(raw):
    s = seg(raw)
    f = head_facts(s['head'])
    m = re.search(r'<html\b[^>]*\blang=["\']([^"\']*)', s['head'], re.I)
    f['lang'] = m.group(1) if m else None
    f['jsonld_info'] = [ld_info(x) for x in f['jsonld']]
    f['jsonld_sha1'] = [hashlib.sha1(x.encode()).hexdigest() for x in f['jsonld']]
    o = {'header': headings(s['header']), 'main': headings(s['main']), 'footer': headings(s['footer'])}
    f['h1_count'] = sum(1 for r in o.values() for h in r if h[0] == 1)
    return f, o


def main():
    pages = load_pages()
    inv = {}; outlines = {}
    for u, raw in sorted(pages.items()):
        f, o = page_facts(raw)
        inv[u.replace(O, '') or '/'] = f
        outlines[u.replace(O, '') or '/'] = o
    json.dump(inv, open(os.path.join(CACHE, 'seo-inventory.json'), 'w'), indent=1)
    stamp.write_json(os.path.join(ROOT, 'docs/heading-outlines.json'), outlines, indent=1, ensure_ascii=False)

    # ---- verbatim static files: robots.txt, every sitemap (and its stylesheet, if cached), feeds
    copies = {}
    if os.path.exists(os.path.join(CACHE, 'robots.txt')): copies['robots.txt'] = 'robots.txt'
    for sub in ('sitemaps', 'probes'):  # crawl.py saved these under their URL paths: /feed/ -> probes/feed/index.xml
        for root, _, files in os.walk(os.path.join(CACHE, sub)):
            for fn in files:
                src = os.path.relpath(os.path.join(root, fn), CACHE)
                copies[src] = os.path.relpath(os.path.join(root, fn), os.path.join(CACHE, sub))
    pub = os.path.join(ROOT, 'public'); os.makedirs(pub, exist_ok=True)
    for src, dst in copies.items():
        stamp.write(os.path.join(pub, dst), open(os.path.join(CACHE, src), 'rb').read())  # verbatim; a hand-edited copy is kept
    print('copied', len(copies), 'static files to public/')
    stamp.script_ran(7)


if __name__ == '__main__':
    main()
