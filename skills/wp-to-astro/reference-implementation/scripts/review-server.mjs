// Local review server for the built site (dist/): `npm run review`.
//
// A static build keeps the markup exactly as served by the old site, so it still contains absolute URLs to the
// production origin (stylesheets, images, scripts, internal links). Opened locally, those would load from, and
// link to, the LIVE site. This server fixes that at SERVE time only: it rewrites the production origin to this
// server's address in text responses, so the built files stay byte-identical to the verified output.
// It also applies the host-level data the build produces: query-string rewrites (src/data/rewrites.json),
// redirects (src/data/redirects.json, plus trailing-slash redirects), content-type overrides
// (src/data/asset-content-types.json) and the themed 404.
// Third-party scripts, beacons and frames are blocked with a Content-Security-Policy so reviewing locally does
// not send hits to analytics or tag managers. Set REVIEW_ALLOW_THIRD_PARTY=1 to switch that off.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('dist');
if (!fs.existsSync(root)) { console.error('dist/ not found: run `npm run build` first.'); process.exit(1); }
const port = Number(process.env.PORT || 4322);
const local = `http://localhost:${port}`;
const site = process.env.SITE_ORIGIN || (fs.readFileSync('astro.config.mjs', 'utf8').match(/site:\s*['"]([^'"]+)['"]/) || [])[1];
const host = site ? new URL(site).host : null;
const json = (f) => (fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : {});
const rewrites = json('src/data/rewrites.json').rules || [];
const redirects = new Map((json('src/data/redirects.json').redirects || []).filter((r) => !r.from.includes(':')).map((r) => [r.from, r]));
const typeOverrides = json('src/data/asset-content-types.json').contentTypes || {};
const allowThirdParty = process.env.REVIEW_ALLOW_THIRD_PARTY === '1';

const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.xml': 'text/xml; charset=utf-8', '.xsl': 'text/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.ico': 'image/x-icon', '.pdf': 'application/pdf', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.wasm': 'application/wasm' };
const textual = /^(text\/|application\/(json|xml))/;

function queryRewrite(u) {
  const q = Object.fromEntries(u.searchParams.entries());
  const keys = Object.keys(q).sort().join();
  for (const r of rewrites) {
    if (r.path === u.pathname && Object.keys(r.query).sort().join() === keys && Object.entries(r.query).every(([k, v]) => q[k] === v)) return r.destination;
  }
  return null;
}
function localise(body) {
  if (!host) return body;
  const esc = host.replace(/\./g, '\\.');
  return body
    .replace(new RegExp(`https?:\\\\?/\\\\?/${esc}`, 'g'), (m) => (m.includes('\\') ? local.replace('//', '\\/\\/').replace(':', ':') : local))
    .replace(new RegExp(`(["'(=\\s])//${esc}`, 'g'), `$1${local}`);
}
const csp = "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-src 'self'";

http.createServer((req, res) => {
  const u = new URL(req.url, local);
  const send = (status, headers, body) => { res.writeHead(status, headers); res.end(body); };
  const red = redirects.get(u.pathname);
  if (red) return send(red.status || 301, { location: /^https?:/.test(red.to) ? red.to : red.to }, '');
  let p = decodeURIComponent(queryRewrite(u) || u.pathname);
  let f = path.join(root, p);
  if (!f.startsWith(root)) return send(403, {}, '');
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) {
    if (!p.endsWith('/')) return send(301, { location: u.pathname + '/' + u.search }, '');  // trailing-slash redirect, as WordPress did
    f = path.join(f, fs.existsSync(path.join(f, 'index.html')) ? 'index.html' : 'index.xml');  // feeds live at /feed/ as index.xml
  }
  let status = 200;
  if (!fs.existsSync(f)) { f = path.join(root, '404.html'); status = 404; if (!fs.existsSync(f)) return send(404, { 'content-type': 'text/plain' }, '404'); }
  const ext = path.extname(f).toLowerCase();
  const override = typeOverrides[p];
  let ct = override || (f.endsWith('index.xml') && !p.endsWith('.xml') ? 'application/rss+xml; charset=UTF-8' : types[ext] || 'application/octet-stream');
  const headers = { 'content-type': ct, 'cache-control': 'no-store' };
  if (!allowThirdParty) headers['content-security-policy'] = csp;
  if (textual.test(ct)) { headers['content-type'] = ct; return send(status, headers, localise(fs.readFileSync(f, 'utf8'))); }
  headers['content-length'] = fs.statSync(f).size;
  res.writeHead(status, headers); fs.createReadStream(f).pipe(res);
}).listen(port, () => {
  console.log(`Reviewing dist/ at ${local}`);
  console.log(`  production origin ${site || '(unknown)'} is rewritten to ${local} in responses (serve time only)`);
  console.log(`  third-party scripts/frames/beacons: ${allowThirdParty ? 'ALLOWED' : 'blocked (REVIEW_ALLOW_THIRD_PARTY=1 to allow)'}`);
});
