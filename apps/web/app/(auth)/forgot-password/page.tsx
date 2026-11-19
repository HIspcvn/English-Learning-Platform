import type { Metadata } from "next";

import { EmailForm } from "@/features/auth/email-form";
import { AuthHeading } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Quên mật khẩu | Nhịp Anh" };

export default function ForgotPasswordPage() {
  return (
    <>
      <AuthHeading title="Quên mật khẩu">Nhập email tài khoản để yêu cầu liên kết đặt lại mật khẩu.</AuthHeading>
      <EmailForm mode="forgot" />
    </>
  );
}
