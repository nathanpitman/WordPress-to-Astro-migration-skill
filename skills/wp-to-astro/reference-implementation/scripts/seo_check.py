#!/usr/bin/env python3
"""Compare the SEO facts of the built pages (dist/) with the inventory taken from the original pages.
Titles, descriptions, canonicals, robots, Open Graph/Twitter, alternates, hreflang, JSON-LD (byte-for-byte via SHA-1)
and heading outlines must be identical. Also checks the verbatim static files in dist/ against public/.
Usage: python3 scripts/seo_check.py   (checks every page that exists in dist/)"""
import hashlib, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, seg
from seo_inventory import head_facts, headings

inv = json.load(open(os.path.join(CACHE, 'seo-inventory.json')))
out = json.load(open(os.path.join(ROOT, 'docs/heading-outlines.json')))
ok = bad = missing = 0
for p, want in inv.items():
    f = os.path.join(ROOT, 'dist', '404.html') if p == '/404/' else os.path.join(ROOT, 'dist', up.unquote(p).strip('/'), 'index.html')
    if not os.path.exists(f): missing += 1; continue
    t = open(f, encoding='utf8').read(); s = seg(t)
    got = head_facts(s['head']); got['lang'] = re.search(r'<html lang="([^"]*)"', s['head']).group(1)
    got['jsonld_sha1'] = [hashlib.sha1(x.encode()).hexdigest() for x in got['jsonld']]
    got = json.loads(json.dumps(got))
    o = {'header': headings(s['header']), 'main': headings(s['main']), 'footer': headings(s['footer'])}
    diffs = [k for k in ('lang', 'title', 'description', 'robots', 'canonical', 'hreflang', 'og', 'twitter', 'alternates', 'shortlink', 'icons', 'jsonld_sha1') if want[k] != got[k]]
    if o != out[p]: diffs.append('headings')
    if diffs: bad += 1; print('DIFF', p, diffs)
    else: ok += 1
print(f'seo check: {ok + bad} pages: {ok} identical, {bad} differ ({missing} not built)')
pub = os.path.join(ROOT, 'public'); sbad = 0
for root, _, files in os.walk(pub):
    for fn in files:
        a = os.path.join(root, fn); b = os.path.join(ROOT, 'dist', os.path.relpath(a, pub))
        if os.path.exists(b) and open(a, 'rb').read() != open(b, 'rb').read(): sbad += 1; print('STATIC DIFF', b)
print('static files differing from public/:', sbad)
sys.exit(1 if bad or sbad else 0)
