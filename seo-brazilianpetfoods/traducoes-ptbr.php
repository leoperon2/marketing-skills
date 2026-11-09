<?php
/* WPCode > PHP Snippet > "Run Everywhere" > nome: "Traduções PT-BR do front-end"
   Traduz textos que ainda saem em inglês (CookieAdmin, 404, Compare, popup de login).
   Troca os textos na hora de gerar a página. Para desfazer, basta desativar o snippet. */
add_action( 'template_redirect', function () {
    if ( is_admin() || wp_doing_ajax() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) { return; }
    ob_start( function ( $html ) {
        if ( ! is_string( $html ) || strpos( $html, '</html>' ) === false ) { return $html; }
        static $map = null;
        if ( null === $map ) {
            $pairs = array(
        'Save My Preferences' => 'Salvar minhas preferências',
        'Accept All' => 'Aceitar todos',
        'Reject All' => 'Rejeitar todos',
        '>Customize<' => '>Personalizar<',
        'Modify Cookie Preferences' => 'Alterar preferências de cookies',
        'Necessary Cookies' => 'Cookies necessários',
        'Functional Cookies' => 'Cookies funcionais',
        'Analytical Cookies' => 'Cookies analíticos',
        'Advertisement Cookies' => 'Cookies de publicidade',
        'Unclassified Cookies' => 'Cookies não classificados',
        'Always Active' => 'Sempre ativos',
        'Necessary cookies enable essential site features like secure log-ins and consent preference adjustments. They do not store personal data.' => 'Os cookies necessários habilitam recursos essenciais do site, como logins seguros e ajustes das preferências de consentimento. Eles não armazenam dados pessoais.',
        'Functional cookies support features like content sharing on social media, collecting feedback, and enabling third-party tools.' => 'Os cookies funcionais dão suporte a recursos como compartilhamento de conteúdo em redes sociais, coleta de opiniões e ferramentas de terceiros.',
        'Analytical cookies track visitor interactions, providing insights on metrics like visitor count, bounce rate, and traffic sources.' => 'Os cookies analíticos acompanham as interações dos visitantes e fornecem métricas como número de visitantes, taxa de rejeição e origens de tráfego.',
        'Advertisement cookies deliver personalized ads based on your previous visits and analyze the effectiveness of ad campaigns.' => 'Os cookies de publicidade exibem anúncios personalizados com base nas suas visitas anteriores e medem a eficácia das campanhas.',
        'Unclassified cookies are cookies that we are in the process of classifying, together with the providers of individual cookies.' => 'Cookies não classificados são aqueles que ainda estamos classificando, junto com os provedores de cada cookie.',
        'We use cookies to ensure smooth navigation and enable essential site functions. You can view detailed information about each cookie category below. ' => 'Usamos cookies para garantir uma navegação tranquila e habilitar as funções essenciais do site. Veja abaixo informações detalhadas sobre cada categoria de cookie. ',
        'Cookies marked as <b>Necessary</b> are stored in your browser because they are essential for basic site functionality. ' => 'Os cookies marcados como <b>Necessários</b> são armazenados no seu navegador porque são essenciais para o funcionamento básico do site. ',
        '<b>These cookies do not require your consent under GDPR.</b> ' => '',
        'We also use third-party cookies to analyze site usage, remember your preferences, and deliver relevant content and ads. These will only be activated with your consent. You can choose to enable or disable these cookies, but please note that turning off some types may affect your browsing experience.' => 'Também usamos cookies de terceiros para analisar o uso do site, lembrar suas preferências e oferecer conteúdo e anúncios relevantes. Eles só serão ativados com o seu consentimento. Você pode ativar ou desativar esses cookies, mas desligar alguns tipos pode afetar a sua experiência de navegação.',
        '<span>Powered by</span>' => '<span>Desenvolvido por</span>',
        '>None<' => '>Nenhum<',
        'That Page Can’t Be Found!' => 'Página não encontrada!',
        'It looks like nothing was found at this location. Maybe try to search for something else' => 'Parece que não há nada neste endereço. Tente buscar por outro conteúdo.',
        'BACK TO HOMEPAGE' => 'VOLTAR PARA A HOME',
        '<span>Compare</span>' => '<span>Comparar</span>',
        '>Compare</span></a>' => '>Comparar</span></a>',
        'class="button link-to-compare">Compare</a>' => 'class="button link-to-compare">Comparar</a>',
        'Remove all products' => 'Remover todos os produtos',
        'Sign in to access your downloads, manage your account, and continue where you left off.' => 'Acesse seus downloads, gerencie sua conta e continue de onde parou.',
        'Sign In' => 'Entrar',
        'Login Account' => 'Entrar na conta',
        'Enter your credentials to access your account' => 'Informe suas credenciais para acessar sua conta',
        '<label form=\'log\'>Login ID</label>' => '<label form=\'log\'>Usuário ou e-mail</label>',
        'Sorry. There are no posts to display' => 'Nenhum post para exibir.',
        '<title>Shopping Cart - ' => '<title>Carrinho - ',
        'No products added to the compare' => 'Nenhum produto adicionado para comparar',
        'Your email address will not be published. Required fields are marked *' => 'Seu endereço de e-mail não será publicado. Os campos obrigatórios estão marcados com *',
        'Cancel reply' => 'Cancelar resposta',
        'Leave a Reply' => 'Deixe um comentário',
        'placeholder="Name *"' => 'placeholder="Nome *"',
        'placeholder="Email *"' => 'placeholder="E-mail *"',
        'placeholder="Your comment *"' => 'placeholder="Seu comentário *"',
        'aria-label="Close"' => 'aria-label="Fechar"',
        'data-dismiss="modal">Close</button>' => 'data-dismiss="modal">Fechar</button>'
            );
            $map = array();
            foreach ( $pairs as $en => $pt ) {
                $map[ $en ] = $pt;
                // Mesmo texto dentro do JSON do CookieAdmin (tags escapadas).
                $enj = str_replace( array( '<', '>' ), array( '\\u003C', '\\u003E' ), $en );
                if ( $enj !== $en ) { $map[ $enj ] = str_replace( array( '<', '>' ), array( '\\u003C', '\\u003E' ), $pt ); }
            }
        }
        return str_replace( array_keys( $map ), array_values( $map ), $html );
    } );
}, 0 );
