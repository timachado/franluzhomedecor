const _renderV112_HOME = window.render;
const _bindV112_HOME = window.bind;

function v113ProfileName(){
  const n=(state.profile&&state.profile.name)||'Cristão';
  return String(n||'Cristão').trim().split(/\s+/).slice(0,2).join(' ');
}
function v113NavKey(){
  const r=state.route;
  if(r==='home'||r==='daily111'||r==='plans111'||r==='planDetail111'||r==='stats111')return 'home';
  if(['bible','reader','favorites','notes','highlighted19','history19'].includes(r))return 'bible';
  if(['ebd','lesson','magazine','magReader','classroom','attendance','agenda','notifications','library'].includes(r))return 'ebd';
  if(['search','concordance','dictionary'].includes(r))return 'search';
  return 'profile';
}
function applyNav113(){
  const key=v113NavKey();
  document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route===key));
}
function quick113(icon,title,sub,route,cls){
  return `<button class="v113-quick ${cls}" data-route="${route}"><span class="v113-quick-icon">${icon}</span><div><strong>${title}</strong><small>${sub}</small></div><b>›</b></button>`;
}
function home113(){
  const name=v113ProfileName();
  const lesson=typeof currentLesson110==='function'?currentLesson110():null;
  const verse=typeof dailyVerse111==='function'?dailyVerse111():null;
  const plan=typeof planData111==='function'?planData111(state.currentPlan111||'john21'):null;
  const planDay=plan&&typeof currentDay111==='function'?currentDay111(plan.id):1;
  const planPct=plan&&typeof planPct111==='function'?planPct111(plan.id):0;
  const hymn=Number(state.hymn||localStorage.getItem('ebd-last-hymn-v191')||1);
  const h=window.harpaCatalogV18?.find?.(x=>x.n===hymn)||window.HARPA_CATALOG_V18?.find?.(x=>x.n===hymn)||{n:hymn,title:'Harpa Cristã'};
  const mag=window.magazineLibrary?.find?.(m=>m.id===state.continueMagazineId)||window.magazineLibrary?.[0];
  const mp=mag&&typeof getMagProgress==='function'?getMagProgress(mag.id):null;
  return `<section class="v113-hero">
    <div class="v113-hero-top"><div><span>BÍBLIA & EBD</span><h1>Olá, ${esc18(name)}!</h1><p>Continue seu estudo de hoje</p></div><button data-route="search" aria-label="Buscar">⌕</button></div>
    <button class="v113-continue" data-route="reader"><span>📖</span><div><small>CONTINUAR LEITURA</small><strong>${esc18(state.book||'João')} ${Number(state.chapter||1)}</strong><em>Abra a Palavra e continue de onde parou</em></div><b>Continuar ›</b></button>
  </section>
  <section class="v113-section"><div class="v113-title"><div><span>ACESSO RÁPIDO</span><h2>Estude em poucos toques</h2></div><small>Essenciais</small></div>
   <div class="v113-grid">
    ${quick113('📖','Bíblia','31 mil+ versículos','bible','purple')}
    ${quick113('🎓','EBD','Lições e revistas','ebd','blue')}
    ${quick113('🎵','Harpa','640 hinos','harpa','red')}
    ${quick113('🗂️','Esboços','Crie seus estudos','outlines','gold')}
    ${quick113('📚','Dicionário','Termos bíblicos','dictionary','green')}
    ${quick113('📝','Notas','Reflexões pessoais','notes','cyan')}
   </div>
  </section>
  ${lesson?`<section class="v113-section"><div class="v113-title"><div><span>ESCOLA BÍBLICA DOMINICAL</span><h2>Lição em destaque</h2></div><button data-route="ebd">Ver todas</button></div>
   <button class="v113-ebd-card" data-lesson110="${lesson.n}"><div class="v113-ebd-badge">🎓</div><div><small>LIÇÃO ${String(lesson.n).padStart(2,'0')} • ${esc18(formatDate110(lesson.date))}</small><strong>${esc18(lesson.title)}</strong><p>${esc18(lesson.ref)} • ${esc18(lesson.focus)}</p><span>${completed110(lesson.n)?'✓ Concluída':'Estudar agora'}</span></div><b>›</b></button>
  </section>`:''}
  <section class="v113-section"><div class="v113-title"><div><span>SUA JORNADA</span><h2>Continue de onde parou</h2></div></div>
   <div class="v113-journey">
    ${plan?`<button data-route="planDetail111"><span>🗓️</span><div><small>PLANO ATUAL</small><strong>${esc18(plan.title)}</strong><p>Dia ${planDay} de ${plan.days}</p><i><u style="width:${planPct}%"></u></i></div><b>${planPct}%</b></button>`:''}
    <button data-route="hymn"><span>🎵</span><div><small>ÚLTIMO HINO</small><strong>Harpa ${h.n}</strong><p>${esc18(h.title||'Harpa Cristã')}</p></div><b>›</b></button>
    ${mag?`<button data-home-mag="${mag.id}"><span>📚</span><div><small>REVISTA EBD</small><strong>${esc18(mag.title)}</strong><p>${mp&&mp.opened?`Página ${mp.page+1} • ${mp.pct}%`:`${esc18(mag.quarter)} ${mag.year}`}</p></div><b>›</b></button>`:''}
   </div>
  </section>
  ${verse?`<section class="v113-verse"><div><span>VERSÍCULO DO DIA</span><strong>${esc18(verse.ref)}</strong></div><p>“${esc18(verse.text)}”</p><button id="v113Daily">Ler passagem</button></section>`:''}
  <section class="v113-more"><button data-route="daily111"><span>🔥</span><strong>Minha Rotina</strong><small>Meta diária e sequência</small></button><button data-route="favorites"><span>❤️</span><strong>Favoritos</strong><small>Passagens salvas</small></button><button data-route="library"><span>📚</span><strong>Biblioteca</strong><small>Revistas e progresso</small></button><button data-route="settings112"><span>⚙️</span><strong>Aparência</strong><small>Fonte e leitura</small></button></section>`;
}

function bind113(){
  document.querySelectorAll('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
  document.querySelectorAll('[data-lesson110]').forEach(e=>e.onclick=()=>goLesson110(Number(e.dataset.lesson110)));
  document.querySelectorAll('[data-home-mag]').forEach(e=>e.onclick=()=>{
    state.magazineId=e.dataset.homeMag;
    if(typeof getMagProgress==='function'){
      const p=getMagProgress(state.magazineId);state.magPage=p.opened?p.page:0;
    }
    nav('magazine');
  });
  document.getElementById('v113Daily')?.addEventListener('click',()=>{
    const v=dailyVerse111();if(v?.parsed)openParsedV19(v.parsed);else nav('daily111');
  });
  applyNav113();
}

window.render=function(){
  if(state.route==='home'){
    document.getElementById('app').innerHTML=home113();
    window.bind();applyUi112?.();applyNav113();return;
  }
  _renderV112_HOME();
  applyNav113();
};
window.bind=function(){_bindV112_HOME();bind113()};

window.render();
