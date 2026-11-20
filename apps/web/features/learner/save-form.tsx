"use client";

import { useEffect, useId, useRef, useState, useSyncExternalStore, useTransition, type FormEvent, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { AuthApiError } from "@/lib/api/auth";
import { LearnerApiError } from "@/lib/api/learner";

import type { FieldIssue } from "../auth/flow";
import { AuthNotice } from "../auth/form";
import { authLink } from "../auth/shell";

const saveClass = "min-h-12 rounded-lg bg-brand px-5 py-3 font-semibold text-white transition-colors hover:bg-brand/90 active:bg-ink focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:cursor-not-allowed disabled:bg-muted-ink motion-reduce:transition-none";
const subscribeToHydration = () => () => {};
const hydratedOnClient = () => true;
const hydratedOnServer = () => false;

function saveError(error: unknown) {
  if (!(error instanceof LearnerApiError || error instanceof AuthApiError)) {
    return "Không thể kết nối. Vui lòng kiểm tra mạng rồi thử lại.";
  }
  if (error.status === 403) return "Không thể xác nhận yêu cầu. Vui lòng thử lại.";
  if (error.status === 422) return "Vui lòng kiểm tra lại thông tin đã nhập.";
  if (error.status === 429) return "Bạn đã gửi quá nhiều yêu cầu. Vui lòng đợi một lúc rồi thử lại.";
  if (error.status === 409) return "Yêu cầu lưu bị xung đột. Vui lòng thử lại.";
  return "Chưa lưu được thông tin. Vui lòng thử lại.";
}

export function SaveForm({ children, label, successMessage, action }: {
  children: (issue?: FieldIssue) => ReactNode;
  label: string;
  successMessage: string;
  action: (data: FormData) => Promise<FieldIssue | void>;
}) {
  const router = useRouter();
  const form = useRef<HTMLFormElement>(null);
  const sending = useRef(false);
  const [pending, setPending] = useState(false);
  const [issue, setIssue] = useState<FieldIssue>();
  const [notice, setNotice] = useState<{ tone: "error" | "success"; message: string }>();
  const [stale, setStale] = useState(false);
  const [reloading, startReload] = useTransition();
  const hydrated = useSyncExternalStore(subscribeToHydration, hydratedOnClient, hydratedOnServer);

  useEffect(() => {
    if (!issue) return;
    const field = form.current?.elements.namedItem(issue.field);
    if (field instanceof HTMLElement) field.focus();
  }, [issue]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sending.current || stale) return;
    const data = new FormData(event.currentTarget);
    sending.current = true;
    setPending(true);
    setIssue(undefined);
    setNotice(undefined);

    try {
      const nextIssue = await action(data);
      if (nextIssue) setIssue(nextIssue);
      else setNotice({ tone: "success", message: successMessage });
    } catch (error) {
      if ((error instanceof LearnerApiError || error instanceof AuthApiError) && error.status === 401) {
        window.location.replace("/login");
      } else if (error instanceof LearnerApiError && error.code === "STALE_REVISION") {
        setStale(true);
        setNotice({
          tone: "error",
          message: "Tùy chọn đã được thay đổi ở nơi khác. Hãy tải lại bản đã lưu để tiếp tục.",
        });
      } else {
        setNotice({ tone: "error", message: saveError(error) });
      }
    } finally {
      sending.current = false;
      setPending(false);
    }
  }

  return (
    <form
      ref={form}
      method="post"
      noValidate
      onSubmit={submit}
      onChange={({ target }) => {
        if (notice?.tone === "success") setNotice(undefined);
        if (issue && target instanceof HTMLElement && target.getAttribute("name") === issue.field) {
          setIssue(undefined);
        }
      }}
    >
      <fieldset className="min-w-0 space-y-5" disabled={!hydrated || pending}>
        {children(issue)}
        {notice && <AuthNotice tone={notice.tone}>{notice.message}</AuthNotice>}
        <div className="flex flex-wrap items-center gap-x-5 gap-y-3 border-t border-line pt-5">
          <button className={`${saveClass} w-full sm:w-auto`} disabled={stale} type="submit">
            {pending ? "Đang lưu…" : hydrated ? label : "Đang tải biểu mẫu…"}
          </button>
          {stale && (
            <button
              className={`${authLink} min-h-11 disabled:text-muted-ink`}
              disabled={reloading}
              type="button"
              onClick={() => startReload(() => router.refresh())}
            >
              {reloading ? "Đang tải tùy chọn…" : "Tải lại tùy chọn đã lưu"}
            </button>
          )}
        </div>
      </fieldset>
      <span className="sr-only" role="status">{pending ? "Đang lưu…" : ""}</span>
    </form>
  );
}

type ControlProps = {
  id: string;
  name: string;
  className: string;
  "aria-invalid"?: true;
  "aria-describedby"?: string;
};

export function LearnerField({ name, label, hint, issue, children }: {
  name: string;
  label: string;
  hint?: string;
  issue?: FieldIssue;
  children: (props: ControlProps) => ReactNode;
}) {
  const id = useId();
  const message = issue?.field === name ? issue.message : undefined;
  const description = [hint && `${id}-hint`, message && `${id}-error`].filter(Boolean).join(" ");
  const border = message ? "border-error-ink" : "border-control-line";

  return (
    <div className="min-w-0">
      <label className="mb-2 block text-sm/5 font-semibold" htmlFor={id}>{label}</label>
      {children({
        id,
        name,
        className: `min-h-12 w-full min-w-0 rounded-lg border ${border} bg-surface px-3.5 py-2.5 text-base/6 text-ink caret-brand hover:border-ink focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:bg-canvas`,
        "aria-invalid": message ? true : undefined,
        "aria-describedby": description || undefined,
      })}
      {hint && <p className="mt-2 text-sm/5 text-muted-ink" id={`${id}-hint`}>{hint}</p>}
      {message && <p className="mt-2 text-sm/5 text-error-ink" id={`${id}-error`} role="alert">{message}</p>}
    </div>
  );
}
