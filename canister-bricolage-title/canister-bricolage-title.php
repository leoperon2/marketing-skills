<?php
/**
 * Plugin Name: Canister - Titulo Bricolage Grotesque
 * Description: Aplica a fonte Bricolage Grotesque nos titulos (H1 e titulo do hero) do site.
 * Version: 1.0.0
 * Author: Canister
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style(
		'canister-bricolage-font',
		'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap',
		array(),
		null
	);

	$css = '
	h1,
	h1 *,
	.elementor-widget-heading h1.elementor-heading-title,
	.wp-block-heading:is(h1),
	.hero h1, .hero-title, .hero__title, .banner-title, .entry-title.hero {
		font-family: "Bricolage Grotesque", sans-serif !important;
		font-optical-sizing: auto;
	}';
	wp_add_inline_style( 'canister-bricolage-font', $css );
}, 99 );
