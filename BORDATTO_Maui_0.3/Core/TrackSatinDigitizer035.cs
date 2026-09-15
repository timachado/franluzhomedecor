using SkiaSharp;

namespace BordattoStudio.Core;

// 0.3.5: preserva o preenchimento cheio da 0.3.4 e melhora a geometria local do Satin.
// Cada trilha calcula uma direção local, encontra as bordas reais do glifo nessa direção
// e corta conexões que atravessariam contraformas/áreas transparentes.
internal static class TrackSatinDigitizer035
{
    private sealed record RowRun(int Y, int Left, int Right)
    {
        public float Center => (Left + Right) * .5f;
        public int Width => Right - Left + 1;
    }

    private sealed record SatinSample(
        float CenterX,
        float CenterY,
        float LeftX,
        float LeftY,
        float RightX,
        float RightY,
        float WidthPx);

    private sealed class Track
    {
        public List<RowRun> Runs { get; } = [];
        public float MinX => Runs.Count == 0 ? 0 : Runs.Min(r => r.Left);
        public float MaxX => Runs.Count == 0 ? 0 : Runs.Max(r => r.Right);
        public int LastY => Runs.Count == 0 ? 0 : Runs[^1].Y;
        public float VerticalSpan => Runs.Count == 0 ? 0 : MathF.Abs(Runs[^1].Y - Runs[0].Y);
    }

    public static EmbroideryDesign Generate(TextObjectModel model, EngineSettings settings, BordattoMode mode)
    {
        var clean = string.Join(" ", model.Text.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries));
        if (string.IsNullOrWhiteSpace(clean))
            throw new InvalidOperationException("Digite um nome para gerar a matriz.");
        clean = clean[..Math.Min(clean.Length, 28)];

        const float pxPerMm = 7f;
        var requestedHeightMm = Math.Clamp(model.HeightMm * model.Scale, 5f, 80f);
        var textPx = requestedHeightMm * pxPerMm;
        var style = model.Bold && model.Italic
            ? SKFontStyle.BoldItalic
            : model.Bold ? SKFontStyle.Bold : model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;

        using var typeface = SKTypeface.FromFamilyName(model.FontFamily, style) ?? SKTypeface.Default;
        using var font = new SKFont(typeface, textPx);
        using var paint = new SKPaint { Color = SKColors.White, IsAntialias = true, Style = SKPaintStyle.Fill };

        var rowStep = Math.Max(1, (int)MathF.Round(Math.Clamp(settings.DensityMm, .14f, .45f) * pxPerMm));
        var pullPx = Math.Clamp(settings.PullCompensationMm, 0f, 1.2f) * pxPerMm;
        var spacingPx = textPx * .075f;
        var cursorPx = 0f;
        var raw = new List<StitchPoint>();
        var hasPreviousCharacter = false;

        void AddPx(float x, float y, StitchCommand command)
            => raw.Add(new StitchPoint(x / pxPerMm, y / pxPerMm, command, model.Color));
        void Jump(float x, float y) => AddPx(x, y, StitchCommand.Jump);
        void Stitch(float x, float y) => AddPx(x, y, StitchCommand.Stitch);
        void TrimAtLastStitch()
        {
            var last = raw.LastOrDefault(p => p.Command == StitchCommand.Stitch);
            if (raw.Count > 0 && last.Command == StitchCommand.Stitch)
                raw.Add(new StitchPoint(last.X, last.Y, StitchCommand.Trim, model.Color));
        }

        foreach (var ch in clean)
        {
            if (ch == ' ')
            {
                cursorPx += textPx * .33f;
                continue;
            }

            var token = ch.ToString();
            var advance = Math.Max(font.MeasureText(token, out var bounds, paint), textPx * .20f);
            var margin = Math.Max(12, (int)MathF.Ceiling(pxPerMm * 2.5f));
            var bw = Math.Clamp((int)MathF.Ceiling(bounds.Width) + margin * 2, 40, 1600);
            var bh = Math.Clamp((int)MathF.Ceiling(bounds.Height) + margin * 2, 40, 1600);

            using var bitmap = new SKBitmap(bw, bh, SKColorType.Bgra8888, SKAlphaType.Premul);
            using (var canvas = new SKCanvas(bitmap))
            {
                canvas.Clear(SKColors.Transparent);
                canvas.DrawText(token, margin - bounds.Left, margin - bounds.Top, SKTextAlign.Left, font, paint);
                canvas.Flush();
            }

            var tracks = BuildTracks(bitmap, rowStep)
                .Where(t => t.Runs.Count >= 3)
                .ToList();
            var ordered = OrderTracks(tracks);

            SKPoint? previousTrackEnd = null;
            var firstTrackOfCharacter = true;

            foreach (var track in ordered)
            {
                var runs = track.Runs;
                if (runs.Count < 2) continue;

                var samples = BuildAdaptiveSamples(bitmap, runs, pullPx, settings.SatinMaxWidthMm * pxPerMm);
                if (samples.Count < 2) continue;

                var firstTarget = settings.CenterUnderlay
                    ? new SKPoint(samples[0].CenterX, samples[0].CenterY)
                    : new SKPoint(samples[0].LeftX, samples[0].LeftY);

                if (firstTrackOfCharacter && hasPreviousCharacter)
                    TrimAtLastStitch();

                if (previousTrackEnd is SKPoint prev)
                {
                    var jumpPx = Dist(prev.X, prev.Y, firstTarget.X, firstTarget.Y);
                    if (jumpPx > pxPerMm * 2.6f || !SegmentStaysInside(bitmap, prev, firstTarget))
                        TrimAtLastStitch();
                }

                if (settings.CenterUnderlay)
                {
                    var stride = Math.Max(2, (int)MathF.Round((1.25f * pxPerMm) / rowStep));
                    var first = samples[0];
                    Jump(cursorPx + first.CenterX, first.CenterY);
                    Stitch(cursorPx + first.CenterX, first.CenterY);
                    for (var i = stride; i < samples.Count; i += stride)
                    {
                        var s = samples[i];
                        Stitch(cursorPx + s.CenterX, s.CenterY);
                    }
                    var last = samples[^1];
                    Stitch(cursorPx + last.CenterX, last.CenterY);
                }

                if (settings.EdgeUnderlay)
                {
                    var stride = Math.Max(2, (int)MathF.Round((.95f * pxPerMm) / rowStep));
                    var first = samples[0];
                    var edgeStart = Lerp(
                        new SKPoint(first.LeftX, first.LeftY),
                        new SKPoint(first.CenterX, first.CenterY),
                        .28f);
                    Jump(cursorPx + edgeStart.X, edgeStart.Y);
                    Stitch(cursorPx + edgeStart.X, edgeStart.Y);
                    for (var i = stride; i < samples.Count; i += stride)
                    {
                        var s = samples[i];
                        var edge = Lerp(
                            new SKPoint(s.LeftX, s.LeftY),
                            new SKPoint(s.CenterX, s.CenterY),
                            .28f);
                        Stitch(cursorPx + edge.X, edge.Y);
                    }
                }

                var f = samples[0];
                Jump(cursorPx + f.LeftX, f.LeftY);
                Stitch(cursorPx + f.LeftX, f.LeftY);
                Stitch(cursorPx + f.RightX, f.RightY);

                var reversePair = true;
                for (var i = 1; i < samples.Count; i++)
                {
                    var s = samples[i];
                    if (reversePair)
                    {
                        Stitch(cursorPx + s.RightX, s.RightY);
                        Stitch(cursorPx + s.LeftX, s.LeftY);
                    }
                    else
                    {
                        Stitch(cursorPx + s.LeftX, s.LeftY);
                        Stitch(cursorPx + s.RightX, s.RightY);
                    }
                    reversePair = !reversePair;
                }

                var end = raw.LastOrDefault(p => p.Command == StitchCommand.Stitch);
                if (raw.Count > 0 && end.Command == StitchCommand.Stitch)
                {
                    raw.Add(new StitchPoint(end.X + .16f, end.Y, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y + .16f, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y, StitchCommand.Stitch, model.Color));
                }

                var lastSample = samples[^1];
                previousTrackEnd = reversePair
                    ? new SKPoint(lastSample.RightX, lastSample.RightY)
                    : new SKPoint(lastSample.LeftX, lastSample.LeftY);
                firstTrackOfCharacter = false;
            }

            if (!firstTrackOfCharacter)
                hasPreviousCharacter = true;

            cursorPx += advance + spacingPx;
        }

        if (raw.Count(p => p.Command == StitchCommand.Stitch) < 12)
            throw new InvalidOperationException("Não foi possível gerar pontadas suficientes para este nome.");

        NormalizePhysicalSize(raw, requestedHeightMm * 1.08f);
        ApplyRotation(raw, model.RotationDegrees);

        var lastStitch = raw.Last(p => p.Command == StitchCommand.Stitch);
        raw.Add(new StitchPoint(lastStitch.X, lastStitch.Y, StitchCommand.End, model.Color));

        var used = raw.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var width = used.Max(p => p.X) - used.Min(p => p.X);
        var height = used.Max(p => p.Y) - used.Min(p => p.Y);

        return new EmbroideryDesign
        {
            Name = clean,
            Stitches = raw,
            WidthMm = width,
            HeightMm = height,
            ThreadColor = model.Color,
            ThreadName = model.Color == 0xFF000000 ? "Preto" : "Rosa Intenso",
            ThreadBrand = "Brother",
            ThreadCode = model.Color == 0xFF000000 ? "900" : "086"
        };
    }

    private static List<SatinSample> BuildAdaptiveSamples(
        SKBitmap bitmap,
        List<RowRun> runs,
        float pullPx,
        float satinMaxWidthPx)
    {
        var samples = new List<SatinSample>(runs.Count);
        var maxRadius = MathF.Sqrt(bitmap.Width * bitmap.Width + bitmap.Height * bitmap.Height);

        for (var i = 0; i < runs.Count; i++)
        {
            var run = runs[i];
            var center = new SKPoint(SmoothedCenter(runs, i), run.Y);
            if (!IsInside(bitmap, center.X, center.Y))
                center = new SKPoint(run.Center, run.Y);

            var (tx, ty) = EstimateTangent(runs, i);
            var nx = ty;
            var ny = -tx;

            if (nx < 0f || (MathF.Abs(nx) < .05f && ny < 0f))
            {
                nx = -nx;
                ny = -ny;
            }

            var right = TraceToEdge(bitmap, center, nx, ny, maxRadius);
            var left = TraceToEdge(bitmap, center, -nx, -ny, maxRadius);
            var widthPx = Dist(left.X, left.Y, right.X, right.Y);

            if (widthPx < 1.2f || !float.IsFinite(widthPx))
            {
                left = new SKPoint(run.Left, run.Y);
                right = new SKPoint(run.Right, run.Y);
                widthPx = run.Width;
                nx = 1f;
                ny = 0f;
            }

            if (widthPx <= satinMaxWidthPx)
            {
                var comp = pullPx * .5f;
                left = new SKPoint(left.X - nx * comp, left.Y - ny * comp);
                right = new SKPoint(right.X + nx * comp, right.Y + ny * comp);
                widthPx += pullPx;
            }

            samples.Add(new SatinSample(
                center.X,
                center.Y,
                left.X,
                left.Y,
                right.X,
                right.Y,
                widthPx));
        }

        return samples;
    }

    private static float SmoothedCenter(List<RowRun> runs, int index)
    {
        var from = Math.Max(0, index - 1);
        var to = Math.Min(runs.Count - 1, index + 1);
        var sum = 0f;
        var weight = 0f;
        for (var i = from; i <= to; i++)
        {
            var w = i == index ? 2f : 1f;
            sum += runs[i].Center * w;
            weight += w;
        }
        return weight <= 0 ? runs[index].Center : sum / weight;
    }

    private static (float X, float Y) EstimateTangent(List<RowRun> runs, int index)
    {
        var a = runs[Math.Max(0, index - 2)];
        var b = runs[Math.Min(runs.Count - 1, index + 2)];
        var dx = b.Center - a.Center;
        var dy = b.Y - a.Y;
        var len = MathF.Sqrt(dx * dx + dy * dy);
        if (len < .001f)
            return (0f, 1f);
        return (dx / len, dy / len);
    }

    private static SKPoint TraceToEdge(SKBitmap bitmap, SKPoint center, float dx, float dy, float maxRadius)
    {
        const float step = .55f;
        var last = center;
        for (var d = step; d <= maxRadius; d += step)
        {
            var x = center.X + dx * d;
            var y = center.Y + dy * d;
            if (!IsInside(bitmap, x, y))
                break;
            last = new SKPoint(x, y);
        }
        return last;
    }

    private static bool SegmentStaysInside(SKBitmap bitmap, SKPoint a, SKPoint b)
    {
        var distance = Dist(a.X, a.Y, b.X, b.Y);
        if (distance < 1f) return true;
        var steps = Math.Max(2, (int)MathF.Ceiling(distance / 1.25f));
        for (var i = 1; i < steps; i++)
        {
            var t = i / (float)steps;
            var x = a.X + (b.X - a.X) * t;
            var y = a.Y + (b.Y - a.Y) * t;
            if (!IsInside(bitmap, x, y))
                return false;
        }
        return true;
    }

    private static bool IsInside(SKBitmap bitmap, float x, float y)
    {
        var ix = (int)MathF.Round(x);
        var iy = (int)MathF.Round(y);
        if (ix < 0 || iy < 0 || ix >= bitmap.Width || iy >= bitmap.Height)
            return false;
        return bitmap.GetPixel(ix, iy).Alpha > 36;
    }

    private static SKPoint Lerp(SKPoint a, SKPoint b, float t)
        => new(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t);

    private static List<Track> BuildTracks(SKBitmap bitmap, int stepY)
    {
        var tracks = new List<Track>();
        var active = new List<int>();
        var maxCenterGap = Math.Max(8f, stepY * 6f);

        for (var y = 0; y < bitmap.Height; y += stepY)
        {
            var runs = GetRuns(bitmap, y);
            if (runs.Count == 0)
            {
                active.Clear();
                continue;
            }

            var next = new List<int>();
            var usedTrack = new HashSet<int>();
            foreach (var run in runs)
            {
                var best = -1;
                var bestScore = float.MaxValue;
                foreach (var ti in active)
                {
                    if (usedTrack.Contains(ti)) continue;
                    var track = tracks[ti];
                    if (Math.Abs(y - track.LastY) > stepY * 2) continue;
                    var prev = track.Runs[^1];
                    var overlap = Math.Min(run.Right, prev.Right) - Math.Max(run.Left, prev.Left);
                    var centerGap = MathF.Abs(run.Center - prev.Center);
                    if (overlap < -2 && centerGap > maxCenterGap) continue;

                    var widthChange = MathF.Abs(run.Width - prev.Width) * .10f;
                    var gapPenalty = overlap >= 0 ? 0f : MathF.Min(18f, -overlap * .75f + 5f);
                    var score = centerGap + widthChange + gapPenalty - Math.Max(0, overlap) * .32f;
                    if (score < bestScore)
                    {
                        bestScore = score;
                        best = ti;
                    }
                }

                if (best < 0)
                {
                    var track = new Track();
                    track.Runs.Add(run);
                    tracks.Add(track);
                    best = tracks.Count - 1;
                }
                else
                {
                    tracks[best].Runs.Add(run);
                }

                usedTrack.Add(best);
                next.Add(best);
            }
            active = next;
        }
        return tracks;
    }

    private static List<RowRun> GetRuns(SKBitmap bitmap, int y)
    {
        var result = new List<RowRun>();
        var x = 0;
        while (x < bitmap.Width)
        {
            while (x < bitmap.Width && bitmap.GetPixel(x, y).Alpha <= 36) x++;
            if (x >= bitmap.Width) break;
            var left = x;
            while (x < bitmap.Width && bitmap.GetPixel(x, y).Alpha > 36) x++;
            var right = x - 1;
            if (right - left >= 1)
                result.Add(new RowRun(y, left, right));
        }
        return result;
    }

    private static List<Track> OrderTracks(List<Track> tracks)
    {
        if (tracks.Count <= 1) return tracks;
        var remaining = new List<Track>(tracks);
        var ordered = new List<Track>(tracks.Count);

        var minX = remaining.Min(t => t.MinX);
        var first = remaining
            .Where(t => t.MinX <= minX + 8f)
            .OrderByDescending(t => t.VerticalSpan)
            .ThenByDescending(t => t.Runs.Count)
            .FirstOrDefault() ?? remaining.OrderBy(t => t.MinX).First();
        ordered.Add(first);
        remaining.Remove(first);

        var endX = first.Runs[^1].Center;
        var endY = first.Runs[^1].Y;
        while (remaining.Count > 0)
        {
            Track? best = null;
            var bestScore = float.MaxValue;
            foreach (var track in remaining)
            {
                var a = track.Runs[0];
                var b = track.Runs[^1];
                var da = Dist(endX, endY, a.Center, a.Y);
                var db = Dist(endX, endY, b.Center, b.Y);
                var local = Math.Min(da, db);
                var score = local + Math.Max(0, track.MinX - endX) * .04f;
                if (score < bestScore)
                {
                    bestScore = score;
                    best = track;
                }
            }

            if (best is null) break;
            var d0 = Dist(endX, endY, best.Runs[0].Center, best.Runs[0].Y);
            var d1 = Dist(endX, endY, best.Runs[^1].Center, best.Runs[^1].Y);
            if (d1 < d0)
                best.Runs.Reverse();
            ordered.Add(best);
            remaining.Remove(best);
            endX = best.Runs[^1].Center;
            endY = best.Runs[^1].Y;
        }
        return ordered;
    }

    private static float Dist(float x1, float y1, float x2, float y2)
    {
        var dx = x2 - x1;
        var dy = y2 - y1;
        return MathF.Sqrt(dx * dx + dy * dy);
    }

    private static void NormalizePhysicalSize(List<StitchPoint> points, float targetHeightMm)
    {
        var used = points.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        if (used.Count == 0) return;
        var minX = used.Min(p => p.X);
        var maxX = used.Max(p => p.X);
        var minY = used.Min(p => p.Y);
        var maxY = used.Max(p => p.Y);
        var h = Math.Max(.1f, maxY - minY);
        var scale = Math.Clamp(targetHeightMm / h, .65f, 1.65f);
        var cx = (minX + maxX) * .5f;
        var cy = (minY + maxY) * .5f;
        for (var i = 0; i < points.Count; i++)
        {
            var p = points[i];
            points[i] = p with
            {
                X = cx + (p.X - cx) * scale,
                Y = cy + (p.Y - cy) * scale
            };
        }
    }

    private static void ApplyRotation(List<StitchPoint> points, float degrees)
    {
        if (MathF.Abs(degrees) < .01f) return;
        var used = points.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var minX = used.Min(p => p.X);
        var maxX = used.Max(p => p.X);
        var minY = used.Min(p => p.Y);
        var maxY = used.Max(p => p.Y);
        var cx = (minX + maxX) * .5f;
        var cy = (minY + maxY) * .5f;
        var radians = degrees * MathF.PI / 180f;
        var c = MathF.Cos(radians);
        var s = MathF.Sin(radians);
        for (var i = 0; i < points.Count; i++)
        {
            var p = points[i];
            var dx = p.X - cx;
            var dy = p.Y - cy;
            points[i] = p with
            {
                X = cx + dx * c - dy * s,
                Y = cy + dx * s + dy * c
            };
        }
    }
}
