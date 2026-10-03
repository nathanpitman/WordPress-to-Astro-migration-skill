"""Generates a small synthetic site that looks like a stock WordPress install (block theme markup, Yoast on most
pages and Rank Math on one, core sitemaps and feed, a Contact Form 7 form with nonces, core /page/2/ pagination, a
themed 404) as site.json. Used by smoke.sh to exercise the reference scripts without any real site.
Usage: python3 gen.py <port>"""
import os, sys
PORT = sys.argv[1]; ORIGIN = f'http://localhost:{PORT}'
site = {}
def head(title, desc, canon, rankmath=False):
    if rankmath:
        seo = f'''<!-- Search Engine Optimization by Rank Math - https://rankmath.com/ -->
<title>{title}</title>
<meta name="description" content="{desc}"/>
<meta name="robots" content="follow, index, max-snippet:-1"/>
<link rel="canonical" href="{canon}" />
<meta property="og:locale" content="en_US" />
<meta property="og:title" content="{title}" />
<script type="application/ld+json" class="rank-math-schema">{{"@context":"https://schema.org","@graph":[{{"@type":"WebPage","name":"{title}"}}]}}</script>
<!-- /Search Engine Optimization by Rank Math plugin -->'''
    else:
        seo = f'''<!-- This site is optimized with the Yoast SEO plugin v22.0 - https://yoast.com/wordpress/plugins/seo/ -->
<title>{title}</title>
<meta name='robots' content='index, follow, max-image-preview:large' />
<meta name="description" content="{desc}" />
<link rel="canonical" href="{canon}" />
<meta property="og:title" content="{title}" />
<meta name="twitter:card" content="summary_large_image" />
<script type="application/ld+json" class="yoast-schema-graph">{{"@context":"https://schema.org","@graph":[{{"@type":"WebPage","name":"{title}"}}]}}</script>
<!-- / Yoast SEO plugin. -->'''
    return f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
{seo}
<link rel='stylesheet' id='theme-css' href='{ORIGIN}/wp-content/themes/twentytwentyfive/style.css?ver=1.0' media='all' />
<link rel="icon" href="{ORIGIN}/wp-content/uploads/icon.png" sizes="32x32" />
<link rel="alternate" type="application/rss+xml" title="Feed" href="{ORIGIN}/feed/" />
<script src="{ORIGIN}/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>
</head>'''
def nav(cur):
    items = [('/', 'Home'), ('/about/', 'About'), ('/contact/', 'Contact'), ('/category/news/', 'News')]
    li = '\n'.join(f'<li class="menu-item{" current-menu-item" if p == cur else ""}"><a href="{ORIGIN}{p}">{n}</a></li>' for p, n in items)
    return f'<header class="wp-block-template-part"><div class="wp-block-group"><p class="site-title"><a href="{ORIGIN}/">Example Blog</a></p><nav class="wp-block-navigation"><ul>\n{li}\n</ul></nav><form role="search" method="get" action="{ORIGIN}/"><input type="search" name="s" /></form></div></header>'
FOOT = '<footer class="wp-block-template-part"><p>© Example Blog</p></footer>'
def page(path, bodycls, title, main, rankmath=False, extra_tail=''):
    html = head(title, f'{title} description', ORIGIN + path, rankmath) + f'''
<body class="{bodycls}">
<script>document.body.classList.add('js');</script>
<div class="wp-site-blocks">
{nav(path)}
<main class="wp-block-group">
{main}
</main>
{FOOT}
</div>
<script id="theme-js" src="{ORIGIN}/wp-content/themes/twentytwentyfive/app.js?ver=1.0"></script>
{extra_tail}
</body>
</html>
'''
    site[path] = html
page('/', 'home blog wp-theme-twentytwentyfive', 'Example Blog', '<h1>Latest posts</h1><article><h2><a href="%s/hello-world/">Hello world</a></h2><img src="%s/wp-content/uploads/2024/01/hero.jpg" alt="Hero" /></article><nav class="pagination"><a href="%s/page/2/">Older</a></nav>' % (ORIGIN, ORIGIN, ORIGIN))
page('/page/2/', 'blog paged paged-2 wp-theme-twentytwentyfive', 'Example Blog - Page 2', '<h1>Older posts</h1><p>None.</p>')
page('/about/', 'page-template-default page page-id-2 wp-theme-twentytwentyfive', 'About - Example Blog', '<h1>About</h1><p>All about us. <a href="%s/missing/">gone</a></p>' % ORIGIN, rankmath=True)
page('/hello-world/', 'post-template-default single single-post postid-1 single-format-standard wp-theme-twentytwentyfive', 'Hello world - Example Blog', '<article><h1>Hello world</h1><p>Welcome to <a href="%s/about/#team">the team</a>.</p></article>' % ORIGIN)
page('/category/news/', 'archive category category-news wp-theme-twentytwentyfive', 'News - Example Blog', '<h1>News</h1><p>Category archive</p>')
page('/contact/', 'page-template-default page page-id-3 wp-theme-twentytwentyfive', 'Contact - Example Blog', '<h1>Contact</h1><div class="wpcf7" id="wpcf7-f5-p3-o1"><form action="/contact/#wpcf7-f5-p3-o1" method="post" class="wpcf7-form" novalidate="novalidate"><input type="hidden" name="_wpnonce" value="a1b2c3d4e5" /><input type="text" name="your-name" /><input type="submit" value="Send" /></form></div>', extra_tail='<script>var x = {"nonce":"0123456789"};</script>')
nf = page('/this-page-does-not-exist/', 'error404 wp-theme-twentytwentyfive', 'Page not found - Example Blog', '<h1>Page not found</h1>')
sm = lambda *u: '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="%s/wp-sitemap.xsl" ?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % (ORIGIN, ''.join('<url><loc>%s%s</loc></url>' % (ORIGIN, x) for x in u))
files = {
 '/robots.txt': 'User-agent: *\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n\nSitemap: %s/wp-sitemap.xml\n' % ORIGIN,
 '/wp-sitemap.xml': '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="%s/wp-sitemap.xsl" ?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>%s/wp-sitemap-posts-post-1.xml</loc></sitemap><sitemap><loc>%s/wp-sitemap-posts-page-1.xml</loc></sitemap></sitemapindex>' % (ORIGIN, ORIGIN, ORIGIN),
 '/wp-sitemap.xsl': '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"/>',
 '/wp-sitemap-posts-post-1.xml': sm('/hello-world/'),
 '/wp-sitemap-posts-page-1.xml': sm('/about/', '/contact/'),
 '/feed/': '<?xml version="1.0"?><rss version="2.0"><channel><title>Example Blog</title></channel></rss>',
 '/wp-content/themes/twentytwentyfive/style.css': 'body{background:url(images/bg.png)}',
 '/wp-content/themes/twentytwentyfive/images/bg.png': 'PNG',
 '/wp-content/themes/twentytwentyfive/app.js': 'console.log(1)',
 '/wp-includes/js/jquery/jquery.min.js': '/*jq*/',
 '/wp-content/uploads/icon.png': 'PNG',
 '/wp-content/uploads/2024/01/hero.jpg': 'JPG',
}
import json
json.dump({'pages': site, 'files': files}, open('site.json', 'w'))
