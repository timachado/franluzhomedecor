// Bíblia EBD 1.15.2 — proxy seguro para OpenAI Responses API.
// Segredos exigidos no ambiente Supabase: OPENAI_API_KEY e BIBLIA_EBD_AI_ACCESS_TOKEN.
const CORS={
  'Access-Control-Allow-Origin':'*',
  'Access-Control-Allow-Headers':'content-type,x-biblia-access',
  'Access-Control-Allow-Methods':'GET,POST,OPTIONS',
  'Content-Type':'application/json; charset=utf-8'
};
const MAX_QUESTION=4000;
const MAX_CONTEXT=16000;
const ACTIONS=new Set(['check','ask','explain','summary','context','outline','ebd']);

function json(data:unknown,status=200){return new Response(JSON.stringify(data),{status,headers:CORS})}
function clean(value:unknown,max:number){return String(value??'').trim().slice(0,max)}
function actionInstruction(action:string,mode:string){
  const role=mode==='Professor'?'professor de Escola Bíblica Dominical':'aluno/estudante da Bíblia';
  const base=`Responda em português do Brasil para um ${role}. Seja claro, respeitoso e útil para estudo cristão. Diferencie explicitamente o texto bíblico fornecido de interpretação, explicação ou aplicação. Quando houver contexto bíblico anexado pelo aplicativo, esse texto vem da base local João Ferreira de Almeida em domínio público, salvo indicação explícita em contrário. Não peça ao usuário qual tradução está usando quando o texto bíblico local já tiver sido anexado. Nunca invente versículos, citações ou fatos como se estivessem no contexto. Se o contexto não for suficiente, diga isso. Não alegue autoridade divina, revelação pessoal ou certeza doutrinária absoluta.`;
  const task:Record<string,string>={
    ask:'Responda à pergunta com base prioritária no contexto bíblico fornecido.',
    explain:'Explique a passagem com mensagem central, contexto imediato, pontos-chave e aplicação prática.',
    summary:'Produza um resumo fiel e conciso, seguido de pontos essenciais.',
    context:'Explique contexto histórico e literário apenas até onde houver base; sinalize claramente inferências.',
    outline:'Crie um esboço de estudo/pregação com título, texto-base, introdução, três pontos, aplicação e conclusão.',
    ebd:'Crie um roteiro de aula EBD com objetivos, introdução, desenvolvimento, perguntas, dinâmica simples e aplicação.'
  };
  return `${base}\n\nTarefa: ${task[action]||task.ask}`;
}
function extractText(data:any){
  if(typeof data?.output_text==='string'&&data.output_text.trim())return data.output_text.trim();
  const parts=[];
  for(const item of Array.isArray(data?.output)?data.output:[]){
    if(item?.type!=='message')continue;
    for(const c of Array.isArray(item.content)?item.content:[]){if(c?.type==='output_text'&&typeof c.text==='string')parts.push(c.text)}
  }
  return parts.join('\n').trim();
}

Deno.serve(async(req:Request)=>{
  if(req.method==='OPTIONS')return new Response(null,{status:204,headers:CORS});
  const apiKey=Deno.env.get('OPENAI_API_KEY')||'';
  const accessExpected=Deno.env.get('BIBLIA_EBD_AI_ACCESS_TOKEN')||'';
  const model=Deno.env.get('OPENAI_MODEL')||'gpt-5.6-luna';
  if(req.method==='GET')return json({online:true,configured:!!apiKey&&!!accessExpected,model:apiKey?model:null});
  if(req.method!=='POST')return json({message:'Método não permitido.'},405);
  if(!apiKey||!accessExpected)return json({message:'Assistente IA ainda não foi configurado no servidor.'},503);
  const access=req.headers.get('x-biblia-access')||'';
  if(access.length<16||access!==accessExpected)return json({message:'Código privado da IA inválido.'},401);

  let body:any;
  try{body=await req.json()}catch(_){return json({message:'Requisição inválida.'},400)}
  const action=clean(body?.action,24);
  if(!ACTIONS.has(action))return json({message:'Ação inválida.'},400);
  if(action==='check')return json({ok:true,configured:true,model});

  const question=clean(body?.question,MAX_QUESTION);
  const mode=clean(body?.mode,24)==='Professor'?'Professor':'Aluno';
  if(!question)return json({message:'Pergunta inválida.'},400);
  const c=body?.context&&typeof body.context==='object'?body.context:null;
  const context=c?{
    kind:clean(c.kind,64),title:clean(c.title,240),reference:clean(c.reference,160),text:clean(c.text,MAX_CONTEXT)
  }:null;
  const input=[
    `Pergunta do usuário: ${question}`,
    context?`Contexto anexado pelo usuário:\nFonte bíblica do aplicativo: João Ferreira de Almeida (domínio público)\nTipo: ${context.kind}\nTítulo: ${context.title}\nReferência: ${context.reference}\nTexto:\n${context.text}`:'Nenhum texto bíblico foi anexado. Não invente conteúdo de passagem; peça referência quando necessário.'
  ].join('\n\n');

  try{
    const upstream=await fetch('https://api.openai.com/v1/responses',{
      method:'POST',headers:{'Authorization':`Bearer ${apiKey}`,'Content-Type':'application/json'},
      body:JSON.stringify({
        model,
        store:false,
        reasoning:{effort:'low'},
        max_output_tokens:1400,
        instructions:actionInstruction(action,mode),
        input
      })
    });
    const data=await upstream.json().catch(()=>({}));
    if(!upstream.ok){
      const message=upstream.status===429?'Limite temporário da IA atingido. Tente novamente em instantes.':'Não foi possível obter resposta da IA.';
      console.error('OpenAI upstream',upstream.status,data?.error?.code||'unknown');
      return json({message},upstream.status===429?429:502);
    }
    const answer=extractText(data);
    if(!answer)return json({message:'A IA respondeu sem texto utilizável.'},502);
    return json({answer,model:data?.model||model,responseId:data?.id||null});
  }catch(err){
    console.error('biblia-ai error',String(err));
    return json({message:'Falha temporária ao conectar com o provedor de IA.'},502);
  }
});
