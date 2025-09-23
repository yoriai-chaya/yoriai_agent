import { defineConfig, devices } from "@playwright/test";
import path from "path";
import { results, base_url } from "./config.shared";

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
    url: "http://localhost:3003",
    reuseExistingServer: false,
  },

  reporter: [
    ["json", { outputFile: path.join(results, "playwright-report.json") }],
  ],
});
