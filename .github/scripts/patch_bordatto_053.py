from pathlib import Path
import runpy

# Build on the validated 0.2.29 source.
runpy.run_path('.github/scripts/patch_bordatto_052.py', run_name='__main__')

path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# ---------------- Lettering: reliable, obvious interaction ----------------
letter_start = text.index('@Composable\nprivate fun LetteringScreen')
letter_end = text.index('@Composable\nprivate fun MachineScreen', letter_start)

lettering = r'''@Composable
private fun LetteringStepper(
    title: String,
    value: String,
    onMinus: () -> Unit,
    onPlus: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = CardBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
    ) {
        Row(
            Modifier.fillMaxWidth().padding(9.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(Modifier.weight(1f)) {
                Text(title, color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                Text(value, color = Gold, fontSize = 13.sp, fontWeight = FontWeight.Bold)
            }
            FilledTonalButton(
                onClick = onMinus,
                modifier = Modifier.size(46.dp),
                contentPadding = PaddingValues(0.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.filledTonalButtonColors(containerColor = SurfaceBrown, contentColor = Gold)
            ) { Text("−", fontSize = 22.sp, fontWeight = FontWeight.Bold) }
            Spacer(Modifier.width(7.dp))
            FilledTonalButton(
                onClick = onPlus,
                modifier = Modifier.size(46.dp),
                contentPadding = PaddingValues(0.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha = .18f), contentColor = Gold)
            ) { Text("+", fontSize = 20.sp, fontWeight = FontWeight.Bold) }
        }
    }
}

@Composable
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
    var advanced by remember { mutableStateOf(false) }
    var localError by remember { mutableStateOf<String?>(null) }
    val fonts = listOf("Regular", "Elegance", "Classic", "Sweet", "Handwriting")
    val options = remember(size, spacing, density, pullComp, satinMax, underlay, font) {
        LetteringOptions(size, spacing, density, pullComp, satinMax, underlay, font)
    }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { PageHeader("Criar nome", onBack) }
        item {
            Surface(
                shape = RoundedCornerShape(18.dp),
                color = Gold.copy(alpha = .08f),
                border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.38f))
            ) {
                Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.AutoAwesome, selected = true, size = 42.dp)
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Lettering Satin", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                        Text("Escolha o nome, a fonte e o tamanho. O BORDATTO cuida do restante.", color = Muted, fontSize = 9.sp)
                    }
                    Text("0.2.30", color = Gold, fontSize = 9.sp, fontWeight = FontWeight.Bold)
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
                supportingText = { Text("Até 28 caracteres") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Gold,
                    unfocusedBorderColor = LineGold,
                    focusedLabelColor = Gold
                )
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Cream), shape = RoundedCornerShape(24.dp)) {
                Box(Modifier.fillMaxWidth().height(160.dp).padding(horizontal = 12.dp), contentAlignment = Alignment.Center) {
                    Text(
                        name.ifBlank { "BORDATTO" },
                        color = GoldDeep,
                        fontSize = 44.sp,
                        fontFamily = when (font) {
                            "Elegance", "Classic" -> FontFamily.Serif
                            "Handwriting" -> FontFamily.Cursive
                            else -> FontFamily.SansSerif
                        },
                        fontWeight = if (font == "Classic" || font == "Sweet") FontWeight.Bold else FontWeight.Normal,
                        fontStyle = if (font == "Elegance") FontStyle.Italic else FontStyle.Normal,
                        textAlign = TextAlign.Center,
                        maxLines = 2
                    )
                }
            }
        }
        item { Text("Escolha a fonte", color = Cream, fontWeight = FontWeight.SemiBold) }
        items(fonts.size) { i ->
            val f = fonts[i]
            val selected = font == f
            Surface(
                modifier = Modifier.fillMaxWidth().heightIn(min = 58.dp).clickable { font = f },
                shape = RoundedCornerShape(18.dp),
                color = if (selected) Gold.copy(alpha=.16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.72f) else LineGold.copy(alpha=.38f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.TextFields, selected = selected, size = 38.dp)
                    Spacer(Modifier.width(10.dp))
                    Text(
                        name.ifBlank { "BORDATTO" },
                        color = Cream,
                        fontFamily = when (f) {
                            "Elegance", "Classic" -> FontFamily.Serif
                            "Handwriting" -> FontFamily.Cursive
                            else -> FontFamily.SansSerif
                        },
                        fontWeight = if (f == "Classic" || f == "Sweet") FontWeight.Bold else FontWeight.Normal,
                        fontStyle = if (f == "Elegance") FontStyle.Italic else FontStyle.Normal,
                        fontSize = 18.sp,
                        maxLines = 1,
                        modifier = Modifier.weight(1f)
                    )
                    Column(horizontalAlignment = Alignment.End) {
                        Text(f, color = if (selected) Gold else Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                        Text(if (selected) "SELECIONADA" else "TOQUE PARA USAR", color = if (selected) Gold else Muted, fontSize = 6.sp)
                    }
                }
            }
        }
        item {
            LetteringStepper(
                title = "Altura do nome",
                value = "${"%.0f".format(size)} mm",
                onMinus = { size = (size - 2f).coerceAtLeast(10f) },
                onPlus = { size = (size + 2f).coerceAtMost(90f) }
            )
        }
        item {
            Text("Espaçamento", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
            Spacer(Modifier.height(7.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                listOf("Compacto" to -8f, "Normal" to 0f, "Aberto" to 16f).forEach { (label, value) ->
                    val selected = kotlin.math.abs(spacing - value) < .5f
                    Surface(
                        modifier = Modifier.weight(1f).heightIn(min = 44.dp).clickable { spacing = value },
                        shape = RoundedCornerShape(14.dp),
                        color = if (selected) Gold.copy(alpha=.18f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.70f) else LineGold.copy(alpha=.35f))
                    ) {
                        Box(Modifier.fillMaxWidth().padding(vertical = 11.dp), contentAlignment = Alignment.Center) {
                            Text(label, color = if (selected) Gold else Cream, fontSize = 9.sp, fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal)
                        }
                    }
                }
            }
        }
        item {
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { advanced = !advanced },
                shape = RoundedCornerShape(17.dp),
                color = SurfaceBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.38f))
            ) {
                Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Tune, null, tint = Gold, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(9.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Ajustes profissionais", color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                        Text("Densidade, compensação, Satin e underlay", color = Muted, fontSize = 8.sp)
                    }
                    Text(if (advanced) "FECHAR" else "ABRIR", color = Gold, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.width(4.dp))
                    Icon(if (advanced) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold)
                }
            }
        }
        if (advanced) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    LetteringStepper(
                        "Densidade Satin",
                        "${"%.2f".format(density)} mm",
                        { density = (density - .02f).coerceAtLeast(.28f) },
                        { density = (density + .02f).coerceAtMost(1f) }
                    )
                    LetteringStepper(
                        "Compensação de puxamento",
                        "${"%.2f".format(pullComp)} mm",
                        { pullComp = (pullComp - .05f).coerceAtLeast(0f) },
                        { pullComp = (pullComp + .05f).coerceAtMost(1f) }
                    )
                    LetteringStepper(
                        "Largura máxima Satin",
                        "${"%.1f".format(satinMax)} mm",
                        { satinMax = (satinMax - .5f).coerceAtLeast(4f) },
                        { satinMax = (satinMax + .5f).coerceAtMost(14f) }
                    )
                }
            }
            item {
                Text("Underlay", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                Spacer(Modifier.height(7.dp))
                Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    listOf(
                        "Padrão recomendado" to "Center + Edge",
                        "Centro" to "Center",
                        "Borda" to "Edge",
                        "Zigzag" to "Zigzag"
                    ).forEach { (label, value) ->
                        val selected = underlay == value
                        Surface(
                            modifier = Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable { underlay = value },
                            shape = RoundedCornerShape(14.dp),
                            color = if (selected) Gold.copy(alpha=.16f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.62f) else LineGold.copy(alpha=.32f))
                        ) {
                            Row(Modifier.fillMaxWidth().padding(horizontal = 11.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                                Text(label, color = if (selected) Gold else Cream, fontSize = 9.sp, modifier = Modifier.weight(1f))
                                Text(if (selected) "ATIVO" else "USAR", color = if (selected) Gold else Muted, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
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
                Text("Gerar matriz do nome", fontWeight = FontWeight.Bold)
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
text = text[:letter_start] + lettering + text[letter_end:]

# ---------------- Viewer: simple by default, professional tools explicit ----------------
old_state = '    var grid by remember { mutableStateOf(true) }\n    var info by remember { mutableStateOf(true) }'
new_state = '    var grid by remember { mutableStateOf(true) }\n    var info by remember { mutableStateOf(false) }\n    var viewerAdvanced by remember { mutableStateOf(false) }'
if old_state not in text:
    raise SystemExit('0.2.30 viewer state anchor not found')
text = text.replace(old_state, new_state, 1)

panel_anchor = '        MachineCheckPanel(workingDesign, machineConfig)'
panel_open = r'''        Surface(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 5.dp).clickable { viewerAdvanced = !viewerAdvanced },
            shape = RoundedCornerShape(18.dp),
            color = SurfaceBrown,
            border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
        ) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 11.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.Build, null, tint = Gold, modifier = Modifier.size(19.dp))
                Spacer(Modifier.width(8.dp))
                Column(Modifier.weight(1f)) {
                    Text("Ferramentas profissionais", color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                    Text("Analyzer • Editor • Cores • Exportação", color = Muted, fontSize = 8.sp)
                }
                Text(if (viewerAdvanced) "FECHAR" else "ABRIR", color = Gold, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.width(4.dp))
                Icon(if (viewerAdvanced) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold)
            }
        }
        if (viewerAdvanced) {
        MachineCheckPanel(workingDesign, machineConfig)'''
if panel_anchor not in text:
    raise SystemExit('0.2.30 professional tools open anchor not found')
text = text.replace(panel_anchor, panel_open, 1)

canvas_anchor = '        Box(\n            Modifier.height(360.dp).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
canvas_new = '        }\n        Box(\n            Modifier.height(420.dp).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
if canvas_anchor not in text:
    raise SystemExit('0.2.30 viewer canvas anchor not found')
text = text.replace(canvas_anchor, canvas_new, 1)

# Increase viewer tool touch target.
old_viewer_tool = 'Surface(modifier = Modifier.clickable(onClick = onClick), shape = RoundedCornerShape(18.dp), color = if (selected) Gold.copy(alpha=.16f) else CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.52f) else LineGold.copy(alpha=.5f)))'
new_viewer_tool = 'Surface(modifier = Modifier.heightIn(min = 44.dp).clickable(onClick = onClick), shape = RoundedCornerShape(18.dp), color = if (selected) Gold.copy(alpha=.16f) else CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.52f) else LineGold.copy(alpha=.5f)))'
if old_viewer_tool in text:
    text = text.replace(old_viewer_tool, new_viewer_tool, 1)

# ---------------- Simulator: casual-first ----------------
sim_start = text.index('@Composable\nprivate fun EmbroiderySimulatorPanel')
sim_end = text.index('\n@Composable\nprivate fun ', sim_start + 30)

simulator = r'''@Composable
private fun EmbroiderySimulatorPanel(
    current: Int,
    total: Int,
    block: Int,
    blockTotal: Int,
    playing: Boolean,
    speed: Float,
    machinePpm: Int,
    onStop: () -> Unit,
    onPrevious: () -> Unit,
    onPlayPause: () -> Unit,
    onNext: () -> Unit,
    onNextColor: () -> Unit,
    onSpeed: (Float) -> Unit
) {
    val progress = if (total <= 0) 0f else current.toFloat() / total.toFloat()
    val percent = (progress.coerceIn(0f, 1f) * 100f).toInt()
    var advanced by remember { mutableStateOf(false) }

    Surface(
        color = SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .46f))
    ) {
        Column(
            Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ExpressiveIconBadge(Icons.Rounded.PlayArrow, selected = playing, size = 40.dp)
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text("Simular bordado", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                    Text(
                        if (total == 0) "Sem pontadas para simular" else "$percent% concluído • $current de $total pontos",
                        color = Muted,
                        fontSize = 9.sp
                    )
                }
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .14f)) {
                    Text("${formatSimulatorSpeed(speed)}×", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                }
            }

            Box(Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(50)).background(LineGold.copy(alpha = .30f))) {
                Box(Modifier.fillMaxWidth(progress.coerceIn(0f, 1f)).fillMaxHeight().background(Gold))
            }

            Button(
                onClick = onPlayPause,
                enabled = total > 0,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(18.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, null)
                Spacer(Modifier.width(7.dp))
                Text(if (playing) "Pausar simulação" else if (current > 0 && current < total) "Continuar simulação" else "Iniciar simulação", fontWeight = FontWeight.Bold)
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                FilledTonalButton(
                    onClick = onStop,
                    enabled = total > 0,
                    modifier = Modifier.weight(1f).heightIn(min = 44.dp),
                    shape = RoundedCornerShape(15.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.RestartAlt, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(5.dp))
                    Text("Reiniciar", fontSize = 9.sp)
                }
                listOf(1f, 2f).forEach { option ->
                    val selected = kotlin.math.abs(speed - option) < .01f
                    Surface(
                        modifier = Modifier.weight(.65f).heightIn(min = 44.dp).clickable(enabled = total > 0) { onSpeed(option) },
                        shape = RoundedCornerShape(15.dp),
                        color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha = .65f) else LineGold.copy(alpha=.32f))
                    ) {
                        Box(Modifier.fillMaxSize().padding(vertical = 11.dp), contentAlignment = Alignment.Center) {
                            Text("${formatSimulatorSpeed(option)}×", color = if (selected) Gold else Cream, fontSize = 9.sp, fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal)
                        }
                    }
                }
            }

            Surface(
                modifier = Modifier.fillMaxWidth().clickable { advanced = !advanced },
                shape = RoundedCornerShape(15.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.30f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Tune, null, tint = Gold, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(7.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Controles avançados", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                        Text("Ponto a ponto, próxima cor e velocidades extras", color = Muted, fontSize = 7.sp)
                    }
                    Icon(if (advanced) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold, modifier = Modifier.size(18.dp))
                }
            }

            if (advanced) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    FilledTonalButton(
                        onClick = onPrevious,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                    ) { Text("◀ Ponto", fontSize = 8.sp) }
                    FilledTonalButton(
                        onClick = onNext,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                    ) { Text("Ponto ▶", fontSize = 8.sp) }
                    FilledTonalButton(
                        onClick = onNextColor,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                    ) { Text("Próx. cor", fontSize = 8.sp) }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    listOf(.25f, .5f, 4f).forEach { option ->
                        val selected = kotlin.math.abs(speed - option) < .01f
                        Surface(
                            modifier = Modifier.weight(1f).heightIn(min = 40.dp).clickable(enabled = total > 0) { onSpeed(option) },
                            shape = RoundedCornerShape(13.dp),
                            color = if (selected) Gold.copy(alpha=.18f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.65f) else LineGold.copy(alpha=.28f))
                        ) {
                            Box(Modifier.fillMaxSize().padding(vertical = 9.dp), contentAlignment = Alignment.Center) {
                                Text("${formatSimulatorSpeed(option)}×", color = if (selected) Gold else Muted, fontSize = 8.sp)
                            }
                        }
                    }
                }
                Text(
                    "Bloco ${block.coerceAtLeast(1)} de ${blockTotal.coerceAtLeast(1)} • ${(machinePpm * speed).toInt()} PPM",
                    color = Muted,
                    fontSize = 7.sp
                )
            }
        }
    }
}
'''
text = text[:sim_start] + simulator + text[sim_end:]

# Version bump.
text = text.replace('0.2.29', '0.2.30')
path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 31', 'versionCode = 32')
gradle = gradle.replace('versionName = "0.2.29"', 'versionName = "0.2.30"')
gradle_path.write_text(gradle, encoding='utf-8')

# Sanity checks.
final = path.read_text(encoding='utf-8')
for required in [
    'Ferramentas profissionais',
    'Simular bordado',
    'Controles avançados',
    'LetteringStepper(',
    'TOQUE PARA USAR',
    'Gerar matriz do nome',
    'viewerAdvanced'
]:
    if required not in final:
        raise SystemExit('0.2.30 sanity check failed: ' + required)

print('BORDATTO 0.2.30 simple interaction mode + simplified simulator applied successfully')
