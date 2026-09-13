package com.bordatto.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.max
import kotlin.math.min

private val Brown = Color(0xFF160B07)
private val SurfaceBrown = Color(0xFF24140D)
private val Gold = Color(0xFFD7B477)
private val Cream = Color(0xFFF7EFE4)

private enum class StitchCommand { STITCH, JUMP, COLOR_CHANGE, END }
private data class StitchPoint(val x: Float, val y: Float, val command: StitchCommand, val color: Int)
private data class Design(
    val name: String,
    val stitches: List<StitchPoint>,
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float,
    val colors: Int
) {
    val width get() = maxX - minX
    val height get() = maxY - minY
    val stitchCount get() = stitches.count { it.command == StitchCommand.STITCH }
    val jumpCount get() = stitches.count { it.command == StitchCommand.JUMP }
    val colorChanges get() = stitches.count { it.command == StitchCommand.COLOR_CHANGE }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val shared = when (intent?.action) {
            Intent.ACTION_VIEW -> intent.data
            Intent.ACTION_SEND -> if (android.os.Build.VERSION.SDK_INT >= 33) intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java) else @Suppress("DEPRECATION") intent.getParcelableExtra(Intent.EXTRA_STREAM)
            else -> null
        }
        setContent { BordattoApp(shared) }
    }
}

@Composable
private fun BordattoApp(initialUri: Uri?) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var design by remember { mutableStateOf<Design?>(null) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var pendingUri by remember { mutableStateOf(initialUri) }

    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        pendingUri = uri
    }

    LaunchedEffect(pendingUri) {
        val uri = pendingUri ?: return@LaunchedEffect
        loading = true
        error = null
        runCatching {
            withContext(Dispatchers.IO) {
                val resolver = context.contentResolver
                val name = resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { c ->
                    if (c.moveToFirst()) c.getString(0) else null
                } ?: uri.lastPathSegment ?: "matriz.dst"
                if (!name.lowercase().endsWith(".dst")) error("Nesta versão 0.1, o formato implementado é DST. Próximos formatos entram nas próximas versões.")
                val bytes = resolver.openInputStream(uri)?.use { it.readBytes() } ?: error("Não foi possível ler o arquivo.")
                parseDst(name, bytes)
            }
        }.onSuccess { design = it }.onFailure { error = it.message ?: "Erro ao abrir a matriz." }
        loading = false
        pendingUri = null
    }

    MaterialTheme(
        colorScheme = darkColorScheme(primary = Gold, background = Brown, surface = SurfaceBrown, onBackground = Cream, onSurface = Cream),
    ) {
        Surface(Modifier.fillMaxSize(), color = Brown) {
            if (design == null) HomeScreen(loading) { picker.launch(arrayOf("*/*")) }
            else ViewerScreen(design!!) { design = null }
        }
        error?.let { message ->
            AlertDialog(
                onDismissRequest = { error = null },
                title = { Text("BORDATTO") },
                text = { Text(message) },
                confirmButton = { TextButton(onClick = { error = null }) { Text("OK") } }
            )
        }
    }
}

@Composable
private fun HomeScreen(loading: Boolean, onOpen: () -> Unit) {
    if (loading) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Gold) }
        return
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(22.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item {
            Spacer(Modifier.height(20.dp))
            Text("BORDATTO", color = Gold, fontSize = 30.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 4.sp)
            Text("Da ideia à matriz. Tudo pelo celular.", color = Cream.copy(alpha = .72f), fontSize = 14.sp)
            Spacer(Modifier.height(28.dp))
            Text("Seu estúdio de bordado", fontSize = 29.sp, lineHeight = 34.sp, fontWeight = FontWeight.SemiBold)
            Text("Visualize e analise matrizes diretamente no Android.", color = Cream.copy(alpha = .72f))
        }
        item { HomeCard("Abrir matriz DST", "Escolha uma matriz no celular, Drive ou armazenamento externo.", true, onOpen) }
        item { HomeCard("Criar projeto", "Base preparada para o futuro editor profissional.", false) {} }
        item { HomeCard("Simular", "Player ponto a ponto entra na próxima evolução.", false) {} }
        item { HomeCard("Converter", "Conversões serão habilitadas por formato validado.", false) {} }
        item { Text("BORDATTO Foundation 0.1 • APK de teste", color = Cream.copy(alpha = .55f), fontSize = 12.sp) }
    }
}

@Composable
private fun HomeCard(title: String, subtitle: String, enabled: Boolean, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(containerColor = if (enabled) Gold.copy(alpha = .16f) else SurfaceBrown)
    ) {
        Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Text(title, fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = if (enabled) Gold else Cream)
            Text(subtitle, fontSize = 13.sp, color = Cream.copy(alpha = .68f))
        }
    }
}

@Composable
private fun ViewerScreen(design: Design, onBack: () -> Unit) {
    var zoom by remember { mutableFloatStateOf(1f) }
    var pan by remember { mutableStateOf(Offset.Zero) }
    var grid by remember { mutableStateOf(true) }
    var info by remember { mutableStateOf(true) }
    val transform = rememberTransformableState { z, p, _ ->
        zoom = (zoom * z).coerceIn(.25f, 20f)
        pan += p
    }

    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onBack) { Text("‹ Voltar") }
            Column(Modifier.weight(1f)) {
                Text(design.name, fontWeight = FontWeight.SemiBold)
                Text("DST • ${design.stitchCount} pontadas • ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm", fontSize = 11.sp, color = Cream.copy(alpha=.7f))
            }
        }
        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(selected = grid, onClick = { grid = !grid }, label = { Text("Grade") })
            FilterChip(selected = info, onClick = { info = !info }, label = { Text("Info") })
            AssistChip(onClick = { zoom = 1f; pan = Offset.Zero }, label = { Text("Centralizar") })
        }
        Box(
            Modifier.weight(1f).fillMaxWidth().background(Color(0xFF0D0806)).transformable(transform).pointerInput(Unit) {
                detectTapGestures(onDoubleTap = { zoom = 1f; pan = Offset.Zero })
            }
        ) {
            StitchCanvas(design, zoom, pan, grid, Modifier.fillMaxSize())
            if (info) {
                Card(Modifier.align(Alignment.TopEnd).padding(12.dp), colors = CardDefaults.cardColors(containerColor = SurfaceBrown.copy(alpha=.95f))) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("Análise", color = Gold, fontWeight = FontWeight.SemiBold)
                        Text("Pontadas: ${design.stitchCount}", fontSize=12.sp)
                        Text("Saltos: ${design.jumpCount}", fontSize=12.sp)
                        Text("Trocas de cor: ${design.colorChanges}", fontSize=12.sp)
                        Text("Cores: ${design.colors}", fontSize=12.sp)
                    }
                }
            }
        }
        Text("Zoom ${"%.0f".format(zoom * 100)}%  •  pinça + arraste  •  duplo toque centraliza", modifier=Modifier.padding(12.dp), fontSize=12.sp, color=Cream.copy(alpha=.7f))
    }
}

@Composable
private fun StitchCanvas(design: Design, zoom: Float, pan: Offset, grid: Boolean, modifier: Modifier) {
    val palette = listOf(Color(0xFFD7B477), Color(0xFFF1E3C6), Color(0xFFBE7C4D), Color(0xFFA96A5B), Color(0xFF7A9273), Color(0xFFE3C17A))
    Canvas(modifier) {
        if (grid) {
            val step = max(24f, 20f * zoom)
            var gx = pan.x % step
            while (gx < size.width) { drawLine(Color.White.copy(alpha=.05f), Offset(gx,0f), Offset(gx,size.height)); gx += step }
            var gy = pan.y % step
            while (gy < size.height) { drawLine(Color.White.copy(alpha=.05f), Offset(0f,gy), Offset(size.width,gy)); gy += step }
        }
        if (design.stitches.isEmpty()) return@Canvas
        val w = max(1f, design.width); val h = max(1f, design.height)
        val fit = min(size.width / w, size.height / h) * .82f
        val px = fit * zoom
        val center = Offset(size.width/2 + pan.x, size.height/2 + pan.y)
        val cx=(design.minX+design.maxX)/2; val cy=(design.minY+design.maxY)/2
        fun map(x:Float,y:Float)=Offset(center.x+(x-cx)*px, center.y+(y-cy)*px)
        val paths=mutableMapOf<Int, Path>(); var previous:Offset?=null; var prevColor=-1
        for (st in design.stitches) {
            val cur=map(st.x,st.y)
            if (st.command==StitchCommand.STITCH) {
                val path=paths.getOrPut(st.color){Path()}
                if (previous==null || prevColor!=st.color) path.moveTo(cur.x,cur.y) else path.lineTo(cur.x,cur.y)
            } else previous=null
            previous=cur; prevColor=st.color
        }
        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }
    }
}

private fun parseDst(fileName: String, bytes: ByteArray): Design {
    require(bytes.size >= 512) { "Arquivo DST inválido ou incompleto." }
    val header = bytes.copyOfRange(0, 512).toString(Charsets.US_ASCII)
    val label = header.lineSequence().firstOrNull { it.startsWith("LA:") }?.removePrefix("LA:")?.trim()?.takeIf { it.isNotBlank() } ?: fileName.substringBeforeLast('.')
    val pts=ArrayList<StitchPoint>(); var x=0; var y=0; var color=0; var minX=0; var maxX=0; var minY=0; var maxY=0; var o=512
    while (o+2 < bytes.size) {
        val a=bytes[o].toInt() and 255; val b=bytes[o+1].toInt() and 255; val c=bytes[o+2].toInt() and 255; o+=3
        if ((c and 0xF3)==0xF3) { pts += StitchPoint(x/10f,y/10f,StitchCommand.END,color); break }
        x += decodeX(a,b,c); y -= decodeY(a,b,c)
        minX=min(minX,x); maxX=max(maxX,x); minY=min(minY,y); maxY=max(maxY,y)
        val command = when { (c and 0xC3)==0xC3 -> StitchCommand.COLOR_CHANGE; (c and 0x83)==0x83 -> StitchCommand.JUMP; else -> StitchCommand.STITCH }
        if (command==StitchCommand.COLOR_CHANGE) color++
        pts += StitchPoint(x/10f,y/10f,command,color)
    }
    return Design(label, pts, minX/10f,minY/10f,maxX/10f,maxY/10f,color+1)
}
private fun decodeX(a:Int,b:Int,c:Int):Int { var x=0; if(a and 1!=0)x+=1;if(a and 2!=0)x-=1;if(a and 4!=0)x+=9;if(a and 8!=0)x-=9;if(b and 1!=0)x+=3;if(b and 2!=0)x-=3;if(b and 4!=0)x+=27;if(b and 8!=0)x-=27;if(c and 4!=0)x+=81;if(c and 8!=0)x-=81;return x }
private fun decodeY(a:Int,b:Int,c:Int):Int { var y=0; if(a and 0x80!=0)y+=1;if(a and 0x40!=0)y-=1;if(a and 0x20!=0)y+=9;if(a and 0x10!=0)y-=9;if(b and 0x80!=0)y+=3;if(b and 0x40!=0)y-=3;if(b and 0x20!=0)y+=27;if(b and 0x10!=0)y-=27;if(c and 0x20!=0)y+=81;if(c and 0x10!=0)y-=81;return y }
