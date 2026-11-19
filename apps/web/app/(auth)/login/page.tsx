import type { Metadata } from "next";

import { LoginForm } from "@/features/auth/login-form";
import { AuthHeading } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Đăng nhập | Nhịp Anh" };

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { verified, reset } = await searchParams;
  const notice = verified === "1"
    ? "Email đã được xác minh."
    : reset === "1"
      ? "Mật khẩu đã được đặt lại."
      : undefined;
  return (
    <>
      <AuthHeading title="Đăng nhập" />
      <LoginForm notice={notice} />
    </>
  );
}
