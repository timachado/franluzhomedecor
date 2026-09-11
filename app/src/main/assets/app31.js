// 1.15.7 — IA integrada a Minha Turma, Chamada e Agenda com contexto agregado e privacidade por padrão.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;

  function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function toastMsg(s){try{if(typeof window.toast==='function')window.toast(s)}catch(_){}}
  function roleIsProfessor(){return (state.profileV16?.role||state.userMode)==='Professor'}
  function fmtDate(date){try{return new Date(date+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'})}catch(_){return date||''}}
  function nextSunday(){try{return typeof nextSunday17==='function'?nextSunday17():''}catch(_){return ''}}
  function currentLesson(){
    try{
      if(typeof lesson110==='function'&&Number(state.ebdLesson110||0)>0)return lesson110(Number(state.ebdLesson110));
      if(typeof currentLesson110==='function')return currentLesson110();
    }catch(_){}
    return null;
  }
  function recordedAttendance(){
    const src=state.attendanceV17&&typeof state.attendanceV17==='object'?state.attendanceV17:{};
    return Object.entries(src).map(([date,row])=>{
      const vals=Object.values(row&&typeof row==='object'?row:{});
      const present=vals.filter(v=>v==='present').length;
      const absent=vals.filter(v=>v==='absent').length;
      const total=present+absent;
      return {date,present,absent,total,pct:total?Math.round(present/total*100):0};
    }).filter(x=>x.total>0).sort((a,b)=>b.date.localeCompare(a.date));
  }
  function trendLabel(){
    const rows=recordedAttendance().slice(0,3);
    if(rows.length<2)return 'Ainda sem histórico suficiente para tendência.';
    const diff=rows[0].pct-rows[1].pct;
    if(Math.abs(diff)<3)return 'Presença estável em relação ao encontro anterior.';
    return diff>0?`Presença subiu ${Math.abs(diff)} ponto(s) percentuais.`:`Presença caiu ${Math.abs(diff)} ponto(s) percentuais.`;
  }
  function agendaSummary(){
    const rows=Array.isArray(state.agendaV17)?state.agendaV17:[];
    const today=new Date().toISOString().slice(0,10);
    const upcoming=rows.filter(x=>x&&x.date>=today).sort((a,b)=>String(a.date).localeCompare(String(b.date)));
    return {count:upcoming.length,nextDate:upcoming[0]?.date||''};
  }
  function aggregateContext(kind='classroom'){
    const cls=state.classV17||{};
    const lesson=currentLesson();
    const hist=recordedAttendance();
    const last=hist[0]||null;
    const ag=agendaSummary();
    const lines=[
      'Contexto agregado da turma — nenhum nome de aluno foi incluído.',
      `Turma: ${cls.name||state.profileV16?.className||'EBD'}`,
      `Dia e horário: ${cls.day||'Domingo'} • ${cls.time||'09:00'}`,
      `Sala: ${cls.room||'Sala principal'}`,
      `Quantidade de alunos matriculados: ${Array.isArray(cls.students)?cls.students.length:0}`,
      `Encontros com chamada registrada: ${hist.length}`,
      last?`Última chamada registrada: ${fmtDate(last.date)} — ${last.present} presentes, ${last.absent} ausentes, ${last.pct}% de presença.`:'Última chamada registrada: ainda não há chamada salva.',
      `Tendência: ${trendLabel()}`,
      `Compromissos futuros adicionados à agenda: ${ag.count}${ag.nextDate?` • próximo em ${fmtDate(ag.nextDate)}`:''}`,
      lesson?`Lição em foco: Lição ${lesson.n} — ${lesson.title} • ${lesson.ref}`:'Lição em foco: não identificada.',
      lesson?.focus?`Foco da lição: ${lesson.focus}`:'',
      'Privacidade: não inferir, pedir ou inventar nomes, contatos, idade, saúde, comportamento individual ou qualquer dado pessoal dos alunos.'
    ].filter(Boolean);
    return {kind:`ebd-${kind}-aggregate`,title:`${cls.name||'Turma EBD'} • visão do professor`,reference:lesson?.ref||'',text:lines.join('\n')};
  }
  function attendanceContext(){
    const base=aggregateContext('attendance');
    const date=state.attendanceDate17||nextSunday();
    const raw=state.attendanceV17?.[date]||{};
    const vals=Object.values(raw);
    const present=vals.filter(v=>v==='present').length;
    const absent=vals.filter(v=>v==='absent').length;
    const total=present+absent;
    base.title=`Chamada ${fmtDate(date)} • dados agregados`;
    base.text+=`\nEncontro selecionado: ${fmtDate(date)}.${total?` ${present} presentes, ${absent} ausentes, ${Math.round(present/total*100)}% de presença.`:' Ainda não há chamada salva para esta data.'}`;
    return base;
  }
  function agendaContext(){
    const base=aggregateContext('agenda');
    const rows=Array.isArray(state.agendaV17)?state.agendaV17:[];
    const today=new Date().toISOString().slice(0,10);
    const upcoming=rows.filter(x=>x&&x.date>=today).sort((a,b)=>String(a.date).localeCompare(String(b.date))).slice(0,6);
    base.title='Agenda EBD • planejamento agregado';
    base.text+=`\nPróximas datas adicionadas pelo professor: ${upcoming.length?upcoming.map(x=>fmtDate(x.date)).join(' • '):'nenhuma'}.\nObservações e textos livres da agenda não foram enviados para preservar privacidade.`;
    return base;
  }
  function openAi(action,question,context){
    const api=window.__EBD_AI_115__;
    if(api?.openWithContext){api.openWithContext(context,action||'ebd',question||'');return}
    state.ai115=state.ai115||{};state.ai115.context=context;state.ai115.action=action||'ebd';state.ai115.question=question||'';nav('ai115');
  }
  function prompt(kind){
    const cls=state.classV17?.name||'EBD';
    const lesson=currentLesson();
    const title=lesson?`Lição ${lesson.n} — ${lesson.title}`:'próxima lição';
    const prompts={
      classPlan:`Como assistente do professor, prepare um plano prático para a próxima aula da turma ${cls}, considerando ${title}, o tamanho agregado da turma e o histórico de presença informado. Inclua preparação antes da aula, abertura, participação, aplicação e fechamento. Não faça inferências sobre alunos individuais.`,
      engagement:`Sugira 6 formas simples e respeitosas de aumentar participação e engajamento da turma ${cls} durante ${title}. Considere somente os dados agregados fornecidos. Separe ideias para abertura, durante a exposição e encerramento.`,
      classMessage:`Escreva uma mensagem geral, curta e acolhedora, para enviar à turma ${cls} lembrando a próxima EBD e incentivando a participação. Use a lição em foco quando disponível. Não cite nomes de alunos e não mencione estatísticas internas de presença.`,
      attendanceAnalysis:'Analise somente os números agregados de presença fornecidos. Explique a situação em linguagem simples, destaque tendência se houver dados suficientes e sugira ações coletivas para melhorar participação. Não tente identificar nem caracterizar alunos ausentes.',
      followup:'Crie um plano de acompanhamento pastoral/educacional para faltas na EBD sem usar nomes ou dados individuais. Dê sugestões de abordagem respeitosa, mensagem geral, acolhimento no retorno e formas de fortalecer vínculo da classe. Não assuma motivo da ausência.',
      encouragement:'Escreva uma mensagem geral de incentivo à participação na EBD, acolhedora e sem cobrança, que possa ser compartilhada com toda a turma. Não mencione nomes nem percentuais de presença.',
      postClass:'Crie um modelo de resumo pós-aula para o professor registrar o que funcionou, participação geral, dúvidas mais comuns, aplicação da lição e próximos passos. Baseie-se apenas nos dados agregados e na lição informada.',
      agendaPlan:'Organize um checklist do professor para os próximos encontros da EBD usando apenas as datas agregadas fornecidas e a lição em foco. Inclua preparação bíblica, materiais, comunicação geral, revisão da aula e acompanhamento.',
      reminder:'Crie uma mensagem curta de lembrete da próxima EBD, adequada para compartilhar com a turma inteira. Inclua dia/horário e tema bíblico quando disponíveis, sem expor dados internos da agenda ou informações pessoais.',
      nextMeetings:'Sugira um plano de preparação para os próximos encontros da EBD com prioridades semanais: estudo bíblico, objetivo da aula, participação, dinâmica simples e revisão. Use somente o contexto agregado.'
    };
    return prompts[kind]||prompts.classPlan;
  }
  function privacyStrip(){return '<div class="ai1157-privacy"><span>🛡️</span><div><strong>IA com dados agregados</strong><small>Nomes dos alunos e observações pessoais não são enviados.</small></div></div>'}
  function classroomCard(){
    const h=recordedAttendance();const last=h[0];
    return `<section class="ai1157-panel" id="aiClassroom1157"><div class="head"><div class="orb">✦</div><div><span>ASSISTENTE DA TURMA</span><strong>Planejamento inteligente do professor</strong><small>${Array.isArray(state.classV17?.students)?state.classV17.students.length:0} alunos • ${last?`${last.pct}% na última chamada`:'sem chamada registrada'}</small></div></div>${privacyStrip()}<div class="grid"><button data-ai-class1157="classPlan"><span>🧑‍🏫</span><strong>Próxima aula</strong><small>Plano para a turma</small></button><button data-ai-class1157="engagement"><span>🙋</span><strong>Engajamento</strong><small>Participação da classe</small></button><button data-ai-class1157="classMessage"><span>💬</span><strong>Mensagem geral</strong><small>Pronta para compartilhar</small></button><button data-ai-class1157="postClass"><span>📝</span><strong>Pós-aula</strong><small>Modelo de revisão</small></button></div></section>`;
  }
  function attendanceCard(){
    const ctx=attendanceContext();
    return `<section class="ai1157-panel compact" id="aiAttendance1157"><div class="head"><div class="orb">✦</div><div><span>IA DA CHAMADA</span><strong>Leia tendências sem expor alunos</strong><small>${esc(ctx.title)}</small></div></div>${privacyStrip()}<div class="grid three"><button data-ai-att1157="attendanceAnalysis"><span>📊</span><strong>Analisar</strong><small>Presença agregada</small></button><button data-ai-att1157="followup"><span>🤝</span><strong>Acompanhar</strong><small>Plano respeitoso</small></button><button data-ai-att1157="encouragement"><span>💬</span><strong>Incentivo</strong><small>Mensagem geral</small></button></div></section>`;
  }
  function agendaCard(){
    const ag=agendaSummary();
    return `<section class="ai1157-panel compact" id="aiAgenda1157"><div class="head"><div class="orb">✦</div><div><span>IA DA AGENDA</span><strong>Organize a preparação dos encontros</strong><small>${ag.count} compromisso(s) futuro(s) adicionado(s)</small></div></div>${privacyStrip()}<div class="grid three"><button data-ai-agenda1157="agendaPlan"><span>✅</span><strong>Checklist</strong><small>Preparação do professor</small></button><button data-ai-agenda1157="reminder"><span>🔔</span><strong>Lembrete</strong><small>Mensagem da EBD</small></button><button data-ai-agenda1157="nextMeetings"><span>🗓️</span><strong>Planejar</strong><small>Próximos encontros</small></button></div></section>`;
  }
  function bindCards(){
    document.querySelectorAll('[data-ai-class1157]').forEach(b=>b.onclick=()=>{if(!roleIsProfessor())return toastMsg('Ative o modo Professor para usar este recurso.');openAi('ebd',prompt(b.dataset.aiClass1157),aggregateContext('classroom'))});
    document.querySelectorAll('[data-ai-att1157]').forEach(b=>b.onclick=()=>{if(!roleIsProfessor())return toastMsg('Ative o modo Professor para usar este recurso.');openAi('ebd',prompt(b.dataset.aiAtt1157),attendanceContext())});
    document.querySelectorAll('[data-ai-agenda1157]').forEach(b=>b.onclick=()=>{if(!roleIsProfessor())return toastMsg('Ative o modo Professor para usar este recurso.');openAi('ebd',prompt(b.dataset.aiAgenda1157),agendaContext())});
  }
  function inject(){
    if(!roleIsProfessor())return;
    const app=document.getElementById('app');if(!app)return;
    if(state.route==='classroom'&&!document.getElementById('aiClassroom1157'))app.insertAdjacentHTML('afterbegin',classroomCard());
    if(state.route==='attendance'&&!document.getElementById('aiAttendance1157'))app.insertAdjacentHTML('afterbegin',attendanceCard());
    if(state.route==='agenda'&&!document.getElementById('aiAgenda1157'))app.insertAdjacentHTML('afterbegin',agendaCard());
    bindCards();
  }
  function updateProfessorEbdShortcut(){
    if(state.route!=='ebd'||!roleIsProfessor())return;
    const tools=document.querySelector('.v17-ebd-tools');
    if(tools&&!document.getElementById('aiClassShortcut1157'))tools.insertAdjacentHTML('beforeend',`<button class="ai1157-ebd-shortcut" id="aiClassShortcut1157" data-route="classroom"><span>✦</span><div><strong>IA da Turma</strong><small>Planejamento, presença e comunicação</small></div><b>›</b></button>`);
  }
  function post(){inject();updateProfessorEbdShortcut();bindCards()}
  window.render=function(){previousRender();requestAnimationFrame(post)};
  window.bind=function(){previousBind();post()};
  window.__EBD_CLASS_AI_1157__=Object.freeze({aggregateContext,attendanceContext,agendaContext,trend:trendLabel});
  window.render();
})();
