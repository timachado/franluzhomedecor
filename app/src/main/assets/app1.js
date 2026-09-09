const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const state={route:location.hash.replace('#/','')||'home',book:'Gênesis',chapter:1,ebdTab:'revistas',notes:JSON.parse(localStorage.getItem('ebd-notes-dark')||'[]'),favs:JSON.parse(localStorage.getItem('ebd-favs-dark')||'[]'),publicNotes:JSON.parse(localStorage.getItem('ebd-public-dark')||'[]')};
const chapterCounts={'Gênesis':50,'Êxodo':40,'Levítico':27,'Números':36,'Deuteronômio':34,'Josué':24,'Juízes':21,'Rute':4,'1 Samuel':31,'2 Samuel':24,'Salmos':150,'Provérbios':31,'Isaías':66,'Jeremias':52,'Mateus':28,'Marcos':16,'Lucas':24,'João':21,'Atos':28,'Romanos':16,'Tiago':5,'Apocalipse':22};
const demo={
'Gênesis 1':['No princípio, criou Deus os céus e a terra.','A terra era sem forma e vazia; havia trevas sobre a face do abismo, e o Espírito de Deus se movia sobre as águas.','E disse Deus: Haja luz. E houve luz.','E viu Deus que era boa a luz; e fez Deus separação entre a luz e as trevas.','E Deus chamou à luz Dia; e às trevas chamou Noite. E foi a tarde e a manhã, o dia primeiro.','E disse Deus: Haja uma expansão no meio das águas, e haja separação entre águas e águas.'],
'Gênesis 2':['Assim os céus, a terra e todo o seu exército foram acabados.','E, havendo Deus acabado no dia sétimo a sua obra, descansou no sétimo dia de toda a sua obra.','E abençoou Deus o dia sétimo e o santificou.'],
'Salmos 23':['O Senhor é o meu pastor; nada me faltará.','Deitar-me faz em verdes pastos, guia-me mansamente a águas tranquilas.','Refrigera a minha alma; guia-me pelas veredas da justiça, por amor do seu nome.','Ainda que eu andasse pelo vale da sombra da morte, não temeria mal algum, porque tu estás comigo.'],
'Tiago 1':['Tiago, servo de Deus e do Senhor Jesus Cristo, às doze tribos que andam dispersas, saúde.','Meus irmãos, tende grande gozo quando cairdes em várias tentações.','Sabendo que a prova da vossa fé obra a paciência.','Tenha, porém, a paciência a sua obra perfeita.'],
'João 3':['E havia entre os fariseus um homem, chamado Nicodemos, príncipe dos judeus.','Este foi ter de noite com Jesus e disse-lhe: Rabi, bem sabemos que és Mestre vindo de Deus.','Jesus respondeu e disse-lhe: Na verdade, na verdade te digo que aquele que não nascer de novo não pode ver o reino de Deus.']
};
const books=Object.keys(chapterCounts);
const hymns=[
{n:1,title:'Chuvas de Graça',theme:'Graça e avivamento'},{n:15,title:'Conversão',theme:'Salvação'},{n:39,title:'Alvo Mais Que a Neve',theme:'Purificação'},{n:187,title:'Mais Perto, Meu Deus, de Ti',theme:'Comunhão'},{n:212,title:'Os Guerreiros se Preparam',theme:'Vigilância'},{n:525,title:'Vencendo Vem Jesus',theme:'Esperança'}
];
const dict={
'graça':{title:'Graça',def:'Favor imerecido de Deus, revelado em sua bondade, misericórdia e ação salvadora.',refs:'Efésios 2:8 • Tito 2:11 • Romanos 3:24'},
'fé':{title:'Fé',def:'Confiança em Deus que se expressa em convicção, perseverança e obediência.',refs:'Hebreus 11:1 • Romanos 10:17 • Tiago 2:17'},
'aliança':{title:'Aliança',def:'Compromisso solene que estrutura relacionamentos e promessas no testemunho bíblico.',refs:'Gênesis 9 • Gênesis 15 • Jeremias 31:31'},
'oração':{title:'Oração',def:'Comunicação reverente com Deus em adoração, petição, intercessão e gratidão.',refs:'Mateus 6:9-13 • Filipenses 4:6 • 1 Tessalonicenses 5:17'}
};
const ebdLesson={title:'A Palavra que transforma a vida',golden:'Sede praticantes da palavra e não somente ouvintes.',truth:'O estudo bíblico alcança seu propósito quando a verdade compreendida se transforma em vida praticada.',objectives:['Entender a diferença entre ouvir e praticar.','Relacionar conhecimento bíblico com obediência diária.','Definir uma aplicação prática para a semana.']};
function nav(r){state.route=r;location.hash='#/'+r;render();scrollTo(0,0);closeMenu()}
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1700)}
function save(){localStorage.setItem('ebd-notes-dark',JSON.stringify(state.notes));localStorage.setItem('ebd-favs-dark',JSON.stringify(state.favs));localStorage.setItem('ebd-public-dark',JSON.stringify(state.publicNotes))}
function tool(emo,title,sub,cls,route,tag=''){return `<button class="tool ${cls}" data-route="${route}">${tag?`<span class="tag">${tag}</span>`:''}<span class="emo">${emo}</span><strong>${title}</strong><small>${sub}</small></button>`}
function home(){return `<section class="welcome"><span class="tiny">Seja muito bem-vindo!</span><h1>Olá, Cristão 👋</h1><p>Continue sua jornada espiritual com a Palavra Sagrada.</p></section>
<section class="section"><div class="section-title"><div><h2>Continuar leitura</h2><small>Retome de onde parou</small></div></div><div class="continue" data-route="reader"><div class="bookico">📖</div><div><strong>${state.book} ${state.chapter}</strong><span>Leitura e ferramentas do capítulo</span></div><button class="go">›</button></div></section>
<section class="section"><div class="section-title"><div><h2>Ferramentas principais</h2><small>Todas as áreas já conectadas</small></div></div><div class="tools">
${tool('📖','Bíblia Sagrada','Leitura, capítulos e estudo.','purple','bible')}
${tool('🎵','Harpa Cristã','Busca e lista de hinos.','red','harpa')}
${tool('❤️','Versículos Favoritos','Seus trechos marcados.','orange','favorites')}
${tool('📝','Minhas Anotações','Seu estudo pessoal.','yellow','notes')}
${tool('🔗','Anotações Públicas','Compartilhe estudos locais.','pink','publicNotes')}
${tool('🗂️','Criador de Esboços','Crie esboços bíblicos.','orange','outlines','AI')}
${tool('📚','Dicionário Bíblico','Termos e referências.','green','dictionary')}
${tool('🎓','Escola Bíblica','Revistas, lições e professor.','blue','ebd')}
${tool('🔎','Concordância Bíblica','Encontre palavras na base.','teal','concordance')}
${tool('🛠️','Novas Ferramentas','Planos, quiz e recursos.','outline','tools')}
</div></section>
<section class="section"><div class="panel quote"><p>“A tua palavra é lâmpada para os meus pés e luz para o meu caminho.”</p><small>Salmos 119:105</small></div></section>`}
function bible(){return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Escolha um Livro</h1><p>Navegue pelas Escrituras Sagradas.</p></div></div><select class="field" id="version"><option>Almeida clássica • demonstração</option><option>Versão licenciada futura</option></select><div class="row" style="margin-top:8px"><input class="field" id="bookSearch" placeholder="Digite o nome do livro..."></div><div class="subhead">Livros recentes</div><div class="chips"><button class="chip" data-openbook="Gênesis">Gênesis</button><button class="chip" data-openbook="Salmos">Salmos</button><button class="chip" data-openbook="Tiago">Tiago</button><button class="chip" data-openbook="João">João</button></div><div class="subhead">Livros</div><div class="book-list" id="bookList">${books.map(b=>`<button class="book" data-openbook="${b}"><strong>${b}</strong><small>${chapterCounts[b]} capítulos</small></button>`).join('')}</div>`}
function reader(){const key=state.book+' '+state.chapter,vs=demo[key]||['Este capítulo ainda não está incluído na base demonstrativa. A navegação já está funcional e receberá o texto completo na integração da Bíblia de domínio público/licenciada.'];const max=chapterCounts[state.book]||1;return `<div class="reader-nav"><button id="prevChapter" ${state.chapter<=1?'disabled':''}>‹</button><select class="field" id="chapterSelect">${Array.from({length:max},(_,i)=>`<option value="${i+1}" ${i+1===state.chapter?'selected':''}>Capítulo ${i+1}</option>`).join('')}</select><button id="nextChapter" ${state.chapter>=max?'disabled':''}>›</button></div><div class="chapter-card"><div class="rowtop"><div><h2>${state.book}</h2><small>Capítulo ${state.chapter}</small></div><div class="num">${state.chapter}</div></div><p style="font-size:9px;margin:8px 0 0">Toque em um versículo para abrir ações de favorito e anotação.</p></div>
<div class="accordion"><div class="acc-head">📚 ESTUDOS DO CAPÍTULO <span>⌄</span></div><div class="acc-body"><b>Contexto</b><p>Observe o tema central, as repetições, os contrastes e a relação do capítulo com o livro inteiro.</p><b>Aplicação para EBD</b><p>Transforme a ideia principal em uma pergunta de participação e uma ação prática.</p></div></div>
<div class="tip"><b>💡 Dica de leitura</b><br>Leia primeiro sem interrupções. Depois releia marcando palavras-chave e perguntas.</div>
<div class="orange-label">Texto do capítulo</div><div class="panel">${vs.map((v,i)=>`<div class="verse" data-verse="${i+1}"><span class="vnum">${i+1}</span>${v}<div class="verse-actions"><button data-fav="${i+1}">❤️ Favoritar</button><button data-noteverse="${i+1}">📝 Anotar</button></div></div>`).join('')}</div>`}