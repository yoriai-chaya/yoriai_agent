import { expect, Page } from "@playwright/test";
import fs from "fs";
import path from "path";
import customConfig from "../playwright.customconfig.json";

/**
 * saveOrCompareScreenshot
 *
 * @param page - Playwright Page object
 * @param filename - Screenshot filename
 * @param maxDiffPixelRatio - An acceptable ratio of pixels (default: 0.02)
 */
export async function saveOrCompareScreenshot(
  page: Page,
  filename: string,
  maxDiffPixelRatio = 0.02
): Promise<void> {
  const parentDir = path.dirname(__dirname);
  const screenshot_dir = customConfig.screenshot_dir;
  const sc_dir = path.join(parentDir, customConfig.results, screenshot_dir);
  const screenshotPath = path.resolve(sc_dir, filename);

  const backupDir = path.join(sc_dir, "backup");

  if (!fs.existsSync(sc_dir)) {
    fs.mkdirSync(sc_dir, { recursive: true });
  }
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
  }

  if (fs.existsSync(screenshotPath)) {
    const stats = fs.statSync(screenshotPath);
    const mtime = stats.mtime;
    const formattedDate = `${mtime.getFullYear()}${String(
      mtime.getMonth() + 1
    ).padStart(2, "0")}${String(mtime.getDate()).padStart(2, "0")}_${String(
      mtime.getHours()
    ).padStart(2, "0")}${String(mtime.getMinutes()).padStart(2, "0")}${String(
      mtime.getSeconds()
    ).padStart(2, "0")}`;
    const backupFilename = `${formattedDate}_${filename}`;
    const backupPath = path.join(backupDir, backupFilename);
    fs.copyFileSync(screenshotPath, backupPath);

    await expect(page).toHaveScreenshot(filename, {
      maxDiffPixelRatio,
    });
  } else {
    const buffer = await page.screenshot();
    fs.writeFileSync(screenshotPath, buffer);
  }

  await page.waitForTimeout(300);
}
