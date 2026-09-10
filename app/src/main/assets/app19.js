// 1.13.3 — restaura os controles do cabeçalho independentemente dos binds legados.
(function(){
  function byId(id){return document.getElementById(id)}
  function openMenu1133(){const s=byId('menuSheet');if(s)s.classList.add('show')}
  function closeMenu1133(){const s=byId('menuSheet');if(s)s.classList.remove('show')}

  function bindHeader1133(){
    const brand=document.querySelector('.brand');
    if(brand)brand.onclick=()=>nav('home');

    const bell=byId('bell');
    if(bell)bell.onclick=()=>nav('notifications');

    const search=byId('globalSearchBtn');
    if(search)search.onclick=()=>nav('search');

    const sun=byId('sun');
    if(sun)sun.onclick=()=>nav('settings112');

    const menu=byId('menu');
    if(menu)menu.onclick=openMenu1133;

    const close=byId('closeMenu');
    if(close)close.onclick=closeMenu1133;

    const sheet=byId('menuSheet');
    if(sheet)sheet.onclick=e=>{if(e.target===sheet)closeMenu1133()};
  }

  const oldBind=window.bind;
  window.bind=function(){
    if(typeof oldBind==='function')oldBind();
    bindHeader1133();
  };

  const oldRender=window.render;
  window.render=function(){
    if(typeof oldRender==='function')oldRender();
    bindHeader1133();
  };

  window.addEventListener('pageshow',bindHeader1133);
  document.addEventListener('DOMContentLoaded',bindHeader1133);
  setTimeout(bindHeader1133,0);
})();
