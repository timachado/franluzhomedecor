package com.timachado.bibliaebd;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import org.json.JSONObject;

import java.lang.reflect.Field;
import java.util.Locale;

public class AuthActivity extends MainActivity {
    private static final int FILE_CHOOSER_REQUEST = 4188;
    private WebView appWebView;
    private ValueCallback<Uri[]> pendingFileCallback;
    private volatile String pendingOAuthCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        captureOAuthIntent(getIntent());
        appWebView = findWebView();
        if (appWebView != null) {
            installFileChooser(appWebView);
            appWebView.addJavascriptInterface(new GoogleBridge(), "BibliaEBDGoogle");
            appWebView.postDelayed(() -> {
                try {
                    String u = appWebView.getUrl();
                    if (u == null || u.startsWith("file:///android_asset/")) appWebView.reload();
                } catch (Exception ignored) {}
            }, 220);
            schedulePendingDelivery();
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        captureOAuthIntent(intent);
        schedulePendingDelivery();
    }

    @Override
    protected void onResume() {
        super.onResume();
        captureOAuthIntent(getIntent());
        schedulePendingDelivery();
    }

    private void captureOAuthIntent(Intent intent) {
        if (intent == null) return;
        try {
            Uri d = intent.getData();
            if (d == null) return;
            if (!"bibliaebd".equalsIgnoreCase(d.getScheme())) return;
            if (!"google-auth".equalsIgnoreCase(d.getHost())) return;
            pendingOAuthCallback = d.toString();
        } catch (Exception ignored) {}
    }

    private void schedulePendingDelivery() {
        WebView w = appWebView != null ? appWebView : findWebView();
        if (w == null) return;
        for (int i = 0; i < 18; i++) {
            final long delay = 200L + (i * 450L);
            w.postDelayed(this::deliverPendingIfReady, delay);
        }
    }

    private void deliverPendingIfReady() {
        final String callback = pendingOAuthCallback;
        if (callback == null || callback.trim().isEmpty()) return;
        WebView w = appWebView != null ? appWebView : findWebView();
        if (w == null) return;
        String js = "(function(){try{if(typeof window.__EBD_GOOGLE_AUTH_CALLBACK__==='function'){window.__EBD_GOOGLE_AUTH_CALLBACK__(" + JSONObject.quote(callback) + ");return 'accepted';}return 'waiting';}catch(e){return 'error';}})()";
        w.evaluateJavascript(js, value -> {
            if (value != null && value.contains("accepted")) pendingOAuthCallback = null;
        });
    }

    private WebView findWebView() {
        try {
            Class<?> c = getClass();
            while (c != null) {
                try {
                    Field f = c.getDeclaredField("webView");
                    f.setAccessible(true);
                    Object v = f.get(this);
                    if (v instanceof WebView) return (WebView) v;
                } catch (NoSuchFieldException ignored) {}
                c = c.getSuperclass();
            }
        } catch (Exception ignored) {}
        return null;
    }

    private void installFileChooser(WebView webView) {
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
                pendingFileCallback = callback;
                try {
                    Intent intent;
                    try { intent = params != null ? params.createIntent() : new Intent(Intent.ACTION_OPEN_DOCUMENT); }
                    catch (Exception ignored) { intent = new Intent(Intent.ACTION_OPEN_DOCUMENT); }
                    intent.setAction(Intent.ACTION_OPEN_DOCUMENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false);
                    intent.setType(resolveMimeType(params));
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Exception e) {
                    pendingFileCallback = null;
                    callback.onReceiveValue(null);
                    return false;
                }
            }
        });
    }

    private String resolveMimeType(WebChromeClient.FileChooserParams params) {
        try {
            String[] types = params != null ? params.getAcceptTypes() : null;
            if (types != null) for (String raw : types) {
                String t = raw == null ? "" : raw.trim().toLowerCase(Locale.ROOT);
                if (t.contains("pdf") || t.contains(".pdf")) return "application/pdf";
                if (t.startsWith("image/") || t.contains(".jpg") || t.contains(".jpeg") || t.contains(".png") || t.contains(".webp")) return "image/*";
            }
        } catch (Exception ignored) {}
        return "*/*";
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST && pendingFileCallback != null) {
            Uri[] result = null;
            try { result = WebChromeClient.FileChooserParams.parseResult(resultCode, data); } catch (Exception ignored) {}
            pendingFileCallback.onReceiveValue(result);
            pendingFileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    public final class GoogleBridge {
        @JavascriptInterface public String ping() { return "ok"; }
        @JavascriptInterface public void openGoogleLogin(String authUrl) {
            if (authUrl == null || !authUrl.startsWith("https://dwpcddiramxlhavdmmyn.supabase.co/auth/v1/authorize")) return;
            runOnUiThread(() -> {
                try {
                    Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(authUrl));
                    i.addCategory(Intent.CATEGORY_BROWSABLE);
                    startActivity(i);
                } catch (Exception ignored) {}
            });
        }
    }

    @Override
    protected void onDestroy() {
        if (pendingFileCallback != null) {
            pendingFileCallback.onReceiveValue(null);
            pendingFileCallback = null;
        }
        super.onDestroy();
    }
}
