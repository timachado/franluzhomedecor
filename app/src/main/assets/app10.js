const _renderV18 = window.render;
const _bindV18 = window.bind;

state.highlightsV19 = JSON.parse(localStorage.getItem('ebd-highlights-v19') || '{}');
state.readingHistoryV19 = JSON.parse(localStorage.getItem('ebd-history-v19') || '[]');
state.selectedVersesV19 = [];
state.studyVerseV19 = null;
state.studyFontV19 = Number(localStorage.getItem('ebd-font-v19') || '100');
state.searchQueryV19 = state.searchQueryV18 || '';

const STOP_V19 = new Set('a o as os um uma uns umas de da do das dos e em no na nos nas por para com sem que se como ao aos à às é são foi ser seu sua seus suas ele ela eles elas eu tu nós vos meu minha meus minhas teu tua teus tuas este esta isto isso aquele aquela quem quando onde porque pois mas ou já não sim mais menos muito toda todo todos todas cada sobre entre até também lhe lhes me te nos vos há'.split(' '));
const HL_V19 = ['yellow','green','blue','pink'];

function saveStudyV19(){
  localStorage.setItem('ebd-highlights-v19', JSON.stringify(state.highlightsV19));
  localStorage.setItem('ebd-history-v19', JSON.stringify(state.readingHistoryV19));
  localStorage.setItem('ebd-font-v19', String(state.studyFontV19));
}
function refV19(v){ return `${state.book} ${state.chapter}:${v}`; }
function verseTextV19(v){ return chapterVerses18(state.book,state.chapter)[Number(v)-1] || ''; }
function selectedV19(v){ return state.selectedVersesV19.includes(Number(v)); }
function highlightV19(ref){ return state.highlightsV19[ref] || ''; }
function toggleSelectV19(v){
  v=Number(v);
  state.selectedVersesV19 = selectedV19(v) ? state.selectedVersesV19.filter(x=>x!==v) : [...state.selectedVersesV19,v].sort((a,b)=>a-b);
  window.render();
}
function clearSelectionV19(){ state.selectedVersesV19=[]; window.render(); }
function pushHistoryV19(){
  const item={book:state.book,chapter:Number(state.chapter),at:Date.now()};
  state.readingHistoryV19=[item,...state.readingHistoryV19.filter(x=>!(x.book===item.book&&Number(x.chapter)===item.chapter))].slice(0,60);
  saveStudyV19();
}
function formatWhenV19(ts){
  const d=new Date(ts), now=new Date(), diff=Math.max(0, now-d);
  if(diff<60000)return 'agora';
  if(diff<3600000)return `${Math.floor(diff/60000)} min`;
  if(diff<86400000)return `${Math.floor(diff/3600000)} h`;
  return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'short'});
}
function normalizeRefInputV19(q=''){
  return String(q).trim().replace(/[–—]/g,'-').replace(/\s+/g,' ').replace(/\s*([:.,-])\s*/g,'$1');
}
function parseRef19(q){
  const clean=normalizeRefInputV19(q);
  let m=clean.match(/^(.+?)\s+(\d+)(?::|\.|,|\s)(\d+)(?:-(\d+))?$/);
  if(m){
    const book=findBook18(m[1]); if(!book)return null;
    const chapter=Number(m[2]), verse=Number(m[3]), endVerse=m[4]?Number(m[4]):verse;
    const meta=bookMeta18(book); if(chapter<1||chapter>meta.chapters)return null;
    const vs=chapterVerses18(book,chapter); if(verse<1||verse>vs.length||endVerse<verse||endVerse>vs.length)return null;
    return {book,chapter,verse,endVerse,text:vs[verse-1]};
  }
  m=clean.match(/^(.+?)\s+(\d+)$/);
  if(m){
    const book=findBook18(m[1]); if(!book)return null;
    const chapter=Number(m[2]),meta=bookMeta18(book); if(chapter<1||chapter>meta.chapters)return null;
    return {book,chapter,verse:null,endVerse:null,text:null};
  }
  return null;
}
parseRef18 = parseRef19;

function significantWordsV19(text){
  return [...new Set(norm18(text).replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(w=>w.length>=5&&!STOP_V19.has(w)))].slice(0,8);
}
function relatedVersesV19(text, currentRef, limit=6){
  const words=significantWordsV19(text); if(!words.length)return [];
  const idx=buildBibleIndex18(), scored=[];
  for(const v of idx){
    const ref=`${v.book} ${v.chapter}:${v.verse}`; if(ref===currentRef)continue;
    let score=0; for(const w of words)if(v.norm.includes(w))score++;
    if(score>=Math.min(2,words.length))scored.push({v,score});
  }
  scored.sort((a,b)=>b.score-a.score || a.v.book.localeCompare(b.v.book) || a.v.chapter-b.v.chapter || a.v.verse-b.v.verse);
  return scored.slice(0,limit).map(x=>x.v);
}
function selectedTextV19(){
  const nums=[...state.selectedVersesV19].sort((a,b)=>a-b);
  if(!nums.length)return '';
  return nums.map(v=>`${state.book} ${state.chapter}:${v} — ${verseTextV19(v)}`).join('\n');
}
function applyHighlightV19(color){
  const nums=state.selectedVersesV19.length?state.selectedVersesV19:(state.studyVerseV19?[state.studyVerseV19]:[]);
  if(!nums.length){toast('Selecione um versículo primeiro');return;}
  nums.forEach(v=>{const r=refV19(v); if(color)state.highlightsV19[r]=color; else delete state.highlightsV19[r];});
  saveStudyV19(); toast(color?'Marca-texto aplicado ✨':'Marca-texto removido'); window.render();
}
function favoriteSelectionV19(){
  if(!state.selectedVersesV19.length){toast('Selecione versículos primeiro');return;}
  let added=0;
  state.selectedVersesV19.forEach(v=>{const r=refV19(v);if(!isVerseFav18(r)){state.favs.unshift({r,t:verseTextV19(v)});added++;}});
  save(); toast(added?`${added} versículo(s) favoritado(s) ❤️`:'Todos já estão nos favoritos'); window.render();
}

function studyPanelV19(){
  const v=Number(state.studyVerseV19||0); if(!v)return '';
  const text=verseTextV19(v), ref=refV19(v), related=relatedVersesV19(text,ref);
  return `<section class="v19-study-panel">
    <div class="v19-study-head"><div><span>PAINEL DE ESTUDO</span><h2>${esc18(ref)}</h2></div><button id="closeStudy19">✕</button></div>
    <blockquote>${esc18(text)}</blockquote>
    <div class="v19-study-actions"><button data-note19="${v}">📝 Anotar</button><button data-copy19="${v}">📋 Copiar</button><button data-fav19="${v}">${isVerseFav18(ref)?'❤️':'🤍'} Favorito</button></div>
    <div class="v19-study-label">Marca-texto</div><div class="v19-palette">${HL_V19.map(c=>`<button class="v19-dot ${c}" data-highlight19="${c}" aria-label="Marca-texto ${c}"></button>`).join('')}<button class="v19-clear-hl" data-highlight19="">Limpar</button></div>
    <div class="v19-study-label">Passagens relacionadas por palavras-chave</div>
    <p class="v19-study-disclaimer">Sugestões automáticas do texto bíblico, não referências editoriais de uma Bíblia de estudo.</p>
    <div class="v19-related">${related.length?related.map(r=>`<button data-related19 data-book="${esc18(r.book)}" data-chapter="${r.chapter}" data-verse="${r.verse}"><strong>${esc18(r.book)} ${r.chapter}:${r.verse}</strong><small>${esc18(r.text)}</small></button>`).join(''):`<div class="v19-related-empty">Nenhuma passagem semelhante encontrada.</div>`}</div>
  </section>`;
}

function selectionBarV19(){
  const n=state.selectedVersesV19.length; if(!n)return '';
  return `<div class="v19-selection-bar"><div><strong>${n} selecionado${n>1?'s':''}</strong><small>${state.book} ${state.chapter}</small></div><button id="copySelected19">📋</button><button id="favSelected19">❤️</button><button id="highlightSelected19">✨</button><button id="clearSelected19">✕</button></div>
  <div class="v19-selection-palette" id="selectionPalette19">${HL_V19.map(c=>`<button class="v19-dot ${c}" data-highlight19="${c}"></button>`).join('')}<button class="v19-clear-hl" data-highlight19="">Sem cor</button></div>`;
}

function reader19(){
  if(!BIBLE_META_V18.some(b=>b.name===state.book))state.book='Gênesis';
  state.chapter=Math.max(1,Math.min(Number(state.chapter||1),bookMeta18(state.book).chapters));
  const verses=chapterVerses18(state.book,state.chapter), max=bookMeta18(state.book).chapters;
  if(!dataReady18())return reader18();
  pushHistoryV19();
  const font=Math.max(90,Math.min(125,state.studyFontV19));
  return `<div class="reader-nav v18-reader-nav v19-reader-nav"><button id="prevChapter19" ${state.chapter<=1?'disabled':''}>‹</button><select class="field" id="chapterSelect19">${Array.from({length:max},(_,i)=>`<option value="${i+1}" ${i+1===state.chapter?'selected':''}>${state.book} ${i+1}</option>`).join('')}</select><button id="nextChapter19" ${state.chapter>=max?'disabled':''}>›</button></div>
  <section class="v18-chapter-head v19-chapter-head"><span>BÍBLIA DE ESTUDO • OFFLINE</span><h1>${state.book} ${state.chapter}</h1><p>${verses.length} versículos • Almeida</p></section>
  <div class="v19-reader-tools"><button data-route="search">🔎 Buscar</button><button data-route="history19">🕘 Histórico</button><button id="fontDown19">A−</button><button id="fontUp19">A+</button></div>
  <div class="v19-reader-tip">💡 Toque em <strong>Selecionar</strong> para trabalhar com vários versículos ao mesmo tempo.</div>
  <article class="v18-verses v19-verses" style="--reader-font:${font}%">${verses.map((text,i)=>{const v=i+1,ref=`${state.book} ${state.chapter}:${v}`,fav=isVerseFav18(ref),hl=highlightV19(ref),sel=selectedV19(v);return `<section class="v18-verse v19-verse ${hl?`hl-${hl}`:''} ${sel?'selected':''}" id="v18verse-${v}"><button class="v18-vnum v19-vnum" data-select19="${v}">${sel?'✓':v}</button><p>${esc18(text)}</p><div class="v18-verse-actions v19-verse-actions"><button data-select19="${v}" class="${sel?'active':''}">${sel?'✅ Selecionado':'☑️ Selecionar'}</button><button data-study19="${v}">🔎 Estudar</button><button data-fav19="${v}" class="${fav?'active':''}">${fav?'❤️':'🤍'}</button><button data-note19="${v}">📝</button><button data-copy19="${v}">📋</button></div></section>`}).join('')}</article>
  ${studyPanelV19()}
  <div class="v18-reader-bottom"><button id="prevChapterBottom19" ${state.chapter<=1?'disabled':''}>‹ Capítulo anterior</button><button id="nextChapterBottom19" ${state.chapter>=max?'disabled':''}>Próximo capítulo ›</button></div>
  ${selectionBarV19()}`;
}

function history19(){
  const list=state.readingHistoryV19;
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Histórico de leitura</h1><p>Seus últimos capítulos lidos neste aparelho.</p></div></div>
  <section class="v19-history-summary"><div>🕘</div><div><span>HISTÓRICO OFFLINE</span><strong>${list.length} capítulo${list.length===1?'':'s'} recente${list.length===1?'':'s'}</strong><small>Armazenado apenas neste dispositivo</small></div>${list.length?'<button id="clearHistory19">Limpar</button>':''}</section>
  <div class="v19-history-list">${list.length?list.map((h,i)=>`<button data-history19 data-book="${esc18(h.book)}" data-chapter="${h.chapter}"><div class="v19-history-icon">📖</div><div><strong>${esc18(h.book)} ${h.chapter}</strong><small>${i===0?'Última leitura':`Lido há ${formatWhenV19(h.at)}`}</small></div><span>›</span></button>`).join(''):`<div class="empty"><div class="big">🕘</div><strong>Seu histórico está vazio</strong><p>Abra um capítulo da Bíblia para começar.</p></div>`}</div>`;
}

function highlighted19(){
  const rows=Object.entries(state.highlightsV19);
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Marca-textos</h1><p>Versículos destacados durante seus estudos.</p></div></div>
  <div class="v19-highlight-list">${rows.length?rows.map(([ref,color])=>{const parsed=parseRef19(ref),text=parsed?.text||'';return `<button class="hl-${color}" data-openhighlight19 data-book="${esc18(parsed?.book||'')}" data-chapter="${parsed?.chapter||1}" data-verse="${parsed?.verse||1}"><strong>${esc18(ref)}</strong><small>${esc18(text)}</small><span>›</span></button>`}).join(''):`<div class="empty"><div class="big">✨</div><strong>Nenhum marca-texto</strong><p>Selecione um versículo e escolha uma cor durante a leitura.</p></div>`}</div>`;
}

function smartReferenceCardV19(q){
  const ref=parseRef19(q); if(!ref)return '';
  const label=`${ref.book} ${ref.chapter}${ref.verse?':'+ref.verse+(ref.endVerse&&ref.endVerse!==ref.verse?'-'+ref.endVerse:''):''}`;
  return `<button class="v19-direct-ref" id="openSmartRef19"><span>📖</span><div><small>REFERÊNCIA RECONHECIDA</small><strong>Abrir ${esc18(label)}</strong></div><b>›</b></button>`;
}
function searchPage19(){
  const q=state.searchQueryV19||'';
  const results=searchAll18(q);
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Busca Bíblica</h1><p>Referências e palavras nos 31.098 versículos.</p></div></div>
  <div class="v18-global-search v19-search"><span>🔎</span><input class="field" id="globalSearch19" value="${esc18(q)}" placeholder="Jo 3:16, João 3 16-18, graça..."></div>
  <div class="v19-search-help"><span>Entende:</span><b>Jo 3:16</b><b>João 3 16</b><b>Sl 23</b><b>Rm 8:28-30</b></div>
  <div id="smartReference19">${smartReferenceCardV19(q)}</div>
  <div id="globalResults19">${searchResultsHtml18(results)}</div>`;
}

function bible19(){
  let html=bible18();
  const recent=state.readingHistoryV19.slice(0,3);
  const addon=`<section class="v19-bible-study-card"><div><span>BÍBLIA DE ESTUDO</span><strong>Leitura, seleção e marca-texto</strong><small>Recursos de estudo funcionando offline</small></div><div class="v19-bible-study-actions"><button data-route="history19">🕘 Histórico</button><button data-route="highlighted19">✨ Marca-textos</button></div>${recent.length?`<div class="v19-recent-row">${recent.map(h=>`<button data-history19 data-book="${esc18(h.book)}" data-chapter="${h.chapter}">${esc18(h.book)} ${h.chapter}</button>`).join('')}</div>`:''}</section>`;
  return html.replace('<section class="v18-source-card">',addon+'<section class="v18-source-card">');
}

function homeAddon19(){
  const highlights=Object.keys(state.highlightsV19).length, last=state.readingHistoryV19[0];
  return `<section class="section v19-home-card"><div class="v19-home-icon">✨</div><div><span>BÍBLIA DE ESTUDO 1.9</span><strong>Estude a Palavra do seu jeito</strong><small>${highlights} marca-texto${highlights===1?'':'s'}${last?` • última leitura: ${esc18(last.book)} ${last.chapter}`:''}</small></div><button data-route="history19">Abrir</button></section>`;
}

window.render=function(){
  if(state.route==='reader'){$('#app').innerHTML=reader19();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='bible'));window.bind();return;}
  if(state.route==='bible'){$('#app').innerHTML=bible19();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='bible'));window.bind();return;}
  if(state.route==='search'){$('#app').innerHTML=searchPage19();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return;}
  if(state.route==='history19'){$('#app').innerHTML=history19();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return;}
  if(state.route==='highlighted19'){$('#app').innerHTML=highlighted19();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return;}
  _renderV18();
  if(state.route==='home'){const app=$('#app');if(app&&!app.querySelector('.v19-home-card'))app.insertAdjacentHTML('afterbegin',homeAddon19());bindV19();}
};
window.bind=function(){_bindV18();bindV19();};

function openParsedV19(ref){
  if(!ref)return;
  state.book=ref.book;state.chapter=ref.chapter;state.pendingVerse18=ref.verse||null;
  state.pendingRangeV19=ref.verse&&ref.endVerse&&ref.endVerse>ref.verse?[ref.verse,ref.endVerse]:null;
  state.selectedVersesV19=[];state.studyVerseV19=null;nav('reader');
}
function chapterMoveV19(delta){
  const max=bookMeta18(state.book).chapters,next=Number(state.chapter)+delta;
  if(next<1||next>max)return;
  state.chapter=next;state.selectedVersesV19=[];state.studyVerseV19=null;window.render();scrollTo(0,0);
}
function noteV19(v){
  v=Number(v);const text=verseTextV19(v),ref=refV19(v),note=prompt(`Anotação • ${ref}`,'Minha aplicação:');
  if(note!==null&&note.trim()){state.notes.unshift({t:ref,x:`${text}\n${note.trim()}`});save();toast('Anotação salva 📝');}
}
function bindV19(){
  $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
  $$('[data-back]').forEach(e=>e.onclick=()=>history.length>1?history.back():nav('home'));

  const cs=$('#chapterSelect19'); if(cs)cs.onchange=()=>{state.chapter=Number(cs.value);state.selectedVersesV19=[];state.studyVerseV19=null;window.render();scrollTo(0,0);};
  $('#prevChapter19')?.addEventListener('click',()=>chapterMoveV19(-1));$('#prevChapterBottom19')?.addEventListener('click',()=>chapterMoveV19(-1));
  $('#nextChapter19')?.addEventListener('click',()=>chapterMoveV19(1));$('#nextChapterBottom19')?.addEventListener('click',()=>chapterMoveV19(1));

  $$('[data-select19]').forEach(b=>b.onclick=()=>toggleSelectV19(b.dataset.select19));
  $$('[data-study19]').forEach(b=>b.onclick=()=>{state.studyVerseV19=Number(b.dataset.study19);window.render();setTimeout(()=>document.querySelector('.v19-study-panel')?.scrollIntoView({behavior:'smooth',block:'start'}),50);});
  $('#closeStudy19')?.addEventListener('click',()=>{state.studyVerseV19=null;window.render();});
  $$('[data-fav19]').forEach(b=>b.onclick=()=>{const v=Number(b.dataset.fav19),r=refV19(v);toggleVerseFav18(r,verseTextV19(v));window.render();});
  $$('[data-note19]').forEach(b=>b.onclick=()=>noteV19(b.dataset.note19));
  $$('[data-copy19]').forEach(b=>b.onclick=()=>{const v=Number(b.dataset.copy19);copy18(`${refV19(v)} — ${verseTextV19(v)}`);});
  $$('[data-highlight19]').forEach(b=>b.onclick=()=>applyHighlightV19(b.dataset.highlight19));
  $('#copySelected19')?.addEventListener('click',()=>copy18(selectedTextV19()));
  $('#favSelected19')?.addEventListener('click',favoriteSelectionV19);
  $('#highlightSelected19')?.addEventListener('click',()=>document.getElementById('selectionPalette19')?.classList.toggle('show'));
  $('#clearSelected19')?.addEventListener('click',clearSelectionV19);

  $('#fontDown19')?.addEventListener('click',()=>{state.studyFontV19=Math.max(90,state.studyFontV19-5);saveStudyV19();window.render();});
  $('#fontUp19')?.addEventListener('click',()=>{state.studyFontV19=Math.min(125,state.studyFontV19+5);saveStudyV19();window.render();});

  $$('[data-related19]').forEach(b=>b.onclick=()=>{state.book=b.dataset.book;state.chapter=Number(b.dataset.chapter);state.pendingVerse18=Number(b.dataset.verse);state.selectedVersesV19=[];state.studyVerseV19=null;nav('reader');});
  $$('[data-history19]').forEach(b=>b.onclick=()=>{state.book=b.dataset.book;state.chapter=Number(b.dataset.chapter);state.selectedVersesV19=[];state.studyVerseV19=null;nav('reader');});
  $$('[data-openhighlight19]').forEach(b=>b.onclick=()=>{state.book=b.dataset.book;state.chapter=Number(b.dataset.chapter);state.pendingVerse18=Number(b.dataset.verse);nav('reader');});
  $('#clearHistory19')?.addEventListener('click',()=>{if(confirm('Limpar todo o histórico de leitura deste aparelho?')){state.readingHistoryV19=[];saveStudyV19();window.render();}});

  const gs=$('#globalSearch19');if(gs)gs.oninput=()=>{state.searchQueryV19=gs.value;state.searchQueryV18=gs.value;const card=$('#smartReference19');if(card)card.innerHTML=smartReferenceCardV19(gs.value);const results=$('#globalResults19');if(results)results.innerHTML=searchResultsHtml18(searchAll18(gs.value));bindSearchResults18();bindSmartRefV19();};
  bindSearchResults18();bindSmartRefV19();

  const bs=$('#v18BookSearch');if(bs){
    bs.placeholder='Livro ou referência: Jo 3:16, Sl 23...';
    bs.onkeydown=e=>{if(e.key==='Enter'){const ref=parseRef19(bs.value);if(ref){e.preventDefault();openParsedV19(ref);}}};
  }
  if(state.pendingRangeV19){const [a,b]=state.pendingRangeV19;state.selectedVersesV19=Array.from({length:b-a+1},(_,i)=>a+i);state.pendingRangeV19=null;setTimeout(()=>window.render(),20);return;}
}
function bindSmartRefV19(){
  const b=$('#openSmartRef19');if(b)b.onclick=()=>openParsedV19(parseRef19(state.searchQueryV19));
}

window.render();
