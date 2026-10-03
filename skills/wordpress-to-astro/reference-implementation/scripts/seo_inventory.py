#!/usr/bin/env python3
"""Phase 7: build the SEO inventory from the cached ORIGINAL pages.

Writes  .crawl-cache/seo-inventory.json  (per-page facts, used by seo_check.py)
        docs/heading-outlines.json       (per-page heading outline for post-migration comparison)
        src/data/redirects.json          (redirects to reproduce at cutover)
        public/{robots.txt,sitemap_index.xml,*-sitemap.xml,main-sitemap.xsl,feed,comments/feed}  (verbatim copies)
and prints the aggregate numbers used in docs/seo-inventory.md."""
import collections, hashlib, json, os, re, shutil, sys, urllib.parse as up
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


def head_facts(head):
    f = {}
    f['lang'] = None
    m = re.search(r'<title>(.*?)</title>', head, re.S); f['title'] = m.group(1) if m else None
    m = re.search(r'<meta name="description" content="([^"]*)"', head); f['description'] = m.group(1) if m else None
    m = re.search(r"<meta name='robots' content='([^']*)'", head); f['robots'] = m.group(1) if m else None
    m = re.search(r'<link rel="canonical" href="([^"]*)"', head); f['canonical'] = m.group(1) if m else None
    f['hreflang'] = re.findall(r'<link[^>]*hreflang[^>]*>', head)
    f['og'] = re.findall(r'<meta property="((?:og|article):[^"]+)" content="([^"]*)"', head)
    f['twitter'] = re.findall(r'<meta name="((?:twitter:|author)[^"]*)" content="([^"]*)"', head)
    f['alternates'] = re.findall(r'<link rel="alternate"[^>]*>', head)
    f['shortlink'] = re.findall(r"<link rel='shortlink'[^>]*>", head)
    f['icons'] = re.findall(r'<link rel="(?:icon|apple-touch-icon)"[^>]*>', head)
    f['jsonld'] = re.findall(r'<script type="application/ld\+json"[^>]*>.*?</script>', head, re.S)
    return f


def ld_info(raw):
    body = re.sub(r'^<script[^>]*>|</script>$', '', raw, flags=re.S)
    try:
        j = json.loads(body)
    except Exception as e:
        return {'valid': False, 'error': str(e), 'types': []}
    nodes = j.get('@graph') if isinstance(j, dict) and '@graph' in j else [j]
    return {'valid': True, 'types': [n.get('@type') for n in nodes if isinstance(n, dict)]}


def main():
    pages = load_pages()
    inv = {}; outlines = {}
    for u, raw in sorted(pages.items()):
        s = seg(raw)
        f = head_facts(s['head'])
        f['lang'] = re.search(r'<html lang="([^"]*)"', s['head']).group(1)
        f['jsonld_info'] = [ld_info(x) for x in f['jsonld']]
        f['jsonld_sha1'] = [hashlib.sha1(x.encode()).hexdigest() for x in f['jsonld']]
        o = {'header': headings(s['header']), 'main': headings(s['main']), 'footer': headings(s['footer'])}
        f['h1_count'] = sum(1 for r in o.values() for h in r if h[0] == 1)
        inv[u.replace(O, '') or '/'] = f
        outlines[u.replace(O, '') or '/'] = o
    json.dump(inv, open(os.path.join(CACHE, 'seo-inventory.json'), 'w'), indent=1)
    stamp.write_json(os.path.join(ROOT, 'docs/heading-outlines.json'), outlines, indent=1, ensure_ascii=False)

    # ---- verbatim static files
    pub = os.path.join(ROOT, 'public'); os.makedirs(pub, exist_ok=True)
    copies = {'robots.txt': 'robots.txt', 'sitemaps/sitemap_index.xml': 'sitemap_index.xml', 'sitemaps/post-sitemap.xml': 'post-sitemap.xml',
              'sitemaps/page-sitemap.xml': 'page-sitemap.xml', 'sitemaps/course-sitemap.xml': 'course-sitemap.xml',
              'probes/main-sitemap.xsl': 'main-sitemap.xsl', 'probes/feed.xml': 'feed/index.xml', 'probes/feed-comments.xml': 'comments/feed/index.xml'}
    for src, dst in copies.items():
        d = os.path.join(pub, dst)
        stamp.write(d, open(os.path.join(CACHE, src), 'rb').read())  # verbatim; a hand-edited copy is kept
    print('copied', len(copies), 'static files to public/')
    stamp.script_ran(7)


if __name__ == '__main__':
    main()
