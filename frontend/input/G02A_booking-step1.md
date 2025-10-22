# Header
Category: GenCode

# Body
Next.js, TailwindCSS, shadcn/uiを用いてフロントエンドのWebアプリケーションプログラムを作成します。

## アプリケーションの要求仕様

- ホテルのWeb予約システムの構築
- 宿泊予約画面の構築を行う
- 下記の「useState Hook」に記載の状態変数をセットする
- 下記の「各要素の概要」に記載の画面要素を配置する

## useState Hook
- 以下の３つの状態変数をセットする
- (1)checkInDate
    - 型: Date | undefined
    - 初期値: undefined
- (2)checkOutDate
    - 型: Date | undefined
    - 初期値: undefined
- (3)guestCount
    - 型: number
    - 初期値: 2

## 使用するShadcn/uiコンポーネント
- 今回作成する画面では以下の４つのshadcn/uiコンポーネントを利用する
- card, select, button, date-picker
- importは「from "@/components/ui/xxx"」(xxx: コンポーネント名)を用いる

## 使用するアイコン
- <SendHorizontal>を利用する。import元は"lucide-react"とする

## 宿泊予約画面のレイアウト
(a)下記に示す各要素を収納するコンテナを作成する
(b)コンテナのクラスとして以下を指定する
    - フレックスボックスで列方向
    - アイテム配置: 中央寄せ
    - パディング: 縦方向: 2
(c)さらに子コンテナを作成し以下を指定する
    - コンテナの幅: 100% (w-full)
    - 横幅の最大値: md

## 各要素の概要

要素01: カード(Card)。宿泊予約に必要な入力項目を扱う要素02以降のコンポーネントをこのカード上に配置する。
要素02: チェックイン日入力コンポーネント
要素03: チェックアウト日入力コンポーネント
要素04: 人数入力コンポーネント
要素05: 「空室検索」ボタンコンポーネント

詳細は下記の「各要素の詳細」を参照のこと。

## 各要素の詳細

### 要素01: カード
- 背景色: gray-100
- 文字色: gray-700
- カードヘッダ(CardHeader)のタイトル(CardTitle): 日付・人数を選択してください
- カード内コンテナ(CardContent): ２列のグリッド構成、gap-4

### 要素02: チェックイン日入力コンポーネント
- コンテナ: フレックスボックスで列方向、中央寄せ
- このコンテナに下記の２つのコンポーネントを配置する
- (1)タイトル
    - タイトル名: チェックイン
    - テストID: checkin-title
- (2)DatePicker
    - 以下の３つのプロパティをセットする
    - date={checkInDate} : useState Hook 状態変数
    - setDate={setCheckInDate} : useState Hook 状態変数
    - name="check-in"

### 要素03: チェックアウト日入力コンポーネント
- コンテナ: フレックスボックスで列方向、中央寄せ
- このコンテナに下記の２つのコンポーネントを配置する
- (1)タイトル
    - タイトル名: チェックアウト
    - テストID: checkout-title
- (2)DatePicker
    - 以下の３つのプロパティをセットする
    - date={checkOutDate} : useState Hook 状態変数
    - setDate={setCheckOutDate} : useState Hook 状態変数
    - name="check-out"

### 要素04: 人数入力コンポーネント
- コンテナ: フレックスボックスで列方向、中央寄せ
- このコンテナに下記の２つのコンポーネントを横並びで配置する
- (1)タイトル
    - タイトル名: 人数
    - マージン: mx-5
    - テキストの折返しをしない(text-nowrap)
- (2)Select
    - guestCountの初期値(=下記のvalue値)に相当する項目名を表示させる
    - 以下の<SelectTrigger>, <SelectValue>, <SelectContent>の３つのサブコンポーネントを配置する。それぞれのサブコンポーネントのクラス設定やプロパティ設定は以下の通りである。
    - (a)SelectTrigger
        - Ring Width: ring-0, focus-visible:ring-0
        - Border-width: border-0
        - Box-shadow: shadow-none
        - テストID: guest-select-trigger
    - (b)SelectValue
        - 現在選択した値あるいは初期値を表示させるために配置する
    - (c)SelectContent
        - ４つの項目<SelectItem>を配置する。詳細は下記の通り。
        - 項目名: 1人, 2人, 3人, 4人
        - value: 1, 2, 3, 4
        - テストID: guest-option-x (x: 1, 2, 3, 4)

### 要素05: 「空室検索」ボタンコンポーネント
- コンテナ: flex
    - grid-column: col-span-2
    - justify-content: justify-center
- このコンテナに下記のコンポーネントを配置する
- Button
    - 背景色: bg-ctm-blue-500
    - hover背景色: bg-ctm-blue-600
    - 幅: デフォルト: w-full, md:w-auto
    - アイコン: <SendHorizontal>
        - アイコン幅: w-5
        - アイコン高さ: h-5
        - マージン: mr-2
    - ボタンタイトル: 空室検索
    - テストID: room-search


## 指示事項

### 指示1
上記の条件に基づき、宿泊予約画面のTypeScriptプログラムを作成する。
プログラムの解説や補足説明は不要。プログラムだけを生成すること。

### 指示2
生成したプログラムは以下のディレクトリに以下のファイル名で保存すること。
directory: app/booking/step-1
filename: page.tsx

# Prerequisites
- TailwindCSSのバージョンはv4を使用
- 最終的にコンポーネントファイル(page.tsx)にそのままコピーペーストできる状態のコードを生成すること。
- 生成するコードの形式はいわゆる"rafce"形式(=ReactArrowFunctionExportComponent)で作成すること
- 関数名は「BookingStep1」とし、その型(React.FC)は明示しないこと
- 各要素にはテスト自動化のためのテストID「data-testid」を付与し、「各要素の詳細」で指定したテストIDの値を付与すること
- ReactのuseStateフックを使うコンポーネントでは、先頭に"use client"を記述すること
- JSX部分の記述のタブは２文字としてコード生成すること
- 各コンポーネントのタイトルは特に指示がある場合を除き<p>タグとする
- <Select>コンポーネントのテストIDの付与は、ラッパーである<Select>に付与するのではなく、クリック可能なトリガーである<SelectTrigger>に付与すること

