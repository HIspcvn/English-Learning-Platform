import { AUTH_SESSION_PATH, readAuthSession } from "./auth";
import type { paths } from "./schema";

const profilePath = "/api/v1/me/profile" satisfies keyof paths;
const preferencesPath = "/api/v1/me/preferences" satisfies keyof paths;

type ProfileOperations = paths[typeof profilePath];
type PreferencesOperations = paths[typeof preferencesPath];

export type LearnerProfile = ProfileOperations["get"]["responses"][200]["content"]["application/json"];
export type ProfilePatch = ProfileOperations["patch"]["requestBody"]["content"]["application/json"];
export type LearningPreferences = PreferencesOperations["get"]["responses"][200]["content"]["application/json"];
export type PreferencesCommand = PreferencesOperations["put"]["requestBody"]["content"]["application/json"];

type ReadContext = { origin: string; cookie: string };

export class LearnerApiError extends Error {
  constructor(readonly status: number, readonly code?: string) {
    super("Learner request failed");
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    cache: "no-store",
    credentials: "same-origin",
    redirect: "error",
    ...options,
  });
  if (response.ok) return response.json();

  const problem: unknown = await response.json().catch(() => undefined);
  const code = problem && typeof problem === "object" && "code" in problem && typeof problem.code === "string"
    ? problem.code
    : undefined;
  throw new LearnerApiError(response.status, code);
}

async function read<T>(path: string, { origin, cookie }: ReadContext): Promise<T> {
  try {
    return await request(new URL(path, origin).href, { headers: { cookie } });
  } catch (error) {
    if (error instanceof LearnerApiError) throw error;
    throw new LearnerApiError(503);
  }
}

async function mutationHeaders(userId: string) {
  const { user, csrf_token } = await readAuthSession(AUTH_SESSION_PATH);
  // Another tab may have signed a different learner into the same browser.
  if (user?.id !== userId) throw new LearnerApiError(401);
  return new Headers({ "Content-Type": "application/json", "X-CSRF-Token": csrf_token });
}

export function readLearnerProfile(context: ReadContext) {
  return read<LearnerProfile>(profilePath, context);
}

export function readLearningPreferences(context: ReadContext) {
  return read<LearningPreferences>(preferencesPath, context);
}

export async function patchLearnerProfile(userId: string, body: ProfilePatch): Promise<LearnerProfile> {
  return request(profilePath, {
    method: "PATCH",
    headers: await mutationHeaders(userId),
    body: JSON.stringify(body),
  });
}

export async function putLearningPreferences(
  userId: string,
  body: PreferencesCommand,
  idempotencyKey: string,
): Promise<LearningPreferences> {
  const headers = await mutationHeaders(userId);
  headers.set("Idempotency-Key", idempotencyKey);
  return request(preferencesPath, { method: "PUT", headers, body: JSON.stringify(body) });
}
