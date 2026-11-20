import type { Metadata } from "next";

import { LearnerEntry } from "@/features/auth/learner-entry";
import { LogoutForm } from "@/features/auth/logout-form";
import { AuthHeading, AuthShell, authLink } from "@/features/auth/shell";
import { PreferenceForm } from "@/features/learner/preference-form";
import { ProfileForm } from "@/features/learner/profile-form";
import { readLearnerProfile, readLearningPreferences } from "@/lib/api/learner";

export const metadata: Metadata = { title: "Cài đặt tài khoản | Nhịp Anh" };

export default function SettingsPage() {
  return (
    <LearnerEntry destination="/settings">
      {async (session) => {
        const [profile, preferences] = await Promise.all([
          readLearnerProfile(session),
          readLearningPreferences(session),
        ]);
        return (
          <AuthShell wide headerAction={<LogoutForm />}>
            <div className="mx-auto max-w-2xl">
              <a className={`${authLink} mb-3 inline-flex min-h-11 items-center`} href="/dashboard">Về trang tài khoản</a>
              <AuthHeading title="Cài đặt tài khoản" />
              <div className="space-y-6">
                <section className="rounded-xl border border-line bg-surface p-4 sm:p-8" aria-labelledby="profile-heading">
                  <h2 className="mb-5 text-2xl/8 font-semibold" id="profile-heading">Hồ sơ cá nhân</h2>
                  <ProfileForm initial={profile} key={session.user.id} userId={session.user.id} />
                </section>
                <section className="rounded-xl border border-line bg-surface p-4 sm:p-8" aria-labelledby="preferences-heading">
                  <h2 className="mb-5 text-2xl/8 font-semibold" id="preferences-heading">Tùy chọn học tập</h2>
                  <PreferenceForm
                    initial={preferences}
                    key={`${session.user.id}:${preferences.revision}`}
                    userId={session.user.id}
                  />
                </section>
              </div>
            </div>
          </AuthShell>
        );
      }}
    </LearnerEntry>
  );
}
