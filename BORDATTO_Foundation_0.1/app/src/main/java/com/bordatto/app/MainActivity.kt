package com.bordatto.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlin.math.max
import kotlin.math.min

private val Ink = Color(0xFF0D0805)
private val Chocolate = Color(0xFF160D08)
private val SurfaceBrown = Color(0xFF21130C)
private val CardBrown = Color(0xFF2B1A10)
private val CardBrown2 = Color(0xFF342014)
private val Gold = Color(0xFFE1B66F)
private val GoldDeep = Color(0xFFB9823D)
private val Cream = Color(0xFFF5E9D7)
private val Muted = Color(0xFFBBA991)
private val LineGold = Color(0xFF6F4C25)

private enum class StitchCommand { STITCH, JUMP, COLOR_CHANGE, END }
private data class StitchPoint(val x: Float, val y: Float, val command: StitchCommand, val color: Int)
private data class Design(
    val name: String,
    val stitches: List<StitchPoint>,
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float,
    val colors: Int
) {
    val width get() = maxX - minX
    val height get() = maxY - minY
    val stitchCount get() = stitches.count { it.command == StitchCommand.STITCH }
    val jumpCount get() = stitches.count { it.command == StitchCommand.JUMP }
    val colorChanges get() = stitches.count { it.command == StitchCommand.COLOR_CHANGE }
}

private enum class MainTab(val title: String) { HOME("Início"), CREATE("Criar"), PROJECTS("Projetos"), LIBRARY("Biblioteca"), PROFILE("Perfil") }
private enum class Page { MAIN, LETTERING, MACHINE }

private fun mainTabIcon(tab: MainTab): ImageVector = when (tab) {
    MainTab.HOME -> Icons.Rounded.Home
    MainTab.CREATE -> Icons.Rounded.AutoAwesome
    MainTab.PROJECTS -> Icons.Rounded.Folder
    MainTab.LIBRARY -> Icons.Rounded.Collections
    MainTab.PROFILE -> Icons.Rounded.Person
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val shared = when (intent?.action) {
            Intent.ACTION_VIEW -> intent.data
            Intent.ACTION_SEND -> if (android.os.Build.VERSION.SDK_INT >= 33) {
                intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
            } else {
                @Suppress("DEPRECATION") intent.getParcelableExtra(Intent.EXTRA_STREAM)
            }
            else -> null
        }
        setContent { BordattoApp(shared) }
    }
}

@Composable
private fun BordattoApp(initialUri: Uri?) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var splash by remember { mutableStateOf(initialUri == null) }
    var design by remember { mutableStateOf<Design?>(null) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var notice by remember { mutableStateOf<String?>(null) }
    var pendingUri by remember { mutableStateOf(initialUri) }
    var activeTab by remember { mutableStateOf(MainTab.HOME) }
    var page by remember { mutableStateOf(Page.MAIN) }

    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri -> pendingUri = uri }

    LaunchedEffect(Unit) {
        if (splash) {
            delay(1150)
            splash = false
        }
    }

    LaunchedEffect(pendingUri) {
        val uri = pendingUri ?: return@LaunchedEffect
        loading = true
        error = null
        runCatching {
            withContext(Dispatchers.IO) {
                val resolver = context.contentResolver
                val name = resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { c ->
                    if (c.moveToFirst()) c.getString(0) else null
                } ?: uri.lastPathSegment ?: "matriz.dst"
                if (!name.lowercase().endsWith(".dst")) error("Nesta versão 0.2.1, a leitura real implementada continua sendo DST. Os demais formatos entrarão conforme forem validados.")
                val bytes = resolver.openInputStream(uri)?.use { it.readBytes() } ?: error("Não foi possível ler o arquivo.")
                parseDst(name, bytes)
            }
        }.onSuccess {
            design = it
            activeTab = MainTab.HOME
            page = Page.MAIN
        }.onFailure { error = it.message ?: "Erro ao abrir a matriz." }
        loading = false
        pendingUri = null
    }

    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Gold,
            secondary = GoldDeep,
            background = Ink,
            surface = SurfaceBrown,
            surfaceVariant = CardBrown,
            onPrimary = Ink,
            onBackground = Cream,
            onSurface = Cream
        ),
        shapes = Shapes(
            extraSmall = RoundedCornerShape(10.dp),
            small = RoundedCornerShape(14.dp),
            medium = RoundedCornerShape(20.dp),
            large = RoundedCornerShape(28.dp),
            extraLarge = RoundedCornerShape(36.dp)
        )
    ) {
        Surface(Modifier.fillMaxSize(), color = Ink) {
            when {
                splash -> SplashScreen()
                design != null -> ViewerScreen(design!!) { design = null }
                page == Page.LETTERING -> LetteringScreen(
                    onBack = { page = Page.MAIN },
                    onGenerate = { notice = "O criador de nomes já está desenhado. A geração real de pontos de bordado entra na próxima etapa do motor de lettering." }
                )
                page == Page.MACHINE -> MachineScreen(
                    onBack = { page = Page.MAIN },
                    onSave = { notice = "Configuração salva para esta sessão de teste. Na próxima versão ela será persistida no aparelho." }
                )
                else -> StudioShell(
                    activeTab = activeTab,
                    loading = loading,
                    onTab = { activeTab = it },
                    onOpenMatrix = { picker.launch(arrayOf("*/*")) },
                    onLettering = { page = Page.LETTERING },
                    onMachine = { page = Page.MACHINE },
                    onSoon = { notice = it }
                )
            }
        }
        error?.let { message ->
            AlertDialog(
                onDismissRequest = { error = null },
                icon = { Icon(Icons.Rounded.WarningAmber, null, tint = Gold) },
                title = { Text("BORDATTO Studio", color = Gold, fontFamily = FontFamily.Serif) },
                text = { Text(message) },
                confirmButton = { TextButton(onClick = { error = null }) { Text("OK") } }
            )
        }
        notice?.let { message ->
            AlertDialog(
                onDismissRequest = { notice = null },
                icon = { Icon(Icons.Rounded.AutoAwesome, null, tint = Gold) },
                title = { Text("Em evolução", color = Gold, fontFamily = FontFamily.Serif) },
                text = { Text(message) },
                confirmButton = { TextButton(onClick = { notice = null }) { Text("Entendi") } }
            )
        }
    }
}

@Composable
private fun SplashScreen() {
    Box(Modifier.fillMaxSize().background(Ink)) {
        Canvas(Modifier.fillMaxSize()) {
            val gold = Gold.copy(alpha = .22f)
            drawCircle(gold, radius = size.minDimension * .48f, center = Offset(-size.width * .15f, size.height * .13f), style = Stroke(2f))
            drawCircle(gold, radius = size.minDimension * .30f, center = Offset(size.width * 1.03f, size.height * .78f), style = Stroke(1.5f))
            drawLine(Gold.copy(alpha = .16f), Offset(0f, size.height * .76f), Offset(size.width, size.height * .63f), strokeWidth = 1.2f)
        }
        Column(Modifier.align(Alignment.Center), horizontalAlignment = Alignment.CenterHorizontally) {
            Surface(shape = RoundedCornerShape(28.dp), color = Gold.copy(alpha = .11f), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold)) {
                Icon(Icons.Rounded.AutoAwesome, null, tint = Gold, modifier = Modifier.padding(18.dp).size(48.dp))
            }
            Spacer(Modifier.height(18.dp))
            Text("BORDATTO", color = Gold, fontSize = 38.sp, letterSpacing = 3.sp, fontFamily = FontFamily.Serif, fontWeight = FontWeight.SemiBold)
            Text("Studio", color = Gold.copy(alpha = .95f), fontSize = 27.sp, fontFamily = FontFamily.Serif, fontStyle = FontStyle.Italic)
            Spacer(Modifier.height(10.dp))
            Text("Seu universo de bordados", color = Cream.copy(alpha = .78f), fontSize = 14.sp)
        }
        Column(Modifier.align(Alignment.BottomCenter).padding(bottom = 42.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Crie. Digitalize. Borde. Venda.", color = Cream.copy(alpha = .82f), fontSize = 13.sp)
            Text("Tudo na palma da sua mão.", color = Muted, fontSize = 12.sp)
        }
    }
}

@Composable
private fun StudioShell(
    activeTab: MainTab,
    loading: Boolean,
    onTab: (MainTab) -> Unit,
    onOpenMatrix: () -> Unit,
    onLettering: () -> Unit,
    onMachine: () -> Unit,
    onSoon: (String) -> Unit
) {
    Scaffold(containerColor = Ink, bottomBar = { StudioBottomBar(activeTab, onTab) }) { padding ->
        Box(Modifier.fillMaxSize().padding(padding)) {
            when (activeTab) {
                MainTab.HOME -> HomeScreen(loading, onOpenMatrix, onLettering, onMachine, onSoon)
                MainTab.CREATE -> CreateHubScreen(onOpenMatrix, onLettering, onSoon)
                MainTab.PROJECTS -> ProjectsScreen(onLettering)
                MainTab.LIBRARY -> LibraryScreen(onSoon)
                MainTab.PROFILE -> ProfileScreen(onMachine, onSoon)
            }
        }
    }
}

@Composable
private fun StudioBottomBar(activeTab: MainTab, onTab: (MainTab) -> Unit) {
    NavigationBar(containerColor = Chocolate, tonalElevation = 0.dp) {
        MainTab.entries.forEach { tab ->
            val selected = activeTab == tab
            val scale by animateFloatAsState(if (selected) 1.14f else .94f, label = "tabIconScale")
            NavigationBarItem(
                selected = selected,
                onClick = { onTab(tab) },
                icon = {
                    Icon(
                        imageVector = mainTabIcon(tab),
                        contentDescription = tab.title,
                        modifier = Modifier.size(24.dp).scale(scale)
                    )
                },
                label = { Text(tab.title, fontSize = 10.sp) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Gold,
                    selectedTextColor = Gold,
                    unselectedIconColor = Muted,
                    unselectedTextColor = Muted,
                    indicatorColor = Gold.copy(alpha = .16f)
                )
            )
        }
    }
}

@Composable
private fun BrandHeader(subtitle: String? = null) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        ExpressiveIconBadge(Icons.Rounded.AutoAwesome, selected = true, size = 44.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.Bottom) {
                Text("BORDATTO", color = Gold, fontSize = 22.sp, fontFamily = FontFamily.Serif, fontWeight = FontWeight.SemiBold, letterSpacing = 1.2.sp)
                Spacer(Modifier.width(6.dp))
                Text("Studio", color = Gold.copy(alpha = .9f), fontSize = 16.sp, fontFamily = FontFamily.Serif, fontStyle = FontStyle.Italic)
            }
            subtitle?.let { Text(it, color = Muted, fontSize = 11.sp) }
        }
        ExpressiveIconButton(Icons.Rounded.Person, "Perfil") { }
    }
}

@Composable
private fun ExpressiveIconBadge(icon: ImageVector, selected: Boolean = false, size: androidx.compose.ui.unit.Dp = 46.dp) {
    val scale by animateFloatAsState(if (selected) 1.06f else 1f, label = "badgeScale")
    Box(
        modifier = Modifier
            .size(size)
            .scale(scale)
            .clip(RoundedCornerShape(if (selected) 18.dp else 14.dp))
            .background(if (selected) Gold.copy(alpha = .16f) else CardBrown2)
            .border(1.dp, if (selected) Gold.copy(alpha = .42f) else LineGold.copy(alpha = .55f), RoundedCornerShape(if (selected) 18.dp else 14.dp)),
        contentAlignment = Alignment.Center
    ) {
        Icon(icon, null, tint = Gold, modifier = Modifier.size(size * .52f))
    }
}

@Composable
private fun ExpressiveIconButton(icon: ImageVector, description: String, onClick: () -> Unit) {
    Surface(
        modifier = Modifier.size(42.dp).clickable(onClick = onClick),
        shape = RoundedCornerShape(17.dp),
        color = CardBrown2,
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .65f))
    ) {
        Box(contentAlignment = Alignment.Center) {
            Icon(icon, description, tint = Gold, modifier = Modifier.size(21.dp))
        }
    }
}

private data class HomeAction(val icon: ImageVector, val title: String, val subtitle: String)

@Composable
private fun HomeScreen(loading: Boolean, onOpen: () -> Unit, onLettering: () -> Unit, onMachine: () -> Unit, onSoon: (String) -> Unit) {
    if (loading) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Gold) }
        return
    }
    val actions = listOf(
        HomeAction(Icons.Rounded.Add, "Nova Matriz", "Comece do zero"),
        HomeAction(Icons.Rounded.TextFields, "Criar Nome", "Textos e monogramas"),
        HomeAction(Icons.Rounded.Image, "Digitalizar Imagem", "Logo, foto ou desenho"),
        HomeAction(Icons.Rounded.AutoAwesome, "PhotoStitch", "Foto em bordado"),
        HomeAction(Icons.Rounded.Description, "Abrir Matriz", "DST real nesta versão"),
        HomeAction(Icons.Rounded.Folder, "Projetos", "Seus trabalhos"),
        HomeAction(Icons.Rounded.Collections, "Biblioteca", "Desenhos e fontes"),
        HomeAction(Icons.Rounded.Settings, "Minha Máquina", "Configure sua máquina")
    )
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(horizontal = 18.dp, vertical = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item { BrandHeader("Seu universo de bordados") }
        item {
            Column {
                Text("Olá!", fontSize = 24.sp, fontFamily = FontFamily.Serif, color = Cream)
                Text("Que vamos criar hoje?", color = Muted, fontSize = 14.sp)
            }
        }
        item {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.height(454.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                userScrollEnabled = false
            ) {
                items(actions) { action ->
                    LuxuryActionCard(action) {
                        when (action.title) {
                            "Abrir Matriz" -> onOpen()
                            "Criar Nome" -> onLettering()
                            "Minha Máquina" -> onMachine()
                            "Nova Matriz" -> onSoon("O editor de matriz ponto a ponto está entrando por etapas. Nesta 0.2.1 você já pode testar a nova linguagem visual Expressive e continuar usando o visualizador DST real.")
                            "Digitalizar Imagem" -> onSoon("A digitalização automática será conectada ao motor de vetorização e geração de pontos em uma próxima versão.")
                            "PhotoStitch" -> onSoon("O modo PhotoStitch está no roadmap. Primeiro vamos estabilizar visualizador, projetos, lettering e editor.")
                            "Projetos" -> onSoon("Use a aba Projetos na barra inferior. A persistência local chega na próxima etapa.")
                            "Biblioteca" -> onSoon("Use a aba Biblioteca na barra inferior para ver a estrutura inicial.")
                        }
                    }
                }
            }
        }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MiniFeature(Icons.Rounded.AutoAwesome, "Qualquer ideia", "em matriz", Modifier.weight(1f))
                MiniFeature(Icons.Rounded.PhoneAndroid, "Sem precisar", "de computador", Modifier.weight(1f))
                MiniFeature(Icons.Rounded.FavoriteBorder, "Feito para", "bordadores", Modifier.weight(1f))
            }
        }
        item { Text("BORDATTO Studio • Foundation 0.2.1 Expressive", color = Muted.copy(alpha = .7f), fontSize = 11.sp, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center) }
    }
}

@Composable
private fun LuxuryActionCard(action: HomeAction, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().aspectRatio(1.18f),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(containerColor = CardBrown),
        border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha = .65f))
    ) {
        Column(Modifier.fillMaxSize().padding(14.dp), verticalArrangement = Arrangement.Center) {
            ExpressiveIconBadge(action.icon, selected = true, size = 46.dp)
            Spacer(Modifier.height(10.dp))
            Text(action.title, color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
            Text(action.subtitle, color = Muted, fontSize = 10.sp, lineHeight = 13.sp)
        }
    }
}

@Composable
private fun MiniFeature(icon: ImageVector, title: String, subtitle: String, modifier: Modifier = Modifier) {
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(icon, null, tint = Gold, modifier = Modifier.size(22.dp))
        Spacer(Modifier.height(4.dp))
        Text(title.uppercase(), color = Cream.copy(alpha = .8f), fontSize = 8.sp, textAlign = TextAlign.Center)
        Text(subtitle.uppercase(), color = Muted, fontSize = 7.sp, textAlign = TextAlign.Center)
    }
}

@Composable
private fun CreateHubScreen(onOpen: () -> Unit, onLettering: () -> Unit, onSoon: (String) -> Unit) {
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { BrandHeader("Criação") }
        item { SectionTitle("Crie do seu jeito", "Ferramentas pensadas para bordado no celular") }
        item { WideStudioCard(Icons.Rounded.TextFields, "Criar Nome", "Lettering, nomes e monogramas", onLettering) }
        item { WideStudioCard(Icons.Rounded.Edit, "Editor de Matriz", "Ponto a ponto, objetos, contornos e preenchimentos") { onSoon("O editor avançado será liberado em etapas para conseguirmos testar cada ferramenta no celular com precisão.") } }
        item { WideStudioCard(Icons.Rounded.Image, "Digitalizar imagem", "Transforme arte em base de bordado") { onSoon("Digitalização automática ainda não está ativa nesta 0.2.1.") } }
        item { WideStudioCard(Icons.Rounded.Description, "Abrir matriz DST", "Visualizador real já funcional", onOpen) }
    }
}

@Composable
private fun ProjectsScreen(onCreate: () -> Unit) {
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { BrandHeader("Projetos") }
        item { SectionTitle("Seus projetos", "Organização local entra na próxima evolução") }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(24.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
                Column(Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    ExpressiveIconBadge(Icons.Rounded.Folder, selected = true, size = 58.dp)
                    Spacer(Modifier.height(12.dp))
                    Text("Nenhum projeto salvo ainda", color = Cream, fontWeight = FontWeight.SemiBold)
                    Text("Estamos validando o fluxo e a aparência antes de persistir arquivos e miniaturas.", color = Muted, fontSize = 12.sp, textAlign = TextAlign.Center)
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = onCreate, colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink), shape = RoundedCornerShape(18.dp)) {
                        Icon(Icons.Rounded.Add, null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Criar primeiro projeto")
                    }
                }
            }
        }
    }
}

private data class LibraryCategory(val name: String, val icon: ImageVector)

@Composable
private fun LibraryScreen(onSoon: (String) -> Unit) {
    val cats = listOf(
        LibraryCategory("Animais", Icons.Rounded.Pets),
        LibraryCategory("Flores", Icons.Rounded.LocalFlorist),
        LibraryCategory("Infantil", Icons.Rounded.ChildCare),
        LibraryCategory("Frases", Icons.Rounded.FormatQuote),
        LibraryCategory("Monogramas", Icons.Rounded.TextFields),
        LibraryCategory("Natal", Icons.Rounded.Star),
        LibraryCategory("Páscoa", Icons.Rounded.Celebration),
        LibraryCategory("Religiosos", Icons.Rounded.AutoAwesome),
        LibraryCategory("Apliques", Icons.Rounded.Layers)
    )
    Column(Modifier.fillMaxSize().padding(horizontal = 18.dp, vertical = 16.dp)) {
        BrandHeader("Biblioteca")
        Spacer(Modifier.height(16.dp))
        Surface(shape = RoundedCornerShape(20.dp), color = CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.Search, null, tint = Gold, modifier = Modifier.size(21.dp))
                Spacer(Modifier.width(10.dp))
                Text("Buscar matrizes...", color = Muted, fontSize = 13.sp)
            }
        }
        Spacer(Modifier.height(12.dp))
        LazyVerticalGrid(columns = GridCells.Fixed(3), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.weight(1f)) {
            items(cats) { cat ->
                Card(onClick = { onSoon("A categoria ${cat.name} será conectada à biblioteca local quando implementarmos importação e organização de arquivos.") }, colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(20.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.45f))) {
                    Column(Modifier.fillMaxWidth().aspectRatio(1f).padding(10.dp), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                        ExpressiveIconBadge(cat.icon, selected = false, size = 44.dp)
                        Spacer(Modifier.height(8.dp))
                        Text(cat.name, color = Cream, fontSize = 10.sp, textAlign = TextAlign.Center)
                    }
                }
            }
        }
    }
}

@Composable
private fun ProfileScreen(onMachine: () -> Unit, onSoon: (String) -> Unit) {
    data class ProfileItem(val icon: ImageVector, val title: String)
    val items = listOf(
        ProfileItem(Icons.Rounded.Person, "Minha Conta"),
        ProfileItem(Icons.Rounded.Folder, "Meus Projetos"),
        ProfileItem(Icons.Rounded.TextFields, "Minhas Fontes"),
        ProfileItem(Icons.Rounded.Cloud, "Backup na Nuvem"),
        ProfileItem(Icons.Rounded.Settings, "Preferências"),
        ProfileItem(Icons.Rounded.HelpOutline, "Ajuda e Suporte"),
        ProfileItem(Icons.Rounded.Info, "Sobre o BORDATTO")
    )
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        item { BrandHeader("Perfil") }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(24.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
                Row(Modifier.fillMaxWidth().padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.Person, selected = true, size = 56.dp)
                    Spacer(Modifier.width(14.dp))
                    Column {
                        Text("Meu Perfil", color = Cream, fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
                        Text("Bordatto • versão de testes", color = Muted, fontSize = 11.sp)
                    }
                }
            }
        }
        item { ProfileRow(Icons.Rounded.Settings, "Minhas Máquinas", onMachine) }
        items(items.size) { i -> ProfileRow(items[i].icon, items[i].title) { onSoon("${items[i].title} será ativado conforme avançarmos o projeto.") } }
        item {
            Column(Modifier.fillMaxWidth().padding(vertical = 16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.AutoAwesome, null, tint = Gold, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("BORDATTO Studio", color = Gold, fontFamily = FontFamily.Serif, fontSize = 18.sp)
                }
                Text("Seu universo de bordados • v0.2.1", color = Muted, fontSize = 10.sp)
            }
        }
    }
}

@Composable
private fun ProfileRow(icon: ImageVector, title: String, onClick: () -> Unit) {
    Surface(modifier = Modifier.fillMaxWidth().clickable(onClick = onClick), shape = RoundedCornerShape(18.dp), color = CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.4f))) {
        Row(Modifier.padding(horizontal = 14.dp, vertical = 13.dp), verticalAlignment = Alignment.CenterVertically) {
            ExpressiveIconBadge(icon, size = 40.dp)
            Spacer(Modifier.width(12.dp))
            Text(title, color = Cream, modifier = Modifier.weight(1f), fontSize = 13.sp)
            Icon(Icons.Rounded.ChevronRight, null, tint = Muted, modifier = Modifier.size(21.dp))
        }
    }
}

@Composable
private fun WideStudioCard(icon: ImageVector, title: String, subtitle: String, onClick: () -> Unit) {
    Card(onClick = onClick, colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
        Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            ExpressiveIconBadge(icon, selected = true, size = 50.dp)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Cream, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                Text(subtitle, color = Muted, fontSize = 11.sp)
            }
            Icon(Icons.Rounded.ChevronRight, null, tint = Gold, modifier = Modifier.size(22.dp))
        }
    }
}

@Composable
private fun SectionTitle(title: String, subtitle: String) {
    Column {
        Text(title, color = Cream, fontSize = 23.sp, fontFamily = FontFamily.Serif)
        Text(subtitle, color = Muted, fontSize = 12.sp)
    }
}

@Composable
private fun PageHeader(title: String, onBack: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = onBack) { Icon(Icons.Rounded.ArrowBack, "Voltar", tint = Gold) }
        Text(title, color = Cream, fontSize = 18.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
        ExpressiveIconBadge(Icons.Rounded.AutoAwesome, selected = true, size = 38.dp)
    }
}

@Composable
private fun LetteringScreen(onBack: () -> Unit, onGenerate: () -> Unit) {
    BackHandler(onBack = onBack)
    var name by remember { mutableStateOf("Maria") }
    var size by remember { mutableFloatStateOf(50f) }
    var spacing by remember { mutableFloatStateOf(0f) }
    var font by remember { mutableStateOf("Elegance") }
    val fonts = listOf("Regular", "Elegance", "Classic", "Sweet", "Handwriting")
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader("Criar Nome", onBack) }
        item {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Nome") },
                leadingIcon = { Icon(Icons.Rounded.TextFields, null, tint = Gold) },
                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Gold, unfocusedBorderColor = LineGold, focusedLabelColor = Gold)
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Cream), shape = RoundedCornerShape(26.dp)) {
                Box(Modifier.fillMaxWidth().height(185.dp), contentAlignment = Alignment.Center) {
                    Text(name.ifBlank { "BORDATTO" }, color = GoldDeep, fontSize = 48.sp, fontFamily = FontFamily.Cursive, textAlign = TextAlign.Center)
                }
            }
        }
        item { Text("Estilo da fonte", color = Cream, fontWeight = FontWeight.SemiBold) }
        items(fonts.size) { i ->
            val f = fonts[i]
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { font = f },
                shape = RoundedCornerShape(18.dp),
                color = if (font == f) Gold.copy(alpha=.16f) else CardBrown,
                border = androidx.compose.foundation.BorderStroke(1.dp, if (font == f) Gold.copy(alpha=.55f) else LineGold.copy(alpha=.45f))
            ) {
                Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
                    ExpressiveIconBadge(Icons.Rounded.TextFields, selected = font == f, size = 40.dp)
                    Spacer(Modifier.width(12.dp))
                    Text(if (f == "Elegance") name else "BORDATTO", color = Cream, fontFamily = if (f == "Elegance" || f == "Handwriting") FontFamily.Cursive else FontFamily.Serif, fontSize = 20.sp, modifier = Modifier.weight(1f))
                    Text(f, color = if (font == f) Gold else Muted, fontSize = 11.sp)
                }
            }
        }
        item {
            Text("Tamanho: ${size.toInt()} mm", color = Cream)
            Slider(size, { size = it }, valueRange = 10f..150f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
            Text("Espaçamento: ${spacing.toInt()}%", color = Cream)
            Slider(spacing, { spacing = it }, valueRange = -20f..50f, colors = SliderDefaults.colors(thumbColor = Gold, activeTrackColor = Gold))
        }
        item {
            Button(onClick = onGenerate, modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(20.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)) {
                Icon(Icons.Rounded.AutoAwesome, null)
                Spacer(Modifier.width(8.dp))
                Text("Gerar Matriz", fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun MachineScreen(onBack: () -> Unit, onSave: () -> Unit) {
    BackHandler(onBack = onBack)
    var brand by remember { mutableStateOf("Brother") }
    var model by remember { mutableStateOf("PE770") }
    var format by remember { mutableStateOf("PES") }
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader("Minha Máquina", onBack) }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = CardBrown), shape = RoundedCornerShape(26.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
                Column(Modifier.fillMaxWidth().padding(22.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    ExpressiveIconBadge(Icons.Rounded.Settings, selected = true, size = 72.dp)
                    Spacer(Modifier.height(10.dp))
                    Text("Configuração da máquina", color = Cream, fontWeight = FontWeight.SemiBold)
                    Text("Use estes dados para preparar exportações futuras.", color = Muted, fontSize = 11.sp, textAlign = TextAlign.Center)
                }
            }
        }
        item { SimpleChoice("Marca", brand, listOf("Brother", "Janome", "Singer", "Bernina")) { brand = it } }
        item { SimpleChoice("Modelo", model, listOf("PE770", "SE600", "NV180", "Outro")) { model = it } }
        item { SimpleChoice("Formato principal", format, listOf("PES", "DST", "JEF", "EXP")) { format = it } }
        item {
            Button(onClick = onSave, modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(20.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold, contentColor = Ink)) {
                Icon(Icons.Rounded.Save, null)
                Spacer(Modifier.width(8.dp))
                Text("Salvar Configurações", fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun SimpleChoice(label: String, value: String, options: List<String>, onChange: (String) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    Column {
        Text(label, color = Muted, fontSize = 11.sp)
        Spacer(Modifier.height(5.dp))
        Box {
            Surface(modifier = Modifier.fillMaxWidth().clickable { expanded = true }, color = CardBrown, shape = RoundedCornerShape(16.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.5f))) {
                Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(value, color = Cream, modifier = Modifier.weight(1f))
                    Icon(Icons.Rounded.ExpandMore, null, tint = Gold)
                }
            }
            DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                options.forEach { option -> DropdownMenuItem(text = { Text(option) }, onClick = { onChange(option); expanded = false }) }
            }
        }
    }
}

@Composable
private fun ViewerScreen(design: Design, onBack: () -> Unit) {
    BackHandler(onBack = onBack)
    var zoom by remember { mutableFloatStateOf(1f) }
    var pan by remember { mutableStateOf(Offset.Zero) }
    var grid by remember { mutableStateOf(true) }
    var info by remember { mutableStateOf(true) }
    val transform = rememberTransformableState { z, p, _ ->
        zoom = (zoom * z).coerceIn(.25f, 20f)
        pan += p
    }
    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.Rounded.ArrowBack, "Voltar", tint = Gold) }
            Column(Modifier.weight(1f)) {
                Text(design.name, color = Cream, fontWeight = FontWeight.SemiBold, maxLines = 1)
                Text("DST • ${design.stitchCount} pontos • ${"%.1f".format(design.width)} × ${"%.1f".format(design.height)} mm", fontSize = 11.sp, color = Muted)
            }
            ExpressiveIconBadge(Icons.Rounded.Visibility, selected = true, size = 40.dp)
        }
        Row(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ViewerTool(Icons.Rounded.GridOn, "Grade", grid) { grid = !grid }
            ViewerTool(Icons.Rounded.Info, "Info", info) { info = !info }
            ViewerTool(Icons.Rounded.CenterFocusStrong, "Centralizar", false) { zoom = 1f; pan = Offset.Zero }
        }
        Box(
            Modifier.weight(1f).fillMaxWidth().background(Ink).transformable(transform).pointerInput(Unit) {
                detectTapGestures(onDoubleTap = { zoom = 1f; pan = Offset.Zero })
            }
        ) {
            StitchCanvas(design, zoom, pan, grid, Modifier.fillMaxSize())
            if (info) {
                Card(Modifier.align(Alignment.TopEnd).padding(12.dp), colors = CardDefaults.cardColors(containerColor = SurfaceBrown.copy(alpha=.96f)), shape = RoundedCornerShape(20.dp), border = androidx.compose.foundation.BorderStroke(1.dp, LineGold.copy(alpha=.55f))) {
                    Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.Analytics, null, tint = Gold, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Análise", color = Gold, fontWeight = FontWeight.SemiBold)
                        }
                        Text("Pontadas: ${design.stitchCount}", fontSize=12.sp, color = Cream)
                        Text("Saltos: ${design.jumpCount}", fontSize=12.sp, color = Cream)
                        Text("Trocas de cor: ${design.colorChanges}", fontSize=12.sp, color = Cream)
                        Text("Cores: ${design.colors}", fontSize=12.sp, color = Cream)
                    }
                }
            }
        }
        Surface(color = Chocolate) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.ZoomIn, null, tint = Gold, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(7.dp))
                Text("${"%.0f".format(zoom * 100)}%", color = Cream, fontSize = 12.sp)
                Spacer(Modifier.weight(1f))
                Text("Pinça • arraste • duplo toque", color = Muted, fontSize = 11.sp)
            }
        }
    }
}

@Composable
private fun ViewerTool(icon: ImageVector, label: String, selected: Boolean, onClick: () -> Unit) {
    Surface(modifier = Modifier.clickable(onClick = onClick), shape = RoundedCornerShape(18.dp), color = if (selected) Gold.copy(alpha=.16f) else CardBrown, border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) Gold.copy(alpha=.52f) else LineGold.copy(alpha=.5f))) {
        Row(Modifier.padding(horizontal = 12.dp, vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, label, tint = if (selected) Gold else Muted, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(6.dp))
            Text(label, color = if (selected) Gold else Cream, fontSize = 11.sp)
        }
    }
}

@Composable
private fun StitchCanvas(design: Design, zoom: Float, pan: Offset, grid: Boolean, modifier: Modifier) {
    val palette = listOf(Gold, Color(0xFFF1E3C6), Color(0xFFBE7C4D), Color(0xFFA96A5B), Color(0xFF7A9273), Color(0xFFE3C17A))
    Canvas(modifier) {
        if (grid) {
            val step = max(24f, 20f * zoom)
            var gx = pan.x % step
            while (gx < size.width) { drawLine(Color.White.copy(alpha=.05f), Offset(gx,0f), Offset(gx,size.height)); gx += step }
            var gy = pan.y % step
            while (gy < size.height) { drawLine(Color.White.copy(alpha=.05f), Offset(0f,gy), Offset(size.width,gy)); gy += step }
        }
        if (design.stitches.isEmpty()) return@Canvas
        val w = max(1f, design.width)
        val h = max(1f, design.height)
        val fit = min(size.width / w, size.height / h) * .82f
        val px = fit * zoom
        val center = Offset(size.width/2 + pan.x, size.height/2 + pan.y)
        val cx=(design.minX+design.maxX)/2
        val cy=(design.minY+design.maxY)/2
        fun map(x:Float,y:Float)=Offset(center.x+(x-cx)*px, center.y+(y-cy)*px)
        val paths=mutableMapOf<Int, Path>()
        var previous:Offset?=null
        var prevColor=-1
        for (st in design.stitches) {
            val cur=map(st.x,st.y)
            if (st.command==StitchCommand.STITCH) {
                val path=paths.getOrPut(st.color){Path()}
                if (previous==null || prevColor!=st.color) path.moveTo(cur.x,cur.y) else path.lineTo(cur.x,cur.y)
            } else previous=null
            previous=cur
            prevColor=st.color
        }
        paths.forEach { (i,p) -> drawPath(p, palette[i%palette.size], style=Stroke(max(1.2f,1.3f*zoom.coerceAtMost(3f)), cap=StrokeCap.Round)) }
    }
}

private fun parseDst(fileName: String, bytes: ByteArray): Design {
    require(bytes.size >= 512) { "Arquivo DST inválido ou incompleto." }
    val header = bytes.copyOfRange(0, 512).toString(Charsets.US_ASCII)
    val label = header.lineSequence().firstOrNull { it.startsWith("LA:") }?.removePrefix("LA:")?.trim()?.takeIf { it.isNotBlank() } ?: fileName.substringBeforeLast('.')
    val pts=ArrayList<StitchPoint>()
    var x=0
    var y=0
    var color=0
    var minX=0
    var maxX=0
    var minY=0
    var maxY=0
    var o=512
    while (o+2 < bytes.size) {
        val a=bytes[o].toInt() and 255
        val b=bytes[o+1].toInt() and 255
        val c=bytes[o+2].toInt() and 255
        o+=3
        if ((c and 0xF3)==0xF3) { pts += StitchPoint(x/10f,y/10f,StitchCommand.END,color); break }
        x += decodeX(a,b,c)
        y -= decodeY(a,b,c)
        minX=min(minX,x)
        maxX=max(maxX,x)
        minY=min(minY,y)
        maxY=max(maxY,y)
        val command = when {
            (c and 0xC3)==0xC3 -> StitchCommand.COLOR_CHANGE
            (c and 0x83)==0x83 -> StitchCommand.JUMP
            else -> StitchCommand.STITCH
        }
        if (command==StitchCommand.COLOR_CHANGE) color++
        pts += StitchPoint(x/10f,y/10f,command,color)
    }
    return Design(label, pts, minX/10f,minY/10f,maxX/10f,maxY/10f,color+1)
}

private fun decodeX(a:Int,b:Int,c:Int):Int {
    var x=0
    if(a and 1!=0)x+=1
    if(a and 2!=0)x-=1
    if(a and 4!=0)x+=9
    if(a and 8!=0)x-=9
    if(b and 1!=0)x+=3
    if(b and 2!=0)x-=3
    if(b and 4!=0)x+=27
    if(b and 8!=0)x-=27
    if(c and 4!=0)x+=81
    if(c and 8!=0)x-=81
    return x
}

private fun decodeY(a:Int,b:Int,c:Int):Int {
    var y=0
    if(a and 0x80!=0)y+=1
    if(a and 0x40!=0)y-=1
    if(a and 0x20!=0)y+=9
    if(a and 0x10!=0)y-=9
    if(b and 0x80!=0)y+=3
    if(b and 0x40!=0)y-=3
    if(b and 0x20!=0)y+=27
    if(b and 0x10!=0)y-=27
    if(c and 0x20!=0)y+=81
    if(c and 0x10!=0)y-=81
    return y
}
