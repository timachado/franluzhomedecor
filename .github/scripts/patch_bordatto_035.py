from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_034.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Non-destructive assisted-correction previews. These never mutate Design or the source file.
marker = '''private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
addition = r'''private enum class AssistedCorrectionKind { CUT_SUGGESTION, SPLIT_SUGGESTION }

private data class AssistedCorrectionPreview(
    val kind: AssistedCorrectionKind,
    val source: DiagnosticMarker,
    val points: List<Offset>,
    val detail: String
)

private fun buildAssistedCorrectionPreview(marker: DiagnosticMarker): AssistedCorrectionPreview? {
    return when (marker.kind) {
        DiagnosticKind.LONG_JUMP -> {
            val sx = marker.startX
            val sy = marker.startY
            if (sx == null || sy == null) null else AssistedCorrectionPreview(
                kind = AssistedCorrectionKind.CUT_SUGGESTION,
                source = marker,
                points = listOf(Offset(sx, sy)),
                detail = "Prévia de corte antes do salto de ${"%.1f".format(marker.value)} mm. O arquivo original não foi alterado."
            )
        }
        DiagnosticKind.LONG_STITCH -> {
            val sx = marker.startX
            val sy = marker.startY
            val ex = marker.endX
            val ey = marker.endY
            if (sx == null || sy == null || ex == null || ey == null) null else {
                val segments = kotlin.math.ceil(marker.value / 8.0).toInt().coerceAtLeast(2)
                val points = (1 until segments).map { i ->
                    val t = i.toFloat() / segments.toFloat()
                    Offset(sx + (ex - sx) * t, sy + (ey - sy) * t)
                }
                AssistedCorrectionPreview(
                    kind = AssistedCorrectionKind.SPLIT_SUGGESTION,
                    source = marker,
                    points = points,
                    detail = "Sugestão: dividir em $segments segmentos de aproximadamente ${"%.1f".format(marker.value / segments)} mm. É apenas uma prévia; a matriz continua intacta."
                )
            }
        }
        DiagnosticKind.DENSE_AREA -> null
    }
}

private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
if marker not in text:
    raise SystemExit('AnalysisIssue insertion marker not found')
text = text.replace(marker, addition, 1)

# Keep selection, ignored occurrences and preview state local to the open design/session.
old = '''    val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }
    var diagnosticsVisible by remember(design) { mutableStateOf(true) }
    var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }

    val visibleUntil = remember(simulatorPosition, stitchIndices) {'''
new = '''    val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }
    var diagnosticsVisible by remember(design) { mutableStateOf(true) }
    var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }
    var selectedDiagnostic by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }
    var ignoredDiagnostics by remember(design) { mutableStateOf<Set<DiagnosticMarker>>(emptySet()) }
    var assistedPreview by remember(design) { mutableStateOf<AssistedCorrectionPreview?>(null) }
    val activeDiagnostics = remember(visualDiagnostics, ignoredDiagnostics) {
        visualDiagnostics.filterNot { it in ignoredDiagnostics }
    }

    val visibleUntil = remember(simulatorPosition, stitchIndices) {'''
if old not in text:
    raise SystemExit('Visual diagnostic viewer state marker not found')
text = text.replace(old, new, 1)

# Hiding diagnostics also closes any active assisted-correction context.
old = '''                diagnosticsVisible = !diagnosticsVisible
                if (!diagnosticsVisible) focusMarker = null
            }'''
new = '''                diagnosticsVisible = !diagnosticsVisible
                if (!diagnosticsVisible) {
                    focusMarker = null
                    selectedDiagnostic = null
                    assistedPreview = null
                }
            }'''
if old not in text:
    raise SystemExit('Diagnostics toggle marker not found')
text = text.replace(old, new, 1)

# Selecting an Analyzer occurrence now opens an assisted-correction panel as well as focusing it.
old = '''            diagnostics = visualDiagnostics,
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
new = '''            diagnostics = activeDiagnostics,
            onFocus = { marker ->
                diagnosticsVisible = true
                simulatorPlaying = false
                simulatorPosition = stitchIndices.size
                focusMarker = marker
                selectedDiagnostic = marker
                assistedPreview = null
                zoom = 3.2f
                pan = Offset.Zero
            }
        )
        selectedDiagnostic?.let { marker ->
            AssistedCorrectionPanel(
                marker = marker,
                preview = assistedPreview?.takeIf { it.source == marker },
                onLocate = {
                    diagnosticsVisible = true
                    simulatorPlaying = false
                    simulatorPosition = stitchIndices.size
                    focusMarker = marker
                    zoom = 3.2f
                    pan = Offset.Zero
                },
                onIgnore = {
                    ignoredDiagnostics = ignoredDiagnostics + marker
                    if (focusMarker == marker) focusMarker = null
                    selectedDiagnostic = null
                    assistedPreview = null
                },
                onSuggest = {
                    assistedPreview = buildAssistedCorrectionPreview(marker)
                    diagnosticsVisible = true
                    simulatorPlaying = false
                    simulatorPosition = stitchIndices.size
                    focusMarker = marker
                    zoom = 3.2f
                    pan = Offset.Zero
                },
                onClearPreview = { assistedPreview = null },
                onClose = {
                    selectedDiagnostic = null
                    assistedPreview = null
                }
            )
        }
        Box('''
if old not in text:
    raise SystemExit('Analyzer focus wiring marker not found')
text = text.replace(old, new, 1)

# Canvas receives only active diagnostics plus an optional correction preview.
old = '''                visibleUntil = visibleUntil,
                diagnostics = if (diagnosticsVisible) visualDiagnostics else emptyList(),
                focusMarker = focusMarker
            )'''
new = '''                visibleUntil = visibleUntil,
                diagnostics = if (diagnosticsVisible) activeDiagnostics else emptyList(),
                focusMarker = focusMarker,
                correctionPreview = if (diagnosticsVisible) assistedPreview else null
            )'''
if old not in text:
    raise SystemExit('StitchCanvas diagnostics call marker not found')
text = text.replace(old, new, 1)

# Insert the contextual assisted-correction UI before the viewer tool controls.
insert_at = text.index('@Composable\nprivate fun ViewerTool')
correction_ui = r'''@Composable
private fun AssistedCorrectionPanel(
    marker: DiagnosticMarker,
    preview: AssistedCorrectionPreview?,
    onLocate: () -> Unit,
    onIgnore: () -> Unit,
    onSuggest: () -> Unit,
    onClearPreview: () -> Unit,
    onClose: () -> Unit
) {
    Surface(
        color = SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .52f))
    ) {
        Column(
            Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 11.dp),
            verticalArrangement = Arrangement.spacedBy(9.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ExpressiveIconBadge(Icons.Rounded.BuildCircle, selected = true, size = 40.dp)
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text("Correção assistida", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                    Text("${diagnosticTitle(marker)} • ${diagnosticValue(marker)}", color = Muted, fontSize = 8.sp)
                }
                IconButton(onClick = onClose) {
                    Icon(Icons.Rounded.Close, "Fechar", tint = Muted)
                }
            }

            Text(
                when (marker.kind) {
                    DiagnosticKind.LONG_JUMP -> "O BORDATTO pode indicar onde um corte pode ser útil antes deste salto. A decisão final continua sendo do bordador."
                    DiagnosticKind.LONG_STITCH -> "O BORDATTO pode calcular pontos intermediários para manter cada trecho em até aproximadamente 8 mm."
                    DiagnosticKind.DENSE_AREA -> "Esta região exige revisão de densidade, tecido e estabilizador. Nesta etapa não há correção automática segura."
                },
                color = Muted,
                fontSize = 9.sp,
                lineHeight = 12.sp
            )

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                FilledTonalButton(
                    onClick = onLocate,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha = .14f), contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.CenterFocusStrong, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(5.dp))
                    Text("Localizar", fontSize = 9.sp)
                }
                FilledTonalButton(
                    onClick = onIgnore,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Muted)
                ) {
                    Icon(Icons.Rounded.VisibilityOff, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(5.dp))
                    Text("Ignorar sessão", fontSize = 9.sp)
                }
            }

            when (marker.kind) {
                DiagnosticKind.LONG_JUMP -> Button(
                    onClick = onSuggest,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(17.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                ) {
                    Icon(Icons.Rounded.ContentCut, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(7.dp))
                    Text("Sugerir corte", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
                DiagnosticKind.LONG_STITCH -> Button(
                    onClick = onSuggest,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(17.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                ) {
                    Icon(Icons.Rounded.CallSplit, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(7.dp))
                    Text("Sugerir divisão do ponto", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
                DiagnosticKind.DENSE_AREA -> Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Gold.copy(alpha = .08f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .38f))
                ) {
                    Row(Modifier.fillMaxWidth().padding(11.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Science, null, tint = Gold, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Revisão manual recomendada — sem alteração automática.", color = Muted, fontSize = 9.sp)
                    }
                }
            }

            if (preview != null) {
                Surface(
                    shape = RoundedCornerShape(17.dp),
                    color = Gold.copy(alpha = .11f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .48f))
                ) {
                    Column(Modifier.fillMaxWidth().padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.Preview, null, tint = Gold, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(7.dp))
                            Text("Prévia — original preservado", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 9.sp)
                        }
                        Text(preview.detail, color = Cream, fontSize = 9.sp, lineHeight = 12.sp)
                        TextButton(onClick = onClearPreview, contentPadding = PaddingValues(0.dp)) {
                            Text("Limpar prévia", color = Gold, fontSize = 9.sp)
                        }
                    }
                }
            }

            Text(
                "Nenhuma opção desta tela grava mudanças na matriz. O editor destrutivo e a exportação corrigida serão etapas posteriores.",
                color = Muted,
                fontSize = 8.sp,
                lineHeight = 11.sp
            )
        }
    }
}

'''
text = text[:insert_at] + correction_ui + text[insert_at:]

# Extend canvas API with a non-destructive assisted-correction preview overlay.
old = '''    diagnostics: List<DiagnosticMarker> = emptyList(),
    focusMarker: DiagnosticMarker? = null
) {'''
new = '''    diagnostics: List<DiagnosticMarker> = emptyList(),
    focusMarker: DiagnosticMarker? = null,
    correctionPreview: AssistedCorrectionPreview? = null
) {'''
if old not in text:
    raise SystemExit('StitchCanvas assisted preview signature marker not found')
text = text.replace(old, new, 1)

# Draw cut/split suggestions over the real geometry without changing stitches.
old = '''        focusMarker?.let { marker ->
            val point = map(marker.x, marker.y)
            drawCircle(Cream.copy(alpha = .18f), radius = 25f, center = point)
            drawCircle(Cream, radius = 25f, center = point, style = Stroke(2.6f))
            drawCircle(Gold, radius = 4.5f, center = point)
        }
    }
}'''
new = '''        correctionPreview?.let { preview ->
            when (preview.kind) {
                AssistedCorrectionKind.CUT_SUGGESTION -> {
                    preview.points.firstOrNull()?.let { designPoint ->
                        val point = map(designPoint.x, designPoint.y)
                        drawCircle(Gold.copy(alpha = .22f), radius = 17f, center = point)
                        drawCircle(Gold, radius = 17f, center = point, style = Stroke(2.4f))
                        drawLine(Cream, Offset(point.x - 8f, point.y - 8f), Offset(point.x + 8f, point.y + 8f), strokeWidth = 2.2f, cap = StrokeCap.Round)
                        drawLine(Cream, Offset(point.x - 8f, point.y + 8f), Offset(point.x + 8f, point.y - 8f), strokeWidth = 2.2f, cap = StrokeCap.Round)
                    }
                }
                AssistedCorrectionKind.SPLIT_SUGGESTION -> {
                    preview.points.forEach { designPoint ->
                        val point = map(designPoint.x, designPoint.y)
                        drawCircle(Gold.copy(alpha = .24f), radius = 9f, center = point)
                        drawCircle(Cream, radius = 6f, center = point, style = Stroke(2f))
                        drawCircle(Gold, radius = 2.8f, center = point)
                    }
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
    raise SystemExit('StitchCanvas correction overlay insertion marker not found')
text = text.replace(old, new, 1)

text = text.replace('0.2.14', '0.2.15')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.15 assisted corrections patch applied successfully')
