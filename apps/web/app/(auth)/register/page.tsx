import type { Metadata } from "next";

import { EmailForm } from "@/features/auth/email-form";
import { AuthHeading } from "@/features/auth/shell";

export const metadata: Metadata = { title: "Đăng ký | Nhịp Anh" };

export default async function RegisterPage({ searchParams }: PageProps<"/register">) {
  const resend = (await searchParams).resend === "1";
  return (
    <>
      <AuthHeading title={resend ? "Gửi lại email xác minh" : "Đăng ký"}>
        {resend
          ? "Nhập email bạn đã dùng để đăng ký để nhận liên kết mới."
          : "Nhập email để nhận liên kết xác minh và tạo tài khoản Nhịp Anh."}
      </AuthHeading>
      <EmailForm key={resend ? "resend" : "register"} mode={resend ? "resend" : "register"} />
    </>
  );
}
