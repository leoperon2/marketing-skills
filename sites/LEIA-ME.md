# Sites de prospecção (protótipos por negócio)

Estado em 2026-10-21. Branch `claude/zen-edison-lxvb0x`.

## O que existe
- `don-alberttoni/`: site feito à mão (modelo de referência, com logo, mosaico e plano B).
- 48 pastas `<slug>/index.html`: geradas por `gen.py` a partir de dados públicos do Google Maps e do Instagram.
- `vary.py`: variação de layout por site (ver abaixo). `variants.json` registra a combinação de cada um.
- `scan/`: varredura do Maps (`scan_maps.py`, Apify) e coleta de detalhes (`fetch_details.py`).
- `sites/prospeccao.csv` (fora do git): lista dos negócios com contato, nota e link do protótipo.

## Pipeline (tudo por script, sem chamadas manuais)
1. `scan/scan_maps.py run|rank` → candidatos e `top50.csv`.
2. `scan/fetch_details.py` → avaliações e fotos de avaliações (`sites/_data/*.json`).
3. Instagram: perfis e publicações via Apify (`apify/instagram-profile-scraper`, `apify/instagram-post-scraper`); resultado em `_data/ig_*.json`, classificação em `ig_status.json`.
4. `fetch_photos.py` (fotos de avaliações) e `ig_photos.py` (fotos do Instagram) → `<slug>/_src/` e `photos.json`.
5. `mark_text.py` → OCR marca fotos com texto (cartazes). `gen.py` descarta essas.
6. `gen.py` → `<slug>/index.html` + `<slug>/img/` (hero, g1..gN, logo). Vetos de fotos em `vetoes_hash.json` (por conteúdo).
7. `vary.py` (roda no fim do `gen.py`, ou sozinho: `python3 vary.py [slug ...]`) injeta um bloco `<!--vary:start-->` por site, idempotente.

## Variação de layout (vary.py)
Sites do mesmo ramo/cidade não podem parecer o mesmo. Cada site recebe uma combinação de 14 dimensões: fonte do título, cor de acento, hero (6 formas: texto/foto invertidos, foto de fundo, centralizado, banner, arco), moldura da foto, cabeçalho (escuro, claro, acento, marca centralizada), galeria (gaps, cantos, P&B no hover), títulos, formas de botão/cartão, prova social, faixa, ordem das seções, sobre e animação de rolagem. As combinações são sorteadas por ramo para maximizar a diferença entre vizinhos. Testado: sem rolagem horizontal em 390 e 1280 px, em todos os sites. `don-alberttoni` e quem já tem site ficam de fora.

## Decisões já tomadas
- Foto de capa (hero): não pode ser foto de cliente/pessoas. Tem que ser comida, produto ou a marca. Trocado à mão no gordo-magro (g4, recorte 4:3); `gen.py` ainda escolhe o hero por qualidade, então rodar de novo desfaz a troca. Revisar a capa dos demais sites.
- Galeria sem legenda nenhuma. Mosaico dinâmico: verticais, dobro do espaço, panorâmicas e pequenas.
- Logo = foto de perfil do Instagram (cabeçalho, selo na foto principal e rodapé).
- Link "Plano B do seu site" (página leosumiu) no rodapé de todos, só para mostrar que a função existe.
- Quem já tem site (Instagram com link de site) sai da prospecção: Suzana Dias, Marshals Tattoo, Win Hamburgueria, Pet Shop Agropal, Pilgrim Burgers (pasta apagada).
- Página de links (Linktree etc.) e agendamento NÃO contam como site.

## Pendências
- Republicar os sites como artefatos (`Artifact` com `url`): depois do `vary.py` TODOS estão desatualizados nos artefatos (os 8 que estavam finais: charles, tayz, gordo-magro, mr-dohms, flex-race, jennifer-benke, los-chicanos, marumbi; os demais estão ainda na versão sem logo/mosaico antigo/com legendas). Publicar uma vez só, no fim. Pilgrim saiu. Lista de ids em `sites/urls.json` (fora do git) e `republish.json`.
- Links dos artefatos são privados. Para mandar aos donos é preciso hospedagem pública (Cloudflare Pages ou GitHub Pages), uma pasta por cliente. Contas e domínios ficam para depois.
- Apify: conta nova com US$ 5 mensais. Trocar tokens que foram colados no chat.
- 4 negócios sem logo (sem Instagram encontrado): nina-pet-shop, clinica-vitza, chewie-burger-and-beer, sereia-ink-tattoo.

## Como gastar menos
- Publicar artefatos uma vez no fim, não a cada ajuste. Cada republicação custa uma chamada por site.
- Quando houver hospedagem pública, publicar com um único `git push` ou script, sem chamadas por site.
- Evitar abrir imagens para conferir; usar uma amostra.
- Trabalhar em sessão curta e nova, partindo deste arquivo.
