package com.timachado.bordatto;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.*;
import android.widget.*;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

public class MainActivity extends Activity {
    private static final int PICK_MATRIX = 1001;
    private static final int PICK_FONT = 1002;
    private static final int PICK_CONVERT = 1003;
    private static final int SAVE_FILE = 1004;

    private final int BROWN = Color.rgb(43, 28, 23);
    private final int BROWN2 = Color.rgb(74, 47, 38);
    private final int GOLD = Color.rgb(215, 180, 106);
    private final int IVORY = Color.rgb(247, 241, 231);

    private LinearLayout root;
    private TextView status;
    private StitchView stitchView;
    private SeekBar simulation;
    private File currentMatrix;
    private File selectedFont;
    private File pendingSave;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(BROWN);
        getWindow().setNavigationBarColor(BROWN);
        if (!Python.isStarted()) Python.start(new AndroidPlatform(this));
        showHome();
    }

    private TextView text(String s, float size, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(s); t.setTextSize(size); t.setTextColor(color);
        t.setPadding(dp(4), dp(4), dp(4), dp(4));
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    private GradientDrawable bg(int color, int radius) {
        GradientDrawable g = new GradientDrawable(); g.setColor(color); g.setCornerRadius(dp(radius)); return g;
    }

    private Button button(String label) {
        Button b = new Button(this); b.setText(label); b.setTextColor(Color.WHITE); b.setTextSize(16); b.setAllCaps(false);
        b.setBackground(bg(BROWN, 18)); b.setPadding(dp(12), dp(12), dp(12), dp(12));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2); p.setMargins(0, dp(6), 0, dp(6)); b.setLayoutParams(p); return b;
    }

    private LinearLayout card(String title, String desc) {
        LinearLayout c = new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setPadding(dp(16), dp(14), dp(16), dp(14)); c.setBackground(bg(Color.WHITE, 20));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2); p.setMargins(0, dp(7), 0, dp(7)); c.setLayoutParams(p);
        c.addView(text(title, 18, BROWN, true)); c.addView(text(desc, 14, BROWN2, false)); return c;
    }

    private void base(String title, String subtitle) {
        ScrollView scroll = new ScrollView(this); scroll.setBackgroundColor(IVORY);
        root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(dp(18), dp(18), dp(18), dp(28)); scroll.addView(root); setContentView(scroll);
        root.addView(text("BORDATTO", 32, BROWN, true)); root.addView(text("Seu estúdio de bordado", 16, GOLD, true));
        Space s = new Space(this); s.setMinimumHeight(dp(14)); root.addView(s); root.addView(text(title, 24, BROWN, true)); root.addView(text(subtitle, 14, BROWN2, false));
    }

    private void showHome() {
        base("Tudo no seu Android", "Visualize, crie nomes, simule e converta matrizes.");
        LinearLayout c1 = card("Abrir matriz", "PES, DST, JEF, PEC, VP3, HUS, EXP, XXX, U01, TBF e dezenas de outros formatos."); c1.setOnClickListener(v -> pickMatrix(PICK_MATRIX)); root.addView(c1);
        LinearLayout c2 = card("Criar nome com sua fonte", "Importe TTF/OTF do celular, escreva o nome, defina largura e cor e gere uma matriz real."); c2.setOnClickListener(v -> showNameCreator()); root.addView(c2);
        LinearLayout c3 = card("Converter formato", "Converta uma matriz para PES, DST, JEF, VP3, EXP, XXX, U01 ou TBF."); c3.setOnClickListener(v -> showConverter()); root.addView(c3);
        LinearLayout c4 = card("BORDATTO + WordPress", "Integração com o plugin BORDATTO Connect, biblioteca e distribuição do APK."); c4.setOnClickListener(v -> showWordPress()); root.addView(c4);
        root.addView(text("Visual Premium • Marrom + dourado • Android nativo", 13, GOLD, true));
    }

    private void addBack() { Button b = button("← Voltar"); b.setOnClickListener(v -> showHome()); root.addView(b, 0); }

    private void pickMatrix(int request) {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("*/*"); startActivityForResult(i, request);
    }

    private File copyUri(Uri uri, String fallback) throws Exception {
        String name = fallback;
        try (android.database.Cursor c = getContentResolver().query(uri, null, null, null, null)) {
            if (c != null && c.moveToFirst()) { int idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME); if (idx >= 0) name = c.getString(idx); }
        }
        name = name.replaceAll("[^A-Za-z0-9._-]", "_"); File out = new File(getCacheDir(), System.currentTimeMillis() + "_" + name);
        try (InputStream in = getContentResolver().openInputStream(uri); OutputStream os = new FileOutputStream(out)) {
            byte[] buf = new byte[8192]; int n; while ((n = in.read(buf)) > 0) os.write(buf, 0, n);
        }
        return out;
    }

    private void showViewer(File f) {
        currentMatrix = f; base("Visualizador de Bordados", f.getName()); addBack();
        stitchView = new StitchView(this); stitchView.setBackgroundColor(Color.rgb(255,252,246)); root.addView(stitchView, new LinearLayout.LayoutParams(-1, dp(390)));
        simulation = new SeekBar(this); simulation.setMax(1000); simulation.setProgress(1000);
        simulation.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            public void onProgressChanged(SeekBar s, int p, boolean fromUser) { stitchView.progress = p / 1000f; stitchView.invalidate(); }
            public void onStartTrackingTouch(SeekBar s) {} public void onStopTrackingTouch(SeekBar s) {}
        });
        root.addView(text("Simulação da ordem de costura", 15, BROWN, true)); root.addView(simulation);
        status = text("Lendo matriz...", 15, BROWN2, false); root.addView(status);
        Button saveAs = button("Converter / salvar em outro formato"); saveAs.setOnClickListener(v -> convertCurrentDialog()); root.addView(saveAs);
        new Thread(() -> { try {
            PyObject mod = Python.getInstance().getModule("bordatto_engine"); String js = mod.callAttr("analyze", f.getAbsolutePath()).toString(); JSONObject o = new JSONObject(js);
            runOnUiThread(() -> applyAnalysis(o));
        } catch (Exception e) { runOnUiThread(() -> status.setText("Erro ao ler: " + e.getMessage())); } }).start();
    }

    private void applyAnalysis(JSONObject o) {
        try {
            JSONArray p = o.getJSONArray("points"); ArrayList<PointF> pts = new ArrayList<>();
            for (int i=0;i<p.length();i++) { JSONArray a = p.getJSONArray(i); pts.add(new PointF((float)a.getDouble(0),(float)a.getDouble(1))); }
            stitchView.setPoints(pts);
            String info = "Pontadas: " + o.optInt("stitches") + "\nSaltos (Jump): " + o.optInt("jumps") + " • Cortes (Trim): " + o.optInt("trims") + "\nTrocas de cor: " + o.optInt("color_changes") + String.format(Locale.getDefault(), "\nDimensões: %.1f × %.1f mm", o.optDouble("width_mm"), o.optDouble("height_mm")) + String.format(Locale.getDefault(), "\nConsumo estimado de linha: %.2f m", o.optDouble("thread_m"));
            status.setText(info);
        } catch (Exception e) { status.setText("Falha na visualização: " + e.getMessage()); }
    }

    private void showNameCreator() {
        base("Criar Nome", "Use uma fonte TTF/OTF do próprio celular."); addBack();
        EditText name = new EditText(this); name.setHint("Digite o nome"); name.setText("Maria"); root.addView(name);
        Button choose = button("Adicionar fonte TTF/OTF"); choose.setOnClickListener(v -> { Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("*/*"); startActivityForResult(i, PICK_FONT); }); root.addView(choose);
        root.addView(text("Largura final (30–200 mm)", 14, BROWN, true)); SeekBar width = new SeekBar(this); width.setMax(170); width.setProgress(60); root.addView(width);
        EditText color = new EditText(this); color.setHint("Cor HEX"); color.setText("#D7B46A"); root.addView(color);
        Spinner format = new Spinner(this); String[] outs = {"PES","DST","JEF","VP3","EXP","XXX","U01","TBF"}; format.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, outs)); root.addView(format);
        status = text(selectedFont == null ? "Selecione sua fonte." : "Fonte: " + selectedFont.getName(), 14, BROWN2, false); root.addView(status);
        Button gen = button("Gerar matriz e visualizar"); gen.setOnClickListener(v -> {
            if (selectedFont == null) { status.setText("Selecione uma fonte TTF/OTF primeiro."); return; }
            String txt = name.getText().toString().trim(); int widthMm = 30 + width.getProgress(); String ext = outs[format.getSelectedItemPosition()].toLowerCase(Locale.ROOT); File out = new File(getCacheDir(), "BORDATTO_" + System.currentTimeMillis() + "." + ext); status.setText("Gerando pontadas...");
            new Thread(() -> { try { Python.getInstance().getModule("bordatto_engine").callAttr("text_to_embroidery", txt, selectedFont.getAbsolutePath(), widthMm, color.getText().toString().trim(), out.getAbsolutePath()); runOnUiThread(() -> showViewer(out)); } catch (Exception e) { runOnUiThread(() -> status.setText("Erro ao gerar: " + e.getMessage())); } }).start();
        }); root.addView(gen);
        root.addView(text("O gerador inicial cria pontadas reais por preenchimento. A camada profissional Satin/Underlay/compensação será evoluída nas próximas versões.", 12, BROWN2, false));
    }

    private void showConverter() {
        base("Converter Formato", "Selecione uma matriz e escolha o formato de saída."); addBack(); status = text("Nenhum arquivo selecionado.", 14, BROWN2, false); root.addView(status); Button pick = button("Selecionar matriz"); pick.setOnClickListener(v -> pickMatrix(PICK_CONVERT)); root.addView(pick);
    }

    private void convertCurrentDialog() {
        if (currentMatrix == null) return; String[] formats = {"PES","DST","JEF","VP3","EXP","XXX","U01","TBF"}; new AlertDialog.Builder(this).setTitle("Formato de saída").setItems(formats, (d, which) -> runConversion(currentMatrix, formats[which])).show();
    }

    private void runConversion(File src, String format) {
        File out = new File(getCacheDir(), "BORDATTO_convertido_" + System.currentTimeMillis() + "." + format.toLowerCase(Locale.ROOT)); Toast.makeText(this, "Convertendo...", Toast.LENGTH_SHORT).show();
        new Thread(() -> { try { Python.getInstance().getModule("bordatto_engine").callAttr("convert", src.getAbsolutePath(), out.getAbsolutePath()); pendingSave = out; runOnUiThread(() -> requestSave(out)); } catch (Exception e) { runOnUiThread(() -> Toast.makeText(this, "Erro: " + e.getMessage(), Toast.LENGTH_LONG).show()); } }).start();
    }

    private void requestSave(File f) {
        pendingSave = f; Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("application/octet-stream"); i.putExtra(Intent.EXTRA_TITLE, f.getName()); startActivityForResult(i, SAVE_FILE);
    }

    private void showWordPress() {
        base("BORDATTO + WordPress", "Integração preparada para seu site."); addBack(); root.addView(card("BORDATTO Connect", "Instale o plugin ZIP no WordPress em Plugins → Adicionar plugin → Enviar plugin.")); root.addView(card("Shortcode", "Use [bordatto_app] para mostrar o aplicativo, plano e links de download.")); root.addView(card("Planos", "Free, Plus, Pro e Studio com biblioteca filtrada por usuário.")); root.addView(card("APK / Google Play", "O plugin possui campos para URL direta do APK e futura página da Google Play."));
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data); if (result != RESULT_OK || data == null || data.getData() == null) return; Uri uri = data.getData();
        try {
            if (request == PICK_MATRIX) { showViewer(copyUri(uri, "matriz.bin")); }
            else if (request == PICK_FONT) { selectedFont = copyUri(uri, "fonte.ttf"); Toast.makeText(this, "Fonte carregada.", Toast.LENGTH_SHORT).show(); showNameCreator(); }
            else if (request == PICK_CONVERT) { File src = copyUri(uri, "matriz.bin"); String[] formats = {"PES","DST","JEF","VP3","EXP","XXX","U01","TBF"}; new AlertDialog.Builder(this).setTitle("Converter para").setItems(formats, (d, which) -> runConversion(src, formats[which])).show(); }
            else if (request == SAVE_FILE && pendingSave != null) { try (InputStream in = new FileInputStream(pendingSave); OutputStream out = getContentResolver().openOutputStream(uri)) { byte[] buf = new byte[8192]; int n; while ((n = in.read(buf)) > 0) out.write(buf,0,n); } Toast.makeText(this, "Arquivo salvo.", Toast.LENGTH_LONG).show(); }
        } catch (Exception e) { Toast.makeText(this, "Erro: " + e.getMessage(), Toast.LENGTH_LONG).show(); }
    }

    private int dp(int n) { return (int)(n * getResources().getDisplayMetrics().density + .5f); }

    class StitchView extends View {
        ArrayList<PointF> pts = new ArrayList<>(); Paint line = new Paint(Paint.ANTI_ALIAS_FLAG); Paint grid = new Paint(Paint.ANTI_ALIAS_FLAG); float scale = 1f, tx = 0f, ty = 0f, progress = 1f; float lastX, lastY; ScaleGestureDetector detector;
        StitchView(Context c) { super(c); line.setColor(BROWN); line.setStrokeWidth(dp(1)); line.setStyle(Paint.Style.STROKE); grid.setColor(Color.rgb(233,224,213)); grid.setStrokeWidth(1); detector = new ScaleGestureDetector(c, new ScaleGestureDetector.SimpleOnScaleGestureListener() { @Override public boolean onScale(ScaleGestureDetector d) { scale *= d.getScaleFactor(); scale = Math.max(.6f, Math.min(scale, 8f)); invalidate(); return true; } }); }
        void setPoints(ArrayList<PointF> p) { pts = p; invalidate(); }
        @Override protected void onDraw(Canvas c) { super.onDraw(c); for (int x=0;x<getWidth();x+=dp(32)) c.drawLine(x,0,x,getHeight(),grid); for (int y=0;y<getHeight();y+=dp(32)) c.drawLine(0,y,getWidth(),y,grid); if (pts.size()<2) return; float minX=Float.MAX_VALUE,maxX=-Float.MAX_VALUE,minY=Float.MAX_VALUE,maxY=-Float.MAX_VALUE; for(PointF p:pts){ minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);} float sx=(getWidth()*.82f)/Math.max(1f,maxX-minX); float sy=(getHeight()*.82f)/Math.max(1f,maxY-minY); float base=Math.min(sx,sy)*scale; int limit=Math.max(2,(int)(pts.size()*progress)); Path path=new Path(); PointF p0=pts.get(0); path.moveTo((p0.x-minX)*base+getWidth()*.09f+tx,(p0.y-minY)*base+getHeight()*.09f+ty); for(int i=1;i<limit;i++){ PointF p=pts.get(i); path.lineTo((p.x-minX)*base+getWidth()*.09f+tx,(p.y-minY)*base+getHeight()*.09f+ty); } c.drawPath(path,line); }
        @Override public boolean onTouchEvent(MotionEvent e) { detector.onTouchEvent(e); if (e.getPointerCount()==1) { if (e.getAction()==MotionEvent.ACTION_DOWN){lastX=e.getX();lastY=e.getY();} else if(e.getAction()==MotionEvent.ACTION_MOVE){ tx += e.getX()-lastX; ty += e.getY()-lastY; lastX=e.getX(); lastY=e.getY(); invalidate(); } } return true; }
    }
}
