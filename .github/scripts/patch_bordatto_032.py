from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_031.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Persist a nominal machine speed (stitches per minute) in the machine profile.
old = '''private data class MachineConfig(
    val brand: String = "Brother",
    val model: String = "PE770",
    val format: String = "PES",
    val selectedHoopIds: Set<String> = setOf("130x180"),
    val customWidthMm: Int? = null,
    val customHeightMm: Int? = null
)'''
new = '''private data class MachineConfig(
    val brand: String = "Brother",
    val model: String = "PE770",
    val format: String = "PES",
    val selectedHoopIds: Set<String> = setOf("130x180"),
    val customWidthMm: Int? = null,
    val customHeightMm: Int? = null,
    val speedPpm: Int = 700
)'''
if old not in text: raise SystemExit('MachineConfig marker not found')
text = text.replace(old, new, 1)

old = '''        selectedHoopIds = ids,
        customWidthMm = cw,
        customHeightMm = ch
    )'''
new = '''        selectedHoopIds = ids,
        customWidthMm = cw,
        customHeightMm = ch,
        speedPpm = p.getInt("machine_speed_ppm", 700).coerceIn(300, 1200)
    )'''
if old not in text: raise SystemExit('loadMachineConfig marker not found')
text = text.replace(old, new, 1)

old = '''        .putInt("machine_custom_w", config.customWidthMm ?: -1)
        .putInt("machine_custom_h", config.customHeightMm ?: -1)
        .apply()'''
new = '''        .putInt("machine_custom_w", config.customWidthMm ?: -1)
        .putInt("machine_custom_h", config.customHeightMm ?: -1)
        .putInt("machine_speed_ppm", config.speedPpm.coerceIn(300, 1200))
        .apply()'''
if old not in text: raise SystemExit('saveMachineConfig marker not found')
text = text.replace(old, new, 1)

# Load/edit speed in Minha Máquina.
old = '''    var format by remember(config) { mutableStateOf(config.format) }
    var selectedHoops by remember(config) { mutableStateOf(config.selectedHoopIds) }'''
new = '''    var format by remember(config) { mutableStateOf(config.format) }
    var speedPpm by remember(config) { mutableIntStateOf(config.speedPpm) }
    var selectedHoops by remember(config) { mutableStateOf(config.selectedHoopIds) }'''
if old not in text: raise SystemExit('MachineScreen state marker not found')
text = text.replace(old, new, 1)

old = '''        item { SimpleChoice("Formato principal", format, listOf("PES", "DST", "JEF", "EXP", "VP3")) { format = it } }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {'''
new = '''        item { SimpleChoice("Formato principal", format, listOf("PES", "DST", "JEF", "EXP", "VP3")) { format = it } }

        item {
            Surface(
                color = CardBrown,
                shape = RoundedCornerShape(22.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .46f))
            ) {
                Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        ExpressiveIconBadge(Icons.Rounded.Speed, selected = true, size = 42.dp)
                        Spacer(Modifier.width(10.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Velocidade da máquina", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                            Text("Usada no tempo estimado e no simulador", color = Muted, fontSize = 9.sp)
                        }
                        Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .15f)) {
                            Text("$speedPpm PPM", color = Gold, fontWeight = FontWeight.Bold, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
                        }
                    }
                    Slider(
                        value = speedPpm.toFloat(),
                        onValueChange = { value ->
                            speedPpm = (kotlin.math.round(value / 50f).toInt() * 50).coerceIn(300, 1200)
                        },
                        valueRange = 300f..1200f,
                        colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold)
                    )
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        listOf(400, 600, 800, 1000).forEach { preset ->
                            val selected = speedPpm == preset
                            Surface(
                                modifier = Modifier.weight(1f).clickable { speedPpm = preset },
                                shape = RoundedCornerShape(if (selected) 15.dp else 11.dp),
                                color = if (selected) Gold.copy(alpha = .17f) else SurfaceBrown,
                                border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha = .70f) else LineGold.copy(alpha = .35f))
                            ) {
                                Text("$preset", color = if (selected) Gold else Muted, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 7.dp))
                            }
                        }
                    }
                    Text("PPM = pontos por minuto. A velocidade efetiva pode variar conforme a máquina, o desenho e o tecido.", color = Muted, fontSize = 8.sp, lineHeight = 11.sp)
                }
            }
        }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {'''
if old not in text: raise SystemExit('Machine speed insertion marker not found')
text = text.replace(old, new, 1)

old = '''                            format = format,
                            selectedHoopIds = selectedHoops,'''
new = '''                            format = format,
                            speedPpm = speedPpm,
                            selectedHoopIds = selectedHoops,'''
if old not in text: raise SystemExit('MachineConfig save constructor marker not found')
text = text.replace(old, new, 1)

# Machine-aware cost estimate.
old = '''                page == Page.COSTS -> CostCalculatorScreen(
                    design = design,
                    onBack = { page = Page.MAIN }
                )'''
new = '''                page == Page.COSTS -> CostCalculatorScreen(
                    design = design,
                    machineConfig = machineConfig,
                    onBack = { page = Page.MAIN }
                )'''
if old not in text: raise SystemExit('Cost route marker not found')
text = text.replace(old, new, 1)

old = '''@Composable
private fun CostCalculatorScreen(design: Design? = null, onBack: () -> Unit) {'''
new = '''private fun estimateMachineMinutes(design: Design, config: MachineConfig): Double {
    val ppm = config.speedPpm.coerceIn(300, 1200).toDouble()
    val sewing = design.stitchCount / ppm
    val jumpOverhead = (design.jumpCount * 0.08) / 60.0
    val colorOverhead = (design.colorChanges * 8.0) / 60.0
    return maxOf(0.5, sewing + jumpOverhead + colorOverhead + 0.25)
}

@Composable
private fun CostCalculatorScreen(design: Design? = null, machineConfig: MachineConfig = MachineConfig(), onBack: () -> Unit) {'''
if old not in text: raise SystemExit('Cost screen signature marker not found')
text = text.replace(old, new, 1)

old = '''    val estimatedMinutes = remember(design) {
        design?.let {
            maxOf(1.0, (it.stitchCount / 700.0) + (it.colorChanges * 0.45) + (it.jumpCount * 0.015))
        } ?: 0.0
    }'''
new = '''    val estimatedMinutes = remember(design, machineConfig) {
        design?.let { estimateMachineMinutes(it, machineConfig) } ?: 0.0
    }'''
if old not in text: raise SystemExit('estimatedMinutes marker not found')
text = text.replace(old, new, 1)

old = '''                        CostRow("Linha estimada + 12%", "${"%.1f".format(estimatedThreadMeters)} m")
                        CostRow("Tempo estimado", "≈ ${kotlin.math.ceil(estimatedMinutes).toInt()} min")'''
new = '''                        CostRow("Linha estimada + 12%", "${"%.1f".format(estimatedThreadMeters)} m")
                        CostRow("Velocidade configurada", "${machineConfig.speedPpm} PPM")
                        CostRow("Tempo estimado", "≈ ${kotlin.math.ceil(estimatedMinutes).toInt()} min")'''
if old not in text: raise SystemExit('Cost matrix rows marker not found')
text = text.replace(old, new, 1)

# Make the simulator clock follow the machine PPM at 1x.
old = '''    LaunchedEffect(simulatorPlaying, simulatorSpeed, design) {
        while (simulatorPlaying && simulatorPosition < stitchIndices.size) {
            delay(40L)
            val batch = maxOf(1, (6f * simulatorSpeed).toInt())
            simulatorPosition = (simulatorPosition + batch).coerceAtMost(stitchIndices.size)
            if (simulatorPosition >= stitchIndices.size) simulatorPlaying = false
        }
    }'''
new = '''    LaunchedEffect(simulatorPlaying, simulatorSpeed, design, machineConfig.speedPpm) {
        while (simulatorPlaying && simulatorPosition < stitchIndices.size) {
            val effectivePpm = (machineConfig.speedPpm * simulatorSpeed).coerceAtLeast(1f)
            val delayMs = (60000f / effectivePpm).toLong().coerceIn(10L, 1000L)
            delay(delayMs)
            simulatorPosition = (simulatorPosition + 1).coerceAtMost(stitchIndices.size)
            if (simulatorPosition >= stitchIndices.size) simulatorPlaying = false
        }
    }'''
if old not in text: raise SystemExit('Simulator timing loop marker not found')
text = text.replace(old, new, 1)

old = '''            playing = simulatorPlaying,
            speed = simulatorSpeed,
            onStop = {'''
new = '''            playing = simulatorPlaying,
            speed = simulatorSpeed,
            machinePpm = machineConfig.speedPpm,
            onStop = {'''
if old not in text: raise SystemExit('Simulator panel call marker not found')
text = text.replace(old, new, 1)

old = '''    playing: Boolean,
    speed: Float,
    onStop: () -> Unit,'''
new = '''    playing: Boolean,
    speed: Float,
    machinePpm: Int,
    onStop: () -> Unit,'''
if old not in text: raise SystemExit('Simulator panel signature marker not found')
text = text.replace(old, new, 1)

old = '''                    Text(
                        if (total == 0) "Sem pontadas para reproduzir" else "Ponto $current de $total • Bloco ${block.coerceAtLeast(1)} de ${blockTotal.coerceAtLeast(1)}",
                        color = Muted,
                        fontSize = 9.sp
                    )'''
new = '''                    Text(
                        if (total == 0) "Sem pontadas para reproduzir" else "Ponto $current de $total • Bloco ${block.coerceAtLeast(1)} de ${blockTotal.coerceAtLeast(1)} • ${(machinePpm * speed).toInt()} PPM",
                        color = Muted,
                        fontSize = 9.sp
                    )'''
if old not in text: raise SystemExit('Simulator subtitle marker not found')
text = text.replace(old, new, 1)

# Add a compact time estimate to the viewer using the selected machine profile.
old = '''        MachineCheckPanel(design, machineConfig)
        Box('''
new = '''        MachineCheckPanel(design, machineConfig)
        MachineTimePanel(design, machineConfig)
        Box('''
if old not in text: raise SystemExit('MachineCheckPanel viewer marker not found')
text = text.replace(old, new, 1)

insert_at = text.index('@Composable\nprivate fun MachineCheckPanel')
time_panel = r'''@Composable
private fun MachineTimePanel(design: Design, config: MachineConfig) {
    val minutes = remember(design, config) { estimateMachineMinutes(design, config) }
    Surface(
        color = Chocolate,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .30f))
    ) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Rounded.Timer, null, tint = Gold, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(7.dp))
            Column(Modifier.weight(1f)) {
                Text("Tempo estimado nesta máquina", color = Cream, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                Text("${config.brand} ${config.model} • ${config.speedPpm} PPM", color = Muted, fontSize = 8.sp)
            }
            Text("≈ ${kotlin.math.ceil(minutes).toInt()} min", color = Gold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        }
    }
}

'''
text = text[:insert_at] + time_panel + text[insert_at:]

text = text.replace('0.2.11', '0.2.12')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.12 machine-aware timing patch applied successfully')
