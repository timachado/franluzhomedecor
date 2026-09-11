// 1.15.9 — Atlas Bíblico ampliado, Dicionário Bíblico + Português e Busca Inteligente local.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const SEARCH_HISTORY='ebd-smart-search-v1159';

  const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const toastMsg=s=>{try{window.toast?.(s)}catch(_){}};

  const LEXICON=[
    {term:'Graça',type:'Bíblico',def:'Favor imerecido de Deus; no Novo Testamento, aparece ligado à salvação, ao sustento e à vida transformada.',refs:['Efésios 2:8','Romanos 3:24','Tito 2:11']},
    {term:'Fé',type:'Bíblico',def:'Confiança em Deus que envolve convicção, dependência e resposta prática.',refs:['Hebreus 11:1','Romanos 10:17','Tiago 2:17']},
    {term:'Aliança',type:'Bíblico',def:'Compromisso solene que organiza uma relação e suas promessas; é um tema central na história bíblica.',refs:['Gênesis 15','Êxodo 24','Jeremias 31:31','Lucas 22:20']},
    {term:'Redenção',type:'Bíblico',def:'Ideia de libertação mediante resgate; na linguagem cristã, descreve a libertação do pecado em Cristo.',refs:['Efésios 1:7','Colossenses 1:14','1 Pedro 1:18']},
    {term:'Justificação',type:'Bíblico',def:'Termo ligado ao ato de declarar justo; Paulo o usa ao explicar a relação entre fé, graça e reconciliação com Deus.',refs:['Romanos 3:24','Romanos 5:1','Gálatas 2:16']},
    {term:'Santificação',type:'Bíblico',def:'Processo e chamado de separação para Deus, crescimento em santidade e transformação de vida.',refs:['1 Tessalonicenses 4:3','Hebreus 12:14','1 Pedro 1:15']},
    {term:'Reconciliação',type:'Bíblico',def:'Restauração de uma relação rompida; no evangelho, aponta para a paz com Deus e para o ministério de reconciliar.',refs:['Romanos 5:10','2 Coríntios 5:18','Colossenses 1:20']},
    {term:'Propiciação',type:'Bíblico',def:'Termo teológico associado ao tratamento do pecado e à restauração da relação com Deus por meio de Cristo.',refs:['Romanos 3:25','1 João 2:2','1 João 4:10']},
    {term:'Salvação',type:'Bíblico',def:'Livramento e restauração oferecidos por Deus; no Novo Testamento, a mensagem é centrada em Jesus Cristo.',refs:['João 3:16','Atos 4:12','Efésios 2:8']},
    {term:'Arrependimento',type:'Bíblico',def:'Mudança de mente e direção que envolve reconhecer o pecado e voltar-se para Deus.',refs:['Marcos 1:15','Atos 2:38','2 Coríntios 7:10']},
    {term:'Evangelho',type:'Bíblico',def:'Boa notícia; no cristianismo, anuncia a obra de Deus em Jesus Cristo e o chamado à fé.',refs:['Marcos 1:1','Romanos 1:16','1 Coríntios 15:1']},
    {term:'Discípulo',type:'Bíblico',def:'Aprendiz ou seguidor; nos Evangelhos, descreve especialmente quem segue Jesus e aprende dele.',refs:['Mateus 4:19','Lucas 9:23','João 8:31']},
    {term:'Apóstolo',type:'Bíblico',def:'Enviado ou mensageiro com missão; o Novo Testamento usa o termo de modo especial para testemunhas e líderes enviados.',refs:['Marcos 3:14','Atos 1:21','Romanos 1:1']},
    {term:'Parábola',type:'Bíblico',def:'Narrativa ou comparação usada para ensinar uma verdade por meio de situações conhecidas.',refs:['Mateus 13:3','Marcos 4:33','Lucas 15:3']},
    {term:'Profecia',type:'Bíblico',def:'Mensagem profética ligada à proclamação da vontade de Deus; deve ser lida no contexto literário e histórico de cada passagem.',refs:['Amós 3:7','1 Coríntios 14:3','2 Pedro 1:20']},
    {term:'Igreja',type:'Bíblico',def:'Assembleia ou comunidade dos chamados; no Novo Testamento, designa tanto comunidades locais quanto o povo de Cristo.',refs:['Mateus 16:18','Atos 2:42','1 Coríntios 12:27']},
    {term:'Oração',type:'Bíblico',def:'Comunicação com Deus que inclui adoração, confissão, gratidão, pedido e intercessão.',refs:['Mateus 6:9','Filipenses 4:6','1 Tessalonicenses 5:17']},
    {term:'Ressurreição',type:'Bíblico',def:'Retorno à vida; a ressurreição de Jesus ocupa lugar central na proclamação cristã e na esperança futura.',refs:['Lucas 24:6','1 Coríntios 15:20','1 Pedro 1:3']},
    {term:'Misericórdia',type:'Bíblico',def:'Compaixão que se move em favor de quem necessita; aparece como atributo divino e virtude esperada dos discípulos.',refs:['Salmos 103:8','Lucas 6:36','Efésios 2:4']},
    {term:'Perseverança',type:'Português',def:'Capacidade de permanecer firme e continuar apesar de dificuldade, demora ou oposição.',refs:['Romanos 5:3','Hebreus 10:36','Tiago 1:3']},
    {term:'Mansidão',type:'Português',def:'Qualidade de quem age com brandura, domínio próprio e ausência de agressividade.',refs:['Mateus 5:5','Gálatas 5:23','1 Pedro 3:15']},
    {term:'Longanimidade',type:'Português',def:'Paciência prolongada; disposição de suportar dificuldades ou ofensas sem reagir precipitadamente.',refs:['Gálatas 5:22','Efésios 4:2','Colossenses 3:12']},
    {term:'Iniquidade',type:'Português',def:'Injustiça, perversidade ou conduta moralmente errada; palavra comum em traduções bíblicas mais tradicionais.',refs:['Salmos 32:5','Mateus 7:23','2 Tessalonicenses 2:7']},
    {term:'Concupiscência',type:'Português',def:'Desejo intenso, frequentemente usado em linguagem bíblica tradicional para desejos desordenados ou pecaminosos.',refs:['Tiago 1:14','1 João 2:16','1 Pedro 2:11']},
    {term:'Remissão',type:'Português',def:'Ato de perdoar, cancelar ou liberar uma dívida ou culpa; em contexto bíblico, pode aparecer ligado ao perdão dos pecados.',refs:['Mateus 26:28','Atos 2:38','Hebreus 9:22']},
    {term:'Exortação',type:'Português',def:'Aconselhamento ou apelo firme que encoraja alguém a agir, corrigir-se ou perseverar.',refs:['Romanos 12:8','1 Tessalonicenses 5:11','Hebreus 3:13']},
    {term:'Edificação',type:'Português',def:'Ato de construir; figuradamente, fortalecer, desenvolver ou fazer crescer uma pessoa ou comunidade.',refs:['Romanos 14:19','1 Coríntios 14:26','Efésios 4:12']},
    {term:'Benevolência',type:'Português',def:'Disposição para fazer o bem, agir com bondade e desejar o bem de outra pessoa.',refs:['Efésios 4:32','Colossenses 3:12']},
    {term:'Soberania',type:'Português',def:'Autoridade suprema ou domínio máximo. Em teologia, o termo é usado para falar do governo de Deus.',refs:['Salmos 103:19','Daniel 4:35','Romanos 9:20']},
    {term:'Temor',type:'Português',def:'Pode significar medo, respeito ou reverência conforme o contexto. Em “temor do Senhor”, normalmente aponta para reverência obediente.',refs:['Provérbios 1:7','Eclesiastes 12:13','Atos 9:31']}
  ];

  const TOPICS=[
    {id:'ansiedade',aliases:['ansiedade','ansioso','preocupacao','preocupado','preocupações'],title:'Ansiedade e preocupação',refs:['Filipenses 4:6-7','1 Pedro 5:7','Mateus 6:25-34','Salmos 55:22']},
    {id:'medo',aliases:['medo','temor','amedrontado'],title:'Medo e coragem',refs:['Isaías 41:10','Josué 1:9','Salmos 56:3','2 Timóteo 1:7']},
    {id:'familia',aliases:['familia','casamento','filhos','pais'],title:'Família',refs:['Deuteronômio 6:6-7','Josué 24:15','Efésios 5:25','Efésios 6:1-4']},
    {id:'oracao',aliases:['oracao','orar','intercessao'],title:'Oração',refs:['Mateus 6:9-13','Filipenses 4:6','1 Tessalonicenses 5:17','Tiago 5:16']},
    {id:'fe',aliases:['fe','confiar','confianca'],title:'Fé e confiança',refs:['Hebreus 11:1','Romanos 10:17','Provérbios 3:5-6','Marcos 9:23']},
    {id:'perdao',aliases:['perdao','perdoar','ofensa'],title:'Perdão',refs:['Mateus 6:14-15','Efésios 4:32','Colossenses 3:13','1 João 1:9']},
    {id:'amor',aliases:['amor','amar'],title:'Amor',refs:['1 Coríntios 13:4-7','João 13:34-35','1 João 4:7-8','Romanos 12:9-10']},
    {id:'esperanca',aliases:['esperanca','desanimo','desanimado'],title:'Esperança e ânimo',refs:['Romanos 15:13','Isaías 40:31','Salmos 42:11','1 Pedro 1:3']},
    {id:'sabedoria',aliases:['sabedoria','decisao','decisoes','direcao'],title:'Sabedoria e decisões',refs:['Tiago 1:5','Provérbios 3:5-6','Provérbios 16:3','Salmos 119:105']},
    {id:'salvacao',aliases:['salvacao','salvo','salvar'],title:'Salvação',refs:['João 3:16','Romanos 10:9-10','Efésios 2:8-9','Atos 4:12']},
    {id:'espirito',aliases:['espirito santo','fruto do espirito'],title:'Espírito Santo',refs:['João 14:26','Atos 1:8','Gálatas 5:22-23','Romanos 8:26']},
    {id:'lideranca',aliases:['lideranca','lider','pastor','professor'],title:'Liderança e serviço',refs:['Marcos 10:43-45','1 Timóteo 3:1-7','1 Pedro 5:2-3','Tiago 3:1']}
  ];

  const ATLAS=[
    {id:'jerusalem',name:'Jerusalém',region:'Judeia',icon:'🏛️',summary:'Centro político e religioso decisivo na história bíblica; cenário do templo, da paixão de Jesus e do Pentecostes.',refs:['2 Samuel 5','Salmos 122','Lucas 19','Atos 2']},
    {id:'belem',name:'Belém',region:'Judeia',icon:'⭐',summary:'Cidade ligada a Rute e Davi e, nos Evangelhos, ao nascimento de Jesus.',refs:['Rute 1','1 Samuel 16','Miqueias 5:2','Mateus 2']},
    {id:'jerico',name:'Jericó',region:'Judeia / Jordão',icon:'🌴',summary:'Cidade do vale do Jordão ligada à conquista de Canaã e a episódios do ministério de Jesus.',refs:['Josué 6','Lucas 10:30','Lucas 19']},
    {id:'hebron',name:'Hebrom',region:'Judá',icon:'⛰️',summary:'Lugar associado aos patriarcas e ao início do reinado de Davi em Judá.',refs:['Gênesis 13:18','Gênesis 23','2 Samuel 2']},
    {id:'nazare',name:'Nazaré',region:'Galileia',icon:'🏠',summary:'Cidade onde Jesus cresceu e onde enfrentou rejeição ao ensinar na sinagoga.',refs:['Mateus 2:23','Lucas 2:39','Lucas 4']},
    {id:'cafarnaum',name:'Cafarnaum',region:'Galileia',icon:'⛵',summary:'Importante base do ministério de Jesus às margens do mar da Galileia.',refs:['Mateus 4:13','Marcos 1','João 6']},
    {id:'caná',name:'Caná',region:'Galileia',icon:'🍇',summary:'Local associado ao primeiro sinal de Jesus narrado no Evangelho de João.',refs:['João 2:1-11','João 4:46']},
    {id:'tiberiades',name:'Mar da Galileia',region:'Galileia',icon:'🌊',summary:'Lago em torno do qual ocorreram muitos episódios do ministério de Jesus e dos discípulos.',refs:['Marcos 4:35','Mateus 14:22','João 21']},
    {id:'samaria',name:'Samaria',region:'Samaria',icon:'🏘️',summary:'Região central ligada ao reino do Norte e, no Novo Testamento, à expansão do evangelho.',refs:['1 Reis 16:24','João 4','Atos 8']},
    {id:'cesareia',name:'Cesareia Marítima',region:'Costa mediterrânea',icon:'⚓',summary:'Centro administrativo romano; Pedro visita Cornélio e Paulo permanece sob custódia antes de seguir para Roma.',refs:['Atos 10','Atos 23:23','Atos 25']},
    {id:'damasco',name:'Damasco',region:'Síria',icon:'🛤️',summary:'Cidade ligada à conversão de Saulo e ao início de sua trajetória cristã.',refs:['Atos 9','Atos 22','Atos 26']},
    {id:'antioquia',name:'Antioquia da Síria',region:'Síria',icon:'🌍',summary:'Centro missionário importante da igreja primitiva e ponto de envio de Paulo e Barnabé.',refs:['Atos 11','Atos 13','Atos 14']},
    {id:'tarso',name:'Tarso',region:'Cilícia',icon:'🏙️',summary:'Cidade de origem do apóstolo Paulo.',refs:['Atos 9:11','Atos 21:39','Atos 22:3']},
    {id:'filipos',name:'Filipos',region:'Macedônia',icon:'⛓️',summary:'Cidade onde Paulo e Silas foram presos e onde surgiu uma importante comunidade cristã.',refs:['Atos 16','Filipenses 1:1']},
    {id:'tessalonica',name:'Tessalônica',region:'Macedônia',icon:'🏛️',summary:'Cidade alcançada durante a segunda viagem missionária de Paulo e destinatária das cartas aos Tessalonicenses.',refs:['Atos 17:1-9','1 Tessalonicenses 1']},
    {id:'atenas',name:'Atenas',region:'Acaia',icon:'🏺',summary:'Cidade onde Paulo discursou no Areópago a respeito do Deus desconhecido.',refs:['Atos 17:16-34']},
    {id:'corinto',name:'Corinto',region:'Acaia',icon:'🏺',summary:'Grande cidade comercial onde Paulo permaneceu por longo período e onde se formou a igreja destinatária das cartas aos Coríntios.',refs:['Atos 18','1 Coríntios 1']},
    {id:'efeso',name:'Éfeso',region:'Ásia Menor',icon:'📜',summary:'Centro urbano importante onde Paulo ensinou por longo período e enfrentou oposição ligada ao culto de Ártemis.',refs:['Atos 19','Efésios 1']},
    {id:'roma',name:'Roma',region:'Itália',icon:'🏛️',summary:'Capital do Império Romano; Atos termina com Paulo em prisão domiciliar anunciando o evangelho.',refs:['Atos 28','Romanos 1']},
    {id:'sinai',name:'Sinai',region:'Deserto',icon:'⛰️',summary:'Região relacionada à aliança, à entrega da Lei e à peregrinação de Israel.',refs:['Êxodo 19','Êxodo 20','Deuteronômio 5']},
    {id:'egito',name:'Egito',region:'Nordeste da África',icon:'🏺',summary:'Terra presente na história dos patriarcas, no Êxodo e na infância de Jesus.',refs:['Gênesis 46','Êxodo 1','Mateus 2:13']},
    {id:'babilonia',name:'Babilônia',region:'Mesopotâmia',icon:'🏙️',summary:'Potência associada à queda de Jerusalém, ao exílio de Judá e ao livro de Daniel.',refs:['2 Reis 25','Daniel 1','Salmos 137']},
    {id:'ninvive',name:'Nínive',region:'Assíria',icon:'🏙️',summary:'Capital assíria conhecida especialmente pela missão do profeta Jonas.',refs:['Jonas 1','Jonas 3','Naum 1']},
    {id:'susa',name:'Susã',region:'Império Persa',icon:'👑',summary:'Cidade palaciana ligada às narrativas de Ester e Neemias.',refs:['Ester 1','Neemias 1']}
  ];

  const JOURNEYS=[
    {id:'jesus',title:'Ministério de Jesus',icon:'✝️',stops:['nazare','caná','cafarnaum','tiberiades','jerico','jerusalem']},
    {id:'paulo',title:'Caminhos de Paulo',icon:'🛤️',stops:['damasco','antioquia','filipos','tessalonica','atenas','corinto','efeso','cesareia','roma']},
    {id:'exodo',title:'Êxodo e peregrinação',icon:'🌊',stops:['egito','sinai','jerico']},
    {id:'exilio',title:'Exílio e retorno',icon:'🏗️',stops:['jerusalem','babilonia','susa','jerusalem']}
  ];

  const PEOPLE=[
    {name:'Paulo',aliases:['paulo','saulo'],summary:'Apóstolo e missionário. Atos registra sua conversão, viagens, prisões e ida a Roma.',refs:['Atos 9','Atos 13','Atos 16','Atos 21','Atos 28']},
    {name:'Pedro',aliases:['pedro','simao pedro'],summary:'Discípulo de Jesus e liderança importante nos primeiros capítulos de Atos.',refs:['Mateus 16','João 21','Atos 2','Atos 10']},
    {name:'Davi',aliases:['davi'],summary:'Pastor, guerreiro e rei de Israel; figura central na história bíblica e nos Salmos.',refs:['1 Samuel 16','1 Samuel 17','2 Samuel 7','Salmos 23']},
    {name:'Moisés',aliases:['moises'],summary:'Líder do Êxodo e mediador da aliança do Sinai.',refs:['Êxodo 3','Êxodo 14','Êxodo 20','Deuteronômio 34']},
    {name:'Abraão',aliases:['abraao','abraam'],summary:'Patriarca chamado por Deus e referência bíblica de fé e promessa.',refs:['Gênesis 12','Gênesis 15','Gênesis 22','Romanos 4']},
    {name:'Ester',aliases:['ester'],summary:'Rainha que agiu com coragem em favor de seu povo no império persa.',refs:['Ester 4','Ester 7','Ester 9']},
    {name:'Daniel',aliases:['daniel'],summary:'Servo judeu no exílio babilônico conhecido por fidelidade, oração e visões.',refs:['Daniel 1','Daniel 6','Daniel 7']}
  ];

  let bibleIndex=null;
  state.smartQuery1159=state.smartQuery1159||'';
  state.smartResults1159=[];
  state.atlasQuery1159=state.atlasQuery1159||'';
  state.atlasRegion1159=state.atlasRegion1159||'Todos';
  state.atlasSelected1159=state.atlasSelected1159||'jerusalem';
  state.dictQuery1159=state.dictQuery1159||'';
  state.dictType1159=state.dictType1159||'Todos';

  function history(){try{const x=JSON.parse(localStorage.getItem(SEARCH_HISTORY)||'[]');return Array.isArray(x)?x:[]}catch(_){return []}}
  function remember(q){q=String(q||'').trim();if(!q)return;const h=[q,...history().filter(x=>norm(x)!==norm(q))].slice(0,8);localStorage.setItem(SEARCH_HISTORY,JSON.stringify(h))}
  function bible(){return window.BIBLE_DATA_V18?.books||[]}
  function buildBibleIndex(){
    if(bibleIndex)return bibleIndex;
    bibleIndex=[];
    for(const b of bible())for(let c=0;c<(b.chapters||[]).length;c++)for(let v=0;v<(b.chapters[c]||[]).length;v++)bibleIndex.push({book:b.name,chapter:c+1,verse:v+1,text:b.chapters[c][v],n:norm(b.chapters[c][v])});
    return bibleIndex;
  }
  function openRef(ref){
    const detector=window.__EBD_AI_1152__?.detectReference;
    const p=typeof detector==='function'?detector(String(ref)):null;
    if(p){state.book=p.book;state.chapter=p.chapter;state.selectedVersesV19=p.verse?Array.from({length:(p.endVerse||p.verse)-p.verse+1},(_,i)=>p.verse+i):[];state.studyVerseV19=p.verse||null;nav('reader');setTimeout(()=>p.verse&&document.getElementById('v18verse-'+p.verse)?.scrollIntoView({block:'center'}),120);return}
    try{const x=parseRef19(String(ref));if(x){state.book=x.book;state.chapter=x.chapter;nav('reader')}}catch(_){toastMsg('Não foi possível abrir a referência.')}
  }
  function verseFromRef(ref){
    const p=window.__EBD_AI_1152__?.detectReference?.(ref);if(!p)return null;
    const vs=typeof chapterVerses18==='function'?chapterVerses18(p.book,p.chapter)||[]:[];if(!vs.length)return null;
    if(!p.verse)return {ref:`${p.book} ${p.chapter}`,text:vs.slice(0,4).join(' '),open:ref};
    const end=p.endVerse||p.verse,parts=[];for(let i=p.verse;i<=end;i++)parts.push(vs[i-1]);
    return {ref:`${p.book} ${p.chapter}:${p.verse}${end!==p.verse?'-'+end:''}`,text:parts.join(' '),open:ref};
  }
  function topicMatch(q){const n=norm(q);return TOPICS.find(t=>t.aliases.some(a=>n.includes(norm(a))))||null}
  function lexMatch(q){const n=norm(q).replace(/^(o que significa|qual o significado de|o que e|significado de)\s+/,'');return LEXICON.find(x=>n.includes(norm(x.term))||norm(x.term).includes(n))||null}
  function atlasMatches(q){const n=norm(q);return ATLAS.filter(p=>n.includes(norm(p.name))||norm(p.name).includes(n)||norm(p.region).includes(n)).slice(0,8)}
  function personMatch(q){const n=norm(q);return PEOPLE.find(p=>p.aliases.some(a=>n.includes(norm(a))))||null}
  function fullText(q,limit=35){
    const raw=norm(q).replace(/\b(versiculos?|biblia|sobre|que|falam?|fala|onde|encontro|mostrar|mostre|buscar|procure|texto|passagem|palavra|de|da|do|dos|das|um|uma|e|o|a)\b/g,' ').replace(/\s+/g,' ').trim();
    if(raw.length<2)return [];
    const tokens=raw.split(' ').filter(x=>x.length>2).slice(0,6),phrase=raw;
    const scored=[];
    for(const row of buildBibleIndex()){
      let score=0;if(row.n.includes(phrase))score+=12;
      for(const t of tokens)if(row.n.includes(t))score+=2;
      if(score>0&&(tokens.length<2||tokens.filter(t=>row.n.includes(t)).length>=Math.min(2,tokens.length)))scored.push({...row,score});
    }
    return scored.sort((a,b)=>b.score-a.score||a.book.localeCompare(b.book)||a.chapter-b.chapter||a.verse-b.verse).slice(0,limit);
  }
  function smartSearch(q){
    q=String(q||'').trim();if(!q)return [];
    remember(q);const out=[];
    const ref=window.__EBD_AI_1152__?.detectReference?.(q);if(ref){const vr=verseFromRef(`${ref.book} ${ref.chapter}${ref.verse?':'+ref.verse+(ref.endVerse&&ref.endVerse!==ref.verse?'-'+ref.endVerse:''):''}`);if(vr)out.push({kind:'reference',title:vr.ref,text:vr.text,ref:vr.open,icon:'📖',priority:100})}
    const topic=topicMatch(q);if(topic){out.push({kind:'topic',title:topic.title,text:`Seleção temática com ${topic.refs.length} passagens para começar o estudo.`,refs:topic.refs,icon:'💡',priority:90});for(const r of topic.refs){const vr=verseFromRef(r);if(vr)out.push({kind:'verse',title:vr.ref,text:vr.text,ref:r,icon:'📖',priority:75})}}
    const lx=lexMatch(q);if(lx)out.push({kind:'dictionary',title:lx.term,text:lx.def,term:lx.term,icon:'📚',priority:85});
    for(const p of atlasMatches(q))out.push({kind:'place',title:p.name,text:`${p.region} • ${p.summary}`,place:p.id,icon:p.icon,priority:80});
    const person=personMatch(q);if(person)out.push({kind:'person',title:person.name,text:person.summary,refs:person.refs,icon:'👤',priority:78});
    if(norm(q).includes('paulo')&&(norm(q).includes('preso')||norm(q).includes('prisao')||norm(q).includes('prisões'))){out.push({kind:'answer',title:'Prisões e custódia de Paulo',text:'Atos registra Paulo preso em Filipos, sob custódia a partir de Jerusalém, detido em Cesareia e depois em prisão domiciliar em Roma.',refs:['Atos 16','Atos 21-23','Atos 23-26','Atos 28'],icon:'⛓️',priority:95})}
    const shouldText=!topic&&(!lx||q.split(/\s+/).length>4)&&!ref;
    if(shouldText)for(const v of fullText(q,30))out.push({kind:'verse',title:`${v.book} ${v.chapter}:${v.verse}`,text:v.text,ref:`${v.book} ${v.chapter}:${v.verse}`,icon:'📖',priority:50+v.score});
    const seen=new Set();return out.sort((a,b)=>b.priority-a.priority).filter(x=>{const k=`${x.kind}|${x.title}`;if(seen.has(k))return false;seen.add(k);return true}).slice(0,40);
  }

  function chips(){return ['versículos sobre ansiedade','o que significa graça?','onde Paulo esteve preso?','Jerusalém','João 3:16'].map(x=>`<button data-smart-example="${esc(x)}">${esc(x)}</button>`).join('')}
  function refsHtml(refs){return `<div class="v1159-refs">${(refs||[]).map(r=>`<button data-smart-ref="${esc(r)}">${esc(r)}</button>`).join('')}</div>`}
  function resultHtml(r){
    const extra=r.refs?refsHtml(r.refs):'';
    return `<article class="v1159-result ${r.kind}" ${r.ref?`data-smart-ref="${esc(r.ref)}"`:''} ${r.term?`data-smart-term="${esc(r.term)}"`:''} ${r.place?`data-smart-place="${esc(r.place)}"`:''}><div class="ico">${r.icon||'🔎'}</div><div class="body"><small>${({reference:'REFERÊNCIA',topic:'TEMA',verse:'BÍBLIA',dictionary:'DICIONÁRIO',place:'ATLAS',person:'PESSOA',answer:'RESPOSTA LOCAL'}[r.kind]||'RESULTADO')}</small><strong>${esc(r.title)}</strong><p>${esc(r.text)}</p>${extra}</div><b>›</b></article>`;
  }
  function smartSearchPage(){
    const q=state.smartQuery1159||'',results=state.smartResults1159||[],h=history();
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Busca Inteligente</h1><p>Bíblia completa, temas, dicionário, pessoas e lugares.</p></div></div>
      <section class="v1159-search-hero"><div class="orb">⌕</div><div><span>BUSCA LOCAL • 31.098 VERSÍCULOS</span><strong>Pergunte do seu jeito</strong><small>Referências, palavras, temas e perguntas simples funcionam sem internet.</small></div></section>
      <div class="v1159-searchbox"><input class="field" id="smartInput1159" value="${esc(q)}" placeholder="Ex.: versículos sobre ansiedade"><button id="smartGo1159">Buscar</button></div>
      <div class="v1159-examples">${chips()}</div>
      ${q?`<div class="v1159-query-meta"><span>${results.length} resultado(s)</span><button id="askAiSearch1159">✦ Perguntar à IA</button></div>`:''}
      <div id="smartResults1159">${q?(results.length?results.map(resultHtml).join(''):'<div class="empty"><div class="big">🔎</div><strong>Nada encontrado localmente</strong><p>Tente palavras diferentes ou envie a pergunta ao Assistente IA.</p></div>'):(h.length?`<section class="v1159-history"><small>BUSCAS RECENTES</small>${h.map(x=>`<button data-smart-example="${esc(x)}">🕘 ${esc(x)}</button>`).join('')}</section>`:'<div class="empty"><div class="big">⌕</div><strong>Busque em todo o Bíblia EBD</strong><p>Experimente uma referência, tema, pessoa ou palavra da Bíblia.</p></div>')}</div>`;
  }

  function dictionaryPage(){
    const q=norm(state.dictQuery1159),type=state.dictType1159;
    const rows=LEXICON.filter(x=>(type==='Todos'||x.type===type)&&(!q||norm(x.term).includes(q)||norm(x.def).includes(q)));
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Dicionário</h1><p>Termos bíblicos e palavras do português usadas no estudo.</p></div></div>
      <section class="v1159-dict-head"><span>📚</span><div><strong>Dicionário Bíblico + Português</strong><small>${LEXICON.length} verbetes locais • funciona offline</small></div></section>
      <input class="field" id="dictInput1159" value="${esc(state.dictQuery1159||'')}" placeholder="Buscar: graça, remissão, mansidão..."><div class="v1159-filter">${['Todos','Bíblico','Português'].map(x=>`<button data-dict-type="${x}" class="${type===x?'active':''}">${x}</button>`).join('')}</div>
      <section class="v1159-dict-list">${rows.length?rows.map(x=>`<article data-dict-term="${esc(x.term)}"><div><small>${x.type.toUpperCase()}</small><strong>${esc(x.term)}</strong><p>${esc(x.def)}</p>${refsHtml(x.refs)}</div><button data-dict-ai="${esc(x.term)}">✦ IA</button></article>`).join(''):'<div class="empty"><div class="big">📚</div><strong>Termo não encontrado</strong><p>Tente outra palavra ou use a Busca Inteligente.</p></div>'}</section>`;
  }

  function atlasPage(){
    const q=norm(state.atlasQuery1159),region=state.atlasRegion1159;
    const regions=['Todos','Judeia','Galileia','Samaria','Síria','Macedônia','Acaia','Ásia Menor','Itália','Mesopotâmia','Deserto','Nordeste da África'];
    const rows=ATLAS.filter(p=>(region==='Todos'||norm(p.region).includes(norm(region)))&&(!q||norm(`${p.name} ${p.region} ${p.summary}`).includes(q)));
    const selected=ATLAS.find(x=>x.id===state.atlasSelected1159)||rows[0]||ATLAS[0];
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Atlas Bíblico</h1><p>Lugares, rotas de estudo e referências na Bíblia.</p></div></div>
      <section class="v1159-atlas-hero"><span>🗺️</span><div><strong>Atlas de estudo offline</strong><small>${ATLAS.length} lugares • referências abrem diretamente na Bíblia</small></div></section>
      <input class="field" id="atlasInput1159" value="${esc(state.atlasQuery1159||'')}" placeholder="Buscar lugar ou região..."><div class="v1159-region-scroll">${regions.map(x=>`<button data-atlas-region="${esc(x)}" class="${region===x?'active':''}">${esc(x)}</button>`).join('')}</div>
      <section class="v1159-journeys"><small>ROTAS DE ESTUDO</small>${JOURNEYS.map(j=>`<button data-journey1159="${j.id}"><span>${j.icon}</span><strong>${j.title}</strong><small>${j.stops.length} paradas</small></button>`).join('')}</section>
      <section class="v1159-place-detail"><div class="icon">${selected.icon}</div><div><small>${esc(selected.region)}</small><h2>${esc(selected.name)}</h2><p>${esc(selected.summary)}</p>${refsHtml(selected.refs)}<button class="ai" id="atlasAi1159">✦ Estudar este lugar com IA</button></div></section>
      <div class="v1159-place-grid">${rows.map(p=>`<button data-place1159="${p.id}" class="${p.id===selected.id?'active':''}"><span>${p.icon}</span><div><strong>${esc(p.name)}</strong><small>${esc(p.region)}</small></div></button>`).join('')}</div>`;
  }

  function bindRefs(){document.querySelectorAll('[data-smart-ref]').forEach(b=>b.onclick=e=>{e.stopPropagation();openRef(b.dataset.smartRef)})}
  function executeSearch(q){state.smartQuery1159=String(q||'').trim();state.smartResults1159=smartSearch(state.smartQuery1159);window.render()}
  function bindSearch(){
    const input=document.getElementById('smartInput1159');document.getElementById('smartGo1159')?.addEventListener('click',()=>executeSearch(input?.value));input?.addEventListener('keydown',e=>{if(e.key==='Enter')executeSearch(input.value)});
    document.querySelectorAll('[data-smart-example]').forEach(b=>b.onclick=()=>executeSearch(b.dataset.smartExample));
    document.querySelectorAll('.v1159-result[data-smart-ref]').forEach(b=>b.onclick=()=>openRef(b.dataset.smartRef));
    document.querySelectorAll('[data-smart-term]').forEach(b=>b.onclick=()=>{state.dictQuery1159=b.dataset.smartTerm;nav('dictionary')});
    document.querySelectorAll('[data-smart-place]').forEach(b=>b.onclick=()=>{state.atlasSelected1159=b.dataset.smartPlace;nav('atlas114')});
    document.getElementById('askAiSearch1159')?.addEventListener('click',()=>{const q=state.smartQuery1159;if(!q)return;window.__EBD_AI_115__?.openWithContext?.(null,'ask',q)});bindRefs();
  }
  function bindDictionary(){
    const inp=document.getElementById('dictInput1159');inp?.addEventListener('input',()=>{state.dictQuery1159=inp.value;clearTimeout(window.__dictTimer1159);window.__dictTimer1159=setTimeout(()=>window.render(),180)});
    document.querySelectorAll('[data-dict-type]').forEach(b=>b.onclick=()=>{state.dictType1159=b.dataset.dictType;window.render()});
    document.querySelectorAll('[data-dict-ai]').forEach(b=>b.onclick=e=>{e.stopPropagation();const term=b.dataset.dictAi,entry=LEXICON.find(x=>x.term===term);window.__EBD_AI_115__?.openWithContext?.(entry?{kind:'dictionary',title:entry.term,reference:entry.refs.join(' • '),text:entry.def}:null,'explain',`Explique o termo “${term}” no contexto bíblico, com exemplos e cuidados de interpretação.`)});bindRefs();
  }
  function journeyHtml(j){const stops=j.stops.map(id=>ATLAS.find(p=>p.id===id)).filter(Boolean);return `<section class="v1159-journey-detail" id="journeyDetail1159"><div><span>${j.icon}</span><strong>${j.title}</strong><button id="closeJourney1159">✕</button></div>${stops.map((p,i)=>`<button data-place1159="${p.id}"><b>${i+1}</b><span>${p.icon}</span><div><strong>${esc(p.name)}</strong><small>${esc(p.region)}</small></div></button>`).join('')}</section>`}
  function bindAtlas(){
    const inp=document.getElementById('atlasInput1159');inp?.addEventListener('input',()=>{state.atlasQuery1159=inp.value;clearTimeout(window.__atlasTimer1159);window.__atlasTimer1159=setTimeout(()=>window.render(),180)});
    document.querySelectorAll('[data-atlas-region]').forEach(b=>b.onclick=()=>{state.atlasRegion1159=b.dataset.atlasRegion;window.render()});
    document.querySelectorAll('[data-place1159]').forEach(b=>b.onclick=()=>{state.atlasSelected1159=b.dataset.place1159;window.render()});
    document.querySelectorAll('[data-journey1159]').forEach(b=>b.onclick=()=>{const j=JOURNEYS.find(x=>x.id===b.dataset.journey1159),old=document.getElementById('journeyDetail1159');old?.remove();if(j){document.querySelector('.v1159-journeys')?.insertAdjacentHTML('afterend',journeyHtml(j));bindAtlas()}});
    document.getElementById('closeJourney1159')?.addEventListener('click',()=>document.getElementById('journeyDetail1159')?.remove());
    document.getElementById('atlasAi1159')?.addEventListener('click',()=>{const p=ATLAS.find(x=>x.id===state.atlasSelected1159);if(p)window.__EBD_AI_115__?.openWithContext?.({kind:'atlas-place',title:p.name,reference:p.refs.join(' • '),text:`${p.region}. ${p.summary}`},'context',`Explique a importância bíblica de ${p.name}, destacando os acontecimentos ligados às referências fornecidas.`)});bindRefs();
  }

  function post(){if(state.route==='search')bindSearch();if(state.route==='dictionary')bindDictionary();if(state.route==='atlas114')bindAtlas()}
  window.render=function(){
    if(state.route==='search'){document.getElementById('app').innerHTML=smartSearchPage();document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.toggle('active',b.dataset.route==='search'));window.bind();return}
    if(state.route==='dictionary'){document.getElementById('app').innerHTML=dictionaryPage();document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
    if(state.route==='atlas114'){document.getElementById('app').innerHTML=atlasPage();document.querySelectorAll('.bottomnav [data-route]').forEach(b=>b.classList.remove('active'));window.bind();return}
    previousRender();post();
  };
  window.bind=function(){previousBind();post()};
  window.__EBD_SMART_1159__=Object.freeze({search:smartSearch,lexicon:LEXICON,topics:TOPICS,atlas:ATLAS,journeys:JOURNEYS});
  window.render();
})();
