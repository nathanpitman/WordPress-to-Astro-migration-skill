"""Serves site.json (written by gen.py) on 127.0.0.1:<port>, answering like WordPress: 301 to the trailing-slash URL, 403 for /wp-admin, themed 404 elsewhere.
Usage: python3 serve.py <port>"""
import http.server, json, sys, urllib.parse as up
d = json.load(open('site.json'))
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = up.urlsplit(self.path).path
        if p.startswith('/wp-admin'): return self.send(403, 'text/plain', 'no')
        if p == '/this-page-does-not-exist/': return self.send(404, 'text/html; charset=UTF-8', d['pages'][p])
        if p in d['pages']: return self.send(200, 'text/html; charset=UTF-8', d['pages'][p])
        if p in d['files']:
            ct = 'text/xml' if p.endswith(('.xml','.xsl')) or p == '/feed/' else 'text/plain' if p.endswith('.txt') else 'application/octet-stream'
            if p.endswith('.css'): ct='text/css'
            if p.endswith('.js'): ct='text/javascript'
            if p.endswith('.jpg'): ct='image/jpeg'
            if p.endswith('.png'): ct='image/png'
            return self.send(200, ct, d['files'][p])
        if p.rstrip('/') + '/' in d['pages'] and not p.endswith('/'):
            self.send_response(301); self.send_header('Location', p + '/'); self.end_headers(); return
        return self.send(404, 'text/html; charset=UTF-8', d['pages']['/this-page-does-not-exist/'])
    def send(self, code, ct, body):
        b = body.encode(); self.send_response(code); self.send_header('Content-Type', ct); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
