using BordattoStudio.Core;
using Microsoft.Maui.Storage;

namespace BordattoStudio;

public sealed class MachinePage : ContentPage
{
    private readonly Entry _name;
    private readonly Slider _speed;
    private readonly Label _speedValue;
    private readonly Picker _hoop;

    public MachinePage()
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;

        _name = new Entry
        {
            Text = Preferences.Default.Get("machine_name", "Minha máquina"),
            TextColor = BordattoColors.Cream,
            BackgroundColor = BordattoColors.PanelSoft,
            Placeholder = "Nome/modelo da máquina",
            PlaceholderColor = BordattoColors.Muted
        };
        _speed = new Slider
        {
            Minimum = 300, Maximum = 1200,
            Value = Preferences.Default.Get("machine_speed", 750d),
            MinimumTrackColor = BordattoColors.Gold,
            MaximumTrackColor = Color.FromArgb("#4B2A1B"),
            ThumbColor = BordattoColors.Gold
        };
        _speedValue = Text($"{_speed.Value:0} pts/min", 16, BordattoColors.Gold, FontAttributes.Bold);
        _speed.ValueChanged += (_, e) => _speedValue.Text = $"{e.NewValue:0} pts/min";
        _hoop = new Picker
        {
            Title = "Bastidor",
            TextColor = BordattoColors.Cream,
            BackgroundColor = BordattoColors.PanelSoft,
            ItemsSource = new[] { "100 × 100 mm", "130 × 180 mm", "160 × 260 mm", "200 × 300 mm" },
            SelectedIndex = Preferences.Default.Get("machine_hoop", 0)
        };

        var save = Primary("Salvar perfil da máquina");
        save.Clicked += async (_, _) =>
        {
            Preferences.Default.Set("machine_name", _name.Text ?? "Minha máquina");
            Preferences.Default.Set("machine_speed", _speed.Value);
            Preferences.Default.Set("machine_hoop", Math.Max(0, _hoop.SelectedIndex));
            await DisplayAlertAsync("Máquina", "Perfil salvo.", "OK");
        };

        var stack = new VerticalStackLayout { Padding = new Thickness(20), Spacing = 14 };
        var back = new Button { Text = "‹  Máquina", BackgroundColor = Colors.Transparent, TextColor = BordattoColors.Gold, FontSize = 18, HorizontalOptions = LayoutOptions.Start };
        back.Clicked += async (_, _) => await Navigation.PopAsync();
        stack.Add(back);
        stack.Add(Text("Perfil da máquina", 25, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(Text("Usado para tempo estimado, Machine Check e produção.", 12, BordattoColors.Muted));
        stack.Add(Text("Nome / modelo", 12, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(_name);
        stack.Add(Text("Velocidade nominal", 12, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(_speedValue); stack.Add(_speed);
        stack.Add(Text("Bastidor principal", 12, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(_hoop);
        stack.Add(save);
        stack.Add(Panel("Machine Check", "O novo motor usa estas informações para validar dimensões e estimar o tempo antes da máquina."));
        Content = new ScrollView { Content = stack };
    }

    private static Border Panel(string title, string detail)
    {
        var s = new VerticalStackLayout { Spacing = 5 };
        s.Add(Text(title, 15, BordattoColors.Gold, FontAttributes.Bold));
        s.Add(Text(detail, 12, BordattoColors.Muted));
        return new Border { Stroke = Color.FromArgb("#4B2A1B"), StrokeThickness = 1, BackgroundColor = BordattoColors.Panel, Padding = new Thickness(15), Content = s };
    }

    private static Button Primary(string text) => new() { Text = text, HeightRequest = 56, CornerRadius = 16, BackgroundColor = BordattoColors.Gold, TextColor = Color.FromArgb("#17100C"), FontAttributes = FontAttributes.Bold };
    private static Label Text(string text, double size, Color color, FontAttributes attrs = FontAttributes.None) => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs };
}
