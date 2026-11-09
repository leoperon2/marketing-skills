(function () {
  var MOBILE = 'https://brazilianpetfoods.com.br/wp-content/uploads/2026/11/hero-960.mp4';
  var small = window.matchMedia('(max-width:1024px)').matches;
  var pending = [], loaded = false;
  function start(v, src) { v.setAttribute('src', src); v.preload = 'auto'; var p = v.play && v.play(); if (p && p.catch) p.catch(function () {}); }
  function fix(v) {
    if (!v || v.tagName !== 'VIDEO' || v.__bpf) return;
    var src = v.getAttribute('src') || '';
    if (src.indexOf('hero-1920') < 0 && src.indexOf('hero-960') < 0) return;
    v.__bpf = 1;
    var real = small ? MOBILE : src;
    v.removeAttribute('src'); v.preload = 'none';
    if (loaded) start(v, real); else pending.push([v, real]);
  }
  new MutationObserver(function (list) {
    list.forEach(function (m) {
      if (m.type === 'attributes') { fix(m.target); return; }
      m.addedNodes.forEach(function (n) {
        if (n.nodeType !== 1) return;
        if (n.tagName === 'VIDEO') fix(n); else if (n.querySelectorAll) n.querySelectorAll('video').forEach(fix);
      });
    });
  }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'] });
  window.addEventListener('load', function () {
    setTimeout(function () { loaded = true; pending.forEach(function (a) { start(a[0], a[1]); }); pending = []; }, 800);
  });
})();
