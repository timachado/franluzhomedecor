from pathlib import Path
import runpy

# Reconstruct the last validated 0.2.30 source first.
runpy.run_path('.github/scripts/patch_bordatto_054.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# LETTERING: restore sliders and make preview respond while dragging.
# -----------------------------------------------------------------------------
helper_anchor = '@Composable\nprivate fun LetteringSimpleScreen030'
helper = r'''@Composable
private fun LetteringSliderControl031(
    title: String,
    valueLabel: String,
    value: Float,
    valueRange: ClosedFloatingPointRange<Float>,
    onValueChange: (Float) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = CardBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
    ) {
        Column(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 9.dp)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(title, color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                Text(valueLabel, color = Gold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(3.dp))
            BordattoParameterSlider(value, onValueChange, valueRange)
        }
    }
}

'''
if helper_anchor not in text:
    raise SystemExit('0.2.31 lettering helper anchor not found')
text = text.replace(helper_anchor, helper + helper_anchor, 1)

# Work only inside the casual Lettering screen so the legacy professional screen is preserved.
ls = text.index('@Composable\nprivate fun LetteringSimpleScreen030')
le = text.index('@Composable\nprivate fun MachineScreen', ls)
letter = text[ls:le]

preview_old = '''                        fontSize = 44.sp,
                        fontFamily = when (font) {'''
preview_new = '''                        fontSize = (size * .74f).coerceIn(18f, 66f).sp,
                        letterSpacing = (spacing / 7f).coerceIn(-2.5f, 6f).sp,
                        fontFamily = when (font) {'''
if preview_old not in letter:
    raise SystemExit('0.2.31 main live preview anchor not found')
letter = letter.replace(preview_old, preview_new, 1)

height_old = '''        item {
            LetteringStepper030(
                title = "Altura do nome",
                value = "${"%.0f".format(size)} mm",
                onMinus = { size = (size - 2f).coerceAtLeast(10f) },
                onPlus = { size = (size + 2f).coerceAtMost(90f) }
            )
        }
'''
height_new = '''        item {
            LetteringSliderControl031(
                title = "Altura do nome",
                valueLabel = "${"%.0f".format(size)} mm",
                value = size,
                valueRange = 10f..90f,
                onValueChange = { size = it }
            )
        }
'''
if height_old not in letter:
    raise SystemExit('0.2.31 height slider anchor not found')
letter = letter.replace(height_old, height_new, 1)

spacing_old = '''        item {
            Text("Espaçamento", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
            Spacer(Modifier.height(7.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                listOf("Compacto" to -8f, "Normal" to 0f, "Aberto" to 16f).forEach { (label, value) ->
                    val selected = kotlin.math.abs(spacing - value) < .5f
                    Surface(
                        modifier = Modifier.weight(1f).height(46.dp).clickable { spacing = value },
                        shape = RoundedCornerShape(14.dp),
                        color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(
                            1.dp,
                            if (selected) Gold.copy(alpha = .70f) else LineGold.copy(alpha = .35f)
                        )
                    ) {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text(
                                label,
                                color = if (selected) Gold else Cream,
                                fontSize = 9.sp,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    }
                }
            }
        }
'''
spacing_new = '''        item {
            LetteringSliderControl031(
                title = "Espaçamento",
                valueLabel = "${"%.0f".format(spacing)}%",
                value = spacing,
                valueRange = -18f..40f,
                onValueChange = { spacing = it }
            )
        }
'''
if spacing_old not in letter:
    raise SystemExit('0.2.31 spacing slider anchor not found')
letter = letter.replace(spacing_old, spacing_new, 1)

advanced_old = '''                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    LetteringStepper030(
                        "Densidade Satin",
                        "${"%.2f".format(density)} mm",
                        { density = (density - .02f).coerceAtLeast(.28f) },
                        { density = (density + .02f).coerceAtMost(1f) }
                    )
                    LetteringStepper030(
                        "Compensação de puxamento",
                        "${"%.2f".format(pullComp)} mm",
                        { pullComp = (pullComp - .05f).coerceAtLeast(0f) },
                        { pullComp = (pullComp + .05f).coerceAtMost(1f) }
                    )
                    LetteringStepper030(
                        "Largura máxima Satin",
                        "${"%.1f".format(satinMax)} mm",
                        { satinMax = (satinMax - .5f).coerceAtLeast(4f) },
                        { satinMax = (satinMax + .5f).coerceAtMost(14f) }
                    )
                }'''
advanced_new = '''                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    LetteringSliderControl031(
                        "Densidade Satin",
                        "${"%.2f".format(density)} mm",
                        density,
                        .28f..1.0f,
                        { density = it }
                    )
                    LetteringSliderControl031(
                        "Compensação de puxamento",
                        "${"%.2f".format(pullComp)} mm",
                        pullComp,
                        0f..1.0f,
                        { pullComp = it }
                    )
                    LetteringSliderControl031(
                        "Largura máxima Satin",
                        "${"%.1f".format(satinMax)} mm",
                        satinMax,
                        4f..14f,
                        { satinMax = it }
                    )
                }'''
if advanced_old not in letter:
    raise SystemExit('0.2.31 advanced sliders anchor not found')
letter = letter.replace(advanced_old, advanced_new, 1)

font_heading = '        item { Text("Escolha a fonte", color = Cream, fontWeight = FontWeight.SemiBold) }'
live_caption = '''        item {
            Text(
                "Prévia em tempo real • ${"%.0f".format(size)} mm • espaçamento ${"%.0f".format(spacing)}%",
                color = Muted,
                fontSize = 8.sp,
                modifier = Modifier.fillMaxWidth()
            )
        }

        item { Text("Escolha a fonte", color = Cream, fontWeight = FontWeight.SemiBold) }'''
if font_heading not in letter:
    raise SystemExit('0.2.31 live caption anchor not found')
letter = letter.replace(font_heading, live_caption, 1)

text = text[:ls] + letter + text[le:]

# -----------------------------------------------------------------------------
# VIEWER: make the circled eye a real show/hide matrix control.
# -----------------------------------------------------------------------------
viewer_start = text.index('@Composable\nprivate fun ViewerScreen')
viewer_end = text.index('\nprivate enum class DiagnosticKind', viewer_start)
viewer = text[viewer_start:viewer_end]

state_old = '''    val visualDiagnostics = remember(workingDesign) { collectDiagnosticMarkers(workingDesign) }
    var diagnosticsVisible by remember(workingDesign) { mutableStateOf(true) }
    var focusMarker by remember(workingDesign) { mutableStateOf<DiagnosticMarker?>(null) }'''
state_new = '''    val visualDiagnostics = remember(workingDesign) { collectDiagnosticMarkers(workingDesign) }
    var diagnosticsVisible by remember(workingDesign) { mutableStateOf(true) }
    var focusMarker by remember(workingDesign) { mutableStateOf<DiagnosticMarker?>(null) }
    var stitchesVisible031 by remember(workingDesign) { mutableStateOf(true) }'''
if state_old not in viewer:
    raise SystemExit('0.2.31 Viewer state anchor not found')
viewer = viewer.replace(state_old, state_new, 1)

eye_old = '            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)'
eye_new = '''            ExpressiveIconButton(
                if (stitchesVisible031) Icons.Rounded.Visibility else Icons.Rounded.VisibilityOff,
                if (stitchesVisible031) "Ocultar matriz" else "Mostrar matriz"
            ) {
                stitchesVisible031 = !stitchesVisible031
                if (!stitchesVisible031) {
                    focusMarker = null
                    selectedDiagnostic = null
                    assistedPreview = null
                }
            }'''
if eye_old not in viewer:
    raise SystemExit('0.2.31 static eye anchor not found')
viewer = viewer.replace(eye_old, eye_new, 1)

canvas_old = '''                visibleUntil = if (sequencePreviewDesign != null) (sequencePreviewDesign?.stitches?.size ?: visibleUntil) else visibleUntil,
                diagnostics = if (diagnosticsVisible) activeDiagnostics else emptyList(),
                focusMarker = focusMarker,
                correctionPreview = if (diagnosticsVisible) assistedPreview else null,'''
canvas_new = '''                visibleUntil = if (stitchesVisible031) {
                    if (sequencePreviewDesign != null) (sequencePreviewDesign?.stitches?.size ?: visibleUntil) else visibleUntil
                } else 0,
                diagnostics = if (stitchesVisible031 && diagnosticsVisible) activeDiagnostics else emptyList(),
                focusMarker = if (stitchesVisible031) focusMarker else null,
                correctionPreview = if (stitchesVisible031 && diagnosticsVisible) assistedPreview else null,'''
if canvas_old not in viewer:
    raise SystemExit('0.2.31 StitchCanvas call anchor not found')
viewer = viewer.replace(canvas_old, canvas_new, 1)

text = text[:viewer_start] + viewer + text[viewer_end:]

# -----------------------------------------------------------------------------
# ANALYZER: preserve expand/collapse, but add obvious real actions.
# -----------------------------------------------------------------------------
a_start = text.index('@Composable\nprivate fun DesignAnalyzerPanel')
a_end = text.index('@Composable\nprivate fun AnalyzerMetric', a_start)
analyzer = text[a_start:a_end]

outer_old = '        modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded },'
outer_new = '        modifier = Modifier.fillMaxWidth(),'
if outer_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer outer click anchor not found')
analyzer = analyzer.replace(outer_old, outer_new, 1)

header_old = '            Row(verticalAlignment = Alignment.CenterVertically) {'
header_new = '''            Row(
                Modifier.fillMaxWidth().clickable { expanded = !expanded },
                verticalAlignment = Alignment.CenterVertically
            ) {'''
if header_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer header anchor not found')
analyzer = analyzer.replace(header_old, header_new, 1)

metrics_old = '''            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                AnalyzerMetric("Ponto máx.", "${"%.1f".format(analysis.maxStitchMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Salto máx.", "${"%.1f".format(analysis.maxJumpMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Pico 5×5", "${analysis.peakCellStitches}", Modifier.weight(1f))
                AnalyzerMetric("Trocas", "${analysis.colorChanges}", Modifier.weight(1f))
            }

            if (expanded) {'''
metrics_new = '''            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                AnalyzerMetric("Ponto máx.", "${"%.1f".format(analysis.maxStitchMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Salto máx.", "${"%.1f".format(analysis.maxJumpMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Pico 5×5", "${analysis.peakCellStitches}", Modifier.weight(1f))
                AnalyzerMetric("Trocas", "${analysis.colorChanges}", Modifier.weight(1f))
            }

            if (diagnostics.isNotEmpty()) {
                Button(
                    onClick = {
                        expanded = true
                        onFocus(diagnostics.first())
                    },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 46.dp),
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                ) {
                    Icon(Icons.Rounded.CenterFocusStrong, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(7.dp))
                    Text("ANALISAR E LOCALIZAR ALERTA", fontSize = 9.sp, fontWeight = FontWeight.Bold)
                }
            }

            if (expanded) {'''
if metrics_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer action insertion anchor not found')
analyzer = analyzer.replace(metrics_old, metrics_new, 1)

locate_old = '                                Icon(Icons.Rounded.CenterFocusStrong, "Localizar", tint = Gold, modifier = Modifier.size(18.dp))'
locate_new = '''                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("VER NO DESENHO", color = Gold, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                                    Spacer(Modifier.width(5.dp))
                                    Icon(Icons.Rounded.CenterFocusStrong, "Localizar", tint = Gold, modifier = Modifier.size(18.dp))
                                }'''
if locate_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer occurrence action anchor not found')
analyzer = analyzer.replace(locate_old, locate_new, 1)

old_guidance = '"Analyzer v1 usa geometria das pontadas. A concentração local é uma aproximação e não substitui análise de objetos, compensação, entretela ou teste físico."'
new_guidance = '"Toque em VER NO DESENHO para centralizar a ocorrência na matriz. A análise usa a geometria real das pontadas; teste físico continua recomendado."'
if old_guidance not in analyzer:
    raise SystemExit('0.2.31 Analyzer guidance anchor not found')
analyzer = analyzer.replace(old_guidance, new_guidance, 1)

text = text[:a_start] + analyzer + text[a_end:]

# Update displayed version without touching historical comments/identifiers.
text = text.replace('Text("0.2.30", color = Gold, fontSize = 9.sp, fontWeight = FontWeight.Bold)',
                    'Text("0.2.31", color = Gold, fontSize = 9.sp, fontWeight = FontWeight.Bold)', 1)
main_path.write_text(text, encoding='utf-8')

# Version + reproducible compile SDK available on current runner.
gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
if 'compileSdk = 37' not in gradle:
    raise SystemExit('0.2.31 compileSdk anchor not found')
gradle = gradle.replace('compileSdk = 37', 'compileSdk = 36', 1)
gradle = gradle.replace('versionCode = 32', 'versionCode = 33', 1)
gradle = gradle.replace('versionName = "0.2.30"', 'versionName = "0.2.31"', 1)
gradle_path.write_text(gradle, encoding='utf-8')

# Exact user-facing regression guards.
required = [
    'private fun LetteringSliderControl031(',
    'fontSize = (size * .74f).coerceIn(18f, 66f).sp',
    'letterSpacing = (spacing / 7f).coerceIn(-2.5f, 6f).sp',
    'valueRange = 10f..90f',
    'valueRange = -18f..40f',
    'var stitchesVisible031 by remember(workingDesign)',
    '"Ocultar matriz" else "Mostrar matriz"',
    'visibleUntil = if (stitchesVisible031)',
    'diagnostics = if (stitchesVisible031 && diagnosticsVisible) activeDiagnostics else emptyList()',
    'Text("ANALISAR E LOCALIZAR ALERTA"',
    'Text("VER NO DESENHO"',
    'MachineCheckPanel(',
    'SafeEditorPanel(',
    'EmbroiderySimulatorPanel(',
    'data class MachineConfig',
    'data class LibraryItem',
    'fun CostCalculatorScreen'
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.31 regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.31 live sliders + functional eye + actionable Analyzer applied successfully')
