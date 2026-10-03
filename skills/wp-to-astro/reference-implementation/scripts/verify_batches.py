#!/usr/bin/env python3
"""Build + verify every page in small batches, deleting dist/ between batches so the run needs little free disk.
Usage: python3 scripts/verify_batches.py [batch_size]"""
import json, os, shutil, subprocess, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
size = int(sys.argv[1]) if len(sys.argv) > 1 else 60
paths = sorted(json.load(open(f))['path'] for f in glob.glob(os.path.join(ROOT, 'src/data/pages/*.json')))
tot_ok = tot_bad = 0; fails = []
for i in range(0, len(paths), size):
    batch = paths[i:i + size]
    shutil.rmtree(os.path.join(ROOT, 'dist'), ignore_errors=True)
    env = dict(os.environ, ONLY_PATHS=','.join(batch))
    r = subprocess.run(['npx', 'astro', 'build'], cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(2)
    v = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/verify.py'), '--show', '3'], cwd=ROOT, capture_output=True, text=True)
    s = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/seo_check.py')], cwd=ROOT, capture_output=True, text=True); print('   ', s.stdout.strip().splitlines()[-2:] if s.stdout.strip() else s.stderr[-300:])
    if s.returncode: fails.append(s.stdout)
    line = v.stdout.splitlines()[0]; print(f'batch {i // size + 1}: {line}', flush=True)
    if v.returncode: fails.append(v.stdout)
    import re
    m = re.search(r'(\d+) identical, (\d+) differ', line); tot_ok += int(m.group(1)); tot_bad += int(m.group(2))
shutil.rmtree(os.path.join(ROOT, 'dist'), ignore_errors=True)
print(f'TOTAL: {tot_ok + tot_bad} pages, {tot_ok} identical, {tot_bad} differ')
open(os.path.join(ROOT, '.crawl-cache', 'verify-failures.txt'), 'w').write('\n'.join(fails))
