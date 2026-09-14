from pathlib import Path
import runpy

# Build on the validated 0.2.30 APK source.
runpy.run_path('.github/scripts/patch_bordatto_054.py', run_name='__main__')

path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# 0.2.31 LETTERING — restore drag sliders and make the preview react live.
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
            BordattoParameterSlider(
                value = value,
                onValueChange = onValueChange,
                valueRange = valueRange
            )
        }
    }
}

'''
if helper_anchor not in text:
    raise SystemExit('0.2.31 lettering helper anchor not found')
text = text.replace(helper_anchor, helper + helper_anchor, 1)

# Main cream preview now follows height + spacing immediately while dragging.
preview_old = '''                        fontSize = 44.sp,
                        fontFamily = when (font) {'''
preview_new = '''                        fontSize = (size * .74f).coerceIn(18f, 66f).sp,
                        letterSpacing = (spacing / 7f).coerceIn(-2.5f, 6f).sp,
                        fontFamily = when (font) {'''
if preview_old not in text:
    raise SystemExit('0.2.31 live preview font anchor not found')
text = text.replace(preview_old, preview_new, 1)

# Restore the former bar interaction for height.
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
if height_old not in text:
    raise SystemExit('0.2.31 height stepper anchor not found')
text = text.replace(height_old, height_new, 1)

# Restore continuous spacing bar instead of three preset cards.
spacing_start = text.index('''        item {
            Text("Espaçamento", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)''')
spacing_end_anchor = '''        item {
            Surface(
                modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).clickable { advanced = !advanced },'''
spacing_end = text.index(spacing_end_anchor, spacing_start)
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
text = text[:spacing_start] + spacing_new + text[spacing_end:]

# Restore bars for professional parameters too.
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
if advanced_old not in text:
    raise SystemExit('0.2.31 professional steppers anchor not found')
text = text.replace(advanced_old, advanced_new, 1)

# Add a clear live-preview caption right after the cream card.
card_tail = '''            }
        }

        item { Text("Escolha a fonte", color = Cream, fontWeight = FontWeight.SemiBold) }'''
card_tail_new = '''            }
        }
        item {
            Text(
                "Prévia em tempo real • ${"%.0f".format(size)} mm • espaçamento ${"%.0f".format(spacing)}%",
                color = Muted,
                fontSize = 8.sp,
                modifier = Modifier.fillMaxWidth()
            )
        }

        item { Text("Escolha a fonte", color = Cream, fontWeight = FontWeight.SemiBold) }'''
# Constrain this replacement to the simple lettering function only.
ls = text.index('@Composable\nprivate fun LetteringSimpleScreen030')
le = text.index('@Composable\nprivate fun MachineScreen', ls)
letter = text[ls:le]
if card_tail not in letter:
    raise SystemExit('0.2.31 live preview caption anchor not found')
letter = letter.replace(card_tail, card_tail_new, 1)
text = text[:ls] + letter + text[le:]

# -----------------------------------------------------------------------------
# 0.2.31 VIEWER — the circled eye is now a real matrix visibility button.
# -----------------------------------------------------------------------------
viewer_start = text.index('@Composable\nprivate fun ViewerScreen')
viewer_end = text.index('\nprivate enum class DiagnosticKind', viewer_start)
viewer = text[viewer_start:viewer_end]

state_old = '''    val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }
    var diagnosticsVisible by remember(design) { mutableStateOf(true) }
    var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }'''
state_new = '''    val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }
    var diagnosticsVisible by remember(design) { mutableStateOf(true) }
    var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }
    var stitchesVisible031 by remember(design) { mutableStateOf(true) }'''
if state_old not in viewer:
    raise SystemExit('0.2.31 viewer visibility state anchor not found')
viewer = viewer.replace(state_old, state_new, 1)

eye_old = '            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)'
eye_new = '''            ExpressiveIconButton(
                if (stitchesVisible031) Icons.Rounded.Visibility else Icons.Rounded.VisibilityOff,
                if (stitchesVisible031) "Ocultar matriz" else "Mostrar matriz"
            ) {
                stitchesVisible031 = !stitchesVisible031
                if (!stitchesVisible031) focusMarker = null
            }'''
if eye_old not in viewer:
    raise SystemExit('0.2.31 static eye badge anchor not found')
viewer = viewer.replace(eye_old, eye_new, 1)

visible_old = '''                visibleUntil = visibleUntil,
                diagnostics = if (diagnosticsVisible) visualDiagnostics else emptyList(),'''
visible_new = '''                visibleUntil = if (stitchesVisible031) visibleUntil else 0,
                diagnostics = if (stitchesVisible031 && diagnosticsVisible) visualDiagnostics else emptyList(),'''
if visible_old not in viewer:
    raise SystemExit('0.2.31 StitchCanvas visibility anchor not found')
viewer = viewer.replace(visible_old, visible_new, 1)

text = text[:viewer_start] + viewer + text[viewer_end:]

# -----------------------------------------------------------------------------
# 0.2.31 ANALYZER — explicit functional action, not only expand/collapse.
# -----------------------------------------------------------------------------
a_start = text.index('@Composable\nprivate fun DesignAnalyzerPanel')
a_end = text.index('@Composable\nprivate fun AnalyzerMetric', a_start)
analyzer = text[a_start:a_end]

# Keep expansion on the header row only so child actions receive taps reliably.
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
    raise SystemExit('0.2.31 Analyzer header row anchor not found')
analyzer = analyzer.replace(header_old, header_new, 1)

metrics_anchor = '''            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
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
if metrics_anchor not in analyzer:
    raise SystemExit('0.2.31 Analyzer metrics/action anchor not found')
analyzer = analyzer.replace(metrics_anchor, metrics_new, 1)

locate_old = '                                Icon(Icons.Rounded.CenterFocusStrong, "Localizar", tint = Gold, modifier = Modifier.size(18.dp))'
locate_new = '''                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("VER NO DESENHO", color = Gold, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                                    Spacer(Modifier.width(5.dp))
                                    Icon(Icons.Rounded.CenterFocusStrong, "Localizar", tint = Gold, modifier = Modifier.size(18.dp))
                                }'''
if locate_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer occurrence CTA anchor not found')
analyzer = analyzer.replace(locate_old, locate_new, 1)

# Make the Analyzer purpose explicit in the expanded view.
disclaimer_old = '"Analyzer v1 usa geometria das pontadas. A concentração local é uma aproximação e não substitui análise de objetos, compensação, entretela ou teste físico."'
disclaimer_new = '"Toque em VER NO DESENHO para centralizar a ocorrência na matriz. A análise usa a geometria real das pontadas; teste físico continua recomendado."'
if disclaimer_old not in analyzer:
    raise SystemExit('0.2.31 Analyzer guidance anchor not found')
analyzer = analyzer.replace(disclaimer_old, disclaimer_new, 1)

text = text[:a_start] + analyzer + text[a_end:]

# Version bump.
text = text.replace('0.2.30', '0.2.31')
path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 32', 'versionCode = 33')
gradle = gradle.replace('versionName = "0.2.30"', 'versionName = "0.2.31"')
gradle_path.write_text(gradle, encoding='utf-8')

# Regression guards.
required = [
    'LetteringSliderControl031(',
    'letterSpacing = (spacing / 7f)',
    'stitchesVisible031',
    '"Ocultar matriz" else "Mostrar matriz"',
    '"ANALISAR E LOCALIZAR ALERTA"',
    '"VER NO DESENHO"',
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
