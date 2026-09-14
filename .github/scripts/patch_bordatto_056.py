from pathlib import Path
import runpy

# Apply the complete 0.2.31 interaction patch first.
runpy.run_path('.github/scripts/patch_bordatto_055.py', run_name='__main__')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')

if 'compileSdk = 37' not in gradle:
    raise SystemExit('0.2.31 compileSdk 37 anchor not found before SDK36 pin')

gradle = gradle.replace('compileSdk = 37', 'compileSdk = 36', 1)

if 'targetSdk = 36' not in gradle:
    raise SystemExit('0.2.31 targetSdk 36 regression guard failed')
if 'versionName = "0.2.31"' not in gradle:
    raise SystemExit('0.2.31 versionName regression guard failed')
if 'versionCode = 33' not in gradle:
    raise SystemExit('0.2.31 versionCode regression guard failed')

gradle_path.write_text(gradle, encoding='utf-8')
print('BORDATTO 0.2.31 Android SDK 36 build pin applied successfully')
