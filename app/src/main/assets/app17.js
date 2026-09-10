const _renderV1131_FIX = window.render;
const _bindV1131_FIX = window.bind;

function navKey1131(){
  const r=state.route;
  if(['home','daily111','plans111','planDetail111','stats111'].includes(r))return 'home';
  if(['bible','reader','favorites','notes','highlighted19','history19'].includes(r))return 'bible';
  if(['ebd','lesson','magazine','magReader','classroom','attendance','agenda','notifications','library','ebdCalendar110'].includes(r))return 'ebd';
  if(['search','concordance','dictionary'].includes(r))return 'search';
  if(r==='profile')return 'profile';
  return '';
}
function applyNav1131(){
  const key=navKey1131();
  document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',!!key&&b.dataset.route===key));
}
function forceTop1131(){
  try{window.scrollTo({top:0,left:0,behavior:'auto'})}catch(e){window.scrollTo(0,0)}
  document.documentElement.scrollTop=0;
  document.body.scrollTop=0;
}
function bindProfileRole1131(){
  document.querySelectorAll('[data-profile-role]').forEach(b=>{
    b.onclick=()=>{
      const role=b.dataset.profileRole||'Aluno';
      state.profileV16.role=role;
      document.querySelectorAll('[data-profile-role]').forEach(x=>x.classList.toggle('active',x===b));
      const hero=document.querySelector('.profile-hero-v16 span');if(hero)hero.textContent=role;
      try{haptic112?.()}catch(e){}
    };
  });
}
function fixRouteTargets1131(){
  document.querySelectorAll('.bottomnav [data-route],.v113-quick[data-route],.v113-more [data-route],.v113-continue[data-route]').forEach(el=>{
    el.setAttribute('role','button');
    el.style.webkitTapHighlightColor='transparent';
  });
}
function postFix1131(){
  applyNav1131();
  bindProfileRole1131();
  fixRouteTargets1131();
  document.body.classList.toggle('v1131-reader',state.route==='reader');
}

window.render=function(){
  _renderV1131_FIX();
  postFix1131();
};
window.bind=function(){
  _bindV1131_FIX();
  postFix1131();
};

// Garante que trocas de rota nunca herdem uma posição de rolagem estranha.
const _nav1131Original=window.nav;
window.nav=function(route){
  _nav1131Original(route);
  forceTop1131();
  requestAnimationFrame(forceTop1131);
  setTimeout(forceTop1131,40);
};
window.addEventListener('hashchange',()=>setTimeout(()=>{applyNav1131();forceTop1131()},0));
window.addEventListener('pageshow',()=>setTimeout(postFix1131,0));
postFix1131();
