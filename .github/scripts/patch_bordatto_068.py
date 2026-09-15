from pathlib import Path
import re
import runpy

# Start from validated 0.2.37 UI/simulator.
runpy.run_path('.github/scripts/patch_bordatto_067.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

# 0.2.38 replaces only the Traditional lettering digitizer. Studio Pro keeps
# the existing professional engine. The new Traditional motor works by glyph,
# extracts a center skeleton, traces local stroke segments and for each segment
# sews: local edge underlay -> immediate satin -> next segment. This mirrors the
# reference behavior much better than the previous global-underlay-first order.
engine = r'''
private data class TraditionalPixel038(val x: Int, val y: Int)
private data class TraditionalRail038(
    val cx: Float,
    val cy: Float,
    val nx: Float,
    val ny: Float,
    val plus: Float,
    val minus: Float
)

private val TraditionalNeighbors038 = arrayOf(
    intArrayOf(0, -1), intArrayOf(1, -1), intArrayOf(1, 0), intArrayOf(1, 1),
    intArrayOf(0, 1), intArrayOf(-1, 1), intArrayOf(-1, 0), intArrayOf(-1, -1)
)

private fun thinTraditionalMask038(source: Array<BooleanArray>): Array<BooleanArray> {
    if (source.size < 3 || source[0].size < 3) return source
    val h = source.size
    val w = source[0].size
    val mask = Array(h) { y -> source[y].clone() }

    fun n(x: Int, y: Int, dx: Int, dy: Int): Boolean = mask[y + dy][x + dx]
    fun countNeighbors(x: Int, y: Int): Int {
        var count = 0
        TraditionalNeighbors038.forEach { d -> if (n(x, y, d[0], d[1])) count++ }
        return count
    }
    fun transitions(x: Int, y: Int): Int {
        val p = BooleanArray(8)
        for (i in 0 until 8) {
            val d = TraditionalNeighbors038[i]
            p[i] = n(x, y, d[0], d[1])
        }
        var t = 0
        for (i in 0 until 8) if (!p[i] && p[(i + 1) % 8]) t++
        return t
    }

    var changed = true
    var iteration = 0
    val remove = ArrayList<TraditionalPixel038>()
    while (changed && iteration < 96) {
        changed = false
        remove.clear()
        for (y in 1 until h - 1) for (x in 1 until w - 1) {
            if (!mask[y][x]) continue
            val b = countNeighbors(x, y)
            if (b !in 2..6 || transitions(x, y) != 1) continue
            val p2 = n(x, y, 0, -1); val p4 = n(x, y, 1, 0)
            val p6 = n(x, y, 0, 1); val p8 = n(x, y, -1, 0)
            if (!(p2 && p4 && p6) && !(p4 && p6 && p8)) remove += TraditionalPixel038(x, y)
        }
        if (remove.isNotEmpty()) {
            changed = true
            remove.forEach { mask[it.y][it.x] = false }
        }

        remove.clear()
        for (y in 1 until h - 1) for (x in 1 until w - 1) {
            if (!mask[y][x]) continue
            val b = countNeighbors(x, y)
            if (b !in 2..6 || transitions(x, y) != 1) continue
            val p2 = n(x, y, 0, -1); val p4 = n(x, y, 1, 0)
            val p6 = n(x, y, 0, 1); val p8 = n(x, y, -1, 0)
            if (!(p2 && p4 && p8) && !(p2 && p6 && p8)) remove += TraditionalPixel038(x, y)
        }
        if (remove.isNotEmpty()) {
            changed = true
            remove.forEach { mask[it.y][it.x] = false }
        }
        iteration++
    }
    return mask
}

private fun traceTraditionalSkeleton038(skeleton: Array<BooleanArray>): List<List<TraditionalPixel038>> {
    val h = skeleton.size
    val w = if (h > 0) skeleton[0].size else 0
    if (w == 0) return emptyList()

    fun key(x: Int, y: Int) = y * w + x
    fun px(k: Int) = TraditionalPixel038(k % w, k / w)
    fun neighbors(k: Int): List<Int> {
        val p = px(k)
        val out = ArrayList<Int>(8)
        TraditionalNeighbors038.forEach { d ->
            val xx = p.x + d[0]; val yy = p.y + d[1]
            if (xx in 0 until w && yy in 0 until h && skeleton[yy][xx]) out += key(xx, yy)
        }
        return out
    }
    fun edgeKey(a: Int, b: Int): Long {
        val lo = minOf(a, b).toLong() and 0xffffffffL
        val hi = maxOf(a, b).toLong() and 0xffffffffL
        return (lo shl 32) or hi
    }

    val points = ArrayList<Int>()
    for (y in 0 until h) for (x in 0 until w) if (skeleton[y][x]) points += key(x, y)
    if (points.isEmpty()) return emptyList()
    val nodeSet = points.filter { neighbors(it).size != 2 }.toHashSet()
    val visited = HashSet<Long>()
    val result = ArrayList<List<TraditionalPixel038>>()

    fun chooseNext(prev: Int, cur: Int, candidates: List<Int>): Int {
        if (candidates.size == 1) return candidates[0]
        val a = px(prev); val b = px(cur)
        val vx = (b.x - a.x).toFloat(); val vy = (b.y - a.y).toFloat()
        val vl = kotlin.math.sqrt(vx * vx + vy * vy).coerceAtLeast(.001f)
        return candidates.maxByOrNull { k ->
            val c = px(k)
            val wx = (c.x - b.x).toFloat(); val wy = (c.y - b.y).toFloat()
            val wl = kotlin.math.sqrt(wx * wx + wy * wy).coerceAtLeast(.001f)
            (vx * wx + vy * wy) / (vl * wl)
        } ?: candidates[0]
    }

    val starts = if (nodeSet.isNotEmpty()) nodeSet.sortedWith(compareBy({ px(it).x }, { px(it).y })) else points.sorted()
    for (start in starts) {
        for (nb in neighbors(start)) {
            if (edgeKey(start, nb) in visited) continue
            val path = ArrayList<TraditionalPixel038>()
            path += px(start)
            var prev = start
            var cur = nb
            visited += edgeKey(prev, cur)
            var guard = 0
            while (guard++ < points.size * 2) {
                path += px(cur)
                if (cur != start && cur in nodeSet) break
                val candidates = neighbors(cur).filter { it != prev && edgeKey(cur, it) !in visited }
                if (candidates.isEmpty()) break
                val next = chooseNext(prev, cur, candidates)
                visited += edgeKey(cur, next)
                prev = cur
                cur = next
                if (cur == start) { path += px(cur); break }
            }
            if (path.size >= 4) result += path
        }
    }

    // Closed loops (o, a, etc.) can have no graph nodes. Trace remaining edges.
    for (start in points.sortedWith(compareBy({ px(it).x }, { px(it).y }))) {
        val first = neighbors(start).firstOrNull { edgeKey(start, it) !in visited } ?: continue
        val path = ArrayList<TraditionalPixel038>()
        path += px(start)
        var prev = start
        var cur = first
        visited += edgeKey(prev, cur)
        var guard = 0
        while (guard++ < points.size * 2) {
            path += px(cur)
            val candidates = neighbors(cur).filter { it != prev && edgeKey(cur, it) !in visited }
            if (candidates.isEmpty()) break
            val next = chooseNext(prev, cur, candidates)
            visited += edgeKey(cur, next)
            prev = cur
            cur = next
            if (cur == start) { path += px(cur); break }
        }
        if (path.size >= 4) result += path
    }

    return result
}

private fun resampleTraditionalPath038(path: List<TraditionalPixel038>, stepPx: Float): List<TraditionalPixel038> {
    if (path.size <= 2) return path
    val out = ArrayList<TraditionalPixel038>()
    out += path.first()
    var accumulated = 0f
    var last = path.first()
    for (i in 1 until path.size) {
        val p = path[i]
        val dx = (p.x - last.x).toFloat(); val dy = (p.y - last.y).toFloat()
        accumulated += kotlin.math.sqrt(dx * dx + dy * dy)
        if (accumulated >= stepPx) {
            out += p
            accumulated = 0f
        }
        last = p
    }
    if (out.last() != path.last()) out += path.last()
    return out
}

private fun generateTraditionalReferenceLettering038(rawText: String, options: LetteringOptions): Design {
    val clean = rawText.trim().replace(Regex("\\s+"), " ").take(28)
    require(clean.isNotBlank()) { "Digite um nome ou texto para gerar a matriz." }

    val pxPerMm = 4.6f
    val paint = android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG).apply {
        color = android.graphics.Color.WHITE
        style = android.graphics.Paint.Style.FILL
        textSize = options.heightMm.coerceIn(8f, 120f) * pxPerMm
        typeface = letteringTypeface(options.fontStyle)
        isSubpixelText = true
    }
    val fm = paint.fontMetrics
    val lineHeight = (fm.bottom - fm.top).coerceAtLeast(paint.textSize)
    val margin = (2.8f * pxPerMm).coerceAtLeast(10f)
    val spacingFactor = (1f + options.spacingPercent / 100f).coerceIn(.78f, 1.55f)
    val densityPx = (options.densityMm.coerceIn(.28f, .9f) * pxPerMm).coerceAtLeast(1.35f)
    val pullPx = options.pullCompensationMm.coerceIn(0f, 1.0f) * pxPerMm
    val stitches = ArrayList<StitchPoint>()
    var cursorPx = 0f
    var lastGlobal: Pair<Float, Float>? = null

    fun addMm(xPx: Float, yPx: Float, command: StitchCommand) {
        stitches += StitchPoint(xPx / pxPerMm, yPx / pxPerMm, command, 0)
        if (command == StitchCommand.STITCH) lastGlobal = xPx to yPx
    }
    fun startTrack(xPx: Float, yPx: Float) {
        addMm(xPx, yPx, StitchCommand.JUMP)
        addMm(xPx, yPx, StitchCommand.STITCH)
    }

    clean.forEach { ch ->
        val token = ch.toString()
        val advance = paint.measureText(token).coerceAtLeast(paint.textSize * .18f) * spacingFactor
        if (ch == ' ') {
            cursorPx += advance
            return@forEach
        }

        val glyphWidth = kotlin.math.ceil(paint.measureText(token) + margin * 2f).toInt().coerceIn(24, 900)
        val glyphHeight = kotlin.math.ceil(lineHeight + margin * 2f).toInt().coerceIn(32, 900)
        val bitmap = android.graphics.Bitmap.createBitmap(glyphWidth, glyphHeight, android.graphics.Bitmap.Config.ARGB_8888)
        val canvas = android.graphics.Canvas(bitmap)
        val baseline = margin - fm.top
        canvas.drawText(token, margin, baseline, paint)
        val pixels = IntArray(glyphWidth * glyphHeight)
        bitmap.getPixels(pixels, 0, glyphWidth, 0, 0, glyphWidth, glyphHeight)
        bitmap.recycle()

        val mask = Array(glyphHeight) { BooleanArray(glyphWidth) }
        var minMaskX = glyphWidth; var maxMaskX = -1; var minMaskY = glyphHeight; var maxMaskY = -1
        for (y in 0 until glyphHeight) for (x in 0 until glyphWidth) {
            val on = android.graphics.Color.alpha(pixels[y * glyphWidth + x]) > 48
            mask[y][x] = on
            if (on) {
                if (x < minMaskX) minMaskX = x; if (x > maxMaskX) maxMaskX = x
                if (y < minMaskY) minMaskY = y; if (y > maxMaskY) maxMaskY = y
            }
        }
        if (maxMaskX < 0) {
            cursorPx += advance
            return@forEach
        }

        val skeleton = thinTraditionalMask038(mask)
        var segments = traceTraditionalSkeleton038(skeleton)
            .filter { it.size >= 4 }
            .sortedWith(compareBy<List<TraditionalPixel038>>(
                { it.map { p -> p.x }.average() },
                { -it.size.toDouble() }
            ))

        if (segments.isEmpty()) {
            cursorPx += advance
            return@forEach
        }

        var previousEnd: TraditionalPixel038? = null
        segments.forEachIndexed { index, rawSegment ->
            var segment = rawSegment
            val first = segment.first(); val last = segment.last()
            val mostlyVertical = kotlin.math.abs(last.y - first.y) > kotlin.math.abs(last.x - first.x)
            if (index == 0) {
                // Match the reference start: left-most vertical stroke runs from
                // its lower edge toward the top before Satin comes back down.
                if (mostlyVertical && first.y < last.y) segment = segment.asReversed()
                else if (!mostlyVertical && first.x > last.x) segment = segment.asReversed()
            } else if (previousEnd != null) {
                val p = previousEnd!!
                fun dist2(q: TraditionalPixel038): Int {
                    val dx = p.x - q.x; val dy = p.y - q.y
                    return dx * dx + dy * dy
                }
                if (dist2(segment.last()) < dist2(segment.first())) segment = segment.asReversed()
            }

            val sampled = resampleTraditionalPath038(segment, densityPx)
            if (sampled.size < 2) return@forEachIndexed
            val rails = ArrayList<TraditionalRail038>()
            var previousNormal: Pair<Float, Float>? = null

            fun inside(x: Float, y: Float): Boolean {
                val xx = kotlin.math.round(x).toInt(); val yy = kotlin.math.round(y).toInt()
                return xx in 0 until glyphWidth && yy in 0 until glyphHeight && mask[yy][xx]
            }
            fun ray(cx: Float, cy: Float, nx: Float, ny: Float, sign: Float): Float {
                var d = .45f
                var lastInside = 0f
                val maxD = maxOf(glyphWidth, glyphHeight).toFloat()
                while (d < maxD) {
                    if (!inside(cx + nx * d * sign, cy + ny * d * sign)) break
                    lastInside = d
                    d += .55f
                }
                return lastInside
            }

            for (i in sampled.indices) {
                val prev = sampled[(i - 1).coerceAtLeast(0)]
                val next = sampled[(i + 1).coerceAtMost(sampled.lastIndex)]
                var tx = (next.x - prev.x).toFloat(); var ty = (next.y - prev.y).toFloat()
                val tl = kotlin.math.sqrt(tx * tx + ty * ty).coerceAtLeast(.001f)
                tx /= tl; ty /= tl
                var nx = -ty; var ny = tx
                previousNormal?.let { old ->
                    if (old.first * nx + old.second * ny < 0f) { nx = -nx; ny = -ny }
                }
                previousNormal = nx to ny
                val plus = ray(sampled[i].x.toFloat(), sampled[i].y.toFloat(), nx, ny, 1f)
                val minus = ray(sampled[i].x.toFloat(), sampled[i].y.toFloat(), nx, ny, -1f)
                if (plus + minus >= 2.2f) rails += TraditionalRail038(sampled[i].x.toFloat(), sampled[i].y.toFloat(), nx, ny, plus, minus)
            }
            if (rails.size < 2) return@forEachIndexed

            val firstRail = rails.first()
            val plusX = firstRail.cx + firstRail.nx * firstRail.plus * .66f
            val minusX = firstRail.cx - firstRail.nx * firstRail.minus * .66f
            val underlayPlus = plusX < minusX
            val underlayStep = maxOf(2, (1.8f / options.densityMm.coerceAtLeast(.28f)).toInt())
            var underlayStarted = false
            rails.forEachIndexed { ri, r ->
                if (ri != 0 && ri != rails.lastIndex && ri % underlayStep != 0) return@forEachIndexed
                val d = if (underlayPlus) r.plus * .66f else -r.minus * .66f
                val lx = cursorPx + r.cx + r.nx * d
                val ly = r.cy + r.ny * d
                if (!underlayStarted) { startTrack(lx, ly); underlayStarted = true }
                else addMm(lx, ly, StitchCommand.STITCH)
            }

            // Satin immediately returns over the same local stroke, instead of
            // running underlay over the entire word first.
            var parity = false
            var satinStarted = false
            rails.asReversed().forEach { r ->
                val totalWidthMm = (r.plus + r.minus) / pxPerMm
                val maxAllowed = maxOf(options.satinMaxWidthMm, 12f)
                val clampScale = if (totalWidthMm > maxAllowed) maxAllowed / totalWidthMm else 1f
                val plusD = r.plus * clampScale + pullPx
                val minusD = r.minus * clampScale + pullPx
                val d = if (parity) plusD else -minusD
                val sx = cursorPx + r.cx + r.nx * d
                val sy = r.cy + r.ny * d
                if (!satinStarted) { addMm(sx, sy, StitchCommand.STITCH); satinStarted = true }
                else addMm(sx, sy, StitchCommand.STITCH)
                parity = !parity
            }

            // Small lock at the end of each local object keeps the simulator and
            // exported matrix visually stable before the jump to the next stroke.
            stitches.lastOrNull { it.command == StitchCommand.STITCH }?.let { end ->
                val lock = .22f
                stitches += StitchPoint(end.x + lock, end.y, StitchCommand.STITCH, 0)
                stitches += StitchPoint(end.x, end.y + lock, StitchCommand.STITCH, 0)
                stitches += StitchPoint(end.x, end.y, StitchCommand.STITCH, 0)
            }
            previousEnd = segment.last()
        }
        cursorPx += advance
    }

    require(stitches.count { it.command == StitchCommand.STITCH } >= 8) { "Não foi possível gerar pontadas suficientes para este nome." }
    val last = stitches.lastOrNull { it.command == StitchCommand.STITCH }!!
    stitches += StitchPoint(last.x, last.y, StitchCommand.END, 0)
    val sew = stitches.filter { it.command == StitchCommand.STITCH || it.command == StitchCommand.JUMP }
    val minX = sew.minOf { it.x }; val maxX = sew.maxOf { it.x }
    val minY = sew.minOf { it.y }; val maxY = sew.maxOf { it.y }
    val goldArgb = 0xFFE1B66F.toInt()
    return Design(
        name = "Lettering • $clean",
        stitches = stitches,
        minX = minX,
        minY = minY,
        maxX = maxX,
        maxY = maxY,
        colors = 1,
        format = "BORDATTO",
        threadColors = listOf(goldArgb),
        threadInfos = listOf(DesignThreadInfo(goldArgb, "Dourado BORDATTO", "BD-001", "BORDATTO", "Tradicional"))
    )
}
'''

insert_at = text.index('@Composable\nprivate fun LetteringDualModeScreen033')
text = text[:insert_at] + engine + '\n' + text[insert_at:]

# Route only the Traditional side of the dual-mode screen to the new engine.
start = text.index('@Composable\nprivate fun LetteringDualModeScreen033')
end = text.index('private data class TraditionalThread034', start)
block = text[start:end]
studio_marker = '    } else {\n        // Studio Pro is intentionally a separate professional experience.'
if studio_marker not in block:
    raise SystemExit('0.2.38 Studio Pro split anchor not found')
traditional, studio = block.split(studio_marker, 1)
count = traditional.count('generateLetteringDesign(name, options)')
if count != 2:
    raise SystemExit(f'0.2.38 expected 2 Traditional generator calls, found {count}')
traditional = traditional.replace('generateLetteringDesign(name, options)', 'generateTraditionalReferenceLettering038(name, options)')
block = traditional + studio_marker + studio
text = text[:start] + block + text[end:]

main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 40', gradle, count=1)
gradle = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "0.2.38"', gradle, count=1)
gradle_path.write_text(gradle, encoding='utf-8')

final = main_path.read_text(encoding='utf-8')
required = [
    'generateTraditionalReferenceLettering038(',
    'thinTraditionalMask038(',
    'traceTraditionalSkeleton038(',
    'Satin immediately returns over the same local stroke',
    'TraditionalSimulationCanvas037(',
    'Bordado concluído!',
]
for token in required:
    if token not in final:
        raise SystemExit('0.2.38 regression guard missing: ' + token)
if final.count('generateTraditionalReferenceLettering038(name, options)') != 2:
    raise SystemExit('0.2.38 Traditional routing guard failed')
# Studio Pro must still retain the original engine.
studio_slice = final[final.index('// Studio Pro is intentionally a separate professional experience.'):]
if 'generateLetteringDesign(name, options)' not in studio_slice:
    raise SystemExit('0.2.38 Studio Pro engine was accidentally replaced')
if 'versionCode = 40' not in gradle_path.read_text(encoding='utf-8') or 'versionName = "0.2.38"' not in gradle_path.read_text(encoding='utf-8'):
    raise SystemExit('0.2.38 version guard failed')

print('BORDATTO 0.2.38 stroke-aware Traditional motor applied successfully')
