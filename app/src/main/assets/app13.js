const _renderV110 = window.render;
const _bindV110 = window.bind;

state.daily111 = JSON.parse(localStorage.getItem('ebd-daily-v111') || '{}');
state.readStats111 = JSON.parse(localStorage.getItem('ebd-readstats-v111') || '{}');
state.planProgress111 = JSON.parse(localStorage.getItem('ebd-plan-progress-v111') || '{}');
state.planDay111 = JSON.parse(localStorage.getItem('ebd-plan-day-v111') || '{}');
state.currentPlan111 = localStorage.getItem('ebd-current-plan-v111') || 'john21';
state.dailyGoal111 = Number(localStorage.getItem('ebd-daily-goal-v111') || '2');

const DAILY_REFS_111 = ['João 3:16','Salmos 23:1','Filipenses 4:6','Isaías 41:10','Romanos 8:28','Provérbios 3:5','Mateus 11:28','Josué 1:9','Salmos 46:1','Jeremias 29:11','2 Coríntios 5:17','Tiago 1:5','Salmos 119:105','Mateus 6:33','Romanos 12:2','Hebreus 11:1','1 Pedro 5:7','Salmos 37:5','Gálatas 5:22','Efésios 2:8','Colossenses 3:15','1 Tessalonicenses 5:17','Apocalipse 21:4','João 14:6'];

function save111(){
 localStorage.setItem('ebd-daily-v111',JSON.stringify(state.daily111));
 localStorage.setItem('ebd-readstats-v111',JSON.stringify(state.readStats111));
 localStorage.setItem('ebd-plan-progress-v111',JSON.stringify(state.planProgress111));
 localStorage.setItem('ebd-plan-day-v111',JSON.stringify(state.planDay111));
 localStorage.setItem('ebd-current-plan-v111',state.currentPlan111);
 localStorage.setItem('ebd-daily-goal-v111',String(state.dailyGoal111));
}
function dateKey111(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function dayOffset111(key,offset){const [y,m,d]=key.split('-').map(Number),x=new Date(y,m-1,d);x.setDate(x.getDate()+offset);return dateKey111(x)}
function dailyVerse111(){
 const k=dateKey111(),seed=[...k].reduce((a,c)=>a+c.charCodeAt(0),0),ref=DAILY_REFS_111[seed%DAILY_REFS_111.length],p=parseRef19(ref);
 return {ref,text:p?.text||'',parsed:p};
}
function dailyState111(key=dateKey111()){return state.daily111[key]||{read:false,reflect:false,pray:false,done:false}}
function toggleDaily111(step){const k=dateKey111(),d=dailyState111(k);d[step]=!d[step];d.done=!!(d.read&&d.reflect&&d.pray);state.daily111[k]=d;save111();window.render()}
function streak111(){
 let n=0,k=dateKey111();
 if(!dailyState111(k).done)k=dayOffset111(k,-1);
 while(state.daily111[k]?.done){n++;k=dayOffset111(k,-1)}
 return n;
}
function trackReader111(){
 if(state.route!=='reader'||!state.book||!state.chapter)return;
 const k=dateKey111(),ref=`${state.book} ${state.chapter}`,row=state.readStats111[k]||{chapters:[]};
 if(!row.chapters.includes(ref)){row.chapters.push(ref);state.readStats111[k]=row;save111()}
}
function todayChapters111(){return (state.readStats111[dateKey111()]?.chapters||[]).length}
function allChapterRefs111(){const out=[];for(const b of BIBLE_META_V18)for(let c=1;c<=b.chapters;c++)out.push({book:b.name,chapter:c});return out}
function split111(items,days){return Array.from({length:days},(_,i)=>items.slice(Math.round(i*items.length/days),Math.round((i+1)*items.length/days)))}
function planData111(id){
 if(id==='john21')return {id,title:'Evangelho de João',days:21,icon:'✨',desc:'Um capítulo por dia para caminhar pelo Evangelho de João.',rows:Array.from({length:21},(_,i)=>[{book:'João',chapter:i+1}])};
 if(id==='psalms30')return {id,title:'30 dias nos Salmos',days:30,icon:'🙏',desc:'Um Salmo por dia para fortalecer oração, confiança e adoração.',rows:Array.from({length:30},(_,i)=>[{book:'Salmos',chapter:i+1}])};
 const all=allChapterRefs111();
 if(id==='nt90'){const start=all.findIndex(x=>x.book==='Mateus');const nt=all.slice(start);return {id,title:'Novo Testamento em 90 dias',days:90,icon:'✝️',desc:'Percorra todo o Novo Testamento em cerca de três capítulos por dia.',rows:split111(nt,90)}};
 return {id:'bible365',title:'Bíblia em 365 dias',days:365,icon:'📖',desc:'Plano anual com toda a Bíblia distribuída em leituras diárias.',rows:split111(all,365)};
}
const PLAN_IDS_111=['john21','psalms30','nt90','bible365'];
function planDoneDays111(id){return state.planProgress111[id]||[]}
function planPct111(id){const p=planData111(id);return Math.round(planDoneDays111(id).length/p.days*100)}
function currentDay111(id){const p=planData111(id),done=planDoneDays111(id),saved=Number(state.planDay111[id]||0);if(saved>=1&&saved<=p.days)return saved;for(let i=1;i<=p.days;i++)if(!done.includes(i))return i;return p.days}
function selectPlan111(id){state.currentPlan111=id;state.planDay111[id]=currentDay111(id);save111();state.route='planDetail111';window.render();scrollTo(0,0)}
function togglePlanDay111(id,day){const a=planDoneDays111(id);state.planProgress111[id]=a.includes(day)?a.filter(x=>x!==day):[...a,day].sort((x,y)=>x-y);state.planDay111[id]=Math.min(planData111(id).days,day+(a.includes(day)?0:1));save111();window.render()}
function openChapter111(book,chapter){state.book=book;state.chapter=Number(chapter);state.selectedVersesV19=[];state.studyVerseV19=null;nav('reader')}
function formatRefs111(rows){return rows.map(r=>`${r.book} ${r.chapter}`).join(' • ')}

function dailyPage111(){
 const v=dailyVerse111(),d=dailyState111(),done=d.done,chap=todayChapters111(),goal=state.dailyGoal111;
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Minha rotina</h1><p>Um passo por dia na Palavra.</p></div></div>
 <section class="v111-daily-hero ${done?'done':''}"><div class="v111-daily-top"><div><span>VERSÍCULO DO DIA</span><h2>${esc18(v.ref)}</h2></div><div class="v111-streak">🔥<b>${streak111()}</b><small>dias</small></div></div><blockquote>${esc18(v.text)}</blockquote><div class="v111-daily-actions"><button id="openDailyVerse111">📖 Abrir</button><button id="copyDaily111">📋 Copiar</button><button id="favDaily111">${v.parsed&&isVerseFav18(v.ref)?'❤️':'🤍'} Favorito</button></div></section>
 <section class="v111-checks"><h3>Rotina de hoje</h3>${[['read','📖','Ler e observar','Leia a passagem com calma.'],['reflect','💡','Refletir','Pense em uma aplicação prática.'],['pray','🙏','Orar','Converse com Deus sobre o que leu.']].map(([k,ic,t,s])=>`<button data-daily111="${k}" class="${d[k]?'done':''}"><span>${d[k]?'✓':ic}</span><div><strong>${t}</strong><small>${s}</small></div></button>`).join('')}</section>
 <section class="v111-goal"><div><span>META DE LEITURA</span><strong>${chap} de ${goal} capítulo${goal>1?'s':''} hoje</strong><small>${chap>=goal?'Meta alcançada 🎉':'Cada capítulo aberto conta automaticamente.'}</small></div><div class="v111-goalbar"><i style="width:${Math.min(100,Math.round(chap/goal*100))}%"></i></div><div class="v111-goal-options">${[1,2,3,5].map(n=>`<button data-goal111="${n}" class="${goal===n?'active':''}">${n}/dia</button>`).join('')}</div></section>
 <div class="v111-shortcuts"><button data-route="plans111"><span>🗓️</span><strong>Planos de leitura</strong><small>21, 30, 90 ou 365 dias</small></button><button data-route="stats111"><span>📊</span><strong>Meu progresso</strong><small>Sequência e últimos 7 dias</small></button></div>`;
}
function plansPage111(){
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Planos de leitura</h1><p>Escolha uma jornada e acompanhe seu progresso offline.</p></div></div>
 <section class="v111-plan-intro"><span>🗓️</span><div><small>PLANOS PESSOAIS</small><strong>Leitura com começo, meio e fim</strong><p>Seu progresso fica salvo neste aparelho.</p></div></section>
 <div class="v111-plan-grid">${PLAN_IDS_111.map(id=>{const p=planData111(id),pct=planPct111(id),cur=currentDay111(id);return `<button data-plan111="${id}" class="${state.currentPlan111===id?'current':''}"><span>${p.icon}</span><div><small>${p.days} DIAS</small><strong>${p.title}</strong><p>${p.desc}</p><div class="v111-plan-progress"><i style="width:${pct}%"></i></div><em>${pct}% • dia ${cur}</em></div><b>›</b></button>`}).join('')}</div>`;
}
function planDetail111(){
 const id=state.currentPlan111,p=planData111(id),day=Math.max(1,Math.min(p.days,Number(state.planDay111[id]||currentDay111(id)))),rows=p.rows[day-1]||[],done=planDoneDays111(id).includes(day),pct=planPct111(id);
 const around=[];for(let i=Math.max(1,day-3);i<=Math.min(p.days,day+3);i++)around.push(i);
 return `<div class="pagehead"><button class="back" data-route="plans111">‹</button><div><h1>${esc18(p.title)}</h1><p>${p.days} dias • ${pct}% concluído</p></div></div>
 <section class="v111-plan-hero"><div><span>${p.icon}</span><div><small>DIA ${day} DE ${p.days}</small><h2>${esc18(formatRefs111(rows))}</h2><p>${esc18(p.desc)}</p></div></div><div class="v111-plan-progress big"><i style="width:${pct}%"></i></div></section>
 <div class="v111-day-strip">${around.map(n=>`<button data-planday111="${n}" class="${n===day?'active':''} ${planDoneDays111(id).includes(n)?'done':''}"><small>DIA</small><b>${n}</b></button>`).join('')}</div>
 <section class="v111-reading-list"><h3>Leitura de hoje</h3>${rows.map((r,i)=>`<button data-openplanref111 data-book="${esc18(r.book)}" data-chapter="${r.chapter}"><span>${i+1}</span><div><strong>${esc18(r.book)} ${r.chapter}</strong><small>Abrir capítulo completo</small></div><b>›</b></button>`).join('')}</section>
 <div class="v111-plan-actions"><button class="btn btn-primary" id="startPlanReading111">📖 Começar leitura</button><button class="btn ${done?'btn-dark':'btn-primary'}" id="completePlanDay111">${done?'✓ Dia concluído':'Marcar dia como concluído'}</button></div>
 <div class="v111-plan-nav"><button id="prevPlanDay111" ${day<=1?'disabled':''}>‹ Dia ${Math.max(1,day-1)}</button><button id="nextPlanDay111" ${day>=p.days?'disabled':''}>Dia ${Math.min(p.days,day+1)} ›</button></div>`;
}
function statsPage111(){
 const today=dateKey111(),days=Array.from({length:7},(_,i)=>dayOffset111(today,i-6)),goal=state.dailyGoal111,total=Object.values(state.readStats111).reduce((a,r)=>a+(r.chapters?.length||0),0),complete=Object.values(state.daily111).filter(x=>x.done).length;
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Meu progresso</h1><p>Estudo e constância neste aparelho.</p></div></div>
 <div class="v111-stat-cards"><article><span>🔥</span><b>${streak111()}</b><small>sequência atual</small></article><article><span>📖</span><b>${total}</b><small>capítulos registrados</small></article><article><span>✅</span><b>${complete}</b><small>rotinas completas</small></article></div>
 <section class="v111-week"><div class="v111-section-head"><div><span>ÚLTIMOS 7 DIAS</span><strong>Capítulos lidos</strong></div><small>meta ${goal}/dia</small></div><div class="v111-bars">${days.map(k=>{const n=state.readStats111[k]?.chapters?.length||0;const d=new Date(k+'T12:00:00');return `<div><div class="v111-bar"><i style="height:${Math.min(100,Math.round(n/goal*100))}%"></i></div><b>${n}</b><small>${d.toLocaleDateString('pt-BR',{weekday:'short'}).replace('.','')}</small></div>`}).join('')}</div></section>
 <section class="v111-plans-summary"><div class="v111-section-head"><div><span>MEUS PLANOS</span><strong>Progresso das jornadas</strong></div><button data-route="plans111">Abrir</button></div>${PLAN_IDS_111.map(id=>{const p=planData111(id),pct=planPct111(id);return `<button data-plan111="${id}"><span>${p.icon}</span><div><strong>${p.title}</strong><div><i style="width:${pct}%"></i></div><small>${planDoneDays111(id).length}/${p.days} dias</small></div><b>${pct}%</b></button>`}).join('')}</section>`;
}
function homeRoutine111(){const v=dailyVerse111(),done=dailyState111().done,chap=todayChapters111(),goal=state.dailyGoal111;return `<section class="section v111-home"><div class="v111-home-icon">${done?'✅':'🔥'}</div><div><span>ROTINA DE HOJE • ${streak111()} DIA${streak111()===1?'':'S'} DE SEQUÊNCIA</span><strong>${esc18(v.ref)} • ${chap}/${goal} capítulos</strong><small>${done?'Rotina concluída. Continue firme!':'Versículo do dia, leitura, reflexão e oração.'}</small></div><button data-route="daily111">Abrir</button></section>`}
function homePlan111(){const p=planData111(state.currentPlan111),day=currentDay111(p.id),pct=planPct111(p.id);return `<section class="section v111-home-plan"><div>🗓️</div><div><span>PLANO ATUAL</span><strong>${esc18(p.title)}</strong><small>Dia ${day} de ${p.days} • ${pct}% concluído</small></div><button data-plan111="${p.id}">Continuar</button></section>`}

window.render=function(){
 if(state.route==='daily111'){$('#app').innerHTML=dailyPage111();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='plans111'){$('#app').innerHTML=plansPage111();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='planDetail111'){$('#app').innerHTML=planDetail111();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='stats111'){$('#app').innerHTML=statsPage111();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 _renderV110();
 trackReader111();
 if(state.route==='home'){
  const app=$('#app');
  if(app&&!app.querySelector('.v111-home-plan'))app.insertAdjacentHTML('afterbegin',homePlan111());
  if(app&&!app.querySelector('.v111-home'))app.insertAdjacentHTML('afterbegin',homeRoutine111());
  bindV111();
 }
};
window.bind=function(){_bindV110();bindV111()};
function bindV111(){
 $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
 $$('[data-daily111]').forEach(b=>b.onclick=()=>toggleDaily111(b.dataset.daily111));
 $$('[data-goal111]').forEach(b=>b.onclick=()=>{state.dailyGoal111=Number(b.dataset.goal111);save111();window.render()});
 $$('[data-plan111]').forEach(b=>b.onclick=()=>selectPlan111(b.dataset.plan111));
 $$('[data-planday111]').forEach(b=>b.onclick=()=>{state.planDay111[state.currentPlan111]=Number(b.dataset.planday111);save111();window.render()});
 $$('[data-openplanref111]').forEach(b=>b.onclick=()=>openChapter111(b.dataset.book,b.dataset.chapter));
 const v=dailyVerse111();
 $('#openDailyVerse111')?.addEventListener('click',()=>v.parsed&&openParsedV19(v.parsed));
 $('#copyDaily111')?.addEventListener('click',()=>copy18(`${v.ref} — ${v.text}`));
 $('#favDaily111')?.addEventListener('click',()=>{if(v.parsed){toggleVerseFav18(v.ref,v.text);window.render()}});
 $('#startPlanReading111')?.addEventListener('click',()=>{const p=planData111(state.currentPlan111),d=Number(state.planDay111[p.id]||currentDay111(p.id)),r=p.rows[d-1]?.[0];if(r)openChapter111(r.book,r.chapter)});
 $('#completePlanDay111')?.addEventListener('click',()=>{const id=state.currentPlan111,d=Number(state.planDay111[id]||currentDay111(id));togglePlanDay111(id,d);toast(planDoneDays111(id).includes(d)?'Dia concluído ✅':'Conclusão removida')});
 $('#prevPlanDay111')?.addEventListener('click',()=>{const id=state.currentPlan111;state.planDay111[id]=Math.max(1,Number(state.planDay111[id]||1)-1);save111();window.render()});
 $('#nextPlanDay111')?.addEventListener('click',()=>{const id=state.currentPlan111,p=planData111(id);state.planDay111[id]=Math.min(p.days,Number(state.planDay111[id]||1)+1);save111();window.render()});
 const menu=document.querySelector('.menu-grid');
 if(menu&&!menu.querySelector('[data-route="daily111"]')){
  menu.insertAdjacentHTML('afterbegin','<button class="menu-item" data-route="daily111"><span>🔥</span><strong>Minha Rotina</strong><small>Versículo, meta e sequência</small></button><button class="menu-item" data-route="plans111"><span>🗓️</span><strong>Planos de Leitura</strong><small>21, 30, 90 ou 365 dias</small></button>');
  $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
 }
}

window.render();
