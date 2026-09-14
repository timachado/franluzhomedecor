from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_038.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# BORDATTO 0.2.18 — Exportação Segura PES + JEF
# - Preserve native thread colors when readers expose them.
# - Keep BDP v1 projects readable while writing BDP v2 with thread colors.
# - Export only to a NEW SAF document (never overwrite the opened source URI).
# - Generate in memory, re-open with the reader and structurally validate before
#   any bytes are written to the user's selected destination.
# -----------------------------------------------------------------------------

# Common Design model now carries native RGB thread metadata when available.
old = '''    val colors: Int,
    val format: String = "DST"
) {'''
new = '''    val colors: Int,
    val format: String = "DST",
    val threadColors: List<Int> = emptyList()
) {'''
if old not in text:
    raise SystemExit('Design format marker not found for thread colors')
text = text.replace(old, new, 1)

# Readers backed by EmbroideryIO retain actual thread colors for PES/JEF and the
# other formats whenever the source contains thread metadata.
old = '''    val parsedName = pattern.getName()?.takeIf { it.isNotBlank() } ?: fileName.substringBeforeLast('.')
    val actualColors = maxOf(1, color + 1)
    return Design(parsedName, pts, minX, minY, maxX, maxY, actualColors, extension)
}'''
new = '''    val parsedName = pattern.getName()?.takeIf { it.isNotBlank() } ?: fileName.substringBeforeLast('.')
    val actualColors = maxOf(1, color + 1)
    val nativeThreadColors = pattern.getThreadlist()
        .map { it.getColor() }
        .take(actualColors)
    return Design(parsedName, pts, minX, minY, maxX, maxY, actualColors, extension, nativeThreadColors)
}'''
if old not in text:
    raise SystemExit('EmbroideryIO parser return marker not found')
text = text.replace(old, new, 1)

# Project snapshots v2 persist thread colors, but v1 snapshots from 0.2.17 remain readable.
old = 'private const val PROJECT_BINARY_VERSION = 1'
new = 'private const val PROJECT_BINARY_VERSION = 2'
if old not in text:
    raise SystemExit('project binary version marker not found')
text = text.replace(old, new, 1)

old = '''        out.writeUTF(design.format.take(32))
        out.writeInt(design.colors)
        out.writeFloat(design.minX)'''
new = '''        out.writeUTF(design.format.take(32))
        out.writeInt(design.colors)
        out.writeInt(design.threadColors.size.coerceAtMost(256))
        design.threadColors.take(256).forEach { out.writeInt(it) }
        out.writeFloat(design.minX)'''
if old not in text:
    raise SystemExit('project writer color metadata marker not found')
text = text.replace(old, new, 1)

old = '''        require(input.readInt() == PROJECT_MAGIC) { "Projeto BORDATTO inválido." }
        require(input.readInt() == PROJECT_BINARY_VERSION) { "Versão interna de projeto incompatível." }
        val name = input.readUTF()
        val format = input.readUTF()
        val colors = input.readInt().coerceAtLeast(1)
        val minX = input.readFloat()'''
new = '''        require(input.readInt() == PROJECT_MAGIC) { "Projeto BORDATTO inválido." }
        val projectVersion = input.readInt()
        require(projectVersion in 1..PROJECT_BINARY_VERSION) { "Versão interna de projeto incompatível." }
        val name = input.readUTF()
        val format = input.readUTF()
        val colors = input.readInt().coerceAtLeast(1)
        val threadColors = if (projectVersion >= 2) {
            val threadCount = input.readInt()
            require(threadCount in 0..256) { "Paleta interna do projeto inválida." }
            List(threadCount) { input.readInt() }
        } else emptyList()
        val minX = input.readFloat()'''
if old not in text:
    raise SystemExit('project reader header marker not found')
text = text.replace(old, new, 1)

old = '        Design(name, stitches, minX, minY, maxX, maxY, colors, format)'
new = '        Design(name, stitches, minX, minY, maxX, maxY, colors, format, threadColors)'
if old not in text:
    raise SystemExit('project reader Design constructor marker not found')
text = text.replace(old, new, 1)

# Writer + round-trip structural validator. Output is held in memory until validation passes.
insert_at = text.index('class MainActivity')
export_core = r'''private val ExportFallbackThreadColors = listOf(
    0xFF171717.toInt(), 0xFFC62828.toInt(), 0xFF1565C0.toInt(), 0xFF2E7D32.toInt(),
    0xFFF9A825.toInt(), 0xFFEF6C00.toInt(), 0xFF6A1B9A.toInt(), 0xFFD81B60.toInt(),
    0xFF6D4C41.toInt(), 0xFF757575.toInt(), 0xFF00838F.toInt(), 0xFFF5F5F5.toInt()
)

private data class ExportValidationReport(
    val valid: Boolean,
    val format: String,
    val byteCount: Int,
    val sourceStitches: Int,
    val roundTripStitches: Int,
    val sourceColors: Int,
    val roundTripColors: Int,
    val widthDeltaMm: Float,
    val heightDeltaMm: Float,
    val nativePalettePreserved: Boolean,
    val notes: List<String>
) {
    fun compactStatus(): String {
        val kb = byteCount / 1024.0
        val delta = maxOf(widthDeltaMm, heightDeltaMm)
        return if (valid) {
            "$format • ROUND-TRIP OK • $roundTripStitches pts • Δ ${"%.2f".format(delta)} mm • ${"%.1f".format(kb)} KB"
        } else {
            "$format • validação estrutural falhou"
        }
    }
}

private data class ExportPayload(
    val bytes: ByteArray,
    val report: ExportValidationReport
)

private fun designToEmbroideryIoPattern(design: Design): org.embroideryio.embroideryio.EmbPattern {
    require(design.stitchCount > 0) { "A cópia de trabalho não possui pontadas para exportar." }
    val pattern = org.embroideryio.embroideryio.EmbPattern()
    pattern.setName(design.name.substringBeforeLast('.').take(255))

    val threadCount = maxOf(1, design.colors)
    val palette = design.threadColors.takeIf { it.isNotEmpty() } ?: ExportFallbackThreadColors
    repeat(threadCount) { index ->
        val color = palette[index % palette.size]
        pattern.addThread(
            org.embroideryio.embroideryio.EmbThread(
                color,
                "BORDATTO ${index + 1}",
                "${index + 1}"
            )
        )
    }

    design.stitches.forEach { stitch ->
        val command = when (stitch.command) {
            StitchCommand.STITCH -> org.embroideryio.embroideryio.EmbConstant.STITCH
            StitchCommand.JUMP -> org.embroideryio.embroideryio.EmbConstant.JUMP
            StitchCommand.TRIM -> org.embroideryio.embroideryio.EmbConstant.TRIM
            StitchCommand.COLOR_CHANGE -> org.embroideryio.embroideryio.EmbConstant.COLOR_CHANGE
            StitchCommand.END -> org.embroideryio.embroideryio.EmbConstant.END
        }
        // BORDATTO internal geometry is mm; EmbroideryIO uses tenths of a millimeter.
        pattern.addStitchAbs(stitch.x * 10f, stitch.y * 10f, command)
    }

    if (design.stitches.lastOrNull()?.command != StitchCommand.END) {
        val last = design.stitches.lastOrNull()
        pattern.addStitchAbs((last?.x ?: 0f) * 10f, (last?.y ?: 0f) * 10f, org.embroideryio.embroideryio.EmbConstant.END)
    }
    return pattern
}

private fun validateEncodedEmbroidery(design: Design, format: String, bytes: ByteArray): ExportValidationReport {
    require(bytes.size > 128) { "O writer retornou um arquivo muito pequeno para ser uma matriz válida." }
    val roundTrip = parseWithEmbroideryIo("bordatto_roundtrip.${format.lowercase()}", bytes)
    val widthDelta = kotlin.math.abs(roundTrip.width - design.width)
    val heightDelta = kotlin.math.abs(roundTrip.height - design.height)
    val geometryOk = widthDelta <= 1.5f && heightDelta <= 1.5f

    val stitchRatio = if (design.stitchCount <= 0) 0.0 else roundTrip.stitchCount.toDouble() / design.stitchCount.toDouble()
    // Writers may legitimately interpolate machine-limited movements. Reject major loss/corruption,
    // but allow extra machine-safe points inserted by the format encoder.
    val stitchesOk = roundTrip.stitchCount > 0 && stitchRatio in 0.80..2.50
    val colorsOk = kotlin.math.abs(roundTrip.colors - design.colors) <= 1
    val valid = geometryOk && stitchesOk && colorsOk

    val notes = buildList {
        if (design.threadColors.isEmpty()) {
            add("A matriz de origem não trouxe paleta RGB utilizável; o BORDATTO aplicou uma paleta determinística de fallback.")
        } else {
            add("Metadados RGB disponíveis no modelo interno foram enviados ao writer.")
        }
        if (format == "JEF") {
            add("JEF trabalha com a paleta Janome e pode aproximar o RGB para a cor compatível mais próxima.")
        }
        if (format == "PES") {
            add("PES é gerado como PES v6 nesta fase de validação.")
        }
        add("Validação BORDATTO = round-trip estrutural; ainda não equivale a certificação em todos os modelos de máquina.")
    }

    return ExportValidationReport(
        valid = valid,
        format = format,
        byteCount = bytes.size,
        sourceStitches = design.stitchCount,
        roundTripStitches = roundTrip.stitchCount,
        sourceColors = design.colors,
        roundTripColors = roundTrip.colors,
        widthDeltaMm = widthDelta,
        heightDeltaMm = heightDelta,
        nativePalettePreserved = design.threadColors.isNotEmpty(),
        notes = notes
    )
}

private fun encodeAndValidateEmbroidery(design: Design, format: String): ExportPayload {
    val normalized = format.uppercase()
    require(normalized == "PES" || normalized == "JEF") { "Exportação liberada nesta versão apenas para PES e JEF." }
    val pattern = designToEmbroideryIoPattern(design)
    val output = java.io.ByteArrayOutputStream()
    if (normalized == "PES") {
        org.embroideryio.embroideryio.EmbroideryIO.writeStream(
            pattern,
            "bordatto.pes",
            output,
            "pes version",
            6
        )
    } else {
        org.embroideryio.embroideryio.EmbroideryIO.writeStream(pattern, "bordatto.jef", output)
    }
    val bytes = output.toByteArray()
    val report = validateEncodedEmbroidery(design, normalized, bytes)
    require(report.valid) {
        "O arquivo foi gerado em memória, mas falhou no round-trip. Nenhum arquivo foi liberado."
    }
    return ExportPayload(bytes, report)
}

private fun safeExportBaseName(name: String): String {
    val base = name.substringBeforeLast('.').trim().ifBlank { "bordatto" }
    return base.replace(Regex("[^A-Za-z0-9._ -]"), "_").take(80).ifBlank { "bordatto" }
}

'''
text = text[:insert_at] + export_core + text[insert_at:]

# Root passes the original source URI so Viewer can hard-block accidental overwrite.
old = '''                    activeProject = activeProject,
                    onWorkingChanged = { current -> workingSeed = current },'''
new = '''                    activeProject = activeProject,
                    sourceUri = currentSourceUri,
                    onWorkingChanged = { current -> workingSeed = current },'''
if old not in text:
    raise SystemExit('Viewer root source URI marker not found')
text = text.replace(old, new, 1)

old = '''    initialWorkingDesign: Design? = null,
    activeProject: ProjectItem? = null,
    onWorkingChanged: (Design) -> Unit = {},'''
new = '''    initialWorkingDesign: Design? = null,
    activeProject: ProjectItem? = null,
    sourceUri: String? = null,
    onWorkingChanged: (Design) -> Unit = {},'''
if old not in text:
    raise SystemExit('Viewer signature source URI marker not found')
text = text.replace(old, new, 1)

# Export state and SAF CreateDocument launcher. The encoded bytes are validated before
# openOutputStream is called; choosing the source URI itself is rejected.
marker = '''    fun commitWorkingEdit(next: Design) {
'''
export_state = r'''    val viewerContext = androidx.compose.ui.platform.LocalContext.current
    var pendingExportUri by remember { mutableStateOf<Uri?>(null) }
    var pendingExportFormat by remember { mutableStateOf<String?>(null) }
    var exporting by remember { mutableStateOf(false) }
    var exportStatus by remember { mutableStateOf<String?>(null) }
    var exportOk by remember { mutableStateOf<Boolean?>(null) }

    val exportLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/octet-stream")
    ) { uri ->
        if (uri == null) {
            pendingExportFormat = null
        } else {
            pendingExportUri = uri
        }
    }

    fun requestSafeExport(format: String) {
        if (exporting) return
        exportStatus = null
        exportOk = null
        pendingExportFormat = format.uppercase()
        val extension = format.lowercase()
        exportLauncher.launch("${safeExportBaseName(workingDesign.name)}_BORDATTO.$extension")
    }

    LaunchedEffect(pendingExportUri) {
        val destination = pendingExportUri ?: return@LaunchedEffect
        val format = pendingExportFormat ?: return@LaunchedEffect
        exporting = true
        exportStatus = "Gerando $format em memória e executando round-trip..."
        exportOk = null
        val snapshot = workingDesign.copy(stitches = workingDesign.stitches.toList(), threadColors = workingDesign.threadColors.toList())
        val result = runCatching {
            require(destination.toString() != sourceUri) {
                "O BORDATTO bloqueou a sobrescrita do arquivo original. Escolha outro nome ou pasta."
            }
            val payload = withContext(Dispatchers.IO) { encodeAndValidateEmbroidery(snapshot, format) }
            withContext(Dispatchers.IO) {
                val stream = viewerContext.contentResolver.openOutputStream(destination, "wt")
                    ?: error("Não foi possível abrir o destino escolhido para gravação.")
                stream.use {
                    it.write(payload.bytes)
                    it.flush()
                }
            }
            payload.report
        }
        result.onSuccess { report ->
            exportOk = true
            exportStatus = report.compactStatus() + "\n" + report.notes.take(2).joinToString(" ")
        }.onFailure { failure ->
            exportOk = false
            exportStatus = "Exportação não liberada: ${failure.message ?: "falha desconhecida"}"
            // Delete only the new destination document. Never delete if it is the opened source URI.
            if (destination.toString() != sourceUri) {
                runCatching { withContext(Dispatchers.IO) { viewerContext.contentResolver.delete(destination, null, null) } }
            }
        }
        exporting = false
        pendingExportUri = null
        pendingExportFormat = null
    }

    fun commitWorkingEdit(next: Design) {
'''
if marker not in text:
    raise SystemExit('Viewer commit marker not found for export state')
text = text.replace(marker, export_state, 1)

# Safe Editor receives export controls and validation status.
old = '''            projectName = localProject?.name,
            savingProject = projectSaving,
            canUndo = undoStack.isNotEmpty(),'''
new = '''            projectName = localProject?.name,
            savingProject = projectSaving,
            exporting = exporting,
            exportStatus = exportStatus,
            exportOk = exportOk,
            canUndo = undoStack.isNotEmpty(),'''
if old not in text:
    raise SystemExit('SafeEditorPanel call export state marker not found')
text = text.replace(old, new, 1)

old = '''            },
            onSaveProject = { saveProjectRequest++ }
        )'''
new = '''            },
            onSaveProject = { saveProjectRequest++ },
            onExport = { format -> requestSafeExport(format) }
        )'''
if old not in text:
    raise SystemExit('SafeEditorPanel call export callback marker not found')
text = text.replace(old, new, 1)

old = '''    projectName: String?,
    savingProject: Boolean,
    canUndo: Boolean,'''
new = '''    projectName: String?,
    savingProject: Boolean,
    exporting: Boolean,
    exportStatus: String?,
    exportOk: Boolean?,
    canUndo: Boolean,'''
if old not in text:
    raise SystemExit('SafeEditorPanel signature export state marker not found')
text = text.replace(old, new, 1)

old = '''    onRedo: () -> Unit,
    onReset: () -> Unit,
    onSaveProject: () -> Unit
) {'''
new = '''    onRedo: () -> Unit,
    onReset: () -> Unit,
    onSaveProject: () -> Unit,
    onExport: (String) -> Unit
) {'''
if old not in text:
    raise SystemExit('SafeEditorPanel signature export callback marker not found')
text = text.replace(old, new, 1)

# Replace the intentionally locked writer card with real PES/JEF safe-export controls.
old = '''            Surface(
                shape = RoundedCornerShape(14.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .32f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.SaveAs, null, tint = Muted, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(7.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Salvar como", color = Muted, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                        Text("Bloqueado até o writer de matriz ser validado — não vamos gerar arquivo falso.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)
                    }
                    Icon(Icons.Rounded.Lock, null, tint = Muted, modifier = Modifier.size(16.dp))
                }
            }'''
new = '''            Surface(
                shape = RoundedCornerShape(16.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, Gold.copy(alpha = .40f))
            ) {
                Column(Modifier.fillMaxWidth().padding(11.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.SaveAs, null, tint = Gold, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(7.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Exportação Segura", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                            Text("Gera em memória → reabre → valida → só então grava o novo arquivo.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)
                        }
                        if (exporting) CircularProgressIndicator(modifier = Modifier.size(17.dp), strokeWidth = 2.dp, color = Gold)
                    }
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                        FilledTonalButton(
                            onClick = { onExport("PES") },
                            enabled = !exporting && working.stitchCount > 0,
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(15.dp),
                            colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha = .16f), contentColor = Gold)
                        ) {
                            Icon(Icons.Rounded.Description, null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(5.dp))
                            Text("PES v6", fontSize = 8.sp, fontWeight = FontWeight.Bold)
                        }
                        FilledTonalButton(
                            onClick = { onExport("JEF") },
                            enabled = !exporting && working.stitchCount > 0,
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(15.dp),
                            colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha = .16f), contentColor = Gold)
                        ) {
                            Icon(Icons.Rounded.Description, null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(5.dp))
                            Text("JEF", fontSize = 8.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                    exportStatus?.let { status ->
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = if (exportOk == true) Gold.copy(alpha = .10f) else SurfaceBrown,
                            border = androidx.compose.foundation.BorderStroke(1.dp, if (exportOk == true) Gold.copy(alpha = .38f) else LineGold.copy(alpha = .30f))
                        ) {
                            Row(Modifier.fillMaxWidth().padding(8.dp), verticalAlignment = Alignment.Top) {
                                Icon(
                                    if (exportOk == true) Icons.Rounded.Verified else if (exportOk == false) Icons.Rounded.WarningAmber else Icons.Rounded.HourglassTop,
                                    null,
                                    tint = if (exportOk == true) Gold else Muted,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(Modifier.width(6.dp))
                                Text(status, color = if (exportOk == true) Cream else Muted, fontSize = 7.sp, lineHeight = 10.sp)
                            }
                        }
                    }
                    Text("O arquivo original nunca é sobrescrito. A validação atual é estrutural por round-trip no próprio BORDATTO.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)
                }
            }'''
if old not in text:
    raise SystemExit('locked writer card not found for safe PES/JEF export')
text = text.replace(old, new, 1)

text = text.replace('0.2.17', '0.2.18')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.18 safe PES/JEF export patch applied successfully')
