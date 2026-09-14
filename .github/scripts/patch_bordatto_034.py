from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_033.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Visual diagnostic primitives derived from the same real stitch geometry used by Analyzer v1.
marker = '''private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
addition = r'''private enum class DiagnosticKind { LONG_STITCH, LONG_JUMP, DENSE_AREA }

private data class DiagnosticMarker(
    val kind: DiagnosticKind,
    val x: Float,
    val y: Float,
    val value: Double,
    val severity: Int,
    val startX: Float? = null,
    val startY: Float? = null,
    val endX: Float? = null,
    val endY: Float? = null
)

private fun collectDiagnosticMarkers(design: Design): List<DiagnosticMarker> {
    val markers = mutableListOf<DiagnosticMarker>()
    val cells = mutableMapOf<Pair<Int, Int>, Int>()
    var previous: StitchPoint? = null

    design.stitches.forEach { current ->
        val prev = previous
        if (prev != null && current.command != StitchCommand.END) {
            val distance = kotlin.math.hypot(
                (current.x - prev.x).toDouble(),
                (current.y - prev.y).toDouble()
            )

            if (current.command == StitchCommand.JUMP && distance > 12.0) {
                markers += DiagnosticMarker(
                    kind = DiagnosticKind.LONG_JUMP,
                    x = (prev.x + current.x) / 2f,
                    y = (prev.y + current.y) / 2f,
                    value = distance,
                    severity = if (distance >= 30.0) 3 else 2,
                    startX = prev.x,
                    startY = prev.y,
                    endX = current.x,
                    endY = current.y
                )
            }

            if (
                current.command == StitchCommand.STITCH &&
                prev.command == StitchCommand.STITCH &&
                current.color == prev.color &&
                distance > 8.0
            ) {
                markers += DiagnosticMarker(
                    kind = DiagnosticKind.LONG_STITCH,
                    x = (prev.x + current.x) / 2f,
                    y = (prev.y + current.y) / 2f,
                    value = distance,
                    severity = if (distance >= 12.0) 3 else 2,
                    startX = prev.x,
                    startY = prev.y,
                    endX = current.x,
                    endY = current.y
                )
            }
        }

        if (current.command == StitchCommand.STITCH) {
            val cellX = kotlin.math.floor(current.x.toDouble() / 5.0).toInt()
            val cellY = kotlin.math.floor(current.y.toDouble() / 5.0).toInt()
            val key = cellX to cellY
            cells[key] = (cells[key] ?: 0) + 1
        }

        previous = if (current.command == StitchCommand.END) null else current
    }

    cells.entries
        .filter { it.value >= 100 }
        .forEach { (cell, count) ->
            markers += DiagnosticMarker(
                kind = DiagnosticKind.DENSE_AREA,
                x = cell.first * 5f + 2.5f,
                y = cell.second * 5f + 2.5f,
                value = count.toDouble(),
                severity = if (count >= 180) 3 else 2
            )
        }

    return markers
        .sortedWith(compareByDescending<DiagnosticMarker> { it.severity }.thenByDescending { it.value })
        .take(80)
}

private fun diagnosticTitle(marker: DiagnosticMarker): String = when (marker.kind) {
    DiagnosticKind.LONG_STITCH -> "Ponto longo"
    DiagnosticKind.LONG_JUMP -> "Salto longo"
    DiagnosticKind.DENSE_AREA -> "Concentração local"
}

private fun diagnosticValue(marker: DiagnosticMarker): String = when (marker.kind) {
    DiagnosticKind.LONG_STITCH, DiagnosticKind.LONG_JUMP -> "${"%.1f".format(marker.value)} mm"
    DiagnosticKind.DENSE_AREA -> "${marker.value.toInt()} pts / 5×5 mm"
}

private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
if marker not in text:
    raise SystemExit('AnalysisIssue marker not found')
text = text.replace(marker, addition, 1)

# Add visual diagnostic state and a focused marker to the viewer.
old = '''    var simulatorPosition by remember(design) { mutableIntStateOf(stitchIndices.size) }
    var simulatorPlaying by remember(design) { mutableStateOf(false) }
    var simulatorSpeed by remember(design) { mutableFloatStateOf(1f) }

    val visibleUntil = remember(simulatorPosition, stitchIndices) {'''
new = '''    var simulatorPosition by remember(design) { mutableIntStateOf(stitchIndices.size) }
    var simulatorPlaying by remember(design) { mutableStateOf(false) }
    var simulatorSpeed by remember(design) { mutableFloatStateOf(1f) }
    val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }
    var diagnosticsVisible by remember(design) { mutableStateOf(true) }
    var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }

    val visibleUntil = remember(simulatorPosition, stitchIndices) {'''
if old not in text:
    raise SystemExit('Viewer simulator state marker not found')
text = text.replace(old, new, 1)

# When the user pans manually, release the automatic diagnostic focus.
old = '''    val transform = rememberTransformableState { z, p, _ ->
        zoom = (zoom * z).coerceIn(.25f, 20f)
        pan += p
    }'''
new = '''    val transform = rememberTransformableState { z, p, _ ->
        zoom = (zoom * z).coerceIn(.25f, 20f)
        pan += p
        if (p != Offset.Zero) focusMarker = null
    }'''
if old not in text:
    raise SystemExit('Viewer transform marker not found')
text = text.replace(old, new, 1)

# Add a compact visual-diagnostics toggle next to the existing Costs shortcut.
old = '''            ExpressiveIconButton(Icons.Rounded.Calculate, "Custos", onCosts)
            Spacer(Modifier.width(7.dp))
            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)'''
new = '''            ExpressiveIconButton(Icons.Rounded.Calculate, "Custos", onCosts)
            Spacer(Modifier.width(7.dp))
            ExpressiveIconButton(
                if (diagnosticsVisible) Icons.Rounded.WarningAmber else Icons.Rounded.VisibilityOff,
                if (diagnosticsVisible) "Ocultar diagnóstico visual" else "Mostrar diagnóstico visual"
            ) {
                diagnosticsVisible = !diagnosticsVisible
                if (!diagnosticsVisible) focusMarker = null
            }
            Spacer(Modifier.width(7.dp))
            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)'''
if old not in text:
    raise SystemExit('Viewer header shortcut marker not found')
text = text.replace(old, new, 1)

# Wire Analyzer occurrences to the viewer focus engine.
old = '''        DesignAnalyzerPanel(design, machineConfig)
        Box('''
new = '''        DesignAnalyzerPanel(
            design = design,
            config = machineConfig,
            diagnostics = visualDiagnostics,
            onFocus = { marker ->
                diagnosticsVisible = true
                simulatorPlaying = false
                simulatorPosition = stitchIndices.size
                focusMarker = marker
                zoom = 3.2f
                pan = Offset.Zero
            }
        )
        Box('''
if old not in text:
    raise SystemExit('Analyzer viewer call marker not found')
text = text.replace(old, new, 1)

# Pass diagnostics into the canvas and clear automatic focus on reset.
old = '''            StitchCanvas(design, zoom, pan, grid, Modifier.fillMaxSize(), visibleUntil = visibleUntil)'''
new = '''            StitchCanvas(
                design = design,
                zoom = zoom,
                pan = pan,
                grid = grid,
                modifier = Modifier.fillMaxSize(),
                visibleUntil = visibleUntil,
                diagnostics = if (diagnosticsVisible) visualDiagnostics else emptyList(),
                focusMarker = focusMarker
            )'''
if old not in text:
    raise SystemExit('StitchCanvas viewer call not found')
text = text.replace(old, new, 1)

old = '''                detectTapGestures(onDoubleTap = { zoom = 1f; pan = Offset.Zero })'''
new = '''                detectTapGestures(onDoubleTap = { zoom = 1f; pan = Offset.Zero; focusMarker = null })'''
if old not in text:
    raise SystemExit('Viewer double-tap marker not found')
text = text.replace(old, new, 1)

# Extend Analyzer with tappable occurrences that focus the exact geometric region.
old = '''private fun DesignAnalyzerPanel(design: Design, config: MachineConfig) {
    val analysis = remember(design, config) { analyzeDesign(design, config) }'''
new = '''private fun DesignAnalyzerPanel(
    design: Design,
    config: MachineConfig,
    diagnostics: List<DiagnosticMarker>,
    onFocus: (DiagnosticMarker) -> Unit
) {
    val analysis = remember(design, config) { analyzeDesign(design, config) }'''
if old not in text:
    raise SystemExit('DesignAnalyzerPanel signature marker not found')
text = text.replace(old, new, 1)

old = '''                    Text(
                        if (analysis.issues.isEmpty()) "Nenhum alerta geométrico relevante" else "${analysis.issues.size} alerta${if (analysis.issues.size == 1) "" else "s"} encontrado${if (analysis.issues.size == 1) "" else "s"}",
                        color = Muted,
                        fontSize = 8.sp
                    )'''
new = '''                    Text(
                        if (analysis.issues.isEmpty()) "Nenhum alerta geométrico relevante"
                        else "${analysis.issues.size} alerta${if (analysis.issues.size == 1) "" else "s"} • ${diagnostics.size} marcação${if (diagnostics.size == 1) "" else "ões"} visual${if (diagnostics.size == 1) "" else "is"}",
                        color = Muted,
                        fontSize = 8.sp
                    )'''
if old not in text:
    raise SystemExit('Analyzer subtitle marker not found')
text = text.replace(old, new, 1)

old = '''                Text(
                    "Analyzer v1 usa geometria das pontadas. A concentração local é uma aproximação e não substitui análise de objetos, compensação, entretela ou teste físico.",
                    color = Muted,
                    fontSize = 8.sp,
                    lineHeight = 11.sp
                )'''
new = '''                if (diagnostics.isNotEmpty()) {
                    Text("Ocorrências no desenho", color = Gold, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                    diagnostics.take(6).forEach { marker ->
                        Surface(
                            modifier = Modifier.fillMaxWidth().clickable { onFocus(marker) },
                            shape = RoundedCornerShape(15.dp),
                            color = Gold.copy(alpha = .08f),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = if (marker.severity >= 3) .58f else .34f))
                        ) {
                            Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    when (marker.kind) {
                                        DiagnosticKind.LONG_STITCH -> Icons.Rounded.Timeline
                                        DiagnosticKind.LONG_JUMP -> Icons.Rounded.SwapHoriz
                                        DiagnosticKind.DENSE_AREA -> Icons.Rounded.BlurOn
                                    },
                                    null,
                                    tint = Gold,
                                    modifier = Modifier.size(17.dp)
                                )
                                Spacer(Modifier.width(8.dp))
                                Column(Modifier.weight(1f)) {
                                    Text(diagnosticTitle(marker), color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                                    Text(diagnosticValue(marker), color = Muted, fontSize = 8.sp)
                                }
                                Icon(Icons.Rounded.CenterFocusStrong, "Localizar", tint = Gold, modifier = Modifier.size(18.dp))
                            }
                        }
                    }
                    if (diagnostics.size > 6) {
                        Text("+ ${diagnostics.size - 6} ocorrência${if (diagnostics.size - 6 == 1) "" else "s"} adicional${if (diagnostics.size - 6 == 1) "" else "is"} marcada${if (diagnostics.size - 6 == 1) "" else "s"} no desenho.", color = Muted, fontSize = 8.sp)
                    }
                }
                Text(
                    "Analyzer v1 usa geometria das pontadas. A concentração local é uma aproximação e não substitui análise de objetos, compensação, entretela ou teste físico.",
                    color = Muted,
                    fontSize = 8.sp,
                    lineHeight = 11.sp
                )'''
if old not in text:
    raise SystemExit('Analyzer disclaimer marker not found')
text = text.replace(old, new, 1)

# Extend the stitch canvas with line/area overlays and exact focus centering.
old = '''private fun StitchCanvas(design: Design, zoom: Float, pan: Offset, grid: Boolean, modifier: Modifier, visibleUntil: Int = design.stitches.size) {'''
new = '''private fun StitchCanvas(
    design: Design,
    zoom: Float,
    pan: Offset,
    grid: Boolean,
    modifier: Modifier,
    visibleUntil: Int = design.stitches.size,
    diagnostics: List<DiagnosticMarker> = emptyList(),
    focusMarker: DiagnosticMarker? = null
) {'''
if old not in text:
    raise SystemExit('StitchCanvas signature marker not found')
text = text.replace(old, new, 1)

old = '''        val px = fit * zoom
        val center = Offset(size.width/2 + pan.x, size.height/2 + pan.y)
        val cx=(design.minX+design.maxX)/2
        val cy=(design.minY+design.maxY)/2
        fun map(x:Float,y:Float)=Offset(center.x+(x-cx)*px, center.y+(y-cy)*px)'''
new = '''        val px = fit * zoom
        val cx=(design.minX+design.maxX)/2
        val cy=(design.minY+design.maxY)/2
        val focusShift = focusMarker?.let { marker -> Offset((marker.x-cx)*px, (marker.y-cy)*px) } ?: Offset.Zero
        val center = Offset(size.width/2 + pan.x - focusShift.x, size.height/2 + pan.y - focusShift.y)
        fun map(x:Float,y:Float)=Offset(center.x+(x-cx)*px, center.y+(y-cy)*px)'''
if old not in text:
    raise SystemExit('StitchCanvas mapping marker not found')
text = text.replace(old, new, 1)

old = '''        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }
    }
}'''
new = '''        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }

        diagnostics.forEach { marker ->
            val point = map(marker.x, marker.y)
            val sx = marker.startX
            val sy = marker.startY
            val ex = marker.endX
            val ey = marker.endY
            when (marker.kind) {
                DiagnosticKind.LONG_STITCH -> {
                    if (sx != null && sy != null && ex != null && ey != null) {
                        drawLine(Cream.copy(alpha = .88f), map(sx, sy), map(ex, ey), strokeWidth = 2.2f, cap = StrokeCap.Round)
                    }
                    drawCircle(Gold.copy(alpha = .24f), radius = 9f, center = point)
                    drawCircle(Gold, radius = 9f, center = point, style = Stroke(1.7f))
                }
                DiagnosticKind.LONG_JUMP -> {
                    if (sx != null && sy != null && ex != null && ey != null) {
                        drawLine(Gold.copy(alpha = .92f), map(sx, sy), map(ex, ey), strokeWidth = 2.4f, cap = StrokeCap.Round)
                    }
                    drawCircle(GoldDeep.copy(alpha = .30f), radius = 10f, center = point)
                    drawCircle(GoldDeep, radius = 10f, center = point, style = Stroke(1.8f))
                }
                DiagnosticKind.DENSE_AREA -> {
                    val radius = (10f + (marker.value.toFloat() / 60f)).coerceIn(11f, 18f)
                    drawCircle(GoldDeep.copy(alpha = .20f), radius = radius, center = point)
                    drawCircle(Gold, radius = radius, center = point, style = Stroke(2f))
                }
            }
        }

        focusMarker?.let { marker ->
            val point = map(marker.x, marker.y)
            drawCircle(Cream.copy(alpha = .18f), radius = 25f, center = point)
            drawCircle(Cream, radius = 25f, center = point, style = Stroke(2.6f))
            drawCircle(Gold, radius = 4.5f, center = point)
        }
    }
}'''
if old not in text:
    raise SystemExit('StitchCanvas paths marker not found')
text = text.replace(old, new, 1)

# Refresh chained version labels.
text = text.replace('0.2.13', '0.2.14')

path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.14 visual diagnostics patch applied successfully')
