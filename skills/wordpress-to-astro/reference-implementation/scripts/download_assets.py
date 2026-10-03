#!/usr/bin/env python3
"""Phase 9, step 2: download every own-domain asset in .crawl-cache/assets-inventory.json to public/<same URL path>.

Files are stored byte-for-byte (no optimisation, no renaming, all size variants kept) and at the SAME path the
markup/CSS already references, so no URL is rewritten. Third-party scripts are not downloaded.
Stylesheets are skipped (already in src/styles). Writes docs/assets-manifest.json."""
import concurrent.futures as cf, hashlib, json, os, sys, time, urllib.parse as up, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O

UA = f"wordpress-to-astro (Claude Code; run by {os.environ['CRAWLER_USER']}; crawling {O.split('//', 1)[1]})"
inv = json.load(open(os.path.join(CACHE, 'assets-inventory.json')))
mf_path = os.path.join(ROOT, 'docs/assets-manifest.json')
manifest = json.load(open(mf_path)) if os.path.exists(mf_path) else {}

def fetch(url):
    p = up.urlsplit(url); local = os.path.join(ROOT, 'public', up.unquote(p.path).lstrip('/'))
    if url in manifest and manifest[url].get('status') == 200 and os.path.exists(local): return url, manifest[url]
    time.sleep(0.15)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=40) as r:
                body = r.read(); ct = r.headers.get('content-type', ''); st = r.status
            os.makedirs(os.path.dirname(local), exist_ok=True); open(local, 'wb').write(body)
            return url, {'status': st, 'bytes': len(body), 'sha1': hashlib.sha1(body).hexdigest(), 'contentType': ct, 'local': os.path.relpath(local, ROOT)}
        except urllib.error.HTTPError as e:
            return url, {'status': e.code, 'error': str(e)}
        except Exception as e:
            err = repr(e); time.sleep(1 + attempt)
    return url, {'status': None, 'error': err}

todo = [u for u, e in inv.items() if e['host'] == O.split('//', 1)[1] and e['kind'] != 'style']
print(len(todo), 'assets to fetch', flush=True)
n = 0
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for url, res in ex.map(fetch, todo):
        e = inv[url]; manifest[url] = {**res, 'kind': e['kind'], 'refs': e['refs'], 'via': e['via'], 'samplePages': e['pages']}
        n += 1
        if n % 100 == 0: print(n, flush=True); json.dump(manifest, open(mf_path, 'w'), indent=0)
json.dump(manifest, open(mf_path, 'w'), indent=0)
ok = sum(1 for m in manifest.values() if m.get('status') == 200); print('done', ok, 'ok of', len(manifest))
bad = {u: m for u, m in manifest.items() if m.get('status') != 200}; print(len(bad), 'failed:'); [print(' ', m.get('status'), u) for u, m in list(bad.items())[:15]]
