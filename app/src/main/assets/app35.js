// 1.16.x — Central de Diagnóstico e Regressão no aparelho.
(function(){
  'use strict';

  const previousRender=window.render;
  const previousBind=window.bind;
  const BUILD='1.16.1';
  const RESULT_KEY='ebd-diagnostics-v1160';
  const MANUAL_KEY='ebd-diagnostics-manual-v1160';
  const ACCESS_KEY='biblia-ai-access-v115';
  const SEARCH_HISTORY_KEY='ebd-smart-search-v1159';
  let running=false;
  let aiStatus=null;

  const safe=(raw,fallback)=>{try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}};
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const toastMsg=message=>{try{window.toast?.(message)}catch(_){}};
  const now=()=>Date.now();

  const savedRun=safe(localStorage.getItem(RESULT_KEY),null);
  let results=Array.isArray(savedRun?.results)?savedRun.results:[];

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
    const books=Array.isArray(window.BIBLE_DATA_V18?.books)?window.BIBLE_DATA_V18.books:[];
    let chapters=0,verses=0;
    books.forEach(book=>{
      const rows=Array.isArray(book.chapters)?book.chapters:[];
      chapters+=rows.length;
      rows.forEach(row=>{verses+=Array.isArray(row)?row.length:0});
    });
    return {books:books.length,chapters,verses};
  }

  function countHarpaLyrics(){
    const source=window.HARPA_LYRICS_USER;
    if(Array.isArray(source))return source.filter(item=>String(item?.lyrics||'').trim().length>0).length;
    if(!source||typeof source!=='object')return 0;
    return Object.values(source).filter(item=>typeof item==='string'?item.trim().length>0:String(item?.lyrics||'').trim().length>0).length;
  }

  function jsonIntegrity(){
    const bad=[];let checked=0;
    for(let i=0;i<localStorage.length;i++){
      const key=localStorage.key(i);
      if(!key||!key.startsWith('ebd-'))continue;
      const text=String(localStorage.getItem(key)||'').trim();
      if(!text||(text[0]!=='{'&&text[0]!=='['))continue;
      checked+=1;try{JSON.parse(text)}catch(_){bad.push(key)}
    }
    return {bad,checked};
  }

  function smartSearchTest(){
    const before=localStorage.getItem(SEARCH_HISTORY_KEY);let rows=[];
    try{rows=window.__EBD_SMART_1159__?.search?.('versículos sobre ansiedade')||[]}
    catch(_){rows=[]}
    finally{
      try{if(before===null)localStorage.removeItem(SEARCH_HISTORY_KEY);else localStorage.setItem(SEARCH_HISTORY_KEY,before)}catch(_){}
    }
    return rows;
  }

  function runAutomatic(){
    if(running)return;
    running=true;results=[];renderDiagnostics();
    try{
      let version='web';try{version=window.AndroidBridge?.appVersion?.()||'web'}catch(_){}
      add('version','Versão Android',String(version).startsWith('1.16.'),'Instalada: '+version);

      const bible=countBible();
      add('bible-count','Bíblia completa',bible.books===66&&bible.chapters===1189&&bible.verses===31098,`${bible.books} livros • ${bible.chapters} capítulos • ${bible.verses} versículos`);
      let john316='';try{john316=chapterVerses18('João',3)?.[15]||''}catch(_){}
      add('bible-sample','Leitura bíblica local',john316.length>20,'João 3:16 '+(john316?'carregado':'não carregado'));
      let parsed=null;try{parsed=parseRef19('João 3:16')}catch(_){}
      add('ref','Referências bíblicas',parsed?.book==='João'&&Number(parsed?.chapter)===3&&Number(parsed?.verse)===16,'Teste: João 3:16');

      const smart=smartSearchTest();
      add('search','Busca Inteligente',Array.isArray(smart)&&smart.length>0,`${Array.isArray(smart)?smart.length:0} resultado(s) no teste temático`);
      const lexicon=window.__EBD_SMART_1159__?.lexicon||[];
      add('dictionary','Dicionário local',Array.isArray(lexicon)&&lexicon.length>=20,`${Array.isArray(lexicon)?lexicon.length:0} verbetes`);
      const atlas=window.__EBD_SMART_1159__?.atlas||[];
      add('atlas','Atlas Bíblico',Array.isArray(atlas)&&atlas.length>=10,`${Array.isArray(atlas)?atlas.length:0} lugares indexados`);

      let lessons=0,lesson13=false;
      try{lessons=typeof EBD_LESSONS_110!=='undefined'?EBD_LESSONS_110.length:0;lesson13=typeof lesson110==='function'&&lesson110(13)?.n===13}catch(_){}
      add('ebd','EBD trimestral',lessons===13&&lesson13,`${lessons} lições disponíveis`);

      const catalog=window.HARPA_CATALOG_V18||[];
      add('harpa-catalog','Harpa — catálogo',Array.isArray(catalog)&&catalog.length===640,`${Array.isArray(catalog)?catalog.length:0}/640 hinos`);
      const lyricCount=countHarpaLyrics();
      let hymn1='';try{hymn1=typeof lyric191==='function'?lyric191(1):''}catch(_){}
      add('harpa-lyrics','Harpa — letras',lyricCount===640&&hymn1.trim().length>20,`${lyricCount}/640 letras carregadas`);

      const outlineApi=window.__EBD_OUTLINES_11510__;let outlines=[];
      try{outlines=outlineApi?.rows?.()||[]}catch(_){}
      add('outlines','Biblioteca de Esboços',!!outlineApi&&Array.isArray(outlines),`${outlines.length} esboço(s) salvo(s)`);

      const backup=window.__EBD_BACKUP_1142__;let backupOk=false,backupCount=0;
      try{const created=backup?.create?.();backupCount=Object.keys(created?.entries||{}).length;backupOk=!!backup?.validate?.(created)}catch(_){}
      add('backup','Backup Seguro',backupOk,`${backupCount} conjunto(s) de dados validado(s)`);

      let storageOk=false;const tempKey='__biblia_ebd_diag_1160__';
      try{localStorage.setItem(tempKey,'ok');storageOk=localStorage.getItem(tempKey)==='ok';localStorage.removeItem(tempKey)}catch(_){}
      add('storage','Armazenamento local',storageOk,'Teste temporário não destrutivo');

      const integrity=jsonIntegrity();
      add('json','Integridade dos dados',integrity.bad.length===0,integrity.bad.length?`JSON inválido: ${integrity.bad.join(', ')}`:`${integrity.checked} estruturas JSON verificadas`);

      let nativeOk=false,speechReady=false,notification='n/d';
      try{
        nativeOk=!!(window.AndroidBridge?.shareText&&window.AndroidBridge?.speakText&&window.AndroidBridge?.scheduleReminder);
        speechReady=!!window.AndroidBridge?.isSpeechReady?.();
        notification=window.AndroidBridge?.notificationPermissionGranted?.()?'permitida':'não permitida';
      }catch(_){}
      add('native','Integração Android',nativeOk,'Compartilhar • voz • lembretes');
      add('tts','Voz do Android',speechReady,speechReady?'Motor de voz pronto':'Motor de voz ainda não ficou pronto','advisory');
      add('notification','Notificações',notification==='permitida',notification==='permitida'?'Permissão autorizada • lembretes locais liberados':'Permissão opcional ainda não autorizada','advisory');

      const ai=window.__EBD_AI_115__,hasToken=!!localStorage.getItem(ACCESS_KEY);
      add('ai-ui','Assistente IA',!!ai?.endpoint&&!!window.__EBD_AI_1154__,`Backend configurado • código local ${hasToken?'presente':'não configurado'}`,hasToken?'required':'advisory');

      const recoveries=[];
      for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);if(key?.startsWith('ebd-recovery-v1141-'))recoveries.push(key)}
      add('recovery','Recuperação de inicialização',recoveries.length===0,recoveries.length?`${recoveries.length} item(ns) isolado(s) anteriormente`:'Nenhum dado corrompido isolado','advisory');
    }catch(error){add('runner','Executor de diagnóstico',false,error?.message||String(error))}

    running=false;
    try{localStorage.setItem(RESULT_KEY,JSON.stringify({version:BUILD,at:now(),results}))}catch(_){}
    renderDiagnostics();
  }

  async function testAi(){
    aiStatus={state:'checking',text:'Verificando conexão segura…'};renderDiagnostics();
    const token=localStorage.getItem(ACCESS_KEY)||'',endpoint=window.__EBD_AI_115__?.endpoint||'';
    if(!token){aiStatus={state:'error',text:'Código da IA não configurado neste aparelho.'};renderDiagnostics();return}
    if(!endpoint){aiStatus={state:'error',text:'Endpoint da IA não encontrado.'};renderDiagnostics();return}
    try{
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','x-biblia-access':token},body:JSON.stringify({action:'check'}),signal:controller.signal});
      clearTimeout(timer);let data={};try{data=await response.json()}catch(_){}
      if(!response.ok)throw new Error(data?.message||`Servidor ${response.status}`);
      aiStatus={state:'ok',text:`Conexão autorizada${data.model?' • '+data.model:''}`};
    }catch(error){aiStatus={state:'error',text:error?.name==='AbortError'?'Tempo de conexão excedido.':(error?.message||'Falha de conexão.')}}
    renderDiagnostics();
  }

  function summary(){
    const required=results.filter(row=>row.level==='required'),pass=required.filter(row=>row.ok).length;
    const advisories=results.filter(row=>row.level==='advisory'),warn=advisories.filter(row=>!row.ok).length;
    return {required:required.length,pass,fail:required.length-pass,warn};
  }
  function manualState(){const value=safe(localStorage.getItem(MANUAL_KEY),{});return value&&typeof value==='object'?value:{}}
  function resultCard(row){
    const status=row.ok?'ok':row.level==='advisory'?'warn':'fail',icon=row.ok?'✓':row.level==='advisory'?'!':'×',label=row.ok?'OK':row.level==='advisory'?'ATENÇÃO':'FALHA';
    return `<article class="v1160-result ${status}" data-diag-id="${esc(row.id)}"><span>${icon}</span><div><strong>${esc(row.title)}</strong><small>${esc(row.detail)}</small></div><b>${label}</b></article>`;
  }
  function manualHtml(){
    const done=manualState(),totalDone=MANUAL.filter(row=>done[row[0]]).length;
    const items=MANUAL.map(([id,title,desc])=>`<label class="v1160-check ${done[id]?'done':''}"><input type="checkbox" data-manual1160="${id}" ${done[id]?'checked':''}><span>✓</span><div><strong>${esc(title)}</strong><small>${esc(desc)}</small></div></label>`).join('');
    return `<section class="v1160-manual"><div class="section-title"><div><span>TESTE REAL NO APARELHO</span><h2>Checklist manual</h2></div><b>${totalDone}/${MANUAL.length}</b></div>${items}</section>`;
  }
  function reportText(){
    const s=summary(),done=manualState();
    const lines=[`Bíblia EBD — Diagnóstico ${BUILD}`,`Data: ${new Date().toLocaleString('pt-BR')}`,`Automático: ${s.pass}/${s.required} obrigatórios • ${s.fail} falha(s) • ${s.warn} aviso(s)`,''];
    results.forEach(row=>lines.push(`${row.ok?'OK':row.level==='advisory'?'AVISO':'FALHA'} — ${row.title}: ${row.detail}`));
    lines.push('',`Checklist manual: ${MANUAL.filter(row=>done[row[0]]).length}/${MANUAL.length}`);
    MANUAL.forEach(([id,title])=>lines.push(`${done[id]?'OK':'PENDENTE'} — ${title}`));
    lines.push('','Nenhum código privado, token ou conteúdo de notas foi incluído neste relatório.');
    return lines.join('\n');
  }
  function shareReport(){
    const text=reportText();
    try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(text,`Diagnóstico Bíblia EBD ${BUILD}`);return}}catch(_){}
    navigator.clipboard?.writeText(text).then(()=>toastMsg('Relatório copiado 📋'));
  }
  function page(){
    const s=summary(),saved=safe(localStorage.getItem(RESULT_KEY),null),last=saved?.at?new Date(saved.at).toLocaleString('pt-BR'):'';
    const health=!results.length?'idle':s.fail?'fail':s.warn?'warn':'ok';
    let headline='Pronto para verificar o app',heroIcon='🧪';
    if(results.length){if(s.fail){headline=`${s.fail} falha(s) precisam de correção`;heroIcon='⚠️'}else if(s.warn){headline='Base aprovada com avisos';heroIcon='🔎'}else{headline='Base automática aprovada';heroIcon='✓'}}
    let body=`<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Diagnóstico</h1><p>Regressão ${BUILD} • testes seguros no próprio aparelho.</p></div></div>`;
    body+=`<section class="v1160-hero ${health}"><div><span>ESTABILIZAÇÃO 1.16.x</span><h2>${esc(headline)}</h2><p>Os testes automáticos não apagam favoritos, notas, turma, estudos ou configurações.</p></div><b>${heroIcon}</b></section>`;
    body+=`<div class="v1160-actions"><button class="primary" id="runDiag1160">${running?'Verificando…':'▶ Executar testes automáticos'}</button><button id="shareDiag1160" ${results.length?'':'disabled'}>↗ Compartilhar relatório</button></div>`;
    if(results.length){
      body+=`<section class="v1160-score"><div><b>${s.pass}/${s.required}</b><small>testes obrigatórios</small></div><div><b>${s.fail}</b><small>falhas</small></div><div><b>${s.warn}</b><small>avisos</small></div></section>`;
      body+=`<section class="v1160-results">${results.map(resultCard).join('')}</section>`;
    }else body+=`<section class="v1160-empty"><span>🛡️</span><strong>Nenhum teste executado nesta sessão</strong><p>${last?'Última execução salva: '+esc(last)+'.':'Toque em Executar testes automáticos.'}</p></section>`;
    body+=`<section class="v1160-ai"><div><span>✦</span><div><strong>Teste online da IA</strong><small>Confere autorização do backend sem enviar Bíblia, notas, histórico ou o código no relatório.</small></div><button id="testAi1160">Testar</button></div>`;
    if(aiStatus)body+=`<p class="${esc(aiStatus.state)}">${aiStatus.state==='ok'?'✓':'⚠️'} ${esc(aiStatus.text)}</p>`;
    body+='</section>'+manualHtml();
    return body;
  }
  function bindDiagnostics(){
    document.getElementById('runDiag1160')?.addEventListener('click',runAutomatic);
    document.getElementById('shareDiag1160')?.addEventListener('click',shareReport);
    document.getElementById('testAi1160')?.addEventListener('click',testAi);
    document.querySelectorAll('[data-manual1160]').forEach(input=>input.addEventListener('change',()=>{const value=manualState();value[input.dataset.manual1160]=input.checked;localStorage.setItem(MANUAL_KEY,JSON.stringify(value));renderDiagnostics()}));
  }
  function renderDiagnostics(){
    if(state.route!=='diagnostics1160')return;
    const app=document.getElementById('app');if(!app)return;
    app.innerHTML=page();document.querySelectorAll('.bottomnav [data-route]').forEach(button=>button.classList.remove('active'));bindDiagnostics();
  }

  window.render=function(){if(state.route==='diagnostics1160'){renderDiagnostics();return}previousRender()};
  window.bind=function(){previousBind();if(state.route==='diagnostics1160')bindDiagnostics()};
  window.__EBD_DIAGNOSTICS_1160__=Object.freeze({run:runAutomatic,report:reportText,getResults:()=>results.slice(),build:BUILD});
  window.render();
})();
