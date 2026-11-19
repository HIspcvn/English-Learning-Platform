import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Nhịp Anh",
  description: "Nền tảng học tiếng Anh dành cho người nói tiếng Việt.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="vi">
      <body className="bg-canvas font-sans text-ink antialiased">{children}</body>
    </html>
  );
}
