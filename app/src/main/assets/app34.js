// 1.15.10 — Biblioteca de Esboços: editar, duplicar, favoritar, pesquisar e organizar por pastas.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const OUTLINES_KEY='ebd-ai-outlines-v1154';
  const FOLDERS_KEY='ebd-outline-folders-v11510';
  const DEFAULT_FOLDERS=['Geral','Pregação','EBD','Devocional','Estudo'];
  const ui={query:'',folder:'all',favorites:false,editorId:null};

  function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function safe(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}}
  function toastMsg(s){try{window.toast?.(s)}catch(_){}}
  function uid(){return 'outline-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
  function short(s='',n=150){s=String(s).replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n-1)+'…':s}
  function norm(s=''){return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
  function now(){return Date.now()}

  function folders(){
    let custom=safe(localStorage.getItem(FOLDERS_KEY),[]);if(!Array.isArray(custom))custom=[];
    return [...new Set([...DEFAULT_FOLDERS,...custom.map(String).map(x=>x.trim()).filter(Boolean)])];
  }
  function saveFolders(list){
    const custom=[...new Set(list.map(String).map(x=>x.trim()).filter(x=>x&&!DEFAULT_FOLDERS.includes(x)))].slice(0,20);
    localStorage.setItem(FOLDERS_KEY,JSON.stringify(custom));
  }
  function inferFolder(r){
    const hay=norm(`${r?.title||''} ${r?.text||''}`);
    if(hay.includes('ebd')||hay.includes('licao'))return 'EBD';
    if(hay.includes('devocional')||hay.includes('oracao'))return 'Devocional';
    if(hay.includes('pregacao')||hay.includes('sermao'))return 'Pregação';
    if(hay.includes('estudo'))return 'Estudo';
    return 'Geral';
  }
  function normalizeRows(write=true){
    let rows=safe(localStorage.getItem(OUTLINES_KEY),[]);if(!Array.isArray(rows))rows=[];
    let changed=false;
    rows=rows.filter(x=>x&&typeof x==='object').map(r=>{
      const x=Object.assign({},r);
      if(!x.id){x.id=uid();changed=true}
      if(!x.folder){x.folder=inferFolder(x);changed=true}
      if(typeof x.favorite!=='boolean'){x.favorite=false;changed=true}
      if(!x.createdAt){x.createdAt=now();changed=true}
      if(!x.updatedAt){x.updatedAt=x.createdAt;changed=true}
      x.title=String(x.title||'Esboço sem título');
      x.text=String(x.text||'');
      x.reference=String(x.reference||'');
      return x;
    });
    if(write&&changed)localStorage.setItem(OUTLINES_KEY,JSON.stringify(rows.slice(0,80)));
    return rows.slice(0,80);
  }
  function saveRows(rows){localStorage.setItem(OUTLINES_KEY,JSON.stringify(rows.slice(0,80)))}
  function findRow(id){return normalizeRows(false).find(x=>x.id===id)||null}
  function formatDate(ts){try{return new Date(Number(ts)||Date.now()).toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'})}catch(_){return ''}}
  function share(text,title){
    try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(String(text),String(title));return}}catch(_){}
    if(navigator.share){navigator.share({title,text:String(text)}).catch(()=>{});return}
    navigator.clipboard?.writeText(String(text)).then(()=>toastMsg('Esboço copiado para compartilhar 📋'));
  }
  function recordText(r){return `${r.title||'Esboço'}${r.reference?`\n${r.reference}`:''}\n\n${r.text||''}`}

  function filtered(){
    const q=norm(ui.query.trim());
    return normalizeRows(false).filter(r=>{
      if(ui.favorites&&!r.favorite)return false;
      if(ui.folder!=='all'&&r.folder!==ui.folder)return false;
      if(q&&!norm(`${r.title} ${r.reference} ${r.folder} ${r.text}`).includes(q))return false;
      return true;
    }).sort((a,b)=>(Number(b.favorite)-Number(a.favorite))||((b.updatedAt||0)-(a.updatedAt||0)));
  }
  function stats(){
    const rows=normalizeRows(false);return {total:rows.length,favs:rows.filter(x=>x.favorite).length,folders:new Set(rows.map(x=>x.folder)).size};
  }
  function folderOptions(selected){return folders().map(f=>`<option ${f===selected?'selected':''}>${esc(f)}</option>`).join('')}
  function libraryHtml(){
    const rows=filtered(),s=stats(),fs=folders();
    return `<section class="v11510-library" id="outlineLibrary11510">
      <div class="v11510-head"><div><span>BIBLIOTECA DE ESBOÇOS</span><h2>Seus roteiros organizados</h2><p>Edite, duplique, favorite e separe por pastas. Tudo salvo neste aparelho e incluído no backup local.</p></div><button id="newManualOutline11510">＋ Novo manual</button></div>
      <div class="v11510-stats"><div><b>${s.total}</b><small>esboços</small></div><div><b>${s.favs}</b><small>favoritos</small></div><div><b>${s.folders}</b><small>pastas usadas</small></div></div>
      <div class="v11510-search"><span>🔎</span><input id="outlineSearch11510" value="${esc(ui.query)}" placeholder="Buscar título, referência ou conteúdo..."><button id="newFolder11510">＋ Pasta</button></div>
      <div class="v11510-filters"><button data-folder11510="all" class="${ui.folder==='all'?'active':''}">Todos</button>${fs.map(f=>`<button data-folder11510="${esc(f)}" class="${ui.folder===f?'active':''}">${esc(f)}</button>`).join('')}<button id="favOnly11510" class="${ui.favorites?'active':''}">★ Favoritos</button></div>
      <div class="v11510-list">${rows.length?rows.map(cardHtml).join(''):`<div class="v11510-empty"><span>🗂️</span><strong>Nenhum esboço neste filtro</strong><p>Crie com IA, faça um esboço manual ou altere os filtros acima.</p></div>`}</div>
    </section>`;
  }
  function cardHtml(r){
    return `<article class="v11510-card ${r.favorite?'favorite':''}" data-outline-card11510="${esc(r.id)}">
      <div class="v11510-cardtop"><div><span>${esc(r.folder||'Geral')}</span><strong>${esc(r.title)}</strong><small>${r.reference?`📖 ${esc(r.reference)} • `:''}Atualizado ${esc(formatDate(r.updatedAt))}</small></div><button class="star" data-fav-outline11510="${esc(r.id)}" aria-label="Favoritar">${r.favorite?'★':'☆'}</button></div>
      <p>${esc(short(r.text||'Esboço ainda sem conteúdo.',190))}</p>
      <div class="v11510-actions"><button data-edit-outline11510="${esc(r.id)}">✏️ Editar</button><button data-dup-outline11510="${esc(r.id)}">⧉ Duplicar</button><button data-copy-outline11510="${esc(r.id)}">📋 Copiar</button><button data-share-outline11510="${esc(r.id)}">↗ Compartilhar</button><button class="danger" data-del-outline11510="${esc(r.id)}">🗑️</button></div>
    </article>`;
  }
  function editorHtml(r){
    if(!r)return '';
    return `<div class="v11510-editor" id="outlineEditor11510"><div class="sheet"><div class="top"><div><span>EDITOR DE ESBOÇO</span><strong>${esc(r.title||'Novo esboço')}</strong></div><button id="closeOutlineEditor11510">✕</button></div>
      <label>Título<input class="field" id="outlineTitle11510" value="${esc(r.title||'')}"></label>
      <div class="two"><label>Referência<input class="field" id="outlineRef11510" value="${esc(r.reference||'')}" placeholder="Ex.: Salmos 23"></label><label>Pasta<select class="field" id="outlineFolder11510">${folderOptions(r.folder||'Geral')}</select></label></div>
      <label>Conteúdo<textarea class="field" id="outlineText11510" rows="16" placeholder="Introdução, pontos, aplicações e conclusão...">${esc(r.text||'')}</textarea></label>
      <div class="editor-actions"><button id="saveOutline11510" class="primary">✓ Salvar alterações</button><button id="copyEditor11510">📋 Copiar</button><button id="shareEditor11510">↗ Compartilhar</button></div>
    </div></div>`;
  }
  function refreshLibrary(){
    const old=document.getElementById('outlineLibrary11510');if(old)old.outerHTML=libraryHtml();
    bindLibrary();
  }
  function openEditor(id){ui.editorId=id;document.getElementById('outlineEditor11510')?.remove();const r=findRow(id);if(!r)return;document.body.insertAdjacentHTML('beforeend',editorHtml(r));bindEditor()}
  function closeEditor(){ui.editorId=null;document.getElementById('outlineEditor11510')?.remove()}
  function saveEditor(){
    const rows=normalizeRows(false),i=rows.findIndex(x=>x.id===ui.editorId);if(i<0)return;
    const title=(document.getElementById('outlineTitle11510')?.value||'').trim()||'Esboço sem título';
    const reference=(document.getElementById('outlineRef11510')?.value||'').trim();
    const text=(document.getElementById('outlineText11510')?.value||'').trim();
    const folder=document.getElementById('outlineFolder11510')?.value||'Geral';
    rows[i]=Object.assign({},rows[i],{title,reference,text,folder,updatedAt:now()});saveRows(rows);closeEditor();refreshLibrary();toastMsg('Esboço salvo ✓');
  }
  function newManual(){
    const rows=normalizeRows(false);const r={id:uid(),title:'Novo esboço',reference:'',text:'',folder:'Geral',favorite:false,createdAt:now(),updatedAt:now(),source:'manual'};rows.unshift(r);saveRows(rows);refreshLibrary();openEditor(r.id)
  }
  function duplicate(id){
    const rows=normalizeRows(false),src=rows.find(x=>x.id===id);if(!src)return;
    const copy=Object.assign({},src,{id:uid(),title:`${src.title} — cópia`,favorite:false,createdAt:now(),updatedAt:now(),source:'duplicate'});rows.unshift(copy);saveRows(rows);refreshLibrary();toastMsg('Cópia criada ⧉');
  }
  function toggleFavorite(id){const rows=normalizeRows(false),r=rows.find(x=>x.id===id);if(!r)return;r.favorite=!r.favorite;r.updatedAt=now();saveRows(rows);refreshLibrary()}
  function removeOutline(id){
    const rows=normalizeRows(false),r=rows.find(x=>x.id===id);if(!r)return;
    if(!confirm(`Excluir “${r.title}”?`))return;saveRows(rows.filter(x=>x.id!==id));refreshLibrary();toastMsg('Esboço excluído.');
  }
  function addFolder(){
    const name=(prompt('Nome da nova pasta','')||'').trim();if(!name)return;
    const list=folders();if(list.some(x=>norm(x)===norm(name)))return toastMsg('Essa pasta já existe.');
    list.push(name);saveFolders(list);ui.folder=name;refreshLibrary();toastMsg('Pasta criada 🗂️');
  }
  function bindLibrary(){
    const search=document.getElementById('outlineSearch11510');if(search&&search.dataset.bound!=='1'){search.dataset.bound='1';search.oninput=()=>{ui.query=search.value;refreshLibrary()}}
    document.querySelectorAll('[data-folder11510]').forEach(b=>b.onclick=()=>{ui.folder=b.dataset.folder11510||'all';refreshLibrary()});
    document.getElementById('favOnly11510')?.addEventListener('click',()=>{ui.favorites=!ui.favorites;refreshLibrary()});
    document.getElementById('newFolder11510')?.addEventListener('click',addFolder);
    document.getElementById('newManualOutline11510')?.addEventListener('click',newManual);
    document.querySelectorAll('[data-edit-outline11510]').forEach(b=>b.onclick=()=>openEditor(b.dataset.editOutline11510));
    document.querySelectorAll('[data-dup-outline11510]').forEach(b=>b.onclick=()=>duplicate(b.dataset.dupOutline11510));
    document.querySelectorAll('[data-fav-outline11510]').forEach(b=>b.onclick=()=>toggleFavorite(b.dataset.favOutline11510));
    document.querySelectorAll('[data-copy-outline11510]').forEach(b=>b.onclick=()=>{const r=findRow(b.dataset.copyOutline11510);if(!r)return;navigator.clipboard?.writeText(recordText(r)).then(()=>toastMsg('Esboço copiado 📋'))});
    document.querySelectorAll('[data-share-outline11510]').forEach(b=>b.onclick=()=>{const r=findRow(b.dataset.shareOutline11510);if(r)share(recordText(r),'Esboço • Bíblia EBD')});
    document.querySelectorAll('[data-del-outline11510]').forEach(b=>b.onclick=()=>removeOutline(b.dataset.delOutline11510));
  }
  function bindEditor(){
    document.getElementById('closeOutlineEditor11510')?.addEventListener('click',closeEditor);
    document.getElementById('saveOutline11510')?.addEventListener('click',saveEditor);
    document.getElementById('copyEditor11510')?.addEventListener('click',()=>{const r={title:document.getElementById('outlineTitle11510')?.value||'',reference:document.getElementById('outlineRef11510')?.value||'',text:document.getElementById('outlineText11510')?.value||''};navigator.clipboard?.writeText(recordText(r)).then(()=>toastMsg('Esboço copiado 📋'))});
    document.getElementById('shareEditor11510')?.addEventListener('click',()=>{const r={title:document.getElementById('outlineTitle11510')?.value||'',reference:document.getElementById('outlineRef11510')?.value||'',text:document.getElementById('outlineText11510')?.value||''};share(recordText(r),'Esboço • Bíblia EBD')});
    document.getElementById('outlineEditor11510')?.addEventListener('click',e=>{if(e.target.id==='outlineEditor11510')closeEditor()});
  }
  function injectLibrary(){
    if(state.route!=='outlines')return;
    normalizeRows(true);
    document.getElementById('aiSavedOutlines1154')?.remove();
    const app=document.getElementById('app');if(!app)return;
    if(!document.getElementById('outlineLibrary11510')){
      const hub=document.getElementById('aiOutlineHub1156');
      if(hub)hub.insertAdjacentHTML('afterend',libraryHtml());else app.insertAdjacentHTML('afterbegin',libraryHtml());
    }
    bindLibrary();
  }
  function post(){injectLibrary();if(ui.editorId&&!document.getElementById('outlineEditor11510')){const r=findRow(ui.editorId);if(r){document.body.insertAdjacentHTML('beforeend',editorHtml(r));bindEditor()}}}

  window.render=function(){previousRender();requestAnimationFrame(post)};
  window.bind=function(){previousBind();post()};
  window.__EBD_OUTLINES_11510__=Object.freeze({rows:()=>normalizeRows(false).map(x=>Object.assign({},x)),folders,openEditor,duplicate,toggleFavorite});
  normalizeRows(true);window.render();
})();
