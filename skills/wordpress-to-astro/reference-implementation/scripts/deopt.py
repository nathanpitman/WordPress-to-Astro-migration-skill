"""Revert hosting-layer output from cached HTML so the remaining markup is the application's own output.

Each layer is one function in LAYERS, keyed by the name used in `hostingLayers` in the config (default: every
layer here). A layer must be safe to run on a page that does not use it. Every transformation is counted in
STATS so it can be logged in docs/deviations.md.

Included: `cloudflare` (email obfuscation, injected challenge script) and `wp-rocket` (lazy-load placeholders,
injected attributes, scripts, styles and comments). Other optimisers (LiteSpeed Cache, W3 Total Cache,
Autoptimize, SG Optimizer, ...) rewrite pages differently: add a function here for the stack found in Phase 0,
following the pattern below, and list its name in the config. Reads from .crawl-cache/ (not committed).
"""
import re, collections
from config import CFG

STATS = collections.Counter()


def _count(key, c=1):
    STATS.update({key: c})


def _strip(t, patterns):
    for pat, key in patterns:
        t, c = re.subn(pat, '', t, flags=re.S)
        _count(key, c)
    return t


# ---------------------------------------------------------------- Cloudflare
def _cf_decode(h):
    k = int(h[:2], 16)
    return ''.join(chr(int(h[i:i + 2], 16) ^ k) for i in range(2, len(h), 2))


def cloudflare(t):
    """Email obfuscation (data-cfemail / email-protection links) and the injected challenge script."""
    def span(m):
        _count('cf-email-text'); return _cf_decode(m.group(1))
    t = re.sub(r'<span class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]</span>', span, t)

    def anchor(m):
        _count('cf-email-anchor'); e = _cf_decode(m.group(1)); return f'<a href="mailto:{e}">{e}</a>'
    t = re.sub(r'<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]</a>', anchor, t)

    def href(m):
        _count('cf-email-href'); return f'href="{_cf_decode(m.group(1))}"'
    t = re.sub(r'href="/cdn-cgi/l/email-protection#([0-9a-f]+)"', href, t)
    return _strip(t, [
        (r'\s*<script>\(function\(\)\{function c\(\)\{var b=a\.contentDocument.*?</script>', 'cf-jsd-script'),
        (r'<script data-cfasync="false" src="/cdn-cgi/scripts/[^"]*email-decode\.min\.js"></script>', 'cf-email-decode-js'),
    ])


# ---------------------------------------------------------------- WP Rocket
_PLACEHOLDER = r"data:image/svg\+xml,%3Csvg%20xmlns='http://www\.w3\.org/2000/svg'%20viewBox='[^']*'%3E%3C/svg%3E"


def wp_rocket(t):
    """Lazy-load placeholders (src and data-lazy-*), injected attributes, preload/prefetch links, inline styles, scripts and comments."""
    def img(m):
        tag = m.group(0)
        if 'data-lazy-src' not in tag:
            return tag
        real = re.search(r'data-lazy-src="([^"]*)"', tag).group(1)
        tag = re.sub(r'\s+data-lazy-src="[^"]*"', '', tag)
        tag = re.sub(r'src="' + _PLACEHOLDER + '"', f'src="{real}"', tag, count=1)
        tag = tag.replace(' data-lazy-srcset=', ' srcset=').replace(' data-lazy-sizes=', ' sizes=')
        _count('rocket-lazy-img'); return tag
    t = re.sub(r'<img\b[^>]*>', img, t)
    # keeps the surrounding spaces: the origin has an empty attribute slot (double space), which the comparison ignores
    t, c = re.subn(r'data-rocket-location-hash="[0-9a-f]+"', '', t); _count('rocket-location-hash', c)
    t, c = re.subn(r'(<img\b[^>]*?/>)<noscript><img\b[^>]*?/></noscript>', r'\1', t); _count('rocket-noscript-img', c)
    if 'data-rocket-preload' in t:
        t, c = re.subn(r'(<img\b[^>]*?) fetchpriority="high"', r'\1', t); _count('rocket-fetchpriority', c)
    t, c = re.subn(r'data-wpr-lazyrender="1"', '', t); _count('rocket-lazyrender-attr', c)
    return _strip(t, [
        (r'<script data-name="wpr-wpr-beacon"[^>]*></script>', 'rocket-beacon-js'),
        (r'<link data-rocket-prefetch [^>]*>\s*', 'rocket-dns-prefetch'),
        (r'<link rel="preload" data-rocket-preload [^>]*>\s*', 'rocket-preload'),
        (r'<style id="rocket-lazyload-nojs-css">.*?</style>\s*', 'rocket-nojs-css'),
        (r'<style id="rocket-lazyrender-inline-css">.*?</style>\s*', 'rocket-lazyrender-css'),
        (r'<meta name="generator" content="WP Rocket[^>]*>', 'rocket-generator-meta'),
        (r'<script id="rocket-[a-z-]*js-[a-z]*"[^>]*>.*?</script>\s*', 'rocket-inline-script'),
        (r'<script>window\.lazyLoadOptions=.*?</script>', 'rocket-lazyload-options'),
        (r'<script data-no-minify="1" async src="[^"]*wp-rocket[^"]*lazyload\.min\.js"></script>', 'rocket-lazyload-js'),
        (r'\s*<script>var rocket_beacon_data = .*?</script>', 'rocket-beacon'),
        (r'\s*<!-- Performance optimized by Redis Object Cache[^>]*-->', 'redis-comment'),
        (r'\s*<!-- This website is like a Rocket[^>]*-->', 'rocket-comment'),
    ])


# name -> function. Add your own layer here and list its name under "hostingLayers" in the config.
LAYERS = {'cloudflare': cloudflare, 'wp-rocket': wp_rocket}


def _enabled():
    names = CFG['hostingLayers']
    if names is None:
        return list(LAYERS.values())
    out = []
    for n in names:
        n = n['name'] if isinstance(n, dict) else n
        if n not in LAYERS:
            raise SystemExit(f'no reversal for hosting layer "{n}" in deopt.py; add one to LAYERS (known: {", ".join(LAYERS)})')
        out.append(LAYERS[n])
    return out


_LAYERS = _enabled()


def deopt(t):
    for layer in _LAYERS:
        t = layer(t)
    return t
