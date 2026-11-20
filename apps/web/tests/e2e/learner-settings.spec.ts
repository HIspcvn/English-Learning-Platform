import { randomUUID } from "node:crypto";

import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { enterPassword, findProofLink, loopbackOrigin, mailpitUrl, openProof } from "./auth-fixtures";

const preferences = "/api/v1/me/preferences";
const password = "synthetic onboarding password";

// Mail and browser requests carry synthetic credentials and one-use proof tokens.
test.use({ trace: "off", screenshot: "off", video: "off" });

async function signIn(page: Page, email: string) {
  await page.getByLabel("Email", { exact: true }).fill(email);
  await enterPassword(page, password);
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
}

async function registerLearner(page: Page, request: APIRequestContext, baseURL: string | undefined) {
  const origin = loopbackOrigin(baseURL);
  const email = `onboarding-${randomUUID()}@example.com`;
  await page.goto("/register");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Gửi email xác minh" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Nếu email có thể xác minh" })).toBeVisible();
  await openProof(page, await findProofLink(request, origin, email, "/verify"));
  await page.getByLabel("Tên hiển thị", { exact: true }).fill("Học viên Onboarding");
  await enterPassword(page, password, true);
  await page.getByRole("button", { name: "Xác minh và tạo tài khoản" }).click();
  await expect(page).toHaveURL(/\/login\?verified=1$/);
  await signIn(page, email);
  await expect(page).toHaveURL(/\/onboarding$/);
  return email;
}

async function expectNoHorizontalOverflow(page: Page, width: number) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
}

test("anonymous learners are redirected to login from each account page", async ({ page }) => {
  for (const path of ["/onboarding", "/dashboard", "/settings"]) {
    await page.goto(path);
    await expect(page).toHaveURL(/\/login$/);
  }
});

test("desktop learners resume onboarding after reload and retry a failed save", async ({
  baseURL, page, request,
}, testInfo) => {
  test.skip(!mailpitUrl, "Set PLAYWRIGHT_MAILPIT_URL for the disposable mail delivery stack");
  test.setTimeout(75_000);
  await page.setViewportSize({ width: 1280, height: 900 });
  await registerLearner(page, request, baseURL);
  await page.goto("/settings");
  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole("heading", { name: "Thiết lập hồ sơ học tập" })).toBeVisible();
  await expectNoHorizontalOverflow(page, 1280);

  const level = page.getByLabel("Trình độ hiện tại", { exact: true });
  const goal = page.getByLabel("Mục tiêu học", { exact: true });
  const exam = page.getByLabel("Kỳ thi", { exact: true });
  const timezone = page.getByLabel("Múi giờ", { exact: true });
  const locale = page.getByLabel("Ngôn ngữ ưu tiên", { exact: true });
  await expect(locale).toHaveValue("vi");
  await level.selectOption("B1");
  await goal.selectOption("exam");
  await exam.selectOption("ielts");
  const continueButton = page.getByRole("button", { name: "Lưu và tiếp tục", exact: true });
  await timezone.fill("Mars/Olympus");
  await continueButton.click();
  await expect(timezone).toBeFocused();
  await expect(timezone).toHaveAttribute("aria-invalid", "true");
  await timezone.fill("Asia/Ho_Chi_Minh");
  await locale.selectOption("en");

  await page.reload();
  await expect(level).toHaveValue("B1");
  await expect(goal).toHaveValue("exam");
  await expect(exam).toHaveValue("ielts");
  await expect(timezone).toHaveValue("Asia/Ho_Chi_Minh");
  await expect(locale).toHaveValue("en");
  await testInfo.attach("desktop-onboarding", {
    body: await page.screenshot({ fullPage: true }), contentType: "image/png",
  });

  const endpoint = `**${preferences}`;
  let release = () => {};
  const held = new Promise<void>((resolve) => { release = resolve; });
  await page.route(endpoint, async (route) => {
    if (route.request().method() !== "PUT") return route.continue();
    await held;
    await route.abort();
  });
  await continueButton.click();
  try {
    await expect(page.getByRole("button", { name: /đang lưu/i })).toBeDisabled();
  } finally {
    release();
  }
  await expect(page.getByRole("alert").filter({
    hasText: "Không thể kết nối. Vui lòng kiểm tra mạng rồi thử lại.",
  })).toBeVisible();
  await expect(level).toHaveValue("B1");
  await expect(exam).toHaveValue("ielts");
  await page.unroute(endpoint);
  await continueButton.click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { level: 1, name: "Tài khoản của bạn" })).toBeVisible();
  await expect(page.getByText("Học viên Onboarding", { exact: true })).toBeVisible();
  await expectNoHorizontalOverflow(page, 1280);
  await page.goto("/onboarding");
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole("link", { name: "Cài đặt tài khoản", exact: true }).first().click();
  await expect(page).toHaveURL(/\/settings$/);
  await expect(page.getByRole("heading", { level: 1, name: "Cài đặt tài khoản" })).toBeVisible();
  await expect(exam).toHaveValue("ielts");
  const name = page.getByLabel("Tên hiển thị", { exact: true });
  const bio = page.getByLabel("Giới thiệu", { exact: true });
  const profileSaveButton = page.getByRole("button", { name: "Lưu hồ sơ", exact: true });
  await name.fill("   ");
  await profileSaveButton.click();
  await expect(name).toBeFocused();
  await expect(name).toHaveAttribute("aria-invalid", "true");
  await name.fill("Học viên đã cập nhật");
  await bio.fill("Mục tiêu của tôi là luyện tiếng Anh mỗi ngày.");
  const savedProfile = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/me/profile") && response.request().method() === "PATCH",
  );
  await profileSaveButton.click();
  expect((await savedProfile).status()).toBe(200);
  await expect(page.getByRole("status").filter({ hasText: "Đã lưu hồ sơ." })).toBeVisible();

  const accent = page.getByLabel("Giọng tiếng Anh", { exact: true });
  await accent.selectOption("uk");
  const savedPreferences = page.waitForResponse((response) =>
    response.url().endsWith(preferences) && response.request().method() === "PUT",
  );
  await page.getByRole("button", { name: "Lưu tùy chọn học tập", exact: true }).click();
  expect((await savedPreferences).status()).toBe(200);
  await expect(page.getByRole("status").filter({ hasText: "Đã lưu tùy chọn học tập." })).toBeVisible();
  await page.reload();
  await expect(name).toHaveValue("Học viên đã cập nhật");
  await expect(bio).toHaveValue("Mục tiêu của tôi là luyện tiếng Anh mỗi ngày.");
  await expect(accent).toHaveValue("uk");
  await expect(locale).toHaveValue("en");

  const session = await page.request.get("/api/v1/auth/session");
  expect(session.ok()).toBe(true);
  const current = await page.request.get(preferences);
  expect(current.ok()).toBe(true);
  const { revision, onboarding_completed_at: completedAt, ...values } = await current.json();
  expect(completedAt).toBeTruthy();
  const concurrentSave = await page.request.put(preferences, {
    headers: {
      Origin: loopbackOrigin(baseURL),
      "X-CSRF-Token": (await session.json()).csrf_token,
      "Idempotency-Key": randomUUID(),
    },
    data: { ...values, default_accent: "us", expected_revision: revision },
  });
  expect(concurrentSave.status()).toBe(200);
  const unsavedBio = "Bản nháp tiểu sử chưa được lưu.";
  await bio.fill(unsavedBio);
  await accent.selectOption("system");
  await page.getByRole("button", { name: "Lưu tùy chọn học tập", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Tùy chọn đã được thay đổi ở nơi khác." })).toBeVisible();
  await expect(accent).toHaveValue("system");
  await page.getByRole("button", { name: /tải lại/i }).click();
  await expect(accent).toHaveValue("us");
  await expect(bio).toHaveValue(unsavedBio);
});

test("mobile learners can finish onboarding by keyboard and return to dashboard after login", async ({
  baseURL, page, request,
}, testInfo) => {
  test.skip(!mailpitUrl, "Set PLAYWRIGHT_MAILPIT_URL for the disposable mail delivery stack");
  test.setTimeout(75_000);
  await page.setViewportSize({ width: 390, height: 844 });
  const email = await registerLearner(page, request, baseURL);
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/onboarding$/);
  await expectNoHorizontalOverflow(page, 390);

  const level = page.getByLabel("Trình độ hiện tại", { exact: true });
  const goal = page.getByLabel("Mục tiêu học", { exact: true });
  const timezone = page.getByLabel("Múi giờ", { exact: true });
  const locale = page.getByLabel("Ngôn ngữ ưu tiên", { exact: true });
  const submit = page.getByRole("button", { name: "Lưu và tiếp tục", exact: true });
  await expect(page.getByLabel("Kỳ thi", { exact: true })).toHaveCount(0);
  await expect(level).toBeEnabled();
  await level.press("ArrowDown");
  await expect(level).toHaveValue("A1");
  await page.keyboard.press("Tab");
  await expect(goal).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(timezone).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(locale).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(submit).toBeFocused();
  await testInfo.attach("mobile-onboarding", {
    body: await page.screenshot({ fullPage: true }), contentType: "image/png",
  });
  await page.keyboard.press("Enter");

  await expect(page).toHaveURL(/\/dashboard$/);
  await expectNoHorizontalOverflow(page, 390);
  await page.reload();
  await expect(page).toHaveURL(/\/dashboard$/);
  await page.goto("/settings");
  await expect(level).toHaveValue("A1");
  await expect(locale).toHaveValue("vi");
  await expect(page.getByLabel("Kỳ thi", { exact: true })).toHaveCount(0);
  await page.setViewportSize({ width: 320, height: 780 });
  await expectNoHorizontalOverflow(page, 320);
  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await signIn(page, email);
  await expect(page).toHaveURL(/\/dashboard$/);
});
