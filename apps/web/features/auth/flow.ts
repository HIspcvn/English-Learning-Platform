export type FieldIssue = { field: string; message: string };

export function loginDestination(onboardingCompleted: boolean) {
  return onboardingCompleted ? "/dashboard" : "/onboarding";
}

export function takeEmailProof(
  location: Pick<Location, "hash" | "pathname" | "search">,
  history: Pick<History, "replaceState" | "state">,
): string {
  const { hash, pathname, search } = location;
  if (hash || search) history.replaceState(history.state, "", pathname);
  const values = new URLSearchParams(hash.slice(1)).getAll("token");
  return values.length === 1 && /^[A-Za-z0-9_-]{43}$/.test(values[0]) ? values[0] : "";
}

export function readText(data: FormData, name: string): string {
  const value = data.get(name);
  return typeof value === "string" ? value : "";
}

export function validateEmail(email: string): FieldIssue | undefined {
  if (email.length > 254 || !/^[^@\s]+@[^@\s]+$/u.test(email)) {
    return { field: "email", message: "Vui lòng nhập địa chỉ email hợp lệ." };
  }
}

export function validateNewPassword(password: string, confirmation: string): FieldIssue | undefined {
  const length = Array.from(password).length;
  if (length < 12 || length > 128) {
    return { field: "password", message: "Mật khẩu phải có từ 12 đến 128 ký tự." };
  }
  if (password !== confirmation) {
    return { field: "confirmation", message: "Hai mật khẩu chưa khớp." };
  }
}
