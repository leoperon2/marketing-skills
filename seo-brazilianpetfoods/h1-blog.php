<?php
/* WPCode > PHP Snippet > "Run Everywhere" > nome: "H1 do blog (invisível)"
   Adiciona um <h1> visualmente oculto na página de listagem do blog (Posts Page),
   que hoje não tem nenhum H1. Não muda o layout. */
add_action( 'loop_start', function ( $query ) {
    static $done = false;
    if ( $done || ! $query->is_main_query() || ! is_home() ) { return; }
    $done = true;
    echo '<h1 style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0">'
        . esc_html( 'Blog da Brazilian Pet Foods: novidades, nutrição e dicas para pets' ) . '</h1>';
} );
