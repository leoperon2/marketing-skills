# Correções técnicas — brazilianpetfoods.com.br

Não tenho acesso ao WordPress; este é o passo a passo para quem edita o site. Não consegui identificar qual plugin de SEO o site usa (não aparece no HTML): onde diz "plugin de SEO", usar o que estiver instalado (Yoast, Rank Math, SEOPress, etc.).

## A. /snowdogflores/ (não deveria estar indexada)
Hoje a URL mostra o mesmo conteúdo da home (canonical já aponta para a home), e o QR code do catálogo Flores aponta para ela, então NÃO apagar: quem escaneia precisa chegar a algum lugar.
1. Criar redirecionamento 301 de `/snowdogflores/` para a página desejada. Sugestão: `/marcas/` (ou a linha Flores no movimentosnow.com.br, se preferirem).
   - Plugin de redirecionamento (Redirection, ou o módulo do plugin de SEO), ou Cloudflare: Rules > Redirect Rules > origem `/snowdogflores*`, destino escolhido, status 301.
2. Remover `/snowdogflores/` do sitemap (o 301 já faz isso; se continuar, marcar `noindex` até o redirecionamento funcionar).
3. Perguntar a quem criou a página por que existe; se for cópia da home feita no Elementor, pode ser movida para a lixeira depois que o 301 estiver ativo.

## C. Páginas fracas: /compare/ e /evercompare/ (e sitemap)
Conteúdo real das duas: "No products added to the compare" e o shortcode `[evercompare_table]` aparecendo sem ser processado. São páginas técnicas do plugin de comparação, sem valor de busca.
1. `/compare/` e `/evercompare/`: em cada página, no plugin de SEO, definir "Permitir que mecanismos de busca mostrem esta página nos resultados" = Não (`noindex`). Isso também as tira do sitemap.
2. `/painel/` e `/cart-2/`: já têm `noindex`, mas continuam listadas no sitemap. Marcar também no plugin de SEO (não só pelo tema/outro plugin) ou excluir do sitemap em Configurações > Sitemap.
3. Se o site não usa comparação de produtos, desativar o plugin de comparação.
4. Depois: testar `https://brazilianpetfoods.com.br/page-sitemap1.xml` e confirmar que as quatro saíram.

## D. H1 em /catalogo2026/ e /blog/
No Elementor, adicionar um widget Título com tag H1 (só um por página):
- /catalogo2026/: `Catálogo 2026 de rações para cães e gatos`
- /blog/: `Blog Brazilian Pet Foods: novidades e cuidados para o seu pet`
Se o /blog/ for um modelo de arquivo do Elementor Pro (Theme Builder > Arquivo), editar o modelo.

## E. Performance
1. **Cache de página:** o servidor envia `Cache-Control: no-store` e a Cloudflare marca `DYNAMIC`. Ativar o cache de página do plugin/hospedagem e, na Cloudflare, criar Cache Rule: hostname = brazilianpetfoods.com.br, ignorar `/wp-admin/`, `/login/`, `/painel/`, `/cart*` e requisições com cookie de login; Edge TTL = respeitar/override 2 h; Browser TTL = 1 h.
2. **Imagens:**
   - Ativar `lazy` nas imagens abaixo da dobra (a home tem 4 de 15).
   - Dois arquivos sem `alt`: `floating1-1.webp` e `floating2.webp` (parecem decorativos: preencher alt vazio é correto se forem só decoração; se mostrarem produto, descrever: "Ração Canister" etc.).
   - Converter imagens grandes para WebP e dimensionar ao tamanho exibido.
3. **Scripts (77 na home):** plugins carregados na home que provavelmente não são necessários nela: WooCommerce (10 arquivos), Download Manager (9), flipbook 3D (3), Mailchimp (2), Contact Form 7 + campos condicionais (3 + 2). Usar Asset CleanUp ou Perfmatters para carregar cada um só nas páginas que precisam; adiar (defer) scripts não essenciais.
4. **HSTS:** Cloudflare > SSL/TLS > Edge Certificates > HTTP Strict Transport Security: ativar com max-age de 6 meses; incluir subdomínios só se todos tiverem HTTPS.
5. **Medir:** rodar pagespeed.web.dev na home e em `/lista-de-produtos/` antes e depois; anotar LCP, CLS e INP.

## F. Imagem de compartilhamento
1. Criar imagem 1200 x 630 px (logo, nome "Brazilian Pet Foods" e marcas Canister, Péddy, Snow Dog, Snow Cat), em JPG/PNG até 1 MB, com margem de segurança de 60 px.
2. No plugin de SEO: Social > imagem padrão do Facebook/Open Graph = essa imagem; Twitter/X > tipo de card = "Resumo com imagem grande" (`summary_large_image`).
3. Testar no depurador de compartilhamento do Facebook e no LinkedIn Post Inspector (limpar o cache).

## G. Rastreamento (correção do que eu disse antes)
Eu havia dito que não achei Analytics; havia sim. A home carrega o **Google Site Kit** com a tag Google `GT-573CSGMH` (gtag.js), e o plugin de cookies (CookieAdmin) pode atrasar o disparo até o consentimento. Falta confirmar se está funcionando:
1. WordPress > Site Kit > Painel: conferir se "Analytics" e "Search Console" estão conectados (sem aviso vermelho).
2. Analytics (GA4) > Relatórios > Tempo real: abrir o site em outra aba (aceitando cookies) e ver se aparece 1 usuário.
3. Search Console: confirmar que a propriedade `brazilianpetfoods.com.br` está verificada e enviar `https://brazilianpetfoods.com.br/sitemaps.xml`.
4. No GA4: marcar como evento-chave os cliques em WhatsApp/telefone e o envio do formulário do SAC/comercial.
5. Se Analytics aparecer desconectado, reconectar pelo Site Kit com a conta Google da empresa.
