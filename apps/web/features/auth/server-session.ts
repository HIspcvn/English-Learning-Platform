import { cookies } from "next/headers";

import { AUTH_SESSION_PATH, readAuthSession, type AuthSession } from "@/lib/api/auth";

const sessionCookieNames = ["__Host-elp_session", "elp_session_local"] as const;

export async function readServerUser(): Promise<AuthSession["user"] | undefined> {
  const jar = await cookies();
  const cookie = sessionCookieNames.flatMap((name) => {
    const value = jar.get(name)?.value;
    return value && /^[A-Za-z0-9_-]{43}$/.test(value) ? [`${name}=${value}`] : [];
  }).join("; ");
  if (!cookie) return null;

  try {
    const url = new URL(AUTH_SESSION_PATH, process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000");
    return (await readAuthSession(url.href, { cookie })).user;
  } catch {
    // The protected page must fail closed when the session service is unavailable.
    return undefined;
  }
}
