from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_061.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

old = '''                    Canvas(Modifier.matchParentSize()) {
                        val step = 32f
                        var x = 0f
                        while (x < size.width) {
                            drawLine(Color(0x1A5E5549), Offset(x, 0f), Offset(x, size.height), strokeWidth = 1f)
                            x += step
                        }
                        var y = 0f
                        while (y < size.height) {
                            drawLine(Color(0x1A5E5549), Offset(0f, y), Offset(size.width, y), strokeWidth = 1f)
                            y += step
                        }
                    }'''
new = '''                    Canvas(Modifier.matchParentSize()) {
                        val canvasSize = this.size
                        val step = 32f
                        var x = 0f
                        while (x < canvasSize.width) {
                            drawLine(Color(0x1A5E5549), Offset(x, 0f), Offset(x, canvasSize.height), strokeWidth = 1f)
                            x += step
                        }
                        var y = 0f
                        while (y < canvasSize.height) {
                            drawLine(Color(0x1A5E5549), Offset(0f, y), Offset(canvasSize.width, y), strokeWidth = 1f)
                            y += step
                        }
                    }'''
if old not in text:
    raise SystemExit('0.2.33 Canvas size shadow fix anchor not found')
text = text.replace(old, new, 1)
main_path.write_text(text, encoding='utf-8')

required = [
    'val canvasSize = this.size',
    'while (x < canvasSize.width)',
    'while (y < canvasSize.height)',
    'private fun LetteringDualModeScreen033(',
    '"CONCLUIR E GERAR MATRIZ"',
    '"Lettering Studio Pro"'
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.33 Canvas fix regression guard failed: ' + ', '.join(missing))

print('BORDATTO 0.2.33 quick canvas size shadow fix applied successfully')
