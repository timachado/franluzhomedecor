package com.timachado.bibliaebd;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.speech.tts.Voice;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import org.json.JSONObject;

import java.lang.reflect.Field;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

public class AuthActivity extends MainActivity {
    private static final int FILE_CHOOSER_REQUEST = 4188;
    private WebView appWebView;
    private ValueCallback<Uri[]> pendingFileCallback;
    private volatile String pendingOAuthCallback;

    private TextToSpeech tts;
    private volatile boolean ttsReady = false;
    private volatile boolean ttsFailed = false;
    private volatile String pendingSpeech;
    private volatile String ttsVoiceLabel = "Português (Brasil)";
    private final AtomicInteger ttsSeq = new AtomicInteger(1);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        captureOAuthIntent(getIntent());
        appWebView = findWebView();
        initTts();
        if (appWebView != null) {
            installFileChooser(appWebView);
            appWebView.addJavascriptInterface(new GoogleBridge(), "BibliaEBDGoogle");
            appWebView.addJavascriptInterface(new TtsBridge(), "BibliaEBDTTS");
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

    private void initTts() {
        try {
            tts = new TextToSpeech(getApplicationContext(), status -> {
                if (status != TextToSpeech.SUCCESS || tts == null) {
                    ttsFailed = true;
                    ttsReady = false;
                    sendTtsEvent("error", "O mecanismo de voz do Android não pôde ser iniciado.");
                    return;
                }
                try {
                    Locale ptBr = new Locale("pt", "BR");
                    int lang = tts.setLanguage(ptBr);
                    if (lang == TextToSpeech.LANG_MISSING_DATA || lang == TextToSpeech.LANG_NOT_SUPPORTED) {
                        ttsFailed = true;
                        ttsReady = false;
                        sendTtsEvent("error", "Ative ou instale uma voz Português (Brasil) nas configurações de texto para fala do Android.");
                        return;
                    }
                    chooseBestBrazilianVoice();
                    tts.setSpeechRate(0.94f);
                    tts.setPitch(1.00f);
                    tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                        @Override public void onStart(String utteranceId) { sendTtsEvent("start", ttsVoiceLabel); }
                        @Override public void onDone(String utteranceId) { sendTtsEvent("done", ttsVoiceLabel); }
                        @Override public void onError(String utteranceId) { sendTtsEvent("error", "Não foi possível reproduzir a voz brasileira neste aparelho."); }
                    });
                    ttsFailed = false;
                    ttsReady = true;
                    sendTtsEvent("ready", ttsVoiceLabel);
                    String queued = pendingSpeech;
                    pendingSpeech = null;
                    if (queued != null && !queued.trim().isEmpty()) speakNow(queued);
                } catch (Exception e) {
                    ttsFailed = true;
                    ttsReady = false;
                    sendTtsEvent("error", "Falha ao preparar a voz brasileira do aparelho.");
                }
            });
        } catch (Exception e) {
            ttsFailed = true;
            ttsReady = false;
        }
    }

    private void chooseBestBrazilianVoice() {
        try {
            Set<Voice> voices = tts.getVoices();
            if (voices == null || voices.isEmpty()) return;
            Voice best = null;
            int bestScore = Integer.MIN_VALUE;
            for (Voice v : voices) {
                Locale l = v.getLocale();
                if (l == null || !"pt".equalsIgnoreCase(l.getLanguage())) continue;
                int score = 0;
                if ("BR".equalsIgnoreCase(l.getCountry())) score += 1000;
                if (!v.isNetworkConnectionRequired()) score += 300;
                score += Math.max(0, v.getQuality());
                score -= Math.max(0, v.getLatency()) / 10;
                String n = v.getName() == null ? "" : v.getName().toLowerCase(Locale.ROOT);
                if (n.contains("br") || n.contains("brazil") || n.contains("pt-br")) score += 120;
                if (score > bestScore) { best = v; bestScore = score; }
            }
            if (best != null) {
                tts.setVoice(best);
                Locale l = best.getLocale();
                ttsVoiceLabel = "Português (Brasil) • " + (best.isNetworkConnectionRequired() ? "voz do sistema" : "voz local");
                if (l != null && !"BR".equalsIgnoreCase(l.getCountry())) ttsVoiceLabel = "Português • voz do sistema";
            }
        } catch (Exception ignored) {}
    }

    private void speakNow(String text) {
        if (tts == null || !ttsReady) return;
        runOnUiThread(() -> {
            try {
                String id = "athos-br-" + ttsSeq.getAndIncrement();
                int r = tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, id);
                if (r == TextToSpeech.ERROR) sendTtsEvent("error", "O Android recusou a reprodução da voz.");
            } catch (Exception e) {
                sendTtsEvent("error", "Não foi possível iniciar a voz brasileira.");
            }
        });
    }

    private void sendTtsEvent(String event, String detail) {
        WebView w = appWebView != null ? appWebView : findWebView();
        if (w == null) return;
        String js = "(function(){try{if(typeof window.__ATHOS_NATIVE_TTS_EVENT__==='function')window.__ATHOS_NATIVE_TTS_EVENT__(" + JSONObject.quote(event) + "," + JSONObject.quote(detail == null ? "" : detail) + ");}catch(e){}})()";
        w.post(() -> {
            try { w.evaluateJavascript(js, null); } catch (Exception ignored) {}
        });
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

    public final class TtsBridge {
        @JavascriptInterface public String ping() { return "ok"; }
        @JavascriptInterface public String voiceLabel() { return ttsVoiceLabel; }
        @JavascriptInterface public boolean isReady() { return ttsReady; }
        @JavascriptInterface public boolean speak(String text) {
            if (text == null || text.trim().isEmpty()) return false;
            if (ttsFailed) return false;
            String safe = text.trim();
            int max = TextToSpeech.getMaxSpeechInputLength();
            if (safe.length() > max) safe = safe.substring(0, max);
            if (!ttsReady) {
                pendingSpeech = safe;
                return true;
            }
            speakNow(safe);
            return true;
        }
        @JavascriptInterface public void stop() {
            pendingSpeech = null;
            runOnUiThread(() -> {
                try { if (tts != null) tts.stop(); } catch (Exception ignored) {}
            });
        }
    }

    @Override
    protected void onDestroy() {
        if (pendingFileCallback != null) {
            pendingFileCallback.onReceiveValue(null);
            pendingFileCallback = null;
        }
        pendingSpeech = null;
        try {
            if (tts != null) {
                tts.stop();
                tts.shutdown();
                tts = null;
            }
        } catch (Exception ignored) {}
        super.onDestroy();
    }
}
