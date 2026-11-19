import type { Metadata } from "next";

import { ProofForm } from "@/features/auth/proof-form";
import { AuthHeading } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Đặt lại mật khẩu | Nhịp Anh" };

export default function ResetPasswordPage() {
  return (
    <>
      <AuthHeading title="Đặt lại mật khẩu">Chọn mật khẩu mới cho tài khoản Nhịp Anh.</AuthHeading>
      <ProofForm mode="reset" />
    </>
  );
}
