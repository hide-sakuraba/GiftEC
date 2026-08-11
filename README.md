# GiftEC

厳選ギフトを探して購入できる、Django製の小規模ECサイトです。商品の検索・カテゴリ絞り込み・カート・会員登録・Stripe Checkoutによる決済を、一連の購入体験として実装しています。

## 主な機能

- 商品一覧、キーワード検索、カテゴリ絞り込み、価格順／新着順の並び替え
- 商品詳細、在庫表示、関連商品のレコメンド
- セッションベースのショッピングカートと消費税計算
- 会員登録・ログイン
- Stripe Checkout決済とWebhookによる支払い確定
- 支払い成功時のみの在庫減算、注文ステータス更新
- 注文者本人または注文時セッションに限定した注文詳細表示
- 管理画面からの商品・カテゴリ・注文管理

## 技術構成

- Backend: Python / Django
- Database: PostgreSQL（ローカルではSQLiteでも起動可能）
- Payment: Stripe Checkout / Stripe Webhook
- Image handling: Pillow
- Dependency management: uv
- Container: Docker Compose

## ローカル起動

```bash
uv sync
copy .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

`http://127.0.0.1:8000/` を開いてください。商品データはDjango管理画面から登録できます。

## Dockerでのローカル起動

PostgreSQLを含めて起動する場合は、`.env` に `USE_SQLITE=False`、`DB_SSLMODE=disable` を設定します。

```bash
docker compose up --build
```

Webアプリは `http://localhost:8000/`、PostgreSQLはホストの `5433` ポートで利用できます。Webコンテナ起動時にマイグレーションも自動実行されます。

## Render + Neonへのデプロイ

このリポジトリにはRender Blueprintとして `render.yaml` を含めています。GitHubへpushした後、Render Dashboardから **New + > Blueprint** を選び、このリポジトリを指定してください。RenderはDockerfileをビルドして、コンテナ内でマイグレーション後にGunicornを起動します。

1. Neonでプロジェクトを作成し、接続文字列を取得する。
2. Renderの環境変数 `DATABASE_URL` にNeonの接続文字列を設定する。
3. Renderが作成した `https://<service>.onrender.com` をStripeのWebhook URLとして登録する。
   `https://<service>.onrender.com/orders/stripe/webhook/`
4. Renderの環境変数に `STRIPE_PUBLIC_KEY`、`STRIPE_SECRET_KEY`、`STRIPE_WEBHOOK_SECRET` を設定する。
5. Stripe Dashboardからテスト決済を行い、Render LogsでWebhook受信と注文の `Paid` 更新を確認する。

`SECRET_KEY`、`DEBUG=False`、`USE_SQLITE=False`、`DB_SSLMODE=require` は `render.yaml` で設定されます。Renderの公開ホスト名は自動的にDjangoの `ALLOWED_HOSTS` と `CSRF_TRUSTED_ORIGINS` に追加されます。

> Render無料Webサービスは15分無アクセスで停止し、ローカルファイルは永続化されません。そのため、`media/` にアップロードした商品画像を本番で保持するには、CloudinaryやS3互換ストレージなどの外部オブジェクトストレージを別途設定してください。

## Stripe Webhook（ローカル開発）

Stripe CLIで以下のコマンドを実行し、表示された署名シークレットを `.env` の `STRIPE_WEBHOOK_SECRET` に設定します。

```bash
stripe listen --forward-to localhost:8000/orders/stripe/webhook/
```

注文はWebhookで `checkout.session.completed` を受信した時点で `Paid` に更新され、在庫を確定します。

## 環境変数

`.env.example` を参考に、少なくとも以下を設定してください。

- `SECRET_KEY`
- `DEBUG=False`（本番環境）
- `ALLOWED_HOSTS`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_WEBHOOK_SECRET`

## 設計上のポイント

- 日本円はゼロ小数点通貨のため、Stripeへは価格を100倍せずに送信します。
- 注文番号をStripe Checkout Sessionのmetadataに保存し、WebhookのセッションIDと照合して注文を更新します。
- 決済成功前にカートを消去・在庫を減算しないことで、決済中断による在庫不整合を防ぎます。
- 画面はモバイルでの購入導線も考慮し、カートをカード型に切り替えます。
