// 1.15.4 — estudos contínuos da IA: sessões locais, follow-up, histórico e esboços.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const ENDPOINT=window.__EBD_AI_115__?.endpoint||'https://dwpcddiramxlhavdmmyn.supabase.co/functions/v1/biblia-ai';
  const ACCESS_KEY='biblia-ai-access-v115';
  const LEGACY_HISTORY='ebd-ai-history-v115';
  const STUDIES_KEY='ebd-ai-studies-v1154';
  const ACTIVE_KEY='ebd-ai-active-study-v1154';
  const OUTLINES_KEY='ebd-ai-outlines-v1154';
  const MAX_STUDIES=12;
  const MAX_MESSAGES=30;
  let historyOpen=false;
  let sending=false;

  function safeJson(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}}
  function esc(value=''){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function toast(message){try{if(typeof window.toast==='function')window.toast(message)}catch(_){}}
  function now(){return Date.now()}
  function uid(){return 'ai-'+now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
  function role(){return state.profileV16?.role||state.userMode||'Aluno'}
  function access(){return localStorage.getItem(ACCESS_KEY)||''}
  function shortTitle(text=''){const s=String(text).replace(/\s+/g,' ').trim();return s.length>46?s.slice(0,43)+'…':s}
  function cleanContext(c){if(!c)return null;return {kind:c.kind||'',title:c.title||'',reference:c.reference||'',text:String(c.text||'').slice(0,16000)}}

  let studies=safeJson(localStorage.getItem(STUDIES_KEY),[]);
  if(!Array.isArray(studies))studies=[];
  studies=studies.filter(x=>x&&x.id&&Array.isArray(x.messages)).slice(0,MAX_STUDIES);
  let activeId=localStorage.getItem(ACTIVE_KEY)||'';

  function legacyMessages(){
    const current=Array.isArray(state.aiHistory115)?state.aiHistory115:safeJson(localStorage.getItem(LEGACY_HISTORY),[]);
    return Array.isArray(current)?current.filter(m=>m&&['user','assistant'].includes(m.role)).slice(-MAX_MESSAGES):[];
  }
  function makeStudy(messages=[],context=null){
    const first=messages.find(m=>m.role==='user')?.text||context?.reference||'Novo estudo';
    return {id:uid(),title:shortTitle(context?.reference||first||'Novo estudo'),createdAt:now(),updatedAt:now(),context:cleanContext(context),messages:messages.slice(-MAX_MESSAGES)};
  }
  function ensureActive(){
    let s=studies.find(x=>x.id===activeId);
    if(!s){
      const legacy=legacyMessages();
      s=makeStudy(legacy,state.ai115?.context||null);
      studies.unshift(s);activeId=s.id;persist();
    }
    return s;
  }
  function active(){return ensureActive()}
  function persist(){
    studies=studies.sort((a,b)=>(b.updatedAt||0)-(a.updatedAt||0)).slice(0,MAX_STUDIES);
    localStorage.setItem(STUDIES_KEY,JSON.stringify(studies));
    localStorage.setItem(ACTIVE_KEY,activeId);
    const s=studies.find(x=>x.id===activeId);
    if(s)localStorage.setItem(LEGACY_HISTORY,JSON.stringify(s.messages.slice(-18)));
  }
  function syncState(){
    const s=active();
    state.aiHistory115=s.messages;
    if(s.context&&!state.ai115.context)state.ai115.context=Object.assign({},s.context,{_study1154:true});
  }
  function captureContext(){
    const s=active();const c=state.ai115?.context;
    if(c){s.context=cleanContext(c);if((!s.title||s.title==='Novo estudo')&&c.reference)s.title=shortTitle(c.reference)}
    s.updatedAt=now();persist();
  }
  function newStudy(){
    const s=makeStudy([],null);studies.unshift(s);activeId=s.id;
    state.ai115.context=null;state.ai115.question='';state.ai115.action='ask';state.aiHistory115=[];
    historyOpen=false;persist();window.render();toast('Novo estudo iniciado ✨');
  }
  function openStudy(id){
    const s=studies.find(x=>x.id===id);if(!s)return;
    activeId=s.id;s.updatedAt=now();state.aiHistory115=s.messages;state.ai115.context=s.context?Object.assign({},s.context,{_study1154:true}):null;state.ai115.question='';historyOpen=false;persist();window.render();
  }
  function deleteStudy(id){
    const was=id===activeId;studies=studies.filter(x=>x.id!==id);
    if(was){const s=makeStudy([],null);studies.unshift(s);activeId=s.id;state.aiHistory115=[];state.ai115.context=null}
    persist();window.render();
  }
  function historyPayload(messages){
    const rows=(messages||[]).filter(m=>!m.error&&['user','assistant'].includes(m.role)).slice(-10).map(m=>({role:m.role,text:String(m.text||'').slice(0,2500)}));
    let total=0;const kept=[];
    for(let i=rows.length-1;i>=0;i--){const n=rows[i].text.length;if(total+n>9000)break;kept.unshift(rows[i]);total+=n}
    return kept;
  }
  function studyTitleFromQuestion(question,ctx){
    if(ctx?.reference)return shortTitle(ctx.reference);
    return shortTitle(question)||'Estudo com IA';
  }
  function saveTranscriptAsNote(){
    const s=active();if(!s.messages.length)return toast('Ainda não há conversa para salvar.');
    const transcript=s.messages.filter(m=>!m.error).map(m=>(m.role==='user'?'Você':'Assistente')+': '+m.text).join('\n\n');
    if(!Array.isArray(state.notes))return toast('Anotações indisponíveis.');
    state.notes.unshift({t:`Estudo IA • ${s.title||'Conversa'}`,x:transcript});
    try{if(typeof save==='function')save()}catch(_){}
    toast('Conversa inteira salva nas anotações 📝');
  }
  function saveOutlineRecord(title,text,context){
    let rows=safeJson(localStorage.getItem(OUTLINES_KEY),[]);if(!Array.isArray(rows))rows=[];
    rows.unshift({id:uid(),title:shortTitle(title||context?.reference||'Esboço IA'),text,reference:context?.reference||'',createdAt:now()});
    localStorage.setItem(OUTLINES_KEY,JSON.stringify(rows.slice(0,20)));
  }
  async function request1154(question,action,saveAsOutline=false){
    if(sending||state.ai115.busy)return;
    const token=access();if(!token)return toast('Confirme primeiro o código privado da IA.');
    const q=String(question||'').trim();if(!q)return toast('Digite uma pergunta para a IA.');
    const s=active();captureContext();const ctx=state.ai115.context||s.context||null;
    const previous=historyPayload(s.messages);
    const userMsg={role:'user',text:q,at:now()};s.messages.push(userMsg);s.messages=s.messages.slice(-MAX_MESSAGES);
    if(!s.title||s.title==='Novo estudo')s.title=studyTitleFromQuestion(q,ctx);
    s.updatedAt=now();state.aiHistory115=s.messages;state.ai115.busy=true;state.ai115.question='';sending=true;persist();window.render();
    let timer=null;
    try{
      const controller=new AbortController();timer=setTimeout(()=>controller.abort(),50000);
      const response=await fetch(ENDPOINT,{method:'POST',headers:{'Content-Type':'application/json','x-biblia-access':token},body:JSON.stringify({action:action||state.ai115.action||'ask',question:q,mode:role(),context:ctx?cleanContext(ctx):null,history:previous}),signal:controller.signal});
      clearTimeout(timer);timer=null;
      let data={};try{data=await response.json()}catch(_){}
      if(!response.ok)throw new Error(data?.message||`Falha do servidor (${response.status})`);
      const answer=String(data.answer||'').trim();if(!answer)throw new Error('A IA não retornou texto.');
      s.messages.push({role:'assistant',text:answer,at:now(),model:data.model||''});s.messages=s.messages.slice(-MAX_MESSAGES);s.updatedAt=now();
      if(saveAsOutline){saveOutlineRecord(s.title,answer,ctx);toast('Esboço gerado e salvo em Esboços 🗂️')}
    }catch(err){
      const msg=err?.name==='AbortError'?'A IA demorou demais para responder. Tente novamente.':(err?.message||'Não foi possível conectar ao Assistente IA.');
      s.messages.push({role:'assistant',text:`⚠️ ${msg}`,at:now(),error:true});s.updatedAt=now();
    }finally{
      if(timer)clearTimeout(timer);sending=false;state.ai115.busy=false;state.aiHistory115=s.messages;persist();window.render();
    }
  }
  function sendCurrent(event){
    if(event){event.preventDefault();event.stopImmediatePropagation()}
    const q=document.getElementById('aiQuestion115')?.value||state.ai115.question||'';
    request1154(q,state.ai115.action||'ask',false);
  }
  function generateOutline(){
    const s=active();if(!s.messages.length)return toast('Converse com a IA antes de gerar o esboço.');
    request1154('Transforme todo o estudo desta conversa em um esboço organizado para estudo ou pregação. Preserve a referência bíblica e os pontos já discutidos.','outline',true);
  }
  function toolbar(){
    const s=active();return `<section class="ai1154-studybar" id="aiStudyBar1154"><div class="current"><span>✦</span><div><small>ESTUDO ATUAL</small><strong>${esc(s.title||'Novo estudo')}</strong></div></div><div class="actions"><button id="newAiStudy1154">＋ Novo</button><button id="toggleAiHistory1154">🕘 Histórico <b>${studies.length}</b></button></div></section>`;
  }
  function historyPanel(){
    if(!historyOpen)return '';
    return `<section class="ai1154-history" id="aiHistoryPanel1154"><div class="head"><div><strong>Meus estudos com IA</strong><small>Salvos somente neste aparelho e incluídos no backup local.</small></div><button id="closeAiHistory1154">✕</button></div>${studies.map(s=>`<article class="${s.id===activeId?'active':''}"><button class="open" data-open-study1154="${esc(s.id)}"><strong>${esc(s.title||'Estudo')}</strong><small>${s.messages.length} mensagens • ${new Date(s.updatedAt||s.createdAt).toLocaleDateString('pt-BR')}</small></button><button class="del" data-del-study1154="${esc(s.id)}" aria-label="Excluir estudo">🗑️</button></article>`).join('')}</section>`;
  }
  function studyActions(){
    const s=active();if(!s.messages.length)return '';
    return `<section class="ai1154-export" id="aiExport1154"><div><strong>Continuar ou aproveitar este estudo</strong><small>As perguntas seguintes mantêm o contexto desta conversa.</small></div><div><button id="saveStudyNote1154">📝 Salvar conversa</button><button id="makeOutline1154">🗂️ Gerar e salvar esboço</button></div></section>`;
  }
  function patchAi(){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    syncState();
    const actions=document.querySelector('.ai115-actions');
    if(actions&&!document.getElementById('aiStudyBar1154'))actions.insertAdjacentHTML('beforebegin',toolbar()+historyPanel());
    else if(document.getElementById('aiStudyBar1154')&&historyOpen&&!document.getElementById('aiHistoryPanel1154'))document.getElementById('aiStudyBar1154').insertAdjacentHTML('afterend',historyPanel());
    const conv=document.getElementById('aiConversation115');
    if(conv&&!document.getElementById('aiExport1154')&&active().messages.length)conv.insertAdjacentHTML('afterend',studyActions());
    bindAi();
  }
  function bindAi(){
    const send=document.getElementById('sendAi115');
    if(send&&send.dataset.cont1154!=='1'){
      send.dataset.cont1154='1';send.addEventListener('click',sendCurrent,true);
    }
    const n=document.getElementById('newAiStudy1154');if(n)n.onclick=newStudy;
    const h=document.getElementById('toggleAiHistory1154');if(h)h.onclick=()=>{historyOpen=!historyOpen;window.render()};
    const c=document.getElementById('closeAiHistory1154');if(c)c.onclick=()=>{historyOpen=false;window.render()};
    document.querySelectorAll('[data-open-study1154]').forEach(b=>b.onclick=()=>openStudy(b.dataset.openStudy1154));
    document.querySelectorAll('[data-del-study1154]').forEach(b=>b.onclick=()=>deleteStudy(b.dataset.delStudy1154));
    const note=document.getElementById('saveStudyNote1154');if(note)note.onclick=saveTranscriptAsNote;
    const outline=document.getElementById('makeOutline1154');if(outline)outline.onclick=generateOutline;
  }
  function injectSavedOutlines(){
    if(typeof state==='undefined'||state.route!=='outlines')return;
    const rows=safeJson(localStorage.getItem(OUTLINES_KEY),[]);if(!Array.isArray(rows)||!rows.length)return;
    const app=document.getElementById('app');if(!app||document.getElementById('aiSavedOutlines1154'))return;
    const html=`<section class="ai1154-saved-outlines" id="aiSavedOutlines1154"><div class="title"><span>✦</span><div><strong>Esboços gerados pela IA</strong><small>${rows.length} salvo(s) neste aparelho</small></div></div>${rows.slice(0,8).map((r,i)=>`<details><summary>${esc(r.title||'Esboço IA')}<small>${esc(r.reference||'')}</small></summary><div class="body">${esc(r.text||'').replace(/\n/g,'<br>')}</div><div class="buttons"><button data-outline-note1154="${i}">📝 Salvar em notas</button><button data-outline-del1154="${i}">Excluir</button></div></details>`).join('')}</section>`;
    app.insertAdjacentHTML('afterbegin',html);
    document.querySelectorAll('[data-outline-note1154]').forEach(b=>b.onclick=()=>{const r=rows[Number(b.dataset.outlineNote1154)];if(r&&Array.isArray(state.notes)){state.notes.unshift({t:`Esboço IA • ${r.title}`,x:r.text});try{if(typeof save==='function')save()}catch(_){}toast('Esboço salvo nas anotações 📝')}});
    document.querySelectorAll('[data-outline-del1154]').forEach(b=>b.onclick=()=>{rows.splice(Number(b.dataset.outlineDel1154),1);localStorage.setItem(OUTLINES_KEY,JSON.stringify(rows));window.render()});
  }

  window.render=function(){previousRender();requestAnimationFrame(()=>{patchAi();injectSavedOutlines()})};
  window.bind=function(){previousBind();bindAi()};
  window.__EBD_AI_1154__=Object.freeze({newStudy,openStudy,request:request1154,getStudies:()=>studies.slice()});
  ensureActive();syncState();window.render();
})();
