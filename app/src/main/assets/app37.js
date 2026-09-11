// 1.16.2 — regressão guiada no aparelho, sem alterar dados do usuário.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const KEY='ebd-guided-regression-v1162';
  const ACTIVE='ebd-guided-active-v1162';

  const TESTS=[
    {id:'nav',icon:'🧭',title:'Navegação geral',route:'home',desc:'Abra Home, menu, barra inferior e use Voltar. Nada deve travar ou abrir tela errada.'},
    {id:'reader',icon:'📖',title:'Leitor da Bíblia',route:'reader',desc:'Teste capítulo anterior/próximo, rolagem, A−/A+, seleção e Estudar.'},
    {id:'study',icon:'✍️',title:'Favoritos e anotações',route:'reader',desc:'Favorite um versículo, faça uma anotação/marca-texto e confirme que continuam após sair e voltar.'},
    {id:'search',icon:'🔎',title:'Busca e referências',route:'search',desc:'Pesquise “versículos sobre ansiedade” e uma referência como João 3:16.'},
    {id:'harpa',icon:'🎵',title:'Harpa Cristã',route:'harpa',desc:'Abra um hino, confira a letra, busca, favorito, A−/A+ e Ouvir.'},
    {id:'ebd',icon:'🎓',title:'EBD Aluno e Professor',route:'ebd',desc:'Abra lições, alterne Aluno/Professor e teste progresso, checklist e ferramentas do professor.'},
    {id:'class',icon:'👥',title:'Turma, chamada e agenda',route:'classroom',desc:'Abra Minha Turma, Chamada e Agenda; confira compartilhamento e lembrete local.'},
    {id:'ai',icon:'✦',title:'Assistente IA',route:'ai115',desc:'Faça uma pergunta com referência, uma continuação sem repetir a referência e salve a resposta.'},
    {id:'outlines',icon:'🗂️',title:'Biblioteca de Esboços',route:'outlines',desc:'Crie/edite, duplique, favorite, pesquise, mova de pasta e compartilhe um esboço.'},
    {id:'native',icon:'🔊',title:'Áudio e recursos Android',route:'reader',desc:'Teste Ouvir/Parar e Compartilhar. Confirme que a permissão de notificações continua verde no Diagnóstico.'},
    {id:'backup',icon:'☁️',title:'Backup Seguro',route:'sync',desc:'Gere um backup, analise-o e confirme que a tela reconhece o arquivo sem erro.'},
    {id:'ministry',icon:'🎙️',title:'Ministério e aparência',route:'ministry114',desc:'Teste Modo Púlpito, manter tela ligada e depois Aparência, foco, contraste e espaçamento.'}
  ];

  function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function load(){try{const x=JSON.parse(localStorage.getItem(KEY)||'{}');return x&&typeof x==='object'?x:{}}catch(_){return {}}}
  function save(x){try{localStorage.setItem(KEY,JSON.stringify(x))}catch(_){}}
  function openRoute(route,id){
    try{localStorage.setItem(ACTIVE,id)}catch(_){}
    try{if(typeof window.nav==='function'){window.nav(route);return}}catch(_){}
    try{state.route=route;window.render()}catch(_){}
  }
  function statusLabel(v){return v?.status==='pass'?'APROVADO':v?.status==='fail'?'FALHOU':'PENDENTE'}
  function setStatus(id,status){
    const data=load(),row=data[id]||{};
    let note=row.note||'';
    if(status==='fail'){
      try{const entered=window.prompt('O que falhou? Descreva em poucas palavras para entrar no relatório.',note);if(entered!==null)note=String(entered).trim()}catch(_){}
    }
    data[id]={status,note,at:Date.now()};save(data);renderGuided();
  }
  function counts(){const data=load();let pass=0,fail=0;TESTS.forEach(t=>{if(data[t.id]?.status==='pass')pass++;if(data[t.id]?.status==='fail')fail++});return {pass,fail,pending:TESTS.length-pass-fail}}
  function report(){
    const data=load(),c=counts();
    return ['Bíblia EBD — Regressão guiada 1.16.2',`Data: ${new Date().toLocaleString('pt-BR')}`,`Resultado: ${c.pass}/${TESTS.length} aprovados • ${c.fail} falha(s) • ${c.pending} pendente(s)`,'',...TESTS.map(t=>{const r=data[t.id]||{};return `${statusLabel(r)} — ${t.title}${r.note?`: ${r.note}`:''}`;}),'','O relatório não inclui notas bíblicas, nomes de alunos, histórico da IA nem códigos privados.'].join('\n');
  }
  function share(){const text=report();try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(text,'Regressão Bíblia EBD 1.16.2');return}}catch(_){}navigator.clipboard?.writeText(text).then(()=>window.toast?.('Relatório copiado 📋'))}

  function card(t,data){
    const r=data[t.id]||{},status=r.status||'pending';
    return `<article class="v1162-test ${status}"><div class="v1162-test-head"><span>${t.icon}</span><div><strong>${esc(t.title)}</strong><small>${esc(t.desc)}</small></div><b>${statusLabel(r)}</b></div>${r.note?`<p class="v1162-note">⚠ ${esc(r.note)}</p>`:''}<div class="v1162-test-actions"><button data-guide-open="${t.id}">Abrir recurso</button><button class="pass" data-guide-pass="${t.id}">✓ Aprovado</button><button class="fail" data-guide-fail="${t.id}">! Falhou</button></div></article>`;
  }
  function guidedHtml(){
    const data=load(),c=counts(),pct=Math.round((c.pass/TESTS.length)*100);
    return `<section class="v1162-guided" id="guidedRegression1162"><div class="v1162-title"><div><span>TESTE REAL NO APARELHO</span><h2>Regressão guiada 1.16.2</h2><p>Abra cada módulo, faça o teste indicado e volte para marcar o resultado.</p></div><b>${c.pass}/${TESTS.length}</b></div><div class="v1162-progress"><i style="width:${pct}%"></i></div><div class="v1162-summary"><span>✓ ${c.pass} aprovados</span><span>! ${c.fail} falhas</span><span>○ ${c.pending} pendentes</span></div><div class="v1162-list">${TESTS.map(t=>card(t,data)).join('')}</div><div class="v1162-footer"><button id="shareGuide1162">↗ Compartilhar resultado</button><button id="resetGuide1162">Reiniciar checklist</button></div></section>`;
  }
  function bindGuided(){
    document.querySelectorAll('[data-guide-open]').forEach(b=>b.onclick=()=>{const t=TESTS.find(x=>x.id===b.dataset.guideOpen);if(t)openRoute(t.route,t.id)});
    document.querySelectorAll('[data-guide-pass]').forEach(b=>b.onclick=()=>setStatus(b.dataset.guidePass,'pass'));
    document.querySelectorAll('[data-guide-fail]').forEach(b=>b.onclick=()=>setStatus(b.dataset.guideFail,'fail'));
    document.getElementById('shareGuide1162')?.addEventListener('click',share);
    document.getElementById('resetGuide1162')?.addEventListener('click',()=>{if(confirm('Reiniciar apenas o checklist da regressão guiada? Seus dados do app não serão apagados.')){localStorage.removeItem(KEY);localStorage.removeItem(ACTIVE);renderGuided()}});
  }
  function renderGuided(){
    if(typeof state==='undefined'||state.route!=='diagnostics1160')return;
    const old=document.getElementById('guidedRegression1162');old?.remove();
    const manual=document.querySelector('.v1160-manual');
    if(manual)manual.insertAdjacentHTML('beforebegin',guidedHtml());
    else document.getElementById('app')?.insertAdjacentHTML('beforeend',guidedHtml());
    bindGuided();
    try{localStorage.removeItem(ACTIVE)}catch(_){}
  }
  function injectReturn(){
    if(typeof state==='undefined'||state.route==='diagnostics1160')return;
    let id='';try{id=localStorage.getItem(ACTIVE)||''}catch(_){}
    if(!id||document.getElementById('returnGuide1162'))return;
    const t=TESTS.find(x=>x.id===id);if(!t)return;
    const bar=document.createElement('div');bar.id='returnGuide1162';bar.className='v1162-return';
    bar.innerHTML=`<div><span>🧪</span><div><strong>Teste: ${esc(t.title)}</strong><small>Quando terminar, volte ao checklist para aprovar ou registrar falha.</small></div></div><button>Voltar ao teste</button>`;
    bar.querySelector('button').onclick=()=>{try{state.route='diagnostics1160';window.render()}catch(_){}};
    document.getElementById('app')?.prepend(bar);
  }
  function post(){requestAnimationFrame(()=>{renderGuided();injectReturn()})}

  window.render=function(){previousRender();post()};
  window.bind=function(){previousBind();post()};
  window.__EBD_GUIDED_1162__=Object.freeze({tests:TESTS,status:load,report,counts});
  post();
})();
