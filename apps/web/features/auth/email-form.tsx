"use client";

import Link from "next/link";
import { useState } from "react";

import { requestEmail } from "@/lib/api/auth";

import { AuthField } from "./fields";
import { readText, validateEmail } from "./flow";
import { AuthForm, AuthNotice } from "./form";
import { AuthFooter, authLink } from "./shell";

type EmailMode = "register" | "resend" | "forgot";

const emailModes = {
  register: { path: "/api/v1/auth/register", action: "Gửi email xác minh" },
  resend: { path: "/api/v1/auth/verification/resend", action: "Gửi lại email xác minh" },
  forgot: { path: "/api/v1/auth/password/forgot", action: "Gửi liên kết đặt lại" },
} as const;

export function EmailForm({ mode }: { mode: EmailMode }) {
  const [sent, setSent] = useState(false);
  const { path, action } = emailModes[mode];

  return (
    <>
      {sent ? (
        <AuthNotice>
          {mode === "forgot"
            ? "Nếu tài khoản có thể khôi phục, Nhịp Anh sẽ gửi email đặt lại mật khẩu. Hãy kiểm tra hộp thư đến và thư rác."
            : "Nếu email có thể xác minh, Nhịp Anh sẽ gửi liên kết xác minh. Hãy kiểm tra hộp thư đến và thư rác."}
        </AuthNotice>
      ) : (
        <AuthForm
          label={action}
          pendingLabel="Đang gửi yêu cầu…"
          validate={(data) => validateEmail(readText(data, "email").trim())}
          action={async (data) => {
            await requestEmail(path, readText(data, "email").trim());
            setSent(true);
          }}
        >
          {(issue) => (
            <AuthField label="Email" name="email" type="email" inputMode="email" autoComplete="email" issue={issue} />
          )}
        </AuthForm>
      )}
      <AuthFooter>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <Link className={authLink} href="/login">{mode === "forgot" ? "Quay lại đăng nhập" : "Đăng nhập"}</Link>
          {mode === "register" && (
            <Link className={authLink} href="/register?resend=1">Gửi lại email xác minh</Link>
          )}
          {mode === "resend" && <Link className={authLink} href="/register">Đăng ký</Link>}
        </div>
      </AuthFooter>
    </>
  );
}
