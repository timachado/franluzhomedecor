const _renderV111_UI = window.render;
const _bindV111_UI = window.bind;

state.ui112 = Object.assign({spacing:'normal',contrast:false,motion:true,haptic:true,keepAwake:false}, JSON.parse(localStorage.getItem('ebd-ui-v112') || '{}'));
state.focus112 = false;

function saveUi112(){localStorage.setItem('ebd-ui-v112',JSON.stringify(state.ui112));applyUi112()}
function native112(){return window.AndroidBridge||null}
function nativeVersion112(){try{return native112()?.appVersion?.()||'1.12.0'}catch(e){return '1.12.0'}}
function haptic112(){if(!state.ui112.haptic)return;try{native112()?.haptic?.()}catch(e){}}
function keepAwake112(on){try{native112()?.setKeepScreenOn?.(!!on)}catch(e){}}
function share112(text,title='Bíblia EBD'){
 if(!text)return toast('Nada para compartilhar');
 try{if(native112()?.shareText){native112().shareText(String(text),String(title));return}}catch(e){}
 if(navigator.share){navigator.share({title,text:String(text)}).catch(()=>{});return}
 copy18(String(text));toast('Texto copiado para compartilhar 📋');
}
function applyUi112(){
 const b=document.body;if(!b)return;
 b.classList.toggle('v112-spacing-compact',state.ui112.spacing==='compact');
 b.classList.toggle('v112-spacing-relaxed',state.ui112.spacing==='relaxed');
 b.classList.toggle('v112-contrast',!!state.ui112.contrast);
 b.classList.toggle('v112-reduce-motion',!state.ui112.motion);
 b.classList.toggle('v112-focus',!!state.focus112&&state.route==='reader');
 keepAwake112(!!state.ui112.keepAwake&&(state.route==='reader'||state.route==='hymn'));
}
function settings112(){
 const bibleFont=Math.max(90,Math.min(125,Number(state.studyFontV19||100))),harpaFont=Math.max(90,Math.min(135,Number(state.harpaFont191||100)));
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Aparência e leitura</h1><p>Ajustes salvos neste aparelho.</p></div></div>
 <section class="v112-device-card"><div>📱</div><div><span>APLICATIVO ANDROID</span><strong>Bíblia EBD ${esc18(nativeVersion112())}</strong><small>Conteúdo principal disponível offline</small></div><b>✓</b></section>
 <section class="v112-setting"><div class="v112-setting-head"><div><span>📖</span><div><strong>Tamanho da Bíblia</strong><small>Texto dos versículos</small></div></div><b>${bibleFont}%</b></div><div class="v112-scale-row">${[90,100,110,120,125].map(n=>`<button data-biblefont112="${n}" class="${bibleFont===n?'active':''}">${n}%</button>`).join('')}</div></section>
 <section class="v112-setting"><div class="v112-setting-head"><div><span>🎵</span><div><strong>Tamanho da Harpa</strong><small>Texto dos hinos</small></div></div><b>${harpaFont}%</b></div><div class="v112-scale-row">${[90,100,110,120,135].map(n=>`<button data-harpafont112="${n}" class="${harpaFont===n?'active':''}">${n}%</button>`).join('')}</div></section>
 <section class="v112-setting"><div class="v112-setting-head"><div><span>↕️</span><div><strong>Espaçamento da leitura</strong><small>Distância entre linhas e blocos</small></div></div></div><div class="v112-choice-row">${[['compact','Compacto'],['normal','Normal'],['relaxed','Confortável']].map(([k,t])=>`<button data-spacing112="${k}" class="${state.ui112.spacing===k?'active':''}">${t}</button>`).join('')}</div></section>
 <section class="v112-toggle-list">
  <button data-toggle112="contrast" class="${state.ui112.contrast?'on':''}"><span>◐</span><div><strong>Alto contraste</strong><small>Realça textos e divisórias.</small></div><i>${state.ui112.contrast?'ON':'OFF'}</i></button>
  <button data-toggle112="motion" class="${state.ui112.motion?'on':''}"><span>✨</span><div><strong>Animações suaves</strong><small>Desative se preferir transições imediatas.</small></div><i>${state.ui112.motion?'ON':'OFF'}</i></button>
  <button data-toggle112="haptic" class="${state.ui112.haptic?'on':''}"><span>📳</span><div><strong>Resposta tátil</strong><small>Pequeno toque ao usar botões no Android.</small></div><i>${state.ui112.haptic?'ON':'OFF'}</i></button>
  <button data-toggle112="keepAwake" class="${state.ui112.keepAwake?'on':''}"><span>💡</span><div><strong>Manter tela acesa</strong><small>Enquanto estiver lendo Bíblia ou Harpa.</small></div><i>${state.ui112.keepAwake?'ON':'OFF'}</i></button>
 </section>
 <section class="v112-tip"><span>🎯</span><div><strong>Modo Foco</strong><p>Dentro de qualquer capítulo, toque em <b>Foco</b> para esconder cabeçalho e navegação e usar a tela inteira para leitura.</p></div></section>`;
}
function homePolish112(){return `<section class="section v112-home-card"><div class="v112-home-icon">📱</div><div><span>LEITURA PERSONALIZADA</span><strong>Modo Foco e ajustes Android</strong><small>Fonte, espaçamento, contraste e tela acesa.</small></div><button data-route="settings112">Ajustar</button></section>`}
function injectReader112(){
 if(state.route!=='reader')return;
 const tools=document.querySelector('.v19-reader-tools');
 if(tools&&!document.getElementById('focusMode112'))tools.insertAdjacentHTML('beforeend',`<button id="focusMode112">${state.focus112?'✕ Sair do foco':'🎯 Foco'}</button>`);
 if(state.focus112&&!document.getElementById('focusExit112'))document.getElementById('app')?.insertAdjacentHTML('beforeend','<button id="focusExit112">✕ Sair do foco</button>');
 const sel=document.querySelector('.v19-selection-bar');if(sel&&!document.getElementById('shareSelected112'))sel.insertAdjacentHTML('beforeend','<button id="shareSelected112">↗️</button>');
}
function injectHymn112(){if(state.route!=='hymn')return;const bar=document.querySelector('.v191-reading-tools');if(bar&&!document.getElementById('shareHymn112'))bar.insertAdjacentHTML('beforeend','<button id="shareHymn112">↗️ Compartilhar</button>')}
function injectHome112(){if(state.route!=='home')return;const app=document.getElementById('app');if(app&&!app.querySelector('.v112-home-card'))app.insertAdjacentHTML('afterbegin',homePolish112())}
function installGlobalHaptic112(){if(window.__v112HapticBound)return;window.__v112HapticBound=true;document.addEventListener('click',e=>{if(e.target.closest('button'))haptic112()},{passive:true})}

window.render=function(){
 if(state.route==='settings112'){
  document.getElementById('app').innerHTML=settings112();document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));applyUi112();window.bind();return;
 }
 _renderV111_UI();applyUi112();injectHome112();injectReader112();injectHymn112();bindV112();
};
window.bind=function(){_bindV111_UI();bindV112()};
function bindV112(){
 document.querySelectorAll('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
 document.querySelectorAll('[data-biblefont112]').forEach(b=>b.onclick=()=>{state.studyFontV19=Number(b.dataset.biblefont112);saveStudyV19();window.render()});
 document.querySelectorAll('[data-harpafont112]').forEach(b=>b.onclick=()=>{state.harpaFont191=Number(b.dataset.harpafont112);saveHarpa191();window.render()});
 document.querySelectorAll('[data-spacing112]').forEach(b=>b.onclick=()=>{state.ui112.spacing=b.dataset.spacing112;saveUi112();window.render()});
 document.querySelectorAll('[data-toggle112]').forEach(b=>b.onclick=()=>{const k=b.dataset.toggle112;state.ui112[k]=!state.ui112[k];saveUi112();window.render()});
 document.getElementById('focusMode112')?.addEventListener('click',()=>{state.focus112=!state.focus112;applyUi112();window.render()});
 document.getElementById('focusExit112')?.addEventListener('click',()=>{state.focus112=false;applyUi112();window.render()});
 document.getElementById('shareSelected112')?.addEventListener('click',()=>share112(selectedTextV19(),'Passagem bíblica'));
 document.getElementById('shareHymn112')?.addEventListener('click',()=>{const h=harpaCatalogV18.find(x=>x.n===Number(state.hymn));if(h)share112(`Harpa Cristã ${h.n} — ${h.title}\n\n${lyric191(h.n)}`,'Harpa Cristã')});
}
window.__ebdNativeBack112=function(){if(state.focus112){state.focus112=false;applyUi112();window.render();return true}return false};
applyUi112();installGlobalHaptic112();window.render();
