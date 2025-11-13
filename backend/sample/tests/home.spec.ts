import { test, expect } from "./base.spec";
import { saveOrCompareScreenshot } from "./screenshot";
test.use({ baseURL: "/" });

test.describe("Home Basic Test", () => {
    test("Check home container", async ({ page }) => {
        const container = page.getByTestId("home-container");
        await expect(container).toBeVisible();
        await expect(container).toHaveClass(/max-w-2xl/);
        await expect(container).toHaveClass(/mx-auto/);
    });

    test("Check hero image", async ({ page }) => {
        const heroImage = page.getByTestId("home-hero-image");
        await expect(heroImage).toBeAttached();
    });

    test("Check title", async ({ page }) => {
        const title = page.getByTestId("home-title");
        await expect(title).toHaveText(/都会の静寂に包まれて、心ほどけるひとときを/);
        await expect(title).toHaveClass(/text-center/);
    });

    test("Check description", async ({ page }) => {
        const description = page.getByTestId("home-description");
        await expect(description).toHaveText(/東京の中心にありながら、/);
    });

    test("Save screen capture", async ({ page }) => {
        await saveOrCompareScreenshot(page, "home.png");
    });
});
