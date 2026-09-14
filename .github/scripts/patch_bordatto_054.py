from pathlib import Path
import runpy

# Always rebuild from the validated 0.2.29 base. Do not delete/replace existing feature blocks.
runpy.run_path('.github/scripts/patch_bordatto_052.py', run_name='__main__')

path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# 0.2.30 LETTERING — add a new casual-first screen and keep legacy screen intact.
# -----------------------------------------------------------------------------
lettering_simple = r'''
@Composable
private fun LetteringStepper030(
    title: String,
    value: String,
    onMinus: () -> Unit,
    onPlus: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = CardBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
    ) {
        Row(
            Modifier.fillMaxWidth().padding(10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(Modifier.weight(1f)) {
                Text(title, color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                Text(value, color = Gold, fontSize = 13.sp, fontWeight = FontWeight.Bold)
            }
            OutlinedButton(
                onClick = onMinus,
                modifier = Modifier.size(48.dp),
                contentPadding = PaddingValues(0.dp),
                shape = RoundedCornerShape(14.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .60f))
            ) {
                Text("−", color = Gold, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.width(8.dp))
            Button(
                onClick = onPlus,
                modifier = Modifier.size(48.dp),
                contentPadding = PaddingValues(0.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Text("+", fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun LetteringSimpleScreen030(onBack: () -> Unit, onGenerate: (Design) -> Unit) {
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
        contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { PageHeader("Criar nome", onBack) }

        item {
            Surface(
                shape = RoundedCornerShape(18.dp),
                color = Gold.copy(alpha = .08f),
                border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .38f))
            ) {
                Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.AutoAwesome, selected = true, size = 42.dp)
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Lettering Satin", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                        Text("Nome, fonte e tamanho. Os ajustes técnicos ficam opcionais.", color = Muted, fontSize = 9.sp)
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
                Box(
                    Modifier.fillMaxWidth().height(160.dp).padding(horizontal = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
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
                modifier = Modifier.fillMaxWidth().heightIn(min = 60.dp).clickable { font = f },
                shape = RoundedCornerShape(18.dp),
                color = if (selected) Gold.copy(alpha = .16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(
                    1.dp,
                    if (selected) Gold.copy(alpha = .72f) else LineGold.copy(alpha = .38f)
                )
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
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
                        Text(
                            if (selected) "SELECIONADA" else "TOQUE PARA USAR",
                            color = if (selected) Gold else Muted,
                            fontSize = 6.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }

        item {
            LetteringStepper030(
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

        item {
            Surface(
                modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).clickable { advanced = !advanced },
                shape = RoundedCornerShape(17.dp),
                color = SurfaceBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .38f))
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
                            modifier = Modifier.fillMaxWidth().heightIn(min = 46.dp).clickable { underlay = value },
                            shape = RoundedCornerShape(14.dp),
                            color = if (selected) Gold.copy(alpha = .16f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (selected) Gold.copy(alpha = .62f) else LineGold.copy(alpha = .32f)
                            )
                        ) {
                            Row(
                                Modifier.fillMaxWidth().padding(horizontal = 11.dp, vertical = 11.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(label, color = if (selected) Gold else Cream, fontSize = 9.sp, modifier = Modifier.weight(1f))
                                Text(
                                    if (selected) "ATIVO" else "USAR",
                                    color = if (selected) Gold else Muted,
                                    fontSize = 7.sp,
                                    fontWeight = FontWeight.Bold
                                )
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
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = Gold.copy(alpha = .08f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .5f))
                ) {
                    Text(message, color = Cream, fontSize = 10.sp, modifier = Modifier.padding(11.dp))
                }
            }
        }
    }
}

'''

machine_anchor = '@Composable\nprivate fun MachineScreen'
if machine_anchor not in text:
    raise SystemExit('0.2.30 machine insertion anchor not found')
text = text.replace(machine_anchor, lettering_simple + machine_anchor, 1)

route_anchor = 'page == Page.LETTERING -> LetteringScreen('
if route_anchor not in text:
    raise SystemExit('0.2.30 lettering route anchor not found')
text = text.replace(route_anchor, 'page == Page.LETTERING -> LetteringSimpleScreen030(', 1)

# -----------------------------------------------------------------------------
# 0.2.30 VIEWER — canvas-first; advanced technical panels collapsed by default.
# -----------------------------------------------------------------------------
old_state = '    var grid by remember { mutableStateOf(true) }\n    var info by remember { mutableStateOf(true) }'
new_state = '    var grid by remember { mutableStateOf(true) }\n    var info by remember { mutableStateOf(false) }\n    var viewerAdvanced030 by remember { mutableStateOf(false) }'
if old_state not in text:
    raise SystemExit('0.2.30 viewer state anchor not found')
text = text.replace(old_state, new_state, 1)

panel_anchor = '        MachineCheckPanel(workingDesign, machineConfig)'
panel_open = r'''        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 10.dp, vertical = 5.dp)
                .heightIn(min = 58.dp)
                .clickable { viewerAdvanced030 = !viewerAdvanced030 },
            shape = RoundedCornerShape(18.dp),
            color = SurfaceBrown,
            border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
        ) {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 11.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Rounded.Settings, null, tint = Gold, modifier = Modifier.size(19.dp))
                Spacer(Modifier.width(8.dp))
                Column(Modifier.weight(1f)) {
                    Text("Ferramentas profissionais", color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                    Text("Analyzer • Editor • Cores • Exportação", color = Muted, fontSize = 8.sp)
                }
                Text(if (viewerAdvanced030) "FECHAR" else "ABRIR", color = Gold, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.width(4.dp))
                Icon(if (viewerAdvanced030) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold)
            }
        }
        if (viewerAdvanced030) {
        MachineCheckPanel(workingDesign, machineConfig)'''
if panel_anchor not in text:
    raise SystemExit('0.2.30 professional tools anchor not found')
text = text.replace(panel_anchor, panel_open, 1)

canvas_anchor = '        Box(\n            Modifier.height(360.dp).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
canvas_new = '        }\n        Box(\n            Modifier.height(420.dp).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
if canvas_anchor not in text:
    raise SystemExit('0.2.30 viewer canvas anchor not found')
text = text.replace(canvas_anchor, canvas_new, 1)

# -----------------------------------------------------------------------------
# 0.2.30 SIMULATOR — add a simple facade; preserve old advanced implementation.
# -----------------------------------------------------------------------------
simulator_simple = r'''
@Composable
private fun SimpleEmbroiderySimulatorPanel030(
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
    val progress = if (total <= 0) 0f else (current.toFloat() / total.toFloat()).coerceIn(0f, 1f)
    val percent = (progress * 100f).toInt()
    var advanced030 by remember { mutableStateOf(false) }

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
                    Text(
                        "${formatSimulatorSpeed(speed)}×",
                        color = Gold,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp)
                    )
                }
            }

            Box(
                Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(50)).background(LineGold.copy(alpha = .30f))
            ) {
                Box(Modifier.fillMaxWidth(progress).fillMaxHeight().background(Gold))
            }

            Button(
                onClick = onPlayPause,
                enabled = total > 0,
                modifier = Modifier.fillMaxWidth().height(54.dp),
                shape = RoundedCornerShape(18.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, null)
                Spacer(Modifier.width(7.dp))
                Text(
                    if (playing) "Pausar simulação"
                    else if (current > 0 && current < total) "Continuar simulação"
                    else "Iniciar simulação",
                    fontWeight = FontWeight.Bold
                )
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(
                    onClick = onStop,
                    enabled = total > 0,
                    modifier = Modifier.weight(1.25f).height(46.dp),
                    shape = RoundedCornerShape(15.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .50f))
                ) {
                    Icon(Icons.Rounded.Refresh, null, tint = Gold, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(5.dp))
                    Text("Reiniciar", color = Gold, fontSize = 9.sp)
                }

                listOf(1f, 2f).forEach { option ->
                    val selected = kotlin.math.abs(speed - option) < .01f
                    Surface(
                        modifier = Modifier.weight(.8f).height(46.dp).clickable(enabled = total > 0) { onSpeed(option) },
                        shape = RoundedCornerShape(15.dp),
                        color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                        border = androidx.compose.foundation.BorderStroke(
                            1.dp,
                            if (selected) Gold.copy(alpha = .65f) else LineGold.copy(alpha = .32f)
                        )
                    ) {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text(
                                "${formatSimulatorSpeed(option)}×",
                                color = if (selected) Gold else Cream,
                                fontSize = 9.sp,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    }
                }
            }

            Surface(
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).clickable { advanced030 = !advanced030 },
                shape = RoundedCornerShape(15.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .30f))
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 9.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Rounded.Tune, null, tint = Gold, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(7.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Controles avançados", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                        Text("Ponto a ponto, próxima cor e velocidades extras", color = Muted, fontSize = 7.sp)
                    }
                    Text(if (advanced030) "FECHAR" else "ABRIR", color = Gold, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.width(3.dp))
                    Icon(if (advanced030) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold, modifier = Modifier.size(18.dp))
                }
            }

            if (advanced030) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    OutlinedButton(
                        onClick = onPrevious,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f).height(44.dp),
                        contentPadding = PaddingValues(horizontal = 6.dp),
                        shape = RoundedCornerShape(14.dp)
                    ) { Text("◀ Ponto", color = Gold, fontSize = 8.sp) }

                    OutlinedButton(
                        onClick = onNext,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f).height(44.dp),
                        contentPadding = PaddingValues(horizontal = 6.dp),
                        shape = RoundedCornerShape(14.dp)
                    ) { Text("Ponto ▶", color = Gold, fontSize = 8.sp) }

                    OutlinedButton(
                        onClick = onNextColor,
                        enabled = total > 0,
                        modifier = Modifier.weight(1f).height(44.dp),
                        contentPadding = PaddingValues(horizontal = 6.dp),
                        shape = RoundedCornerShape(14.dp)
                    ) { Text("Próx. cor", color = Gold, fontSize = 8.sp) }
                }

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    listOf(.25f, .5f, 4f).forEach { option ->
                        val selected = kotlin.math.abs(speed - option) < .01f
                        Surface(
                            modifier = Modifier.weight(1f).height(42.dp).clickable(enabled = total > 0) { onSpeed(option) },
                            shape = RoundedCornerShape(13.dp),
                            color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (selected) Gold.copy(alpha = .65f) else LineGold.copy(alpha = .28f)
                            )
                        ) {
                            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                Text(
                                    "${formatSimulatorSpeed(option)}×",
                                    color = if (selected) Gold else Muted,
                                    fontSize = 8.sp
                                )
                            }
                        }
                    }
                }

                Text(
                    "Cor/bloco ${block.coerceAtLeast(1)} de ${blockTotal.coerceAtLeast(1)} • ${(machinePpm * speed).toInt()} PPM",
                    color = Muted,
                    fontSize = 7.sp
                )
            }
        }
    }
}

'''

sim_decl_anchor = '@Composable\nprivate fun EmbroiderySimulatorPanel('
if sim_decl_anchor not in text:
    raise SystemExit('0.2.30 simulator declaration anchor not found')
text = text.replace(sim_decl_anchor, simulator_simple + sim_decl_anchor, 1)

sim_call_anchor = '        EmbroiderySimulatorPanel(\n            current = simulatorPosition,'
if sim_call_anchor not in text:
    raise SystemExit('0.2.30 simulator call anchor not found')
text = text.replace(
    sim_call_anchor,
    '        SimpleEmbroiderySimulatorPanel030(\n            current = simulatorPosition,',
    1
)

# Make the existing top-level viewer pills feel like real controls on touch screens.
viewer_tool_anchor = 'Surface(modifier = Modifier.clickable(onClick = onClick), shape = RoundedCornerShape(18.dp)'
if viewer_tool_anchor in text:
    text = text.replace(
        viewer_tool_anchor,
        'Surface(modifier = Modifier.heightIn(min = 44.dp).clickable(onClick = onClick), shape = RoundedCornerShape(18.dp)',
        1
    )

# Version bump.
text = text.replace('0.2.29', '0.2.30')
path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 31', 'versionCode = 32')
gradle = gradle.replace('versionName = "0.2.29"', 'versionName = "0.2.30"')
gradle_path.write_text(gradle, encoding='utf-8')

# Regression guards: these declarations were accidentally deleted by the first 0.2.30 attempt.
required = [
    'private data class MachineConfig',
    'private fun loadMachineConfig',
    'private data class LibraryItem',
    'private fun CostCalculatorScreen',
    'private fun appPrefs',
    'LetteringSimpleScreen030',
    'Ferramentas profissionais',
    'SimpleEmbroiderySimulatorPanel030',
    'Controles avançados',
    'TOQUE PARA USAR',
    'Gerar matriz do nome'
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.30 regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.30 safe casual-first interaction patch applied successfully')
