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
- G04A_MainNav.md

#### (b)概況
- 「MainNav.tsx」でコンポーネント名を表示するだけの骨組みだけ作成完了したところ。本プロンプトで実際の処理の実装着手する。
- 漸進的開発により、機能を少しずつ実装していく。

#### (c)後続プロンプト
- G10A_MainNav.md

## 3. 改善・機能追加
### (1)子コンポーネント(MainNav)の作成
今回作成する子コンポーネント(MainNav)はデスクトップ画面を想定した
ナビゲーションバー用コンポーネントである。

現状のプログラムファイル(MainNav.tsx)を示す。
{{file:app/components/MainNav.tsx}}

今回このコンポーネントに以下の条件に基づく実装を追加する。

### (2)今回使用する部品のインポート
クライアントコンポーネントとして生成し、以下のimport文を挿入すること。

"use client"
import { SendHorizontal } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

### (3)条件
以下の順番で階層化させる。

#### 最上位コンテナ(div)
- md未満で非表示、md以上でflex、幅100%(hidden md:flex w-full)

#### ナビゲーションコンテナ(nav)
- Gridレイアウトで３列等分グリッド(grid grid-cols-3)
- 幅100%(w-full)
- 垂直方向に中央寄せ(items-center)
- グリッド間の間隔: 4 (gap-4)

３列等分のグリッドをそれぞれＡ列、Ｂ列、Ｃ列としたとき、それぞれ
以下のような仕様とする。

#### Ａ列
- コンテナ(div): フレックス、垂直方向で中央寄せ、間隔４(flex items-center gap-4)
- ここに下記の２つのリンクコンポーネント(Link)を配置
  - (1)客室リンク
    - リンク先: "/rooms"
    - 表示文字列: 客室
  - (2)ダイニングリンク
    - リンク先: "/dining"
    - 表示文字列: ダイニング

#### Ｂ列
- コンテナ(div): テキストを中央寄せ(text-center)
- ここに文字列を配置
  - 表示文字列のサイズ: text-lg
  - 表示文字列: ホテル東京

#### Ｃ列
- コンテナ(div): フレックス、垂直方向で中央寄せ、水平方向で右寄せ、間隔４(flex items-center justify-end gap-4)
- ここにボタン(Button)を配置
  - 背景色: bg-ctm-blue-500
  - ホバー時背景色: bg-ctm-blue-600
  - 表示アイコン: <SendHorizontal>
    - 表示アイコンのクラス指定: "w-5 h-5 mr-2"
  - 表示文字列: 宿泊予約

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
- 生成するコード形式はいわゆる"rafce"形式(=ReactArrowFunctionExportComponent)で生成すること
- プレースホルダー文字列は<div>タグでのみ囲み、その他の要素は使用しないこと
- プログラム生成時のインデント幅=2とする

