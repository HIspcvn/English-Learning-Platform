"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { resetPassword, verifyEmail } from "@/lib/api/auth";

import { AuthField } from "./fields";
import { readText, takeEmailProof, validateNewPassword } from "./flow";
import { AuthForm, AuthNotice } from "./form";
import { AuthFooter, authLink } from "./shell";

export function ProofForm({ mode }: { mode: "verify" | "reset" }) {
  const [proof, setProof] = useState<string | null>(null);
  const verifying = mode === "verify";

  useEffect(() => {
    let disposed = false;
    function takeProof() {
      setProof(takeEmailProof(window.location, window.history));
    }
    queueMicrotask(() => {
      if (!disposed) takeProof();
    });
    function readNewFragment() {
      if (window.location.hash.startsWith("#token=")) takeProof();
    }
    window.addEventListener("hashchange", readNewFragment);
    return () => {
      disposed = true;
      window.removeEventListener("hashchange", readNewFragment);
    };
  }, []);

  return (
    <>
      {proof === null && <p className="text-sm/6 text-muted-ink" role="status">Đang kiểm tra liên kết…</p>}
      {proof === "" && (
        <div className="space-y-4">
          <AuthNotice tone="error">Liên kết này không hợp lệ hoặc đã hết hạn.</AuthNotice>
          {verifying ? (
            <Link className={authLink} href="/register?resend=1">Gửi lại email xác minh</Link>
          ) : (
            <Link className={authLink} href="/forgot-password">Yêu cầu liên kết mới</Link>
          )}
        </div>
      )}
      {proof && (
        <AuthForm
          label={verifying ? "Xác minh và tạo tài khoản" : "Lưu mật khẩu mới"}
          pendingLabel={verifying ? "Đang xác minh…" : "Đang lưu mật khẩu…"}
          onUnavailableProof={() => setProof("")}
          validate={(data) => {
            if (verifying) {
              const name = readText(data, "display_name").trim();
              if (!name || Array.from(name).length > 80) {
                return { field: "display_name", message: "Tên hiển thị phải có từ 1 đến 80 ký tự." };
              }
            }
            return validateNewPassword(readText(data, "password"), readText(data, "confirmation"));
          }}
          action={async (data) => {
            const password = readText(data, "password");
            if (verifying) {
              await verifyEmail({ token: proof, password, display_name: readText(data, "display_name").trim() });
            } else {
              await resetPassword({ token: proof, password });
            }
            window.location.replace(verifying ? "/login?verified=1" : "/login?reset=1");
          }}
        >
          {(issue) => (
            <>
              {verifying && <AuthField label="Tên hiển thị" name="display_name" autoComplete="nickname" issue={issue} />}
              <AuthField label="Mật khẩu" name="password" type="password" autoComplete="new-password" hint="Dùng từ 12 đến 128 ký tự." issue={issue} />
              <AuthField label="Nhập lại mật khẩu" name="confirmation" type="password" autoComplete="new-password" issue={issue} />
            </>
          )}
        </AuthForm>
      )}
      <AuthFooter><Link className={authLink} href="/login">Quay lại đăng nhập</Link></AuthFooter>
    </>
  );
}
