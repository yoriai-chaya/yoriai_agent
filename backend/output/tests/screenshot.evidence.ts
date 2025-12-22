import { Page } from "@playwright/test";
import fs from "fs";
import path from "path";
import customConfig from "../playwright.customconfig.json";

function formatTimestamp(date: Date): string {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hh = String(date.getHours()).padStart(2, "0");
  const mi = String(date.getMinutes()).padStart(2, "0");
  const ss = String(date.getSeconds()).padStart(2, "0");

  return `${yyyy}${mm}${dd}_${hh}${mi}${ss}`;
}

export async function captureEvidenceScreenshot(
  page: Page,
  filename: string
): Promise<void> {
  const parentDir = path.dirname(__dirname);
  const evidenceDir = path.join(parentDir, customConfig.results, "evidence");

  if (!fs.existsSync(evidenceDir)) {
    fs.mkdirSync(evidenceDir, { recursive: true });
  }

  const timestamp = formatTimestamp(new Date());
  const evidenceFilename = `${timestamp}_${filename}`;
  const filePath = path.join(evidenceDir, evidenceFilename);

  await page.screenshot({
    path: filePath,
    fullPage: true,
  });
}
