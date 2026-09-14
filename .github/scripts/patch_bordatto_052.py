from pathlib import Path
import runpy

# Apply the full 0.2.29 patch first.
runpy.run_path('.github/scripts/patch_bordatto_051.py', run_name='__main__')

path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = path.read_text(encoding='utf-8')

old = '@Composable\nprivate fun BordattoParameterSlider('
new = '@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)\n@Composable\nprivate fun BordattoParameterSlider('
if old not in text:
    raise SystemExit('0.2.29 slider opt-in anchor not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

print('BORDATTO 0.2.29 Material3 slider opt-in applied successfully')
