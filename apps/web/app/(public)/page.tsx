import Link from "next/link";

import { authLink } from "@/features/auth/shell";
import { ApiStatus } from "@/features/platform-status/api-status";

export default function Home() {
  return (
    <>
      <a
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:rounded-md focus:bg-surface focus:px-4 focus:py-3 focus:text-brand"
        href="#main-content"
      >
        Bỏ qua đến nội dung chính
      </a>
      <main
        className="mx-auto flex min-h-dvh max-w-5xl flex-col justify-center gap-8 px-5 py-12 sm:px-10 lg:grid lg:grid-cols-[1fr_20rem] lg:content-center lg:items-center lg:gap-16"
        id="main-content"
        tabIndex={-1}
      >
        <div>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">Nhịp Anh</h1>
          <p className="mt-4 max-w-md text-lg/8 text-muted-ink">
            Nền tảng học tiếng Anh dành cho người nói tiếng Việt.
          </p>
          <nav aria-label="Tài khoản" className="mt-7 flex flex-wrap items-center gap-x-6 gap-y-3">
            <Link
              className="rounded-lg bg-brand px-5 py-3 font-semibold text-white hover:bg-brand/90 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus"
              href="/register"
            >
              Đăng ký
            </Link>
            <Link className={authLink} href="/login">Đăng nhập</Link>
          </nav>
        </div>
        <ApiStatus />
      </main>
    </>
  );
}
