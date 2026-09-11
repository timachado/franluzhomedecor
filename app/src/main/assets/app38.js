// 1.17.1 — escala global segura: aplica zoom nativo somente quando o valor muda.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  const KEY='ebd-ui-scale-v1170';
  const LEVELS=[100,112,120,125];
  let lastNativeScale=null;

  function normalize(value){
    const n=Number(value||112);
    if(n===140)return 125; // migração da 1.17.0: 140% era agressivo demais para layouts móveis.
    if(LEVELS.includes(n))return n;
    if(n<106)return 100;
    if(n<116)return 112;
    if(n<123)return 120;
    return 125;
  }
  function load(){try{return normalize(localStorage.getItem(KEY)||112)}catch(_){return 112}}
  function save(value){try{localStorage.setItem(KEY,String(normalize(value)))}catch(_){}}
  function apply(value,showToast){
    const scale=normalize(value);save(scale);
    document.documentElement.dataset.uiScale1170=String(scale);
    document.body?.classList.remove('v1170-scale-100','v1170-scale-112','v1170-scale-120','v1170-scale-125','v1170-scale-140');
    document.body?.classList.add(`v1170-scale-${scale}`);

    // Não reaplica TextZoom em cada render. Na 1.17.0 isso podia causar reflow
    // durante toques em Perfil, selects e outros controles.
    if(lastNativeScale!==scale){
      lastNativeScale=scale;
      try{window.AndroidBridge?.setTextScale?.(scale)}catch(_){}
    }
    if(showToast)try{window.toast?.(`Tamanho do aplicativo: ${scale}%`)}catch(_){}
    return scale;
  }
  function current(){return load()}
  function scaleCard(){
    const value=current();
    const label=n=>n===100?'Padrão':n===112?'Confortável':n===120?'Grande':'Extra grande';
    return `<section class="v1170-setting" id="globalScale1170"><div class="v1170-setting-head"><div><span>🔠</span><div><strong>Tamanho do aplicativo</strong><small>Aumenta fontes, ícones, menus e botões em todo o Bíblia EBD.</small></div></div><b>${value}%</b></div><div class="v1170-scale-row">${LEVELS.map(n=>`<button type="button" data-ui-scale1170="${n}" class="${value===n?'active':''}">${label(n)}<small>${n}%</small></button>`).join('')}</div><p class="v1170-help">A preferência fica salva neste aparelho. O limite de 125% preserva o encaixe e as áreas de toque em telas móveis.</p></section>`;
  }
  function injectSettings(){
    if(typeof state==='undefined'||state.route!=='settings112')return;
    if(document.getElementById('globalScale1170'))return;
    const device=document.querySelector('.v112-device-card');
    if(device)device.insertAdjacentHTML('afterend',scaleCard());
    else document.getElementById('app')?.insertAdjacentHTML('afterbegin',scaleCard());
  }
  function injectTools(){
    if(typeof state==='undefined'||state.route!=='tools')return;
    if(document.getElementById('globalScaleShortcut1170'))return;
    const app=document.getElementById('app');if(!app)return;
    app.insertAdjacentHTML('afterbegin',`<section class="v1170-shortcut" id="globalScaleShortcut1170"><span>🔠</span><div><strong>Tamanho do aplicativo</strong><small>Atual: ${current()}% • fontes, ícones e botões</small></div><button type="button" data-route="settings112">Ajustar</button></section>`);
  }
  function bindScale(){
    // Escopo estrito: só os botões dentro do card de escala podem mudar o zoom.
    document.querySelectorAll('#globalScale1170 [data-ui-scale1170]').forEach(button=>{
      button.onclick=event=>{
        event.preventDefault();
        event.stopPropagation();
        apply(Number(button.dataset.uiScale1170),true);
        window.render();
      };
    });
    document.querySelectorAll('#globalScaleShortcut1170 [data-route]').forEach(button=>button.onclick=event=>{event.preventDefault();event.stopPropagation();nav(button.dataset.route)});
  }
  function post(){
    apply(current(),false);
    injectSettings();
    injectTools();
    bindScale();
  }

  window.render=function(){previousRender();requestAnimationFrame(post)};
  window.bind=function(){previousBind();post()};
  window.__EBD_UI_SCALE_1170__=Object.freeze({levels:LEVELS,current,apply});
  apply(current(),false);
  window.render();
})();
