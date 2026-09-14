from pathlib import Path
import runpy

# patch_055 contains the complete requested 0.2.31 feature set, but its Viewer
# anchors predate workingDesign / sequencePreviewDesign. Adapt those anchors at
# runtime without mutating the historical patch.
source_path = Path('.github/scripts/patch_bordatto_055.py')
source = source_path.read_text(encoding='utf-8')

replacements = {
    'val visualDiagnostics = remember(design) { collectDiagnosticMarkers(design) }':
        'val visualDiagnostics = remember(workingDesign) { collectDiagnosticMarkers(workingDesign) }',
    'var diagnosticsVisible by remember(design) { mutableStateOf(true) }':
        'var diagnosticsVisible by remember(workingDesign) { mutableStateOf(true) }',
    'var focusMarker by remember(design) { mutableStateOf<DiagnosticMarker?>(null) }':
        'var focusMarker by remember(workingDesign) { mutableStateOf<DiagnosticMarker?>(null) }',
    '''visible_old = \'\'\'                visibleUntil = visibleUntil,\n                diagnostics = if (diagnosticsVisible) visualDiagnostics else emptyList(),\'\'\''''':
        '''visible_old = \'\'\'                visibleUntil = if (sequencePreviewDesign != null) (sequencePreviewDesign?.stitches?.size ?: visibleUntil) else visibleUntil,\n                diagnostics = if (diagnosticsVisible) activeDiagnostics else emptyList(),\'\'\''''',
    '''visible_new = \'\'\'                visibleUntil = if (stitchesVisible031) visibleUntil else 0,\n                diagnostics = if (stitchesVisible031 && diagnosticsVisible) visualDiagnostics else emptyList(),\'\'\''''':
        '''visible_new = \'\'\'                visibleUntil = if (stitchesVisible031) (if (sequencePreviewDesign != null) (sequencePreviewDesign?.stitches?.size ?: visibleUntil) else visibleUntil) else 0,\n                diagnostics = if (stitchesVisible031 && diagnosticsVisible) activeDiagnostics else emptyList(),\'\'\'''''
}

for old, new in replacements.items():
    if old not in source:
        raise SystemExit('0.2.31 runtime patch source anchor not found: ' + old[:80])
    source = source.replace(old, new, 1)

runtime_path = Path('.github/scripts/_patch_bordatto_055_runtime_fixed.py')
runtime_path.write_text(source, encoding='utf-8')
runpy.run_path(str(runtime_path), run_name='__main__')

# Complete matrix hide/show: assisted-correction overlays must disappear too.
main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')
old_preview = 'correctionPreview = if (diagnosticsVisible) assistedPreview else null,'
new_preview = 'correctionPreview = if (stitchesVisible031 && diagnosticsVisible) assistedPreview else null,'
if old_preview not in text:
    raise SystemExit('0.2.31 correction preview visibility anchor not found')
text = text.replace(old_preview, new_preview, 1)
main_path.write_text(text, encoding='utf-8')

# CI runner currently exposes Android platform 36 reliably. The app already
# targets 36; compile with the same public SDK without changing app behavior.
gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
if 'compileSdk = 37' not in gradle:
    raise SystemExit('0.2.31 compileSdk 37 anchor not found')
gradle = gradle.replace('compileSdk = 37', 'compileSdk = 36', 1)
if 'targetSdk = 36' not in gradle:
    raise SystemExit('0.2.31 targetSdk 36 regression guard failed')
if 'versionCode = 33' not in gradle or 'versionName = "0.2.31"' not in gradle:
    raise SystemExit('0.2.31 version metadata regression guard failed')
gradle_path.write_text(gradle, encoding='utf-8')

# Strong regression checks for the exact user-reported areas.
checks = [
    'LetteringSliderControl031(',
    'fontSize = (size * .74f).coerceIn(18f, 66f).sp',
    'letterSpacing = (spacing / 7f).coerceIn(-2.5f, 6f).sp',
    'var stitchesVisible031 by remember(workingDesign)',
    'if (stitchesVisible031) Icons.Rounded.Visibility else Icons.Rounded.VisibilityOff',
    'visibleUntil = if (stitchesVisible031)',
    'diagnostics = if (stitchesVisible031 && diagnosticsVisible) activeDiagnostics else emptyList()',
    'correctionPreview = if (stitchesVisible031 && diagnosticsVisible) assistedPreview else null',
    'Text("ANALISAR E LOCALIZAR ALERTA"',
    'Text("VER NO DESENHO"',
    'modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded }',
    'SafeEditorPanel(',
    'EmbroiderySimulatorPanel(',
    'MachineCheckPanel('
]
missing = [c for c in checks if c not in text]
if missing:
    raise SystemExit('0.2.31 final regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.31 corrected Viewer anchors + SDK36 pin applied successfully')
