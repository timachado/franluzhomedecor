<?php
/**
 * Plugin Name: FranLuz Seller App Lock
 * Description: Valida o FranLuz Seller como TWA e mantém o aplicativo restrito ao Seller Center.
 * Version: 1.1.0
 * Author: T.I. Machado — Soluções em Tecnologia
 */

defined('ABSPATH') || exit;

final class FranLuz_Seller_App_Lock {
    const VERSION = '1.1.0';
    const HOME_PACKAGE = 'com.franluz.homedecor';
    const HOME_FINGERPRINT = 'D5:37:A7:2C:E6:8A:15:54:93:BB:3D:94:C9:53:09:66:DF:B0:03:4C:AF:47:C0:8A:64:4F:33:9B:D5:0C:EA:68';
    const SELLER_PACKAGE = 'com.franluz.seller';
    const SELLER_FINGERPRINT = '79:E2:22:E5:19:B9:40:D1:23:86:D1:08:E8:F2:4E:B6:4A:23:02:78:6A:D4:DC:D8:78:0B:DE:1B:4C:30:9E:60';

    public function __construct() {
        add_action('template_redirect', [$this, 'bootstrap_route'], -100);
        add_action('wp_head', [$this, 'inject_lock'], 0);
        add_action('login_head', [$this, 'inject_lock'], 0);
        add_action('admin_init', [$this, 'ensure_assetlinks']);
        add_action('admin_notices', [$this, 'admin_notice']);
    }

    public static function activate(): void {
        $self = new self();
        $self->write_assetlinks();
    }


    private function seller_user_allowed(): bool {
        if (!is_user_logged_in()) {
            return false;
        }

        $user = wp_get_current_user();
        $roles = (array) $user->roles;
        $seller_roles = ['administrator', 'shop_manager', 'seller', 'vendedor', 'vendor'];

        return (bool) array_intersect($seller_roles, $roles)
            || user_can($user, 'manage_woocommerce')
            || user_can($user, 'edit_products');
    }

    public function bootstrap_route(): void {
        if (is_admin()) {
            return;
        }

        $uri = isset($_SERVER['REQUEST_URI']) ? wp_unslash($_SERVER['REQUEST_URI']) : '';
        $path = wp_parse_url($uri, PHP_URL_PATH);
        if ($path !== '/franluz-seller-app' && $path !== '/franluz-seller-app/') {
            return;
        }

        nocache_headers();
        header('Content-Type: text/html; charset=utf-8');

        if (is_user_logged_in() && !$this->seller_user_allowed()) {
            $logout = wp_logout_url(home_url('/franluz-seller-app/'));
            ?>
            <!doctype html>
            <html lang="pt-BR">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
                <meta name="theme-color" content="#fff8ef">
                <title>FranLuz Seller</title>
                <style>html,body{margin:0;min-height:100%;background:#fff8ef}body{display:grid;place-items:center;font-family:system-ui;color:#573225;padding:24px;box-sizing:border-box}.box{max-width:440px;text-align:center;background:#fff;padding:28px;border-radius:22px;box-shadow:0 12px 34px rgba(87,50,37,.1)}h1{font-size:24px}p{color:#756760;line-height:1.5}a{display:block;margin-top:18px;padding:14px 18px;background:#573225;color:#fff;text-decoration:none;border-radius:14px;font-weight:700}</style>
            </head>
            <body>
                <div class="box">
                    <h1>Acesso exclusivo do vendedor</h1>
                    <p>Esta conta não possui permissão para o FranLuz Seller. Entre com a conta de vendedor/administrador autorizada.</p>
                    <a href="<?php echo esc_url($logout); ?>">Sair desta conta</a>
                </div>
                <script>sessionStorage.setItem('franluzSellerAppModeV1','1');</script>
            </body>
            </html>
            <?php
            exit;
        }

        $target = is_user_logged_in()
            ? home_url('/seller-franluz/?seller_app=1&twa=1')
            : home_url('/minha-conta/?seller_app_auth=1');
        ?>
        <!doctype html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
            <meta name="theme-color" content="#fff8ef">
            <title>FranLuz Seller</title>
            <style>html,body{margin:0;min-height:100%;background:#fff8ef}body{display:grid;place-items:center;font-family:system-ui;color:#573225}.f{font-size:52px;font-weight:800}</style>
        </head>
        <body>
            <div class="f">F</div>
            <script>
            sessionStorage.setItem('franluzSellerAppModeV1','1');
            window.location.replace(<?php echo wp_json_encode($target); ?>);
            </script>
        </body>
        </html>
        <?php
        exit;
    }

    private function assetlinks_path(): string {
        return trailingslashit(ABSPATH) . '.well-known/assetlinks.json';
    }

    private function expected_entries(): array {
        return [
            [
                'relation' => ['delegate_permission/common.handle_all_urls'],
                'target' => [
                    'namespace' => 'android_app',
                    'package_name' => self::HOME_PACKAGE,
                    'sha256_cert_fingerprints' => [self::HOME_FINGERPRINT],
                ],
            ],
            [
                'relation' => ['delegate_permission/common.handle_all_urls'],
                'target' => [
                    'namespace' => 'android_app',
                    'package_name' => self::SELLER_PACKAGE,
                    'sha256_cert_fingerprints' => [self::SELLER_FINGERPRINT],
                ],
            ],
        ];
    }

    public function write_assetlinks(): bool {
        $dir = trailingslashit(ABSPATH) . '.well-known';
        if (!is_dir($dir) && !wp_mkdir_p($dir)) {
            update_option('franluz_seller_assetlinks_error', 'Não foi possível criar a pasta .well-known.');
            return false;
        }

        $existing = [];
        $path = $this->assetlinks_path();
        if (is_file($path)) {
            $raw = @file_get_contents($path);
            $decoded = json_decode((string) $raw, true);
            if (is_array($decoded)) {
                foreach ($decoded as $entry) {
                    $package = $entry['target']['package_name'] ?? '';
                    if (!in_array($package, [self::HOME_PACKAGE, self::SELLER_PACKAGE], true)) {
                        $existing[] = $entry;
                    }
                }
            }
        }

        $payload = array_merge($existing, $this->expected_entries());
        $json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        $written = @file_put_contents($path, $json . "\n", LOCK_EX);

        if ($written === false) {
            update_option('franluz_seller_assetlinks_error', 'Não foi possível atualizar .well-known/assetlinks.json. Verifique as permissões da hospedagem.');
            return false;
        }

        delete_option('franluz_seller_assetlinks_error');
        return true;
    }

    public function ensure_assetlinks(): void {
        if (!current_user_can('manage_options')) {
            return;
        }

        $path = $this->assetlinks_path();
        $needs_update = !is_file($path);

        if (!$needs_update) {
            $raw = (string) @file_get_contents($path);
            $needs_update = strpos($raw, self::HOME_PACKAGE) === false
                || strpos($raw, self::HOME_FINGERPRINT) === false
                || strpos($raw, self::SELLER_PACKAGE) === false
                || strpos($raw, self::SELLER_FINGERPRINT) === false;
        }

        if ($needs_update) {
            $this->write_assetlinks();
        }
    }

    public function admin_notice(): void {
        if (!current_user_can('manage_options')) {
            return;
        }

        $error = get_option('franluz_seller_assetlinks_error');
        if ($error) {
            echo '<div class="notice notice-error"><p><strong>FranLuz Seller:</strong> ' . esc_html($error) . '</p></div>';
        }
    }

    public function inject_lock(): void {
        if (is_admin()) {
            return;
        }

        $seller_url = home_url('/seller-franluz/?seller_app=1&twa=1');
        $bootstrap_url = home_url('/franluz-seller-app/');
        $logged_in = is_user_logged_in();
        $seller_allowed = $this->seller_user_allowed();
        ?>
        <style id="franluz-seller-app-lock-style">
            html.franluz-seller-app-mode #wpadminbar,
            html.franluz-seller-app-mode #masthead,
            html.franluz-seller-app-mode #colophon,
            html.franluz-seller-app-mode .site-header,
            html.franluz-seller-app-mode .site-footer,
            html.franluz-seller-app-mode .storefront-primary-navigation,
            html.franluz-seller-app-mode .main-navigation,
            html.franluz-seller-app-mode .handheld-navigation,
            html.franluz-seller-app-mode .site-search,
            html.franluz-seller-app-mode .woocommerce-store-notice,
            html.franluz-seller-app-mode .whatsapp-float,
            html.franluz-seller-app-mode .floating-whatsapp,
            html.franluz-seller-app-mode .franluz-bottom-nav,
            html.franluz-seller-app-mode .flc-bottom-nav,
            html.franluz-seller-app-mode .mobile-bottom-nav {
                display: none !important;
            }
            html.franluz-seller-app-mode,
            html.franluz-seller-app-mode body {
                margin-top: 0 !important;
                background: #fff8ef !important;
            }
        </style>
        <script id="franluz-seller-app-lock-script">
        (function () {
            'use strict';

            var KEY = 'franluzSellerAppModeV1';
            var sellerUrl = <?php echo wp_json_encode($seller_url); ?>;
            var bootstrapUrl = <?php echo wp_json_encode($bootstrap_url); ?>;
            var loggedIn = <?php echo $logged_in ? 'true' : 'false'; ?>;
            var sellerAllowed = <?php echo $seller_allowed ? 'true' : 'false'; ?>;
            var current = new URL(window.location.href);

            if (current.searchParams.get('seller_app') === '1') {
                sessionStorage.setItem(KEY, '1');
            }

            if (sessionStorage.getItem(KEY) !== '1') {
                return;
            }

            document.documentElement.classList.add('franluz-seller-app-mode');

            if (loggedIn && !sellerAllowed) {
                window.location.replace(bootstrapUrl);
                return;
            }

            function isSellerPath(path) {
                return path === '/seller-franluz' || path.indexOf('/seller-franluz/') === 0;
            }

            function isAuthPath(path) {
                return path === '/wp-login.php'
                    || path === '/minha-conta'
                    || path.indexOf('/minha-conta/') === 0;
            }

            function isAllowed(url) {
                if (url.origin !== window.location.origin) {
                    return false;
                }
                if (isSellerPath(url.pathname)) {
                    return true;
                }
                return !loggedIn && isAuthPath(url.pathname);
            }

            function normalizeSellerLink(url) {
                if (isSellerPath(url.pathname)) {
                    url.searchParams.set('seller_app', '1');
                    url.searchParams.set('twa', '1');
                }
                return url;
            }

            if (!isAllowed(current)) {
                window.location.replace(sellerUrl);
                return;
            }

            document.addEventListener('click', function (event) {
                var anchor = event.target && event.target.closest ? event.target.closest('a[href]') : null;
                if (!anchor) return;

                var raw = anchor.getAttribute('href') || '';
                if (!raw || raw.charAt(0) === '#' || raw.indexOf('javascript:') === 0) return;
                if (raw.indexOf('mailto:') === 0 || raw.indexOf('tel:') === 0 || raw.indexOf('whatsapp:') === 0) return;

                var target;
                try { target = new URL(anchor.href, window.location.href); } catch (e) { return; }

                if (isAllowed(target)) {
                    if (isSellerPath(target.pathname)) {
                        anchor.href = normalizeSellerLink(target).href;
                    }
                    return;
                }

                event.preventDefault();
                event.stopImmediatePropagation();
                window.location.assign(sellerUrl);
            }, true);

            document.addEventListener('submit', function (event) {
                var form = event.target;
                if (!form || !form.action) return;

                var target;
                try { target = new URL(form.action, window.location.href); } catch (e) { return; }

                if (isAllowed(target)) return;

                event.preventDefault();
                event.stopImmediatePropagation();
                window.location.assign(sellerUrl);
            }, true);

            window.addEventListener('pageshow', function () {
                var here = new URL(window.location.href);
                if (sessionStorage.getItem(KEY) === '1' && !isAllowed(here)) {
                    window.location.replace(sellerUrl);
                }
            });
        })();
        </script>
        <?php
    }
}

register_activation_hook(__FILE__, ['FranLuz_Seller_App_Lock', 'activate']);
new FranLuz_Seller_App_Lock();
