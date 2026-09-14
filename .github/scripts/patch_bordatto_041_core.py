from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_040.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

text = text.replace(
'''private data class Design(\n''',
'''private data class DesignThreadInfo(\n    val color: Int,\n    val name: String = "",\n    val catalog: String = "",\n    val brand: String = "",\n    val chart: String = ""\n)\n\nprivate data class Design(\n''', 1)
text = text.replace(
'''    val colors: Int,\n    val format: String = "DST",\n    val threadColors: List<Int> = emptyList()\n) {''',
'''    val colors: Int,\n    val format: String = "DST",\n    val threadColors: List<Int> = emptyList(),\n    val threadInfos: List<DesignThreadInfo> = emptyList()\n) {''', 1)

old = '''    val nativeThreadColors = pattern.getThreadlist()\n        .map { it.getColor() }\n        .take(actualColors)\n    return Design(parsedName, pts, minX, minY, maxX, maxY, actualColors, extension, nativeThreadColors)\n}'''
new = '''    val nativeThreads = pattern.getThreadlist().take(actualColors)\n    val nativeThreadColors = nativeThreads.map { it.getColor() }\n    val nativeThreadInfos = nativeThreads.map { thread ->\n        DesignThreadInfo(\n            color = thread.getColor(),\n            name = thread.getDescription().orEmpty(),\n            catalog = thread.getCatalogNumber().orEmpty(),\n            brand = thread.getBrand().orEmpty(),\n            chart = thread.getChart().orEmpty()\n        )\n    }\n    return Design(parsedName, pts, minX, minY, maxX, maxY, actualColors, extension, nativeThreadColors, nativeThreadInfos)\n}'''
if old not in text: raise SystemExit('parser thread marker not found')
text = text.replace(old, new, 1)

text = text.replace('private const val PROJECT_BINARY_VERSION = 2', 'private const val PROJECT_BINARY_VERSION = 3', 1)
old = '''        out.writeInt(design.threadColors.size.coerceAtMost(256))\n        design.threadColors.take(256).forEach { out.writeInt(it) }\n        out.writeFloat(design.minX)'''
new = '''        out.writeInt(design.threadColors.size.coerceAtMost(256))\n        design.threadColors.take(256).forEach { out.writeInt(it) }\n        out.writeInt(design.threadInfos.size.coerceAtMost(256))\n        design.threadInfos.take(256).forEach { info ->\n            out.writeInt(info.color)\n            out.writeUTF(info.name.take(1024))\n            out.writeUTF(info.catalog.take(512))\n            out.writeUTF(info.brand.take(512))\n            out.writeUTF(info.chart.take(512))\n        }\n        out.writeFloat(design.minX)'''
if old not in text: raise SystemExit('project writer marker not found')
text = text.replace(old, new, 1)
old = '''        val threadColors = if (projectVersion >= 2) {\n            val threadCount = input.readInt()\n            require(threadCount in 0..256) { "Paleta interna do projeto inválida." }\n            List(threadCount) { input.readInt() }\n        } else emptyList()\n        val minX = input.readFloat()'''
new = '''        val threadColors = if (projectVersion >= 2) {\n            val threadCount = input.readInt()\n            require(threadCount in 0..256) { "Paleta interna do projeto inválida." }\n            List(threadCount) { input.readInt() }\n        } else emptyList()\n        val threadInfos = if (projectVersion >= 3) {\n            val infoCount = input.readInt()\n            require(infoCount in 0..256) { "Metadados internos de linha inválidos." }\n            List(infoCount) {\n                DesignThreadInfo(input.readInt(), input.readUTF(), input.readUTF(), input.readUTF(), input.readUTF())\n            }\n        } else threadColors.map { DesignThreadInfo(color = it) }\n        val minX = input.readFloat()'''
if old not in text: raise SystemExit('project reader marker not found')
text = text.replace(old, new, 1)
text = text.replace(
'        Design(name, stitches, minX, minY, maxX, maxY, colors, format, threadColors)',
'        Design(name, stitches, minX, minY, maxX, maxY, colors, format, threadColors, threadInfos)', 1)

old = '''    val threadCount = maxOf(1, design.colors)\n    val palette = design.threadColors.takeIf { it.isNotEmpty() } ?: ExportFallbackThreadColors\n    repeat(threadCount) { index ->\n        val color = palette[index % palette.size]\n        pattern.addThread(\n            org.embroideryio.embroideryio.EmbThread(\n                color,\n                "BORDATTO ${index + 1}",\n                "${index + 1}"\n            )\n        )\n    }'''
new = '''    val threadCount = maxOf(1, design.colors)\n    repeat(threadCount) { index ->\n        val info = design.threadInfos.getOrNull(index)\n        val color = info?.color ?: design.threadColors.getOrNull(index) ?: ExportFallbackThreadColors[index % ExportFallbackThreadColors.size]\n        val thread = org.embroideryio.embroideryio.EmbThread(\n            color,\n            info?.name?.takeIf { it.isNotBlank() } ?: "BORDATTO ${index + 1}",\n            info?.catalog?.takeIf { it.isNotBlank() } ?: "${index + 1}"\n        )\n        info?.brand?.takeIf { it.isNotBlank() }?.let { thread.setBrand(it) }\n        info?.chart?.takeIf { it.isNotBlank() }?.let { thread.setChart(it) }\n        pattern.addThread(thread)\n    }'''
if old not in text: raise SystemExit('export thread block not found')
text = text.replace(old, new, 1)
text = text.replace(
'''        val snapshot = workingDesign.copy(stitches = workingDesign.stitches.toList(), threadColors = workingDesign.threadColors.toList())''',
'''        val snapshot = workingDesign.copy(\n            stitches = workingDesign.stitches.toList(),\n            threadColors = workingDesign.threadColors.toList(),\n            threadInfos = workingDesign.threadInfos.toList()\n        )''', 1)

insert_at = text.index('class MainActivity')
core = r'''private data class ThreadColorStat(val index:Int,val color:Int,val stitchCount:Int,val percent:Float,val estimatedMeters:Float,val blockCount:Int,val info:DesignThreadInfo?)
private data class ThreadBlockStat(val sequence:Int,val colorIndex:Int,val stitchCount:Int)
private data class JefThreadMatch(val paletteIndex:Int,val color:Int,val name:String,val catalog:String,val exactRgb:Boolean)

private fun effectiveThreadColor(design: Design, index: Int): Int =
    design.threadInfos.getOrNull(index)?.color ?: design.threadColors.getOrNull(index)
    ?: ExportFallbackThreadColors[index.mod(ExportFallbackThreadColors.size)]

private fun formatThreadHex(color:Int):String = "#%06X".format(color and 0xFFFFFF)
private fun parseThreadHex(value:String):Int? {
    val clean=value.trim().removePrefix("#").removePrefix("0x").removePrefix("0X")
    if(!clean.matches(Regex("[0-9A-Fa-f]{6}"))) return null
    return runCatching { 0xFF000000.toInt() or clean.toInt(16) }.getOrNull()
}
private fun nearestJefThread(color:Int):JefThreadMatch {
    val palette=org.embroideryio.embroideryio.EmbThreadJef.getThreadSet()
    val index=org.embroideryio.embroideryio.EmbThread.findNearestColorIndex(color,palette.asList()).coerceIn(0,palette.lastIndex)
    val t=palette[index]
    return JefThreadMatch(index,t.getColor(),t.getDescription().orEmpty(),t.getCatalogNumber().orEmpty(),(t.getColor() and 0xFFFFFF)==(color and 0xFFFFFF))
}
private fun calculateThreadBlocks(design:Design):List<ThreadBlockStat> {
    val out=mutableListOf<ThreadBlockStat>(); var current:Int?=null; var count=0
    fun flush(){ current?.let { if(count>0) out += ThreadBlockStat(out.size+1,it,count) } }
    design.stitches.forEach { s -> if(s.command==StitchCommand.STITCH){ val c=s.color.coerceAtLeast(0); if(current==null){current=c;count=1}else if(current==c) count++ else {flush();current=c;count=1} } }
    flush(); return out
}
private fun calculateThreadColorStats(design:Design):List<ThreadColorStat> {
    val count=maxOf(1,design.colors); val stitches=IntArray(count); val path=FloatArray(count); var prev:StitchPoint?=null
    design.stitches.forEach { s ->
        if(s.command==StitchCommand.STITCH){ val i=s.color.coerceIn(0,count-1); stitches[i]++; val p=prev; if(p!=null&&p.command==StitchCommand.STITCH&&p.color==s.color){ val dx=s.x-p.x; val dy=s.y-p.y; path[i]+=kotlin.math.sqrt(dx*dx+dy*dy) } }
        prev=s
    }
    val blockCounts=IntArray(count); calculateThreadBlocks(design).forEach { if(it.colorIndex in 0 until count) blockCounts[it.colorIndex]++ }
    val total=stitches.sum().coerceAtLeast(1)
    return List(count){ i -> ThreadColorStat(i,effectiveThreadColor(design,i),stitches[i],stitches[i]*100f/total,path[i]/1000f*1.12f,blockCounts[i],design.threadInfos.getOrNull(i)) }
}

'''
text = text[:insert_at] + core + text[insert_at:]

old = '''    val palette = listOf(Gold, Color(0xFFF1E3C6), Color(0xFFBE7C4D), Color(0xFFA96A5B), Color(0xFF7A9273), Color(0xFFE3C17A))\n    Canvas(modifier) {'''
new = '''    val palette = remember(design.threadColors, design.threadInfos, design.colors) {\n        List(maxOf(1, design.colors)) { index -> Color(effectiveThreadColor(design, index)) }\n    }\n    Canvas(modifier) {'''
if old not in text: raise SystemExit('canvas palette marker not found')
text = text.replace(old,new,1)

path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.20 thread metadata core applied')
