from pathlib import Path
import runpy

# Build on the validated 0.2.32 source.
runpy.run_path('.github/scripts/patch_bordatto_060.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

# Quick editor needs direct drag interaction on the name object.
if 'import androidx.compose.foundation.gestures.detectDragGestures' not in text:
    anchor = 'import androidx.compose.foundation.gestures.detectTapGestures\n'
    if anchor not in text:
        raise SystemExit('0.2.33 gesture import anchor not found')
    text = text.replace(anchor, anchor + 'import androidx.compose.foundation.gestures.detectDragGestures\n', 1)

start = text.index('@Composable\nprivate fun LetteringDualModeScreen032')
end = text.index('@Composable\nprivate fun MachineScreen', start)

screen = r'''@Composable
private fun LetteringModeToggle033(
    mode: String,
    hasStudioAccess: Boolean,
    onModeChange: (String) -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .42f))
    ) {
        Row(Modifier.fillMaxWidth().padding(5.dp), horizontalArrangement = Arrangement.spacedBy(5.dp)) {
            listOf("Rápido", "Studio Pro").forEach { label ->
                val studio = label == "Studio Pro"
                val selected = mode == label
                Surface(
                    modifier = Modifier.weight(1f).height(44.dp).clickable {
                        if (!studio || hasStudioAccess) onModeChange(label)
                    },
                    shape = RoundedCornerShape(12.dp),
                    color = if (selected) Gold else CardBrown,
                    border = androidx.compose.foundation.BorderStroke(
                        1.dp,
                        if (selected) Gold else LineGold.copy(alpha = .28f)
                    )
                ) {
                    Row(
                        Modifier.fillMaxSize().padding(horizontal = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        if (studio) {
                            Icon(Icons.Rounded.WorkspacePremium, null, tint = if (selected) Ink else Gold, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(5.dp))
                        }
                        Text(
                            if (studio && !hasStudioAccess) "STUDIO PRO 🔒" else label.uppercase(),
                            color = if (selected) Ink else Cream,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun LetteringDualModeScreen033(onBack: () -> Unit, onGenerate: (Design) -> Unit) {
    BackHandler(onBack = onBack)

    var mode by remember { mutableStateOf("Rápido") }
    var name by remember { mutableStateOf("Maria") }
    var size by remember { mutableFloatStateOf(42f) }
    var spacing by remember { mutableFloatStateOf(0f) }
    var density by remember { mutableFloatStateOf(.42f) }
    var pullComp by remember { mutableFloatStateOf(.30f) }
    var satinMax by remember { mutableFloatStateOf(9f) }
    var font by remember { mutableStateOf("Regular") }
    var underlay by remember { mutableStateOf("Center + Edge") }
    var quickTab by remember { mutableStateOf("Fonte") }
    var quickStyle by remember { mutableStateOf("Normal") }
    var quickColorArgb by remember { mutableStateOf(0xFFD08B4BL) }
    var quickX by remember { mutableFloatStateOf(0f) }
    var quickY by remember { mutableFloatStateOf(0f) }
    var localError by remember { mutableStateOf<String?>(null) }

    // Development APK: unlocked for owner testing. This is the entitlement hook
    // that will later be fed by BORDATTO Studio subscription / lifetime license.
    val hasStudioAccess033 = true

    val quickFonts = listOf("Regular", "Elegance", "Classic", "Handwriting")
    val proFonts = listOf("Regular", "Elegance", "Classic", "Sweet", "Handwriting")
    val quickColors = listOf(
        0xFFD08B4BL,
        0xFF7D4B32L,
        0xFF101010L,
        0xFF1D5C8EL,
        0xFFB12D4AL,
        0xFF5F8D4EL
    )

    val options = remember(size, spacing, density, pullComp, satinMax, underlay, font, mode, quickStyle) {
        val engineFont = if (mode == "Rápido") {
            when (quickStyle) {
                "Itálico" -> if (font == "Handwriting") "Handwriting" else "Elegance"
                "Negrito" -> if (font == "Handwriting") "Handwriting" else "Classic"
                else -> font
            }
        } else font
        LetteringOptions(
            size,
            if (mode == "Rápido") 0f else spacing,
            if (mode == "Rápido") .42f else density,
            if (mode == "Rápido") .30f else pullComp,
            if (mode == "Rápido") 9f else satinMax,
            if (mode == "Rápido") "Center + Edge" else underlay,
            engineFont
        )
    }

    val technicalPreview = remember(name, options, mode) {
        if (mode == "Studio Pro" && name.isNotBlank()) {
            runCatching { generateLetteringDesign(name, options) }.getOrNull()
        } else null
    }

    if (mode == "Rápido") {
        Column(Modifier.fillMaxSize().background(Ink)) {
            Column(Modifier.padding(start = 14.dp, top = 12.dp, end = 14.dp)) {
                PageHeader("Novo nome", onBack)
                Spacer(Modifier.height(8.dp))
                LetteringModeToggle033(mode, hasStudioAccess033) { mode = it }
                Spacer(Modifier.height(8.dp))
            }

            // Traditional quick canvas: the name is edited directly on the hoop.
            Surface(
                modifier = Modifier.fillMaxWidth().weight(1f).padding(horizontal = 12.dp),
                shape = RoundedCornerShape(18.dp),
                color = Color(0xFFF0E8D8),
                border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFB7AA95))
            ) {
                Box(Modifier.fillMaxSize().padding(12.dp)) {
                    Canvas(Modifier.matchParentSize()) {
                        val step = 32f
                        var x = 0f
                        while (x < size.width) {
                            drawLine(Color(0x1A5E5549), Offset(x, 0f), Offset(x, size.height), strokeWidth = 1f)
                            x += step
                        }
                        var y = 0f
                        while (y < size.height) {
                            drawLine(Color(0x1A5E5549), Offset(0f, y), Offset(size.width, y), strokeWidth = 1f)
                            y += step
                        }
                    }

                    Surface(
                        modifier = Modifier.fillMaxSize().padding(18.dp),
                        shape = RoundedCornerShape(18.dp),
                        color = Color.Transparent,
                        border = androidx.compose.foundation.BorderStroke(2.dp, Color(0xFF776D60))
                    ) {}

                    Text(
                        "Bastidor 100 × 100 mm",
                        color = Color(0xFF776D60),
                        fontSize = 7.sp,
                        modifier = Modifier.align(Alignment.TopCenter).padding(top = 22.dp)
                    )

                    Surface(
                        modifier = Modifier
                            .align(Alignment.Center)
                            .offset(x = quickX.dp, y = quickY.dp)
                            .pointerInput(name, size, font) {
                                detectDragGestures { _, dragAmount ->
                                    quickX = (quickX + dragAmount.x / 2.8f).coerceIn(-105f, 105f)
                                    quickY = (quickY + dragAmount.y / 2.8f).coerceIn(-145f, 145f)
                                }
                            },
                        shape = RoundedCornerShape(7.dp),
                        color = Color.Transparent,
                        border = androidx.compose.foundation.BorderStroke(1.dp, Color(quickColorArgb))
                    ) {
                        Box(Modifier.padding(horizontal = 8.dp, vertical = 5.dp), contentAlignment = Alignment.Center) {
                            Text(
                                name.ifBlank { "Nome" },
                                color = Color(quickColorArgb),
                                fontSize = (size * .70f).coerceIn(18f, 58f).sp,
                                fontFamily = when (font) {
                                    "Elegance", "Classic" -> FontFamily.Serif
                                    "Handwriting" -> FontFamily.Cursive
                                    else -> FontFamily.SansSerif
                                },
                                fontWeight = if (quickStyle == "Negrito" || font == "Classic") FontWeight.Bold else FontWeight.Normal,
                                fontStyle = if (quickStyle == "Itálico" || font == "Elegance") FontStyle.Italic else FontStyle.Normal,
                                maxLines = 1,
                                textAlign = TextAlign.Center
                            )
                        }
                    }

                    Surface(
                        modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 10.dp),
                        shape = RoundedCornerShape(12.dp),
                        color = Ink.copy(alpha = .84f)
                    ) {
                        Text(
                            "Arraste o nome para posicionar no bastidor",
                            color = Cream,
                            fontSize = 7.sp,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        )
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Bottom editor follows the reference flow: text + Fonte/Tamanho/Cor/Estilo.
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(topStart = 22.dp, topEnd = 22.dp),
                color = SurfaceBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .40f))
            ) {
                Column(
                    Modifier.fillMaxWidth().padding(start = 14.dp, top = 12.dp, end = 14.dp, bottom = 14.dp),
                    verticalArrangement = Arrangement.spacedBy(9.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Texto", color = Cream, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f))
                        Text(
                            "Concluir",
                            color = Gold,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.clickable {
                                localError = null
                                runCatching {
                                    val generated = generateLetteringDesign(name, options)
                                    generated.copy(stitches = generated.stitches.map { it.copy(color = quickColorArgb.toInt()) })
                                }.onSuccess(onGenerate).onFailure {
                                    localError = it.message ?: "Falha ao gerar o nome."
                                }
                            }.padding(8.dp)
                        )
                    }

                    OutlinedTextField(
                        value = name,
                        onValueChange = { name = it.take(28) },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        placeholder = { Text("Digite o nome") },
                        trailingIcon = { Icon(Icons.Rounded.Keyboard, null, tint = Gold) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Gold,
                            unfocusedBorderColor = LineGold,
                            focusedTextColor = Cream,
                            unfocusedTextColor = Cream
                        )
                    )

                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        listOf("Fonte", "Tamanho", "Cor", "Estilo").forEach { tab ->
                            val selected = quickTab == tab
                            Surface(
                                modifier = Modifier.weight(1f).height(34.dp).clickable { quickTab = tab },
                                shape = RoundedCornerShape(10.dp),
                                color = if (selected) Gold else CardBrown
                            ) {
                                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                    Text(
                                        tab,
                                        color = if (selected) Ink else Cream,
                                        fontSize = 8.sp,
                                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
                                    )
                                }
                            }
                        }
                    }

                    when (quickTab) {
                        "Fonte" -> {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                quickFonts.forEach { f ->
                                    val selected = font == f
                                    Surface(
                                        modifier = Modifier.weight(1f).height(64.dp).clickable { font = f },
                                        shape = RoundedCornerShape(12.dp),
                                        color = if (selected) Gold.copy(alpha = .18f) else CardBrown,
                                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold else LineGold.copy(alpha=.28f))
                                    ) {
                                        Column(Modifier.fillMaxSize().padding(5.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                                            Text(
                                                "Aa",
                                                color = if (selected) Gold else Cream,
                                                fontFamily = when (f) {
                                                    "Elegance", "Classic" -> FontFamily.Serif
                                                    "Handwriting" -> FontFamily.Cursive
                                                    else -> FontFamily.SansSerif
                                                },
                                                fontWeight = if (f == "Classic") FontWeight.Bold else FontWeight.Normal,
                                                fontStyle = if (f == "Elegance") FontStyle.Italic else FontStyle.Normal,
                                                fontSize = 19.sp
                                            )
                                            Text(f.take(7), color = Muted, fontSize = 6.sp, maxLines = 1)
                                        }
                                    }
                                }
                            }
                        }
                        "Tamanho" -> {
                            LetteringSliderControl031(
                                "Tamanho do nome",
                                "${"%.0f".format(size)} mm",
                                size,
                                10f..90f
                            ) { size = it }
                        }
                        "Cor" -> {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                                quickColors.forEach { c ->
                                    val selected = quickColorArgb == c
                                    Surface(
                                        modifier = Modifier.size(if (selected) 42.dp else 36.dp).clickable { quickColorArgb = c },
                                        shape = CircleShape,
                                        color = Color(c),
                                        border = androidx.compose.foundation.BorderStroke(if (selected) 3.dp else 1.dp, if (selected) Cream else LineGold)
                                    ) {}
                                }
                            }
                        }
                        else -> {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                                listOf("Normal", "Negrito", "Itálico").forEach { style ->
                                    val selected = quickStyle == style
                                    Surface(
                                        modifier = Modifier.weight(1f).height(46.dp).clickable { quickStyle = style },
                                        shape = RoundedCornerShape(12.dp),
                                        color = if (selected) Gold else CardBrown,
                                        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold else LineGold.copy(alpha=.28f))
                                    ) {
                                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                            Text(
                                                style,
                                                color = if (selected) Ink else Cream,
                                                fontSize = 8.sp,
                                                fontWeight = if (style == "Negrito") FontWeight.Bold else FontWeight.Normal,
                                                fontStyle = if (style == "Itálico") FontStyle.Italic else FontStyle.Normal
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Button(
                        onClick = {
                            localError = null
                            runCatching {
                                val generated = generateLetteringDesign(name, options)
                                generated.copy(stitches = generated.stitches.map { it.copy(color = quickColorArgb.toInt()) })
                            }.onSuccess(onGenerate).onFailure {
                                localError = it.message ?: "Falha ao gerar o nome."
                            }
                        },
                        enabled = name.isNotBlank(),
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                    ) {
                        Icon(Icons.Rounded.PlayArrow, null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("CONCLUIR E GERAR MATRIZ", fontSize = 9.sp, fontWeight = FontWeight.Bold)
                    }

                    localError?.let { Text(it, color = Gold, fontSize = 8.sp) }
                }
            }
        }
    } else {
        // Studio Pro is intentionally a separate professional experience.
        LazyColumn(
            Modifier.fillMaxSize(),
            contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 30.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item { PageHeader("Lettering Studio Pro", onBack) }
            item { LetteringModeToggle033(mode, hasStudioAccess033) { mode = it } }

            item {
                Surface(
                    shape = RoundedCornerShape(18.dp),
                    color = Gold.copy(alpha=.09f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.45f))
                ) {
                    Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        ExpressiveIconBadge(Icons.Rounded.WorkspacePremium, selected = true, size = 42.dp)
                        Spacer(Modifier.width(9.dp))
                        Column(Modifier.weight(1f)) {
                            Text("BORDATTO Studio Pro", color = Gold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            Text("Assinatura Studio ou licença vitalícia", color = Muted, fontSize = 8.sp)
                        }
                        Text("PRO", color = Gold, fontSize = 8.sp, fontWeight = FontWeight.Bold)
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
                Card(
                    colors = CardDefaults.cardColors(containerColor = Ink),
                    shape = RoundedCornerShape(22.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.42f))
                ) {
                    Column(Modifier.fillMaxWidth().padding(10.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("Prévia técnica das pontadas", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 10.sp)
                            Spacer(Modifier.weight(1f))
                            Text("TEMPO REAL", color = Gold, fontWeight = FontWeight.Bold, fontSize = 7.sp)
                        }
                        Box(Modifier.fillMaxWidth().height(230.dp).background(Ink)) {
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
                Text("Fonte profissional", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                Spacer(Modifier.height(6.dp))
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    proFonts.forEach { f ->
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

            item {
                Button(
                    onClick = {
                        localError = null
                        runCatching { generateLetteringDesign(name, options) }
                            .onSuccess(onGenerate)
                            .onFailure { localError = it.message ?: "Falha ao gerar o lettering profissional." }
                    },
                    enabled = name.isNotBlank(),
                    modifier = Modifier.fillMaxWidth().height(58.dp),
                    shape = RoundedCornerShape(20.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                ) {
                    Icon(Icons.Rounded.AutoAwesome, null)
                    Spacer(Modifier.width(8.dp))
                    Text("GERAR MATRIZ PROFISSIONAL", fontWeight = FontWeight.Bold)
                }
            }

            localError?.let { message ->
                item {
                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = Gold.copy(alpha=.08f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.5f))
                    ) {
                        Text(message, color = Cream, fontSize = 10.sp, modifier = Modifier.padding(11.dp))
                    }
                }
            }
        }
    }
}

'''

text = text[:start] + screen + text[end:]

route_old = 'page == Page.LETTERING -> LetteringDualModeScreen032('
route_new = 'page == Page.LETTERING -> LetteringDualModeScreen033('
if route_old not in text:
    raise SystemExit('0.2.33 lettering route anchor not found')
text = text.replace(route_old, route_new, 1)

main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
if 'versionCode = 34' not in gradle or 'versionName = "0.2.32"' not in gradle:
    raise SystemExit('0.2.33 version anchors not found')
gradle = gradle.replace('versionCode = 34', 'versionCode = 35', 1)
gradle = gradle.replace('versionName = "0.2.32"', 'versionName = "0.2.33"', 1)
gradle_path.write_text(gradle, encoding='utf-8')

required = [
    'private fun LetteringDualModeScreen033(',
    'private fun LetteringModeToggle033(',
    '"Novo nome"',
    '"Bastidor 100 × 100 mm"',
    'detectDragGestures',
    'listOf("Fonte", "Tamanho", "Cor", "Estilo")',
    '"CONCLUIR E GERAR MATRIZ"',
    '"Lettering Studio Pro"',
    '"Prévia técnica das pontadas"',
    '"Densidade Satin"',
    '"Compensação de puxamento"',
    '"Largura máxima Satin"',
    '"GERAR MATRIZ PROFISSIONAL"',
    'MachineCheckPanel(',
    'SafeEditorPanel(',
    'EmbroiderySimulatorPanel(',
    'var stitchesVisible031 by remember(workingDesign)',
    'Text("ANALISAR E LOCALIZAR ALERTA"'
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.33 regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.33 traditional Quick canvas + isolated Studio Pro lettering applied successfully')
