// Typed access to the extracted page records, shared fragments and verbatim <main> content.
import fs from 'node:fs';
import path from 'node:path';
import chrome from '../data/chrome.json';
import headItems from '../data/head-items.json';
import tailItems from '../data/tail-items.json';

export type SeoItem = string[];
export type Entry = string | { raw: string } | { seo: true };
export interface PageRecord {
  path: string;
  template: 'home' | 'page' | 'course' | 'post';
  bodyClass: string;
  head: Entry[];
  seo: SeoItem[];
  headerPatches: [number, number, string][];
  footerPatches: [number, number, string][];
  tail: Entry[];
  content: string;
}

export { chrome };
export const headRegistry = headItems as Record<string, string>;
export const tailRegistry = tailItems as Record<string, string>;

/** Apply [start, end, replacement] line splices (from the bottom up so indexes stay valid). */
export function applyPatches(base: string, patches: [number, number, string][]): string {
  if (!patches.length) return base;
  const lines = base.split('\n');
  for (const [s, e, text] of [...patches].reverse()) lines.splice(s, e - s, text);
  return lines.join('\n');
}

/** Livewire embeds the current path (JSON-escaped) in the header search component. */
export function livewirePath(path: string): string {
  const p = path.replace(/^\/|\/$/g, '');
  return p ? encodeURI(decodeURI(p)).replace(/%[0-9a-f]{2}/gi, (m) => m.toUpperCase()).replace(/\//g, '\\/') : '\\/';
}

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
