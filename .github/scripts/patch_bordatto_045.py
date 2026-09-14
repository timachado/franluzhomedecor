from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_044.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# BORDATTO 0.2.24 — Comparador Antes/Depois + Safety Check de Sequência
# - Visual toggle ORIGINAL / PROPOSTA on the real embroidery canvas.
# - Geometric overlap-order safety check before applying optimization.
# - Compares thread changes, connector travel and machine-aware estimated time.
# - Still never applies a proposal without explicit user confirmation.
# -----------------------------------------------------------------------------

insert_at = text.index('class MainActivity')
core = r'''private data class SequenceBlockBounds(
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float
) {
    val width: Float get() = (maxX - minX).coerceAtLeast(0f)
    val height: Float get() = (maxY - minY).coerceAtLeast(0f)
    val area: Double get() = width.toDouble() * height.toDouble()
}

private data class SequenceSafetyReport(
    val overlappingPairs: Int,
    val reversedOverlapPairs: Int,
    val significantReversedPairs: Int,
    val severity: Int,
    val label: String,
    val detail: String
)

private fun sequenceBlockBounds(design: Design, block: ThreadSequenceBlock): SequenceBlockBounds? {
    val start = block.startRaw.coerceIn(0, design.stitches.size)
    val end = block.endRawExclusive.coerceIn(start, design.stitches.size)
    val stitches = design.stitches.subList(start, end).filter { it.command == StitchCommand.STITCH }
    if (stitches.isEmpty()) return null
    return SequenceBlockBounds(
        minX = stitches.minOf { it.x },
        minY = stitches.minOf { it.y },
        maxX = stitches.maxOf { it.x },
        maxY = stitches.maxOf { it.y }
    )
}

private fun expandedSequenceBounds(bounds: SequenceBlockBounds, marginMm: Float = 0.6f): SequenceBlockBounds =
    SequenceBlockBounds(bounds.minX - marginMm, bounds.minY - marginMm, bounds.maxX + marginMm, bounds.maxY + marginMm)

private fun sequenceBoundsOverlapRatio(a: SequenceBlockBounds, b: SequenceBlockBounds): Double {
    val aa = expandedSequenceBounds(a)
    val bb = expandedSequenceBounds(b)
    val ix = (minOf(aa.maxX, bb.maxX) - maxOf(aa.minX, bb.minX)).coerceAtLeast(0f)
    val iy = (minOf(aa.maxY, bb.maxY) - maxOf(aa.minY, bb.minY)).coerceAtLeast(0f)
    val intersection = ix.toDouble() * iy.toDouble()
    if (intersection <= 0.0) return 0.0
    val base = minOf(aa.area, bb.area).coerceAtLeast(0.0001)
    return (intersection / base).coerceIn(0.0, 1.0)
}

private fun evaluateSequenceSafety(design: Design, proposal: SequenceOptimizationProposal): SequenceSafetyReport {
    val blocks = calculateThreadSequenceBlocks(design)
    if (blocks.size < 2) {
        return SequenceSafetyReport(0, 0, 0, 0, "BAIXO RISCO", "Poucos blocos para comparar geometricamente.")
    }
    val proposedPosition = proposal.orderedBlockIndices.mapIndexed { index, blockIndex -> blockIndex to index }.toMap()
    val bounds = blocks.associate { it.index to sequenceBlockBounds(design, it) }
    var overlaps = 0
    var reversed = 0
    var significant = 0
    for (i in 0 until blocks.lastIndex) {
        for (j in i + 1 until blocks.size) {
            val a = blocks[i]
            val b = blocks[j]
            val ab = bounds[a.index] ?: continue
            val bb = bounds[b.index] ?: continue
            val ratio = sequenceBoundsOverlapRatio(ab, bb)
            if (ratio <= 0.0) continue
            overlaps++
            val pa = proposedPosition[a.index] ?: i
            val pb = proposedPosition[b.index] ?: j
            if (pa > pb) {
                reversed++
                if (ratio >= 0.12) significant++
            }
        }
    }
    return when {
        significant > 0 -> SequenceSafetyReport(
            overlaps, reversed, significant, 2, "REVISAR",
            "$significant inversão${if (significant == 1) "" else "ões"} de ordem ocorre${if (significant == 1) "" else "m"} entre blocos com sobreposição geométrica relevante."
        )
        reversed > 0 -> SequenceSafetyReport(
            overlaps, reversed, significant, 1, "ATENÇÃO",
            "$reversed par${if (reversed == 1) "" else "es"} de blocos sobrepostos muda${if (reversed == 1) "" else "m"} de ordem na proposta."
        )
        else -> SequenceSafetyReport(
            overlaps, 0, 0, 0, "BAIXO RISCO",
            "Nenhum par de blocos geometricamente sobreposto teve a ordem invertida pela proposta."
        )
    }
}

'''
text = text[:insert_at] + core + text[insert_at:]

# Viewer owns a temporary visual proposal that never enters the working copy until confirmed.
old = '    var focusedThreadBlock by remember(workingDesign) { mutableStateOf<Int?>(null) }\n'
new = '    var focusedThreadBlock by remember(workingDesign) { mutableStateOf<Int?>(null) }\n    var sequencePreviewDesign by remember(workingDesign) { mutableStateOf<Design?>(null) }\n'
if old not in text:
    raise SystemExit('0.2.24 focusedThreadBlock state anchor not found')
text = text.replace(old, new, 1)

# Feed machine profile and preview callback into Safe Editor.
old = '''        SafeEditorPanel(
            original = design,
            working = workingDesign,'''
new = '''        SafeEditorPanel(
            original = design,
            working = workingDesign,
            machineConfig = machineConfig,'''
if old not in text:
    raise SystemExit('0.2.24 SafeEditorPanel invocation anchor not found')
text = text.replace(old, new, 1)

old = '''            onApplySequenceOptimization = { order ->
                runCatching { applySequenceOptimization(workingDesign, order) }.getOrNull()?.let {
                    commitWorkingEdit(it)
                    simulatorPlaying = false
                    focusMarker = null
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusedThreadBlock = null
                    zoom = 1f
                    pan = Offset.Zero
                }
            }
        )'''
new = '''            onApplySequenceOptimization = { order ->
                runCatching { applySequenceOptimization(workingDesign, order) }.getOrNull()?.let {
                    sequencePreviewDesign = null
                    commitWorkingEdit(it)
                    simulatorPlaying = false
                    focusMarker = null
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusedThreadBlock = null
                    zoom = 1f
                    pan = Offset.Zero
                }
            },
            onPreviewSequenceOptimization = { order ->
                sequencePreviewDesign = order?.let { proposedOrder ->
                    runCatching { applySequenceOptimization(workingDesign, proposedOrder) }.getOrNull()
                }
                simulatorPlaying = false
                simulatorPosition = stitchIndices.size
                focusMarker = null
                selectedDiagnostic = null
                assistedPreview = null
                focusedThreadBlock = null
                zoom = 1f
                pan = Offset.Zero
            }
        )'''
if old not in text:
    raise SystemExit('0.2.24 optimizer callback anchor not found')
text = text.replace(old, new, 1)

# Canvas displays the temporary proposal only while the user asks for it.
viewer_start = text.index('@Composable\nprivate fun ViewerScreen(')
viewer_end = text.index('private enum class DiagnosticKind', viewer_start)
viewer = text[viewer_start:viewer_end]
canvas_old = '''                design = workingDesign,
                zoom = zoom,'''
canvas_new = '''                design = sequencePreviewDesign ?: workingDesign,
                zoom = zoom,'''
if canvas_old not in viewer:
    raise SystemExit('0.2.24 StitchCanvas design anchor not found')
viewer = viewer.replace(canvas_old, canvas_new, 1)
visible_old = '                visibleUntil = visibleUntil,\n'
visible_new = '                visibleUntil = if (sequencePreviewDesign != null) (sequencePreviewDesign?.stitches?.size ?: visibleUntil) else visibleUntil,\n'
if visible_old not in viewer:
    raise SystemExit('0.2.24 StitchCanvas visibleUntil anchor not found')
viewer = viewer.replace(visible_old, visible_new, 1)
text = text[:viewer_start] + viewer + text[viewer_end:]

# Extend Safe Editor contract.
old = '''private fun SafeEditorPanel(
    original: Design,
    working: Design,'''
new = '''private fun SafeEditorPanel(
    original: Design,
    working: Design,
    machineConfig: MachineConfig,'''
if old not in text:
    raise SystemExit('0.2.24 SafeEditorPanel signature machine anchor not found')
text = text.replace(old, new, 1)

old = '''    onFocusThreadBlock: (Int) -> Unit,
    onApplySequenceOptimization: (List<Int>) -> Unit
) {'''
new = '''    onFocusThreadBlock: (Int) -> Unit,
    onApplySequenceOptimization: (List<Int>) -> Unit,
    onPreviewSequenceOptimization: (List<Int>?) -> Unit
) {'''
if old not in text:
    raise SystemExit('0.2.24 SafeEditorPanel callback signature anchor not found')
text = text.replace(old, new, 1)

old = 'ThreadPalettePanel(design=working,onChangeColor=onThreadColorChange,onApplyCatalogThread=onCatalogThreadApply,onMoveBlock=onMoveThreadBlock,onApplyBlockThread=onApplyBlockThread,onFocusBlock=onFocusThreadBlock,onApplyOptimizedSequence=onApplySequenceOptimization)'
new = 'ThreadPalettePanel(design=working,machineConfig=machineConfig,onChangeColor=onThreadColorChange,onApplyCatalogThread=onCatalogThreadApply,onMoveBlock=onMoveThreadBlock,onApplyBlockThread=onApplyBlockThread,onFocusBlock=onFocusThreadBlock,onApplyOptimizedSequence=onApplySequenceOptimization,onPreviewOptimizedSequence=onPreviewSequenceOptimization)'
if old not in text:
    raise SystemExit('0.2.24 ThreadPalettePanel call anchor not found')
text = text.replace(old, new, 1)

old = 'private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit,onMoveBlock:(Int,Int)->Unit,onApplyBlockThread:(Int,DesignThreadInfo)->Unit,onFocusBlock:(Int)->Unit,onApplyOptimizedSequence:(List<Int>)->Unit){'
new = 'private fun ThreadPalettePanel(design:Design,machineConfig:MachineConfig,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit,onMoveBlock:(Int,Int)->Unit,onApplyBlockThread:(Int,DesignThreadInfo)->Unit,onFocusBlock:(Int)->Unit,onApplyOptimizedSequence:(List<Int>)->Unit,onPreviewOptimizedSequence:(List<Int>?)->Unit){'
if old not in text:
    raise SystemExit('0.2.24 ThreadPalettePanel signature anchor not found')
text = text.replace(old, new, 1)

# Add visual comparison mode state beside the existing optimizer preview.
old = '    var optimizationPreview by remember(design){mutableStateOf<SequenceOptimizationProposal?>(null)}\n'
new = '    var optimizationPreview by remember(design){mutableStateOf<SequenceOptimizationProposal?>(null)}\n    var showingOptimizedCanvas by remember(design){mutableStateOf(false)}\n'
if old not in text:
    raise SystemExit('0.2.24 optimizationPreview state anchor not found')
text = text.replace(old, new, 1)

# Reset visual proposal whenever a new simulation is requested.
old = '                            onClick={ optimizationPreview=buildSequenceOptimizationProposal(design) },\n'
new = '''                            onClick={
                                optimizationPreview=buildSequenceOptimizationProposal(design)
                                showingOptimizedCanvas=false
                                onPreviewOptimizedSequence(null)
                            },
'''
if old not in text:
    raise SystemExit('0.2.24 optimizer button anchor not found')
text = text.replace(old, new, 1)

# Enrich optimizer preview with safety, machine-aware timing and ORIGINAL/PROPOSTA visual toggle.
old = '''                        optimizationPreview?.let{preview->
                            val travelSaved=preview.travelDeltaMm
                            Surface(shape=RoundedCornerShape(13.dp),color=CardBrown,border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.42f))){'''
new = '''                        optimizationPreview?.let{preview->
                            val travelSaved=preview.travelDeltaMm
                            val safety=remember(design,preview){evaluateSequenceSafety(design,preview)}
                            val proposalDesign=remember(design,preview){runCatching{applySequenceOptimization(design,preview.orderedBlockIndices)}.getOrNull()}
                            val beforeMinutes=remember(design,machineConfig){estimateMachineMinutes(design,machineConfig)}
                            val afterMinutes=remember(proposalDesign,machineConfig){proposalDesign?.let{estimateMachineMinutes(it,machineConfig)}?:beforeMinutes}
                            Surface(shape=RoundedCornerShape(13.dp),color=CardBrown,border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.42f))){'''
if old not in text:
    raise SystemExit('0.2.24 optimizer preview header anchor not found')
text = text.replace(old, new, 1)

old = '''                                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=SurfaceBrown){Column(Modifier.padding(7.dp)){Text("ANTES",color=Muted,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.before.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.before.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp)}}
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=Gold.copy(alpha=.10f)){Column(Modifier.padding(7.dp)){Text("PROPOSTA",color=Gold,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.after.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.after.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp)}}
                                    }'''
new = '''                                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=SurfaceBrown){Column(Modifier.padding(7.dp)){Text("ANTES",color=Muted,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.before.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.before.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp);Text("≈ ${kotlin.math.ceil(beforeMinutes).toInt()} min",color=Muted,fontSize=7.sp)}}
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=Gold.copy(alpha=.10f)){Column(Modifier.padding(7.dp)){Text("PROPOSTA",color=Gold,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.after.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.after.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp);Text("≈ ${kotlin.math.ceil(afterMinutes).toInt()} min",color=Gold,fontSize=7.sp)}}
                                    }
                                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                                        FilledTonalButton(
                                            onClick={showingOptimizedCanvas=false;onPreviewOptimizedSequence(null)},
                                            modifier=Modifier.weight(1f),shape=RoundedCornerShape(13.dp),
                                            colors=ButtonDefaults.filledTonalButtonColors(containerColor=if(!showingOptimizedCanvas)Gold.copy(alpha=.20f) else SurfaceBrown,contentColor=if(!showingOptimizedCanvas)Gold else Muted)
                                        ){Icon(Icons.Rounded.Layers,null,modifier=Modifier.size(15.dp));Spacer(Modifier.width(4.dp));Text("ORIGINAL",fontSize=7.sp,fontWeight=FontWeight.Bold)}
                                        FilledTonalButton(
                                            onClick={showingOptimizedCanvas=true;onPreviewOptimizedSequence(preview.orderedBlockIndices)},
                                            modifier=Modifier.weight(1f),shape=RoundedCornerShape(13.dp),
                                            colors=ButtonDefaults.filledTonalButtonColors(containerColor=if(showingOptimizedCanvas)Gold.copy(alpha=.20f) else SurfaceBrown,contentColor=if(showingOptimizedCanvas)Gold else Muted)
                                        ){Icon(Icons.Rounded.AutoFixHigh,null,modifier=Modifier.size(15.dp));Spacer(Modifier.width(4.dp));Text("PROPOSTA",fontSize=7.sp,fontWeight=FontWeight.Bold)}
                                    }
                                    Text(if(showingOptimizedCanvas)"O desenho acima está mostrando a PROPOSTA temporária. Nada foi aplicado." else "O desenho acima está mostrando a sequência ORIGINAL da cópia de trabalho.",color=if(showingOptimizedCanvas)Gold else Muted,fontSize=7.sp,lineHeight=10.sp)
                                    Surface(shape=RoundedCornerShape(11.dp),color=if(safety.severity>=2)Cream.copy(alpha=.08f) else Gold.copy(alpha=.07f),border=androidx.compose.foundation.BorderStroke(1.dp,if(safety.severity>=2)Cream.copy(alpha=.45f) else Gold.copy(alpha=.28f))){
                                        Column(Modifier.fillMaxWidth().padding(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
                                            Row(verticalAlignment=Alignment.CenterVertically){Icon(if(safety.severity>=2)Icons.Rounded.ReportProblem else if(safety.severity==1)Icons.Rounded.WarningAmber else Icons.Rounded.Verified,null,tint=Gold,modifier=Modifier.size(16.dp));Spacer(Modifier.width(5.dp));Text("Safety Check • ${safety.label}",color=if(safety.severity>=2)Cream else Gold,fontSize=8.sp,fontWeight=FontWeight.Bold)}
                                            Text(safety.detail,color=Muted,fontSize=7.sp,lineHeight=10.sp)
                                            Text("${safety.overlappingPairs} pares com proximidade/sobreposição • ${safety.reversedOverlapPairs} inversões • ${safety.significantReversedPairs} relevantes",color=Muted,fontSize=7.sp)
                                            Text("Checagem geométrica: não substitui a intenção de digitalização, underlay, cobertura ou teste físico.",color=Muted,fontSize=6.sp,lineHeight=9.sp)
                                        }
                                    }'''
if old not in text:
    raise SystemExit('0.2.24 before/after metrics anchor not found')
text = text.replace(old, new, 1)

# Applying/cancelling always clears the temporary canvas proposal.
old = 'onClick={onApplyOptimizedSequence(preview.orderedBlockIndices);optimizationPreview=null},'
new = 'onClick={onPreviewOptimizedSequence(null);showingOptimizedCanvas=false;onApplyOptimizedSequence(preview.orderedBlockIndices);optimizationPreview=null},'
if old not in text:
    raise SystemExit('0.2.24 apply optimizer button anchor not found')
text = text.replace(old, new, 1)

old = 'TextButton(onClick={optimizationPreview=null},modifier=Modifier.fillMaxWidth()){' 
new = 'TextButton(onClick={onPreviewOptimizedSequence(null);showingOptimizedCanvas=false;optimizationPreview=null},modifier=Modifier.fillMaxWidth()){' 
if old not in text:
    raise SystemExit('0.2.24 cancel optimizer preview anchor not found')
text = text.replace(old, new, 1)

text = text.replace('0.2.23', '0.2.24')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.24 visual sequence comparator + safety check applied successfully')
