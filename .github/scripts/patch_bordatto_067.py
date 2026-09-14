from pathlib import Path
import re
import runpy

# Start from validated 0.2.36 (full-name lettering + Traditional isolation).
runpy.run_path('.github/scripts/patch_bordatto_066.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')


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

# Faithful simulation canvas based on the reference behavior:
# - complete design remains as a pale ghost
# - actual embroidery sequence is revealed in real order
# - running/underlay segments remain thin; satin/fill segments are stronger
# - no fake full-word guide phase
simulation_canvas = r'''
@Composable
private fun TraditionalSimulationCanvas037(
    design: Design,
    current: Int,
    modifier: Modifier = Modifier
) {
    Canvas(modifier) {
        val canvasSize = this.size
        val grid = Color(0x175E5549)
        val hoop = Color(0xFF35374B)
        val step = 32f
        var gx = 0f
        while (gx < canvasSize.width) {
            drawLine(grid, Offset(gx, 0f), Offset(gx, canvasSize.height), strokeWidth = 1f)
            gx += step
        }
        var gy = 0f
        while (gy < canvasSize.height) {
            drawLine(grid, Offset(0f, gy), Offset(canvasSize.width, gy), strokeWidth = 1f)
            gy += step
        }

        val pad = 28f
        drawRoundRect(
            color = hoop,
            topLeft = Offset(pad, pad),
            size = androidx.compose.ui.geometry.Size(
                (canvasSize.width - pad * 2f).coerceAtLeast(1f),
                (canvasSize.height - pad * 2f).coerceAtLeast(1f)
            ),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(18f, 18f),
            style = Stroke(
                width = 2f,
                pathEffect = androidx.compose.ui.graphics.PathEffect.dashPathEffect(floatArrayOf(10f, 7f))
            )
        )

        val center = Offset(canvasSize.width / 2f, canvasSize.height / 2f)
        val radius = minOf(canvasSize.width, canvasSize.height)
        drawCircle(Color(0x145E5549), radius = radius * .19f, center = center, style = Stroke(width = 1f))
        drawCircle(Color(0x145E5549), radius = radius * .34f, center = center, style = Stroke(width = 1f))

        if (design.stitches.isEmpty()) return@Canvas
        val w = design.width.coerceAtLeast(1f)
        val h = design.height.coerceAtLeast(1f)
        val usableW = (canvasSize.width - 84f).coerceAtLeast(1f)
        val usableH = (canvasSize.height - 84f).coerceAtLeast(1f)
        val scale = minOf(usableW / w, usableH / h)
        val left = (canvasSize.width - w * scale) / 2f
        val top = (canvasSize.height - h * scale) / 2f
        fun map(p: StitchPoint): Offset = Offset(
            left + (p.x - design.minX) * scale,
            top + (p.y - design.minY) * scale
        )

        fun drawPass(limit: Int, ghost: Boolean) {
            var previous: StitchPoint? = null
            design.stitches.take(limit.coerceIn(0, design.stitches.size)).forEach { point ->
                when (point.command) {
                    StitchCommand.STITCH -> {
                        val prev = previous
                        if (prev != null && prev.command == StitchCommand.STITCH) {
                            val a = map(prev)
                            val b = map(point)
                            val dx = kotlin.math.abs(point.x - prev.x)
                            val dy = kotlin.math.abs(point.y - prev.y)
                            val underlayLike = dy < 1.25f || (dx > 0.01f && dy / dx.coerceAtLeast(.01f) < .34f)
                            val baseColor = Color(point.color)
                            if (ghost) {
                                drawLine(
                                    baseColor.copy(alpha = if (underlayLike) .08f else .13f),
                                    a,
                                    b,
                                    strokeWidth = if (underlayLike) 1.0f else 2.1f,
                                    cap = StrokeCap.Round
                                )
                            } else {
                                if (!underlayLike) {
                                    drawLine(Color.Black.copy(alpha = .10f), a + Offset(.8f, .8f), b + Offset(.8f, .8f), strokeWidth = 3.2f, cap = StrokeCap.Round)
                                }
                                drawLine(
                                    baseColor.copy(alpha = if (underlayLike) .92f else 1f),
                                    a,
                                    b,
                                    strokeWidth = if (underlayLike) 1.35f else 2.8f,
                                    cap = StrokeCap.Round
                                )
                                if (!underlayLike) {
                                    drawLine(Color.White.copy(alpha = .09f), a, b, strokeWidth = .7f, cap = StrokeCap.Round)
                                }
                            }
                        }
                    }
                    StitchCommand.JUMP, StitchCommand.COLOR_CHANGE, StitchCommand.TRIM, StitchCommand.END -> Unit
                }
                previous = when (point.command) {
                    StitchCommand.JUMP, StitchCommand.COLOR_CHANGE, StitchCommand.TRIM, StitchCommand.END -> null
                    else -> point
                }
            }
        }

        // Full matrix is visible as the translucent reference, just like the model app.
        drawPass(design.stitches.size, ghost = true)
        // Real embroidery sequence is then applied on top, in its actual stitch order.
        drawPass(current, ghost = false)
    }
}
'''
insert_at = text.index('@Composable\nprivate fun TraditionalSimulatorScreen034')
text = text[:insert_at] + simulation_canvas + '\n' + text[insert_at:]

ss, se = balanced_block(text, '@Composable\nprivate fun TraditionalSimulatorScreen034')
new_sim = r'''@Composable
private fun TraditionalSimulatorScreen034(design: Design, onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var playing by remember { mutableStateOf(false) }
    var speed by remember { mutableFloatStateOf(1f) }
    var current by remember(design) { mutableIntStateOf(0) }
    var showCompleted by remember(design) { mutableStateOf(false) }

    val sequenceTotal = design.stitches.size.coerceAtLeast(1)
    val stitchTotal = design.stitchCount.coerceAtLeast(1)
    val progress = (current.toFloat() / sequenceTotal.toFloat()).coerceIn(0f, 1f)
    val completedPoints = remember(design, current) {
        design.stitches.take(current.coerceIn(0, design.stitches.size)).count { it.command == StitchCommand.STITCH }
    }
    val remainingPoints = (stitchTotal - completedPoints).coerceAtLeast(0)
    val remainingSeconds = kotlin.math.ceil(
        remainingPoints / (750.0 * speed.coerceAtLeast(1f)) * 60.0
    ).toInt().coerceAtLeast(0)

    val activeStitch = remember(design, current) {
        val end = current.coerceIn(0, design.stitches.size)
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

    LaunchedEffect(playing, speed, sequenceTotal) {
        while (playing && current < sequenceTotal) {
            // Reference pace: ~750 points/min at 1x.
            delay(80L)
            current = (current + speed.toInt().coerceAtLeast(1)).coerceAtMost(sequenceTotal)
        }
        if (current >= sequenceTotal) {
            playing = false
            if (current > 0) showCompleted = true
        }
    }

    val simBg = Color(0xFF0E0B15)
    val simCard = Color(0xFF1B1924)
    val simSoft = Color(0xFF25222E)
    val simMuted = Color(0xFFBBB6C2)
    val finished = current >= sequenceTotal

    Box(Modifier.fillMaxSize().background(simBg)) {
        Column(Modifier.fillMaxSize()) {
            Box(Modifier.fillMaxWidth().height(66.dp).background(simBg)) {
                IconButton(onClick = onBack, modifier = Modifier.align(Alignment.CenterStart).padding(start = 4.dp)) {
                    Icon(Icons.Rounded.ArrowBack, "Voltar", tint = Cream)
                }
                Text("Simulação", color = Cream, fontSize = 15.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.align(Alignment.Center))
                Surface(modifier = Modifier.align(Alignment.CenterEnd).padding(end = 10.dp), shape = RoundedCornerShape(14.dp), color = simCard) {
                    Row(Modifier.padding(4.dp), verticalAlignment = Alignment.CenterVertically) {
                        listOf(1f, 2f, 4f).forEach { value ->
                            val selected = kotlin.math.abs(speed - value) < .01f
                            Surface(
                                modifier = Modifier.clickable(enabled = !finished) { speed = value },
                                shape = RoundedCornerShape(10.dp),
                                color = if (selected) accent else Color.Transparent
                            ) {
                                Text(
                                    "${value.toInt()}×",
                                    color = if (selected) Color.White else simMuted,
                                    fontSize = 9.sp,
                                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                                )
                            }
                        }
                    }
                }
            }

            Box(Modifier.fillMaxWidth().weight(1f).background(Color(0xFFF0E8D8))) {
                TraditionalSimulationCanvas037(
                    design = design,
                    current = current,
                    modifier = Modifier.fillMaxSize()
                )
                TraditionalSimulationNeedle035(
                    design = design,
                    current = current,
                    accent = accent,
                    modifier = Modifier.fillMaxSize()
                )
                Surface(modifier = Modifier.align(Alignment.TopStart).padding(10.dp), shape = RoundedCornerShape(50), color = Color(0xFF403D43)) {
                    Text(
                        "${"%.1f".format(progress * 100f)}%",
                        color = Color.White,
                        fontSize = 8.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                    )
                }
                Surface(modifier = Modifier.align(Alignment.TopEnd).padding(10.dp), shape = RoundedCornerShape(50), color = Color(0xFF403D43)) {
                    Text(
                        "${"%.0f".format(design.width)} × ${"%.0f".format(design.height)} mm",
                        color = Color.White,
                        fontSize = 8.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                    )
                }
            }

            Column(
                Modifier.fillMaxWidth().background(simBg).padding(horizontal = 14.dp, vertical = 10.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    color = simCard,
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha=.06f))
                ) {
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
                    Text(if (finished) "Completo ✓" else "Restante: ${formatTraditionalRemaining035(remainingSeconds)}", color = simMuted, fontSize = 9.sp)
                }

                Surface(shape = RoundedCornerShape(50), color = simCard, border = androidx.compose.foundation.BorderStroke(1.dp, accent.copy(alpha=.85f))) {
                    Row(Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(12.dp).clip(CircleShape).background(accent)); Spacer(Modifier.width(5.dp))
                        Text(matching.code, color = Cream, fontSize = 8.sp, fontWeight = FontWeight.SemiBold); Spacer(Modifier.width(3.dp))
                        Icon(if (finished) Icons.Rounded.Check else Icons.Rounded.PlayArrow, null, tint = if (finished) accent else simMuted, modifier = Modifier.size(14.dp))
                    }
                }

                Slider(
                    value = current.toFloat(),
                    onValueChange = {
                        playing = false
                        showCompleted = false
                        current = it.toInt().coerceIn(0, sequenceTotal)
                    },
                    valueRange = 0f..sequenceTotal.toFloat(),
                    enabled = !showCompleted,
                    modifier = Modifier.fillMaxWidth().height(32.dp),
                    colors = SliderDefaults.colors(thumbColor = accent, activeTrackColor = accent, inactiveTrackColor = simSoft)
                )

                if (!finished) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                        Surface(
                            modifier = Modifier.width(86.dp).height(58.dp).clickable {
                                current = (current - maxOf(1, sequenceTotal / 10)).coerceAtLeast(0)
                                playing = false
                                showCompleted = false
                            },
                            shape = RoundedCornerShape(16.dp),
                            color = simSoft
                        ) {
                            Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(Icons.Rounded.SkipPrevious, null, tint = Cream, modifier = Modifier.size(20.dp))
                                Text("−10%", color = Cream, fontSize = 8.sp)
                            }
                        }
                        Button(
                            onClick = { playing = !playing },
                            modifier = Modifier.weight(1f).height(58.dp),
                            shape = RoundedCornerShape(16.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White)
                        ) {
                            Icon(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, null)
                            Spacer(Modifier.width(7.dp))
                            Text(if (playing) "Pausar" else if (current > 0) "Continuar" else "Iniciar Simulação", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        }
                        Surface(
                            modifier = Modifier.width(86.dp).height(58.dp).clickable(enabled = current > 0) {
                                current = 0
                                playing = false
                                showCompleted = false
                            },
                            shape = RoundedCornerShape(16.dp),
                            color = simSoft
                        ) {
                            Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(Icons.Rounded.Stop, null, tint = if (current > 0) accent else simMuted, modifier = Modifier.size(20.dp))
                                Text("Parar", color = if (current > 0) accent else simMuted, fontSize = 8.sp)
                            }
                        }
                    }
                } else {
                    Button(
                        onClick = { current = 0; playing = false; showCompleted = false },
                        modifier = Modifier.fillMaxWidth().height(58.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White)
                    ) {
                        Icon(Icons.Rounded.Refresh, null); Spacer(Modifier.width(7.dp)); Text("Reiniciar", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        if (showCompleted) {
            Box(
                Modifier.fillMaxSize().background(Color.Black.copy(alpha = .72f)),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    Modifier.fillMaxWidth(.84f),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Box(Modifier.size(92.dp).clip(CircleShape).background(Color(0xFF31C89A)), contentAlignment = Alignment.Center) {
                        Icon(Icons.Rounded.Check, null, tint = Color.White, modifier = Modifier.size(54.dp))
                    }
                    Text("Bordado concluído!", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                    Text("$stitchTotal pontos aplicados", color = simMuted, fontSize = 13.sp)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Surface(
                            modifier = Modifier.weight(1f).height(54.dp).clickable { showCompleted = false },
                            shape = RoundedCornerShape(16.dp),
                            color = simSoft
                        ) {
                            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                Text("Fechar", color = Cream, fontWeight = FontWeight.Bold)
                            }
                        }
                        Button(
                            onClick = { current = 0; playing = false; showCompleted = false },
                            modifier = Modifier.weight(1.25f).height(54.dp),
                            shape = RoundedCornerShape(16.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White)
                        ) {
                            Icon(Icons.Rounded.Refresh, null); Spacer(Modifier.width(6.dp)); Text("Reiniciar", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}'''
text = text[:ss] + new_sim + text[se:]

# Remove the previous artificial-guide implementation from the generated source
# when present. It is not called anymore, but removing it avoids future regressions.
if '@Composable\nprivate fun TraditionalGuideOverlay036' in text:
    gs, ge = balanced_block(text, '@Composable\nprivate fun TraditionalGuideOverlay036')
    text = text[:gs] + text[ge:]

main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 39', gradle, count=1)
gradle = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "0.2.37"', gradle, count=1)
gradle_path.write_text(gradle, encoding='utf-8')

final = main_path.read_text(encoding='utf-8')
required = [
    'TraditionalSimulationCanvas037(',
    'drawPass(design.stitches.size, ghost = true)',
    'drawPass(current, ghost = false)',
    'Bordado concluído!',
    'pontos aplicados',
    'Iniciar Simulação',
    '−10%',
    'Completo ✓',
    'glyphPath.addPath(charPath)',
]
for token in required:
    if token not in final:
        raise SystemExit('0.2.37 regression guard missing: ' + token)
if 'val guideSteps = 52' in final:
    raise SystemExit('0.2.37 artificial guide timeline still present')
if 'versionCode = 39' not in gradle_path.read_text(encoding='utf-8') or 'versionName = "0.2.37"' not in gradle_path.read_text(encoding='utf-8'):
    raise SystemExit('0.2.37 version guard failed')

print('BORDATTO 0.2.37 faithful Traditional real-sequence simulation applied successfully')
