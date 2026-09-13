from pathlib import Path

path = Path("BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt")
text = path.read_text(encoding="utf-8")

# Keep all validated 0.2.2 safe-area and Home fixes.
replacements = [
    (
        'Surface(Modifier.fillMaxSize(), color = Ink) {',
        'Surface(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing), color = Ink) {'
    ),
    (
'''private fun ExpressiveIconBadge(icon: ImageVector, selected: Boolean = false, size: androidx.compose.ui.unit.Dp = 46.dp) {
    val scale by animateFloatAsState(if (selected) 1.06f else 1f, label = "badgeScale")
    Box(
        modifier = Modifier
            .size(size)
            .scale(scale)
            .clip(RoundedCornerShape(if (selected) 18.dp else 14.dp))
            .background(if (selected) Gold.copy(alpha = .16f) else CardBrown2)
            .border(1.dp, if (selected) Gold.copy(alpha = .42f) else LineGold.copy(alpha = .55f), RoundedCornerShape(if (selected) 18.dp else 14.dp)),
        contentAlignment = Alignment.Center
    ) {
        Icon(icon, null, tint = Gold, modifier = Modifier.size(size * .52f))
    }
}''',
'''private fun ExpressiveIconBadge(icon: ImageVector, selected: Boolean = false, size: androidx.compose.ui.unit.Dp = 46.dp) {
    val iconScale by animateFloatAsState(if (selected) 1.08f else 1f, label = "badgeIconScale")
    val shape = RoundedCornerShape(if (selected) 18.dp else 14.dp)
    Box(
        modifier = Modifier
            .size(size)
            .clip(shape)
            .background(if (selected) Gold.copy(alpha = .16f) else CardBrown2)
            .border(1.dp, if (selected) Gold.copy(alpha = .42f) else LineGold.copy(alpha = .55f), shape),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            icon,
            null,
            tint = Gold,
            modifier = Modifier
                .size(size * .46f)
                .scale(iconScale)
        )
    }
}'''
    )
]

old_grid = '''        item {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.height(454.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                userScrollEnabled = false
            ) {
                items(actions) { action ->
                    LuxuryActionCard(action) {
                        when (action.title) {
                            "Abrir Matriz" -> onOpen()
                            "Criar Nome" -> onLettering()
                            "Minha Máquina" -> onMachine()
                            "Nova Matriz" -> onSoon("O editor de matriz ponto a ponto está entrando por etapas. Nesta 0.2.1 você já pode testar a nova linguagem visual Expressive e continuar usando o visualizador DST real.")
                            "Digitalizar Imagem" -> onSoon("A digitalização automática será conectada ao motor de vetorização e geração de pontos em uma próxima versão.")
                            "PhotoStitch" -> onSoon("O modo PhotoStitch está no roadmap. Primeiro vamos estabilizar visualizador, projetos, lettering e editor.")
                            "Projetos" -> onSoon("Use a aba Projetos na barra inferior. A persistência local chega na próxima etapa.")
                            "Biblioteca" -> onSoon("Use a aba Biblioteca na barra inferior para ver a estrutura inicial.")
                        }
                    }
                }
            }
        }'''

new_grid = '''        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                actions.chunked(2).forEach { rowActions ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        rowActions.forEach { action ->
                            Box(Modifier.weight(1f)) {
                                LuxuryActionCard(action) {
                                    when (action.title) {
                                        "Abrir Matriz" -> onOpen()
                                        "Criar Nome" -> onLettering()
                                        "Minha Máquina" -> onMachine()
                                        "Nova Matriz" -> onSoon("O editor de matriz ponto a ponto está entrando por etapas. Nesta 0.2.3 você já pode testar a linguagem Material 3 Expressive e continuar usando o visualizador DST real.")
                                        "Digitalizar Imagem" -> onSoon("A digitalização automática será conectada ao motor de vetorização e geração de pontos em uma próxima versão.")
                                        "PhotoStitch" -> onSoon("O modo PhotoStitch está no roadmap. Primeiro vamos estabilizar visualizador, projetos, lettering e editor.")
                                        "Projetos" -> onSoon("Use a aba Projetos na barra inferior. A persistência local chega na próxima etapa.")
                                        "Biblioteca" -> onSoon("Use a aba Biblioteca na barra inferior para ver a estrutura inicial.")
                                    }
                                }
                            }
                        }
                        if (rowActions.size == 1) Spacer(Modifier.weight(1f))
                    }
                }
            }
        }'''
replacements.append((old_grid, new_grid))

# Extra breathing room on standalone screens.
replacements.append((
    'LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {\n        item { PageHeader("Criar Nome", onBack) }',
    'LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {\n        item { PageHeader("Criar Nome", onBack) }'
))
replacements.append((
    'LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {\n        item { PageHeader("Minha Máquina", onBack) }',
    'LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {\n        item { PageHeader("Minha Máquina", onBack) }'
))

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Expected source block not found:\n{old[:180]}")
    text = text.replace(old, new, 1)

# Replace the whole lettering screen with a real interactive visual preview.
start = text.index('@Composable\nprivate fun LetteringScreen')
end = text.index('@Composable\nprivate fun MachineScreen', start)

new_lettering = r'''private data class LetteringStyle(
    val name: String,
    val family: FontFamily,
    val weight: FontWeight,
    val style: FontStyle,
    val tracking: Float,
    val previewScale: Float
)

@Composable
private fun LetteringScreen(onBack: () -> Unit, onGenerate: () -> Unit) {
    BackHandler(onBack = onBack)
    var name by remember { mutableStateOf("Maria") }
    var size by remember { mutableFloatStateOf(50f) }
    var spacing by remember { mutableFloatStateOf(0f) }
    var font by remember { mutableStateOf("Elegance") }

    val styles = listOf(
        LetteringStyle("Regular", FontFamily.SansSerif, FontWeight.Medium, FontStyle.Normal, 0.0f, 1.00f),
        LetteringStyle("Elegance", FontFamily.Cursive, FontWeight.Normal, FontStyle.Italic, 0.2f, 1.08f),
        LetteringStyle("Classic", FontFamily.Serif, FontWeight.SemiBold, FontStyle.Normal, 0.6f, 1.00f),
        LetteringStyle("Sweet", FontFamily.Serif, FontWeight.Light, FontStyle.Italic, 1.4f, 0.96f),
        LetteringStyle("Handwriting", FontFamily.Cursive, FontWeight.Bold, FontStyle.Normal, -0.2f, 1.12f)
    )
    val selectedStyle = styles.first { it.name == font }
    val previewSize by animateFloatAsState(
        targetValue = (34f + (size.coerceIn(10f, 150f) / 150f) * 36f) * selectedStyle.previewScale,
        label = "letteringPreviewSize"
    )
    val previewTracking by animateFloatAsState(
        targetValue = selectedStyle.tracking + spacing / 8f,
        label = "letteringTracking"
    )

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item { PageHeader("Criar Nome", onBack) }
        item {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Nome") },
                leadingIcon = { Icon(Icons.Rounded.TextFields, null, tint = Gold) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Gold,
                    unfocusedBorderColor = LineGold,
                    focusedLabelColor = Gold
                )
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Cream), shape = RoundedCornerShape(28.dp)) {
                Box(Modifier.fillMaxWidth().height(205.dp)) {
                    Surface(
                        modifier = Modifier.align(Alignment.TopEnd).padding(12.dp),
                        shape = RoundedCornerShape(50),
                        color = GoldDeep.copy(alpha = .12f)
                    ) {
                        Text(
                            selectedStyle.name,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            color = GoldDeep,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                    Text(
                        text = name.ifBlank { "BORDATTO" },
                        color = GoldDeep,
                        fontSize = previewSize.sp,
                        fontFamily = selectedStyle.family,
                        fontWeight = selectedStyle.weight,
                        fontStyle = selectedStyle.style,
                        letterSpacing = previewTracking.sp,
                        textAlign = TextAlign.Center,
                        maxLines = 1,
                        modifier = Modifier.align(Alignment.Center).padding(horizontal = 18.dp)
                    )
                    Row(
                        Modifier.align(Alignment.BottomCenter).padding(bottom = 13.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Rounded.TouchApp, null, tint = GoldDeep.copy(alpha = .72f), modifier = Modifier.size(15.dp))
                        Spacer(Modifier.width(5.dp))
                        Text("Prévia em tempo real", color = GoldDeep.copy(alpha = .72f), fontSize = 10.sp)
                    }
                }
            }
        }
        item {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("Estilo da fonte", color = Cream, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .14f)) {
                    Text(font, color = Gold, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp))
                }
            }
        }
        items(styles.size) { i ->
            val current = styles[i]
            val selected = font == current.name
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { font = current.name },
                shape = RoundedCornerShape(if (selected) 24.dp else 18.dp),
                color = if (selected) Gold.copy(alpha=.16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.68f) else LineGold.copy(alpha=.45f))
            ) {
                Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.TextFields, selected = selected, size = 42.dp)
                    Spacer(Modifier.width(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text(
                            text = name.ifBlank { "Maria" },
                            color = Cream,
                            fontFamily = current.family,
                            fontWeight = current.weight,
                            fontStyle = current.style,
                            letterSpacing = current.tracking.sp,
                            fontSize = (21f * current.previewScale).sp,
                            maxLines = 1
                        )
                        Text(current.name, color = if (selected) Gold else Muted, fontSize = 10.sp)
                    }
                    if (selected) {
                        Surface(shape = CircleShape, color = Gold) {
                            Icon(Icons.Rounded.Check, "Selecionado", tint = Ink, modifier = Modifier.padding(5.dp).size(16.dp))
                        }
                    } else {
                        Icon(Icons.Rounded.ChevronRight, null, tint = Muted, modifier = Modifier.size(22.dp))
                    }
                }
            }
        }
        item {
            Surface(
                color = CardBrown,
                shape = RoundedCornerShape(22.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .45f))
            ) {
                Column(Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Straighten, null, tint = Gold, modifier = Modifier.size(19.dp))
                        Spacer(Modifier.width(7.dp))
                        Text("Tamanho: ${size.toInt()} mm", color = Cream, modifier = Modifier.weight(1f))
                        Text("visual", color = Muted, fontSize = 10.sp)
                    }
                    Slider(size, { size = it }, valueRange = 10f..150f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
                    Spacer(Modifier.height(4.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.SpaceBar, null, tint = Gold, modifier = Modifier.size(19.dp))
                        Spacer(Modifier.width(7.dp))
                        Text("Espaçamento: ${spacing.toInt()}%", color = Cream)
                    }
                    Slider(spacing, { spacing = it }, valueRange = -20f..50f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
                }
            }
        }
        item {
            Button(
                onClick = onGenerate,
                modifier = Modifier.fillMaxWidth().height(58.dp),
                shape = RoundedCornerShape(22.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(Icons.Rounded.AutoAwesome, null)
                Spacer(Modifier.width(8.dp))
                Text("Gerar Matriz", fontWeight = FontWeight.Bold)
            }
        }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.Info, null, tint = Muted, modifier = Modifier.size(14.dp))
                Spacer(Modifier.width(5.dp))
                Text("Nesta etapa a prévia é tipográfica. A conversão em pontos de bordado entra no motor de lettering.", color = Muted, fontSize = 9.sp, textAlign = TextAlign.Center)
            }
        }
    }
}

'''

text = text[:start] + new_lettering + text[end:]

# Version labels/messages for this build.
text = text.replace("0.2.1", "0.2.3")
text = text.replace("0.2.2", "0.2.3")

path.write_text(text, encoding="utf-8")
print("BORDATTO 0.2.3 lettering preview patch applied successfully")
