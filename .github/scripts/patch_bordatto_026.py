from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_025.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Route the calculator before the viewer so an open design can remain in memory while costs are shown.
old = '''            when {
                splash -> SplashScreen()
                design != null -> ViewerScreen(design!!) { design = null }
                page == Page.LETTERING -> LetteringScreen('''
new = '''            when {
                splash -> SplashScreen()
                page == Page.COSTS -> CostCalculatorScreen(
                    design = design,
                    onBack = { page = Page.MAIN }
                )
                design != null -> ViewerScreen(
                    design = design!!,
                    onBack = { design = null },
                    onCosts = { page = Page.COSTS }
                )
                page == Page.LETTERING -> LetteringScreen('''
if old not in text: raise SystemExit('main route block not found')
text = text.replace(old, new, 1)

old = '                page == Page.COSTS -> CostCalculatorScreen(onBack = { page = Page.MAIN })\n'
if old not in text: raise SystemExit('old costs route not found')
text = text.replace(old, '', 1)

# Upgrade calculator to accept an open design and calculate technical estimates.
old = '''@Composable
private fun CostCalculatorScreen(onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var materials by remember { mutableStateOf("7,20") }
    var laborHour by remember { mutableStateOf("20,00") }
    var machineHour by remember { mutableStateOf("8,00") }
    var minutes by remember { mutableStateOf("15") }'''
new = '''@Composable
private fun CostCalculatorScreen(design: Design? = null, onBack: () -> Unit) {
    BackHandler(onBack = onBack)

    val estimatedThreadMeters = remember(design) {
        if (design == null) 0.0 else {
            var totalMm = 0.0
            var previous: StitchPoint? = null
            design.stitches.forEach { current ->
                if (current.command == StitchCommand.STITCH) {
                    val prev = previous
                    if (prev != null && prev.command == StitchCommand.STITCH && prev.color == current.color) {
                        totalMm += kotlin.math.hypot(
                            (current.x - prev.x).toDouble(),
                            (current.y - prev.y).toDouble()
                        )
                    }
                    previous = current
                } else {
                    previous = null
                }
            }
            (totalMm / 1000.0) * 1.12
        }
    }
    val estimatedMinutes = remember(design) {
        design?.let {
            maxOf(1.0, (it.stitchCount / 700.0) + (it.colorChanges * 0.45) + (it.jumpCount * 0.015))
        } ?: 0.0
    }

    var materials by remember { mutableStateOf("7,20") }
    var laborHour by remember { mutableStateOf("20,00") }
    var machineHour by remember { mutableStateOf("8,00") }
    var minutes by remember(design) {
        mutableStateOf(if (design != null) kotlin.math.ceil(estimatedMinutes).toInt().toString() else "15")
    }
    var timeFromMatrix by remember(design) { mutableStateOf(design != null) }'''
if old not in text: raise SystemExit('calculator header not found')
text = text.replace(old, new, 1)

# Add design analysis card under calculator intro card.
marker = '''        item { CostField("Materiais por peça", materials) { materials = it } }'''
insert = '''        if (design != null) {
            item {
                Surface(
                    color = Gold.copy(alpha = .10f),
                    shape = RoundedCornerShape(24.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .58f))
                ) {
                    Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            ExpressiveIconBadge(Icons.Rounded.Analytics, selected = true, size = 42.dp)
                            Spacer(Modifier.width(10.dp))
                            Column(Modifier.weight(1f)) {
                                Text("Dados da matriz", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                                Text(design.name, color = Cream, fontSize = 11.sp, maxLines = 1)
                            }
                            Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .15f)) {
                                Text("DST", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                            }
                        }
                        HorizontalDivider(color = LineGold.copy(alpha = .46f))
                        CostRow("Pontadas", "${design.stitchCount}")
                        CostRow("Dimensões", "${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm")
                        CostRow("Cores", "${design.colors}")
                        CostRow("Saltos", "${design.jumpCount}")
                        CostRow("Linha estimada + 12%", "${"%.1f".format(estimatedThreadMeters)} m")
                        CostRow("Tempo estimado", "≈ ${kotlin.math.ceil(estimatedMinutes).toInt()} min")
                        Text(
                            "Tempo e consumo são estimativas iniciais; a velocidade real da máquina, cortes, trocas e configuração do bordado podem alterar o resultado.",
                            color = Muted,
                            fontSize = 8.sp,
                            lineHeight = 11.sp
                        )
                    }
                }
            }
        }
        item { CostField("Materiais por peça", materials) { materials = it } }'''
if marker not in text: raise SystemExit('calculator material marker not found')
text = text.replace(marker, insert, 1)

old = '''                CostField("Tempo (min)", minutes, Modifier.weight(1f), false) { minutes = it }
                CostField("Custos extras", extras, Modifier.weight(1f)) { extras = it }'''
new = '''                CostField("Tempo (min)", minutes, Modifier.weight(1f), false) {
                    minutes = it
                    timeFromMatrix = false
                }
                CostField("Custos extras", extras, Modifier.weight(1f)) { extras = it }'''
if old not in text: raise SystemExit('time field block not found')
text = text.replace(old, new, 1)

# Show when time was populated from the matrix and provide a one-tap restore.
old = '''        item { CostField("Quantidade", quantity, moneyPrefix = false) { quantity = it } }
        item {
            Surface(shape = RoundedCornerShape(22.dp), color = CardBrown,'''
new = '''        if (design != null) {
            item {
                Surface(
                    modifier = Modifier.fillMaxWidth().clickable {
                        minutes = kotlin.math.ceil(estimatedMinutes).toInt().toString()
                        timeFromMatrix = true
                    },
                    shape = RoundedCornerShape(16.dp),
                    color = if (timeFromMatrix) Gold.copy(alpha = .13f) else CardBrown,
                    border = androidx.compose.foundation.BorderStroke(1.dp, if (timeFromMatrix) Gold.copy(alpha = .52f) else LineGold.copy(alpha=.38f))
                ) {
                    Row(Modifier.padding(horizontal = 13.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Timer, null, tint = Gold, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(8.dp))
                        Text(
                            if (timeFromMatrix) "Tempo preenchido automaticamente pela matriz" else "Restaurar tempo estimado da matriz",
                            color = if (timeFromMatrix) Gold else Cream,
                            fontSize = 10.sp,
                            modifier = Modifier.weight(1f)
                        )
                        if (timeFromMatrix) Icon(Icons.Rounded.Check, null, tint = Gold, modifier = Modifier.size(17.dp))
                    }
                }
            }
        }
        item { CostField("Quantidade", quantity, moneyPrefix = false) { quantity = it } }
        item {
            Surface(shape = RoundedCornerShape(22.dp), color = CardBrown,'''
if old not in text: raise SystemExit('quantity/margin marker not found')
text = text.replace(old, new, 1)

old = '            Text("Futuramente pontos, tempo e consumo de linha poderão vir automaticamente da matriz aberta.", color = Muted, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())'
new = '            Text(if (design == null) "Abra uma matriz DST e acesse Custos pelo visualizador para preencher dados técnicos automaticamente." else "Dados técnicos carregados da matriz aberta. Ajuste os valores comerciais conforme sua realidade.", color = Muted, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())'
if old not in text: raise SystemExit('calculator footer not found')
text = text.replace(old, new, 1)

# Add cost shortcut in the viewer header while preserving the open design.
old = '''@Composable
private fun ViewerScreen(design: Design, onBack: () -> Unit) {
    BackHandler(onBack = onBack)'''
new = '''@Composable
private fun ViewerScreen(design: Design, onBack: () -> Unit, onCosts: () -> Unit) {
    BackHandler(onBack = onBack)'''
if old not in text: raise SystemExit('viewer signature not found')
text = text.replace(old, new, 1)

old = '''            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)
        }'''
new = '''            ExpressiveIconButton(Icons.Rounded.Calculate, "Custos", onCosts)
            Spacer(Modifier.width(7.dp))
            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)
        }'''
if old not in text: raise SystemExit('viewer header marker not found')
text = text.replace(old, new, 1)

text = text.replace('0.2.5', '0.2.6')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.6 matrix-aware cost calculator patch applied successfully')
