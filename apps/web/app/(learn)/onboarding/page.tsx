import type { Metadata } from "next";

import { LearnerEntry } from "@/features/auth/learner-entry";

export const metadata: Metadata = { title: "Thiết lập hồ sơ học tập | Nhịp Anh" };

export default function OnboardingPage() {
  return <LearnerEntry destination="/onboarding" />;
}
