# Header
- Category: GenCode

# Body
Next.js, TailwindCSS, shadcn/ui を用いてフロントエンドのプログラムを作成します。

## アプリケーションの要求仕様

- ホテルの Web 予約システムの構築
- 各画面で利用するヘッダサブコンポーネント（ナビゲーションバー）を作成する

## 開発概況
- ヘッダサブコンポーネント(Header.tsx)はすでに作成済
- このサブコンポーネント<Header />をlayout.tsxに挿入したい

## 指示事項
以下に現行のプログラムファイル(layout.tsx)を示します。

{{file:app/layout.tsx}}

以下の条件に基づき、現行のプログラムを修正してください。

### 挿入条件
- Header.tsxは下記ディレクトリに格納されており、これをimportする
directory: app/components/
- <body>タグ内の{children}の手前に<Header />を配置すること

# Prerequisites
- 特になし

