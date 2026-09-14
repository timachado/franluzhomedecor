from pathlib import Path
import runpy
import re

runpy.run_path('.github/scripts/patch_bordatto_043.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

panel_start = text.index('private fun ThreadPalettePanel(')
panel_end = text.index('\n@Composable\nprivate fun SafeEditorPanel(', panel_start)
panel = text[panel_start:panel_end]

# 0.2.21 formatting differs slightly from the original patch anchor. Inject the
# 0.2.22 state from the actual catalog state line instead of relying on spacing.
if 'var blockCatalogIndex' not in panel or 'val sequenceBlocks' not in panel or 'val potentialSavings' not in panel:
    match = re.search(r'(?m)^(\s*)var catalogIndex by remember\s*\{\s*mutableStateOf<Int\?>\(null\)\s*\}\s*$', panel)
    if not match:
        raise SystemExit('0.2.22 fix: catalogIndex state anchor not found')
    indent = match.group(1)
    insertion = (
        match.group(0) + '\n' +
        indent + 'var blockCatalogIndex by remember{mutableStateOf<Int?>(null)}\n' +
        indent + 'val sequenceBlocks=remember(design){calculateThreadSequenceBlocks(design)}\n' +
        indent + 'val potentialSavings=remember(design){potentialThreadChangeSavings(design)}'
    )
    panel = panel[:match.start()] + insertion + panel[match.end():]

for required in ('blockCatalogIndex', 'sequenceBlocks', 'potentialSavings'):
    if required not in panel:
        raise SystemExit(f'0.2.22 fix: missing {required} after injection')

text = text[:panel_start] + panel + text[panel_end:]
path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.22 sequence panel state fix applied successfully')
