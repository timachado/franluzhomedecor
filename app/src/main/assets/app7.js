const _renderV15=window.render;
const _bindV15=window.bind;

state.profileV16=JSON.parse(localStorage.getItem('ebd-profile-v16')||'null')||{name:'Cristão',church:'',className:'Adultos',role:state.userMode||'Aluno',weeklyGoal:5};
state.globalQuery=state.globalQuery||'';

function saveProfileV16(){
  localStorage.setItem('ebd-profile-v16',JSON.stringify(state.profileV16));
  state.userMode=state.profileV16.role||state.userMode||'Aluno';
  if(typeof saveV15==='function')saveV15();
}
function escV16(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function readingMagazineStats(){
  const opened=Object.keys(state.magProgress||{}).filter(id=>state.magProgress[id]?.opened);
  const complete=opened.filter(id=>getMagProgress(id).pct>=100);
  const avg=opened.length?Math.round(opened.reduce((a,id)=>a+getMagProgress(id).pct,0)/opened.length):0;
  return {opened:opened.length,complete:complete.length,avg};
}
function searchAllV16(q){
  q=(q||'').trim().toLowerCase();
  if(q.length<2)return [];
  const out=[];
  Object.entries(demo).forEach(([ref,verses])=>{
    verses.forEach((text,i)=>{if(text.toLowerCase().includes(q)||ref.toLowerCase().includes(q)){const m=ref.match(/^(.*) (\d+)$/);out.push({type:'bible',icon:'📖',title:`${ref}:${i+1}`,sub:text,book:m?.[1]||state.book,chapter:Number(m?.[2]||1)})}})
  });
  magazineLibrary.forEach(m=>{const hay=`${m.title} ${m.subtitle} ${m.audience} ${m.edition} ${m.quarter} ${m.year}`.toLowerCase();if(hay.includes(q))out.push({type:'mag',icon:'📚',title:m.title,sub:`${m.quarter} ${m.year} • ${m.audience} • ${m.edition}`,id:m.id})});
  hymns.forEach(h=>{if(`${h.n} ${h.title} ${h.theme}`.toLowerCase().includes(q))out.push({type:'hymn',icon:'🎵',title:`Hino ${h.n} • ${h.title}`,sub:h.theme,n:h.n})});
  Object.entries(dict).forEach(([k,d])=>{if(`${k} ${d.title} ${d.def} ${d.refs}`.toLowerCase().includes(q))out.push({type:'dict',icon:'📚',title:d.title,sub:d.def,key:k})});
  return out.slice(0,40);
}
function searchPageV16(){
  const results=searchAllV16(state.globalQuery);
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Busca Global</h1><p>Bíblia, revistas, Harpa e dicionário em uma só busca.</p></div></div>
  <div class="global-search-box"><span>🔎</span><input class="field" id="globalSearchInput" value="${escV16(state.globalQuery)}" placeholder="Digite pelo menos 2 letras..."></div>
  <div class="search-scope-chips"><span>📖 Bíblia</span><span>📚 Revistas</span><span>🎵 Harpa</span><span>🔎 Dicionário</span></div>
  <div id="globalSearchResults">${globalResultsHtmlV16(results)}</div>`;
}
function globalResultsHtmlV16(results){
  if((state.globalQuery||'').trim().length<2)return `<div class="empty"><div class="big">🔎</div><strong>Pesquise em todo o aplicativo</strong><p>Ex.: fé, graça, Gênesis, jovens, oração...</p></div>`;
  if(!results.length)return `<div class="empty"><div class="big">📭</div><strong>Nenhum resultado</strong><p>Tente outra palavra ou expressão.</p></div>`;
  return `<div class="global-results">${results.map((r,i)=>`<article class="global-result" data-search-result="${i}" data-type="${r.type}" ${r.book?`data-book="${escV16(r.book)}" data-chapter="${r.chapter}"`:''} ${r.id?`data-magid="${r.id}"`:''} ${r.n?`data-hymn="${r.n}"`:''} ${r.key?`data-dictkey="${escV16(r.key)}"`:''}><div class="global-result-icon">${r.icon}</div><div><strong>${escV16(r.title)}</strong><p>${escV16(r.sub)}</p></div><span class="go-arrow">›</span></article>`).join('')}</div>`;
}
function libraryV16(){
  const ids=[...myMagazineIds()];
  const list=ids.map(id=>magazineLibrary.find(m=>m.id===id)).filter(Boolean).sort((a,b)=>(state.magProgress[b.id]?.updatedAt||0)-(state.magProgress[a.id]?.updatedAt||0));
  const stats=readingMagazineStats();
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Minha Biblioteca</h1><p>Seu conteúdo salvo, offline e em andamento.</p></div></div>
  <section class="library-summary"><div><span>📚</span><b>${list.length}</b><small>revistas</small></div><div><span>✅</span><b>${stats.complete}</b><small>concluídas</small></div><div><span>📊</span><b>${stats.avg}%</b><small>média</small></div></section>
  <div class="library-shortcuts"><button data-library-filter="reading">▶ Em andamento</button><button data-library-filter="favorites">❤️ Favoritas</button><button data-library-filter="offline">⬇ Offline</button></div>
  <div id="libraryList">${libraryListHtmlV16(list,'all')}</div>`;
}
function libraryListHtmlV16(list,filter){
  let arr=list;
  if(filter==='reading')arr=arr.filter(m=>getMagProgress(m.id).opened&&getMagProgress(m.id).pct<100);
  if(filter==='favorites')arr=arr.filter(m=>isMagFav(m.id));
  if(filter==='offline')arr=arr.filter(m=>isMagDownloaded(m.id));
  if(!arr.length)return `<div class="empty"><div class="big">📚</div><strong>Nenhuma revista aqui ainda</strong><p>Abra uma edição, favorite ou marque para uso offline.</p></div>`;
  return arr.map(m=>{const p=getMagProgress(m.id);return `<article class="library-row" data-library-mag="${m.id}"><div class="library-thumb">${magazineCoverV14(m)}</div><div class="library-info"><strong>${m.title}</strong><small>${m.quarter} ${m.year} • ${m.edition}</small><div class="library-tags">${isMagFav(m.id)?'<span>❤️ favorita</span>':''}${isMagDownloaded(m.id)?'<span>⬇ offline</span>':''}</div>${p.opened?`<div class="library-progress"><span style="width:${p.pct}%"></span></div><em>${p.pct}% • página ${p.page+1}/${p.total}</em>`:'<em>Não iniciada</em>'}</div><span class="go-arrow">›</span></article>`}).join('');
}
function profileV16(){
  const s=readingMagazineStats();
  const p=state.profileV16;
  return `<div class="pagehead"><div><h1>Meu Perfil</h1><p>Preferências, progresso e dados de estudo.</p></div></div>
  <section class="profile-hero-v16"><div class="profile-avatar-v16">${escV16((p.name||'C').trim().charAt(0).toUpperCase()||'C')}</div><div><span>${escV16(p.role)}</span><h2>${escV16(p.name||'Cristão')}</h2><p>${escV16(p.church||'Bíblia EBD • estudo pessoal')}</p></div></section>
  <section class="profile-stats-v16"><div><b>${s.opened}</b><span>Revistas iniciadas</span></div><div><b>${state.notes.length}</b><span>Anotações</span></div><div><b>${state.favs.length}</b><span>Versículos salvos</span></div><div><b>${s.avg}%</b><span>Progresso médio</span></div></section>
  <section class="form-card profile-form-v16"><h3>Dados do perfil</h3><label>Nome</label><input class="field" id="profileName" value="${escV16(p.name)}" placeholder="Seu nome"><label>Igreja / congregação</label><input class="field" id="profileChurch" value="${escV16(p.church)}" placeholder="Opcional"><label>Classe principal</label><select class="field" id="profileClass"><option ${p.className==='Adultos'?'selected':''}>Adultos</option><option ${p.className==='Jovens'?'selected':''}>Jovens</option><option ${p.className==='Adolescentes'?'selected':''}>Adolescentes</option><option ${p.className==='Infantil'?'selected':''}>Infantil</option></select><label>Modo</label><div class="profile-role-switch"><button class="${p.role==='Aluno'?'active':''}" data-profile-role="Aluno">👤 Aluno</button><button class="${p.role==='Professor'?'active':''}" data-profile-role="Professor">🧑‍🏫 Professor</button></div><button class="btn btn-primary" id="saveProfileV16">Salvar perfil</button></section>
  <div class="tool-row clickable" data-route="library"><div class="ico">📚</div><div class="grow"><strong>Minha Biblioteca</strong><small>Revistas, favoritos e offline.</small></div><span>›</span></div>
  <div class="tool-row clickable" data-route="sync"><div class="ico">☁️</div><div class="grow"><strong>Backup & Sincronização</strong><small>Proteja seus dados locais.</small></div><span>›</span></div>`;
}
function backupObjectV16(){return {version:16,createdAt:new Date().toISOString(),profile:state.profileV16,notes:state.notes,favs:state.favs,publicNotes:state.publicNotes,magFavs:state.magFavs,magDownloads:state.magDownloads,magProgress:state.magProgress,userMode:state.userMode,continueMagazineId:state.continueMagazineId}}
function syncV16(){
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Backup & Sincronização</h1><p>Seus dados continuam funcionando offline.</p></div></div>
  <section class="sync-status-v16"><div class="sync-cloud">☁️</div><div><span class="badge-soft">MODO LOCAL ATIVO</span><h2>Dados protegidos no aparelho</h2><p>Esta versão prepara a estrutura para conta online futura, sem depender da internet para leitura e anotações.</p></div></section>
  <section class="form-card"><h3>Backup manual</h3><p class="sync-help">Gere um backup em texto para guardar suas anotações, progresso, perfil e biblioteca. Depois você pode restaurar neste aparelho.</p><button class="btn btn-purple" id="generateBackupV16">Gerar backup</button><textarea class="field backup-area-v16" id="backupTextV16" placeholder="O backup aparecerá aqui..."></textarea><div class="row"><button class="btn btn-dark" id="copyBackupV16">Copiar</button><button class="btn btn-primary" id="restoreBackupV16">Restaurar</button></div></section>
  <section class="panel sync-future-v16"><strong>Próxima etapa online</strong><p>Login, conta Google/e-mail e sincronização entre aparelhos podem ser conectados a um backend seguro sem remover o modo offline atual.</p></section>`;
}
function homeV16(){
  let base=homeV15();
  const p=state.profileV16,s=readingMagazineStats();
  base=base.replace('Olá, Cristão 👋',`Olá, ${escV16(p.name||'Cristão')} 👋`);
  const block=`<section class="section dashboard-v16"><button class="home-global-search" data-route="search"><span>🔎</span><div><strong>Buscar em tudo</strong><small>Bíblia, revistas, Harpa e dicionário</small></div><b>›</b></button><div class="dashboard-stats-v16"><div><span>📚</span><b>${s.opened}</b><small>revistas iniciadas</small></div><div><span>📝</span><b>${state.notes.length}</b><small>anotações</small></div><div><span>❤️</span><b>${state.favs.length}</b><small>versículos</small></div></div><div class="dashboard-actions-v16"><button data-route="library">📚 Minha Biblioteca</button><button data-route="profile">👤 Meu Perfil</button></div></section>`;
  return base.replace('</section>',`</section>${block}`);
}

window.render=function(){
  if(state.route==='home'){$('#app').innerHTML=homeV16();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='home'));window.bind();return}
  if(state.route==='search'){$('#app').innerHTML=searchPageV16();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='library'){$('#app').innerHTML=libraryV16();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='profile'){$('#app').innerHTML=profileV16();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='profile'));window.bind();return}
  if(state.route==='sync'){$('#app').innerHTML=syncV16();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  _renderV15();
};

window.bind=function(){
  _bindV15();
  const gsi=$('#globalSearchInput');if(gsi)gsi.oninput=()=>{state.globalQuery=gsi.value;const box=$('#globalSearchResults');if(box)box.innerHTML=globalResultsHtmlV16(searchAllV16(state.globalQuery));bindSearchV16()};
  bindSearchV16();
  $$('[data-library-filter]').forEach(b=>b.onclick=()=>{const ids=[...myMagazineIds()],list=ids.map(id=>magazineLibrary.find(m=>m.id===id)).filter(Boolean);$('#libraryList').innerHTML=libraryListHtmlV16(list,b.dataset.libraryFilter);bindLibraryV16()});
  bindLibraryV16();
  $$('[data-profile-role]').forEach(b=>b.onclick=()=>{$$('[data-profile-role]').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.profileV16.role=b.dataset.profileRole});
  const sp=$('#saveProfileV16');if(sp)sp.onclick=()=>{state.profileV16.name=$('#profileName').value.trim()||'Cristão';state.profileV16.church=$('#profileChurch').value.trim();state.profileV16.className=$('#profileClass').value;saveProfileV16();toast('Perfil salvo ✅');window.render()};
  const gb=$('#generateBackupV16');if(gb)gb.onclick=()=>{$('#backupTextV16').value=JSON.stringify(backupObjectV16());toast('Backup gerado')};
  const cb=$('#copyBackupV16');if(cb)cb.onclick=async()=>{const t=$('#backupTextV16');if(!t.value)return toast('Gere o backup primeiro');try{await navigator.clipboard.writeText(t.value);toast('Backup copiado 📋')}catch(e){t.select();document.execCommand('copy');toast('Backup copiado 📋')}};
  const rb=$('#restoreBackupV16');if(rb)rb.onclick=()=>{try{const d=JSON.parse($('#backupTextV16').value);if(!d||!d.version)throw new Error('invalid');state.profileV16=d.profile||state.profileV16;state.notes=Array.isArray(d.notes)?d.notes:state.notes;state.favs=Array.isArray(d.favs)?d.favs:state.favs;state.publicNotes=Array.isArray(d.publicNotes)?d.publicNotes:state.publicNotes;state.magFavs=Array.isArray(d.magFavs)?d.magFavs:state.magFavs;state.magDownloads=Array.isArray(d.magDownloads)?d.magDownloads:state.magDownloads;state.magProgress=d.magProgress||state.magProgress;state.userMode=d.userMode||state.userMode;state.continueMagazineId=d.continueMagazineId||state.continueMagazineId;save();saveMagState();saveV15();saveProfileV16();toast('Backup restaurado ✅');setTimeout(()=>nav('profile'),500)}catch(e){toast('Backup inválido')}};
};
function bindSearchV16(){
  $$('[data-search-result]').forEach(el=>el.onclick=()=>{const type=el.dataset.type;if(type==='bible'){state.book=el.dataset.book;state.chapter=Number(el.dataset.chapter||1);nav('reader')}else if(type==='mag'){state.magazineId=el.dataset.magid;nav('magazine')}else if(type==='hymn'){state.hymn=Number(el.dataset.hymn);nav('hymn')}else if(type==='dict'){state.globalQuery='';nav('dictionary');setTimeout(()=>{const q=$('#dictQ');if(q){q.value=el.dataset.dictkey;const go=$('#dictGo');if(go)go.click()}},50)}})
}
function bindLibraryV16(){$$('[data-library-mag]').forEach(el=>el.onclick=()=>{state.magazineId=el.dataset.libraryMag;const p=getMagProgress(state.magazineId);state.magPage=p.page;nav('magazine')})}

const topSearch=document.getElementById('globalSearchBtn');if(topSearch)topSearch.onclick=()=>nav('search');
saveProfileV16();
window.render();
