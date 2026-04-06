import { test, expect, type Page } from "@playwright/test";

const TEST_USER = {
  email: "test@hazn.ai",
  password: "testpass123",
};

async function loginUser(page: Page) {
  await page.goto("/login");
  await page.waitForTimeout(1000);
  await page.getByRole("textbox", { name: "Email" }).fill(TEST_USER.email);
  await page.getByRole("textbox", { name: "Password" }).fill(TEST_USER.password);
  await page.getByRole("button", { name: "Sign In" }).click();
  // Wait for redirect away from login
  await page.waitForURL(/^(?!.*\/login)/, { timeout: 10000 });
  // Wait for workspace to render (sidebar/header should appear)
  await page.waitForTimeout(2000);
}

test.describe("Auth flow", () => {
  test("login page renders with form fields and OAuth buttons", async ({
    page,
  }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "Hazn" })).toBeVisible();
    await expect(
      page.getByRole("textbox", { name: "Email" }),
    ).toBeVisible();
    await expect(
      page.getByRole("textbox", { name: "Password" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Sign In" }),
    ).toBeVisible();
    // OAuth buttons
    await expect(
      page.getByRole("button", { name: /Google/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Facebook/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Apple/i }),
    ).toBeVisible();
    // Magic link tab
    await expect(page.getByRole("tab", { name: "Magic Link" })).toBeVisible();
  });

  test("login with valid credentials redirects to dashboard", async ({
    page,
  }) => {
    await loginUser(page);
    await expect(page).not.toHaveURL(/login/);
  });

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/login");
    await page.waitForTimeout(1000);
    await page.getByRole("textbox", { name: "Email" }).fill("wrong@example.com");
    await page.getByRole("textbox", { name: "Password" }).fill("wrongpass");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page.getByText(/not correct|failed|error/i)).toBeVisible({
      timeout: 5000,
    });
  });

  test("signup link navigates to signup page", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: "Sign up" }).click();
    await expect(page).toHaveURL(/signup/);
  });
});

test.describe("Workspace (authenticated)", () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test("dashboard loads after login", async ({ page }) => {
    const body = page.locator("body");
    await expect(body).toBeVisible();
    const text = await body.textContent();
    expect(text?.length).toBeGreaterThan(0);
  });

  test("navigate to clients via client-side routing", async ({ page }) => {
    const link = page.getByRole("link", { name: /client/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/clients/, { timeout: 5000 });
    }
  });

  test("navigate to workflows via client-side routing", async ({ page }) => {
    const link = page.getByRole("link", { name: /workflow/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/workflows/, { timeout: 5000 });
    }
  });

  test("navigate to approvals via client-side routing", async ({ page }) => {
    const link = page.getByRole("link", { name: /approval/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/approvals/, { timeout: 5000 });
    }
  });

  test("navigate to deliverables via client-side routing", async ({
    page,
  }) => {
    const link = page.getByRole("link", { name: /deliverable/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/deliverables/, { timeout: 5000 });
    }
  });

  test("navigate to memory via client-side routing", async ({ page }) => {
    const link = page.getByRole("link", { name: /memory/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/memory/, { timeout: 5000 });
    }
  });

  test("navigate to settings via client-side routing", async ({ page }) => {
    const link = page.getByRole("link", { name: /setting/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await expect(page).toHaveURL(/settings/, { timeout: 5000 });
    }
  });
});
