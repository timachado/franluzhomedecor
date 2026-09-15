namespace BordattoStudio;

public sealed class App : Application
{
    protected override Window CreateWindow(IActivationState? activationState)
    {
        var navigation = new NavigationPage(new MainPage())
        {
            BarBackgroundColor = Core.BordattoColors.Background,
            BarTextColor = Core.BordattoColors.Cream
        };
        return new Window(navigation);
    }
}
