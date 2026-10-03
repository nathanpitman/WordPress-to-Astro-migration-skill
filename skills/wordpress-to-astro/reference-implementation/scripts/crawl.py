#!/usr/bin/env python3
"""Polite BFS crawler. Stdlib only. Caches raw body + headers; does not follow redirects automatically."""
import hashlib, http.client, json, os, re, sys, time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag, quote

ORIGIN = os.environ["SITE_ORIGIN"].rstrip("/")
HOST = ORIGIN.split("//", 1)[1]
UA = f"wordpress-to-astro (Claude Code; run by {os.environ['CRAWLER_USER']}; crawling {HOST})"
DELAY = 0.6  # seconds between requests (robots.txt declares no crawl-delay)
ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(ROOT, "pages")
INDEX = os.path.join(ROOT, "crawl-index.json")
os.makedirs(PAGES, exist_ok=True)

DISALLOWED = [re.compile(p) for p in (r"^/wp/wp-admin/(?!admin-ajax\.php)", r"^/\?s=", r"^/page/[^/]*/\?s=", r"^/search/")]


def allowed(path_query):
    return not any(r.search(path_query) for r in DISALLOWED)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []  # (kind, url)
        self.canonical = None
        self.title = ""
        self._t = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(("a", a["href"]))
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if "canonical" in rel.split():
                self.canonical = a.get("href")
            if a.get("href") and any(x in rel for x in ("next", "prev", "alternate", "amphtml")):
                self.links.append(("link-" + rel, a["href"]))
        elif tag == "form" and a.get("action"):
            self.links.append(("form", a["action"]))
        elif tag == "title":
            self._t = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False

    def handle_data(self, d):
        if self._t:
            self.title += d


def key(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def fetch(url):
    sp = urlsplit(url)
    path = quote(sp.path or "/", safe="/%:@!$&'()*+,;=-._~")
    if sp.query:
        path += "?" + quote(sp.query, safe="/%:@!$&'()*+,;=-._~?")
    conn = http.client.HTTPSConnection(sp.netloc, timeout=30)
    conn.request("GET", path, headers={"User-Agent": UA, "Accept": "text/html,*/*", "Accept-Encoding": "identity"})
    r = conn.getresponse()
    body = r.read()
    hdrs = [(k, v) for k, v in r.getheaders()]
    conn.close()
    return r.status, hdrs, body


def norm(href, base):
    href = href.strip()
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:", "#", "sms:")):
        return None
    u = urldefrag(urljoin(base, href))[0]
    return u


def main():
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else {"pages": {}, "external": {}, "assets": {}}
    seeds = [ORIGIN + "/"]
    for f in ("post", "page", "course"):
        t = open(os.path.join(ROOT, "sitemaps", f"{f}-sitemap.xml")).read()
        seeds += re.findall(r"<loc>([^<]*)</loc>", t)
    queue = []
    seen = set(idx["pages"].keys())
    for s in seeds:
        if s not in seen and s not in queue:
            queue.append(s)
            idx.setdefault("discovered", {}).setdefault(s, ["sitemap" if s != ORIGIN + "/" else "seed"])
    # re-queue anything discovered but not yet fetched
    for u in list(idx.get("discovered", {})):
        if u not in seen and u not in queue:
            queue.append(u)

    n = 0
    while queue:
        url = queue.pop(0)
        if url in idx["pages"]:
            continue
        sp = urlsplit(url)
        pq = (sp.path or "/") + (("?" + sp.query) if sp.query else "")
        if not allowed(pq):
            idx["pages"][url] = {"skipped": "robots.txt disallow"}
            continue
        chain = []
        cur = url
        status = None
        for _ in range(8):
            time.sleep(DELAY)
            try:
                status, hdrs, body = fetch(cur)
            except Exception as e:
                idx["pages"][url] = {"error": repr(e), "chain": chain}
                status = None
                break
            h = {k.lower(): v for k, v in hdrs}
            chain.append({"url": cur, "status": status, "location": h.get("location")})
            k = key(cur)
            with open(os.path.join(PAGES, k + ".headers.json"), "w") as f:
                json.dump({"url": cur, "status": status, "headers": hdrs}, f)
            if status in (301, 302, 303, 307, 308) and h.get("location"):
                nxt = urljoin(cur, h["location"])
                if urlsplit(nxt).netloc != HOST:
                    break
                cur = nxt
                continue
            break
        if status is None:
            continue
        final = cur
        entry = {"final": final, "status": status, "chain": chain, "key": key(final)}
        ct = (h.get("content-type") or "")
        entry["content_type"] = ct
        if "html" in ct:
            with open(os.path.join(PAGES, key(final) + ".html"), "wb") as f:
                f.write(body)
            p = Links()
            try:
                p.feed(body.decode("utf-8", "replace"))
            except Exception as e:
                entry["parse_error"] = repr(e)
            entry["title"] = " ".join(p.title.split())
            entry["canonical"] = p.canonical
            internal = []
            for kind, href in p.links:
                u = norm(href, final)
                if not u:
                    continue
                us = urlsplit(u)
                if us.netloc == HOST:
                    # only crawl HTML-ish paths (skip obvious assets)
                    if re.search(r"\.(jpe?g|png|gif|svg|webp|avif|pdf|zip|css|js|ico|woff2?|ttf|mp4|mp3|docx?|xlsx?|pptx?)$", us.path, re.I):
                        idx["assets"].setdefault(u, []).append(final)
                        continue
                    if us.path.startswith("/wp-json/") or us.path.endswith("/feed/") or us.path.startswith("/wp/xmlrpc"):
                        idx["assets"].setdefault(u, []).append(final)  # API/feed endpoints: recorded, not crawled
                        continue
                    internal.append((kind, u))
                    if u not in idx["pages"] and u not in queue:
                        queue.append(u)
                        idx.setdefault("discovered", {}).setdefault(u, []).append("link from " + final)
                    elif u in idx.get("discovered", {}) and len(idx["discovered"][u]) < 5:
                        idx["discovered"][u].append("link from " + final)
                else:
                    idx["external"].setdefault(u, []).append(final)
            entry["links"] = internal
        idx["pages"][url] = entry
        n += 1
        if n % 20 == 0:
            json.dump(idx, open(INDEX, "w"))
            print(f"{n} fetched, {len(queue)} queued", flush=True)
    json.dump(idx, open(INDEX, "w"))
    print("done", len(idx["pages"]), "pages")


if __name__ == "__main__":
    main()
