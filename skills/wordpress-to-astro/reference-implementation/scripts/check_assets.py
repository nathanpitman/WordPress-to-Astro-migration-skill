#!/usr/bin/env python3
"""Every own-domain asset URL under the configured prefixes (default /wp-content/ and /wp-includes/) found in the built HTML and CSS must exist in dist/ at the same path.
Usage: npm run build && python3 scripts/check_assets.py"""
import glob, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CFG, ROOT, ORIGIN, require_origin
require_origin()
PREFIXES = '|'.join(re.escape(p.rstrip('/')) for p in CFG['assets']['prefixes'])
D = os.path.join(ROOT, 'dist')
pat = re.compile(r'(?:' + re.escape(ORIGIN) + r')?((?:' + PREFIXES + r')/[^\s"\'<>)\\,{}]+?\.(?:jpe?g|png|gif|svg|webp|avif|ico|js|css|pdf|woff2?|ttf|otf|eot))(?=[\s"\'<>)\\,?#&;]|$)', re.I)
missing = {}; seen = set(); files = 0
for f in glob.glob(D + '/**/*.html', recursive=True) + glob.glob(D + '/**/*.css', recursive=True):
    base = '/' + os.path.relpath(f, D)
    t = open(f, encoding='utf8', errors='replace').read().replace('\\/', '/')
    files += 1
    cands = set(m.group(1) for m in pat.finditer(t))
    if f.endswith('.css'):  # relative url() inside a stylesheet
        for u in re.findall(r'url\(\s*["\']?([^"\')]+)', t):
            if not u.startswith(('data:', 'http', '/')): cands.add(up.urljoin(base, u).split('?')[0].split('#')[0])
    for c in cands:
        c = up.unquote(c).split('?')[0]; seen.add(c)
        if not os.path.exists(D + c): missing.setdefault(c, set()).add(base)
print(f'{files} files scanned, {len(seen)} distinct asset paths, {len(missing)} missing in dist/')
for c, p in list(missing.items())[:20]: print(' ', c, '<-', sorted(p)[:2])
sys.exit(1 if missing else 0)
