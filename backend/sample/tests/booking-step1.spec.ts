import { test, expect } from "./base.spec";
import { saveOrCompareScreenshot } from "./screenshot";
test.use({ baseURL: "/booking/step-1" });

test.describe("Booking step-1 Basic Test", () => {

    test("Check check-in date operation", async({ page }) => {
        const checkinTitle = page.getByTestId("checkin-title");
        await expect(checkinTitle).toHaveText(/チェックイン/);
        const checkInInput = page.getByLabel("check-in");
        await checkInInput.click();
        const checkInCalendar = page.getByTestId("check-in-calendar");
        await expect(checkInCalendar).toBeVisible();
        const CHECKIN_DAY = 12;
        const checkInButton = checkInCalendar.locator("table button", { hasText: String(CHECKIN_DAY) });
        await checkInButton.click();
        await page.waitForTimeout(1000);
    });

    test("Check check-out date operation", async({ page }) => {
        const checkoutTitle = page.getByTestId("checkout-title");
        await expect(checkoutTitle).toHaveText(/チェックアウト/);
        const checkOutInput = page.getByLabel("check-out");
        await checkOutInput.click();
        const checkOutCalendar = page.getByTestId("check-out-calendar");
        await expect(checkOutCalendar).toBeVisible();
        const CHECKOUT_DAY = 14;
        const checkOutButton = checkOutCalendar.locator("table button", { hasText: String(CHECKOUT_DAY) });
        await checkOutButton.click();
        await page.waitForTimeout(1000);
    });

    test("Check select number of guests", async({ page }) => {
        const guestSelectTrigger = page.getByTestId("guest-select-trigger");
        await expect(guestSelectTrigger).toHaveText(/2人/);
        await guestSelectTrigger.click();
        const guestOption3 = page.getByTestId("guest-option-3");
        await expect(guestOption3).toBeVisible();
        await guestOption3.click();
        await expect(guestSelectTrigger).toHaveText(/3人/);
        await page.waitForTimeout(1000);
    });

    test("Check search operation", async({ page }) => {
        const roomSearchButton = page.getByTestId("room-search");
        await roomSearchButton.click();
        await page.waitForTimeout(1000);
    });

    test("Save screen capture", async ({ page }) => {
        await saveOrCompareScreenshot(page, "booking-step1.png");
    });
});