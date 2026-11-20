import { randomBytes, randomUUID } from "node:crypto";

import { expect, test } from "@playwright/test";

import { enterPassword, findProofLink, loopbackOrigin, mailpitUrl, openProof } from "./auth-fixtures";

const auth = "/api/v1/auth";
const password = "synthetic learner password";
const newPassword = "synthetic replacement credential";

// Browser and mail requests contain synthetic credentials and proof links.
test.use({ trace: "off", screenshot: "off", video: "off" });

test("auth forms fit a 320px viewport and missing proof offers recovery", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 780 });
  const pages = [
    ["/register", "Đăng ký"],
    ["/login", "Đăng nhập"],
    ["/forgot-password", "Quên mật khẩu"],
    ["/verify", "Xác minh email"],
    ["/reset-password", "Đặt lại mật khẩu"],
  ];
  for (const [path, heading] of pages) {
    const response = await page.goto(path);
    await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(320);
    if (path === "/verify" || path === "/reset-password") {
      expect(response?.headers()["referrer-policy"]).toBe("no-referrer");
      await expect(page.getByText("Liên kết này không hợp lệ hoặc đã hết hạn.", { exact: true })).toBeVisible();
      const name = path === "/verify" ? "Gửi lại email xác minh" : "Yêu cầu liên kết mới";
      await expect(page.getByRole("link", { name })).toBeVisible();
    }
  }
});

test("keyboard users can reveal a password and retry a failed auth request", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
  const email = page.getByLabel("Email", { exact: true });
  const field = page.getByLabel("Mật khẩu", { exact: true });
  await email.press("Enter");
  await expect(email).toBeFocused();
  await expect(email).toHaveAttribute("aria-invalid", "true");
  await page.keyboard.type("keyboard@example.com");
  await page.keyboard.press("Tab");
  await expect(field).toBeFocused();
  await page.keyboard.type("short");
  await field.press("Enter");
  await expect(field).toBeFocused();
  await expect(field).toHaveAttribute("aria-invalid", "true");
  await field.fill(password);
  await page.keyboard.press("Tab");
  const toggle = page.getByRole("button", { name: "Hiện mật khẩu", exact: true });
  await expect(toggle).toBeFocused();
  await page.keyboard.press("Space");
  await expect(field).toHaveAttribute("type", "text");
  await page.keyboard.press("Space");
  await expect(field).toHaveAttribute("type", "password");

  const bootstrap = `**${auth}/session`;
  let releaseRequest = () => {};
  const requestHeld = new Promise<void>((resolve) => { releaseRequest = resolve; });
  await page.route(bootstrap, async (route) => {
    await requestHeld;
    await route.abort();
  });
  await field.press("Enter");
  try {
    await expect(page.getByRole("button", { name: "Đang đăng nhập…" })).toBeDisabled();
  } finally {
    releaseRequest();
  }
  await expect(page.getByRole("alert").filter({
    hasText: "Không thể kết nối. Vui lòng kiểm tra mạng rồi thử lại.",
  })).toBeVisible();
  await page.unroute(bootstrap);
  await field.press("Enter");
  await expect(page.getByRole("alert").filter({
    hasText: "Email hoặc mật khẩu không đúng, hoặc tài khoản chưa sẵn sàng.",
  })).toBeVisible();
});

test("register, verify, persist a cookie, and recover through Next and Mailpit at 390px", async ({
  baseURL, browser, context, page, request,
}) => {
  test.skip(!mailpitUrl, "Set PLAYWRIGHT_MAILPIT_URL for the disposable mail delivery stack");
  test.setTimeout(75_000);
  const origin = loopbackOrigin(baseURL);
  const email = `learner-${randomUUID()}@example.com`;
  const viewport = { width: 390, height: 844 };
  await page.setViewportSize(viewport);

  await page.goto("/register");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Gửi email xác minh" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Nếu email có thể xác minh" })).toBeVisible();
  await openProof(page, await findProofLink(request, origin, email, "/verify"));
  await page.getByLabel("Tên hiển thị", { exact: true }).fill("Học viên E2E");
  await enterPassword(page, password, true);
  await page.getByRole("button", { name: "Xác minh và tạo tài khoản" }).click();
  await expect(page).toHaveURL(/\/login\?verified=1$/);
  await expect(page.getByText("Email đã được xác minh.", { exact: true })).toBeVisible();

  await page.getByLabel("Email", { exact: true }).fill(email);
  await enterPassword(page, password);
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole("heading", { name: "Thiết lập hồ sơ học tập" })).toBeVisible();
  const cookieName = "elp_session_local";
  const cookie = (await context.cookies(origin)).find(({ name }) => name === cookieName);
  const persistedCookie = cookie && cookie.httpOnly && !cookie.secure &&
    cookie.sameSite === "Lax" && cookie.expires > Date.now() / 1000;
  expect(Boolean(persistedCookie)).toBe(true);
  expect(await page.evaluate((name) => document.cookie.includes(name), cookieName)).toBe(false);
  const reloaded = await page.reload();
  expect(reloaded?.headers()["cache-control"]).toContain("no-store");
  await expect(page.getByRole("heading", { name: "Thiết lập hồ sơ học tập" })).toBeVisible();

  const restarted = await browser.newContext({
    baseURL: origin, viewport, storageState: await context.storageState(),
  });
  const recovered = await browser.newContext({ baseURL: origin, viewport });
  try {
    const persisted = await restarted.newPage();
    await persisted.goto("/dashboard");
    await expect(persisted).toHaveURL(/\/onboarding$/);
    await expect(persisted.getByRole("heading", { name: "Thiết lập hồ sơ học tập" })).toBeVisible();
    await persisted.getByRole("link", { name: "Nhịp Anh, trang chủ" }).click();
    await expect(persisted).toHaveURL(`${origin}/`);

    const recoveryPage = await recovered.newPage();
    await recoveryPage.goto("/forgot-password");
    await recoveryPage.getByLabel("Email", { exact: true }).fill(email);
    await recoveryPage.getByRole("button", { name: "Gửi liên kết đặt lại" }).click();
    await expect(recoveryPage.getByRole("status").filter({ hasText: "Nếu tài khoản có thể khôi phục" })).toBeVisible();
    const resetProof = await findProofLink(request, origin, email, "/reset-password");
    await openProof(recoveryPage, resetProof);
    await enterPassword(recoveryPage, newPassword, true);
    await recoveryPage.getByRole("button", { name: "Lưu mật khẩu mới" }).click();
    await expect(recoveryPage).toHaveURL(/\/login\?reset=1$/);
    await expect(recoveryPage.getByText("Mật khẩu đã được đặt lại.", { exact: true })).toBeVisible();

    await page.reload();
    await expect(page).toHaveURL(/\/login$/);
    await persisted.goBack();
    await expect(persisted).toHaveURL(/\/login$/);

    await openProof(recoveryPage, resetProof);
    await enterPassword(recoveryPage, password, true);
    await recoveryPage.getByRole("button", { name: "Lưu mật khẩu mới" }).click();
    await expect(recoveryPage.getByText("Liên kết này không hợp lệ hoặc đã hết hạn.", { exact: true })).toBeVisible();

    await recoveryPage.goto("/login");
    await recoveryPage.getByLabel("Email", { exact: true }).fill(email);
    await enterPassword(recoveryPage, newPassword);
    await recoveryPage.getByRole("button", { name: "Đăng nhập", exact: true }).click();
    await expect(recoveryPage).toHaveURL(/\/onboarding$/);
    await recoveryPage.getByRole("button", { name: "Đăng xuất" }).click();
    await expect(recoveryPage).toHaveURL(/\/login$/);
    await recoveryPage.goto("/onboarding");
    await expect(recoveryPage).toHaveURL(/\/login$/);
  } finally {
    await restarted.close();
    await recovered.close();
  }
});

test("Next proxy holds the same IP quota when forwarded values change", async ({ request, baseURL }) => {
  test.skip(!mailpitUrl, "The shared IP quota test needs the disposable auth stack");
  const origin = loopbackOrigin(baseURL);
  const bootstrap = await request.get(`${auth}/session`);
  expect(bootstrap.status()).toBe(200);
  const { csrf_token } = await bootstrap.json() as { csrf_token: string };
  let limited = false;
  let accepted = 0;

  for (let index = 1; index <= 11; index += 1) {
    const suppliedIp = `203.0.113.${index}`;
    const response = await request.post(`${auth}/password/reset`, {
      headers: {
        Origin: origin,
        "X-CSRF-Token": csrf_token,
        Forwarded: `for=${suppliedIp}`,
        "X-Forwarded-For": suppliedIp,
        "X-Real-IP": suppliedIp,
      },
      data: { token: randomBytes(32).toString("base64url"), password: newPassword },
    });
    if (response.status() === 429) {
      expect((await response.json()).code).toBe("RATE_LIMITED");
      expect(Number(response.headers()["retry-after"])).toBeGreaterThan(0);
      limited = true;
    } else {
      expect(limited).toBe(false);
      expect(response.status()).toBe(410);
      accepted += 1;
    }
  }
  expect(accepted).toBeGreaterThan(0);
  expect(limited).toBe(true);
});
