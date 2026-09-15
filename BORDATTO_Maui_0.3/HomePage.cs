using BordattoStudio.Core;
using Microsoft.Maui.Storage;

namespace BordattoStudio;

public sealed class HomePage : ContentPage
{
    private readonly ContentView _body = new();
    private readonly Button[] _navButtons = new Button[5];
    private int _activeTab;

    public HomePage()
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;

        var root = new Grid
        {
            RowDefinitions =
            {
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Star),
                new RowDefinition(GridLength.Auto)
            }
        };
        var header = BuildHeader();
        root.Add(header); root.SetRow(header, 0);
        root.Add(_body); root.SetRow(_body, 1);
        var nav = BuildBottomNavigation();
        root.Add(nav); root.SetRow(nav, 2);
        Content = root;
        ShowTab(0);
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        if (_activeTab == 2) _body.Content = BuildProjects();
    }

    private View BuildHeader()
    {
        var title = new VerticalStackLayout { Spacing = 1 };
        title.Add(Label("BORDATTO Studio", 24, BordattoColors.Cream, FontAttributes.Bold));
        title.Add(Label("Da ideia à matriz. Tudo pelo celular.", 11, BordattoColors.Muted));
        var badge = new Border
        {
            Stroke = Color.FromArgb("#5A3827"),
            StrokeThickness = 1,
            BackgroundColor = BordattoColors.Panel,
            Padding = new Thickness(12, 8),
            Content = Label("0.3.6 • MAUI/SKIA", 9, BordattoColors.Gold, FontAttributes.Bold)
        };
        var g = new Grid
        {
            Padding = new Thickness(20, 14, 16, 10),
            ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) }
        };
        g.Add(title); g.Add(badge); g.SetColumn(badge, 1);
        return g;
    }

    private View BuildBottomNavigation()
    {
        var nav = new Grid
        {
            Padding = new Thickness(4, 7, 4, 10),
            ColumnSpacing = 0,
            BackgroundColor = Color.FromArgb("#140C09"),
            ColumnDefinitions =
            {
                new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(GridLength.Star)
            }
        };
        var items = new[]
        {
            ("⌂\nInício", 0), ("✦\nCriar", 1), ("▣\nProjetos", 2),
            ("▤\nBiblioteca", 3), ("●\nPerfil", 4)
        };
        foreach (var (item, i) in items)
        {
            var b = new Button
            {
                Text = item,
                FontSize = 10,
                HeightRequest = 58,
                CornerRadius = 14,
                BackgroundColor = Colors.Transparent,
                TextColor = BordattoColors.Muted,
                Padding = new Thickness(2)
            };
            var idx = i;
            b.Clicked += (_, _) => ShowTab(idx);
            _navButtons[i] = b;
            nav.Add(b); nav.SetColumn(b, i);
        }
        return nav;
    }

    private void ShowTab(int index)
    {
        _activeTab = index;
        for (var i = 0; i < _navButtons.Length; i++)
        {
            _navButtons[i].TextColor = i == index ? BordattoColors.Gold : BordattoColors.Muted;
            _navButtons[i].BackgroundColor = i == index ? Color.FromArgb("#2A160F") : Colors.Transparent;
        }

        _body.Content = index switch
        {
            1 => BuildCreate(),
            2 => BuildProjects(),
            3 => BuildLibrary(),
            4 => BuildProfile(),
            _ => BuildHome()
        };
    }

    private View BuildHome()
    {
        var stack = new VerticalStackLayout { Padding = new Thickness(18, 6, 18, 20), Spacing = 14 };

        var hero = new Border
        {
            Stroke = Color.FromArgb("#553321"), StrokeThickness = 1,
            BackgroundColor = BordattoColors.Panel,
            Padding = new Thickness(20, 18)
        };
        var heroStack = new VerticalStackLayout { Spacing = 10 };
        heroStack.Add(Label("Criar novo bordado", 22, BordattoColors.Cream, FontAttributes.Bold));
        heroStack.Add(Label("Tradicional para um fluxo simples ou Studio Pro com controles técnicos. Os dois usam o motor Satin adaptativo com correção de contraformas.", 12, BordattoColors.Muted));
        var create = Primary("✦  NOVO BORDADO");
        create.Clicked += async (_, _) => await Navigation.PushAsync(new MainPage(BordattoMode.Tradicional));
        heroStack.Add(create);
        hero.Content = heroStack;
        stack.Add(hero);

        stack.Add(Label("Ferramentas", 17, BordattoColors.Cream, FontAttributes.Bold));
        var tools = new Grid
        {
            ColumnSpacing = 10, RowSpacing = 10,
            ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) },
            RowDefinitions = { new RowDefinition(GridLength.Auto), new RowDefinition(GridLength.Auto), new RowDefinition(GridLength.Auto) }
        };
        AddTool(tools, 0, 0, "Aa", "Lettering", "Tradicional", async () => await Navigation.PushAsync(new MainPage(BordattoMode.Tradicional)));
        AddTool(tools, 1, 0, "✦", "Studio Pro", "Editor responsivo + aba PRO", async () => await Navigation.PushAsync(new MainPage(BordattoMode.StudioPro)));
        AddTool(tools, 0, 1, "⚙", "Máquina", "Perfil, velocidade e bastidor", async () => await Navigation.PushAsync(new MachinePage()));
        AddTool(tools, 1, 1, "R$", "Custos", "Tempo e produção", async () => await Navigation.PushAsync(new CostPage()));
        AddTool(tools, 0, 2, "▶", "Simulação", "Abra pelo editor da matriz", async () => await DisplayAlertAsync("Simulação", "Crie uma matriz e toque no botão ▶ do editor para executar a sequência real de pontadas.", "OK"));
        AddTool(tools, 1, 2, "✓", "Machine Check", "Validação pelo perfil salvo", async () => await ShowMachineCheckInfo());
        stack.Add(tools);

        stack.Add(Label("Motor 0.3.5 • Editor 0.3.6", 15, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(Card("Satin adaptativo", "Eixo local da letra → underlay → pares Satin pelas bordas reais → correção de contraformas e deslocamentos locais. O editor 0.3.6 acrescenta manipulação direta no bastidor."));
        return new ScrollView { Content = stack };
    }

    private View BuildCreate()
    {
        var stack = PageStack("Criar", "Escolha como começar seu bordado.");
        stack.Add(ActionCard("Aa", "Lettering Tradicional", "Texto → matriz → editor → simulação", async () => await Navigation.PushAsync(new MainPage(BordattoMode.Tradicional))));
        stack.Add(ActionCard("✦", "Lettering Studio Pro", "Editor responsivo + densidade, compensação, underlay e Satin", async () => await Navigation.PushAsync(new MainPage(BordattoMode.StudioPro))));
        stack.Add(ActionCard("▧", "Abrir matriz", "Selecionar um arquivo do aparelho", PickMatrixAsync));
        stack.Add(Card("Imagem / desenho", "O digitalizador visual ainda está em portabilidade para MAUI. Ele permanece visível no fluxo para não desaparecer do aplicativo."));
        return new ScrollView { Content = stack };
    }

    private View BuildProjects()
    {
        var stack = PageStack("Projetos", "Matrizes criadas recentemente nesta base.");
        var newProject = Primary("+  NOVO PROJETO");
        newProject.Clicked += async (_, _) => await Navigation.PushAsync(new MainPage(BordattoMode.Tradicional));
        stack.Add(newProject);
        var recent = ProjectStore.Load();
        if (recent.Count == 0)
        {
            stack.Add(Card("Nenhum projeto salvo ainda", "Gere uma matriz no Tradicional ou Studio Pro e ela aparecerá aqui."));
        }
        else
        {
            foreach (var p in recent)
                stack.Add(Card(p.Name, $"{p.Mode} • {p.Stitches:N0} pts • {p.WidthMm:0.0} × {p.HeightMm:0.0} mm\nAtualizado {p.UpdatedAt:dd/MM HH:mm}"));
        }
        return new ScrollView { Content = stack };
    }

    private View BuildLibrary()
    {
        var stack = PageStack("Biblioteca", "Arquivos, linhas, bastidores e referências.");
        stack.Add(ActionCard("▧", "Abrir arquivo do aparelho", "DST • PES • JEF • VP3 • EXP e outros", PickMatrixAsync));
        stack.Add(Card("Linhas", "Brother • Madeira • cores e códigos de referência"));
        stack.Add(Card("Bastidores", "100×100 • 130×180 • 160×260 • 200×300 mm"));
        stack.Add(Card("Formatos", "A leitura completa dos formatos do motor 0.2.x será reconectada nesta aba; selecionar arquivo já funciona nesta base."));
        return new ScrollView { Content = stack };
    }

    private View BuildProfile()
    {
        var stack = PageStack("Perfil", "Configurações do BORDATTO Studio.");
        stack.Add(Card("Versão", "0.3.6 • .NET MAUI 10 • SkiaSharp 4.152"));
        stack.Add(ActionCard("⚙", "Configuração da máquina", "Velocidade e bastidor", async () => await Navigation.PushAsync(new MachinePage())));
        stack.Add(ActionCard("R$", "Calculadora de custos", "Linha, máquina e tempo", async () => await Navigation.PushAsync(new CostPage())));
        stack.Add(Card("Tradicional + Studio Pro", "Os dois modos compartilham o motor Satin adaptativo. O Studio Pro expõe uma aba PRO dedicada aos parâmetros técnicos."));
        return new ScrollView { Content = stack };
    }

    private async Task PickMatrixAsync()
    {
        try
        {
            var result = await FilePicker.Default.PickAsync(new PickOptions { PickerTitle = "Selecionar matriz de bordado" });
            if (result is null) return;
            await DisplayAlertAsync("Arquivo selecionado", $"{result.FileName}\n\nO seletor está ativo. A importação completa de pontos do motor 0.2.x ainda será reconectada ao núcleo MAUI.", "OK");
        }
        catch (Exception ex)
        {
            await DisplayAlertAsync("BORDATTO", ex.Message, "OK");
        }
    }

    private async Task ShowMachineCheckInfo()
    {
        var speed = Preferences.Default.Get("machine_speed", 750d);
        var hoopIndex = Preferences.Default.Get("machine_hoop", 0);
        var hoops = new[] { "100 × 100 mm", "130 × 180 mm", "160 × 260 mm", "200 × 300 mm" };
        hoopIndex = Math.Clamp(hoopIndex, 0, hoops.Length - 1);
        await DisplayAlertAsync("Machine Check", $"Perfil ativo\nVelocidade: {speed:0} pts/min\nBastidor: {hoops[hoopIndex]}\n\nA matriz gerada mostra dimensões e pontos no editor antes da simulação.", "OK");
    }

    private static VerticalStackLayout PageStack(string title, string subtitle)
    {
        var stack = new VerticalStackLayout { Padding = new Thickness(18, 12, 18, 20), Spacing = 12 };
        stack.Add(Label(title, 25, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(Label(subtitle, 12, BordattoColors.Muted));
        return stack;
    }

    private static Border Card(string title, string subtitle)
    {
        var content = new VerticalStackLayout { Spacing = 5 };
        content.Add(Label(title, 15, BordattoColors.Cream, FontAttributes.Bold));
        content.Add(Label(subtitle, 11, BordattoColors.Muted));
        return new Border
        {
            Stroke = Color.FromArgb("#452B1E"), StrokeThickness = 1,
            BackgroundColor = BordattoColors.Panel, Padding = new Thickness(16, 14),
            Content = content
        };
    }

    private static Border ActionCard(string icon, string title, string subtitle, Func<Task> action)
    {
        var card = Card($"{icon}   {title}", subtitle);
        var tap = new TapGestureRecognizer();
        tap.Tapped += async (_, _) => await action();
        card.GestureRecognizers.Add(tap);
        return card;
    }

    private static void AddTool(Grid grid, int col, int row, string icon, string title, string subtitle, Func<Task> action)
    {
        var stack = new VerticalStackLayout { Spacing = 5 };
        stack.Add(Label(icon, 23, BordattoColors.Gold, FontAttributes.Bold));
        stack.Add(Label(title, 14, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(Label(subtitle, 10, BordattoColors.Muted));
        var border = new Border
        {
            Stroke = Color.FromArgb("#452B1E"), StrokeThickness = 1,
            BackgroundColor = BordattoColors.Panel, Padding = new Thickness(14, 12),
            Content = stack
        };
        var tap = new TapGestureRecognizer();
        tap.Tapped += async (_, _) => await action();
        border.GestureRecognizers.Add(tap);
        grid.Add(border); grid.SetColumn(border, col); grid.SetRow(border, row);
    }

    private static Button Primary(string text) => new()
    {
        Text = text, HeightRequest = 58, CornerRadius = 17,
        BackgroundColor = BordattoColors.Gold, TextColor = Color.FromArgb("#17100C"),
        FontAttributes = FontAttributes.Bold, FontSize = 14
    };

    private static Label Label(string text, double size, Color color, FontAttributes attrs = FontAttributes.None)
        => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs };
}
