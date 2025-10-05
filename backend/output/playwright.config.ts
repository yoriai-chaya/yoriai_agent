import { defineConfig, devices } from "@playwright/test";
import path from "path";
import customConfig from "./playwright.customconfig.json";
const base_url = customConfig.base_url;
const results = path.join(__dirname, customConfig.results);
const playwright_report_file = customConfig.playwright_report_file;

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
    [
      "json",
      {
        outputFile: path.join(results, playwright_report_file),
      },
    ],
  ],
});
