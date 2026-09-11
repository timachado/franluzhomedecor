// 1.16.1 — ação direta para autorizar notificações no Diagnóstico.
(function(){
  'use strict';
  const previousRender=window.render;
  const previousBind=window.bind;
  let requesting=false;

  function toastMsg(message){try{window.toast?.(message)}catch(_){}}
  function granted(){
    try{return !!window.AndroidBridge?.notificationPermissionGranted?.()}catch(_){return false}
  }
  function notificationCard(){
    return document.querySelector('.v1160-result[data-diag-id="notification"]');
  }
  function decorate(){
    if(typeof state==='undefined'||state.route!=='diagnostics1160')return;
    const card=notificationCard();if(!card)return;
    card.querySelector('.v1161-notif-action')?.remove();
    if(granted())return;
    const box=document.createElement('div');
    box.className='v1161-notif-action';
    box.innerHTML='<small>É uma permissão opcional do Android. Ela é necessária apenas para receber os lembretes locais da EBD.</small><button id="enableNotifications1161">🔔 Ativar notificações</button>';
    card.appendChild(box);
    document.getElementById('enableNotifications1161')?.addEventListener('click',requestPermission);
  }
  function requestPermission(){
    if(requesting)return;
    if(granted()){refresh(true);return}
    requesting=true;
    const button=document.getElementById('enableNotifications1161');
    if(button){button.disabled=true;button.textContent='Abrindo permissão…'}
    try{
      window.AndroidBridge?.requestNotificationPermission?.();
      setTimeout(()=>{
        requesting=false;
        if(granted())refresh(true);
        else {
          const btn=document.getElementById('enableNotifications1161');
          if(btn){btn.disabled=false;btn.textContent='🔔 Ativar notificações'}
        }
      },1800);
    }catch(_){requesting=false;toastMsg('Não foi possível abrir a permissão de notificações.')}
  }
  function refresh(fromPermission){
    if(typeof state==='undefined'||state.route!=='diagnostics1160')return;
    const card=notificationCard();
    if(granted()){
      if(fromPermission)toastMsg('Notificações ativadas 🔔');
      if(fromPermission||!card||card.classList.contains('warn'))window.__EBD_DIAGNOSTICS_1160__?.run?.();
      return;
    }
    requestAnimationFrame(decorate);
  }
  function permissionResult(ok){
    requesting=false;
    if(ok){refresh(true);return}
    toastMsg('Permissão não concedida. Os demais recursos continuam funcionando normalmente.');
    requestAnimationFrame(decorate);
  }
  function post(){requestAnimationFrame(decorate)}

  window.render=function(){previousRender();post()};
  window.bind=function(){previousBind();post()};
  window.__EBD_NOTIFICATIONS_1161__=Object.freeze({refresh:()=>refresh(false),permissionResult});
  post();
})();
