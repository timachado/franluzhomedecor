from pathlib import Path
import runpy

# Apply the complete, Kotlin-valid 0.2.31 feature patch.
runpy.run_path('.github/scripts/patch_bordatto_058.py', run_name='__main__')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')

old_bom = 'androidx.compose:compose-bom:2026.08.00'
new_bom = 'androidx.compose:compose-bom:2026.04.01'
if old_bom not in gradle:
    raise SystemExit('0.2.31 Compose BOM anchor not found')
gradle = gradle.replace(old_bom, new_bom, 1)

# Keep runtime target unchanged; only compile compatibility is pinned.
checks = [
    'compileSdk = 36',
    'targetSdk = 36',
    'versionCode = 33',
    'versionName = "0.2.31"',
    new_bom
]
missing = [item for item in checks if item not in gradle]
if missing:
    raise SystemExit('0.2.31 Gradle compatibility guard failed: ' + ', '.join(missing))

gradle_path.write_text(gradle, encoding='utf-8')
print('BORDATTO 0.2.31 Compose BOM 2026.04.01 / SDK36 compatibility pin applied successfully')
