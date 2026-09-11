# Bíblia EBD — Public Release

## Canal atual

A versão pública inicial é **1.14.1 Public Beta**, pacote `com.timachado.bibliaebd`, `versionCode 106`.

Ela é gerada somente a partir da branch `build-biblia-ebd-public` e não altera a `main` nem a branch privada `build-biblia-ebd-temp`.

## Conteúdo permitido no build público

- Bíblia João Ferreira de Almeida conforme corpus identificado pela fonte como domínio público;
- 66 livros / 1.189 capítulos / 31.098 versículos;
- recursos offline de leitura, busca e estudo;
- EBD e materiais autorais do projeto;
- rotina de estudo, planos, dicionário, concordância e esboços;
- catálogo da Harpa com números e títulos dos 640 hinos.

## Conteúdo proibido no build público

- letras privadas dos 640 hinos da Harpa;
- backups, notas, favoritos ou dados de qualquer usuário;
- chaves de produção, senhas, tokens ou credenciais de publicação.

A pipeline pública recria `harpa-lyrics-user.js` obrigatoriamente como objeto vazio e falha na validação caso isso não aconteça.

## Privacidade

A edição pública é offline-first e não solicita a permissão Android de Internet. Dados pessoais de estudo ficam armazenados localmente no aparelho. Não há analytics nem publicidade próprios nesta versão.

## Assinatura

A Public Beta usa temporariamente a assinatura de testes já compatível com as instalações privadas existentes. Isso permite testar a atualização sem apagar dados.

**Não usar essa chave como estratégia definitiva de produção.** Antes do lançamento oficial em loja, definir Play App Signing/chave de produção e testar cuidadosamente a migração de dados e de assinatura.

## Checklist antes de promover de Beta para Estável

- testar atualização por cima da versão instalada;
- confirmar rolagem da Home e do menu;
- confirmar botão Voltar Android;
- testar Bíblia, EBD, Busca, Harpa pública, Favoritos, Notas e Backup;
- validar 66 / 1.189 / 31.098;
- validar 640 títulos da Harpa e 0 letras privadas;
- testar funcionamento com modo avião;
- revisar política de privacidade e avisos de terceiros;
- criar chave/estratégia de assinatura de produção;
- gerar AAB final;
- preparar ficha da loja, classificação indicativa, segurança de dados e screenshots.
