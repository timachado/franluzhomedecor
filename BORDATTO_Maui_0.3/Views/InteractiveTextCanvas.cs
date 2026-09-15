using BordattoStudio.Core;
using SkiaSharp;
using SkiaSharp.Views.Maui;
using SkiaSharp.Views.Maui.Controls;

namespace BordattoStudio.Views;

public sealed class InteractiveTextCanvas : SKCanvasView
{
    private enum GestureMode { None, Drag, Rotate, Resize, Multi }

    private readonly Dictionary<long, SKPoint> _touches = [];
    private readonly Dictionary<long, SKPoint> _previousTouches = [];
    private GestureMode _gesture;
    private SKPoint _rotateHandle;
    private SKPoint _resizeHandle;
    private SKPoint _screenCenter;
    private float _canvasWidth;
    private float _canvasHeight;

    public TextObjectModel Model { get; set; } = new();
    public bool Selected { get; set; } = true;
    public event EventHandler? ModelChanged;

    public InteractiveTextCanvas()
    {
        EnableTouchEvents = true;
        Touch += OnTouch;
        PaintSurface += OnPaintSurface;
        BackgroundColor = BordattoColors.Canvas;
    }

    private void OnPaintSurface(object? sender, SKPaintSurfaceEventArgs e)
    {
        var canvas = e.Surface.Canvas;
        var w = e.Info.Width;
        var h = e.Info.Height;
        _canvasWidth = w;
        _canvasHeight = h;
        canvas.Clear(new SKColor(0xF3, 0xEC, 0xDD));

        using var gridPaint = new SKPaint { Color = new SKColor(0x70, 0x68, 0x59, 0x18), StrokeWidth = 1, IsAntialias = true };
        var gridStep = Math.Max(28f, w / 12f);
        for (var x = 0f; x <= w; x += gridStep) canvas.DrawLine(x, 0, x, h, gridPaint);
        for (var y = 0f; y <= h; y += gridStep) canvas.DrawLine(0, y, w, y, gridPaint);

        var pad = Math.Max(40f, w * .075f);
        var hoop = new SKRect(pad, pad * .75f, w - pad, h - pad * .75f);
        using var hoopPaint = new SKPaint { Color = new SKColor(0x55, 0x51, 0x49), StrokeWidth = 4, Style = SKPaintStyle.Stroke, IsAntialias = true };
        canvas.DrawRoundRect(hoop, 28, 28, hoopPaint);

        using var captionFont = new SKFont(SKTypeface.Default, Math.Max(16, w * .025f));
        using var captionPaint = new SKPaint { Color = new SKColor(0x76, 0x70, 0x65), IsAntialias = true };
        canvas.DrawText("Bastidor 100 × 100 mm", w / 2f, hoop.Top + 30f, SKTextAlign.Center, captionFont, captionPaint);

        var pxPerMm = hoop.Width / 100f;
        var textSize = Math.Clamp(Model.HeightMm * pxPerMm * Model.Scale, 22f, hoop.Height * .65f);
        var style = Model.Bold && Model.Italic ? SKFontStyle.BoldItalic : Model.Bold ? SKFontStyle.Bold : Model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;
        using var typeface = SKTypeface.FromFamilyName(Model.FontFamily, style) ?? SKTypeface.Default;
        using var textFont = new SKFont(typeface, textSize);
        using var textPaint = new SKPaint { Color = EmbroideryEngine.ToSkColor(Model.Color), IsAntialias = true, Style = SKPaintStyle.Fill };
        textFont.MeasureText(Model.Text, out var bounds, textPaint);
        var margin = 14f;
        _screenCenter = new SKPoint(
            hoop.Left + Math.Clamp(Model.CenterX, 0f, 1f) * hoop.Width,
            hoop.Top + Math.Clamp(Model.CenterY, 0f, 1f) * hoop.Height);

        canvas.Save();
        canvas.Translate(_screenCenter.X, _screenCenter.Y);
        canvas.RotateDegrees(Model.RotationDegrees);
        canvas.DrawText(Model.Text, -bounds.MidX, -bounds.MidY, SKTextAlign.Left, textFont, textPaint);

        if (Selected)
        {
            var box = new SKRect(bounds.Left - bounds.MidX - margin, bounds.Top - bounds.MidY - margin, bounds.Right - bounds.MidX + margin, bounds.Bottom - bounds.MidY + margin);
            using var boxPaint = new SKPaint { Color = new SKColor(0xE5, 0x17, 0x66), StrokeWidth = 3.2f, Style = SKPaintStyle.Stroke, IsAntialias = true };
            canvas.DrawRoundRect(box, 10, 10, boxPaint);
            var rotateLocal = new SKPoint(box.MidX, box.Bottom + 64f);
            var resizeLocal = new SKPoint(box.Right, box.Bottom);
            canvas.DrawLine(box.MidX, box.Bottom, rotateLocal.X, rotateLocal.Y - 20f, boxPaint);
            using var handleFill = new SKPaint { Color = new SKColor(0x1C, 0x1A, 0x25), Style = SKPaintStyle.Fill, IsAntialias = true };
            canvas.DrawCircle(rotateLocal, 23, handleFill);
            canvas.DrawCircle(resizeLocal, 23, handleFill);
            using var iconPaint = new SKPaint { Color = SKColors.White, StrokeWidth = 3, Style = SKPaintStyle.Stroke, IsAntialias = true, StrokeCap = SKStrokeCap.Round };
            canvas.DrawArc(new SKRect(rotateLocal.X - 10, rotateLocal.Y - 10, rotateLocal.X + 10, rotateLocal.Y + 10), -55, 260, false, iconPaint);
            canvas.DrawLine(resizeLocal.X - 9, resizeLocal.Y + 7, resizeLocal.X + 8, resizeLocal.Y - 10, iconPaint);
            canvas.Restore();

            _rotateHandle = TransformLocal(rotateLocal, Model.RotationDegrees, _screenCenter);
            _resizeHandle = TransformLocal(resizeLocal, Model.RotationDegrees, _screenCenter);
        }
        else canvas.Restore();
    }

    private void OnTouch(object? sender, SKTouchEventArgs e)
    {
        var p = e.Location;
        switch (e.ActionType)
        {
            case SKTouchAction.Pressed:
                _touches[e.Id] = p;
                _previousTouches[e.Id] = p;
                if (_touches.Count >= 2) { _gesture = GestureMode.Multi; Selected = true; }
                else if (Distance(p, _rotateHandle) <= 38f) { _gesture = GestureMode.Rotate; Selected = true; }
                else if (Distance(p, _resizeHandle) <= 38f) { _gesture = GestureMode.Resize; Selected = true; }
                else if (HitTextBox(p)) { _gesture = GestureMode.Drag; Selected = true; }
                else { _gesture = GestureMode.None; Selected = false; }
                InvalidateSurface();
                break;

            case SKTouchAction.Moved:
                if (!_touches.ContainsKey(e.Id)) break;
                _touches[e.Id] = p;
                if (_gesture == GestureMode.Multi && _touches.Count >= 2)
                {
                    var ids = _touches.Keys.Take(2).ToArray();
                    var a0 = _previousTouches[ids[0]]; var b0 = _previousTouches[ids[1]];
                    var a1 = _touches[ids[0]]; var b1 = _touches[ids[1]];
                    var oldMid = Mid(a0, b0); var newMid = Mid(a1, b1);
                    var oldVec = new SKPoint(b0.X - a0.X, b0.Y - a0.Y);
                    var newVec = new SKPoint(b1.X - a1.X, b1.Y - a1.Y);
                    Model.Scale = Math.Clamp(Model.Scale * Math.Max(1f, Length(newVec)) / Math.Max(1f, Length(oldVec)), .25f, 4f);
                    Model.RotationDegrees = Normalize(Model.RotationDegrees + Angle(newVec) - Angle(oldVec));
                    MoveCenterBy(newMid.X - oldMid.X, newMid.Y - oldMid.Y);
                    _previousTouches[ids[0]] = a1; _previousTouches[ids[1]] = b1;
                    RaiseChanged();
                }
                else
                {
                    var prev = _previousTouches[e.Id];
                    if (_gesture == GestureMode.Drag)
                    {
                        MoveCenterBy(p.X - prev.X, p.Y - prev.Y);
                        RaiseChanged();
                    }
                    else if (_gesture == GestureMode.Rotate)
                    {
                        Model.RotationDegrees = Normalize(Angle(new SKPoint(p.X - _screenCenter.X, p.Y - _screenCenter.Y)) + 90f);
                        RaiseChanged();
                    }
                    else if (_gesture == GestureMode.Resize)
                    {
                        Model.Scale = Math.Clamp(Model.Scale * Math.Max(1f, Distance(p, _screenCenter)) / Math.Max(1f, Distance(prev, _screenCenter)), .25f, 4f);
                        RaiseChanged();
                    }
                    _previousTouches[e.Id] = p;
                }
                InvalidateSurface();
                break;

            case SKTouchAction.Released:
            case SKTouchAction.Cancelled:
                _touches.Remove(e.Id); _previousTouches.Remove(e.Id);
                _gesture = _touches.Count >= 2 ? GestureMode.Multi : GestureMode.None;
                InvalidateSurface();
                break;
        }
        e.Handled = true;
    }

    private bool HitTextBox(SKPoint world)
    {
        var local = InverseTransform(world, Model.RotationDegrees, _screenCenter);
        var style = Model.Bold && Model.Italic ? SKFontStyle.BoldItalic : Model.Bold ? SKFontStyle.Bold : Model.Italic ? SKFontStyle.Italic : SKFontStyle.Normal;
        using var typeface = SKTypeface.FromFamilyName(Model.FontFamily, style) ?? SKTypeface.Default;
        var pxPerMm = Math.Max(1f, (_canvasWidth - Math.Max(80f, _canvasWidth * .15f)) / 100f);
        using var font = new SKFont(typeface, Math.Clamp(Model.HeightMm * pxPerMm * Model.Scale, 22f, _canvasHeight * .65f));
        using var paint = new SKPaint { IsAntialias = true };
        font.MeasureText(Model.Text, out var bounds, paint);
        var box = new SKRect(bounds.Left - bounds.MidX - 20, bounds.Top - bounds.MidY - 20, bounds.Right - bounds.MidX + 20, bounds.Bottom - bounds.MidY + 20);
        return box.Contains(local.X - _screenCenter.X, local.Y - _screenCenter.Y);
    }

    private void MoveCenterBy(float dx, float dy)
    {
        if (_canvasWidth <= 1 || _canvasHeight <= 1) return;
        Model.CenterX = Math.Clamp(Model.CenterX + dx / (_canvasWidth * .85f), .05f, .95f);
        Model.CenterY = Math.Clamp(Model.CenterY + dy / (_canvasHeight * .85f), .05f, .95f);
    }

    private void RaiseChanged() => ModelChanged?.Invoke(this, EventArgs.Empty);
    private static float Distance(SKPoint a, SKPoint b) => MathF.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Y - b.Y) * (a.Y - b.Y));
    private static float Length(SKPoint a) => MathF.Sqrt(a.X * a.X + a.Y * a.Y);
    private static SKPoint Mid(SKPoint a, SKPoint b) => new((a.X + b.X) * .5f, (a.Y + b.Y) * .5f);
    private static float Angle(SKPoint v) => MathF.Atan2(v.Y, v.X) * 180f / MathF.PI;
    private static float Normalize(float d) { while (d > 180) d -= 360; while (d < -180) d += 360; return d; }
    private static SKPoint TransformLocal(SKPoint local, float degrees, SKPoint center)
    {
        var r = degrees * MathF.PI / 180f; var c = MathF.Cos(r); var s = MathF.Sin(r);
        return new SKPoint(center.X + local.X * c - local.Y * s, center.Y + local.X * s + local.Y * c);
    }
    private static SKPoint InverseTransform(SKPoint world, float degrees, SKPoint center)
    {
        var dx = world.X - center.X; var dy = world.Y - center.Y;
        var r = -degrees * MathF.PI / 180f; var c = MathF.Cos(r); var s = MathF.Sin(r);
        return new SKPoint(center.X + dx * c - dy * s, center.Y + dx * s + dy * c);
    }
}
