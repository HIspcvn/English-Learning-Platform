import { cookies } from "next/headers";

import { AUTH_SESSION_PATH, readAuthSession, type AuthSession } from "@/lib/api/auth";

const sessionCookieNames = ["__Host-elp_session", "elp_session_local"] as const;

export type LearnerSession = {
  user: NonNullable<AuthSession["user"]>;
  origin: string;
  cookie: string;
};

export async function readServerLearner(): Promise<LearnerSession | null | undefined> {
  const jar = await cookies();
  const cookie = sessionCookieNames.flatMap((name) => {
    const value = jar.get(name)?.value;
    return value && /^[A-Za-z0-9_-]{43}$/.test(value) ? [`${name}=${value}`] : [];
  }).join("; ");
  if (!cookie) return null;

  try {
    const origin = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
    const url = new URL(AUTH_SESSION_PATH, origin);
    const { user } = await readAuthSession(url.href, { cookie });
    return user ? { user, origin, cookie } : null;
  } catch {
    // The protected page must fail closed when the session service is unavailable.
    return undefined;
  }
}
