(function(){
'use strict';
if(window.__EBD_OCR_SELECTION_1172__)return;
window.__EBD_OCR_SELECTION_1172__=true;

var ROOTS='[data-ocr-text],[data-ocr-result],[data-ocr-output],[data-ocr-overlay],#ocrText,#ocrResult,#ocrOutput,#ocrResults,.ocr-text,.ocr-result,.ocr-output,.ocr-results,.ocr-overlay,.ocr-recognized-text,.recognized-text,.text-recognition-result,.lens-text,[class*="ocr"],[id*="ocr"],[data-feature*="ocr"],[data-mode*="ocr"],[data-tool*="ocr"]';
var WORD='[data-ocr-word],.ocr-word,[data-word]';
var activeRoot=null, activeControl=null, dragRoot=null, dragAnchor=-1, manualText='', bar=null, hideTimer=0;

function clean(v){return String(v||'').replace(/\s+/g,' ').trim();}
function message(t){
  try{var e=document.getElementById('toast');if(e){e.textContent=t;e.classList.add('show');setTimeout(function(){e.classList.remove('show');},1700);}}catch(_){}
}
function controlText(c){
  try{var a=c.selectionStart,b=c.selectionEnd;return b>a?clean(c.value.slice(a,b)):'';}catch(_){return '';}
}
function selectedText(){
  if(manualText)return clean(manualText);
  if(activeControl){var c=controlText(activeControl);if(c)return c;}
  try{return clean(window.getSelection().toString());}catch(_){return '';}
}
function ensureBar(){
  if(bar&&bar.isConnected)return bar;
  bar=document.createElement('div');
  bar.id='ebdOcrSelectionBar1172';
  bar.className='ebd-ocr-selection-bar-1172';
  bar.setAttribute('role','toolbar');
  bar.setAttribute('aria-label','Ações do texto OCR selecionado');
  bar.innerHTML='<button data-a="copy">📋 <span>Copiar</span></button><button data-a="all">▣ <span>Tudo</span></button><button data-a="search">🔎 <span>Buscar</span></button><button data-a="share">↗ <span>Compartilhar</span></button><button data-a="clear" aria-label="Limpar seleção">✕</button>';
  bar.addEventListener('pointerdown',function(e){e.preventDefault();e.stopPropagation();});
  bar.addEventListener('click',function(e){
    var b=e.target.closest('[data-a]');if(!b)return;
    var a=b.getAttribute('data-a');
    if(a==='all'){selectAll();return;}
    if(a==='clear'){clearSelection();return;}
    var t=selectedText();if(!t){hideBar();return;}
    if(a==='copy'){copyText(t);return;}
    if(a==='search'){searchText(t);return;}
    if(a==='share'){shareText(t);}
  });
  document.body.appendChild(bar);
  return bar;
}
function showBar(root,control){
  activeRoot=root||activeRoot;activeControl=control||null;
  if(!selectedText()){hideBar();return;}
  clearTimeout(hideTimer);ensureBar().classList.add('is-visible');
}
function hideBar(delay){
  clearTimeout(hideTimer);
  var fn=function(){if(bar)bar.classList.remove('is-visible');};
  if(delay)hideTimer=setTimeout(fn,delay);else fn();
}
function clearWords(){
  document.querySelectorAll('.ebd-ocr-word-selected-1172').forEach(function(w){w.classList.remove('ebd-ocr-word-selected-1172');});
  manualText='';dragRoot=null;dragAnchor=-1;
}
function clearSelection(){
  clearWords();
  try{if(activeControl){var p=activeControl.selectionEnd||0;activeControl.setSelectionRange(p,p);}}catch(_){}
  try{window.getSelection().removeAllRanges();}catch(_){}
  activeControl=null;hideBar();
}
function selectAll(){
  clearWords();
  if(activeControl){
    try{activeControl.focus({preventScroll:true});activeControl.select();showBar(activeControl,activeControl);return;}catch(_){}
  }
  if(!activeRoot)return;
  var words=Array.from(activeRoot.querySelectorAll(WORD));
  if(words.length){
    words.forEach(function(w){w.classList.add('ebd-ocr-word-selected-1172');});
    manualText=clean(words.map(function(w){return w.textContent;}).join(' '));showBar(activeRoot,null);return;
  }
  try{
    var r=document.createRange();r.selectNodeContents(activeRoot);
    var s=window.getSelection();s.removeAllRanges();s.addRange(r);showBar(activeRoot,null);
  }catch(_){}
}
function copyText(t){
  try{
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){message('Texto OCR copiado.');}).catch(function(){fallbackCopy(t);});
      return;
    }
  }catch(_){}
  fallbackCopy(t);
}
function fallbackCopy(t){
  var x=document.createElement('textarea');x.value=t;x.setAttribute('readonly','');x.style.position='fixed';x.style.opacity='0';
  document.body.appendChild(x);x.select();try{document.execCommand('copy');message('Texto OCR copiado.');}catch(_){}x.remove();
}
function shareText(t){
  try{
    if(navigator.share){
      navigator.share({title:'Texto reconhecido — Bíblia EBD',text:t}).catch(function(e){if(!e||e.name!=='AbortError')fallbackCopy(t);});
      return;
    }
  }catch(_){}
  fallbackCopy(t);message('Texto copiado para compartilhar.');
}
function searchText(t){
  var q=t.length>220?t.slice(0,220):t;
  try{if(typeof state!=='undefined'&&state){state.globalQuery=q;state.searchQueryV19=q;}}catch(_){}
  try{if(typeof nav==='function'){nav('search');return;}}catch(_){}
  try{location.hash='#/search';if(typeof render==='function')render();}catch(_){}
}
function sameRootSelection(root,s){
  if(!root||!s||!s.rangeCount)return false;
  try{var n=s.getRangeAt(0).commonAncestorContainer;if(n.nodeType!==1)n=n.parentNode;return n===root||root.contains(n);}catch(_){return false;}
}
function applyWordRange(root,a,b){
  var words=Array.from(root.querySelectorAll(WORD)),lo=Math.max(0,Math.min(a,b)),hi=Math.min(words.length-1,Math.max(a,b));
  words.forEach(function(w,i){w.classList.toggle('ebd-ocr-word-selected-1172',i>=lo&&i<=hi);});
  manualText=clean(words.slice(lo,hi+1).map(function(w){return w.textContent;}).join(' '));
  activeRoot=root;activeControl=null;showBar(root,null);
}
function installWordDrag(root){
  if(root.dataset.ebdWordDrag1172==='1')return;root.dataset.ebdWordDrag1172='1';
  root.addEventListener('pointerdown',function(e){
    var w=e.target.closest(WORD);if(!w||!root.contains(w))return;
    var words=Array.from(root.querySelectorAll(WORD)),i=words.indexOf(w);if(i<0)return;
    e.preventDefault();clearWords();dragRoot=root;dragAnchor=i;applyWordRange(root,i,i);
    try{root.setPointerCapture(e.pointerId);}catch(_){}
  });
  root.addEventListener('pointermove',function(e){
    if(dragRoot!==root||dragAnchor<0)return;
    var w=document.elementFromPoint(e.clientX,e.clientY);w=w&&w.closest? w.closest(WORD):null;if(!w||!root.contains(w))return;
    var words=Array.from(root.querySelectorAll(WORD)),i=words.indexOf(w);if(i>=0){e.preventDefault();applyWordRange(root,dragAnchor,i);}
  });
  function end(e){if(dragRoot!==root)return;dragRoot=null;try{root.releasePointerCapture(e.pointerId);}catch(_){}if(manualText)showBar(root,null);}
  root.addEventListener('pointerup',end);root.addEventListener('pointercancel',end);
}
function installControl(c){
  if(!c||c.dataset.ebdOcrSelection1172==='1')return;c.dataset.ebdOcrSelection1172='1';c.classList.add('ebd-ocr-selectable-1172');
  function sync(){var t=controlText(c);if(t){manualText='';activeRoot=c;activeControl=c;showBar(c,c);}else if(activeControl===c)hideBar(160);}
  c.addEventListener('select',sync);c.addEventListener('keyup',sync);c.addEventListener('pointerup',function(){setTimeout(sync,0);});
}
function enhance(root){
  if(!root||root.nodeType!==1)return;
  if(root.matches('textarea,input[type="text"],input:not([type])')){installControl(root);return;}
  if(root.dataset.ebdOcrSelection1172==='1')return;
  root.dataset.ebdOcrSelection1172='1';root.classList.add('ebd-ocr-selectable-1172');root.style.webkitUserSelect='text';root.style.userSelect='text';
  root.querySelectorAll('textarea,input[type="text"],input:not([type])').forEach(installControl);installWordDrag(root);
}
function scan(scope){
  var base=scope&&scope.querySelectorAll?scope:document;
  try{base.querySelectorAll(ROOTS).forEach(function(n){var t=clean(n.textContent);if(t.length>1||n.querySelector(WORD)||n.matches('textarea,input'))enhance(n);});}catch(_){}
  try{if(base.matches&&base.matches(ROOTS))enhance(base);}catch(_){}
}
document.addEventListener('selectionchange',function(){
  if(manualText||dragRoot)return;
  var s=window.getSelection();if(!s||s.isCollapsed||!s.rangeCount){if(!activeControl)hideBar(160);return;}
  var roots=Array.from(document.querySelectorAll('[data-ebd-ocr-selection1172],[data-ebd-ocr-selection-1172],[data-ebd-ocr-selection]'));
  if(!roots.length)roots=Array.from(document.querySelectorAll('.ebd-ocr-selectable-1172'));
  var root=roots.find(function(r){return sameRootSelection(r,s);});
  if(root){activeRoot=root;activeControl=null;showBar(root,null);}else hideBar(160);
});
var observer=new MutationObserver(function(records){records.forEach(function(r){r.addedNodes.forEach(function(n){if(n.nodeType===1)scan(n);});});});
function start(){
  ensureBar();scan(document);observer.observe(document.documentElement,{childList:true,subtree:true});
  window.BibliaEBDOCRSelection={enhance:enhance,rescan:scan,getSelectedText:selectedText,selectAll:selectAll,clear:clearSelection,version:'1.17.2'};
  document.dispatchEvent(new CustomEvent('biblia-ebd:ocr-selection-ready',{detail:{version:'1.17.2'}}));
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();