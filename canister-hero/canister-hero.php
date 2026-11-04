<?php
/**
 * Plugin Name: Canister - Hero da Home
 * Description: Cria a secao hero da home (Sabor de comida caseira.) ja com a fonte Bricolage Grotesque. Use o shortcode [canister_hero]. Ao ativar, cria uma pagina rascunho "Home Canister".
 * Version: 1.0.0
 * Author: Canister
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function canister_hero_assets() {
	wp_enqueue_style(
		'canister-hero-font',
		'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800&display=swap',
		array(),
		null
	);
	$css = '
	.cn-hero{position:relative;overflow:hidden;background-color:#2b2a29;background-image:radial-gradient(rgba(255,255,255,.05) 1px,transparent 1px),radial-gradient(rgba(0,0,0,.25) 1px,transparent 1px);background-size:7px 7px,11px 11px;color:#f3efe8;font-family:"Bricolage Grotesque",sans-serif}
	.cn-hero *{box-sizing:border-box}
	.cn-hero__inner{max-width:1200px;margin:0 auto;padding:72px 24px;display:flex;align-items:center;gap:32px;min-height:560px}
	.cn-hero__text{flex:1 1 55%}
	.cn-hero__eyebrow{margin:0 0 24px;color:#ee2a3c;font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
	.cn-hero h1.cn-hero__title{margin:0 0 28px;font-family:"Bricolage Grotesque",sans-serif!important;font-weight:800;font-size:clamp(48px,8vw,96px);line-height:.98;letter-spacing:-.02em;color:#f3efe8}
	.cn-hero__title span{color:#ee2a3c}
	.cn-hero__sub{margin:0 0 32px;max-width:480px;font-size:19px;line-height:1.6;color:#e9e4da}
	.cn-hero__btn{display:inline-block;background:#ee2a3c;color:#fff;padding:14px 28px;border-radius:999px;font-weight:700;text-decoration:none}
	.cn-hero__img{flex:1 1 45%;text-align:center}
	.cn-hero__img img{max-width:100%;height:auto}
	@media(max-width:800px){.cn-hero__inner{flex-direction:column;text-align:left;padding:48px 20px}}';
	wp_add_inline_style( 'canister-hero-font', $css );
}
add_action( 'wp_enqueue_scripts', 'canister_hero_assets' );

function canister_hero_shortcode( $atts ) {
	$a = shortcode_atts(
		array(
			'eyebrow' => 'Canister Premium · Cães e Gatos',
			'titulo'  => 'Sabor de comida',
			'destaque' => 'caseira.',
			'texto'   => 'Nutrição, sabor e carinho em cada refeição, para o momento favorito do seu pet.',
			'imagem'  => '',
			'botao'   => '',
			'link'    => '#',
		),
		$atts
	);
	ob_start(); ?>
	<section class="cn-hero">
		<div class="cn-hero__inner">
			<div class="cn-hero__text">
				<p class="cn-hero__eyebrow"><?php echo esc_html( $a['eyebrow'] ); ?></p>
				<h1 class="cn-hero__title"><?php echo esc_html( $a['titulo'] ); ?> <span><?php echo esc_html( $a['destaque'] ); ?></span></h1>
				<p class="cn-hero__sub"><?php echo esc_html( $a['texto'] ); ?></p>
				<?php if ( $a['botao'] ) : ?>
					<a class="cn-hero__btn" href="<?php echo esc_url( $a['link'] ); ?>"><?php echo esc_html( $a['botao'] ); ?></a>
				<?php endif; ?>
			</div>
			<?php if ( $a['imagem'] ) : ?>
				<div class="cn-hero__img"><img src="<?php echo esc_url( $a['imagem'] ); ?>" alt=""></div>
			<?php endif; ?>
		</div>
	</section>
	<?php
	return ob_get_clean();
}
add_shortcode( 'canister_hero', 'canister_hero_shortcode' );

register_activation_hook( __FILE__, function () {
	if ( get_page_by_title( 'Home Canister' ) ) {
		return;
	}
	wp_insert_post(
		array(
			'post_title'   => 'Home Canister',
			'post_status'  => 'draft',
			'post_type'    => 'page',
			'post_content' => '[canister_hero]',
		)
	);
} );
