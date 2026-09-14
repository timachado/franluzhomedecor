from pathlib import Path
import runpy

# Start from the validated 0.2.34 Traditional/Studio Pro split.
runpy.run_path('.github/scripts/patch_bordatto_064.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')


def balanced_block(source: str, signature: str):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1, source[start:i + 1]
    raise SystemExit('Could not find balanced block for ' + signature)

# Make the Traditional hoop outline match the dashed reference visual.
canvas_sig = '@Composable\nprivate fun TraditionalDesignCanvas034'
cs, ce, canvas_block = balanced_block(text, canvas_sig)
old_border = '''        drawRoundRect(
            color = Color(0xFF776D60),
            topLeft = Offset(pad, pad),
            size = androidx.compose.ui.geometry.Size((canvasSize.width - pad * 2).coerceAtLeast(1f), (canvasSize.height - pad * 2).coerceAtLeast(1f)),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(16f, 16f),
            style = Stroke(width = 2f)
        )'''
new_border = '''        drawRoundRect(
            color = Color(0xFF303247),
            topLeft = Offset(pad, pad),
            size = androidx.compose.ui.geometry.Size((canvasSize.width - pad * 2).coerceAtLeast(1f), (canvasSize.height - pad * 2).coerceAtLeast(1f)),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(16f, 16f),
            style = Stroke(
                width = 2f,
                pathEffect = androidx.compose.ui.graphics.PathEffect.dashPathEffect(floatArrayOf(10f, 7f))
            )
        )'''
if old_border not in canvas_block:
    raise SystemExit('0.2.35 Traditional dashed hoop anchor not found')
canvas_block = canvas_block.replace(old_border, new_border, 1)
text = text[:cs] + canvas_block + text[ce:]

simulator = r'''private fun formatTraditionalRemaining035(seconds: Int): String {
    val safe = seconds.coerceAtLeast(0)
    val minutes = safe / 60
    val secs = safe % 60
    return if (minutes > 0) "${minutes}m ${secs.toString().padStart(2, '0')}s" else "${secs}s"
}

@Composable
private fun TraditionalSimulationNeedle035(
    design: Design,
    current: Int,
    accent: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier) {
        val canvasSize = this.size
        val ring = minOf(canvasSize.width, canvasSize.height)
        drawCircle(
            color = Color(0x16000000),
            radius = ring * .22f,
            center = Offset(canvasSize.width / 2f, canvasSize.height / 2f),
            style = Stroke(width = 1f)
        )
        drawCircle(
            color = Color(0x16000000),
            radius = ring * .38f,
            center = Offset(canvasSize.width / 2f, canvasSize.height / 2f),
            style = Stroke(width = 1f)
        )

        if (current <= 0 || design.stitches.isEmpty()) return@Canvas
        val index = (current - 1).coerceIn(0, design.stitches.lastIndex)
        val needle = design.stitches[index]
        val w = design.width.coerceAtLeast(1f)
        val h = design.height.coerceAtLeast(1f)
        val usableW = (canvasSize.width - 84f).coerceAtLeast(1f)
        val usableH = (canvasSize.height - 84f).coerceAtLeast(1f)
        val scale = minOf(usableW / w, usableH / h)
        val left = (canvasSize.width - w * scale) / 2f
        val top = (canvasSize.height - h * scale) / 2f
        val pos = Offset(
            left + (needle.x - design.minX) * scale,
            top + (needle.y - design.minY) * scale
        )
        drawLine(Color(0x443C3B43), Offset(28f, pos.y), Offset(canvasSize.width - 28f, pos.y), strokeWidth = 1f)
        drawLine(Color(0x443C3B43), Offset(pos.x, 28f), Offset(pos.x, canvasSize.height - 28f), strokeWidth = 1f)
        drawCircle(Color.White.copy(alpha = .90f), radius = 7.2f, center = pos)
        drawCircle(accent, radius = 5.4f, center = pos)
    }
}

@Composable
private fun TraditionalSimulatorScreen034(design: Design, onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var playing by remember { mutableStateOf(false) }
    var speed by remember { mutableFloatStateOf(1f) }
    var current by remember(design) { mutableIntStateOf(0) }

    val sequenceTotal = design.stitches.size.coerceAtLeast(1)
    val stitchTotal = design.stitchCount.coerceAtLeast(1)
    val progress = (current.toFloat() / sequenceTotal.toFloat()).coerceIn(0f, 1f)
    val completedPoints = remember(design, current) {
        design.stitches.take(current.coerceIn(0, design.stitches.size)).count { it.command == StitchCommand.STITCH }
    }
    val remainingPoints = (stitchTotal - completedPoints).coerceAtLeast(0)
    val remainingSeconds = kotlin.math.ceil(remainingPoints / 750.0 * 60.0).toInt()

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
            val dr = r1 - r2; val dg = g1 - g2; val db = b1 - b2
            dr * dr + dg * dg + db * db
        } ?: TraditionalThreads034.first()
    }

    LaunchedEffect(playing, speed, sequenceTotal) {
        while (playing && current < sequenceTotal) {
            delay(80L)
            current = (current + speed.toInt().coerceAtLeast(1)).coerceAtMost(sequenceTotal)
        }
        if (current >= sequenceTotal) playing = false
    }

    val simBg = Color(0xFF0E0B15)
    val simCard = Color(0xFF1B1924)
    val simSoft = Color(0xFF25222E)
    val simMuted = Color(0xFFBBB6C2)

    Column(Modifier.fillMaxSize().background(simBg)) {
        Box(Modifier.fillMaxWidth().height(66.dp).background(simBg)) {
            IconButton(
                onClick = onBack,
                modifier = Modifier.align(Alignment.CenterStart).padding(start = 4.dp)
            ) {
                Icon(Icons.Rounded.ArrowBack, "Voltar", tint = Cream)
            }
            Text(
                "Simulação",
                color = Cream,
                fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.align(Alignment.Center)
            )
            Surface(
                modifier = Modifier.align(Alignment.CenterEnd).padding(end = 10.dp),
                shape = RoundedCornerShape(14.dp),
                color = simCard
            ) {
                Row(Modifier.padding(4.dp), verticalAlignment = Alignment.CenterVertically) {
                    listOf(1f, 2f, 4f).forEach { value ->
                        val selected = kotlin.math.abs(speed - value) < .01f
                        Surface(
                            modifier = Modifier.clickable { speed = value },
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
            TraditionalDesignCanvas034(
                design = design,
                displayMode = "Sólida",
                showGrid = true,
                showConnections = false,
                layerVisible = true,
                layerOpacity = 1f,
                visibleUntil = current,
                ghostRemaining = true,
                modifier = Modifier.fillMaxSize()
            )
            TraditionalSimulationNeedle035(
                design = design,
                current = current,
                accent = accent,
                modifier = Modifier.fillMaxSize()
            )
            Surface(
                modifier = Modifier.align(Alignment.TopStart).padding(10.dp),
                shape = RoundedCornerShape(50),
                color = Color(0xFF403D43)
            ) {
                Text(
                    "${"%.1f".format(progress * 100f)}%",
                    color = Color.White,
                    fontSize = 8.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }
            Surface(
                modifier = Modifier.align(Alignment.TopEnd).padding(10.dp),
                shape = RoundedCornerShape(50),
                color = Color(0xFF403D43)
            ) {
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
                border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha = .06f))
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        Modifier.size(44.dp)
                            .clip(CircleShape)
                            .background(accent)
                            .border(2.dp, Color.White.copy(alpha = .22f), CircleShape)
                    )
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "${matching.name} • ${matching.brand} ${matching.code}",
                            color = Cream,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1
                        )
                        Box(
                            Modifier.fillMaxWidth().height(4.dp).clip(RoundedCornerShape(50)).background(simSoft)
                        ) {
                            Box(
                                Modifier.fillMaxWidth(progress).fillMaxHeight().background(accent)
                            )
                        }
                    }
                    Spacer(Modifier.width(10.dp))
                    Surface(shape = RoundedCornerShape(12.dp), color = simSoft) {
                        Text(
                            "Fio ${activeThread + 1} / ${threadSequence.size.coerceAtLeast(1)}",
                            color = simMuted,
                            fontSize = 8.sp,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)
                        )
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "$completedPoints / $stitchTotal pts",
                    color = simMuted,
                    fontSize = 9.sp,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    "Restante: ${formatTraditionalRemaining035(remainingSeconds)}",
                    color = simMuted,
                    fontSize = 9.sp
                )
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    shape = RoundedCornerShape(50),
                    color = simCard,
                    border = androidx.compose.foundation.BorderStroke(1.dp, accent.copy(alpha = .85f))
                ) {
                    Row(
                        Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(Modifier.size(12.dp).clip(CircleShape).background(accent))
                        Spacer(Modifier.width(5.dp))
                        Text(matching.code, color = Cream, fontSize = 8.sp, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.width(3.dp))
                        Icon(Icons.Rounded.PlayArrow, null, tint = simMuted, modifier = Modifier.size(14.dp))
                    }
                }
            }

            Slider(
                value = current.toFloat(),
                onValueChange = {
                    playing = false
                    current = it.toInt().coerceIn(0, sequenceTotal)
                },
                valueRange = 0f..sequenceTotal.toFloat(),
                modifier = Modifier.fillMaxWidth().height(32.dp),
                colors = SliderDefaults.colors(
                    thumbColor = accent,
                    activeTrackColor = accent,
                    inactiveTrackColor = simSoft
                )
            )

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                Surface(
                    modifier = Modifier.width(86.dp).height(58.dp).clickable {
                        current = (current - maxOf(1, sequenceTotal / 10)).coerceAtLeast(0)
                        playing = false
                    },
                    shape = RoundedCornerShape(16.dp),
                    color = simSoft
                ) {
                    Column(
                        Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Rounded.SkipPrevious, null, tint = Cream, modifier = Modifier.size(20.dp))
                        Text("−10%", color = Cream, fontSize = 8.sp)
                    }
                }

                Button(
                    onClick = {
                        if (current >= sequenceTotal) current = 0
                        playing = !playing
                    },
                    modifier = Modifier.weight(1f).height(58.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White)
                ) {
                    Icon(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, null)
                    Spacer(Modifier.width(7.dp))
                    Text(
                        if (playing) "Pausar" else if (current > 0) "Continuar" else "Iniciar",
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                Surface(
                    modifier = Modifier.width(86.dp).height(58.dp).clickable {
                        playing = false
                        current = 0
                    },
                    shape = RoundedCornerShape(16.dp),
                    color = simSoft
                ) {
                    Column(
                        Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Rounded.Stop, null, tint = accent, modifier = Modifier.size(20.dp))
                        Text("Parar", color = accent, fontSize = 8.sp)
                    }
                }
            }
        }
    }
}
'''

sim_sig = '@Composable\nprivate fun TraditionalSimulatorScreen034'
ss, se, _old_sim = balanced_block(text, sim_sig)
# Put helper functions immediately before the replacement simulator.
text = text[:ss] + simulator + text[se:]

# Keep the visible app version consistent with the APK version.
text = text.replace('0.2.34', '0.2.35')
main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
if 'versionCode = 36' not in gradle or 'versionName = "0.2.34"' not in gradle:
    raise SystemExit('0.2.35 version anchors not found')
gradle = gradle.replace('versionCode = 36', 'versionCode = 37', 1)
gradle = gradle.replace('versionName = "0.2.34"', 'versionName = "0.2.35"', 1)
gradle_path.write_text(gradle, encoding='utf-8')

required = [
    'private fun TraditionalSimulationNeedle035(',
    'formatTraditionalRemaining035(',
    'delay(80L)',
    'listOf(1f, 2f, 4f)',
    '"Simulação"',
    '"%.1f".format(progress * 100f)',
    'ghostRemaining = true',
    'displayMode = "Sólida"',
    '"Restante: ${formatTraditionalRemaining035(remainingSeconds)}"',
    '"Fio ${activeThread + 1} / ${threadSequence.size.coerceAtLeast(1)}"',
    'Slider(',
    '"−10%"',
    '"Parar"',
    'PathEffect.dashPathEffect',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.35 simulator regression guard failed: ' + ', '.join(missing))

# Guard the key product requirement again: Traditional simulation may not leak Pro tools.
ss2, se2, sim_slice = balanced_block(text, '@Composable\nprivate fun TraditionalSimulatorScreen034')
for forbidden in ['MachineCheckPanel(', 'DesignAnalyzerPanel(', 'SafeEditorPanel(', 'Ferramentas profissionais']:
    if forbidden in sim_slice:
        raise SystemExit('0.2.35 Traditional simulator isolation failed: ' + forbidden)

print('BORDATTO 0.2.35 reference-style Traditional simulation applied successfully')
