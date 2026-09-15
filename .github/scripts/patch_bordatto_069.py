from pathlib import Path

# patch 068 contains the complete 0.2.38 motor. Its only blocker is an
# over-broad routing guard that also counts the Studio Pro technical preview.
source = Path('.github/scripts/patch_bordatto_068.py').read_text(encoding='utf-8')
old = '''traditional, studio = block.split(studio_marker, 1)
count = traditional.count('generateLetteringDesign(name, options)')
if count != 2:
    raise SystemExit(f'0.2.38 expected 2 Traditional generator calls, found {count}')
traditional = traditional.replace('generateLetteringDesign(name, options)', 'generateTraditionalReferenceLettering038(name, options)')
block = traditional + studio_marker + studio'''
new = '''before_studio, studio = block.split(studio_marker, 1)
traditional_marker = '    if (mode == "Tradicional") {'
if traditional_marker not in before_studio:
    raise SystemExit('0.2.38 Traditional branch anchor not found')
prefix, traditional = before_studio.split(traditional_marker, 1)
count = traditional.count('generateLetteringDesign(name, options)')
if count != 2:
    raise SystemExit(f'0.2.38 expected 2 Traditional generator calls, found {count}')
traditional = traditional.replace('generateLetteringDesign(name, options)', 'generateTraditionalReferenceLettering038(name, options)')
block = prefix + traditional_marker + traditional + studio_marker + studio'''
if old not in source:
    raise SystemExit('0.2.38 routing guard source anchor not found')
source = source.replace(old, new, 1)
exec(compile(source, '.github/scripts/patch_bordatto_068.py<routing-fixed>', 'exec'), {'__name__': '__main__'})
print('BORDATTO 0.2.38 Traditional routing guard fixed successfully')
