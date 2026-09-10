// 1.13.6 — fallback manual de rolagem para Android WebView.
(function(){
  const content=()=>document.querySelector('.content');
  let active=false,startY=0,startX=0,startScroll=0,lastY=0,lastT=0,velocity=0,moved=false,raf=0;

  function clamp(v,min,max){return Math.max(min,Math.min(max,v));}
  function maxScroll(el){return Math.max(0,el.scrollHeight-el.clientHeight);}
  function stopMomentum(){if(raf){cancelAnimationFrame(raf);raf=0;}}

  function onStart(ev){
    const el=content();
    if(!el||!ev.touches||ev.touches.length!==1)return;
    const t=ev.touches[0];
    active=true;moved=false;startY=t.clientY;startX=t.clientX;lastY=t.clientY;lastT=performance.now();startScroll=el.scrollTop;velocity=0;stopMomentum();
  }

  function onMove(ev){
    if(!active||!ev.touches||ev.touches.length!==1)return;
    const el=content();if(!el)return;
    const t=ev.touches[0];
    const dy=startY-t.clientY,dx=t.clientX-startX;
    if(!moved&&Math.abs(dy)<6)return;
    if(Math.abs(dx)>Math.abs(dy)*1.25&&!moved)return;
    moved=true;
    const now=performance.now(),dt=Math.max(8,now-lastT);
    velocity=(lastY-t.clientY)/dt;
    lastY=t.clientY;lastT=now;
    el.scrollTop=clamp(startScroll+dy,0,maxScroll(el));
    if(ev.cancelable)ev.preventDefault();
  }

  function momentum(){
    const el=content();if(!el){raf=0;return;}
    if(Math.abs(velocity)<0.015){raf=0;return;}
    el.scrollTop=clamp(el.scrollTop+velocity*16,0,maxScroll(el));
    velocity*=0.92;
    raf=requestAnimationFrame(momentum);
  }

  function onEnd(){
    if(!active)return;
    active=false;
    if(moved&&Math.abs(velocity)>0.06)raf=requestAnimationFrame(momentum);
  }

  document.addEventListener('touchstart',onStart,{passive:true,capture:true});
  document.addEventListener('touchmove',onMove,{passive:false,capture:true});
  document.addEventListener('touchend',onEnd,{passive:true,capture:true});
  document.addEventListener('touchcancel',onEnd,{passive:true,capture:true});

  // Exposto apenas para diagnóstico interno.
  window.__ebdScrollDiagnostics=function(){
    const el=content();
    return el?{clientHeight:el.clientHeight,scrollHeight:el.scrollHeight,scrollTop:el.scrollTop,maxScroll:maxScroll(el)}:null;
  };
})();
