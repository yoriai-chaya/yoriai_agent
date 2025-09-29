import { defineConfig, devices } from "@playwright/test";
import path from "path";
import { results, base_url, playwright_report_file } from "./playwright.customconfig";

export default defineConfig({
  testDir: "tests",
  snapshotPathTemplate: path.join(results, "{testFilePath}/{arg}{ext}"),
  timeout: 9_000,
  use: {
    baseURL: base_url,
    headless: false,
    navigationTimeout: 12_000,
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    command: "npm run dev",
    url: base_url,
    reuseExistingServer: false,
  },

  reporter: [
    ["json", { outputFile: path.join(results, playwright_report_file) }],
  ],
});
