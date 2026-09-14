from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_032.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Add the Analyzer panel to the viewer stack, below the machine/time checks and above the canvas.
old = '''        MachineCheckPanel(design, machineConfig)
        MachineTimePanel(design, machineConfig)
        Box('''
new = '''        MachineCheckPanel(design, machineConfig)
        MachineTimePanel(design, machineConfig)
        DesignAnalyzerPanel(design, machineConfig)
        Box('''
if old not in text:
    raise SystemExit('Viewer Machine Check/time stack marker not found')
text = text.replace(old, new, 1)

# Insert real geometry-based analysis helpers and Material 3 Expressive UI before the time panel.
insert_at = text.index('@Composable\nprivate fun MachineTimePanel')
analyzer_code = r'''private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)

private data class DesignAnalysis(
    val status: String,
    val issues: List<AnalysisIssue>,
    val longJumpCount: Int,
    val longStitchCount: Int,
    val maxJumpMm: Double,
    val maxStitchMm: Double,
    val peakCellStitches: Int,
    val fitsConfiguredHoop: Boolean?,
    val colorChanges: Int
)

private fun analyzeDesign(design: Design, config: MachineConfig): DesignAnalysis {
    var previous: StitchPoint? = null
    var longJumpCount = 0
    var longStitchCount = 0
    var maxJumpMm = 0.0
    var maxStitchMm = 0.0
    val localCells = mutableMapOf<Pair<Int, Int>, Int>()

    design.stitches.forEach { current ->
        val prev = previous
        if (prev != null && current.command != StitchCommand.END) {
            val distance = kotlin.math.hypot(
                (current.x - prev.x).toDouble(),
                (current.y - prev.y).toDouble()
            )

            if (current.command == StitchCommand.JUMP) {
                maxJumpMm = maxOf(maxJumpMm, distance)
                if (distance > 12.0) longJumpCount++
            }

            if (
                current.command == StitchCommand.STITCH &&
                prev.command == StitchCommand.STITCH &&
                current.color == prev.color
            ) {
                maxStitchMm = maxOf(maxStitchMm, distance)
                if (distance > 8.0) longStitchCount++
            }
        }

        if (current.command == StitchCommand.STITCH) {
            val cellX = kotlin.math.floor(current.x.toDouble() / 5.0).toInt()
            val cellY = kotlin.math.floor(current.y.toDouble() / 5.0).toInt()
            val key = cellX to cellY
            localCells[key] = (localCells[key] ?: 0) + 1
        }

        previous = if (current.command == StitchCommand.END) null else current
    }

    val peakCellStitches = localCells.values.maxOrNull() ?: 0

    val configuredHoops = buildList {
        addAll(StandardHoops.filter { it.id in config.selectedHoopIds })
        val cw = config.customWidthMm
        val ch = config.customHeightMm
        if (cw != null && ch != null) add(HoopOption("custom", cw, ch))
    }
    val fitsConfiguredHoop = if (configuredHoops.isEmpty()) null else configuredHoops.any { hoop ->
        (design.width <= hoop.widthMm && design.height <= hoop.heightMm) ||
            (design.width <= hoop.heightMm && design.height <= hoop.widthMm)
    }

    val issues = mutableListOf<AnalysisIssue>()

    if (design.stitchCount == 0) {
        issues += AnalysisIssue(
            "Sem pontadas válidas",
            "O arquivo foi aberto, mas não há pontos de costura utilizáveis no modelo interno.",
            3
        )
    }

    when (fitsConfiguredHoop) {
        null -> issues += AnalysisIssue(
            "Bastidor não configurado",
            "Cadastre pelo menos um bastidor em Minha Máquina para concluir a validação de tamanho.",
            2
        )
        false -> issues += AnalysisIssue(
            "Matriz fora dos bastidores cadastrados",
            "${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm não cabe em nenhum bastidor selecionado, mesmo considerando rotação de 90°.",
            3
        )
        true -> Unit
    }

    if (longStitchCount > 0) {
        val severe = maxStitchMm >= 12.0 || longStitchCount >= 25
        issues += AnalysisIssue(
            "Pontos muito longos detectados",
            "$longStitchCount trecho${if (longStitchCount == 1) "" else "s"} acima de 8 mm; máximo de ${"%.1f".format(maxStitchMm)} mm. Revise se esses pontos são intencionais.",
            if (severe) 3 else 2
        )
    }

    if (longJumpCount > 0) {
        val severe = maxJumpMm >= 30.0 || longJumpCount >= 20
        issues += AnalysisIssue(
            "Saltos longos detectados",
            "$longJumpCount salto${if (longJumpCount == 1) "" else "s"} acima de 12 mm; máximo de ${"%.1f".format(maxJumpMm)} mm. Pode exigir corte ou otimização de sequência.",
            if (severe) 3 else 2
        )
    }

    if (peakCellStitches >= 100) {
        val severe = peakCellStitches >= 180
        issues += AnalysisIssue(
            "Concentração local elevada",
            "A região de 5 × 5 mm mais carregada contém aproximadamente $peakCellStitches pontos. É uma heurística geométrica; revise densidade, tecido e estabilizador.",
            if (severe) 3 else 2
        )
    }

    val highest = issues.maxOfOrNull { it.severity } ?: 0
    val status = when {
        highest >= 3 -> "REVISAR"
        highest >= 2 -> "ATENÇÃO"
        else -> "TUDO CERTO"
    }

    return DesignAnalysis(
        status = status,
        issues = issues,
        longJumpCount = longJumpCount,
        longStitchCount = longStitchCount,
        maxJumpMm = maxJumpMm,
        maxStitchMm = maxStitchMm,
        peakCellStitches = peakCellStitches,
        fitsConfiguredHoop = fitsConfiguredHoop,
        colorChanges = design.colorChanges
    )
}

@Composable
private fun DesignAnalyzerPanel(design: Design, config: MachineConfig) {
    val analysis = remember(design, config) { analyzeDesign(design, config) }
    var expanded by remember(design) { mutableStateOf(false) }
    val hasCritical = analysis.issues.any { it.severity >= 3 }

    Surface(
        modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded },
        color = if (hasCritical) Gold.copy(alpha = .10f) else SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            if (analysis.issues.isEmpty()) LineGold.copy(alpha = .35f) else Gold.copy(alpha = .58f)
        )
    ) {
        Column(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ExpressiveIconBadge(
                    if (analysis.issues.isEmpty()) Icons.Rounded.CheckCircle else Icons.Rounded.FactCheck,
                    selected = analysis.issues.isNotEmpty(),
                    size = 40.dp
                )
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text("BORDATTO Analyzer", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                    Text(
                        if (analysis.issues.isEmpty()) "Nenhum alerta geométrico relevante" else "${analysis.issues.size} alerta${if (analysis.issues.size == 1) "" else "s"} encontrado${if (analysis.issues.size == 1) "" else "s"}",
                        color = Muted,
                        fontSize = 8.sp
                    )
                }
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .15f)) {
                    Text(analysis.status, color = Gold, fontWeight = FontWeight.Bold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                }
                Spacer(Modifier.width(5.dp))
                Icon(if (expanded) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold)
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                AnalyzerMetric("Ponto máx.", "${"%.1f".format(analysis.maxStitchMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Salto máx.", "${"%.1f".format(analysis.maxJumpMm)} mm", Modifier.weight(1f))
                AnalyzerMetric("Pico 5×5", "${analysis.peakCellStitches}", Modifier.weight(1f))
                AnalyzerMetric("Trocas", "${analysis.colorChanges}", Modifier.weight(1f))
            }

            if (expanded) {
                HorizontalDivider(color = LineGold.copy(alpha = .38f))
                if (analysis.issues.isEmpty()) {
                    Row(verticalAlignment = Alignment.Top) {
                        Icon(Icons.Rounded.Verified, null, tint = Gold, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(8.dp))
                        Text(
                            "A geometria básica não apresentou alertas nos limites atuais. Ainda é recomendável fazer uma amostra no tecido e estabilizador reais.",
                            color = Muted,
                            fontSize = 9.sp,
                            lineHeight = 12.sp
                        )
                    }
                } else {
                    analysis.issues.forEach { issue ->
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = CardBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (issue.severity >= 3) Gold.copy(alpha = .60f) else LineGold.copy(alpha = .40f))
                        ) {
                            Row(Modifier.fillMaxWidth().padding(11.dp), verticalAlignment = Alignment.Top) {
                                Icon(
                                    if (issue.severity >= 3) Icons.Rounded.ErrorOutline else Icons.Rounded.WarningAmber,
                                    null,
                                    tint = Gold,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(Modifier.width(8.dp))
                                Column {
                                    Text(issue.title, color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 10.sp)
                                    Text(issue.detail, color = Muted, fontSize = 8.sp, lineHeight = 11.sp)
                                }
                            }
                        }
                    }
                }
                Text(
                    "Analyzer v1 usa geometria das pontadas. A concentração local é uma aproximação e não substitui análise de objetos, compensação, entretela ou teste físico.",
                    color = Muted,
                    fontSize = 8.sp,
                    lineHeight = 11.sp
                )
            }
        }
    }
}

@Composable
private fun AnalyzerMetric(label: String, value: String, modifier: Modifier = Modifier) {
    Surface(modifier = modifier, shape = RoundedCornerShape(12.dp), color = CardBrown) {
        Column(Modifier.padding(horizontal = 6.dp, vertical = 7.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(label, color = Muted, fontSize = 7.sp, maxLines = 1)
            Text(value, color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold, maxLines = 1)
        }
    }
}

'''
text = text[:insert_at] + analyzer_code + text[insert_at:]

# Refresh version labels produced by the chained build patches.
text = text.replace('0.2.12', '0.2.13')

path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.13 Analyzer + Machine Check Pro patch applied successfully')
