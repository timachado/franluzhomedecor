from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_043_fix.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# BORDATTO 0.2.23 — Otimizador Assistido de Sequência
# - Computes a deterministic heuristic proposal from the real color blocks.
# - Preview compares thread changes + connector travel before/after.
# - Never applies automatically; user must explicitly confirm.
# - Reuses the reversible working-copy/undo stack from the Safe Editor.
# -----------------------------------------------------------------------------

insert_at = text.index('class MainActivity')
core = r'''private data class SequenceOptimizationMetrics(
    val threadChanges: Int,
    val connectorTravelMm: Double
)

private data class SequenceOptimizationProposal(
    val orderedBlockIndices: List<Int>,
    val before: SequenceOptimizationMetrics,
    val after: SequenceOptimizationMetrics,
    val movedBlocks: Int,
    val moves: List<Pair<Int, Int>>
) {
    val savedChanges: Int get() = (before.threadChanges - after.threadChanges).coerceAtLeast(0)
    val travelDeltaMm: Double get() = before.connectorTravelMm - after.connectorTravelMm
}

private fun sequenceBlockFirstStitch(design: Design, block: ThreadSequenceBlock): StitchPoint? =
    design.stitches.subList(
        block.startRaw.coerceIn(0, design.stitches.size),
        block.endRawExclusive.coerceIn(block.startRaw.coerceIn(0, design.stitches.size), design.stitches.size)
    ).firstOrNull { it.command == StitchCommand.STITCH }

private fun sequenceBlockLastStitch(design: Design, block: ThreadSequenceBlock): StitchPoint? =
    design.stitches.subList(
        block.startRaw.coerceIn(0, design.stitches.size),
        block.endRawExclusive.coerceIn(block.startRaw.coerceIn(0, design.stitches.size), design.stitches.size)
    ).lastOrNull { it.command == StitchCommand.STITCH }

private fun sequenceConnectorDistance(design: Design, a: ThreadSequenceBlock, b: ThreadSequenceBlock): Double {
    val end = sequenceBlockLastStitch(design, a) ?: return 0.0
    val start = sequenceBlockFirstStitch(design, b) ?: return 0.0
    return kotlin.math.hypot((start.x - end.x).toDouble(), (start.y - end.y).toDouble())
}

private fun measureThreadSequence(design: Design, order: List<ThreadSequenceBlock>): SequenceOptimizationMetrics {
    if (order.isEmpty()) return SequenceOptimizationMetrics(0, 0.0)
    var changes = 0
    var travel = 0.0
    order.zipWithNext().forEach { (a, b) ->
        if (threadIdentity(threadInfoForSequenceBlock(design, a)) != threadIdentity(threadInfoForSequenceBlock(design, b))) {
            changes++
        }
        travel += sequenceConnectorDistance(design, a, b)
    }
    return SequenceOptimizationMetrics(changes, travel)
}

private fun buildSequenceOptimizationProposal(design: Design): SequenceOptimizationProposal? {
    val blocks = calculateThreadSequenceBlocks(design)
    if (blocks.size < 2) return null

    // Linked grouping keeps each thread's internal embroidery order stable. The heuristic
    // only chooses the order of thread groups, which minimizes repeated thread changes,
    // then samples group starts to reduce connector travel within that constraint.
    val groups = linkedMapOf<String, MutableList<ThreadSequenceBlock>>()
    blocks.forEach { block ->
        val key = threadIdentity(threadInfoForSequenceBlock(design, block))
        groups.getOrPut(key) { mutableListOf() } += block
    }
    val grouped = groups.values.map { it.toList() }

    fun candidateFrom(startGroup: Int): List<ThreadSequenceBlock> {
        val remaining = grouped.indices.filter { it != startGroup }.toMutableSet()
        val ordered = grouped[startGroup].toMutableList()
        while (remaining.isNotEmpty()) {
            val previous = ordered.last()
            val nextGroup = remaining.minByOrNull { groupIndex ->
                val first = grouped[groupIndex].first()
                sequenceConnectorDistance(design, previous, first)
            } ?: remaining.first()
            ordered += grouped[nextGroup]
            remaining.remove(nextGroup)
        }
        return ordered
    }

    val before = measureThreadSequence(design, blocks)
    val starts = if (grouped.size <= 24) grouped.indices.toList() else listOf(0) + (1 until grouped.size step 3).take(23)
    val candidates = starts.map { candidateFrom(it) }
    val best = candidates.minWithOrNull(
        compareBy<List<ThreadSequenceBlock>> { measureThreadSequence(design, it).threadChanges }
            .thenBy { measureThreadSequence(design, it).connectorTravelMm }
    ) ?: blocks
    val after = measureThreadSequence(design, best)
    val newPositions = best.mapIndexed { newIndex, block -> block.index to newIndex }.toMap()
    val moves = blocks.mapNotNull { block ->
        val next = newPositions[block.index] ?: block.index
        if (next == block.index) null else (block.index to next)
    }
    return SequenceOptimizationProposal(
        orderedBlockIndices = best.map { it.index },
        before = before,
        after = after,
        movedBlocks = moves.size,
        moves = moves
    )
}

private fun applySequenceOptimization(design: Design, orderedBlockIndices: List<Int>): Design {
    val blocks = calculateThreadSequenceBlocks(design)
    require(orderedBlockIndices.size == blocks.size) { "A proposta não corresponde mais à sequência atual." }
    require(orderedBlockIndices.distinct().size == blocks.size) { "A proposta contém blocos duplicados." }
    val byIndex = blocks.associateBy { it.index }
    val ordered = orderedBlockIndices.map { index -> byIndex[index] ?: error("Bloco $index não encontrado na sequência atual.") }
    return rebuildThreadSequence(design, ordered)
}

'''
text = text[:insert_at] + core + text[insert_at:]

# Viewer commits a confirmed proposal as one reversible edit.
old = '''            onFocusThreadBlock = { blockIndex ->
                val block=calculateThreadSequenceBlocks(workingDesign).getOrNull(blockIndex)
                if(block!=null){ simulatorPlaying=false; simulatorPosition=stitchIndices.size; focusMarker=null; selectedDiagnostic=null; assistedPreview=null; focusedThreadBlock=blockIndex; zoom=1.35f; pan=Offset.Zero }
            }
        )'''
new = '''            onFocusThreadBlock = { blockIndex ->
                val block=calculateThreadSequenceBlocks(workingDesign).getOrNull(blockIndex)
                if(block!=null){ simulatorPlaying=false; simulatorPosition=stitchIndices.size; focusMarker=null; selectedDiagnostic=null; assistedPreview=null; focusedThreadBlock=blockIndex; zoom=1.35f; pan=Offset.Zero }
            },
            onApplySequenceOptimization = { order ->
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
if old not in text:
    raise SystemExit('0.2.23 viewer optimizer callback anchor not found')
text = text.replace(old, new, 1)

old = '''    onApplyBlockThread: (Int, DesignThreadInfo) -> Unit,
    onFocusThreadBlock: (Int) -> Unit
) {'''
new = '''    onApplyBlockThread: (Int, DesignThreadInfo) -> Unit,
    onFocusThreadBlock: (Int) -> Unit,
    onApplySequenceOptimization: (List<Int>) -> Unit
) {'''
if old not in text:
    raise SystemExit('0.2.23 SafeEditorPanel signature anchor not found')
text = text.replace(old, new, 1)

old = 'ThreadPalettePanel(design=working,onChangeColor=onThreadColorChange,onApplyCatalogThread=onCatalogThreadApply,onMoveBlock=onMoveThreadBlock,onApplyBlockThread=onApplyBlockThread,onFocusBlock=onFocusThreadBlock)'
new = 'ThreadPalettePanel(design=working,onChangeColor=onThreadColorChange,onApplyCatalogThread=onCatalogThreadApply,onMoveBlock=onMoveThreadBlock,onApplyBlockThread=onApplyBlockThread,onFocusBlock=onFocusThreadBlock,onApplyOptimizedSequence=onApplySequenceOptimization)'
if old not in text:
    raise SystemExit('0.2.23 ThreadPalettePanel call anchor not found')
text = text.replace(old, new, 1)

old = 'private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit,onMoveBlock:(Int,Int)->Unit,onApplyBlockThread:(Int,DesignThreadInfo)->Unit,onFocusBlock:(Int)->Unit){'
new = 'private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit,onMoveBlock:(Int,Int)->Unit,onApplyBlockThread:(Int,DesignThreadInfo)->Unit,onFocusBlock:(Int)->Unit,onApplyOptimizedSequence:(List<Int>)->Unit){'
if old not in text:
    raise SystemExit('0.2.23 ThreadPalettePanel signature anchor not found')
text = text.replace(old, new, 1)

# Preview state resets whenever the working design changes (manual move, color edit, undo/redo, etc.).
old = '    var blockCatalogIndex by remember{mutableStateOf<Int?>(null)}\n'
new = '    var blockCatalogIndex by remember{mutableStateOf<Int?>(null)}\n    var optimizationPreview by remember(design){mutableStateOf<SequenceOptimizationProposal?>(null)}\n'
if old not in text:
    raise SystemExit('0.2.23 optimizer preview state anchor not found')
text = text.replace(old, new, 1)

# Add simulation/confirmation UI immediately after the sequence header and advisory.
anchor = '''                        if(potentialSavings>0) Text("Estimativa: blocos que usam a mesma linha poderiam ficar juntos. O BORDATTO não muda a ordem sozinho.",color=Gold,fontSize=7.sp,lineHeight=10.sp)
                        sequenceBlocks.take(24).forEachIndexed{position,block->'''
optimizer_ui = r'''                        if(potentialSavings>0) Text("Estimativa: blocos que usam a mesma linha poderiam ficar juntos. O BORDATTO não muda a ordem sozinho.",color=Gold,fontSize=7.sp,lineHeight=10.sp)
                        FilledTonalButton(
                            onClick={ optimizationPreview=buildSequenceOptimizationProposal(design) },
                            enabled=sequenceBlocks.size>1,
                            modifier=Modifier.fillMaxWidth(),
                            shape=RoundedCornerShape(14.dp),
                            colors=ButtonDefaults.filledTonalButtonColors(containerColor=Gold.copy(alpha=.14f),contentColor=Gold)
                        ){
                            Icon(Icons.Rounded.AutoFixHigh,null,modifier=Modifier.size(16.dp));Spacer(Modifier.width(6.dp))
                            Text("Simular otimização assistida",fontSize=8.sp,fontWeight=FontWeight.Bold)
                        }
                        optimizationPreview?.let{preview->
                            val travelSaved=preview.travelDeltaMm
                            Surface(shape=RoundedCornerShape(13.dp),color=CardBrown,border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.42f))){
                                Column(Modifier.fillMaxWidth().padding(9.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
                                    Row(verticalAlignment=Alignment.CenterVertically){
                                        Icon(Icons.Rounded.CompareArrows,null,tint=Gold,modifier=Modifier.size(17.dp));Spacer(Modifier.width(6.dp))
                                        Column(Modifier.weight(1f)){
                                            Text("Prévia antes / depois",color=Cream,fontSize=9.sp,fontWeight=FontWeight.SemiBold)
                                            Text("Heurística: agrupa a mesma linha e preserva a ordem interna de cada grupo.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
                                        }
                                    }
                                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=SurfaceBrown){Column(Modifier.padding(7.dp)){Text("ANTES",color=Muted,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.before.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.before.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp)}}
                                        Surface(Modifier.weight(1f),shape=RoundedCornerShape(10.dp),color=Gold.copy(alpha=.10f)){Column(Modifier.padding(7.dp)){Text("PROPOSTA",color=Gold,fontSize=6.sp,fontWeight=FontWeight.Bold);Text("${preview.after.threadChanges} trocas",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold);Text("${"%.1f".format(preview.after.connectorTravelMm)} mm desloc.",color=Muted,fontSize=7.sp)}}
                                    }
                                    Text(
                                        buildString{
                                            append(if(preview.savedChanges>0) "−${preview.savedChanges} troca${if(preview.savedChanges==1)"" else "s"}" else "sem redução de trocas")
                                            append(" • ")
                                            append(if(travelSaved>=0) "−${"%.1f".format(travelSaved)} mm de deslocamento" else "+${"%.1f".format(-travelSaved)} mm de deslocamento")
                                            append(" • ${preview.movedBlocks} bloco${if(preview.movedBlocks==1)"" else "s"} mudaria${if(preview.movedBlocks==1)"" else "m"} de posição")
                                        },
                                        color=if(preview.savedChanges>0 || travelSaved>0) Gold else Muted,
                                        fontSize=7.sp,lineHeight=10.sp
                                    )
                                    if(preview.moves.isNotEmpty()){
                                        Text("Movimentos: "+preview.moves.take(10).joinToString(" • "){(from,to)->"B${from+1}→${to+1}"}+if(preview.moves.size>10)" • +${preview.moves.size-10}" else "",color=Muted,fontSize=7.sp,lineHeight=10.sp)
                                    }
                                    if(preview.movedBlocks==0){
                                        Text("A sequência atual já coincide com a melhor proposta encontrada por esta heurística.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
                                    }else{
                                        Button(
                                            onClick={onApplyOptimizedSequence(preview.orderedBlockIndices);optimizationPreview=null},
                                            modifier=Modifier.fillMaxWidth(),
                                            shape=RoundedCornerShape(14.dp),
                                            colors=ButtonDefaults.buttonColors(containerColor=Gold,contentColor=Ink)
                                        ){
                                            Icon(Icons.Rounded.DoneAll,null,modifier=Modifier.size(16.dp));Spacer(Modifier.width(6.dp));Text("Aplicar proposta à cópia de trabalho",fontSize=8.sp,fontWeight=FontWeight.Bold)
                                        }
                                    }
                                    TextButton(onClick={optimizationPreview=null},modifier=Modifier.fillMaxWidth()){
                                        Text("Cancelar prévia",color=Muted,fontSize=8.sp)
                                    }
                                    Text("A proposta é heurística e não analisa objetos, sobreposições ou intenção artística. Revise no simulador antes de exportar.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
                                }
                            }
                        }
                        sequenceBlocks.take(24).forEachIndexed{position,block->'''
if anchor not in text:
    raise SystemExit('0.2.23 sequence optimizer UI anchor not found')
text = text.replace(anchor, optimizer_ui, 1)

text = text.replace('0.2.22', '0.2.23')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.23 assisted sequence optimizer applied successfully')
