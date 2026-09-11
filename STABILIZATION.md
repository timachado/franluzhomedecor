# Bíblia EBD — caminho até a versão estável

Este arquivo acompanha somente a linha Android `build-biblia-ebd-temp`. A branch `main` não deve ser alterada pelo trabalho do Bíblia EBD.

## Meta

Chegar a uma versão estável somente depois de completar as funcionalidades planejadas e passar pelos gates de qualidade abaixo, preservando dados locais entre atualizações. Publicação em loja fica fora deste ciclo.

## 1.14.1 — Integridade e inicialização

- [x] Manter correção de rolagem/menu confirmada em aparelho.
- [x] Manter navegação Android Back controlada pela SPA.
- [x] Corrigir fallback de versão Android.
- [x] Carregar camada de estabilização antes de `app1.js`.
- [x] Isolar JSON local corrompido sem derrubar a inicialização.
- [x] Guardar diagnóstico do último erro JavaScript.
- [x] Criar variante Diagnóstico com pacote separado para testes sem tocar no app principal.
- [ ] Confirmar Home, Bíblia, EBD, Harpa, Busca, Perfil e menu no aparelho durante a regressão 1.16.x.

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

## 1.15.x — Expansão funcional antes da estável

### Assistente Bíblia EBD — IA

- [x] Criar uma tela própria de Assistente IA integrada ao visual do aplicativo.
- [x] Permitir iniciar a IA a partir de um versículo, seleção de versículos, capítulo, lição EBD ou esboço.
- [x] Explicar versículo e contexto sem substituir o texto bíblico original.
- [x] Resumir passagem ou capítulo.
- [x] Responder perguntas sobre o texto usando a Bíblia disponível no app como contexto principal.
- [x] Gerar esboço de pregação/estudo a partir de tema ou referência.
- [x] Gerar perguntas, objetivos, aplicações e roteiro de aula para EBD.
- [x] Oferecer modos Aluno e Professor com respostas adequadas ao objetivo de cada perfil.
- [x] Permitir salvar uma resposta da IA como anotação, copiar e compartilhar.
- [x] Mostrar claramente o que é texto bíblico e o que é conteúdo gerado pela IA.
- [x] Exigir ação explícita do usuário antes de enviar conteúdo para a IA.
- [x] Nunca enviar notas, favoritos, histórico ou dados pessoais automaticamente.
- [x] Manter Bíblia, Harpa, EBD, notas e demais recursos funcionando offline quando a IA estiver indisponível.
- [x] Não armazenar chave secreta de provedor de IA dentro do APK; usar backend intermediário seguro.
- [x] Tratar ausência de internet, timeout, limite do serviço e falhas do backend sem travar o aplicativo.
- [x] Conversa contínua com histórico de estudos salvo localmente.
- [x] Reconhecimento automático de referências bíblicas digitadas.
- [x] Leitura confortável das respostas da IA com A− / A+.
- [x] Central IA do Professor com duração de aula e público da classe.
- [x] IA da Turma com planejamento, engajamento, mensagem geral e revisão pós-aula.
- [x] IA da Chamada com análise somente de dados agregados, sem enviar nomes de alunos.
- [x] IA da Agenda com checklist, lembrete e planejamento de encontros sem enviar observações livres.

### Recursos adicionais já previstos

- [x] Evoluir Esboços para editar, duplicar, favoritar, pesquisar, criar manualmente e organizar por pastas.
- [x] Evoluir Atlas Bíblico com mais lugares, referências, rotas de estudo e navegação entre local e passagem.
- [x] Melhorar Dicionário Bíblico e Português e conectá-los ao fluxo de estudo.
- [x] Melhorar busca unificada e busca por linguagem natural, mantendo busca bíblica local completa.
- [x] Ampliar recursos do Professor: perguntas, dinâmica, plano de aula e material de apoio com IA.
- [x] Integrar Minha Turma, chamada e agenda à IA preservando dados pessoais.
- [x] Compartilhamento da turma e agenda pela folha nativa do Android, sem cadastro online.
- [x] Lembretes locais da próxima EBD, com opção de 1 dia ou 1 hora antes.
- [x] Leitura em voz alta usando o mecanismo de voz do Android para Bíblia, Harpa e respostas da IA.

## 1.16.x — Regressão completa dos recursos

### 1.16.0 — Central de Diagnóstico

- [x] Criar Central de Diagnóstico dentro do app, sem apagar ou substituir dados do usuário.
- [x] Verificar automaticamente contagem e leitura da Bíblia, parser de referência, Busca Inteligente, Dicionário e Atlas.
- [x] Verificar automaticamente EBD, catálogo/letras da Harpa, Esboços, Backup Seguro e integridade do armazenamento local.
- [x] Verificar presença da ponte Android para compartilhamento, voz e lembretes.
- [x] Criar teste separado da conexão da IA sem incluir código de acesso, notas ou histórico no relatório.
- [x] Criar checklist manual para os fluxos que exigem interação real no aparelho.
- [x] Permitir compartilhar relatório de diagnóstico sem conteúdo pessoal.
- [ ] Executar a Central de Diagnóstico na build completa 1.16.0 em aparelho real e corrigir qualquer falha encontrada.

### Regressão funcional em aparelho

- [ ] Bíblia: 66 livros / 1.189 capítulos / 31.098 versículos.
- [ ] Busca por texto e referências.
- [ ] Favoritos e anotações.
- [ ] Seleção múltipla, copiar e compartilhar.
- [ ] Marca-textos e histórico.
- [ ] Rotina, metas e planos de leitura.
- [ ] EBD: 13 lições, Aluno/Professor, checklist, progresso e próxima aula.
- [ ] Minha Turma, chamada e agenda.
- [ ] Harpa Cristã completa: validar 640/640 no build que inclui as letras.
- [ ] Dicionário, concordância, esboços, Atlas e Ministério & Estudo.
- [ ] Assistente IA: contexto, respostas, salvamento, Professor/EBD, Turma/Chamada/Agenda e tratamento de falhas.
- [ ] Leitura em voz alta, compartilhamento nativo e lembretes locais.
- [ ] Modo Púlpito e manter tela ligada.
- [ ] Aparência, foco, contraste e espaçamento.
- [ ] Backup/restauração e persistência após fechar/reabrir o app.

## 1.17.x — Polimento

- [ ] Remover textos, rótulos e fallbacks legados que não representam mais o app atual.
- [ ] Revisar acessibilidade e tamanhos de toque.
- [ ] Revisar telas vazias e mensagens de erro.
- [ ] Revisar desempenho da Home, busca e listas longas.
- [ ] Garantir que nenhuma atualização limpe dados locais.
- [ ] Revisar comportamento online/offline do Assistente IA.

## Release Candidate

Uma build RC só será criada quando as funcionalidades planejadas acima estiverem concluídas, todos os testes de regressão tiverem passado e não houver bug bloqueador conhecido.

## Versão estável

A versão estável final será promovida somente depois de teste real em aparelho, validação do backup/restauração, validação da IA e definição segura da assinatura usada para atualizar a instalação principal. Publicação em loja é uma decisão separada e permanece pausada.
