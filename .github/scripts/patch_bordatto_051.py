from pathlib import Path
import runpy

# Start from the cumulative, tested 0.2.28 source.
runpy.run_path('.github/scripts/patch_bordatto_050.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

# Needed by the new scrollable Viewer content.
if 'import androidx.compose.foundation.rememberScrollState' not in text:
    text = text.replace(
        'import androidx.compose.foundation.layout.*\n',
        'import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll\n',
        1
    )

# A compact, reliable Material slider with a circular thumb and BORDATTO colors.
# This removes the tall split-looking thumb seen on-device while keeping native tap/drag behavior.
lettering_anchor = '@Composable\nprivate fun LetteringScreen'
idx = text.index(lettering_anchor)
slider_helper = r'''@Composable
private fun BordattoParameterSlider(
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>
) {
    Slider(
        value = value,
        onValueChange = onValueChange,
        valueRange = valueRange,
        modifier = Modifier.fillMaxWidth().height(38.dp),
        colors = SliderDefaults.colors(
            thumbColor = Gold,
            activeTrackColor = Gold,
            inactiveTrackColor = LineGold.copy(alpha = .55f),
            activeTickColor = Color.Transparent,
            inactiveTickColor = Color.Transparent
        ),
        thumb = {
            Box(
                Modifier
                    .size(22.dp)
                    .clip(CircleShape)
                    .background(Gold)
                    .border(2.dp, Cream.copy(alpha = .85f), CircleShape)
            )
        }
    )
}

'''
text = text[:idx] + slider_helper + text[idx:]

# Font preview must reflect the text the user typed in EVERY font card, not only Elegance.
old_card = 'Text(if (f == "Elegance") name.ifBlank { "Maria" } else "BORDATTO", color = Cream, fontFamily = if (f == "Elegance" || f == "Handwriting") FontFamily.Cursive else FontFamily.Serif, fontSize = 19.sp, modifier = Modifier.weight(1f))'
new_card = '''Text(
                        name.ifBlank { "BORDATTO" },
                        color = Cream,
                        fontFamily = when (f) {
                            "Elegance", "Classic" -> FontFamily.Serif
                            "Handwriting" -> FontFamily.Cursive
                            else -> FontFamily.SansSerif
                        },
                        fontWeight = if (f == "Classic" || f == "Sweet") FontWeight.Bold else FontWeight.Normal,
                        fontStyle = if (f == "Elegance") FontStyle.Italic else FontStyle.Normal,
                        fontSize = 19.sp,
                        maxLines = 1,
                        modifier = Modifier.weight(1f)
                    )'''
if old_card not in text:
    raise SystemExit('0.2.29 font-card preview anchor not found')
text = text.replace(old_card, new_card, 1)

# Main preview should use the same family logic as the actual font mapping.
old_family = 'fontFamily = if (font == "Elegance" || font == "Handwriting") FontFamily.Cursive else FontFamily.Serif,'
new_family = '''fontFamily = when (font) {
                            "Elegance", "Classic" -> FontFamily.Serif
                            "Handwriting" -> FontFamily.Cursive
                            else -> FontFamily.SansSerif
                        },'''
if old_family not in text:
    raise SystemExit('0.2.29 main font preview anchor not found')
text = text.replace(old_family, new_family, 1)

# Replace the five visually broken parameter sliders with the compact reliable slider.
slider_replacements = {
    'Slider(size, { size = it }, valueRange = 10f..90f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))':
        'BordattoParameterSlider(size, { size = it }, 10f..90f)',
    'Slider(spacing, { spacing = it }, valueRange = -18f..40f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))':
        'BordattoParameterSlider(spacing, { spacing = it }, -18f..40f)',
    'Slider(density, { density = it }, valueRange = .28f..1.0f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))':
        'BordattoParameterSlider(density, { density = it }, .28f..1.0f)',
    'Slider(pullComp, { pullComp = it }, valueRange = 0f..1.0f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))':
        'BordattoParameterSlider(pullComp, { pullComp = it }, 0f..1.0f)',
    'Slider(satinMax, { satinMax = it }, valueRange = 4f..14f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))':
        'BordattoParameterSlider(satinMax, { satinMax = it }, 4f..14f)'
}
for old, new in slider_replacements.items():
    if old not in text:
        raise SystemExit('0.2.29 parameter slider anchor not found: ' + old[:28])
    text = text.replace(old, new, 1)

# Viewer bug: the previous root Column contained many expandable panels before a weight(1f) canvas.
# Expanding Analyzer/Editor/Colors pushed later content below the physical screen with no scrolling.
viewer_start = text.index('@Composable\nprivate fun ViewerScreen')
viewer_end = text.index('\nprivate enum class DiagnosticKind', viewer_start)
viewer = text[viewer_start:viewer_end]

# Open a vertically scrollable content area immediately after the tools row.
tools_anchor = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        if (info) {'''
tools_new = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        val viewerScroll = rememberScrollState()
        Column(
            Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(viewerScroll)
        ) {
        if (info) {'''
if tools_anchor not in viewer:
    raise SystemExit('0.2.29 Viewer scroll start anchor not found')
viewer = viewer.replace(tools_anchor, tools_new, 1)

# The matrix canvas needs a real height inside a scroll container; weight would collapse to zero.
canvas_old = 'Modifier.weight(1f).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
canvas_new = 'Modifier.height(360.dp).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {'
if canvas_old not in viewer:
    raise SystemExit('0.2.29 Viewer canvas weight anchor not found')
viewer = viewer.replace(canvas_old, canvas_new, 1)

# Close the scrollable region after the simulator and keep the zoom footer fixed/visible.
footer_anchor = '\n        Surface(color = Chocolate) {'
footer_pos = viewer.rfind(footer_anchor)
if footer_pos < 0:
    raise SystemExit('0.2.29 Viewer footer anchor not found')
viewer = viewer[:footer_pos] + '\n        Spacer(Modifier.height(18.dp))\n        }' + viewer[footer_pos:]

text = text[:viewer_start] + viewer + text[viewer_end:]

# Sanity checks against regressions seen in the videos.
checks = [
    'verticalScroll(viewerScroll)',
    'Modifier.height(360.dp).fillMaxWidth().background(Ink)',
    'BordattoParameterSlider(size',
    'name.ifBlank { "BORDATTO" }',
    'MachineCheckPanel(workingDesign, machineConfig)',
    'SafeEditorPanel(',
    'EmbroiderySimulatorPanel('
]
missing = [c for c in checks if c not in text]
if missing:
    raise SystemExit('0.2.29 sanity check failed: ' + ', '.join(missing))

text = text.replace('0.2.28', '0.2.29')
main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 30', 'versionCode = 31')
gradle = gradle.replace('versionName = "0.2.28"', 'versionName = "0.2.29"')
gradle_path.write_text(gradle, encoding='utf-8')

print('BORDATTO 0.2.29 responsive Viewer + Lettering UI fixes applied successfully')
