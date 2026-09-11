// 1.14.2 — Backup completo, validação e restauração segura.
(function () {
  'use strict';

  const previousRender = window.render;
  const previousBind = window.bind;
  const BACKUP_SCHEMA = 'biblia-ebd-local-backup';
  const BACKUP_FORMAT = 2;
  const AUTO_ROLLBACK_KEY = 'ebd-auto-backup-before-restore-v1142';
  const EXCLUDED_PREFIXES = ['ebd-recovery-v1141-'];
  const EXCLUDED_KEYS = new Set(['ebd-last-error-v1141', AUTO_ROLLBACK_KEY]);
  const MAX_BACKUP_CHARS = 4 * 1024 * 1024;
  let pendingRestore = null;

  function app1142() { return document.getElementById('app'); }
  function esc1142(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  }
  function toast1142(message) {
    if (typeof window.toast === 'function') window.toast(message);
    else console.log('[Bíblia EBD]', message);
  }
  function currentVersion1142() {
    try {
      if (window.AndroidBridge && typeof window.AndroidBridge.appVersion === 'function') return window.AndroidBridge.appVersion();
    } catch (_) {}
    return '1.14.2';
  }
  function isBackupKey1142(key) {
    return typeof key === 'string' && key.startsWith('ebd-') && !EXCLUDED_KEYS.has(key) && !EXCLUDED_PREFIXES.some(p => key.startsWith(p));
  }
  function collectEntries1142() {
    const entries = {};
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (!isBackupKey1142(key)) continue;
      const value = localStorage.getItem(key);
      if (typeof value === 'string') entries[key] = value;
    }
    return entries;
  }
  function createBackup1142() {
    return {
      schema: BACKUP_SCHEMA,
      format: BACKUP_FORMAT,
      appVersion: currentVersion1142(),
      createdAt: new Date().toISOString(),
      entries: collectEntries1142()
    };
  }
  function legacyToV2_1142(data) {
    if (!data || typeof data !== 'object' || !data.version || data.entries) return null;
    const entries = {};
    const putJson = (key, value) => { if (value !== undefined) entries[key] = JSON.stringify(value); };
    const putText = (key, value) => { if (value !== undefined && value !== null) entries[key] = String(value); };
    putJson('ebd-profile-v16', data.profile);
    putJson('ebd-notes-dark', data.notes);
    putJson('ebd-favs-dark', data.favs);
    putJson('ebd-public-dark', data.publicNotes);
    putJson('ebd-mag-favs', data.magFavs);
    putJson('ebd-mag-downloads', data.magDownloads);
    putJson('ebd-mag-progress-v15', data.magProgress);
    putText('ebd-user-mode-v15', data.userMode);
    putText('ebd-continue-mag-v15', data.continueMagazineId);
    return {
      schema: BACKUP_SCHEMA,
      format: BACKUP_FORMAT,
      appVersion: `legado-v${data.version}`,
      createdAt: data.createdAt || null,
      entries
    };
  }
  function normalizeBackup1142(data) {
    if (data && data.schema === BACKUP_SCHEMA && Number(data.format) === BACKUP_FORMAT) return data;
    const legacy = legacyToV2_1142(data);
    if (legacy) return legacy;
    throw new Error('Formato de backup não reconhecido.');
  }
  function validateBackup1142(data) {
    const normalized = normalizeBackup1142(data);
    if (!normalized.entries || typeof normalized.entries !== 'object' || Array.isArray(normalized.entries)) throw new Error('Backup sem dados locais válidos.');
    const clean = {};
    let chars = 0;
    for (const [key, value] of Object.entries(normalized.entries)) {
      if (!/^ebd-[a-z0-9._-]{1,100}$/i.test(key) || !isBackupKey1142(key)) throw new Error(`Chave não permitida: ${key}`);
      if (typeof value !== 'string') throw new Error(`Valor inválido em ${key}`);
      chars += key.length + value.length;
      if (chars > MAX_BACKUP_CHARS) throw new Error('Backup grande demais para restauração local segura.');
      const trimmed = value.trim();
      if (trimmed && (trimmed[0] === '[' || trimmed[0] === '{')) {
        try { JSON.parse(trimmed); } catch (_) { throw new Error(`JSON interno corrompido em ${key}`); }
      }
      clean[key] = value;
    }
    if (!Object.keys(clean).length) throw new Error('Backup vazio.');
    return {...normalized, entries: clean};
  }
  function formatSize1142(chars) {
    if (chars < 1024) return `${chars} B`;
    return `${(chars / 1024).toFixed(1)} KB`;
  }
  function backupSummary1142(data) {
    const keys = Object.keys(data.entries || {});
    const chars = keys.reduce((sum, key) => sum + key.length + String(data.entries[key]).length, 0);
    let created = 'data não informada';
    if (data.createdAt) {
      const dt = new Date(data.createdAt);
      if (!Number.isNaN(dt.getTime())) created = dt.toLocaleString('pt-BR');
    }
    return {count: keys.length, size: formatSize1142(chars), created, appVersion: data.appVersion || 'não informada'};
  }
  function sync1142() {
    return `<div class="pagehead"><button class="back" data-back>‹</button><div><h1>Backup & Recuperação</h1><p>Proteção completa dos dados locais do Bíblia EBD.</p></div></div>
      <section class="sync-status-v16"><div class="sync-cloud">🛡️</div><div><span class="badge-soft">MODO LOCAL SEGURO</span><h2>Seus dados continuam no aparelho</h2><p>O backup reúne automaticamente favoritos, notas, marca-textos, histórico, progresso, EBD, perfil e preferências salvas pelo aplicativo.</p></div></section>
      <section class="form-card"><h3>Gerar backup completo</h3><p class="sync-help">Gere o JSON, copie ou compartilhe e guarde em local seguro. Dados de diagnóstico e arquivos de recuperação automática não entram no backup normal.</p><button class="btn btn-purple" id="generateBackup1142">Gerar backup</button><textarea class="field backup-area-v16" id="backupText1142" placeholder="Seu backup aparecerá aqui, ou cole um backup para analisar..."></textarea><div class="row"><button class="btn btn-dark" id="copyBackup1142">Copiar</button><button class="btn btn-dark" id="shareBackup1142">Compartilhar</button><button class="btn btn-primary" id="analyzeBackup1142">Analisar para restaurar</button></div><div id="backupPreview1142"></div></section>
      <section class="panel sync-future-v16"><strong>Restauração protegida</strong><p>Antes de aplicar um backup, o app valida todas as chaves e o JSON interno. A restauração sobrescreve somente os dados presentes no backup e mantém os demais dados atuais. Um ponto automático de retorno é salvo antes da alteração.</p></section>`;
  }
  function showPreview1142(data) {
    pendingRestore = data;
    const summary = backupSummary1142(data);
    const box = document.getElementById('backupPreview1142');
    if (!box) return;
    box.innerHTML = `<div class="result"><b>✅ Backup válido</b><p><strong>${summary.count}</strong> conjuntos de dados • ${esc1142(summary.size)}<br>Origem: ${esc1142(summary.appVersion)}<br>Criado em: ${esc1142(summary.created)}</p><p>Nada será restaurado até você tocar no botão abaixo.</p><button class="btn btn-primary" id="applyBackup1142">Restaurar agora</button></div>`;
    const apply = document.getElementById('applyBackup1142');
    if (apply) apply.onclick = applyRestore1142;
  }
  function restoreEntriesTransactional1142(entries) {
    const before = {};
    const existed = {};
    Object.keys(entries).forEach(key => {
      const old = localStorage.getItem(key);
      existed[key] = old !== null;
      before[key] = old;
    });
    const snapshot = {
      schema: BACKUP_SCHEMA,
      format: BACKUP_FORMAT,
      appVersion: currentVersion1142(),
      createdAt: new Date().toISOString(),
      reason: 'automatic-before-restore',
      entries: collectEntries1142()
    };
    try {
      localStorage.setItem(AUTO_ROLLBACK_KEY, JSON.stringify(snapshot));
    } catch (_) {
      throw new Error('Sem espaço para criar o ponto automático de retorno. Libere espaço e tente novamente.');
    }
    const changed = [];
    try {
      for (const [key, value] of Object.entries(entries)) {
        localStorage.setItem(key, value);
        changed.push(key);
      }
    } catch (err) {
      changed.reverse().forEach(key => {
        try {
          if (existed[key]) localStorage.setItem(key, before[key]);
          else localStorage.removeItem(key);
        } catch (_) {}
      });
      throw new Error('A restauração foi revertida porque não foi possível gravar todos os dados.');
    }
  }
  function applyRestore1142() {
    if (!pendingRestore) return toast1142('Analise o backup antes de restaurar.');
    try {
      restoreEntriesTransactional1142(pendingRestore.entries);
      toast1142('Backup restaurado com segurança ✅');
      pendingRestore = null;
      setTimeout(() => location.reload(), 350);
    } catch (err) {
      toast1142(err.message || 'Não foi possível restaurar o backup.');
    }
  }
  function bindSync1142() {
    const generate = document.getElementById('generateBackup1142');
    if (generate) generate.onclick = () => {
      const textarea = document.getElementById('backupText1142');
      if (!textarea) return;
      const backup = createBackup1142();
      textarea.value = JSON.stringify(backup);
      pendingRestore = null;
      const preview = document.getElementById('backupPreview1142');
      if (preview) preview.innerHTML = '';
      toast1142('Backup completo gerado ✅');
    };
    const copy = document.getElementById('copyBackup1142');
    if (copy) copy.onclick = async () => {
      const textarea = document.getElementById('backupText1142');
      if (!textarea || !textarea.value.trim()) return toast1142('Gere ou cole um backup primeiro.');
      try {
        await navigator.clipboard.writeText(textarea.value);
        toast1142('Backup copiado 📋');
      } catch (_) {
        textarea.select();
        try { document.execCommand('copy'); toast1142('Backup copiado 📋'); }
        catch (_) { toast1142('Não foi possível copiar automaticamente.'); }
      }
    };
    const share = document.getElementById('shareBackup1142');
    if (share) share.onclick = () => {
      const textarea = document.getElementById('backupText1142');
      if (!textarea || !textarea.value.trim()) return toast1142('Gere ou cole um backup primeiro.');
      try {
        if (window.AndroidBridge && typeof window.AndroidBridge.shareText === 'function') {
          window.AndroidBridge.shareText(textarea.value, 'Backup Bíblia EBD');
          return;
        }
      } catch (_) {}
      toast1142('Compartilhamento nativo indisponível. Use Copiar.');
    };
    const analyze = document.getElementById('analyzeBackup1142');
    if (analyze) analyze.onclick = () => {
      const textarea = document.getElementById('backupText1142');
      if (!textarea || !textarea.value.trim()) return toast1142('Cole um backup para analisar.');
      try {
        if (textarea.value.length > MAX_BACKUP_CHARS * 1.25) throw new Error('Backup grande demais.');
        const parsed = JSON.parse(textarea.value);
        const validated = validateBackup1142(parsed);
        showPreview1142(validated);
        toast1142('Backup validado ✅');
      } catch (err) {
        pendingRestore = null;
        const preview = document.getElementById('backupPreview1142');
        if (preview) preview.innerHTML = `<div class="result"><b>⚠️ Backup não aplicado</b><p>${esc1142(err.message || 'Conteúdo inválido.')}</p></div>`;
        toast1142('Backup inválido');
      }
    };
  }

  window.render = function () {
    if (state.route === 'sync') {
      const root = app1142();
      if (root) root.innerHTML = sync1142();
      $$('.bottomnav [data-route]').forEach(b => b.classList.remove('active'));
      window.bind();
      return;
    }
    previousRender();
  };

  window.bind = function () {
    previousBind();
    if (state.route === 'sync') bindSync1142();
  };

  window.__EBD_BACKUP_1142__ = Object.freeze({
    create: createBackup1142,
    validate: validateBackup1142,
    collect: collectEntries1142
  });

  window.render();
})();
