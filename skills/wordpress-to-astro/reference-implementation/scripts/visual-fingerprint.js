// Paste into the browser console (or run through a browser tool) on BOTH the live page and the local review page
// at the same viewport, then compare the strings. Measures each top-level region while it is scrolled into view.
//
// Why "in view": WP Rocket's `content-visibility: auto` collapses off-screen sections on the live site, and its lazy
// loader leaves some images as placeholders, so measuring everything from the top gives misleading heights.
(async () => {
  await new Promise((r) => setTimeout(r, 1000));
  const els = [document.querySelector('header'), ...document.querySelectorAll('main > section, main > div'), document.querySelector('footer')].filter(Boolean);
  const out = [];
  for (const e of els) {
    e.scrollIntoView({ block: 'center' });
    await new Promise((r) => setTimeout(r, 300));
    out.push(Math.round(e.getBoundingClientRect().height));
  }
  window.scrollTo(0, 0);
  return `${location.pathname} vw=${innerWidth} scrollW=${document.documentElement.scrollWidth} ${out.join(',')}`;
})();
