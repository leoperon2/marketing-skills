<?php
/* WPCode > PHP Snippet > "Run Everywhere" > nome: "Posts: títulos em ADLaM + Leia também + CTA"
   Só atua em posts individuais que NÃO usam o layout novo (.bpf-art). Para desfazer, desative o snippet. */
add_action( 'wp_head', function () {
    if ( ! is_singular( 'post' ) ) { return; }
    echo '<style>.single-post .entry-content h2.wp-block-heading{font-family:"ADLaM Display",sans-serif;font-weight:700;color:#021B3F;margin:1.6em 0 .5em}'
       . '.bpf-more{margin:2.5em 0 0;padding:24px;background:#F2F6FA;border:1px solid #DCE4EE;border-radius:12px}'
       . '.bpf-more h3{font-family:"ADLaM Display",sans-serif;color:#021B3F;margin:0 0 12px}'
       . '.bpf-more ul{margin:0 0 16px;padding-left:18px}.bpf-more a{color:#025AA6}'
       . '.bpf-more a.bpf-btn{display:inline-block;background:#FFD812;color:#021B3F;font-weight:700;padding:12px 22px;border-radius:999px;text-decoration:none}</style>';
}, 20 );
add_filter( 'the_content', function ( $content ) {
    if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) { return $content; }
    if ( false !== strpos( $content, 'bpf-art' ) ) { return $content; }
    $id   = get_the_ID();
    $tags = wp_get_post_tags( $id, array( 'fields' => 'ids' ) );
    $args = array( 'post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => 2, 'post__not_in' => array( $id ), 'no_found_rows' => true );
    if ( $tags ) { $args['tag__in'] = $tags; }
    $rel = get_posts( $args );
    if ( count( $rel ) < 2 ) { $rel = get_posts( array_diff_key( $args, array( 'tag__in' => 1 ) ) ); }
    $html = '<aside class="bpf-more"><h3>Leia também</h3><ul>';
    foreach ( $rel as $p ) { $html .= '<li><a href="' . esc_url( get_permalink( $p ) ) . '">' . esc_html( get_the_title( $p ) ) . '</a></li>'; }
    $html .= '<li><a href="' . esc_url( home_url( '/fabrica-de-racao/' ) ) . '">Como funciona a nossa fábrica de ração</a></li></ul>'
           . '<a class="bpf-btn" href="' . esc_url( home_url( '/fabrica-de-racao/' ) ) . '">Conheça a fábrica</a></aside>';
    return $content . $html;
}, 20 );
