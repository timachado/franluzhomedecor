const _renderV191 = window.render;
const _bindV191 = window.bind;

state.ebd110Tab = localStorage.getItem('ebd-tab-v110') || 'licoes';
state.ebdCompleted110 = JSON.parse(localStorage.getItem('ebd-completed-v110') || '[]');
state.ebdChecklist110 = JSON.parse(localStorage.getItem('ebd-checklist-v110') || '{}');
state.ebdLesson110 = Number(localStorage.getItem('ebd-current-lesson-v110') || '1');

const EBD_LESSONS_110 = [
 {n:1,date:'2026-07-05',title:'A Palavra que transforma a vida',ref:'Tiago 1:22-25',gold:'Tiago 1:22',truth:'A verdade bíblica produz fruto quando deixa de ser apenas informação e passa a orientar atitudes.',focus:'Ouvir, compreender e praticar a Palavra.',topics:[['Receber a Palavra','O discípulo se aproxima das Escrituras com disposição para aprender e ser corrigido.'],['Olhar com atenção','A leitura cuidadosa revela áreas da vida que precisam ser alinhadas à vontade de Deus.'],['Praticar com constância','A maturidade aparece quando o ensino recebido se transforma em decisões e hábitos.']],questions:['O que diferencia ouvir de praticar?','Qual área da sua rotina precisa responder à Palavra?','Que atitude concreta você pode assumir nesta semana?']},
 {n:2,date:'2026-07-12',title:'Fé que persevera',ref:'Hebreus 11:1-6',gold:'Hebreus 11:6',truth:'A fé bíblica confia no caráter de Deus e permanece firme mesmo quando nem todas as respostas são visíveis.',focus:'Confiança, perseverança e esperança.',topics:[['Fé e confiança','Crer envolve descansar no caráter de Deus, não apenas em circunstâncias favoráveis.'],['Fé que se movimenta','A confiança verdadeira conduz a escolhas coerentes com aquilo que professamos.'],['Fé que permanece','A perseverança amadurece quando continuamos obedecendo durante a espera.']],questions:['Em que situação você precisa perseverar?','Como a fé influencia decisões práticas?','O que ajuda a manter a esperança durante a espera?']},
 {n:3,date:'2026-07-19',title:'Sabedoria para decidir',ref:'Provérbios 3:5-7',gold:'Provérbios 3:5',truth:'Decisões sábias nascem de uma vida que reconhece a direção de Deus e não depende apenas da própria percepção.',focus:'Discernimento nas escolhas do cotidiano.',topics:[['Reconhecer limites','Nem sempre nossa percepção enxerga todas as consequências de uma escolha.'],['Buscar direção','Oração, Escritura e conselho maduro ajudam a organizar prioridades.'],['Caminhar com humildade','Sabedoria inclui disposição para rever caminhos e aprender.']],questions:['Qual decisão exige mais discernimento hoje?','Quem são suas referências maduras para aconselhamento?','Como a Bíblia pode orientar essa escolha?']},
 {n:4,date:'2026-07-26',title:'O valor da comunhão',ref:'Atos 2:42-47',gold:'Atos 2:42',truth:'A igreja cresce de forma saudável quando Palavra, oração, serviço e relacionamento fazem parte da vida comunitária.',focus:'Comunhão cristã e cuidado mútuo.',topics:[['Aprender juntos','A comunidade se fortalece quando o ensino bíblico é compartilhado com constância.'],['Cuidar uns dos outros','Comunhão inclui presença, generosidade e responsabilidade mútua.'],['Testemunhar em unidade','Relacionamentos saudáveis tornam visível a graça que anunciamos.']],questions:['Como fortalecer a comunhão da sua classe?','Que necessidade você pode ajudar a suprir?','O que a unidade comunica para quem está de fora?']},
 {n:5,date:'2026-08-02',title:'Servindo com propósito',ref:'Marcos 10:42-45',gold:'Marcos 10:45',truth:'No Reino de Deus, grandeza não é medida por posição, mas pela disposição de servir com amor e responsabilidade.',focus:'Serviço cristão com humildade.',topics:[['Um modelo diferente','Jesus redefine liderança ao colocar o serviço no centro.'],['Dons em movimento','Cada pessoa pode contribuir com habilidades, tempo e cuidado.'],['Servir sem buscar palco','O propósito do serviço é edificar pessoas e glorificar a Deus.']],questions:['Onde você já pode servir?','Qual dom precisa ser mais desenvolvido?','Como evitar transformar serviço em busca de reconhecimento?']},
 {n:6,date:'2026-08-09',title:'Paz em tempos difíceis',ref:'Filipenses 4:4-9',gold:'Filipenses 4:7',truth:'A paz de Deus não ignora os problemas; ela guarda o coração enquanto aprendemos a orar, pensar e agir com confiança.',focus:'Ansiedade, oração e disciplina dos pensamentos.',topics:[['Levar preocupações a Deus','A oração transforma ansiedade em dependência consciente.'],['Cultivar bons pensamentos','Aquilo que alimentamos na mente influencia emoções e decisões.'],['Praticar o que é saudável','Hábitos espirituais consistentes ajudam a atravessar períodos de pressão.']],questions:['Que preocupação precisa ser apresentada a Deus?','O que tem alimentado seus pensamentos?','Qual hábito pode fortalecer sua paz nesta semana?']},
 {n:7,date:'2026-08-16',title:'Uma mente renovada',ref:'Romanos 12:1-2',gold:'Romanos 12:2',truth:'Transformação cristã envolve permitir que Deus reorganize valores, pensamentos e prioridades.',focus:'Renovação da mente e discernimento.',topics:[['Não viver no automático','O discípulo avalia padrões culturais em vez de apenas repeti-los.'],['Renovar pensamentos','A Palavra oferece novos critérios para interpretar a vida.'],['Discernir a vontade de Deus','Mente renovada produz escolhas mais coerentes com o evangelho.']],questions:['Que padrão precisa ser reavaliado?','Que verdade bíblica precisa ocupar mais espaço na sua mente?','Como discernimento muda suas prioridades?']},
 {n:8,date:'2026-08-23',title:'Firmes na batalha espiritual',ref:'Efésios 6:10-18',gold:'Efésios 6:11',truth:'A vida cristã exige vigilância, dependência de Deus e uso consciente dos recursos espirituais que Ele oferece.',focus:'Vigilância, oração e firmeza.',topics:[['Fortalecer-se no Senhor','Nossa segurança não nasce apenas de força pessoal.'],['Vestir toda a armadura','Verdade, justiça, fé e Palavra precisam estar presentes no cotidiano.'],['Perseverar em oração','Vigilância espiritual é sustentada por uma vida de oração.']],questions:['Onde você percebe maior vulnerabilidade?','Qual aspecto da armadura precisa de atenção?','Como tornar a oração mais constante?']},
 {n:9,date:'2026-08-30',title:'Fruto que revela Cristo',ref:'Gálatas 5:22-25',gold:'Gálatas 5:22',truth:'O caráter cristão amadurece quando o Espírito produz em nós atitudes que refletem a vida de Cristo.',focus:'Caráter e fruto do Espírito.',topics:[['Fruto antes de aparência','Maturidade não se resume a atividade religiosa, mas inclui caráter.'],['Crescimento progressivo','O fruto é cultivado ao longo do tempo em comunhão com Deus.'],['Relacionamentos como campo de prova','Amor, paciência e domínio próprio aparecem especialmente na convivência.']],questions:['Qual aspecto do fruto precisa crescer em você?','Que relacionamento mais desafia seu caráter?','Que prática pode favorecer esse crescimento?']},
 {n:10,date:'2026-09-06',title:'Confiança no cuidado de Deus',ref:'Mateus 6:25-34',gold:'Mateus 6:33',truth:'Confiar no cuidado de Deus nos ajuda a ordenar prioridades sem permitir que a preocupação governe cada decisão.',focus:'Prioridades, provisão e confiança.',topics:[['Preocupação não é direção','A ansiedade pode ocupar energia sem produzir soluções.'],['O Pai conhece necessidades','Confiança cresce quando lembramos quem Deus é.'],['Buscar primeiro o Reino','Prioridades espirituais organizam a maneira como lidamos com necessidades reais.']],questions:['O que mais tem ocupado sua preocupação?','Como diferenciar planejamento de ansiedade?','O que significa buscar primeiro o Reino nesta semana?']},
 {n:11,date:'2026-09-13',title:'Relacionamentos transformados',ref:'Colossenses 3:12-17',gold:'Colossenses 3:13',truth:'A graça recebida de Deus se torna visível quando tratamos pessoas com compaixão, perdão, paciência e amor.',focus:'Perdão, convivência e maturidade.',topics:[['Vestir novas atitudes','Compaixão e humildade precisam ser escolhas conscientes.'],['Aprender a perdoar','Perdão não apaga limites, mas impede que ressentimento governe o coração.'],['Deixar a paz governar','Relacionamentos saudáveis exigem diálogo, gratidão e compromisso com a unidade.']],questions:['Qual atitude precisa mudar em seus relacionamentos?','Existe alguém a quem você precisa oferecer perdão?','Como cultivar conversas mais cheias de graça?']},
 {n:12,date:'2026-09-20',title:'Testemunho com graça',ref:'1 Pedro 3:15-17',gold:'1 Pedro 3:15',truth:'O testemunho cristão combina convicção firme com respeito, mansidão e coerência de vida.',focus:'Defesa da fé e testemunho pessoal.',topics:[['Estar preparado','Conhecer aquilo em que cremos nos ajuda a responder com clareza.'],['Responder com mansidão','A forma da resposta também comunica o evangelho.'],['Viver de modo coerente','Um bom testemunho sustenta aquilo que nossas palavras afirmam.']],questions:['Você consegue explicar sua esperança com simplicidade?','Como responder sem agressividade?','Que área da vida precisa ficar mais coerente com sua mensagem?']},
 {n:13,date:'2026-09-27',title:'Perseverando até o fim',ref:'2 Timóteo 4:6-8',gold:'2 Timóteo 4:7',truth:'A caminhada cristã é uma jornada de fidelidade: começamos pela graça e seguimos firmes até completar a carreira.',focus:'Fidelidade, legado e esperança.',topics:[['Olhar para a caminhada','Reconhecer o caminho percorrido produz gratidão e aprendizado.'],['Combater o bom combate','Perseverança exige escolhas repetidas de fidelidade.'],['Viver com esperança','A expectativa futura fortalece o serviço no presente.']],questions:['Que aprendizados este trimestre deixou?','Onde você precisa permanecer firme?','Que legado espiritual deseja construir?']}
];

function saveEbd110(){
 localStorage.setItem('ebd-tab-v110',state.ebd110Tab);
 localStorage.setItem('ebd-completed-v110',JSON.stringify(state.ebdCompleted110));
 localStorage.setItem('ebd-checklist-v110',JSON.stringify(state.ebdChecklist110));
 localStorage.setItem('ebd-current-lesson-v110',String(state.ebdLesson110||1));
}
function lesson110(n){return EBD_LESSONS_110.find(x=>x.n===Number(n))||EBD_LESSONS_110[0]}
function completed110(n){return state.ebdCompleted110.includes(Number(n))}
function currentLesson110(){
 const today=new Date();today.setHours(0,0,0,0);
 let i=EBD_LESSONS_110.findIndex(l=>new Date(l.date+'T00:00:00')>=today);
 if(i<0)i=EBD_LESSONS_110.length-1;
 return EBD_LESSONS_110[i];
}
function formatDate110(s){return new Date(s+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'})}
function ebdPct110(){return Math.round((state.ebdCompleted110.length/EBD_LESSONS_110.length)*100)}
function checklist110(n){return state.ebdChecklist110[String(n)]||{read:false,reflect:false,note:false,pray:false}}
function toggleChecklist110(n,key){const c=checklist110(n);c[key]=!c[key];state.ebdChecklist110[String(n)]=c;saveEbd110();window.render()}
function openBible110(ref){const p=parseRef19(ref);if(!p)return toast('Referência não encontrada');openParsedV19(p)}
function status110(l){if(completed110(l.n))return 'done';const cur=currentLesson110();if(l.n===cur.n)return 'current';return new Date(l.date)<new Date()?'past':'future'}
function statusLabel110(l){const s=status110(l);return s==='done'?'Concluída':s==='current'?'Próxima aula':s==='past'?'Pendente':'Programada'}
function lessonList110(){return `<div class="v110-lesson-list">${EBD_LESSONS_110.map(l=>`<button data-lesson110="${l.n}" class="${status110(l)}"><span class="v110-lesson-num">${completed110(l.n)?'✓':String(l.n).padStart(2,'0')}</span><div><small>${formatDate110(l.date)} • ${statusLabel110(l)}</small><strong>${esc18(l.title)}</strong><p>${esc18(l.ref)}</p></div><b>›</b></button>`).join('')}</div>`}
function magazineCards110(){
 const list=magazineLibrary.filter(m=>state.userMode==='Professor'||m.edition!=='Professor').sort((a,b)=>(b.year-a.year)||((parseInt(b.quarter)||0)-(parseInt(a.quarter)||0))).slice(0,6);
 return `<div class="v110-mag-row">${list.map(m=>`<button data-mag110="${m.id}"><div>${magazineCoverV14(m)}</div><strong>${esc18(m.title)}</strong><small>${esc18(m.quarter)} ${m.year} • ${esc18(m.edition)}</small></button>`).join('')}</div>`;
}
function professor110(){
 const l=currentLesson110(),c=checklist110(l.n);
 if(state.userMode!=='Professor')return `<section class="v110-role-lock"><div>🧑‍🏫</div><h2>Área do Professor</h2><p>Alterne para o modo Professor para acessar preparação de aula, turma, chamada e agenda.</p><button class="btn btn-primary" id="switchProfessor110">Ativar modo Professor</button></section>`;
 return `<section class="v110-teacher-hero"><span>PLANO DA SEMANA</span><h2>Lição ${String(l.n).padStart(2,'0')} • ${esc18(l.title)}</h2><p>${formatDate110(l.date)} • ${esc18(state.classV17?.time||'09:00')} • ${esc18(state.classV17?.room||'Sala principal')}</p></section>
 <div class="v110-teacher-grid"><button data-route="attendance"><span>✅</span><strong>Chamada</strong><small>Registrar frequência</small></button><button data-route="classroom"><span>👥</span><strong>Turma</strong><small>${state.classV17?.students?.length||0} alunos</small></button><button data-route="agenda"><span>📅</span><strong>Agenda</strong><small>Compromissos</small></button><button data-route="outlines"><span>🗂️</span><strong>Esboços</strong><small>Preparar roteiro</small></button></div>
 <section class="v110-plan"><h3>Roteiro sugerido • 45 minutos</h3><div><b>5 min</b><p>Acolhimento e pergunta de abertura.</p></div><div><b>10 min</b><p>Leitura e observação de ${esc18(l.ref)}.</p></div><div><b>20 min</b><p>Exposição dos três tópicos centrais.</p></div><div><b>7 min</b><p>Perguntas, participação e aplicação.</p></div><div><b>3 min</b><p>Compromisso da semana e oração final.</p></div></section>
 <section class="v110-prep"><h3>Checklist de preparação</h3>${[['read','📖','Ler o texto-base'],['reflect','💡','Revisar objetivos e tópicos'],['note','📝','Preparar anotações'],['pray','🙏','Orar pela classe']].map(([k,ic,tx])=>`<button data-check110="${k}" data-lesson="${l.n}" class="${c[k]?'done':''}"><span>${c[k]?'✓':ic}</span><strong>${tx}</strong></button>`).join('')}</section>`;
}
function calendar110(){return `<div class="pagehead"><button class="back" data-route="ebd">‹</button><div><h1>Calendário EBD</h1><p>3º trimestre de 2026 • 13 domingos.</p></div></div><section class="v110-calendar-head"><div>📅</div><div><span>JULHO — SETEMBRO</span><strong>${state.ebdCompleted110.length} de 13 lições concluídas</strong><small>Progresso salvo neste aparelho</small></div><b>${ebdPct110()}%</b></section>${lessonList110()}`}
function ebdContent110(){
 if(state.ebd110Tab==='revistas')return `<div class="v110-section-title"><div><h2>Biblioteca trimestral</h2><p>Revistas da Bíblia EBD organizadas por classe e edição.</p></div><button id="openAllMag110">Ver todas</button></div>${magazineCards110()}`;
 if(state.ebd110Tab==='professor')return professor110();
 if(state.ebd110Tab==='calendario')return `<div class="v110-section-title"><div><h2>13 domingos de estudo</h2><p>Acompanhe a sequência do trimestre e abra qualquer lição.</p></div></div>${lessonList110()}`;
 return `<div class="v110-section-title"><div><h2>Lições do trimestre</h2><p>Conteúdo original da Bíblia EBD com leitura, aplicação e progresso.</p></div><span>${state.ebdCompleted110.length}/13</span></div>${lessonList110()}`;
}
function ebd110(){
 const cur=currentLesson110(),pct=ebdPct110();
 return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Escola Bíblica Dominical</h1><p>Estudo semanal, revistas e preparação de aula.</p></div></div>
 <section class="v110-current"><div class="v110-current-top"><div><span>PRÓXIMO DOMINGO • LIÇÃO ${String(cur.n).padStart(2,'0')}</span><h2>${esc18(cur.title)}</h2><p>${formatDate110(cur.date)} • ${esc18(cur.ref)}</p></div><div class="v110-ring"><b>${pct}%</b><small>trimestre</small></div></div><div class="v110-progress"><span style="width:${pct}%"></span></div><div class="v110-current-actions"><button class="btn btn-primary" data-lesson110="${cur.n}">📖 Abrir lição</button><button data-bible110="${esc18(cur.ref)}">🔗 Texto-base</button></div></section>
 <div class="v110-role"><span>Modo atual</span><div><button class="${state.userMode==='Aluno'?'active':''}" data-mode110="Aluno">👤 Aluno</button><button class="${state.userMode==='Professor'?'active':''}" data-mode110="Professor">🧑‍🏫 Professor</button></div></div>
 <div class="v110-tabs">${[['licoes','📖 Lições'],['revistas','📚 Revistas'],['professor','🧑‍🏫 Professor'],['calendario','📅 Calendário']].map(([k,l])=>`<button class="${state.ebd110Tab===k?'active':''}" data-ebd110tab="${k}">${l}</button>`).join('')}</div>
 <div class="v110-content">${ebdContent110()}</div>`;
}
function lessonDetail110(){
 const l=lesson110(state.ebdLesson110),c=checklist110(l.n),gold=parseRef19(l.gold),done=completed110(l.n),isTeacher=state.userMode==='Professor';
 return `<div class="pagehead"><button class="back" data-route="ebd">‹</button><div><h1>Lição ${String(l.n).padStart(2,'0')}</h1><p>${formatDate110(l.date)}</p></div></div>
 <section class="v110-lesson-hero"><span>3º TRIMESTRE • 2026</span><h1>${esc18(l.title)}</h1><p>${esc18(l.focus)}</p><button data-bible110="${esc18(l.ref)}">📖 ${esc18(l.ref)}</button></section>
 <section class="v110-golden"><small>TEXTO ÁUREO • ${esc18(l.gold)}</small><blockquote>${esc18(gold?.text||'Abra a passagem para realizar a leitura bíblica.')}</blockquote></section>
 <section class="v110-truth"><span>💡</span><div><small>VERDADE PRÁTICA</small><p>${esc18(l.truth)}</p></div></section>
 <div class="subhead">Objetivos da aula</div><section class="v110-objectives"><div><b>1</b><p>Compreender o ensino central sobre ${esc18(l.focus.toLowerCase())}</p></div><div><b>2</b><p>Relacionar a passagem bíblica com situações reais da vida cristã.</p></div><div><b>3</b><p>Definir uma resposta prática para a semana.</p></div></section>
 <div class="subhead">Desenvolvimento</div><section class="v110-topics">${l.topics.map((t,i)=>`<article><span>${i+1}</span><div><h3>${esc18(t[0])}</h3><p>${esc18(t[1])}</p></div></article>`).join('')}</section>
 <section class="v110-questions"><h3>❓ Para refletir e conversar</h3>${l.questions.map((q,i)=>`<p><b>${i+1}.</b> ${esc18(q)}</p>`).join('')}</section>
 ${isTeacher?`<section class="v110-teacher-note"><span>🧑‍🏫 PLANO DO PROFESSOR</span><h3>Condução sugerida</h3><p>Abra com uma pergunta do cotidiano, faça a leitura do texto-base, desenvolva os três tópicos, permita participação da classe e finalize com uma aplicação concreta.</p><button id="teacherNote110">📝 Criar nota de aula</button></section>`:''}
 <section class="v110-study-check"><h3>Meu estudo desta lição</h3>${[['read','📖','Li o texto-base'],['reflect','💡','Refleti nos tópicos'],['note','📝','Registrei minha aplicação'],['pray','🙏','Orei sobre a lição']].map(([k,ic,tx])=>`<button data-check110="${k}" data-lesson="${l.n}" class="${c[k]?'done':''}"><span>${c[k]?'✓':ic}</span><strong>${tx}</strong></button>`).join('')}</section>
 <div class="v110-lesson-actions"><button class="btn btn-dark" id="lessonNote110">📝 Minha anotação</button><button class="btn ${done?'btn-dark':'btn-primary'}" id="completeLesson110">${done?'✓ Lição concluída':'Marcar como concluída'}</button></div>
 <div class="v110-lesson-nav"><button id="prevLesson110" ${l.n===1?'disabled':''}>‹ Lição ${Math.max(1,l.n-1)}</button><button data-route="ebd">Todas</button><button id="nextLesson110" ${l.n===13?'disabled':''}>Lição ${Math.min(13,l.n+1)} ›</button></div>`;
}
function homeEbd110(){const l=currentLesson110();return `<section class="section v110-home"><div class="v110-home-icon">🎓</div><div><span>EBD • PRÓXIMO DOMINGO</span><strong>Lição ${String(l.n).padStart(2,'0')} • ${esc18(l.title)}</strong><small>${formatDate110(l.date)} • ${ebdPct110()}% do trimestre concluído</small></div><button data-lesson110="${l.n}">Estudar</button></section>`}

window.render=function(){
 if(state.route==='ebd'){$('#app').innerHTML=ebd110();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='lesson'){$('#app').innerHTML=lessonDetail110();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 if(state.route==='ebdCalendar110'){$('#app').innerHTML=calendar110();$$('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
 _renderV191();
 if(state.route==='home'){const app=$('#app');if(app&&!app.querySelector('.v110-home'))app.insertAdjacentHTML('afterbegin',homeEbd110());bindV110()}
};
window.bind=function(){_bindV191();bindV110()};
function goLesson110(n){state.ebdLesson110=Math.max(1,Math.min(13,Number(n)||1));saveEbd110();nav('lesson')}
function bindV110(){
 $$('[data-route]').forEach(e=>e.onclick=()=>nav(e.dataset.route));
 $$('[data-lesson110]').forEach(b=>b.onclick=()=>goLesson110(b.dataset.lesson110));
 $$('[data-ebd110tab]').forEach(b=>b.onclick=()=>{state.ebd110Tab=b.dataset.ebd110tab;saveEbd110();window.render()});
 $$('[data-mode110]').forEach(b=>b.onclick=()=>{state.userMode=b.dataset.mode110;saveV15();window.render()});
 $('#switchProfessor110')?.addEventListener('click',()=>{state.userMode='Professor';saveV15();window.render()});
 $$('[data-bible110]').forEach(b=>b.onclick=()=>openBible110(b.dataset.bible110));
 $$('[data-check110]').forEach(b=>b.onclick=()=>toggleChecklist110(Number(b.dataset.lesson),b.dataset.check110));
 $$('[data-mag110]').forEach(b=>b.onclick=()=>{state.magazineId=b.dataset.mag110;nav('magazine')});
 $('#openAllMag110')?.addEventListener('click',()=>{state.ebdTab='revistas';state.ebd110Tab='revistas';state.magView='all';window.render()});
 $('#lessonNote110')?.addEventListener('click',()=>{const l=lesson110(state.ebdLesson110),note=prompt(`Minha anotação • Lição ${l.n}`,'Minha aplicação:');if(note&&note.trim()){state.notes.unshift({t:`EBD • Lição ${l.n} • ${l.title}`,x:note.trim()});save();toast('Anotação salva 📝')}});
 $('#teacherNote110')?.addEventListener('click',()=>{const l=lesson110(state.ebdLesson110),note=prompt(`Plano do professor • Lição ${l.n}`,'Abertura:\nPontos principais:\nAplicação:\n');if(note&&note.trim()){state.notes.unshift({t:`Plano de aula • Lição ${l.n}`,x:note.trim()});save();toast('Plano salvo 🧑‍🏫')}});
 $('#completeLesson110')?.addEventListener('click',()=>{const n=Number(state.ebdLesson110);state.ebdCompleted110=completed110(n)?state.ebdCompleted110.filter(x=>x!==n):[...state.ebdCompleted110,n].sort((a,b)=>a-b);saveEbd110();toast(completed110(n)?'Lição concluída ✅':'Conclusão removida');window.render()});
 $('#prevLesson110')?.addEventListener('click',()=>goLesson110(Number(state.ebdLesson110)-1));
 $('#nextLesson110')?.addEventListener('click',()=>goLesson110(Number(state.ebdLesson110)+1));
 const menuEbd=[...document.querySelectorAll('.menu-item')].find(x=>x.dataset.route==='ebd');if(menuEbd){const s=menuEbd.querySelector('small');if(s)s.textContent='13 lições • revistas e professor'}
}

window.render();
