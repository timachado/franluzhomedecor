using BordattoStudio.Core;
using SkiaSharp;
using SkiaSharp.Views.Maui;
using SkiaSharp.Views.Maui.Controls;

namespace BordattoStudio.Views;

public sealed class InteractiveDesignCanvas : SKCanvasView
{
    private enum GestureMode { None, Drag, Rotate, Resize, Multi }
    private readonly Dictionary<long, SKPoint> _touches = [];
    private readonly Dictionary<long, SKPoint> _previous = [];
    private GestureMode _gesture;
    private SKPoint _center;
    private SKPoint _rotateHandle;
    private SKPoint _resizeHandle;
    private SKRect _worldBox;
    private float _w;
    private float _h;

    public EmbroideryDesign Design { get; set; } = new();
    public float DesignScale { get; set; } = 1f;
    public float RotationDegrees { get; set; }
    public float CenterX { get; set; } = .5f;
    public float CenterY { get; set; } = .5f;
    public bool Selected { get; set; } = true;
    public event EventHandler? TransformChanged;

    public InteractiveDesignCanvas()
    {
        EnableTouchEvents = true;
        Touch += OnTouch;
        PaintSurface += Paint;
        BackgroundColor = BordattoColors.Canvas;
    }

    private void Paint(object? sender, SKPaintSurfaceEventArgs e)
    {
        var c = e.Surface.Canvas; var w = e.Info.Width; var h = e.Info.Height; _w = w; _h = h;
        c.Clear(new SKColor(0xF3, 0xEC, 0xDD));
        using var gridPaint = new SKPaint { Color = new SKColor(0x70,0x68,0x59,0x18), StrokeWidth = 1 };
        var step = Math.Max(28f, w / 12f);
        for (var x=0f;x<=w;x+=step) c.DrawLine(x,0,x,h,gridPaint);
        for (var y=0f;y<=h;y+=step) c.DrawLine(0,y,w,y,gridPaint);
        var pad = Math.Max(30f,w*.04f);
        var hoop = new SKRect(pad,pad,w-pad,h-pad);
        using var hoopPaint = new SKPaint { Color = new SKColor(0x35,0x37,0x4B), Style=SKPaintStyle.Stroke, StrokeWidth=3, PathEffect=SKPathEffect.CreateDash([12,8],0), IsAntialias=true };
        c.DrawRoundRect(hoop,24,24,hoopPaint);
        using var capFont = new SKFont(SKTypeface.Default, Math.Max(15,w*.022f));
        using var capPaint = new SKPaint { Color=new SKColor(0x72,0x6C,0x62), IsAntialias=true };
        c.DrawText("Bastidor 100 × 100 mm",w/2f,hoop.Top+24,SKTextAlign.Center,capFont,capPaint);

        var pts = Design.Stitches.Where(p=>p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        if (pts.Count < 2) return;
        var minX=pts.Min(p=>p.X); var maxX=pts.Max(p=>p.X); var minY=pts.Min(p=>p.Y); var maxY=pts.Max(p=>p.Y);
        var dw=Math.Max(.1f,maxX-minX); var dh=Math.Max(.1f,maxY-minY);
        var fit=Math.Min((hoop.Width*.86f)/dw,(hoop.Height*.72f)/dh) * DesignScale;
        _center=new SKPoint(hoop.Left+CenterX*hoop.Width,hoop.Top+CenterY*hoop.Height);
        var localW=dw*fit; var localH=dh*fit;
        var left=-localW/2f; var top=-localH/2f;
        var lineColor=EmbroideryEngine.ToSkColor(Design.ThreadColor);
        using var stitchPaint = new SKPaint { Color=lineColor, StrokeWidth=Math.Max(1.3f,w*.0025f), Style=SKPaintStyle.Stroke, IsAntialias=true, StrokeCap=SKStrokeCap.Round };
        c.Save(); c.Translate(_center.X,_center.Y); c.RotateDegrees(RotationDegrees);
        StitchPoint? previous=null;
        foreach(var p in Design.Stitches)
        {
            if(p.Command==StitchCommand.Stitch && previous is { } prev && prev.Command==StitchCommand.Stitch)
            {
                var a=new SKPoint(left+(prev.X-minX)*fit, top+(prev.Y-minY)*fit);
                var b=new SKPoint(left+(p.X-minX)*fit, top+(p.Y-minY)*fit);
                c.DrawLine(a,b,stitchPaint);
            }
            previous=p.Command is StitchCommand.Jump or StitchCommand.Trim or StitchCommand.ColorChange or StitchCommand.End ? null : p;
        }

        var box=new SKRect(left-12,top-12,left+localW+12,top+localH+12);
        if(Selected)
        {
            using var sel=new SKPaint { Color=new SKColor(0xE7,0xBB,0x68),StrokeWidth=3,Style=SKPaintStyle.Stroke,IsAntialias=true };
            c.DrawRoundRect(box,10,10,sel);
            var rotLocal=new SKPoint(box.MidX,box.Bottom+60);
            var resizeLocal=new SKPoint(box.Right,box.Bottom);
            c.DrawLine(box.MidX,box.Bottom,rotLocal.X,rotLocal.Y-21,sel);
            using var fill=new SKPaint { Color=new SKColor(0x1C,0x1A,0x25),Style=SKPaintStyle.Fill,IsAntialias=true };
            c.DrawCircle(rotLocal,23,fill); c.DrawCircle(resizeLocal,23,fill);
            using var white=new SKPaint { Color=SKColors.White,StrokeWidth=3,Style=SKPaintStyle.Stroke,IsAntialias=true,StrokeCap=SKStrokeCap.Round };
            c.DrawArc(new SKRect(rotLocal.X-10,rotLocal.Y-10,rotLocal.X+10,rotLocal.Y+10),-55,260,false,white);
            c.DrawLine(resizeLocal.X-9,resizeLocal.Y+7,resizeLocal.X+8,resizeLocal.Y-10,white);
            _rotateHandle=Transform(rotLocal,RotationDegrees,_center);
            _resizeHandle=Transform(resizeLocal,RotationDegrees,_center);
        }
        c.Restore();
        _worldBox=WorldBounds(box,RotationDegrees,_center);
    }

    private void OnTouch(object? sender, SKTouchEventArgs e)
    {
        var p=e.Location;
        switch(e.ActionType)
        {
            case SKTouchAction.Pressed:
                _touches[e.Id]=p; _previous[e.Id]=p;
                if(_touches.Count>=2){_gesture=GestureMode.Multi;Selected=true;}
                else if(Distance(p,_rotateHandle)<=38){_gesture=GestureMode.Rotate;Selected=true;}
                else if(Distance(p,_resizeHandle)<=38){_gesture=GestureMode.Resize;Selected=true;}
                else if(_worldBox.Contains(p.X,p.Y)){_gesture=GestureMode.Drag;Selected=true;}
                else{_gesture=GestureMode.None;Selected=false;}
                InvalidateSurface(); break;
            case SKTouchAction.Moved:
                if(!_touches.ContainsKey(e.Id)) break;
                _touches[e.Id]=p;
                if(_gesture==GestureMode.Multi && _touches.Count>=2)
                {
                    var ids=_touches.Keys.Take(2).ToArray(); var a0=_previous[ids[0]]; var b0=_previous[ids[1]]; var a1=_touches[ids[0]]; var b1=_touches[ids[1]];
                    var oldMid=Mid(a0,b0); var newMid=Mid(a1,b1); var ov=new SKPoint(b0.X-a0.X,b0.Y-a0.Y); var nv=new SKPoint(b1.X-a1.X,b1.Y-a1.Y);
                    DesignScale=Math.Clamp(DesignScale*Math.Max(1f,Length(nv))/Math.Max(1f,Length(ov)),.25f,4f);
                    RotationDegrees=Normalize(RotationDegrees+Angle(nv)-Angle(ov)); Move(newMid.X-oldMid.X,newMid.Y-oldMid.Y);
                    _previous[ids[0]]=a1; _previous[ids[1]]=b1; Changed();
                }
                else
                {
                    var prev=_previous[e.Id];
                    if(_gesture==GestureMode.Drag){Move(p.X-prev.X,p.Y-prev.Y);Changed();}
                    else if(_gesture==GestureMode.Rotate){RotationDegrees=Normalize(Angle(new SKPoint(p.X-_center.X,p.Y-_center.Y))+90f);Changed();}
                    else if(_gesture==GestureMode.Resize){DesignScale=Math.Clamp(DesignScale*Math.Max(1f,Distance(p,_center))/Math.Max(1f,Distance(prev,_center)),.25f,4f);Changed();}
                    _previous[e.Id]=p;
                }
                InvalidateSurface(); break;
            case SKTouchAction.Released:
            case SKTouchAction.Cancelled:
                _touches.Remove(e.Id); _previous.Remove(e.Id); _gesture=_touches.Count>=2?GestureMode.Multi:GestureMode.None; InvalidateSurface(); break;
        }
        e.Handled=true;
    }

    private void Move(float dx,float dy){if(_w<=1||_h<=1)return;CenterX=Math.Clamp(CenterX+dx/(_w*.92f),.05f,.95f);CenterY=Math.Clamp(CenterY+dy/(_h*.92f),.05f,.95f);}
    private void Changed()=>TransformChanged?.Invoke(this,EventArgs.Empty);
    private static float Distance(SKPoint a,SKPoint b)=>MathF.Sqrt((a.X-b.X)*(a.X-b.X)+(a.Y-b.Y)*(a.Y-b.Y));
    private static float Length(SKPoint a)=>MathF.Sqrt(a.X*a.X+a.Y*a.Y);
    private static SKPoint Mid(SKPoint a,SKPoint b)=>new((a.X+b.X)*.5f,(a.Y+b.Y)*.5f);
    private static float Angle(SKPoint v)=>MathF.Atan2(v.Y,v.X)*180f/MathF.PI;
    private static float Normalize(float d){while(d>180)d-=360;while(d<-180)d+=360;return d;}
    private static SKPoint Transform(SKPoint local,float deg,SKPoint center){var r=deg*MathF.PI/180f;var c=MathF.Cos(r);var s=MathF.Sin(r);return new(center.X+local.X*c-local.Y*s,center.Y+local.X*s+local.Y*c);}
    private static SKRect WorldBounds(SKRect box,float deg,SKPoint center)
    {
        var pts=new[]{new SKPoint(box.Left,box.Top),new SKPoint(box.Right,box.Top),new SKPoint(box.Right,box.Bottom),new SKPoint(box.Left,box.Bottom)}.Select(p=>Transform(p,deg,center)).ToArray();
        return new SKRect(pts.Min(p=>p.X),pts.Min(p=>p.Y),pts.Max(p=>p.X),pts.Max(p=>p.Y));
    }
}
