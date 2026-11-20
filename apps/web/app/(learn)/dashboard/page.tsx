import type { Metadata } from "next";

import { LearnerEntry } from "@/features/auth/learner-entry";
import { LogoutForm } from "@/features/auth/logout-form";
import { AuthHeading, AuthShell, authLink } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Tài khoản của bạn | Nhịp Anh" };

const upcomingModules = [
  { title: "Lộ trình học", description: "Khóa học và bài luyện theo trình độ." },
  { title: "Từ vựng", description: "Bộ từ cá nhân và bài ôn theo lịch." },
  { title: "Tiến độ học tập", description: "Lịch sử bài học và mục tiêu hằng ngày." },
];

export default function DashboardPage() {
  return (
    <LearnerEntry destination="/dashboard">
      {({ user }) => (
        <AuthShell wide headerAction={<LogoutForm />}>
          <AuthHeading title="Tài khoản của bạn">
            <span className="wrap-anywhere">Chào {user.display_name}.</span>{" "}
            Hồ sơ học tập của bạn đã sẵn sàng.
          </AuthHeading>
          <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] lg:gap-12">
            <section className="min-w-0" aria-labelledby="modules-heading">
              <h2 className="mb-4 text-2xl/8 font-semibold" id="modules-heading">Khu vực học tập</h2>
              <ul className="divide-y divide-line rounded-xl border border-line bg-surface">
                {upcomingModules.map(({ title, description }) => (
                  <li className="flex flex-wrap items-start justify-between gap-2 p-4 sm:p-5" key={title}>
                    <div className="min-w-0">
                      <h3 className="font-semibold">{title}</h3>
                      <p className="mt-1 text-sm/6 text-muted-ink">{description}</p>
                    </div>
                    <span className="rounded-md bg-canvas px-2 py-1 text-xs/4 font-semibold text-muted-ink">Sắp mở</span>
                  </li>
                ))}
              </ul>
            </section>
            <section className="min-w-0" aria-labelledby="snapshot-heading">
              <h2 className="mb-4 text-2xl/8 font-semibold" id="snapshot-heading">Thông tin cá nhân</h2>
              <dl className="space-y-4 rounded-xl border border-line bg-surface p-4 sm:p-5">
                <div>
                  <dt className="text-sm text-muted-ink">Tên hiển thị</dt>
                  <dd className="mt-1 wrap-anywhere font-medium">{user.display_name}</dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-ink">Múi giờ</dt>
                  <dd className="mt-1 wrap-anywhere font-medium">{user.timezone}</dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-ink">Ngôn ngữ ưu tiên</dt>
                  <dd className="mt-1 font-medium">{user.locale === "en" ? <span lang="en">English</span> : "Tiếng Việt"}</dd>
                </div>
              </dl>
              <a className={`${authLink} mt-3 inline-flex min-h-11 items-center`} href="/settings">Cài đặt tài khoản</a>
            </section>
          </div>
        </AuthShell>
      )}
    </LearnerEntry>
  );
}
