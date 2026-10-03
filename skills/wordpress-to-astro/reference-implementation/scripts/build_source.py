#!/usr/bin/env python3
"""Decompose the cached WordPress pages into Astro source (Phase 5).

Reads  .crawl-cache/  (raw HTML, not committed)
Writes src/data/**    (shared registries + one record per page)
       src/content/** (the verbatim <main> element of every page, one .html file each)

The only transformations applied to the served HTML are listed in deopt.py (hosting layers) and the
TODO comments inserted above forms. Everything else is carried over byte-for-byte.
"""
import collections, difflib, hashlib, json, os, re, shutil, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, O, load_pages, seg, mask
import deopt, stamp

SRC = os.path.join(ROOT, 'src')
TOK = re.compile(r'<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<noscript\b[^>]*>.*?</noscript>|<title\b[^>]*>.*?</title>|<(?:meta|link|base)\b[^>]*>', re.S)
TAIL_TOK = re.compile(r'<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>', re.S)
def nk(t):
    """comparison key: per-render tokens masked, whitespace collapsed"""
    return re.sub(r'\s+', ' ', mask(t))


FORM_TODO = '<!-- TODO(manual): Hook this form up to Salesforce and server-side code. See docs/forms.md#{fid} -->'


def split_items(text, tok):
    out, pos = [], 0
    for m in tok.finditer(text):
        gap = text[pos:m.start()]
        if gap.strip():
            out.append(('html', gap))
        out.append(('el', m.group(0)))
        pos = m.end()
    gap = text[pos:]
    if gap.strip():
        out.append(('html', gap))
    return out


def h6(s):
    return hashlib.md5(s.encode()).hexdigest()[:6]


def item_id(raw, used):
    """Readable id for a registry item: script/link/style id attribute, comment text, else tag + hash."""
    m = re.match(r"<(script|link|style)\b[^>]*?\bid=['\"]([^'\"]+)['\"]", raw)
    if m:
        base = re.sub(r'[^A-Za-z0-9_-]+', '-', m.group(2)).strip('-')
    elif raw.startswith('<!--'):
        base = 'comment-' + re.sub(r'[^a-z0-9]+', '-', re.sub(r'<!--|-->', '', raw).strip().lower())[:40].strip('-')
    else:
        tag = re.match(r'<(\w+)', raw)
        base = (tag.group(1) if tag else 'html')
        if base == 'script':
            ms = re.search(r'src=["\']([^"\']+)', raw[:300])
            if ms:
                base = 'script-' + re.sub(r'[^a-z0-9]+', '-', ms.group(1).split('?')[0].split('/')[-1].lower()).strip('-')[:30]
    return base


# ---------------------------------------------------------------- SEO block
META_FMT = {
    'robots': "<meta name='robots' content='{v}' />",
    'description': '<meta name="description" content="{v}" />',
}


def parse_seo_item(raw):
    m = re.fullmatch(r"<meta name='robots' content='([^']*)' />", raw)
    if m: return ['robots', m.group(1)]
    m = re.fullmatch(r'<title>(.*)</title>', raw, re.S)
    if m: return ['title', m.group(1)]
    m = re.fullmatch(r'<meta name="description" content="([^"]*)" />', raw)
    if m: return ['description', m.group(1)]
    m = re.fullmatch(r'<link rel="canonical" href="([^"]*)" />', raw)
    if m: return ['canonical', m.group(1)]
    m = re.fullmatch(r'<meta property="([^"]+)" content="([^"]*)" />', raw)
    if m: return ['property', m.group(1), m.group(2)]
    m = re.fullmatch(r'<meta name="((?:twitter:|author)[^"]*)" content="([^"]*)" />', raw)
    if m: return ['name', m.group(1), m.group(2)]
    if raw.startswith('<script type="application/ld+json" class="yoast-schema-graph">'):
        return ['jsonld', raw]
    if re.match(r'<!-- (This site is optimized|/ Yoast SEO)', raw):
        return ['comment', raw]
    return None


def render_seo_item(it):
    k = it[0]
    if k == 'robots': return "<meta name='robots' content='%s' />" % it[1]
    if k == 'title': return '<title>%s</title>' % it[1]
    if k == 'description': return '<meta name="description" content="%s" />' % it[1]
    if k == 'canonical': return '<link rel="canonical" href="%s" />' % it[1]
    if k == 'property': return '<meta property="%s" content="%s" />' % (it[1], it[2])
    if k == 'name': return '<meta name="%s" content="%s" />' % (it[1], it[2])
    return it[1]


# ---------------------------------------------------------------- helpers for page records
def slug_of(url):
    p = up.unquote(url.replace(O, '')).strip('/')
    return p or 'index'


def template_of(bodyopen):
    cls = re.search(r'class="([^"]*)"', bodyopen).group(1).split()
    if 'single-course' in cls: return 'course'
    if 'single-post' in cls: return 'post'
    if 'home' in cls: return 'home'
    return 'page'


def lw_path(url):
    from lib import PUBLIC
    url = PUBLIC.get(url, url).split('?')[0]
    p = up.quote(up.unquote(url.replace(O, '')).strip('/'), safe="/-_.~%")
    return (p or '').replace('/', '\\/') if p else '\\/'


def line_patches(base, other):
    """Line-level splice list turning base into other: [[start, end, 'replacement'], ...]."""
    a, b = base.split('\n'), other.split('\n')
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != 'equal':
            out.append([i1, i2, '\n'.join(b[j1:j2])])
    return out


def main():
    pages = load_pages()
    deopt.STATS.clear()
    D = {u: deopt.deopt(t) for u, t in pages.items()}
    S = {u: seg(t) for u, t in D.items()}

    # ---- chrome constants (identical on every page)
    for k in ('pre', 'mid', 'post'):
        assert len({re.sub(r'\s+', ' ', s[k]) for s in S.values()}) == 1, k  # whitespace-only differences (attribute slot spacing) are insignificant
    chrome = {'pre': S[next(iter(S))]['pre'], 'mid': S[next(iter(S))]['mid'], 'post': S[next(iter(S))]['post']}

    # ---- header / footer: base variant (by masked text) + per-page line patches
    def base_variant(key):
        c = collections.Counter(nk(s[key]) for s in S.values())
        top = c.most_common(1)[0][0]
        for u, s in S.items():
            if nk(s[key]) == top:
                return s[key], u
    hdr_base, hdr_u = base_variant('header')
    ftr_base, ftr_u = base_variant('footer')
    # Livewire snapshot path in the base header becomes a placeholder substituted per page
    hdr_path = lw_path(hdr_u)
    assert hdr_base.count('&quot;path&quot;:&quot;%s&quot;' % hdr_path) >= 1
    hdr_base = hdr_base.replace('&quot;path&quot;:&quot;%s&quot;' % hdr_path, '&quot;path&quot;:&quot;{{LW_PATH}}&quot;')

    # ---- head & tail items
    head_items, tail_items = {}, {}
    for u, s in S.items():
        head_items[u] = split_items(s['head'].split('<!DOCTYPE html>', 1)[1].split('<head>', 1)[1].replace('</head>', ''), TOK)
        tail_items[u] = split_items(s['tail'].replace('</body>', '').replace('</html>', ''), TAIL_TOK)
        # sanity: nothing but whitespace between items
    hcount = collections.Counter(nk(r) for l in head_items.values() for (_, r) in {x for x in l})
    tcount = collections.Counter(nk(r) for l in tail_items.values() for (_, r) in {x for x in l})
    head_reg, tail_reg = {}, {}
    hkey2id, tkey2id = {}, {}
    used = collections.Counter()

    def reg_id(raw, store, key2id, mk):
        if mk in key2id: return key2id[mk]
        base = item_id(raw, used)
        i = base
        n = 2
        while i in store:
            i = f'{base}-{n}'; n += 1
        key2id[mk] = i; store[i] = raw
        return i

    records = {}
    content_dir = os.path.join(SRC, 'content')
    stamp.clean(content_dir)  # removes only files this script wrote and nobody has edited
    stats = collections.Counter()
    for u in sorted(S):
        s = S[u]
        tpl = template_of(s['bodyopen'])
        from lib import PUBLIC
        rec = {'path': u.replace(O, ''), 'url': PUBLIC.get(u, u).replace(O, ''), 'template': tpl,
               'bodyClass': re.search(r'class="([^"]*)"', s['bodyopen']).group(1)}
        # head
        seo, head_out, seo_done = [], [], False
        for kind, raw in head_items[u]:
            if kind == 'html':
                raise SystemExit('unexpected text in head of ' + u + ': ' + raw[:80])
            p = parse_seo_item(raw)
            if p and render_seo_item(p) == raw:
                if not seo_done:
                    head_out.append({'seo': True}); seo_done = True
                seo.append(p)
                continue
            mk = nk(raw)
            if hcount[mk] >= 2:
                head_out.append(reg_id(raw, head_reg, hkey2id, mk))
            else:
                head_out.append({'raw': raw})
        rec['head'] = head_out
        rec['seo'] = seo
        # header / footer
        hh = s['header'].replace('&quot;path&quot;:&quot;%s&quot;' % lw_path(u), '&quot;path&quot;:&quot;{{LW_PATH}}&quot;')
        rec['headerPatches'] = line_patches(hdr_base, hh) if nk(hh) != nk(hdr_base) else []
        rec['footerPatches'] = line_patches(ftr_base, s['footer']) if nk(s['footer']) != nk(ftr_base) else []
        # tail
        t_out = []
        for kind, raw in tail_items[u]:
            mk = nk(raw)
            if tcount[mk] >= 2:
                t_out.append(reg_id(raw, tail_reg, tkey2id, mk))
            else:
                t_out.append({'raw': raw})
        rec['tail'] = t_out
        # main -> content file, with TODO comments above each <form
        main_html = s['main']
        def todo(m):
            fid = re.search(r"id=['\"](gform_\d+)", m.group(0)).group(1)
            stats['forms'] += 1
            return FORM_TODO.format(fid=fid) + '\n' + m.group(0)
        main_html = re.sub(r"<form\b[^>]*id=['\"]gform_\d+['\"][^>]*>", todo, main_html)
        slug = slug_of(u)
        rel = slug + '.html'
        fp = os.path.join(content_dir, rel)
        stamp.write(fp, main_html)
        rec['content'] = rel
        records[u] = rec

    # ---- write data
    data = os.path.join(SRC, 'data')
    stamp.clean(os.path.join(data, 'pages'))  # only generated files; redirects/rewrites/asset data live beside them
    stamp.write_json(os.path.join(data, 'chrome.json'), {'headerBase': hdr_base, 'footerBase': ftr_base, **chrome}, ensure_ascii=False, indent=1)
    stamp.write_json(os.path.join(data, 'head-items.json'), head_reg, ensure_ascii=False, indent=1)
    stamp.write_json(os.path.join(data, 'tail-items.json'), tail_reg, ensure_ascii=False, indent=1)
    for u, rec in records.items():
        name = rec['content'].replace('.html', '').replace(os.sep, '__') + '.json'
        stamp.write_json(os.path.join(data, 'pages', name), rec, ensure_ascii=False, indent=1)
    print('pages', len(records), 'head registry', len(head_reg), 'tail registry', len(tail_reg), 'forms', stats['forms'])
    print('header patches:', sum(1 for r in records.values() if r['headerPatches']), 'footer patches:', sum(1 for r in records.values() if r['footerPatches']))
    print('inline head raw items:', sum(1 for r in records.values() for e in r['head'] if isinstance(e, dict) and 'raw' in e), 'inline tail raw items:', sum(1 for r in records.values() for e in r['tail'] if isinstance(e, dict)))
    json.dump(dict(deopt.STATS), open(os.path.join(ROOT, '.crawl-cache', 'deopt-stats.json'), 'w'), indent=1)
    stamp.script_ran(5)


if __name__ == '__main__':
    main()
