import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { LearnerApiError } from "@/lib/api/learner";

import { loginDestination } from "./flow";
import { readServerLearner, type LearnerSession } from "./server-session";
import { AuthHeading, AuthShell, authLink } from "./shell";

type LearnerEntryProps = {
  destination: "/onboarding" | "/dashboard" | "/settings";
  children: (session: LearnerSession) => ReactNode | Promise<ReactNode>;
};

function EntryUnavailable({ destination }: Pick<LearnerEntryProps, "destination">) {
  return (
    <AuthShell>
      <AuthHeading title="Chưa thể tải tài khoản">
        Vui lòng thử lại để kiểm tra phiên và tải thông tin của bạn.
      </AuthHeading>
      <a className={authLink} href={destination}>Thử lại</a>
    </AuthShell>
  );
}

export async function LearnerEntry({ destination, children }: LearnerEntryProps) {
  const session = await readServerLearner();
  if (session === null) redirect("/login");
  if (!session) return <EntryUnavailable destination={destination} />;

  const expected = loginDestination(session.user.onboarding_completed);
  if ((destination === "/onboarding") !== (expected === "/onboarding")) redirect(expected);

  try {
    return await children(session);
  } catch (error) {
    if (!(error instanceof LearnerApiError)) throw error;
    if (error.status === 401) redirect("/login");
    return <EntryUnavailable destination={destination} />;
  }
}
