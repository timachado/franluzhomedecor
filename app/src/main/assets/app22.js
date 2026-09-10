// 1.14.0 — Central de Ministério & Estudo (offline)
(function(){
  const oldRender114=window.render;
  const oldBind114=window.bind;
  const app114=()=>document.getElementById('app');
  const esc114=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));

  const PLACES114=[
    {id:'jerusalem',name:'Jerusalém',region:'Judeia',icon:'🏛️',x:57,y:54,summary:'Centro de adoração de Israel e cenário decisivo do ministério, morte e ressurreição de Jesus.',refs:['2 Samuel 5','Salmos 122','Lucas 19','Atos 2']},
    {id:'belem',name:'Belém',region:'Judeia',icon:'⭐',x:55,y:61,summary:'Cidade ligada a Davi e ao nascimento de Jesus.',refs:['Rute 1','1 Samuel 16','Miqueias 5:2','Mateus 2']},
    {id:'nazare',name:'Nazaré',region:'Galileia',icon:'🏠',x:49,y:30,summary:'Cidade onde Jesus cresceu e iniciou sua vida pública entre conhecidos.',refs:['Mateus 2:23','Lucas 2:39','Lucas 4']},
    {id:'cafarnaum',name:'Cafarnaum',region:'Galileia',icon:'⛵',x:57,y:23,summary:'Importante base do ministério de Jesus na Galileia.',refs:['Mateus 4:13','Marcos 1','João 6']},
    {id:'jerico',name:'Jericó',region:'Vale do Jordão',icon:'🌴',x:66,y:54,summary:'Cidade associada à conquista de Canaã e a encontros marcantes de Jesus.',refs:['Josué 6','Lucas 10:30','Lucas 19']},
    {id:'hebron',name:'Hebrom',region:'Judá',icon:'⛰️',x:49,y:70,summary:'Lugar ligado aos patriarcas e ao início do reinado de Davi sobre Judá.',refs:['Gênesis 13:18','Gênesis 23','2 Samuel 2']},
    {id:'samaria',name:'Samaria',region:'Samaria',icon:'🏘️',x:51,y:41,summary:'Região central importante na história do reino do Norte e na expansão do evangelho.',refs:['1 Reis 16:24','João 4','Atos 8']},
    {id:'damasco',name:'Damasco',region:'Síria',icon:'🛤️',x:75,y:14,summary:'Cidade antiga conhecida no Novo Testamento pela conversão de Saulo no caminho.',refs:['Atos 9','Atos 22','Atos 26']},
    {id:'sinai',name:'Sinai',region:'Deserto',icon:'⛰️',x:39,y:91,summary:'Região tradicionalmente relacionada à aliança e à entrega da Lei a Israel.',refs:['Êxodo 19','Êxodo 20','Deuteronômio 5']},
    {id:'egito',name:'Egito',region:'Nordeste da África',icon:'🏺',x:18,y:84,summary:'Terra presente desde os patriarcas, no Êxodo e na infância de Jesus.',refs:['Gênesis 46','Êxodo 1','Mateus 2:13']},
    {id:'babilonia',name:'Babilônia',region:'Mesopotâmia',icon:'🏙️',x:91,y:34,summary:'Potência ligada ao exílio de Judá e ao ministério de Daniel.',refs:['2 Reis 25','Daniel 1','Salmos 137']},
    {id:'antioquia',name:'Antioquia',region:'Síria',icon:'🌍',x:74,y:5,summary:'Centro missionário fundamental da igreja primitiva.',refs:['Atos 11','Atos 13','Atos 14']}
  ];

  const PEOPLE114=[
    {id:'abraao',name:'Abraão',icon:'⛺',era:'Patriarcas',summary:'Chamado por Deus para viver pela fé e tornar-se referência da promessa e da aliança.',refs:['Gênesis 12','Gênesis 15','Gênesis 22','Romanos 4']},
    {id:'moises',name:'Moisés',icon:'📜',era:'Êxodo',summary:'Líder do Êxodo e mediador da aliança do Sinai.',refs:['Êxodo 3','Êxodo 14','Êxodo 20','Deuteronômio 34']},
    {id:'josue',name:'Josué',icon:'🛡️',era:'Conquista',summary:'Sucessor de Moisés que liderou Israel na entrada em Canaã.',refs:['Josué 1','Josué 6','Josué 24']},
    {id:'davi',name:'Davi',icon:'👑',era:'Monarquia',summary:'Pastor, guerreiro e rei, figura central na história de Israel e na esperança messiânica.',refs:['1 Samuel 16','1 Samuel 17','2 Samuel 7','Salmos 23']},
    {id:'salomao',name:'Salomão',icon:'⚖️',era:'Monarquia',summary:'Rei conhecido por sabedoria e pela construção do templo em Jerusalém.',refs:['1 Reis 3','1 Reis 8','Provérbios 1']},
    {id:'elias',name:'Elias',icon:'🔥',era:'Profetas',summary:'Profeta que confrontou a idolatria e chamou Israel de volta à fidelidade a Deus.',refs:['1 Reis 17','1 Reis 18','2 Reis 2']},
    {id:'daniel',name:'Daniel',icon:'🦁',era:'Exílio',summary:'Servo fiel no exílio babilônico, conhecido por integridade, oração e visões proféticas.',refs:['Daniel 1','Daniel 6','Daniel 7']},
    {id:'ester',name:'Ester',icon:'👸',era:'Império Persa',summary:'Rainha que agiu com coragem em favor de seu povo.',refs:['Ester 4','Ester 7','Ester 9']},
    {id:'joao-batista',name:'João Batista',icon:'🌊',era:'Evangelhos',summary:'Precursor de Jesus que anunciou arrependimento e preparou o caminho do Senhor.',refs:['Mateus 3','João 1']},
    {id:'pedro',name:'Pedro',icon:'🔑',era:'Igreja Primitiva',summary:'Discípulo de Jesus e importante liderança no início da igreja.',refs:['Mateus 16','João 21','Atos 2','Atos 10']},
    {id:'paulo',name:'Paulo',icon:'🛤️',era:'Igreja Primitiva',summary:'Apóstolo e missionário cuja trajetória ocupa grande parte do livro de Atos e das epístolas.',refs:['Atos 9','Atos 13','Atos 17','2 Timóteo 4']},
    {id:'timoteo',name:'Timóteo',icon:'📖',era:'Igreja Primitiva',summary:'Cooperador de Paulo e exemplo de liderança cristã em formação.',refs:['Atos 16','1 Timóteo 4','2 Timóteo 1']}
  ];

  const ERAS114=[
    {icon:'🌍',title:'Origens',sub:'Criação, queda, dilúvio e povos',refs:['Gênesis 1','Gênesis 3','Gênesis 6','Gênesis 11']},
    {icon:'⛺',title:'Patriarcas',sub:'Abraão, Isaque, Jacó e José',refs:['Gênesis 12','Gênesis 26','Gênesis 28','Gênesis 37']},
    {icon:'🌊',title:'Êxodo e Sinai',sub:'Libertação, aliança e peregrinação',refs:['Êxodo 3','Êxodo 14','Êxodo 20','Números 14']},
    {icon:'🛡️',title:'Conquista e Juízes',sub:'Entrada em Canaã e ciclos de liderança',refs:['Josué 1','Josué 6','Juízes 2']},
    {icon:'👑',title:'Monarquia',sub:'Saul, Davi, Salomão e divisão do reino',refs:['1 Samuel 10','2 Samuel 5','1 Reis 3','1 Reis 12']},
    {icon:'🔥',title:'Profetas e Exílio',sub:'Chamados ao arrependimento e queda de Jerusalém',refs:['Isaías 6','Jeremias 1','2 Reis 25','Daniel 1']},
    {icon:'🏗️',title:'Retorno e Restauração',sub:'Retorno, templo e reconstrução de Jerusalém',refs:['Esdras 1','Neemias 2','Neemias 8']},
    {icon:'✝️',title:'Jesus e os Evangelhos',sub:'Nascimento, ministério, cruz e ressurreição',refs:['Mateus 1','Marcos 1','Lucas 24','João 20']},
    {icon:'🌍',title:'Igreja Primitiva',sub:'Pentecostes, missão e expansão do evangelho',refs:['Atos 2','Atos 8','Atos 13','Atos 28']}
  ];

  const THEMES114=[
    {id:'fe',icon:'✨',title:'Fé',summary:'Confiar em Deus, perseverar e responder com obediência.',refs:['Hebreus 11:1','Romanos 10:17','Tiago 2:17','Marcos 9:23']},
    {id:'oracao',icon:'🙏',title:'Oração',summary:'Adoração, dependência, intercessão e perseverança diante de Deus.',refs:['Mateus 6:9','Filipenses 4:6','1 Tessalonicenses 5:17','Tiago 5:16']},
    {id:'graca',icon:'💜',title:'Graça',summary:'Favor de Deus que salva, sustenta e ensina uma nova maneira de viver.',refs:['Efésios 2:8','Romanos 3:24','Tito 2:11','2 Coríntios 12:9']},
    {id:'lideranca',icon:'🧭',title:'Liderança',summary:'Servir com caráter, sabedoria, exemplo e responsabilidade.',refs:['Êxodo 18:21','Marcos 10:43','1 Timóteo 3:1','1 Pedro 5:2']},
    {id:'familia',icon:'🏠',title:'Família',summary:'Relacionamentos moldados por amor, ensino, honra e cuidado mútuo.',refs:['Deuteronômio 6:6','Josué 24:15','Efésios 5:25','Efésios 6:1']},
    {id:'missao',icon:'🌍',title:'Missão',summary:'Testemunhar de Cristo e participar da expansão do evangelho.',refs:['Mateus 28:19','Atos 1:8','Romanos 10:14','2 Coríntios 5:20']},
    {id:'sabedoria',icon:'💡',title:'Sabedoria',summary:'Aplicar a verdade de Deus às decisões, palavras e relacionamentos.',refs:['Provérbios 1:7','Provérbios 3:5','Tiago 1:5','Tiago 3:17']},
    {id:'esperanca',icon:'🌅',title:'Esperança',summary:'Olhar para as promessas de Deus com perseverança em meio às lutas.',refs:['Romanos 5:3','Romanos 15:13','1 Pedro 1:3','Apocalipse 21:4']}
  ];

  state.place114=state.place114||'jerusalem';
  state.person114=state.person114||'abraao';
  state.theme114=state.theme114||'fe';
  state.pulpitStep114=0;
  state.pulpit114=Object.assign({title:'',ref:'',intro:'',points:'',conclusion:''},JSON.parse(localStorage.getItem('ebd-pulpit-v114')||'{}'));

  function openRef114(ref){
    try{
      const p=typeof parseRef19==='function'?parseRef19(ref):(typeof parseRef18==='function'?parseRef18(ref):null);
      if(p){state.book=p.book;state.chapter=p.chapter;state.selectedVersesV19=[];state.studyVerseV19=null;nav('reader');setTimeout(()=>{if(p.verse)document.getElementById('v18verse-'+p.verse)?.scrollIntoView({block:'center'})},80);return}
    }catch(e){}
    toast('Referência: '+ref);
  }
  function refs114(refs){return `<div class="v114-refs">${refs.map(r=>`<button data-ref114="${esc114(r)}">📖 ${esc114(r)}</button>`).join('')}</div>`}

  function ministry114(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Ministério & Estudo</h1><p>Ferramentas offline para preparar, ensinar e ministrar.</p></div></div>
    <section class="v114-hero"><div><span>CENTRAL DE MINISTÉRIO</span><h2>Da pesquisa à ministração</h2><p>Explore contexto bíblico, organize ideias e leve seu esboço para o púlpito.</p></div><b>✝️</b></section>
    <div class="v114-grid">
      <button data-route="atlas114"><span>🗺️</span><strong>Atlas Bíblico</strong><small>Lugares e referências</small></button>
      <button data-route="people114"><span>👥</span><strong>Pessoas da Bíblia</strong><small>Personagens e trajetória</small></button>
      <button data-route="timeline114"><span>⏳</span><strong>Linha do Tempo</strong><small>Grandes períodos bíblicos</small></button>
      <button data-route="themes114"><span>💡</span><strong>Estudos Temáticos</strong><small>Temas e passagens</small></button>
      <button data-route="outlines"><span>🗂️</span><strong>Esboços</strong><small>Prepare seu roteiro</small></button>
      <button data-route="pulpit114" class="accent"><span>🎙️</span><strong>Modo Púlpito</strong><small>Apresente em tela grande</small></button>
    </div>
    <section class="v114-info"><span>📶</span><div><strong>Funciona offline</strong><p>Os conteúdos desta central ficam dentro do aplicativo e as referências abrem na Bíblia completa offline.</p></div></section>`}

  function atlas114(){
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Atlas Bíblico</h1><p>Visão esquemática de lugares importantes.</p></div></div>
      <section class="v114-map"><div class="v114-sea">MAR<br>MEDITERRÂNEO</div><div class="v114-jordan"></div>${PLACES114.map(p=>`<button class="v114-pin" style="left:${p.x}%;top:${p.y}%" data-place114="${p.id}" title="${esc114(p.name)}"><i></i><span>${esc114(p.name)}</span></button>`).join('')}<small>Mapa esquemático para estudo • posições aproximadas</small></section>
      <div class="subhead">Lugares em destaque</div><div class="v114-place-list">${PLACES114.map(p=>`<button data-place114="${p.id}"><span>${p.icon}</span><div><strong>${esc114(p.name)}</strong><small>${esc114(p.region)} • ${esc114(p.summary)}</small></div><b>›</b></button>`).join('')}</div>`;
  }
  function place114(){const p=PLACES114.find(x=>x.id===state.place114)||PLACES114[0];return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>${p.icon} ${esc114(p.name)}</h1><p>${esc114(p.region)}</p></div></div><section class="v114-detail"><span>LUGAR BÍBLICO</span><h2>${esc114(p.name)}</h2><p>${esc114(p.summary)}</p></section><h3 class="v114-title">Passagens para estudar</h3>${refs114(p.refs)}<button class="btn btn-purple v114-wide" data-route="atlas114">🗺️ Voltar ao Atlas</button>`}

  function people114(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Pessoas da Bíblia</h1><p>Perfis rápidos para consulta e ensino.</p></div></div><div class="v114-people">${PEOPLE114.map(p=>`<button data-person114="${p.id}"><span>${p.icon}</span><div><small>${esc114(p.era)}</small><strong>${esc114(p.name)}</strong><p>${esc114(p.summary)}</p></div><b>›</b></button>`).join('')}</div>`}
  function person114(){const p=PEOPLE114.find(x=>x.id===state.person114)||PEOPLE114[0];return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>${p.icon} ${esc114(p.name)}</h1><p>${esc114(p.era)}</p></div></div><section class="v114-detail person"><span>PERSONAGEM BÍBLICO</span><h2>${esc114(p.name)}</h2><p>${esc114(p.summary)}</p></section><h3 class="v114-title">Leituras essenciais</h3>${refs114(p.refs)}<button class="btn btn-dark v114-wide" data-route="people114">👥 Ver outros personagens</button>`}

  function timeline114(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Linha do Tempo</h1><p>Panorama dos grandes períodos bíblicos.</p></div></div><section class="v114-timeline">${ERAS114.map((e,i)=>`<article><div class="v114-time-dot">${e.icon}</div><div><small>ETAPA ${String(i+1).padStart(2,'0')}</small><h2>${esc114(e.title)}</h2><p>${esc114(e.sub)}</p>${refs114(e.refs)}</div></article>`).join('')}</section><section class="v114-note">ℹ️ Esta linha do tempo organiza os períodos pela sequência narrativa bíblica; não pretende fixar datas históricas controversas.</section>`}

  function themes114(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Estudos Temáticos</h1><p>Comece por um assunto e siga pelas Escrituras.</p></div></div><div class="v114-themes">${THEMES114.map(t=>`<button data-theme114="${t.id}"><span>${t.icon}</span><div><strong>${esc114(t.title)}</strong><small>${esc114(t.summary)}</small></div><b>›</b></button>`).join('')}</div>`}
  function theme114(){const t=THEMES114.find(x=>x.id===state.theme114)||THEMES114[0];return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>${t.icon} ${esc114(t.title)}</h1><p>Estudo temático guiado por referências.</p></div></div><section class="v114-detail theme"><span>TEMA DE ESTUDO</span><h2>${esc114(t.title)}</h2><p>${esc114(t.summary)}</p></section><h3 class="v114-title">Roteiro sugerido</h3><div class="v114-study-steps"><article><b>1</b><div><strong>Observe</strong><small>Leia as passagens e destaque palavras, repetições e contrastes.</small></div></article><article><b>2</b><div><strong>Relacione</strong><small>Compare como cada texto amplia ou equilibra o tema.</small></div></article><article><b>3</b><div><strong>Aplique</strong><small>Escreva uma atitude prática e uma pergunta para discussão.</small></div></article></div>${refs114(t.refs)}<button class="btn btn-primary v114-wide" data-route="outlines">🗂️ Criar esboço sobre este tema</button>`}

  function savePulpit114(){
    const get=id=>document.getElementById(id)?.value??'';
    state.pulpit114={title:get('pulpitTitle114'),ref:get('pulpitRef114'),intro:get('pulpitIntro114'),points:get('pulpitPoints114'),conclusion:get('pulpitConclusion114')};
    localStorage.setItem('ebd-pulpit-v114',JSON.stringify(state.pulpit114));toast('Esboço do púlpito salvo ✓');
  }
  function pulpitSlides114(){const d=state.pulpit114,pts=String(d.points||'').split('\n').map(x=>x.trim()).filter(Boolean);const slides=[];slides.push({kind:'cover',title:d.title||'Minha Mensagem',text:d.ref||'Bíblia EBD'});if(d.intro)slides.push({kind:'intro',title:'Introdução',text:d.intro});pts.forEach((p,i)=>slides.push({kind:'point',title:`Ponto ${i+1}`,text:p}));if(d.conclusion)slides.push({kind:'end',title:'Conclusão',text:d.conclusion});return slides}
  function pulpit114(){const d=state.pulpit114;return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Modo Púlpito</h1><p>Prepare e apresente sua mensagem sem distrações.</p></div></div><section class="v114-pulpit-card"><span>🎙️</span><div><strong>Seu esboço fica salvo neste aparelho</strong><small>Durante a apresentação a tela permanece acesa.</small></div></section><div class="v114-pulpit-form"><label>Título da mensagem<input class="field" id="pulpitTitle114" value="${esc114(d.title)}" placeholder="Ex.: Uma fé que permanece"></label><label>Texto principal<input class="field" id="pulpitRef114" value="${esc114(d.ref)}" placeholder="Ex.: Hebreus 11:1"></label><label>Introdução<textarea class="field" id="pulpitIntro114" rows="3" placeholder="Abertura da mensagem...">${esc114(d.intro)}</textarea></label><label>Pontos principais <small>um ponto por linha</small><textarea class="field" id="pulpitPoints114" rows="7" placeholder="1. Deus chama\n2. A fé responde\n3. A obediência transforma">${esc114(d.points)}</textarea></label><label>Conclusão<textarea class="field" id="pulpitConclusion114" rows="3" placeholder="Aplicação e encerramento...">${esc114(d.conclusion)}</textarea></label></div><div class="v114-pulpit-actions"><button class="btn btn-dark" id="savePulpit114">💾 Salvar</button><button class="btn btn-purple" id="openPulpit114">🎙️ Apresentar</button><button class="btn btn-dark" id="sharePulpit114">↗️ Compartilhar</button></div>`}
  function pulpitPresent114(){const slides=pulpitSlides114();state.pulpitStep114=Math.max(0,Math.min(state.pulpitStep114,slides.length-1));const s=slides[state.pulpitStep114]||slides[0];return `<section class="v114-present"><button class="v114-present-close" id="closePulpit114">✕</button><div class="v114-present-counter">${state.pulpitStep114+1} / ${slides.length}</div><div class="v114-present-body"><small>${s.kind==='cover'?'MODO PÚLPITO':esc114(s.title).toUpperCase()}</small><h1>${esc114(s.kind==='cover'?s.title:s.text)}</h1>${s.kind==='cover'?`<p>${esc114(s.text)}</p>`:''}</div><div class="v114-present-nav"><button id="prevPulpit114" ${state.pulpitStep114<=0?'disabled':''}>‹ Anterior</button><button id="nextPulpit114" ${state.pulpitStep114>=slides.length-1?'disabled':''}>Próximo ›</button></div></section>`}

  function homeCard114(){return `<section class="section v114-home"><div class="v114-home-icon">🎙️</div><div><span>NOVO • MINISTÉRIO & ESTUDO</span><strong>Atlas, temas, pessoas e Modo Púlpito</strong><small>Ferramentas para pesquisa e preparação bíblica.</small></div><button data-route="ministry114">Abrir</button></section>`}
  function injectHome114(){if(state.route!=='home')return;const a=app114();if(a&&!a.querySelector('.v114-home'))a.insertAdjacentHTML('afterbegin',homeCard114())}

  function render114Route(){
    const map={ministry114,atlas114,place114,people114,person114,timeline114,themes114,theme114,pulpit114,pulpitPresent114};
    const fn=map[state.route];if(!fn)return false;
    app114().innerHTML=fn();
    document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));
    if(state.route==='pulpitPresent114'){document.body.classList.add('v114-presentation');try{keepAwake112(true)}catch(e){}}
    else document.body.classList.remove('v114-presentation');
    window.bind();return true;
  }

  window.render=function(){
    document.body.classList.remove('v114-presentation');
    if(render114Route())return;
    oldRender114();injectHome114();bind114();
  };
  window.bind=function(){oldBind114();bind114()};

  function bind114(){
    document.querySelectorAll('[data-route]').forEach(b=>b.onclick=()=>nav(b.dataset.route));
    document.querySelectorAll('[data-place114]').forEach(b=>b.onclick=()=>{state.place114=b.dataset.place114;nav('place114')});
    document.querySelectorAll('[data-person114]').forEach(b=>b.onclick=()=>{state.person114=b.dataset.person114;nav('person114')});
    document.querySelectorAll('[data-theme114]').forEach(b=>b.onclick=()=>{state.theme114=b.dataset.theme114;nav('theme114')});
    document.querySelectorAll('[data-ref114]').forEach(b=>b.onclick=()=>openRef114(b.dataset.ref114));
    document.getElementById('savePulpit114')?.addEventListener('click',savePulpit114);
    document.getElementById('openPulpit114')?.addEventListener('click',()=>{savePulpit114();state.pulpitStep114=0;nav('pulpitPresent114')});
    document.getElementById('sharePulpit114')?.addEventListener('click',()=>{savePulpit114();const d=state.pulpit114,text=[d.title,d.ref,d.intro,d.points,d.conclusion].filter(Boolean).join('\n\n');try{share112(text,d.title||'Esboço Bíblico')}catch(e){copy18(text)}});
    document.getElementById('closePulpit114')?.addEventListener('click',()=>{try{keepAwake112(false)}catch(e){};nav('pulpit114')});
    document.getElementById('prevPulpit114')?.addEventListener('click',()=>{state.pulpitStep114=Math.max(0,state.pulpitStep114-1);window.render()});
    document.getElementById('nextPulpit114')?.addEventListener('click',()=>{state.pulpitStep114=Math.min(pulpitSlides114().length-1,state.pulpitStep114+1);window.render()});
  }
})();
