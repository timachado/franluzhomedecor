from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_046.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

insert_at = text.index('class MainActivity')
core = r'''private data class VerifiedExportHistoryItem(
    val createdAt: Long,
    val displayName: String,
    val format: String,
    val sha256: String,
    val machine: String,
    val hoops: String,
    val stitchCount: Int,
    val colors: Int,
    val widthMm: Float,
    val heightMm: Float,
    val preflightStatus: String
)

private const val EXPORT_HISTORY_PREF_KEY = "verified_export_history_v1"

private fun exportHoopSummary(config: MachineConfig): String {
    val standard = config.selectedHoopIds.sorted().joinToString(", ")
    val custom = if (config.customWidthMm != null && config.customHeightMm != null)
        "${config.customWidthMm}×${config.customHeightMm} mm" else ""
    return listOf(standard, custom).filter { it.isNotBlank() }.joinToString(" • ").ifBlank { "não configurado" }
}

private fun loadVerifiedExportHistory(context: android.content.Context): List<VerifiedExportHistoryItem> {
    val raw = appPrefs(context).getString(EXPORT_HISTORY_PREF_KEY, "[]") ?: "[]"
    return runCatching {
        val array = org.json.JSONArray(raw)
        buildList {
            for (i in 0 until array.length()) {
                val o = array.getJSONObject(i)
                add(VerifiedExportHistoryItem(
                    createdAt = o.optLong("createdAt", 0L),
                    displayName = o.optString("displayName", "Matriz BORDATTO"),
                    format = o.optString("format", "PES"),
                    sha256 = o.optString("sha256", ""),
                    machine = o.optString("machine", "Máquina não informada"),
                    hoops = o.optString("hoops", "não configurado"),
                    stitchCount = o.optInt("stitchCount", 0),
                    colors = o.optInt("colors", 0),
                    widthMm = o.optDouble("widthMm", 0.0).toFloat(),
                    heightMm = o.optDouble("heightMm", 0.0).toFloat(),
                    preflightStatus = o.optString("preflightStatus", "VERIFICADO")
                ))
            }
        }
    }.getOrElse { emptyList() }.sortedByDescending { it.createdAt }.take(50)
}

private fun persistVerifiedExportHistory(context: android.content.Context, items: List<VerifiedExportHistoryItem>) {
    val array = org.json.JSONArray()
    items.sortedByDescending { it.createdAt }.take(50).forEach { item ->
        array.put(org.json.JSONObject().apply {
            put("createdAt", item.createdAt); put("displayName", item.displayName); put("format", item.format)
            put("sha256", item.sha256); put("machine", item.machine); put("hoops", item.hoops)
            put("stitchCount", item.stitchCount); put("colors", item.colors)
            put("widthMm", item.widthMm.toDouble()); put("heightMm", item.heightMm.toDouble())
            put("preflightStatus", item.preflightStatus)
        })
    }
    appPrefs(context).edit().putString(EXPORT_HISTORY_PREF_KEY, array.toString()).apply()
}

private fun formatVerifiedExportDate(timestamp: Long): String = runCatching {
    java.text.SimpleDateFormat("dd/MM/yy • HH:mm", java.util.Locale.getDefault()).format(java.util.Date(timestamp))
}.getOrDefault("—")

'''
text = text[:insert_at] + core + text[insert_at:]

old = '''    var lastExportUri by remember { mutableStateOf<Uri?>(null) }
    var lastExportFormat by remember { mutableStateOf<String?>(null) }
    var lastExportSha by remember { mutableStateOf<String?>(null) }

    val exportLauncher = rememberLauncherForActivityResult('''
new = '''    var lastExportUri by remember { mutableStateOf<Uri?>(null) }
    var lastExportFormat by remember { mutableStateOf<String?>(null) }
    var lastExportSha by remember { mutableStateOf<String?>(null) }
    var verifiedExportHistory by remember(viewerContext) { mutableStateOf(loadVerifiedExportHistory(viewerContext)) }

    val exportLauncher = rememberLauncherForActivityResult('''
if old not in text: raise SystemExit('0.2.26 history state anchor not found')
text = text.replace(old, new, 1)

old = '''            lastExportUri = destination
            lastExportFormat = format
            lastExportSha = verified.sha256
            exportStatus = verified.report.compactStatus() +'''
new = '''            lastExportUri = destination
            lastExportFormat = format
            lastExportSha = verified.sha256
            val preflight = buildExportPreflight(snapshot, machineConfig, format)
            val historyItem = VerifiedExportHistoryItem(
                createdAt = System.currentTimeMillis(),
                displayName = "${safeExportBaseName(snapshot.name)}_BORDATTO.${format.lowercase()}",
                format = format,
                sha256 = verified.sha256,
                machine = "${machineConfig.brand} ${machineConfig.model}",
                hoops = exportHoopSummary(machineConfig),
                stitchCount = snapshot.stitchCount,
                colors = snapshot.colors,
                widthMm = snapshot.width,
                heightMm = snapshot.height,
                preflightStatus = preflight.status
            )
            verifiedExportHistory = (listOf(historyItem) + verifiedExportHistory).take(50)
            persistVerifiedExportHistory(viewerContext, verifiedExportHistory)
            exportStatus = verified.report.compactStatus() +'''
if old not in text: raise SystemExit('0.2.26 export success history anchor not found')
text = text.replace(old, new, 1)

old = '''            lastExportSha = lastExportSha,
            canShareLastExport = lastExportUri != null && exportOk == true,
            canUndo = undoStack.isNotEmpty(),'''
new = '''            lastExportSha = lastExportSha,
            canShareLastExport = lastExportUri != null && exportOk == true,
            verifiedExportHistory = verifiedExportHistory,
            canUndo = undoStack.isNotEmpty(),'''
if old not in text: raise SystemExit('0.2.26 SafeEditor history argument anchor not found')
text = text.replace(old, new, 1)

old = '''    canShareLastExport: Boolean,
    canUndo: Boolean,'''
new = '''    canShareLastExport: Boolean,
    verifiedExportHistory: List<VerifiedExportHistoryItem>,
    canUndo: Boolean,'''
if old not in text: raise SystemExit('0.2.26 SafeEditor history signature anchor not found')
text = text.replace(old, new, 1)

old = '''    val pesPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "PES") }
    val jefPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "JEF") }
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
new = '''    val pesPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "PES") }
    val jefPreflight = remember(working, machineConfig) { buildExportPreflight(working, machineConfig, "JEF") }
    var exportHistoryExpanded by remember { mutableStateOf(false) }
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }'''
if old not in text: raise SystemExit('0.2.26 history expanded anchor not found')
text = text.replace(old, new, 1)

old = '''                    Text("O arquivo original nunca é sobrescrito. Formato do perfil é uma preferência configurada, não uma certificação universal de máquina.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)'''
new = r'''                    Text("O arquivo original nunca é sobrescrito. Formato do perfil é uma preferência configurada, não uma certificação universal de máquina.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)
                    Surface(modifier=Modifier.fillMaxWidth().clickable{exportHistoryExpanded=!exportHistoryExpanded},shape=RoundedCornerShape(13.dp),color=SurfaceBrown,border=androidx.compose.foundation.BorderStroke(1.dp,LineGold.copy(alpha=.30f))){
                        Row(Modifier.fillMaxWidth().padding(horizontal=9.dp,vertical=8.dp),verticalAlignment=Alignment.CenterVertically){
                            Icon(Icons.Rounded.History,null,tint=Gold,modifier=Modifier.size(16.dp));Spacer(Modifier.width(7.dp))
                            Column(Modifier.weight(1f)){Text("Histórico verificado",color=Cream,fontSize=9.sp,fontWeight=FontWeight.SemiBold);Text("${verifiedExportHistory.size} registro(s)",color=Muted,fontSize=7.sp)}
                            Icon(if(exportHistoryExpanded)Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore,null,tint=Gold,modifier=Modifier.size(18.dp))
                        }
                    }
                    if(exportHistoryExpanded){
                        if(verifiedExportHistory.isEmpty()) Text("Nenhuma exportação totalmente verificada ainda.",color=Muted,fontSize=7.sp)
                        else verifiedExportHistory.take(5).forEach{item->
                            Surface(shape=RoundedCornerShape(12.dp),color=CardBrown){Column(Modifier.fillMaxWidth().padding(8.dp),verticalArrangement=Arrangement.spacedBy(2.dp)){
                                Row(verticalAlignment=Alignment.CenterVertically){Text(item.format,color=Gold,fontSize=7.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.width(6.dp));Text(item.displayName,color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold,maxLines=1)}
                                Text("${formatVerifiedExportDate(item.createdAt)} • ${item.stitchCount} pts • ${item.colors} cores",color=Muted,fontSize=6.sp)
                                Text("${"%.1f".format(item.widthMm)}×${"%.1f".format(item.heightMm)} mm • ${item.machine} • ${item.preflightStatus}",color=Muted,fontSize=6.sp,maxLines=1)
                                Text("Bastidor: ${item.hoops} • SHA-256 ${item.sha256.take(12)}…",color=Muted,fontSize=6.sp,maxLines=1)
                            }}
                        }
                        Text("Mostra até 5 recentes. O BORDATTO guarda só metadados de rastreabilidade; não duplica nem apaga o arquivo exportado.",color=Muted,fontSize=6.sp,lineHeight=9.sp)
                    }'''
if old not in text: raise SystemExit('0.2.26 history UI anchor not found')
text = text.replace(old, new, 1)

text = text.replace('0.2.25', '0.2.26')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.26 export traceability history applied successfully')
