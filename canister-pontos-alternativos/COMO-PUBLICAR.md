# Canister Pontos Alternativos: como publicar

Site estático (HTML + imagens). Não precisa de servidor, banco de dados nem build.

Conteúdo: `index.html` + pasta `img/`. Mantenha os dois juntos, na mesma pasta.

## Opção A: dentro do site da empresa (ex.: seusite.com.br/pontos-alternativos/)
1. Descompacte `canister-pontos-alternativos.zip`.
2. Envie `index.html` e a pasta `img/` para uma pasta nova no servidor do site (FTP, cPanel/Gerenciador de arquivos ou pedido ao time de TI), por exemplo `/pontos-alternativos/`.
3. O link será `https://seusite.com.br/pontos-alternativos/`.

## Opção B: link rápido e grátis (Netlify Drop)
1. Acesse https://app.netlify.com/drop
2. Arraste a pasta descompactada para a tela.
3. Ele devolve um link `https://nome.netlify.app`. Dá para trocar o nome e ligar um domínio próprio depois.

## Opção C: GitHub Pages
1. No GitHub: Settings > Pages > Deploy from a branch, escolha a branch e a pasta `/canister-pontos-alternativos`.
2. O link sai como `https://usuario.github.io/repositorio/`.

## Notas
- As fontes (Bricolage Grotesque e DM Sans) carregam do Google Fonts. Sem internet, o navegador usa fontes parecidas do sistema.
- Para trocar texto, edite o `index.html`. Para trocar imagem, substitua o arquivo em `img/` mantendo o mesmo nome.
- Se publicar em um subdiretório, os caminhos (`img/...`) já são relativos e funcionam sem ajuste.

## Imagem ao compartilhar no WhatsApp
No `index.html`, a linha `og:image` precisa do endereço completo da imagem. Troque
`https://SEU-DOMINIO.com.br/pontos-alternativos/img/og.jpg` pelo endereço real onde o site ficou.
Exemplo no Netlify: `https://nome.netlify.app/img/og.jpg`.
O WhatsApp guarda o resultado em cache. Para um link já compartilhado, teste com um endereço novo, por exemplo adicionando `?v=2` no final.
