"use client";

import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";

import { AuthApiError } from "@/lib/api/auth";

import type { FieldIssue } from "./flow";

type AuthNoticeProps = { children: ReactNode; tone?: "error" | "success" };

export function AuthNotice({ children, tone = "success" }: AuthNoticeProps) {
  return (
    <p
      className={`rounded-lg px-4 py-3 text-sm/6 ${tone === "error" ? "bg-error-bg text-error-ink" : "bg-success-bg text-success-ink"}`}
      role={tone === "error" ? "alert" : "status"}
    >
      {children}
    </p>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof AuthApiError) {
    switch (error.status) {
      case 401:
        return "Email hoặc mật khẩu không đúng, hoặc tài khoản chưa sẵn sàng.";
      case 403:
        return "Không thể xác nhận yêu cầu. Vui lòng thử lại.";
      case 422:
        return "Vui lòng kiểm tra lại thông tin đã nhập.";
      case 429:
        return "Bạn đã gửi quá nhiều yêu cầu. Vui lòng đợi một lúc rồi thử lại.";
      default:
        return "Dịch vụ đang tạm gián đoạn. Vui lòng thử lại sau.";
    }
  }
  return "Không thể kết nối. Vui lòng kiểm tra mạng rồi thử lại.";
}

type AuthFormProps = {
  children?: (issue?: FieldIssue) => ReactNode;
  label: string;
  pendingLabel: string;
  action: (data: FormData) => Promise<void>;
  validate?: (data: FormData) => FieldIssue | undefined;
  onUnavailableProof?: () => void;
};

export function AuthForm({ children, action, validate, label, pendingLabel, onUnavailableProof }: AuthFormProps) {
  const form = useRef<HTMLFormElement>(null);
  const sending = useRef(false);
  const [pending, setPending] = useState(false);
  const [issue, setIssue] = useState<FieldIssue>();
  const [error, setError] = useState("");

  useEffect(() => {
    if (!issue) return;
    const field = form.current?.elements.namedItem(issue.field);
    if (field instanceof HTMLInputElement) field.focus();
  }, [issue]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sending.current) return;
    const data = new FormData(event.currentTarget);
    const nextIssue = validate?.(data);
    setIssue(nextIssue);
    setError("");
    if (nextIssue) return;

    sending.current = true;
    setPending(true);
    try {
      await action(data);
    } catch (error) {
      if (error instanceof AuthApiError && error.status === 410 && onUnavailableProof) {
        onUnavailableProof();
      } else {
        setError(errorMessage(error));
      }
    } finally {
      sending.current = false;
      setPending(false);
    }
  }

  return (
    <form ref={form} method="post" noValidate onSubmit={submit}>
      <fieldset className="space-y-5" disabled={pending}>
        {children?.(issue)}
        {error && <AuthNotice tone="error">{error}</AuthNotice>}
        <button
          className="min-h-12 w-full rounded-lg bg-brand px-4 py-3 text-base/6 font-semibold text-white transition-colors hover:bg-brand/90 active:bg-ink focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:cursor-wait disabled:bg-muted-ink motion-reduce:transition-none"
          type="submit"
        >
          {pending ? pendingLabel : label}
        </button>
      </fieldset>
      <span className="sr-only" role="status">{pending ? pendingLabel : ""}</span>
    </form>
  );
}
