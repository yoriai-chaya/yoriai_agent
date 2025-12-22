// screenshot.snapshot.ts
import { expect, Page } from "@playwright/test";

export async function compareWithSnapshot(
  page: Page,
  filename: string,
  maxDiffPixelRatio = 0.02
) {
  await expect(page).toHaveScreenshot(filename, {
    maxDiffPixelRatio,
  });
}
