using Microsoft.Maui.ApplicationModel;

namespace BordattoStudio;

public sealed class StartupPage : ContentPage
{
    private readonly Label _status;
    private readonly Label _details;
    private bool _started;

    public StartupPage()
    {
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = Core.BordattoColors.Background;

        var mark = new Label
        {
            Text = "✦",
            FontSize = 48,
            TextColor = Core.BordattoColors.Gold,
            HorizontalTextAlignment = TextAlignment.Center
        };
        var title = new Label
        {
            Text = "BORDATTO Studio",
            FontSize = 28,
            FontAttributes = FontAttributes.Bold,
            TextColor = Core.BordattoColors.Cream,
            HorizontalTextAlignment = TextAlignment.Center
        };
        _status = new Label
        {
            Text = "Inicializando motor MAUI/Skia…",
            FontSize = 14,
            TextColor = Core.BordattoColors.Muted,
            HorizontalTextAlignment = TextAlignment.Center
        };
        _details = new Label
        {
            IsVisible = false,
            FontSize = 11,
            TextColor = Colors.OrangeRed,
            HorizontalTextAlignment = TextAlignment.Start
        };

        Content = new ScrollView
        {
            Content = new VerticalStackLayout
            {
                Padding = new Thickness(28),
                Spacing = 14,
                VerticalOptions = LayoutOptions.Center,
                Children = { mark, title, _status, _details }
            }
        };
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        if (_started) return;
        _started = true;
        Dispatcher.Dispatch(async () => await OpenAppAsync());
    }

    private async Task OpenAppAsync()
    {
        try
        {
            await Task.Delay(250);
            _status.Text = "Carregando BORDATTO…";
            var home = new HomePage();
            await Navigation.PushAsync(home, false);
#if ANDROID
            Android.Util.Log.Info("BORDATTO", "App shell ready");
#endif
            Navigation.RemovePage(this);
        }
        catch (Exception ex)
        {
            _status.Text = "Falha ao inicializar o aplicativo";
            _details.IsVisible = true;
            _details.Text = ex.ToString();
#if ANDROID
            Android.Util.Log.Error("BORDATTO", "App startup failed: " + ex);
#endif
        }
    }
}
