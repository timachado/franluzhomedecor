package com.timachado.bibliaebd;

import android.Manifest;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
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
    private ValueCallback<Uri[]> pendingCameraCallback;
    private Uri pendingCameraUri;
    private PermissionRequest pendingWebPermission;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        appWebView = findWebView();
        if (appWebView != null) appWebView.setWebChromeClient(new LensChromeClient());
    }

    private WebView findWebView() {
        try {
            Class<?> c=getClass();
            while(c!=null){
                try{
                    Field f=c.getDeclaredField("webView"); f.setAccessible(true);
                    Object v=f.get(this); if(v instanceof WebView)return (WebView)v;
                }catch(NoSuchFieldException ignored){}
                c=c.getSuperclass();
            }
        }catch(Throwable ignored){}
        try {
            Class<?> c=getClass().getSuperclass();
            while(c!=null){
                try{
                    Field f=c.getDeclaredField("appWebView"); f.setAccessible(true);
                    Object v=f.get(this); if(v instanceof WebView)return (WebView)v;
                }catch(NoSuchFieldException ignored){}
                c=c.getSuperclass();
            }
        }catch(Throwable ignored){}
        return null;
    }

    private final class LensChromeClient extends WebChromeClient {
        @Override public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> cb, FileChooserParams params) {
            if (pendingCameraCallback != null) pendingCameraCallback.onReceiveValue(null);
            pendingCameraCallback=cb;
            try {
                if (params != null && params.isCaptureEnabled()) return openCamera();
                return openGallery(params);
            } catch(Throwable e) {
                pendingCameraCallback=null; cb.onReceiveValue(null); return false;
            }
        }

        @Override public void onPermissionRequest(PermissionRequest request) {
            if(request==null)return;
            runOnUiThread(() -> {
                boolean wantsCamera=Arrays.asList(request.getResources()).contains(PermissionRequest.RESOURCE_VIDEO_CAPTURE);
                if(!wantsCamera){ request.deny(); return; }
                if(android.os.Build.VERSION.SDK_INT<23 || checkSelfPermission(Manifest.permission.CAMERA)==PackageManager.PERMISSION_GRANTED){
                    request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE}); return;
                }
                pendingWebPermission=request;
                requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_REQUEST);
            });
        }

        @Override public void onPermissionRequestCanceled(PermissionRequest request) {
            if(pendingWebPermission==request)pendingWebPermission=null;
            super.onPermissionRequestCanceled(request);
        }
    }

    private boolean openCamera() {
        try {
            ContentValues values=new ContentValues();
            values.put(MediaStore.Images.Media.DISPLAY_NAME,"athos-camera.jpg");
            values.put(MediaStore.Images.Media.MIME_TYPE,"image/jpeg");
            Uri uri=getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,values);
            if(uri==null)return false;
            pendingCameraUri=uri;
            Intent i=new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            i.putExtra(MediaStore.EXTRA_OUTPUT,uri);
            i.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivityForResult(i,FILE_CHOOSER_REQUEST);
            return true;
        }catch(Throwable ignored){ return false; }
    }

    private boolean openGallery(WebChromeClient.FileChooserParams params) {
        try {
            Intent i;
            try { i=params!=null?params.createIntent():new Intent(Intent.ACTION_OPEN_DOCUMENT); }
            catch(Throwable ignored){ i=new Intent(Intent.ACTION_OPEN_DOCUMENT); }
            i.setAction(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("image/*");
            startActivityForResult(i,FILE_CHOOSER_REQUEST);
            return true;
        }catch(Throwable ignored){ return false; }
    }

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        if(requestCode==FILE_CHOOSER_REQUEST && pendingCameraCallback!=null){
            Uri[] result=null;
            if(resultCode==RESULT_OK){
                try{
                    Uri picked=data!=null?data.getData():null;
                    if(picked!=null)result=new Uri[]{picked};
                    else if(pendingCameraUri!=null)result=new Uri[]{pendingCameraUri};
                }catch(Throwable ignored){}
            }
            ValueCallback<Uri[]> cb=pendingCameraCallback; pendingCameraCallback=null; pendingCameraUri=null;
            cb.onReceiveValue(result); return;
        }
        super.onActivityResult(requestCode,resultCode,data);
    }

    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        if(requestCode==CAMERA_PERMISSION_REQUEST){
            PermissionRequest request=pendingWebPermission; pendingWebPermission=null;
            if(request!=null){
                boolean granted=grantResults!=null&&grantResults.length>0&&grantResults[0]==PackageManager.PERMISSION_GRANTED;
                if(granted)request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE}); else request.deny();
            }
        }
    }

    @Override protected void onDestroy(){
        if(pendingCameraCallback!=null){ pendingCameraCallback.onReceiveValue(null); pendingCameraCallback=null; }
        if(pendingWebPermission!=null){ try{pendingWebPermission.deny();}catch(Throwable ignored){} pendingWebPermission=null; }
        super.onDestroy();
    }
}
