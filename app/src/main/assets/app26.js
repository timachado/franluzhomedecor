// 1.15.2 — referência bíblica digitada -> contexto local visível + formatação segura das respostas.
(function(){
  'use strict';

  const previousRender=window.render;
  const previousBind=window.bind;
  let ignoredQuestion='';

  function norm1152(value=''){
    try{if(typeof norm18==='function')return norm18(value)}catch(_){}
    return String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  }
  function esc1152(value=''){
    return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#039;'}[c]));
  }
  function escapeRe1152(value=''){return String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}

  function allBookCandidates1152(){
    const out=[];
    try{
      if(typeof BIBLE_META_V18!=='undefined'){
        BIBLE_META_V18.forEach(b=>out.push({token:norm1152(b.name),book:b.name,priority:2}));
      }
      if(typeof ALIASES_V18!=='undefined'){
        Object.entries(ALIASES_V18).forEach(([alias,book])=>{
          const token=norm1152(alias);
          if(token.length>=2)out.push({token,book,priority:1});
        });
      }
    }catch(_){}
    const seen=new Set();
    return out.filter(x=>{const k=`${x.token}|${x.book}`;if(seen.has(k))return false;seen.add(k);return true})
      .sort((a,b)=>b.priority-a.priority||b.token.length-a.token.length);
  }

  function detectReference1152(question=''){
    const q=norm1152(question).replace(/[–—]/g,'-');
    if(!q)return null;
    for(const item of allBookCandidates1152()){
      const token=escapeRe1152(item.token);
      // Aceita: Efésios 4:13, Efésios capítulo 4 versículo 13, Ef 4 13, Sl 23.
      const re=new RegExp(`(?:^|[^a-z0-9])${token}\\s+(?:capitulo\\s+)?(\\d{1,3})(?:\\s*(?:(?:versiculo|versiculos)\\s+|[:.,]\\s*|\\s+)(\\d{1,3})(?:\\s*(?:-|a|ate)\\s*(\\d{1,3}))?)?`,'i');
      const m=q.match(re);if(!m)continue;
      const chapter=Number(m[1]),verse=m[2]?Number(m[2]):null,endVerse=m[3]?Number(m[3]):verse;
      let meta=null,verses=[];
      try{meta=typeof bookMeta18==='function'?bookMeta18(item.book):null;verses=typeof chapterVerses18==='function'?chapterVerses18(item.book,chapter)||[]:[]}catch(_){}
      const maxCh=Number(meta?.chapters||0);
      if(!chapter||chapter<1||(maxCh&&chapter>maxCh)||!verses.length)continue;
      if(verse!==null&&(verse<1||verse>verses.length||endVerse<verse||endVerse>verses.length))continue;
      return {book:item.book,chapter,verse,endVerse};
    }
    return null;
  }

  function contextFromRef1152(ref){
    if(!ref)return null;
    let verses=[];try{verses=chapterVerses18(ref.book,ref.chapter)||[]}catch(_){return null}
    if(!verses.length)return null;
    if(ref.verse){
      const end=ref.endVerse||ref.verse;
      const rows=[];for(let v=ref.verse;v<=end;v++)rows.push(`${ref.book} ${ref.chapter}:${v} — ${verses[v-1]}`);
      const label=`${ref.book} ${ref.chapter}:${ref.verse}${end!==ref.verse?'-'+end:''}`;
      return {_auto1152:true,kind:end===ref.verse?'bible-verse':'bible-selection',title:label,reference:label,text:rows.join('\n')};
    }
    return {_auto1152:true,kind:'bible-chapter',title:`${ref.book} ${ref.chapter}`,reference:`${ref.book} ${ref.chapter}`,text:verses.map((t,i)=>`${i+1}. ${t}`).join('\n')};
  }

  function contextHtml1152(ctx){
    const excerpt=String(ctx?.text||'').slice(0,260);
    return `<span>📖</span><div><small>REFERÊNCIA DETECTADA • TEXTO DA BÍBLIA LOCAL</small><strong>${esc1152(ctx.reference||ctx.title||'Passagem')}</strong><p>${esc1152(excerpt)}${String(ctx?.text||'').length>260?'…':''}</p></div><button id="clearAutoContext1152" aria-label="Remover contexto">✕</button>`;
  }
  function emptyContextHtml1152(){
    return '<span>📎</span><div><strong>Sem contexto anexado</strong><small>Digite uma referência, como Efésios 4:13, ou abra a IA pela Bíblia/EBD.</small></div>';
  }

  function patchContextCard1152(){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    const ctx=state.ai115?.context;
    const card=document.querySelector('.ai115-context');
    if(!card)return;
    if(ctx?._auto1152){
      card.classList.remove('emptyctx');
      card.innerHTML=contextHtml1152(ctx);
      const clear=document.getElementById('clearAutoContext1152');
      if(clear)clear.onclick=()=>{
        ignoredQuestion=String(document.getElementById('aiQuestion115')?.value||'');
        state.ai115.context=null;
        card.classList.add('emptyctx');card.innerHTML=emptyContextHtml1152();
      };
    }
  }

  function syncQuestionContext1152(force=false){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    const field=document.getElementById('aiQuestion115');if(!field)return;
    const question=String(field.value||'');
    if(question!==ignoredQuestion)ignoredQuestion='';
    const existing=state.ai115?.context;
    if(existing&&!existing._auto1152)return; // Contexto vindo da Bíblia/EBD tem prioridade.
    if(!question.trim()&&existing?._auto1152)return; // Mantém a referência após o envio para salvar/compartilhar a resposta corretamente.
    if(!force&&ignoredQuestion===question)return;
    const detected=detectReference1152(question);
    if(detected){
      const ctx=contextFromRef1152(detected);
      if(ctx){state.ai115.context=ctx;patchContextCard1152();return}
    }
    if(existing?._auto1152){state.ai115.context=null;const card=document.querySelector('.ai115-context');if(card){card.classList.add('emptyctx');card.innerHTML=emptyContextHtml1152()}}
  }

  function bindQuestionDetector1152(){
    const field=document.getElementById('aiQuestion115');if(!field||field.dataset.ref1152==='1')return;
    field.dataset.ref1152='1';
    field.addEventListener('input',()=>syncQuestionContext1152(false));
    field.addEventListener('blur',()=>syncQuestionContext1152(false));
    syncQuestionContext1152(false);
  }

  function formatAiMessages1152(){
    document.querySelectorAll('.ai115-msg.assistant .ai115-bubble p').forEach(p=>{
      if(p.dataset.md1152==='1')return;
      // app24 escapa HTML antes de inserir a resposta; por isso esta conversão limitada é segura.
      let html=p.innerHTML;
      html=html.replace(/\*\*([^*<>]+)\*\*/g,'<strong>$1</strong>');
      html=html.replace(/(^|<br>)\s*[-•]\s+([^<]+)/g,'$1<span class="ai1152-bullet">• $2</span>');
      p.innerHTML=html;p.dataset.md1152='1';
    });
  }

  function patch1152(){
    if(typeof state==='undefined'||state.route!=='ai115')return;
    bindQuestionDetector1152();patchContextCard1152();formatAiMessages1152();
  }

  window.render=function(){previousRender();requestAnimationFrame(patch1152)};
  window.bind=function(){previousBind();patch1152()};
  window.__EBD_AI_1152__=Object.freeze({detectReference:detectReference1152,contextFromRef:contextFromRef1152});
  window.render();
})();
