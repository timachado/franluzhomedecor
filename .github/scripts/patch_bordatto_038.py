from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_037.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# BORDATTO 0.2.17 — Projetos Editáveis
# Internal project format: app-private BDP snapshots of the original + working
# Design model. This is intentionally NOT an embroidery export writer.
# -----------------------------------------------------------------------------

insert_at = text.index('class MainActivity')
project_core = r'''private data class ProjectItem(
    val id: String,
    val name: String,
    val sourceUri: String?,
    val format: String,
    val widthMm: Float,
    val heightMm: Float,
    val stitchCount: Int,
    val colors: Int,
    val createdAt: Long,
    val updatedAt: Long,
    val favorite: Boolean = false,
    val notes: String = "",
    val editCount: Int = 0
)

private data class ProjectBundle(
    val original: Design,
    val working: Design
)

private const val PROJECTS_PREF_KEY = "editable_projects_json_v1"
private const val PROJECT_MAGIC = 0x42445031 // BDP1
private const val PROJECT_BINARY_VERSION = 1

private fun projectDirectory(context: android.content.Context): java.io.File =
    java.io.File(context.filesDir, "bordatto_projects").apply { mkdirs() }

private fun projectOriginalFile(context: android.content.Context, id: String) =
    java.io.File(projectDirectory(context), "$id.original.bdp")

private fun projectWorkingFile(context: android.content.Context, id: String) =
    java.io.File(projectDirectory(context), "$id.working.bdp")

private fun projectSort(items: List<ProjectItem>): List<ProjectItem> =
    items.sortedWith(compareByDescending<ProjectItem> { it.favorite }.thenByDescending { it.updatedAt })

private fun loadProjects(context: android.content.Context): List<ProjectItem> {
    val raw = appPrefs(context).getString(PROJECTS_PREF_KEY, "[]") ?: "[]"
    return runCatching {
        val array = org.json.JSONArray(raw)
        buildList {
            for (i in 0 until array.length()) {
                val o = array.getJSONObject(i)
                add(
                    ProjectItem(
                        id = o.getString("id"),
                        name = o.optString("name", "Projeto BORDATTO"),
                        sourceUri = o.optString("sourceUri", "").takeIf { it.isNotBlank() },
                        format = o.optString("format", "DST"),
                        widthMm = o.optDouble("w", 0.0).toFloat(),
                        heightMm = o.optDouble("h", 0.0).toFloat(),
                        stitchCount = o.optInt("stitches", 0),
                        colors = o.optInt("colors", 0),
                        createdAt = o.optLong("created", 0L),
                        updatedAt = o.optLong("updated", 0L),
                        favorite = o.optBoolean("favorite", false),
                        notes = o.optString("notes", ""),
                        editCount = o.optInt("edits", 0)
                    )
                )
            }
        }
    }.getOrElse { emptyList() }.let(::projectSort)
}

private fun persistProjects(context: android.content.Context, items: List<ProjectItem>) {
    val array = org.json.JSONArray()
    items.forEach { item ->
        array.put(org.json.JSONObject().apply {
            put("id", item.id)
            put("name", item.name)
            put("sourceUri", item.sourceUri ?: "")
            put("format", item.format)
            put("w", item.widthMm.toDouble())
            put("h", item.heightMm.toDouble())
            put("stitches", item.stitchCount)
            put("colors", item.colors)
            put("created", item.createdAt)
            put("updated", item.updatedAt)
            put("favorite", item.favorite)
            put("notes", item.notes)
            put("edits", item.editCount)
        })
    }
    appPrefs(context).edit().putString(PROJECTS_PREF_KEY, array.toString()).apply()
}

private fun commandToProjectByte(command: StitchCommand): Int = when (command) {
    StitchCommand.STITCH -> 0
    StitchCommand.JUMP -> 1
    StitchCommand.COLOR_CHANGE -> 2
    StitchCommand.TRIM -> 3
    StitchCommand.END -> 4
}

private fun projectByteToCommand(value: Int): StitchCommand = when (value) {
    0 -> StitchCommand.STITCH
    1 -> StitchCommand.JUMP
    2 -> StitchCommand.COLOR_CHANGE
    3 -> StitchCommand.TRIM
    4 -> StitchCommand.END
    else -> error("Comando interno de projeto inválido: $value")
}

private fun writeProjectDesign(file: java.io.File, design: Design) {
    val tmp = java.io.File(file.parentFile, file.name + ".tmp")
    java.io.DataOutputStream(java.io.BufferedOutputStream(java.io.FileOutputStream(tmp))).use { out ->
        out.writeInt(PROJECT_MAGIC)
        out.writeInt(PROJECT_BINARY_VERSION)
        out.writeUTF(design.name.take(2048))
        out.writeUTF(design.format.take(32))
        out.writeInt(design.colors)
        out.writeFloat(design.minX)
        out.writeFloat(design.minY)
        out.writeFloat(design.maxX)
        out.writeFloat(design.maxY)
        out.writeInt(design.stitches.size)
        design.stitches.forEach { stitch ->
            out.writeFloat(stitch.x)
            out.writeFloat(stitch.y)
            out.writeByte(commandToProjectByte(stitch.command))
            out.writeInt(stitch.color)
        }
    }
    if (file.exists() && !file.delete()) error("Não foi possível atualizar o snapshot do projeto.")
    if (!tmp.renameTo(file)) {
        tmp.copyTo(file, overwrite = true)
        tmp.delete()
    }
}

private fun readProjectDesign(file: java.io.File): Design {
    require(file.exists()) { "Snapshot interno do projeto não encontrado." }
    return java.io.DataInputStream(java.io.BufferedInputStream(java.io.FileInputStream(file))).use { input ->
        require(input.readInt() == PROJECT_MAGIC) { "Projeto BORDATTO inválido." }
        require(input.readInt() == PROJECT_BINARY_VERSION) { "Versão interna de projeto incompatível." }
        val name = input.readUTF()
        val format = input.readUTF()
        val colors = input.readInt().coerceAtLeast(1)
        val minX = input.readFloat()
        val minY = input.readFloat()
        val maxX = input.readFloat()
        val maxY = input.readFloat()
        val count = input.readInt()
        require(count in 0..5_000_000) { "Quantidade de pontos inválida no projeto." }
        val stitches = ArrayList<StitchPoint>(count)
        repeat(count) {
            stitches += StitchPoint(
                x = input.readFloat(),
                y = input.readFloat(),
                command = projectByteToCommand(input.readUnsignedByte()),
                color = input.readInt()
            )
        }
        Design(name, stitches, minX, minY, maxX, maxY, colors, format)
    }
}

private fun loadProjectBundle(context: android.content.Context, item: ProjectItem): ProjectBundle =
    ProjectBundle(
        original = readProjectDesign(projectOriginalFile(context, item.id)),
        working = readProjectDesign(projectWorkingFile(context, item.id))
    )

private fun projectEditCount(original: Design, working: Design): Int {
    val added = (working.stitchCount - original.stitchCount).coerceAtLeast(0)
    val trims = working.stitches.count { it.command == StitchCommand.TRIM }
    return added + trims
}

private fun saveEditableProjectFiles(
    context: android.content.Context,
    existing: ProjectItem?,
    sourceUri: String?,
    original: Design,
    working: Design
): ProjectItem {
    val now = System.currentTimeMillis()
    val id = existing?.id ?: java.util.UUID.randomUUID().toString()
    val originalFile = projectOriginalFile(context, id)
    if (existing == null || !originalFile.exists()) writeProjectDesign(originalFile, original)
    writeProjectDesign(projectWorkingFile(context, id), working)
    return ProjectItem(
        id = id,
        name = existing?.name ?: "${original.name} • Projeto",
        sourceUri = sourceUri ?: existing?.sourceUri,
        format = working.format,
        widthMm = working.width,
        heightMm = working.height,
        stitchCount = working.stitchCount,
        colors = working.colors,
        createdAt = existing?.createdAt ?: now,
        updatedAt = now,
        favorite = existing?.favorite ?: false,
        notes = existing?.notes ?: "",
        editCount = projectEditCount(original, working)
    )
}

private fun deleteProjectFiles(context: android.content.Context, item: ProjectItem) {
    projectOriginalFile(context, item.id).delete()
    projectWorkingFile(context, item.id).delete()
}

private fun duplicateProjectFiles(context: android.content.Context, item: ProjectItem): ProjectItem {
    val bundle = loadProjectBundle(context, item)
    val now = System.currentTimeMillis()
    val copy = saveEditableProjectFiles(
        context = context,
        existing = null,
        sourceUri = item.sourceUri,
        original = bundle.original,
        working = bundle.working
    )
    return copy.copy(
        name = item.name + " • Cópia",
        notes = item.notes,
        favorite = false,
        createdAt = now,
        updatedAt = now
    )
}

private fun formatProjectDate(timestamp: Long): String = runCatching {
    java.text.SimpleDateFormat("dd/MM • HH:mm", java.util.Locale.getDefault()).format(java.util.Date(timestamp))
}.getOrDefault("—")

'''
text = text[:insert_at] + project_core + text[insert_at:]

# Root state: persisted project list + currently open project/snapshot.
old = '''    var machineConfig by remember(context) { mutableStateOf(loadMachineConfig(context)) }
    var libraryItems by remember(context) { mutableStateOf(loadLibrary(context)) }
'''
new = '''    var machineConfig by remember(context) { mutableStateOf(loadMachineConfig(context)) }
    var libraryItems by remember(context) { mutableStateOf(loadLibrary(context)) }
    var projectItems by remember(context) { mutableStateOf(loadProjects(context)) }
    var activeProject by remember { mutableStateOf<ProjectItem?>(null) }
    var workingSeed by remember { mutableStateOf<Design?>(null) }
    var currentSourceUri by remember { mutableStateOf<String?>(null) }
    var pendingProject by remember { mutableStateOf<ProjectItem?>(null) }
'''
if old not in text: raise SystemExit('root persisted state marker not found')
text = text.replace(old, new, 1)

# A normal file open starts a new unsaved working session, separate from any project.
old = '''        }.onSuccess { openedDesign ->
            design = openedDesign
            libraryItems = upsertLibrary('''
new = '''        }.onSuccess { openedDesign ->
            design = openedDesign
            workingSeed = null
            activeProject = null
            currentSourceUri = uri.toString()
            libraryItems = upsertLibrary('''
if old not in text: raise SystemExit('open success project reset marker not found')
text = text.replace(old, new, 1)

# Load editable projects from app-private snapshots; reopening does not modify or depend on the external source file.
insert_marker = '''    MaterialTheme(
'''
pending_project_effect = r'''    LaunchedEffect(pendingProject?.id) {
        val project = pendingProject ?: return@LaunchedEffect
        loading = true
        error = null
        runCatching {
            withContext(Dispatchers.IO) { loadProjectBundle(context, project) }
        }.onSuccess { bundle ->
            design = bundle.original
            workingSeed = bundle.working
            activeProject = project
            currentSourceUri = project.sourceUri
            activeTab = MainTab.HOME
            page = Page.MAIN
        }.onFailure {
            error = it.message ?: "Não foi possível abrir o projeto salvo."
        }
        loading = false
        pendingProject = null
    }

    MaterialTheme(
'''
if insert_marker not in text: raise SystemExit('MaterialTheme marker for project loader not found')
text = text.replace(insert_marker, pending_project_effect, 1)

# Costs follow the current in-memory working copy when available.
old = '''                page == Page.COSTS -> CostCalculatorScreen(
                    design = design,
                    machineConfig = machineConfig,'''
new = '''                page == Page.COSTS -> CostCalculatorScreen(
                    design = workingSeed ?: design,
                    machineConfig = machineConfig,'''
if old not in text: raise SystemExit('cost route working copy marker not found')
text = text.replace(old, new, 1)

# Viewer receives/restores the editable project snapshot and can persist it asynchronously.
old = '''                design != null -> ViewerScreen(
                    design = design!!,
                    machineConfig = machineConfig,
                    onBack = { design = null },
                    onCosts = { page = Page.COSTS }
                )'''
new = '''                design != null -> ViewerScreen(
                    design = design!!,
                    machineConfig = machineConfig,
                    initialWorkingDesign = workingSeed,
                    activeProject = activeProject,
                    onWorkingChanged = { current -> workingSeed = current },
                    onSaveProject = { original, working ->
                        val saved = withContext(Dispatchers.IO) {
                            saveEditableProjectFiles(
                                context = context,
                                existing = activeProject,
                                sourceUri = currentSourceUri,
                                original = original,
                                working = working
                            )
                        }
                        projectItems = projectSort(projectItems.filterNot { it.id == saved.id } + saved)
                        persistProjects(context, projectItems)
                        activeProject = saved
                        workingSeed = working
                        saved
                    },
                    onBack = {
                        design = null
                        workingSeed = null
                        activeProject = null
                        currentSourceUri = null
                    },
                    onCosts = { page = Page.COSTS }
                )'''
if old not in text: raise SystemExit('viewer route for editable projects not found')
text = text.replace(old, new, 1)

# Project callbacks into StudioShell.
old = '''                    onCosts = { page = Page.COSTS },
                    libraryItems = libraryItems,'''
new = '''                    onCosts = { page = Page.COSTS },
                    projectItems = projectItems,
                    onOpenProject = { item ->
                        pendingProject = item
                        activeTab = MainTab.HOME
                    },
                    onToggleProjectFavorite = { item ->
                        projectItems = projectSort(projectItems.map { if (it.id == item.id) it.copy(favorite = !it.favorite) else it })
                        persistProjects(context, projectItems)
                    },
                    onUpdateProject = { item, name, notes ->
                        val updated = item.copy(
                            name = name.trim().ifBlank { item.name },
                            notes = notes.trim(),
                            updatedAt = System.currentTimeMillis()
                        )
                        projectItems = projectSort(projectItems.map { if (it.id == item.id) updated else it })
                        persistProjects(context, projectItems)
                        if (activeProject?.id == item.id) activeProject = updated
                    },
                    onDuplicateProject = { item ->
                        runCatching { duplicateProjectFiles(context, item) }
                            .onSuccess { copy ->
                                projectItems = projectSort(projectItems + copy)
                                persistProjects(context, projectItems)
                            }
                            .onFailure { error = it.message ?: "Não foi possível duplicar o projeto." }
                    },
                    onDeleteProject = { item ->
                        deleteProjectFiles(context, item)
                        projectItems = projectItems.filterNot { it.id == item.id }
                        persistProjects(context, projectItems)
                    },
                    libraryItems = libraryItems,'''
if old not in text: raise SystemExit('StudioShell root project args marker not found')
text = text.replace(old, new, 1)

# StudioShell signature and Projects route.
old = '''    onCosts: () -> Unit,
    libraryItems: List<LibraryItem>,'''
new = '''    onCosts: () -> Unit,
    projectItems: List<ProjectItem>,
    onOpenProject: (ProjectItem) -> Unit,
    onToggleProjectFavorite: (ProjectItem) -> Unit,
    onUpdateProject: (ProjectItem, String, String) -> Unit,
    onDuplicateProject: (ProjectItem) -> Unit,
    onDeleteProject: (ProjectItem) -> Unit,
    libraryItems: List<LibraryItem>,'''
if old not in text: raise SystemExit('StudioShell signature project marker not found')
text = text.replace(old, new, 1)

old = '''                MainTab.PROJECTS -> ProjectsScreen(onLettering)'''
new = '''                MainTab.PROJECTS -> ProjectsScreen(
                    items = projectItems,
                    onOpen = onOpenProject,
                    onToggleFavorite = onToggleProjectFavorite,
                    onUpdate = onUpdateProject,
                    onDuplicate = onDuplicateProject,
                    onDelete = onDeleteProject,
                    onImport = onOpenMatrix
                )'''
if old not in text: raise SystemExit('Projects route marker not found')
text = text.replace(old, new, 1)

# Replace the old empty Projects screen with the real editable-project library.
start = text.index('@Composable\nprivate fun ProjectsScreen')
end = text.index('private data class LibraryCategory', start)
projects_ui = r'''@Composable
private fun ProjectsScreen(
    items: List<ProjectItem>,
    onOpen: (ProjectItem) -> Unit,
    onToggleFavorite: (ProjectItem) -> Unit,
    onUpdate: (ProjectItem, String, String) -> Unit,
    onDuplicate: (ProjectItem) -> Unit,
    onDelete: (ProjectItem) -> Unit,
    onImport: () -> Unit
) {
    var query by remember { mutableStateOf("") }
    var favoritesOnly by remember { mutableStateOf(false) }
    var editingProject by remember { mutableStateOf<ProjectItem?>(null) }
    var editName by remember { mutableStateOf("") }
    var editNotes by remember { mutableStateOf("") }
    var deleteProject by remember { mutableStateOf<ProjectItem?>(null) }

    val filtered = remember(items, query, favoritesOnly) {
        items.filter { item ->
            (!favoritesOnly || item.favorite) &&
                (query.isBlank() || item.name.contains(query, ignoreCase = true) || item.notes.contains(query, ignoreCase = true))
        }
    }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 18.dp, top = 16.dp, end = 18.dp, bottom = 26.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { BrandHeader("Projetos") }
        item {
            Row(verticalAlignment = Alignment.Bottom) {
                Column(Modifier.weight(1f)) {
                    Text("Projetos editáveis", color = Cream, fontSize = 23.sp, fontFamily = FontFamily.Serif)
                    Text("Retome sua cópia de trabalho sem tocar no arquivo original", color = Muted, fontSize = 10.sp)
                }
                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha = .13f)) {
                    Text("${items.size} projeto${if (items.size == 1) "" else "s"}", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
                }
            }
        }
        item {
            Surface(
                color = Gold.copy(alpha = .08f),
                shape = RoundedCornerShape(20.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .35f))
            ) {
                Row(Modifier.fillMaxWidth().padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Shield, null, tint = Gold, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(9.dp))
                    Text(
                        "O projeto guarda snapshots internos BORDATTO do original e da cópia editada. Isso não regrava DST/PES/JEF nem altera o arquivo escolhido no celular.",
                        color = Muted,
                        fontSize = 8.sp,
                        lineHeight = 11.sp
                    )
                }
            }
        }
        item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Buscar projeto ou anotação") },
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
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                FilterChip(
                    selected = !favoritesOnly,
                    onClick = { favoritesOnly = false },
                    label = { Text("Recentes") },
                    leadingIcon = { Icon(Icons.Rounded.History, null, modifier = Modifier.size(16.dp)) },
                    colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Gold.copy(alpha=.16f), selectedLabelColor = Gold, selectedLeadingIconColor = Gold)
                )
                FilterChip(
                    selected = favoritesOnly,
                    onClick = { favoritesOnly = true },
                    label = { Text("Favoritos") },
                    leadingIcon = { Icon(Icons.Rounded.Favorite, null, modifier = Modifier.size(16.dp)) },
                    colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Gold.copy(alpha=.16f), selectedLabelColor = Gold, selectedLeadingIconColor = Gold)
                )
                Spacer(Modifier.weight(1f))
                FilledTonalButton(
                    onClick = onImport,
                    shape = RoundedCornerShape(17.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha=.14f), contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.FileOpen, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(5.dp))
                    Text("Abrir matriz", fontSize = 9.sp)
                }
            }
        }

        if (filtered.isEmpty()) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = CardBrown),
                    shape = RoundedCornerShape(26.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.52f))
                ) {
                    Column(Modifier.fillMaxWidth().padding(26.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        ExpressiveIconBadge(Icons.Rounded.FolderOpen, selected = true, size = 62.dp)
                        Spacer(Modifier.height(13.dp))
                        Text(if (items.isEmpty()) "Nenhum projeto salvo ainda" else "Nenhum projeto encontrado", color = Cream, fontWeight = FontWeight.SemiBold)
                        Text(
                            if (items.isEmpty()) "Abra uma matriz, faça ou não suas correções e toque em Salvar projeto no Editor Seguro."
                            else "Tente outro termo ou volte para Recentes.",
                            color = Muted,
                            fontSize = 10.sp,
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
            repeat(filtered.size) { index ->
                val project = filtered[index]
                item {
                    Card(
                        onClick = { onOpen(project) },
                        colors = CardDefaults.cardColors(containerColor = CardBrown),
                        shape = RoundedCornerShape(23.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (project.favorite) Gold.copy(alpha=.62f) else LineGold.copy(alpha=.43f))
                    ) {
                        Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                ExpressiveIconBadge(if (project.editCount > 0) Icons.Rounded.EditNote else Icons.Rounded.Folder, selected = project.favorite, size = 46.dp)
                                Spacer(Modifier.width(10.dp))
                                Column(Modifier.weight(1f)) {
                                    Text(project.name, color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 13.sp, maxLines = 1)
                                    Text("${project.format} • ${project.stitchCount} pontos • ${"%.1f".format(project.widthMm)} × ${"%.1f".format(project.heightMm)} mm", color = Muted, fontSize = 8.sp, maxLines = 1)
                                    Text("Atualizado ${formatProjectDate(project.updatedAt)}", color = Muted.copy(alpha=.8f), fontSize = 7.sp)
                                }
                                IconButton(onClick = { onToggleFavorite(project) }) {
                                    Icon(if (project.favorite) Icons.Rounded.Favorite else Icons.Rounded.FavoriteBorder, "Favorito", tint = if (project.favorite) Gold else Muted)
                                }
                            }

                            if (project.notes.isNotBlank()) {
                                Text(project.notes, color = Cream.copy(alpha=.82f), fontSize = 8.sp, lineHeight = 11.sp, maxLines = 2)
                            }

                            Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                                Surface(shape = RoundedCornerShape(50), color = Gold.copy(alpha=.12f)) {
                                    Text(
                                        if (project.editCount == 0) "SEM CORREÇÕES" else "${project.editCount} ALTERAÇÃO${if (project.editCount == 1) "" else "ÕES"}",
                                        color = Gold,
                                        fontSize = 7.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 5.dp)
                                    )
                                }
                                Spacer(Modifier.weight(1f))
                                ExpressiveIconButton(Icons.Rounded.Edit, "Renomear e anotar") {
                                    editingProject = project
                                    editName = project.name
                                    editNotes = project.notes
                                }
                                ExpressiveIconButton(Icons.Rounded.ContentCopy, "Duplicar") { onDuplicate(project) }
                                ExpressiveIconButton(Icons.Rounded.DeleteOutline, "Excluir") { deleteProject = project }
                            }
                        }
                    }
                }
            }
        }

        item {
            Text(
                "Projetos são locais ao BORDATTO. Desinstalar o app ou limpar seus dados remove estes snapshots; o arquivo original externo continua independente.",
                color = Muted,
                fontSize = 8.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth().padding(top = 4.dp)
            )
        }
    }

    editingProject?.let { project ->
        AlertDialog(
            onDismissRequest = { editingProject = null },
            icon = { Icon(Icons.Rounded.EditNote, null, tint = Gold) },
            title = { Text("Editar projeto", color = Gold, fontFamily = FontFamily.Serif) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = editName,
                        onValueChange = { editName = it.take(80) },
                        label = { Text("Nome") },
                        singleLine = true,
                        shape = RoundedCornerShape(16.dp),
                        colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold)
                    )
                    OutlinedTextField(
                        value = editNotes,
                        onValueChange = { editNotes = it.take(300) },
                        label = { Text("Anotações") },
                        minLines = 3,
                        maxLines = 5,
                        shape = RoundedCornerShape(16.dp),
                        colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold)
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    onUpdate(project, editName, editNotes)
                    editingProject = null
                }) { Text("Salvar", color = Gold) }
            },
            dismissButton = { TextButton(onClick = { editingProject = null }) { Text("Cancelar") } }
        )
    }

    deleteProject?.let { project ->
        AlertDialog(
            onDismissRequest = { deleteProject = null },
            icon = { Icon(Icons.Rounded.DeleteOutline, null, tint = Gold) },
            title = { Text("Excluir projeto?", color = Gold, fontFamily = FontFamily.Serif) },
            text = { Text("Isso remove apenas os snapshots internos e o registro do projeto. O arquivo original não será apagado.") },
            confirmButton = {
                TextButton(onClick = {
                    onDelete(project)
                    deleteProject = null
                }) { Text("Excluir", color = Gold) }
            },
            dismissButton = { TextButton(onClick = { deleteProject = null }) { Text("Cancelar") } }
        )
    }
}

'''
text = text[:start] + projects_ui + text[end:]

# Viewer signature: seed the working copy from a persisted project and keep it lifted to root.
old = '''private fun ViewerScreen(design: Design, machineConfig: MachineConfig, onBack: () -> Unit, onCosts: () -> Unit) {
    BackHandler(onBack = onBack)
    var workingDesign by remember(design) { mutableStateOf(design.copy(stitches = design.stitches.toList())) }
    var undoStack by remember(design) { mutableStateOf<List<Design>>(emptyList()) }
    var redoStack by remember(design) { mutableStateOf<List<Design>>(emptyList()) }
'''
new = '''private fun ViewerScreen(
    design: Design,
    machineConfig: MachineConfig,
    initialWorkingDesign: Design? = null,
    activeProject: ProjectItem? = null,
    onWorkingChanged: (Design) -> Unit = {},
    onSaveProject: suspend (Design, Design) -> ProjectItem?,
    onBack: () -> Unit,
    onCosts: () -> Unit
) {
    BackHandler(onBack = onBack)
    var workingDesign by remember(design, initialWorkingDesign) {
        mutableStateOf(initialWorkingDesign ?: design.copy(stitches = design.stitches.toList()))
    }
    var savedWorkingSnapshot by remember(design, initialWorkingDesign, activeProject?.id) {
        mutableStateOf(initialWorkingDesign ?: design.copy(stitches = design.stitches.toList()))
    }
    var localProject by remember(activeProject) { mutableStateOf(activeProject) }
    var projectSaving by remember { mutableStateOf(false) }
    var saveProjectRequest by remember { mutableIntStateOf(0) }
    var undoStack by remember(design, initialWorkingDesign) { mutableStateOf<List<Design>>(emptyList()) }
    var redoStack by remember(design, initialWorkingDesign) { mutableStateOf<List<Design>>(emptyList()) }

    LaunchedEffect(workingDesign) { onWorkingChanged(workingDesign) }
    LaunchedEffect(saveProjectRequest) {
        if (saveProjectRequest > 0 && !projectSaving) {
            projectSaving = true
            runCatching { onSaveProject(design, workingDesign) }
                .onSuccess { saved ->
                    if (saved != null) {
                        localProject = saved
                        savedWorkingSnapshot = workingDesign
                    }
                }
            projectSaving = false
        }
    }
'''
if old not in text: raise SystemExit('ViewerScreen signature/state marker not found for projects')
text = text.replace(old, new, 1)

# Pass project save state into the Safe Editor panel.
old = '''        SafeEditorPanel(
            original = design,
            working = workingDesign,
            canUndo = undoStack.isNotEmpty(),
            canRedo = redoStack.isNotEmpty(),'''
new = '''        SafeEditorPanel(
            original = design,
            working = workingDesign,
            savedWorking = savedWorkingSnapshot,
            projectName = localProject?.name,
            savingProject = projectSaving,
            canUndo = undoStack.isNotEmpty(),
            canRedo = redoStack.isNotEmpty(),'''
if old not in text: raise SystemExit('SafeEditorPanel call project status marker not found')
text = text.replace(old, new, 1)

old = '''            onReset = {
                if (workingDesign != design) {
                    commitWorkingEdit(design.copy(stitches = design.stitches.toList()))
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                }
            }
        )'''
new = '''            onReset = {
                if (workingDesign != design) {
                    commitWorkingEdit(design.copy(stitches = design.stitches.toList()))
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                }
            },
            onSaveProject = { saveProjectRequest++ }
        )'''
if old not in text: raise SystemExit('SafeEditorPanel reset marker not found for save project')
text = text.replace(old, new, 1)

# Extend SafeEditorPanel to distinguish original/working/saved-project states.
old = '''private fun SafeEditorPanel(
    original: Design,
    working: Design,
    canUndo: Boolean,
    canRedo: Boolean,
    onUndo: () -> Unit,
    onRedo: () -> Unit,
    onReset: () -> Unit
) {
    val changed = working != original
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }
    val addedStitches = (working.stitchCount - original.stitchCount).coerceAtLeast(0)'''
new = '''private fun SafeEditorPanel(
    original: Design,
    working: Design,
    savedWorking: Design,
    projectName: String?,
    savingProject: Boolean,
    canUndo: Boolean,
    canRedo: Boolean,
    onUndo: () -> Unit,
    onRedo: () -> Unit,
    onReset: () -> Unit,
    onSaveProject: () -> Unit
) {
    val changed = working != original
    val unsaved = working != savedWorking
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }
    val addedStitches = (working.stitchCount - original.stitchCount).coerceAtLeast(0)'''
if old not in text: raise SystemExit('SafeEditorPanel signature marker not found for project persistence')
text = text.replace(old, new, 1)

old = '''                    Text(
                        if (changed) "Cópia de trabalho • alterações não salvas" else "Original preservado • nenhuma alteração aplicada",
                        color = if (changed) Gold else Muted,
                        fontSize = 8.sp
                    )'''
new = '''                    Text(
                        when {
                            projectName != null && unsaved -> "$projectName • alterações não salvas"
                            projectName != null -> "$projectName • projeto salvo"
                            changed -> "Cópia de trabalho • ainda não salva como projeto"
                            else -> "Original preservado • pronto para virar projeto"
                        },
                        color = if (unsaved || changed) Gold else Muted,
                        fontSize = 8.sp,
                        maxLines = 1
                    )'''
if old not in text: raise SystemExit('SafeEditorPanel subtitle marker not found')
text = text.replace(old, new, 1)

# Add an explicit project-save control above the intentionally locked embroidery writer.
old = '''            Surface(
                shape = RoundedCornerShape(14.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .32f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.SaveAs, null, tint = Muted, modifier = Modifier.size(17.dp))'''
new = '''            Button(
                onClick = onSaveProject,
                enabled = !savingProject,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
            ) {
                if (savingProject) {
                    CircularProgressIndicator(modifier = Modifier.size(17.dp), strokeWidth = 2.dp, color = Ink)
                } else {
                    Icon(if (projectName == null) Icons.Rounded.CreateNewFolder else Icons.Rounded.Save, null, modifier = Modifier.size(18.dp))
                }
                Spacer(Modifier.width(7.dp))
                Text(
                    when {
                        savingProject -> "Salvando projeto..."
                        projectName == null -> "Salvar como projeto editável"
                        unsaved -> "Atualizar projeto"
                        else -> "Projeto salvo"
                    },
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Surface(
                shape = RoundedCornerShape(14.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .32f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.SaveAs, null, tint = Muted, modifier = Modifier.size(17.dp))'''
if old not in text: raise SystemExit('SafeEditorPanel locked writer marker not found')
text = text.replace(old, new, 1)

# Refresh user-facing copy and version stamp.
text = text.replace('Organização local entra na próxima evolução', 'Projetos editáveis salvos no aparelho')
text = text.replace('0.2.16', '0.2.17')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.17 editable projects patch applied successfully')
