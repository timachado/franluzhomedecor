# Bíblia EBD Android

Aplicativo Android da Bíblia EBD / Escola Bíblica Dominical.

- Pacote: `com.timachado.bibliaebd`
- Versão: `1.0.0`
- minSdk: 24
- targetSdk / compileSdk: 36
- Interface empacotada localmente no APK, portanto a tela inicial funciona sem internet.

## Build local
Use JDK 17, Android SDK 36, Build Tools 35.0.0 e Gradle 8.13.

```bash
gradle assembleDebug
```

APK: `app/build/outputs/apk/debug/app-debug.apk`

## Google Play
Para publicação, gere um Android App Bundle (`bundleRelease`) e configure uma chave de upload mantida em local seguro / Play App Signing. Nunca versionar a chave de produção no repositório.
