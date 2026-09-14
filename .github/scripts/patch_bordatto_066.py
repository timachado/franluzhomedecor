from pathlib import Path
import re
import runpy

runpy.run_path('.github/scripts/patch_bordatto_065.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

# 0.2.36: Paint.getTextPath may replace the destination Path. Accumulate each
# glyph into its own Path so Traditional lettering keeps the complete name.
old_glyph = '''    val glyphPath = android.graphics.Path()
    var cursorX = 0f
    val spacingFactor = (1f + options.spacingPercent / 100f).coerceIn(.72f, 1.65f)
    clean.forEach { ch ->
        val token = ch.toString()
        if (ch != ' ') paint.getTextPath(token, 0, token.length, cursorX, 0f, glyphPath)
        cursorX += paint.measureText(token).coerceAtLeast(paint.textSize * .18f) * spacingFactor
    }'''
new_glyph = '''    val glyphPath = android.graphics.Path()
    var cursorX = 0f
    val spacingFactor = (1f + options.spacingPercent / 100f).coerceIn(.72f, 1.65f)
    clean.forEach { ch ->
        val token = ch.toString()
        if (ch != ' ') {
            val charPath = android.graphics.Path()
            paint.getTextPath(token, 0, token.length, cursorX, 0f, charPath)
            glyphPath.addPath(charPath)
        }
        cursorX += paint.measureText(token).coerceAtLeast(paint.textSize * .18f) * spacingFactor
    }'''
if old_glyph not in text:
    raise SystemExit('0.2.36 complete-name glyph anchor not found')
text = text.replace(old_glyph, new_glyph, 1)


def balanced_block(source: str, signature: str):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit('Could not find balanced block: ' + signature)

# Add the reference-style first phase: a guide/run line traverses the complete
# lettering before the actual stitches begin to fill the name.
guide_overlay = r'''
@Composable
private fun TraditionalGuideOverlay036(
    design: Design,
    guideProgress: Float,
    accent: Color,
    keepGuide: Boolean,
    modifier: Modifier = Modifier
) {
    Canvas(modifier) {
        val canvasSize = this.size
        val pad = 42f
        val w = design.width.coerceAtLeast(1f)
        val h = design.height.coerceAtLeast(1f)
        val usableW = (canvasSize.width - pad * 2f).coerceAtLeast(1f)
        val usableH = (canvasSize.height - pad * 2f).coerceAtLeast(1f)
        val scale = minOf(usableW / w, usableH / h)
        val left = (canvasSize.width - w * scale) / 2f
        val right = left + w * scale
        val top = (canvasSize.height - h * scale) / 2f
        val centerY = top + h * scale * .52f
        val p = guideProgress.coerceIn(0f, 1f)
        val currentX = left + (right - left) * p
        if (p > 0f || keepGuide) {
            val endX = if (keepGuide) right else currentX
            drawLine(
                color = accent.copy(alpha = if (keepGuide) .25f else .92f),
                start = Offset(left, centerY),
                end = Offset(endX, centerY),
                strokeWidth = if (keepGuide) 1.4f else 2.2f,
                cap = StrokeCap.Round
            )
        }
        if (!keepGuide && p > 0f) {
            drawLine(Color(0x443C3B43), Offset(pad, centerY), Offset(canvasSize.width - pad, centerY), strokeWidth = 1f)
            drawLine(Color(0x443C3B43), Offset(currentX, pad), Offset(currentX, canvasSize.height - pad), strokeWidth = 1f)
            drawCircle(Color.White.copy(alpha = .92f), radius = 7.2f, center = Offset(currentX, centerY))
            drawCircle(accent, radius = 5.4f, center = Offset(currentX, centerY))
        }
    }
}
'''
insert_at = text.index('@Composable\nprivate fun TraditionalSimulatorScreen034')
text = text[:insert_at] + guide_overlay + '\n' + text[insert_at:]

sim_sig = '@Composable\nprivate fun TraditionalSimulatorScreen034'
ss, se = balanced_block(text, sim_sig)
new_sim = r'''@Composable
private fun TraditionalSimulatorScreen034(design: Design, onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var playing by remember { mutableStateOf(false) }
    var speed by remember { mutableFloatStateOf(1f) }
    var timeline by remember(design) { mutableIntStateOf(0) }

    // Reference flow: first the run/guide line is shown; only after it reaches
    // the end of the name does the actual embroidery sequence begin.
    val guideSteps = 52
    val sequenceTotal = design.stitches.size.coerceAtLeast(1)
    val timelineTotal = guideSteps + sequenceTotal
    val inGuide = timeline < guideSteps
    val guideProgress = (timeline.toFloat() / guideSteps.toFloat()).coerceIn(0f, 1f)
    val actualCurrent = (timeline - guideSteps).coerceIn(0, sequenceTotal)
    val progress = (timeline.toFloat() / timelineTotal.toFloat()).coerceIn(0f, 1f)
    val stitchTotal = design.stitchCount.coerceAtLeast(1)
    val completedPoints = remember(design, actualCurrent) {
        design.stitches.take(actualCurrent.coerceIn(0, design.stitches.size)).count { it.command == StitchCommand.STITCH }
    }
    val remainingPoints = (stitchTotal - completedPoints).coerceAtLeast(0)
    val guideRemainingSeconds = if (inGuide) kotlin.math.ceil((guideSteps - timeline) * .08 / speed.coerceAtLeast(1f)).toInt() else 0
    val remainingSeconds = guideRemainingSeconds + kotlin.math.ceil(remainingPoints / (750.0 * speed.coerceAtLeast(1f)) * 60.0).toInt()

    val activeStitch = remember(design, actualCurrent) {
        val end = actualCurrent.coerceIn(0, design.stitches.size)
        if (end > 0) design.stitches.take(end).lastOrNull { it.command == StitchCommand.STITCH }
        else design.stitches.firstOrNull { it.command == StitchCommand.STITCH }
    }
    val activeColor = activeStitch?.color
        ?: design.stitches.firstOrNull { it.command == StitchCommand.STITCH }?.color
        ?: 0xFFE91E63.toInt()
    val accent = Color(activeColor)
    val threadSequence = remember(design) {
        val ordered = mutableListOf<Int>()
        design.stitches.forEach { stitch ->
            if (stitch.command == StitchCommand.STITCH && ordered.lastOrNull() != stitch.color) ordered += stitch.color
        }
        ordered.ifEmpty { listOf(activeColor) }
    }
    val activeThread = threadSequence.indexOf(activeColor).let { if (it < 0) 0 else it }
    val matching = remember(activeColor) {
        TraditionalThreads034.minByOrNull { thread ->
            val r1 = (thread.color shr 16) and 0xFF
            val g1 = (thread.color shr 8) and 0xFF
            val b1 = thread.color and 0xFF
            val r2 = (activeColor shr 16) and 0xFF
            val g2 = (activeColor shr 8) and 0xFF
            val b2 = activeColor and 0xFF
            val dr = r1-r2; val dg = g1-g2; val db = b1-b2
            dr*dr + dg*dg + db*db
        } ?: TraditionalThreads034.first()
    }

    LaunchedEffect(playing, speed, timelineTotal) {
        while (playing && timeline < timelineTotal) {
            // 1x intentionally follows a realistic ~750 stitch/min visual pace.
            delay(80L)
            timeline = (timeline + speed.toInt().coerceAtLeast(1)).coerceAtMost(timelineTotal)
        }
        if (timeline >= timelineTotal) playing = false
    }

    val simBg = Color(0xFF0E0B15)
    val simCard = Color(0xFF1B1924)
    val simSoft = Color(0xFF25222E)
    val simMuted = Color(0xFFBBB6C2)

    Column(Modifier.fillMaxSize().background(simBg)) {
        Box(Modifier.fillMaxWidth().height(66.dp).background(simBg)) {
            IconButton(onClick = onBack, modifier = Modifier.align(Alignment.CenterStart).padding(start = 4.dp)) {
                Icon(Icons.Rounded.ArrowBack, "Voltar", tint = Cream)
            }
            Text("Simulação", color = Cream, fontSize = 15.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.align(Alignment.Center))
            Surface(modifier = Modifier.align(Alignment.CenterEnd).padding(end = 10.dp), shape = RoundedCornerShape(14.dp), color = simCard) {
                Row(Modifier.padding(4.dp), verticalAlignment = Alignment.CenterVertically) {
                    listOf(1f, 2f, 4f).forEach { value ->
                        val selected = kotlin.math.abs(speed - value) < .01f
                        Surface(modifier = Modifier.clickable { speed = value }, shape = RoundedCornerShape(10.dp), color = if (selected) accent else Color.Transparent) {
                            Text("${value.toInt()}×", color = if (selected) Color.White else simMuted, fontSize = 9.sp, fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium, modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp))
                        }
                    }
                }
            }
        }

        Box(Modifier.fillMaxWidth().weight(1f).background(Color(0xFFF0E8D8))) {
            TraditionalDesignCanvas034(
                design = design,
                displayMode = "Sólida",
                showGrid = true,
                showConnections = false,
                layerVisible = true,
                layerOpacity = 1f,
                visibleUntil = actualCurrent,
                ghostRemaining = true,
                modifier = Modifier.fillMaxSize()
            )
            TraditionalGuideOverlay036(
                design = design,
                guideProgress = guideProgress,
                accent = accent,
                keepGuide = !inGuide,
                modifier = Modifier.fillMaxSize()
            )
            if (!inGuide) {
                TraditionalSimulationNeedle035(design = design, current = actualCurrent, accent = accent, modifier = Modifier.fillMaxSize())
            }
            Surface(modifier = Modifier.align(Alignment.TopStart).padding(10.dp), shape = RoundedCornerShape(50), color = Color(0xFF403D43)) {
                Text("${"%.1f".format(progress * 100f)}%", color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
            }
            Surface(modifier = Modifier.align(Alignment.TopEnd).padding(10.dp), shape = RoundedCornerShape(50), color = Color(0xFF403D43)) {
                Text("${"%.0f".format(design.width)} × ${"%.0f".format(design.height)} mm", color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
            }
        }

        Column(Modifier.fillMaxWidth().background(simBg).padding(horizontal = 14.dp, vertical = 10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Surface(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), color = simCard, border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha=.06f))) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(44.dp).clip(CircleShape).background(accent).border(2.dp, Color.White.copy(alpha=.22f), CircleShape))
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text("${matching.name} • ${matching.brand} ${matching.code}", color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, maxLines = 1)
                        Box(Modifier.fillMaxWidth().height(4.dp).clip(RoundedCornerShape(50)).background(simSoft)) {
                            Box(Modifier.fillMaxWidth(progress).fillMaxHeight().background(accent))
                        }
                    }
                    Spacer(Modifier.width(10.dp))
                    Surface(shape = RoundedCornerShape(12.dp), color = simSoft) {
                        Text("Fio ${activeThread + 1} / ${threadSequence.size.coerceAtLeast(1)}", color = simMuted, fontSize = 8.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp))
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("$completedPoints / $stitchTotal pts", color = simMuted, fontSize = 9.sp, modifier = Modifier.weight(1f))
                Text("Restante: ${formatTraditionalRemaining035(remainingSeconds)}", color = simMuted, fontSize = 9.sp)
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Surface(shape = RoundedCornerShape(50), color = simCard, border = androidx.compose.foundation.BorderStroke(1.dp, accent.copy(alpha=.85f))) {
                    Row(Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(12.dp).clip(CircleShape).background(accent)); Spacer(Modifier.width(5.dp))
                        Text(matching.code, color = Cream, fontSize = 8.sp, fontWeight = FontWeight.SemiBold); Spacer(Modifier.width(3.dp))
                        Icon(Icons.Rounded.PlayArrow, null, tint = simMuted, modifier = Modifier.size(14.dp))
                    }
                }
            }

            Slider(
                value = timeline.toFloat(),
                onValueChange = { playing = false; timeline = it.toInt().coerceIn(0, timelineTotal) },
                valueRange = 0f..timelineTotal.toFloat(),
                modifier = Modifier.fillMaxWidth().height(32.dp),
                colors = SliderDefaults.colors(thumbColor = accent, activeTrackColor = accent, inactiveTrackColor = simSoft)
            )

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                Surface(modifier = Modifier.width(86.dp).height(58.dp).clickable {
                    timeline = (timeline - maxOf(1, timelineTotal / 10)).coerceAtLeast(0); playing = false
                }, shape = RoundedCornerShape(16.dp), color = simSoft) {
                    Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Rounded.SkipPrevious, null, tint = Cream, modifier = Modifier.size(20.dp)); Text("−10%", color = Cream, fontSize = 8.sp)
                    }
                }
                Button(onClick = {
                    if (timeline >= timelineTotal) timeline = 0
                    playing = !playing
                }, modifier = Modifier.weight(1f).height(58.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White)) {
                    Icon(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, null); Spacer(Modifier.width(7.dp))
                    Text(if (playing) "Pausar" else if (timeline > 0) "Continuar" else "Iniciar", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
                Surface(modifier = Modifier.width(86.dp).height(58.dp).clickable { timeline = 0; playing = false }, shape = RoundedCornerShape(16.dp), color = simSoft) {
                    Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Rounded.Stop, null, tint = if (timeline > 0) accent else simMuted, modifier = Modifier.size(20.dp)); Text("Parar", color = if (timeline > 0) accent else simMuted, fontSize = 8.sp)
                    }
                }
            }
        }
    }
}'''
text = text[:ss] + new_sim + text[se:]

main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 38', gradle, count=1)
gradle = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "0.2.36"', gradle, count=1)
gradle_path.write_text(gradle, encoding='utf-8')

# Guards: full name accumulation, two-phase simulation and Traditional isolation.
final = main_path.read_text(encoding='utf-8')
for token in ['glyphPath.addPath(charPath)', 'TraditionalGuideOverlay036(', 'val guideSteps = 52', 'val actualCurrent = (timeline - guideSteps)', 'page == Page.TRADITIONAL_SIMULATOR && design != null']:
    if token not in final:
        raise SystemExit('0.2.36 regression guard missing: ' + token)
if 'paint.getTextPath(token, 0, token.length, cursorX, 0f, glyphPath)' in final:
    raise SystemExit('0.2.36 old single-glyph destination still present')
if 'versionCode = 38' not in gradle_path.read_text(encoding='utf-8') or 'versionName = "0.2.36"' not in gradle_path.read_text(encoding='utf-8'):
    raise SystemExit('0.2.36 version guard failed')

print('BORDATTO 0.2.36 full-name lettering + guide-then-embroider simulation applied successfully')
