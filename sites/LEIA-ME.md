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

## Estado em 2026-10-22 (hospedagem pública e refinamento do Charles)
- Demos públicas: repositório `leoperon2/demos` (GitHub Pages). `prospeccao/publish.py` copia cada site para uma pasta com código não adivinhável (sal em `prospeccao/.salt`, fora do git), injeta `<meta viewport>`/charset e `noindex`, e grava `prospeccao/urls.json` (fora do git). Clone de trabalho: `/home/user/demos` (git add/commit/push main). Pages leva ~1 min; cache do navegador ~10 min (testar com `?v=N`).
- Sem a meta viewport os celulares renderizavam a 980 px e encolhiam tudo. O publicador agora injeta; no Artifact o esqueleto já traz.
- `vary.py` guarda as variações por site e os ajustes feitos à mão por slug: `OVERRIDE` (hero 6 = capa em tela cheia com parallax, gallery 5 = filtro quente + brilho na rolagem, proof 4 = cards roláveis, about 3), `FOCO_MOBILE`, `FORCE_DARK`, `DM_SITES` (modo ampliado quando a tela de toque abre a ~980 px), `LEGIVEL`, `INTRO` (animação de entrada + scroll de poucos px), `GALERIA_TEXTO`, `SOBRE_TEXTO`, `WA_TEXTO` (mensagem pronta do WhatsApp), `AVAL_LINK`. Hoje tudo isso só vale para `charles-tattoo-piercing`; os outros sites seguem o sorteio por ramo.
- `python3 vary.py [slug]` é idempotente (rodar duas vezes dá o mesmo arquivo). `python3 ../prospeccao/publish.py` regenera as pastas no clone de demos.
- Página de prospecção (`prospeccao/`, `build.py` + `template.html`): artefato https://claude.ai/artifact/CCjCvVs4Ny7Va2txNvbzy3. Só republicar quando o usuário pedir. Os links "Ver site de demonstração" do artefato publicado ainda apontam para a versão antiga; rodar `build.py` e republicar atualiza para as URLs públicas.
- Avaliações com link: todo site com seção de avaliações ganhou o último card "Veja todas as avaliações no Google" (`add_qmore` no `vary.py`, usa o `query_place_id` do link do Maps). Link direto para CADA avaliação: o `gen.py` já renderiza "Ver no Google ↗" quando a avaliação traz `reviewUrl`. O `scan/fetch_details.py` salva o item completo do Apify e agora imprime quantas avaliações vieram com `reviewUrl`. Se vier 0, o campo não veio naquela coleta: refazer só os negócios que responderem (custo do Apify), regenerar com o `gen.py` e rodar `vary.py` + `publish.py`.
- Sites refinados à mão até 2026-10-23 (cada um com bloco próprio em `vary.py`: OVERRIDE, TEMA_CUSTOM/TEMA_LIGHT, FONTE_CUSTOM, HERO_TEXTO, SOBRE_TEXTO, GALERIA_TEXTO, FINAL_TEXTO, WA_TEXTO, CSS_EXTRA): charles-tattoo-piercing, don-alberttoni, jennifer-benke, tayz-bessa, nina-pet-shop, aure-art-studio, excellence-studio, barbearia-los-chicanos, new-visuallize. As capas são montadas por `make_hero_<nome>.py` a partir de `sites/_fontes/` (recortes de prints do Instagram, sem clientes) e geram `hero.jpg`/`hero-m.jpg`. Foto de capa nunca com cliente. `publish.py` versiona imagens por hash e carimba cada página para se atualizar sozinha (cache do GitHub Pages é de 10 min). `sites/instagram.json` alimenta o link do Instagram (contato e rodapé).
- Pendências extras: 79 textos com contraste entre 3 e 4,5 em 18 sites; rodapé apagado fora dos refinados; Chewie e Clínica Vitza sem Instagram.
- Pendências: levar para os outros sites as melhorias do Charles (começar pelos de tatuagem); revisar capas com foto de cliente; trocar fotos com rosto e a foto com "Depois" na galeria do Charles; confirmar no celular se o scroll de entrada recolhe a barra do navegador.
- Para gastar menos token: sessão nova partindo deste arquivo, ajustes em lote e conferir por medição, sem abrir capturas à toa.

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
