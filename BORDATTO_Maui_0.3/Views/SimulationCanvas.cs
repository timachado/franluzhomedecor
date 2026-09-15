using BordattoStudio.Core;
using SkiaSharp;
using SkiaSharp.Views.Maui;
using SkiaSharp.Views.Maui.Controls;

namespace BordattoStudio.Views;

public sealed class SimulationCanvas : SKCanvasView
{
    public EmbroideryDesign Design { get; set; } = new();
    public int Current { get; set; }

    public SimulationCanvas()
    {
        PaintSurface += Paint;
        BackgroundColor = BordattoColors.Canvas;
    }

    private void Paint(object? sender, SKPaintSurfaceEventArgs e)
    {
        var c=e.Surface.Canvas; var w=e.Info.Width; var h=e.Info.Height;
        c.Clear(new SKColor(0xF3,0xEC,0xDD));
        using var grid=new SKPaint{Color=new SKColor(0x70,0x68,0x59,0x18),StrokeWidth=1};
        var step=Math.Max(28f,w/12f);
        for(var x=0f;x<=w;x+=step)c.DrawLine(x,0,x,h,grid);
        for(var y=0f;y<=h;y+=step)c.DrawLine(0,y,w,y,grid);
        var pad=Math.Max(18f,w*.025f); var hoop=new SKRect(pad,pad,w-pad,h-pad);
        using var hoopPaint=new SKPaint{Color=new SKColor(0x35,0x37,0x4B),Style=SKPaintStyle.Stroke,StrokeWidth=3,PathEffect=SKPathEffect.CreateDash([12,8],0),IsAntialias=true};
        c.DrawRoundRect(hoop,22,22,hoopPaint);
        var center=new SKPoint(w/2f,h/2f); var r=Math.Min(w,h);
        using var circle=new SKPaint{Color=new SKColor(0x6F,0x66,0x57,0x1A),Style=SKPaintStyle.Stroke,StrokeWidth=1};
        c.DrawCircle(center,r*.18f,circle); c.DrawCircle(center,r*.33f,circle);

        var pts=Design.Stitches.Where(p=>p.Command is StitchCommand.Stitch or StitchCommand.Jump).ToList();
        if(pts.Count<2)return;
        var minX=pts.Min(p=>p.X);var maxX=pts.Max(p=>p.X);var minY=pts.Min(p=>p.Y);var maxY=pts.Max(p=>p.Y);
        var dw=Math.Max(.1f,maxX-minX);var dh=Math.Max(.1f,maxY-minY);
        var fit=Math.Min((hoop.Width*.88f)/dw,(hoop.Height*.70f)/dh);
        var left=w/2f-dw*fit/2f;var top=h/2f-dh*fit/2f;
        SKPoint Map(StitchPoint p)=>new(left+(p.X-minX)*fit,top+(p.Y-minY)*fit);
        var color=EmbroideryEngine.ToSkColor(Design.ThreadColor);

        void DrawSequence(int limit,bool ghost)
        {
            StitchPoint? previous=null;
            var take=Math.Clamp(limit,0,Design.Stitches.Count);
            for(var i=0;i<take;i++)
            {
                var p=Design.Stitches[i];
                if(p.Command==StitchCommand.Stitch && previous is { } prev && prev.Command==StitchCommand.Stitch)
                {
                    var a=Map(prev);var b=Map(p);
                    using var paint=new SKPaint{Color=ghost?color.WithAlpha(34):color,StrokeWidth=ghost?1.4f:2.6f,Style=SKPaintStyle.Stroke,IsAntialias=true,StrokeCap=SKStrokeCap.Round};
                    c.DrawLine(a,b,paint);
                }
                previous=p.Command is StitchCommand.Jump or StitchCommand.Trim or StitchCommand.ColorChange or StitchCommand.End?null:p;
            }
        }

        DrawSequence(Design.Stitches.Count,true);
        DrawSequence(Current,false);

        var lastIndex=Math.Clamp(Current-1,0,Design.Stitches.Count-1);
        StitchPoint? needle=null;
        for(var i=lastIndex;i>=0;i--){if(Design.Stitches[i].Command==StitchCommand.Stitch){needle=Design.Stitches[i];break;}}
        if(needle is { } n && Current>0)
        {
            var p=Map(n);
            using var guides=new SKPaint{Color=new SKColor(0x55,0x4E,0x48,0x3A),StrokeWidth=1};
            c.DrawLine(p.X,hoop.Top,p.X,hoop.Bottom,guides); c.DrawLine(hoop.Left,p.Y,hoop.Right,p.Y,guides);
            using var outer=new SKPaint{Color=SKColors.White,Style=SKPaintStyle.Fill,IsAntialias=true};
            using var inner=new SKPaint{Color=color,Style=SKPaintStyle.Fill,IsAntialias=true};
            c.DrawCircle(p,7,outer);c.DrawCircle(p,5,inner);
        }
    }
}
