using SkiaSharp;

namespace BordattoStudio.Core;

public static class EmbroideryEngine
{
    private sealed record RowRun(int Y, int Left, int Right)
    {
        public float Center => (Left + Right) * .5f;
        public int Width => Right - Left + 1;
    }

    private sealed class SatinTrack
    {
        public List<RowRun> Runs { get; } = [];
        public float LastCenter => Runs.Count == 0 ? 0 : Runs[^1].Center;
        public int LastY => Runs.Count == 0 ? int.MinValue : Runs[^1].Y;
        public float MinCenter => Runs.Count == 0 ? 0 : Runs.Min(r => r.Center);
        public float AverageCenter => Runs.Count == 0 ? 0 : Runs.Average(r => r.Center);
    }

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

        // A referência trabalha com uma sequência Satin muito mais densa e orientada ao traço.
        // Em 6 px/mm, 1 px equivale a ~0,167 mm.
        var densityPx = Math.Max(1, (int)MathF.Round(Math.Clamp(settings.DensityMm, .15f, .90f) * pxPerMm));
        var pullPx = Math.Clamp(settings.PullCompensationMm, 0f, 1.5f) * pxPerMm;
        var spacingPx = textPx * .045f;
        var cursorPx = 0f;
        var raw = new List<StitchPoint>();

        void AddPx(float x, float y, StitchCommand command)
            => raw.Add(new StitchPoint(x / pxPerMm, y / pxPerMm, command, model.Color));

        void JumpTo(float x, float y)
            => AddPx(x, y, StitchCommand.Jump);

        void StitchTo(float x, float y)
            => AddPx(x, y, StitchCommand.Stitch);

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

            // Em vez de varrer colunas inteiras (que fazia o M virar linhas verticais enormes),
            // seguimos as faixas horizontais do glifo e encadeamos essas faixas em trilhas locais.
            // Para um traço vertical isso gera Satin horizontal, exatamente como se vê no vídeo.
            var tracks = BuildStrokeTracks(bitmap, densityPx);
            var useful = tracks
                .Where(t => t.Runs.Count >= Math.Max(4, (int)MathF.Round(pxPerMm * .8f / densityPx)))
                .OrderBy(t => t.MinCenter)
                .ThenBy(t => t.Runs[0].Y)
                .ToList();

            foreach (var track in useful)
            {
                var runs = track.Runs;
                if (runs.Count < 2) continue;

                // 1) Underlay local do MESMO traço. Não percorre a palavra inteira antes do Satin.
                if (settings.CenterUnderlay)
                {
                    var underlayStride = Math.Max(2, (int)MathF.Round((1.35f * pxPerMm) / densityPx));
                    var first = runs[0];
                    JumpTo(cursorPx + first.Center, first.Y);
                    StitchTo(cursorPx + first.Center, first.Y);
                    for (var i = underlayStride; i < runs.Count; i += underlayStride)
                    {
                        var r = runs[i];
                        StitchTo(cursorPx + r.Center, r.Y);
                    }
                    var last = runs[^1];
                    StitchTo(cursorPx + last.Center, last.Y);
                }

                if (settings.EdgeUnderlay)
                {
                    var edgeStride = Math.Max(2, (int)MathF.Round((1.0f * pxPerMm) / densityPx));
                    var first = runs[0];
                    JumpTo(cursorPx + first.Left + first.Width * .26f, first.Y);
                    StitchTo(cursorPx + first.Left + first.Width * .26f, first.Y);
                    for (var i = edgeStride; i < runs.Count; i += edgeStride)
                    {
                        var r = runs[i];
                        StitchTo(cursorPx + r.Left + r.Width * .26f, r.Y);
                    }
                }

                // 2) Volta somente ao início desta trilha e borda o Satin imediatamente.
                // Cada passo troca de lado, fazendo a agulha preencher o traço local antes de seguir adiante.
                var firstRun = runs[0];
                var firstLeft = firstRun.Left - pullPx * .5f;
                JumpTo(cursorPx + firstLeft, firstRun.Y);
                StitchTo(cursorPx + firstLeft, firstRun.Y);

                var rightSide = true;
                for (var i = 1; i < runs.Count; i++)
                {
                    var r = runs[i];
                    var satinWidthMm = r.Width / pxPerMm;
                    var compensation = satinWidthMm <= Math.Max(3f, settings.SatinMaxWidthMm) ? pullPx * .5f : 0f;
                    var x = rightSide ? r.Right + compensation : r.Left - compensation;
                    StitchTo(cursorPx + x, r.Y);
                    rightSide = !rightSide;
                }

                // Pequeno tie-out local, sem criar linha atravessando outra letra.
                var end = raw.LastOrDefault(p => p.Command == StitchCommand.Stitch);
                if (end.Command == StitchCommand.Stitch)
                {
                    raw.Add(new StitchPoint(end.X + .18f, end.Y, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y + .18f, StitchCommand.Stitch, model.Color));
                    raw.Add(new StitchPoint(end.X, end.Y, StitchCommand.Stitch, model.Color));
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
        var lastStitch = rotated.Last(p => p.Command == StitchCommand.Stitch);
        rotated.Add(new StitchPoint(lastStitch.X, lastStitch.Y, StitchCommand.End, model.Color));

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

    private static List<SatinTrack> BuildStrokeTracks(SKBitmap bitmap, int stepY)
    {
        var tracks = new List<SatinTrack>();
        var active = new List<int>();
        var maxCenterGap = Math.Max(7f, stepY * 5.5f);

        for (var y = 0; y < bitmap.Height; y += stepY)
        {
            var runs = new List<RowRun>();
            var x = 0;
            while (x < bitmap.Width)
            {
                while (x < bitmap.Width && bitmap.GetPixel(x, y).Alpha <= 24) x++;
                if (x >= bitmap.Width) break;
                var left = x;
                while (x < bitmap.Width && bitmap.GetPixel(x, y).Alpha > 24) x++;
                var right = x - 1;
                if (right - left >= 1) runs.Add(new RowRun(y, left, right));
            }

            if (runs.Count == 0)
            {
                active.Clear();
                continue;
            }

            var nextActive = new List<int>();
            var used = new HashSet<int>();

            foreach (var run in runs)
            {
                var bestTrack = -1;
                var bestScore = float.MaxValue;
                foreach (var ti in active)
                {
                    if (used.Contains(ti)) continue;
                    var t = tracks[ti];
                    if (y - t.LastY > stepY * 2) continue;
                    var prev = t.Runs[^1];
                    var overlaps = run.Left <= prev.Right + 2 && run.Right >= prev.Left - 2;
                    var gap = MathF.Abs(run.Center - prev.Center);
                    if (!overlaps && gap > maxCenterGap) continue;
                    var score = gap + (overlaps ? 0 : maxCenterGap * .45f);
                    if (score < bestScore)
                    {
                        bestScore = score;
                        bestTrack = ti;
                    }
                }

                if (bestTrack < 0)
                {
                    var t = new SatinTrack();
                    t.Runs.Add(run);
                    tracks.Add(t);
                    bestTrack = tracks.Count - 1;
                }
                else
                {
                    tracks[bestTrack].Runs.Add(run);
                }

                used.Add(bestTrack);
                nextActive.Add(bestTrack);
            }

            active = nextActive;
        }

        return tracks;
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
