const _renderV1132_FIX = window.render;
const _bindV1132_FIX = window.bind;
let _lastHomeBack1132 = 0;

function navKey1132(){
  const r=state.route;
  if(['home','daily111','plans111','planDetail111','stats111'].includes(r))return 'home';
  if(['bible','reader','favorites','notes','highlighted19','history19'].includes(r))return 'bible';
  if(['ebd','lesson','magazine','magReader','classroom','attendance','agenda','library','ebdCalendar110'].includes(r))return 'ebd';
  if(['search','concordance','dictionary'].includes(r))return 'search';
  if(r==='profile')return 'profile';
  return '';
}
function applyNav1132(){
  const key=navKey1132();
  document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',!!key&&b.dataset.route===key));
}
function top1132(){
  try{window.scrollTo({top:0,left:0,behavior:'auto'})}catch(e){window.scrollTo(0,0)}
  document.documentElement.scrollTop=0;document.body.scrollTop=0;
}
function post1132(){
  applyNav1132();
  document.body.classList.toggle('v1132-notifications',state.route==='notifications');
  document.body.classList.toggle('v1132-home',state.route==='home');
}

window.render=function(){_renderV1132_FIX();post1132();};
window.bind=function(){_bindV1132_FIX();post1132();};

// Voltar no Android: evita saída acidental na Home e mantém o Modo Foco consistente.
window.__ebdNativeBack112=function(){
  if(state.focus112){state.focus112=false;applyUi112();window.render();return true;}
  if(state.route!=='home')return false;
  const now=Date.now();
  if(now-_lastHomeBack1132<1800){_lastHomeBack1132=0;return false;}
  _lastHomeBack1132=now;
  toast('Pressione voltar novamente para sair');
  return true;
};

window.addEventListener('hashchange',()=>setTimeout(()=>{post1132();top1132();},0));
window.addEventListener('pageshow',()=>setTimeout(post1132,0));
post1132();
