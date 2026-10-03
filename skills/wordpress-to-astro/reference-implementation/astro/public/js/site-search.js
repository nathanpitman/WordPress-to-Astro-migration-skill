/* Static-host replacement for WordPress's server-side search (core ?s=term, or any theme search box named "s").
 * Searches the Pagefind index built from the finished site and lists matches inside <main>; every other page
 * and all markup are untouched. This file is the only addition (log it in docs/deviations.md).
 * Build the index after `astro build` with:  npx pagefind --site dist
 * Without the index, or without JavaScript, the form simply submits as before. */
(function () {
  'use strict';
  var inputs = document.querySelectorAll('input[name="s"]');
  if (!inputs.length) return;
  var pagefind;
  function load() {
    return pagefind || (pagefind = import('/pagefind/pagefind.js').then(function (m) { return m.init ? m.init().then(function () { return m; }) : m; }));
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function run(q) {
    var main = document.querySelector('main');
    if (!main || !q.trim()) return Promise.resolve(false);
    return load().then(function (m) { return m.search(q); }).then(function (r) {
      return Promise.all(r.results.slice(0, 50).map(function (x) { return x.data(); }));
    }).then(function (docs) {
      main.innerHTML = '<h1>Search results for “' + esc(q) + '”</h1>' + (docs.length
        ? '<ul>' + docs.map(function (d) { return '<li><a href="' + esc(d.url) + '">' + esc((d.meta && d.meta.title) || d.url) + '</a></li>'; }).join('') + '</ul>'
        : '<p>No results found.</p>');
      return true;
    });
  }
  inputs.forEach(function (input) {
    var form = input.form;
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = input.value;
      run(q).then(function (shown) {
        if (shown) history.replaceState(null, '', '/?s=' + encodeURIComponent(q));
        else form.submit(); // no index available: fall back to the normal submit
      }, function () { form.submit(); });
    });
  });
  var initial = new URLSearchParams(location.search).get('s'); // a shared /?s=term link
  if (initial) run(initial);
})();
