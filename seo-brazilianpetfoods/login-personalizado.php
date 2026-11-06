<?php
/**
 * Personalização da tela de login (wp-login.php) — Brazilian Pet Foods.
 *
 * Como usar: colar no plugin WPCode / Code Snippets (tipo PHP, "Executar em todo o site"),
 * ou no functions.php do tema filho. NÃO funciona em "CSS adicional" do tema, porque essa
 * área não é carregada na tela de login.
 *
 * Antes de ativar, ajustar as 4 cores e o endereço do logo abaixo.
 */

add_action( 'login_enqueue_scripts', function () {
	$logo      = 'https://brazilianpetfoods.com.br/wp-content/uploads/2026/03/BrazilianPetFoods-150px.png'; // trocar por logo maior (ideal: 320x120 px, PNG/SVG transparente)
	$cor_marca = '#0B4F9E'; // [CONFIRMAR] azul/cor principal da marca
	$cor_dest  = '#F5B800'; // [CONFIRMAR] amarelo/cor de destaque
	$cor_fundo = '#F7F4EC'; // fundo claro
	$cor_texto = '#1F2A37';
	?>
	<style>
		body.login {
			background: <?php echo esc_html( $cor_fundo ); ?>;
			color: <?php echo esc_html( $cor_texto ); ?>;
		}
		body.login::before {
			content: "";
			position: fixed; inset: 0 0 auto 0; height: 8px;
			background: <?php echo esc_html( $cor_dest ); ?>;
		}
		#login h1 a {
			background-image: url('<?php echo esc_url( $logo ); ?>');
			background-size: contain;
			background-repeat: no-repeat;
			background-position: center;
			width: 220px; height: 110px;
		}
		.login form {
			border: 0;
			border-radius: 12px;
			box-shadow: 0 8px 24px rgba(0,0,0,.08);
			padding: 28px 24px;
		}
		.login label { font-weight: 600; }
		.login input[type="text"],
		.login input[type="password"] {
			border-radius: 8px;
			border: 1px solid #cfd6df;
			min-height: 44px;
		}
		.login input:focus {
			border-color: <?php echo esc_html( $cor_marca ); ?>;
			box-shadow: 0 0 0 1px <?php echo esc_html( $cor_marca ); ?>;
		}
		.wp-core-ui .button-primary {
			background: <?php echo esc_html( $cor_marca ); ?>;
			border-color: <?php echo esc_html( $cor_marca ); ?>;
			border-radius: 8px;
			min-height: 44px;
			font-weight: 600;
		}
		.wp-core-ui .button-primary:hover,
		.wp-core-ui .button-primary:focus {
			background: <?php echo esc_html( $cor_dest ); ?>;
			border-color: <?php echo esc_html( $cor_dest ); ?>;
			color: #1F2A37;
		}
		.login #nav a, .login #backtoblog a { color: <?php echo esc_html( $cor_marca ); ?>; }
	</style>
	<?php
} );

// O logo deixa de apontar para wordpress.org e passa a apontar para o site.
add_filter( 'login_headerurl', fn() => home_url( '/' ) );
add_filter( 'login_headertext', fn() => 'Brazilian Pet Foods' );

// Tela de login fora do índice do Google.
add_action( 'login_head', function () {
	echo '<meta name="robots" content="noindex, nofollow">' . "\n";
} );
