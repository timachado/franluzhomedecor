from pathlib import Path
import runpy

# Start from the known-good cumulative 0.2.27 build.
runpy.run_path('.github/scripts/patch_bordatto_049.py', run_name='__main__')

main_path = Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text = main_path.read_text(encoding='utf-8')

old = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        MachineCheckPanel(workingDesign, machineConfig)'''

new = '''        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        if (info) {
            Surface(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp),
                shape = RoundedCornerShape(16.dp),
                color = CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .45f))
            ) {
                Column(
                    Modifier.fillMaxWidth().padding(11.dp),
                    verticalArrangement = Arrangement.spacedBy(5.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Info, null, tint = Gold, modifier = Modifier.size(17.dp))
                        Spacer(Modifier.width(7.dp))
                        Text("Informações da matriz", color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 10.sp)
                    }
                    Text(
                        "${workingDesign.name} • ${workingDesign.stitchCount} pontos • ${workingDesign.colors} cor(es)",
                        color = Cream,
                        fontSize = 8.sp
                    )
                    Text(
                        "${"%.1f".format(workingDesign.width)} × ${"%.1f".format(workingDesign.height)} mm • ${workingDesign.jumpCount} saltos",
                        color = Muted,
                        fontSize = 7.sp
                    )
                    Text(
                        "Grade mostra a referência visual. Centralizar restaura zoom e posição da matriz.",
                        color = Muted,
                        fontSize = 7.sp,
                        lineHeight = 10.sp
                    )
                }
            }
        }
        MachineCheckPanel(workingDesign, machineConfig)'''

if old not in text:
    raise SystemExit('0.2.28 Viewer Info anchor not found')
text = text.replace(old, new, 1)

# Ensure the Info state now controls visible UI exactly once.
if text.count('if (info) {') < 1:
    raise SystemExit('0.2.28 Viewer Info panel was not inserted')

text = text.replace('0.2.27', '0.2.28')
main_path.write_text(text, encoding='utf-8')

gradle_path = Path('BORDATTO_Foundation_0.1/app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = gradle.replace('versionCode = 29', 'versionCode = 30')
gradle = gradle.replace('versionName = "0.2.27"', 'versionName = "0.2.28"')
gradle_path.write_text(gradle, encoding='utf-8')

print('BORDATTO 0.2.28 Viewer Info panel fix applied successfully')