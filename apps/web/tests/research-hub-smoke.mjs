import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);

function loadPlaywright() {
  const explicitPath = process.env.PLAYWRIGHT_CORE_PATH;
  if (explicitPath) {
    return require(explicitPath);
  }

  const tempPath = path.join(
    process.env.TEMP || process.env.TMP || "",
    "nx-playwright-core",
    "node_modules",
    "playwright-core",
  );

  try {
    return require(tempPath);
  } catch {
    return require("playwright-core");
  }
}

const { chromium } = loadPlaywright();

const baseUrl = process.env.SMOKE_BASE_URL || "http://localhost:3000";
const expectedProvider = process.env.EXPECT_PROVIDER || "";
const runOfflineCheck = process.env.RUN_OFFLINE_CHECK === "1";

const browser = await chromium.launch({ channel: "msedge", headless: true });
const context = await browser.newContext({
  viewport: { width: 1366, height: 900 },
  permissions: ["clipboard-read", "clipboard-write"],
});
const page = await context.newPage();
const consoleErrors = [];

page.on("console", (message) => {
  if (message.type() === "error") {
    consoleErrors.push(message.text());
  }
});

try {
  await page.goto(baseUrl, { waitUntil: "networkidle" });

  if (runOfflineCheck) {
    const researchHub = page.locator('section[aria-labelledby="research-hub-title"]');
    await researchHub.getByLabel("Topic").fill("offline research validation");
    await researchHub
      .getByLabel("Objective")
      .fill("Confirm offline Research Hub error handling.");
    await researchHub.getByRole("button", { name: "Run Research" }).click();
    await researchHub
      .getByText(/GrowthOS API is offline|Research Hub is unavailable|Unable to run Research Hub/i)
      .first()
      .waitFor({ timeout: 15000 });
  } else {
    await page.getByRole("link", { name: "Research Hub" }).waitFor({ timeout: 20000 });
    await page.getByRole("link", { name: "Research Hub" }).click();
    const researchHub = page.locator('section[aria-labelledby="research-hub-title"]');
    await researchHub.getByLabel("Topic").fill("boutique agency AI automation trends");
    await researchHub
      .getByLabel("Objective")
      .fill("Find practical opportunities and risks.");
    await researchHub.getByLabel("Audience").fill("agency founders");
    await researchHub.getByRole("button", { name: "Run Research" }).click();
    await researchHub.getByText("Executive summary").waitFor({ timeout: 90000 });

    if (expectedProvider) {
      await researchHub
        .getByText(expectedProvider, { exact: true })
        .waitFor({ timeout: 10000 });
    }

    await researchHub
      .getByRole("button", { name: /Copy report|Copied|Copy failed/i })
      .click();
    await researchHub.getByRole("button", { name: "Regenerate" }).click();
    await researchHub.getByText("Executive summary").waitFor({ timeout: 90000 });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole("link", { name: "Research" }).waitFor({ timeout: 10000 });
    await page.setViewportSize({ width: 1366, height: 900 });
  }

  const unexpectedConsoleErrors = runOfflineCheck
    ? consoleErrors.filter((message) => !message.includes("ERR_CONNECTION_REFUSED"))
    : consoleErrors;

  if (unexpectedConsoleErrors.length > 0) {
    throw new Error(`Browser console errors: ${unexpectedConsoleErrors.join(" | ")}`);
  }

  console.log("Research Hub smoke passed");
} finally {
  await browser.close();
}
