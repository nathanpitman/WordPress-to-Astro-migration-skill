"""Revert hosting-layer output (WP Rocket, Cloudflare) from cached HTML so the remaining markup
is the application's own output. Every transformation is counted so it can be logged in docs/deviations.md.
Reads from .crawl-cache/ (not committed)."""
import re, collections
STATS = collections.Counter()
PH = r"data:image/svg\+xml,%3Csvg%20xmlns='http://www\.w3\.org/2000/svg'%20viewBox='[^']*'%3E%3C/svg%3E"

def cf_decode(h):
    k = int(h[:2], 16)
    return ''.join(chr(int(h[i:i+2], 16) ^ k) for i in range(2, len(h), 2))

def deopt(t):
    n = lambda key, c=1: STATS.update({key: c})
    # --- Cloudflare email obfuscation
    def span(m):
        n('cf-email-text'); return cf_decode(m.group(1))
    t = re.sub(r'<span class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]</span>', span, t)
    def anch_cls(m):  # <a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="..">[email&#160;protected]</a>
        n('cf-email-anchor'); return cf_decode(m.group(2))
    t = re.sub(r'(<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]</a>)', lambda m: f'<a href="mailto:{cf_decode(m.group(2))}">{cf_decode(m.group(2))}</a>', t)
    def hrefsub(m):
        n('cf-email-href'); return f'href="{cf_decode(m.group(1))}"'
    t = re.sub(r'href="/cdn-cgi/l/email-protection#([0-9a-f]+)"', hrefsub, t)
    # --- Cloudflare challenge/jsd injected script
    t, c = re.subn(r"\s*<script>\(function\(\)\{function c\(\)\{var b=a\.contentDocument.*?</script>", '', t, flags=re.S); n('cf-jsd-script', c)
    # --- Rocket lazyload images: placeholder src + data-lazy-*
    def img(m):
        tag = m.group(0)
        if 'data-lazy-src' not in tag: return tag
        real = re.search(r'data-lazy-src="([^"]*)"', tag).group(1)
        tag = re.sub(r'\s+data-lazy-src="[^"]*"', '', tag)
        tag = re.sub(r'src="'+PH+'"', f'src="{real}"', tag, count=1)
        tag = tag.replace(' data-lazy-srcset=', ' srcset=').replace(' data-lazy-sizes=', ' sizes=')
        n('rocket-lazy-img'); return tag
    t = re.sub(r'<img\b[^>]*>', img, t)
    # --- other Rocket attributes / elements
    t, c = re.subn(r'data-rocket-location-hash="[0-9a-f]+"', '', t); n('rocket-location-hash', c)  # keeps the surrounding spaces: origin has an empty attribute slot (double space)
    t, c = re.subn(r'(<img\b[^>]*?/>)<noscript><img\b[^>]*?/></noscript>', r'\1', t); n('rocket-noscript-img', c)
    if 'data-rocket-preload' in t:
        t, c = re.subn(r'(<img\b[^>]*?) fetchpriority="high"', r'\1', t); n('rocket-fetchpriority', c)
    t, c = re.subn(r'data-wpr-lazyrender="1"', '', t); n('rocket-lazyrender-attr', c)
    for pat, key in [
        (r'<script data-name="wpr-wpr-beacon"[^>]*></script>', 'rocket-beacon-js'),
        (r'<script data-cfasync="false" src="/cdn-cgi/scripts/[^"]*email-decode\.min\.js"></script>', 'cf-email-decode-js'),
        (r'<link data-rocket-prefetch [^>]*>\s*', 'rocket-dns-prefetch'),
        (r'<link rel="preload" data-rocket-preload [^>]*>\s*', 'rocket-preload'),
        (r'<style id="rocket-lazyload-nojs-css">.*?</style>\s*', 'rocket-nojs-css'),
        (r'<style id="rocket-lazyrender-inline-css">.*?</style>\s*', 'rocket-lazyrender-css'),
        (r'<meta name="generator" content="WP Rocket[^>]*>', 'rocket-generator-meta'),
        (r'<script id="rocket-[a-z-]*js-[a-z]*">.*?</script>\s*', 'rocket-inline-script'),
        (r'<script id="rocket-[a-z-]*js-[a-z]*"[^>]*>.*?</script>\s*', 'rocket-inline-script2'),
        (r'<script>window\.lazyLoadOptions=.*?</script>', 'rocket-lazyload-options'),
        (r'<script data-no-minify="1" async src="[^"]*wp-rocket[^"]*lazyload\.min\.js"></script>', 'rocket-lazyload-js'),
        (r'\s*<script>var rocket_beacon_data = .*?</script>', 'rocket-beacon'),
        (r'\s*<!-- Performance optimized by Redis Object Cache[^>]*-->', 'redis-comment'),
        (r'\s*<!-- This website is like a Rocket[^>]*-->', 'rocket-comment'),
    ]:
        t, c = re.subn(pat, '', t, flags=re.S); n(key, c)
    return t
