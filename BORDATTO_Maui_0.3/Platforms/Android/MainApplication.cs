using Android.App;
using Android.Runtime;

namespace BordattoStudio;

[Application]
public class MainApplication(IntPtr handle, JniHandleOwnership ownership) : MauiApplication(handle, ownership)
{
    public override void OnCreate()
    {
        AndroidEnvironment.UnhandledExceptionRaiser += (_, e) =>
        {
            Android.Util.Log.Error("BORDATTO", e.Exception?.ToString() ?? "Unhandled Android exception");
        };
        AppDomain.CurrentDomain.UnhandledException += (_, e) =>
        {
            Android.Util.Log.Error("BORDATTO", e.ExceptionObject?.ToString() ?? "Unhandled .NET exception");
        };
        TaskScheduler.UnobservedTaskException += (_, e) =>
        {
            Android.Util.Log.Error("BORDATTO", e.Exception.ToString());
            e.SetObserved();
        };

        base.OnCreate();
        Android.Util.Log.Info("BORDATTO", "MainApplication.OnCreate completed");
    }

    protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
}
