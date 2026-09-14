from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_029.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

old = 'org.embroideryio.embroideryio.EmbPattern.readStream(fileName, input)'
new = 'org.embroideryio.embroideryio.EmbroideryIO.readStream(fileName, input)'
if old not in text:
    raise SystemExit('EmbroideryIO readStream call marker not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.9 EmbroideryIO 0.0.7 API adapter applied successfully')
