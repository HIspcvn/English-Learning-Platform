import type { Metadata } from "next";

import { LearnerEntry } from "@/features/auth/learner-entry";

export const metadata: Metadata = { title: "Tài khoản của bạn | Nhịp Anh" };

export default function DashboardPage() {
  return <LearnerEntry destination="/dashboard" />;
}
