<?php
/**
 * Plugin Name: Canister - Titulos em Bricolage Grotesque
 * Description: Corrige a fonte dos titulos (H1-H3) do site para Bricolage Grotesque, sobrescrevendo a regra que forca ADLaM Display.
 * Version: 1.1.0
 * Author: Canister
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'wp_head', function () {
	echo '<style id="canister-bricolage-fix">
	body .elementor h1, body .elementor h2, body .elementor h3,
	body.canister-home .hero h1, body.canister-home h1, body.canister-home h2, body.canister-home h3,
	body h1.hero-title {
		font-family: "Bricolage Grotesque", "Bricolage Fallback", sans-serif !important;
	}
	</style>' . "\n";
}, 99999 );
