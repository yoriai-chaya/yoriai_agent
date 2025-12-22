import { test, expect } from "./base.spec";
import { captureEvidenceScreenshot } from "./screenshot.evidence";
import { compareWithSnapshot } from "./screenshot.snapshot";

test.describe("Home Basic Test with MobileNav", () => {
  test("Check MobileNav Visible", async ({ page }) => {
    const mobileNav = page.getByTestId("mobile-nav");
    await expect(mobileNav).toBeVisible();
    const mainNav = page.getByTestId("main-nav");
    await expect(mainNav).toBeHidden();
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

  test("Save screen capture", async ({ page }) => {
    await captureEvidenceScreenshot(page, "homeMobileNav.png");
    await compareWithSnapshot(page, "homeMobileNav.png");
  });
});
