using SkiaSharp;

namespace BordattoStudio.Core;

// 0.3.4: mantém o glifo CHEIO e divide cada letra em trilhas locais.
// Não usa skeleton/thinning: o caminho é derivado diretamente da área real do glifo.
internal static class TrackSatinDigitizer034
{
    private sealed record RowRun(int Y, int Left, int Right)
    {
        public float Center => (Left + Right) * .5f;
        public int Width => Right - Left + 1;
    }

    private sealed class Track
    {
        public List<RowRun> Runs { get; } = [];
        public float MinX => Runs.Count == 0 ? 0 : Runs.Min(r => r.Left);
        public float MaxX => Runs.Count == 0 ? 0 : Runs.Max(r => r.Right);
        public float CenterX => (MinX + MaxX) * .5f;
        public int FirstY => Runs.Count == 0 ? 0 : Runs[0].Y;
        public int LastY => Runs.Count == 0 ? 0 : Runs[^1].Y;
        public float LastCenter => Runs.Count == 0 ? 0 : Runs[^1].Center;
        public float VerticalSpan => Runs.Count == 0 ? 0 : Runs[^1].Y - Runs[0].Y;
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

        // Cada pixel vertical representa ~0,143 mm: densidade próxima de lettering Satin real.
        var rowStep = Math.Max(1, (int)MathF.Round(Math.Clamp(settings.DensityMm, .14f, .45f) * pxPerMm));
        var pullPx = Math.Clamp(settings.PullCompensationMm, 0f, 1.2f) * pxPerMm;
        var spacingPx = textPx * .075f;
        var cursorPx = 0f;
        var raw = new List<StitchPoint>();

        void AddPx(float x, float y, StitchCommand command)
            => raw.Add(new StitchPoint(x / pxPerMm, y / pxPerMm, command, model.Color));
        void Jump(float x, float y) => AddPx(x, y, StitchCommand.Jump);
        void Stitch(float x, float y) => AddPx(x, y, StitchCommand.Stitch);

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

            // Começa pela haste mais à esquerda e prioriza uma haste longa/vertical.
            // Depois segue pela trilha cujo início está mais perto do fim da anterior.
            var ordered = OrderTracks(tracks);

            foreach (var track in ordered)
            {
                var runs = track.Runs;
                if (runs.Count < 2) continue;

                // Orientação: primeira haste esquerda desce de cima para baixo como na referência.
                if (runs[0].Y > runs[^1].Y)
                    runs.Reverse();

                // 1) Underlay somente desta haste/curva.
                if (settings.CenterUnderlay)
                {
                    var stride = Math.Max(2, (int)MathF.Round((1.25f * pxPerMm) / rowStep));
                    var first = runs[0];
                    Jump(cursorPx + first.Center, first.Y);
                    Stitch(cursorPx + first.Center, first.Y);
                    for (var i = stride; i < runs.Count; i += stride)
                    {
                        var r = runs[i];
                        Stitch(cursorPx + r.Center, r.Y);
                    }
                    var last = runs[^1];
                    Stitch(cursorPx + last.Center, last.Y);
                }

                if (settings.EdgeUnderlay)
                {
                    var stride = Math.Max(2, (int)MathF.Round((.95f * pxPerMm) / rowStep));
                    var first = runs[0];
                    Jump(cursorPx + first.Left + first.Width * .28f, first.Y);
                    Stitch(cursorPx + first.Left + first.Width * .28f, first.Y);
                    for (var i = stride; i < runs.Count; i += stride)
                    {
                        var r = runs[i];
                        Stitch(cursorPx + r.Left + r.Width * .28f, r.Y);
                    }
                }

                // 2) Volta ao início da MESMA haste e aplica Satin cheio.
                // Dois pontos por avanço (esquerda→direita / direita→esquerda) deixam o preenchimento
                // contínuo e evitam o aspecto de esqueleto/linha da 0.3.3.
                var f = runs[0];
                var fComp = (f.Width / pxPerMm <= settings.SatinMaxWidthMm ? pullPx * .5f : 0f);
                Jump(cursorPx + f.Left - fComp, f.Y);
                Stitch(cursorPx + f.Left - fComp, f.Y);
                Stitch(cursorPx + f.Right + fComp, f.Y);

                var reversePair = true;
                for (var i = 1; i < runs.Count; i++)
                {
                    var r = runs[i];
                    var widthMm = r.Width / pxPerMm;
                    var comp = widthMm <= settings.SatinMaxWidthMm ? pullPx * .5f : 0f;
                    var left = cursorPx + r.Left - comp;
                    var right = cursorPx + r.Right + comp;
                    if (reversePair)
                    {
                        Stitch(right, r.Y);
                        Stitch(left, r.Y);
                    }
                    else
                    {
                        Stitch(left, r.Y);
                        Stitch(right, r.Y);
                    }
                    reversePair = !reversePair;
                }

                // tie-out curto e local.
                var end = raw.LastOrDefault(p => p.Command == StitchCommand.Stitch);
                if (end.Command == StitchCommand.Stitch)
                {
                    raw.Add(new StitchPoint(end.X + .16f, end.Y, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y + .16f, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y, StitchCommand.Stitch, model.Color));
                }
            }

            cursorPx += advance + spacingPx;
        }

        if (raw.Count(p => p.Command == StitchCommand.Stitch) < 12)
            throw new InvalidOperationException("Não foi possível gerar pontadas suficientes para este nome.");

        // Normaliza a altura REAL do bordado. Fontes Android normalmente ocupam só ~70–78%
        // do tamanho nominal; sem isto a 0.3.3 saiu ~64×14 mm. A referência de Maria fica ~89×21 mm.
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
                    var t = tracks[ti];
                    if (y - t.LastY > stepY * 2) continue;
                    var prev = t.Runs[^1];
                    var overlap = Math.Min(run.Right, prev.Right) - Math.Max(run.Left, prev.Left);
                    var centerGap = MathF.Abs(run.Center - prev.Center);
                    if (overlap < -2 && centerGap > maxCenterGap) continue;
                    var widthChange = MathF.Abs(run.Width - prev.Width) * .12f;
                    var score = centerGap + widthChange + (overlap >= 0 ? -Math.Min(overlap, 10) * .35f : 6f);
                    if (score < bestScore)
                    {
                        bestScore = score;
                        best = ti;
                    }
                }

                if (best < 0)
                {
                    var t = new Track();
                    t.Runs.Add(run);
                    tracks.Add(t);
                    best = tracks.Count - 1;
                }
                else tracks[best].Runs.Add(run);

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
            if (right - left >= 1) result.Add(new RowRun(y, left, right));
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
        ordered.Add(first); remaining.Remove(first);

        var endX = first.Runs[^1].Center;
        var endY = first.Runs[^1].Y;
        while (remaining.Count > 0)
        {
            Track? best = null;
            var bestScore = float.MaxValue;
            foreach (var t in remaining)
            {
                var a = t.Runs[0];
                var b = t.Runs[^1];
                var da = Dist(endX, endY, a.Center, a.Y);
                var db = Dist(endX, endY, b.Center, b.Y);
                var local = Math.Min(da, db);
                // preferência leve por continuar da esquerda para direita, sem saltar para outra letra.
                var score = local + Math.Max(0, t.MinX - endX) * .04f;
                if (score < bestScore) { bestScore = score; best = t; }
            }
            if (best is null) break;
            var d0 = Dist(endX, endY, best.Runs[0].Center, best.Runs[0].Y);
            var d1 = Dist(endX, endY, best.Runs[^1].Center, best.Runs[^1].Y);
            if (d1 < d0) best.Runs.Reverse();
            ordered.Add(best); remaining.Remove(best);
            endX = best.Runs[^1].Center; endY = best.Runs[^1].Y;
        }
        return ordered;
    }

    private static float Dist(float x1, float y1, float x2, float y2)
    {
        var dx = x2 - x1; var dy = y2 - y1;
        return MathF.Sqrt(dx * dx + dy * dy);
    }

    private static void NormalizePhysicalSize(List<StitchPoint> points, float targetHeightMm)
    {
        var used = points.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        if (used.Count == 0) return;
        var minX = used.Min(p => p.X); var maxX = used.Max(p => p.X);
        var minY = used.Min(p => p.Y); var maxY = used.Max(p => p.Y);
        var h = Math.Max(.1f, maxY - minY);
        var scale = Math.Clamp(targetHeightMm / h, .65f, 1.65f);
        var cx = (minX + maxX) * .5f; var cy = (minY + maxY) * .5f;
        for (var i = 0; i < points.Count; i++)
        {
            var p = points[i];
            points[i] = p with { X = cx + (p.X - cx) * scale, Y = cy + (p.Y - cy) * scale };
        }
    }

    private static void ApplyRotation(List<StitchPoint> points, float degrees)
    {
        if (MathF.Abs(degrees) < .01f) return;
        var used = points.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var minX = used.Min(p => p.X); var maxX = used.Max(p => p.X);
        var minY = used.Min(p => p.Y); var maxY = used.Max(p => p.Y);
        var cx = (minX + maxX) * .5f; var cy = (minY + maxY) * .5f;
        var r = degrees * MathF.PI / 180f; var c = MathF.Cos(r); var s = MathF.Sin(r);
        for (var i = 0; i < points.Count; i++)
        {
            var p = points[i];
            var dx = p.X - cx; var dy = p.Y - cy;
            points[i] = p with { X = cx + dx * c - dy * s, Y = cy + dx * s + dy * c };
        }
    }
}
