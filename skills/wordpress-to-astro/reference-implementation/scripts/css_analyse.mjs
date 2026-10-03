// Parse each cached stylesheet with postcss and report size, @-rules, url() references and exact duplicate rules.
import postcss from 'postcss';
import fs from 'node:fs';
import path from 'node:path';
const dir = '.crawl-cache/css';
const out = {};
for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.css')).sort()) {
  const css = fs.readFileSync(path.join(dir, f), 'utf8');
  const root = postcss.parse(css);
  const seen = new Map(); let rules = 0, dups = 0; const at = {}; const urls = new Set(); const dupSamples = [];
  const walk = (node, ctx) => node.each((n) => {
    if (n.type === 'rule') {
      rules++;
      const key = ctx + '|' + n.selector.replace(/\s+/g, ' ') + '{' + n.nodes.map((d) => d.toString()).join(';') + '}';
      if (seen.has(key)) { dups++; if (dupSamples.length < 3) dupSamples.push(n.selector.slice(0, 60)); } else seen.set(key, 1);
    }
    if (n.type === 'atrule') { at[n.name] = (at[n.name] || 0) + 1; if (n.nodes) walk(n, ctx + '@' + n.name + ' ' + n.params); }
  });
  walk(root, '');
  for (const m of css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g)) if (!m[2].startsWith('data:')) urls.add(m[2]);
  out[f] = { bytes: css.length, rules, exactDuplicateRules: dups, atRules: at, urls: [...urls], dupSamples, imports: [...css.matchAll(/@import[^;]+;/g)].map((m) => m[0]) };
}
console.log(JSON.stringify(out, null, 1));
