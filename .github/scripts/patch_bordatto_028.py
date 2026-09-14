from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_027.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Persistent local library model and lightweight storage helpers.
marker = '''private data class HoopFit(
    val hoop: HoopOption,
    val fits: Boolean,
    val rotated: Boolean
)
'''
addition = '''private data class HoopFit(
    val hoop: HoopOption,
    val fits: Boolean,
    val rotated: Boolean
)

private data class LibraryItem(
    val uri: String,
    val name: String,
    val widthMm: Float,
    val heightMm: Float,
    val stitchCount: Int,
    val colors: Int,
    val openedAt: Long,
    val favorite: Boolean = false
)

private const val PREFS_NAME = "bordatto_local_v1"

private fun appPrefs(context: android.content.Context) =
    context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)

private fun loadMachineConfig(context: android.content.Context): MachineConfig {
    val p = appPrefs(context)
    val ids = p.getString("machine_hoops", "130x180")
        ?.split('|')?.filter { it.isNotBlank() }?.toSet() ?: setOf("130x180")
    val cw = p.getInt("machine_custom_w", -1).takeIf { it > 0 }
    val ch = p.getInt("machine_custom_h", -1).takeIf { it > 0 }
    return MachineConfig(
        brand = p.getString("machine_brand", "Brother") ?: "Brother",
        model = p.getString("machine_model", "PE770") ?: "PE770",
        format = p.getString("machine_format", "PES") ?: "PES",
        selectedHoopIds = ids,
        customWidthMm = cw,
        customHeightMm = ch
    )
}

private fun saveMachineConfig(context: android.content.Context, config: MachineConfig) {
    appPrefs(context).edit()
        .putString("machine_brand", config.brand)
        .putString("machine_model", config.model)
        .putString("machine_format", config.format)
        .putString("machine_hoops", config.selectedHoopIds.joinToString("|"))
        .putInt("machine_custom_w", config.customWidthMm ?: -1)
        .putInt("machine_custom_h", config.customHeightMm ?: -1)
        .apply()
}

private fun loadLibrary(context: android.content.Context): List<LibraryItem> {
    val raw = appPrefs(context).getString("library_json", "[]") ?: "[]"
    return runCatching {
        val array = org.json.JSONArray(raw)
        buildList {
            for (i in 0 until array.length()) {
                val o = array.getJSONObject(i)
                add(
                    LibraryItem(
                        uri = o.getString("uri"),
                        name = o.optString("name", "matriz.dst"),
                        widthMm = o.optDouble("w", 0.0).toFloat(),
                        heightMm = o.optDouble("h", 0.0).toFloat(),
                        stitchCount = o.optInt("stitches", 0),
                        colors = o.optInt("colors", 0),
                        openedAt = o.optLong("opened", 0L),
                        favorite = o.optBoolean("favorite", false)
                    )
                )
            }
        }.sortedWith(compareByDescending<LibraryItem> { it.favorite }.thenByDescending { it.openedAt })
    }.getOrElse { emptyList() }
}

private fun persistLibrary(context: android.content.Context, items: List<LibraryItem>) {
    val array = org.json.JSONArray()
    items.forEach { item ->
        array.put(org.json.JSONObject().apply {
            put("uri", item.uri)
            put("name", item.name)
            put("w", item.widthMm.toDouble())
            put("h", item.heightMm.toDouble())
            put("stitches", item.stitchCount)
            put("colors", item.colors)
            put("opened", item.openedAt)
            put("favorite", item.favorite)
        })
    }
    appPrefs(context).edit().putString("library_json", array.toString()).apply()
}

private fun upsertLibrary(context: android.content.Context, current: List<LibraryItem>, item: LibraryItem): List<LibraryItem> {
    val previous = current.firstOrNull { it.uri == item.uri }
    val merged = item.copy(favorite = previous?.favorite ?: item.favorite)
    val next = (current.filterNot { it.uri == item.uri } + merged)
        .sortedWith(compareByDescending<LibraryItem> { it.favorite }.thenByDescending { it.openedAt })
        .take(100)
    persistLibrary(context, next)
    return next
}
'''
if marker not in text: raise SystemExit('HoopFit marker not found')
text = text.replace(marker, addition, 1)

# Load persisted state instead of resetting every app launch.
old = '''    var machineConfig by remember { mutableStateOf(MachineConfig()) }
'''
new = '''    var machineConfig by remember(context) { mutableStateOf(loadMachineConfig(context)) }
    var libraryItems by remember(context) { mutableStateOf(loadLibrary(context)) }
'''
if old not in text: raise SystemExit('machineConfig root state not found')
text = text.replace(old, new, 1)

# Try to retain Android document permission so Library entries can be reopened after app restart.
old = '''                val resolver = context.contentResolver
                val name = resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { c ->'''
new = '''                val resolver = context.contentResolver
                runCatching {
                    resolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }
                val name = resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { c ->'''
if old not in text: raise SystemExit('resolver block not found')
text = text.replace(old, new, 1)

# Save successful DST opens into the local persistent library.
old = '''        }.onSuccess {
            design = it
            activeTab = MainTab.HOME
            page = Page.MAIN
        }.onFailure { error = it.message ?: "Erro ao abrir a matriz." }'''
new = '''        }.onSuccess { openedDesign ->
            design = openedDesign
            libraryItems = upsertLibrary(
                context,
                libraryItems,
                LibraryItem(
                    uri = uri.toString(),
                    name = openedDesign.name,
                    widthMm = openedDesign.width,
                    heightMm = openedDesign.height,
                    stitchCount = openedDesign.stitchCount,
                    colors = openedDesign.colors,
                    openedAt = System.currentTimeMillis()
                )
            )
            activeTab = MainTab.HOME
            page = Page.MAIN
        }.onFailure { error = it.message ?: "Erro ao abrir a matriz." }'''
if old not in text: raise SystemExit('open success block not found')
text = text.replace(old, new, 1)

# Persist machine configuration permanently on save.
old = '''                    onSave = { saved ->
                        machineConfig = saved
                        page = Page.MAIN
                        notice = "Máquina e bastidores salvos nesta sessão. O Machine Check já vai usar essa configuração nas matrizes abertas."
                    }
                )'''
new = '''                    onSave = { saved ->
                        machineConfig = saved
                        saveMachineConfig(context, saved)
                        page = Page.MAIN
                        notice = "Máquina e bastidores salvos no aparelho. O Machine Check continuará usando essa configuração mesmo depois de fechar o BORDATTO."
                    }
                )'''
if old not in text: raise SystemExit('machine save block not found')
text = text.replace(old, new, 1)

# Pass persistent library state/actions into StudioShell.
old = '''                    onMachine = { page = Page.MACHINE },
                    onCosts = { page = Page.COSTS },
                    onSoon = { notice = it }
                )'''
new = '''                    onMachine = { page = Page.MACHINE },
                    onCosts = { page = Page.COSTS },
                    libraryItems = libraryItems,
                    onOpenLibraryItem = { item ->
                        pendingUri = Uri.parse(item.uri)
                        activeTab = MainTab.HOME
                        page = Page.MAIN
                    },
                    onToggleLibraryFavorite = { item ->
                        libraryItems = libraryItems.map {
                            if (it.uri == item.uri) it.copy(favorite = !it.favorite) else it
                        }.sortedWith(compareByDescending<LibraryItem> { it.favorite }.thenByDescending { it.openedAt })
                        persistLibrary(context, libraryItems)
                    },
                    onDeleteLibraryItem = { item ->
                        libraryItems = libraryItems.filterNot { it.uri == item.uri }
                        persistLibrary(context, libraryItems)
                    },
                    onSoon = { notice = it }
                )'''
if old not in text: raise SystemExit('StudioShell root args not found')
text = text.replace(old, new, 1)

old = '''    onLettering: () -> Unit,
    onMachine: () -> Unit,
    onCosts: () -> Unit,
    onSoon: (String) -> Unit
) {'''
new = '''    onLettering: () -> Unit,
    onMachine: () -> Unit,
    onCosts: () -> Unit,
    libraryItems: List<LibraryItem>,
    onOpenLibraryItem: (LibraryItem) -> Unit,
    onToggleLibraryFavorite: (LibraryItem) -> Unit,
    onDeleteLibraryItem: (LibraryItem) -> Unit,
    onSoon: (String) -> Unit
) {'''
if old not in text: raise SystemExit('StudioShell signature not found')
text = text.replace(old, new, 1)

old = '''                MainTab.LIBRARY -> LibraryScreen(onSoon)'''
new = '''                MainTab.LIBRARY -> LibraryScreen(
                    items = libraryItems,
                    onOpen = onOpenLibraryItem,
                    onToggleFavorite = onToggleLibraryFavorite,
                    onDelete = onDeleteLibraryItem,
                    onImport = onOpenMatrix
                )'''
if old not in text: raise SystemExit('Library route not found')
text = text.replace(old, new, 1)

# Replace placeholder category library with a real recent/favorites library.
start = text.index('@Composable\nprivate fun LibraryScreen')
end = text.index('@Composable\nprivate fun ProfileScreen', start)
new_library = r'''@Composable
private fun LibraryScreen(
    items: List<LibraryItem>,
    onOpen: (LibraryItem) -> Unit,
    onToggleFavorite: (LibraryItem) -> Unit,
    onDelete: (LibraryItem) -> Unit,
    onImport: () -> Unit
) {
    var query by remember { mutableStateOf("") }
    var favoritesOnly by remember { mutableStateOf(false) }
    val filtered = remember(items, query, favoritesOnly) {
        items.filter { item ->
            (!favoritesOnly || item.favorite) &&
                (query.isBlank() || item.name.contains(query, ignoreCase = true))
        }
    }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 18.dp, top = 16.dp, end = 18.dp, bottom = 22.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { BrandHeader("Biblioteca") }
        item {
            Row(verticalAlignment = Alignment.Bottom) {
                Column(Modifier.weight(1f)) {
                    Text("Minhas matrizes", color = Cream, fontSize = 23.sp, fontFamily = FontFamily.Serif)
                    Text("Recentes salvos localmente no aparelho", color = Muted, fontSize = 11.sp)
                }
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .13f)) {
                    Text("${items.size} arquivo${if (items.size == 1) "" else "s"}", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
                }
            }
        }
        item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Buscar pelo nome da matriz") },
                leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Gold) },
                trailingIcon = {
                    if (query.isNotBlank()) IconButton(onClick = { query = "" }) {
                        Icon(Icons.Rounded.Close, "Limpar busca", tint = Muted)
                    }
                },
                singleLine = true,
                shape = RoundedCornerShape(20.dp),
                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold)
            )
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                FilterChip(
                    selected = !favoritesOnly,
                    onClick = { favoritesOnly = false },
                    label = { Text("Recentes") },
                    leadingIcon = { Icon(Icons.Rounded.History, null, modifier = Modifier.size(17.dp)) },
                    colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Gold.copy(alpha = .17f), selectedLabelColor = Gold, selectedLeadingIconColor = Gold)
                )
                FilterChip(
                    selected = favoritesOnly,
                    onClick = { favoritesOnly = true },
                    label = { Text("Favoritos") },
                    leadingIcon = { Icon(Icons.Rounded.Favorite, null, modifier = Modifier.size(17.dp)) },
                    colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Gold.copy(alpha = .17f), selectedLabelColor = Gold, selectedLeadingIconColor = Gold)
                )
                Spacer(Modifier.weight(1f))
                FilledTonalButton(
                    onClick = onImport,
                    shape = RoundedCornerShape(18.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha=.14f), contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.FileOpen, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Importar", fontSize = 10.sp)
                }
            }
        }

        if (filtered.isEmpty()) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = CardBrown),
                    shape = RoundedCornerShape(26.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.5f))
                ) {
                    Column(Modifier.fillMaxWidth().padding(26.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        ExpressiveIconBadge(if (favoritesOnly) Icons.Rounded.FavoriteBorder else Icons.Rounded.Collections, selected = true, size = 62.dp)
                        Spacer(Modifier.height(13.dp))
                        Text(if (favoritesOnly) "Nenhum favorito ainda" else if (items.isEmpty()) "Sua biblioteca está vazia" else "Nenhum resultado encontrado", color = Cream, fontWeight = FontWeight.SemiBold)
                        Text(
                            if (favoritesOnly) "Toque no coração de uma matriz para deixá-la sempre no topo."
                            else if (items.isEmpty()) "Abra um arquivo DST e ele aparecerá aqui automaticamente."
                            else "Tente outro nome na busca.",
                            color = Muted,
                            fontSize = 11.sp,
                            textAlign = TextAlign.Center
                        )
                        if (items.isEmpty()) {
                            Spacer(Modifier.height(14.dp))
                            Button(onClick = onImport, colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink), shape = RoundedCornerShape(18.dp)) {
                                Icon(Icons.Rounded.FileOpen, null, modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(7.dp))
                                Text("Abrir primeira matriz")
                            }
                        }
                    }
                }
            }
        } else {
            items(filtered.size) { index ->
                val item = filtered[index]
                Card(
                    onClick = { onOpen(item) },
                    colors = CardDefaults.cardColors(containerColor = CardBrown),
                    shape = RoundedCornerShape(22.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, if (item.favorite) Gold.copy(alpha=.62f) else LineGold.copy(alpha=.43f))
                ) {
                    Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                        ExpressiveIconBadge(Icons.Rounded.Description, selected = item.favorite, size = 50.dp)
                        Spacer(Modifier.width(12.dp))
                        Column(Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(item.name, color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 13.sp, maxLines = 1, modifier = Modifier.weight(1f))
                                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha=.13f)) {
                                    Text("DST", color = Gold, fontSize = 8.sp, modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp))
                                }
                            }
                            Spacer(Modifier.height(4.dp))
                            Text("${item.stitchCount} pontos • ${"%.1f".format(item.widthMm)} × ${"%.1f".format(item.heightMm)} mm • ${item.colors} cores", color = Muted, fontSize = 9.sp, maxLines = 1)
                            Text("Toque para reabrir", color = Gold.copy(alpha=.82f), fontSize = 8.sp)
                        }
                        IconButton(onClick = { onToggleFavorite(item) }) {
                            Icon(if (item.favorite) Icons.Rounded.Favorite else Icons.Rounded.FavoriteBorder, if (item.favorite) "Remover favorito" else "Favoritar", tint = if (item.favorite) Gold else Muted)
                        }
                        IconButton(onClick = { onDelete(item) }) {
                            Icon(Icons.Rounded.DeleteOutline, "Remover da biblioteca", tint = Muted)
                        }
                    }
                }
            }
        }
        item {
            Surface(color = SurfaceBrown, shape = RoundedCornerShape(18.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.35f))) {
                Row(Modifier.fillMaxWidth().padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Storage, null, tint = Gold, modifier = Modifier.size(19.dp))
                    Spacer(Modifier.width(9.dp))
                    Text("A Biblioteca guarda metadados e o acesso ao arquivo no próprio aparelho. O arquivo original continua no local escolhido por você.", color = Muted, fontSize = 9.sp, lineHeight = 12.sp)
                }
            }
        }
    }
}

'''
text = text[:start] + new_library + text[end:]

text = text.replace('0.2.7', '0.2.8')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.8 persistence and real library patch applied successfully')
