from pathlib import Path
import runpy
import re

# Rebuild the known-good 0.2.26 source first.
runpy.run_path('.github/scripts/patch_bordatto_047.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')
patch48 = Path('.github/scripts/patch_bordatto_048.py').read_text(encoding='utf-8')

# Reuse the already-reviewed 0.2.27 engine/UI payload, but DO NOT execute patch 048,
# because its old screen replacement spanned until MachineScreen and removed helper declarations.
def extract_raw_block(source: str, variable: str) -> str:
    marker = variable + " = r'''"
    start = source.index(marker) + len(marker)
    end = source.index("'''", start)
    return source[start:end]

core = extract_raw_block(patch48, 'core')
lettering_ui = extract_raw_block(patch48, 'lettering_ui')

# Insert the new engine at top level, preserving every 0.2.26 helper.
insert_at = text.index('class MainActivity')
text = text[:insert_at] + core + text[insert_at:]

# Update only the navigation call for LetteringScreen.
pattern = re.compile(
    r'''page == Page\.LETTERING -> LetteringScreen\(\s*onBack = \{ page = Page\.MAIN \},\s*onGenerate = \{.*?\}\s*\)''',
    re.S
)
replacement = '''page == Page.LETTERING -> LetteringScreen(\n                    onBack = { page = Page.MAIN },\n                    onGenerate = { generated ->\n                        design = generated\n                        page = Page.MAIN\n                        activeTab = MainTab.CREATE\n                    }\n                )'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('0.2.27 navigation callback anchor not found')

# Replace ONLY LetteringScreen itself using balanced braces. This is the critical fix:
# helper declarations inserted between screens by previous versions remain untouched.
signature = '@Composable\nprivate fun LetteringScreen'
start = text.index(signature)
open_brace = text.index('{', start)
depth = 0
end = None
for i in range(open_brace, len(text)):
    ch = text[i]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit('0.2.27 could not find balanced end of LetteringScreen')

# Keep trailing newlines stable.
while end < len(text) and text[end] in '\r\n':
    end += 1
text = text[:start] + lettering_ui + text[end:]

# Sanity checks: all critical helpers from the known-good 0.2.26 must survive.
required = [
    'MachineConfig', 'LibraryItem', 'StandardHoops', 'appPrefs',
    'loadMachineConfig', 'loadLibrary', 'CostCalculatorScreen',
    'estimateMachineMinutes', 'saveMachineConfig'
]
missing = [name for name in required if name not in text]
if missing:
    raise SystemExit('0.2.27 helper preservation failed: ' + ', '.join(missing))

text = text.replace('0.2.26', '0.2.27')
main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 28', 'versionCode = 29')
gradle = gradle.replace('versionName = "0.2.26"', 'versionName = "0.2.27"')
gradle_path.write_text(gradle, encoding='utf-8')

print('BORDATTO 0.2.27 Lettering Pro Satin safe screen replacement applied successfully')
