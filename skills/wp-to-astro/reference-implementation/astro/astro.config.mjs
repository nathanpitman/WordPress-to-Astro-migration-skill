import { defineConfig } from 'astro/config';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Copies each stylesheet from src/styles/ to the exact URL path the pages already link to, so no <link>
// markup has to change (src/styles/manifest.json lists the mapping and the per-template load order).
const serveStyles = {
  name: 'serve-original-stylesheet-paths',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const manifest = JSON.parse(fs.readFileSync('src/styles/manifest.json', 'utf8'));
      for (const s of manifest.stylesheets) {
        const dest = path.join(fileURLToPath(dir), s.servedPath);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.copyFileSync(s.source, dest);
      }
    },
  },
};

// Static output that mirrors the WordPress URL scheme: trailing slashes everywhere, one directory per page.
export default defineConfig({
  site: 'https://example.com'  // set to the production origin,
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  compressHTML: false,
  integrations: [serveStyles],
});
