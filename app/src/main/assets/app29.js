// 1.15.4 — fixa o contexto atual em follow-ups, mas permite trocar ao digitar nova referência.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;

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

  window.render=function(){previousRender();requestAnimationFrame(attach1154ContextPin)};
  window.bind=function(){previousBind();attach1154ContextPin()};
  window.__EBD_AI_1154_CONTEXT__=Object.freeze({attach:attach1154ContextPin});
  window.render();
})();
