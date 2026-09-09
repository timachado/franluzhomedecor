const _renderV13=window.render;
const _bindV13=window.bind;
state.magFavs=JSON.parse(localStorage.getItem('ebd-mag-favs')||'[]');
state.magDownloads=JSON.parse(localStorage.getItem('ebd-mag-downloads')||'[]');
state.magPage=Number(localStorage.getItem('ebd-mag-page')||0);
state.magView=state.magView||'all';

magazineLibrary.forEach((m,i)=>{
  m.year=m.year||2026;
  m.quarter=m.quarter||'3º trimestre';
  m.isNew=typeof m.isNew==='boolean'?m.isNew:i<3;
  m.author=m.author||'Equipe Bíblia EBD';
});

function saveMagState(){
  localStorage.setItem('ebd-mag-favs',JSON.stringify(state.magFavs));
  localStorage.setItem('ebd-mag-downloads',JSON.stringify(state.magDownloads));
  localStorage.setItem('ebd-mag-page',String(state.magPage||0));
}
function isMagFav(id){return state.magFavs.includes(id)}
function isMagDownloaded(id){return state.magDownloads.includes(id)}
function toggleMagFav(id){
  state.magFavs=isMagFav(id)?state.magFavs.filter(x=>x!==id):[...state.magFavs,id];
  saveMagState();
  toast(isMagFav(id)?'Revista adicionada aos favoritos ❤️':'Revista removida dos favoritos');
}
function toggleMagDownload(id){
  state.magDownloads=isMagDownloaded(id)?state.magDownloads.filter(x=>x!==id):[...state.magDownloads,id];
  saveMagState();
  toast(isMagDownloaded(id)?'Revista disponível offline ⬇️':'Download offline removido');
}
function filteredMagazinesV14(){
  const q=(state.magQuery||'').trim().toLowerCase();
  return magazineLibrary.filter(m=>{
    const catOk=state.magFilter==='all'||m.cat===state.magFilter;
    const qOk=!q||`${m.title} ${m.subtitle} ${m.audience} ${m.edition} ${m.year} ${m.quarter}`.toLowerCase().includes(q);
    const viewOk=state.magView==='all'||(state.magView==='favorites'&&isMagFav(m.id))||(state.magView==='offline'&&isMagDownloaded(m.id));
    return catOk&&qOk&&viewOk;
  });
}
function magazineCoverV14(m){
  return `<div class="mag-cover-art mag-cover-v14 ${m.cover}" data-symbol="${m.symbol}">
    <div class="mag-cover-badges">${m.isNew?'<span class="mag-new">NOVA</span>':''}<span>${m.edition.toUpperCase()}</span></div>
    <div class="mag-series">${m.quarter} • ${m.year}</div>
    <div class="mag-cover-title">LIÇÕES<br>BÍBLICAS<small>${m.title}</small></div>
    <div class="mag-cover-foot"><span>Bíblia EBD</span><span>${m.audience}</span></div>
  </div>`;
}
function magazineGridV14(){
  const list=filteredMagazinesV14();
  if(!list.length)return `<div class="mag-empty"><div style="font-size:30px;margin-bottom:8px">📚</div>Nenhuma revista encontrada nesta seleção.</div>`;
  return `<div class="mag-grid mag-grid-v14">${list.map(m=>`<article class="mag-card mag-card-v14" data-magazine-card="${m.id}">
    <div class="mag-card-cover-wrap">${magazineCoverV14(m)}<button class="mag-heart ${isMagFav(m.id)?'active':''}" data-magfav-card="${m.id}" aria-label="Favoritar">${isMagFav(m.id)?'❤️':'🤍'}</button>${isMagDownloaded(m.id)?'<span class="mag-offline-badge">⬇ offline</span>':''}</div>
    <div class="mag-card-meta"><strong>${m.title}</strong><small>${m.quarter} ${m.year}</small><span class="mag-category">${m.catLabel} • ${m.edition}</span></div>
  </article>`).join('')}</div>`;
}
window.ebdContent=function(){
  if(state.ebdTab!=='revistas')return _ebdContentV12();
  return `<section class="mag-library-head mag-library-v14">
    <div class="mag-library-title"><span class="tiny-label">BIBLIOTECA EBD</span><h2>Revistas de Estudo</h2><p>Aprofunde seus conhecimentos nas Escrituras com lições trimestrais organizadas por classe.</p></div>
    <div class="mag-search"><input class="field" id="magSearch" value="${state.magQuery||''}" placeholder="Pesquisar por título, classe, trimestre ou ano..."></div>
    <div class="mag-view-tabs"><button class="${state.magView==='all'?'active':''}" data-magview="all">Todas</button><button class="${state.magView==='favorites'?'active':''}" data-magview="favorites">❤️ Favoritas</button><button class="${state.magView==='offline'?'active':''}" data-magview="offline">⬇ Offline</button></div>
    <div class="mag-filters">${[['all','Todas'],['adultos','Adultos'],['jovens','Jovens'],['adolescentes','Adolescentes'],['professor','Professor'],['infantil','Infantil']].map(([k,l])=>`<button class="mag-filter ${state.magFilter===k?'active':''}" data-magfilter="${k}">${l}</button>`).join('')}</div>
    <div id="magGrid">${magazineGridV14()}</div>
  </section>`;
};

function magazineDetailV14(){
  const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0];
  const lessonNames=['A Palavra que transforma a vida','Fé que persevera','Sabedoria para decidir','O valor da comunhão','Servindo com propósito','Esperança em tempos difíceis'];
  const fav=isMagFav(m.id),off=isMagDownloaded(m.id);
  return `<div class="pagehead"><button class="back" data-route="ebd">‹</button><div><h1>${m.edition==='Professor'?'Revista do Professor':'Revista de Estudo'}</h1><p>${m.audience} • ${m.quarter} ${m.year}</p></div></div>
  <div class="mag-detail-hero"><div class="mag-detail-cover-v14">${magazineCoverV14(m)}</div><div class="mag-detail-shine"></div></div>
  <section class="mag-info-panel mag-info-v14">
    <div class="mag-detail-tags"><span>${m.catLabel}</span><span>${m.edition}</span>${m.isNew?'<span class="new">Nova edição</span>':''}${off?'<span class="offline">Disponível offline</span>':''}</div>
    <h2>${m.title}</h2><p class="mag-subtitle">${m.subtitle}</p><p>${m.desc}</p>
    <div class="mag-meta-grid"><div><small>Trimestre</small><strong>${m.quarter}</strong></div><div><small>Ano</small><strong>${m.year}</strong></div><div><small>Classe</small><strong>${m.audience}</strong></div><div><small>Edição</small><strong>${m.edition}</strong></div></div>
    <div class="mag-actions mag-actions-v14"><button class="btn btn-primary" id="readMagazine">📖 Ler revista</button><button class="btn btn-dark" id="downloadMagazine">${off?'✓ Offline':'⬇ Baixar'}</button></div>
    <button class="mag-wide-action ${fav?'active':''}" id="favoriteMagazine">${fav?'❤️ Revista favoritada':'🤍 Adicionar aos favoritos'}</button>
  </section>
  <div class="subhead">Lições desta revista</div>${lessonNames.map((x,i)=>`<div class="list-card mag-lesson clickable" data-maglesson="${i+1}"><div class="mag-lesson-num">${String(i+1).padStart(2,'0')}</div><div><strong>${x}</strong><p>${i===0?'Texto áureo, verdade prática, objetivos e aplicação.':'Conteúdo demonstrativo da biblioteca EBD.'}</p></div><span style="margin-left:auto">›</span></div>`).join('')}`;
}

function getMagazinePages(m){
  return [
    {type:'cover',html:`<div class="reader-cover-page">${magazineCoverV14(m)}<div class="reader-cover-caption"><span>${m.quarter} ${m.year}</span><strong>${m.title}</strong><small>${m.subtitle}</small></div></div>`},
    {type:'content',html:`<div class="mag-page-kicker">APRESENTAÇÃO</div><h1>${m.title}</h1><p>${m.desc}</p><div class="mag-page-quote">“Ensinar a Palavra com clareza é ajudar cada aluno a perceber como a verdade bíblica alcança a vida cotidiana.”</div><p>Esta edição demonstrativa da Bíblia EBD foi estruturada para leitura pessoal, preparação do professor e participação da classe.</p>`},
    {type:'content',html:`<div class="mag-page-kicker">LIÇÃO 01</div><h1>A Palavra que transforma a vida</h1><div class="mag-page-highlight"><small>Texto áureo</small><strong>“Sede praticantes da palavra e não somente ouvintes.”</strong><span>Tiago 1:22</span></div><p><b>Verdade prática:</b> o estudo bíblico alcança seu propósito quando a verdade compreendida se transforma em vida praticada.</p>`},
    {type:'content',html:`<div class="mag-page-kicker">OBJETIVOS</div><h1>O que a classe deve compreender</h1><div class="mag-page-numbered"><div><span>1</span><p>Entender a diferença entre ouvir a Palavra e praticá-la.</p></div><div><span>2</span><p>Relacionar conhecimento bíblico com obediência diária.</p></div><div><span>3</span><p>Definir uma aplicação concreta para a semana.</p></div></div>`},
    {type:'content',html:`<div class="mag-page-kicker">DESENVOLVIMENTO</div><h1>Da compreensão para a prática</h1><h3>1. O perigo de apenas ouvir</h3><p>Conhecer o texto é essencial, porém Tiago apresenta uma fé que responde à Palavra com atitudes concretas.</p><h3>2. A Palavra como espelho</h3><p>O texto bíblico confronta pensamentos, hábitos e decisões, conduzindo o discípulo à transformação.</p><h3>3. Aplicação na classe</h3><p>Peça aos alunos que expressem uma atitude específica que pretendem praticar até o próximo encontro.</p>`},
    {type:'content',html:`<div class="mag-page-kicker">PROFESSOR & ALUNO</div><h1>Para continuar estudando</h1><div class="mag-page-question"><b>Perguntas para a classe</b><p>• Qual a diferença entre conhecer e obedecer?</p><p>• Que hábito pode transformar leitura em prática?</p><p>• Qual será sua aplicação nesta semana?</p></div><div class="mag-page-highlight"><small>Próxima etapa</small><strong>Registre suas anotações e prepare a aula.</strong><span>Bíblia EBD</span></div>`}
  ];
}
function magazineReaderV14(){
  const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0];
  const pages=getMagazinePages(m); state.magPage=Math.max(0,Math.min(state.magPage,pages.length-1)); const p=pages[state.magPage];
  return `<div class="mag-reader-top"><button class="back" data-route="magazine">‹</button><div><strong>${m.title}</strong><small>${state.magPage+1} de ${pages.length}</small></div><button class="mag-reader-menu" id="readerBookmark">${isMagFav(m.id)?'❤️':'🤍'}</button></div>
  <div class="mag-page-progress"><span style="width:${((state.magPage+1)/pages.length)*100}%"></span></div>
  <article class="magazine-page ${p.type==='cover'?'cover-page':''}">${p.html}</article>
  <div class="mag-reader-controls"><button id="prevMagPage" ${state.magPage===0?'disabled':''}>‹ Anterior</button><span>Página ${state.magPage+1}</span><button id="nextMagPage" ${state.magPage===pages.length-1?'disabled':''}>Próxima ›</button></div>`;
}

window.render=function(){
  if(state.route==='magazine'){$('#app').innerHTML=magazineDetailV14();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='magReader'){$('#app').innerHTML=magazineReaderV14();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  _renderV13();
};
window.bind=function(){
  _bindV13();
  const s=$('#magSearch');if(s)s.oninput=()=>{state.magQuery=s.value;const g=$('#magGrid');if(g)g.innerHTML=magazineGridV14();bindMagazineV14()};
  $$('[data-magfilter]').forEach(b=>b.onclick=()=>{state.magFilter=b.dataset.magfilter;window.render()});
  $$('[data-magview]').forEach(b=>b.onclick=()=>{state.magView=b.dataset.magview;window.render()});
  bindMagazineV14();
  const favBtn=$('#favoriteMagazine');if(favBtn)favBtn.onclick=()=>{toggleMagFav(state.magazineId);window.render()};
  const dlBtn=$('#downloadMagazine');if(dlBtn)dlBtn.onclick=()=>{toggleMagDownload(state.magazineId);window.render()};
  const read=$('#readMagazine');if(read)read.onclick=()=>{state.magPage=0;saveMagState();nav('magReader')};
  const rb=$('#readerBookmark');if(rb)rb.onclick=()=>{toggleMagFav(state.magazineId);window.render()};
  const prev=$('#prevMagPage');if(prev)prev.onclick=()=>{if(state.magPage>0){state.magPage--;saveMagState();window.render();scrollTo(0,0)}};
  const next=$('#nextMagPage');if(next)next.onclick=()=>{const m=magazineLibrary.find(x=>x.id===state.magazineId)||magazineLibrary[0];const max=getMagazinePages(m).length-1;if(state.magPage<max){state.magPage++;saveMagState();window.render();scrollTo(0,0)}};
};
function bindMagazineV14(){
  $$('[data-magazine-card]').forEach(c=>c.onclick=()=>{state.magazineId=c.dataset.magazineCard;state.magPage=0;saveMagState();nav('magazine')});
  $$('[data-magfav-card]').forEach(b=>b.onclick=e=>{e.stopPropagation();toggleMagFav(b.dataset.magfavCard);const g=$('#magGrid');if(g)g.innerHTML=magazineGridV14();bindMagazineV14()});
}
window.render();