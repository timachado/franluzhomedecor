from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_041.py', run_name='__main__')
path=Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text=path.read_text(encoding='utf-8')

old='''            onThreadColorChange = { index, newColor ->
                val count = maxOf(workingDesign.colors, index + 1)
                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }
                palette[index] = newColor
                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }
                infos[index] = infos[index].copy(color = newColor)
                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))
            }
        )'''
new='''            onThreadColorChange = { index, newColor ->
                val count = maxOf(workingDesign.colors, index + 1)
                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }
                palette[index] = newColor
                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }
                infos[index] = infos[index].copy(color = newColor)
                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))
            },
            onCatalogThreadApply = { index, selected ->
                val count = maxOf(workingDesign.colors, index + 1)
                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }
                palette[index] = selected.color
                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }
                infos[index] = selected
                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))
            }
        )'''
if old not in text: raise SystemExit('catalog callback marker not found')
text=text.replace(old,new,1)
text=text.replace(
'''    onShareLastExport: () -> Unit,
    onThreadColorChange: (Int, Int) -> Unit
) {''',
'''    onShareLastExport: () -> Unit,
    onThreadColorChange: (Int, Int) -> Unit,
    onCatalogThreadApply: (Int, DesignThreadInfo) -> Unit
) {''',1)
text=text.replace(
'            ThreadPalettePanel(design = working, onChangeColor = onThreadColorChange)',
'            ThreadPalettePanel(design = working, onChangeColor = onThreadColorChange, onApplyCatalogThread = onCatalogThreadApply)',1)

insert_at=text.index('class MainActivity')
core=r'''private data class ThreadCatalogEntry(val info:DesignThreadInfo,val source:String)

private val BuiltInThreadCatalog:List<ThreadCatalogEntry> by lazy {
    val brother=org.embroideryio.embroideryio.EmbThreadPec.getThreadSet().mapNotNull { t ->
        val name=t.getDescription().orEmpty(); val code=t.getCatalogNumber().orEmpty()
        if(code=="0" && name.equals("Unknown",true)) null else ThreadCatalogEntry(
            DesignThreadInfo(t.getColor(),name,code,"Brother","PEC"),"Brother / PEC")
    }
    val janome=org.embroideryio.embroideryio.EmbThreadJef.getThreadSet().mapNotNull { t ->
        val name=t.getDescription().orEmpty(); val code=t.getCatalogNumber().orEmpty()
        if(code=="0" && name.equals("Unknown",true)) null else ThreadCatalogEntry(
            DesignThreadInfo(t.getColor(),name,code,"Janome","JEF"),"Janome / JEF")
    }
    (brother+janome).distinctBy { "${it.info.brand}|${it.info.catalog}|${it.info.color}" }
}

private fun rgbCatalogDistance(a:Int,b:Int):Int {
    val ar=(a shr 16) and 255; val ag=(a shr 8) and 255; val ab=a and 255
    val br=(b shr 16) and 255; val bg=(b shr 8) and 255; val bb=b and 255
    val dr=ar-br; val dg=ag-bg; val db=ab-bb
    return kotlin.math.sqrt((dr*dr+dg*dg+db*db).toDouble()).toInt()
}

private fun rgbCatalogQuality(distance:Int):String=when {
    distance<=12 -> "Muito próxima"
    distance<=30 -> "Próxima"
    distance<=60 -> "Aproximação aceitável"
    else -> "Diferença visível"
}

private fun catalogSearchResults(query:String,brand:String,currentColor:Int):List<ThreadCatalogEntry>{
    val q=query.trim().lowercase()
    val filtered=BuiltInThreadCatalog.filter { e ->
        (brand=="Todos" || e.info.brand==brand) && if(q.isBlank()) true else {
            val i=e.info; val hex=formatThreadHex(i.color).lowercase()
            i.name.lowercase().contains(q) || i.catalog.lowercase().contains(q) ||
            i.brand.lowercase().contains(q) || i.chart.lowercase().contains(q) ||
            hex.contains(q) || hex.removePrefix("#").contains(q.removePrefix("#"))
        }
    }
    return if(q.isBlank()) filtered.sortedBy { rgbCatalogDistance(currentColor,it.info.color) }
    else filtered.sortedWith(compareBy<ThreadCatalogEntry> {
        when {
            it.info.catalog.equals(query.trim(),true)->0
            it.info.name.equals(query.trim(),true)->1
            else->2
        }
    }.thenBy { rgbCatalogDistance(currentColor,it.info.color) })
}

'''
text=text[:insert_at]+core+text[insert_at:]
path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.21 thread catalog core applied')
