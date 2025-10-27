# Header
- Category: GenCode

# Body
Next.js, TailwindCSS, shadcn/ui を用いてフロントエンドの
アプリケーションプログラムを作成します。

## 1. 背景・ゴール
### (1) 目的・概要
- ホテルのWeb予約システムを構築する

### (2) アプリケーション概要
- Next.js, TypeScript, TailwindCSS, Shadcn/uiを用いたフロントエンドアプリケーション
- ホテルの予約に必要な情報を画面上から取り込み、その内容をバックエンドAPIサーバに送信し、バックエンドからの受信データを画面に表示する
- レスポンシブデザインを採用し、画面サイズに応じてデスクトップ版、モバイル版のコンポーネントを用意する

### (3) 直近のゴール
- ホテルのHome画面(A)と宿泊予約(STEP-1)画面(B)の２つの画面を作成する
- Home画面から宿泊予約画面への画面遷移（戻ることも含む）ができることを確認する

## 2. 現状
### (1) アプリケーションの構成
- 基本的にはNext.jsのApp Router構成に従う。
- 現時点でのディレクトリ構成を示す。
    📁 ディレクトリ構成
    project-root/
    ├── app/
    │   ├── app.css : カスタムCSSの定義
    │   ├── globals.css : 標準CSS（先頭行にカスタムCSSファイルをimport）
    │   ├── layout.tsx : 全ページ共通レイアウト定義
    │   ├── page.tsx : Home画面(A)
    │   ├── booking
    │   │   ├── step-1
    │   │   │   └── page.tsx : (B)宿泊予約(STEP-1)画面
    │   │   └── (step-2)  * 次フェーズ以降で開発予定
    │   └── components
    │       ├── Header.tsx : ナビゲーションバー(layout.tsxにて取り込む)
    │       ├── MainNav.tsx : デスクトップ版ナビゲーションバー
    │       └── MobileNav.tsx : モバイル版ナビゲーションバー
    └── components/ui : Shadcn/uiコンポーネント格納ディレクトリ

### (2) 現時点の実装状況
#### (a)前提プロンプト
- G07A_MainNav.md

#### (b)概況
- 「MainNav.tsx」でナビゲーションの基本的な部分を作成したところ。
- 漸進的開発により、機能を少しずつ実装していく。

#### (c)後続プロンプト
- 未定

## 3. 改善・機能追加
### (1)子コンポーネント(MainNav)の作成
今回作成する子コンポーネント(MainNav)はデスクトップ画面を想定した
ナビゲーションバー用コンポーネントである。

現状のプログラムファイル(MainNav.tsx)を示す。
{{file:app/components/MainNav.tsx}}

今回このコンポーネントに以下の条件に基づく実装を修正・追加する。

### (2)追加する実装機能一覧
1. Home画面に限りナビゲーションバー上の「宿泊予約」ボタンを表示するように修正する。
2. 「宿泊予約」ボタン押下時に画面遷移するロジックを追加する。
3. テストIDの追加

### (3)Reactフックの追加
上記(1)(2)を実装するために、「useRouter」「userPathname」の２つをReactフックとして追加する。

import { useRouter, usePathname } from "next/navigation"

### (4)「宿泊予約」ボタン表示条件
- usePathname()で得られるパスが"/"であるときに限り、「宿泊予約」ボタンを表示させるよう修正する。

### (5)「宿泊予約」ボタン押下時の画面遷移の実装
- useRouter()で得られるルータを用いて、コールバック関数handleSearch()の中で以下に指定するパスに遷移するロジックを追加する。
  - 遷移先のパス: /booking/step-1

### (6)テストIDの追加
- (a)以下の２つのリンク要素にそれぞれ下記のテストIDを付与する
  - "/rooms"リンク: main-navbar-link-rooms
  - "/dining"リンク: main-navbar-link-dining

- (b)「ホテル東京」の文字列表示要素に下記のテストIDを付与する
  - テストID: main-navbar-title

- (c)「宿泊予約」ボタンに対してテストIDを付与する
  - テストID: main-navbar-button-booking

## 4. 指示事項

### (1)プログラムの修正
上記の条件に基づき、現状のプログラムファイル(MainNav.tsx)を修正する。
プログラムの解説や補足説明は不要。プログラムだけを生成すること。

### (2)修正プログラムの保存先
生成したプログラムは以下のディレクトリに以下のファイル名で保存すること。
directory: app/components
filename: MainNav.tsx

# Prerequisites

## 5. 前提条件
- TailwindCSSのバージョンはv4を使用
- 最終的にメインページ(page.tsx)コンポーネントファイルにそのままコピーペーストできる状態のコードを生成すること
- 生成するコード形式はいわゆる"rafce"形式(=ReactArrowFunctionExportComponent)で生成すること
- プレースホルダー文字列は<div>タグでのみ囲み、その他の要素は使用しないこと
- プログラム生成時のインデント幅=2とする

