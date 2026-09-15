using BordattoStudio.Core;

namespace BordattoStudio;

// Compatibility entry point used by HomePage. It redirects to the 0.3.6 editor
// while preserving the previous MainPage implementation in git history for rollback.
public sealed class MainPage : ContentPage
{
    private readonly BordattoMode _initialMode;
    private bool _redirected;

    public MainPage(BordattoMode initialMode = BordattoMode.Tradicional)
    {
        _initialMode = initialMode;
        NavigationPage.SetHasNavigationBar(this, false);
        BackgroundColor = BordattoColors.Background;
        Content = new Grid
        {
            Children =
            {
                new ActivityIndicator
                {
                    IsRunning = true,
                    Color = BordattoColors.Gold,
                    WidthRequest = 38,
                    HeightRequest = 38,
                    HorizontalOptions = LayoutOptions.Center,
                    VerticalOptions = LayoutOptions.Center
                }
            }
        };
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        if (_redirected) return;
        _redirected = true;
        Dispatcher.Dispatch(async () =>
        {
            var replacement = new MainPage036(_initialMode);
            await Navigation.PushAsync(replacement, false);
            if (Navigation.NavigationStack.Contains(this))
                Navigation.RemovePage(this);
        });
    }
}
