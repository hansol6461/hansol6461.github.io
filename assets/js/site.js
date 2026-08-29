/* Publication year filter. Progressive: the buttons stay hidden
   unless JS runs, so the full list is always readable. */
(function () {
  var bar = document.querySelector('[data-filter]');
  if (!bar) return;
  bar.hidden = false;

  var items = Array.prototype.slice.call(document.querySelectorAll('.pub'));

  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('.chip');
    if (!btn) return;

    var year = btn.dataset.year;
    bar.querySelectorAll('.chip').forEach(function (c) {
      c.classList.toggle('is-on', c === btn);
    });
    items.forEach(function (li) {
      li.hidden = !(year === 'all' || li.dataset.year === year);
    });
  });
})();

/* Highlight the section currently in view in the rail nav. */
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a'));
  if (!links.length || !('IntersectionObserver' in window)) return;

  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });

  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      var a = map[en.target.id];
      if (a) a.setAttribute('aria-current', en.isIntersecting ? 'true' : 'false');
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  Object.keys(map).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) obs.observe(el);
  });
})();
