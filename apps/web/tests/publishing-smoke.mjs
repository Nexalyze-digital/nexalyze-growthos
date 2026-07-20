import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
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
const launchOptions = process.env.PLAYWRIGHT_CHANNEL
  ? { channel: process.env.PLAYWRIGHT_CHANNEL, headless: true }
  : { headless: true };

const browser = await chromium.launch(launchOptions);
const context = await browser.newContext({
  permissions: ["clipboard-read", "clipboard-write"],
  viewport: { width: 1366, height: 900 },
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
  await page.evaluate(() => window.localStorage.removeItem("growthos.session.v1"));
  await page.reload({ waitUntil: "networkidle" });
  await authenticate();

  const publishing = page.locator('section[aria-labelledby="publishing-title"]');
  await page.getByRole("link", { name: "Publishing" }).click();
  await publishing.getByRole("button", { name: "New draft" }).click();
  await publishing.getByLabel("Title").fill("Publishing smoke draft");
  await publishing.getByLabel("Rich text draft body").fill("Draft body for Publishing Engine smoke validation.");
  await publishing.getByLabel("Hashtags").fill("#GrowthOS #Publishing");
  await publishing.getByRole("button", { name: "Create draft" }).click();
  await publishing.getByRole("button", { name: "Save new version" }).waitFor({ timeout: 15000 });
  await publishing.getByText("Version 1").waitFor({ timeout: 15000 });

  await publishing.getByLabel("Rich text draft body").fill("Updated draft body for version history.");
  await publishing.getByRole("button", { name: "Save new version" }).click();
  await publishing.getByText("Version 2").waitFor({ timeout: 15000 });

  await publishing.getByRole("button", { name: "Submit" }).click();
  await publishing.getByText("Draft submitted for review.").waitFor({ timeout: 15000 });
  await allowSelfApprovalForActiveWorkspace();

  await publishing.getByRole("tab", { name: "Review" }).click();
  await publishing.getByLabel("Review comment").fill("Approved in smoke test.");
  await publishing.getByRole("button", { name: "Approve" }).click();
  await publishing.getByText("Review updated.").waitFor({ timeout: 15000 });

  await publishing.getByRole("tab", { name: "Editor" }).click();
  await publishing.locator('input[type="datetime-local"]').first().fill(futureLocalDateTime());
  await publishing.getByRole("button", { name: "Schedule approved draft" }).click();
  await publishing.getByText("Draft scheduled.").waitFor({ timeout: 15000 });
  await publishing.getByRole("button", { name: "Enqueue draft" }).click();
  await publishing.getByText("Draft added to the publishing queue.").waitFor({ timeout: 15000 });

  await publishing.getByRole("tab", { name: "Queue" }).click();
  await publishing.getByText(/LinkedIn|pending|cancelled/i).first().waitFor({ timeout: 15000 });

  await publishing.getByRole("tab", { name: "Library" }).click();
  await publishing.getByLabel("Search").fill("Publishing smoke");
  await publishing.getByRole("button", { name: "Filter" }).click();
  await publishing.getByText("Publishing smoke draft").waitFor({ timeout: 15000 });

  await setStoredRole("viewer");
  await page.reload({ waitUntil: "networkidle" });
  await publishing.getByRole("tab", { name: "Library" }).waitFor({ timeout: 15000 });
  await expectButtonHidden("New draft");
  await expectButtonHidden("Create draft");
  await expectButtonHidden("Approve");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("link", { name: "Publish" }).waitFor({ timeout: 10000 });
  await page.getByRole("link", { name: "Publish" }).click();
  await publishing.getByRole("tab", { name: "Library" }).waitFor({ timeout: 10000 });

  if (consoleErrors.length > 0) {
    throw new Error(`Browser console errors: ${consoleErrors.join(" | ")}`);
  }

  console.log("Publishing smoke passed");
} finally {
  await browser.close();
}

async function authenticate() {
  const email = `publishing-smoke-${Date.now()}@example.com`;
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByLabel("Name").fill("Publishing Smoke");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("StrongPass123");
  await page.getByLabel("Organization").fill("Smoke Organization");
  await page.getByLabel("Workspace").fill("Smoke Workspace");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.getByRole("heading", { name: "AI Content Studio" }).waitFor({ timeout: 20000 });
}

async function setStoredRole(role) {
  const ids = await page.evaluate((nextRole) => {
    const raw = window.localStorage.getItem("growthos.session.v1");
    if (!raw) {
      throw new Error("No stored session to update.");
    }
    const session = JSON.parse(raw);
    session.workspaces = session.workspaces.map((workspace) =>
      workspace.id === session.active_workspace_id
        ? { ...workspace, role: nextRole }
        : workspace,
    );
    window.localStorage.setItem("growthos.session.v1", JSON.stringify(session));
    return {
      userId: session.user.id,
      workspaceId: session.active_workspace_id,
    };
  }, role);
  const apiDir = path.resolve(process.cwd(), "..", "api");
  const python = path.join(apiDir, ".venv", "Scripts", "python.exe");
  const code = [
    "from app.db.session import SessionLocal",
    "from app.db.models import WorkspaceMembership",
    `workspace_id = ${JSON.stringify(ids.workspaceId)}`,
    `user_id = ${JSON.stringify(ids.userId)}`,
    `role = ${JSON.stringify(role)}`,
    "with SessionLocal() as db:",
    "    membership = db.query(WorkspaceMembership).filter_by(workspace_id=workspace_id, user_id=user_id).one()",
    "    membership.role = role",
    "    db.commit()",
  ].join("\n");
  execFileSync(python, ["-c", code], { cwd: apiDir, stdio: "pipe" });
}

async function allowSelfApprovalForActiveWorkspace() {
  const workspaceId = await page.evaluate(() => {
    const raw = window.localStorage.getItem("growthos.session.v1");
    if (!raw) {
      throw new Error("No stored session.");
    }
    return JSON.parse(raw).active_workspace_id;
  });
  const apiDir = path.resolve(process.cwd(), "..", "api");
  const python = path.join(apiDir, ".venv", "Scripts", "python.exe");
  const code = [
    "from app.db.session import SessionLocal",
    "from app.db.models import WorkspacePublishingSettings",
    `workspace_id = ${JSON.stringify(workspaceId)}`,
    "with SessionLocal() as db:",
    "    settings = db.query(WorkspacePublishingSettings).filter_by(workspace_id=workspace_id).one_or_none()",
    "    if settings is None:",
    "        settings = WorkspacePublishingSettings(workspace_id=workspace_id)",
    "        db.add(settings)",
    "    settings.prevent_self_approval = False",
    "    db.commit()",
  ].join("\n");
  execFileSync(python, ["-c", code], { cwd: apiDir, stdio: "pipe" });
}

async function expectButtonHidden(name) {
  const count = await page.getByRole("button", { name }).count();
  if (count !== 0) {
    throw new Error(`Expected ${name} button to be hidden for viewer role.`);
  }
}

function futureLocalDateTime() {
  const date = new Date(Date.now() + 24 * 60 * 60 * 1000);
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
