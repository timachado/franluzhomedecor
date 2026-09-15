using BordattoStudio.Core;
using Microsoft.Maui.Storage;

namespace BordattoStudio;

public sealed class CostPage : ContentPage
{
    private readonly Entry _stitches;
    private readonly Entry _threadCost;
    private readonly Entry _machineHour;
    private readonly Label _result;

    public CostPage()
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;

        _stitches = NumberEntry("1888");
        _threadCost = NumberEntry("0,80");
        _machineHour = NumberEntry("18,00");
        _result = Text("Preencha os dados e toque em Calcular.", 13, BordattoColors.Muted);

        var calculate = Primary("Calcular custo e tempo");
        calculate.Clicked += (_, _) => Calculate();

        var stack = new VerticalStackLayout { Padding = new Thickness(20), Spacing = 12 };
        var back = new Button { Text = "‹  Custos", BackgroundColor = Colors.Transparent, TextColor = BordattoColors.Gold, FontSize = 18, HorizontalOptions = LayoutOptions.Start };
        back.Clicked += async (_, _) => await Navigation.PopAsync();
        stack.Add(back);
        stack.Add(Text("Calculadora de produção", 25, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(Text("Estimativa simples usando a velocidade salva no perfil da máquina.", 12, BordattoColors.Muted));
        stack.Add(Field("Pontos da matriz", _stitches));
        stack.Add(Field("Custo estimado de linha (R$)", _threadCost));
        stack.Add(Field("Custo máquina / hora (R$)", _machineHour));
        stack.Add(calculate);
        stack.Add(new Border
        {
            Stroke = Color.FromArgb("#4B2A1B"), StrokeThickness = 1,
            BackgroundColor = BordattoColors.Panel,
            Padding = new Thickness(16),
            Content = _result
        });
        Content = new ScrollView { Content = stack };
        Calculate();
    }

    private void Calculate()
    {
        var stitches = Parse(_stitches.Text, 0);
        var thread = Parse(_threadCost.Text, 0);
        var hourly = Parse(_machineHour.Text, 0);
        var speed = Math.Max(1d, Preferences.Default.Get("machine_speed", 750d));
        var minutes = stitches / speed;
        var machineCost = hourly * minutes / 60d;
        var subtotal = thread + machineCost;
        _result.Text = $"Velocidade: {speed:0} pts/min\nTempo estimado: {minutes:0.0} min\nLinha: R$ {thread:0.00}\nMáquina: R$ {machineCost:0.00}\n\nCusto base estimado: R$ {subtotal:0.00}".Replace('.', ',');
    }

    private static double Parse(string? text, double fallback)
    {
        if (double.TryParse((text ?? "").Replace(',', '.'), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var value))
            return Math.Max(0, value);
        return fallback;
    }

    private static View Field(string title, Entry entry)
    {
        var stack = new VerticalStackLayout { Spacing = 5 };
        stack.Add(Text(title, 12, BordattoColors.Cream, FontAttributes.Bold));
        stack.Add(entry);
        return stack;
    }

    private static Entry NumberEntry(string value) => new()
    {
        Text = value,
        Keyboard = Keyboard.Numeric,
        TextColor = BordattoColors.Cream,
        BackgroundColor = BordattoColors.PanelSoft
    };

    private static Button Primary(string text) => new() { Text = text, HeightRequest = 56, CornerRadius = 16, BackgroundColor = BordattoColors.Gold, TextColor = Color.FromArgb("#17100C"), FontAttributes = FontAttributes.Bold };
    private static Label Text(string text, double size, Color color, FontAttributes attrs = FontAttributes.None) => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs };
}
