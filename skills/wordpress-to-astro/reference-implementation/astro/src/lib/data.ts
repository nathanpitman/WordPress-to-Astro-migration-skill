// Typed access to the extracted page records, shared fragments and verbatim <main> content.
import fs from 'node:fs';
import path from 'node:path';
import chrome from '../data/chrome.json';
import headItems from '../data/head-items.json';
import tailItems from '../data/tail-items.json';

export type Patch = [number, number, string];
export type Region = 'pre' | 'header' | 'mid' | 'post' | 'footer';
export interface SeoItem { kind: string; name: string; value: string | null; raw: string }
export type Entry = string | { raw: string } | { seo: number };
export interface PageRecord {
  path: string;
  /** WordPress template inferred from the body classes: home, page, post, a custom post type, archive, search, 404 */
  template: string;
  htmlAttrs: Record<string, string>;
  bodyAttrs: Record<string, string>;
  head: Entry[];
  seo: SeoItem[];
  patches: Record<Region, Patch[]>;
  tail: Entry[];
  content: string;
}

export const headRegistry = headItems as Record<string, string>;
export const tailRegistry = tailItems as Record<string, string>;

/** Apply [start, end, replacement] line splices (from the bottom up so indexes stay valid). */
export function applyPatches(base: string, patches: Patch[]): string {
  if (!patches.length) return base;
  const lines = base.split('\n');
  for (const [s, e, text] of [...patches].reverse()) lines.splice(s, e - s, text);
  return lines.join('\n');
}

/** One page's markup for a region: the shared base variant plus this page's differences. */
export function region(page: PageRecord, name: Region): string {
  return applyPatches((chrome as Record<Region, string>)[name], page.patches[name]);
}

/** The one approved client script (search / load-more on a static host) is only emitted when the file exists. */
export const hasSearchScript = fs.existsSync(path.resolve('public/js/site-search.js'));

/** Read the page records and verbatim <main> files from disk at build time (nothing is bundled into the server chunk). */
export function loadPages() {
  const root = path.resolve('src');
  const dir = path.join(root, 'data/pages');
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .sort()
    .map((f) => {
      const record = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')) as PageRecord;
      return { record, main: fs.readFileSync(path.join(root, 'content', record.content), 'utf8') };
    });
}
