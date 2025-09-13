import { defineConfig, devices } from '@playwright/test';

console.log("Loaded Playwright config: ", __filename);
export default defineConfig({
  workers: 1,
  fullyParallel: false,
  use: {

    baseURL: "http://localhost:3003",
    headless: false,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3003',
    reuseExistingServer: true,
  },
});

