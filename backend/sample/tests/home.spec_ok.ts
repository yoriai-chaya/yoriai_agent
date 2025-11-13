import { test, expect } from "./base.spec";

test.use({ baseURL: "/" });

test.describe("Home Basic Test", () => {
  test("Check container", async ({ page }) => {
    const container = page.getByTestId("home-container");
    await expect(container).toBeVisible();
    await expect(container).toHaveClass(/max-w-2xl/);
    await expect(container).toHaveClass(/mx-auto/);
    await page.waitForTimeout(300);
  });

  test("Check hero image", async ({ page }) => {
    const heroImage = page.getByTestId("home-hero-image");
    await expect(heroImage).toBeAttached();
    await expect(heroImage).toHaveAttribute("alt");
    await page.waitForTimeout(300);
  });

  test("Check title", async ({ page }) => {
    const title = page.getByTestId("home-title");
    await expect(title).toHaveText(
      "都会の静寂に包まれて、心ほどけるひとときを"
    );
    await expect(title).toHaveClass(/text-center/);
    await page.waitForTimeout(300);
  });

  test("Check description", async ({ page }) => {
    const description = page.getByTestId("home-description");
    await expect(description).toHaveText(/東京の中心にありながら、/);
    await page.waitForTimeout(300);
  });

  test("Save screen capture", async ({ page }) => {
    await expect(page).toHaveScreenshot("home.png", {
      maxDiffPixelRatio: 0.02,
    });
    await page.waitForTimeout(300);
  });
});
