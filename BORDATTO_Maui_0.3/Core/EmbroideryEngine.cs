using SkiaSharp;

namespace BordattoStudio.Core;

public static class EmbroideryEngine
{
    private sealed record Band(int Top, int Bottom);
    private sealed record ColumnBand(int X, IReadOnlyList<Band> Bands);

    public static EmbroideryDesign Generate(TextObjectModel model, EngineSettings settings, BordattoMode mode)
    {
        var clean = string.Join(" ", model.Text.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries));
        if (string.IsNullOrWhiteSpace(clean)) throw new InvalidOperationException("Digite um nome para gerar a matriz.");
        clean = clean[..Math.Min(clean.Length, 28)];

        const float pxPerMm = 6f;
        var heightMm = Math.Clamp(model.HeightMm * model.Scale, 5f, 80f);
        var textPx = heightMm * pxPerMm;
        var style = model.Bold && model.Italic ? SKFontStyle.BoldItalic : model.Bold ? SKFontStyle.Bold : model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;
        using var typeface = SKTypeface.FromFamilyName(model.FontFamily, style) ?? SKTypeface.Default;
        using var font = new SKFont(typeface, textPx);
        using var paint = new SKPaint { Color = SKColors.White, IsAntialias = true, Style = SKPaintStyle.Fill };

        var densityPx = Math.Max(2, (int)MathF.Round(Math.Clamp(settings.DensityMm, .25f, 1.2f) * pxPerMm));
        var pullPx = Math.Clamp(settings.PullCompensationMm, 0f, 1.5f) * pxPerMm;
        var spacingPx = textPx * .045f;
        var cursorPx = 0f;
        var raw = new List<StitchPoint>();

        void AddPx(float x, float y, StitchCommand command)
            => raw.Add(new StitchPoint(x / pxPerMm, y / pxPerMm, command, model.Color));

        void StartTrack(float x, float y)
        {
            AddPx(x, y, StitchCommand.Jump);
            AddPx(x, y, StitchCommand.Stitch);
        }

        foreach (var ch in clean)
        {
            if (ch == ' ')
            {
                cursorPx += textPx * .34f;
                continue;
            }

            var token = ch.ToString();
            var advance = Math.Max(font.MeasureText(token, out var bounds, paint), textPx * .20f);
            var margin = Math.Max(8, (int)MathF.Ceiling(pxPerMm * 2.5f));
            var bitmapW = Math.Clamp((int)MathF.Ceiling(bounds.Width) + margin * 2, 32, 1600);
            var bitmapH = Math.Clamp((int)MathF.Ceiling(bounds.Height) + margin * 2, 32, 1600);

            using var bitmap = new SKBitmap(bitmapW, bitmapH, SKColorType.Bgra8888, SKAlphaType.Premul);
            using (var canvas = new SKCanvas(bitmap))
            {
                canvas.Clear(SKColors.Transparent);
                canvas.DrawText(token, margin - bounds.Left, margin - bounds.Top, SKTextAlign.Left, font, paint);
                canvas.Flush();
            }

            var columns = new List<ColumnBand>();
            for (var x = 0; x < bitmapW; x += densityPx)
            {
                var bands = new List<Band>();
                var y = 0;
                while (y < bitmapH)
                {
                    if (bitmap.GetPixel(x, y).Alpha > 24)
                    {
                        var top = y;
                        var bottom = y;
                        y++;
                        while (y < bitmapH && bitmap.GetPixel(x, y).Alpha > 24)
                        {
                            bottom = y;
                            y++;
                        }
                        if (bottom - top >= 1) bands.Add(new Band(top, bottom));
                    }
                    y++;
                }
                if (bands.Count > 0) columns.Add(new ColumnBand(x, bands));
            }

            if (columns.Count > 1)
            {
                var maxTracks = columns.Max(c => c.Bands.Count);
                for (var track = 0; track < maxTracks; track++)
                {
                    var segment = new List<(int X, Band Band)>();

                    void FlushSegment()
                    {
                        if (segment.Count < 2)
                        {
                            segment.Clear();
                            return;
                        }

                        if (settings.CenterUnderlay)
                        {
                            var stride = Math.Max(1, (int)MathF.Round(1.8f / Math.Max(settings.DensityMm, .25f)));
                            var first = true;
                            for (var i = 0; i < segment.Count; i += stride)
                            {
                                var item = segment[i];
                                var cx = cursorPx + item.X;
                                var cy = (item.Band.Top + item.Band.Bottom) * .5f;
                                if (first) { StartTrack(cx, cy); first = false; }
                                else AddPx(cx, cy, StitchCommand.Stitch);
                            }
                            var lastItem = segment[^1];
                            AddPx(cursorPx + lastItem.X, (lastItem.Band.Top + lastItem.Band.Bottom) * .5f, StitchCommand.Stitch);
                        }

                        if (settings.EdgeUnderlay)
                        {
                            var first = true;
                            foreach (var item in segment)
                            {
                                var x = cursorPx + item.X;
                                var y = item.Band.Top + (item.Band.Bottom - item.Band.Top) * .22f;
                                if (first) { StartTrack(x, y); first = false; }
                                else AddPx(x, y, StitchCommand.Stitch);
                            }
                        }

                        var parity = false;
                        var satinStarted = false;
                        for (var i = segment.Count - 1; i >= 0; i--)
                        {
                            var item = segment[i];
                            var widthMm = (item.Band.Bottom - item.Band.Top) / pxPerMm;
                            var limitMm = Math.Max(3f, settings.SatinMaxWidthMm);
                            var halfExtra = widthMm > limitMm ? 0f : pullPx;
                            var y = parity ? item.Band.Top - halfExtra : item.Band.Bottom + halfExtra;
                            var x = cursorPx + item.X;
                            if (!satinStarted)
                            {
                                if (!settings.CenterUnderlay && !settings.EdgeUnderlay) StartTrack(x, y);
                                else AddPx(x, y, StitchCommand.Stitch);
                                satinStarted = true;
                            }
                            else AddPx(x, y, StitchCommand.Stitch);
                            parity = !parity;
                        }

                        var end = raw.LastOrDefault(p => p.Command == StitchCommand.Stitch);
                        if (end.Command == StitchCommand.Stitch)
                        {
                            raw.Add(new StitchPoint(end.X + .20f, end.Y, StitchCommand.Stitch, model.Color));
                            raw.Add(new StitchPoint(end.X, end.Y + .20f, StitchCommand.Stitch, model.Color));
                            raw.Add(new StitchPoint(end.X, end.Y, StitchCommand.Stitch, model.Color));
                        }
                        segment.Clear();
                    }

                    var lastX = int.MinValue;
                    foreach (var col in columns)
                    {
                        var band = track < col.Bands.Count ? col.Bands[track] : null;
                        if (band is null || (lastX != int.MinValue && col.X - lastX > densityPx * 2))
                        {
                            FlushSegment();
                            lastX = int.MinValue;
                            if (band is null) continue;
                        }
                        segment.Add((col.X, band));
                        lastX = col.X;
                    }
                    FlushSegment();
                }
            }

            cursorPx += advance + spacingPx;
        }

        if (raw.Count(p => p.Command == StitchCommand.Stitch) < 6)
            throw new InvalidOperationException("Não foi possível gerar pontadas suficientes para este nome.");

        var stitchOnly = raw.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var minX = stitchOnly.Min(p => p.X); var maxX = stitchOnly.Max(p => p.X);
        var minY = stitchOnly.Min(p => p.Y); var maxY = stitchOnly.Max(p => p.Y);
        var centerX = (minX + maxX) * .5f; var centerY = (minY + maxY) * .5f;
        var radians = model.RotationDegrees * MathF.PI / 180f;
        var cos = MathF.Cos(radians); var sin = MathF.Sin(radians);

        var rotated = new List<StitchPoint>(raw.Count + 1);
        foreach (var p in raw)
        {
            var dx = p.X - centerX; var dy = p.Y - centerY;
            rotated.Add(p with { X = centerX + dx * cos - dy * sin, Y = centerY + dx * sin + dy * cos });
        }
        var last = rotated.Last(p => p.Command == StitchCommand.Stitch);
        rotated.Add(new StitchPoint(last.X, last.Y, StitchCommand.End, model.Color));

        var finalPts = rotated.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var fMinX = finalPts.Min(p => p.X); var fMaxX = finalPts.Max(p => p.X);
        var fMinY = finalPts.Min(p => p.Y); var fMaxY = finalPts.Max(p => p.Y);

        return new EmbroideryDesign
        {
            Name = clean,
            Stitches = rotated,
            WidthMm = fMaxX - fMinX,
            HeightMm = fMaxY - fMinY,
            ThreadColor = model.Color,
            ThreadName = model.Color == 0xFF000000 ? "Preto" : "Rosa Intenso",
            ThreadBrand = "Brother",
            ThreadCode = model.Color == 0xFF000000 ? "900" : "086"
        };
    }

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
