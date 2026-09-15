using SkiaSharp;

namespace BordattoStudio.Core;

internal static class StrokeSatinDigitizer
{
    private readonly record struct Pixel(int X, int Y);
    private readonly record struct RailPair(SKPoint Center, SKPoint Left, SKPoint Right, float WidthPx);

    private sealed class StrokePath
    {
        public List<Pixel> Points { get; } = [];
        public float MinX => Points.Count == 0 ? 0 : Points.Min(p => p.X);
        public float MinY => Points.Count == 0 ? 0 : Points.Min(p => p.Y);
        public float MaxX => Points.Count == 0 ? 0 : Points.Max(p => p.X);
        public float MaxY => Points.Count == 0 ? 0 : Points.Max(p => p.Y);
        public float HorizontalSpan => MaxX - MinX;
        public float VerticalSpan => MaxY - MinY;
        public float Length
        {
            get
            {
                var total = 0f;
                for (var i = 1; i < Points.Count; i++)
                {
                    var dx = Points[i].X - Points[i - 1].X;
                    var dy = Points[i].Y - Points[i - 1].Y;
                    total += MathF.Sqrt(dx * dx + dy * dy);
                }
                return total;
            }
        }
    }

    public static EmbroideryDesign Generate(TextObjectModel model, EngineSettings settings, BordattoMode mode)
    {
        var clean = string.Join(" ", model.Text.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries));
        if (string.IsNullOrWhiteSpace(clean))
            throw new InvalidOperationException("Digite um nome para gerar a matriz.");
        clean = clean[..Math.Min(clean.Length, 28)];

        const float pxPerMm = 8f;
        var heightMm = Math.Clamp(model.HeightMm * model.Scale, 5f, 80f);
        var textPx = heightMm * pxPerMm;
        var style = model.Bold && model.Italic
            ? SKFontStyle.BoldItalic
            : model.Bold ? SKFontStyle.Bold : model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;

        using var typeface = SKTypeface.FromFamilyName(model.FontFamily, style) ?? SKTypeface.Default;
        using var font = new SKFont(typeface, textPx);
        using var paint = new SKPaint
        {
            Color = SKColors.White,
            IsAntialias = true,
            Style = SKPaintStyle.Fill
        };

        // Tracking aproximado do vídeo de referência: “Maria” fica perto de 89 mm de largura.
        var spacingPx = textPx * .18f;
        var cursorPx = 0f;
        var raw = new List<StitchPoint>();
        var pullPx = Math.Clamp(settings.PullCompensationMm, 0f, 1.5f) * pxPerMm;
        var sampleSpacingPx = Math.Max(1.05f, Math.Clamp(settings.DensityMm, .12f, .80f) * pxPerMm);

        void AddPx(float x, float y, StitchCommand command)
            => raw.Add(new StitchPoint(x / pxPerMm, y / pxPerMm, command, model.Color));

        void Jump(float x, float y) => AddPx(x, y, StitchCommand.Jump);
        void Stitch(float x, float y) => AddPx(x, y, StitchCommand.Stitch);

        foreach (var ch in clean)
        {
            if (ch == ' ')
            {
                cursorPx += textPx * .42f;
                continue;
            }

            var token = ch.ToString();
            var advance = Math.Max(font.MeasureText(token, out var bounds, paint), textPx * .22f);
            var margin = Math.Max(14, (int)MathF.Ceiling(pxPerMm * 3f));
            var bitmapW = Math.Clamp((int)MathF.Ceiling(bounds.Width) + margin * 2, 48, 1800);
            var bitmapH = Math.Clamp((int)MathF.Ceiling(bounds.Height) + margin * 2, 48, 1800);

            using var bitmap = new SKBitmap(bitmapW, bitmapH, SKColorType.Bgra8888, SKAlphaType.Premul);
            using (var canvas = new SKCanvas(bitmap))
            {
                canvas.Clear(SKColors.Transparent);
                canvas.DrawText(token, margin - bounds.Left, margin - bounds.Top, SKTextAlign.Left, font, paint);
                canvas.Flush();
            }

            var mask = BuildMask(bitmap);
            var skeleton = Thin(mask);
            var paths = ExtractPaths(skeleton)
                .Where(p => p.Points.Count >= 3 && p.Length >= pxPerMm * .85f)
                .ToList();

            var ordered = OrderPaths(paths, pxPerMm);
            foreach (var path in ordered)
            {
                var sampled = Resample(path.Points, sampleSpacingPx);
                if (sampled.Count < 2) continue;

                var pairs = BuildRailPairs(sampled, mask, settings, pxPerMm, pullPx);
                if (pairs.Count < 2) continue;

                // Underlay local do mesmo traço: primeiro percorre apenas o eixo daquela haste/curva.
                if (settings.CenterUnderlay)
                {
                    var stride = Math.Max(1, (int)MathF.Round((1.25f * pxPerMm) / sampleSpacingPx));
                    Jump(cursorPx + pairs[0].Center.X, pairs[0].Center.Y);
                    Stitch(cursorPx + pairs[0].Center.X, pairs[0].Center.Y);
                    for (var i = stride; i < pairs.Count; i += stride)
                        Stitch(cursorPx + pairs[i].Center.X, pairs[i].Center.Y);
                    var last = pairs[^1];
                    Stitch(cursorPx + last.Center.X, last.Center.Y);
                }

                if (settings.EdgeUnderlay)
                {
                    var stride = Math.Max(1, (int)MathF.Round((1.0f * pxPerMm) / sampleSpacingPx));
                    var first = Lerp(pairs[0].Center, pairs[0].Left, .58f);
                    Jump(cursorPx + first.X, first.Y);
                    Stitch(cursorPx + first.X, first.Y);
                    for (var i = stride; i < pairs.Count; i += stride)
                    {
                        var p = Lerp(pairs[i].Center, pairs[i].Left, .58f);
                        Stitch(cursorPx + p.X, p.Y);
                    }
                }

                // Satin verdadeiro por pares: em cada avanço longitudinal a agulha atravessa
                // de um lado ao outro da coluna. Isso evita o “desenho de linha” da 0.3.2.
                var firstPair = pairs[0];
                Jump(cursorPx + firstPair.Left.X, firstPair.Left.Y);
                Stitch(cursorPx + firstPair.Left.X, firstPair.Left.Y);
                Stitch(cursorPx + firstPair.Right.X, firstPair.Right.Y);

                for (var i = 1; i < pairs.Count; i++)
                {
                    var pair = pairs[i];
                    Stitch(cursorPx + pair.Left.X, pair.Left.Y);
                    Stitch(cursorPx + pair.Right.X, pair.Right.Y);
                }

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

        return FinalizeDesign(clean, raw, model, mode);
    }

    private static bool[,] BuildMask(SKBitmap bitmap)
    {
        var mask = new bool[bitmap.Width, bitmap.Height];
        for (var y = 0; y < bitmap.Height; y++)
        for (var x = 0; x < bitmap.Width; x++)
            mask[x, y] = bitmap.GetPixel(x, y).Alpha > 42;
        return mask;
    }

    private static bool[,] Thin(bool[,] source)
    {
        var w = source.GetLength(0);
        var h = source.GetLength(1);
        var img = (bool[,])source.Clone();
        var remove = new List<Pixel>();
        var changed = true;
        var iteration = 0;

        while (changed && iteration++ < 160)
        {
            changed = false;
            remove.Clear();
            for (var y = 1; y < h - 1; y++)
            for (var x = 1; x < w - 1; x++)
            {
                if (!img[x, y]) continue;
                var n = NeighbourBits(img, x, y);
                var b = n.Sum();
                var a = Transitions(n);
                if (b is >= 2 and <= 6 && a == 1 && n[0] * n[2] * n[4] == 0 && n[2] * n[4] * n[6] == 0)
                    remove.Add(new Pixel(x, y));
            }
            if (remove.Count > 0)
            {
                changed = true;
                foreach (var p in remove) img[p.X, p.Y] = false;
            }

            remove.Clear();
            for (var y = 1; y < h - 1; y++)
            for (var x = 1; x < w - 1; x++)
            {
                if (!img[x, y]) continue;
                var n = NeighbourBits(img, x, y);
                var b = n.Sum();
                var a = Transitions(n);
                if (b is >= 2 and <= 6 && a == 1 && n[0] * n[2] * n[6] == 0 && n[0] * n[4] * n[6] == 0)
                    remove.Add(new Pixel(x, y));
            }
            if (remove.Count > 0)
            {
                changed = true;
                foreach (var p in remove) img[p.X, p.Y] = false;
            }
        }
        return img;
    }

    private static int[] NeighbourBits(bool[,] img, int x, int y)
        =>
        [
            img[x, y - 1] ? 1 : 0,       // p2
            img[x + 1, y - 1] ? 1 : 0,   // p3
            img[x + 1, y] ? 1 : 0,       // p4
            img[x + 1, y + 1] ? 1 : 0,   // p5
            img[x, y + 1] ? 1 : 0,       // p6
            img[x - 1, y + 1] ? 1 : 0,   // p7
            img[x - 1, y] ? 1 : 0,       // p8
            img[x - 1, y - 1] ? 1 : 0    // p9
        ];

    private static int Transitions(int[] n)
    {
        var a = 0;
        for (var i = 0; i < 8; i++)
            if (n[i] == 0 && n[(i + 1) % 8] == 1) a++;
        return a;
    }

    private static List<StrokePath> ExtractPaths(bool[,] skeleton)
    {
        var w = skeleton.GetLength(0);
        var h = skeleton.GetLength(1);
        var pixels = new List<Pixel>();
        for (var y = 0; y < h; y++)
        for (var x = 0; x < w; x++)
            if (skeleton[x, y]) pixels.Add(new Pixel(x, y));

        List<Pixel> Neighbors(Pixel p)
        {
            var list = new List<Pixel>(8);
            for (var dy = -1; dy <= 1; dy++)
            for (var dx = -1; dx <= 1; dx++)
            {
                if (dx == 0 && dy == 0) continue;
                var nx = p.X + dx; var ny = p.Y + dy;
                if (nx >= 0 && nx < w && ny >= 0 && ny < h && skeleton[nx, ny])
                    list.Add(new Pixel(nx, ny));
            }
            return list;
        }

        long Id(Pixel p) => (long)p.Y * w + p.X;
        ulong Edge(Pixel a, Pixel b)
        {
            var ia = (ulong)Id(a); var ib = (ulong)Id(b);
            var lo = Math.Min(ia, ib); var hi = Math.Max(ia, ib);
            return (lo << 32) ^ hi;
        }

        var used = new HashSet<ulong>();
        var paths = new List<StrokePath>();

        StrokePath Trace(Pixel start, Pixel next)
        {
            var path = new StrokePath();
            path.Points.Add(start);
            var prev = start;
            var current = next;
            used.Add(Edge(prev, current));
            var guard = 0;

            while (guard++ < w * h)
            {
                path.Points.Add(current);
                var neighbours = Neighbors(current);
                if (!current.Equals(start) && neighbours.Count != 2) break;

                Pixel? candidate = null;
                foreach (var n in neighbours)
                {
                    if (n.Equals(prev)) continue;
                    if (used.Contains(Edge(current, n))) continue;
                    candidate = n;
                    break;
                }
                if (candidate is null) break;
                prev = current;
                current = candidate.Value;
                used.Add(Edge(prev, current));
                if (current.Equals(start))
                {
                    path.Points.Add(current);
                    break;
                }
            }
            return path;
        }

        foreach (var p in pixels)
        {
            var neighbours = Neighbors(p);
            if (neighbours.Count == 2) continue;
            foreach (var n in neighbours)
            {
                if (used.Contains(Edge(p, n))) continue;
                var path = Trace(p, n);
                if (path.Points.Count >= 2) paths.Add(path);
            }
        }

        // Ciclos (a, o, e etc.) não têm endpoint. Percorre as arestas restantes.
        foreach (var p in pixels)
        foreach (var n in Neighbors(p))
        {
            if (used.Contains(Edge(p, n))) continue;
            var path = Trace(p, n);
            if (path.Points.Count >= 2) paths.Add(path);
        }

        return paths;
    }

    private static List<StrokePath> OrderPaths(List<StrokePath> paths, float pxPerMm)
    {
        if (paths.Count <= 1) return paths;
        var remaining = new List<StrokePath>(paths);
        var ordered = new List<StrokePath>(paths.Count);
        var globalMinX = remaining.Min(p => p.MinX);
        var leftBand = globalMinX + pxPerMm * 1.2f;
        var first = remaining
            .Where(p => p.MinX <= leftBand)
            .OrderByDescending(p => p.VerticalSpan)
            .ThenByDescending(p => p.Length)
            .FirstOrDefault() ?? remaining.OrderBy(p => p.MinX).ThenBy(p => p.MinY).First();

        OrientFirst(first);
        ordered.Add(first);
        remaining.Remove(first);
        var current = first.Points[^1];

        while (remaining.Count > 0)
        {
            StrokePath? best = null;
            var reverse = false;
            var bestScore = float.MaxValue;
            foreach (var p in remaining)
            {
                var d0 = Distance(current, p.Points[0]);
                var d1 = Distance(current, p.Points[^1]);
                var score = Math.Min(d0, d1) + p.MinX * .015f;
                if (score < bestScore)
                {
                    bestScore = score;
                    best = p;
                    reverse = d1 < d0;
                }
            }
            if (best is null) break;
            if (reverse) best.Points.Reverse();
            ordered.Add(best);
            current = best.Points[^1];
            remaining.Remove(best);
        }
        return ordered;
    }

    private static void OrientFirst(StrokePath path)
    {
        if (path.Points.Count < 2) return;
        var a = path.Points[0];
        var b = path.Points[^1];
        if (path.VerticalSpan >= path.HorizontalSpan)
        {
            // O vídeo inicia a haste esquerda do M pelo topo e desce.
            if (a.Y > b.Y) path.Points.Reverse();
        }
        else if (a.X > b.X)
            path.Points.Reverse();
    }

    private static float Distance(Pixel a, Pixel b)
    {
        var dx = a.X - b.X; var dy = a.Y - b.Y;
        return MathF.Sqrt(dx * dx + dy * dy);
    }

    private static List<SKPoint> Resample(IReadOnlyList<Pixel> path, float spacing)
    {
        var result = new List<SKPoint>();
        if (path.Count == 0) return result;
        result.Add(new SKPoint(path[0].X, path[0].Y));
        var remaining = spacing;
        var ax = (float)path[0].X; var ay = (float)path[0].Y;

        for (var i = 1; i < path.Count; i++)
        {
            var bx = (float)path[i].X; var by = (float)path[i].Y;
            while (true)
            {
                var dx = bx - ax; var dy = by - ay;
                var len = MathF.Sqrt(dx * dx + dy * dy);
                if (len < 0.0001f) break;
                if (len < remaining)
                {
                    remaining -= len;
                    ax = bx; ay = by;
                    break;
                }
                var t = remaining / len;
                ax += dx * t; ay += dy * t;
                result.Add(new SKPoint(ax, ay));
                remaining = spacing;
            }
        }

        var last = path[^1];
        if (result.Count == 0 || MathF.Abs(result[^1].X - last.X) + MathF.Abs(result[^1].Y - last.Y) > spacing * .35f)
            result.Add(new SKPoint(last.X, last.Y));
        return result;
    }

    private static List<RailPair> BuildRailPairs(
        IReadOnlyList<SKPoint> centers,
        bool[,] mask,
        EngineSettings settings,
        float pxPerMm,
        float pullPx)
    {
        var pairs = new List<RailPair>(centers.Count);
        var maxRadius = Math.Max(12f, settings.SatinMaxWidthMm * pxPerMm * .75f);

        for (var i = 0; i < centers.Count; i++)
        {
            var prev = centers[Math.Max(0, i - 1)];
            var next = centers[Math.Min(centers.Count - 1, i + 1)];
            var tx = next.X - prev.X; var ty = next.Y - prev.Y;
            var len = MathF.Sqrt(tx * tx + ty * ty);
            if (len < .001f) continue;
            tx /= len; ty /= len;
            var nx = -ty; var ny = tx;
            var c = centers[i];
            var left = WalkEdge(mask, c, nx, ny, maxRadius);
            var right = WalkEdge(mask, c, -nx, -ny, maxRadius);
            var wx = left.X - right.X; var wy = left.Y - right.Y;
            var width = MathF.Sqrt(wx * wx + wy * wy);
            if (width < 1.2f) continue;

            var widthMm = width / pxPerMm;
            var compensation = widthMm <= settings.SatinMaxWidthMm ? pullPx * .5f : 0f;
            left = new SKPoint(left.X + nx * compensation, left.Y + ny * compensation);
            right = new SKPoint(right.X - nx * compensation, right.Y - ny * compensation);
            pairs.Add(new RailPair(c, left, right, width));
        }
        return pairs;
    }

    private static SKPoint WalkEdge(bool[,] mask, SKPoint center, float dx, float dy, float maxRadius)
    {
        var last = center;
        var outside = 0;
        for (var d = .5f; d <= maxRadius; d += .5f)
        {
            var x = center.X + dx * d;
            var y = center.Y + dy * d;
            if (Inside(mask, x, y))
            {
                last = new SKPoint(x, y);
                outside = 0;
            }
            else if (++outside >= 2)
                break;
        }
        return last;
    }

    private static bool Inside(bool[,] mask, float x, float y)
    {
        var ix = (int)MathF.Round(x); var iy = (int)MathF.Round(y);
        return ix >= 0 && ix < mask.GetLength(0) && iy >= 0 && iy < mask.GetLength(1) && mask[ix, iy];
    }

    private static SKPoint Lerp(SKPoint a, SKPoint b, float t)
        => new(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t);

    private static EmbroideryDesign FinalizeDesign(string name, List<StitchPoint> raw, TextObjectModel model, BordattoMode mode)
    {
        var points = raw.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        var minX = points.Min(p => p.X); var maxX = points.Max(p => p.X);
        var minY = points.Min(p => p.Y); var maxY = points.Max(p => p.Y);
        var cx = (minX + maxX) * .5f; var cy = (minY + maxY) * .5f;
        var radians = model.RotationDegrees * MathF.PI / 180f;
        var cos = MathF.Cos(radians); var sin = MathF.Sin(radians);

        var rotated = new List<StitchPoint>(raw.Count + 1);
        foreach (var p in raw)
        {
            var dx = p.X - cx; var dy = p.Y - cy;
            rotated.Add(p with
            {
                X = cx + dx * cos - dy * sin,
                Y = cy + dx * sin + dy * cos
            });
        }

        var last = rotated.Last(p => p.Command == StitchCommand.Stitch);
        rotated.Add(new StitchPoint(last.X, last.Y, StitchCommand.End, model.Color));
        var used = rotated.Where(p => p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();

        return new EmbroideryDesign
        {
            Name = name,
            Stitches = rotated,
            WidthMm = used.Max(p => p.X) - used.Min(p => p.X),
            HeightMm = used.Max(p => p.Y) - used.Min(p => p.Y),
            ThreadColor = model.Color,
            ThreadName = model.Color == 0xFF000000 ? "Preto" : "Rosa Intenso",
            ThreadBrand = "Brother",
            ThreadCode = model.Color == 0xFF000000 ? "900" : "086"
        };
    }
}
