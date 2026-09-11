const _renderV19_private = window.render;
const _bindV19_private = window.bind;
const HARPA_USER_191 = window.HARPA_LYRICS_USER || {};
state.harpaFont191 = Number(localStorage.getItem('ebd-harpa-font-191') || '100');
state.lastHymn191 = Number(localStorage.getItem('ebd-last-hymn-191') || '1');

function saveHarpa191(){
  localStorage.setItem('ebd-harpa-font-191', String(state.harpaFont191));
  localStorage.setItem('ebd-last-hymn-191', String(state.lastHymn191));
}
function hymnPrivate191(n){
  n=Number(n);
  if(Array.isArray(HARPA_USER_191)) return HARPA_USER_191.find(x=>Number(x?.n)===n)||null;
  const direct=HARPA_USER_191[String(n)];
  if(typeof direct==='string') return {n,lyrics:direct};
  if(direct&&typeof direct==='object') return direct;
  const idx=HARPA_USER_191[n-1];
  if(idx&&typeof idx==='object'&&Number(idx.n)===n) return idx;
  return null;
}
function lyric191(n){ const h=hymnPrivate191(n); return String(h?.lyrics || ''); }
function privateTitle191(n){ const h=hymnPrivate191(n); return String(h?.title || ''); }
function harpaReady191(){ return Array.from({length:640},(_,i)=>i+1).every(n=>lyric191(n).trim().length>0); }
function lyricHtml191(text){
  if(!text)return '<div class="v191-no-lyric">Letra não disponível nesta instalação. O catálogo de números e títulos continua funcionando.</div>';
  return text.split(/\n\s*\n/).map((stanza,idx)=>`<div class="v191-stanza" data-stanza="${idx+1}">${stanza.split('\n').filter(Boolean).map(line=>`<div>${esc18(line)}</div>`).join('')}</div>`).join('');
}
function hymnSearchMatch191(h,q){
  if(!q)return true;
  const n=norm18(q), l=norm18(lyric191(h.n)), pt=norm18(privateTitle191(h.n));
  return String(h.n).includes(q.trim()) || norm18(h.title).includes(n) || pt.includes(n) || l.includes(n);
}

harpa18 = function(){
  const raw=String(state.harpaQueryV18||''), q=norm18(raw), complete=harpaReady191();
  let list=harpaCatalogV18.filter(h=>hymnSearchMatch191(h,raw));
  const total=list.length, show=q?list.slice(0,180):list.slice(0,state.harpaLimitV18);
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Harpa Cristã</h1><p>${complete?'640 hinos com letras disponíveis offline.':'640 hinos no catálogo offline.'}</p></div></div>
  <section class="v191-harpa-hero"><div class="v191-harpa-icon">🎵</div><div><span>${complete?'HARPA COMPLETA • OFFLINE':'HARPA • CATÁLOGO OFFLINE'}</span><h2>${complete?'640 hinos com letras':'640 números e títulos'}</h2><p>${complete?'Leitura, busca e favoritos disponíveis no aplicativo.':'Catálogo de números e títulos disponível offline.'}</p></div><b>${complete?'✓':'i'}</b></section>
  <div class="v18-harpa-search"><span>🔎</span><input class="field" id="harpaSearch18" value="${esc18(raw)}" placeholder="${complete?'Número, título ou palavra da letra...':'Número ou título do hino...'}"></div>
  <div class="v191-harpa-actions"><button id="continueHymn191">▶️ Continuar no hino ${state.lastHymn191||1}</button><button id="hymnFavFilter18">❤️ ${state.hymnFavsV18.length} favoritos</button></div>
  <div class="v191-result-count">${total} resultado${total===1?'':'s'}${q?' para “'+esc18(raw)+'”':''}</div>
  <div id="harpaList18" class="v18-hymn-list v191-hymn-list">${hymnRows18(show)}</div>${!q&&state.harpaLimitV18<list.length?`<button class="v18-load-more" id="loadMoreHarpa18">Carregar mais hinos (${Math.min(80,list.length-state.harpaLimitV18)})</button>`:''}`;
};

hymnDetail18 = function(){
  const h=harpaCatalogV18.find(x=>x.n===Number(state.hymn))||harpaCatalogV18[0];
  if(!h)return harpa18();
  const privateH=hymnPrivate191(h.n), lyrics=lyric191(h.n), title=privateH?.title||h.title, font=Math.max(90,Math.min(135,state.harpaFont191));
  state.lastHymn191=h.n; saveHarpa191();
  return `<div class="pagehead"><button class="back" data-route="harpa">‹</button><div><h1>Hino ${h.n}</h1><p>Harpa Cristã • leitura offline</p></div></div>
  <section class="v191-hymn-head"><div class="v191-hymn-number">${h.n}</div><div><span>HARPA CRISTÃ</span><h1>${esc18(title)}</h1><small>${lyrics?'Letra disponível offline':'Catálogo offline'}</small></div></section>
  <div class="v191-hymn-toolbar"><button id="prevHymn191" ${h.n<=1?'disabled':''}>‹ Anterior</button><button id="favHymn18">${isHymnFav18(h.n)?'❤️ Favorito':'🤍 Favoritar'}</button><button id="nextHymn191" ${h.n>=640?'disabled':''}>Próximo ›</button></div>
  <div class="v191-reading-tools"><button id="harpaFontDown191">A−</button><span>${font}%</span><button id="harpaFontUp191">A+</button>${lyrics?'<button id="copyHymn191">📋 Copiar</button>':''}</div>
  <article class="v191-lyrics" style="--harpa-font:${font}%">${lyricHtml191(lyrics)}</article>
  <div class="v191-hymn-bottom"><button id="prevHymnBottom191" ${h.n<=1?'disabled':''}>‹ Hino ${Math.max(1,h.n-1)}</button><button data-route="harpa">🎵 Todos os hinos</button><button id="nextHymnBottom191" ${h.n>=640?'disabled':''}>Hino ${Math.min(640,h.n+1)} ›</button></div>`;
};

const _contentInfo18_private = contentInfo18;
contentInfo18 = function(){
  const base=_contentInfo18_private();
  if(!harpaReady191()) return base;
  return base.replace(/<section class="v18-info-card"><span>🎵<\/span>[\s\S]*?<\/section>/,
  `<section class="v18-info-card v191-private-source"><span>🎵</span><div><strong>Harpa Cristã • offline</strong><p>640 hinos com letras disponíveis nesta instalação.</p><small>Conteúdo integrado ao módulo Harpa Cristã do Bíblia EBD.</small></div></section>`);
};

function harpaHome191(){
  const complete=harpaReady191();
  return `<section class="section v191-home-harpa"><div class="v191-home-icon">🎵</div><div><span>${complete?'HARPA COMPLETA':'HARPA CRISTÃ'}</span><strong>${complete?'640 hinos com letras':'640 hinos • catálogo'}</strong><small>${complete?'Busca por número, título ou trecho • offline':'Números e títulos disponíveis offline'}</small></div><button data-route="harpa">Abrir</button></section>`;
}

window.render=function(){
  _renderV19_private();
  if(state.route==='home'){
    const app=$('#app');
    if(app&&!app.querySelector('.v191-home-harpa'))app.insertAdjacentHTML('afterbegin',harpaHome191());
    bindV191();
  }
};
window.bind=function(){ _bindV19_private(); bindV191(); };

function goHymn191(n){
  n=Math.max(1,Math.min(640,Number(n)||1));
  state.hymn=n;state.lastHymn191=n;saveHarpa191();nav('hymn');
}
function bindV191(){
  $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
  const hs=$('#harpaSearch18');
  if(hs)hs.oninput=()=>{state.harpaQueryV18=hs.value;state.harpaLimitV18=80;window.render();};
  $$('[data-hymn18]').forEach(b=>b.onclick=()=>goHymn191(b.dataset.hymn18));
  $('#continueHymn191')?.addEventListener('click',()=>goHymn191(state.lastHymn191||1));
  $('#loadMoreHarpa18')?.addEventListener('click',()=>{state.harpaLimitV18+=80;window.render();});
  $('#hymnFavFilter18')?.addEventListener('click',()=>{
    const favs=harpaCatalogV18.filter(h=>isHymnFav18(h.n));
    const box=$('#harpaList18');if(box)box.innerHTML=hymnRows18(favs);
    $$('[data-hymn18]').forEach(b=>b.onclick=()=>goHymn191(b.dataset.hymn18));
  });
  $('#prevHymn191')?.addEventListener('click',()=>goHymn191(Number(state.hymn)-1));
  $('#prevHymnBottom191')?.addEventListener('click',()=>goHymn191(Number(state.hymn)-1));
  $('#nextHymn191')?.addEventListener('click',()=>goHymn191(Number(state.hymn)+1));
  $('#nextHymnBottom191')?.addEventListener('click',()=>goHymn191(Number(state.hymn)+1));
  $('#harpaFontDown191')?.addEventListener('click',()=>{state.harpaFont191=Math.max(90,state.harpaFont191-5);saveHarpa191();window.render();});
  $('#harpaFontUp191')?.addEventListener('click',()=>{state.harpaFont191=Math.min(135,state.harpaFont191+5);saveHarpa191();window.render();});
  $('#copyHymn191')?.addEventListener('click',()=>{
    const h=harpaCatalogV18.find(x=>x.n===Number(state.hymn)), p=hymnPrivate191(state.hymn);
    if(h&&lyric191(h.n))copy18(`Harpa Cristã ${h.n} — ${p?.title||h.title}\n\n${lyric191(h.n)}`);
  });
  const menuHarpa=[...document.querySelectorAll('.menu-item')].find(x=>x.dataset.route==='harpa');
  if(menuHarpa){const s=menuHarpa.querySelector('small');if(s)s.textContent=harpaReady191()?'640 hinos com letras':'640 hinos • catálogo';}
}

window.render();
