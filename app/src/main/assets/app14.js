// Compatibilidade da fonte privada da Harpa: aceita lista [{n,title,lyrics}] ou mapa {"1":"..."}.
function harpaRow111(n){
 const src=window.HARPA_LYRICS_USER||{},num=Number(n);
 if(Array.isArray(src)){
  const direct=src[num-1];
  if(direct&&Number(direct.n)===num)return direct;
  return src.find(x=>x&&Number(x.n)===num)||null;
 }
 const raw=src[String(num)];
 if(typeof raw==='string')return {n:num,lyrics:raw};
 return raw&&typeof raw==='object'?raw:null;
}
lyric191=function(n){const r=harpaRow111(n);return r?String(r.lyrics||r.text||''):''};
harpaReady191=function(){
 const src=window.HARPA_LYRICS_USER||{};
 if(Array.isArray(src))return src.length===640&&src.every((x,i)=>x&&Number(x.n)===i+1&&String(x.lyrics||'').trim());
 return Array.from({length:640},(_,i)=>String(src[String(i+1)]?.lyrics||src[String(i+1)]||'').trim()).every(Boolean);
};
hymnSearchMatch191=function(h,q){
 if(!q)return true;
 const raw=String(q).trim(),n=norm18(raw),l=norm18(lyric191(h.n));
 return String(h.n).includes(raw)||norm18(h.title).includes(n)||l.includes(n);
};
window.render();
