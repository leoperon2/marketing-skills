/* WPCode > Snippet JavaScript > Local: Cabeçalho do site (Site Wide Header)
   Elementor: o link do vídeo do HERO deve ser o arquivo de DESKTOP (hero-desktop.mp4).
   Em telas até 1024px este script troca para o arquivo leve (hero-960.mp4). */
(function () {
  if (!window.matchMedia('(max-width:1024px)').matches) return;
  var DESK = 'hero-desktop', MOBILE = 'https://brazilianpetfoods.com.br/wp-content/uploads/2026/11/hero-960.mp4';
  function fix(v) {
    if (v && v.tagName === 'VIDEO' && (v.getAttribute('src') || '').indexOf(DESK) > -1) v.setAttribute('src', MOBILE);
  }
  new MutationObserver(function (list) {
    list.forEach(function (m) {
      if (m.type === 'attributes') { fix(m.target); return; }
      m.addedNodes.forEach(function (n) {
        if (n.nodeType !== 1) return;
        if (n.tagName === 'VIDEO') fix(n);
        else if (n.querySelectorAll) n.querySelectorAll('video').forEach(fix);
      });
    });
  }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'] });
})();
