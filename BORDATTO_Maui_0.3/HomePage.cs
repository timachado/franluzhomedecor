using BordattoStudio.Core;

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
            Content = Label("MAUI • SKIA", 10, BordattoColors.Gold, FontAttributes.Bold)
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
            b.Clicked += async (_, _) =>
            {
                if (idx == 1)
                {
                    await Navigation.PushAsync(new MainPage());
                    return;
                }
                ShowTab(idx);
            };
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
            if (_navButtons[i] is null) continue;
            _navButtons[i].TextColor = i == index ? BordattoColors.Gold : BordattoColors.Muted;
            _navButtons[i].BackgroundColor = i == index ? Color.FromArgb("#2A160F") : Colors.Transparent;
        }

        _body.Content = index switch
        {
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
        heroStack.Add(Label("Tradicional para um fluxo simples ou Studio Pro com controles técnicos. Ambos usam o mesmo núcleo de pontadas.", 12, BordattoColors.Muted));
        var create = Primary("✦  NOVO BORDADO");
        create.Clicked += async (_, _) => await Navigation.PushAsync(new MainPage());
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
        AddTool(tools, 0, 0, "Aa", "Lettering", "Criar nomes e textos", async () => await Navigation.PushAsync(new MainPage()));
        AddTool(tools, 1, 0, "▶", "Simulação", "Sequência real das pontadas", async () => await DisplayAlertAsync("Simulação", "Gere ou abra uma matriz e toque em ▶ para simular.", "OK"));
        AddTool(tools, 0, 1, "✓", "Machine Check", "Validação antes da máquina", async () => await DisplayAlertAsync("Machine Check", "O Machine Check continua no roteiro de portabilidade para a base MAUI. O motor de geração e simulação já está ativo nesta versão.", "OK"));
        AddTool(tools, 1, 1, "≋", "Analyzer", "Diagnóstico da matriz", async () => await DisplayAlertAsync("Analyzer", "O Analyzer será conectado ao mesmo design gerado pelo novo motor.", "OK"));
        AddTool(tools, 0, 2, "⇩", "Exportar", "PES • JEF • DST", async () => await DisplayAlertAsync("Exportação", "A exportação multi-formato está sendo portada para a base MAUI sem alterar o novo motor.", "OK"));
        AddTool(tools, 1, 2, "$", "Custos", "Linha, tempo e produção", async () => await DisplayAlertAsync("Calculadora", "A calculadora profissional será reativada no menu completo.", "OK"));
        stack.Add(tools);

        stack.Add(Label("Motor atual", 15, BordattoColors.Cream, FontAttributes.Bold));
        var engine = new Border
        {
            Stroke = Color.FromArgb("#3D281D"), StrokeThickness = 1,
            BackgroundColor = Color.FromArgb("#1B110D"), Padding = new Thickness(16, 13),
            Content = Label("SkiaSharp • Satin orientado ao traço • Underlay local • Tradicional + Studio Pro", 12, BordattoColors.Muted)
        };
        stack.Add(engine);

        return new ScrollView { Content = stack };
    }

    private View BuildProjects()
    {
        var stack = PageStack("Projetos", "Seus bordados ficam organizados aqui.");
        var newProject = Primary("+  NOVO PROJETO");
        newProject.Clicked += async (_, _) => await Navigation.PushAsync(new MainPage());
        stack.Add(newProject);
        stack.Add(Card("Projetos recentes", "Os projetos criados nesta nova base aparecerão aqui conforme o armazenamento persistente for religado."));
        stack.Add(Card("Histórico de exportação", "Rastreabilidade por formato, data e máquina."));
        return new ScrollView { Content = stack };
    }

    private View BuildLibrary()
    {
        var stack = PageStack("Biblioteca", "Recursos de bordado e referências técnicas.");
        stack.Add(Card("Linhas", "Brother • Madeira • cores e códigos"));
        stack.Add(Card("Bastidores", "Perfis e limites de área útil"));
        stack.Add(Card("Máquinas", "Perfis para Machine Check e tempo estimado"));
        stack.Add(Card("Formatos", "DST • PES • JEF e demais formatos do BORDATTO"));
        stack.Add(Card("Lettering", "Fontes e presets de Satin"));
        return new ScrollView { Content = stack };
    }

    private View BuildProfile()
    {
        var stack = PageStack("Perfil", "BORDATTO Studio");
        stack.Add(Card("Versão", "0.3.2 • MAUI/Skia engine"));
        stack.Add(Card("Modo Tradicional", "Fluxo simplificado com motor compartilhado"));
        stack.Add(Card("Studio Pro", "Densidade, compensação e underlay avançados"));
        stack.Add(Card("Diagnóstico", "Inicialização protegida e registro de falhas Android"));
        return new ScrollView { Content = stack };
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
