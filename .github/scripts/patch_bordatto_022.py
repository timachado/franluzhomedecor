from pathlib import Path

path = Path("BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt")
text = path.read_text(encoding="utf-8")

replacements = []

replacements.append((
    'Surface(Modifier.fillMaxSize(), color = Ink) {',
    'Surface(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing), color = Ink) {'
))

replacements.append((
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
))

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
                                        "Nova Matriz" -> onSoon("O editor de matriz ponto a ponto está entrando por etapas. Nesta 0.2.2 você já pode testar a linguagem Material 3 Expressive e continuar usando o visualizador DST real.")
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

replacements.append((
    'Text("BORDATTO Studio • Foundation 0.2.1 Expressive", color = Muted.copy(alpha = .7f), fontSize = 11.sp, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center)',
    'Text("BORDATTO Studio • Foundation 0.2.2 Expressive", color = Muted.copy(alpha = .7f), fontSize = 11.sp, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center)'
))

replacements.append((
    'Text("Seu universo de bordados • v0.2.1", color = Muted, fontSize = 10.sp)',
    'Text("Seu universo de bordados • v0.2.2", color = Muted, fontSize = 10.sp)'
))

replacements.append((
    'if (!name.lowercase().endsWith(".dst")) error("Nesta versão 0.2.1, a leitura real implementada continua sendo DST. Os demais formatos entrarão conforme forem validados.")',
    'if (!name.lowercase().endsWith(".dst")) error("Nesta versão 0.2.2, a leitura real implementada continua sendo DST. Os demais formatos entrarão conforme forem validados.")'
))

# Extra breathing room at the bottom of standalone screens so CTA buttons never sit on Android navigation.
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

path.write_text(text, encoding="utf-8")
print("BORDATTO 0.2.2 patch applied successfully")
