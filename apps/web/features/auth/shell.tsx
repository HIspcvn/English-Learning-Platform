import type { ReactNode } from "react";

export const authLink = "rounded-sm font-semibold text-brand underline underline-offset-4 hover:decoration-2 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus";

export function AuthShell({ children, wide = false, headerAction }: {
  children: ReactNode;
  wide?: boolean;
  headerAction?: ReactNode;
}) {
  return (
    <div className="flex min-h-dvh flex-col bg-surface sm:bg-canvas">
      <a
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-10 focus:rounded-md focus:bg-surface focus:px-4 focus:py-3 focus:text-brand"
        href="#main-content"
      >
        Bỏ qua đến nội dung chính
      </a>
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex min-h-16 max-w-5xl items-center justify-between gap-4 px-5 sm:px-10">
          {/* eslint-disable-next-line @next/next/no-html-link-for-pages -- Returning to a learner page must reach the server guard instead of Next's client cache. */}
          <a
            className="rounded-sm text-xl font-semibold tracking-tight text-brand focus-visible:outline-3 focus-visible:outline-offset-4 focus-visible:outline-focus"
            href="/"
            aria-label="Nhịp Anh, trang chủ"
          >
            Nhịp Anh
          </a>
          {headerAction}
        </div>
      </header>
      <main
        className={wide
          ? "mx-auto w-full max-w-5xl flex-1 px-5 py-8 sm:px-10 sm:py-12"
          : "mx-auto w-full max-w-[30rem] flex-1 px-5 pt-10 pb-12 sm:px-0 sm:pt-[clamp(3rem,10vh,6rem)]"}
        id="main-content"
        tabIndex={-1}
      >
        {wide ? children : <div className="bg-surface sm:rounded-xl sm:border sm:border-line sm:p-10">{children}</div>}
      </main>
    </div>
  );
}

export function AuthHeading({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="mb-8">
      <h1 className="text-[2rem]/10 font-semibold tracking-tight text-balance sm:text-[2.5rem]/12">
        {title}
      </h1>
      {children && <p className="mt-3 text-base/6.5 text-muted-ink">{children}</p>}
    </header>
  );
}

export function AuthFooter({ children }: { children: ReactNode }) {
  return <div className="mt-7 border-t border-line pt-5 text-sm/6 text-muted-ink">{children}</div>;
}
