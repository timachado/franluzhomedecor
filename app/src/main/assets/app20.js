// 1.13.4 — navegação interna determinística + rolagem no painel de conteúdo.
(function(){
  const originalNav1134=window.nav;
  let routeStack1134=[(window.state&&state.route)||'home'];
  let lastHomeBack1134=0;

  function content1134(){return document.querySelector('.content')}
  function scrollTop1134(){
    const c=content1134();
    if(c){c.scrollTop=0;try{c.scrollTo({top:0,left:0,behavior:'auto'})}catch(e){}}
  }
  function closeMenu1134(){const s=document.getElementById('menuSheet');if(s)s.classList.remove('show')}
  function routeParent1134(r){
    const map={
      reader:'bible',favorites:'bible',notes:'bible',highlighted19:'bible',history19:'bible',
      lesson:'ebd',magazine:'ebd',magReader:'magazine',classroom:'ebd',attendance:'ebd',agenda:'ebd',notifications:'home',library:'ebd',ebdCalendar110:'ebd',
      hymn:'harpa',planDetail111:'plans111',plans111:'home',daily111:'home',stats111:'home',settings112:'home',
      harpa:'home',outlines:'home',dictionary:'home',concordance:'search',tools:'home',sync:'home',contentInfo:'home',search:'home',profile:'home'
    };
    return map[r]||'home';
  }
  function syncStack1134(){
    if(!window.state)return;
    const r=state.route||'home';
    if(routeStack1134[routeStack1134.length-1]!==r)routeStack1134.push(r);
    if(routeStack1134.length>40)routeStack1134=routeStack1134.slice(-30);
  }
  function go1134(route,push){
    if(!route)route='home';
    if(push){
      syncStack1134();
      if(routeStack1134[routeStack1134.length-1]!==route)routeStack1134.push(route);
    }
    if(typeof originalNav1134==='function')originalNav1134(route);
    else{
      state.route=route;
      location.hash='#/'+route;
      if(typeof window.render==='function')window.render();
    }
    closeMenu1134();
    requestAnimationFrame(scrollTop1134);
    setTimeout(scrollTop1134,30);
  }

  window.nav=function(route){go1134(route,true)};

  function back1134(){
    if(window.state&&state.focus112){
      state.focus112=false;
      try{applyUi112()}catch(e){}
      if(typeof window.render==='function')window.render();
      return true;
    }
    const sheet=document.getElementById('menuSheet');
    if(sheet&&sheet.classList.contains('show')){closeMenu1134();return true;}
    const current=(window.state&&state.route)||'home';
    if(current!=='home'){
      syncStack1134();
      while(routeStack1134.length&&routeStack1134[routeStack1134.length-1]===current)routeStack1134.pop();
      const target=routeStack1134.length?routeStack1134[routeStack1134.length-1]:routeParent1134(current);
      go1134(target,false);
      return true;
    }
    const now=Date.now();
    if(now-lastHomeBack1134<1800){lastHomeBack1134=0;return false;}
    lastHomeBack1134=now;
    try{toast('Pressione voltar novamente para sair')}catch(e){}
    return true;
  }
  window.__ebdNativeBack112=back1134;

  function bindBackButtons1134(){
    document.querySelectorAll('[data-back]').forEach(el=>{el.onclick=(ev)=>{ev.preventDefault();back1134()}});
  }
  const oldRender1134=window.render;
  window.render=function(){
    oldRender1134();
    bindBackButtons1134();
    requestAnimationFrame(()=>{
      const c=content1134();
      if(c){c.style.overflowY='auto';c.style.touchAction='pan-y'}
    });
  };
  const oldBind1134=window.bind;
  window.bind=function(){oldBind1134();bindBackButtons1134()};

  window.addEventListener('hashchange',()=>{
    if(window.state){state.route=location.hash.replace('#/','')||'home';syncStack1134()}
    setTimeout(scrollTop1134,0);
  });
  window.addEventListener('pageshow',()=>{bindBackButtons1134();setTimeout(scrollTop1134,0)});
  bindBackButtons1134();
})();
