from pathlib import Path
import runpy

# Start from the validated 0.2.3 UI/lettering build.
runpy.run_path('.github/scripts/patch_bordatto_023.py', run_name='__main__')

path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

start = text.index('@Composable\nprivate fun MachineScreen')
end = text.index('@Composable\nprivate fun SimpleChoice', start)

new_machine = r'''private data class HoopOption(
    val id: String,
    val widthMm: Int,
    val heightMm: Int
) {
    val label: String get() = "$widthMm × $heightMm"
}

@Composable
private fun MachineScreen(onBack: () -> Unit, onSave: () -> Unit) {
    BackHandler(onBack = onBack)
    var brand by remember { mutableStateOf("Brother") }
    var model by remember { mutableStateOf("PE770") }
    var format by remember { mutableStateOf("PES") }

    val hoopOptions = listOf(
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
    var selectedHoops by remember { mutableStateOf(setOf("130x180")) }
    var customEnabled by remember { mutableStateOf(false) }
    var customWidth by remember { mutableStateOf("") }
    var customHeight by remember { mutableStateOf("") }

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
                    Text("Esses dados serão usados para preparar e validar suas matrizes.", color = Muted, fontSize = 11.sp, textAlign = TextAlign.Center)
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
                Text("Marque os bastidores que sua máquina realmente aceita.", color = Muted, fontSize = 10.sp)
            }
        }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                hoopOptions.chunked(3).forEach { rowHoops ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        rowHoops.forEach { hoop ->
                            val selected = hoop.id in selectedHoops
                            Surface(
                                modifier = Modifier.weight(1f).clickable {
                                    selectedHoops = if (selected) selectedHoops - hoop.id else selectedHoops + hoop.id
                                },
                                shape = RoundedCornerShape(if (selected) 22.dp else 16.dp),
                                color = if (selected) Gold.copy(alpha = .16f) else CardBrown,
                                border = androidx.compose.foundation.BorderStroke(
                                    1.dp,
                                    if (selected) Gold.copy(alpha = .72f) else LineGold.copy(alpha = .46f)
                                )
                            ) {
                                Column(
                                    Modifier.fillMaxWidth().padding(horizontal = 7.dp, vertical = 12.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(width = 38.dp, height = 46.dp)
                                            .border(
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
            val selectedLabels = hoopOptions.filter { it.id in selectedHoops }.map { it.label + " mm" }.toMutableList()
            if (customEnabled && customWidth.isNotBlank() && customHeight.isNotBlank()) selectedLabels += "$customWidth × $customHeight mm"
            Surface(
                color = SurfaceBrown,
                shape = RoundedCornerShape(20.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .38f))
            ) {
                Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.Top) {
                    Icon(Icons.Rounded.Verified, null, tint = Gold, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(9.dp))
                    Column {
                        Text("Preparado para o Machine Check", color = Gold, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                        Text(
                            if (selectedLabels.isEmpty()) "Selecione pelo menos um bastidor para futuras validações de tamanho."
                            else "O BORDATTO poderá verificar automaticamente se uma matriz cabe em: ${selectedLabels.joinToString()}.",
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
                onClick = onSave,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(20.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                Icon(Icons.Rounded.Save, null)
                Spacer(Modifier.width(8.dp))
                Text("Salvar Configurações", fontWeight = FontWeight.Bold)
            }
        }
    }
}

'''

text = text[:start] + new_machine + text[end:]
text = text.replace('0.2.3', '0.2.4')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.4 hoop configuration patch applied successfully')
