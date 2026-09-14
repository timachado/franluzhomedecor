from pathlib import Path
import runpy
import re

runpy.run_path('.github/scripts/patch_bordatto_035.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# Editor v1 introduces an internal trim command. It exists only in the in-memory working copy in this release.
old = 'private enum class StitchCommand { STITCH, JUMP, COLOR_CHANGE, END }'
new = 'private enum class StitchCommand { STITCH, JUMP, COLOR_CHANGE, TRIM, END }'
if old not in text:
    raise SystemExit('StitchCommand marker not found')
text = text.replace(old, new, 1)

# Real, reversible edits applied to a working Design copy only.
marker = '''private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
helpers = r'''private fun sameEditorPoint(x1: Float, y1: Float, x2: Float?, y2: Float?): Boolean {
    if (x2 == null || y2 == null) return false
    return kotlin.math.abs(x1 - x2) < 0.02f && kotlin.math.abs(y1 - y2) < 0.02f
}

private fun applyCorrectionToWorkingCopy(design: Design, marker: DiagnosticMarker): Design? {
    val stitches = design.stitches
    if (stitches.size < 2) return null

    return when (marker.kind) {
        DiagnosticKind.LONG_STITCH -> {
            val index = (1 until stitches.size).firstOrNull { i ->
                val prev = stitches[i - 1]
                val cur = stitches[i]
                prev.command == StitchCommand.STITCH &&
                    cur.command == StitchCommand.STITCH &&
                    prev.color == cur.color &&
                    sameEditorPoint(prev.x, prev.y, marker.startX, marker.startY) &&
                    sameEditorPoint(cur.x, cur.y, marker.endX, marker.endY)
            } ?: return null

            val prev = stitches[index - 1]
            val cur = stitches[index]
            val distance = kotlin.math.hypot((cur.x - prev.x).toDouble(), (cur.y - prev.y).toDouble())
            val segments = kotlin.math.ceil(distance / 8.0).toInt().coerceAtLeast(2)
            val inserted = (1 until segments).map { part ->
                val t = part.toFloat() / segments.toFloat()
                StitchPoint(
                    x = prev.x + (cur.x - prev.x) * t,
                    y = prev.y + (cur.y - prev.y) * t,
                    command = StitchCommand.STITCH,
                    color = cur.color
                )
            }
            val next = buildList {
                addAll(stitches.subList(0, index))
                addAll(inserted)
                addAll(stitches.subList(index, stitches.size))
            }
            design.copy(stitches = next)
        }

        DiagnosticKind.LONG_JUMP -> {
            val index = (1 until stitches.size).firstOrNull { i ->
                val prev = stitches[i - 1]
                val cur = stitches[i]
                cur.command == StitchCommand.JUMP &&
                    prev.command != StitchCommand.TRIM &&
                    sameEditorPoint(prev.x, prev.y, marker.startX, marker.startY) &&
                    sameEditorPoint(cur.x, cur.y, marker.endX, marker.endY)
            } ?: return null

            val prev = stitches[index - 1]
            val next = buildList {
                addAll(stitches.subList(0, index))
                add(StitchPoint(prev.x, prev.y, StitchCommand.TRIM, prev.color))
                addAll(stitches.subList(index, stitches.size))
            }
            design.copy(stitches = next)
        }

        DiagnosticKind.DENSE_AREA -> null
    }
}

private data class AnalysisIssue(
    val title: String,
    val detail: String,
    val severity: Int
)
'''
if marker not in text:
    raise SystemExit('AnalysisIssue marker for safe editor helpers not found')
text = text.replace(marker, helpers, 1)

# A trim directly before a jump is considered an assisted fix, so Analyzer no longer reports that jump as untrimmed.
old = 'if (current.command == StitchCommand.JUMP && distance > 12.0) {'
new = 'if (current.command == StitchCommand.JUMP && prev.command != StitchCommand.TRIM && distance > 12.0) {'
if old not in text:
    raise SystemExit('visual long jump analyzer marker not found')
text = text.replace(old, new, 1)

old = '''            if (current.command == StitchCommand.JUMP) {
                maxJumpMm = maxOf(maxJumpMm, distance)
                if (distance > 12.0) longJumpCount++
            }'''
new = '''            if (current.command == StitchCommand.JUMP && prev.command != StitchCommand.TRIM) {
                maxJumpMm = maxOf(maxJumpMm, distance)
                if (distance > 12.0) longJumpCount++
            }'''
if old not in text:
    raise SystemExit('design long jump analyzer marker not found')
text = text.replace(old, new, 1)

# Account for in-memory trim commands in machine-time estimation.
old = '''    val jumpOverhead = (design.jumpCount * 0.08) / 60.0
    val colorOverhead = (design.colorChanges * 8.0) / 60.0
    return maxOf(0.5, sewing + jumpOverhead + colorOverhead + 0.25)'''
new = '''    val jumpOverhead = (design.jumpCount * 0.08) / 60.0
    val colorOverhead = (design.colorChanges * 8.0) / 60.0
    val trimCount = design.stitches.count { it.command == StitchCommand.TRIM }
    val trimOverhead = (trimCount * 2.0) / 60.0
    return maxOf(0.5, sewing + jumpOverhead + colorOverhead + trimOverhead + 0.25)'''
if old not in text:
    raise SystemExit('machine estimate marker not found')
text = text.replace(old, new, 1)

# Make the entire open-matrix viewer operate on a working copy, while preserving the original parameter.
start = text.index('@Composable\nprivate fun ViewerScreen(')
end = text.index('private enum class DiagnosticKind', start)
viewer = text[start:end]
viewer = re.sub(r'\bdesign\b', 'workingDesign', viewer)
viewer = viewer.replace('private fun ViewerScreen(workingDesign: Design', 'private fun ViewerScreen(design: Design', 1)

state_marker = '''    BackHandler(onBack = onBack)
'''
state_addition = '''    BackHandler(onBack = onBack)
    var workingDesign by remember(design) { mutableStateOf(design.copy(stitches = design.stitches.toList())) }
    var undoStack by remember(design) { mutableStateOf<List<Design>>(emptyList()) }
    var redoStack by remember(design) { mutableStateOf<List<Design>>(emptyList()) }

    fun commitWorkingEdit(next: Design) {
        if (next == workingDesign) return
        undoStack = (undoStack + workingDesign).takeLast(20)
        workingDesign = next
        redoStack = emptyList()
    }

    fun applySelectedCorrection(marker: DiagnosticMarker) {
        val next = applyCorrectionToWorkingCopy(workingDesign, marker) ?: return
        commitWorkingEdit(next)
    }
'''
if state_marker not in viewer:
    raise SystemExit('viewer BackHandler marker not found')
viewer = viewer.replace(state_marker, state_addition, 1)

# Apply button from the correction assistant now commits to the working copy.
old = '''                onSuggest = {
                    assistedPreview = buildAssistedCorrectionPreview(marker)
                    diagnosticsVisible = true
                    simulatorPlaying = false
                    simulatorPosition = stitchIndices.size
                    focusMarker = marker
                    zoom = 3.2f
                    pan = Offset.Zero
                },
                onClearPreview = { assistedPreview = null },'''
new = '''                onSuggest = {
                    assistedPreview = buildAssistedCorrectionPreview(marker)
                    diagnosticsVisible = true
                    simulatorPlaying = false
                    simulatorPosition = stitchIndices.size
                    focusMarker = marker
                    zoom = 3.2f
                    pan = Offset.Zero
                },
                onApply = {
                    applySelectedCorrection(marker)
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                },
                onClearPreview = { assistedPreview = null },'''
if old not in viewer:
    raise SystemExit('AssistedCorrectionPanel viewer call marker not found')
viewer = viewer.replace(old, new, 1)

# Add the Safe Editor status/undo toolbar before the canvas.
canvas_marker = '''        Box(
            Modifier.weight(1f).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'''
editor_call = '''        SafeEditorPanel(
            original = design,
            working = workingDesign,
            canUndo = undoStack.isNotEmpty(),
            canRedo = redoStack.isNotEmpty(),
            onUndo = {
                undoStack.lastOrNull()?.let { previous ->
                    redoStack = (redoStack + workingDesign).takeLast(20)
                    workingDesign = previous
                    undoStack = undoStack.dropLast(1)
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                }
            },
            onRedo = {
                redoStack.lastOrNull()?.let { next ->
                    undoStack = (undoStack + workingDesign).takeLast(20)
                    workingDesign = next
                    redoStack = redoStack.dropLast(1)
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                }
            },
            onReset = {
                if (workingDesign != design) {
                    commitWorkingEdit(design.copy(stitches = design.stitches.toList()))
                    selectedDiagnostic = null
                    assistedPreview = null
                    focusMarker = null
                    simulatorPlaying = false
                }
            }
        )
        Box(
            Modifier.weight(1f).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'''
if canvas_marker not in viewer:
    raise SystemExit('viewer canvas marker for SafeEditorPanel not found')
viewer = viewer.replace(canvas_marker, editor_call, 1)

text = text[:start] + viewer + text[end:]

# Add an apply callback to the assisted correction panel.
old = '''    onIgnore: () -> Unit,
    onSuggest: () -> Unit,
    onClearPreview: () -> Unit,'''
new = '''    onIgnore: () -> Unit,
    onSuggest: () -> Unit,
    onApply: () -> Unit,
    onClearPreview: () -> Unit,'''
if old not in text:
    raise SystemExit('AssistedCorrectionPanel signature marker not found')
text = text.replace(old, new, 1)

# A real edit can only be committed after the user has inspected a preview.
old = '''                        Text(preview.detail, color = Cream, fontSize = 9.sp, lineHeight = 12.sp)
                        TextButton(onClick = onClearPreview, contentPadding = PaddingValues(0.dp)) {
                            Text("Limpar prévia", color = Gold, fontSize = 9.sp)
                        }'''
new = '''                        Text(preview.detail, color = Cream, fontSize = 9.sp, lineHeight = 12.sp)
                        Button(
                            onClick = onApply,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(15.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)
                        ) {
                            Icon(Icons.Rounded.DoneAll, null, modifier = Modifier.size(17.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Aplicar à cópia de trabalho", fontSize = 9.sp, fontWeight = FontWeight.Bold)
                        }
                        TextButton(onClick = onClearPreview, contentPadding = PaddingValues(0.dp)) {
                            Text("Limpar prévia", color = Gold, fontSize = 9.sp)
                        }'''
if old not in text:
    raise SystemExit('assisted preview block marker not found')
text = text.replace(old, new, 1)

# Update the disclaimer: applying now edits only the reversible in-memory working copy.
old = '"Nenhuma opção desta tela grava mudanças na matriz. O editor destrutivo e a exportação corrigida serão etapas posteriores."'
new = '"Aplicar modifica somente a cópia de trabalho em memória. O arquivo original permanece intacto e ainda não há exportação de matriz modificada nesta versão."'
if old not in text:
    raise SystemExit('assisted correction disclaimer marker not found')
text = text.replace(old, new, 1)

# Safe Editor Material 3 Expressive toolbar.
insert_at = text.index('@Composable\nprivate fun AssistedCorrectionPanel')
safe_editor_ui = r'''@Composable
private fun SafeEditorPanel(
    original: Design,
    working: Design,
    canUndo: Boolean,
    canRedo: Boolean,
    onUndo: () -> Unit,
    onRedo: () -> Unit,
    onReset: () -> Unit
) {
    val changed = working != original
    val trimCount = working.stitches.count { it.command == StitchCommand.TRIM }
    val addedStitches = (working.stitchCount - original.stitchCount).coerceAtLeast(0)

    Surface(
        color = if (changed) Gold.copy(alpha = .09f) else SurfaceBrown,
        border = androidx.compose.foundation.BorderStroke(1.dp, if (changed) Gold.copy(alpha = .50f) else LineGold.copy(alpha = .32f))
    ) {
        Column(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 9.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ExpressiveIconBadge(if (changed) Icons.Rounded.EditNote else Icons.Rounded.Shield, selected = changed, size = 38.dp)
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text("Editor Seguro", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                    Text(
                        if (changed) "Cópia de trabalho • alterações não salvas" else "Original preservado • nenhuma alteração aplicada",
                        color = if (changed) Gold else Muted,
                        fontSize = 8.sp
                    )
                }
                Surface(shape = RoundedCornerShape(50), color = if (changed) Gold.copy(alpha = .15f) else CardBrown) {
                    Text(if (changed) "EDITANDO" else "ORIGINAL", color = if (changed) Gold else Muted, fontWeight = FontWeight.Bold, fontSize = 8.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
                }
            }

            if (changed) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Surface(Modifier.weight(1f), shape = RoundedCornerShape(12.dp), color = CardBrown) {
                        Text("+$addedStitches pontos", color = Cream, fontSize = 8.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 7.dp))
                    }
                    Surface(Modifier.weight(1f), shape = RoundedCornerShape(12.dp), color = CardBrown) {
                        Text("$trimCount cortes internos", color = Cream, fontSize = 8.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 7.dp))
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                FilledTonalButton(
                    onClick = onUndo,
                    enabled = canUndo,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(15.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.Undo, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Desfazer", fontSize = 8.sp)
                }
                FilledTonalButton(
                    onClick = onRedo,
                    enabled = canRedo,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(15.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Gold)
                ) {
                    Icon(Icons.Rounded.Redo, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Refazer", fontSize = 8.sp)
                }
                FilledTonalButton(
                    onClick = onReset,
                    enabled = changed,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(15.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = CardBrown, contentColor = Muted)
                ) {
                    Icon(Icons.Rounded.RestartAlt, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Original", fontSize = 8.sp)
                }
            }

            Surface(
                shape = RoundedCornerShape(14.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .32f))
            ) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.SaveAs, null, tint = Muted, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(7.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Salvar como", color = Muted, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)
                        Text("Bloqueado até o writer de matriz ser validado — não vamos gerar arquivo falso.", color = Muted, fontSize = 7.sp, lineHeight = 10.sp)
                    }
                    Icon(Icons.Rounded.Lock, null, tint = Muted, modifier = Modifier.size(16.dp))
                }
            }
        }
    }
}

'''
text = text[:insert_at] + safe_editor_ui + text[insert_at:]

text = text.replace('0.2.15', '0.2.16')
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.16 safe editor patch applied successfully')
