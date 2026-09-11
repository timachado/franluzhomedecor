# Bíblia EBD — caminho até a versão estável

Este arquivo acompanha somente a linha Android `build-biblia-ebd-temp`. A branch `main` não deve ser alterada pelo trabalho do Bíblia EBD.

## Meta

Chegar a uma versão estável somente depois de passar pelos gates abaixo, preservando dados locais entre atualizações.

## 1.14.1 — Integridade e inicialização

- [x] Manter correção de rolagem/menu confirmada em aparelho.
- [x] Manter navegação Android Back controlada pela SPA.
- [x] Corrigir fallback de versão Android.
- [x] Carregar camada de estabilização antes de `app1.js`.
- [x] Isolar JSON local corrompido sem derrubar a inicialização.
- [x] Guardar diagnóstico do último erro JavaScript.
- [ ] Testar atualização por cima da versão já instalada, sem desinstalar.
- [ ] Confirmar Home, Bíblia, EBD, Harpa, Busca, Perfil e menu no aparelho.

## 1.14.2 — Backup e recuperação

- [ ] Validar exportação JSON com favoritos, notas, marca-textos, histórico, progresso e configurações.
- [ ] Validar restauração em instalação de teste.
- [ ] Impedir que backup inválido sobrescreva dados bons.
- [ ] Exibir resumo do que será restaurado antes de aplicar.
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

A versão estável final será promovida somente depois de teste real em aparelho, atualização por cima da linha anterior e validação do backup/restauração. Publicação em loja é uma decisão separada e não faz parte deste ciclo de estabilização.
