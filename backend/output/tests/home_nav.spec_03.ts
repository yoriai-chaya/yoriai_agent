import { Page } from "@playwright/test";
import { test, expect } from "./base.spec";
import { captureEvidenceScreenshot } from "./screenshot.evidence";
import { compareWithSnapshot } from "./screenshot.snapshot";

async function checkHomeBasicContents(page: Page) {
  const homeContainer = page.getByTestId("home-container");
  await expect(homeContainer).toBeVisible();
  await expect(homeContainer).toHaveClass(/max-w-2xl/);
  await expect(homeContainer).toHaveClass(/mx-auto/);

  const heroImage = page.getByTestId("home-hero-image");
  await expect(heroImage).toBeAttached();

  const title = page.getByTestId("home-title");
  await expect(title).toHaveText(/都会の静寂に包まれて、心ほどけるひとときを/);
  await expect(title).toHaveClass(/text-center/);

  const description = page.getByTestId("home-description");
  await expect(description).toHaveText(/東京の中心にありながら、/);
}

test.describe("Home Navigation Test", () => {
  test("Navigation visibility by device", async ({ page }, testInfo) => {
    const isMobile = testInfo.project.name.includes("mobile");

    const mainNav = page.getByTestId("main-nav");
    const mobileNav = page.getByTestId("mobile-nav");

    if (isMobile) {
      await expect(mobileNav).toBeVisible();
      await expect(mainNav).toBeHidden();
    } else {
      await expect(mainNav).toBeVisible();
      await expect(mobileNav).toBeHidden();
    }
  });

  test("Check home basic contents", async ({ page }) => {
    await checkHomeBasicContents(page);
  });

  test("Transition to booking step-1 (PC only)", async ({ page }, testInfo) => {
    if (testInfo.project.name.includes("mobile")) {
      test.skip();
    }

    const bookingButton = page
      .getByTestId("main-nav")
      .getByTestId("main-navbar-button-booking");

    await bookingButton.click();
    await expect(page).toHaveURL(/\/booking\/step-1$/);

    const title = page.getByTestId("booking-step1-title");
    await expect(title).toHaveText(/日付・人数を選択してください/);
  });

  test("Save screenshot", async ({ page }, testInfo) => {
    const suffix = testInfo.project.name.includes("mobile") ? "Mobile" : "Main";

    const filename = `homeNav${suffix}.png`;

    await captureEvidenceScreenshot(page, filename);
    await compareWithSnapshot(page, filename);
  });
});
