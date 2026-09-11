// Bíblia EBD 1.14.1 — camada de estabilização carregada antes do app.
(function () {
  'use strict';

  const VERSION = '1.14.1';
  const RECOVERY_PREFIX = 'ebd-recovery-v1141-';
  const DIAG_KEY = 'ebd-last-error-v1141';
  const recovered = [];

  function safeSet(key, value) {
    try {
      localStorage.setItem(key, value);
      return true;
    } catch (_) {
      return false;
    }
  }

  function isolateCorruptedJson(key, raw) {
    const stamp = Date.now();
    const recoveryKey = `${RECOVERY_PREFIX}${stamp}-${key}`;
    if (safeSet(recoveryKey, raw)) {
      try { localStorage.removeItem(key); } catch (_) {}
      recovered.push({ key, recoveryKey });
      console.warn(`[Bíblia EBD ${VERSION}] Dado local corrompido isolado: ${key}`);
    }
  }

  try {
    const keys = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (key) keys.push(key);
    }

    keys.forEach((key) => {
      if (!key.startsWith('ebd-') || key.startsWith(RECOVERY_PREFIX) || key === DIAG_KEY) return;
      const raw = localStorage.getItem(key);
      if (typeof raw !== 'string') return;
      const trimmed = raw.trim();
      if (!trimmed || (trimmed[0] !== '[' && trimmed[0] !== '{')) return;
      try {
        JSON.parse(trimmed);
      } catch (_) {
        isolateCorruptedJson(key, raw);
      }
    });
  } catch (err) {
    console.warn(`[Bíblia EBD ${VERSION}] Pré-validação de dados locais não pôde ser concluída.`, err);
  }

  function rememberRuntimeError(kind, message, source, line, column) {
    const payload = {
      version: VERSION,
      at: new Date().toISOString(),
      kind,
      message: String(message || 'Erro desconhecido').slice(0, 800),
      source: String(source || '').slice(0, 300),
      line: Number(line || 0),
      column: Number(column || 0)
    };
    safeSet(DIAG_KEY, JSON.stringify(payload));
  }

  window.addEventListener('error', (event) => {
    rememberRuntimeError('error', event.message, event.filename, event.lineno, event.colno);
  });

  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason && (event.reason.stack || event.reason.message || event.reason);
    rememberRuntimeError('unhandledrejection', reason || 'Promise rejeitada sem tratamento', '', 0, 0);
  });

  window.__ebdSafeJson1141 = function (raw, fallback) {
    try {
      return JSON.parse(raw);
    } catch (_) {
      return fallback;
    }
  };

  window.__EBD_STABILITY_1141__ = Object.freeze({
    version: VERSION,
    recoveredCount: recovered.length,
    recovered
  });
})();
