// 1.15.3 — leitura confortável da IA: fonte ajustável + markdown simples.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const KEY='ebd-ai-text-size-v1153';
  const LEVELS=['small','normal','large'];
  let level=Number(localStorage.getItem(KEY)||1);
  if(!Number.isInteger(level)||level<0||level>2)level=1;

  function applySize1153(){
    const root=document.documentElement;
    LEVELS.forEach(x=>root.classList.remove('ai1153-'+x));
    root.classList.add('ai1153-'+LEVELS[level]);
  }
  function pct1153(){return ['90%','100%','118%'][level]}
  function readerBar1153(){
    return `<section class="ai1153-readerbar" id="aiReaderBar1153"><div class="label"><span>Aa</span><div><strong>Tamanho da leitura</strong><small>Ajuste o texto das respostas da IA</small></div></div><button id="aiFontMinus1153" aria-label="Diminuir texto">A−</button><span class="pct" id="aiFontPct1153">${pct1153()}</span><button id="aiFontPlus1153" aria-label="Aumentar texto">A+</button></section>`;
  }
  function setLevel1153(next){
    level=Math.max(0,Math.min(2,next));
    localStorage.setItem(KEY,String(level));
    applySize1153();
    const pct=document.getElementById('aiFontPct1153');if(pct)pct.textContent=pct1153();
  }
  function enhanceMarkdown1153(){
    document.querySelectorAll('.ai115-msg.assistant .ai115-bubble p').forEach(p=>{
      if(p.dataset.read1153==='1')return;
      let html=p.innerHTML;
      html=html.replace(/(^|<br>\s*<br>)\s*#{2,3}\s*([^<]+)/g,'$1<span class="ai1153-heading">$2</span>');
      html=html.replace(/(^|<br>)\s*&gt;\s*([^<]+)/g,'$1<span class="ai1153-quote">$2</span>');
      p.innerHTML=html;
      p.dataset.read1153='1';
    });
  }
  function patch1153(){
    applySize1153();
    if(typeof state==='undefined'||state.route!=='ai115')return;
    const conversation=document.getElementById('aiConversation115');
    if(conversation&&!document.getElementById('aiReaderBar1153'))conversation.insertAdjacentHTML('beforebegin',readerBar1153());
    const minus=document.getElementById('aiFontMinus1153');if(minus)minus.onclick=()=>setLevel1153(level-1);
    const plus=document.getElementById('aiFontPlus1153');if(plus)plus.onclick=()=>setLevel1153(level+1);
    enhanceMarkdown1153();
  }
  window.render=function(){previousRender();requestAnimationFrame(patch1153)};
  window.bind=function(){previousBind();patch1153()};
  window.__EBD_AI_1153__=Object.freeze({getLevel:()=>level,setLevel:setLevel1153});
  applySize1153();
  window.render();
})();
