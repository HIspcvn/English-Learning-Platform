import type { Metadata } from "next";

import { ProofForm } from "@/features/auth/proof-form";
import { AuthHeading } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Xác minh email | Nhịp Anh" };

export default function VerifyPage() {
  return (
    <>
      <AuthHeading title="Xác minh email">Chọn tên hiển thị và mật khẩu để hoàn tất đăng ký.</AuthHeading>
      <ProofForm mode="verify" />
    </>
  );
}
