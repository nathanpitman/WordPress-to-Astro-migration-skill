"""Shared helpers for the migration scripts. Reads the crawl cache in ../.crawl-cache (not committed)."""
import json, os, re
from config import CFG, ROOT, require_origin

CACHE = os.path.join(ROOT, '.crawl-cache')
O = require_origin()  # production origin, e.g. https://example.com (no trailing slash)

PUBLIC = {}  # internal listing URL -> public URL (with query string)


def _read(key):
    return open(os.path.join(CACHE, 'pages', key + '.html'), encoding='utf8', errors='replace').read()


def load_pages():
    """final URL -> raw cached HTML (200 responses, main domain, no query, deduped), plus the themed 404 and any listing variants."""
    index = json.load(open(os.path.join(CACHE, 'crawl-index.json')))['pages']
    out = {}
    for u, e in index.items():
        if e.get('status') == 200 and '?' not in e['final'] and e['final'] != O and e['final'] not in out:
            out[e['final']] = _read(e['key'])
    ex = os.path.join(CACHE, 'extra-index.json')
    if os.path.exists(ex):  # unlinked main-domain pages found in Phase 2 (own 200 response, same host)
        for u, e in json.load(open(ex)).items():
            if u.startswith(O + '/') and e['final'] == u and e['status'] == 200 and u not in out:
                out[u] = _read(e['key'])
    # the themed 404 template: any unknown URL renders the same page, so one crawled 404 stands in for all
    nf = index.get(O + (os.environ.get('NOT_FOUND_SAMPLE') or CFG['notFoundSample']))
    if nf and nf.get('status') == 404:
        out[O + '/404/'] = _read(nf['key'])
        PUBLIC[O + '/404/'] = O + '/404/'
    from listings import variants, internal_for  # listing variants: keyed by their internal static URL
    for pu, k in variants():
        out[O + internal_for(pu)] = _read(k)
        PUBLIC[O + internal_for(pu)] = pu
    return out


# ---------------------------------------------------------------- splitting a page into regions
def _balanced_end(t, tag, start):
    """Index just past the </tag> that closes the <tag> opening at `start` (handles nesting)."""
    depth, pos = 0, start
    pat = re.compile(r'<(/?)%s(?=[\s>/])[^>]*>' % tag, re.I)
    for m in pat.finditer(t, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    raise ValueError('unclosed <%s>' % tag)


def _first(t, tag, start=0):
    m = re.compile(r'<%s(?=[\s>/])' % tag, re.I).search(t, start)
    if not m:
        raise ValueError('no <%s> landmark; adapt seg() to this theme\'s structure' % tag)
    return m.start(), _balanced_end(t, tag, m.start())


def seg(t):
    """Split a page at its landmarks: head | <body> | pre | <header> | mid | <main> | post | <footer> | tail.
    Needs one <header>, <main> and <footer> (all current block themes and most classic themes emit them);
    other markup is kept in the gaps (pre/mid/post/tail) and carried verbatim."""
    b = re.search(r'<body\b', t, re.I).start(); be = t.index('>', b) + 1
    h, he = _first(t, 'header', be)
    m, me = _first(t, 'main', he)
    f, fe = _first(t, 'footer', me)
    return dict(head=t[:b], bodyopen=t[b:be], pre=t[be:h], header=t[h:he], mid=t[he:m], main=t[m:me], post=t[me:f], footer=t[f:fe], tail=t[fe:])


# ---------------------------------------------------------------- comparison contract
# Per-render values that cannot be reproduced without the site's secrets. Enable by name with "volatileTokens".
MASKS = {
    'wp-nonce': [
        (r'nonce":"[0-9a-f]{10}"', 'nonce":"‹NONCE›"'),
        (r'(name=[\'"]_wpnonce[\'"][^>]*value=[\'"])[0-9a-f]{10}', r'\1‹NONCE›'),
        (r'(name=[\'"]wpforms\[nonce\][\'"][^>]*value=[\'"])[0-9a-f]{10}', r'\1‹NONCE›'),
    ],
    'gravityforms-state': [
        (r'(name=[\'"]state_\d+[\'"][^>]*value=[\'"])[^\'"]*', r'\1‹GFSTATE›'),
        (r'(name=[\'"]gform_currency[\'"][^>]*value=[\'"])[^\'"]*', r'\1‹GFCUR›'),
        (r'input_[0-9a-f]{32}', 'input_‹RECAPTCHA›'),
        (r'(&amp;hash=)[0-9a-f]{6,40}', r'\1‹GFHASH›'),
    ],
}


def _mask_rules():
    rules = []
    for name in CFG['volatileTokens']:
        if name not in MASKS:
            raise SystemExit(f'unknown volatile token set "{name}"; known: {", ".join(MASKS)} (or add your own under "masks")')
        rules += MASKS[name]
    rules += [(m['pattern'], m['replacement']) for m in CFG['masks']]
    return [(re.compile(p), r) for p, r in rules]


_RULES = _mask_rules()


def mask(t):
    for pat, repl in _RULES:
        t = pat.sub(repl, t)
    return t


def norm(t):
    """Whitespace-insignificant comparison form (also drops the TODO(manual) form comments and the approved search script tag we add)."""
    t = re.sub(r'<!-- TODO\(manual\):[^>]*-->', '', t)
    t = re.sub(r'<!-- Static-host search/filter script[^>]*-->\s*<script[^>]*src="/js/site-search\.js"[^>]*></script>', '', t)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'>\s+<', '><', t)
    return t.strip()
