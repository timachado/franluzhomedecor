using BordattoStudio.Core;
using BordattoStudio.Views;

namespace BordattoStudio;

public sealed class SimulatorPage : ContentPage
{
    private readonly EmbroideryDesign _design;
    private readonly SimulationCanvas _canvas;
    private readonly Label _percent;
    private readonly Label _points;
    private readonly Label _remaining;
    private readonly ProgressBar _progress;
    private readonly Slider _timeline;
    private readonly Button _play;
    private readonly Button[] _speedButtons;
    private readonly Grid _completedOverlay;
    private readonly IDispatcherTimer _timer;
    private int _current;
    private double _speed = 1;
    private double _accumulator;
    private bool _playing;

    public SimulatorPage(EmbroideryDesign design)
    {
        _design = design;
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = Color.FromArgb("#0E0B15");
        _canvas = new SimulationCanvas { Design = design };
        _percent = Text("0,0%", 10, Colors.White, FontAttributes.Bold);
        _points = Text($"0 / {design.StitchCount:N0} pts", 11, Color.FromArgb("#BBB6C2"));
        _remaining = Text("Restante: --", 11, Color.FromArgb("#BBB6C2"));
        _progress = new ProgressBar { Progress = 0, ProgressColor = ThreadColor(), BackgroundColor = Color.FromArgb("#25222E"), HeightRequest = 5 };
        _timeline = new Slider { Minimum = 0, Maximum = Math.Max(1, design.Stitches.Count), Value = 0, MinimumTrackColor = ThreadColor(), MaximumTrackColor = Color.FromArgb("#25222E"), ThumbColor = ThreadColor() };
        _timeline.ValueChanged += (_, e) => { if (!_playing) { _current = (int)e.NewValue; UpdateUi(); } };
        _play = new Button { Text = "▶  Iniciar", HeightRequest = 60, CornerRadius = 16, BackgroundColor = ThreadColor(), TextColor = Colors.White, FontAttributes = FontAttributes.Bold, FontSize = 15 };
        _play.Clicked += (_, _) => TogglePlay();
        _speedButtons = new[] { SpeedButton("1×", 1), SpeedButton("2×", 2), SpeedButton("4×", 4) };

        _timer = Dispatcher.CreateTimer();
        _timer.Interval = TimeSpan.FromMilliseconds(80);
        _timer.Tick += (_, _) => Tick();

        var root = new Grid { RowDefinitions = { new RowDefinition(GridLength.Auto), new RowDefinition(GridLength.Star), new RowDefinition(GridLength.Auto) } };
        var header = BuildHeader(); root.Add(header); Grid.SetRow(header, 0);
        var canvasArea = BuildCanvasArea(); root.Add(canvasArea); Grid.SetRow(canvasArea, 1);
        var controls = BuildControls(); root.Add(controls); Grid.SetRow(controls, 2);
        _completedOverlay = BuildCompletedOverlay(); root.Add(_completedOverlay); Grid.SetRowSpan(_completedOverlay, 3); _completedOverlay.IsVisible = false;
        Content = root;
        SetSpeed(1);
        UpdateUi();
    }

    private View BuildHeader()
    {
        var back = new Button { Text = "‹", FontSize = 36, TextColor = Colors.White, BackgroundColor = Colors.Transparent, WidthRequest = 56, Padding = 0 };
        back.Clicked += async (_, _) => { StopTimer(); await Navigation.PopAsync(); };
        var title = Text("Simulação", 19, Colors.White, FontAttributes.Bold, TextAlignment.Center);
        var speed = new HorizontalStackLayout { Spacing = 2, Padding = new Thickness(4), BackgroundColor = Color.FromArgb("#1B1924") };
        foreach (var b in _speedButtons) speed.Add(b);
        var grid = new Grid { Padding = new Thickness(10, 10), ColumnDefinitions = { new ColumnDefinition(GridLength.Auto), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        grid.Add(back); grid.Add(title); grid.Add(speed); Grid.SetColumn(title, 1); Grid.SetColumn(speed, 2);
        return grid;
    }

    private View BuildCanvasArea()
    {
        var grid = new Grid { BackgroundColor = BordattoColors.Canvas };
        grid.Add(_canvas);
        var leftPill = new Border { BackgroundColor = Color.FromArgb("#403D43"), StrokeThickness = 0, Padding = new Thickness(12, 7), Margin = new Thickness(12), HorizontalOptions = LayoutOptions.Start, VerticalOptions = LayoutOptions.Start, Content = _percent };
        var size = Text($"{_design.WidthMm:0} × {_design.HeightMm:0} mm", 10, Colors.White, FontAttributes.Bold);
        var rightPill = new Border { BackgroundColor = Color.FromArgb("#403D43"), StrokeThickness = 0, Padding = new Thickness(12, 7), Margin = new Thickness(12), HorizontalOptions = LayoutOptions.End, VerticalOptions = LayoutOptions.Start, Content = size };
        grid.Add(leftPill); grid.Add(rightPill);
        return grid;
    }

    private View BuildControls()
    {
        var panel = new VerticalStackLayout { Padding = new Thickness(14, 10, 14, 14), Spacing = 8, BackgroundColor = Color.FromArgb("#0E0B15") };
        var threadCard = new Grid { Padding = new Thickness(12, 10), BackgroundColor = Color.FromArgb("#1B1924"), ColumnDefinitions = { new ColumnDefinition(GridLength.Auto), new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Auto) } };
        var swatch = new Border { WidthRequest = 46, HeightRequest = 46, BackgroundColor = ThreadColor(), Stroke = Colors.White.WithAlpha(.2f), StrokeThickness = 2 };
        var info = new VerticalStackLayout { Spacing = 5 };
        info.Add(Text($"{_design.ThreadName} · {_design.ThreadBrand} {_design.ThreadCode}", 12, Colors.White, FontAttributes.Bold));
        info.Add(_progress);
        var fio = new Border { BackgroundColor = Color.FromArgb("#25222E"), Padding = new Thickness(12, 8), Content = Text("Fio 1 / 1", 10, Color.FromArgb("#BBB6C2")) };
        threadCard.Add(swatch); threadCard.Add(info); threadCard.Add(fio); Grid.SetColumn(info, 1); Grid.SetColumn(fio, 2);
        panel.Add(threadCard);

        var stats = new Grid { ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        stats.Add(_points); stats.Add(_remaining); Grid.SetColumn(_remaining, 1); _remaining.HorizontalTextAlignment = TextAlignment.End;
        panel.Add(stats);

        var code = new Border { HorizontalOptions = LayoutOptions.Start, Stroke = ThreadColor(), StrokeThickness = 1, BackgroundColor = Color.FromArgb("#1B1924"), Padding = new Thickness(12, 6), Content = Text($"●  {_design.ThreadCode}  ▶", 10, Colors.White, FontAttributes.Bold) };
        panel.Add(code);
        panel.Add(_timeline);

        var buttons = new Grid { ColumnSpacing = 10, ColumnDefinitions = { new ColumnDefinition(new GridLength(.85, GridUnitType.Star)), new ColumnDefinition(new GridLength(2.1, GridUnitType.Star)), new ColumnDefinition(new GridLength(.85, GridUnitType.Star)) } };
        var minus = new Button { Text = "|◀\n−10%", HeightRequest = 60, CornerRadius = 16, BackgroundColor = Color.FromArgb("#25222E"), TextColor = Colors.White, FontSize = 12 };
        minus.Clicked += (_, _) => { Pause(); _current = Math.Max(0, _current - Math.Max(1, _design.Stitches.Count / 10)); UpdateUi(); };
        var stop = new Button { Text = "■\nParar", HeightRequest = 60, CornerRadius = 16, BackgroundColor = Color.FromArgb("#25222E"), TextColor = ThreadColor(), FontSize = 12 };
        stop.Clicked += (_, _) => { Pause(); _current = 0; UpdateUi(); };
        buttons.Add(minus); buttons.Add(_play); buttons.Add(stop); Grid.SetColumn(_play, 1); Grid.SetColumn(stop, 2);
        panel.Add(buttons);
        return panel;
    }

    private Button SpeedButton(string text, double value)
    {
        var b = new Button { Text = text, FontSize = 11, HeightRequest = 42, WidthRequest = 48, CornerRadius = 12, BackgroundColor = Colors.Transparent, TextColor = Color.FromArgb("#BBB6C2"), Padding = 0 };
        b.Clicked += (_, _) => SetSpeed(value);
        return b;
    }

    private Grid BuildCompletedOverlay()
    {
        var overlay = new Grid { BackgroundColor = Colors.Black.WithAlpha(.78f) };
        var card = new VerticalStackLayout { WidthRequest = 330, Spacing = 14, HorizontalOptions = LayoutOptions.Center, VerticalOptions = LayoutOptions.Center };
        var check = new Border { BackgroundColor = Color.FromArgb("#31C89A"), WidthRequest = 92, HeightRequest = 92, HorizontalOptions = LayoutOptions.Center, Content = Text("✓", 54, Colors.White, FontAttributes.Bold, TextAlignment.Center) };
        card.Add(check); card.Add(Text("Bordado concluído!", 22, Colors.White, FontAttributes.Bold, TextAlignment.Center)); card.Add(Text($"{_design.StitchCount:N0} pontos aplicados", 13, Color.FromArgb("#BBB6C2"), FontAttributes.None, TextAlignment.Center));
        var row = new Grid { ColumnSpacing = 10, ColumnDefinitions = { new ColumnDefinition(GridLength.Star), new ColumnDefinition(GridLength.Star) } };
        var close = new Button { Text = "Fechar", HeightRequest = 54, CornerRadius = 16, BackgroundColor = Color.FromArgb("#25222E"), TextColor = Colors.White, FontAttributes = FontAttributes.Bold };
        close.Clicked += (_, _) => _completedOverlay.IsVisible = false;
        var restart = new Button { Text = "↻ Reiniciar", HeightRequest = 54, CornerRadius = 16, BackgroundColor = ThreadColor(), TextColor = Colors.White, FontAttributes = FontAttributes.Bold };
        restart.Clicked += (_, _) => { _completedOverlay.IsVisible = false; _current = 0; UpdateUi(); };
        row.Add(close); row.Add(restart); Grid.SetColumn(restart, 1); card.Add(row); overlay.Add(card); return overlay;
    }

    private void TogglePlay()
    {
        if (_current >= _design.Stitches.Count) _current = 0;
        _playing = !_playing;
        if (_playing) { _timer.Start(); _play.Text = "Ⅱ  Pausar"; }
        else { _timer.Stop(); _play.Text = _current > 0 ? "▶  Continuar" : "▶  Iniciar"; }
    }

    private void Tick()
    {
        if (!_playing) return;
        // The reference sample shows ~1,888 points in about 4m21s at 1× (~434 ppm).
        const double referencePpm = 434.0;
        _accumulator += referencePpm / 60.0 * 0.080 * _speed;
        var add = (int)Math.Floor(_accumulator);
        if (add <= 0) return;
        _accumulator -= add;
        _current = Math.Min(_design.Stitches.Count, _current + add);
        UpdateUi();
        if (_current >= _design.Stitches.Count)
        {
            Pause();
            _completedOverlay.IsVisible = true;
        }
    }

    private void Pause()
    {
        _playing = false; _timer.Stop(); _play.Text = _current > 0 ? "▶  Continuar" : "▶  Iniciar";
    }

    private void StopTimer() { _playing = false; _timer.Stop(); }

    private void SetSpeed(double value)
    {
        _speed = value;
        for (var i = 0; i < _speedButtons.Length; i++)
        {
            var active = Math.Abs(new[] { 1d, 2d, 4d }[i] - value) < .01;
            _speedButtons[i].BackgroundColor = active ? ThreadColor() : Colors.Transparent;
            _speedButtons[i].TextColor = active ? Colors.White : Color.FromArgb("#BBB6C2");
        }
    }

    private void UpdateUi()
    {
        var total = Math.Max(1, _design.Stitches.Count);
        var p = Math.Clamp(_current / (double)total, 0, 1);
        var donePts = _design.Stitches.Take(Math.Clamp(_current, 0, _design.Stitches.Count)).Count(s => s.Command == StitchCommand.Stitch);
        var remainingPts = Math.Max(0, _design.StitchCount - donePts);
        var secs = (int)Math.Ceiling(remainingPts / (434.0 * _speed) * 60.0);
        _canvas.Current = _current; _canvas.InvalidateSurface();
        _percent.Text = $"{p * 100:0.0}%".Replace('.', ',');
        _points.Text = $"{donePts:N0} / {_design.StitchCount:N0} pts";
        _remaining.Text = _current >= total ? "Completo ✓" : $"Restante: {secs / 60}m {secs % 60:00}s";
        _progress.Progress = p;
        if (!_timeline.IsFocused) _timeline.Value = _current;
    }

    protected override void OnDisappearing() { StopTimer(); base.OnDisappearing(); }
    private Color ThreadColor() => Color.FromArgb($"#{_design.ThreadColor:X8}");
    private static Label Text(string text, double size, Color color, FontAttributes attrs = FontAttributes.None, TextAlignment align = TextAlignment.Start)
        => new() { Text = text, FontSize = size, TextColor = color, FontAttributes = attrs, HorizontalTextAlignment = align, VerticalTextAlignment = TextAlignment.Center };
}
