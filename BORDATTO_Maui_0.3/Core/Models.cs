using SkiaSharp;

namespace BordattoStudio.Core;

public enum BordattoMode { Tradicional, StudioPro }
public enum StitchCommand { Stitch, Jump, Trim, ColorChange, End }

public readonly record struct StitchPoint(float X, float Y, StitchCommand Command, uint Color);

public sealed class EmbroideryDesign
{
    public string Name { get; init; } = "Bordado";
    public List<StitchPoint> Stitches { get; init; } = [];
    public float WidthMm { get; init; }
    public float HeightMm { get; init; }
    public uint ThreadColor { get; init; } = 0xFFE91E63;
    public string ThreadName { get; init; } = "Rosa Intenso";
    public string ThreadBrand { get; init; } = "Brother";
    public string ThreadCode { get; init; } = "086";
    public int StitchCount => Stitches.Count(s => s.Command == StitchCommand.Stitch);
}

public sealed class TextObjectModel
{
    public string Text { get; set; } = "Maria";
    public string FontFamily { get; set; } = "sans-serif";
    public float HeightMm { get; set; } = 19f;
    public float CenterX { get; set; } = 0.50f;
    public float CenterY { get; set; } = 0.48f;
    public float Scale { get; set; } = 1f;
    public float RotationDegrees { get; set; }
    public uint Color { get; set; } = 0xFFE91E63;
    public bool Bold { get; set; } = true;
    public bool Italic { get; set; }
}

public sealed class EngineSettings
{
    public float DensityMm { get; set; } = 0.18f;
    public float PullCompensationMm { get; set; } = 0.25f;
    public float SatinMaxWidthMm { get; set; } = 9f;
    public bool CenterUnderlay { get; set; } = true;
    public bool EdgeUnderlay { get; set; }
    public float StitchLengthMm { get; set; } = 2.2f;

    public static EngineSettings TraditionalPreset() => new()
    {
        DensityMm = 0.18f,
        PullCompensationMm = 0.25f,
        SatinMaxWidthMm = 9f,
        CenterUnderlay = true,
        EdgeUnderlay = false,
        StitchLengthMm = 2.2f
    };

    public static EngineSettings StudioPreset() => new()
    {
        DensityMm = 0.18f,
        PullCompensationMm = 0.30f,
        SatinMaxWidthMm = 10f,
        CenterUnderlay = true,
        EdgeUnderlay = true,
        StitchLengthMm = 2.0f
    };
}

public static class BordattoColors
{
    public static readonly Color Background = Color.FromArgb("#0B0807");
    public static readonly Color Panel = Color.FromArgb("#2A160F");
    public static readonly Color PanelSoft = Color.FromArgb("#351D13");
    public static readonly Color Gold = Color.FromArgb("#E7BB68");
    public static readonly Color Cream = Color.FromArgb("#F4E8D1");
    public static readonly Color Muted = Color.FromArgb("#B7A998");
    public static readonly Color Canvas = Color.FromArgb("#F3ECDD");
}
