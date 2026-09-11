// 1.15.6 — Central IA do Professor + EBD contextual + Esboços inteligentes.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const OUTLINES_KEY='ebd-ai-outlines-v1154';
  const EBD_PREF_KEY='ebd-ai-professor-pref-v1156';

  function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function toastMsg(s){try{if(typeof window.toast==='function')window.toast(s)}catch(_){}}
  function safeJson(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch(_){return fallback}}
  function currentOpenedLesson(){
    try{
      if(typeof lesson110==='function'){
        const n=Number(state.ebdLesson110||state.ebdLesson||0);
        if(n>0)return lesson110(n);
      }
      if(typeof currentLesson110==='function')return currentLesson110();
    }catch(_){}
    return null;
  }
  function lessonContext1156(){
    const l=currentOpenedLesson();
    if(!l)return null;
    const text=[
      `Texto-base: ${l.ref||''}`,
      `Texto Áureo: ${l.gold||''}`,
      `Verdade Prática: ${l.truth||''}`,
      `Foco: ${l.focus||''}`,
      ...(Array.isArray(l.topics)?l.topics.map((x,i)=>`Tópico ${i+1} — ${x?.[0]||''}: ${x?.[1]||''}`):[]),
      ...(Array.isArray(l.questions)?l.questions.map((q,i)=>`Pergunta ${i+1}: ${q}`):[])
    ].filter(Boolean).join('\n');
    return {kind:'ebd-lesson',title:`Lição ${l.n} • ${l.title}`,reference:l.ref||'',text};
  }
  function openAi(action,question,context){
    const api=window.__EBD_AI_115__;
    const ctx=arguments.length>=3?context:lessonContext1156();
    if(api?.openWithContext){api.openWithContext(ctx,action||'ebd',question||'');return}
    state.ai115=state.ai115||{};state.ai115.context=ctx;state.ai115.action=action||'ebd';state.ai115.question=question||'';nav('ai115');
  }
  function roleIsProfessor(){return state.userMode==='Professor'||state.profileV16?.role==='Professor'}
  function getPrefs(){return Object.assign({duration:45,audience:'Adultos'},safeJson(localStorage.getItem(EBD_PREF_KEY),{}))}
  function savePrefs(p){localStorage.setItem(EBD_PREF_KEY,JSON.stringify(p))}

  function teacherCenterHtml(){
    const l=currentOpenedLesson();if(!l)return '';
    const p=getPrefs();
    return `<section class="ai1156-teacher" id="aiTeacherCenter1156">
      <div class="ai1156-title"><div class="orb">✦</div><div><span>CENTRAL IA DO PROFESSOR</span><strong>Prepare a Lição ${String(l.n).padStart(2,'0')} com assistência inteligente</strong><small>${esc(l.title)} • ${esc(l.ref)}</small></div></div>
      <div class="ai1156-options"><label>Tempo da aula<select id="aiEbdDuration1156"><option value="30" ${p.duration==30?'selected':''}>30 minutos</option><option value="45" ${p.duration==45?'selected':''}>45 minutos</option><option value="60" ${p.duration==60?'selected':''}>60 minutos</option></select></label><label>Classe<select id="aiEbdAudience1156"><option ${p.audience==='Adultos'?'selected':''}>Adultos</option><option ${p.audience==='Jovens'?'selected':''}>Jovens</option><option ${p.audience==='Adolescentes'?'selected':''}>Adolescentes</option><option ${p.audience==='Mista'?'selected':''}>Mista</option></select></label></div>
      <div class="ai1156-grid">
        <button data-ai-ebd1156="plan"><span>🧑‍🏫</span><strong>Plano completo</strong><small>Roteiro com tempo</small></button>
        <button data-ai-ebd1156="questions"><span>❓</span><strong>Perguntas</strong><small>Participação da classe</small></button>
        <button data-ai-ebd1156="dynamic"><span>🤝</span><strong>Dinâmica</strong><small>Atividade simples</small></button>
        <button data-ai-ebd1156="application"><span>🎯</span><strong>Aplicações</strong><small>Vida prática</small></button>
        <button data-ai-ebd1156="summary"><span>📝</span><strong>Resumo</strong><small>Revisão do professor</small></button>
        <button data-ai-ebd1156="outline"><span>🗂️</span><strong>Esboço</strong><small>Mensagem da lição</small></button>
      </div>
    </section>`;
  }
  function studentEbdHtml(){
    const l=currentOpenedLesson();if(!l)return '';
    return `<section class="ai1156-student" id="aiStudentEbd1156"><span>✦</span><div><strong>Estudar esta lição com IA</strong><small>Explicação, resumo, perguntas e aplicação da Lição ${l.n}</small></div><button data-ai-ebd1156="student">Estudar</button></section>`;
  }
  function promptFor(kind){
    const p=getPrefs();
    const audience=p.audience||'Adultos',duration=Number(p.duration)||45;
    const prompts={
      plan:`Prepare um plano completo desta lição EBD para uma classe de ${audience}, com duração total de ${duration} minutos. Distribua o tempo por etapas, inclua abertura, leitura bíblica, objetivos, desenvolvimento dos tópicos, perguntas à classe, uma dinâmica simples, aplicação prática e encerramento em oração.`,
      questions:`Crie 8 perguntas progressivas para esta lição EBD para uma classe de ${audience}: 3 de observação do texto, 3 de compreensão/reflexão e 2 de aplicação. Inclua uma breve orientação ao professor sobre o objetivo de cada bloco.`,
      dynamic:`Crie uma dinâmica simples e respeitosa para esta lição EBD, adequada a ${audience}, que possa ser realizada em até 10 minutos e sem materiais difíceis. Explique objetivo, preparação, passo a passo e ligação com o texto bíblico.`,
      application:`Crie aplicações práticas desta lição para a vida cotidiana de uma classe de ${audience}. Separe aplicação pessoal, familiar, igreja/comunidade e compromisso para a semana.`,
      summary:'Crie um resumo de preparação para o professor desta lição: ideia central, contexto do texto-base, três pontos essenciais, cuidados de interpretação, perguntas prováveis dos alunos e conclusão.',
      outline:'Transforme esta lição EBD em um esboço de estudo/pregação com título, texto-base, introdução, três pontos expositivos, aplicações e conclusão.',
      student:'Ajude o aluno a estudar esta lição EBD. Explique em linguagem clara a ideia central, o texto-base, os tópicos e proponha 3 perguntas de reflexão e 1 compromisso prático para a semana.'
    };
    return prompts[kind]||prompts.plan;
  }
  function bindTeacherOptions(){
    const dur=document.getElementById('aiEbdDuration1156'),aud=document.getElementById('aiEbdAudience1156');
    const save=()=>savePrefs({duration:Number(dur?.value)||45,audience:aud?.value||'Adultos'});
    dur?.addEventListener('change',save);aud?.addEventListener('change',save);
    document.querySelectorAll('[data-ai-ebd1156]').forEach(b=>b.onclick=()=>{
      save();const kind=b.dataset.aiEbd1156;const action=kind==='outline'?'outline':kind==='summary'?'summary':'ebd';
      openAi(action,promptFor(kind),lessonContext1156());
    });
  }
  function injectEbd(){
    if(!['ebd','lesson'].includes(state.route))return;
    const app=document.getElementById('app');if(!app)return;
    document.getElementById('openAiEbd115')?.remove();
    if(document.getElementById('aiTeacherCenter1156')||document.getElementById('aiStudentEbd1156'))return;
    const html=roleIsProfessor()?teacherCenterHtml():studentEbdHtml();
    if(html)app.insertAdjacentHTML('afterbegin',html);
    bindTeacherOptions();
  }

  function outlineHubHtml(){
    const count=(safeJson(localStorage.getItem(OUTLINES_KEY),[])||[]).length;
    return `<section class="ai1156-outline-hub" id="aiOutlineHub1156"><div class="head"><span>✦</span><div><strong>Esboços com IA</strong><small>Crie a partir de tema ou de uma passagem bíblica • ${count} salvo(s)</small></div></div><div class="quick"><button data-ai-outline1156="expository">📖 Expositivo</button><button data-ai-outline1156="thematic">💡 Temático</button><button data-ai-outline1156="devotional">🙏 Devocional</button><button data-ai-outline1156="ebd">🎓 EBD</button></div><div class="topic"><input class="field" id="aiOutlineTopic1156" placeholder="Tema ou referência, ex.: Salmos 23"><button class="btn btn-primary" id="aiOutlineCreate1156">✦ Criar com IA</button></div></section>`;
  }
  function outlinePrompt(type,topic){
    const map={
      expository:'Crie um esboço expositivo fiel ao texto, com contexto, ideia central, introdução, três pontos derivados da passagem, aplicações e conclusão.',
      thematic:'Crie um esboço temático bíblico com introdução, três pontos, referências de apoio, aplicações e conclusão. Não invente referências.',
      devotional:'Crie um esboço devocional breve, acolhedor e bíblico com reflexão, três verdades, aplicação pessoal e oração final sugerida.',
      ebd:'Crie um esboço para ensino em EBD com objetivos, três pontos, perguntas para a classe, aplicação e conclusão.'
    };
    return `${map[type]||map.expository}\n\nTema ou referência solicitada: ${topic||'Use o contexto bíblico anexado, se houver.'}`;
  }
  function bindOutlineHub(){
    let type='expository';
    document.querySelectorAll('[data-ai-outline1156]').forEach(b=>b.onclick=()=>{type=b.dataset.aiOutline1156;document.querySelectorAll('[data-ai-outline1156]').forEach(x=>x.classList.toggle('active',x===b))});
    const first=document.querySelector('[data-ai-outline1156="expository"]');if(first)first.classList.add('active');
    document.getElementById('aiOutlineCreate1156')?.addEventListener('click',()=>{
      const topic=(document.getElementById('aiOutlineTopic1156')?.value||'').trim();
      if(!topic)return toastMsg('Digite um tema ou referência para o esboço.');
      let context=null;
      try{
        const api=window.__EBD_AI_1152__;
        const parsed=typeof api?.detectReference==='function'?api.detectReference(topic):null;
        context=parsed&&typeof api?.contextFromRef==='function'?api.contextFromRef(parsed):null;
      }catch(_){}
      openAi('outline',outlinePrompt(type,topic),context);
    });
  }
  function injectOutlines(){
    if(state.route!=='outlines')return;
    const app=document.getElementById('app');if(!app||document.getElementById('aiOutlineHub1156'))return;
    app.insertAdjacentHTML('afterbegin',outlineHubHtml());bindOutlineHub();
  }

  function patchSavedOutlineActions(){
    if(state.route!=='outlines')return;
    const root=document.getElementById('aiSavedOutlines1154');if(!root)return;
    root.querySelectorAll('details').forEach((d,index)=>{
      if(d.querySelector('[data-outline-copy1156]'))return;
      const box=d.querySelector('.buttons');if(!box)return;
      box.insertAdjacentHTML('afterbegin',`<button data-outline-copy1156="${index}">📋 Copiar</button><button data-outline-share1156="${index}">↗ Compartilhar</button>`);
    });
    root.querySelectorAll('[data-outline-copy1156]').forEach(b=>b.onclick=()=>{
      const rows=safeJson(localStorage.getItem(OUTLINES_KEY),[]);const r=rows[Number(b.dataset.outlineCopy1156)];
      if(!r)return;const text=`${r.title||'Esboço'}\n${r.reference||''}\n\n${r.text||''}`;
      if(navigator.clipboard?.writeText)navigator.clipboard.writeText(text).then(()=>toastMsg('Esboço copiado 📋'));else toastMsg('Não foi possível copiar.');
    });
    root.querySelectorAll('[data-outline-share1156]').forEach(b=>b.onclick=()=>{
      const rows=safeJson(localStorage.getItem(OUTLINES_KEY),[]);const r=rows[Number(b.dataset.outlineShare1156)];if(!r)return;
      const text=`${r.title||'Esboço'}\n${r.reference||''}\n\n${r.text||''}`;
      try{if(window.AndroidBridge?.shareText){window.AndroidBridge.shareText(text,'Esboço • Bíblia EBD');return}}catch(_){}
      if(navigator.share)navigator.share({title:'Esboço • Bíblia EBD',text}).catch(()=>{});
    });
  }

  function post(){injectEbd();injectOutlines();patchSavedOutlineActions()}
  window.render=function(){previousRender();requestAnimationFrame(post)};
  window.bind=function(){previousBind();post()};
  window.__EBD_AI_EBD_1156__=Object.freeze({lessonContext:lessonContext1156,open:openAi,prompt:promptFor});
  window.render();
})();
