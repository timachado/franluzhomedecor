package com.timachado.bibliaebd;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {
    private WebView webView;
    private FrameLayout root;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(7, 9, 22));

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(7, 9, 22));
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));
        setContentView(root);

        root.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                android.graphics.Insets bars = insets.getInsets(
                        WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout()
                );
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            } else {
                @SuppressWarnings("deprecation") int left = insets.getSystemWindowInsetLeft();
                @SuppressWarnings("deprecation") int top = insets.getSystemWindowInsetTop();
                @SuppressWarnings("deprecation") int right = insets.getSystemWindowInsetRight();
                @SuppressWarnings("deprecation") int bottom = insets.getSystemWindowInsetBottom();
                view.setPadding(left, top, right, bottom);
            }
            return insets;
        });
        root.requestApplyInsets();

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleUri(request.getUrl());
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUri(Uri.parse(url));
            }
        });

        if (savedInstanceState == null) loadBundledApp(); else webView.restoreState(savedInstanceState);
    }

    private boolean handleUri(Uri uri) {
        String host = uri.getHost();
        if ("app.local".equalsIgnoreCase(host) || "about".equalsIgnoreCase(uri.getScheme())) return false;
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) {}
        return true;
    }

    private void loadBundledApp() {
        try {
            InputStream input = getAssets().open("index.html");
            BufferedReader reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8));
            StringBuilder html = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) html.append(line).append('\n');
            reader.close();
            webView.loadDataWithBaseURL("https://app.local/", html.toString(), "text/html", "UTF-8", null);
        } catch (Exception e) {
            String safe = "<html><body style='background:#070916;color:#fff;font-family:sans-serif;padding:24px'>" +
                    "<h2>Bíblia EBD</h2><p>Falha ao carregar a interface.</p><p style='opacity:.7;font-size:12px'>" +
                    e.getClass().getSimpleName() + "</p></body></html>";
            webView.loadData(safe, "text/html", "UTF-8");
        }
    }

    @Override protected void onSaveInstanceState(Bundle outState) { webView.saveState(outState); super.onSaveInstanceState(outState); }
    @Override @SuppressWarnings("deprecation") public void onBackPressed() { if (webView != null && webView.canGoBack()) webView.goBack(); else super.onBackPressed(); }
    @Override protected void onDestroy() { if (webView != null) { webView.stopLoading(); webView.loadUrl("about:blank"); webView.destroy(); webView = null; } super.onDestroy(); }
}
