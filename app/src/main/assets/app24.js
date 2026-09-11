// 1.15.0 — Assistente Bíblia EBD: interface contextual + cliente de IA seguro.
(function(){
  'use strict';

  const oldRender115=window.render;
  const oldBind115=window.bind;
  const AI_ENDPOINT_115='https://dwpcddiramxlhavdmmyn.supabase.co/functions/v1/biblia-ai';
  const AI_HISTORY_KEY_115='ebd-ai-history-v115';
  const AI_ACCESS_KEY_115='biblia-ai-access-v115'; // fora do backup ebd-* de propósito
  const MAX_HISTORY_115=18;

  state.ai115=Object.assign({action:'ask',question:'',busy:false,context:null},state.ai115||{});
  state.aiHistory115=safeJson115(localStorage.getItem(AI_HISTORY_KEY_115),[]);
  if(!Array.isArray(state.aiHistory115))state.aiHistory115=[];

  function safeJson115(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}}
  function esc115(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function textHtml115(s=''){return esc115(s).replace(/\n/g,'<br>')}
  function toast115(s){if(typeof toast==='function')toast(s)}
  function role115(){return state.profileV16?.role||state.userMode||'Aluno'}
  function saveHistory115(){
    state.aiHistory115=state.aiHistory115.slice(-MAX_HISTORY_115);
    try{localStorage.setItem(AI_HISTORY_KEY_115,JSON.stringify(state.aiHistory115))}catch(_){}
  }
  function aiAccess115(){return localStorage.getItem(AI_ACCESS_KEY_115)||''}
  function setAiAccess115(value){
    value=String(value||'').trim();
    if(value)localStorage.setItem(AI_ACCESS_KEY_115,value);else localStorage.removeItem(AI_ACCESS_KEY_115);
  }
  function currentLessonContext115(){
    try{
      if(typeof currentLesson110==='function'){
        const l=currentLesson110();
        if(l)return {kind:'ebd',title:`Lição ${l.n} • ${l.title}`,reference:l.ref,text:[`Texto áureo: ${l.gold}`,`Verdade prática: ${l.truth}`,`Foco: ${l.focus}`,...(l.topics||[]).map(x=>`${x[0]}: ${x[1]}`)].join('\n')};
      }
    }catch(_){}
    return null;
  }
  function currentBibleContext115(){
    try{
      if(!state.book||!state.chapter||typeof chapterVerses18!=='function')return null;
      const verses=chapterVerses18(state.book,state.chapter)||[];
      if(!verses.length)return null;
      const selected=Array.isArray(state.selectedVersesV19)?state.selectedVersesV19:[];
      if(selected.length){
        const rows=selected.slice(0,30).map(v=>`${state.book} ${state.chapter}:${v} ${verses[Number(v)-1]||''}`);
        return {kind:'bible-selection',title:`${state.book} ${state.chapter} • ${rows.length} versículo(s)`,reference:`${state.book} ${state.chapter}`,text:rows.join('\n')};
      }
      const rows=verses.map((t,i)=>`${i+1}. ${t}`);
      return {kind:'bible-chapter',title:`${state.book} ${state.chapter}`,reference:`${state.book} ${state.chapter}`,text:rows.join('\n')};
    }catch(_){return null}
  }
  function contextFromRoute115(){
    if(state.route==='reader')return currentBibleContext115();
    if(state.route==='ebd'||state.route==='lesson'||state.route==='classroom'||state.route==='attendance'||state.route==='agenda')return currentLessonContext115();
    return state.ai115.context||null;
  }
  function setContextAndOpen115(context,action='ask',question=''){
    state.ai115.context=context||null;state.ai115.action=action;state.ai115.question=question;nav('ai115');
  }
  function actionLabel115(a){return ({ask:'Perguntar',explain:'Explicar',summary:'Resumir',context:'Contexto',outline:'Gerar esboço',ebd:'Preparar EBD'}[a]||'Perguntar')}
  function actionPlaceholder115(a){return ({ask:'Faça uma pergunta sobre a passagem ou tema...',explain:'O que você quer compreender melhor nesta passagem?',summary:'Algum foco para o resumo? (opcional)',context:'Ex.: contexto histórico, literário, personagens...',outline:'Tema, público e objetivo do esboço...',ebd:'Ex.: preparar aula para adultos, jovens ou professor...'}[a]||'Digite sua pergunta...')}
  function defaultQuestion115(a,c){
    const ref=c?.reference||c?.title||'esta passagem';
    if(a==='explain')return `Explique ${ref} de forma clara, destacando contexto, mensagem central e aplicação.`;
    if(a==='summary')return `Resuma ${ref}, destacando a ideia principal e os pontos essenciais.`;
    if(a==='context')return `Apresente o contexto histórico e literário de ${ref} e explique como isso ajuda na leitura.`;
    if(a==='outline')return `Crie um esboço bíblico baseado em ${ref}, com introdução, 3 pontos, aplicação e conclusão.`;
    if(a==='ebd')return `Prepare um roteiro de aula EBD baseado em ${ref}, com objetivos, perguntas, dinâmica simples e aplicação.`;
    return '';
  }
  function contextCard115(c){
    if(!c)return `<section class="ai115-context emptyctx"><span>📎</span><div><strong>Sem contexto anexado</strong><small>Você pode perguntar por tema ou abrir a IA a partir da Bíblia/EBD.</small></div></section>`;
    return `<section class="ai115-context"><span>${c.kind==='ebd'?'🎓':'📖'}</span><div><small>CONTEXTO ENVIADO SOMENTE AO TOCAR EM PERGUNTAR</small><strong>${esc115(c.title||c.reference||'Contexto bíblico')}</strong><p>${esc115((c.text||'').slice(0,220))}${(c.text||'').length>220?'…':''}</p></div><button id="clearAiContext115">✕</button></section>`;
  }
  function messageHtml115(m,i){
    const isAi=m.role==='assistant';
    return `<article class="ai115-msg ${isAi?'assistant':'user'}"><div class="ai115-avatar">${isAi?'✦':'👤'}</div><div class="ai115-bubble"><small>${isAi?'Assistente Bíblia EBD':'Você'}</small><p>${textHtml115(m.text||'')}</p>${isAi?`<div class="ai115-msg-actions"><button data-ai-copy115="${i}">📋 Copiar</button><button data-ai-note115="${i}">📝 Salvar em notas</button><button data-ai-share115="${i}">↗ Compartilhar</button></div>`:''}</div></article>`;
  }
  function aiPage115(){
    const c=state.ai115.context||contextFromRoute115();
    if(c&&!state.ai115.context)state.ai115.context=c;
    const hasAccess=!!aiAccess115();
    const hist=state.aiHistory115;
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Assistente Bíblia EBD</h1><p>IA para estudo, EBD e preparação de esboços.</p></div></div>
      <section class="ai115-hero"><div class="ai115-orb">✦</div><div><span>ASSISTENTE IA • ONLINE OPCIONAL</span><h2>Estude com contexto, não no escuro</h2><p>A Bíblia do aplicativo fornece o texto de contexto. A resposta da IA é interpretação/apoio de estudo e nunca substitui o texto bíblico.</p></div></section>
      <div class="ai115-actions">${[['ask','💬','Perguntar'],['explain','🔎','Explicar'],['summary','🧾','Resumir'],['context','🏛️','Contexto'],['outline','🗂️','Esboço'],['ebd','🎓','EBD']].map(([a,ic,t])=>`<button data-ai-action115="${a}" class="${state.ai115.action===a?'active':''}"><span>${ic}</span>${t}</button>`).join('')}</div>
      ${contextCard115(c)}
      <section class="ai115-compose"><div class="ai115-mode"><span>${role115()==='Professor'?'🧑‍🏫':'👤'}</span><strong>Modo ${esc115(role115())}</strong><small>${hasAccess?'Servidor conectado por código privado':'Informe o código privado para ativar chamadas reais'}</small></div>
        ${!hasAccess?`<div class="ai115-access"><label>Código privado da IA</label><div><input class="field" id="aiAccess115" type="password" autocomplete="off" placeholder="Código configurado no servidor"><button class="btn btn-dark" id="saveAiAccess115">Salvar</button></div><small>O código fica somente neste aparelho e não entra no backup do Bíblia EBD.</small></div>`:''}
        <label>${esc115(actionLabel115(state.ai115.action))}</label><textarea class="field ai115-question" id="aiQuestion115" placeholder="${esc115(actionPlaceholder115(state.ai115.action))}">${esc115(state.ai115.question||defaultQuestion115(state.ai115.action,c))}</textarea>
        <div class="ai115-send-row"><span>🔒 Nada é enviado automaticamente.</span><button class="btn btn-primary" id="sendAi115" ${state.ai115.busy?'disabled':''}>${state.ai115.busy?'Pensando…':'✦ Perguntar à IA'}</button></div>
      </section>
      <section class="ai115-conversation" id="aiConversation115">${hist.length?hist.map(messageHtml115).join(''):`<div class="empty"><div class="big">✦</div><strong>Comece pelo texto bíblico</strong><p>Abra um capítulo ou selecione versículos e toque em “Estudar com IA”. Você decide exatamente o que será enviado.</p></div>`}</section>
      ${hist.length?`<button class="ai115-clear" id="clearAiHistory115">Limpar conversa local</button>`:''}
      <section class="ai115-privacy"><span>🛡️</span><div><strong>Privacidade por padrão</strong><p>Favoritos, anotações, histórico, perfil e dados da turma não são enviados automaticamente. Somente a pergunta e o contexto mostrado acima seguem para o servidor quando você confirma.</p></div></section>`;
  }
  async function sendAi115(){
    if(state.ai115.busy)return;
    const input=document.getElementById('aiQuestion115');
    const question=(input?.value||'').trim();
    if(!question)return toast115('Digite uma pergunta para a IA.');
    const access=aiAccess115();
    if(!access)return toast115('Informe primeiro o código privado da IA.');
    const context=state.ai115.context||null;
    const userMsg={role:'user',text:question,at:Date.now()};
    state.aiHistory115.push(userMsg);saveHistory115();
    state.ai115.busy=true;state.ai115.question='';window.render();
    try{
      const controller=new AbortController();
      const timer=setTimeout(()=>controller.abort(),45000);
      const res=await fetch(AI_ENDPOINT_115,{method:'POST',headers:{'Content-Type':'application/json','x-biblia-access':access},body:JSON.stringify({action:state.ai115.action,question,mode:role115(),context:context?{kind:context.kind,title:context.title,reference:context.reference,text:String(context.text||'').slice(0,16000)}:null}),signal:controller.signal});
      clearTimeout(timer);
      let data={};try{data=await res.json()}catch(_){}
      if(!res.ok)throw new Error(data?.message||data?.error||`Falha do servidor (${res.status})`);
      const answer=String(data.answer||'').trim();
      if(!answer)throw new Error('A IA não retornou texto.');
      state.aiHistory115.push({role:'assistant',text:answer,at:Date.now(),model:data.model||''});
      saveHistory115();
    }catch(err){
      const msg=err?.name==='AbortError'?'A IA demorou demais para responder. Tente novamente.':(err?.message||'Não foi possível conectar ao Assistente IA.');
      state.aiHistory115.push({role:'assistant',text:`⚠️ ${msg}`,at:Date.now(),error:true});saveHistory115();
    }finally{state.ai115.busy=false;window.render()}
  }
  function saveAiNote115(index){
    const m=state.aiHistory115[Number(index)];if(!m||m.role!=='assistant')return;
    const ref=state.ai115.context?.reference||'Estudo com IA';
    const note={t:`IA • ${ref}`,x:m.text};
    if(Array.isArray(state.notes)){state.notes.unshift(note);try{if(typeof save==='function')save()}catch(_){}toast115('Resposta salva nas anotações 📝')}
  }
  function copy115(text){
    if(navigator.clipboard?.writeText)navigator.clipboard.writeText(text).then(()=>toast115('Copiado 📋')).catch(()=>{});
    else if(typeof copy18==='function')copy18(text);
  }
  function share115(text){
    try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(text,'Assistente Bíblia EBD');return}}catch(_){}
    if(typeof share112==='function')share112(text,'Assistente Bíblia EBD');else copy115(text);
  }
  function injectReaderAi115(){
    if(state.route!=='reader')return;
    const tools=document.querySelector('.v19-reader-tools');
    if(tools&&!document.getElementById('openAiReader115'))tools.insertAdjacentHTML('beforeend','<button id="openAiReader115">✦ IA</button>');
    const bar=document.querySelector('.v19-selection-bar');
    if(bar&&!document.getElementById('studySelectionAi115'))bar.insertAdjacentHTML('beforeend','<button id="studySelectionAi115">✦ IA</button>');
  }
  function injectEbdAi115(){
    if(state.route!=='ebd'&&state.route!=='lesson')return;
    const root=document.getElementById('app');
    if(root&&!document.getElementById('openAiEbd115'))root.insertAdjacentHTML('afterbegin','<button class="ai115-inline-entry" id="openAiEbd115"><span>✦</span><div><strong>Preparar com IA</strong><small>Objetivos, perguntas, aplicação e roteiro de aula</small></div><b>›</b></button>');
  }
  function injectMinistryAi115(){
    if(state.route!=='ministry114')return;
    const grid=document.querySelector('.v114-grid');
    if(grid&&!document.getElementById('openAiMinistry115'))grid.insertAdjacentHTML('afterbegin','<button id="openAiMinistry115" class="ai115-ministry"><span>✦</span><strong>Assistente IA</strong><small>Estudo, contexto e esboços</small></button>');
  }
  function injectHomeAi115(){
    if(state.route!=='home')return;
    const root=document.getElementById('app');
    if(root&&!document.getElementById('openAiHome115'))root.insertAdjacentHTML('afterbegin','<section class="section ai115-home"><div class="ai115-home-orb">✦</div><div><span>ASSISTENTE BÍBLIA EBD</span><strong>Estudo com inteligência artificial</strong><small>Explique textos, prepare EBD e crie esboços com contexto bíblico.</small></div><button id="openAiHome115">Abrir IA</button></section>');
  }
  function bindInjected115(){
    document.getElementById('openAiReader115')?.addEventListener('click',()=>setContextAndOpen115(currentBibleContext115(),'explain'));
    document.getElementById('studySelectionAi115')?.addEventListener('click',()=>setContextAndOpen115(currentBibleContext115(),'explain'));
    document.getElementById('openAiEbd115')?.addEventListener('click',()=>setContextAndOpen115(currentLessonContext115(),'ebd'));
    document.getElementById('openAiMinistry115')?.addEventListener('click',()=>setContextAndOpen115(null,'ask'));
    document.getElementById('openAiHome115')?.addEventListener('click',()=>setContextAndOpen115(null,'ask'));
  }
  function bindAiPage115(){
    $$('[data-ai-action115]').forEach(b=>b.onclick=()=>{state.ai115.action=b.dataset.aiAction115;state.ai115.question=defaultQuestion115(state.ai115.action,state.ai115.context);window.render()});
    document.getElementById('clearAiContext115')?.addEventListener('click',()=>{state.ai115.context=null;window.render()});
    document.getElementById('saveAiAccess115')?.addEventListener('click',()=>{const v=document.getElementById('aiAccess115')?.value||'';if(!v.trim())return toast115('Digite o código privado.');setAiAccess115(v);toast115('Código salvo somente neste aparelho 🔒');window.render()});
    document.getElementById('sendAi115')?.addEventListener('click',sendAi115);
    document.getElementById('aiQuestion115')?.addEventListener('input',e=>{state.ai115.question=e.target.value});
    document.getElementById('clearAiHistory115')?.addEventListener('click',()=>{state.aiHistory115=[];saveHistory115();window.render()});
    $$('[data-ai-copy115]').forEach(b=>b.onclick=()=>copy115(state.aiHistory115[Number(b.dataset.aiCopy115)]?.text||''));
    $$('[data-ai-note115]').forEach(b=>b.onclick=()=>saveAiNote115(b.dataset.aiNote115));
    $$('[data-ai-share115]').forEach(b=>b.onclick=()=>share115(state.aiHistory115[Number(b.dataset.aiShare115)]?.text||''));
  }

  window.render=function(){
    if(state.route==='ai115'){
      document.getElementById('app').innerHTML=aiPage115();
      $$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));
      window.bind();return;
    }
    oldRender115();
    injectHomeAi115();injectReaderAi115();injectEbdAi115();injectMinistryAi115();bindInjected115();
  };
  window.bind=function(){oldBind115();if(state.route==='ai115')bindAiPage115();else bindInjected115()};

  window.__EBD_AI_115__=Object.freeze({
    endpoint:AI_ENDPOINT_115,
    openWithContext:setContextAndOpen115,
    bibleContext:currentBibleContext115,
    lessonContext:currentLessonContext115
  });

  window.render();
})();
