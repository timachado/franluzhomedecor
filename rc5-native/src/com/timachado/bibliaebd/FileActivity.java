package com.timachado.bibliaebd;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

import java.lang.reflect.Field;

/**
 * RC5 native file chooser bridge.
 * The existing MainActivity remains untouched; this subclass only adds Android's file picker
 * so <input type="file"> works for profile photos and EBD PDF magazines.
 */
public final class FileActivity extends MainActivity {
    private static final int FILE_CHOOSER_REQUEST = 4187;
    private ValueCallback<Uri[]> pendingFileCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        installFileChooser();
    }

    private void installFileChooser() {
        try {
            Field field = MainActivity.class.getDeclaredField("webView");
            field.setAccessible(true);
            Object value = field.get(this);
            if (!(value instanceof WebView)) return;
            WebView webView = (WebView) value;
            webView.setWebChromeClient(new WebChromeClient() {
                @Override
                public boolean onShowFileChooser(WebView view,
                                                 ValueCallback<Uri[]> filePathCallback,
                                                 FileChooserParams fileChooserParams) {
                    if (pendingFileCallback != null) {
                        pendingFileCallback.onReceiveValue(null);
                    }
                    pendingFileCallback = filePathCallback;

                    Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType(resolveMimeType(fileChooserParams));
                    intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false);

                    try {
                        startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                        return true;
                    } catch (Exception firstError) {
                        try {
                            Intent fallback = fileChooserParams != null
                                    ? fileChooserParams.createIntent()
                                    : new Intent(Intent.ACTION_GET_CONTENT).setType("*/*");
                            startActivityForResult(fallback, FILE_CHOOSER_REQUEST);
                            return true;
                        } catch (Exception ignored) {
                            pendingFileCallback.onReceiveValue(null);
                            pendingFileCallback = null;
                            return false;
                        }
                    }
                }
            });
        } catch (Throwable ignored) {
            // Keep the existing app usable even if a future MainActivity changes internally.
        }
    }

    private String resolveMimeType(WebChromeClient.FileChooserParams params) {
        if (params == null) return "*/*";
        String[] accepted = params.getAcceptTypes();
        if (accepted == null || accepted.length == 0) return "*/*";
        boolean image = false;
        boolean pdf = false;
        for (String raw : accepted) {
            if (raw == null) continue;
            String type = raw.trim().toLowerCase();
            if (type.startsWith("image/") || type.contains(".jpg") || type.contains(".jpeg")
                    || type.contains(".png") || type.contains(".webp")) image = true;
            if (type.contains("pdf") || type.contains(".pdf")) pdf = true;
        }
        if (image && !pdf) return "image/*";
        if (pdf && !image) return "application/pdf";
        return "*/*";
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST) {
            ValueCallback<Uri[]> callback = pendingFileCallback;
            pendingFileCallback = null;
            if (callback != null) {
                Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
                callback.onReceiveValue(result);
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
}
