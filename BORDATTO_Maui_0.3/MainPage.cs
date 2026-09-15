using BordattoStudio.Core;
using BordattoStudio.Views;

namespace BordattoStudio;

// 0.3.6: editor responsivo de nome no bastidor, com interação inspirada no vídeo de referência.
// O bastidor é a área principal e os parâmetros técnicos do Studio Pro vivem numa aba PRO própria.
public sealed class MainPage : ContentPage
{
    private readonly TextObjectModel _model = new();
    private EngineSettings _settings = EngineSettings.TraditionalPreset();
    private BordattoMode _mode = BordattoMode.Tradicional;
    private readonly InteractiveTextCanvas036 _canvas;
    private readonly VerticalStackLayout _optionsHost;
    private readonly Button _traditionalButton;
    private readonly Button _studioButton;
    private readonly Label _modeHint;
    private readonly Entry _entry;
    private readonly Button _generateButton;
    private readonly Border _toolsPanel;
    private readonly Dictionary<string, Button> _tabButtons = new(StringComparer.OrdinalIgnoreCase);
    private string _activeTab = "Fonte";
    private bool _generating;

    public MainPage(BordattoMode initialMode = BordattoMode.Tradicional)
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;

        _canvas = new InteractiveTextCanvas036
        {
            Model = _model,
            MinimumHeightRequest = 210
        };
        _canvas.ModelChanged += (_, _) => { };

        _optionsHost = new VerticalStackLayout { Spacing = 9 };
        _modeHint = NewLabel("TRADICIONAL", 10, BordattoColors.Gold, FontAttributes.Bold);

        _entry = new Entry
        {
            Text = _model.Text,
            TextColor = BordattoColors.Cream,
            BackgroundColor = Color.FromArgb("#17151F"),
            FontSize = 18,
            Placeholder = "Digite o texto...",
            PlaceholderColor = BordattoColors.Muted,
            Margin = new Thickness(0),
            HeightRequest = 54,
            ReturnType = ReturnType.Done
        };
        _entry.TextChanged += (_, e) =>
        {
            var value = e.NewTextValue ?? string.Empty;
            _model.Text = string.IsNullOrWhiteSpace(value) ? " " : value[..Math.Min(28, value.Length)];
            _canvas.Selected = true;
            _canvas.InvalidateSurface();
        };
        _entry.Completed += (_, _) => FinishTextEditing();

        _traditionalButton = Segment("TRADICIONAL", () => SetMode(BordattoMode.Tradicional));
        _studioButton = Segment("✦ STUDIO PRO", () => SetMode(BordattoMode.StudioPro));

        _generateButton = new Button
        {
            Text = "▶  CONCLUIR E GERAR MATRIZ",
            BackgroundColor = BordattoColors.Gold,
            TextColor = Color.FromArgb("#17100C"),
            FontAttributes = FontAttributes.Bold,
            FontSize = 13,
            HeightRequest = 52,
            CornerRadius = 16
        };
        _generateButton.Clicked += async (_, _) => await GenerateAsync();

        _toolsPanel = BuildToolsPanel();
        var editorHeader = BuildEditorHeader();

        var root = new Grid
        {
            RowSpacing = 0,
            RowDefinitions =
            {
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Star),
                new RowDefinition(GridLength.Auto)
            }
        };
        root.Add(editorHeader); root.SetRow(editorHeader, 0);
        root.Add(_canvas); root.SetRow(_canvas, 1);
        root.Add(_toolsPanel); root.SetRow(_toolsPanel, 2);
        Content = root;

        // Durante a digitação o painel inferior some e o bastidor recebe toda a área livre.
        // O botão "Concluir" restaura os ajustes sem gerar a matriz automaticamente.
        _entry.Focused += (_, _) =>
        {
            _toolsPanel.IsVisible = false;
            _canvas.Selected = true;
            _canvas.InvalidateSurface();
        };

        SizeChanged += (_, _) => ApplyResponsiveLayout();
        SetMode(initialMode);
        ShowTab("Fonte");
    }

    private View BuildEditorHeader()
    {
        var back = new Button
        {
            Text = "‹",
            FontSize = 30,
            TextColor = BordattoColors.Cream,
            BackgroundColor = Colors.Transparent,
            WidthRequest = 38,
            HeightRequest = 38,
            Padding = 0
        };
        back.Clicked += async (_, _) => await Navigation.PopAsync();

        var title = NewLabel("Editar texto", 13, BordattoColors.Muted);
        var done = new Button
        {
            Text = "Concluir",
            TextColor = Color.FromArgb("#E51766"),
            BackgroundColor = Colors.Transparent,
            FontAttributes = FontAttributes.Bold,
            FontSize = 13,
            Padding = new Thickness(8, 0)
        };
        done.Clicked += (_, _) => FinishTextEditing();

        var top = new Grid
        {
            ColumnDefinitions =
            {
                new ColumnDefinition(GridLength.Auto),
                new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(GridLength.Auto)
            }
        };
        top.Add(back); top.SetColumn(back, 0);
        top.Add(title); top.SetColumn(title, 1);
        top.Add(done); top.SetColumn(done, 2);

        var entryBorder = new Border
        {
            Stroke = Color.FromArgb("#E51766"),
            StrokeThickness = 1,
            BackgroundColor = Color.FromArgb("#17151F"),
            Content = _entry,
            Padding = new Thickness(6, 0)
        };

        var hint = NewLabel("Arraste • ↻ gire • ↗ redimensione • 2 dedos: mover + girar + zoom", 9, BordattoColors.Muted);

        var stack = new VerticalStackLayout
        {
            Spacing = 7,
            Padding = new Thickness(14, 8, 14, 9),
            Children = { top, entryBorder, hint }
        };
        return new Border
        {
            StrokeThickness = 0,
            BackgroundColor = Color.FromArgb("#0E0B13"),
            Content = stack
        };
    }

    private Border BuildToolsPanel()
    {
        var modeSwitcher = new Grid
        {
            ColumnSpacing = 8,
            ColumnDefinitions =
            {
                new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(GridLength.Star)
            }
        };
        modeSwitcher.Add(_traditionalButton); modeSwitcher.SetColumn(_traditionalButton, 0);
        modeSwitcher.Add(_studioButton); modeSwitcher.SetColumn(_studioButton, 1);

        var tabs = new Grid { ColumnSpacing = 4 };
        for (var i = 0; i < 5; i++)
            tabs.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Star));

        var names = new[] { "Fonte", "Tamanho", "Cor", "Estilo", "PRO" };
        for (var i = 0; i < names.Length; i++)
        {
            var name = names[i];
            var b = new Button
            {
                Text = name,
                FontSize = 10,
                HeightRequest = 40,
                CornerRadius = 12,
                BackgroundColor = Color.FromArgb("#351D13"),
                TextColor = BordattoColors.Cream,
                Padding = new Thickness(2)
            };
            b.Clicked += (_, _) => ShowTab(name);
            _tabButtons[name] = b;
            tabs.Add(b); tabs.SetColumn(b, i);
        }

        var content = new VerticalStackLayout
        {
            Spacing = 8,
            Padding = new Thickness(14, 10, 14, 12),
            Children = { modeSwitcher, tabs, _optionsHost, _modeHint, _generateButton }
        };

        return new Border
        {
            Stroke = Color.FromArgb("#4B2A1B"),
            StrokeThickness = 1,
            BackgroundColor = Color.FromArgb("#21120D"),
            HeightRequest = 220,
            Content = new ScrollView { Content = content }
        };
    }

    private void ApplyResponsiveLayout()
    {
        if (Height <= 0) return;

        // Em telas menores o painel cede espaço ao bastidor; o conteúdo técnico continua rolável.
        var panelHeight = Height < 680 ? 176 : Height < 760 ? 192 : Height < 860 ? 212 : 238;
        _toolsPanel.HeightRequest = panelHeight;
        _canvas.MinimumHeightRequest = Height < 680 ? 170 : Height < 760 ? 190 : 220;
        _canvas.InvalidateSurface();
    }

    private void FinishTextEditing()
    {
        _entry.Unfocus();
        _toolsPanel.IsVisible = true;
        ApplyResponsiveLayout();
        _canvas.Selected = true;
        _canvas.InvalidateSurface();
    }

    private void SetMode(BordattoMode mode)
    {
        _mode = mode;
        _settings = mode == BordattoMode.Tradicional
            ? EngineSettings.TraditionalPreset()
            : EngineSettings.StudioPreset();

        _traditionalButton.BackgroundColor = mode == BordattoMode.Tradicional ? BordattoColors.Gold : BordattoColors.PanelSoft;
        _traditionalButton.TextColor = mode == BordattoMode.Tradicional ? Color.FromArgb("#19100B") : BordattoColors.Cream;
        _studioButton.BackgroundColor = mode == BordattoMode.StudioPro ? BordattoColors.Gold : BordattoColors.PanelSoft;
        _studioButton.TextColor = mode == BordattoMode.StudioPro ? Color.FromArgb("#19100B") : BordattoColors.Cream;
        _modeHint.Text = mode == BordattoMode.Tradicional
            ? "TRADICIONAL • simples, direto e funcional"
            : "STUDIO PRO • Satin adaptativo + controles técnicos";

        if (_tabButtons.TryGetValue("PRO", out var pro))
        {
            pro.IsEnabled = mode == BordattoMode.StudioPro;
            pro.Opacity = mode == BordattoMode.StudioPro ? 1 : .42;
        }

        if (mode == BordattoMode.Tradicional && _activeTab.Equals("PRO", StringComparison.OrdinalIgnoreCase))
            _activeTab = "Fonte";

        ShowTab(_activeTab);
    }

    private void ShowTab(string name)
    {
        if (name.Equals("PRO", StringComparison.OrdinalIgnoreCase) && _mode != BordattoMode.StudioPro)
            name = "Fonte";

        _activeTab = name;
        foreach (var pair in _tabButtons)
        {
            var selected = pair.Key.Equals(name, StringComparison.OrdinalIgnoreCase);
            pair.Value.BackgroundColor = selected ? BordattoColors.Gold : Color.FromArgb("#351D13");
            pair.Value.TextColor = selected ? Color.FromArgb("#19100B") : BordattoColors.Cream;
        }

        _optionsHost.Clear();
        if (name == "Fonte") BuildFontOptions();
        else if (name == "Tamanho") BuildSizeOptions();
        else if (name == "Cor") BuildColorOptions();
        else if (name == "Estilo") BuildStyleOptions();
        else BuildProfessionalOptions();
    }

    private void BuildFontOptions()
    {
        var grid = new Grid { ColumnSpacing = 6 };
        for (var i = 0; i < 4; i++)
            grid.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Star));

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
            var b = new Button
            {
                Text = $"Aa\n{f.Label}",
                FontSize = 12,
                HeightRequest = 60,
                CornerRadius = 12,
                BackgroundColor = BordattoColors.PanelSoft,
                TextColor = BordattoColors.Cream,
                Padding = new Thickness(2)
            };
            b.Clicked += (_, _) =>
            {
                _model.FontFamily = f.Family;
                _model.Bold = f.Bold;
                _model.Italic = f.Italic;
                RefreshCanvas();
            };
            grid.Add(b); grid.SetColumn(b, i);
        }
        _optionsHost.Add(grid);
    }

    private void BuildSizeOptions()
    {
        var value = NewLabel($"Altura: {_model.HeightMm:0.0} mm", 16, BordattoColors.Gold, FontAttributes.Bold);
        var slider = new Slider
        {
            Minimum = 5,
            Maximum = 40,
            Value = _model.HeightMm,
            MinimumTrackColor = BordattoColors.Gold,
            MaximumTrackColor = Color.FromArgb("#4B2A1B"),
            ThumbColor = BordattoColors.Gold
        };
        slider.ValueChanged += (_, e) =>
        {
            _model.HeightMm = (float)e.NewValue;
            value.Text = $"Altura: {_model.HeightMm:0.0} mm";
            RefreshCanvas();
        };
        _optionsHost.Add(value);
        _optionsHost.Add(slider);
    }

    private void BuildColorOptions()
    {
        var grid = new Grid { ColumnSpacing = 8 };
        for (var i = 0; i < 5; i++)
            grid.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Star));

        var colors = new uint[] { 0xFF000000, 0xFFFFC6D9, 0xFFF15A91, 0xFFE51664, 0xFFB91F4B };
        for (var i = 0; i < colors.Length; i++)
        {
            var argb = colors[i];
            var b = new Button
            {
                Text = "●",
                FontSize = 26,
                HeightRequest = 50,
                CornerRadius = 12,
                BackgroundColor = BordattoColors.PanelSoft,
                TextColor = Color.FromArgb($"#{argb:X8}")
            };
            b.Clicked += (_, _) =>
            {
                _model.Color = argb;
                RefreshCanvas();
            };
            grid.Add(b); grid.SetColumn(b, i);
        }
        _optionsHost.Add(grid);
    }

    private void BuildStyleOptions()
    {
        var row = new Grid { ColumnSpacing = 8 };
        for (var i = 0; i < 3; i++)
            row.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Star));

        var bold = Segment("Negrito", () => { _model.Bold = !_model.Bold; RefreshCanvas(); });
        var italic = Segment("Itálico", () => { _model.Italic = !_model.Italic; RefreshCanvas(); });
        var reset = Segment("↻ Reset", () =>
        {
            _model.RotationDegrees = 0;
            _model.Scale = 1;
            _model.CenterX = .5f;
            _model.CenterY = .5f;
            RefreshCanvas();
        });
        row.Add(bold); row.Add(italic); row.Add(reset);
        row.SetColumn(italic, 1); row.SetColumn(reset, 2);
        _optionsHost.Add(row);
    }

    private void BuildProfessionalOptions()
    {
        _optionsHost.Add(NewLabel("Ajustes Studio Pro", 12, BordattoColors.Gold, FontAttributes.Bold));
        _optionsHost.Add(NewLabel("Esses parâmetros afetam a matriz gerada; o texto no bastidor mantém sua forma visual.", 9, BordattoColors.Muted));

        AddProSlider("Densidade Satin", .12, .80, _settings.DensityMm, "mm", v => _settings.DensityMm = (float)v);
        AddProSlider("Compensação", 0, 1.0, _settings.PullCompensationMm, "mm", v => _settings.PullCompensationMm = (float)v);
        AddProSlider("Largura máxima Satin", 4, 14, _settings.SatinMaxWidthMm, "mm", v => _settings.SatinMaxWidthMm = (float)v);
        AddProSlider("Comprimento base", 1.0, 4.0, _settings.StitchLengthMm, "mm", v => _settings.StitchLengthMm = (float)v);
        AddProToggle("Underlay central", _settings.CenterUnderlay, value => _settings.CenterUnderlay = value);
        AddProToggle("Underlay de borda", _settings.EdgeUnderlay, value => _settings.EdgeUnderlay = value);
    }

    private void AddProSlider(string title, double min, double max, double current, string suffix, Action<double> changed)
    {
        var row = new Grid
        {
            ColumnDefinitions =
            {
                new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(new GridLength(150))
            },
            ColumnSpacing = 10
        };
        var label = NewLabel($"{title}: {current:0.00} {suffix}", 10, BordattoColors.Cream);
        var slider = new Slider
        {
            Minimum = min,
            Maximum = max,
            Value = Math.Clamp(current, min, max),
            MinimumTrackColor = BordattoColors.Gold,
            ThumbColor = BordattoColors.Gold,
            MaximumTrackColor = Color.FromArgb("#4B2A1B")
        };
        slider.ValueChanged += (_, e) =>
        {
            changed(e.NewValue);
            label.Text = $"{title}: {e.NewValue:0.00} {suffix}";
        };
        row.Add(label); row.SetColumn(label, 0);
        row.Add(slider); row.SetColumn(slider, 1);
        _optionsHost.Add(row);
    }

    private void AddProToggle(string title, bool current, Action<bool> changed)
    {
        var row = new Grid
        {
            ColumnDefinitions =
            {
                new ColumnDefinition(GridLength.Star),
                new ColumnDefinition(GridLength.Auto)
            }
        };
        var label = NewLabel(title, 10, BordattoColors.Cream);
        var toggle = new Switch
        {
            IsToggled = current,
            OnColor = BordattoColors.Gold,
            ThumbColor = BordattoColors.Cream
        };
        toggle.Toggled += (_, e) => changed(e.Value);
        row.Add(label); row.SetColumn(label, 0);
        row.Add(toggle); row.SetColumn(toggle, 1);
        _optionsHost.Add(row);
    }

    private void RefreshCanvas()
    {
        _canvas.Selected = true;
        _canvas.InvalidateSurface();
    }

    private async Task GenerateAsync()
    {
        if (_generating) return;
        if (string.IsNullOrWhiteSpace(_model.Text))
        {
            await DisplayAlertAsync("BORDATTO", "Digite um nome antes de gerar a matriz.", "OK");
            return;
        }

        FinishTextEditing();
        _generating = true;
        var oldText = _generateButton.Text;
        _generateButton.Text = "GERANDO MATRIZ…";
        _generateButton.IsEnabled = false;
        try
        {
            var design = await Task.Run(() => EmbroideryEngine.Generate(_model, _settings, _mode));
            ProjectStore.Remember(design, _mode);
            await Navigation.PushAsync(new EditorPage(design, _mode));
        }
        catch (Exception ex)
        {
            await DisplayAlertAsync("BORDATTO", ex.Message, "OK");
        }
        finally
        {
            _generating = false;
            _generateButton.Text = oldText;
            _generateButton.IsEnabled = true;
        }
    }

    private static Button Segment(string text, Action clicked)
    {
        var b = new Button
        {
            Text = text,
            BackgroundColor = BordattoColors.PanelSoft,
            TextColor = BordattoColors.Cream,
            HeightRequest = 44,
            CornerRadius = 13,
            FontAttributes = FontAttributes.Bold,
            FontSize = 11
        };
        b.Clicked += (_, _) => clicked();
        return b;
    }

    private static Label NewLabel(string text, double size, Color color, FontAttributes attrs = FontAttributes.None, TextAlignment align = TextAlignment.Start)
        => new()
        {
            Text = text,
            FontSize = size,
            TextColor = color,
            FontAttributes = attrs,
            HorizontalTextAlignment = align,
            VerticalTextAlignment = TextAlignment.Center
        };
}
