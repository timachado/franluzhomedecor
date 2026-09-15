using BordattoStudio.Core;
using SkiaSharp;
using SkiaSharp.Views.Maui;
using SkiaSharp.Views.Maui.Controls;

namespace BordattoStudio.Views;

// 0.3.6: interação direta do texto no bastidor inspirada na referência.
// Arraste direto, rotação pela alça inferior central, escala pela alça inferior direita
// e gesto de dois dedos para mover + girar + escalar. O objeto inteiro permanece no bastidor.
public sealed class InteractiveTextCanvas036 : SKCanvasView
{
    private enum GestureMode { None, Drag, Rotate, Resize, Multi }

    private readonly Dictionary<long, SKPoint> _touches = [];
    private readonly Dictionary<long, SKPoint> _previousTouches = [];
    private GestureMode _gesture;
    private SKRect _hoopRect;
    private SKRect _selectionLocal;
    private SKPoint _rotateHandle;
    private SKPoint _resizeHandle;
    private SKPoint _screenCenter;
    private bool _hasGeometry;

    public TextObjectModel Model { get; set; } = new();
    public bool Selected { get; set; } = true;
    public event EventHandler? ModelChanged;

    public InteractiveTextCanvas036()
    {
        EnableTouchEvents = true;
        Touch += OnTouch;
        PaintSurface += OnPaintSurface;
        BackgroundColor = BordattoColors.Canvas;
    }

    private void OnPaintSurface(object? sender, SKPaintSurfaceEventArgs e)
    {
        var canvas = e.Surface.Canvas;
        var w = (float)e.Info.Width;
        var h = (float)e.Info.Height;
        canvas.Clear(new SKColor(0xF3, 0xEC, 0xDD));

        // Reserva espaço real para a legenda e para a alça de rotação. Assim o bastidor
        // continua quadrado e as alças não são cortadas pela borda inferior do canvas.
        var outerPad = Math.Max(28f, w * .045f);
        var captionGap = Math.Max(30f, w * .042f);
        var handleReserve = Math.Clamp(w * .065f, 48f, 72f);
        var maxSideW = Math.Max(80f, w - outerPad * 2f);
        var maxSideH = Math.Max(80f, h - outerPad * 2f - captionGap - handleReserve);
        var side = Math.Max(80f, Math.Min(maxSideW, maxSideH));
        var left = (w - side) * .5f;
        var top = outerPad + captionGap;
        if (top + side + handleReserve > h - outerPad)
            top = Math.Max(captionGap + 8f, h - outerPad - handleReserve - side);
        _hoopRect = new SKRect(left, top, left + side, top + side);

        DrawGrid(canvas);

        using var hoopPaint = new SKPaint
        {
            Color = new SKColor(0x62, 0x5D, 0x58),
            StrokeWidth = Math.Max(2.5f, w * .004f),
            Style = SKPaintStyle.Stroke,
            IsAntialias = true,
            PathEffect = SKPathEffect.CreateDash(new float[] { 12f, 9f }, 0)
        };
        canvas.DrawRoundRect(_hoopRect, 22, 22, hoopPaint);

        using var captionFont = new SKFont(SKTypeface.Default, Math.Max(13f, w * .021f));
        using var captionPaint = new SKPaint { Color = new SKColor(0x76, 0x70, 0x65), IsAntialias = true };
        canvas.DrawText("Bastidor 100 × 100 mm", _hoopRect.MidX, _hoopRect.Top - 12f, SKTextAlign.Center, captionFont, captionPaint);

        var style = Model.Bold && Model.Italic
            ? SKFontStyle.BoldItalic
            : Model.Bold ? SKFontStyle.Bold : Model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;
        using var typeface = SKTypeface.FromFamilyName(Model.FontFamily, style) ?? SKTypeface.Default;
        using var textPaint = new SKPaint
        {
            Color = EmbroideryEngine.ToSkColor(Model.Color),
            IsAntialias = true,
            Style = SKPaintStyle.Fill
        };

        var text = string.IsNullOrWhiteSpace(Model.Text) ? "Seu texto" : Model.Text;
        var pxPerMm = _hoopRect.Width / 100f;
        var textSize = Math.Clamp(Model.HeightMm * pxPerMm * Model.Scale, 8f, _hoopRect.Height * .72f);
        var textFont = new SKFont(typeface, textSize);
        textFont.MeasureText(text, out var bounds, textPaint);
        _selectionLocal = BuildSelection(bounds, textSize);

        // Se uma alteração de fonte/tamanho fizer a caixa ultrapassar o bastidor,
        // reduzimos a escala mantendo a proporção. Isso evita o caso em que só o centro
        // fica dentro, mas as extremidades do nome somem para fora do bastidor.
        var fit = GetFitFactor(_selectionLocal, Model.RotationDegrees);
        if (fit < .995f && Model.Scale > .12f)
        {
            Model.Scale = Math.Max(.12f, Model.Scale * fit * .985f);
            textFont.Dispose();
            textSize = Math.Clamp(Model.HeightMm * pxPerMm * Model.Scale, 8f, _hoopRect.Height * .72f);
            textFont = new SKFont(typeface, textSize);
            textFont.MeasureText(text, out bounds, textPaint);
            _selectionLocal = BuildSelection(bounds, textSize);
        }

        _screenCenter = new SKPoint(
            _hoopRect.Left + Math.Clamp(Model.CenterX, 0f, 1f) * _hoopRect.Width,
            _hoopRect.Top + Math.Clamp(Model.CenterY, 0f, 1f) * _hoopRect.Height);
        ConstrainCenterToHoop(updateModel: true);

        canvas.Save();
        canvas.Translate(_screenCenter.X, _screenCenter.Y);
        canvas.RotateDegrees(Model.RotationDegrees);
        canvas.DrawText(text, -bounds.MidX, -bounds.MidY, SKTextAlign.Left, textFont, textPaint);
        if (Selected)
            DrawSelection(canvas, textSize);
        canvas.Restore();

        textFont.Dispose();
        _hasGeometry = true;
    }

    private static SKRect BuildSelection(SKRect bounds, float textSize)
    {
        var margin = Math.Max(10f, textSize * .12f);
        return new SKRect(
            bounds.Left - bounds.MidX - margin,
            bounds.Top - bounds.MidY - margin,
            bounds.Right - bounds.MidX + margin,
            bounds.Bottom - bounds.MidY + margin);
    }

    private float GetFitFactor(SKRect localRect, float rotationDegrees)
    {
        if (_hoopRect.Width <= 1 || localRect.Width <= 1) return 1f;
        var r = rotationDegrees * MathF.PI / 180f;
        var c = MathF.Abs(MathF.Cos(r));
        var s = MathF.Abs(MathF.Sin(r));
        var rotatedWidth = localRect.Width * c + localRect.Height * s;
        var rotatedHeight = localRect.Width * s + localRect.Height * c;
        var innerPad = Math.Max(8f, _hoopRect.Width * .015f);
        var availableW = Math.Max(1f, _hoopRect.Width - innerPad * 2f);
        var availableH = Math.Max(1f, _hoopRect.Height - innerPad * 2f);
        return Math.Min(1f, Math.Min(availableW / Math.Max(1f, rotatedWidth), availableH / Math.Max(1f, rotatedHeight)));
    }

    private void DrawGrid(SKCanvas canvas)
    {
        using var minor = new SKPaint
        {
            Color = new SKColor(0x70, 0x68, 0x59, 0x20),
            StrokeWidth = 1,
            IsAntialias = true
        };
        using var major = new SKPaint
        {
            Color = new SKColor(0x70, 0x68, 0x59, 0x35),
            StrokeWidth = 1.4f,
            IsAntialias = true
        };

        // 10 mm por divisão principal; subdivisão de 5 mm para referência visual fina.
        for (var i = 0; i <= 20; i++)
        {
            var t = i / 20f;
            var x = _hoopRect.Left + _hoopRect.Width * t;
            var y = _hoopRect.Top + _hoopRect.Height * t;
            var paint = i % 2 == 0 ? major : minor;
            canvas.DrawLine(x, _hoopRect.Top, x, _hoopRect.Bottom, paint);
            canvas.DrawLine(_hoopRect.Left, y, _hoopRect.Right, y, paint);
        }
    }

    private void DrawSelection(SKCanvas canvas, float textSize)
    {
        using var boxPaint = new SKPaint
        {
            Color = new SKColor(0xE5, 0x17, 0x66),
            StrokeWidth = 3.1f,
            Style = SKPaintStyle.Stroke,
            IsAntialias = true
        };
        canvas.DrawRoundRect(_selectionLocal, 8, 8, boxPaint);

        var handleRadius = Math.Clamp(textSize * .18f, 17f, 24f);
        var stem = Math.Clamp(textSize * .40f, 34f, 54f);
        var rotateLocal = new SKPoint(_selectionLocal.MidX, _selectionLocal.Bottom + stem);
        var resizeLocal = new SKPoint(_selectionLocal.Right, _selectionLocal.Bottom);
        canvas.DrawLine(_selectionLocal.MidX, _selectionLocal.Bottom, rotateLocal.X, rotateLocal.Y - handleRadius * .75f, boxPaint);

        using var handleFill = new SKPaint
        {
            Color = new SKColor(0x1C, 0x1A, 0x25),
            Style = SKPaintStyle.Fill,
            IsAntialias = true
        };
        canvas.DrawCircle(rotateLocal, handleRadius, handleFill);
        canvas.DrawCircle(resizeLocal, handleRadius, handleFill);

        using var iconPaint = new SKPaint
        {
            Color = SKColors.White,
            StrokeWidth = 3,
            Style = SKPaintStyle.Stroke,
            IsAntialias = true,
            StrokeCap = SKStrokeCap.Round
        };
        var iconR = handleRadius * .46f;
        canvas.DrawArc(
            new SKRect(rotateLocal.X - iconR, rotateLocal.Y - iconR, rotateLocal.X + iconR, rotateLocal.Y + iconR),
            -55, 260, false, iconPaint);
        canvas.DrawLine(
            resizeLocal.X - iconR * .75f,
            resizeLocal.Y + iconR * .6f,
            resizeLocal.X + iconR * .7f,
            resizeLocal.Y - iconR * .85f,
            iconPaint);

        _rotateHandle = LocalToWorld(rotateLocal);
        _resizeHandle = LocalToWorld(resizeLocal);
    }

    private void OnTouch(object? sender, SKTouchEventArgs e)
    {
        var p = e.Location;
        switch (e.ActionType)
        {
            case SKTouchAction.Pressed:
                _touches[e.Id] = p;
                _previousTouches[e.Id] = p;

                if (_touches.Count >= 2)
                {
                    _gesture = GestureMode.Multi;
                    Selected = true;
                }
                else if (Selected && _hasGeometry && Distance(p, _rotateHandle) <= 46f)
                {
                    _gesture = GestureMode.Rotate;
                }
                else if (Selected && _hasGeometry && Distance(p, _resizeHandle) <= 46f)
                {
                    _gesture = GestureMode.Resize;
                }
                else if (_hasGeometry && HitTextBox(p))
                {
                    _gesture = GestureMode.Drag;
                    Selected = true;
                }
                else
                {
                    _gesture = GestureMode.None;
                    Selected = false;
                }
                InvalidateSurface();
                break;

            case SKTouchAction.Moved:
                if (!_touches.ContainsKey(e.Id)) break;
                _touches[e.Id] = p;

                if (_gesture == GestureMode.Multi && _touches.Count >= 2)
                {
                    var ids = _touches.Keys.Take(2).ToArray();
                    if (!_previousTouches.TryGetValue(ids[0], out var a0) || !_previousTouches.TryGetValue(ids[1], out var b0))
                        break;
                    var a1 = _touches[ids[0]];
                    var b1 = _touches[ids[1]];
                    var oldMid = Mid(a0, b0);
                    var newMid = Mid(a1, b1);
                    var oldVec = new SKPoint(b0.X - a0.X, b0.Y - a0.Y);
                    var newVec = new SKPoint(b1.X - a1.X, b1.Y - a1.Y);

                    var ratio = Math.Clamp(Math.Max(1f, Length(newVec)) / Math.Max(1f, Length(oldVec)), .72f, 1.38f);
                    Model.Scale = Math.Clamp(Model.Scale * ratio, .12f, 4f);
                    Model.RotationDegrees = Normalize(Model.RotationDegrees + Angle(newVec) - Angle(oldVec));
                    MoveCenterBy(newMid.X - oldMid.X, newMid.Y - oldMid.Y);
                    ConstrainCenterToHoop(updateModel: true);

                    _previousTouches[ids[0]] = a1;
                    _previousTouches[ids[1]] = b1;
                    RaiseChanged();
                }
                else
                {
                    var prev = _previousTouches[e.Id];
                    if (_gesture == GestureMode.Drag)
                    {
                        MoveCenterBy(p.X - prev.X, p.Y - prev.Y);
                        ConstrainCenterToHoop(updateModel: true);
                        RaiseChanged();
                    }
                    else if (_gesture == GestureMode.Rotate)
                    {
                        // A alça parte de baixo do objeto (vetor de +90° na tela). Para que
                        // essa posição represente rotação 0°, o offset correto é -90°.
                        // O +90° anterior causava um salto de quase 180° ao iniciar o gesto.
                        Model.RotationDegrees = Normalize(
                            Angle(new SKPoint(p.X - _screenCenter.X, p.Y - _screenCenter.Y)) - 90f);
                        ConstrainCenterToHoop(updateModel: true);
                        RaiseChanged();
                    }
                    else if (_gesture == GestureMode.Resize)
                    {
                        var oldDistance = Math.Max(1f, Distance(prev, _screenCenter));
                        var newDistance = Math.Max(1f, Distance(p, _screenCenter));
                        var ratio = Math.Clamp(newDistance / oldDistance, .78f, 1.28f);
                        Model.Scale = Math.Clamp(Model.Scale * ratio, .12f, 4f);
                        RaiseChanged();
                    }
                    _previousTouches[e.Id] = p;
                }
                InvalidateSurface();
                break;

            case SKTouchAction.Released:
            case SKTouchAction.Cancelled:
                _touches.Remove(e.Id);
                _previousTouches.Remove(e.Id);
                _gesture = _touches.Count >= 2 ? GestureMode.Multi : GestureMode.None;
                InvalidateSurface();
                break;
        }
        e.Handled = true;
    }

    private bool HitTextBox(SKPoint world)
    {
        var local = WorldToLocal(world);
        var hit = _selectionLocal;
        hit.Inflate(16f, 16f);
        return hit.Contains(local.X, local.Y);
    }

    private void MoveCenterBy(float dx, float dy)
    {
        if (_hoopRect.Width <= 1 || _hoopRect.Height <= 1) return;
        _screenCenter = new SKPoint(_screenCenter.X + dx, _screenCenter.Y + dy);
        Model.CenterX = Math.Clamp((_screenCenter.X - _hoopRect.Left) / _hoopRect.Width, 0f, 1f);
        Model.CenterY = Math.Clamp((_screenCenter.Y - _hoopRect.Top) / _hoopRect.Height, 0f, 1f);
    }

    private void ConstrainCenterToHoop(bool updateModel)
    {
        if (_hoopRect.Width <= 1 || _selectionLocal.Width <= 1) return;

        var corners = new[]
        {
            LocalToWorld(new SKPoint(_selectionLocal.Left, _selectionLocal.Top)),
            LocalToWorld(new SKPoint(_selectionLocal.Right, _selectionLocal.Top)),
            LocalToWorld(new SKPoint(_selectionLocal.Right, _selectionLocal.Bottom)),
            LocalToWorld(new SKPoint(_selectionLocal.Left, _selectionLocal.Bottom))
        };
        var minX = corners.Min(c => c.X);
        var maxX = corners.Max(c => c.X);
        var minY = corners.Min(c => c.Y);
        var maxY = corners.Max(c => c.Y);
        var innerPad = Math.Max(8f, _hoopRect.Width * .015f);
        var left = _hoopRect.Left + innerPad;
        var right = _hoopRect.Right - innerPad;
        var top = _hoopRect.Top + innerPad;
        var bottom = _hoopRect.Bottom - innerPad;

        var dx = 0f;
        var dy = 0f;
        var boxWidth = maxX - minX;
        var boxHeight = maxY - minY;
        if (boxWidth > right - left)
            dx = _hoopRect.MidX - (minX + maxX) * .5f;
        else if (minX < left)
            dx = left - minX;
        else if (maxX > right)
            dx = right - maxX;

        if (boxHeight > bottom - top)
            dy = _hoopRect.MidY - (minY + maxY) * .5f;
        else if (minY < top)
            dy = top - minY;
        else if (maxY > bottom)
            dy = bottom - maxY;

        if (MathF.Abs(dx) > .01f || MathF.Abs(dy) > .01f)
            _screenCenter = new SKPoint(_screenCenter.X + dx, _screenCenter.Y + dy);

        if (updateModel)
        {
            Model.CenterX = Math.Clamp((_screenCenter.X - _hoopRect.Left) / _hoopRect.Width, 0f, 1f);
            Model.CenterY = Math.Clamp((_screenCenter.Y - _hoopRect.Top) / _hoopRect.Height, 0f, 1f);
        }
    }

    private SKPoint LocalToWorld(SKPoint local)
    {
        var r = Model.RotationDegrees * MathF.PI / 180f;
        var c = MathF.Cos(r);
        var s = MathF.Sin(r);
        return new SKPoint(
            _screenCenter.X + local.X * c - local.Y * s,
            _screenCenter.Y + local.X * s + local.Y * c);
    }

    private SKPoint WorldToLocal(SKPoint world)
    {
        var dx = world.X - _screenCenter.X;
        var dy = world.Y - _screenCenter.Y;
        var r = -Model.RotationDegrees * MathF.PI / 180f;
        var c = MathF.Cos(r);
        var s = MathF.Sin(r);
        return new SKPoint(dx * c - dy * s, dx * s + dy * c);
    }

    private void RaiseChanged() => ModelChanged?.Invoke(this, EventArgs.Empty);
    private static float Distance(SKPoint a, SKPoint b) => MathF.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Y - b.Y) * (a.Y - b.Y));
    private static float Length(SKPoint a) => MathF.Sqrt(a.X * a.X + a.Y * a.Y);
    private static SKPoint Mid(SKPoint a, SKPoint b) => new((a.X + b.X) * .5f, (a.Y + b.Y) * .5f);
    private static float Angle(SKPoint v) => MathF.Atan2(v.Y, v.X) * 180f / MathF.PI;
    private static float Normalize(float d)
    {
        while (d > 180) d -= 360;
        while (d < -180) d += 360;
        return d;
    }
}
