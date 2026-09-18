package com.timachado.bibliaebd;

import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.*;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.*;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.*;
import android.os.*;
import android.util.Size;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.*;

public class LiveLensActivity extends Activity {
  public static final String EXTRA_SELECTED_TEXT="selected_text";
  private static final int REQ_CAMERA=5193;
  private FrameLayout root; private TextureView texture; private Button select; private TextView status; private WebView web;
  private HandlerThread thread; private Handler handler; private CameraDevice camera; private CameraCaptureSession session;
  private CaptureRequest.Builder preview; private ImageReader reader; private Size previewSize,captureSize; private String cameraId;
  private CameraCharacteristics chars; private boolean opening,capturing; private File captureFile;

  @Override protected void onCreate(Bundle b){
    super.onCreate(b);getWindow().setStatusBarColor(Color.BLACK);getWindow().setNavigationBarColor(Color.BLACK);
    root=new FrameLayout(this);root.setBackgroundColor(Color.BLACK);setContentView(root);startThread();showCamera();
  }
  private int dp(float v){return Math.round(v*getResources().getDisplayMetrics().density);}
  private Button btn(String t,boolean p){Button b=new Button(this);b.setText(t);b.setAllCaps(false);b.setTextColor(p?Color.rgb(30,24,10):Color.WHITE);b.setBackgroundColor(p?Color.rgb(232,195,87):Color.rgb(23,29,42));return b;}
  private TextView txt(String t,int sp){TextView v=new TextView(this);v.setText(t);v.setTextSize(sp);v.setTextColor(Color.WHITE);return v;}

  private void showCamera(){
    destroyWeb();closeCamera();root.removeAllViews();capturing=false;
    texture=new TextureView(this);root.addView(texture,new FrameLayout.LayoutParams(-1,-1));
    LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(10),dp(8),dp(10),dp(8));top.setBackgroundColor(Color.argb(130,0,0,0));
    Button close=btn("‹",false);TextView title=txt("Lens • Bíblia EBD",17);title.setGravity(Gravity.CENTER);top.addView(close,new LinearLayout.LayoutParams(dp(56),dp(48)));top.addView(title,new LinearLayout.LayoutParams(0,dp(48),1));top.addView(new View(this),new LinearLayout.LayoutParams(dp(56),dp(48)));root.addView(top,new FrameLayout.LayoutParams(-1,dp(66),Gravity.TOP));close.setOnClickListener(v->finish());
    LinearLayout bottom=new LinearLayout(this);bottom.setOrientation(LinearLayout.VERTICAL);bottom.setGravity(Gravity.CENTER);bottom.setPadding(dp(14),dp(10),dp(14),dp(16));bottom.setBackgroundColor(Color.argb(150,0,0,0));
    status=txt("Aponte para o texto e toque em Selecionar texto",12);status.setGravity(Gravity.CENTER);select=btn("Selecionar texto",true);select.setEnabled(false);bottom.addView(status,new LinearLayout.LayoutParams(-1,dp(34)));bottom.addView(select,new LinearLayout.LayoutParams(-1,dp(56)));root.addView(bottom,new FrameLayout.LayoutParams(-1,dp(120),Gravity.BOTTOM));select.setOnClickListener(v->capture());
    texture.setSurfaceTextureListener(new TextureView.SurfaceTextureListener(){
      public void onSurfaceTextureAvailable(SurfaceTexture s,int w,int h){open();}
      public void onSurfaceTextureSizeChanged(SurfaceTexture s,int w,int h){}
      public boolean onSurfaceTextureDestroyed(SurfaceTexture s){closeCamera();return true;}
      public void onSurfaceTextureUpdated(SurfaceTexture s){}
    });
    if(checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.CAMERA},REQ_CAMERA);else if(texture.isAvailable())open();
  }

  private void startThread(){if(thread!=null)return;thread=new HandlerThread("BibliaEBD-LiveLens");thread.start();handler=new Handler(thread.getLooper());}
  private void stopThread(){HandlerThread t=thread;thread=null;handler=null;if(t!=null)try{t.quitSafely();t.join(800);}catch(Exception ignored){}}
  private void setStatus(String s){runOnUiThread(()->{if(status!=null)status.setText(s);});}
  private void fail(String s){setStatus(s);runOnUiThread(()->Toast.makeText(this,s,Toast.LENGTH_LONG).show());}

  private void open(){
    if(web!=null||camera!=null||opening||texture==null||!texture.isAvailable()||checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)return;
    CameraManager m=(CameraManager)getSystemService(CAMERA_SERVICE);if(m==null){fail("Câmera indisponível.");return;}
    try{choose(m);if(cameraId==null){fail("Câmera traseira não encontrada.");return;}opening=true;m.openCamera(cameraId,new CameraDevice.StateCallback(){
      public void onOpened(CameraDevice c){opening=false;camera=c;preview();}
      public void onDisconnected(CameraDevice c){opening=false;c.close();camera=null;}
      public void onError(CameraDevice c,int e){opening=false;c.close();camera=null;fail("Não foi possível abrir a câmera.");}
    },handler);}catch(SecurityException e){requestPermissions(new String[]{Manifest.permission.CAMERA},REQ_CAMERA);}catch(Exception e){opening=false;fail("Falha ao preparar a câmera.");}
  }
  private void choose(CameraManager m)throws CameraAccessException{
    if(cameraId!=null)return;
    for(String id:m.getCameraIdList()){
      CameraCharacteristics c=m.getCameraCharacteristics(id);Integer f=c.get(CameraCharacteristics.LENS_FACING);if(f!=null&&f==CameraCharacteristics.LENS_FACING_FRONT)continue;
      StreamConfigurationMap map=c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);if(map==null)continue;Size[] jpg=map.getOutputSizes(ImageFormat.JPEG),pre=map.getOutputSizes(SurfaceTexture.class);if(jpg==null||pre==null||jpg.length==0||pre.length==0)continue;
      cameraId=id;chars=c;captureSize=pickCapture(jpg);previewSize=pickPreview(pre,captureSize);return;
    }
  }
  private Size pickCapture(Size[] a){List<Size> l=new ArrayList<>(Arrays.asList(a));Collections.sort(l,(x,y)->Long.compare((long)y.getWidth()*y.getHeight(),(long)x.getWidth()*x.getHeight()));for(Size s:l){long p=(long)s.getWidth()*s.getHeight();if(p<=4200000L&&s.getWidth()>=1280&&s.getHeight()>=720)return s;}return l.get(0);}
  private Size pickPreview(Size[] a,Size cap){double target=cap.getWidth()/(double)cap.getHeight(),best=Double.MAX_VALUE;Size out=a[0];for(Size s:a){long p=(long)s.getWidth()*s.getHeight();if(p>3000000L)continue;double score=Math.abs(s.getWidth()/(double)s.getHeight()-target)*10+Math.abs(1920-s.getWidth())/1920.0;if(score<best){best=score;out=s;}}return out;}
  private void preview(){
    if(camera==null||texture==null||!texture.isAvailable())return;
    try{SurfaceTexture st=texture.getSurfaceTexture();st.setDefaultBufferSize(previewSize.getWidth(),previewSize.getHeight());Surface ps=new Surface(st);
      if(reader!=null)reader.close();reader=ImageReader.newInstance(captureSize.getWidth(),captureSize.getHeight(),ImageFormat.JPEG,2);reader.setOnImageAvailableListener(r->{Image im=null;try{im=r.acquireLatestImage();if(im==null)return;ByteBuffer b=im.getPlanes()[0].getBuffer();byte[] bytes=new byte[b.remaining()];b.get(bytes);File f=new File(getCacheDir(),"live-lens-capture.jpg");try(FileOutputStream o=new FileOutputStream(f,false)){o.write(bytes);}captureFile=f;runOnUiThread(()->showOcr(f));}catch(Exception e){capturing=false;fail("Não foi possível capturar o quadro.");}finally{if(im!=null)im.close();}},handler);
      preview=camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);preview.addTarget(ps);preview.set(CaptureRequest.CONTROL_AF_MODE,CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
      camera.createCaptureSession(Arrays.asList(ps,reader.getSurface()),new CameraCaptureSession.StateCallback(){public void onConfigured(CameraCaptureSession s){if(camera==null)return;session=s;try{s.setRepeatingRequest(preview.build(),null,handler);runOnUiThread(()->{if(select!=null)select.setEnabled(true);setStatus("Aponte para o texto e toque em Selecionar texto");});}catch(Exception e){fail("Falha ao iniciar a prévia.");}}public void onConfigureFailed(CameraCaptureSession s){fail("A prévia não pôde ser configurada.");}},handler);
    }catch(Exception e){fail("Falha ao configurar a câmera.");}
  }
  private void capture(){if(capturing||camera==null||session==null||reader==null)return;capturing=true;if(select!=null)select.setEnabled(false);setStatus("Congelando quadro para reconhecer o texto…");try{CaptureRequest.Builder b=camera.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);b.addTarget(reader.getSurface());b.set(CaptureRequest.CONTROL_AF_MODE,CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);b.set(CaptureRequest.JPEG_ORIENTATION,orientation());session.capture(b.build(),null,handler);}catch(Exception e){capturing=false;if(select!=null)select.setEnabled(true);fail("Não foi possível selecionar este quadro.");}}
  private int orientation(){int r=getWindowManager().getDefaultDisplay().getRotation(),d=r==Surface.ROTATION_90?90:r==Surface.ROTATION_180?180:r==Surface.ROTATION_270?270:0;Integer s=chars==null?90:chars.get(CameraCharacteristics.SENSOR_ORIENTATION);return ((s==null?90:s)+d+360)%360;}
  private void closeCamera(){try{if(session!=null)session.close();}catch(Exception ignored){}session=null;try{if(camera!=null)camera.close();}catch(Exception ignored){}camera=null;try{if(reader!=null)reader.close();}catch(Exception ignored){}reader=null;preview=null;opening=false;}

  private void showOcr(File f){
    closeCamera();root.removeAllViews();web=new WebView(this);web.setBackgroundColor(Color.rgb(5,9,20));WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setCacheMode(WebSettings.LOAD_DEFAULT);if(Build.VERSION.SDK_INT>=21)s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);web.addJavascriptInterface(new Bridge(),"LensNative");web.setWebViewClient(new LocalClient(f));root.addView(web,new FrameLayout.LayoutParams(-1,-1));web.loadUrl("https://lens.local/lens-live.html");
  }
  private final class LocalClient extends WebViewClient{
    private final File file;LocalClient(File f){file=f;}
    @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest req){
      try{android.net.Uri u=req.getUrl();if(!"lens.local".equalsIgnoreCase(u.getHost()))return null;String p=u.getPath()==null?"/":u.getPath();Map<String,String> h=new HashMap<>();h.put("Cache-Control","no-store");h.put("Access-Control-Allow-Origin","*");if("/lens-live.html".equals(p)||"/".equals(p))return new WebResourceResponse("text/html","UTF-8",200,"OK",h,getAssets().open("lens-live.html"));if("/capture.jpg".equals(p))return new WebResourceResponse("image/jpeg",null,200,"OK",h,new FileInputStream(file));}catch(Exception ignored){}return null;
    }
  }
  public final class Bridge{
    @JavascriptInterface public void useText(String t){if(t==null||t.trim().isEmpty())return;runOnUiThread(()->{Intent d=new Intent();d.putExtra(EXTRA_SELECTED_TEXT,t.trim());setResult(RESULT_OK,d);finish();});}
    @JavascriptInterface public void retake(){runOnUiThread(LiveLensActivity.this::showCamera);}
    @JavascriptInterface public void close(){runOnUiThread(LiveLensActivity.this::finish);}
    @JavascriptInterface public void copy(String t){if(t==null||t.trim().isEmpty())return;runOnUiThread(()->{ClipboardManager cm=(ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(cm!=null)cm.setPrimaryClip(ClipData.newPlainText("Texto OCR",t.trim()));Toast.makeText(LiveLensActivity.this,"Texto copiado",Toast.LENGTH_SHORT).show();});}
    @JavascriptInterface public void share(String t){if(t==null||t.trim().isEmpty())return;runOnUiThread(()->{try{Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,t.trim());startActivity(Intent.createChooser(i,"Compartilhar texto"));}catch(Exception ignored){}});}
  }
  private void destroyWeb(){if(web==null)return;try{web.removeJavascriptInterface("LensNative");web.stopLoading();web.loadUrl("about:blank");web.destroy();}catch(Exception ignored){}web=null;}
  @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_CAMERA){if(g.length>0&&g[0]==PackageManager.PERMISSION_GRANTED)open();else{Toast.makeText(this,"Permissão da câmera é necessária para o Lens.",Toast.LENGTH_LONG).show();finish();}}}
  @Override protected void onResume(){super.onResume();if(web==null&&texture!=null&&texture.isAvailable())open();}
  @Override protected void onPause(){if(web==null)closeCamera();super.onPause();}
  @Override public void onBackPressed(){if(web!=null)showCamera();else finish();}
  @Override protected void onDestroy(){closeCamera();destroyWeb();stopThread();if(captureFile!=null)try{captureFile.delete();}catch(Exception ignored){}super.onDestroy();}
}
