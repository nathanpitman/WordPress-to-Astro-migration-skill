#!/usr/bin/env python3
"""Decompose the cached WordPress pages into Astro source (Phase 5).

Reads  .crawl-cache/  (raw HTML, not committed)
Writes src/data/**    (shared registries + one record per page)
       src/content/** (the verbatim <main> element of every page, one .html file each)

A page is split at its <header>, <main> and <footer> landmarks into five regions (pre, header, mid, post,
footer) plus <head> and the tail after the footer. Each region is stored once as a base variant (the most common
form) with per-page line patches for the differences (typically the "current menu item" classes). <head> and
tail items that repeat across pages become shared fragments referenced by id.

The only transformations applied to the served HTML are listed in deopt.py (hosting layers) and the TODO
comments inserted above forms. Everything else is carried over byte-for-byte.
"""
import collections, difflib, hashlib, html, json, os, re, sys, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CFG
from lib import ROOT, O, PUBLIC, load_pages, seg, mask
import deopt, stamp

SRC = os.path.join(ROOT, 'src')
REGIONS = ('pre', 'header', 'mid', 'post', 'footer')
TOK = re.compile(r'<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<noscript\b[^>]*>.*?</noscript>|<title\b[^>]*>.*?</title>|<(?:meta|link|base)\b[^>]*>', re.S)
TAIL_TOK = re.compile(r'<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>', re.S)


def nk(t):
    """comparison key: per-render tokens masked, whitespace collapsed"""
    return re.sub(r'\s+', ' ', mask(t))


FORM_TODO = '<!-- TODO(manual): Hook this form up to a form handler (service or server-side code). See docs/forms.md#{fid} -->'


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


def item_id(raw):
    """Readable id for a registry item: script/link/style id attribute, comment text, else tag (+ script file name)."""
    m = re.match(r"<(script|link|style)\b[^>]*?\bid=['\"]([^'\"]+)['\"]", raw)
    if m:
        return re.sub(r'[^A-Za-z0-9_-]+', '-', m.group(2)).strip('-')
    if raw.startswith('<!--'):
        return 'comment-' + re.sub(r'[^a-z0-9]+', '-', re.sub(r'<!--|-->', '', raw).strip().lower())[:40].strip('-')
    tag = re.match(r'<(\w+)', raw)
    base = tag.group(1) if tag else 'html'
    if base == 'script':
        ms = re.search(r'src=["\']([^"\']+)', raw[:300])
        if ms:
            base = 'script-' + re.sub(r'[^a-z0-9]+', '-', ms.group(1).split('?')[0].split('/')[-1].lower()).strip('-')[:30]
    return base


# ---------------------------------------------------------------- SEO items
# Whatever SEO plugin wrote them (Yoast, Rank Math, AIOSEO, SEOPress, The SEO Framework, theme code), these head
# items are recorded with their raw markup, in their original position, and re-emitted verbatim. `kind`, `name`
# and `value` are there for the CMS modelling phase; the build never re-renders from them.
SEO_PLUGIN_COMMENT = ('Yoast SEO', 'Rank Math', 'All in One SEO', 'AIOSEO', 'SEOPress', 'The SEO Framework')


def attr(raw, name):
    m = re.search(r'\s%s\s*=\s*(?:"([^"]*)"|\'([^\']*)\')' % re.escape(name), raw, re.I)
    return None if not m else (m.group(1) if m.group(1) is not None else m.group(2))


def classify_seo(raw):
    """-> {'kind', 'name', 'value'} for an SEO head item, else None."""
    if raw.startswith('<title'):
        return {'kind': 'title', 'name': '', 'value': re.sub(r'^<title[^>]*>|</title>$', '', raw, flags=re.S)}
    if raw.startswith('<meta'):
        name, prop, content = attr(raw, 'name'), attr(raw, 'property'), attr(raw, 'content')
        if name and (name.lower() in ('robots', 'description', 'author', 'googlebot', 'bingbot') or name.lower().startswith('twitter:')):
            return {'kind': 'meta', 'name': name, 'value': content}
        if prop and re.match(r'(og|article|fb|profile|book|music|video):', prop):
            return {'kind': 'property', 'name': prop, 'value': content}
    if raw.startswith('<link') and (attr(raw, 'rel') or '').lower() == 'canonical':
        return {'kind': 'canonical', 'name': '', 'value': attr(raw, 'href')}
    if raw.startswith('<script') and re.search(r'type=["\']application/ld\+json', raw[:200]):
        return {'kind': 'jsonld', 'name': '', 'value': None}
    if raw.startswith('<!--') and any(k in raw for k in SEO_PLUGIN_COMMENT):
        return {'kind': 'comment', 'name': '', 'value': None}
    return None


# ---------------------------------------------------------------- helpers for page records
def slug_of(url):
    p = up.unquote(url.replace(O, '')).strip('/')
    return p or 'index'


def parse_attrs(s):
    """Attribute string of an opening tag -> ordered dict (entities decoded; Astro re-escapes on output)."""
    out = {}
    for m in re.finditer(r'([^\s=/>"\']+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+)))?', s):
        v = next((g for g in m.groups()[1:] if g is not None), '')
        out[m.group(1)] = html.unescape(v)
    return out


def template_of(cls):
    """Name of the WordPress template from the body classes: configured map first, then the standard classes."""
    for k, v in CFG['templates'].items():
        if k in cls:
            return v
    if 'error404' in cls: return '404'
    if 'home' in cls: return 'home'
    for c in cls:
        if c.startswith('single-') and not c.startswith('single-format-'):
            return c[len('single-'):]  # single-post -> post, single-product -> product, single-<custom type> -> <custom type>
    if 'search' in cls: return 'search'
    if {'archive', 'category', 'tag', 'author', 'tax', 'blog', 'paged'} & set(cls) or any(c.startswith('tax-') for c in cls): return 'archive'
    return 'page'


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

    # ---- regions: base variant (most common masked text) + per-page line patches
    bases = {}
    for key in REGIONS:
        c = collections.Counter(nk(s[key]) for s in S.values())
        top = c.most_common(1)[0][0]
        bases[key] = next(s[key] for s in S.values() if nk(s[key]) == top)

    # ---- head & tail items
    head_items, tail_items = {}, {}
    for u, s in S.items():
        head_m = re.search(r'<head\b[^>]*>', s['head'], re.I)
        head_text = s['head'][head_m.end():]
        head_items[u] = split_items(head_text[:head_text.lower().rfind('</head>')] if '</head>' in head_text.lower() else head_text, TOK)
        tail_items[u] = split_items(re.sub(r'</body>|</html>', '', s['tail'], flags=re.I), TAIL_TOK)
    hcount = collections.Counter(nk(r) for l in head_items.values() for (_, r) in {x for x in l})
    tcount = collections.Counter(nk(r) for l in tail_items.values() for (_, r) in {x for x in l})
    head_reg, tail_reg = {}, {}
    hkey2id, tkey2id = {}, {}

    def reg_id(raw, store, key2id, mk):
        if mk in key2id: return key2id[mk]
        base = item_id(raw)
        i, n = base, 2
        while i in store:
            i = f'{base}-{n}'; n += 1
        key2id[mk] = i; store[i] = raw
        return i

    records = {}
    content_dir = os.path.join(SRC, 'content')
    stamp.clean(content_dir)  # removes only files this script wrote and nobody has edited
    stats = collections.Counter()
    skip_roles = set(CFG['skipFormRoles'])
    for u in sorted(S):
        s = S[u]
        body_attrs = parse_attrs(re.sub(r'^<body\b|>$', '', s['bodyopen'], flags=re.I))
        html_m = re.search(r'<html\b([^>]*)>', s['head'], re.I)
        rec = {'path': u.replace(O, ''), 'url': PUBLIC.get(u, u).replace(O, ''),
               'template': template_of(body_attrs.get('class', '').split()),
               'htmlAttrs': parse_attrs(html_m.group(1)) if html_m else {}, 'bodyAttrs': body_attrs}
        # head: SEO items stay where they were and are recorded in rec['seo']; the rest are shared ids or inline raw items
        seo, head_out = [], []
        for kind, raw in head_items[u]:
            if kind == 'html':
                raise SystemExit('unexpected text in head of ' + u + ': ' + raw[:80])
            c = classify_seo(raw)
            if c:
                head_out.append({'seo': len(seo)}); seo.append({**c, 'raw': raw})
                continue
            mk = nk(raw)
            head_out.append(reg_id(raw, head_reg, hkey2id, mk) if hcount[mk] >= 2 else {'raw': raw})
        rec['head'], rec['seo'] = head_out, seo
        # regions
        rec['patches'] = {k: (line_patches(bases[k], s[k]) if nk(s[k]) != nk(bases[k]) else []) for k in REGIONS}
        # tail
        rec['tail'] = [reg_id(raw, tail_reg, tkey2id, nk(raw)) if tcount[nk(raw)] >= 2 else {'raw': raw} for _, raw in tail_items[u]]
        # main -> content file, with a TODO comment above each data-entry form
        def todo(m):
            tag = m.group(0)
            if (attr(tag, 'role') or '') in skip_roles:
                return tag
            stats['forms'] += 1
            return FORM_TODO.format(fid=attr(tag, 'id') or f"form-{stats['forms']}") + '\n' + tag
        main_html = re.sub(r'<form\b[^>]*>', todo, s['main'])
        rel = slug_of(u) + '.html'
        stamp.write(os.path.join(content_dir, rel), main_html)
        rec['content'] = rel
        records[u] = rec

    # ---- write data
    data = os.path.join(SRC, 'data')
    stamp.clean(os.path.join(data, 'pages'))  # only generated files; redirects/rewrites/asset data live beside them
    stamp.write_json(os.path.join(data, 'chrome.json'), {k: bases[k] for k in REGIONS}, ensure_ascii=False, indent=1)
    stamp.write_json(os.path.join(data, 'head-items.json'), head_reg, ensure_ascii=False, indent=1)
    stamp.write_json(os.path.join(data, 'tail-items.json'), tail_reg, ensure_ascii=False, indent=1)
    for u, rec in records.items():
        name = rec['content'].replace('.html', '').replace(os.sep, '__') + '.json'
        stamp.write_json(os.path.join(data, 'pages', name), rec, ensure_ascii=False, indent=1)
    print('pages', len(records), 'head registry', len(head_reg), 'tail registry', len(tail_reg), 'forms', stats['forms'])
    print('pages with patches:', {k: sum(1 for r in records.values() if r['patches'][k]) for k in REGIONS})
    print('inline head raw items:', sum(1 for r in records.values() for e in r['head'] if isinstance(e, dict) and 'raw' in e), 'inline tail raw items:', sum(1 for r in records.values() for e in r['tail'] if isinstance(e, dict)))
    json.dump(dict(deopt.STATS), open(os.path.join(ROOT, '.crawl-cache', 'deopt-stats.json'), 'w'), indent=1)
    stamp.script_ran(5)


if __name__ == '__main__':
    main()
