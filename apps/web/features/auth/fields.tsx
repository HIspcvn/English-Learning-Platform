"use client";

import { useId, useState, type ComponentPropsWithoutRef } from "react";

import type { FieldIssue } from "./flow";

type AuthFieldProps = ComponentPropsWithoutRef<"input"> & {
  name: string;
  label: string;
  hint?: string;
  issue?: FieldIssue;
};

export function AuthField({ name, label, hint, issue, type = "text", ...input }: AuthFieldProps) {
  const id = useId();
  const error = issue?.field === name ? issue.message : undefined;
  const [visible, setVisible] = useState(false);
  const password = type === "password";
  const visibilityLabel = name === "confirmation" ? "mật khẩu nhập lại" : "mật khẩu";
  const ariaDescription = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(" ");

  return (
    <div className="min-w-0">
      <label className="mb-2 block text-sm/5 font-semibold" htmlFor={id}>{label}</label>
      <div className="flex min-w-0 gap-2">
        <input
          {...input}
          id={id}
          name={name}
          type={password && visible ? "text" : type}
          aria-invalid={error ? true : undefined}
          aria-describedby={ariaDescription || undefined}
          required
          className={`min-h-12 w-full min-w-0 rounded-lg border bg-surface px-3.5 py-2.5 text-base/6 text-ink caret-brand outline-none transition-colors hover:border-ink focus-visible:border-focus focus-visible:outline-3 focus-visible:outline-offset-1 focus-visible:outline-focus disabled:bg-canvas motion-reduce:transition-none ${error ? "border-error-ink" : "border-control-line"}`}
        />
        {password && (
          <button
            aria-label={`${visible ? "Ẩn" : "Hiện"} ${visibilityLabel}`}
            aria-controls={id}
            className="min-h-12 min-w-14 flex-none rounded-lg border border-control-line bg-surface px-2.5 text-sm font-semibold text-brand hover:bg-canvas focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:text-muted-ink"
            type="button"
            onClick={() => setVisible((current) => !current)}
          >
            {visible ? "Ẩn" : "Hiện"}
          </button>
        )}
      </div>
      {hint && <p className="mt-2 text-sm/5 text-muted-ink" id={`${id}-hint`}>{hint}</p>}
      {error && <p className="mt-2 text-sm/5 text-error-ink" id={`${id}-error`} role="alert">{error}</p>}
    </div>
  );
}
