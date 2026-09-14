from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_030.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Add true-sequence simulator state to the existing multi-format viewer.
old = '''    var grid by remember { mutableStateOf(true) }
    var info by remember { mutableStateOf(true) }
    val transform = rememberTransformableState { z, p, _ ->'''
new = '''    var grid by remember { mutableStateOf(true) }
    var info by remember { mutableStateOf(true) }

    val stitchIndices = remember(design) {
        design.stitches.mapIndexedNotNull { index, stitch ->
            if (stitch.command == StitchCommand.STITCH) index else null
        }
    }
    val colorBlockStarts = remember(design, stitchIndices) {
        if (stitchIndices.isEmpty()) emptyList() else buildList {
            add(0)
            var lastColor = design.stitches[stitchIndices.first()].color
            stitchIndices.forEachIndexed { position, rawIndex ->
                val color = design.stitches[rawIndex].color
                if (position > 0 && color != lastColor) add(position)
                lastColor = color
            }
        }
    }
    var simulatorPosition by remember(design) { mutableIntStateOf(stitchIndices.size) }
    var simulatorPlaying by remember(design) { mutableStateOf(false) }
    var simulatorSpeed by remember(design) { mutableFloatStateOf(1f) }

    val visibleUntil = remember(simulatorPosition, stitchIndices) {
        if (simulatorPosition <= 0 || stitchIndices.isEmpty()) 0
        else stitchIndices[(simulatorPosition - 1).coerceIn(0, stitchIndices.lastIndex)] + 1
    }
    val simulatorBlock = remember(simulatorPosition, colorBlockStarts) {
        if (colorBlockStarts.isEmpty()) 0 else {
            val probe = (simulatorPosition - 1).coerceAtLeast(0)
            colorBlockStarts.indexOfLast { it <= probe }.coerceAtLeast(0) + 1
        }
    }

    LaunchedEffect(simulatorPlaying, simulatorSpeed, design) {
        while (simulatorPlaying && simulatorPosition < stitchIndices.size) {
            delay(40L)
            val batch = maxOf(1, (6f * simulatorSpeed).toInt())
            simulatorPosition = (simulatorPosition + batch).coerceAtMost(stitchIndices.size)
            if (simulatorPosition >= stitchIndices.size) simulatorPlaying = false
        }
    }

    val transform = rememberTransformableState { z, p, _ ->'''
if old not in text:
    raise SystemExit('viewer simulator state marker not found')
text = text.replace(old, new, 1)

# Render only the sequence reached by the simulator playhead.
old = '            StitchCanvas(design, zoom, pan, grid, Modifier.fillMaxSize())'
new = '            StitchCanvas(design, zoom, pan, grid, Modifier.fillMaxSize(), visibleUntil = visibleUntil)'
if old not in text:
    raise SystemExit('StitchCanvas viewer call not found')
text = text.replace(old, new, 1)

# Add the simulator controller under the canvas without covering the matrix.
old = '''        Surface(color = Chocolate) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {'''
new = '''        EmbroiderySimulatorPanel(
            current = simulatorPosition,
            total = stitchIndices.size,
            block = simulatorBlock,
            blockTotal = colorBlockStarts.size,
            playing = simulatorPlaying,
            speed = simulatorSpeed,
            onStop = {
                simulatorPlaying = false
                simulatorPosition = 0
            },
            onPrevious = {
                simulatorPlaying = false
                simulatorPosition = (simulatorPosition - 1).coerceAtLeast(0)
            },
            onPlayPause = {
                if (stitchIndices.isNotEmpty()) {
                    if (!simulatorPlaying && simulatorPosition >= stitchIndices.size) simulatorPosition = 0
                    simulatorPlaying = !simulatorPlaying
                }
            },
            onNext = {
                simulatorPlaying = false
                simulatorPosition = (simulatorPosition + 1).coerceAtMost(stitchIndices.size)
            },
            onNextColor = {
                simulatorPlaying = false
                if (stitchIndices.isNotEmpty()) {
                    if (simulatorPosition == 0) {
                        simulatorPosition = 1
                    } else {
                        val next = colorBlockStarts.firstOrNull { it >= simulatorPosition && it > 0 }
                        simulatorPosition = if (next == null) stitchIndices.size else (next + 1).coerceAtMost(stitchIndices.size)
                    }
                }
            },
            onSpeed = { simulatorSpeed = it }
        )
        Surface(color = Chocolate) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {'''
if old not in text:
    raise SystemExit('viewer footer marker not found')
text = text.replace(old, new, 1)

# Insert the Material 3 Expressive simulator controls before ViewerTool.
insert_at = text.index('@Composable\nprivate fun ViewerTool')
simulator_ui = r'''@Composable
private fun EmbroiderySimulatorPanel(
    current: Int,
    total: Int,
    block: Int,
    blockTotal: Int,
    playing: Boolean,
    speed: Float,
    onStop: () -> Unit,
    onPrevious: () -> Unit,
    onPlayPause: () -> Unit,
    onNext: () -> Unit,
    onNextColor: () -> Unit,
    onSpeed: (Float) -> Unit
) {
    val progress = if (total <= 0) 0f else current.toFloat() / total.toFloat()
    val speeds = listOf(.25f, .5f, 1f, 2f, 4f)

    Surface(
        color = SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .46f))
    ) {
        Column(
            Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 11.dp),
            verticalArrangement = Arrangement.spacedBy(9.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ExpressiveIconBadge(Icons.Rounded.PlayArrow, selected = playing, size = 38.dp)
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text("Simulador de bordado", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                    Text(
                        if (total == 0) "Sem pontadas para reproduzir" else "Ponto $current de $total • Bloco ${block.coerceAtLeast(1)} de ${blockTotal.coerceAtLeast(1)}",
                        color = Muted,
                        fontSize = 9.sp
                    )
                }
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .14f)) {
                    Text("${formatSimulatorSpeed(speed)}×", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                }
            }

            Box(
                Modifier.fillMaxWidth().height(5.dp).clip(RoundedCornerShape(50)).background(LineGold.copy(alpha = .35f))
            ) {
                Box(
                    Modifier.fillMaxWidth(progress.coerceIn(0f, 1f)).fillMaxHeight().background(Gold)
                )
            }

            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                SimulatorAction(Icons.Rounded.Stop, "Parar", false, 40.dp, onStop)
                SimulatorAction(Icons.Rounded.ChevronLeft, "Ponto anterior", false, 40.dp, onPrevious)
                SimulatorAction(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, if (playing) "Pausar" else "Reproduzir", true, 52.dp, onPlayPause)
                SimulatorAction(Icons.Rounded.ChevronRight, "Próximo ponto", false, 40.dp, onNext)
                SimulatorAction(Icons.Rounded.Palette, "Próxima cor", false, 40.dp, onNextColor)
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                speeds.forEach { option ->
                    val selected = kotlin.math.abs(speed - option) < .01f
                    Surface(
                        modifier = Modifier.weight(1f).clickable { onSpeed(option) },
                        shape = RoundedCornerShape(if (selected) 16.dp else 12.dp),
                        color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha = .70f) else LineGold.copy(alpha = .35f))
                    ) {
                        Text(
                            "${formatSimulatorSpeed(option)}×",
                            color = if (selected) Gold else Muted,
                            fontSize = 9.sp,
                            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 7.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SimulatorAction(icon: ImageVector, description: String, primary: Boolean, size: androidx.compose.ui.unit.Dp, onClick: () -> Unit) {
    Surface(
        modifier = Modifier.size(size).clickable(onClick = onClick),
        shape = CircleShape,
        color = if (primary) Gold else CardBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, if (primary) Gold else LineGold.copy(alpha = .55f))
    ) {
        Box(contentAlignment = Alignment.Center) {
            Icon(icon, description, tint = if (primary) Ink else Gold, modifier = Modifier.size(if (primary) 27.dp else 21.dp))
        }
    }
}

private fun formatSimulatorSpeed(speed: Float): String = when (speed) {
    .25f -> "0,25"
    .5f -> "0,5"
    1f -> "1"
    2f -> "2"
    4f -> "4"
    else -> "${speed}"
}

'''
text = text[:insert_at] + simulator_ui + text[insert_at:]

# Allow the canvas to render a progressive prefix of the true design sequence.
old = '''private fun StitchCanvas(design: Design, zoom: Float, pan: Offset, grid: Boolean, modifier: Modifier) {'''
new = '''private fun StitchCanvas(design: Design, zoom: Float, pan: Offset, grid: Boolean, modifier: Modifier, visibleUntil: Int = design.stitches.size) {'''
if old not in text:
    raise SystemExit('StitchCanvas signature not found')
text = text.replace(old, new, 1)

canvas_start = text.index('private fun StitchCanvas(')
canvas_end = text.index('\nprivate fun parseEmbroidery', canvas_start)
canvas = text[canvas_start:canvas_end]
old_loop = '        for (st in design.stitches) {'
new_loop = '''        val end = visibleUntil.coerceIn(0, design.stitches.size)
        for (index in 0 until end) {
            val st = design.stitches[index]'''
if old_loop not in canvas:
    raise SystemExit('StitchCanvas drawing loop not found')
canvas = canvas.replace(old_loop, new_loop, 1)
text = text[:canvas_start] + canvas + text[canvas_end:]

text = text.replace('0.2.10', '0.2.11')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.11 true-sequence embroidery simulator patch applied successfully')
