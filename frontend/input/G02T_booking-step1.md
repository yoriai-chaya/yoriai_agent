# Header
Category: GenCode

# Body
Playwright用のフロントエンドアプリケーションのテストプログラムを作成します。

## テストプログラムの要求仕様

- テスト対象アプリケーション概要: Next.js, TypeScript, TailwindCSS, shadcn/uiにて作成したホーム画面
- 作成するテストプログラムファイル: tests/booking-step1.spec.ts

## テスト対象アプリケーションファイル
{{file:app/booking/step-1/page.tsx}}

## テスト対象URL
- "/booking/step-1"

## テストケース
テストケースとして以下の５ケースを作成する。

### テストグループ
- テストグループ名: "Booking step-1 Basic Test"

### テストケース1
- テストケース名: "Check check-in date operation"
- TestId="checkin-title"でロケータを取得し、テキストが「チェックイン」であることを確認する
- getByLabel("check-in")でロケータを取得し、クリックできることを確認する
- TestId="check-in-calendar"でロケータ取得し、カレンダ要素が表示されていること(toBeVisible)であることを確認する
- 後述の「カレンダボタン日付確認方法」に基づき、「日付」=「12」ボタンが押下できることを確認する

### テストケース2
- テストケース名: "Check check-out date operation"
- TestId="checkout-title"でロケータを取得し、テキストが「チェックアウト」であることを確認する
- getByLabel("check-out")でロケータを取得し、クリックできることを確認する
- TestId="check-out-calendar"でロケータ取得し、カレンダ要素が表示されていること(toBeVisible)であることを確認する
- 後述の「カレンダボタン日付確認方法」に基づき、「日付」=「14」ボタンが押下できることを確認する

### テストケース3
- テストケース名: "Check select number of guests"
- TestId="guest-select-trigger"でロケータを取得し、テキストが「2人」であること、及びクリック操作できることを確認する
- クリック後にTestId="guest-option-3"でロケータ取得し、クリック操作ができることを確認し、クリック後に表示テキストが「3人」であることを確認する

### テストケース4
- テストケース名: "Check search operation"
- TestId="room-search"でロケータを取得し、クリック操作できることを確認する

### テストケース5
- テストケース名: "Save screen capture"
- 表示画面のスクリーンショットを取得する
- ファイル名: booking-step1.png


## 指示事項

### 指示1
生成したプログラムは以下のディレクトリに以下のファイル名で保存すること。

directory: tests
filename: booking-step1.spec.ts

# Prerequisites

## テスト共通事項
- 上記の条件に基づき、予約画面のPlaywright用テストプログラムを作成する。プログラムの解説や補足説明は不要。プログラムだけを生成すること。

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

- ロケータはTestIdをキーとして取得する(getByTestId)

- 各々のテストケースに「await page.goto("/");」を記述する必要はない。なぜなら先頭行でimportしている「base.spec.ts」の中でgoto()しているからである。

- スクリーンショットの取得

スクリーンショット取得のテストケースがある場合は、以下のコードを
加えること。

  test("Save screen capture", async ({ page }) => {
    await saveOrCompareScreenshot(page, (指定したファイル名));
  });

- クラスの指定確認（toHaveClass）を用いる場合は引数の指定は文字列("xxx")ではなく、正規表現(/xxx/)でコード生成すること。

## テスト個別事項
- <Select>や<Button>の表示確認および操作性確認は下記のコードテンプレートをベースとしてコード記述すること

await expect(locator).toBeVisible();
await locator.click();

- 各々のテストケースの結果をしっかりと目視確認したいので、各々のテストケースの最後に下記のコードを記述すること

await page.waitForTimeout(1000);

- カレンダボタン日付確認方法

カレンダボタンの日付確認は下記のコード断片を元に作成する。

const XXX_DAY = (具体的な日付を表す数値);
const xxxButton = calendarLocator.locator("table button", {
  hasText: String(XXX_DAY),
});
await xxxButton.click();

