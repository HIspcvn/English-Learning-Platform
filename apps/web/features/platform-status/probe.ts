import type { paths } from "@/lib/api/schema";

export const LIVE_PATH = "/health/live" satisfies keyof paths;

type LiveResponse = paths[typeof LIVE_PATH]["get"]["responses"][200]["content"]["application/json"];
const expectedStatus: LiveResponse["status"] = "ok";

export async function isLiveResponse(response: Response): Promise<boolean> {
  if (response.status !== 200) {
    return false;
  }

  try {
    const body: unknown = await response.json();
    return typeof body === "object" && body !== null && "status" in body && body.status === expectedStatus;
  } catch {
    return false;
  }
}
