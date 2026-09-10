const _renderV17=window.render;
const _bindV17=window.bind;

const BIBLE_META_V18=[
['Gênesis','genesis',50],['Êxodo','exodus',40],['Levítico','leviticus',27],['Números','numbers',36],['Deuteronômio','deuteronomy',34],['Josué','joshua',24],['Juízes','judges',21],['Rute','ruth',4],['1 Samuel','i-samuel',31],['2 Samuel','ii-samuel',24],['1 Reis','i-kings',22],['2 Reis','ii-kings',25],['1 Crônicas','i-chronicles',29],['2 Crônicas','ii-chronicles',36],['Esdras','ezra',10],['Neemias','nehemiah',13],['Ester','esther',10],['Jó','job',42],['Salmos','psalms',150],['Provérbios','proverbs',31],['Eclesiastes','ecclesiastes',12],['Cânticos','song-of-solomon',8],['Isaías','isaiah',66],['Jeremias','jeremiah',52],['Lamentações','lamentations',5],['Ezequiel','ezekiel',48],['Daniel','daniel',12],['Oseias','hosea',14],['Joel','joel',3],['Amós','amos',9],['Obadias','obadiah',1],['Jonas','jonah',4],['Miqueias','micah',7],['Naum','nahum',3],['Habacuque','habakkuk',3],['Sofonias','zephaniah',3],['Ageu','haggai',2],['Zacarias','zechariah',14],['Malaquias','malachi',4],['Mateus','matthew',28],['Marcos','mark',16],['Lucas','luke',24],['João','john',21],['Atos','acts',28],['Romanos','romans',16],['1 Coríntios','i-corinthians',16],['2 Coríntios','ii-corinthians',13],['Gálatas','galatians',6],['Efésios','ephesians',6],['Filipenses','philippians',4],['Colossenses','colossians',4],['1 Tessalonicenses','i-thessalonians',5],['2 Tessalonicenses','ii-thessalonians',3],['1 Timóteo','i-timothy',6],['2 Timóteo','ii-timothy',4],['Tito','titus',3],['Filemom','philemon',1],['Hebreus','hebrews',13],['Tiago','james',5],['1 Pedro','i-peter',5],['2 Pedro','ii-peter',3],['1 João','i-john',5],['2 João','ii-john',1],['3 João','iii-john',1],['Judas','jude',1],['Apocalipse','revelation-of-john',22]
].map((x,i)=>({name:x[0],slug:x[1],chapters:x[2],testament:i<39?'Antigo Testamento':'Novo Testamento'}));

const ALIASES_V18={
'gn':'Gênesis','gen':'Gênesis','genesis':'Gênesis','ex':'Êxodo','exo':'Êxodo','exodo':'Êxodo','lv':'Levítico','lev':'Levítico','levitico':'Levítico','nm':'Números','num':'Números','numeros':'Números','dt':'Deuteronômio','deut':'Deuteronômio','deuteronomio':'Deuteronômio','js':'Josué','jos':'Josué','josue':'Josué','jz':'Juízes','juizes':'Juízes','rt':'Rute','rute':'Rute','1sm':'1 Samuel','1samuel':'1 Samuel','2sm':'2 Samuel','2samuel':'2 Samuel','1rs':'1 Reis','1reis':'1 Reis','2rs':'2 Reis','2reis':'2 Reis','1cr':'1 Crônicas','1cronicas':'1 Crônicas','2cr':'2 Crônicas','2cronicas':'2 Crônicas','ed':'Esdras','edr':'Esdras','esdras':'Esdras','ne':'Neemias','nee':'Neemias','neemias':'Neemias','et':'Ester','ester':'Ester','jo':'Jó','job':'Jó','sl':'Salmos','sal':'Salmos','salmo':'Salmos','salmos':'Salmos','pv':'Provérbios','proverbios':'Provérbios','ec':'Eclesiastes','eclesiastes':'Eclesiastes','ct':'Cânticos','canticos':'Cânticos','is':'Isaías','isa':'Isaías','isaias':'Isaías','jr':'Jeremias','jer':'Jeremias','jeremias':'Jeremias','lm':'Lamentações','lamentacoes':'Lamentações','ez':'Ezequiel','eze':'Ezequiel','ezequiel':'Ezequiel','dn':'Daniel','dan':'Daniel','daniel':'Daniel','os':'Oseias','oseias':'Oseias','jl':'Joel','joel':'Joel','am':'Amós','amos':'Amós','ob':'Obadias','obadias':'Obadias','jn':'Jonas','jonas':'Jonas','mq':'Miqueias','miqueias':'Miqueias','na':'Naum','naum':'Naum','hc':'Habacuque','habacuque':'Habacuque','sf':'Sofonias','sofonias':'Sofonias','ag':'Ageu','ageu':'Ageu','zc':'Zacarias','zacarias':'Zacarias','ml':'Malaquias','malaquias':'Malaquias','mt':'Mateus','mateus':'Mateus','mc':'Marcos','marcos':'Marcos','lc':'Lucas','lucas':'Lucas','joao':'João','at':'Atos','atos':'Atos','rm':'Romanos','rom':'Romanos','romanos':'Romanos','1co':'1 Coríntios','1corintios':'1 Coríntios','2co':'2 Coríntios','2corintios':'2 Coríntios','gl':'Gálatas','galatas':'Gálatas','ef':'Efésios','efesios':'Efésios','fp':'Filipenses','filipenses':'Filipenses','cl':'Colossenses','colossenses':'Colossenses','1ts':'1 Tessalonicenses','1tessalonicenses':'1 Tessalonicenses','2ts':'2 Tessalonicenses','2tessalonicenses':'2 Tessalonicenses','1tm':'1 Timóteo','1timoteo':'1 Timóteo','2tm':'2 Timóteo','2timoteo':'2 Timóteo','tt':'Tito','tito':'Tito','fm':'Filemom','filemom':'Filemom','hb':'Hebreus','hebreus':'Hebreus','tg':'Tiago','tiago':'Tiago','1pe':'1 Pedro','1pedro':'1 Pedro','2pe':'2 Pedro','2pedro':'2 Pedro','1jo':'1 João','1joao':'1 João','2jo':'2 João','2joao':'2 João','3jo':'3 João','3joao':'3 João','jd':'Judas','judas':'Judas','ap':'Apocalipse','apo':'Apocalipse','apocalipse':'Apocalipse'
};

const bibleDataV18=window.BIBLE_DATA_V18;
const harpaCatalogV18=Array.isArray(window.HARPA_CATALOG_V18)?window.HARPA_CATALOG_V18:[];
state.hymnFavsV18=JSON.parse(localStorage.getItem('ebd-hymn-favs-v18')||'[]');
state.harpaQueryV18='';
state.harpaLimitV18=80;
state.bibleSearchV18='';
state.searchQueryV18=state.globalQuery||'';
let bibleSearchIndexV18=null;
let searchTimerV18=null;

function norm18(s=''){return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim()}
function esc18(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function dataReady18(){return !!(bibleDataV18&&Array.isArray(bibleDataV18.books)&&bibleDataV18.books.length===66)}
function bookMeta18(name){return BIBLE_META_V18.find(b=>b.name===name)||BIBLE_META_V18[0]}
function bookData18(name){return dataReady18()?bibleDataV18.books.find(b=>b.name===name):null}
function chapterVerses18(name,chapter){const b=bookData18(name);return b?.chapters?.[Number(chapter)-1]||[]}
function saveHymnFavs18(){localStorage.setItem('ebd-hymn-favs-v18',JSON.stringify(state.hymnFavsV18))}
function isHymnFav18(n){return state.hymnFavsV18.includes(Number(n))}
function toggleHymnFav18(n){n=Number(n);state.hymnFavsV18=isHymnFav18(n)?state.hymnFavsV18.filter(x=>x!==n):[...state.hymnFavsV18,n];saveHymnFavs18();toast(isHymnFav18(n)?'Hino salvo nos favoritos ❤️':'Hino removido dos favoritos')}
function isVerseFav18(ref){return state.favs.some(f=>f.r===ref)}
function toggleVerseFav18(ref,text){const i=state.favs.findIndex(f=>f.r===ref);if(i>=0){state.favs.splice(i,1);toast('Versículo removido dos favoritos')}else{state.favs.unshift({r:ref,t:text});toast('Versículo salvo ❤️')}save()}
function copy18(text){if(navigator.clipboard?.writeText){navigator.clipboard.writeText(text).then(()=>toast('Copiado 📋')).catch(()=>fallbackCopy18(text))}else fallbackCopy18(text)}
function fallbackCopy18(text){const t=document.createElement('textarea');t.value=text;document.body.appendChild(t);t.select();try{document.execCommand('copy');toast('Copiado 📋')}catch(e){toast('Não foi possível copiar')}t.remove()}
function findBook18(raw){const n=norm18(raw).replace(/[.\s]+/g,' ').trim();const compact=n.replace(/\s/g,'');if(ALIASES_V18[compact])return ALIASES_V18[compact];const byName=BIBLE_META_V18.find(b=>norm18(b.name)===n||norm18(b.name).replace(/\s/g,'')===compact);return byName?.name||null}
function parseRef18(q){const clean=String(q||'').trim().replace(/\s*:\s*/g,':');const m=clean.match(/^(.+?)\s+(\d+)(?::(\d+))?$/);if(!m)return null;const book=findBook18(m[1]);if(!book)return null;const meta=bookMeta18(book),chapter=Number(m[2]),verse=m[3]?Number(m[3]):null;if(chapter<1||chapter>meta.chapters)return null;const vs=chapterVerses18(book,chapter);if(verse!==null&&(verse<1||verse>vs.length))return null;return {book,chapter,verse,text:verse?vs[verse-1]:null}}

function bible18(){
 const q=norm18(state.bibleSearchV18||'');
 const list=BIBLE_META_V18.filter(b=>!q||norm18(b.name).includes(q));
 const at=list.filter(b=>b.testament==='Antigo Testamento'),nt=list.filter(b=>b.testament==='Novo Testamento');
 const cards=arr=>arr.map(b=>`<button class="v18-book" data-book18="${b.name}"><span>📖</span><div><strong>${b.name}</strong><small>${b.chapters} capítulo${b.chapters>1?'s':''}</small></div><b>›</b></button>`).join('');
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Bíblia Sagrada</h1><p>66 livros completos disponíveis offline.</p></div></div>
 <section class="v18-source-card"><div>📖</div><div><span>JOÃO FERREIRA DE ALMEIDA</span><strong>31.098 versículos • 1.189 capítulos</strong><small>Texto de domínio público • armazenado no aplicativo</small></div><button data-route="contentInfo">ⓘ</button></section>
 <div class="v18-bible-search"><span>🔎</span><input class="field" id="v18BookSearch" value="${esc18(state.bibleSearchV18||'')}" placeholder="Livro ou referência, ex.: João 3:16"></div>
 <div id="v18ReferenceHit"></div>
 <div class="subhead">Antigo Testamento • 39 livros</div><div class="v18-books">${cards(at)}</div>
 <div class="subhead">Novo Testamento • 27 livros</div><div class="v18-books">${cards(nt)}</div>`;
}

function reader18(){
 const meta=bookMeta18(state.book);if(!BIBLE_META_V18.some(b=>b.name===state.book))state.book='Gênesis';state.chapter=Math.max(1,Math.min(Number(state.chapter||1),bookMeta18(state.book).chapters));
 const verses=chapterVerses18(state.book,state.chapter),max=bookMeta18(state.book).chapters;
 if(!dataReady18())return `<div class="pagehead"><button class="back" data-route="bible">‹</button><div><h1>${state.book} ${state.chapter}</h1><p>Base bíblica indisponível nesta compilação.</p></div></div><div class="v18-error">⚠️ O arquivo da Bíblia completa não foi empacotado. Instale novamente a versão 1.8.0 oficial.</div>`;
 return `<div class="reader-nav v18-reader-nav"><button id="prevChapter18" ${state.chapter<=1?'disabled':''}>‹</button><select class="field" id="chapterSelect18">${Array.from({length:max},(_,i)=>`<option value="${i+1}" ${i+1===state.chapter?'selected':''}>${state.book} ${i+1}</option>`).join('')}</select><button id="nextChapter18" ${state.chapter>=max?'disabled':''}>›</button></div>
 <section class="v18-chapter-head"><span>LEITURA BÍBLICA</span><h1>${state.book} ${state.chapter}</h1><p>${verses.length} versículos • Almeida em domínio público</p></section>
 <div class="v18-reader-tools"><button data-route="search">🔎 Buscar</button><button id="copyChapterRef18">🔗 Copiar referência</button><button data-route="notes">📝 Anotações</button></div>
 <article class="v18-verses">${verses.map((text,i)=>{const ref=`${state.book} ${state.chapter}:${i+1}`,fav=isVerseFav18(ref);return `<section class="v18-verse" id="v18verse-${i+1}"><button class="v18-vnum" data-copyverse18="${i+1}">${i+1}</button><p>${esc18(text)}</p><div class="v18-verse-actions"><button data-fav18="${i+1}" class="${fav?'active':''}">${fav?'❤️':'🤍'} Favoritar</button><button data-note18="${i+1}">📝 Anotar</button><button data-copyverse18="${i+1}">📋 Copiar</button></div></section>`}).join('')}</article>
 <div class="v18-reader-bottom"><button id="prevChapterBottom18" ${state.chapter<=1?'disabled':''}>‹ Capítulo anterior</button><button id="nextChapterBottom18" ${state.chapter>=max?'disabled':''}>Próximo capítulo ›</button></div>`;
}

function harpa18(){
 const q=norm18(state.harpaQueryV18||'');
 let list=harpaCatalogV18.filter(h=>!q||String(h.n).includes(q)||norm18(h.title).includes(q));
 const total=list.length,show=q?list.slice(0,150):list.slice(0,state.harpaLimitV18);
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Harpa Cristã</h1><p>Catálogo dos 640 hinos, busca e favoritos.</p></div></div>
 <section class="v18-harpa-hero"><div>🎵</div><div><span>CATÁLOGO COMPLETO</span><h2>640 hinos indexados</h2><p>Número e título disponíveis offline.</p></div></section>
 <div class="v18-legal-note">ℹ️ As letras integrais não são distribuídas nesta compilação até haver autorização/licenciamento inequívoco para uso no produto final.</div>
 <div class="v18-harpa-search"><span>🔎</span><input class="field" id="harpaSearch18" value="${esc18(state.harpaQueryV18||'')}" placeholder="Número ou título do hino..."></div>
 <div class="v18-harpa-summary"><span>${total} resultado${total===1?'':'s'}</span><button id="hymnFavFilter18">❤️ ${state.hymnFavsV18.length} favoritos</button></div>
 <div id="harpaList18" class="v18-hymn-list">${hymnRows18(show)}</div>${!q&&state.harpaLimitV18<list.length?`<button class="v18-load-more" id="loadMoreHarpa18">Carregar mais hinos (${Math.min(80,list.length-state.harpaLimitV18)})</button>`:''}`;
}
function hymnRows18(list){return list.map(h=>`<button class="v18-hymn-row" data-hymn18="${h.n}"><div class="v18-hymn-num">${h.n}</div><div><strong>${esc18(h.title)}</strong><small>Harpa Cristã • Hino ${h.n}</small></div><span>${isHymnFav18(h.n)?'❤️':'›'}</span></button>`).join('')||`<div class="empty"><div class="big">🎵</div><strong>Nenhum hino encontrado</strong><p>Tente outro número ou título.</p></div>`}
function hymnDetail18(){const h=harpaCatalogV18.find(x=>x.n===Number(state.hymn))||harpaCatalogV18[0];if(!h)return harpa18();return `<div class="pagehead"><button class="back" data-route="harpa">‹</button><div><h1>Hino ${h.n}</h1><p>Harpa Cristã</p></div></div><section class="v18-hymn-detail"><div class="v18-hymn-big">${h.n}</div><span>HARPA CRISTÃ</span><h1>${esc18(h.title)}</h1><button class="btn btn-primary" id="favHymn18">${isHymnFav18(h.n)?'❤️ Favoritado':'🤍 Adicionar aos favoritos'}</button></section><section class="v18-license-panel"><strong>📜 Sobre a letra deste hino</strong><p>O número e o título fazem parte do catálogo offline. A letra completa não foi incorporada nesta versão de produção porque a Bíblia EBD só distribuirá textos musicais com autorização ou licença claramente válida para redistribuição.</p><small>Isso não impede a busca, organização e favoritos dos 640 hinos.</small></section>`}

function buildBibleIndex18(){
 if(bibleSearchIndexV18||!dataReady18())return bibleSearchIndexV18||[];
 bibleSearchIndexV18=[];bibleDataV18.books.forEach(b=>b.chapters.forEach((vs,ci)=>vs.forEach((text,vi)=>bibleSearchIndexV18.push({book:b.name,chapter:ci+1,verse:vi+1,text,norm:norm18(text)}))));return bibleSearchIndexV18;
}
function searchBible18(q,limit=70){const n=norm18(q);if(n.length<2)return [];const idx=buildBibleIndex18(),out=[];for(const v of idx){if(v.norm.includes(n)){out.push(v);if(out.length>=limit)break}}return out}
function searchAll18(q){
 const text=String(q||'').trim(),n=norm18(text),out=[];if(!text)return out;
 const ref=parseRef18(text);if(ref){if(ref.verse)out.push({type:'bible',icon:'📖',title:`${ref.book} ${ref.chapter}:${ref.verse}`,sub:ref.text,book:ref.book,chapter:ref.chapter,verse:ref.verse});else out.push({type:'chapter',icon:'📖',title:`${ref.book} ${ref.chapter}`,sub:'Abrir capítulo completo',book:ref.book,chapter:ref.chapter})}
 if(n.length>=2)searchBible18(text,55).forEach(v=>{if(!out.some(x=>x.type==='bible'&&x.book===v.book&&x.chapter===v.chapter&&x.verse===v.verse))out.push({type:'bible',icon:'📖',title:`${v.book} ${v.chapter}:${v.verse}`,sub:v.text,book:v.book,chapter:v.chapter,verse:v.verse})});
 if(n.length>=2)magazineLibrary.filter(m=>norm18(`${m.title} ${m.subtitle} ${m.audience} ${m.edition}`).includes(n)).slice(0,8).forEach(m=>out.push({type:'mag',icon:'📚',title:m.title,sub:`${m.quarter} ${m.year} • ${m.edition}`,id:m.id}));
 if(n.length>=2)harpaCatalogV18.filter(h=>String(h.n)===n||norm18(h.title).includes(n)).slice(0,10).forEach(h=>out.push({type:'hymn',icon:'🎵',title:`Hino ${h.n} • ${h.title}`,sub:'Harpa Cristã',n:h.n}));
 if(n.length>=2)Object.entries(dict).filter(([k,d])=>norm18(`${k} ${d.title} ${d.def}`).includes(n)).forEach(([k,d])=>out.push({type:'dict',icon:'📘',title:d.title,sub:d.def,key:k}));
 return out.slice(0,80);
}
function searchPage18(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Busca Global</h1><p>Pesquise nos 31.098 versículos, revistas, Harpa e dicionário.</p></div></div><div class="v18-global-search"><span>🔎</span><input class="field" id="globalSearch18" value="${esc18(state.searchQueryV18||'')}" placeholder="Ex.: João 3:16, graça, esperança..."></div><div class="v18-search-chips"><span>📖 31.098 versículos</span><span>🎵 640 hinos</span><span>📚 Revistas EBD</span></div><div id="globalResults18">${searchResultsHtml18(searchAll18(state.searchQueryV18))}</div>`}
function searchResultsHtml18(results){if(!(state.searchQueryV18||'').trim())return `<div class="empty v18-search-empty"><div class="big">🔎</div><strong>Encontre uma passagem em segundos</strong><p>Você também pode digitar uma referência direta como “Apocalipse 22:21”.</p></div>`;if(!results.length)return `<div class="empty"><div class="big">📭</div><strong>Nenhum resultado</strong><p>Confira a grafia ou tente uma palavra menor.</p></div>`;return `<div class="v18-results">${results.map(r=>`<button class="v18-result" data-result18="${r.type}" ${r.book?`data-book="${r.book}" data-chapter="${r.chapter}"`:''} ${r.verse?`data-verse="${r.verse}"`:''} ${r.id?`data-mag="${r.id}"`:''} ${r.n?`data-hymn="${r.n}"`:''} ${r.key?`data-key="${esc18(r.key)}"`:''}><span>${r.icon}</span><div><strong>${esc18(r.title)}</strong><small>${esc18(r.sub)}</small></div><b>›</b></button>`).join('')}</div>`}

function contentInfo18(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Fontes e Licenças</h1><p>Transparência do conteúdo da Bíblia EBD.</p></div></div><section class="v18-info-card"><span>📖</span><div><strong>Bíblia • João Ferreira de Almeida</strong><p>66 livros • 1.189 capítulos • 31.098 versículos.</p><small>Corpus: pd-text-corpus / seven1m open-bibles. Texto português identificado pela fonte como domínio público.</small></div></section><section class="v18-info-card"><span>🎵</span><div><strong>Harpa Cristã • catálogo</strong><p>640 números e títulos indexados para busca e favoritos.</p><small>A Bíblia EBD não inclui letras integrais nesta compilação. Letras serão adicionadas somente com autorização/licenciamento apropriado.</small></div></section><section class="v18-info-card"><span>📚</span><div><strong>Revistas EBD</strong><p>Conteúdo demonstrativo/original da Bíblia EBD.</p><small>Revistas comerciais de terceiros só serão distribuídas mediante autorização.</small></div></section>`}

function homeBadge18(){return `<section class="section v18-production"><div class="v18-production-icon">📖</div><div><span>BASE BÍBLICA OFFLINE</span><strong>66 livros completos</strong><small>1.189 capítulos • 31.098 versículos • Almeida</small></div><button data-route="bible">Abrir</button></section>`}

window.render=function(){
 if(state.route==='bible'){$('#app').innerHTML=bible18();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='bible'));window.bind();return}
 if(state.route==='reader'){$('#app').innerHTML=reader18();$$('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='bible'));window.bind();return}
 if(state.route==='harpa'){$('#app').innerHTML=harpa18();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='hymn'){$('#app').innerHTML=hymnDetail18();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='search'){$('#app').innerHTML=searchPage18();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='contentInfo'){$('#app').innerHTML=contentInfo18();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 _renderV17();
 if(state.route==='home'){const app=$('#app');if(app&&!app.querySelector('.v18-production'))app.insertAdjacentHTML('afterbegin',homeBadge18());bindV18()}
};
window.bind=function(){_bindV17();bindV18()};
function bindV18(){
 $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
 $$('[data-back]').forEach(e=>e.onclick=()=>history.length>1?history.back():nav('home'));
 $$('[data-book18]').forEach(b=>b.onclick=()=>{state.book=b.dataset.book18;state.chapter=1;nav('reader')});
 const bs=$('#v18BookSearch');if(bs)bs.oninput=()=>{state.bibleSearchV18=bs.value;const ref=parseRef18(bs.value);const hit=$('#v18ReferenceHit');if(hit)hit.innerHTML=ref?`<button class="v18-ref-hit" id="openRef18">📖 Abrir ${ref.book} ${ref.chapter}${ref.verse?':'+ref.verse:''}<span>›</span></button>`:'';$('#openRef18')?.addEventListener('click',()=>{state.book=ref.book;state.chapter=ref.chapter;state.pendingVerse18=ref.verse||null;nav('reader')});const q=norm18(bs.value);$$('.v18-book').forEach(el=>el.style.display=!q||norm18(el.textContent).includes(q)?'flex':'none')};
 const cs=$('#chapterSelect18');if(cs)cs.onchange=()=>{state.chapter=Number(cs.value);window.render();scrollTo(0,0)};
 const prev=()=>{if(state.chapter>1){state.chapter--;window.render();scrollTo(0,0)}};const next=()=>{if(state.chapter<bookMeta18(state.book).chapters){state.chapter++;window.render();scrollTo(0,0)}};
 $('#prevChapter18')?.addEventListener('click',prev);$('#prevChapterBottom18')?.addEventListener('click',prev);$('#nextChapter18')?.addEventListener('click',next);$('#nextChapterBottom18')?.addEventListener('click',next);
 $$('[data-fav18]').forEach(b=>b.onclick=()=>{const v=Number(b.dataset.fav18),text=chapterVerses18(state.book,state.chapter)[v-1],ref=`${state.book} ${state.chapter}:${v}`;toggleVerseFav18(ref,text);window.render()});
 $$('[data-note18]').forEach(b=>b.onclick=()=>{const v=Number(b.dataset.note18),text=chapterVerses18(state.book,state.chapter)[v-1],ref=`${state.book} ${state.chapter}:${v}`,note=prompt(`Anotação • ${ref}`,'Minha aplicação:');if(note!==null){state.notes.unshift({t:ref,x:`${text}\n${note}`});save();toast('Anotação salva 📝')}});
 $$('[data-copyverse18]').forEach(b=>b.onclick=()=>{const v=Number(b.dataset.copyverse18),text=chapterVerses18(state.book,state.chapter)[v-1];copy18(`${state.book} ${state.chapter}:${v} — ${text}`)});
 $('#copyChapterRef18')?.addEventListener('click',()=>copy18(`${state.book} ${state.chapter}`));
 if(state.pendingVerse18){setTimeout(()=>{document.getElementById(`v18verse-${state.pendingVerse18}`)?.scrollIntoView({behavior:'smooth',block:'center'});state.pendingVerse18=null},80)}
 const hs=$('#harpaSearch18');if(hs)hs.oninput=()=>{state.harpaQueryV18=hs.value;state.harpaLimitV18=80;window.render()};
 $$('[data-hymn18]').forEach(b=>b.onclick=()=>{state.hymn=Number(b.dataset.hymn18);nav('hymn')});
 $('#loadMoreHarpa18')?.addEventListener('click',()=>{state.harpaLimitV18+=80;window.render()});
 $('#hymnFavFilter18')?.addEventListener('click',()=>{const favs=harpaCatalogV18.filter(h=>isHymnFav18(h.n));$('#harpaList18').innerHTML=hymnRows18(favs);$$('[data-hymn18]').forEach(b=>b.onclick=()=>{state.hymn=Number(b.dataset.hymn18);nav('hymn')})});
 $('#favHymn18')?.addEventListener('click',()=>{toggleHymnFav18(state.hymn);window.render()});
 const gs=$('#globalSearch18');if(gs)gs.oninput=()=>{state.searchQueryV18=gs.value;clearTimeout(searchTimerV18);const box=$('#globalResults18');if(box)box.innerHTML='<div class="v18-searching">🔎 Pesquisando na Bíblia...</div>';searchTimerV18=setTimeout(()=>{if(box)box.innerHTML=searchResultsHtml18(searchAll18(state.searchQueryV18));bindSearchResults18()},220)};
 bindSearchResults18();
}
function bindSearchResults18(){$$('[data-result18]').forEach(b=>b.onclick=()=>{const type=b.dataset.result18;if(type==='bible'||type==='chapter'){state.book=b.dataset.book;state.chapter=Number(b.dataset.chapter);state.pendingVerse18=b.dataset.verse?Number(b.dataset.verse):null;nav('reader')}else if(type==='mag'){state.magazineId=b.dataset.mag;nav('magazine')}else if(type==='hymn'){state.hymn=Number(b.dataset.hymn);nav('hymn')}else if(type==='dict'){state.globalQuery=b.dataset.key;nav('dictionary')}})}

if(!dataReady18())console.error('Bíblia EBD 1.8.0: corpus bíblico completo ausente.');
window.render();
