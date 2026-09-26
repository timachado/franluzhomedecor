# FranLuz Seller App Lock 1.1.0

Companion plugin do FranLuz Seller TWA v2.1.3.

- Preserva a associação TWA do FranLuz Home Decor.
- Adiciona a associação do pacote com.franluz.seller v2.1.2.
- Atualiza /.well-known/assetlinks.json.
- Ativa uma trava de navegação somente quando o Seller abre com seller_app=1.
- Mantém a sessão do app restrita ao /seller-franluz/ e às rotas de autenticação necessárias.
- Não altera WooCommerce, PagBank ou Melhor Envio.

- A v2.1.3 inicia por `/franluz-seller-app/`, que ativa a trava antes de qualquer redirecionamento de login.
