import type { paths } from "./schema";

export const AUTH_SESSION_PATH = "/api/v1/auth/session" satisfies keyof paths;
export type AuthSession = paths[typeof AUTH_SESSION_PATH]["get"]["responses"][200]["content"]["application/json"];

type CommandPath =
  | "/api/v1/auth/register"
  | "/api/v1/auth/verification/resend"
  | "/api/v1/auth/verify"
  | "/api/v1/auth/login"
  | "/api/v1/auth/logout"
  | "/api/v1/auth/password/forgot"
  | "/api/v1/auth/password/reset";

type RequestBody<Path extends CommandPath> = paths[Path]["post"]["requestBody"] extends {
  content: { "application/json": infer Body };
}
  ? Body
  : undefined;

type LoginResponse = paths["/api/v1/auth/login"]["post"]["responses"][200]["content"]["application/json"];

export class AuthApiError extends Error {
  constructor(readonly status: number) {
    super("Auth request failed");
  }
}

const authRequestOptions: RequestInit = {
  cache: "no-store",
  credentials: "same-origin",
  redirect: "error",
};

export async function readAuthSession(url: string, headers?: HeadersInit): Promise<AuthSession> {
  const response = await fetch(url, { ...authRequestOptions, headers });
  if (!response.ok) throw new AuthApiError(response.status);
  return response.json();
}

async function sendAuthCommand<Path extends CommandPath>(path: Path, body: RequestBody<Path>) {
  const { csrf_token } = await readAuthSession(AUTH_SESSION_PATH);
  const headers = new Headers({ "X-CSRF-Token": csrf_token });
  if (body !== undefined) headers.set("Content-Type", "application/json");
  const response = await fetch(path, {
    ...authRequestOptions,
    method: "POST",
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new AuthApiError(response.status);
  return response;
}

export async function login(body: RequestBody<"/api/v1/auth/login">): Promise<LoginResponse> {
  const response = await sendAuthCommand("/api/v1/auth/login", body);
  return response.json();
}

export async function logout() {
  await sendAuthCommand("/api/v1/auth/logout", undefined);
}

type EmailPath = "/api/v1/auth/register" | "/api/v1/auth/verification/resend" | "/api/v1/auth/password/forgot";

export async function requestEmail(path: EmailPath, email: string) {
  await sendAuthCommand(path, { email });
}

export async function verifyEmail(body: RequestBody<"/api/v1/auth/verify">) {
  await sendAuthCommand("/api/v1/auth/verify", body);
}

export async function resetPassword(body: RequestBody<"/api/v1/auth/password/reset">) {
  await sendAuthCommand("/api/v1/auth/password/reset", body);
}
