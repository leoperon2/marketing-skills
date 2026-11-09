<?php
/* WPCode > PHP Snippet > "Run Everywhere" > nome: "Scripts para o rodapé (velocidade)"
   Move 4 scripts (jQuery Migrate e Download Manager) do <head> para o fim da página,
   só para visitantes (não afeta quem está logado nem o editor do Elementor).
   Para desfazer, basta desativar o snippet. */
add_action( 'template_redirect', function () {
    if ( is_admin() || is_user_logged_in() || wp_doing_ajax() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) { return; }
    ob_start( function ( $html ) {
        if ( ! is_string( $html ) || strpos( $html, '</body>' ) === false ) { return $html; }
        $moved = '';
        foreach ( array( 'jquery-migrate-js', 'wpdm-modal-js', 'wpdm-frontend-js-js', 'wpdm-frontjs-js' ) as $id ) {
            $re = '#<script[^>]*\sid=["\']' . preg_quote( $id, '#' ) . '["\'][^>]*></script>\s*#';
            if ( preg_match( $re, $html, $m ) ) {
                $moved .= trim( $m[0] ) . "\n";
                $html = str_replace( $m[0], '', $html );
            }
        }
        if ( '' === $moved ) { return $html; }
        $pos = strrpos( $html, '</body>' );
        return substr( $html, 0, $pos ) . $moved . substr( $html, $pos );
    } );
}, 1 );
