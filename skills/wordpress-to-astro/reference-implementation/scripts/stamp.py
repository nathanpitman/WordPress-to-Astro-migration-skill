#!/usr/bin/env python3
"""Version stamps and the generated-file manifest (policies/updating-a-run.md).

Library use (from the generators):
    import stamp
    stamp.write_json(path, obj, indent=1)    # write a generated file, but never over a local edit
    stamp.write(path, text_or_bytes)
    stamp.clean(dir)                         # replaces shutil.rmtree for generated folders
    stamp.script_ran(5)                      # note in docs/run-state.json that a script for phase 5 ran

Command line:
    python scripts/stamp.py adopt            # one-off, for runs that pre-date the manifest: trust what is on disk
    python scripts/stamp.py status           # locally modified files, .updated files, stale phases
    python scripts/stamp.py complete 5 6     # at a gate: phases finished under this skill version
    python scripts/stamp.py crawled          # record crawledAt after Phase 1

docs/generated-manifest.json maps each generated file to the SHA-256 of what a script last wrote. A file whose
hash no longer matches has been edited by hand: it is kept, and the regenerated version is written beside it as
<name>.updated for the user to merge. Standard library only.
"""
import atexit, datetime, glob, hashlib, json, os, sys

# Keep in step with `version` in the skill's SKILL.md (see reference/extending.md, "Releasing a change").
SKILL_VERSION = '2.1.0'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'docs', 'generated-manifest.json')
RUN_STATE = os.path.join(ROOT, 'docs', 'run-state.json')
# What the generators own. `adopt` records these as they stand; anything else is the user's.
GENERATED = ['src/data/pages', 'src/content', 'src/data/chrome.json', 'src/data/head-items.json', 'src/data/tail-items.json',
             'src/data/asset-content-types.json', 'docs/assets-manifest.json', 'docs/heading-outlines.json']
UPDATED = '.updated'

_state = {'files': None, 'dirty': False, 'kept': []}


def _rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, '/')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _files():
    if _state['files'] is None:
        _state['files'] = json.load(open(MANIFEST)).get('files', {}) if os.path.exists(MANIFEST) else {}
        atexit.register(_save)
    return _state['files']


def _save():
    if _state['dirty']:
        os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
        json.dump({'skillVersion': SKILL_VERSION, 'files': dict(sorted(_state['files'].items()))},
                  open(MANIFEST, 'w'), indent=1)
        _state['dirty'] = False
    if _state['kept']:
        print(f"\n{len(_state['kept'])} locally edited file(s) kept; the regenerated versions are beside them as *{UPDATED}:")
        for k in _state['kept'][:20]:
            print('  ', k)
        if len(_state['kept']) > 20:
            print('   ...')


def _keep(rel):
    if rel not in _state['kept']:
        _state['kept'].append(rel)


def _set(rel, digest):
    _files()[rel] = digest
    _state['dirty'] = True


def _need_adopt():
    raise SystemExit('No docs/generated-manifest.json yet, but generated files already exist. They pre-date the manifest. '
                     'If they have not been edited by hand, run `python scripts/stamp.py adopt` once, then re-run this.')


def write(path, data, encoding='utf8'):
    """Write a generated file. Returns True if written in place, False if the existing file was edited by hand
    (then the new version goes to <path>.updated). Never clobbers a local edit."""
    b = data if isinstance(data, bytes) else data.encode(encoding)
    rel, files = _rel(path), _files()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        cur = sha256(path)
        if cur == hashlib.sha256(b).hexdigest():
            _set(rel, cur)
            return True
        if rel in files and files[rel] != cur or rel not in files and os.path.exists(MANIFEST):
            open(path + UPDATED, 'wb').write(b)
            _keep(rel)
            return False
        if rel not in files:
            _need_adopt()
    open(path, 'wb').write(b)
    _set(rel, hashlib.sha256(b).hexdigest())
    return True


def write_json(path, obj, **kw):
    kw.setdefault('indent', 1)
    return write(path, json.dumps(obj, **kw))


def clean(directory):
    """Delete the generated files under `directory` ahead of regenerating them, except locally edited ones.
    Use instead of shutil.rmtree for any folder a generator rebuilds."""
    files = _files()
    if not os.path.isdir(directory):
        return
    for dp, dns, fns in os.walk(directory, topdown=False):
        for fn in fns:
            p = os.path.join(dp, fn); rel = _rel(p)
            if fn.endswith(UPDATED):
                os.remove(p)
            elif rel in files and files[rel] == sha256(p):
                os.remove(p); del files[rel]; _state['dirty'] = True
            elif rel in files:
                _keep(rel)       # edited by hand: stays, regenerated copy will land beside it
            elif os.path.exists(MANIFEST):
                _keep(rel)       # not ours: leave it
            else:
                _need_adopt()
        if not os.listdir(dp) and os.path.abspath(dp) != os.path.abspath(directory):
            os.rmdir(dp)
    if os.path.isdir(directory) and not os.listdir(directory):
        os.rmdir(directory)


def record(*paths):
    """Record files a script wrote itself (for example downloaded assets) so later runs can spot edits."""
    for p in paths:
        if os.path.isfile(p):
            _set(_rel(p), sha256(p))


# ---- run state -------------------------------------------------------------------------------------------------

def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


def _run_state():
    return json.load(open(RUN_STATE)) if os.path.exists(RUN_STATE) else None


def _save_run_state(st):
    json.dump(st, open(RUN_STATE, 'w'), indent=2)


def script_ran(phase):
    """Note that a script for `phase` ran. This does NOT mark the phase complete or clear `stale`: the report that
    goes with it is still to be written, and only the gate (`complete`) says the phase is done."""
    st = _run_state()
    if st is None:
        return
    st.setdefault('phaseRuns', {}).setdefault(str(phase), {})['lastScriptRun'] = {'version': SKILL_VERSION, 'at': _now()}
    _save_run_state(st)


def crawled():
    st = _run_state()
    if st is None:
        return
    st['crawledAt'] = _now(); _save_run_state(st)
    print('crawledAt', st['crawledAt'])


def complete(phases):
    st = _run_state()
    if st is None:
        raise SystemExit('docs/run-state.json does not exist yet.')
    for p in phases:
        st.setdefault('phases', {})[str(p)] = 'done'
        st.setdefault('phaseRuns', {}).setdefault(str(p), {}).update({'ranWith': SKILL_VERSION, 'ranAt': _now()})
    if 'stale' not in st.get('phases', {}).values():
        st['skillVersion'] = SKILL_VERSION
    _save_run_state(st)
    print('phases', ', '.join(map(str, phases)), 'recorded as run with', SKILL_VERSION)


# ---- commands --------------------------------------------------------------------------------------------------

def adopt():
    n = 0
    for g in GENERATED:
        top = os.path.join(ROOT, g)
        paths = [top] if os.path.isfile(top) else [os.path.join(dp, f) for dp, _, fs in os.walk(top) for f in fs if not f.endswith(UPDATED)]
        for p in paths:
            _set(_rel(p), sha256(p)); n += 1
    am = os.path.join(ROOT, 'docs', 'assets-manifest.json')
    if os.path.exists(am):  # downloaded assets sit at their original paths under public/
        for e in json.load(open(am)).values():
            if e.get('local') and os.path.isfile(os.path.join(ROOT, e['local'])):
                _set(e['local'].replace(os.sep, '/'), sha256(os.path.join(ROOT, e['local']))); n += 1
    print('adopted', n, 'files as they stand. Anything edited by hand before now is treated as generated.')


def status():
    files = _files()
    mod = [r for r, h in files.items() if os.path.exists(os.path.join(ROOT, r)) and sha256(os.path.join(ROOT, r)) != h]
    gone = [r for r in files if not os.path.exists(os.path.join(ROOT, r))]
    upd = [_rel(p) for p in glob.glob(os.path.join(ROOT, '**', '*' + UPDATED), recursive=True) if 'node_modules' not in p]
    print(len(files), 'generated files tracked;', len(mod), 'edited by hand;', len(gone), 'missing;', len(upd), UPDATED, 'files waiting')
    for label, items in (('edited by hand', mod), ('missing', gone), ('waiting to be merged', upd)):
        for r in items[:25]:
            print(f'  {label}: {r}')
    st = _run_state()
    if st:
        stale = [p for p, s in st.get('phases', {}).items() if s == 'stale']
        print('run state: skillVersion', st.get('skillVersion', '0 (unstamped)'), '| skill', SKILL_VERSION, '| stale phases:', ', '.join(stale) or 'none')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'adopt': adopt()
    elif cmd == 'status': status()
    elif cmd == 'complete' and len(sys.argv) > 2: complete(sys.argv[2:])
    elif cmd == 'crawled': crawled()
    else: raise SystemExit(__doc__)
