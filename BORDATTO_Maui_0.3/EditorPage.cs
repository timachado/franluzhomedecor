using BordattoStudio.Core;
using BordattoStudio.Views;

namespace BordattoStudio;

public sealed class EditorPage : ContentPage
{
    private readonly EmbroideryDesign _design;
    private readonly BordattoMode _mode;
    private readonly InteractiveDesignCanvas _canvas;
    private readonly Label _saveState;

    public EditorPage(EmbroideryDesign design, BordattoMode mode)
    {
        _design = design;
        _mode = mode;
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;
        _canvas = new InteractiveDesignCanvas { Design = design };
        _saveState = LabelText("Alterações não salvas", 12, BordattoColors.Muted);
        _canvas.TransformChanged += (_, _) => _saveState.Text = "Alterações não salvas";

        var root = new Grid
        {
            RowDefinitions =
            {
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Auto),
                new RowDefinition(GridLength.Star),
                new RowDefinition(GridLength.Auto)
            }
        };
        Add(root, BuildHeader(), 0);
        Add(root, BuildNameBar(), 1);
        Add(root, BuildSaveBar(), 2);
        Add(root, BuildCanvasArea(), 3);
        Add(root, BuildBottomNav(), 4);
        Content = root;
    }

    private View BuildHeader()
    {
        var back = new Button { Text = "‹", FontSize = 36, TextColor = BordattoColors.Cream, BackgroundColor = Colors.Transparent, WidthRequest = 54, Padding = 0 };
        back.Clicked += async (_, _) => await Navigation.PopAsync();
        var title = new VerticalStackLayout { Spacing = 1 };
        title.Add(LabelText(_design.Name, 23, BordattoColors.Cream, FontAttributes.Bold));
        title.Add(LabelText($"{(_mode == BordattoMode.Tradicional ? "TRADICIONAL" : "STUDIO PRO")} · {_design.StitchCount:N0} pts · 1 cor", 10, BordattoColors.Muted));
        var badge = new Border { Stroke = Color.FromArgb("#4B2A1B"), StrokeThickness = 1, BackgroundColor = BordattoColors.PanelSoft, Padding = new Thickness(14, 8), Content = LabelText(_mode == BordattoMode.Tradicional ? "TRADICIONAL" : "STUDIO PRO", 10, BordattoColors.Gold, FontAttributes.Bold) };
        var g = new Grid { Padding = new Thickness(14, 12, 14, 8), ColumnDefinitions = { new ColumnDefinition(GridLength.Auto), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        g.Add(back); g.Add(title); g.Add(badge); g.SetColumn(title, 1); g.SetColumn(badge, 2);
        return g;
    }

    private View BuildNameBar()
    {
        var left = new HorizontalStackLayout { Spacing = 10, VerticalOptions = LayoutOptions.Center };
        left.Add(LabelText("▰", 18, BordattoColors.Gold));
        left.Add(LabelText("Dê um nome ao seu bordado", 13, BordattoColors.Cream));
        var name = new Button { Text = "Nomear", TextColor = BordattoColors.Gold, BackgroundColor = Colors.Transparent, FontAttributes = FontAttributes.Bold, FontSize = 12 };
        var g = new Grid { Padding = new Thickness(22, 12), BackgroundColor = BordattoColors.Panel, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        g.Add(left); g.Add(name); g.SetColumn(name, 1);
        return g;
    }

    private View BuildSaveBar()
    {
        var left = new HorizontalStackLayout { Spacing = 10, VerticalOptions = LayoutOptions.Center };
        left.Add(LabelText("≡", 17, BordattoColors.Muted)); left.Add(_saveState);
        var save = new Button { Text = "Salvar", TextColor = BordattoColors.Gold, BackgroundColor = Colors.Transparent, FontAttributes = FontAttributes.Bold, FontSize = 12 };
        save.Clicked += (_, _) => _saveState.Text = "Salvo";
        var g = new Grid { Padding = new Thickness(22, 10), BackgroundColor = BordattoColors.Panel, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        g.Add(left); g.Add(save); g.SetColumn(save, 1);
        return g;
    }

    private View BuildCanvasArea()
    {
        var g = new Grid { BackgroundColor = BordattoColors.Canvas };
        g.Add(_canvas);
        var play = new Button
        {
            Text = "▶",
            FontSize = 28,
            WidthRequest = 72,
            HeightRequest = 72,
            CornerRadius = 36,
            BackgroundColor = BordattoColors.Gold,
            TextColor = Color.FromArgb("#17100C"),
            Margin = new Thickness(0, 0, 18, 18),
            HorizontalOptions = LayoutOptions.End,
            VerticalOptions = LayoutOptions.End
        };
        play.Clicked += async (_, _) =>
        {
            var transformed = EmbroideryEngine.Transform(_design, _canvas.DesignScale, _canvas.RotationDegrees);
            await Navigation.PushAsync(new SimulatorPage(transformed));
        };
        g.Add(play);
        return g;
    }

    private View BuildBottomNav()
    {
        var g = new Grid { Padding = new Thickness(10, 8, 10, 10), BackgroundColor = Color.FromArgb("#160D09"), ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var items = new[] { ("+", "Adicionar"), ("☷", "Ajustes"), ("◇", "Camadas"), ("●", "Linhas") };
        for (var i = 0; i < items.Length; i++)
        {
            var stack = new VerticalStackLayout { Spacing = 1, HorizontalOptions = LayoutOptions.Center };
            stack.Add(LabelText(items[i].Item1, 24, BordattoColors.Cream, FontAttributes.Bold, TextAlignment.Center));
            stack.Add(LabelText(items[i].Item2, 10, BordattoColors.Muted, FontAttributes.None, TextAlignment.Center));
            g.Add(stack); g.SetColumn(stack, i);
        }
        return g;
    }

    private static void Add(Grid grid, View view, int row) { grid.Add(view); grid.SetRow(view, row); }
    private static Label LabelText(string text, double size, Color color, FontAttributes attrs = FontAttributes.None, TextAlignment alignment = TextAlignment.Start)
        => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs, HorizontalTextAlignment = alignment, VerticalTextAlignment = TextAlignment.Center };
}
