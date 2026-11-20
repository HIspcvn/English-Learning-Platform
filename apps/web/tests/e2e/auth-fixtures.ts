import { expect, type APIRequestContext, type Page } from "@playwright/test";

export const mailpitUrl = process.env.PLAYWRIGHT_MAILPIT_URL;

export function loopbackOrigin(value: string | undefined): string {
  if (!value) throw new Error("Configure a disposable local auth stack to run this test");
  const url = new URL(value);
  if (!["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)) {
    throw new Error("Auth fixtures require a loopback URL");
  }
  return url.origin;
}

export async function findProofLink(
  request: APIRequestContext,
  baseURL: string | undefined,
  email: string,
  path: "/verify" | "/reset-password",
) {
  const prefix = `${loopbackOrigin(baseURL)}${path}#token=`;
  const mailbox = new URL("/api/v1/search", loopbackOrigin(mailpitUrl));
  mailbox.searchParams.set("query", `to:${email}`);
  let proofLink = "";

  await expect.poll(async () => {
    const result = await request.get(mailbox.href);
    if (!result.ok()) return false;
    const { messages } = await result.json() as { messages?: { ID: string }[] };
    for (const { ID } of messages ?? []) {
      const response = await request.get(new URL(`/api/v1/message/${ID}`, mailbox).href);
      if (!response.ok()) continue;
      const { Text } = await response.json() as { Text?: string };
      proofLink = Text?.split(/\r?\n/).map((line) => line.trim()).find((line) => line.startsWith(prefix)) ?? "";
      if (proofLink) return true;
    }
    return false;
  }, { message: `Waiting for the worker to deliver mail for ${path}`, timeout: 20_000 }).toBe(true);
  return proofLink;
}

export async function openProof(page: Page, link: string) {
  try {
    await page.goto(link);
  } catch {
    throw new Error("Could not open the auth email link");
  }
  await expect.poll(() => Boolean(new URL(page.url()).hash)).toBe(false);
}

export async function enterPassword(page: Page, value: string, confirm = false) {
  await page.getByLabel("Mật khẩu", { exact: true }).fill(value);
  if (confirm) await page.getByLabel("Nhập lại mật khẩu", { exact: true }).fill(value);
}
