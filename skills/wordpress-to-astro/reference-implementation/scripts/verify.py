#!/usr/bin/env python3
"""Compare the built Astro pages (dist/) with the cached originals (after the documented hosting-layer
reversal in deopt.py). Volatile per-render tokens are masked and whitespace is normalised on both sides.
Usage: python3 scripts/verify.py [--show N]   (checks every page that exists in dist/)"""
import difflib, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, O, load_pages, mask, norm
import deopt

def dist_file(url):
    p = up.unquote(url.replace(O, '')).strip('/')
    if p == '404': return os.path.join(ROOT, 'dist', '404.html')  # themed 404 page is emitted as dist/404.html
    return os.path.join(ROOT, 'dist', p, 'index.html')

def prep(t):
    return norm(mask(t))

def main():
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 3
    pages = load_pages(); ok = bad = missing = 0; diffs = []
    for u, raw in sorted(pages.items()):
        f = dist_file(u)
        if not os.path.exists(f):
            missing += 1; continue
        a = prep(deopt.deopt(raw)); b = prep(open(f, encoding='utf8').read())
        # the live pages end after </html>; Astro adds nothing, so compare as-is
        if a == b: ok += 1
        else:
            bad += 1; diffs.append((u, a, b))
    print(f'verified {ok + bad} pages: {ok} identical, {bad} differ ({missing} not built)')
    for u, a, b in diffs[:show]:
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        print('\n==', u.replace(O, ''), len(a), len(b))
        n = 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                print(' ', tag, repr(a[max(0, i1 - 40):i2 + 40][:240]), '|||', repr(b[max(0, j1 - 40):j2 + 40][:240])); n += 1
                if n >= 6: break
    return bad

if __name__ == '__main__':
    sys.exit(1 if main() else 0)
