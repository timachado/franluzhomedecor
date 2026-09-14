from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_045.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

insert_at = text.index('class MainActivity')
core = r'''private data class ExportPreflightReport(
    val format: String,
    val status: String,
    val blocked: List<String>,
    val review: List<String>,
    val okCount: Int
) {
    val canExport: Boolean get() = blocked.isEmpty()
}

private fun buildExportPreflight(design: Design, config: MachineConfig, format: String): ExportPreflightReport {
    val f = format.uppercase()
    val analysis = analyzeDesign(design, config)
    val blocked = mutableListOf<String>()
    val review = mutableListOf<String>()
    var ok = 0

    if (design.stitchCount <= 0) blocked += "Sem pontadas válidas" else ok++
    when (analysis.fitsConfiguredHoop) {
        false -> blocked += "Matriz fora dos bastidores configurados"
        null -> review += "Bastidor não configurado"
        true -> ok++
    }
    if (analysis.longStitchCount > 0) review += "${analysis.longStitchCount} ponto(s) acima de 8 mm" else ok++
    if (analysis.longJumpCount > 0) review += "${analysis.longJumpCount} salto(s) acima de 12 mm" else ok++
    if (analysis.peakCellStitches >= 100) review += "Concentração local: ${analysis.peakCellStitches} pts / 5×5 mm" else ok++
    if (design.colors <= 0) blocked += "Sequência de cores inválida" else ok++
    if (design.threadInfos.isEmpty() && design.threadColors.isEmpty()) review += "Sem metadados RGB nativos completos" else ok++
    if (f != "PES" && f != "JEF") blocked += "Writer $f não validado" else ok++
    if (config.format.uppercase() != f) review += "Perfil da máquina prefere ${config.format.uppercase()}" else ok++

    val status = when {
        blocked.isNotEmpty() -> "BLOQUEADO"
        review.isNotEmpty() -> "REVISAR"
        else -> "PRONTO PARA EXPORTAR"
    }
    return ExportPreflightReport(f, status, blocked, review, ok)
}

'''
text = text[:insert_at] + core + text[insert_at:]

old = '''    fun requestSafeExport(format: String) {
        if (exporting) return
        exportStatus = null
        exportOk = null
        lastExportUri = null
        lastExportFormat = null
        lastExportSha = null
        pendingExportFormat = format.uppercase()
        val extension = format.lowercase()
        exportLauncher.launch("${safeExportBaseName(workingDesign.name)}_BORDATTO.$extension")
    }'''
new = '''    fun requestSafeExport(format: String) {
        if (exporting) return
        val preflight = buildExportPreflight(workingDesign, machineConfig, format)
        exportStatus = null
        exportOk = null
        lastExportUri = null
        lastExportFormat = null
        lastExportSha = null
        if (!preflight.canExport) {
            exportOk = false
            exportStatus = "PREFLIGHT BLOQUEADO • ${preflight.blocked.joinToString(" • ")}"
            return
        }
        if (preflight.review.isNotEmpty()) {
            exportStatus = "PREFLIGHT: REVISAR • ${preflight.review.joinToString(" • ")}"
        }
        pendingExportFormat = format.uppercase()
        val extension = format.lowercase()
        exportLauncher.launch("${safeExportBaseName(workingDesign.name)}_BORDATTO.$extension")
    }'''
if old not in text: raise SystemExit('0.2.25 requestSafeExport anchor not found')
text = text.replace(old, new, 1)

insert_at = text.index('@Composable\nprivate fun SafeEditorPanel')
ui = r'''@Composable
private fun ExportPreflightCard(report: ExportPreflightReport) {
    val alert = report.status != "PRONTO PARA EXPORTAR"
    Surface(
        shape = RoundedCornerShape(13.dp),
        color = if (alert) Gold.copy(alpha = .07f) else SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, if (alert) Gold.copy(alpha = .55f) else LineGold.copy(alpha = .34f))
    ) {
        Column(Modifier.fillMaxWidth().padding(9.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(if (report.blocked.isNotEmpty()) Icons.Rounded.ErrorOutline else if (report.review.isNotEmpty()) Icons.Rounded.WarningAmber else Icons.Rounded.Verified, null, tint = Gold, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(6.dp))
                Text("Preflight ${report.format}", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                Text(report.status, color = Gold, fontSize = 7.sp, fontWeight = FontWeight.Bold)
            }
            Text("${report.okCount} verificações ok • ${report.review.size} revisar • ${report.blocked.size} bloqueio(s)", color = Muted, fontSize = 7.sp)
            (report.blocked + report.review).take(3).forEach { Text("• $it", color = Muted, fontSize = 7.sp, lineHeight = 10.sp) }
        }
    }
}

'''
text = text[:insert_at] + ui + text[insert_at:]

old = '''    val preferredFormat = machineFormat.uppercase()
    val preferredExportAvailable = preferredFormat == "PES" || preferredFormat == "JEF"
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
new = '''    val preferredFormat = machineFormat.uppercase()
    val preferredExportAvailable = preferredFormat == "PES" || preferredFormat == "JEF"
    val pesPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "PES") }
    val jefPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "JEF") }
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
if old not in text: raise SystemExit('0.2.25 preflight state anchor not found')
text = text.replace(old, new, 1)

text = text.replace(
    'Text("Valida em memória → grava → relê do armazenamento → valida de novo.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)',
    'Text("Preflight → round-trip → grava → relê → compara bytes → SHA-256.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)',
    1
)

marker = '''                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = if (preferredExportAvailable) Gold.copy(alpha = .08f) else SurfaceBrown,'''
new_marker = '''                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        ExportPreflightCard(pesPreflight)
                        ExportPreflightCard(jefPreflight)
                    }
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = if (preferredExportAvailable) Gold.copy(alpha = .08f) else SurfaceBrown,'''
if marker not in text: raise SystemExit('0.2.25 export card anchor not found')
text = text.replace(marker, new_marker, 1)

old_enabled = 'enabled = !exporting && working.stitchCount > 0,'
if text.count(old_enabled) < 2: raise SystemExit('0.2.25 export buttons anchor not found')
text = text.replace(old_enabled, 'enabled = !exporting && pesPreflight.canExport,', 1)
text = text.replace(old_enabled, 'enabled = !exporting && jefPreflight.canExport,', 1)

text = text.replace('0.2.24', '0.2.25')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.25 professional export preflight applied successfully')
