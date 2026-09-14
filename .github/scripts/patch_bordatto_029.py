from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_028.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Make format part of the common internal design model.
old = '''private data class Design(
    val name: String,
    val stitches: List<StitchPoint>,
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float,
    val colors: Int
) {'''
new = '''private data class Design(
    val name: String,
    val stitches: List<StitchPoint>,
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float,
    val colors: Int,
    val format: String = "DST"
) {'''
if old not in text: raise SystemExit('Design model not found')
text = text.replace(old, new, 1)

# Persist the originating embroidery format in the real local library.
old = '''private data class LibraryItem(
    val uri: String,
    val name: String,
    val widthMm: Float,
    val heightMm: Float,
    val stitchCount: Int,
    val colors: Int,
    val openedAt: Long,
    val favorite: Boolean = false
)'''
new = '''private data class LibraryItem(
    val uri: String,
    val name: String,
    val widthMm: Float,
    val heightMm: Float,
    val stitchCount: Int,
    val colors: Int,
    val format: String,
    val openedAt: Long,
    val favorite: Boolean = false
)'''
if old not in text: raise SystemExit('LibraryItem model not found')
text = text.replace(old, new, 1)

old = '''                        colors = o.optInt("colors", 0),
                        openedAt = o.optLong("opened", 0L),'''
new = '''                        colors = o.optInt("colors", 0),
                        format = o.optString("format", o.optString("name", "matriz.dst").substringAfterLast('.', "DST").uppercase()),
                        openedAt = o.optLong("opened", 0L),'''
if old not in text: raise SystemExit('Library load format marker not found')
text = text.replace(old, new, 1)

old = '''            put("colors", item.colors)
            put("opened", item.openedAt)'''
new = '''            put("colors", item.colors)
            put("format", item.format)
            put("opened", item.openedAt)'''
if old not in text: raise SystemExit('Library persist marker not found')
text = text.replace(old, new, 1)

# Accept only formats that are truly parsed in this build, then dispatch through the common model.
old = '''                if (!name.lowercase().endsWith(".dst")) error("Nesta versão 0.2.8, a leitura real implementada continua sendo DST. Os demais formatos entrarão conforme forem validados.")
                val bytes = resolver.openInputStream(uri)?.use { it.readBytes() } ?: error("Não foi possível ler o arquivo.")
                parseDst(name, bytes)'''
new = '''                val extension = name.substringAfterLast('.', "").lowercase()
                if (extension !in setOf("dst", "pes", "jef")) {
                    error("Formato .$extension ainda não está liberado nesta versão. Suporte real atual: DST, PES e JEF.")
                }
                val bytes = resolver.openInputStream(uri)?.use { it.readBytes() } ?: error("Não foi possível ler o arquivo.")
                parseEmbroidery(name, bytes)'''
if old not in text: raise SystemExit('old DST-only open block not found')
text = text.replace(old, new, 1)

old = '''                    stitchCount = openedDesign.stitchCount,
                    colors = openedDesign.colors,
                    openedAt = System.currentTimeMillis()'''
new = '''                    stitchCount = openedDesign.stitchCount,
                    colors = openedDesign.colors,
                    format = openedDesign.format,
                    openedAt = System.currentTimeMillis()'''
if old not in text: raise SystemExit('library upsert design marker not found')
text = text.replace(old, new, 1)

# Replace hard-coded DST format labels with the real originating format.
text = text.replace('Text("DST • ${design.stitchCount} pontos • ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm",', 'Text("${design.format} • ${design.stitchCount} pontos • ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm",')
text = text.replace('Text("DST", color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))', 'Text(design.format, color = Gold, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))')
text = text.replace('Text("DST", color = Gold, fontSize = 8.sp, modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp))', 'Text(item.format, color = Gold, fontSize = 8.sp, modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp))')

# Update user-facing copy now that all three formats feed the same viewer/check/cost pipeline.
text = text.replace('DST real nesta versão', 'DST, PES e JEF reais')
text = text.replace('Abrir matriz DST', 'Abrir Matriz')
text = text.replace('Visualizador real já funcional', 'DST, PES e JEF no mesmo visualizador')
text = text.replace('Abra um arquivo DST e ele aparecerá aqui automaticamente.', 'Abra uma matriz DST, PES ou JEF e ela aparecerá aqui automaticamente.')
text = text.replace('Abra uma matriz DST e acesse Custos pelo visualizador para preencher dados técnicos automaticamente.', 'Abra uma matriz DST, PES ou JEF e acesse Custos pelo visualizador para preencher os dados técnicos automaticamente.')
text = text.replace('Suporte real atual: DST.', 'Suporte real atual: DST, PES e JEF.')

# Common parser dispatcher. DST keeps the existing native Kotlin parser; PES/JEF use EmbroideryIO Android.
insert_at = text.index('private fun parseDst(fileName: String, bytes: ByteArray): Design')
multiformat = r'''private fun parseEmbroidery(fileName: String, bytes: ByteArray): Design {
    return when (fileName.substringAfterLast('.', "").lowercase()) {
        "dst" -> parseDst(fileName, bytes)
        "pes", "jef" -> parseWithEmbroideryIo(fileName, bytes)
        else -> error("Formato ainda não suportado pelo núcleo multiformato.")
    }
}

private fun parseWithEmbroideryIo(fileName: String, bytes: ByteArray): Design {
    val extension = fileName.substringAfterLast('.', "").uppercase()
    val pattern = java.io.ByteArrayInputStream(bytes).use { input ->
        org.embroideryio.embroideryio.EmbPattern.readStream(fileName, input)
    }
    require(pattern.size() > 0) { "Arquivo $extension inválido, vazio ou incompatível com o leitor atual." }

    val pts = ArrayList<StitchPoint>(pattern.size())
    var color = 0
    var minX = Float.POSITIVE_INFINITY
    var minY = Float.POSITIVE_INFINITY
    var maxX = Float.NEGATIVE_INFINITY
    var maxY = Float.NEGATIVE_INFINITY

    for (i in 0 until pattern.size()) {
        // EmbroideryIO follows pyembroidery's internal embroidery units: 10 units = 1 mm.
        val x = pattern.getX(i) / 10f
        val y = pattern.getY(i) / 10f
        minX = kotlin.math.min(minX, x)
        minY = kotlin.math.min(minY, y)
        maxX = kotlin.math.max(maxX, x)
        maxY = kotlin.math.max(maxY, y)

        val raw = pattern.getData(i)
        val cmd = raw and org.embroideryio.embroideryio.EmbConstant.COMMAND_MASK
        val command = when (cmd) {
            org.embroideryio.embroideryio.EmbConstant.STITCH -> StitchCommand.STITCH
            org.embroideryio.embroideryio.EmbConstant.JUMP,
            org.embroideryio.embroideryio.EmbConstant.TRIM -> StitchCommand.JUMP
            org.embroideryio.embroideryio.EmbConstant.COLOR_CHANGE,
            org.embroideryio.embroideryio.EmbConstant.NEEDLE_SET,
            org.embroideryio.embroideryio.EmbConstant.STOP -> StitchCommand.COLOR_CHANGE
            org.embroideryio.embroideryio.EmbConstant.END -> StitchCommand.END
            else -> StitchCommand.JUMP
        }
        if (command == StitchCommand.COLOR_CHANGE) color++
        pts += StitchPoint(x, y, command, color)
    }

    if (!minX.isFinite() || !minY.isFinite() || !maxX.isFinite() || !maxY.isFinite()) {
        error("Não foi possível obter as dimensões da matriz $extension.")
    }
    val parsedName = pattern.getName()?.takeIf { it.isNotBlank() } ?: fileName.substringBeforeLast('.')
    val actualColors = maxOf(1, color + 1)
    return Design(parsedName, pts, minX, minY, maxX, maxY, actualColors, extension)
}

'''
text = text[:insert_at] + multiformat + text[insert_at:]

# Make DST explicit in the common model.
old = 'return Design(label, pts, minX/10f,minY/10f,maxX/10f,maxY/10f,color+1)'
new = 'return Design(label, pts, minX/10f,minY/10f,maxX/10f,maxY/10f,color+1, "DST")'
if old not in text: raise SystemExit('DST return model not found')
text = text.replace(old, new, 1)

text = text.replace('0.2.8', '0.2.9')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.9 real DST/PES/JEF multi-format patch applied successfully')
