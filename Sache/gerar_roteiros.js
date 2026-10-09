const fs = require('fs'), path = require('path');
const dir = process.argv[2];
const html = fs.readFileSync(path.join(dir, 'mente-do-pet-roteiro.html'), 'utf8');
const a = html.indexOf('var STYLE'), b = html.indexOf('var KEY');
const { STYLE, PETS } = new Function(html.slice(a, b) + '; return {STYLE,PETS};')();
const names = {
  gato: ['Video_1_Gato_Carne_ao_Molho', 'Vídeo 1 · Gato · Sachê Carne ao Molho'],
  cao: ['Video_2_Cao_Almondega_ao_Pomodoro', 'Vídeo 2 · Cão · Sachê Almôndega ao Pomodoro']
};
for (const pet of ['gato', 'cao']) {
  const d = PETS[pet];
  let md = `# ${names[pet][1]}\n\n${d.sub}\n\nFormato: vertical 9:16. Cenas marcadas com [PDV] formam o corte de 15s.\n\n## Blocos fixos\n\n**Personagem:** ${d.char}\n\n**Estilo real:** ${STYLE.real}\n\n**Estilo fantasia:** ${STYLE.fant}\n\n---\n\n`;
  d.scenes.forEach((s, i) => {
    const p = s.p.replace('{P}', d.char) + ', ' + STYLE[s.s];
    md += `## Cena ${i + 1} · ${s.title} (${s.t})${s.pdv ? ' [PDV]' : ''}\n\n**Tipo:** ${s.s === 'real' ? 'Vida real' : 'Fantasia'}\n\n**Descrição:** ${s.d}\n\n**Prompt:**\n\n${p}\n\n`;
  });
  md += `---\n\n## Observações\n\n- Packshot e logo entram na edição (embalagem real + marca Canister). Os prompts pedem espaço vazio.\n- Use a primeira imagem aprovada do pet como referência nas cenas seguintes.\n- No corte de PDV, o vídeo precisa funcionar sem som.\n- Apelos permitidos na assinatura (da embalagem): "Seu Pet Merece!", "Sem corantes", "Vitaminas & Minerais".\n`;
  fs.writeFileSync(path.join(dir, names[pet][0] + '.md'), md, 'utf8');
}
console.log('ok');
