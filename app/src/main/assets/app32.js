// 1.15.8 — leitura em voz alta, lembrete local da EBD e compartilhamento do professor.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const REMINDER_KEY='ebd-reminder-v1158';
  const REMINDER_ID=1158;

  function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function toastMsg(s){try{if(typeof window.toast==='function')window.toast(s)}catch(_){}}
  function native(){return window.AndroidBridge||null}
  function roleIsProfessor(){return (state.profileV16?.role||state.userMode)==='Professor'}
  function shareText(text,title='Bíblia EBD'){
    if(!text)return toastMsg('Nada para compartilhar.');
    try{if(native()?.shareText){native().shareText(String(text),String(title));return}}catch(_){}
    try{if(navigator.share){navigator.share({title,text:String(text)}).catch(()=>{});return}}catch(_){}
    if(navigator.clipboard?.writeText)navigator.clipboard.writeText(String(text)).then(()=>toastMsg('Texto copiado 📋'));
  }
  function speak(text){
    text=String(text||'').trim();if(!text)return toastMsg('Não há texto para ouvir.');
    try{
      const ok=native()?.speakText?.(text);
      if(ok===false)return toastMsg('A voz do Android não está pronta.');
      toastMsg('Leitura em voz alta iniciada 🔊');
    }catch(_){toastMsg('Leitura em voz alta indisponível neste aparelho.')}
  }
  function stopSpeech(){try{native()?.stopSpeech?.();toastMsg('Leitura pausada ⏹️')}catch(_){}}
  function bibleSpeechText(){
    try{
      const book=state.book||'João',chapter=Number(state.chapter||1),verses=chapterVerses18(book,chapter)||[];
      if(!verses.length)return '';
      const selected=Array.isArray(state.selectedVersesV19)?state.selectedVersesV19.map(Number).filter(Boolean).sort((a,b)=>a-b):[];
      const rows=selected.length?selected.map(v=>`Versículo ${v}. ${verses[v-1]||''}`).filter(x=>x.trim()):verses.map((t,i)=>`Versículo ${i+1}. ${t}`);
      return `${book}, capítulo ${chapter}.\n${rows.join('\n')}`;
    }catch(_){return ''}
  }
  function hymnSpeechText(){
    try{
      const n=Number(state.hymn||1),cat=window.harpaCatalogV18||window.HARPA_CATALOG_V18||[],h=cat.find(x=>Number(x.n)===n),lyrics=typeof lyric191==='function'?lyric191(n):'';
      if(!lyrics.trim())return '';
      return `Harpa Cristã, hino ${n}${h?.title?`, ${h.title}`:''}.\n${lyrics}`;
    }catch(_){return ''}
  }
  function latestAiText(){
    const rows=Array.isArray(state.aiHistory115)?state.aiHistory115:[];
    for(let i=rows.length-1;i>=0;i--)if(rows[i]?.role==='assistant'&&!rows[i]?.error)return String(rows[i].text||'');
    return '';
  }
  function injectReaderAudio(){
    if(state.route!=='reader')return;
    const tools=document.querySelector('.v19-reader-tools');if(!tools||document.getElementById('speakBible1158'))return;
    tools.insertAdjacentHTML('beforeend','<button id="speakBible1158">🔊 Ouvir</button><button id="stopSpeech1158">⏹ Parar</button>');
  }
  function injectHymnAudio(){
    if(state.route!=='hymn')return;
    const bar=document.querySelector('.v191-reading-tools');if(!bar||document.getElementById('speakHymn1158'))return;
    bar.insertAdjacentHTML('beforeend','<button id="speakHymn1158">🔊 Ouvir</button><button id="stopHymnSpeech1158">⏹ Parar</button>');
  }
  function injectAiAudio(){
    if(state.route!=='ai115'||!latestAiText())return;
    const conversation=document.getElementById('aiConversation115');if(!conversation||document.getElementById('speakAi1158'))return;
    conversation.insertAdjacentHTML('beforebegin','<div class="v1158-ai-audio"><button id="speakAi1158">🔊 Ouvir última resposta</button><button id="stopAiSpeech1158">⏹ Parar</button></div>');
  }
  function classSummary(){
    const cls=state.classV17||{};let lesson=null;try{lesson=typeof currentLesson110==='function'?currentLesson110():null}catch(_){}
    const date=typeof nextSunday17==='function'?nextSunday17():'';
    const lines=[
      '📚 Bíblia EBD — Próxima Escola Bíblica',
      `Turma: ${cls.name||'EBD'}`,
      date&&typeof formatDate17==='function'?`Data: ${formatDate17(date)}`:'',
      `Horário: ${cls.time||'09:00'}`,
      `Local: ${cls.room||'Sala principal'}`,
      lesson?`Lição ${lesson.n}: ${lesson.title}`:'',
      lesson?.ref?`Texto-base: ${lesson.ref}`:'',
      '',
      'Esperamos você para estudarmos juntos a Palavra de Deus. 🙏'
    ].filter(Boolean);
    return lines.join('\n');
  }
  function agendaShareText(){
    const cls=state.classV17||{},rows=Array.isArray(state.agendaV17)?state.agendaV17:[],today=new Date().toISOString().slice(0,10);
    const upcoming=rows.filter(x=>x&&x.date>=today).sort((a,b)=>String(a.date).localeCompare(String(b.date))).slice(0,8);
    const lines=['📅 Agenda EBD',`${cls.name||'Turma EBD'} • ${cls.day||'Domingo'} às ${cls.time||'09:00'}`,`Local: ${cls.room||'Sala principal'}`,''];
    if(upcoming.length)upcoming.forEach(x=>lines.push(`• ${typeof formatDate17==='function'?formatDate17(x.date):x.date} — ${x.title||'Compromisso'}`));
    else lines.push('• Próximo encontro da EBD conforme horário da turma.');
    return lines.join('\n');
  }
  function injectClassShare(){
    if(state.route!=='classroom'||!roleIsProfessor())return;
    const app=document.getElementById('app');if(!app||document.getElementById('shareClass1158'))return;
    app.insertAdjacentHTML('afterbegin','<section class="v1158-share"><span>↗️</span><div><strong>Compartilhar convite da turma</strong><small>Envia horário, local e lição — sem lista de alunos.</small></div><button id="shareClass1158">Compartilhar</button></section>');
  }
  function meetingTimestamp(){
    try{
      let date=typeof nextSunday17==='function'?nextSunday17():'';if(!date)return 0;
      const [y,m,d]=date.split('-').map(Number),parts=String(state.classV17?.time||'09:00').split(':').map(Number);
      let dt=new Date(y,m-1,d,parts[0]||9,parts[1]||0,0,0);
      if(dt.getTime()<=Date.now())dt.setDate(dt.getDate()+7);
      return dt.getTime();
    }catch(_){return 0}
  }
  function reminderState(){try{return JSON.parse(localStorage.getItem(REMINDER_KEY)||'null')}catch(_){return null}}
  function scheduleReminder(offset,label){
    const meet=meetingTimestamp();if(!meet)return toastMsg('Não foi possível identificar o próximo encontro.');
    const when=meet-offset;if(when<=Date.now())return toastMsg('Esse horário de lembrete já passou.');
    const cls=state.classV17||{};
    try{
      native()?.requestNotificationPermission?.();
      const ok=native()?.scheduleReminder?.(when,'Bíblia EBD • Próxima aula',`${cls.name||'Turma EBD'} começa ${label==='1 dia antes'?'amanhã':'em cerca de 1 hora'} às ${cls.time||'09:00'}.`,REMINDER_ID);
      if(ok===false)return toastMsg('Não foi possível programar o lembrete.');
      localStorage.setItem(REMINDER_KEY,JSON.stringify({when,meet,offset,label,createdAt:Date.now()}));
      toastMsg(`Lembrete programado: ${label} 🔔`);window.render();
    }catch(_){toastMsg('Lembretes não estão disponíveis neste aparelho.')}
  }
  function cancelReminder(){
    try{native()?.cancelReminder?.(REMINDER_ID)}catch(_){}
    localStorage.removeItem(REMINDER_KEY);toastMsg('Lembrete cancelado.');window.render();
  }
  function reminderCard(){
    const r=reminderState(),meet=meetingTimestamp();
    const meetText=meet?new Date(meet).toLocaleString('pt-BR',{weekday:'long',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}):'próximo encontro';
    return `<section class="v1158-reminder" id="localReminder1158"><div class="head"><span>🔔</span><div><strong>Lembrete local da EBD</strong><small>${esc(meetText)} • funciona sem IA</small></div></div>${r?`<div class="active"><b>✓ Programado ${esc(r.label||'')}</b><button id="cancelReminder1158">Cancelar</button></div>`:`<div class="choices"><button id="remindDay1158">1 dia antes</button><button id="remindHour1158">1 hora antes</button></div>`}<button class="share" id="shareAgenda1158">↗ Compartilhar agenda</button></section>`;
  }
  function injectAgendaReminder(){
    if(state.route!=='agenda'||!roleIsProfessor())return;
    const app=document.getElementById('app');if(!app||document.getElementById('localReminder1158'))return;
    app.insertAdjacentHTML('afterbegin',reminderCard());
  }
  function bind1158(){
    document.getElementById('speakBible1158')?.addEventListener('click',()=>speak(bibleSpeechText()));
    document.getElementById('stopSpeech1158')?.addEventListener('click',stopSpeech);
    document.getElementById('speakHymn1158')?.addEventListener('click',()=>speak(hymnSpeechText()));
    document.getElementById('stopHymnSpeech1158')?.addEventListener('click',stopSpeech);
    document.getElementById('speakAi1158')?.addEventListener('click',()=>speak(latestAiText()));
    document.getElementById('stopAiSpeech1158')?.addEventListener('click',stopSpeech);
    document.getElementById('shareClass1158')?.addEventListener('click',()=>shareText(classSummary(),'Convite EBD'));
    document.getElementById('shareAgenda1158')?.addEventListener('click',()=>shareText(agendaShareText(),'Agenda EBD'));
    document.getElementById('remindDay1158')?.addEventListener('click',()=>scheduleReminder(24*60*60*1000,'1 dia antes'));
    document.getElementById('remindHour1158')?.addEventListener('click',()=>scheduleReminder(60*60*1000,'1 hora antes'));
    document.getElementById('cancelReminder1158')?.addEventListener('click',cancelReminder);
  }
  function post(){injectReaderAudio();injectHymnAudio();injectAiAudio();injectClassShare();injectAgendaReminder();bind1158()}
  window.render=function(){previousRender();requestAnimationFrame(post)};
  window.bind=function(){previousBind();post()};
  window.__EBD_NATIVE_1158__=Object.freeze({bibleSpeechText,hymnSpeechText,classSummary,agendaShareText,meetingTimestamp});
  window.render();
})();
