#!/usr/bin/env python3
"""Phase 10: accessibility audit of the cached ORIGINAL pages. RECORD ONLY: nothing is fixed.

Static markup checks (no rendering, no assistive technology). Shared regions (header, footer, cookie banner,
pre-header) are audited once and attributed to every page; <main> is audited per page.
Writes .crawl-cache/a11y-findings.json"""
import collections, glob, html as H, json, os, re, sys
from html.parser import HTMLParser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ROOT, CACHE, O, load_pages, seg
import deopt, stamp

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
SKIPTEXT = {'script', 'style', 'noscript', 'template'}


class Node:
    __slots__ = ('tag', 'attrs', 'children', 'parent', 'text', 'line')
    def __init__(self, tag, attrs, parent):
        self.tag = tag; self.attrs = attrs; self.children = []; self.parent = parent; self.text = []


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root', {}, None); self.cur = self.root; self.all = []
    def handle_starttag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else '') for k, v in attrs}, self.cur)
        self.cur.children.append(n); self.all.append(n)
        if tag not in VOID: self.cur = n
    def handle_startendtag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else '') for k, v in attrs}, self.cur)
        self.cur.children.append(n); self.all.append(n)
    def handle_endtag(self, tag):
        c = self.cur
        while c is not self.root and c.tag != tag: c = c.parent
        if c is not self.root: self.cur = c.parent
    def handle_data(self, d):
        self.cur.text.append(d)


def parse(html):
    t = Tree(); t.feed(html); return t


def own_text(n):
    """visible text of a node (skips script/style, includes descendants; svg <title> excluded)"""
    out = []
    def walk(x):
        if x.tag in SKIPTEXT: return
        out.append(''.join(x.text))
        for c in x.children:
            if c.tag == 'svg': continue
            walk(c)
    walk(n); return ' '.join(' '.join(out).split())


def svg_name(n):
    for x in n.children:
        if x.tag == 'svg':
            for y in [x] + x.children:
                if y.tag == 'title' and ''.join(y.text).strip(): return ''.join(y.text).strip()
            if x.attrs.get('aria-label'): return x.attrs['aria-label']
    return ''


def sel(n):
    def one(x):
        s = x.tag
        if x.attrs.get('id'): s += '#' + x.attrs['id']
        cls = [c for c in x.attrs.get('class', '').split() if c][:3]
        if cls: s += '.' + '.'.join(cls)
        return s
    chain = [one(n)]; p = n.parent
    for _ in range(1):
        if p and p.tag != '#root': chain.insert(0, one(p)); p = p.parent
    return ' > '.join(chain)[:140]


def accname(n, ids):
    a = n.attrs
    if a.get('aria-label', '').strip(): return a['aria-label'].strip()
    if a.get('aria-labelledby'):
        t = ' '.join(own_text(ids[i]) for i in a['aria-labelledby'].split() if i in ids).strip()
        if t: return t
    t = own_text(n)
    if t: return t
    for c in n.children:
        if c.tag == 'img' and c.attrs.get('alt', '').strip(): return c.attrs['alt'].strip()
    for x in walk_desc(n):
        if x.tag == 'img' and x.attrs.get('alt', '').strip(): return x.attrs['alt'].strip()
    s = svg_name(n)
    if s: return s
    for x in walk_desc(n):
        if x.tag == 'svg' and (x.attrs.get('aria-label') or any(y.tag == 'title' for y in x.children)): return 'svg-name'
    return a.get('title', '').strip()


def walk_desc(n):
    for c in n.children:
        yield c
        yield from walk_desc(c)


NONDESC = re.compile(r'^(click here|here|read more|learn more|more|find out more|view more|view|link|more info|details|load more…?|load more\.*)$', re.I)
RGB = {}
css = open(os.path.join(ROOT, 'src/styles/theme/app.css'), encoding='utf8').read()
for name, v in re.findall(r'--tw-color-([a-z0-9-]+):(\d+ \d+ \d+)', css): RGB[name] = tuple(int(x) for x in v.split())


def lum(c):
    def f(v):
        v /= 255; return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi + .05) / (lo + .05)


def classes(n): return n.attrs.get('class', '').split()


def color_of(n, prefix):
    x = n
    while x and x.tag != '#root':
        if prefix == 'bg' and (re.search(r'background', x.attrs.get('style', '')) or any(c.startswith(('bg-[', 'bg-gradient', 'bg-cover', 'bg-opacity')) or ':bg-' in c and False for c in classes(x))):
            return '?'  # background set by an arbitrary value, gradient, image or inline style: not resolvable from classes
        for c in classes(x):
            if c.startswith(prefix + '-') and ':' not in c and '[' not in c and c[len(prefix) + 1:] in RGB:
                return c[len(prefix) + 1:]
        x = x.parent
    return None


FONT_LARGE = re.compile(r'\b(text-(?:xl|2xl|3xl|4xl|h[1-3]|lg)|h[1-3])\b')


def audit(tree, ids, region, page, F):
    def add(rule, wcag, sev, n, note, extra=''):
        F.append({'rule': rule, 'wcag': wcag, 'severity': sev, 'region': region, 'page': page, 'selector': sel(n) if n else '', 'detail': extra, 'note': note})
    heads = []
    for n in tree.all:
        t, a = n.tag, n.attrs
        if t == 'img':
            if 'alt' not in a: add('img-missing-alt', '1.1.1', 'serious', n, 'Add alt (descriptive, or alt="" if decorative).', a.get('src', '')[-70:])
        if t == 'a' and 'href' in a:
            nm = accname(n, ids)
            if not nm: add('link-empty-name', '2.4.4 / 4.1.2', 'serious', n, 'Give the link an accessible name (visible text, aria-label, or image alt).', a['href'][-70:])
            elif NONDESC.match(nm): add('link-text-non-descriptive', '2.4.4', 'moderate', n, 'Make link text describe the destination, or add aria-label/aria-describedby.', f'"{nm}" -> {a["href"][-60:]}')
        if t == 'a' and 'href' not in a and not a.get('role') and own_text(n): add('anchor-without-href', '2.1.1', 'minor', n, 'Anchor without href is not focusable; use a button or add href.')
        if t == 'button':
            if not accname(n, ids): add('button-empty-name', '4.1.2', 'serious', n, 'Give the button an accessible name (aria-label or visible text).', a.get('wire:click', a.get('class', ''))[:60])
        if re.fullmatch(r'h[1-6]', t):
            heads.append((int(t[1]), n))
            if not own_text(n) and not any(x.tag == 'img' and x.attrs.get('alt') for x in walk_desc(n)): add('heading-empty', '2.4.6', 'moderate', n, 'Empty heading: remove or add text.')
        if t == 'input':
            ty = a.get('type', 'text').lower()
            if ty not in ('hidden', 'submit', 'button', 'image', 'reset'):
                named = bool(a.get('aria-label', '').strip() or a.get('aria-labelledby') or a.get('title', '').strip())
                if not named and a.get('id'):
                    named = any(x.tag == 'label' and x.attrs.get('for') == a['id'] and own_text(x) for x in tree.all)
                if not named:
                    p = n.parent
                    while p and p.tag != '#root':
                        if p.tag == 'label' and own_text(p): named = True; break
                        p = p.parent
                if not named: add('form-control-no-label', '1.3.1 / 3.3.2 / 4.1.2', 'serious', n, 'Associate a <label> or aria-label; a placeholder is not a label.', f'type={ty} placeholder="{a.get("placeholder", "")}"')
                nm = (a.get('name', '') + ' ' + a.get('placeholder', '') + ' ' + a.get('id', '')).lower()
                if ty in ('email', 'tel') or re.search(r'first.?name|last.?name|company|phone|email|telephone', nm):
                    if 'autocomplete' not in a: add('input-autocomplete-missing', '1.3.5', 'moderate', n, 'Add an autocomplete token (given-name, family-name, email, tel, organization).', f'type={ty} name={a.get("name", "")}')
        if t in ('textarea', 'select'):
            ok = a.get('aria-label') or a.get('aria-labelledby') or any(x.tag == 'label' and x.attrs.get('for') == a.get('id') for x in tree.all)
            if not ok: add('form-control-no-label', '1.3.1 / 3.3.2 / 4.1.2', 'serious', n, 'Associate a <label> or aria-label.')
        if a.get('tabindex', '').lstrip('-').isdigit() and int(a['tabindex']) > 0: add('tabindex-positive', '2.4.3', 'moderate', n, 'Avoid positive tabindex; use DOM order.')
        if a.get('aria-hidden') == 'true':
            foc = t in ('a', 'button', 'input', 'select', 'textarea') and a.get('tabindex') != '-1' or (a.get('tabindex', 'x').lstrip('-').isdigit() and int(a['tabindex']) >= 0)
            inner = [x for x in walk_desc(n) if x.tag in ('a', 'button', 'input', 'select', 'textarea') and x.attrs.get('tabindex') != '-1' and not x.attrs.get('disabled')]
            if foc or inner: add('aria-hidden-focusable', '4.1.2', 'serious', n, 'aria-hidden content must not contain focusable elements.')
        for ref in ('aria-labelledby', 'aria-describedby', 'aria-controls'):
            if a.get(ref):
                miss = [i for i in a[ref].split() if i not in ids]
                if miss: add('aria-ref-missing', '1.3.1 / 4.1.2', 'moderate', n, f'{ref} points to an id that does not exist on the page.', ref + '=' + ','.join(miss)[:60])
        if 'role' in a:
            r = a['role'].split()[0]
            valid = {'alert', 'alertdialog', 'application', 'article', 'banner', 'button', 'cell', 'checkbox', 'complementary', 'contentinfo', 'dialog', 'document', 'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading', 'img', 'link', 'list', 'listbox', 'listitem', 'main', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation', 'none', 'note', 'option', 'presentation', 'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup', 'search', 'searchbox', 'separator', 'slider', 'spinbutton', 'status', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox', 'timer', 'toolbar', 'tooltip', 'tree', 'treeitem', 'combobox', 'columnheader', 'rowheader'}
            if r not in valid: add('aria-invalid-role', '4.1.2', 'moderate', n, 'Invalid ARIA role.', 'role=' + r)
            if r in ('button', 'link') and t not in ('a', 'button', 'input') and 'tabindex' not in a: add('aria-role-not-focusable', '2.1.1 / 4.1.2', 'serious', n, 'Elements with role=button/link must be focusable (tabindex) and keyboard operable.', 'role=' + r)
            if r == 'dialog' and not (a.get('aria-label') or a.get('aria-labelledby')): add('dialog-no-name', '4.1.2', 'moderate', n, 'Dialogs need an accessible name.')
        if t in ('div', 'span', 'li', 'p', 'section') and any(k in a for k in ('onclick', 'wire:click')) and 'role' not in a and 'tabindex' not in a:
            add('click-on-non-interactive', '2.1.1', 'serious', n, 'Click handler on a non-interactive element: not keyboard accessible.')
        if t == 'iframe' and not a.get('title') and not a.get('aria-label') and 'display:none' not in a.get('style', '').replace(' ', ''):
            add('iframe-no-title', '4.1.2 / 2.4.1', 'serious', n, 'Give the iframe a title.', a.get('src', '')[:70])
        if t in ('video', 'audio') and 'autoplay' in a: add('media-autoplay', '1.4.2 / 2.2.2', 'serious', n, 'Autoplaying media needs a pause/stop control and no audio.')
        if t == 'iframe' and re.search(r'autoplay=1|autoplay=true', a.get('src', '')): add('media-autoplay', '1.4.2 / 2.2.2', 'serious', n, 'Embedded player autoplays.', a.get('src', '')[:80])
        if t == 'video' and 'controls' not in a: add('video-no-controls', '1.4.2 / 2.1.1', 'moderate', n, 'Video has no controls attribute.')
        if t == 'a' and a.get('target') == '_blank' and not re.search(r'new (tab|window)|opens', accname(n, ids), re.I) and 'aria-label' not in a:
            add('link-new-window-unannounced', '3.2.5 (AAA) / G201', 'minor', n, 'Warn users that the link opens a new tab/window.', a.get('href', '')[-60:])
        cls = classes(n)
        if ('outline-none' in cls or 'focus:outline-none' in cls or 'focus-visible:outline-none' in cls) and t in ('input', 'a', 'button', 'select', 'textarea', 'summary') and not any(c in cls for c in ('focus:ring', 'focus-visible:ring', 'focus:ring-2', 'focus:border-blue')):
            add('focus-indicator-removed', '2.4.7', 'serious', n, 'outline removed without a visible replacement (check the stylesheet for a :focus-visible rule).', ' '.join(c for c in cls if 'outline' in c or 'ring' in c))
        if t == 'meta' and a.get('name') == 'viewport' and re.search(r'user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*[01](\.\d+)?\b', a.get('content', '')): add('viewport-zoom-disabled', '1.4.4', 'serious', n, 'Do not disable zoom.')
        # contrast (indicative): element with its own direct text
        if own_direct(n):
            fg, bg = color_of(n, 'text'), color_of(n, 'bg')
            if fg and bg != '?':
                r = ratio(RGB[fg], RGB[bg or 'white'])
                large = bool(FONT_LARGE.search(' '.join(cls))) or t in ('h1', 'h2', 'h3')
                need = 3.0 if large else 4.5
                if r < need: add('color-contrast-indicative', '1.4.3', 'moderate', n, f'Utility classes give {fg} on {bg or "white (assumed)"} = {r:.2f}:1 (needs {need}:1). Indicative only: computed styles, overlays and gradients not evaluated.', f'{fg}/{bg or "white"} {r:.2f}')
    # headings
    prev = 0
    for lvl, n in heads:
        if prev and lvl > prev + 1: add('heading-level-skip', '1.3.1 / 2.4.6', 'moderate', n, f'Heading jumps from h{prev} to h{lvl}.', f'h{prev}->h{lvl}: ' + own_text(n)[:50])
        prev = lvl


def own_direct(n):
    return bool(n.tag not in SKIPTEXT and ''.join(n.text).strip()) and n.tag not in ('html', 'body', 'head', 'title', 'option')


def main():
    pages = load_pages()
    chrome = json.load(open(os.path.join(ROOT, 'src/data/chrome.json')))
    tail_reg = json.load(open(os.path.join(ROOT, 'src/data/tail-items.json')))
    F = []; per_page = {}
    # ---- shared regions, once
    hdr = chrome['headerBase'].replace('{{LW_PATH}}', 'x'); ftr = chrome['footerBase']
    tail_html = '\n'.join(v for k, v in tail_reg.items() if not v.startswith('<script') and not v.startswith('<!--'))
    shared = {'Header': hdr, 'Footer': ftr, 'Pre-header (skip link)': chrome['pre'], 'Cookie banner and popups (tail)': tail_html}
    ids_shared = {}
    for name, html in shared.items(): ids_shared.update({n.attrs['id']: n for n in parse(html).all if n.attrs.get('id')})
    sf = []
    for name, html in shared.items():
        t = parse(html); audit(t, {**ids_shared, **{n.attrs['id']: n for n in t.all if n.attrs.get('id')}}, name, '*', sf)
    # ---- per page: main + duplicate ids + head facts
    pf = []
    for u, raw in sorted(pages.items()):
        s = seg(deopt.deopt(raw)); path = u.replace(O, '') or '/'
        full = parse(s['head'] + s['bodyopen'] + s['pre'] + s['header'] + s['main'] + s['footer'] + s['tail'])
        ids = {}; dup = collections.Counter()
        for n in full.all:
            i = n.attrs.get('id')
            if i: dup[i] += 1; ids[i] = n
        main_t = parse(s['main'])
        audit(main_t, ids, 'Main content', path, pf)
        for i, c in dup.items():
            if c > 1: pf.append({'rule': 'duplicate-id', 'wcag': '4.1.1 (obsolete in WCAG 2.2) / 1.3.1', 'severity': 'moderate', 'region': 'Main content' if i.startswith(('gform', 'input_', 'field_', 'label_', 'choice_', 'validation_')) else 'Whole page', 'page': path, 'selector': '#' + i, 'detail': f'{c} elements share the id', 'note': 'IDs must be unique; duplicated ids break label association and ARIA references.'})
        # document-level
        nmain = len([n for n in full.all if n.tag == 'main'])
        navs = [n for n in full.all if n.tag == 'nav']
        if nmain != 1: pf.append({'rule': 'landmark-main', 'wcag': '1.3.6 / 2.4.1', 'severity': 'moderate', 'region': 'Whole page', 'page': path, 'selector': 'main', 'detail': f'{nmain} <main>', 'note': 'Exactly one main landmark expected.'})
        if len(navs) > 1 and sum(1 for n in navs if n.attrs.get('aria-label') or n.attrs.get('aria-labelledby')) < len(navs):
            pf.append({'rule': 'nav-unlabelled', 'wcag': '1.3.1 / 2.4.1', 'severity': 'minor', 'region': 'Whole page', 'page': path, 'selector': 'nav', 'detail': f'{len(navs)} <nav>, {sum(1 for n in navs if not (n.attrs.get("aria-label") or n.attrs.get("aria-labelledby")))} unlabelled', 'note': 'Label each nav landmark when there are several (e.g. "Primary", "Footer").'})
        skip = [n for n in full.all if n.tag == 'a' and n.attrs.get('href', '').startswith('#') and re.search(r'skip', own_text(n), re.I)]
        if not skip: pf.append({'rule': 'skip-link-missing', 'wcag': '2.4.1', 'severity': 'serious', 'region': 'Whole page', 'page': path, 'selector': 'a[href^="#"]', 'detail': '', 'note': 'No skip link.'})
        elif skip[0].attrs['href'][1:] not in ids: pf.append({'rule': 'skip-link-broken', 'wcag': '2.4.1', 'severity': 'serious', 'region': 'Whole page', 'page': path, 'selector': sel(skip[0]), 'detail': skip[0].attrs['href'], 'note': 'Skip link target not found.'})
        if not re.search(r'<html[^>]*\slang="[a-z]', s['head']): pf.append({'rule': 'html-lang-missing', 'wcag': '3.1.1', 'severity': 'serious', 'region': 'Whole page', 'page': path, 'selector': 'html', 'detail': '', 'note': 'Missing lang.'})
        if not re.search(r'<title>[^<]+', s['head']): pf.append({'rule': 'title-missing', 'wcag': '2.4.2', 'severity': 'serious', 'region': 'Whole page', 'page': path, 'selector': 'title', 'detail': '', 'note': 'Missing title.'})
        h1 = [n for n in main_t.all if n.tag == 'h1'] + [n for n in parse(s['header'] + s['footer']).all if n.tag == 'h1']
        if len(h1) == 0: pf.append({'rule': 'heading-no-h1', 'wcag': '1.3.1 / 2.4.6', 'severity': 'moderate', 'region': 'Main content', 'page': path, 'selector': 'h1', 'detail': '', 'note': 'No h1.'})
        if len(h1) > 1: pf.append({'rule': 'heading-multiple-h1', 'wcag': '1.3.1 / 2.4.6', 'severity': 'minor', 'region': 'Main content', 'page': path, 'selector': 'h1', 'detail': ' | '.join(own_text(n)[:30] for n in h1), 'note': 'More than one h1.'})
        if re.search(r'autoplay\s*:\s*(\{|true)', s['main'] + s['tail']): pf.append({'rule': 'carousel-autoplay-indicative', 'wcag': '2.2.2', 'severity': 'moderate', 'region': 'Main content', 'page': path, 'selector': 'swiper', 'detail': 'autoplay in inline config', 'note': 'Auto-moving carousels need a pause control. Indicative: configuration found in inline script.'})
    json.dump({'shared': sf, 'pages': pf, 'npages': len(pages)}, open(os.path.join(CACHE, 'a11y-findings.json'), 'w'))
    print('shared findings', len(sf), 'page findings', len(pf), 'pages', len(pages))
    stamp.script_ran(10)


if __name__ == '__main__':
    main()
