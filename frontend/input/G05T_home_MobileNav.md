# Header
Category: GenCode

# Body
Playwright用のフロントエンドアプリケーションのテストプログラムを作成します。

## テストプログラムの要求仕様

- テスト対象アプリケーション概要: Next.js, TypeScript, TailwindCSS, shadcn/uiにて作成したホーム画面
- 作成するテストプログラムファイル: tests/home_main.spec.ts

## テスト対象アプリケーションファイル
{{file:app/page.tsx}}

## テスト対象URL
- "/"

## テストケース
テストケースとして以下の６ケースを作成する。

### テストグループ
- テストグループ名: "Home Basic Test with MobileNav"

### テストケース1
- テストケース名: "Check MobileNav Visible"
- MobileNavコンポーネント: TestId="mobile-nav"でロケータを取得
- MobileNavコンポーネントが存在・表示されていること(toBeVisible)
- MainNavコンポーネント: TestId="main-nav"でロケータを取得
- MainNavコンポーネントが非表示であること(toBeHidden)

### テストケース2
- テストケース名: "Check home container"
- TestId="home-container"でロケータを取得
- コンテナクラスが存在・表示されていること(toBeVisible)
- "max-w-2xl"クラスが指定されていること(toHaveClass)
- "mx-auto"クラスが指定されていること(toHaveClass)

### テストケース3
- テストケース名: "Check hero image"
- TestId="home-hero-image"でロケータを取得
- imgタグにアタッチできること(toBeAttached)

### テストケース4
- テストケース名: "Check title"
- TestId="home-title"でロケータを取得
- 以下のテキストが存在すること

都会の静寂に包まれて、心ほどけるひとときを

- "text-center"クラスが指定されていること(toHaveClass)

### テストケース5
- テストケース名: "Check description"
- TestId="home-description"でロケータを取得
- 以下のテキストで始まるテキストが存在すること(toHaveText)

東京の中心にありながら、

### テストケース6
- テストケース名: "Save screen capture"
- 表示画面のスクリーンショットを取得する
- ファイル名: homeMobileNav.png


## 指示事項
生成したプログラムは以下のディレクトリに以下のファイル名で保存すること。
directory: tests
filename: home_mobile.spec.ts

# Prerequisites

## テスト共通事項
- 上記の条件に基づき、ホーム画面のPlaywright用テストプログラムを作成する。プログラムの解説や補足説明は不要。プログラムだけを生成すること。

- テストコードの先頭に以下の行を記述すること。

import { test, expect } from "./base.spec";
import { saveOrCompareScreenshot } from "./screenshot";
test.use({ baseURL: (テスト対象URL) });

- テストグループ名をtest.describe()にて指定すること。

- テストケース記述は下記の雛形を元に作成すること。

test("テストケース名", async({ page }) => {
    //各々の確認事項のコードを生成する
}

- Playwrightのテスト実行時のコマンドライン

$ npx playwright test (テストプログラムファイル名)

- ロケーターはTestIdをキーとして取得する(getByTestId)

- 各々のテストケースに「await page.goto("/")を記述する必要はない。なぜなら先頭行でimportしている「base.spec.ts」の中でgoto()しているからである。

- スクリーンショットの取得

スクリーンショット取得のテストケースがある場合は、以下のコードを
加えること。

  test("Save screen capture", async ({ page }) => {
    await saveOrCompareScreenshot(page, (指定したファイル名));
  });

- クラスの指定確認（toHaveClass）を用いる場合は引数の指定は文字列("xxx")ではなく、正規表現(/xxx/)でコード生成すること。

- 文字列の部分一致の確認は正規表現を用いて記述すること。

（例）
  await expect(locator).toHaveText(/xxx/);

## テスト個別事項
- 特になし

