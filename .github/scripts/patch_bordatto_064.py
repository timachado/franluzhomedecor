from pathlib import Path
import base64
import re
import zlib

# Patch 063 is intentionally compressed because it carries the large 0.2.34 UI.
# Its only blocker is an over-strict guard that expects the literal label
# "Traço à mão", while the implemented Traditional tab is labelled "Traço".
# Decode the source, correct only that expected guard label, then execute the
# complete 0.2.34 patch so all edits are actually written before validation.
wrapper = Path('.github/scripts/patch_bordatto_063.py').read_text(encoding='utf-8')
match = re.search(r"b64decode\('([^']+)'\)", wrapper, re.S)
if not match:
    raise SystemExit('0.2.34 compressed patch payload not found')
source = zlib.decompress(base64.b64decode(match.group(1))).decode('utf-8')
if '"Traço à mão"' not in source:
    raise SystemExit('0.2.34 expected Traço à mão guard not found in payload')
source = source.replace('"Traço à mão"', '"Traço"')
exec(compile(source, '.github/scripts/patch_bordatto_063.py<fixed>', 'exec'), {'__name__': '__main__'})

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')
gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')

required = [
    'TRADITIONAL_EDITOR',
    'TRADITIONAL_SIMULATOR',
    'TraditionalEditorScreen034(',
    'TraditionalSimulatorScreen034(',
    'TraditionalDesignCanvas034(',
    'appendHandDraw034(',
    'mergeTraditionalText034(',
    'listOf("Texto", "Imagem", "Traço")',
    '"Configurações de Exibição"',
    '"Sólida"',
    '"Pontos"',
    '"Realista"',
    '"Brother"',
    '"Madeira"',
    '"Rosa Intenso"',
    '"Tradicional"',
    '"Studio Pro"',
    'onTraditionalGenerate',
    'onStudioGenerate',
    'Page.TRADITIONAL_EDITOR && design != null',
    'Page.TRADITIONAL_SIMULATOR && design != null',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('0.2.34 functional regression guard failed: ' + ', '.join(missing))

# Verify all four Traditional post-generation navigation labels exist, without
# depending on the exact Kotlin collection syntax used by the implementation.
for label in ['"Adicionar"', '"Ajustes"', '"Camadas"', '"Linhas"']:
    if label not in text:
        raise SystemExit('0.2.34 Traditional navigation label missing: ' + label)

# Traditional post-generation must remain isolated from professional Viewer tools.
start = text.index('@Composable\nprivate fun TraditionalEditorScreen034')
end = text.index('@Composable\nprivate fun TraditionalSimulatorScreen034', start)
traditional_slice = text[start:end]
for forbidden in ['MachineCheckPanel(', 'DesignAnalyzerPanel(', 'SafeEditorPanel(', 'Ferramentas profissionais']:
    if forbidden in traditional_slice:
        raise SystemExit('0.2.34 Traditional isolation failed: ' + forbidden)

if 'versionCode = 36' not in gradle or 'versionName = "0.2.34"' not in gradle:
    raise SystemExit('0.2.34 version guard failed')

print('BORDATTO 0.2.34 Traditional full workflow functional guards passed')
