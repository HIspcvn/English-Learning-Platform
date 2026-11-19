"use client";

import Link from "next/link";

import { login } from "@/lib/api/auth";

import { AuthField } from "./fields";
import { loginDestination, readText, validateEmail } from "./flow";
import { AuthForm, AuthNotice } from "./form";
import { AuthFooter, authLink } from "./shell";

export function LoginForm({ notice }: { notice?: string }) {
  return (
    <>
      {notice && <div className="mb-5"><AuthNotice>{notice}</AuthNotice></div>}
      <AuthForm
        label="Đăng nhập"
        pendingLabel="Đang đăng nhập…"
        validate={(data) => {
          const emailIssue = validateEmail(readText(data, "email").trim());
          if (emailIssue) return emailIssue;
          const length = Array.from(readText(data, "password")).length;
          if (length === 0 || length > 128) {
            return { field: "password", message: "Vui lòng nhập mật khẩu tối đa 128 ký tự." };
          }
        }}
        action={async (data) => {
          const { user } = await login({
            email: readText(data, "email").trim(),
            password: readText(data, "password"),
          });
          window.location.replace(loginDestination(user.onboarding_completed));
        }}
      >
        {(issue) => (
          <>
            <AuthField label="Email" name="email" type="email" inputMode="email" autoComplete="username" issue={issue} />
            <AuthField label="Mật khẩu" name="password" type="password" autoComplete="current-password" issue={issue} />
            <div className="flex justify-end text-sm/6">
              <Link className={authLink} href="/forgot-password">Quên mật khẩu?</Link>
            </div>
          </>
        )}
      </AuthForm>
      <AuthFooter>
        Chưa có tài khoản? <Link className={authLink} href="/register">Đăng ký</Link>
      </AuthFooter>
    </>
  );
}
