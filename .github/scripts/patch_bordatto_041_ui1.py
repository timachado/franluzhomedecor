from pathlib import Path
import runpy
runpy.run_path('.github/scripts/patch_bordatto_041_core.py', run_name='__main__')
path=Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text=path.read_text(encoding='utf-8')
old='''            onSaveProject = { saveProjectRequest++ },\n            onExport = { format -> requestSafeExport(format) },\n            onShareLastExport = { shareLastVerifiedExport() }\n        )'''
new='''            onSaveProject = { saveProjectRequest++ },\n            onExport = { format -> requestSafeExport(format) },\n            onShareLastExport = { shareLastVerifiedExport() },\n            onThreadColorChange = { index, newColor ->\n                val count = maxOf(workingDesign.colors, index + 1)\n                val palette = MutableList(count) { i -> effectiveThreadColor(workingDesign, i) }\n                palette[index] = newColor\n                val infos = MutableList(count) { i -> workingDesign.threadInfos.getOrNull(i) ?: DesignThreadInfo(color = palette[i]) }\n                infos[index] = infos[index].copy(color = newColor)\n                commitWorkingEdit(workingDesign.copy(threadColors = palette, threadInfos = infos))\n            }\n        )'''
if old not in text: raise SystemExit('callbacks marker not found')
text=text.replace(old,new,1)
old='''    onSaveProject: () -> Unit,\n    onExport: (String) -> Unit,\n    onShareLastExport: () -> Unit\n) {'''
new='''    onSaveProject: () -> Unit,\n    onExport: (String) -> Unit,\n    onShareLastExport: () -> Unit,\n    onThreadColorChange: (Int, Int) -> Unit\n) {'''
if old not in text: raise SystemExit('signature marker not found')
text=text.replace(old,new,1)
central=text.index('Text("Central de Exportação", color = Cream, fontSize = 9.sp, fontWeight = FontWeight.SemiBold)')
surface=text.rfind('            Surface(',0,central)
if surface<0: raise SystemExit('central surface not found')
text=text[:surface]+'            ThreadPalettePanel(design = working, onChangeColor = onThreadColorChange)\n\n'+text[surface:]
path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.20 color callbacks applied')
