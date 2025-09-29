import {
  test as base,
  expect as baseExpect,
  Page,
  Response,
} from "@playwright/test";
import { results, base_url, playwright_info_file } from "../playwright.customconfig";
import path from "path";
import fs from "fs/promises";

let sharedPage: Page | undefined;
let url: string | undefined;
let status: number | undefined;

const info_file = path.join(results, playwright_info_file);
const backup_dir = path.join(results, "backup");

function formatDateTime(d: Date) {
  const y = d.getFullYear().toString();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const h = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  const s = String(d.getSeconds()).padStart(2, "0");
  return `${y}${m}${dd}_${h}${min}${s}`;
}

async function ensureDirs() {
  await fs.mkdir(results, { recursive: true });
  await fs.mkdir(backup_dir, { recursive: true });
}

async function backupExistingIfAny() {
  try {
    const stats = await fs.stat(info_file);
    const mtime = stats.mtime;
    const ts = formatDateTime(mtime);

    const parsed = path.parse(playwright_info_file);
    const newName = `${parsed.name}_${ts}${parsed.ext}`;

    const dest = path.join(backup_dir, newName);
    await fs.rename(info_file, dest);
    console.log(`Backed up existing ${info_file} -> ${dest}`);
  } catch (err: unknown) {
    if (
      err instanceof Error &&
      (err as NodeJS.ErrnoException).code === "ENOENT"
    ) {
      // none
    } else {
      throw err;
    }
  }
}

async function updateInfoFile(data: Record<string, unknown>) {
  let current: Record<string, unknown> = {};
  try {
    const content = await fs.readFile(info_file, "utf-8");
    current = JSON.parse(content);
  } catch (err: unknown) {
    if (
      err instanceof Error &&
      (err as NodeJS.ErrnoException).code === "ENOENT"
    ) {
      current = {};
    } else {
      throw err;
    }
  }
  const merged = { ...current, ...data };
  await fs.writeFile(info_file, JSON.stringify(merged, null, 2));
  console.log(`Updated info file: ${JSON.stringify(data)}`);
}

export const test = base.extend<{ page: Page }>({
  page: async ({ browser, baseURL }, run, testInfo) => {
    console.log("base: page fixture called");

    let finalURL = baseURL ?? base_url;
    if (baseURL?.startsWith("/")) {
      finalURL = `${base_url}${baseURL}`;
    }
    if (!sharedPage) {
      sharedPage = await browser.newPage();
      const response: Response | null = await sharedPage.goto(finalURL);
      url = response?.url();
      status = response?.status();
    }

    // run tests
    await run(sharedPage);

    try {
      const titlePath = testInfo.titlePath;
      const describeName =
        titlePath.length > 0 ? titlePath[0] : "(no describe)";
      await updateInfoFile({
        url,
        status,
        describe: describeName,
      });
    } catch (err) {
      console.error("Failed to update info file from fixture: ", err);
    }
  },
});

test.beforeAll(async () => {
  console.log("base: beforeAll called");
  await ensureDirs();
  await backupExistingIfAny();
  const startTime = formatDateTime(new Date());
  await updateInfoFile({ startTime });
  console.log(`Recorded startTime: ${startTime}`);
});

test.afterAll(async () => {
  const endTime = formatDateTime(new Date());
  await updateInfoFile({ endTime });
  console.log(`Recorded endTime: ${endTime}`);
});

export const expect = baseExpect;
