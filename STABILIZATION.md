# Bíblia EBD — caminho até a versão estável

Este arquivo acompanha somente a linha Android `build-biblia-ebd-temp`. A branch `main` não deve ser alterada pelo trabalho do Bíblia EBD.

## Meta

Chegar a uma versão estável somente depois de passar pelos gates abaixo, preservando dados locais entre atualizações. Publicação em loja fica fora deste ciclo.

## 1.14.1 — Integridade e inicialização

- [x] Manter correção de rolagem/menu confirmada em aparelho.
- [x] Manter navegação Android Back controlada pela SPA.
- [x] Corrigir fallback de versão Android.
- [x] Carregar camada de estabilização antes de `app1.js`.
- [x] Isolar JSON local corrompido sem derrubar a inicialização.
- [x] Guardar diagnóstico do último erro JavaScript.
- [x] Criar variante Diagnóstico com pacote separado para testes sem tocar no app principal.
- [ ] Confirmar Home, Bíblia, EBD, Harpa, Busca, Perfil e menu no aparelho.

## 1.14.2 — Backup e recuperação

- [x] Gerar backup completo das chaves locais `ebd-*`, cobrindo favoritos, notas, marca-textos, histórico, progresso, EBD, perfil e configurações.
- [x] Manter compatibilidade de leitura com o formato de backup anterior.
- [x] Validar estrutura, chaves, tipos, JSON interno e tamanho antes de restaurar.
- [x] Impedir que backup inválido seja aplicado.
- [x] Exibir resumo do backup antes de qualquer restauração.
- [x] Restaurar apenas as chaves presentes no backup, sem apagar dados atuais ausentes nele.
- [x] Criar ponto automático de retorno antes da restauração.
- [x] Reverter alterações se uma gravação falhar no meio da restauração.
- [ ] Validar geração, análise e restauração em aparelho usando a variante Diagnóstico.
- [ ] Validar persistência após fechar e reabrir o aplicativo.

## 1.14.3 — Regressão dos recursos

- [ ] Bíblia: 66 livros / 1.189 capítulos / 31.098 versículos.
- [ ] Busca por texto e referências.
- [ ] Favoritos e anotações.
- [ ] Seleção múltipla, copiar e compartilhar.
- [ ] Marca-textos e histórico.
- [ ] Rotina, metas e planos de leitura.
- [ ] EBD: 13 lições, Aluno/Professor, checklist, progresso e próxima aula.
- [ ] Minha Turma, chamada e agenda.
- [ ] Harpa privada: validar 640/640 somente no build privado.
- [ ] Dicionário, concordância, esboços e Ministério & Estudo.
- [ ] Modo Púlpito e manter tela ligada.
- [ ] Aparência, foco, contraste e espaçamento.

## 1.15.x — Polimento

- [ ] Remover textos, rótulos e fallbacks legados que não representam mais o app atual.
- [ ] Revisar acessibilidade e tamanhos de toque.
- [ ] Revisar telas vazias e mensagens de erro.
- [ ] Revisar desempenho da Home, busca e listas longas.
- [ ] Garantir que nenhuma atualização limpe dados locais.

## Release Candidate

Uma build RC só será criada quando todos os testes de regressão acima estiverem concluídos e não houver bug bloqueador conhecido.

## Versão estável

A versão estável final será promovida somente depois de teste real em aparelho, validação do backup/restauração e definição segura da assinatura usada para atualizar a instalação principal. Publicação em loja é uma decisão separada e permanece pausada.
