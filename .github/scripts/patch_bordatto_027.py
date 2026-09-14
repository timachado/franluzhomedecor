from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_026.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Shared machine/hoop model so the viewer can use the configuration saved in this app session.
old = '''private data class HoopOption(
    val id: String,
    val widthMm: Int,
    val heightMm: Int
) {
    val label: String get() = "$widthMm × $heightMm"
}
'''
new = '''private data class HoopOption(
    val id: String,
    val widthMm: Int,
    val heightMm: Int
) {
    val label: String get() = "$widthMm × $heightMm"
}

private val StandardHoops = listOf(
    HoopOption("40x40", 40, 40),
    HoopOption("100x100", 100, 100),
    HoopOption("130x180", 130, 180),
    HoopOption("160x260", 160, 260),
    HoopOption("180x300", 180, 300),
    HoopOption("200x300", 200, 300),
    HoopOption("240x360", 240, 360),
    HoopOption("260x400", 260, 400),
    HoopOption("360x360", 360, 360)
)

private data class MachineConfig(
    val brand: String = "Brother",
    val model: String = "PE770",
    val format: String = "PES",
    val selectedHoopIds: Set<String> = setOf("130x180"),
    val customWidthMm: Int? = null,
    val customHeightMm: Int? = null
)

private data class HoopFit(
    val hoop: HoopOption,
    val fits: Boolean,
    val rotated: Boolean
)
'''
if old not in text: raise SystemExit('HoopOption block not found')
text = text.replace(old, new, 1)

# Keep machine configuration at app level for the current session.
old = '''    var activeTab by remember { mutableStateOf(MainTab.HOME) }
    var page by remember { mutableStateOf(Page.MAIN) }
'''
new = '''    var activeTab by remember { mutableStateOf(MainTab.HOME) }
    var page by remember { mutableStateOf(Page.MAIN) }
    var machineConfig by remember { mutableStateOf(MachineConfig()) }
'''
if old not in text: raise SystemExit('root state marker not found')
text = text.replace(old, new, 1)

# Pass machine config to the open-matrix viewer.
old = '''                design != null -> ViewerScreen(
                    design = design!!,
                    onBack = { design = null },
                    onCosts = { page = Page.COSTS }
                )'''
new = '''                design != null -> ViewerScreen(
                    design = design!!,
                    machineConfig = machineConfig,
                    onBack = { design = null },
                    onCosts = { page = Page.COSTS }
                )'''
if old not in text: raise SystemExit('viewer route not found')
text = text.replace(old, new, 1)

# Save machine/bastidor choices back to the session-level model.
old = '''                page == Page.MACHINE -> MachineScreen(
                    onBack = { page = Page.MAIN },
                    onSave = { notice = "Configuração salva para esta sessão de teste. A persistência definitiva entra em uma próxima etapa." }
                )'''
new = '''                page == Page.MACHINE -> MachineScreen(
                    config = machineConfig,
                    onBack = { page = Page.MAIN },
                    onSave = { saved ->
                        machineConfig = saved
                        page = Page.MAIN
                        notice = "Máquina e bastidores salvos nesta sessão. O Machine Check já vai usar essa configuração nas matrizes abertas."
                    }
                )'''
if old not in text: raise SystemExit('machine route not found')
text = text.replace(old, new, 1)

# Replace the machine screen so its values are initialized from and saved into MachineConfig.
start = text.index('@Composable\nprivate fun MachineScreen')
end = text.index('@Composable\nprivate fun SimpleChoice', start)
new_machine = r'''@Composable
private fun MachineScreen(config: MachineConfig, onBack: () -> Unit, onSave: (MachineConfig) -> Unit) {
    BackHandler(onBack = onBack)
    var brand by remember(config) { mutableStateOf(config.brand) }
    var model by remember(config) { mutableStateOf(config.model) }
    var format by remember(config) { mutableStateOf(config.format) }
    var selectedHoops by remember(config) { mutableStateOf(config.selectedHoopIds) }
    var customEnabled by remember(config) { mutableStateOf(config.customWidthMm != null && config.customHeightMm != null) }
    var customWidth by remember(config) { mutableStateOf(config.customWidthMm?.toString() ?: "") }
    var customHeight by remember(config) { mutableStateOf(config.customHeightMm?.toString() ?: "") }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item { PageHeader("Minha Máquina", onBack) }
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = CardBrown),
                shape = RoundedCornerShape(26.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))
            ) {
                Column(Modifier.fillMaxWidth().padding(22.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    ExpressiveIconBadge(Icons.Rounded.PrecisionManufacturing, selected = true, size = 72.dp)
                    Spacer(Modifier.height(10.dp))
                    Text("Configuração da máquina", color = Cream, fontWeight = FontWeight.SemiBold)
                    Text("Máquina e bastidores alimentam o Machine Check das matrizes.", color = Muted, fontSize = 11.sp, textAlign = TextAlign.Center)
                }
            }
        }
        item { SimpleChoice("Marca", brand, listOf("Brother", "Janome", "Singer", "Bernina", "Elna", "Husqvarna Viking", "Pfaff", "Outra")) { brand = it } }
        item { SimpleChoice("Modelo", model, listOf("PE770", "SE600", "NV180", "Outro")) { model = it } }
        item { SimpleChoice("Formato principal", format, listOf("PES", "DST", "JEF", "EXP", "VP3")) { format = it } }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.CropFree, null, tint = Gold, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Bastidores disponíveis", color = Cream, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                    Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .14f)) {
                        val count = selectedHoops.size + if (customEnabled && customWidth.isNotBlank() && customHeight.isNotBlank()) 1 else 0
                        Text("$count selecionado${if (count == 1) "" else "s"}", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                    }
                }
                Text("O Machine Check compara a matriz com estes tamanhos.", color = Muted, fontSize = 10.sp)
            }
        }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                StandardHoops.chunked(3).forEach { rowHoops ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        rowHoops.forEach { hoop ->
                            val selected = hoop.id in selectedHoops
                            Surface(
                                modifier = Modifier.weight(1f).clickable {
                                    selectedHoops = if (selected) selectedHoops - hoop.id else selectedHoops + hoop.id
                                },
                                shape = RoundedCornerShape(if (selected) 22.dp else 16.dp),
                                color = if (selected) Gold.copy(alpha = .16f) else CardBrown,
                                border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha = .72f) else LineGold.copy(alpha = .46f))
                            ) {
                                Column(Modifier.fillMaxWidth().padding(horizontal = 7.dp, vertical = 12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                                    Box(
                                        modifier = Modifier.size(width = 38.dp, height = 46.dp).border(
                                            width = if (selected) 2.dp else 1.dp,
                                            color = if (selected) Gold else Muted.copy(alpha = .65f),
                                            shape = RoundedCornerShape(7.dp)
                                        ),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        if (selected) Icon(Icons.Rounded.Check, null, tint = Gold, modifier = Modifier.size(17.dp))
                                    }
                                    Spacer(Modifier.height(7.dp))
                                    Text(hoop.label, color = if (selected) Gold else Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, textAlign = TextAlign.Center)
                                    Text("mm", color = Muted, fontSize = 8.sp)
                                }
                            }
                        }
                        repeat(3 - rowHoops.size) { Spacer(Modifier.weight(1f)) }
                    }
                }
            }
        }

        item {
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { customEnabled = !customEnabled },
                shape = RoundedCornerShape(if (customEnabled) 22.dp else 18.dp),
                color = if (customEnabled) Gold.copy(alpha = .13f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (customEnabled) Gold.copy(alpha = .65f) else LineGold.copy(alpha = .45f))
            ) {
                Column(Modifier.padding(14.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        ExpressiveIconBadge(Icons.Rounded.AddBox, selected = customEnabled, size = 42.dp)
                        Spacer(Modifier.width(11.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Bastidor personalizado", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                            Text("Informe largura e altura em milímetros", color = Muted, fontSize = 9.sp)
                        }
                        Icon(if (customEnabled) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null, tint = Gold)
                    }
                    if (customEnabled) {
                        Spacer(Modifier.height(14.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            OutlinedTextField(
                                value = customWidth,
                                onValueChange = { customWidth = it.filter(Char::isDigit).take(4) },
                                modifier = Modifier.weight(1f),
                                label = { Text("Largura") },
                                suffix = { Text("mm") },
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold, focusedLabelColor = Gold)
                            )
                            OutlinedTextField(
                                value = customHeight,
                                onValueChange = { customHeight = it.filter(Char::isDigit).take(4) },
                                modifier = Modifier.weight(1f),
                                label = { Text("Altura") },
                                suffix = { Text("mm") },
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold, focusedLabelColor = Gold)
                            )
                        }
                    }
                }
            }
        }

        item {
            val selectedLabels = StandardHoops.filter { it.id in selectedHoops }.map { it.label + " mm" }.toMutableList()
            if (customEnabled && customWidth.isNotBlank() && customHeight.isNotBlank()) selectedLabels += "$customWidth × $customHeight mm"
            Surface(color = SurfaceBrown, shape = RoundedCornerShape(20.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .38f))) {
                Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.Top) {
                    Icon(Icons.Rounded.Verified, null, tint = Gold, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(9.dp))
                    Column {
                        Text("Machine Check ativo", color = Gold, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                        Text(
                            if (selectedLabels.isEmpty()) "Selecione pelo menos um bastidor para validar matrizes."
                            else "Serão verificados: ${selectedLabels.joinToString()}.",
                            color = Muted,
                            fontSize = 9.sp,
                            lineHeight = 12.sp
                        )
                    }
                }
            }
        }

        item {
            Button(
                onClick = {
                    val cw = if (customEnabled) customWidth.toIntOrNull()?.takeIf { it > 0 } else null
                    val ch = if (customEnabled) customHeight.toIntOrNull()?.takeIf { it > 0 } else null
                    onSave(
                        MachineConfig(
                            brand = brand,
                            model = model,
                            format = format,
                            selectedHoopIds = selectedHoops,
                            customWidthMm = if (cw != null && ch != null) cw else null,
                            customHeightMm = if (cw != null && ch != null) ch else null
                        )
                    )
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(20.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(Icons.Rounded.Save, null)
                Spacer(Modifier.width(8.dp))
                Text("Salvar e ativar Machine Check", fontWeight = FontWeight.Bold)
            }
        }
    }
}

'''
text = text[:start] + new_machine + text[end:]

# Upgrade the viewer signature and insert a compact real Machine Check panel.
old = '''private fun ViewerScreen(design: Design, onBack: () -> Unit, onCosts: () -> Unit) {
    BackHandler(onBack = onBack)'''
new = '''private fun ViewerScreen(design: Design, machineConfig: MachineConfig, onBack: () -> Unit, onCosts: () -> Unit) {
    BackHandler(onBack = onBack)'''
if old not in text: raise SystemExit('viewer signature not found for Machine Check')
text = text.replace(old, new, 1)

old = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        Box('''
new = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        MachineCheckPanel(design, machineConfig)
        Box('''
if old not in text: raise SystemExit('viewer toolbar block not found')
text = text.replace(old, new, 1)

insert_at = text.index('@Composable\nprivate fun ViewerTool')
machine_check = r'''@Composable
private fun MachineCheckPanel(design: Design, config: MachineConfig) {
    val hoops = remember(config) {
        buildList {
            addAll(StandardHoops.filter { it.id in config.selectedHoopIds })
            val cw = config.customWidthMm
            val ch = config.customHeightMm
            if (cw != null && ch != null) add(HoopOption("custom", cw, ch))
        }
    }
    val fits = remember(design, hoops) {
        hoops.map { hoop ->
            val direct = design.width <= hoop.widthMm && design.height <= hoop.heightMm
            val rotated = !direct && design.width <= hoop.heightMm && design.height <= hoop.widthMm
            HoopFit(hoop, direct || rotated, rotated)
        }
    }
    val compatible = fits.filter { it.fits }.sortedBy { it.hoop.widthMm * it.hoop.heightMm }
    val best = compatible.firstOrNull()
    val statusColor = if (best != null) Gold else Color(0xFFE6A19A)

    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 5.dp),
        shape = RoundedCornerShape(20.dp),
        color = if (best != null) Gold.copy(alpha = .09f) else Color(0xFF4B2725),
        border = androidx.compose.foundation.BorderStroke(1.dp, statusColor.copy(alpha = .62f))
    ) {
        Column(Modifier.padding(horizontal = 13.dp, vertical = 11.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    if (best != null) Icons.Rounded.Verified else Icons.Rounded.WarningAmber,
                    null,
                    tint = statusColor,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(Modifier.width(8.dp))
                Column(Modifier.weight(1f)) {
                    Text("Machine Check", color = statusColor, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                    Text("${config.brand} ${config.model} • ${config.format}", color = Muted, fontSize = 9.sp)
                }
                Surface(shape = RoundedCornerShape(50), color = statusColor.copy(alpha=.14f)) {
                    Text(
                        if (best != null) "COMPATÍVEL" else "ATENÇÃO",
                        color = statusColor,
                        fontSize = 8.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp)
                    )
                }
            }

            if (hoops.isEmpty()) {
                Text("Nenhum bastidor foi selecionado. Configure em Minha Máquina antes de validar.", color = Cream, fontSize = 10.sp)
            } else if (best != null) {
                val rotationText = if (best.rotated) " • girando a matriz 90°" else ""
                Text(
                    "Matriz ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm • menor bastidor compatível: ${best.hoop.label} mm$rotationText",
                    color = Cream,
                    fontSize = 10.sp,
                    lineHeight = 13.sp
                )
                if (compatible.size > 1) {
                    Text(
                        "Também cabe em: ${compatible.drop(1).joinToString { it.hoop.label + " mm" }}",
                        color = Muted,
                        fontSize = 9.sp,
                        lineHeight = 12.sp
                    )
                }
            } else {
                val largest = hoops.maxByOrNull { it.widthMm * it.heightMm }
                Text(
                    "A matriz mede ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm e não cabe em nenhum bastidor cadastrado${largest?.let { ". Maior disponível: ${it.label} mm" } ?: ""}.",
                    color = Cream,
                    fontSize = 10.sp,
                    lineHeight = 13.sp
                )
            }

            Text(
                "Validação geométrica inicial; a área útil real pode variar conforme fabricante, modelo e orientação do bastidor.",
                color = Muted,
                fontSize = 8.sp,
                lineHeight = 10.sp
            )
        }
    }
}

'''
text = text[:insert_at] + machine_check + text[insert_at:]

text = text.replace('0.2.6', '0.2.7')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.7 Machine Check patch applied successfully')
