"""Shared helpers for the migration scripts. Reads the crawl cache in ../.crawl-cache (not committed)."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, '.crawl-cache')
O = os.environ.get('SITE_ORIGIN', '').rstrip('/')  # e.g. https://example.com (no trailing slash)
if not O: raise SystemExit('Set SITE_ORIGIN, e.g. SITE_ORIGIN=https://example.com')

def load_pages():
    """final URL -> raw cached HTML (200 responses, main domain, no query, deduped)."""
    i = json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages']
    out = {}
    for u, e in i.items():
        if e.get('status') == 200 and '?' not in e['final'] and e['final'] != O and e['final'] not in out:
            out[e['final']] = open(os.path.join(CACHE, 'pages', e['key'] + '.html'), encoding='utf8', errors='replace').read()
    ex = os.path.join(CACHE, 'extra-index.json')
    if os.path.exists(ex):  # unlinked main-domain pages found in Phase 2 (own 200 response, same host)
        for u, e in json.load(open(ex)).items():
            if u.startswith(O + '/') and e['final'] == u and e['status'] == 200 and u not in out:
                out[u] = open(os.path.join(CACHE, 'pages', e['key'] + '.html'), encoding='utf8', errors='replace').read()
    ci = json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages']  # the themed 404 template (any unknown URL renders the same page)
    nf = ci.get(O + os.environ.get('NOT_FOUND_SAMPLE', '/this-page-does-not-exist/'))  # a crawled URL that returned 404; its body is the themed 404 template
    if nf and nf.get('status') == 404:
        out[O + '/404/'] = open(os.path.join(CACHE, 'pages', nf['key'] + '.html'), encoding='utf8', errors='replace').read()
        PUBLIC[O + '/404/'] = O + '/404/'
    for pu, k in __import__('listings').variants():  # listing variants: keyed by their internal static URL
        out[O + __import__('listings').internal_for(pu)] = open(os.path.join(CACHE, 'pages', k + '.html'), encoding='utf8', errors='replace').read()
        PUBLIC[O + __import__('listings').internal_for(pu)] = pu
    return out

PUBLIC = {}  # internal listing URL -> public URL (with query string)

def seg(t):
    b = t.index('<body'); be = t.index('>', b) + 1
    h = t.index('<header'); he = t.index('</header>') + 9
    m = t.find('<main'); me = t.find('</main>') + 7
    f = t.index('<footer'); fe = t.index('</footer>') + 9
    return dict(head=t[:b], bodyopen=t[b:be], pre=t[be:h], header=t[h:he], mid=t[he:m], main=t[m:me], post=t[me:f], footer=t[f:fe], tail=t[fe:])

def mask(t):
    """Per-render random/derived tokens that cannot be reproduced without the WordPress/Laravel secrets."""
    t = re.sub(r'&quot;id&quot;:&quot;[A-Za-z0-9]{20}&quot;', '&quot;id&quot;:&quot;‹LWID›&quot;', t)
    t = re.sub(r'checksum&quot;:&quot;[0-9a-f]{64}&quot;', 'checksum&quot;:&quot;‹LWSUM›&quot;', t)
    t = re.sub(r'wire:id="[A-Za-z0-9]{20}"', 'wire:id="‹LWID›"', t)
    t = re.sub(r'&quot;path&quot;:&quot;[^&]*&quot;', '&quot;path&quot;:&quot;‹PATH›&quot;', t)
    t = re.sub(r'nonce":"[0-9a-f]{10}"', 'nonce":"‹NONCE›"', t)
    # Gravity Forms per-render values inside forms
    t = re.sub(r'(name=[\'"]state_\d+[\'"][^>]*value=[\'"])[^\'"]*', r'\1‹GFSTATE›', t)
    t = re.sub(r'(name=[\'"]gform_currency[\'"][^>]*value=[\'"])[^\'"]*', r'\1‹GFCUR›', t)
    t = re.sub(r'input_[0-9a-f]{32}', 'input_‹RECAPTCHA›', t)
    t = re.sub(r'(&amp;hash=)[0-9a-f]{6,40}', r'\1‹GFHASH›', t)
    return t

def norm(t):
    """Whitespace-insignificant comparison form (also drops the TODO(manual) form comments we add)."""
    t = re.sub(r'<!-- TODO\(manual\):[^>]*-->', '', t)
    t = re.sub(r'<!-- Replaces Livewire search/filter/load-more[^>]*-->\s*<script src="/js/site-search\.js" defer></script>', '', t)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'>\s+<', '><', t)
    return t.strip()
