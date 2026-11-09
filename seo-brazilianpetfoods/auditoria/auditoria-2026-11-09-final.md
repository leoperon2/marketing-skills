# Auditoria final — brazilianpetfoods.com.br (9/11/2026)

## Evolução (rastreio de 197–203 URLs)
| Indicador | 1ª auditoria | Após rodada 4 | Agora |
|---|---|---|---|
| URLs fora do ar (não-200) | 2 | 0 | 0 |
| Páginas sem descrição | 120 | 4 | 4 |
| Títulos > 60 caracteres | 53 | 1 | 1 (corrigido agora) |
| Páginas indexáveis sem H1 | 2 | 2 | 0 |
| Resposta HTML média (curl) | 0,94 s | 0,96 s | 0,42 s |

## Velocidade
- PageSpeed (usuário): celular 61→83, desktop 93. Lighthouse local (mais lento): celular 62, desktop 70.
- Cache de página ativo (sessão PHP do plugin CAPTCHA removida).
- Pendentes: Pagelayer (2), CSS/JS bloqueantes, Cloudflare Browser Cache TTL 1 ano.

## Pendências
- 58 URLs de tag noindex ainda no sitemap (SiteSEO > Sitemap XML).
- Home listada em 3 sitemaps (post, page, product).
- Segurança: /wp-json/wp/v2/users público; readme.html e license.txt públicos; sem HSTS/X-Frame/X-Content-Type.
- /imagens/ e /kitvendas-canister/ abrem sem login (noindex, mas visíveis).
- Sem descrição: brazilian-swine-tech, tags petfood/canister/brazilianpetfoods. Descrição >160: marcas magic-pet, canister, snow-dog.
- robots.txt (gerenciado pelo Cloudflare) bloqueia crawlers de IA (GPTBot, ClaudeBot, Google-Extended etc.).
- Acessibilidade 91: contraste (mantido por decisão do cliente), ordem de títulos, links sem nome.
