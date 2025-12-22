import { test, expect } from "./base.spec";
import { captureEvidenceScreenshot } from "./screenshot.evidence";
import { compareWithSnapshot } from "./screenshot.snapshot";

test.describe("Home Basic Test with MainNav", () => {
  test("Check MainNav Visible", async ({ page }) => {
    const mainNav = page.getByTestId("main-nav");
    await expect(mainNav).toBeVisible();
    const mobileNav = page.getByTestId("mobile-nav");
    await expect(mobileNav).toBeHidden();
  });

  test("Check home container", async ({ page }) => {
    const homeContainer = page.getByTestId("home-container");
    await expect(homeContainer).toBeVisible();
    await expect(homeContainer).toHaveClass(/max-w-2xl/);
    await expect(homeContainer).toHaveClass(/mx-auto/);
  });

  test("Check hero image", async ({ page }) => {
    const heroImage = page.getByTestId("home-hero-image");
    await expect(heroImage).toBeAttached();
  });

  test("Check title", async ({ page }) => {
    const title = page.getByTestId("home-title");
    await expect(title).toHaveText(
      /都会の静寂に包まれて、心ほどけるひとときを/
    );
    await expect(title).toHaveClass(/text-center/);
  });

  test("Check description", async ({ page }) => {
    const description = page.getByTestId("home-description");
    await expect(description).toHaveText(/東京の中心にありながら、/);
  });

  test("Transition from home to booking/step-1", async ({ page }) => {
    const bookingButton = page
      .getByTestId("main-nav")
      .getByTestId("main-navbar-button-booking");
    await expect(bookingButton).toBeVisible();
    await bookingButton.click();
    await expect(page).toHaveURL(/\/booking\/step-1$/);
  });

  test("Check the main display item", async ({ page }) => {
    await page.goto("/booking/step-1");
    const bookingStep1Title = page.getByTestId("booking-step1-title");
    await expect(bookingStep1Title).toBeVisible();
    await expect(bookingStep1Title).toHaveText(/日付・人数を選択してください/);
  });

  test("Save screen capture", async ({ page }) => {
    await captureEvidenceScreenshot(page, "homeMainNav.png");
    await compareWithSnapshot(page, "homeMainNav.png");
  });
});
