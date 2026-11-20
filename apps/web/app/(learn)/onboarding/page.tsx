import type { Metadata } from "next";

import { LearnerEntry } from "@/features/auth/learner-entry";
import { LogoutForm } from "@/features/auth/logout-form";
import { AuthHeading, AuthShell } from "@/features/auth/shell";
import { PreferenceForm } from "@/features/learner/preference-form";
import { readLearningPreferences } from "@/lib/api/learner";

export const metadata: Metadata = { title: "Thiết lập hồ sơ học tập | Nhịp Anh" };

export default function OnboardingPage() {
  return (
    <LearnerEntry destination="/onboarding">
      {async (session) => {
        const preferences = await readLearningPreferences(session);
        return (
          <AuthShell wide headerAction={<LogoutForm />}>
            <div className="mx-auto max-w-2xl sm:rounded-xl sm:border sm:border-line sm:bg-surface sm:p-8 lg:p-10">
              <AuthHeading title="Thiết lập hồ sơ học tập">
                <span className="wrap-anywhere">Chào {session.user.display_name}.</span>{" "}
                Chọn trình độ và tùy chọn học tập của bạn. Bạn có thể cập nhật chúng trong Cài đặt.
              </AuthHeading>
              <PreferenceForm
                initial={preferences}
                key={`${session.user.id}:${preferences.revision}`}
                userId={session.user.id}
                onboarding
              />
            </div>
          </AuthShell>
        );
      }}
    </LearnerEntry>
  );
}
