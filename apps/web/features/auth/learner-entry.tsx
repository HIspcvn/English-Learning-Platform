import { redirect } from "next/navigation";

import { loginDestination } from "./flow";
import { LogoutForm } from "./logout-form";
import { readServerUser } from "./server-session";
import { AuthHeading, AuthShell, authLink } from "./shell";

export async function LearnerEntry({ destination }: { destination: "/onboarding" | "/dashboard" }) {
  const user = await readServerUser();
  if (user === null) redirect("/login");
  if (!user) {
    return (
      <AuthShell>
        <AuthHeading title="Chưa thể tải phiên">
          Không thể kiểm tra phiên đăng nhập. Vui lòng thử lại.
        </AuthHeading>
        <a className={authLink} href={destination}>Thử lại</a>
      </AuthShell>
    );
  }
  const expected = loginDestination(user.onboarding_completed);
  if (destination !== expected) redirect(expected);

  const onboarding = destination === "/onboarding";
  return (
    <AuthShell>
      <AuthHeading title={onboarding ? "Thiết lập hồ sơ học tập" : "Tài khoản của bạn"}>
        <span className="wrap-anywhere">Bạn đã đăng nhập với tên {user.display_name}.</span>
      </AuthHeading>
      <p className="mb-6 text-sm/6 text-muted-ink">
        {onboarding ? "Phần thiết lập hồ sơ học tập sẽ mở ở bản cập nhật tiếp theo." : "Khu vực học tập chưa mở."}
      </p>
      <LogoutForm />
    </AuthShell>
  );
}
