from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_039.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# BORDATTO 0.2.19 — Central de Exportação + Validação de Máquina
# - Keep 0.2.18 PES/JEF in-memory round-trip validation.
# - After writing, read the destination document back and validate it again.
# - Verify byte-for-byte persistence with SHA-256 before calling export successful.
# - Surface the preferred format from Minha Máquina without claiming universal
#   machine compatibility.
# - Allow sharing the last fully verified SAF export through Android Sharesheet.
# -----------------------------------------------------------------------------

# Stored-file verification helpers. A successful 0.2.19 export has therefore passed
# two stages: generated-byte round trip and actual destination-document read-back.
marker = '''private fun safeExportBaseName(name: String): String {
'''
helpers = r'''private data class StoredExportVerification(
    val report: ExportValidationReport,
    val sha256: String
)

private fun sha256Hex(bytes: ByteArray): String {
    val digest = java.security.MessageDigest.getInstance("SHA-256").digest(bytes)
    return digest.joinToString("") { "%02x".format(it) }
}

private fun verifyStoredExport(
    context: android.content.Context,
    destination: Uri,
    expectedBytes: ByteArray,
    design: Design,
    format: String
): StoredExportVerification {
    val storedBytes = context.contentResolver.openInputStream(destination)?.use { it.readBytes() }
        ?: error("O arquivo foi gravado, mas não pôde ser relido para a verificação final.")
    require(storedBytes.contentEquals(expectedBytes)) {
        "Os bytes relidos do armazenamento diferem do arquivo validado em memória. A exportação foi bloqueada."
    }
    val report = validateEncodedEmbroidery(design, format, storedBytes)
    require(report.valid) { "O arquivo salvo falhou na segunda validação estrutural." }
    return StoredExportVerification(report, sha256Hex(storedBytes))
}

private fun safeExportBaseName(name: String): String {
'''
if marker not in text:
    raise SystemExit('safeExportBaseName marker not found for stored verification helpers')
text = text.replace(marker, helpers, 1)

# Keep the last successfully verified destination so it can be shared immediately.
old = '''    var exportStatus by remember { mutableStateOf<String?>(null) }
    var exportOk by remember { mutableStateOf<Boolean?>(null) }

    val exportLauncher = rememberLauncherForActivityResult('''
new = '''    var exportStatus by remember { mutableStateOf<String?>(null) }
    var exportOk by remember { mutableStateOf<Boolean?>(null) }
    var lastExportUri by remember { mutableStateOf<Uri?>(null) }
    var lastExportFormat by remember { mutableStateOf<String?>(null) }
    var lastExportSha by remember { mutableStateOf<String?>(null) }

    val exportLauncher = rememberLauncherForActivityResult('''
if old not in text:
    raise SystemExit('export viewer state marker not found')
text = text.replace(old, new, 1)

old = '''        exportStatus = null
        exportOk = null
        pendingExportFormat = format.uppercase()'''
new = '''        exportStatus = null
        exportOk = null
        lastExportUri = null
        lastExportFormat = null
        lastExportSha = null
        pendingExportFormat = format.uppercase()'''
if old not in text:
    raise SystemExit('requestSafeExport reset marker not found')
text = text.replace(old, new, 1)

# Strengthen the transaction: validate bytes, write, read the actual destination back,
# require identical bytes, parse it again, then retain the URI for sharing.
old = '''            val payload = withContext(Dispatchers.IO) { encodeAndValidateEmbroidery(snapshot, format) }
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
            exportStatus = report.compactStatus() + "\\n" + report.notes.take(2).joinToString(" ")
        }.onFailure { failure ->
            exportOk = false
            exportStatus = "Exportação não liberada: ${failure.message ?: "falha desconhecida"}"
            // Delete only the new destination document. Never delete if it is the opened source URI.
            if (destination.toString() != sourceUri) {
                runCatching { withContext(Dispatchers.IO) { viewerContext.contentResolver.delete(destination, null, null) } }
            }
        }'''
new = '''            val payload = withContext(Dispatchers.IO) { encodeAndValidateEmbroidery(snapshot, format) }
            withContext(Dispatchers.IO) {
                val stream = viewerContext.contentResolver.openOutputStream(destination, "wt")
                    ?: error("Não foi possível abrir o destino escolhido para gravação.")
                stream.use {
                    it.write(payload.bytes)
                    it.flush()
                }
            }
            val verified = withContext(Dispatchers.IO) {
                verifyStoredExport(viewerContext, destination, payload.bytes, snapshot, format)
            }
            runCatching {
                viewerContext.contentResolver.takePersistableUriPermission(
                    destination,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
                )
            }
            verified
        }
        result.onSuccess { verified ->
            exportOk = true
            lastExportUri = destination
            lastExportFormat = format
            lastExportSha = verified.sha256
            exportStatus = verified.report.compactStatus() +
                "\\nARQUIVO GRAVADO E RELIDO • SHA-256 ${verified.sha256.take(12)}…" +
                "\\n" + verified.report.notes.take(1).joinToString(" ")
        }.onFailure { failure ->
            exportOk = false
            lastExportUri = null
            lastExportFormat = null
            lastExportSha = null
            exportStatus = "Exportação não liberada: ${failure.message ?: "falha desconhecida"}"
            // Delete only the new destination document. Never delete if it is the opened source URI.
            if (destination.toString() != sourceUri) {
                runCatching { withContext(Dispatchers.IO) { viewerContext.contentResolver.delete(destination, null, null) } }
            }
        }'''
if old not in text:
    raise SystemExit('export transaction marker not found for double validation')
text = text.replace(old, new, 1)

# Android Sharesheet for the last destination that passed both validations.
marker = '''    fun commitWorkingEdit(next: Design) {
'''
share_fn = r'''    fun shareLastVerifiedExport() {
        val uri = lastExportUri ?: return
        val format = lastExportFormat ?: "Matriz"
        val share = Intent(Intent.ACTION_SEND).apply {
            type = "application/octet-stream"
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        runCatching {
            viewerContext.startActivity(Intent.createChooser(share, "Compartilhar $format validado"))
        }.onFailure {
            exportStatus = "O arquivo está validado, mas não foi possível abrir o compartilhamento neste dispositivo."
        }
    }

    fun commitWorkingEdit(next: Design) {
'''
if marker not in text:
    raise SystemExit('commitWorkingEdit marker not found for sharing function')
text = text.replace(marker, share_fn, 1)

# Feed the machine profile and verified-export state into the central export panel.
old = '''            exporting = exporting,
            exportStatus = exportStatus,
            exportOk = exportOk,
            canUndo = undoStack.isNotEmpty(),'''
new = '''            exporting = exporting,
            exportStatus = exportStatus,
            exportOk = exportOk,
            machineFormat = machineConfig.format,
            lastExportFormat = lastExportFormat,
            lastExportSha = lastExportSha,
            canShareLastExport = lastExportUri != null && exportOk == true,
            canUndo = undoStack.isNotEmpty(),'''
if old not in text:
    raise SystemExit('SafeEditorPanel call export state marker not found for machine profile')
text = text.replace(old, new, 1)

old = '''            onSaveProject = { saveProjectRequest++ },
            onExport = { format -> requestSafeExport(format) }
        )'''
new = '''            onSaveProject = { saveProjectRequest++ },
            onExport = { format -> requestSafeExport(format) },
            onShareLastExport = { shareLastVerifiedExport() }
        )'''
if old not in text:
    raise SystemExit('SafeEditorPanel callback marker not found for share')
text = text.replace(old, new, 1)

old = '''    exporting: Boolean,
    exportStatus: String?,
    exportOk: Boolean?,
    canUndo: Boolean,'''
new = '''    exporting: Boolean,
    exportStatus: String?,
    exportOk: Boolean?,
    machineFormat: String,
    lastExportFormat: String?,
    lastExportSha: String?,
    canShareLastExport: Boolean,
    canUndo: Boolean,'''
if old not in text:
    raise SystemExit('SafeEditorPanel signature state marker not found for export center')
text = text.replace(old, new, 1)

old = '''    onReset: () -> Unit,
    onSaveProject: () -> Unit,
    onExport: (String) -> Unit
) {'''
new = '''    onReset: () -> Unit,
    onSaveProject: () -> Unit,
    onExport: (String) -> Unit,
    onShareLastExport: () -> Unit
) {'''
if old not in text:
    raise SystemExit('SafeEditorPanel signature callback marker not found for share')
text = text.replace(old, new, 1)

old = '''    val changed = working != original
    val unsaved = working != savedWorking
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
new = '''    val changed = working != original
    val unsaved = working != savedWorking
    val preferredFormat = machineFormat.uppercase()
    val preferredExportAvailable = preferredFormat == "PES" || preferredFormat == "JEF"
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
if old not in text:
    raise SystemExit('SafeEditorPanel local state marker not found for preferred format')
text = text.replace(old, new, 1)

text = text.replace('Text("Exportação Segura", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)',
                    'Text("Central de Exportação", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)', 1)
text = text.replace('Text("Gera em memória → reabre → valida → só então grava o novo arquivo.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)',
                    'Text("Valida em memória → grava → relê do armazenamento → valida de novo.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)', 1)

# Insert a profile-aware recommendation without claiming the configured machine is
# universally compatible with that format.
marker = '''                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                        FilledTonalButton(
                            onClick = { onExport("PES") },'''
profile_ui = r'''                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = if (preferredExportAvailable) Gold.copy(alpha = .08f) else SurfaceBrown,
                        border = androidx.compose.foundation.BorderStroke(1.dp, if (preferredExportAvailable) Gold.copy(alpha = .28f) else LineGold.copy(alpha = .28f))
                    ) {
                        Row(Modifier.fillMaxWidth().padding(horizontal = 9.dp, vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.PrecisionManufacturing, null, tint = if (preferredExportAvailable) Gold else Muted, modifier = Modifier.size(15.dp))
                            Spacer(Modifier.width(6.dp))
                            Text(
                                if (preferredExportAvailable)
                                    "Formato preferencial configurado em Minha Máquina: $preferredFormat. O BORDATTO vai destacá-lo abaixo."
                                else
                                    "Minha Máquina está configurada para $preferredFormat. A exportação validada desta fase ainda está limitada a PES/JEF.",
                                color = Muted,
                                fontSize = 7.sp,
                                lineHeight = 10.sp
                            )
                        }
                    }
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                        FilledTonalButton(
                            onClick = { onExport("PES") },'''
if marker not in text:
    raise SystemExit('export button row marker not found for profile recommendation')
text = text.replace(marker, profile_ui, 1)

text = text.replace('Text("PES v6", fontSize = 8.sp, fontWeight = FontWeight.Bold)',
                    'Text(if (preferredFormat == "PES") "PES v6 • PERFIL" else "PES v6", fontSize = 8.sp, fontWeight = FontWeight.Bold)', 1)
text = text.replace('Text("JEF", fontSize = 8.sp, fontWeight = FontWeight.Bold)',
                    'Text(if (preferredFormat == "JEF") "JEF • PERFIL" else "JEF", fontSize = 8.sp, fontWeight = FontWeight.Bold)', 1)

# After a full stored-file verification, make the exported matrix shareable from the same panel.
old = '''                    Text("O arquivo original nunca é sobrescrito. A validação atual é estrutural por round-trip no próprio BORDATTO.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)'''
new = '''                    if (canShareLastExport) {
                        FilledTonalButton(
                            onClick = onShareLastExport,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(14.dp),
                            colors = ButtonDefaults.filledTonalButtonColors(containerColor = Gold.copy(alpha = .14f), contentColor = Gold)
                        ) {
                            Icon(Icons.Rounded.Share, null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Compartilhar ${lastExportFormat ?: "matriz"} verificado", fontSize = 8.sp, fontWeight = FontWeight.Bold)
                        }
                        lastExportSha?.let { sha ->
                            Text("Integridade SHA-256: ${sha.take(16)}…", color = Muted, fontSize = 7.sp)
                        }
                    }
                    Text("O arquivo original nunca é sobrescrito. Formato do perfil é uma preferência configurada, não uma certificação universal de máquina.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)'''
if old not in text:
    raise SystemExit('export disclaimer marker not found for share action')
text = text.replace(old, new, 1)

text = text.replace('0.2.18', '0.2.19')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.19 export center + stored-file verification patch applied successfully')
