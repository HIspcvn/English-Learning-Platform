import { AuthShell } from "@/features/auth/shell";

export default function LearnerLoading() {
  return (
    <AuthShell wide>
      <p className="mx-auto max-w-2xl text-base/6 text-muted-ink" role="status">Đang tải tài khoản…</p>
      <div aria-hidden="true" className="mx-auto mt-5 h-56 max-w-2xl rounded-xl border border-line bg-surface" />
    </AuthShell>
  );
}
