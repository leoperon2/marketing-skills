// Coleta gratuita do Google Maps com Chromium headless (Playwright). Sem Apify.
// Uso: node scan_free.js "barbearia,oficina de motos" "Curitiba PR,Londrina PR" 40 saida.json
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('fs');
const [niches, cities, perArg, out] = process.argv.slice(2);
const PER = parseInt(perArg || '40', 10), CONC = 4;

const num = s => { const m = (s || '').replace(/\./g, '').match(/[\d,]+/); return m ? parseFloat(m[0].replace(',', '.')) : null; };

async function listPlaces(ctx, q) {
  const p = await ctx.newPage();
  await p.goto(`https://www.google.com/maps/search/${encodeURIComponent(q)}?hl=pt-BR`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  try { await p.click('button:has-text("Aceitar tudo")', { timeout: 3000 }); } catch {}
  await p.waitForSelector('a.hfpxzc', { timeout: 20000 }).catch(() => {});
  let last = 0, stale = 0;
  while (stale < 3) {
    const n = await p.locator('a.hfpxzc').count();
    if (n >= PER) break;
    stale = n === last ? stale + 1 : 0; last = n;
    await p.locator('div[role="feed"]').evaluate(el => el.scrollBy(0, 4000)).catch(() => {});
    await p.waitForTimeout(1500);
  }
  const hrefs = await p.locator('a.hfpxzc').evaluateAll(a => a.map(x => x.href));
  await p.close();
  return [...new Set(hrefs)].slice(0, PER);
}

async function detail(ctx, url) {
  const p = await ctx.newPage();
  try {
    await p.goto(url + (url.includes('?') ? '&' : '?') + 'hl=pt-BR', { waitUntil: 'domcontentloaded', timeout: 45000 });
    await p.waitForSelector('h1', { timeout: 15000 });
    await p.waitForTimeout(1200);
    return await p.evaluate(() => {
      const t = sel => document.querySelector(sel)?.textContent?.trim() || '';
      const attr = (sel, a) => document.querySelector(sel)?.getAttribute(a) || '';
      const rate = document.querySelector('div.F7nice span[aria-hidden="true"]')?.textContent || '';
      const revLabel = document.querySelector('div.F7nice span[aria-label*="avalia"]')?.getAttribute('aria-label') || '';
      const phoneBtn = document.querySelector('button[data-item-id^="phone:tel:"]');
      return {
        nome: t('h1'), categoria: t('button.DkEaL'), rating: rate, avaliacoes_txt: revLabel,
        telefone: phoneBtn ? phoneBtn.getAttribute('data-item-id').replace('phone:tel:', '') : '',
        site: attr('a[data-item-id="authority"]', 'href'),
        endereco: t('button[data-item-id="address"]'),
        fotos_txt: [...document.querySelectorAll('button[aria-label]')].map(b => b.getAttribute('aria-label')).find(l => /foto/i.test(l) && /\d/.test(l)) || '',
        fechado: /permanentemente/i.test(document.body.innerText.slice(0, 3000)),
      };
    }).then(d => ({ ...d, nota: num(d.rating), reviews: num(d.avaliacoes_txt), url }));
  } catch (e) { return { url, erro: e.message.slice(0, 80) }; }
  finally { await p.close(); }
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium', args: ['--no-sandbox'],
    proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const ctx = await b.newContext({ locale: 'pt-BR', ignoreHTTPSErrors: true, viewport: { width: 1280, height: 900 } });
  const results = [], seen = new Set();
  for (const city of cities.split(',')) for (const niche of niches.split(',')) {
    const q = `${niche.trim()} em ${city.trim()}`;
    const urls = (await listPlaces(ctx, q)).filter(u => !seen.has(u));
    urls.forEach(u => seen.add(u));
    console.error(q, '->', urls.length, 'negócios');
    for (let i = 0; i < urls.length; i += CONC) {
      const batch = await Promise.all(urls.slice(i, i + CONC).map(u => detail(ctx, u)));
      batch.forEach(r => results.push({ ...r, busca: q }));
      fs.writeFileSync(out, JSON.stringify(results, null, 1));
    }
  }
  await b.close();
  console.error('total', results.length);
})();
