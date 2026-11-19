"use client";

import { useEffect, useState } from "react";

import { isLiveResponse, LIVE_PATH } from "./probe";

const display = {
  checking: { text: "Đang kiểm tra API", color: "bg-canvas text-muted-ink" },
  available: { text: "API đang hoạt động", color: "bg-success-bg text-success-ink" },
  unavailable: { text: "Chưa kết nối được API", color: "bg-error-bg text-error-ink" },
};

export function ApiStatus() {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ attempt: number; available: boolean }>();
  const phase = result?.attempt === attempt
    ? (result.available ? "available" : "unavailable")
    : "checking";

  useEffect(() => {
    let current = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 5_000);

    const saveResult = (available: boolean) => {
      window.clearTimeout(timeout);
      if (current) {
        setResult({ attempt, available });
      }
    };

    void fetch(LIVE_PATH, { cache: "no-store", signal: controller.signal })
      .then(isLiveResponse)
      .then(saveResult, () => saveResult(false));

    return () => {
      current = false;
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [attempt]);

  return (
    <section
      aria-labelledby="api-status-title"
      className="max-w-sm rounded-xl border border-line bg-surface p-5 sm:p-6"
    >
      <h2 className="text-lg font-semibold" id="api-status-title">
        Kết nối dịch vụ
      </h2>
      <p className={`mt-3 rounded-md px-3 py-2 text-sm font-medium ${display[phase].color}`} role="status">
        {display[phase].text}
      </p>
      <button
        className="mt-3 min-h-11 rounded-md px-3 text-sm font-semibold text-brand underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:cursor-wait disabled:text-muted-ink"
        disabled={phase === "checking"}
        onClick={() => setAttempt((previous) => previous + 1)}
        type="button"
      >
        {phase === "unavailable" ? "Thử lại" : "Kiểm tra lại"}
      </button>
    </section>
  );
}
