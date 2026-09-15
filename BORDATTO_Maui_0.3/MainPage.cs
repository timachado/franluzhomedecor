using BordattoStudio.Core;
using BordattoStudio.Views;

namespace BordattoStudio;

public sealed class MainPage : ContentPage
{
    private readonly TextObjectModel _model = new();
    private EngineSettings _settings = EngineSettings.TraditionalPreset();
    private BordattoMode _mode = BordattoMode.Tradicional;
    private readonly InteractiveTextCanvas _canvas;
    private readonly VerticalStackLayout _optionsHost;
    private readonly Button _traditionalButton;
    private readonly Button _studioButton;
    private readonly Label _modeHint;
    private readonly Entry _entry;
    private string _activeTab = "Fonte";

    public MainPage()
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;
        _canvas = new InteractiveTextCanvas { Model = _model, HeightRequest = 520 };
        _canvas.ModelChanged += (_, _) => { };
        _optionsHost = new VerticalStackLayout { Spacing = 10 };
        _modeHint = NewLabel("TRADICIONAL", 11, BordattoColors.Gold, FontAttributes.Bold);
        _entry = new Entry
        {
            Text = _model.Text,
            TextColor = BordattoColors.Cream,
            BackgroundColor = Color.FromArgb("#160D09"),
            FontSize = 22,
            Placeholder = "Digite o nome",
            PlaceholderColor = BordattoColors.Muted,
            Margin = new Thickness(0, 2)
        };
        _entry.TextChanged += (_, e) =>
        {
            _model.Text = string.IsNullOrWhiteSpace(e.NewTextValue) ? " " : e.NewTextValue[..Math.Min(28, e.NewTextValue.Length)];
            _canvas.InvalidateSurface();
        };

        _traditionalButton = Segment("TRADICIONAL", () => SetMode(BordattoMode.Tradicional));
        _studioButton = Segment("✦ STUDIO PRO", () => SetMode(BordattoMode.StudioPro));

        var root = new Grid
        {
            RowDefinitions =
            {
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Star),
                new RowDefinition(GridLength.Auto)
            }
        };
        root.Add(BuildHeader()); Grid.SetRow(root.Children[^1], 0);
        root.Add(BuildModeSwitcher()); Grid.SetRow(root.Children[^1], 1);
        root.Add(_canvas); Grid.SetRow(_canvas, 2);
        root.Add(BuildBottomSheet()); Grid.SetRow(root.Children[^1], 3);
        Content = root;

        SetMode(BordattoMode.Tradicional);
        ShowTab("Fonte");
    }

    private View BuildHeader()
    {
        var back = new Button { Text = "‹", FontSize = 35, TextColor = BordattoColors.Gold, BackgroundColor = Colors.Transparent, WidthRequest = 54, HeightRequest = 54, Padding = 0 };
        var title = NewLabel("Novo bordado", 25, BordattoColors.Cream, FontAttributes.Bold);
        var sparkle = new Border
        {
            Stroke = BordattoColors.Gold,
            StrokeThickness = 1,
            BackgroundColor = Color.FromArgb("#2A160F"),
            WidthRequest = 54,
            HeightRequest = 54,
            Content = NewLabel("✦", 24, BordattoColors.Gold, FontAttributes.Bold, TextAlignment.Center)
        };
        var grid = new Grid { Padding = new Thickness(14, 10, 14, 6), ColumnDefinitions = { new ColumnDefinition(GridLength.Auto), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        grid.Add(back); Grid.SetColumn(back, 0);
        grid.Add(title); Grid.SetColumn(title, 1); title.VerticalTextAlignment = TextAlignment.Center;
        grid.Add(sparkle); Grid.SetColumn(sparkle, 2);
        return grid;
    }

    private View BuildModeSwitcher()
    {
        var grid = new Grid
        {
            Padding = new Thickness(22, 6, 22, 10),
            ColumnSpacing = 8,
            ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) }
        };
        grid.Add(_traditionalButton); Grid.SetColumn(_traditionalButton, 0);
        grid.Add(_studioButton); Grid.SetColumn(_studioButton, 1);
        return grid;
    }

    private View BuildBottomSheet()
    {
        var titleRow = new Grid { ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        var textTitle = NewLabel("Texto", 18, BordattoColors.Cream, FontAttributes.Bold);
        var done = new Button { Text = "Concluir", TextColor = BordattoColors.Gold, BackgroundColor = Colors.Transparent, FontAttributes = FontAttributes.Bold, Padding = new Thickness(10, 0) };
        titleRow.Add(textTitle); titleRow.Add(done); Grid.SetColumn(done, 1);

        var tabs = new Grid { ColumnSpacing = 5, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var names = new[] { "Fonte", "Tamanho", "Cor", "Estilo" };
        for (var i = 0; i < names.Length; i++)
        {
            var n = names[i];
            var b = new Button { Text = n, FontSize = 12, HeightRequest = 48, CornerRadius = 15, BackgroundColor = Color.FromArgb("#351D13"), TextColor = BordattoColors.Cream };
            b.Clicked += (_, _) => ShowTab(n);
            tabs.Add(b); Grid.SetColumn(b, i);
        }

        var generate = new Button
        {
            Text = "▶  CONCLUIR E GERAR MATRIZ",
            BackgroundColor = BordattoColors.Gold,
            TextColor = Color.FromArgb("#17100C"),
            FontAttributes = FontAttributes.Bold,
            FontSize = 14,
            HeightRequest = 62,
            CornerRadius = 18
        };
        generate.Clicked += async (_, _) => await GenerateAsync();
        done.Clicked += async (_, _) => await GenerateAsync();

        var stack = new VerticalStackLayout { Spacing = 10, Padding = new Thickness(22, 14, 22, 20) };
        stack.Add(titleRow);
        stack.Add(_entry);
        stack.Add(tabs);
        stack.Add(_optionsHost);
        stack.Add(_modeHint);
        stack.Add(generate);
        return new Border { Stroke = Color.FromArgb("#4B2A1B"), StrokeThickness = 1, BackgroundColor = Color.FromArgb("#21120D"), Content = stack };
    }

    private void SetMode(BordattoMode mode)
    {
        _mode = mode;
        _settings = mode == BordattoMode.Tradicional ? EngineSettings.TraditionalPreset() : EngineSettings.StudioPreset();
        _traditionalButton.BackgroundColor = mode == BordattoMode.Tradicional ? BordattoColors.Gold : BordattoColors.PanelSoft;
        _traditionalButton.TextColor = mode == BordattoMode.Tradicional ? Color.FromArgb("#19100B") : BordattoColors.Cream;
        _studioButton.BackgroundColor = mode == BordattoMode.StudioPro ? BordattoColors.Gold : BordattoColors.PanelSoft;
        _studioButton.TextColor = mode == BordattoMode.StudioPro ? Color.FromArgb("#19100B") : BordattoColors.Cream;
        _modeHint.Text = mode == BordattoMode.Tradicional ? "TRADICIONAL • simples, direto e funcional" : "STUDIO PRO • mesmo motor com controles técnicos avançados";
        ShowTab(_activeTab);
    }

    private void ShowTab(string name)
    {
        _activeTab = name;
        _optionsHost.Clear();
        if (name == "Fonte") BuildFontOptions();
        else if (name == "Tamanho") BuildSizeOptions();
        else if (name == "Cor") BuildColorOptions();
        else BuildStyleOptions();
        if (_mode == BordattoMode.StudioPro) BuildProfessionalOptions();
    }

    private void BuildFontOptions()
    {
        var grid = new Grid { ColumnSpacing = 6, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var fonts = new (string Label, string Family, bool Bold, bool Italic)[]
        {
            ("Regular", "sans-serif", false, false),
            ("Elegance", "serif", false, true),
            ("Classic", "sans-serif", true, false),
            ("Handwriting", "cursive", false, false)
        };
        for (var i = 0; i < fonts.Length; i++)
        {
            var f = fonts[i];
            var b = new Button { Text = $"Aa\n{f.Label}", FontSize = 15, HeightRequest = 76, CornerRadius = 15, BackgroundColor = BordattoColors.PanelSoft, TextColor = BordattoColors.Cream };
            b.Clicked += (_, _) => { _model.FontFamily = f.Family; _model.Bold = f.Bold; _model.Italic = f.Italic; _canvas.InvalidateSurface(); };
            grid.Add(b); Grid.SetColumn(b, i);
        }
        _optionsHost.Add(grid);
    }

    private void BuildSizeOptions()
    {
        var value = NewLabel($"{_model.HeightMm:0} mm", 22, BordattoColors.Gold, FontAttributes.Bold);
        var slider = new Slider { Minimum = 5, Maximum = 40, Value = _model.HeightMm, MinimumTrackColor = BordattoColors.Gold, MaximumTrackColor = Color.FromArgb("#4B2A1B"), ThumbColor = BordattoColors.Gold };
        slider.ValueChanged += (_, e) => { _model.HeightMm = (float)e.NewValue; value.Text = $"{_model.HeightMm:0} mm"; _canvas.InvalidateSurface(); };
        _optionsHost.Add(value); _optionsHost.Add(slider);
    }

    private void BuildColorOptions()
    {
        var grid = new Grid { ColumnSpacing = 8, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var colors = new uint[] { 0xFF000000, 0xFFFFC6D9, 0xFFF15A91, 0xFFE51664, 0xFFB91F4B };
        for (var i = 0; i < colors.Length; i++)
        {
            var argb = colors[i];
            var b = new Button { Text = "●", FontSize = 30, HeightRequest = 58, CornerRadius = 15, BackgroundColor = BordattoColors.PanelSoft, TextColor = Color.FromArgb($"#{argb:X8}") };
            b.Clicked += (_, _) => { _model.Color = argb; _canvas.InvalidateSurface(); };
            grid.Add(b); Grid.SetColumn(b, i);
        }
        _optionsHost.Add(grid);
    }

    private void BuildStyleOptions()
    {
        var row = new Grid { ColumnSpacing = 8, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var bold = Segment("Negrito", () => { _model.Bold = !_model.Bold; _canvas.InvalidateSurface(); });
        var italic = Segment("Itálico", () => { _model.Italic = !_model.Italic; _canvas.InvalidateSurface(); });
        var reset = Segment("↻ 0°", () => { _model.RotationDegrees = 0; _model.Scale = 1; _canvas.InvalidateSurface(); });
        row.Add(bold); row.Add(italic); row.Add(reset); Grid.SetColumn(italic, 1); Grid.SetColumn(reset, 2);
        _optionsHost.Add(row);
        _optionsHost.Add(NewLabel("No bastidor: arraste o nome; use a alça ↻ para girar e a alça diagonal para redimensionar. Com dois dedos, mova + gire + dê zoom ao mesmo tempo.", 12, BordattoColors.Muted));
    }

    private void BuildProfessionalOptions()
    {
        var title = NewLabel("Ajustes Studio Pro", 14, BordattoColors.Gold, FontAttributes.Bold);
        _optionsHost.Add(title);
        AddProSlider("Densidade Satin", .28, 1.0, _settings.DensityMm, "mm", v => _settings.DensityMm = (float)v);
        AddProSlider("Compensação", 0, 1.0, _settings.PullCompensationMm, "mm", v => _settings.PullCompensationMm = (float)v);
        AddProSlider("Largura máxima Satin", 4, 14, _settings.SatinMaxWidthMm, "mm", v => _settings.SatinMaxWidthMm = (float)v);
    }

    private void AddProSlider(string title, double min, double max, double current, string suffix, Action<double> changed)
    {
        var label = NewLabel($"{title}: {current:0.00} {suffix}", 12, BordattoColors.Cream);
        var slider = new Slider { Minimum = min, Maximum = max, Value = current, MinimumTrackColor = BordattoColors.Gold, ThumbColor = BordattoColors.Gold, MaximumTrackColor = Color.FromArgb("#4B2A1B") };
        slider.ValueChanged += (_, e) => { changed(e.NewValue); label.Text = $"{title}: {e.NewValue:0.00} {suffix}"; };
        _optionsHost.Add(label); _optionsHost.Add(slider);
    }

    private async Task GenerateAsync()
    {
        try
        {
            var design = EmbroideryEngine.Generate(_model, _settings, _mode);
            await Navigation.PushAsync(new EditorPage(design, _mode));
        }
        catch (Exception ex)
        {
            await DisplayAlert("BORDATTO", ex.Message, "OK");
        }
    }

    private static Button Segment(string text, Action clicked)
    {
        var b = new Button { Text = text, BackgroundColor = BordattoColors.PanelSoft, TextColor = BordattoColors.Cream, HeightRequest = 56, CornerRadius = 16, FontAttributes = FontAttributes.Bold, FontSize = 13 };
        b.Clicked += (_, _) => clicked();
        return b;
    }

    private static Label NewLabel(string text, double size, Color color, FontAttributes attrs = FontAttributes.None, TextAlignment align = TextAlignment.Start)
        => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs, HorizontalTextAlignment = align, VerticalTextAlignment = TextAlignment.Center };
}
