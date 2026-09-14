from pathlib import Path
import runpy
import re

runpy.run_path('.github/scripts/patch_bordatto_047.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

insert_at = text.index('class MainActivity')
core = r'''private data class LetteringOptions(
    val heightMm: Float,
    val spacingPercent: Float,
    val densityMm: Float,
    val pullCompensationMm: Float,
    val satinMaxWidthMm: Float,
    val underlay: String,
    val fontStyle: String
)

private data class LetteringScanBand(val top: Int, val bottom: Int)
private data class LetteringScanColumn(val x: Int, val bands: List<LetteringScanBand>)

private fun letteringTypeface(style: String): android.graphics.Typeface = when (style) {
    "Elegance" -> android.graphics.Typeface.create("serif", android.graphics.Typeface.ITALIC)
    "Classic" -> android.graphics.Typeface.create("serif", android.graphics.Typeface.BOLD)
    "Sweet" -> android.graphics.Typeface.create("sans-serif", android.graphics.Typeface.BOLD)
    "Handwriting" -> android.graphics.Typeface.create("cursive", android.graphics.Typeface.NORMAL)
    else -> android.graphics.Typeface.create("sans-serif", android.graphics.Typeface.NORMAL)
}

private fun generateLetteringDesign(rawText: String, options: LetteringOptions): Design {
    val clean = rawText.trim().replace(Regex("\\s+"), " ").take(28)
    require(clean.isNotBlank()) { "Digite um nome ou texto para gerar a matriz." }
    require(options.heightMm in 8f..160f) { "Tamanho de lettering fora da faixa de teste." }

    val pxPerMm = 5.5f
    val paint = android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG).apply {
        color = android.graphics.Color.WHITE
        style = android.graphics.Paint.Style.FILL
        textSize = options.heightMm * pxPerMm
        typeface = letteringTypeface(options.fontStyle)
        isSubpixelText = true
    }
    val glyphPath = android.graphics.Path()
    var cursorX = 0f
    val spacingFactor = (1f + options.spacingPercent / 100f).coerceIn(.72f, 1.65f)
    clean.forEach { ch ->
        val token = ch.toString()
        if (ch != ' ') paint.getTextPath(token, 0, token.length, cursorX, 0f, glyphPath)
        cursorX += paint.measureText(token).coerceAtLeast(paint.textSize * .18f) * spacingFactor
    }
    require(!glyphPath.isEmpty) { "A fonte selecionada não gerou contornos válidos." }

    val rawBounds = android.graphics.RectF()
    glyphPath.computeBounds(rawBounds, true)
    val marginPx = (3.5f + options.pullCompensationMm) * pxPerMm
    val matrix = android.graphics.Matrix().apply {
        setTranslate(-rawBounds.left + marginPx, -rawBounds.top + marginPx)
    }
    val movedPath = android.graphics.Path()
    glyphPath.transform(matrix, movedPath)
    val bounds = android.graphics.RectF()
    movedPath.computeBounds(bounds, true)

    val bitmapWidth = kotlin.math.ceil(bounds.right + marginPx).toInt().coerceIn(32, 4096)
    val bitmapHeight = kotlin.math.ceil(bounds.bottom + marginPx).toInt().coerceIn(32, 4096)
    val bitmap = android.graphics.Bitmap.createBitmap(bitmapWidth, bitmapHeight, android.graphics.Bitmap.Config.ARGB_8888)
    android.graphics.Canvas(bitmap).drawPath(movedPath, paint)

    val left = kotlin.math.floor(bounds.left).toInt().coerceAtLeast(0)
    val right = kotlin.math.ceil(bounds.right).toInt().coerceAtMost(bitmapWidth - 1)
    val top = kotlin.math.floor(bounds.top).toInt().coerceAtLeast(0)
    val bottom = kotlin.math.ceil(bounds.bottom).toInt().coerceAtMost(bitmapHeight - 1)
    val densityPx = (options.densityMm.coerceIn(.25f, 1.2f) * pxPerMm).toInt().coerceAtLeast(1)
    val columns = ArrayList<LetteringScanColumn>()
    val pixel = IntArray(1)

    var x = left
    while (x <= right) {
        val bands = ArrayList<LetteringScanBand>()
        var y = top
        while (y <= bottom) {
            bitmap.getPixels(pixel, 0, 1, x, y, 1, 1)
            val alpha = android.graphics.Color.alpha(pixel[0])
            if (alpha > 24) {
                val start = y
                var end = y
                y++
                while (y <= bottom) {
                    bitmap.getPixels(pixel, 0, 1, x, y, 1, 1)
                    if (android.graphics.Color.alpha(pixel[0]) <= 24) break
                    end = y
                    y++
                }
                if (end - start >= 1) bands += LetteringScanBand(start, end)
            }
            y++
        }
        if (bands.isNotEmpty()) columns += LetteringScanColumn(x, bands)
        x += densityPx
    }
    bitmap.recycle()
    require(columns.size >= 2) { "Texto muito pequeno para a densidade escolhida." }

    val stitches = ArrayList<StitchPoint>()
    val originX = bounds.left
    val originY = bounds.top
    fun mmX(px: Float) = (px - originX) / pxPerMm
    fun mmY(px: Float) = (px - originY) / pxPerMm
    fun addPoint(px: Float, py: Float, command: StitchCommand) {
        stitches += StitchPoint(mmX(px), mmY(py), command, 0)
    }
    fun startTrack(px: Float, py: Float) {
        addPoint(px, py, StitchCommand.JUMP)
        addPoint(px, py, StitchCommand.STITCH)
    }

    val maxTracks = columns.maxOfOrNull { it.bands.size } ?: 1
    val underlayStep = (densityPx * 3).coerceAtLeast(2)

    if (options.underlay.contains("Center", ignoreCase = true)) {
        for (track in 0 until maxTracks) {
            var lastX: Int? = null
            columns.forEach { col ->
                val band = col.bands.getOrNull(track) ?: run { lastX = null; return@forEach }
                val cy = (band.top + band.bottom) / 2f
                if (lastX == null || col.x - lastX!! > densityPx * 2) startTrack(col.x.toFloat(), cy)
                else addPoint(col.x.toFloat(), cy, StitchCommand.STITCH)
                lastX = col.x
            }
        }
    }

    if (options.underlay.contains("Edge", ignoreCase = true)) {
        for (track in 0 until maxTracks) {
            var first = true
            columns.forEach { col ->
                val band = col.bands.getOrNull(track) ?: run { first = true; return@forEach }
                val y = band.top.toFloat()
                if (first) { startTrack(col.x.toFloat(), y); first = false }
                else addPoint(col.x.toFloat(), y, StitchCommand.STITCH)
            }
            first = true
            columns.asReversed().forEach { col ->
                val band = col.bands.getOrNull(track) ?: run { first = true; return@forEach }
                val y = band.bottom.toFloat()
                if (first) { startTrack(col.x.toFloat(), y); first = false }
                else addPoint(col.x.toFloat(), y, StitchCommand.STITCH)
            }
        }
    }

    if (options.underlay.contains("Zigzag", ignoreCase = true)) {
        for (track in 0 until maxTracks) {
            var first = true
            var parity = false
            var sampledX = Int.MIN_VALUE
            columns.forEach { col ->
                if (sampledX != Int.MIN_VALUE && col.x - sampledX < underlayStep) return@forEach
                val band = col.bands.getOrNull(track) ?: run { first = true; return@forEach }
                val y = if (parity) band.top + (band.bottom - band.top) * .22f else band.bottom - (band.bottom - band.top) * .22f
                if (first) { startTrack(col.x.toFloat(), y); first = false }
                else addPoint(col.x.toFloat(), y, StitchCommand.STITCH)
                parity = !parity
                sampledX = col.x
            }
        }
    }

    val pullPx = options.pullCompensationMm.coerceIn(0f, 1.5f) * pxPerMm
    val satinLimit = options.satinMaxWidthMm.coerceIn(3f, 18f)
    val tatamiRowPx = (2.1f * pxPerMm).toInt().coerceAtLeast(3)

    for (track in 0 until maxTracks) {
        var parity = false
        var connected = false
        var lastX = Int.MIN_VALUE
        columns.forEach { col ->
            val band = col.bands.getOrNull(track) ?: run { connected = false; return@forEach }
            if (lastX != Int.MIN_VALUE && col.x - lastX > densityPx * 2) connected = false
            val bandMm = (band.bottom - band.top) / pxPerMm
            if (bandMm <= satinLimit) {
                val y = if (parity) band.top - pullPx else band.bottom + pullPx
                if (!connected) { startTrack(col.x.toFloat(), y); connected = true }
                else addPoint(col.x.toFloat(), y, StitchCommand.STITCH)
                parity = !parity
            } else {
                val ys = ArrayList<Float>()
                var yy = band.top.toFloat()
                while (yy <= band.bottom) { ys += yy; yy += tatamiRowPx }
                if (parity) ys.reverse()
                if (ys.isNotEmpty()) {
                    if (!connected) { startTrack(col.x.toFloat(), ys.first()); connected = true }
                    ys.forEachIndexed { index, py -> if (index > 0 || stitches.lastOrNull()?.command != StitchCommand.STITCH) addPoint(col.x.toFloat(), py, StitchCommand.STITCH) }
                }
                parity = !parity
            }
            lastX = col.x
        }
    }

    require(stitches.count { it.command == StitchCommand.STITCH } >= 6) { "Não foi possível gerar pontadas suficientes." }
    val last = stitches.last()
    val tie = 0.28f
    stitches += StitchPoint(last.x + tie, last.y, StitchCommand.STITCH, 0)
    stitches += StitchPoint(last.x, last.y + tie, StitchCommand.STITCH, 0)
    stitches += StitchPoint(last.x, last.y, StitchCommand.STITCH, 0)
    stitches += StitchPoint(last.x, last.y, StitchCommand.END, 0)

    val sew = stitches.filter { it.command == StitchCommand.STITCH || it.command == StitchCommand.JUMP }
    val minX = sew.minOf { it.x }
    val maxX = sew.maxOf { it.x }
    val minY = sew.minOf { it.y }
    val maxY = sew.maxOf { it.y }
    val goldArgb = 0xFFE1B66F.toInt()
    return Design(
        name = "Lettering • $clean",
        stitches = stitches,
        minX = minX,
        minY = minY,
        maxX = maxX,
        maxY = maxY,
        colors = 1,
        format = "BORDATTO",
        threadColors = listOf(goldArgb),
        threadInfos = listOf(DesignThreadInfo(goldArgb, "Dourado BORDATTO", "BD-001", "BORDATTO", "Lettering Pro"))
    )
}

'''
text = text[:insert_at] + core + text[insert_at:]

pattern = re.compile(
    r'''page == Page\.LETTERING -> LetteringScreen\(\s*onBack = \{ page = Page\.MAIN \},\s*onGenerate = \{.*?\}\s*\)''',
    re.S
)
replacement = '''page == Page.LETTERING -> LetteringScreen(\n                    onBack = { page = Page.MAIN },\n                    onGenerate = { generated ->\n                        design = generated\n                        page = Page.MAIN\n                        activeTab = MainTab.CREATE\n                    }\n                )'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('0.2.27 LetteringScreen callback anchor not found')

start = text.index('@Composable\nprivate fun LetteringScreen')
end = text.index('@Composable\nprivate fun MachineScreen', start)
lettering_ui = r'''@Composable
private fun LetteringScreen(onBack: () -> Unit, onGenerate: (Design) -> Unit) {
    BackHandler(onBack = onBack)
    var name by remember { mutableStateOf("Maria") }
    var size by remember { mutableFloatStateOf(42f) }
    var spacing by remember { mutableFloatStateOf(0f) }
    var density by remember { mutableFloatStateOf(.42f) }
    var pullComp by remember { mutableFloatStateOf(.30f) }
    var satinMax by remember { mutableFloatStateOf(9f) }
    var font by remember { mutableStateOf("Elegance") }
    var underlay by remember { mutableStateOf("Center + Edge") }
    var localError by remember { mutableStateOf<String?>(null) }
    val fonts = listOf("Regular", "Elegance", "Classic", "Sweet", "Handwriting")
    val options = remember(size, spacing, density, pullComp, satinMax, underlay, font) {
        LetteringOptions(size, spacing, density, pullComp, satinMax, underlay, font)
    }

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader("Lettering Pro • Satin", onBack) }
        item {
            Surface(shape = RoundedCornerShape(18.dp), color = Gold.copy(alpha = .08f), border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.42f))) {
                Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.AutoAwesome, selected = true, size = 42.dp)
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Motor Satin Inicial", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                        Text("Underlay + compensação + fallback Tatami + pontos reais", color = Muted, fontSize = 9.sp)
                    }
                    Text("0.2.27", color = Gold, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
        item {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it.take(28) },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Nome ou texto") },
                leadingIcon = { Icon(Icons.Rounded.TextFields, null, tint = Gold) },
                supportingText = { Text("Até 28 caracteres • gera pontos e abre no visualizador/editor") },
                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold, focusedLabelColor = Gold)
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Cream), shape = RoundedCornerShape(26.dp)) {
                Box(Modifier.fillMaxWidth().height(175.dp).padding(horizontal = 12.dp), contentAlignment = Alignment.Center) {
                    Text(
                        name.ifBlank { "BORDATTO" },
                        color = GoldDeep,
                        fontSize = 46.sp,
                        fontFamily = if (font == "Elegance" || font == "Handwriting") FontFamily.Cursive else FontFamily.Serif,
                        fontWeight = if (font == "Classic" || font == "Sweet") FontWeight.Bold else FontWeight.Normal,
                        fontStyle = if (font == "Elegance") FontStyle.Italic else FontStyle.Normal,
                        textAlign = TextAlign.Center,
                        maxLines = 2
                    )
                }
            }
        }
        item { Text("Fonte", color = Cream, fontWeight = FontWeight.SemiBold) }
        items(fonts.size) { i ->
            val f = fonts[i]
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { font = f },
                shape = RoundedCornerShape(18.dp),
                color = if (font == f) Gold.copy(alpha=.16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (font == f) Gold.copy(alpha=.55f) else LineGold.copy(alpha=.45f))
            ) {
                Row(Modifier.padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.TextFields, selected = font == f, size = 38.dp)
                    Spacer(Modifier.width(10.dp))
                    Text(if (f == "Elegance") name.ifBlank { "Maria" } else "BORDATTO", color = Cream, fontFamily = if (f == "Elegance" || f == "Handwriting") FontFamily.Cursive else FontFamily.Serif, fontSize = 19.sp, modifier = Modifier.weight(1f))
                    Text(f, color = if (font == f) Gold else Muted, fontSize = 10.sp)
                }
            }
        }
        item {
            Text("Parâmetros profissionais", color = Cream, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            Text("Altura: ${"%.0f".format(size)} mm", color = Cream, fontSize = 12.sp)
            Slider(size, { size = it }, valueRange = 10f..90f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
            Text("Espaçamento: ${spacing.toInt()}%", color = Cream, fontSize = 12.sp)
            Slider(spacing, { spacing = it }, valueRange = -18f..40f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
            Text("Densidade Satin: ${"%.2f".format(density)} mm", color = Cream, fontSize = 12.sp)
            Slider(density, { density = it }, valueRange = .28f..1.0f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
            Text("Compensação de puxamento: ${"%.2f".format(pullComp)} mm", color = Cream, fontSize = 12.sp)
            Slider(pullComp, { pullComp = it }, valueRange = 0f..1.0f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
            Text("Largura máxima Satin: ${"%.1f".format(satinMax)} mm", color = Cream, fontSize = 12.sp)
            Slider(satinMax, { satinMax = it }, valueRange = 4f..14f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
        }
        item {
            Text("Underlay", color = Cream, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                listOf("Center", "Edge", "Zigzag").forEach { item ->
                    val selected = underlay == item
                    Surface(
                        modifier = Modifier.weight(1f).clickable { underlay = item },
                        shape = RoundedCornerShape(14.dp),
                        color = if (selected) Gold.copy(alpha=.16f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.55f) else LineGold.copy(alpha=.4f))
                    ) { Text(item, color = if (selected) Gold else Cream, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 10.dp)) }
                }
            }
            Spacer(Modifier.height(7.dp))
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { underlay = "Center + Edge" },
                shape = RoundedCornerShape(14.dp),
                color = if (underlay == "Center + Edge") Gold.copy(alpha=.16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (underlay == "Center + Edge") Gold.copy(alpha=.55f) else LineGold.copy(alpha=.4f))
            ) { Text("Center + Edge • recomendado para o teste", color = if (underlay == "Center + Edge") Gold else Cream, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 10.dp)) }
        }
        item {
            Surface(shape = RoundedCornerShape(16.dp), color = SurfaceBrown, border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.42f))) {
                Column(Modifier.fillMaxWidth().padding(11.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Verified, null, tint = Gold, modifier = Modifier.size(17.dp))
                        Spacer(Modifier.width(7.dp))
                        Text("Preflight do lettering", color = Gold, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                    }
                    Text("Satin até ${"%.1f".format(satinMax)} mm; acima disso o motor usa preenchimento Tatami de segurança.", color = Muted, fontSize = 8.sp)
                    Text("Densidade ${"%.2f".format(density)} mm • pull ${"%.2f".format(pullComp)} mm • underlay $underlay", color = Muted, fontSize = 8.sp)
                    Text("Depois de gerar, use o visualizador/editor e o Preflight PES/JEF antes de exportar.", color = Muted, fontSize = 8.sp)
                }
            }
        }
        item {
            Button(
                onClick = {
                    localError = null
                    runCatching { generateLetteringDesign(name, options) }
                        .onSuccess(onGenerate)
                        .onFailure { localError = it.message ?: "Falha ao gerar o lettering." }
                },
                enabled = name.isNotBlank(),
                modifier = Modifier.fillMaxWidth().height(58.dp),
                shape = RoundedCornerShape(20.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(Icons.Rounded.AutoAwesome, null)
                Spacer(Modifier.width(8.dp))
                Text("Gerar pontos e abrir no Editor", fontWeight = FontWeight.Bold)
            }
        }
        localError?.let { message ->
            item {
                Surface(shape = RoundedCornerShape(14.dp), color = Gold.copy(alpha=.08f), border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.5f))) {
                    Text(message, color = Cream, fontSize = 10.sp, modifier = Modifier.padding(11.dp))
                }
            }
        }
    }
}

'''
text = text[:start] + lettering_ui + text[end:]

text = text.replace('0.2.26', '0.2.27')
path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 28', 'versionCode = 29')
gradle = gradle.replace('versionName = "0.2.26"', 'versionName = "0.2.27"')
gradle_path.write_text(gradle, encoding='utf-8')

print('BORDATTO 0.2.27 Lettering Pro Satin initial engine applied successfully')
