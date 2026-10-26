# Pacote SEO — brazilianpetfoods.com.br

Foco: posicionar "fábrica de ração" + marcas + correções técnicas.
Itens entre [COLCHETES] são dados reais que só a empresa tem: preencher antes de publicar. Não publique números ou certificações inventados.

---

## 1. HOME — title, description, H1

**Title (≤ 60 caracteres)**
```
Fábrica de Ração para Cães e Gatos | Brazilian Pet Foods
```

**Meta description (≤ 155 caracteres)**
```
Fábrica de ração para cães e gatos desde 1992. Canister, Péddy, Snow Dog e Snow Cat. Fale com nosso time comercial e seja revendedor.
```

**H1 (substituir "Há mais de 30 anos, alimentando momentos")**
```
Fábrica de ração para cães e gatos: mais de 30 anos alimentando momentos
```

**Parágrafo de apoio abaixo do H1 (texto visível, não escondido)**
```
A Brazilian Pet Foods é uma fábrica de ração para cães e gatos desde 1992. Produzimos as marcas Canister, Péddy, Snow Dog e Snow Cat com controle de qualidade em todas as etapas, da seleção dos ingredientes à entrega ao ponto de venda. Atendemos pet shops, agropecuárias e distribuidores em [REGIÕES ATENDIDAS].
```

**Onde editar:** Yoast/Rank Math (title e description) e Elementor (H1 e parágrafo).

---

## 2. NOVA PÁGINA — /fabrica-de-racao/

Slug: `fabrica-de-racao` · Título da página (H1): **Fábrica de Ração para Cães e Gatos**

**Title SEO:** `Fábrica de Ração para Cães e Gatos desde 1992 | Brazilian Pet Foods`
**Meta description:** `Conheça a fábrica de ração da Brazilian Pet Foods: processo, controle de qualidade e marcas Canister, Péddy, Snow Dog e Snow Cat. Seja nosso revendedor.`

### Texto

# Fábrica de Ração para Cães e Gatos

A Brazilian Pet Foods é uma fábrica de ração para cães e gatos em [CIDADE/UF], operando desde 1992. Da formulação à embalagem, cada etapa é controlada para entregar alimentos seguros, palatáveis e nutricionalmente completos.

## Nossa fábrica em números
- Fundada em 1992
- [CAPACIDADE PRODUTIVA, ex.: X toneladas/mês]
- [ÁREA DA PLANTA, ex.: X m²]
- [Nº DE PONTOS DE VENDA / CIDADES ATENDIDAS]

## Como fabricamos nossas rações
1. **Seleção e recebimento de ingredientes:** análise de cada lote antes de entrar na produção.
2. **Formulação:** receitas desenvolvidas por [nutricionista/médico-veterinário responsável].
3. **Moagem e mistura:** dosagem precisa de cada ingrediente.
4. **Extrusão:** cozimento que melhora digestibilidade e segurança alimentar.
5. **Secagem, cobertura e resfriamento:** [DETALHAR, se aplicável].
6. **Embalagem e rastreabilidade:** cada lote é identificado e rastreável.
7. **Controle de qualidade:** análises [FÍSICO-QUÍMICAS E MICROBIOLÓGICAS] em laboratório.

## Qualidade e certificações
Registro no MAPA: [Nº]. [BPF / ISO / HACCP / outras certificações reais].

## Marcas produzidas em nossa fábrica
- **Canister** — [descrição em 1 linha] → link para a página da marca
- **Péddy** — [descrição] → link
- **Snow Dog** — [descrição] → link
- **Snow Cat** — [descrição] → link

## Seja revendedor
Atendemos pet shops, agropecuárias, clínicas veterinárias e distribuidores. Fale com o time comercial: [BOTÃO → /fale-conosco-sac/ ou WhatsApp].

## Perguntas frequentes
**Vocês vendem direto da fábrica?** [RESPONDER: vendas para lojistas/distribuidores; consumidor final compra nos pontos de venda.]
**Onde fica a fábrica?** [ENDEREÇO].
**Qual o pedido mínimo para revenda?** [RESPONDER].
**As rações são registradas no MAPA?** [RESPONDER].
**Quais regiões vocês atendem?** [RESPONDER].

### Âncoras internas a usar em outras páginas apontando para esta
"fábrica de ração", "nossa fábrica", "fábrica de ração para cães e gatos".

---

## 3. PÁGINA OPCIONAL — /marca-propria-racao/ (só se a empresa oferece)

**Title:** `Marca Própria de Ração (Private Label) | Brazilian Pet Foods`
**Description:** `Fábrica de ração com serviço de marca própria para cães e gatos: formulação, produção e embalagem. Peça uma proposta.`
H1: **Marca própria de ração para cães e gatos**
Seções: como funciona, formulações, volumes mínimos [RESPONDER], prazo, embalagem, CTA de proposta.

---

## 4. SCHEMA JSON-LD (colar na home e na página da fábrica)

Em Yoast/Rank Math: nome da organização preenchido nas configurações. Ou colar via plugin "Insert Headers and Footers" / Elementor HTML. Substituir [ ].

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://brazilianpetfoods.com.br/#organization",
      "name": "Brazilian Pet Foods",
      "url": "https://brazilianpetfoods.com.br/",
      "logo": "https://brazilianpetfoods.com.br/wp-content/uploads/2025/08/cropped-favicon-bpf.png",
      "foundingDate": "1992",
      "description": "Fábrica de ração para cães e gatos. Marcas Canister, Péddy, Snow Dog e Snow Cat.",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "[RUA, Nº]",
        "addressLocality": "[CIDADE]",
        "addressRegion": "[UF]",
        "postalCode": "[CEP]",
        "addressCountry": "BR"
      },
      "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "[+55 ...]",
        "contactType": "sales",
        "areaServed": "BR",
        "availableLanguage": "pt-BR"
      },
      "sameAs": ["[URL INSTAGRAM]", "[URL FACEBOOK]", "[URL LINKEDIN]", "[URL YOUTUBE]"]
    },
    {
      "@type": "WebSite",
      "@id": "https://brazilianpetfoods.com.br/#website",
      "url": "https://brazilianpetfoods.com.br/",
      "name": "Brazilian Pet Foods",
      "inLanguage": "pt-BR",
      "publisher": { "@id": "https://brazilianpetfoods.com.br/#organization" }
    }
  ]
}
</script>
```

Na página da fábrica, adicionar também `FAQPage` com as perguntas acima (depois de respondidas) e `BreadcrumbList`.

---

## 5. ARTIGOS DO BLOG (todos linkam para /fabrica-de-racao/)

| # | Título | Palavra-chave |
|---|---|---|
| 1 | Como é feita a ração para cães: o passo a passo dentro de uma fábrica | como é feita a ração |
| 2 | Ração extrusada: o que é e por que ela é segura e digestível | ração extrusada |
| 3 | Como escolher uma fábrica de ração para marca própria | fábrica de ração marca própria |
| 4 | Como virar revendedor de ração premium: guia para pet shops | revender ração premium |
| 5 | Ração para gatos castrados: o que observar no rótulo | ração gatos castrados |
| 6 | Ração para filhotes, adultos e sênior: diferenças e como escolher | ração por idade |

---

## 6. CORREÇÕES TÉCNICAS (checklist)

- [ ] **robots.txt:** linha de sitemap aponta para `/sitemaps.xml`. Corrigir para `Sitemap: https://brazilianpetfoods.com.br/sitemap.xml` e enviar no Search Console.
- [ ] **Open Graph:** trocar `og:image` (logo 150 px) por imagem 1200×630 px; `twitter:card` = `summary_large_image`.
- [ ] **Schema:** preencher o `name` vazio da Organization (item 4).
- [ ] **noindex:** `/login/`, resultados de busca interna, tags sem conteúdo.
- [ ] **Cache:** ativar cache de página (WP Rocket/LiteSpeed/Cloudflare APO); hoje o HTML é servido com `no-store`.
- [ ] **Imagens:** converter para WebP, `loading="lazy"` abaixo da dobra, preencher `alt` (2+ imagens da home sem alt).
- [ ] **Scripts:** auditar plugins (77 scripts na home); adiar/remover os não essenciais.
- [ ] **Cloudflare:** ativar HSTS.
- [ ] **Menu e rodapé:** linkar "Fábrica" e as quatro marcas.
- [ ] **Search Console + GA4:** confirmar instalados; acompanhar impressões para "fábrica de ração".
- [ ] **Google Business Profile:** criar/otimizar com endereço da fábrica, se aplicável.

## 7. ORDEM DE EXECUÇÃO
1. Home (item 1) e schema (item 4)
2. Página /fabrica-de-racao/ (item 2), linkada no menu
3. Correções técnicas rápidas (item 6)
4. Artigos 1–2, depois 3–6 (um por semana)
