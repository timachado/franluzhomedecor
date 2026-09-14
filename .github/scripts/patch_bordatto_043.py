from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_042.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# BORDATTO 0.2.22 — Gerenciador de Sequência de Cores
insert_at = text.index('class MainActivity')
core = r'''private data class ThreadSequenceBlock(
    val index: Int,
    val colorIndex: Int,
    val stitchCount: Int,
    val startRaw: Int,
    val endRawExclusive: Int,
    val startStitchPosition: Int
)

private fun calculateThreadSequenceBlocks(design: Design): List<ThreadSequenceBlock> {
    val out = mutableListOf<ThreadSequenceBlock>()
    var currentColor: Int? = null
    var blockStartRaw = 0
    var blockStartStitchPosition = 0
    var blockStitches = 0
    var stitchPosition = 0
    var pendingBoundary: Int? = null
    design.stitches.forEachIndexed { rawIndex, point ->
        if (point.command == StitchCommand.STITCH) {
            val color = point.color.coerceAtLeast(0)
            if (currentColor == null) {
                currentColor = color
                blockStartRaw = pendingBoundary ?: rawIndex
                blockStartStitchPosition = stitchPosition
                blockStitches = 1
            } else if (color != currentColor) {
                val nextStart = pendingBoundary ?: rawIndex
                out += ThreadSequenceBlock(out.size,currentColor!!,blockStitches,blockStartRaw,nextStart,blockStartStitchPosition)
                currentColor = color
                blockStartRaw = nextStart
                blockStartStitchPosition = stitchPosition
                blockStitches = 1
            } else blockStitches++
            pendingBoundary = null
            stitchPosition++
        } else if (currentColor != null && pendingBoundary == null && point.command != StitchCommand.END) {
            pendingBoundary = rawIndex
        }
    }
    currentColor?.let { color ->
        val end = design.stitches.indexOfLast { it.command == StitchCommand.END }.takeIf { it >= blockStartRaw } ?: design.stitches.size
        out += ThreadSequenceBlock(out.size,color,blockStitches,blockStartRaw,end,blockStartStitchPosition)
    }
    return out
}

private fun threadInfoForSequenceBlock(design: Design, block: ThreadSequenceBlock): DesignThreadInfo =
    design.threadInfos.getOrNull(block.colorIndex) ?: DesignThreadInfo(color = effectiveThreadColor(design, block.colorIndex))

private fun threadIdentity(info: DesignThreadInfo): String {
    val brand = info.brand.trim().lowercase(); val catalog = info.catalog.trim().lowercase()
    return if (brand.isNotBlank() || catalog.isNotBlank()) "$brand|$catalog|${info.color and 0xFFFFFF}" else "rgb|${info.color and 0xFFFFFF}"
}

private fun potentialThreadChangeSavings(design: Design): Int {
    val blocks = calculateThreadSequenceBlocks(design)
    if (blocks.size < 2) return 0
    val uniqueThreads = blocks.map { threadIdentity(threadInfoForSequenceBlock(design,it)) }.distinct().size
    return (blocks.size - uniqueThreads).coerceAtLeast(0)
}

private data class PreparedSequenceBlock(val source: ThreadSequenceBlock,val info: DesignThreadInfo,val events: List<StitchPoint>)

private fun rebuildThreadSequence(design: Design, orderedBlocks: List<ThreadSequenceBlock>, overrides: Map<Int,DesignThreadInfo> = emptyMap()): Design {
    require(orderedBlocks.isNotEmpty()) { "A matriz não possui blocos de cor para reorganizar." }
    val prepared = orderedBlocks.map { block ->
        val start = block.startRaw.coerceIn(0,design.stitches.size)
        val end = block.endRawExclusive.coerceIn(start,design.stitches.size)
        val raw = design.stitches.subList(start,end)
        val firstStitch = raw.indexOfFirst { it.command == StitchCommand.STITCH }
        require(firstStitch >= 0) { "Bloco ${block.index+1} sem pontadas válidas." }
        PreparedSequenceBlock(block,overrides[block.index] ?: threadInfoForSequenceBlock(design,block),raw.drop(firstStitch).filter { it.command != StitchCommand.COLOR_CHANGE && it.command != StitchCommand.END })
    }
    val rebuilt = mutableListOf<StitchPoint>(); val normalizedInfos = mutableListOf<DesignThreadInfo>()
    var activeIdentity:String?=null; var activeColorIndex=-1
    prepared.forEach { pb ->
        val first = pb.events.firstOrNull { it.command == StitchCommand.STITCH } ?: return@forEach
        val identity = threadIdentity(pb.info)
        if (activeIdentity != identity) {
            activeColorIndex++
            normalizedInfos += pb.info
            if (rebuilt.isNotEmpty()) rebuilt += StitchPoint(first.x,first.y,StitchCommand.COLOR_CHANGE,activeColorIndex)
            activeIdentity = identity
        }
        rebuilt += StitchPoint(first.x,first.y,StitchCommand.JUMP,activeColorIndex)
        pb.events.forEach { rebuilt += it.copy(color=activeColorIndex) }
    }
    require(rebuilt.any { it.command == StitchCommand.STITCH }) { "A reorganização não produziu uma sequência válida." }
    val last = rebuilt.last(); rebuilt += StitchPoint(last.x,last.y,StitchCommand.END,activeColorIndex.coerceAtLeast(0))
    return design.copy(stitches=rebuilt,colors=normalizedInfos.size.coerceAtLeast(1),threadColors=normalizedInfos.map { it.color },threadInfos=normalizedInfos)
}

private fun reorderThreadSequenceBlock(design: Design, from:Int, to:Int): Design {
    val blocks=calculateThreadSequenceBlocks(design); require(from in blocks.indices && to in blocks.indices) { "Bloco de sequência inválido." }
    if(from==to) return design
    val order=blocks.toMutableList(); val moved=order.removeAt(from); order.add(to,moved)
    return rebuildThreadSequence(design,order)
}

private fun applyCatalogThreadToSequenceBlock(design: Design, blockIndex:Int, selected:DesignThreadInfo): Design {
    val blocks=calculateThreadSequenceBlocks(design); require(blockIndex in blocks.indices) { "Bloco de sequência inválido." }
    return rebuildThreadSequence(design,blocks,mapOf(blockIndex to selected))
}

'''
text=text[:insert_at]+core+text[insert_at:]

old='''            onCatalogThreadApply = { index, selected ->
                val count = maxOf(workingDesign.colors, index + 1)
                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }
                palette[index] = selected.color
                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }
                infos[index] = selected
                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))
            }
        )'''
new='''            onCatalogThreadApply = { index, selected ->
                val count = maxOf(workingDesign.colors, index + 1)
                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }
                palette[index] = selected.color
                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }
                infos[index] = selected
                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))
            },
            onMoveThreadBlock = { from, to ->
                runCatching { reorderThreadSequenceBlock(workingDesign,from,to) }.getOrNull()?.let {
                    commitWorkingEdit(it); simulatorPlaying=false; focusMarker=null; selectedDiagnostic=null; assistedPreview=null
                }
            },
            onApplyBlockThread = { blockIndex, selected ->
                runCatching { applyCatalogThreadToSequenceBlock(workingDesign,blockIndex,selected) }.getOrNull()?.let {
                    commitWorkingEdit(it); simulatorPlaying=false; focusMarker=null; selectedDiagnostic=null; assistedPreview=null
                }
            },
            onFocusThreadBlock = { blockIndex ->
                val block=calculateThreadSequenceBlocks(workingDesign).getOrNull(blockIndex)
                if(block!=null){ simulatorPlaying=false; simulatorPosition=stitchIndices.size; focusMarker=null; selectedDiagnostic=null; assistedPreview=null; focusedThreadBlock=blockIndex; zoom=1.35f; pan=Offset.Zero }
            }
        )'''
if old not in text: raise SystemExit('0.2.22 SafeEditor callback marker not found')
text=text.replace(old,new,1)

text=text.replace('''    onShareLastExport: () -> Unit,
    onThreadColorChange: (Int, Int) -> Unit,
    onCatalogThreadApply: (Int, DesignThreadInfo) -> Unit
) {''','''    onShareLastExport: () -> Unit,
    onThreadColorChange: (Int, Int) -> Unit,
    onCatalogThreadApply: (Int, DesignThreadInfo) -> Unit,
    onMoveThreadBlock: (Int, Int) -> Unit,
    onApplyBlockThread: (Int, DesignThreadInfo) -> Unit,
    onFocusThreadBlock: (Int) -> Unit
) {''',1)

old='            ThreadPalettePanel(design = working, onChangeColor = onThreadColorChange, onApplyCatalogThread = onCatalogThreadApply)'
new='''            ThreadPalettePanel(design=working,onChangeColor=onThreadColorChange,onApplyCatalogThread=onCatalogThreadApply,onMoveBlock=onMoveThreadBlock,onApplyBlockThread=onApplyBlockThread,onFocusBlock=onFocusThreadBlock)'''
if old not in text: raise SystemExit('0.2.22 palette call marker not found')
text=text.replace(old,new,1)

old='''    var simulatorSpeed by remember(workingDesign) { mutableFloatStateOf(1f) }
    val visualDiagnostics = remember(workingDesign) { collectDiagnosticMarkers(workingDesign) }'''
new='''    var simulatorSpeed by remember(workingDesign) { mutableFloatStateOf(1f) }
    var focusedThreadBlock by remember(workingDesign) { mutableStateOf<Int?>(null) }
    val focusedThreadRange = remember(workingDesign, focusedThreadBlock) {
        focusedThreadBlock?.let { index -> calculateThreadSequenceBlocks(workingDesign).getOrNull(index)?.let { it.startRaw until it.endRawExclusive } }
    }
    val visualDiagnostics = remember(workingDesign) { collectDiagnosticMarkers(workingDesign) }'''
if old not in text: raise SystemExit('0.2.22 viewer focus state marker not found')
text=text.replace(old,new,1)
text=text.replace('        if (p != Offset.Zero) focusMarker = null','''        if (p != Offset.Zero) { focusMarker = null; focusedThreadBlock = null }''',1)

old='''                focusMarker = focusMarker,
                correctionPreview = if (diagnosticsVisible) assistedPreview else null
            )'''
new='''                focusMarker = focusMarker,
                correctionPreview = if (diagnosticsVisible) assistedPreview else null,
                highlightRawRange = focusedThreadRange
            )'''
if old not in text: raise SystemExit('0.2.22 canvas call marker not found')
text=text.replace(old,new,1)

text=text.replace('''    diagnostics: List<DiagnosticMarker> = emptyList(),
    focusMarker: DiagnosticMarker? = null,
    correctionPreview: AssistedCorrectionPreview? = null
) {''','''    diagnostics: List<DiagnosticMarker> = emptyList(),
    focusMarker: DiagnosticMarker? = null,
    correctionPreview: AssistedCorrectionPreview? = null,
    highlightRawRange: IntRange? = null
) {''',1)

old='''        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }

        diagnostics.forEach { marker ->'''
new='''        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }
        highlightRawRange?.let { range ->
            val highlight=Path(); var prev:Offset?=null; var prevColor=-1
            range.forEach { rawIndex ->
                if(rawIndex in design.stitches.indices){
                    val point=design.stitches[rawIndex]; val mapped=map(point.x,point.y)
                    if(point.command==StitchCommand.STITCH){
                        if(prev==null || prevColor!=point.color) highlight.moveTo(mapped.x,mapped.y) else highlight.lineTo(mapped.x,mapped.y)
                        prev=mapped; prevColor=point.color
                    } else { prev=null; prevColor=-1 }
                }
            }
            drawPath(highlight,Cream.copy(alpha=.96f),style=Stroke(max(3.2f,3.5f*zoom.coerceAtMost(2.2f)),cap=StrokeCap.Round))
            drawPath(highlight,Gold,style=Stroke(max(1.6f,1.8f*zoom.coerceAtMost(2.2f)),cap=StrokeCap.Round))
        }

        diagnostics.forEach { marker ->'''
if old not in text: raise SystemExit('0.2.22 highlight marker not found')
text=text.replace(old,new,1)

text=text.replace('''private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit){''','''private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit,onMoveBlock:(Int,Int)->Unit,onApplyBlockThread:(Int,DesignThreadInfo)->Unit,onFocusBlock:(Int)->Unit){''',1)
text=text.replace('''    var catalogIndex by remember{mutableStateOf<Int?>(null)}
    val stats=remember(design){calculateThreadColorStats(design)}
    val blocks=remember(design){calculateThreadBlocks(design)}''','''    var catalogIndex by remember{mutableStateOf<Int?>(null)}
    var blockCatalogIndex by remember{mutableStateOf<Int?>(null)}
    val stats=remember(design){calculateThreadColorStats(design)}
    val blocks=remember(design){calculateThreadBlocks(design)}
    val sequenceBlocks=remember(design){calculateThreadSequenceBlocks(design)}
    val potentialSavings=remember(design){potentialThreadChangeSavings(design)}''',1)

old='''                Text("Sequência: "+blocks.take(12).joinToString(" › "){"${it.sequence}:C${it.colorIndex+1}"}+if(blocks.size>12)" › +${blocks.size-12}" else "",color=Muted,fontSize=7.sp)
                stats.take(32).forEach{stat->'''
new=r'''                Surface(shape=RoundedCornerShape(14.dp),color=Gold.copy(alpha=.07f),border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.30f))){
                    Column(Modifier.fillMaxWidth().padding(9.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
                        Row(verticalAlignment=Alignment.CenterVertically){
                            Icon(Icons.Rounded.FormatListNumbered,null,tint=Gold,modifier=Modifier.size(17.dp));Spacer(Modifier.width(7.dp))
                            Column(Modifier.weight(1f)){
                                Text("Sequência de produção",color=Cream,fontSize=9.sp,fontWeight=FontWeight.SemiBold)
                                Text("${sequenceBlocks.size} blocos • ${if(potentialSavings>0)"até $potentialSavings troca${if(potentialSavings==1)"" else "s"} agrupável${if(potentialSavings==1)"" else "eis"}" else "ordem já sem repetição óbvia"}",color=Muted,fontSize=7.sp)
                            }
                        }
                        if(potentialSavings>0) Text("Estimativa: blocos que usam a mesma linha poderiam ficar juntos. O BORDATTO não muda a ordem sozinho.",color=Gold,fontSize=7.sp,lineHeight=10.sp)
                        sequenceBlocks.take(24).forEachIndexed{position,block->
                            val color=effectiveThreadColor(design,block.colorIndex);val info=threadInfoForSequenceBlock(design,block)
                            Surface(shape=RoundedCornerShape(11.dp),color=SurfaceBrown,border=androidx.compose.foundation.BorderStroke(1.dp,LineGold.copy(alpha=.24f))){
                                Row(Modifier.fillMaxWidth().padding(horizontal=7.dp,vertical=6.dp),verticalAlignment=Alignment.CenterVertically){
                                    Surface(shape=CircleShape,color=Gold.copy(alpha=.14f)){Text("${position+1}",color=Gold,fontSize=8.sp,fontWeight=FontWeight.Bold,modifier=Modifier.padding(horizontal=7.dp,vertical=4.dp))}
                                    Spacer(Modifier.width(6.dp));Box(Modifier.size(20.dp).clip(CircleShape).background(Color(color)).border(1.dp,Cream.copy(alpha=.30f),CircleShape));Spacer(Modifier.width(7.dp))
                                    Column(Modifier.weight(1f)){
                                        Text(info.name.takeIf{it.isNotBlank()}?:"Cor ${block.colorIndex+1}",color=Cream,fontSize=8.sp,fontWeight=FontWeight.SemiBold,maxLines=1)
                                        Text("${block.stitchCount} pts • ${info.brand.takeIf{it.isNotBlank()}?:"RGB"} ${info.catalog.takeIf{it.isNotBlank()}?.let{"• $it"}?:""}",color=Muted,fontSize=7.sp,maxLines=1)
                                    }
                                    IconButton(onClick={onFocusBlock(block.index)}){Icon(Icons.Rounded.CenterFocusStrong,"Localizar bloco",tint=Gold,modifier=Modifier.size(16.dp))}
                                    IconButton(onClick={blockCatalogIndex=block.index}){Icon(Icons.Rounded.Palette,"Trocar linha deste bloco",tint=Gold,modifier=Modifier.size(16.dp))}
                                    IconButton(enabled=position>0,onClick={onMoveBlock(block.index,block.index-1)}){Icon(Icons.Rounded.KeyboardArrowUp,"Mover para cima",tint=if(position>0)Gold else Muted.copy(alpha=.35f),modifier=Modifier.size(17.dp))}
                                    IconButton(enabled=position<sequenceBlocks.lastIndex,onClick={onMoveBlock(block.index,block.index+1)}){Icon(Icons.Rounded.KeyboardArrowDown,"Mover para baixo",tint=if(position<sequenceBlocks.lastIndex)Gold else Muted.copy(alpha=.35f),modifier=Modifier.size(17.dp))}
                                }
                            }
                        }
                        if(sequenceBlocks.size>24) Text("Exibindo 24 de ${sequenceBlocks.size} blocos.",color=Muted,fontSize=7.sp)
                        Text("Mover um bloco altera a ordem da cópia de trabalho. Blocos adjacentes da mesma linha são unidos e a sequência é normalizada para exportação PES/JEF.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
                    }
                }
                stats.take(32).forEach{stat->'''
if old not in text: raise SystemExit('0.2.22 sequence UI marker not found')
text=text.replace(old,new,1)

old='''    catalogIndex?.let{index->
        ThreadCatalogDialog(
            colorIndex=index,design=design,onDismiss={catalogIndex=null},
            onApply={selected->onApplyCatalogThread(index,selected)}
        )
    }

}'''
new='''    catalogIndex?.let{index->
        ThreadCatalogDialog(colorIndex=index,design=design,onDismiss={catalogIndex=null},onApply={selected->onApplyCatalogThread(index,selected)})
    }
    blockCatalogIndex?.let{blockIndex->
        calculateThreadSequenceBlocks(design).getOrNull(blockIndex)?.let{block->
            ThreadCatalogDialog(colorIndex=block.colorIndex,design=design,onDismiss={blockCatalogIndex=null},onApply={selected->onApplyBlockThread(blockIndex,selected)})
        }
    }

}'''
if old not in text: raise SystemExit('0.2.22 block catalog dialog marker not found')
text=text.replace(old,new,1)
text=text.replace('0.2.21','0.2.22')
path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.22 color sequence manager applied successfully')
