package com.timachado.bibliaebd;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.Gravity;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.Locale;

public class MainActivity extends Activity {
    private static final int DARK = Color.rgb(7, 9, 22);
    private static final int NOTIFICATION_PERMISSION_REQUEST = 1158;
    private WebView webView;
    private FrameLayout root;
    private View splashView;
    private boolean splashHidden = false;
    private TextToSpeech tts;
    private volatile boolean ttsReady = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(DARK);
        getWindow().setNavigationBarColor(DARK);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            getWindow().setNavigationBarContrastEnforced(false);
            getWindow().setStatusBarContrastEnforced(false);
        }

        initTextToSpeech();
        root = new FrameLayout(this);
        root.setBackgroundColor(DARK);
        webView = new WebView(this);
        webView.setBackgroundColor(DARK);
        webView.setAlpha(0.01f);
        webView.setVerticalScrollBarEnabled(true);
        webView.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        root.addView(webView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        splashView = createSplash();
        splashView.setClickable(false);
        splashView.setFocusable(false);
        splashView.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        root.addView(splashView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        root.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
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
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setTextZoom(108);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setSaveFormData(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) settings.setSafeBrowsingEnabled(true);

        WebView.setWebContentsDebuggingEnabled(false);
        webView.addJavascriptInterface(new NativeBridge(), "AndroidBridge");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return handleUri(request.getUrl()); }
            @Override @SuppressWarnings("deprecation") public boolean shouldOverrideUrlLoading(WebView view, String url) { return handleUri(Uri.parse(url)); }
            @Override public void onPageFinished(WebView view, String url) { hideSplash(); view.requestFocus(); }
        });

        if (savedInstanceState == null) webView.loadUrl("file:///android_asset/index.html");
        else if (webView.restoreState(savedInstanceState) == null) webView.loadUrl("file:///android_asset/index.html");
        root.postDelayed(this::hideSplash, 1400);
    }

    private void initTextToSpeech() {
        tts = new TextToSpeech(getApplicationContext(), status -> {
            if (status != TextToSpeech.SUCCESS || tts == null) { ttsReady = false; return; }
            int result = tts.setLanguage(new Locale("pt", "BR"));
            tts.setSpeechRate(0.94f);
            tts.setPitch(1.0f);
            ttsReady = result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED;
        });
    }

    private View createSplash() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setBackgroundColor(DARK);
        int pad = (int) (28 * getResources().getDisplayMetrics().density);
        box.setPadding(pad, pad, pad, pad);
        TextView cross = new TextView(this); cross.setText("✝"); cross.setTextColor(Color.rgb(196, 181, 253)); cross.setTextSize(48); cross.setGravity(Gravity.CENTER); box.addView(cross);
        TextView title = new TextView(this); title.setText("Bíblia EBD"); title.setTextColor(Color.WHITE); title.setTextSize(24); title.setGravity(Gravity.CENTER); title.setPadding(0, pad / 3, 0, 0); box.addView(title);
        TextView subtitle = new TextView(this); subtitle.setText("Palavra • EBD • Harpa • Assistente IA"); subtitle.setTextColor(Color.rgb(155, 164, 186)); subtitle.setTextSize(11); subtitle.setGravity(Gravity.CENTER); subtitle.setPadding(0, pad / 4, 0, 0); box.addView(subtitle);
        return box;
    }

    private void hideSplash() {
        if (splashHidden || webView == null) return;
        splashHidden = true;
        webView.animate().cancel(); webView.setAlpha(1f); webView.setVisibility(View.VISIBLE); webView.requestFocus();
        if (splashView != null) { splashView.animate().cancel(); splashView.clearAnimation(); splashView.setVisibility(View.GONE); if (splashView.getParent() == root) root.removeView(splashView); splashView = null; }
    }

    private boolean handleUri(Uri uri) {
        String scheme = uri.getScheme();
        if ("file".equalsIgnoreCase(scheme) || "about".equalsIgnoreCase(scheme)) return false;
        if (!"http".equalsIgnoreCase(scheme) && !"https".equalsIgnoreCase(scheme) && !"mailto".equalsIgnoreCase(scheme) && !"tel".equalsIgnoreCase(scheme)) return true;
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) {}
        return true;
    }

    private void handleBack() {
        if (webView == null) { finish(); return; }
        webView.evaluateJavascript("!!(window.__ebdNativeBack112 && window.__ebdNativeBack112())", value -> {
            if ("true".equalsIgnoreCase(value)) return;
            if ("false".equalsIgnoreCase(value)) { finish(); return; }
            if (webView != null && webView.canGoBack()) webView.goBack(); else finish();
        });
    }

    private String installedVersionName() {
        try { return getPackageManager().getPackageInfo(getPackageName(), 0).versionName; }
        catch (Exception ignored) { return "1.15.10"; }
    }

    private PendingIntent reminderPendingIntent(int requestCode, String title, String text) {
        Intent intent = new Intent(this, ReminderReceiver.class);
        intent.putExtra("title", title);
        intent.putExtra("text", text);
        intent.putExtra("notificationId", requestCode);
        return PendingIntent.getBroadcast(this, requestCode, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private class NativeBridge {
        @JavascriptInterface public String appVersion() { return installedVersionName(); }
        @JavascriptInterface public void haptic() { runOnUiThread(() -> { if (root != null) root.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP); }); }
        @JavascriptInterface public void setKeepScreenOn(boolean enabled) { runOnUiThread(() -> { if (enabled) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON); else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON); }); }
        @JavascriptInterface public void shareText(String text, String title) { runOnUiThread(() -> { try { Intent send = new Intent(Intent.ACTION_SEND); send.setType("text/plain"); send.putExtra(Intent.EXTRA_TEXT, text); send.putExtra(Intent.EXTRA_SUBJECT, title); startActivity(Intent.createChooser(send, "Compartilhar")); } catch (Exception ignored) {} }); }
        @JavascriptInterface public boolean isSpeechReady() { return ttsReady && tts != null; }

        @JavascriptInterface public boolean speakText(String text) {
            if (!ttsReady || tts == null || text == null || text.trim().isEmpty()) return false;
            final String clean = text.trim();
            runOnUiThread(() -> {
                if (tts == null) return;
                tts.stop();
                int max = Math.max(800, TextToSpeech.getMaxSpeechInputLength() - 200);
                int start = 0; boolean first = true; int part = 0;
                while (start < clean.length()) {
                    int end = Math.min(clean.length(), start + max);
                    if (end < clean.length()) {
                        int split = clean.lastIndexOf('\n', end);
                        if (split <= start + max / 2) split = clean.lastIndexOf('.', end);
                        if (split > start + max / 2) end = split + 1;
                    }
                    String chunk = clean.substring(start, end).trim();
                    if (!chunk.isEmpty()) tts.speak(chunk, first ? TextToSpeech.QUEUE_FLUSH : TextToSpeech.QUEUE_ADD, null, "ebd-1158-" + (part++));
                    first = false; start = end;
                }
            });
            return true;
        }

        @JavascriptInterface public void stopSpeech() { runOnUiThread(() -> { if (tts != null) tts.stop(); }); }
        @JavascriptInterface public boolean notificationPermissionGranted() { return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED; }
        @JavascriptInterface public void requestNotificationPermission() { if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIFICATION_PERMISSION_REQUEST)); }

        @JavascriptInterface public boolean scheduleReminder(long triggerAtMillis, String title, String text, int requestCode) {
            if (triggerAtMillis <= System.currentTimeMillis()) return false;
            AlarmManager alarm = (AlarmManager) getSystemService(ALARM_SERVICE);
            if (alarm == null) return false;
            try { alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, reminderPendingIntent(requestCode, title, text)); return true; }
            catch (Exception ignored) { return false; }
        }

        @JavascriptInterface public void cancelReminder(int requestCode) {
            AlarmManager alarm = (AlarmManager) getSystemService(ALARM_SERVICE);
            if (alarm == null) return;
            try { alarm.cancel(reminderPendingIntent(requestCode, "", "")); } catch (Exception ignored) {}
        }
    }

    @Override protected void onSaveInstanceState(Bundle outState) { if (webView != null) webView.saveState(outState); super.onSaveInstanceState(outState); }
    @Override @SuppressWarnings("deprecation") public void onBackPressed() { handleBack(); }
    @Override protected void onPause() { super.onPause(); }
    @Override protected void onResume() { super.onResume(); if (root != null) root.requestApplyInsets(); if (webView != null) webView.requestFocus(); }
    @Override protected void onDestroy() {
        if (tts != null) { tts.stop(); tts.shutdown(); tts = null; ttsReady = false; }
        if (webView != null) { webView.removeJavascriptInterface("AndroidBridge"); webView.stopLoading(); webView.loadUrl("about:blank"); webView.destroy(); webView = null; }
        super.onDestroy();
    }
}
