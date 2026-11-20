"use client";

import { useEffect } from "react";

import { logout } from "@/lib/api/auth";

import { AuthForm } from "./form";

export function LogoutForm() {
  useEffect(() => {
    function revalidateRestoredPage(event: PageTransitionEvent) {
      if (event.persisted) window.location.reload();
    }
    window.addEventListener("pageshow", revalidateRestoredPage);
    return () => window.removeEventListener("pageshow", revalidateRestoredPage);
  }, []);

  return (
    <AuthForm
      label="Đăng xuất"
      pendingLabel="Đang đăng xuất…"
      action={async () => {
        await logout();
        window.location.replace("/login");
      }}
    />
  );
}
