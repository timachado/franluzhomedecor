// 1.15.1 — configuração segura do código privado + teste de conexão.
(function(){
  'use strict';

  const previousRender=window.render;
  const previousBind=window.bind;
  const ACCESS_KEY='biblia-ai-access-v115';
  const ENDPOINT=window.__EBD_AI_115__?.endpoint||'https://dwpcddiramxlhavdmmyn.supabase.co/functions/v1/biblia-ai';
  let editing=false;
  let checking=false;
  let checkedToken='';
  let connectionState='idle'; // idle | checking | valid | invalid | error
  let connectionMessage='';

  function toast1151(message){if(typeof window.toast==='function')window.toast(message)}
  function token1151(){return localStorage.getItem(ACCESS_KEY)||''}
  function esc1151(v=''){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}

  async function verify1151(value){
    const token=String(value||'').trim();
    if(token.length<16)return {ok:false,status:400,message:'O código precisa ter pelo menos 16 caracteres.'};
    try{
      const controller=new AbortController();
      const timeout=setTimeout(()=>controller.abort(),12000);
      const response=await fetch(ENDPOINT,{
        method:'POST',
        headers:{'Content-Type':'application/json','x-biblia-access':token},
        body:JSON.stringify({action:'check'}),
        signal:controller.signal
      });
      clearTimeout(timeout);
      let data={};try{data=await response.json()}catch(_){}
      if(response.ok&&data?.ok)return {ok:true,status:response.status,message:'Código confirmado pelo servidor.',model:data.model||''};
      return {ok:false,status:response.status,message:data?.message||'O servidor recusou este código.'};
    }catch(err){
      return {ok:false,status:0,message:err?.name==='AbortError'?'O servidor demorou para responder.':'Não foi possível verificar o servidor agora.'};
    }
  }

  async function autoCheck1151(){
    const value=token1151();
    if(!value||checking||checkedToken===value)return;
    checking=true;checkedToken=value;connectionState='checking';connectionMessage='Verificando código salvo…';patch1151();
    const result=await verify1151(value);
    checking=false;
    if(result.ok){connectionState='valid';connectionMessage=`Conexão autorizada${result.model?' • '+result.model:''}`;editing=false}
    else{connectionState=result.status===401?'invalid':'error';connectionMessage=result.message;editing=result.status===401}
    patch1151();
  }

  function statusHtml1151(hasToken){
    if(!hasToken)return '<span class="ai1151-dot off"></span><div><strong>IA ainda não autorizada neste aparelho</strong><small>Informe o mesmo valor salvo em BIBLIA_EBD_AI_ACCESS_TOKEN no Supabase.</small></div>';
    if(connectionState==='checking')return '<span class="ai1151-dot wait"></span><div><strong>Verificando conexão…</strong><small>Confirmando o código com o servidor sem consumir a IA.</small></div>';
    if(connectionState==='valid')return `<span class="ai1151-dot ok"></span><div><strong>Conexão privada autorizada</strong><small>${esc1151(connectionMessage)}</small></div>`;
    if(connectionState==='invalid')return `<span class="ai1151-dot bad"></span><div><strong>Código não confere com o servidor</strong><small>${esc1151(connectionMessage)} O digest SHA-256 mostrado no Supabase não é o código.</small></div>`;
    if(connectionState==='error')return `<span class="ai1151-dot bad"></span><div><strong>Não foi possível validar agora</strong><small>${esc1151(connectionMessage)}</small></div>`;
    return '<span class="ai1151-dot wait"></span><div><strong>Código salvo</strong><small>Toque em Verificar para confirmar a conexão.</small></div>';
  }

  function connectionCard1151(){
    const current=token1151();
    const showEditor=editing||!current||connectionState==='invalid';
    return `<section class="ai1151-connection" id="aiConnection1151">
      <div class="ai1151-status">${statusHtml1151(!!current)}</div>
      ${showEditor?`<div class="ai1151-editor"><label>${current?'Novo código privado':'Código privado da IA'}</label><div><input class="field" id="aiAccess1151" type="password" autocomplete="off" placeholder="Cole o valor original, não o SHA-256"><button class="btn btn-primary" id="testSaveAi1151">Testar e salvar</button></div><small>O teste apenas valida o código no servidor e não consome uma resposta da IA.</small></div>`:''}
      <div class="ai1151-actions">${current&&!showEditor?'<button id="verifyAi1151">✓ Verificar</button><button id="changeAi1151">✎ Alterar código</button>':''}${current?'<button class="danger" id="removeAi1151">Remover código</button>':''}</div>
    </section>`;
  }

  function patch1151(){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    document.querySelector('.ai115-access')?.remove();
    const compose=document.querySelector('.ai115-compose');
    if(!compose)return;
    document.getElementById('aiConnection1151')?.remove();
    const mode=compose.querySelector('.ai115-mode');
    if(mode)mode.insertAdjacentHTML('afterend',connectionCard1151());else compose.insertAdjacentHTML('afterbegin',connectionCard1151());

    const send=document.getElementById('sendAi115');
    if(send){
      const allowed=connectionState==='valid';
      send.disabled=!allowed||!!state.ai115?.busy;
      if(!allowed&&!state.ai115?.busy)send.title='Confirme primeiro o código privado da IA.';
    }
    bindPatch1151();
    if(token1151()&&connectionState==='idle')autoCheck1151();
  }

  function bindPatch1151(){
    const verify=document.getElementById('verifyAi1151');
    if(verify)verify.onclick=()=>{checkedToken='';connectionState='idle';autoCheck1151()};
    const change=document.getElementById('changeAi1151');
    if(change)change.onclick=()=>{editing=true;patch1151();setTimeout(()=>document.getElementById('aiAccess1151')?.focus(),50)};
    const remove=document.getElementById('removeAi1151');
    if(remove)remove.onclick=()=>{localStorage.removeItem(ACCESS_KEY);editing=true;checkedToken='';connectionState='idle';connectionMessage='';toast1151('Código removido deste aparelho.');patch1151()};
    const save=document.getElementById('testSaveAi1151');
    if(save)save.onclick=async()=>{
      const field=document.getElementById('aiAccess1151');
      const value=String(field?.value||'').trim();
      if(value.length<16){toast1151('Use um código de pelo menos 16 caracteres.');return}
      save.disabled=true;save.textContent='Testando…';
      const result=await verify1151(value);
      if(result.ok){
        localStorage.setItem(ACCESS_KEY,value);
        checkedToken=value;connectionState='valid';connectionMessage=`Conexão autorizada${result.model?' • '+result.model:''}`;editing=false;
        toast1151('Código confirmado e salvo ✅');
      }else{
        connectionState=result.status===401?'invalid':'error';connectionMessage=result.message;editing=true;
        toast1151(result.message);
      }
      patch1151();
    };
  }

  window.render=function(){previousRender();requestAnimationFrame(patch1151)};
  window.bind=function(){previousBind();bindPatch1151()};
  window.__EBD_AI_1151__=Object.freeze({verify:verify1151,remove:()=>localStorage.removeItem(ACCESS_KEY)});
  window.render();
})();
