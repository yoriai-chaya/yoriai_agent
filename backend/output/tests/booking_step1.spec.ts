import { test, expect } from "./base.spec";

test.use({ baseURL: "/booking/step-1" });

test.describe("Booking step-1 Basic Test", () => {
  test("Check check-in date operation", async ({ page }) => {
    const checkInTitle = page.getByTestId("checkin-title");
    await expect(checkInTitle).toHaveText("チェックイン");

    const checkInPicker = page.getByLabel("check-in");
    await checkInPicker.click();
    await page.waitForTimeout(1000);

    const checkInCalendar = page.getByTestId("check-in-calendar");
    await expect(checkInCalendar).toBeVisible();

    const CHECKIN_DAY = 12;
    const checkInDayButton = checkInCalendar.locator("table button", {
      hasText: String(CHECKIN_DAY),
    });
    await checkInDayButton.click();
    await page.waitForTimeout(1000);
  });

  test("Check check-out date operation", async ({ page }) => {
    const checkOutTitle = page.getByTestId("checkout-title");
    await expect(checkOutTitle).toHaveText("チェックアウト");

    const checkOutPicker = page.getByLabel("check-out");
    await checkOutPicker.click();
    await page.waitForTimeout(1000);

    const checkOutCalendar = page.getByTestId("check-out-calendar");
    await expect(checkOutCalendar).toBeVisible();

    const CHECKOUT_DAY = 14;
    const checkOutDayButton = checkOutCalendar.locator("table button", {
      hasText: String(CHECKOUT_DAY),
    });
    await checkOutDayButton.click();
    await page.waitForTimeout(1000);
  });

  test("Check select number of guests", async ({ page }) => {
    const selectTrigger = page.getByTestId("guest-select-trigger");
    await expect(selectTrigger).toHaveText("2人");
    await selectTrigger.click();
    const option3 = page.getByTestId("guest-option-3");
    await option3.click();
    await page.waitForTimeout(1000);
  });

  test("Check search operation", async ({ page }) => {
    const searchButton = page.getByRole("button", { name: "空室検索" });
    await searchButton.click();
    await page.waitForTimeout(1000);
  });

  test("Save screen capture", async ({ page }) => {
    await expect(page).toHaveScreenshot("booking_step1.png", {
      maxDiffPixelRatio: 0.02,
    });
  });
});
