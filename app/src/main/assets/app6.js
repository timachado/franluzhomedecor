const _renderV14=window.render;
const _bindV14=window.bind;
const _ebdContentV14=window.ebdContent;

state.magProgress=JSON.parse(localStorage.getItem('ebd-mag-progress-v15')||'{}');
state.userMode=localStorage.getItem('ebd-user-mode-v15')||'Aluno';
state.magView=state.magView||'all';
state.continueMagazineId=localStorage.getItem('ebd-continue-mag-v15')||magazineLibrary[0].id;

const extraMagazines=[
{id:'adultos-q2-2026',cat:'adultos',catLabel:'Adultos',cover:'bluecover',symbol:'⛵',series:'Bíblia EBD • 2º trimestre 2026',title:'Caminhando com Propósito',subtitle:'Discípulos em missão',audience:'Adultos',edition:'Aluno',desc:'Uma jornada trimestral sobre discipulado, serviço cristão e missão no cotidiano.',year:2026,quarter:'2º trimestre',isNew:false,author:'Equipe Bíblia EBD'},
{id:'professor-q2-2026',cat:'professor',catLabel:'Professor',cover:'bluecover',symbol:'🧭',series:'Bíblia EBD • 2º trimestre 2026',title:'Caminhando com Propósito',subtitle:'Manual do Professor',audience:'Adultos',edition:'Professor',desc:'Guia do professor para o segundo trimestre, com roteiro, objetivos e perguntas.',year:2026,quarter:'2º trimestre',isNew:false,author:'Equipe Bíblia EBD'},
{id:'jovens-q2-2026',cat:'jovens',catLabel:'Jovens',cover:'purplecover',symbol:'🚀',series:'Bíblia EBD • 2º trimestre 2026',title:'Chamados para Influenciar',subtitle:'Fé, cultura e testemunho',audience:'Jovens',edition:'Aluno',desc:'Estudos para jovens sobre identidade cristã, escolhas e influência saudável.',year:2026,quarter:'2º trimestre',isNew:false,author:'Equipe Bíblia EBD'},
{id:'adultos-q1-2026',cat:'adultos',catLabel:'Adultos',cover:'greencover',symbol:'🌿',series:'Bíblia EBD • 1º trimestre 2026',title:'Raízes da Fé',subtitle:'Fundamentos para uma vida firme',audience:'Adultos',edition:'Aluno',desc:'Lições sobre fundamentos da fé, oração, comunhão e perseverança.',year:2026,quarter:'1º trimestre',isNew:false,author:'Equipe Bíblia EBD'},
{id:'professor-q1-2026',cat:'professor',catLabel:'Professor',cover:'goldcover',symbol:'📚',series:'Bíblia EBD • 1º trimestre 2026',title:'Raízes da Fé',subtitle:'Manual do Professor',audience:'Adultos',edition:'Professor',desc:'Material de apoio ao professor para conduzir as lições de fundamentos da fé.',year:2026,quarter:'1º trimestre',isNew:false,author:'Equipe Bíblia EBD'},
{id:'infantil-q2-2026',cat:'infantil',catLabel:'Infantil',cover:'redcover',symbol:'🌈',series:'Bíblia EBD • 2º trimestre 2026',title:'Amigos de Jesus',subtitle:'Aprendendo a amar e servir',audience:'Infantil',edition:'Aluno',desc:'Histórias e atividades para crianças aprenderem sobre amor, serviço e amizade com Jesus.',year:2026,quarter:'2º trimestre',isNew:false,author:'Equipe Bíblia EBD'}
];
extraMagazines.forEach(m=>{if(!magazineLibrary.some(x=>x.id===m.id))magazineLibrary.push(m)});

function saveV15(){
  localStorage.setItem('ebd-mag-progress-v15',JSON.stringify(state.magProgress));
  localStorage.setItem('ebd-user-mode-v15',state.userMode);
  localStorage.setItem('ebd-continue-mag-v15',state.continueMagazineId||'');
}
function magazineTotalPages(m){return getMagazinePages(m).length}
function getMagProgress(id){
  const m=magazineLibrary.find(x=>x.id===id)||magazineLibrary[0];
  const total=magazineTotalPages(m);
  const data=state.magProgress[id]||{page:0,opened:false};
  const page=Math.max(0,Math.min(Number(data.page||0),total-1));
  const pct=data.opened?Math.round(((page+1)/total)*100):0;
  return {page,pct,total,opened:!!data.opened};
}
function setMagProgress(id,page){
  state.magProgress[id]={page:Number(page||0),opened:true,updatedAt:Date.now()};
  state.continueMagazineId=id;
  saveV15();
}
function myMagazineIds(){
  return new Set([...state.magFavs,...state.magDownloads,...Object.keys(state.magProgress).filter(id=>state.magProgress[id]?.opened)]);
}
function filterV15(){
  const q=(state.magQuery||'').trim().toLowerCase();
  const mine=myMagazineIds();
  return magazineLibrary.filter(m=>{
    const catOk=state.magFilter==='all'||m.cat===state.magFilter;
    const qOk=!q||`${m.title} ${m.subtitle} ${m.audience} ${m.edition} ${m.year} ${m.quarter}`.toLowerCase().includes(q);
    const viewOk=state.magView==='all'||(state.magView==='favorites'&&isMagFav(m.id))||(state.magView==='offline'&&isMagDownloaded(m.id))||(state.magView==='mine'&&mine.has(m.id));
    const modeOk=state.userMode==='Professor'?true:m.edition!=='Professor';
    return catOk&&qOk&&viewOk&&modeOk;
  }).sort((a,b)=>(b.year-a.year)||((parseInt(b.quarter)||0)-(parseInt(a.quarter)||0))||Number(b.isNew)-Number(a.isNew));
}
function magGridV15(){
  const list=filterV15();
  if(!list.length)return `<div class="mag-empty"><div style="font-size:30px;margin-bottom:8px">📚</div>Nenhuma revista encontrada nesta seleção.</div>`;
  return `<div class="mag-grid mag-grid-v14">${list.map(m=>{const p=getMagProgress(m.id);return `<article class="mag-card mag-card-v14" data-magazine-card="${m.id}"><div class="mag-card-cover-wrap">${magazineCoverV14(m)}<button class="mag-heart ${isMagFav(m.id)?'active':''}" data-magfav-card="${m.id}">${isMagFav(m.id)?'❤️':'🤍'}</button>${isMagDownloaded(m.id)?'<span class="mag-offline-badge">⬇ offline</span>':''}${p.opened?`<span class="mag-progress-badge">${p.pct}%</span>`:''}</div><div class="mag-card-meta"><strong>${m.title}</strong><small>${m.quarter} ${m.year}</small><span class="mag-category">${m.catLabel} • ${m.edition}</span>${p.opened?`<div class="mag-mini-progress"><span style="width:${p.pct}%"></span></div>`:''}</div></article>`}).join('')}</div>`;
}

window.ebdContent=function(){
  if(state.ebdTab!=='revistas')return _ebdContentV14();
  return `<section class="mag-library-head mag-library-v14"><div class="mag-library-title"><span class="tiny-label">BIBLIOTECA EBD</span><h2>Revistas de Estudo</h2><p>Revistas trimestrais, progresso de leitura e biblioteca pessoal.</p></div><div class="mode-switch"><span>Visualização</span><div><button class="${state.userMode==='Aluno'?'active':''}" data-usermode="Aluno">👤 Aluno</button><button class="${state.userMode==='Professor'?'active':''}" data-usermode="Professor">🧑‍🏫 Professor</button></div></div><div class="mag-search"><input class="field" id="magSearch" value="${state.magQuery||''}" placeholder="Pesquisar por título, classe, trimestre ou ano..."></div><div class="mag-view-tabs mag-view-v15"><button class="${state.magView==='all'?'active':''}" data-magview="all">Todas</button><button class="${state.magView==='mine'?'active':''}" data-magview="mine">📚 Minhas Revistas</button><button class="${state.magView==='favorites'?'active':''}" data-magview="favorites">❤️ Favoritas</button><button class="${state.magView==='offline'?'active':''}" data-magview="offline">⬇ Offline</button></div><div class="mag-filters">${[['all','Todas'],['adultos','Adultos'],['jovens','Jovens'],['adolescentes','Adolescentes'],['professor','Professor'],['infantil','Infantil']].map(([k,l])=>`<button class="mag-filter ${state.magFilter===k?'active':''}" data-magfilter="${k}">${l}</button>`).join('')}</div><div id="magGrid">${magGridV15()}</div></section>`;
};

function homeV15(){
  const featured=magazineLibrary.find(m=>m.isNew&&m.edition===(state.userMode==='Professor'?'Professor':'Aluno'))||magazineLibrary[0];
  const c=magazineLibrary.find(m=>m.id===state.continueMagazineId)||featured;
  const cp=getMagProgress(c.id);
  const base=home();
  const block=`<section class="section home-mag-section"><div class="section-title"><div><h2>Edição em destaque</h2><small>${state.userMode} • ${featured.quarter} ${featured.year}</small></div><button class="home-mode-chip" id="homeModeToggle">${state.userMode==='Professor'?'🧑‍🏫 Professor':'👤 Aluno'}</button></div><article class="featured-mag" data-home-mag="${featured.id}"><div class="featured-mag-cover">${magazineCoverV14(featured)}</div><div class="featured-mag-info"><span class="featured-new">NOVA EDIÇÃO</span><h3>${featured.title}</h3><p>${featured.subtitle}</p><button class="btn btn-primary">Abrir revista</button></div></article>${cp.opened?`<article class="continue-mag" data-home-mag="${c.id}"><div><span class="tiny-label">CONTINUAR REVISTA</span><strong>${c.title}</strong><small>Página ${cp.page+1} de ${cp.total}</small><div class="continue-progress"><span style="width:${cp.pct}%"></span></div></div><b>${cp.pct}%</b></article>`:''}</section>`;
  return base.replace('<section class="section"><div class="section-title"><div><h2>Ferramentas principais</h2>',block+'<section class="section"><div class="section-title"><div><h2>Ferramentas principais</h2>');
}

function magazineDetailV15(){
  const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0];
  const p=getMagProgress(m.id),fav=isMagFav(m.id),off=isMagDownloaded(m.id);
  return `<div class="pagehead"><button class="back" data-route="ebd">‹</button><div><h1>${m.edition==='Professor'?'Revista do Professor':'Revista de Estudo'}</h1><p>${m.audience} • ${m.quarter} ${m.year}</p></div></div><div class="mag-detail-hero"><div class="mag-detail-cover-v14">${magazineCoverV14(m)}</div><div class="mag-detail-shine"></div></div><section class="mag-info-panel mag-info-v14"><div class="mag-detail-tags"><span>${m.catLabel}</span><span>${m.edition}</span>${m.isNew?'<span class="new">Nova edição</span>':''}${off?'<span class="offline">Disponível offline</span>':''}</div><h2>${m.title}</h2><p class="mag-subtitle">${m.subtitle}</p><p>${m.desc}</p><div class="mag-meta-grid"><div><small>Trimestre</small><strong>${m.quarter}</strong></div><div><small>Ano</small><strong>${m.year}</strong></div><div><small>Classe</small><strong>${m.audience}</strong></div><div><small>Edição</small><strong>${m.edition}</strong></div></div>${p.opened?`<div class="detail-progress"><div><strong>Seu progresso</strong><span>${p.pct}%</span></div><div class="continue-progress"><span style="width:${p.pct}%"></span></div><small>Página ${p.page+1} de ${p.total}</small></div>`:''}<div class="mag-actions mag-actions-v14"><button class="btn btn-primary" id="readMagazine">${p.opened?'▶ Continuar lendo':'📖 Ler revista'}</button><button class="btn btn-dark" id="downloadMagazine">${off?'✓ Offline':'⬇ Baixar'}</button></div><button class="mag-wide-action ${fav?'active':''}" id="favoriteMagazine">${fav?'❤️ Revista favoritada':'🤍 Adicionar às Minhas Revistas'}</button></section><div class="subhead">Conteúdo desta edição</div><div class="list-card"><strong>📖 6 páginas demonstrativas</strong><p>Apresentação, Texto Áureo, objetivos, desenvolvimento e perguntas para a classe.</p></div>`;
}

function magazineReaderV15(){
  const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0];
  const pages=getMagazinePages(m),pinfo=getMagProgress(m.id);state.magPage=Math.max(0,Math.min(state.magPage,pages.length-1));const p=pages[state.magPage];
  return `<div class="mag-reader-top"><button class="back" data-route="magazine">‹</button><div><strong>${m.title}</strong><small>${state.magPage+1} de ${pages.length} • ${Math.round(((state.magPage+1)/pages.length)*100)}%</small></div><button class="mag-reader-menu" id="readerBookmark">${isMagFav(m.id)?'❤️':'🤍'}</button></div><div class="mag-page-progress"><span style="width:${((state.magPage+1)/pages.length)*100}%"></span></div><article class="magazine-page ${p.type==='cover'?'cover-page':''}">${p.html}</article><div class="mag-reader-controls"><button id="prevMagPage" ${state.magPage===0?'disabled':''}>‹ Anterior</button><span>Página ${state.magPage+1}</span><button id="nextMagPage" ${state.magPage===pages.length-1?'disabled':''}>Próxima ›</button></div>`;
}

window.render=function(){
  if(state.route==='home'){$('#app').innerHTML=homeV15();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='home'));window.bind();return}
  if(state.route==='magazine'){$('#app').innerHTML=magazineDetailV15();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='magReader'){$('#app').innerHTML=magazineReaderV15();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  _renderV14();
};

window.bind=function(){
  _bindV14();
  const ms=$('#magSearch');if(ms)ms.oninput=()=>{state.magQuery=ms.value;const g=$('#magGrid');if(g)g.innerHTML=magGridV15();bindV15Cards()};
  $$('[data-usermode]').forEach(b=>b.onclick=()=>{state.userMode=b.dataset.usermode;saveV15();window.render()});
  $$('[data-magview]').forEach(b=>b.onclick=()=>{state.magView=b.dataset.magview;window.render()});
  $$('[data-magfilter]').forEach(b=>b.onclick=()=>{state.magFilter=b.dataset.magfilter;window.render()});
  bindV15Cards();
  $$('[data-home-mag]').forEach(el=>el.onclick=()=>{state.magazineId=el.dataset.homeMag;const p=getMagProgress(state.magazineId);state.magPage=p.opened?p.page:0;nav(p.opened?'magReader':'magazine')});
  const mt=$('#homeModeToggle');if(mt)mt.onclick=e=>{e.stopPropagation();state.userMode=state.userMode==='Aluno'?'Professor':'Aluno';saveV15();window.render()};
  const fav=$('#favoriteMagazine');if(fav)fav.onclick=()=>{toggleMagFav(state.magazineId);window.render()};
  const dl=$('#downloadMagazine');if(dl)dl.onclick=()=>{toggleMagDownload(state.magazineId);window.render()};
  const read=$('#readMagazine');if(read)read.onclick=()=>{const p=getMagProgress(state.magazineId);state.magPage=p.opened?p.page:0;setMagProgress(state.magazineId,state.magPage);nav('magReader')};
  const rb=$('#readerBookmark');if(rb)rb.onclick=()=>{toggleMagFav(state.magazineId);window.render()};
  const prev=$('#prevMagPage');if(prev)prev.onclick=()=>{if(state.magPage>0){state.magPage--;setMagProgress(state.magazineId,state.magPage);window.render();scrollTo(0,0)}};
  const next=$('#nextMagPage');if(next)next.onclick=()=>{const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0],max=getMagazinePages(m).length-1;if(state.magPage<max){state.magPage++;setMagProgress(state.magazineId,state.magPage);window.render();scrollTo(0,0)}};
};
function bindV15Cards(){
  $$('[data-magazine-card]').forEach(c=>c.onclick=()=>{state.magazineId=c.dataset.magazineCard;const p=getMagProgress(state.magazineId);state.magPage=p.opened?p.page:0;nav('magazine')});
  $$('[data-magfav-card]').forEach(b=>b.onclick=e=>{e.stopPropagation();toggleMagFav(b.dataset.magfavCard);const g=$('#magGrid');if(g)g.innerHTML=magGridV15();bindV15Cards()});
}
window.render();