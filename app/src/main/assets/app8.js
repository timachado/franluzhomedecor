const _renderV16=window.render;
const _bindV16=window.bind;

state.classV17=JSON.parse(localStorage.getItem('ebd-class-v17')||'null')||{
  name:(state.profileV16?.className||'Adultos'),teacher:(state.profileV16?.name||'Professor'),room:'Sala principal',day:'Domingo',time:'09:00',
  students:['Ana Souza','Bruno Lima','Carla Mendes','Daniel Rocha','Ester Alves']
};
state.attendanceV17=JSON.parse(localStorage.getItem('ebd-attendance-v17')||'{}');
state.agendaV17=JSON.parse(localStorage.getItem('ebd-agenda-v17')||'[]');
state.notificationsV17=JSON.parse(localStorage.getItem('ebd-notifications-v17')||'null')||[
  {id:'welcome17',icon:'🎓',title:'Sua Escola Bíblica está organizada',text:'Turma, chamada e agenda já podem ser usadas neste aparelho.',read:false},
  {id:'mag17',icon:'📚',title:'Revistas EBD disponíveis',text:'Continue suas revistas e acompanhe o progresso de leitura.',read:false},
  {id:'backup17',icon:'☁️',title:'Proteja suas anotações',text:'Use Backup no Perfil para guardar seus dados locais.',read:true}
];

function saveV17(){
  localStorage.setItem('ebd-class-v17',JSON.stringify(state.classV17));
  localStorage.setItem('ebd-attendance-v17',JSON.stringify(state.attendanceV17));
  localStorage.setItem('ebd-agenda-v17',JSON.stringify(state.agendaV17));
  localStorage.setItem('ebd-notifications-v17',JSON.stringify(state.notificationsV17));
}
function esc17(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function iso17(d){return d.toISOString().slice(0,10)}
function formatDate17(x){const d=new Date(x+'T12:00:00');return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'})}
function nextSunday17(){const d=new Date();d.setHours(12,0,0,0);const add=(7-d.getDay())%7;d.setDate(d.getDate()+add);return iso17(d)}
function unread17(){return state.notificationsV17.filter(n=>!n.read).length}
function currentRole17(){return state.profileV16?.role||state.userMode||'Aluno'}
function attendanceFor17(date){
  const saved=state.attendanceV17[date]||{};
  const obj={};state.classV17.students.forEach(s=>obj[s]=saved[s]||'present');return obj;
}
function attendancePct17(date){const a=attendanceFor17(date),v=Object.values(a);return v.length?Math.round(v.filter(x=>x==='present').length/v.length*100):0}

function homeAddon17(){
  const date=nextSunday17(),pct=attendancePct17(date),role=currentRole17();
  return `<section class="section v17-home-ebd"><div class="section-title"><div><h2>Próxima Escola Bíblica</h2><small>${formatDate17(date)} • ${esc17(state.classV17.time)}</small></div><span class="v17-role">${role==='Professor'?'🧑‍🏫':'👤'} ${role}</span></div>
  <article class="v17-next-card"><div class="v17-next-icon">🎓</div><div class="v17-next-main"><span>${esc17(state.classV17.name)}</span><strong>Lição 01 • A Palavra que transforma a vida</strong><small>${esc17(state.classV17.room)} • ${esc17(state.classV17.teacher)}</small></div><button data-route="classroom">Abrir</button></article>
  <div class="v17-home-actions"><button data-route="attendance">✅ Chamada</button><button data-route="agenda">📅 Agenda</button><button data-route="notifications">🔔 Avisos ${unread17()?`<b>${unread17()}</b>`:''}</button></div></section>`;
}
function ebdAddon17(){return `<section class="v17-ebd-tools"><div><span class="tiny-label">GESTÃO DA EBD</span><h3>Minha turma</h3><p>Organize horário, alunos, chamada e próximos encontros.</p></div><div class="v17-ebd-grid"><button data-route="classroom"><span>🎓</span><strong>Turma</strong><small>${state.classV17.students.length} alunos</small></button><button data-route="attendance"><span>✅</span><strong>Chamada</strong><small>Presença</small></button><button data-route="agenda"><span>📅</span><strong>Agenda</strong><small>Domingos</small></button><button data-route="notifications"><span>🔔</span><strong>Avisos</strong><small>${unread17()} novos</small></button></div></section>`}

function classroom17(){
  const professor=currentRole17()==='Professor';
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Minha Turma</h1><p>Organização local da Escola Bíblica Dominical.</p></div></div>
  <section class="v17-class-hero"><div class="v17-class-icon">🎓</div><div><span>${professor?'MODO PROFESSOR':'MODO ALUNO'}</span><h2>${esc17(state.classV17.name)}</h2><p>${esc17(state.classV17.day)} • ${esc17(state.classV17.time)} • ${esc17(state.classV17.room)}</p></div></section>
  <section class="v17-class-info"><div><small>Professor</small><strong>${esc17(state.classV17.teacher)}</strong></div><div><small>Alunos</small><strong>${state.classV17.students.length}</strong></div><div><small>Próximo encontro</small><strong>${formatDate17(nextSunday17())}</strong></div></section>
  ${professor?`<section class="form-card v17-class-form"><h3>Configurações da turma</h3><label>Nome da turma</label><input class="field" id="v17ClassName" value="${esc17(state.classV17.name)}"><div class="v17-two"><div><label>Horário</label><input class="field" id="v17ClassTime" type="time" value="${esc17(state.classV17.time)}"></div><div><label>Sala</label><input class="field" id="v17ClassRoom" value="${esc17(state.classV17.room)}"></div></div><label>Professor</label><input class="field" id="v17ClassTeacher" value="${esc17(state.classV17.teacher)}"><button class="btn btn-primary" id="saveClass17">Salvar turma</button></section>`:''}
  <div class="subhead">Alunos da turma</div><section class="v17-student-list">${state.classV17.students.map((s,i)=>`<article><div class="v17-student-avatar">${esc17(s.charAt(0))}</div><div><strong>${esc17(s)}</strong><small>Aluno da EBD</small></div>${professor?`<button data-remove-student17="${i}">×</button>`:''}</article>`).join('')}</section>
  ${professor?`<button class="v17-add-student" id="addStudent17">＋ Adicionar aluno</button>`:`<div class="v17-info-note">👤 No modo Aluno, a lista é somente para consulta. A chamada é registrada pelo professor.</div>`}
  <div class="v17-class-actions"><button data-route="attendance">✅ Fazer chamada</button><button data-route="agenda">📅 Ver agenda</button></div>`;
}
function attendance17(){
  const professor=currentRole17()==='Professor',date=state.attendanceDate17||nextSunday17(),a=attendanceFor17(date),pct=attendancePct17(date);
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Chamada EBD</h1><p>Presença da turma por domingo.</p></div></div>
  <section class="v17-att-head"><div><span class="tiny-label">ENCONTRO</span><h2>${formatDate17(date)}</h2><p>${esc17(state.classV17.name)} • ${esc17(state.classV17.time)}</p></div><div class="v17-att-ring"><b>${pct}%</b><small>presença</small></div></section>
  <div class="v17-date-row"><button id="prevSunday17">‹</button><input class="field" id="attendanceDate17" type="date" value="${date}"><button id="nextSunday17">›</button></div>
  ${professor?`<section class="v17-att-list">${state.classV17.students.map(s=>`<article><div><strong>${esc17(s)}</strong><small>${a[s]==='present'?'Presente':'Ausente'}</small></div><div class="v17-presence"><button class="${a[s]==='present'?'active present':''}" data-att17="present" data-student17="${esc17(s)}">✓</button><button class="${a[s]==='absent'?'active absent':''}" data-att17="absent" data-student17="${esc17(s)}">×</button></div></article>`).join('')}</section><button class="btn btn-primary v17-save-att" id="saveAttendance17">Salvar chamada</button>`:`<section class="v17-info-note">✅ A frequência desta turma é registrada pelo professor. Você pode consultar o percentual geral do encontro.</section>`}
  <section class="v17-att-summary"><div><b>${Object.values(a).filter(x=>x==='present').length}</b><small>presentes</small></div><div><b>${Object.values(a).filter(x=>x==='absent').length}</b><small>ausentes</small></div><div><b>${state.classV17.students.length}</b><small>matriculados</small></div></section>`;
}
function agenda17(){
  const base=[{id:'lesson01',date:nextSunday17(),icon:'🎓',title:'EBD • Lição 01',text:'A Palavra que transforma a vida',fixed:true}];
  const all=[...base,...state.agendaV17].sort((a,b)=>a.date.localeCompare(b.date));
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Agenda da EBD</h1><p>Domingos, lições e lembretes da turma.</p></div></div>
  <section class="v17-agenda-hero"><span>📅</span><div><small>PRÓXIMO DOMINGO</small><h2>${formatDate17(nextSunday17())}</h2><p>${esc17(state.classV17.time)} • ${esc17(state.classV17.room)}</p></div></section>
  ${currentRole17()==='Professor'?`<section class="form-card v17-agenda-form"><h3>Novo compromisso</h3><div class="v17-two"><input class="field" id="agendaDate17" type="date" value="${nextSunday17()}"><input class="field" id="agendaTitle17" placeholder="Título"></div><textarea class="field" id="agendaText17" placeholder="Observação, material ou lembrete..."></textarea><button class="btn btn-primary" id="addAgenda17">Adicionar à agenda</button></section>`:''}
  <div class="subhead">Próximos compromissos</div><section class="v17-agenda-list">${all.map(e=>`<article><div class="v17-agenda-date"><b>${new Date(e.date+'T12:00:00').getDate()}</b><small>${new Date(e.date+'T12:00:00').toLocaleDateString('pt-BR',{month:'short'})}</small></div><div class="v17-agenda-body"><span>${e.icon||'📌'} ${esc17(e.title)}</span><p>${esc17(e.text||'')}</p></div>${!e.fixed&&currentRole17()==='Professor'?`<button data-del-agenda17="${e.id}">×</button>`:''}</article>`).join('')}</section>`;
}
function notifications17(){
  return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Notificações</h1><p>Avisos internos da Bíblia EBD.</p></div></div>
  <div class="v17-notif-tools"><span>${unread17()} não lidas</span><div><button id="readAll17">Marcar todas como lidas</button><button id="clearRead17">Limpar lidas</button></div></div>
  <section class="v17-notif-list">${state.notificationsV17.length?state.notificationsV17.map(n=>`<article class="${n.read?'read':''}" data-notif17="${n.id}"><div class="v17-notif-icon">${n.icon}</div><div><strong>${esc17(n.title)}</strong><p>${esc17(n.text)}</p><small>${n.read?'Lida':'Nova'}</small></div><button data-del-notif17="${n.id}">×</button></article>`).join(''):`<div class="empty"><div class="big">🔔</div><strong>Nenhuma notificação</strong><p>Os próximos avisos aparecerão aqui.</p></div>`}</section>
  <div class="v17-info-note">📱 Estes avisos são internos e funcionam sem internet. Push real entre aparelhos será conectado junto com a conta online.</div>`;
}

window.render=function(){
  if(state.route==='classroom'){$('#app').innerHTML=classroom17();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='attendance'){$('#app').innerHTML=attendance17();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='agenda'){$('#app').innerHTML=agenda17();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  if(state.route==='notifications'){$('#app').innerHTML=notifications17();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
  _renderV16();
  if(state.route==='home'){const app=$('#app');if(app&&!app.querySelector('.v17-home-ebd'))app.insertAdjacentHTML('beforeend',homeAddon17());bindV17Extra()}
  if(state.route==='ebd'){const app=$('#app');if(app&&!app.querySelector('.v17-ebd-tools'))app.insertAdjacentHTML('afterbegin',ebdAddon17());bindV17Extra()}
};
window.bind=function(){_bindV16();bindV17Extra()};
function bindV17Extra(){
  $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
  const bell=$('#bell');if(bell){bell.onclick=()=>nav('notifications');bell.innerHTML=unread17()?`🔔<i class="v17-bell-badge">${unread17()}</i>`:'🔔'}
  const sc=$('#saveClass17');if(sc)sc.onclick=()=>{state.classV17.name=$('#v17ClassName').value.trim()||'Adultos';state.classV17.time=$('#v17ClassTime').value||'09:00';state.classV17.room=$('#v17ClassRoom').value.trim()||'Sala principal';state.classV17.teacher=$('#v17ClassTeacher').value.trim()||state.profileV16?.name||'Professor';saveV17();toast('Turma salva ✅');window.render()};
  const add=$('#addStudent17');if(add)add.onclick=()=>{const n=prompt('Nome do aluno','');if(n&&n.trim()){state.classV17.students.push(n.trim());saveV17();toast('Aluno adicionado');window.render()}};
  $$('[data-remove-student17]').forEach(b=>b.onclick=()=>{const i=Number(b.dataset.removeStudent17);state.classV17.students.splice(i,1);saveV17();window.render()});
  const date=$('#attendanceDate17');if(date)date.onchange=()=>{state.attendanceDate17=date.value;window.render()};
  const ps=$('#prevSunday17');if(ps)ps.onclick=()=>{const d=new Date((state.attendanceDate17||nextSunday17())+'T12:00:00');d.setDate(d.getDate()-7);state.attendanceDate17=iso17(d);window.render()};
  const ns=$('#nextSunday17');if(ns)ns.onclick=()=>{const d=new Date((state.attendanceDate17||nextSunday17())+'T12:00:00');d.setDate(d.getDate()+7);state.attendanceDate17=iso17(d);window.render()};
  $$('[data-att17]').forEach(b=>b.onclick=()=>{const d=state.attendanceDate17||nextSunday17(),student=b.dataset.student17;state.attendanceV17[d]=state.attendanceV17[d]||{};state.attendanceV17[d][student]=b.dataset.att17;saveV17();window.render()});
  const sa=$('#saveAttendance17');if(sa)sa.onclick=()=>{saveV17();state.notificationsV17.unshift({id:'att'+Date.now(),icon:'✅',title:'Chamada salva',text:`Frequência de ${formatDate17(state.attendanceDate17||nextSunday17())}: ${attendancePct17(state.attendanceDate17||nextSunday17())}%`,read:false});saveV17();toast('Chamada salva ✅');window.render()};
  const aa=$('#addAgenda17');if(aa)aa.onclick=()=>{const t=$('#agendaTitle17').value.trim();if(!t)return toast('Digite um título');state.agendaV17.push({id:'ev'+Date.now(),date:$('#agendaDate17').value||nextSunday17(),icon:'📌',title:t,text:$('#agendaText17').value.trim()});saveV17();toast('Compromisso adicionado 📅');window.render()};
  $$('[data-del-agenda17]').forEach(b=>b.onclick=()=>{state.agendaV17=state.agendaV17.filter(e=>e.id!==b.dataset.delAgenda17);saveV17();window.render()});
  $$('[data-notif17]').forEach(a=>a.onclick=e=>{if(e.target.closest('[data-del-notif17]'))return;const n=state.notificationsV17.find(x=>x.id===a.dataset.notif17);if(n){n.read=true;saveV17();window.render()}});
  $$('[data-del-notif17]').forEach(b=>b.onclick=e=>{e.stopPropagation();state.notificationsV17=state.notificationsV17.filter(n=>n.id!==b.dataset.delNotif17);saveV17();window.render()});
  const ra=$('#readAll17');if(ra)ra.onclick=()=>{state.notificationsV17.forEach(n=>n.read=true);saveV17();window.render()};
  const cr=$('#clearRead17');if(cr)cr.onclick=()=>{state.notificationsV17=state.notificationsV17.filter(n=>!n.read);saveV17();window.render()};
}

window.render();