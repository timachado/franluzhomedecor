package com.franluz.homedecor;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.SslErrorHandler;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String HOME_URL = "https://franluzhomedecor.infinityfree.io/?pwa=1&app=android";
    private static final String HOME_HOST = "franluzhomedecor.infinityfree.io";
    private static final int FILE_CHOOSER_REQUEST = 9021;
    private static final int IVORY = Color.rgb(255, 250, 244);
    private static final int CHOCOLATE = Color.rgb(77, 47, 36);

    private WebView webView;
    private ProgressBar progressBar;
    private FrameLayout loadingOverlay;
    private ProgressBar loadingSpinner;
    private TextView loadingStatus;
    private Button retryButton;
    private ValueCallback<Uri[]> filePathCallback;
    private boolean pageError = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(CHOCOLATE);
        getWindow().setNavigationBarColor(Color.rgb(48, 32, 25));

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(IVORY);

        webView = new WebView(this);
        webView.setBackgroundColor(IVORY);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setScrollbarFadingEnabled(true);

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(100);

        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        FrameLayout.LayoutParams progressParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(3));
        progressParams.gravity = Gravity.TOP;
        root.addView(progressBar, progressParams);

        buildLoadingOverlay();
        root.addView(loadingOverlay, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        setContentView(root);
        configureWebView();

        if (savedInstanceState == null) {
            showLoading("Abrindo a FranLuz…");
            handleIntent(getIntent());
        } else {
            webView.restoreState(savedInstanceState);
            loadingOverlay.setVisibility(View.GONE);
        }
    }

    private void buildLoadingOverlay() {
        loadingOverlay = new FrameLayout(this);
        loadingOverlay.setBackgroundColor(IVORY);
        loadingOverlay.setClickable(true);
        loadingOverlay.setFocusable(true);

        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setPadding(dp(32), dp(32), dp(32), dp(32));

        TextView brand = new TextView(this);
        brand.setText("FranLuz Home Decor");
        brand.setTextColor(CHOCOLATE);
        brand.setTextSize(25);
        brand.setGravity(Gravity.CENTER);
        brand.setTypeface(android.graphics.Typeface.SERIF, android.graphics.Typeface.BOLD);

        TextView signature = new TextView(this);
        signature.setText("ASSINATURA ARTESANAL");
        signature.setTextColor(Color.rgb(166, 124, 74));
        signature.setTextSize(10);
        signature.setGravity(Gravity.CENTER);
        signature.setLetterSpacing(0.15f);

        loadingSpinner = new ProgressBar(this);
        LinearLayout.LayoutParams spinnerParams = new LinearLayout.LayoutParams(dp(42), dp(42));
        spinnerParams.topMargin = dp(26);

        loadingStatus = new TextView(this);
        loadingStatus.setTextColor(CHOCOLATE);
        loadingStatus.setTextSize(14);
        loadingStatus.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams statusParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        statusParams.topMargin = dp(16);

        retryButton = new Button(this);
        retryButton.setText("Tentar novamente");
        retryButton.setAllCaps(false);
        retryButton.setTextColor(Color.WHITE);
        retryButton.setBackgroundColor(CHOCOLATE);
        retryButton.setVisibility(View.GONE);
        LinearLayout.LayoutParams retryParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                dp(48));
        retryParams.topMargin = dp(18);
        retryButton.setOnClickListener(v -> {
            showLoading("Reconectando à loja…");
            webView.loadUrl(HOME_URL);
        });

        box.addView(brand);
        box.addView(signature);
        box.addView(loadingSpinner, spinnerParams);
        box.addView(loadingStatus, statusParams);
        box.addView(retryButton, retryParams);

        FrameLayout.LayoutParams boxParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        boxParams.gravity = Gravity.CENTER;
        loadingOverlay.addView(box, boxParams);
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadsImagesAutomatically(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setDefaultTextEncodingName("UTF-8");

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return routeUrl(request.getUrl());
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                pageError = false;
                showLoading("Carregando sua experiência…");
            }

            @Override
            public void onPageCommitVisible(WebView view, String url) {
                super.onPageCommitVisible(view, url);
                if (!pageError) {
                    hideLoading();
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                CookieManager.getInstance().flush();
                if (!pageError) {
                    hideLoading();
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    pageError = true;
                    showError("Não foi possível carregar a loja. Verifique sua internet e tente novamente.");
                }
            }

            @Override
            public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse errorResponse) {
                if (request.isForMainFrame() && errorResponse.getStatusCode() >= 400) {
                    pageError = true;
                    showError("A FranLuz respondeu com erro " + errorResponse.getStatusCode() + ". Tente novamente em instantes.");
                }
            }

            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                handler.cancel();
                pageError = true;
                showError("Não foi possível validar a conexão segura da FranLuz. Por segurança, a página não foi aberta.");
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                progressBar.setVisibility(newProgress >= 100 ? View.GONE : View.VISIBLE);
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback, FileChooserParams fileChooserParams) {
                if (filePathCallback != null) {
                    filePathCallback.onReceiveValue(null);
                }
                filePathCallback = callback;
                Intent intent = fileChooserParams.createIntent();
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (ActivityNotFoundException e) {
                    filePathCallback = null;
                    return false;
                }
            }
        });
    }

    private void showLoading(String message) {
        pageError = false;
        loadingStatus.setText(message);
        loadingSpinner.setVisibility(View.VISIBLE);
        retryButton.setVisibility(View.GONE);
        loadingOverlay.setVisibility(View.VISIBLE);
        loadingOverlay.bringToFront();
        progressBar.bringToFront();
    }

    private void hideLoading() {
        loadingOverlay.setVisibility(View.GONE);
    }

    private void showError(String message) {
        loadingStatus.setText(message);
        loadingSpinner.setVisibility(View.GONE);
        retryButton.setVisibility(View.VISIBLE);
        loadingOverlay.setVisibility(View.VISIBLE);
        loadingOverlay.bringToFront();
        progressBar.setVisibility(View.GONE);
    }

    private boolean routeUrl(Uri uri) {
        String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase();
        String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase();

        if (("https".equals(scheme) || "http".equals(scheme)) && HOME_HOST.equals(host)) {
            return false;
        }

        if ("about".equals(scheme) || "data".equals(scheme) || "blob".equals(scheme)) {
            return false;
        }

        try {
            Intent external = new Intent(Intent.ACTION_VIEW, uri);
            startActivity(external);
        } catch (Exception ignored) {
            if ("http".equals(scheme) || "https".equals(scheme)) {
                showLoading("Abrindo página…");
                webView.loadUrl(uri.toString());
            }
        }
        return true;
    }

    private void handleIntent(Intent intent) {
        Uri data = intent != null ? intent.getData() : null;
        if (data != null && HOME_HOST.equalsIgnoreCase(data.getHost())) {
            webView.loadUrl(data.toString());
        } else {
            webView.loadUrl(HOME_URL);
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        showLoading("Abrindo link…");
        handleIntent(intent);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            showLoading("Voltando…");
            webView.goBack();
        } else {
            moveTaskToBack(true);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && filePathCallback != null) {
            Uri[] results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.setWebChromeClient(null);
            webView.setWebViewClient(null);
            webView.destroy();
        }
        super.onDestroy();
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
