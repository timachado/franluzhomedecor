from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_036.py', run_name='__main__')
path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

# patch_bordatto_036 intentionally rewrites ViewerScreen references from the original
# design to workingDesign. Two helper calls use Kotlin named arguments and their
# parameter name must remain `design`, even though the value is the working copy.
wrong = 'workingDesign = workingDesign,'
count = text.count(wrong)
if count != 2:
    raise SystemExit(f'Expected exactly 2 rewritten named design arguments, found {count}')
text = text.replace(wrong, 'design = workingDesign,')

path.write_text(text, encoding='utf-8')
print('BORDATTO 0.2.16 safe editor named-argument fix applied successfully')
