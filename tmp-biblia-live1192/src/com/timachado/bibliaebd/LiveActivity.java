package com.timachado.bibliaebd;

import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.webkit.WebView;
import java.lang.reflect.Field;

public final class LiveActivity extends LensActivity {
    private static final int CAMERA_PERMISSION_REQUEST = 91192;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ensureCameraPermission();
        installLiveCameraChromeClient();
    }

    @Override
    protected void onResume() {
        super.onResume();
        installLiveCameraChromeClient();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST) {
            installLiveCameraChromeClient();
        }
    }

    private void ensureCameraPermission() {
        if (Build.VERSION.SDK_INT >= 23 &&
                checkSelfPermission("android.permission.CAMERA") != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{"android.permission.CAMERA"}, CAMERA_PERMISSION_REQUEST);
        }
    }

    private void installLiveCameraChromeClient() {
        WebView webView = findAppWebView();
        if (webView != null) {
            webView.setWebChromeClient(new LiveLensChromeClient(this));
        }
    }

    private WebView findAppWebView() {
        try {
            Class<?> type = getClass();
            while (type != null) {
                try {
                    Field field = type.getDeclaredField("webView");
                    field.setAccessible(true);
                    Object value = field.get(this);
                    if (value instanceof WebView) return (WebView) value;
                } catch (NoSuchFieldException ignored) {
                }
                type = type.getSuperclass();
            }
        } catch (Throwable ignored) {
        }
        return null;
    }
}
