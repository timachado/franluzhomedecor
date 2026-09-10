// 1.13.11 — rolagem touch controlada com prioridade para overlays/modais.
(function(){
  const content=()=>document.querySelector('.content');
  const openMenu=()=>document.querySelector('.menu-sheet.show');
  let active=false,target=null,startY=0,startX=0,startScroll=0,lastY=0,lastT=0,velocity=0,moved=false,raf=0;

  function clamp(v,min,max){return Math.max(min,Math.min(max,v));}
  function maxScroll(el){return el?Math.max(0,el.scrollHeight-el.clientHeight):0;}
  function stopMomentum(){if(raf){cancelAnimationFrame(raf);raf=0;}}
  function reset(){active=false;target=null;moved=false;velocity=0;}

  function resolveTarget(ev){
    const menu=openMenu();
    if(menu){
      const card=ev.target&&ev.target.closest?ev.target.closest('.menu-card'):null;
      return card||null; // menu aberto: nunca deixa o gesto cair no fundo
    }
    return content();
  }

  function onStart(ev){
    if(!ev.touches||ev.touches.length!==1)return;
    stopMomentum();
    target=resolveTarget(ev);
    if(!target){
      active=false;
      return;
    }
    const t=ev.touches[0];
    active=true;moved=false;startY=t.clientY;startX=t.clientX;lastY=t.clientY;lastT=performance.now();startScroll=target.scrollTop;velocity=0;
  }

  function onMove(ev){
    if(!ev.touches||ev.touches.length!==1)return;

    // Se um overlay estiver aberto e o gesto começou fora do card, bloqueia o fundo.
    if(!active){
      if(openMenu()&&ev.cancelable)ev.preventDefault();
      return;
    }
    if(!target)return;

    const t=ev.touches[0];
    const dy=startY-t.clientY,dx=t.clientX-startX;
    if(!moved&&Math.abs(dy)<6)return;
    if(Math.abs(dx)>Math.abs(dy)*1.25&&!moved)return;
    moved=true;
    const now=performance.now(),dt=Math.max(8,now-lastT);
    velocity=(lastY-t.clientY)/dt;
    lastY=t.clientY;lastT=now;
    target.scrollTop=clamp(startScroll+dy,0,maxScroll(target));
    if(ev.cancelable)ev.preventDefault();
  }

  function momentum(){
    if(!target){raf=0;return;}
    if(Math.abs(velocity)<0.015){raf=0;target=null;return;}
    target.scrollTop=clamp(target.scrollTop+velocity*16,0,maxScroll(target));
    velocity*=0.92;
    raf=requestAnimationFrame(momentum);
  }

  function onEnd(){
    if(!active){reset();return;}
    active=false;
    if(moved&&Math.abs(velocity)>0.06)raf=requestAnimationFrame(momentum);
    else target=null;
  }

  document.addEventListener('touchstart',onStart,{passive:true,capture:true});
  document.addEventListener('touchmove',onMove,{passive:false,capture:true});
  document.addEventListener('touchend',onEnd,{passive:true,capture:true});
  document.addEventListener('touchcancel',()=>{stopMomentum();reset();},{passive:true,capture:true});

  // Impede scroll do painel de fundo sempre que o menu/modal estiver aberto.
  const observer=new MutationObserver(()=>{
    const c=content(),menu=openMenu();
    if(c)c.toggleAttribute('data-scroll-locked',!!menu);
    if(menu){
      const card=menu.querySelector('.menu-card');
      if(card)card.setAttribute('data-overlay-scroll','1');
    }
  });
  document.addEventListener('DOMContentLoaded',()=>{
    const sheet=document.getElementById('menuSheet');
    if(sheet)observer.observe(sheet,{attributes:true,attributeFilter:['class']});
  });

  window.__ebdScrollDiagnostics=function(){
    const el=content(),menu=openMenu(),card=menu&&menu.querySelector('.menu-card');
    return {
      content:el?{clientHeight:el.clientHeight,scrollHeight:el.scrollHeight,scrollTop:el.scrollTop,maxScroll:maxScroll(el)}:null,
      menu:card?{clientHeight:card.clientHeight,scrollHeight:card.scrollHeight,scrollTop:card.scrollTop,maxScroll:maxScroll(card)}:null,
      menuOpen:!!menu
    };
  };
})();
