// 1.15.5 — contexto contínuo da IA + correção real do tamanho de fonte da Bíblia.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;

  function ensureReaderCss1155(){
    if(document.getElementById('v1155ReaderCss'))return;
    const link=document.createElement('link');
    link.id='v1155ReaderCss';
    link.rel='stylesheet';
    link.href='v1155.css';
    document.head.appendChild(link);
  }

  function attach1154ContextPin(){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    const field=document.getElementById('aiQuestion115');
    if(!field||field.dataset.pin1154==='1')return;
    field.dataset.pin1154='1';
    field.addEventListener('input',event=>{
      const question=String(event.target?.value||'');
      const detector=window.__EBD_AI_1152__?.detectReference;
      const detected=typeof detector==='function'?detector(question):null;
      const ctx=state.ai115?.context;
      if(detected){
        // Nova referência digitada: libera o detector 1.15.2 para substituir o contexto.
        if(ctx?._study1154)state.ai115.context=null;
        return;
      }
      if(ctx?._auto1152&&Array.isArray(state.aiHistory115)&&state.aiHistory115.length){
        const pinned=Object.assign({},ctx,{_study1154:true});
        delete pinned._auto1152;
        state.ai115.context=pinned;
      }
    },true);
  }

  function readerFontFeedback1155(){
    if(typeof state==='undefined'||state.route!=='reader')return;
    const pct=Math.max(90,Math.min(125,Number(state.studyFontV19||100)));
    const down=document.getElementById('fontDown19');
    const up=document.getElementById('fontUp19');
    if(down)down.setAttribute('aria-label',`Diminuir tamanho da Bíblia. Atual ${pct}%`);
    if(up)up.setAttribute('aria-label',`Aumentar tamanho da Bíblia. Atual ${pct}%`);
  }

  function post1155(){
    ensureReaderCss1155();
    attach1154ContextPin();
    readerFontFeedback1155();
  }

  window.render=function(){previousRender();requestAnimationFrame(post1155)};
  window.bind=function(){previousBind();post1155()};
  window.__EBD_AI_1154_CONTEXT__=Object.freeze({attach:attach1154ContextPin});
  window.__EBD_READER_1155__=Object.freeze({ensureCss:ensureReaderCss1155});
  ensureReaderCss1155();
  window.render();
})();
