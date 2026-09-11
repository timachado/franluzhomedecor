# Bíblia EBD — Escola Dominical

Aplicativo Android para leitura bíblica, estudo e Escola Bíblica Dominical, com funcionamento offline como prioridade.

## Aplicativo

- Pacote: `com.timachado.bibliaebd`
- minSdk: 24
- targetSdk: 36
- compileSdk: 36
- Interface: WebView Android com conteúdo empacotado localmente
- Linha pública atual: **1.14.1 Public Beta** (`versionCode 106`, aplicado pela pipeline pública)

## Conteúdo principal

- Bíblia João Ferreira de Almeida em corpus identificado pela fonte como domínio público
- 66 livros, 1.189 capítulos e 31.098 versículos
- Busca bíblica e por referência
- Favoritos, anotações, marca-texto e histórico
- Escola Bíblica Dominical
- Rotina de estudo e planos de leitura
- Dicionário bíblico, concordância, esboços e busca global
- Backup local em JSON

## Harpa Cristã

A edição pública distribui **somente o catálogo com números e títulos dos 640 hinos**.

As letras completas usadas na edição particular do desenvolvedor **não fazem parte do repositório nem dos builds públicos**. Qualquer inclusão futura de letras completas dependerá de revisão de direitos/licenças para redistribuição.

## Branches

- `build-biblia-ebd-temp`: desenvolvimento/edição privada
- `build-biblia-ebd-public`: preparação e builds públicos
- `main`: não é usada para o desenvolvimento do Bíblia EBD

## Build público

O GitHub Actions da branch pública monta a Bíblia a partir do snapshot fixado do corpus, gera apenas o catálogo público da Harpa, força o arquivo privado de letras a ficar vazio, aplica `versionCode 106 / versionName 1.14.1` no ambiente de CI e gera APK/AAB de release para testes públicos.

A assinatura utilizada nesta fase é temporária e serve para compatibilidade com as instalações de teste existentes. Antes de uma publicação definitiva na Google Play, deve ser criada uma estratégia de assinatura de produção/Play App Signing e a migração dos dados locais deve ser validada.

## Privacidade

O aplicativo trabalha localmente e a build pública não solicita a permissão Android de Internet. Favoritos, notas, progresso e preferências permanecem no dispositivo. Consulte `PRIVACY_POLICY.md` para a política de privacidade da edição pública.

## Conteúdo de terceiros

Consulte `app/src/main/assets/THIRD_PARTY_NOTICES.txt`.
