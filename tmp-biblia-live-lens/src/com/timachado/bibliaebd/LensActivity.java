package com.timachado.bibliaebd;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

import java.lang.reflect.Field;
import java.util.Arrays;

public class LensActivity extends AuthActivity {
    private static final int FILE_CHOOSER_REQUEST = 4192;
    private static final int CAMERA_PERMISSION_REQUEST = 5192;

    private WebView appWebView;
    private ValueCallback<Uri[]> pendingFileCallback;
    private PermissionRequest pendingWebPermission;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        appWebView = findWebView();
        if (appWebView != null) appWebView.setWebChromeClient(new LensChromeClient());
    }

    private WebView findWebView() {
        try {
            Class<?> c = getClass();
            while (c != null) {
                for (String fieldName : new String[]{"webView","appWebView"}) {
                    try {
                        Field f = c.getDeclaredField(fieldName);
                        f.setAccessible(true);
                        Object v = f.get(this);
                        if (v instanceof WebView) return (WebView)v;
                    } catch (NoSuchFieldException ignored) {}
                }
                c = c.getSuperclass();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    private final class LensChromeClient extends WebChromeClient {
        @Override
        public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
            pendingFileCallback = callback;
            try {
                Intent intent = params != null ? params.createIntent() : new Intent(Intent.ACTION_OPEN_DOCUMENT);
                startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                return true;
            } catch (Throwable first) {
                try {
                    Intent fallback = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    fallback.addCategory(Intent.CATEGORY_OPENABLE);
                    fallback.setType("*/*");
                    startActivityForResult(fallback, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Throwable ignored) {
                    pendingFileCallback = null;
                    callback.onReceiveValue(null);
                    return false;
                }
            }
        }

        @Override
        public void onPermissionRequest(PermissionRequest request) {
            if (request == null) return;
            runOnUiThread(() -> {
                boolean wantsCamera = Arrays.asList(request.getResources()).contains(PermissionRequest.RESOURCE_VIDEO_CAPTURE);
                if (!wantsCamera) {
                    request.deny();
                    return;
                }
                if (android.os.Build.VERSION.SDK_INT < 23 ||
                        checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                    request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
                    return;
                }
                pendingWebPermission = request;
                requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_REQUEST);
            });
        }

        @Override
        public void onPermissionRequestCanceled(PermissionRequest request) {
            if (pendingWebPermission == request) pendingWebPermission = null;
            super.onPermissionRequestCanceled(request);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST) {
            ValueCallback<Uri[]> cb = pendingFileCallback;
            pendingFileCallback = null;
            if (cb != null) {
                Uri[] result = null;
                try { result = WebChromeClient.FileChooserParams.parseResult(resultCode, data); }
                catch (Throwable ignored) {}
                cb.onReceiveValue(result);
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != CAMERA_PERMISSION_REQUEST) return;

        PermissionRequest request = pendingWebPermission;
        pendingWebPermission = null;
        if (request == null) return;

        boolean granted = grantResults != null && grantResults.length > 0 &&
                grantResults[0] == PackageManager.PERMISSION_GRANTED;
        if (granted) request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
        else request.deny();
    }

    @Override
    protected void onDestroy() {
        if (pendingFileCallback != null) {
            pendingFileCallback.onReceiveValue(null);
            pendingFileCallback = null;
        }
        if (pendingWebPermission != null) {
            try { pendingWebPermission.deny(); } catch (Throwable ignored) {}
            pendingWebPermission = null;
        }
        super.onDestroy();
    }
}
