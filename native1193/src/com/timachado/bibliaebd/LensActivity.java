package com.timachado.bibliaebd;

import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

import java.lang.reflect.Field;

public class LensActivity extends AuthActivity {
    private static final int FILE_CHOOSER_REQUEST = 4192;
    private static final int LIVE_LENS_REQUEST = 5193;
    private WebView appWebView;
    private ValueCallback<Uri[]> pendingCameraCallback;
    private Uri pendingCameraUri;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        appWebView = findWebView();
        if (appWebView != null) appWebView.setWebChromeClient(new LensChromeClient(this));
    }

    private WebView findWebView() {
        try {
            Class<?> c=getClass();
            while(c!=null){
                try{
                    Field f=c.getDeclaredField("webView");
                    f.setAccessible(true);
                    Object v=f.get(this);
                    if(v instanceof WebView)return (WebView)v;
                }catch(NoSuchFieldException ignored){}
                c=c.getSuperclass();
            }
        }catch(Throwable ignored){}
        return null;
    }

    boolean handleFileChooser(WebChromeClient.FileChooserParams params, ValueCallback<Uri[]> cb) {
        if (pendingCameraCallback != null) pendingCameraCallback.onReceiveValue(null);
        pendingCameraCallback=cb;
        try {
            if (params != null && params.isCaptureEnabled()) {
                startActivityForResult(new Intent(this, LiveLensActivity.class), LIVE_LENS_REQUEST);
                return true;
            }
            return openGallery(params);
        } catch(Throwable e) {
            pendingCameraCallback=null;
            cb.onReceiveValue(null);
            return false;
        }
    }

    private boolean openGallery(WebChromeClient.FileChooserParams params) {
        try {
            Intent i;
            try { i=params!=null?params.createIntent():new Intent(Intent.ACTION_OPEN_DOCUMENT); }
            catch(Throwable ignored){ i=new Intent(Intent.ACTION_OPEN_DOCUMENT); }
            startActivityForResult(i,FILE_CHOOSER_REQUEST);
            return true;
        } catch(Throwable ignored){ return false; }
    }

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        if(requestCode==LIVE_LENS_REQUEST){
            if (pendingCameraCallback != null) {
                pendingCameraCallback.onReceiveValue(null);
                pendingCameraCallback=null;
            }
            if(resultCode==RESULT_OK && data!=null && appWebView!=null){
                String text=data.getStringExtra(LiveLensActivity.EXTRA_SELECTED_TEXT);
                if(text!=null&&!text.trim().isEmpty()){
                    String js="window.__EBD_LIVE_LENS_RESULT__&&window.__EBD_LIVE_LENS_RESULT__("+org.json.JSONObject.quote(text.trim())+")";
                    appWebView.post(()->{try{appWebView.evaluateJavascript(js,null);}catch(Throwable ignored){}});
                }
            }
            return;
        }
        if(requestCode==FILE_CHOOSER_REQUEST && pendingCameraCallback!=null){
            Uri[] result=null;
            try{result=WebChromeClient.FileChooserParams.parseResult(resultCode,data);}catch(Throwable ignored){}
            ValueCallback<Uri[]> cb=pendingCameraCallback;
            pendingCameraCallback=null;
            pendingCameraUri=null;
            cb.onReceiveValue(result);
            return;
        }
        super.onActivityResult(requestCode,resultCode,data);
    }

    @Override protected void onDestroy(){
        if(pendingCameraCallback!=null){pendingCameraCallback.onReceiveValue(null);pendingCameraCallback=null;}
        pendingCameraUri=null;
        super.onDestroy();
    }
}

final class LensChromeClient extends WebChromeClient {
    private final LensActivity owner;
    LensChromeClient(LensActivity owner){this.owner=owner;}
    @Override public boolean onShowFileChooser(WebView webView,ValueCallback<Uri[]> cb,FileChooserParams params){
        return owner.handleFileChooser(params,cb);
    }
}
