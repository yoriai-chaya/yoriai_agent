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
- G05A_MobileNav.md

#### (b)概況
- 「MobileNav.tsx」でコンポーネント名を表示するだけの骨組みだけ作成完了したところ。本プロンプトで実際の処理の実装着手する。
- 漸進的開発により、機能を少しずつ実装していく。

#### (c)後続プロンプト
- G09A_MobileNav.md

## 3. 改善・機能追加
### (1)子コンポーネント(MobileNav)の作成
今回作成する子コンポーネント(MobileNav)はデスクトップ画面を想定した
ナビゲーションバー用コンポーネントである。

現状のプログラムファイル(MobileNav.tsx)を示す。
{{file:app/components/MobileNav.tsx}}

今回このコンポーネントに以下の条件に基づく実装を追加する。

### (2)今回使用する部品のインポート
クライアントコンポーネントとして生成し、以下のimport文を挿入すること。

"use client"
import { AlignJustify, House } from "lucide-react"
import Link from "next/link"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

### (3)条件
以下の順番で階層化させる。

#### 最上位コンテナ(div)
- md以上で非表示(md:hidden)

#### Sheetコンポーネント
- 以下の２つのコンポーネントを配置
- (1)SheetTrigger
  - 内部に<AlignJustify>アイコンを配置
- (2)SheetContent
  - コンポーネントが表示される画面の端(side): left

#### SheetContentコンポーネント
- コンテナ: SheetHeader
- SheetHeaderに以下の３つのコンポーネントを配置
- (1)SheetTitle
  - 表示文字列: ホテル東京
- (2)Link
  - リンク先: "/"
  - 表示アイコン: <House>アイコン
    - アイコンのサイズ: 20
- (3)<nav>要素
  - 以下の２つのリンクコンポーネント(Link)を配置
  - (a)客室リンク
    - リンク先: "/rooms"
    - 表示文字列: 客室
  - (b)ダイニングリンク
    - リンク先: "/dining"
    - 表示文字列: ダイニング

## 4. 指示事項

### (1)プログラムの修正
上記の条件に基づき、現状のプログラムファイル(MobileNav.tsx)を修正する。
プログラムの解説や補足説明は不要。プログラムだけを生成すること。

### (2)修正プログラムの保存先
生成したプログラムは以下のディレクトリに以下のファイル名で保存すること。
directory: app/components
filename: MobileNav.tsx

# Prerequisites

## 5. 前提条件
- TailwindCSSのバージョンはv4を使用
- 生成するコード形式はいわゆる"rafce"形式(=ReactArrowFunctionExportComponent)で生成すること
- プレースホルダー文字列は<div>タグでのみ囲み、その他の要素は使用しないこと
- プログラム生成時のインデント幅=2とする

