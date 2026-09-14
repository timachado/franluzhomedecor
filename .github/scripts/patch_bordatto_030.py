from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_029_api_fix.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

text = text.replace('setOf("dst", "pes", "jef")', 'setOf("dst", "pes", "jef", "vp3", "exp", "tbf", "u01")')
text = text.replace('Suporte real atual: DST, PES e JEF.', 'Suporte real atual: DST, PES, JEF, VP3, EXP, TBF e U01.')
text = text.replace('DST, PES e JEF reais', 'DST, PES, JEF, VP3, EXP, TBF e U01')
text = text.replace('DST, PES e JEF no mesmo visualizador', '7 formatos no mesmo visualizador')
text = text.replace('DST, PES ou JEF', 'DST, PES, JEF, VP3, EXP, TBF ou U01')
text = text.replace('"pes", "jef" -> parseWithEmbroideryIo(fileName, bytes)', '"pes", "jef", "vp3", "exp", "tbf", "u01" -> parseWithEmbroideryIo(fileName, bytes)')
text = text.replace('Suporte real atual: DST, PES e JEF', 'Suporte real atual: DST, PES, JEF, VP3, EXP, TBF e U01')
text = text.replace('0.2.9', '0.2.10')

path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.10 extended multi-format patch applied successfully')
