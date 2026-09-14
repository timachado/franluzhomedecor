from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_024.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

text = text.replace('private enum class Page { MAIN, LETTERING, MACHINE }', 'private enum class Page { MAIN, LETTERING, MACHINE, COSTS }', 1)

old = '''                page == Page.MACHINE -> MachineScreen(
                    onBack = { page = Page.MAIN },
                    onSave = { notice = "Configuração salva para esta sessão de teste. Na próxima versão ela será persistida no aparelho." }
                )
                else -> StudioShell('''
new = '''                page == Page.MACHINE -> MachineScreen(
                    onBack = { page = Page.MAIN },
                    onSave = { notice = "Configuração salva para esta sessão de teste. A persistência definitiva entra em uma próxima etapa." }
                )
                page == Page.COSTS -> CostCalculatorScreen(onBack = { page = Page.MAIN })
                else -> StudioShell('''
if old not in text: raise SystemExit('root route not found')
text = text.replace(old, new, 1)

old = '''                    onLettering = { page = Page.LETTERING },
                    onMachine = { page = Page.MACHINE },
                    onSoon = { notice = it }'''
new = '''                    onLettering = { page = Page.LETTERING },
                    onMachine = { page = Page.MACHINE },
                    onCosts = { page = Page.COSTS },
                    onSoon = { notice = it }'''
if old not in text: raise SystemExit('root shell args not found')
text = text.replace(old, new, 1)

old = '''    onLettering: () -> Unit,
    onMachine: () -> Unit,
    onSoon: (String) -> Unit'''
new = '''    onLettering: () -> Unit,
    onMachine: () -> Unit,
    onCosts: () -> Unit,
    onSoon: (String) -> Unit'''
if old not in text: raise SystemExit('shell signature not found')
text = text.replace(old, new, 1)

old = 'MainTab.HOME -> HomeScreen(loading, onOpenMatrix, onLettering, onMachine, onSoon)'
new = 'MainTab.HOME -> HomeScreen(loading, onOpenMatrix, onLettering, onMachine, onCosts, onSoon)'
if old not in text: raise SystemExit('home route not found')
text = text.replace(old, new, 1)

old = 'private fun HomeScreen(loading: Boolean, onOpen: () -> Unit, onLettering: () -> Unit, onMachine: () -> Unit, onSoon: (String) -> Unit) {'
new = 'private fun HomeScreen(loading: Boolean, onOpen: () -> Unit, onLettering: () -> Unit, onMachine: () -> Unit, onCosts: () -> Unit, onSoon: (String) -> Unit) {'
if old not in text: raise SystemExit('home signature not found')
text = text.replace(old, new, 1)

old = '        HomeAction(Icons.Rounded.Description, "Abrir Matriz", "DST real nesta versão"),\n        HomeAction(Icons.Rounded.Folder, "Projetos", "Seus trabalhos"),'
new = '        HomeAction(Icons.Rounded.Description, "Abrir Matriz", "DST real nesta versão"),\n        HomeAction(Icons.Rounded.Calculate, "Calcular Custos", "Custo, preço e margem"),\n        HomeAction(Icons.Rounded.Folder, "Projetos", "Seus trabalhos"),'
if old not in text: raise SystemExit('home actions not found')
text = text.replace(old, new, 1)

old = '                                        "Minha Máquina" -> onMachine()\n                                        "Nova Matriz" -> onSoon('
new = '                                        "Minha Máquina" -> onMachine()\n                                        "Calcular Custos" -> onCosts()\n                                        "Nova Matriz" -> onSoon('
if old not in text: raise SystemExit('home handler not found')
text = text.replace(old, new, 1)

old = '        item { ProfileRow(Icons.Rounded.Settings, "Minhas Máquinas", onMachine) }\n        items(items.size)'
new = '        item { ProfileRow(Icons.Rounded.Settings, "Minhas Máquinas", onMachine) }\n        item { ProfileRow(Icons.Rounded.Star, "Meu Plano") { onSoon("Planos BORDATTO estão em estudo. Durante o desenvolvimento, nenhum recurso está bloqueado por assinatura.") } }\n        items(items.size)'
if old not in text: raise SystemExit('profile insertion not found')
text = text.replace(old, new, 1)

insert_at = text.index('private data class HoopOption(')
calculator = r'''@Composable
private fun CostCalculatorScreen(onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var materials by remember { mutableStateOf("7,20") }
    var laborHour by remember { mutableStateOf("20,00") }
    var machineHour by remember { mutableStateOf("8,00") }
    var minutes by remember { mutableStateOf("15") }
    var extras by remember { mutableStateOf("2,00") }
    var margin by remember { mutableStateOf("50") }
    var quantity by remember { mutableStateOf("1") }

    fun n(v: String) = v.replace(',', '.').toDoubleOrNull() ?: 0.0
    fun money(v: Double) = "R$ " + "%.2f".format(v)
    val timeCost = (n(laborHour) + n(machineHour)) * (n(minutes) / 60.0)
    val unitCost = n(materials) + n(extras) + timeCost
    val marginPct = n(margin).coerceIn(0.0, 80.0)
    val sale = if (marginPct == 0.0) unitCost else unitCost / (1.0 - marginPct / 100.0)
    val profit = (sale - unitCost).coerceAtLeast(0.0)
    val qty = n(quantity).toInt().coerceAtLeast(1)

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, top = 16.dp, end = 16.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item { PageHeader("Calculadora de Custos", onBack) }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(26.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
                Row(Modifier.fillMaxWidth().padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.Calculate, selected = true, size = 56.dp)
                    Spacer(Modifier.width(13.dp))
                    Column {
                        Text("Custo e preço de venda", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                        Text("Faça a conta do bordado sem sair do BORDATTO.", color = Muted, fontSize = 10.sp)
                    }
                }
            }
        }
        item { CostField("Materiais por peça", materials) { materials = it } }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                CostField("Mão de obra / hora", laborHour, Modifier.weight(1f)) { laborHour = it }
                CostField("Máquina / hora", machineHour, Modifier.weight(1f)) { machineHour = it }
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                CostField("Tempo (min)", minutes, Modifier.weight(1f), false) { minutes = it }
                CostField("Custos extras", extras, Modifier.weight(1f)) { extras = it }
            }
        }
        item { CostField("Quantidade", quantity, moneyPrefix = false) { quantity = it } }
        item {
            Surface(shape = RoundedCornerShape(22.dp), color = CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.45f))) {
                Column(Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Margem desejada", color = Cream, modifier = Modifier.weight(1f))
                        Text("${marginPct.toInt()}%", color = Gold, fontWeight = FontWeight.Bold)
                    }
                    Slider(marginPct.toFloat(), { margin = it.toInt().toString() }, valueRange = 0f..80f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
                    Text("Margem calculada sobre o preço final de venda.", color = Muted, fontSize = 9.sp)
                }
            }
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Gold.copy(alpha=.13f)), shape = RoundedCornerShape(28.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha=.7f))) {
                Column(Modifier.fillMaxWidth().padding(18.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
                    Text("Resumo", color = Gold, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                    CostRow("Custo por peça", money(unitCost))
                    CostRow("Preço sugerido", money(sale), true)
                    CostRow("Lucro bruto por peça", money(profit))
                    if (qty > 1) {
                        HorizontalDivider(color = LineGold.copy(alpha=.5f))
                        CostRow("Custo total ($qty peças)", money(unitCost * qty))
                        CostRow("Venda total", money(sale * qty), true)
                    }
                }
            }
        }
        item {
            Text("Futuramente pontos, tempo e consumo de linha poderão vir automaticamente da matriz aberta.", color = Muted, fontSize = 9.sp, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
        }
    }
}

@Composable
private fun CostField(label: String, value: String, modifier: Modifier = Modifier.fillMaxWidth(), moneyPrefix: Boolean = true, onChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = { onChange(it.filter { c -> c.isDigit() || c == ',' || c == '.' }.take(10)) },
        modifier = modifier,
        label = { Text(label, fontSize = 10.sp) },
        prefix = if (moneyPrefix) ({ Text("R$") }) else null,
        singleLine = true,
        colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold, focusedLabelColor = Gold)
    )
}

@Composable
private fun CostRow(label: String, value: String, highlight: Boolean = false) {
    Row(Modifier.fillMaxWidth()) {
        Text(label, color = if (highlight) Cream else Muted, fontSize = if (highlight) 12.sp else 10.sp, modifier = Modifier.weight(1f))
        Text(value, color = if (highlight) Gold else Cream, fontWeight = if (highlight) FontWeight.Bold else FontWeight.Medium, fontSize = if (highlight) 15.sp else 11.sp)
    }
}

'''
text = text[:insert_at] + calculator + text[insert_at:]
text = text.replace('0.2.4', '0.2.5')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.5 cost calculator patch applied successfully')
