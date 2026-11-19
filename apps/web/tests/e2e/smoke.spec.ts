import { expect, test } from "@playwright/test";

test("the public page is visible without horizontal overflow at 390px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: "Nhịp Anh" })).toBeVisible();
  await expect(page.getByRole("main")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
});

test("the browser reaches the real API through the web origin", async ({ page, baseURL }) => {
  const responsePromise = page.waitForResponse(new URL("/health/live", baseURL).href);
  await page.goto("/");
  const response = await responsePromise;
  expect(response.ok()).toBe(true);
  expect(await response.json()).toEqual({ status: "ok" });
  expect(response.headers()["x-request-id"]).toBeTruthy();
  await expect(page.getByRole("status")).toHaveText("API đang hoạt động");
});

test("the page can retry a failed API connection", async ({ page }) => {
  await page.route("**/health/live", (route) => route.abort());
  await page.goto("/");
  await expect(page.getByRole("status")).toHaveText("Chưa kết nối được API");

  await page.unroute("**/health/live");
  await page.getByRole("button", { name: "Thử lại" }).click();
  await expect(page.getByRole("status")).toHaveText("API đang hoạt động");
});

test("the web origin serves readiness and versioned OpenAPI", async ({ request }) => {
  const readiness = await request.get("/health/ready");
  expect(readiness.ok()).toBe(true);
  expect(await readiness.json()).toEqual({ status: "ready" });

  const schema = await request.get("/api/v1/openapi.json");
  expect(schema.ok()).toBe(true);
  expect((await schema.json()).paths).toHaveProperty(["/health/live", "get"]);
});
