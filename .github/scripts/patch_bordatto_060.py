from pathlib import Path
import runpy

# Build on the validated 0.2.31 source + SDK36 compatibility pin.
runpy.run_path('.github/scripts/patch_bordatto_059.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

start = text.index('@Composable\nprivate fun LetteringSimpleScreen030')
end = text.index('@Composable\nprivate fun MachineScreen', start)

screen = r'''@Composable
private fun LetteringDualModeScreen032(onBack: () -> Unit, onGenerate: (Design) -> Unit) {
    BackHandler(onBack = onBack)

    var mode by remember { mutableStateOf("Rápido") }
    var name by remember { mutableStateOf("Maria") }
    var size by remember { mutableFloatStateOf(42f) }
    var spacing by remember { mutableFloatStateOf(0f) }
    var density by remember { mutableFloatStateOf(.42f) }
    var pullComp by remember { mutableFloatStateOf(.30f) }
    var satinMax by remember { mutableFloatStateOf(9f) }
    var font by remember { mutableStateOf("Elegance") }
    var underlay by remember { mutableStateOf("Center + Edge") }
    var localError by remember { mutableStateOf<String?>(null) }

    // Development APK: Studio mode stays unlocked so the owner can test the full UX.
    // This boolean is the single entitlement hook to connect to BORDATTO Studio / lifetime licensing later.
    val hasStudioAccess032 = true

    val fonts = listOf("Regular", "Elegance", "Classic", "Sweet", "Handwriting")
    val options = remember(size, spacing, density, pullComp, satinMax, underlay, font) {
        LetteringOptions(size, spacing, density, pullComp, satinMax, underlay, font)
    }
    val technicalPreview = remember(name, options, mode) {
        if (mode == "Studio" && name.isNotBlank()) runCatching { generateLetteringDesign(name, options) }.getOrNull() else null
    }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { PageHeader("Criar nome", onBack) }

        item {
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = SurfaceBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .45f))
            ) {
                Column(Modifier.fillMaxWidth().padding(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Como você quer criar?", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Surface(
                            modifier = Modifier.weight(1f).heightIn(min = 64.dp).clickable { mode = "Rápido" },
                            shape = RoundedCornerShape(16.dp),
                            color = if (mode == "Rápido") Gold.copy(alpha = .18f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (mode == "Rápido") Gold else LineGold.copy(alpha=.35f))
                        ) {
                            Column(Modifier.padding(10.dp)) {
                                Text("RÁPIDO", color = if (mode == "Rápido") Gold else Cream, fontWeight = FontWeight.Bold, fontSize = 10.sp)
                                Text("Nome pronto em poucos toques", color = Muted, fontSize = 8.sp, lineHeight = 10.sp)
                            }
                        }
                        Surface(
                            modifier = Modifier.weight(1f).heightIn(min = 64.dp).clickable {
                                if (hasStudioAccess032) mode = "Studio"
                            },
                            shape = RoundedCornerShape(16.dp),
                            color = if (mode == "Studio") Gold.copy(alpha = .18f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (mode == "Studio") Gold else LineGold.copy(alpha=.35f))
                        ) {
                            Column(Modifier.padding(10.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("STUDIO PRO", color = if (mode == "Studio") Gold else Cream, fontWeight = FontWeight.Bold, fontSize = 10.sp)
                                    Spacer(Modifier.weight(1f))
                                    Text(if (hasStudioAccess032) "TESTE" else "🔒", color = Gold, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                                }
                                Text("Controle profissional da matriz", color = Muted, fontSize = 8.sp, lineHeight = 10.sp)
                            }
                        }
                    }
                    Text(
                        if (mode == "Rápido") "Ideal para praticidade: digite, escolha a fonte e o tamanho e gere a matriz."
                        else "BORDATTO Studio / Vitalícia • densidade, compensação, Satin, espaçamento e underlay.",
                        color = Muted,
                        fontSize = 8.sp,
                        lineHeight = 11.sp
                    )
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

        if (mode == "Rápido") {
            item {
                Card(colors = CardDefaults.cardColors(containerColor = Cream), shape = RoundedCornerShape(24.dp)) {
                    Box(
                        Modifier.fillMaxWidth().height(180.dp).padding(horizontal = 12.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            name.ifBlank { "BORDATTO" },
                            color = GoldDeep,
                            fontSize = (size * .82f).coerceIn(20f, 70f).sp,
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

            item {
                Text("Fonte", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
            }
            items(fonts.size) { i ->
                val f = fonts[i]
                val selected = font == f
                Surface(
                    modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).clickable { font = f },
                    shape = RoundedCornerShape(17.dp),
                    color = if (selected) Gold.copy(alpha = .16f) else CardBrown,
                    border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.72f) else LineGold.copy(alpha=.35f))
                ) {
                    Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) {
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
                            modifier = Modifier.weight(1f),
                            maxLines = 1
                        )
                        Text(if (selected) "SELECIONADA" else f, color = if (selected) Gold else Muted, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
            item {
                LetteringSliderControl031(
                    title = "Tamanho",
                    valueLabel = "${"%.0f".format(size)} mm",
                    value = size,
                    valueRange = 10f..90f,
                    onValueChange = { size = it }
                )
            }
            item {
                Surface(
                    shape = RoundedCornerShape(15.dp),
                    color = Gold.copy(alpha=.08f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.32f))
                ) {
                    Text(
                        "Modo rápido usa ajustes seguros automáticos para Satin, compensação e underlay.",
                        color = Muted,
                        fontSize = 8.sp,
                        lineHeight = 11.sp,
                        modifier = Modifier.padding(11.dp)
                    )
                }
            }
        } else {
            item {
                Surface(
                    shape = RoundedCornerShape(18.dp),
                    color = Gold.copy(alpha=.09f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.45f))
                ) {
                    Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        ExpressiveIconBadge(Icons.Rounded.Tune, selected = true, size = 40.dp)
                        Spacer(Modifier.width(9.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Studio Pro", color = Gold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            Text("Os controles abaixo alteram a construção real das pontadas.", color = Muted, fontSize = 8.sp)
                        }
                        Text("0.2.32", color = Gold, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            item {
                Card(colors = CardDefaults.cardColors(containerColor = Ink), shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.42f))) {
                    Column(Modifier.fillMaxWidth().padding(10.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("Prévia técnica da matriz", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 10.sp)
                            Spacer(Modifier.weight(1f))
                            Text("TEMPO REAL", color = Gold, fontWeight = FontWeight.Bold, fontSize = 7.sp)
                        }
                        Box(Modifier.fillMaxWidth().height(220.dp).background(Ink)) {
                            if (technicalPreview != null) {
                                StitchCanvas(
                                    design = technicalPreview,
                                    zoom = 1f,
                                    pan = Offset.Zero,
                                    grid = true,
                                    modifier = Modifier.fillMaxSize()
                                )
                            } else {
                                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                    Text("Digite um nome para gerar a prévia técnica", color = Muted, fontSize = 9.sp)
                                }
                            }
                        }
                        technicalPreview?.let { preview ->
                            Text(
                                "${preview.stitches.size} comandos • ${"%.1f".format(preview.width)} × ${"%.1f".format(preview.height)} mm",
                                color = Gold,
                                fontSize = 8.sp
                            )
                        }
                    }
                }
            }

            item {
                Text("Fonte", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                Spacer(Modifier.height(6.dp))
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    fonts.forEach { f ->
                        val selected = font == f
                        Surface(
                            modifier = Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable { font = f },
                            shape = RoundedCornerShape(14.dp),
                            color = if (selected) Gold.copy(alpha=.15f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold else LineGold.copy(alpha=.32f))
                        ) {
                            Row(Modifier.padding(horizontal = 11.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                                Text(f, color = if (selected) Gold else Cream, fontSize = 9.sp, modifier = Modifier.weight(1f))
                                Text(if (selected) "ATIVA" else "USAR", color = if (selected) Gold else Muted, fontSize = 7.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            item { LetteringSliderControl031("Altura", "${"%.0f".format(size)} mm", size, 10f..90f) { size = it } }
            item { LetteringSliderControl031("Espaçamento", "${"%.0f".format(spacing)}%", spacing, -18f..40f) { spacing = it } }
            item { LetteringSliderControl031("Densidade Satin", "${"%.2f".format(density)} mm", density, .28f..1f) { density = it } }
            item { LetteringSliderControl031("Compensação de puxamento", "${"%.2f".format(pullComp)} mm", pullComp, 0f..1f) { pullComp = it } }
            item { LetteringSliderControl031("Largura máxima Satin", "${"%.1f".format(satinMax)} mm", satinMax, 4f..14f) { satinMax = it } }

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
                            color = if (selected) Gold.copy(alpha=.16f) else CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.62f) else LineGold.copy(alpha=.32f))
                        ) {
                            Row(Modifier.fillMaxWidth().padding(horizontal = 11.dp, vertical = 11.dp), verticalAlignment = Alignment.CenterVertically) {
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
                Text(if (mode == "Rápido") "Gerar matriz do nome" else "Gerar matriz profissional", fontWeight = FontWeight.Bold)
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

text = text[:start] + screen + text[end:]

route_old = 'page == Page.LETTERING -> LetteringSimpleScreen030('
route_new = 'page == Page.LETTERING -> LetteringDualModeScreen032('
if route_old not in text:
    raise SystemExit('0.2.32 lettering route anchor not found')
text = text.replace(route_old, route_new, 1)

main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
if 'versionCode = 33' not in gradle or 'versionName = "0.2.31"' not in gradle:
    raise SystemExit('0.2.32 version anchors not found')
gradle = gradle.replace('versionCode = 33', 'versionCode = 34', 1)
gradle = gradle.replace('versionName = "0.2.31"', 'versionName = "0.2.32"', 1)
gradle_path.write_text(gradle, encoding='utf-8')

required = [
    'private fun LetteringDualModeScreen032(',
    'var mode by remember { mutableStateOf("Rápido") }',
    '"Como você quer criar?"',
    '"RÁPIDO"',
    '"STUDIO PRO"',
    'val hasStudioAccess032 = true',
    '"Prévia técnica da matriz"',
    'technicalPreview',
    'StitchCanvas(',
    '"Modo rápido usa ajustes seguros automáticos',
    '"Gerar matriz profissional"',
    'MachineCheckPanel(',
    'SafeEditorPanel(',
    'EmbroiderySimulatorPanel(',
    'var stitchesVisible031 by remember(workingDesign)',
    'Text("ANALISAR E LOCALIZAR ALERTA"'
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.32 regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.32 Quick + Studio Pro dual lettering mode applied successfully')
