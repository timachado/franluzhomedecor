// 1.16.0 — Central de Diagnóstico e Regressão no aparelho.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const RESULT_KEY='ebd-diagnostics-v1160';
  const MANUAL_KEY='ebd-diagnostics-manual-v1160';
  const ACCESS_KEY='biblia-ai-access-v115';
  let running=false;
  let results=[];
  let aiStatus=null;

  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const safe=(raw,fallback)=>{try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}};
  const toastMsg=s=>{try{window.toast?.(s)}catch(_){}};
  const now=()=>Date.now();

  const MANUAL=[
    ['nav','Navegação geral','Home, menu, barra inferior e botão Voltar funcionam sem travar.'],
    ['reader','Leitor da Bíblia','A− / A+ alteram o texto; rolagem, capítulo anterior/próximo e seleção funcionam.'],
    ['study','Estudo bíblico','Favoritar, anotar, marca-texto, copiar e compartilhar permanecem após reabrir o app.'],
    ['audio','Áudio','Ouvir/Parar funciona na Bíblia e na Harpa usando a voz do Android.'],
    ['harpa','Harpa Cristã','Busca, letras, favoritos, A− / A+ e navegação entre hinos funcionam.'],
    ['ebd','EBD Aluno/Professor','13 lições, alternância Aluno/Professor, checklist e progresso funcionam.'],
    ['class','Turma e Agenda','Minha Turma, Chamada, Agenda, compartilhamento e lembrete local funcionam.'],
    ['ai','Assistente IA','Referência automática, contexto bíblico, conversa contínua e salvar resposta funcionam.'],
    ['outline','Esboços','Criar, editar, duplicar, favoritar, pasta, pesquisar e compartilhar funcionam.'],
    ['backup','Backup','Gerar, analisar e restaurar um backup de teste preserva os dados corretamente.']
  ];

  function add(id,title,ok,detail='',level='required'){
    results.push({id,title,ok:!!ok,detail:String(detail||''),level,at:now()});
  }
  function countBible(){
    const data=window.BIBLE_DATA_V18;
    const books=Array.isArray(data?.books)?data.books:[];
    let chapters=0,verses=0;
    books.forEach(b=>{const cs=Array.isArray(b.chapters)?b.chapters:[];chapters+=cs.length;cs.forEach(v=>verses+=Array.isArray(v)?v.length:0)});
    return {books:books.length,chapters,verses};
  }
  function jsonIntegrity(){
    const bad=[],checked=[];
    for(let i=0;i<localStorage.length;i++){
      const key=localStorage.key(i);if(!key||!key.startsWith('ebd-'))continue;
      const value=localStorage.getItem(key)||'',t=value.trim();
      if(t[0]==='{'||t[0]==='['){checked.push(key);try{JSON.parse(t)}catch(_){bad.push(key)}}
    }
    return {bad,checked:checked.length};
  }
  function runAutomatic(){
    if(running)return;running=true;results=[];
    try{
      let version='web';try{version=window.AndroidBridge?.appVersion?.()||'web'}catch(_){}
      add('version','Versão Android',String(version).startsWith('1.16.0'),`Instalada: ${version}`);

      const bc=countBible();
      add('bible-count','Bíblia completa',bc.books===66&&bc.chapters===1189&&bc.verses===31098,`${bc.books} livros • ${bc.chapters} capítulos • ${bc.verses} versículos`);
      let j316='';try{j316=chapterVerses18('João',3)?.[15]||''}catch(_){}
      add('bible-sample','Leitura bíblica local',j316.length>20,`João 3:16 ${j316?'carregado':'não carregado'}`);
      let ref=null;try{ref=parseRef19('João 3:16')}catch(_){}
      add('ref','Referências bíblicas',ref?.book==='João'&&Number(ref?.chapter)===3&&Number(ref?.verse)===16,'Teste: João 3:16');

      let smart=[];try{smart=window.__EBD_SMART_1159__?.search?.('versículos sobre ansiedade')||[]}catch(_){}
      add('search','Busca Inteligente',Array.isArray(smart)&&smart.length>0,`${Array.isArray(smart)?smart.length:0} resultado(s) no teste temático`);
      const lex=window.__EBD_SMART_1159__?.lexicon||[];
      add('dictionary','Dicionário local',Array.isArray(lex)&&lex.length>=20,`${Array.isArray(lex)?lex.length:0} verbetes`);
      const atlas=window.__EBD_SMART_1159__?.atlas||[];
      add('atlas','Atlas Bíblico',Array.isArray(atlas)&&atlas.length>=10,`${Array.isArray(atlas)?atlas.length:0} lugares indexados`);

      let lessons=0,lesson13=false;try{lessons=typeof EBD_LESSONS_110!=='undefined'?EBD_LESSONS_110.length:0;lesson13=typeof lesson110==='function'&&lesson110(13)?.n===13}catch(_){}
      add('ebd','EBD trimestral',lessons===13&&lesson13,`${lessons} lições disponíveis`);

      const catalog=window.HARPA_CATALOG_V18||[];
      add('harpa-catalog','Harpa — catálogo',Array.isArray(catalog)&&catalog.length===640,`${Array.isArray(catalog)?catalog.length:0}/640 hinos`);
      const lyricObj=window.HARPA_LYRICS_USER||{};const lyricCount=Object.keys(lyricObj).filter(k=>String(lyricObj[k]||'').trim()).length;
      let hymn1='';try{hymn1=typeof lyric191==='function'?lyric191(1):String(lyricObj['1']||lyricObj[1]||'')}catch(_){}
      add('harpa-lyrics','Harpa — letras',lyricCount===640&&hymn1.trim().length>20,`${lyricCount}/640 letras carregadas`);

      const outlineApi=window.__EBD_OUTLINES_11510__;let outlines=[];try{outlines=outlineApi?.rows?.()||[]}catch(_){}
      add('outlines','Biblioteca de Esboços',!!outlineApi&&Array.isArray(outlines),`${outlines.length} esboço(s) salvo(s)`);

      const backup=window.__EBD_BACKUP_1142__;let backupOk=false,backupCount=0;
      try{const created=backup?.create?.();backupCount=Object.keys(created?.entries||{}).length;backupOk=!!backup?.validate?.(created)}catch(_){}
      add('backup','Backup Seguro',backupOk,`${backupCount} conjunto(s) de dados validado(s)`);

      let storageOk=false;const temp='__biblia_ebd_diag_1160__';
      try{localStorage.setItem(temp,'ok');storageOk=localStorage.getItem(temp)==='ok';localStorage.removeItem(temp)}catch(_){}
      add('storage','Armazenamento local',storageOk,'Teste temporário não destrutivo');

      const integrity=jsonIntegrity();
      add('json','Integridade dos dados',integrity.bad.length===0,integrity.bad.length?`JSON inválido: ${integrity.bad.join(', ')}`:`${integrity.checked} estruturas JSON verificadas`);

      let nativeOk=false,speechReady=false,notification='n/d';
      try{nativeOk=!!(window.AndroidBridge?.shareText&&window.AndroidBridge?.speakText&&window.AndroidBridge?.scheduleReminder);speechReady=!!window.AndroidBridge?.isSpeechReady?.();notification=window.AndroidBridge?.notificationPermissionGranted?.()?'permitida':'não permitida'}catch(_){}
      add('native','Integração Android',nativeOk,'Compartilhar • voz • lembretes');
      add('tts','Voz do Android',speechReady,speechReady?'Motor de voz pronto':'Motor de voz ainda não ficou pronto','advisory');
      add('notification','Notificações',notification==='permitida',`Permissão: ${notification}`,'advisory');

      const ai=window.__EBD_AI_115__;const hasToken=!!localStorage.getItem(ACCESS_KEY);
      add('ai-ui','Assistente IA',!!ai?.endpoint&&!!window.__EBD_AI_1154__,`Backend configurado • código local ${hasToken?'presente':'não configurado'}`,hasToken?'required':'advisory');

      const recoveries=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k?.startsWith('ebd-recovery-v1141-'))recoveries.push(k)}
      add('recovery','Recuperação de inicialização',recoveries.length===0,recoveries.length?`${recoveries.length} item(ns) isolado(s) anteriormente`:'Nenhum dado corrompido isolado','advisory');
    }catch(err){add('runner','Executor de diagnóstico',false,err?.message||String(err))}
    running=false;
    try{localStorage.setItem(RESULT_KEY,JSON.stringify({version:'1.16.0',at:now(),results}))}catch(_){}
    renderDiagnostics();
  }

  async function testAi(){
    aiStatus={state:'checking',text:'Verificando conexão segura…'};renderDiagnostics();
    const token=localStorage.getItem(ACCESS_KEY)||'';const endpoint=window.__EBD_AI_115__?.endpoint||'';
    if(!token){aiStatus={state:'error',text:'Código da IA não configurado neste aparelho.'};renderDiagnostics();return}
    if(!endpoint){aiStatus={state:'error',text:'Endpoint da IA não encontrado.'};renderDiagnostics();return}
    try{
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
      const res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','x-biblia-access':token},body:JSON.stringify({action:'check'}),signal:controller.signal});
      clearTimeout(timer);let data={};try{data=await res.json()}catch(_){}
      if(!res.ok)throw new Error(data?.message||`Servidor ${res.status}`);
      aiStatus={state:'ok',text:`Conexão autorizada${data.model?` • ${data.model}`:''}`};
    }catch(err){aiStatus={state:'error',text:err?.name==='AbortError'?'Tempo de conexão excedido.':(err?.message||'Falha de conexão.')}
    renderDiagnostics();
  }

  function summary(){
    const req=results.filter(x=>x.level==='required'),pass=req.filter(x=>x.ok).length;
    const advisory=results.filter(x=>x.level==='advisory'),warn=advisory.filter(x=>!x.ok).length;
    return {required:req.length,pass,fail:req.length-pass,warn};
  }
  function statusClass(r){return r.ok?'ok':r.level==='advisory'?'warn':'fail'}
  function resultCard(r){return `<article class="v1160-result ${statusClass(r)}"><span>${r.ok?'✓':r.level==='advisory'?'!':'×'}</span><div><strong>${esc(r.title)}</strong><small>${esc(r.detail)}</small></div><b>${r.ok?'OK':r.level==='advisory'?'ATENÇÃO':'FALHA'}</b></article>`}
  function manualState(){const x=safe(localStorage.getItem(MANUAL_KEY),{});return x&&typeof x==='object'?x:{}}
  function manualHtml(){const done=manualState();return `<section class="v1160-manual"><div class="section-title"><div><span>TESTE REAL NO APARELHO</span><h2>Checklist manual</h2></div><b>${MANUAL.filter(x=>done[x[0]]).length}/${MANUAL.length}</b></div>${MANUAL.map(([id,title,desc])=>`<label class="v1160-check ${done[id]?'done':''}"><input type="checkbox" data-manual1160="${id}" ${done[id]?'checked':''}><span>✓</span><div><strong>${esc(title)}</strong><small>${esc(desc)}</small></div></label>`).join('')}</section>`}
  function reportText(){
    const s=summary(),done=manualState();
    return ['Bíblia EBD — Diagnóstico 1.16.0',`Data: ${new Date().toLocaleString('pt-BR')}`,`Automático: ${s.pass}/${s.required} obrigatórios • ${s.fail} falha(s) • ${s.warn} aviso(s)`,'',...results.map(r=>`${r.ok?'OK':r.level==='advisory'?'AVISO':'FALHA'} — ${r.title}: ${r.detail}`),'',`Checklist manual: ${MANUAL.filter(x=>done[x[0]]).length}/${MANUAL.length}`,...MANUAL.map(([id,title])=>`${done[id]?'OK':'PENDENTE'} — ${title}`),'','Nenhum código privado, token ou conteúdo de notas foi incluído neste relatório.'].join('\n');
  }
  function shareReport(){const text=reportText();try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(text,'Diagnóstico Bíblia EBD 1.16.0');return}}catch(_){}navigator.clipboard?.writeText(text).then(()=>toastMsg('Relatório copiado 📋'))}

  function page(){
    const s=summary(),saved=safe(localStorage.getItem(RESULT_KEY),null),last=saved?.at?new Date(saved.at).toLocaleString('pt-BR'):'';
    const health=!results.length?'idle':s.fail?'fail':s.warn?'warn':'ok';
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Diagnóstico</h1><p>Regressão 1.16.0 • testes seguros no próprio aparelho.</p></div></div>
      <section class="v1160-hero ${health}"><div><span>ESTABILIZAÇÃO 1.16.0</span><h2>${!results.length?'Pronto para verificar o app':s.fail?`${s.fail} falha(s) precisam de correção`:s.warn?'Base aprovada com avisos':'Base automática aprovada'}</h2><p>Os testes automáticos não apagam favoritos, notas, turma, estudos ou configurações.</p></div><b>${!results.length?'🧪':s.fail?'⚠️':s.warn?'🔎':'✓'}</b></section>
      <div class="v1160-actions"><button class="primary" id="runDiag1160">${running?'Verificando…':'▶ Executar testes automáticos'}</button><button id="shareDiag1160" ${results.length?'':'disabled'}>↗ Compartilhar relatório</button></div>
      ${results.length?`<section class="v1160-score"><div><b>${s.pass}/${s.required}</b><small>testes obrigatórios</small></div><div><b>${s.fail}</b><small>falhas</small></div><div><b>${s.warn}</b><small>avisos</small></div></section><section class="v1160-results">${results.map(resultCard).join('')}</section>`:`<section class="v1160-empty"><span>🛡️</span><strong>Nenhum teste executado nesta sessão</strong><p>${last?`Última execução salva: ${esc(last)}.`:'Toque em Executar testes automáticos.'}</p></section>`}
      <section class="v1160-ai"><div><span>✦</span><div><strong>Teste online da IA</strong><small>Confere autorização do backend sem enviar Bíblia, notas, histórico ou o código no relatório.</small></div><button id="testAi1160">Testar</button></div>${aiStatus?`<p class="${aiStatus.state}">${aiStatus.state==='ok'?'✓':'⚠️'} ${esc(aiStatus.text)}</p>`:''}</section>
      ${manualHtml()}`;
  }
  function renderDiagnostics(){
    if(state.route!=='diagnostics1160')return;
    const app=document.getElementById('app');if(!app)return;app.innerHTML=page();
    document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));
    bindDiagnostics();
  }
  function bindDiagnostics(){
    document.getElementById('runDiag1160')?.addEventListener('click',runAutomatic);
    document.getElementById('shareDiag1160')?.addEventListener('click',shareReport);
    document.getElementById('testAi1160')?.addEventListener('click',testAi);
    document.querySelectorAll('[data-manual1160]').forEach(input=>input.addEventListener('change',()=>{
      const st=manualState();st[input.dataset.manual1160]=input.checked;localStorage.setItem(MANUAL_KEY,JSON.stringify(st));renderDiagnostics();
    }));
  }

  window.render=function(){if(state.route==='diagnostics1160'){renderDiagnostics();return}previousRender()};
  window.bind=function(){previousBind();if(state.route==='diagnostics1160')bindDiagnostics()};
  window.__EBD_DIAGNOSTICS_1160__=Object.freeze({run:runAutomatic,report:reportText,getResults:()=>results.slice()});
  window.render();
})();
