/* Replaces the Livewire behaviour that does not exist on a static site:
 *  - header "Search courses…" dropdown and the /courses/ grid search (Pagefind index of the course pages)
 *  - /courses/ category filter (navigates to the pre-rendered ?course_category=… page)
 *  - "Load more…" on /courses/ and /articles/ (appends the pre-rendered next ?page=N page)
 * Markup is untouched; this file is the only addition (docs/deviations.md D10). */
(function () {
  'use strict';
  var pagefind;
  function loadPagefind() {
    return pagefind || (pagefind = import('/pagefind/pagefind.js').then(function (m) { return m.init ? m.init().then(function () { return m; }) : m; }));
  }
  function debounce(fn, ms) { var t; return function () { var a = arguments, c = this; clearTimeout(t); t = setTimeout(function () { fn.apply(c, a); }, ms); }; }
  function search(q) {
    return loadPagefind().then(function (m) { return m.search(q); }).then(function (r) {
      return Promise.all(r.results.slice(0, 48).map(function (x) { return x.data(); }));
    }).then(function (ds) {
      return ds.map(function (d) { return { url: d.url, title: (d.meta && d.meta.title) || d.url, image: d.meta && d.meta.image }; });
    });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // ---- header dropdown search
  document.querySelectorAll('details.responsive-select').forEach(function (d) {
    var input = d.querySelector('input[placeholder="Search courses..."]');
    var box = d.querySelector('.brand-dropdown--results');
    if (!input || !box) return;
    var wrap = d.querySelector('.responsive-select__wrapper');
    var show = function (on) {
      ['group-open:grid-rows-[1fr]', 'group-open:opacity-100', 'group-open:shadow-[0_0_6.5px_0_rgba(0,0,0,0.10)]'].forEach(function (c) { if (wrap) wrap.classList[on ? 'add' : 'remove'](c); });
    };
    var run = function () {
      var q = input.value.trim();
      if (q.length < 2) { box.innerHTML = ''; show(false); return; }
      search(q).then(function (items) {
        box.innerHTML = items.length ? items.map(function (i) {
          return '<a href="' + esc(i.url) + '" style="display:block;padding:8px 0;color:inherit;text-decoration:none">' + esc(i.title) + '</a>';
        }).join('') : '<span style="display:block;padding:8px 0">No courses found</span>';
        box.scrollTop = 0; d.open = true; show(true);
      });
    };
    input.addEventListener('input', debounce(run, 250));
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); run(); } });
    var btn = d.querySelector('summary button');
    if (btn) btn.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); run(); });
  });

  // ---- /courses/ and /articles/ grid
  var main = document.querySelector('main');
  var grid = main && main.querySelector('.grid > a[href*="/courses/"], .grid > a[href*="/articles/"]');
  grid = grid && grid.parentElement;
  if (!grid) return;
  var isCourses = location.pathname.indexOf('/courses/') === 0;
  var gridInput = main.querySelector('input[placeholder="Search courses..."]');
  var more = main.querySelector('button[wire\\:click="nextPage"]');

  var current = new URLSearchParams(location.search).get('course_category');
  main.querySelectorAll('input[type=radio][value]').forEach(function (r) {
    if (current && r.value === current) r.checked = true;
    r.addEventListener('change', function () { location.href = '/courses/?course_category=' + encodeURIComponent(r.value); });
  });

  if (gridInput) {
    var card = function (i) {
      return '<a href="' + esc(i.url) + '"><article class="relative block h-full overflow-hidden rounded-[30px] border bg-white border-blue">' +
        '<div class="course-card__image max-h-190 w-full overflow-hidden">' + (i.image ? '<img decoding="async" src="' + esc(i.image) + '" class="w-full h-auto object-cover object-center" alt="" />' : '') + '</div>' +
        '<div class="course-card__content flex flex-col items-start gap-10 p-20"><h6 class="line-clamp-2 text-ellipsis text-md leading-2 text-charcoal">' + esc(i.title) + '</h6></div></article></a>';
    };
    var go = function () {
      var q = gridInput.value.trim();
      if (!q) { location.href = '/courses/'; return; }
      search(q).then(function (items) {
        grid.innerHTML = items.length ? items.map(card).join('') : '<p>No courses found.</p>';
        if (more) more.parentElement.style.display = 'none';
      });
    };
    gridInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); go(); } });
    var gb = gridInput.parentElement.querySelector('button');
    if (gb) gb.addEventListener('click', function (e) { e.preventDefault(); go(); });
  }

  if (more) {
    var params = new URLSearchParams(location.search);
    var page = parseInt(params.get('page') || '1', 10);
    more.addEventListener('click', function () {
      var p = new URLSearchParams(location.search); p.set('page', String(page + 1));
      fetch(location.pathname + '?' + p.toString()).then(function (r) { return r.text(); }).then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var first = doc.querySelector('main .grid > a');
        var g2 = first && first.parentElement;
        var known = {}; grid.querySelectorAll(':scope > a').forEach(function (a) { known[a.getAttribute('href')] = 1; });
        var added = 0;
        if (g2) g2.querySelectorAll(':scope > a').forEach(function (a) { if (!known[a.getAttribute('href')]) { grid.appendChild(document.importNode(a, true)); added++; } });
        if (!added) { more.parentElement.style.display = 'none'; return; }
        page += 1; history.replaceState(null, '', location.pathname + '?' + p.toString());
        if (!doc.querySelector('main button[wire\\:click="nextPage"]')) more.parentElement.style.display = 'none';
      });
    });
  }
})();
