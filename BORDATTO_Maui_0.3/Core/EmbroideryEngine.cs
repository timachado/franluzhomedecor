using SkiaSharp;

namespace BordattoStudio.Core;

public static class EmbroideryEngine
{
    public static EmbroideryDesign Generate(TextObjectModel model, EngineSettings settings, BordattoMode mode)
        => TrackSatinDigitizer035.Generate(model, settings, mode);

    public static EmbroideryDesign Transform(EmbroideryDesign design, float scale, float rotationDegrees)
    {
        var pts = design.Stitches.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        if (pts.Count == 0) return design;
        var minX = pts.Min(p => p.X); var maxX = pts.Max(p => p.X);
        var minY = pts.Min(p => p.Y); var maxY = pts.Max(p => p.Y);
        var cx = (minX + maxX) * .5f; var cy = (minY + maxY) * .5f;
        var r = rotationDegrees * MathF.PI / 180f; var c = MathF.Cos(r); var s = MathF.Sin(r);
        var transformed = design.Stitches.Select(p =>
        {
            if (p.Command == StitchCommand.End) return p;
            var dx = (p.X - cx) * scale; var dy = (p.Y - cy) * scale;
            return p with { X = cx + dx * c - dy * s, Y = cy + dx * s + dy * c };
        }).ToList();
        var used = transformed.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        return new EmbroideryDesign
        {
            Name = design.Name,
            Stitches = transformed,
            WidthMm = used.Max(p => p.X) - used.Min(p => p.X),
            HeightMm = used.Max(p => p.Y) - used.Min(p => p.Y),
            ThreadColor = design.ThreadColor,
            ThreadName = design.ThreadName,
            ThreadBrand = design.ThreadBrand,
            ThreadCode = design.ThreadCode
        };
    }

    public static SKColor ToSkColor(uint argb)
        => new((byte)((argb >> 16) & 0xFF), (byte)((argb >> 8) & 0xFF), (byte)(argb & 0xFF), (byte)((argb >> 24) & 0xFF));
}
