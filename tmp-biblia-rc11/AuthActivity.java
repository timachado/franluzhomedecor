package com.timachado.bibliaebd;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.Field;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.UUID;

public class AuthActivity extends MainActivity {
    private static final int FILE_CHOOSER_REQUEST = 4188;
    private static final int OAUTH_PORT = 3000;
    private volatile ServerSocket oauthServer;
    private volatile boolean oauthDone;
    private volatile String localSecret = "";
    private WebView appWebView;
    private ValueCallback<Uri[]> pendingFileCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        appWebView = findWebView();
        if (appWebView != null) {
            installFileChooser(appWebView);
            appWebView.addJavascriptInterface(new GoogleBridge(), "BibliaEBDGoogle");
            // addJavascriptInterface becomes visible to page JS after the next reload.
            appWebView.postDelayed(() -> {
                try {
                    String u = appWebView.getUrl();
                    if (u == null || u.startsWith("file:///android_asset/")) appWebView.reload();
                } catch (Exception ignored) {}
            }, 220);
        }
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
            if (authUrl == null || !authUrl.startsWith("https://dwpcddiramxlhavdmmyn.supabase.co/auth/v1/authorize")) {
                deliverError("Endereço de login Google inválido.");
                return;
            }
            startLoopback(authUrl);
        }
    }

    private void startLoopback(String authUrl) {
        new Thread(() -> {
            stopLoopback();
            oauthDone = false;
            localSecret = UUID.randomUUID().toString();
            try {
                ServerSocket server = new ServerSocket();
                server.setReuseAddress(true);
                server.bind(new InetSocketAddress("127.0.0.1", OAUTH_PORT));
                server.setSoTimeout(180000);
                oauthServer = server;
                runOnUiThread(() -> {
                    try {
                        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(authUrl));
                        i.addCategory(Intent.CATEGORY_BROWSABLE);
                        startActivity(i);
                    } catch (Exception e) {
                        deliverError("Não encontrei um navegador para abrir o login Google.");
                        stopLoopback();
                    }
                });
                while (!oauthDone && !server.isClosed()) {
                    try (Socket socket = server.accept()) {
                        if (!socket.getInetAddress().isLoopbackAddress()) {
                            respond(socket, 403, "text/plain; charset=utf-8", "Acesso negado.");
                            continue;
                        }
                        handleSocket(socket);
                    }
                }
            } catch (Exception e) {
                if (!oauthDone) deliverError("Não foi possível preparar o retorno do Google. Tente novamente.");
            } finally { stopLoopback(); }
        }, "BibliaEBD-GoogleOAuth").start();
    }

    private void handleSocket(Socket socket) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
        String request = reader.readLine();
        if (request == null || request.isEmpty()) return;
        String[] first = request.split(" ");
        String method = first.length > 0 ? first[0] : "GET";
        String path = first.length > 1 ? first[1] : "/";
        int contentLength = 0;
        String line;
        while ((line = reader.readLine()) != null && !line.isEmpty()) {
            int colon = line.indexOf(':');
            if (colon > 0 && "content-length".equalsIgnoreCase(line.substring(0, colon).trim())) {
                try { contentLength = Integer.parseInt(line.substring(colon + 1).trim()); } catch (Exception ignored) {}
            }
        }
        if ("POST".equalsIgnoreCase(method) && path.startsWith("/complete")) {
            char[] chars = new char[Math.max(0, Math.min(contentLength, 24000))];
            int got = 0;
            while (got < chars.length) { int n = reader.read(chars, got, chars.length - got); if (n < 0) break; got += n; }
            String body = new String(chars, 0, got);
            int cut = body.indexOf('\n');
            String secret = cut >= 0 ? body.substring(0, cut) : "";
            String encoded = cut >= 0 ? body.substring(cut + 1) : "";
            if (!localSecret.equals(secret)) { respond(socket, 403, "text/plain; charset=utf-8", "Solicitação inválida."); return; }
            String callback = URLDecoder.decode(encoded, StandardCharsets.UTF_8.name());
            respond(socket, 200, "text/plain; charset=utf-8", "ok");
            deliver(callback);
            oauthDone = true;
            return;
        }
        respond(socket, 200, "text/html; charset=utf-8", returnPage(localSecret));
    }

    private String returnPage(String secret) {
        return "<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Bíblia EBD</title><style>html,body{margin:0;height:100%;background:#070916;color:#f8f5ff;font-family:system-ui,sans-serif}.w{min-height:100%;display:grid;place-items:center;padding:28px;box-sizing:border-box}.c{max-width:520px;text-align:center;background:#11162b;border:1px solid #2b3358;border-radius:24px;padding:30px}.i{font-size:54px}.t{color:#e0bc67;font-size:24px;font-weight:800;margin:12px}.m{color:#adb5cf;line-height:1.5}</style></head><body><div class=\"w\"><div class=\"c\"><div class=\"i\">📖</div><div id=\"t\" class=\"t\">Concluindo login…</div><div id=\"m\" class=\"m\">Aguarde um instante.</div></div></div><script>(async()=>{const s="+JSONObject.quote(secret)+";try{await fetch('/complete',{method:'POST',headers:{'Content-Type':'text/plain;charset=UTF-8'},body:s+'\\n'+encodeURIComponent(location.href),cache:'no-store'});document.getElementById('t').textContent='Login concluído ✓';document.getElementById('m').textContent='Voltando ao Bíblia EBD…';setTimeout(()=>{location.href='intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;package=com.timachado.bibliaebd.diag;end'},350)}catch(e){document.getElementById('t').textContent='Não foi possível concluir';document.getElementById('m').textContent='Volte ao Bíblia EBD e tente novamente.'}})();</script></body></html>";
    }

    private void respond(Socket socket, int status, String type, String body) throws Exception {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        BufferedWriter w = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
        w.write("HTTP/1.1 " + status + (status == 200 ? " OK" : " Error") + "\r\n");
        w.write("Content-Type: " + type + "\r\nContent-Length: " + bytes.length + "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
        w.flush();
        socket.getOutputStream().write(bytes); socket.getOutputStream().flush();
    }

    private void deliverError(String message) { deliver("http://localhost:3000/?error_description=" + Uri.encode(message)); }
    private void deliver(String callback) {
        WebView w = appWebView != null ? appWebView : findWebView();
        if (w == null || callback == null) return;
        w.post(() -> w.evaluateJavascript("window.__EBD_GOOGLE_AUTH_CALLBACK__&&window.__EBD_GOOGLE_AUTH_CALLBACK__(" + JSONObject.quote(callback) + ");", null));
    }
    private void stopLoopback() {
        oauthDone = true;
        ServerSocket s = oauthServer; oauthServer = null;
        if (s != null) try { s.close(); } catch (Exception ignored) {}
    }
    @Override protected void onDestroy() {
        stopLoopback();
        if (pendingFileCallback != null) { pendingFileCallback.onReceiveValue(null); pendingFileCallback = null; }
        super.onDestroy();
    }
}
